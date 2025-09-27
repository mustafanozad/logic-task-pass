const moment = require('moment');
const Employee = require('../models/Employee');
const Event = require('../models/Event');

class CalculationEngine {
  constructor() {
    this.today = moment();
  }

  // حساب الخدمة الفعلية (غير متأثرة بالإجازات عدا الطويلة)
  calculateActualService(hireDate, events) {
    let serviceDays = this.today.diff(moment(hireDate), 'days');
    
    // طرح أيام الإجازات الطويلة
    const longLeaves = events.filter(event => 
      ['leave_no_pay', 'leave_disabled', 'leave_5_years'].includes(event.type) &&
      event.startDate && event.endDate
    );
    
    longLeaves.forEach(leave => {
      const leaveDays = moment(leave.endDate).diff(moment(leave.startDate), 'days');
      serviceDays -= leaveDays;
    });
    
    const years = Math.floor(serviceDays / 365);
    const months = Math.floor((serviceDays % 365) / 30);
    const days = serviceDays % 30;
    
    return { years, months, days };
  }

  // حساب التأثير من الأحداث على تاريخ الاستحقاق
  calculateEventImpact(events, baseDate) {
    let adjustedDate = moment(baseDate);
    
    events.forEach(event => {
      if (event.applied) return; // تم تطبيقه سابقاً
      
      switch(event.type) {
        case 'commendation':
          // تقليل المدة
          adjustedDate.subtract(event.reductionPeriod, 'months');
          break;
        case 'notice_penalty':
          adjustedDate.add(3, 'months');
          break;
        case 'warning_penalty':
          adjustedDate.add(6, 'months');
          break;
        case 'reprimand_penalty':
          adjustedDate.add(12, 'months');
          break;
        case 'degree_upgrade':
          adjustedDate.subtract(12, 'months');
          break;
        case 'leave_no_pay':
        case 'leave_disabled':
        case 'leave_5_years':
        case 'leave_maternity':
          // تجميد الحسابات خلال الإجازة
          if (event.startDate && event.endDate) {
            const freezeDays = moment(event.endDate).diff(moment(event.startDate), 'days');
            adjustedDate.add(freezeDays, 'days');
          }
          break;
        case 'custom':
          if (event.adjustmentType === 'add') {
            adjustedDate.add(event.adjustmentMonths, 'months');
          } else {
            adjustedDate.subtract(event.adjustmentMonths, 'months');
          }
          break;
      }
    });
    
    return adjustedDate;
  }

  // تحديد نوع الاستحقاق القادم بناءً على مؤشر التتبع
  getNextEntitlementType(tracker, grade) {
    if (grade === 1) {
      return tracker < 10 ? 'allowance' : null; // الدرجة 1 لها علاوات فقط حتى 10
    }
    
    const [cycle, position] = tracker.split('/').map(Number);
    
    if (grade >= 6 && grade <= 10) {
      // دورة 4: 3 علاوات + 1 ترفيع
      return position < 3 ? 'allowance' : 'promotion';
    } else if (grade >= 2 && grade <= 5) {
      // دورة 5: 4 علاوات + 1 ترفيع
      return position < 4 ? 'allowance' : 'promotion';
    }
    
    return 'allowance'; // افتراضي
  }

  // حساب الاستحقاق التالي
  calculateNextEntitlement(employee, events) {
    const baseDate = moment(employee.lastAllowanceDate);
    const adjustedDate = this.calculateEventImpact(events, baseDate);
    
    // إضافة 12 شهراً
    let nextDate = adjustedDate.clone().add(12, 'months');
    
    const type = this.getNextEntitlementType(employee.promotionTracker, employee.grade);
    
    let newGrade = employee.grade;
    let newStage = employee.stage;
    
    if (type === 'allowance') {
      newStage += 1;
    } else if (type === 'promotion') {
      newGrade -= 1;
      newStage = 1;
    }
    
    return {
      type,
      date: nextDate.toDate(),
      newGrade,
      newStage
    };
  }

  // تحديث مسار الموظف بالعلاوات والترفيعات المفقودة
  updateCareerHistory(employee, events) {
    const history = [];
    let currentDate = moment(employee.lastAllowanceDate);
    let currentTracker = employee.promotionTracker;
    let currentGrade = employee.grade;
    let currentStage = employee.stage;
    
    while (currentDate.isBefore(this.today)) {
      const adjustedDate = this.calculateEventImpact(events, currentDate);
      const nextDate = adjustedDate.clone().add(12, 'months');
      
      if (nextDate.isAfter(this.today)) break;
      
      const type = this.getNextEntitlementType(currentTracker, currentGrade);
      
      if (type === 'allowance') {
        currentStage += 1;
        const [cycle, pos] = currentTracker.split('/').map(Number);
        currentTracker = `${cycle}/${pos + 1}`;
        history.push({
          type: 'allowance',
          date: nextDate.toDate(),
          description: `تمت إضافة علاوة سنوية - المرحلة ${currentStage}`,
          grade: currentGrade,
          stage: currentStage
        });
      } else if (type === 'promotion') {
        currentGrade -= 1;
        currentStage = 1;
        currentTracker = currentGrade >= 6 ? '4/0' : '5/0';
        history.push({
          type: 'promotion',
          date: nextDate.toDate(),
          description: `تم الترفيع إلى الدرجة ${currentGrade} المرحلة ${currentStage}`,
          grade: currentGrade,
          stage: currentStage
        });
      }
      
      currentDate = nextDate;
    }
    
    return {
      history,
      updatedTracker: currentTracker,
      updatedGrade: currentGrade,
      updatedStage: currentStage
    };
  }

  // تشغيل المحرك لموظف معين
  async processEmployee(employeeId) {
    const employee = await Employee.findById(employeeId);
    const events = await Event.find({ employeeId }).sort({ documentDate: 1 });
    
    // حساب الخدمة الفعلية
    const service = this.calculateActualService(employee.hireDate, events);
    
    // تحديث المسار الوظيفي
    const careerUpdate = this.updateCareerHistory(employee, events);
    
    // حساب الاستحقاق القادم
    const nextEntitlement = this.calculateNextEntitlement(employee, events);
    
    // تحديث الموظف
    employee.serviceYears = service.years;
    employee.serviceMonths = service.months;
    employee.serviceDays = service.days;
    employee.grade = careerUpdate.updatedGrade;
    employee.stage = careerUpdate.updatedStage;
    employee.promotionTracker = careerUpdate.updatedTracker;
    employee.nextEntitlement = nextEntitlement;
    employee.careerHistory = [...employee.careerHistory, ...careerUpdate.history];
    
    await employee.save();
    
    // تحديث الأحداث كمطبقة
    await Event.updateMany({ employeeId }, { applied: true });
    
    return employee;
  }
}

module.exports = new CalculationEngine();
