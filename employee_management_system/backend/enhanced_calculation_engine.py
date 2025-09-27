#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
المحرك الذكي المحسّن للحسابات
Enhanced Intelligent Calculation Engine for Employee Promotions and Allowances

هذا المحرك مسؤول عن:
- حساب العلاوات والترفيعات التلقائية بدقة عالية
- تطبيق تأثير الأحداث المهنية على المدد الزمنية
- إدارة منطق مؤشر تتبع الترفيع المعقد
- معالجة الحالات الخاصة مثل الترفيع السريع
- حساب التواريخ بدقة مع مراعاة السنوات الكبيسة
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from backend.enhanced_models import Employee, ProfessionalEvent, CareerHistory, EventType, CareerEventType, db
import logging
import calendar

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCalculationEngine:
    """المحرك الذكي المحسّن لحساب العلاوات والترفيعات"""
    
    def __init__(self, employee):
        """
        تهيئة المحرك للموظف المحدد
        
        Args:
            employee: كائن الموظف من قاعدة البيانات
        """
        self.employee = employee
        self.current_date = date.today()
        self.base_entitlement_months = 12  # المدة الأساسية للاستحقاق (12 شهر)
        
        # جلب جميع الأحداث المهنية للموظف مرتبة حسب التاريخ
        self.professional_events = ProfessionalEvent.query.filter_by(
            employee_id=employee.id
        ).order_by(ProfessionalEvent.event_date).all()
        
        logger.info(f"تم تهيئة المحرك المحسّن للموظف: {employee.full_name}")
    
    def add_months_precisely(self, start_date, months):
        """
        إضافة أشهر بدقة مع مراعاة السنوات الكبيسة وأطوال الأشهر المختلفة
        
        Args:
            start_date: التاريخ الأساسي
            months: عدد الأشهر المراد إضافتها
            
        Returns:
            date: التاريخ الجديد
        """
        try:
            # استخدام relativedelta للحساب الدقيق
            new_date = start_date + relativedelta(months=months)
            return new_date
        except Exception as e:
            logger.error(f"خطأ في حساب التاريخ: {e}")
            # في حالة الخطأ، استخدم الطريقة التقليدية
            return start_date + timedelta(days=months * 30)
    
    def calculate_effective_service(self):
        """
        حساب سنوات الخدمة الفعلية مع مراعاة الإجازات الطويلة
        
        Returns:
            dict: معلومات الخدمة الفعلية
        """
        start_date = self.employee.start_date
        end_date = self.current_date
        
        # حساب المدة الإجمالية
        total_delta = end_date - start_date
        total_days = total_delta.days
        
        # حساب أيام الإجازات التي تؤثر على الخدمة الفعلية
        freeze_days = 0
        
        for event in self.professional_events:
            if event.event_type in [
                EventType.UNPAID_LEAVE,
                EventType.DISABILITY_CARE_LEAVE,
                EventType.FIVE_YEAR_LEAVE,
                EventType.MATERNITY_LEAVE
            ]:
                if event.leave_start_date and event.leave_end_date:
                    leave_delta = event.leave_end_date - event.leave_start_date
                    freeze_days += leave_delta.days
        
        # حساب الخدمة الفعلية
        effective_days = total_days - freeze_days
        effective_years = effective_days // 365
        remaining_days = effective_days % 365
        effective_months = remaining_days // 30
        effective_days_final = remaining_days % 30
        
        return {
            'total_days': total_days,
            'freeze_days': freeze_days,
            'effective_days': effective_days,
            'years': effective_years,
            'months': effective_months,
            'days': effective_days_final,
            'formatted': f"{effective_years} سنة، {effective_months} شهر، {effective_days_final} يوم"
        }
    
    def parse_promotion_tracker(self, tracker_str):
        """
        تحليل مؤشر تتبع الترفيع
        
        Args:
            tracker_str: نص المؤشر مثل "3/4" أو "4/5"
            
        Returns:
            tuple: (الرقم الحالي، الرقم الإجمالي)
        """
        try:
            current, total = map(int, tracker_str.split('/'))
            return current, total
        except:
            logger.error(f"خطأ في تحليل مؤشر التتبع: {tracker_str}")
            return 0, 4  # القيمة الافتراضية
    
    def get_next_event_type(self):
        """
        تحديد نوع الحدث القادم (علاوة أم ترفيع)
        
        Returns:
            CareerEventType: نوع الحدث القادم
        """
        current, total = self.parse_promotion_tracker(self.employee.promotion_tracker)
        
        # التحقق من الحالة الخاصة للترفيع السريع
        if self.is_fast_promotion_case():
            return CareerEventType.PROMOTION
        
        # إذا وصل المؤشر للحد الأقصى، الحدث القادم ترفيع
        if current >= total - 1:
            return CareerEventType.PROMOTION
        else:
            return CareerEventType.ALLOWANCE
    
    def is_fast_promotion_case(self):
        """
        التحقق من حالة الترفيع السريع
        (موظف جديد بدرجة 8 مرحلة 5 وشهادة دبلوم)
        
        Returns:
            bool: True إذا كانت حالة ترفيع سريع
        """
        return (
            self.employee.start_date == self.employee.last_allowance_date and
            self.employee.job_grade == 8 and
            self.employee.current_stage == 5 and
            "دبلوم" in self.employee.academic_degree.lower()
        )
    
    def calculate_next_entitlement_date(self, base_date):
        """
        حساب تاريخ الاستحقاق القادم مع تطبيق تأثير الأحداث المهنية
        
        Args:
            base_date: التاريخ الأساسي للحساب
            
        Returns:
            date: تاريخ الاستحقاق القادم
        """
        # البدء بالمدة الأساسية (12 شهر)
        months_to_add = self.base_entitlement_months
        
        # تطبيق تأثير الأحداث المهنية
        for event in self.professional_events:
            if event.event_date >= base_date:
                continue  # تجاهل الأحداث المستقبلية
            
            # الأحداث الإيجابية (تقليص المدة)
            if event.event_type == EventType.COMMENDATION:
                if event.reduction_months:
                    months_to_add -= event.reduction_months
            elif event.event_type == EventType.HIGHER_DEGREE:
                months_to_add -= 12  # تقليص سنة كاملة (Step)
            
            # الأحداث السلبية (زيادة المدة)
            elif event.event_type == EventType.NOTICE_PENALTY:
                months_to_add += 3
            elif event.event_type == EventType.WARNING_PENALTY:
                months_to_add += 6
            elif event.event_type == EventType.REPRIMAND_PENALTY:
                months_to_add += 12
            
            # الأحداث المخصصة
            elif event.event_type == EventType.CUSTOM_EVENT:
                if event.impact_months:
                    months_to_add += event.impact_months
        
        # التأكد من أن المدة لا تقل عن شهر واحد
        months_to_add = max(1, months_to_add)
        
        # حساب التاريخ الجديد
        next_date = self.add_months_precisely(base_date, months_to_add)
        
        # تطبيق تأثير الإجازات (تجميد الخدمة)
        for event in self.professional_events:
            if event.event_type in [
                EventType.UNPAID_LEAVE,
                EventType.DISABILITY_CARE_LEAVE,
                EventType.FIVE_YEAR_LEAVE,
                EventType.MATERNITY_LEAVE
            ]:
                if (event.leave_start_date and event.leave_end_date and
                    event.leave_start_date <= next_date):
                    # إضافة مدة الإجازة للتاريخ
                    leave_days = (event.leave_end_date - event.leave_start_date).days
                    next_date += timedelta(days=leave_days)
        
        return next_date
    
    def process_single_entitlement(self, entitlement_date):
        """
        معالجة استحقاق واحد (علاوة أو ترفيع)
        
        Args:
            entitlement_date: تاريخ الاستحقاق
            
        Returns:
            dict: تفاصيل الاستحقاق المعالج
        """
        event_type = self.get_next_event_type()
        current, total = self.parse_promotion_tracker(self.employee.promotion_tracker)
        
        # معلومات الحالة الحالية
        from_grade = self.employee.job_grade
        from_stage = self.employee.current_stage
        from_tracker = self.employee.promotion_tracker
        
        if event_type == CareerEventType.ALLOWANCE:
            # معالجة العلاوة
            new_stage = from_stage + 1
            new_tracker_current = current + 1
            new_tracker = f"{new_tracker_current}/{total}"
            
            # تحديث بيانات الموظف
            self.employee.current_stage = new_stage
            self.employee.promotion_tracker = new_tracker
            self.employee.last_allowance_date = entitlement_date
            
            # إنشاء سجل في المسار الوظيفي
            career_record = CareerHistory(
                employee_id=self.employee.id,
                event_type=CareerEventType.ALLOWANCE,
                event_date=entitlement_date,
                from_grade=from_grade,
                to_grade=from_grade,
                from_stage=from_stage,
                to_stage=new_stage,
                tracker_before=from_tracker,
                tracker_after=new_tracker,
                description=f"علاوة سنوية - انتقل من المرحلة {from_stage} إلى المرحلة {new_stage}",
                is_automatic=True
            )
            
            return {
                'type': 'allowance',
                'date': entitlement_date,
                'from_stage': from_stage,
                'to_stage': new_stage,
                'tracker_before': from_tracker,
                'tracker_after': new_tracker,
                'record': career_record
            }
        
        else:  # ترفيع
            # معالجة الترفيع
            new_grade = from_grade - 1  # الدرجة تقل بالترفيع
            new_stage = 1  # العودة للمرحلة الأولى
            
            # تحديد المؤشر الجديد حسب الدرجة الجديدة
            if new_grade >= 6:
                new_tracker = "0/4"
            elif new_grade >= 2:
                new_tracker = "0/5"
            else:  # الدرجة الأولى
                new_tracker = "0/10"  # علاوات فقط
            
            # تحديث بيانات الموظف
            self.employee.job_grade = new_grade
            self.employee.current_stage = new_stage
            self.employee.promotion_tracker = new_tracker
            self.employee.last_allowance_date = entitlement_date
            self.employee.last_promotion_date = entitlement_date
            
            # إنشاء سجل في المسار الوظيفي
            career_record = CareerHistory(
                employee_id=self.employee.id,
                event_type=CareerEventType.PROMOTION,
                event_date=entitlement_date,
                from_grade=from_grade,
                to_grade=new_grade,
                from_stage=from_stage,
                to_stage=new_stage,
                tracker_before=from_tracker,
                tracker_after=new_tracker,
                description=f"ترفيع - من الدرجة {from_grade} إلى الدرجة {new_grade}",
                is_automatic=True
            )
            
            return {
                'type': 'promotion',
                'date': entitlement_date,
                'from_grade': from_grade,
                'to_grade': new_grade,
                'from_stage': from_stage,
                'to_stage': new_stage,
                'tracker_before': from_tracker,
                'tracker_after': new_tracker,
                'record': career_record
            }
    
    def process_all_entitlements(self):
        """
        معالجة جميع الاستحقاقات من آخر تاريخ استحقاق حتى اليوم
        
        Returns:
            dict: نتائج المعالجة
        """
        processed_entitlements = []
        current_base_date = self.employee.last_allowance_date
        
        logger.info(f"بدء معالجة الاستحقاقات للموظف {self.employee.full_name}")
        logger.info(f"نقطة البداية: {current_base_date}")
        
        # حلقة معالجة الاستحقاقات
        max_iterations = 50  # حماية من الحلقات اللانهائية
        iteration = 0
        
        while iteration < max_iterations:
            # حساب تاريخ الاستحقاق التالي
            next_entitlement_date = self.calculate_next_entitlement_date(current_base_date)
            
            logger.info(f"تاريخ الاستحقاق التالي المحسوب: {next_entitlement_date}")
            
            # إذا كان التاريخ في المستقبل، توقف
            if next_entitlement_date > self.current_date:
                break
            
            # معالجة الاستحقاق
            entitlement_result = self.process_single_entitlement(next_entitlement_date)
            processed_entitlements.append(entitlement_result)
            
            # إضافة السجل لقاعدة البيانات
            db.session.add(entitlement_result['record'])
            
            # تحديث نقطة البداية للحلقة التالية
            current_base_date = next_entitlement_date
            
            iteration += 1
            logger.info(f"تم معالجة استحقاق رقم {iteration}: {entitlement_result['type']}")
        
        # حفظ التغييرات
        try:
            db.session.commit()
            logger.info(f"تم حفظ {len(processed_entitlements)} استحقاق للموظف {self.employee.full_name}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في حفظ الاستحقاقات: {e}")
            raise
        
        return {
            'employee_name': self.employee.full_name,
            'processed_count': len(processed_entitlements),
            'entitlements': processed_entitlements,
            'current_grade': self.employee.job_grade,
            'current_stage': self.employee.current_stage,
            'current_tracker': self.employee.promotion_tracker
        }
    
    def get_next_entitlement(self):
        """
        الحصول على معلومات الاستحقاق القادم
        
        Returns:
            dict: معلومات الاستحقاق القادم
        """
        # أولاً، معالجة أي استحقاقات متأخرة
        self.process_all_entitlements()
        
        # حساب الاستحقاق القادم
        next_date = self.calculate_next_entitlement_date(self.employee.last_allowance_date)
        next_type = self.get_next_event_type()
        
        # تحديد التفاصيل حسب نوع الاستحقاق
        if next_type == CareerEventType.ALLOWANCE:
            next_stage = self.employee.current_stage + 1
            description = f"علاوة سنوية - الانتقال إلى المرحلة {next_stage}"
            details = f"الدرجة {self.employee.job_grade} - المرحلة {next_stage}"
        else:  # ترفيع
            next_grade = self.employee.job_grade - 1
            description = f"ترفيع - الانتقال إلى الدرجة {next_grade}"
            details = f"الدرجة {next_grade} - المرحلة 1"
        
        return {
            'type': next_type.value,
            'type_arabic': 'علاوة' if next_type == CareerEventType.ALLOWANCE else 'ترفيع',
            'date': next_date,
            'description': description,
            'details': details,
            'days_remaining': (next_date - self.current_date).days
        }
    
    def validate_event_constraints(self, event_type, employee_id, event_date):
        """
        التحقق من قيود الأحداث المهنية
        
        Args:
            event_type: نوع الحدث
            employee_id: معرف الموظف
            event_date: تاريخ الحدث
            
        Returns:
            dict: نتيجة التحقق
        """
        if event_type == EventType.COMMENDATION:
            # التحقق من القيد السنوي لكتب الشكر
            year_start = date(event_date.year, 1, 1)
            year_end = date(event_date.year, 12, 31)
            
            commendations_this_year = ProfessionalEvent.query.filter(
                and_(
                    ProfessionalEvent.employee_id == employee_id,
                    ProfessionalEvent.event_type == EventType.COMMENDATION,
                    ProfessionalEvent.event_date >= year_start,
                    ProfessionalEvent.event_date <= year_end
                )
            ).count()
            
            if commendations_this_year >= 3:
                return {
                    'valid': False,
                    'message': 'تم تجاوز الحد الأقصى لكتب الشكر في السنة (3 كتب)'
                }
            
            # التحقق من القيد الوظيفي لكتب الشكر 6 أشهر
            six_month_commendations = ProfessionalEvent.query.filter(
                and_(
                    ProfessionalEvent.employee_id == employee_id,
                    ProfessionalEvent.event_type == EventType.COMMENDATION,
                    ProfessionalEvent.reduction_months == 6
                )
            ).count()
            
            if six_month_commendations >= 2:
                return {
                    'valid': False,
                    'message': 'تم تجاوز الحد الأقصى لكتب الشكر 6 أشهر طوال المسيرة الوظيفية (2 كتب)'
                }
        
        return {'valid': True, 'message': 'الحدث صالح'}

# دوال مساعدة
def recalculate_employee_entitlements(employee_id):
    """
    إعادة حساب استحقاقات موظف محدد
    
    Args:
        employee_id: معرف الموظف
        
    Returns:
        dict: نتائج إعادة الحساب
    """
    employee = Employee.query.get(employee_id)
    if not employee:
        return {'error': 'الموظف غير موجود'}
    
    # حذف السجلات التلقائية السابقة
    CareerHistory.query.filter(
        and_(
            CareerHistory.employee_id == employee_id,
            CareerHistory.is_automatic == True
        )
    ).delete()
    
    # إعادة تعيين حالة الموظف لآخر استحقاق يدوي
    # هذا يتطلب منطق إضافي لتحديد الحالة الصحيحة
    
    # إعادة حساب الاستحقاقات
    engine = EnhancedCalculationEngine(employee)
    result = engine.process_all_entitlements()
    
    return result

def bulk_recalculate_all_employees():
    """
    إعادة حساب استحقاقات جميع الموظفين
    
    Returns:
        dict: نتائج إعادة الحساب الجماعي
    """
    employees = Employee.query.filter_by(status='active').all()
    results = []
    
    for employee in employees:
        try:
            result = recalculate_employee_entitlements(employee.id)
            results.append({
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'success': True,
                'result': result
            })
        except Exception as e:
            results.append({
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'success': False,
                'error': str(e)
            })
    
    return {
        'total_employees': len(employees),
        'results': results,
        'success_count': len([r for r in results if r['success']]),
        'error_count': len([r for r in results if not r['success']])
    }

