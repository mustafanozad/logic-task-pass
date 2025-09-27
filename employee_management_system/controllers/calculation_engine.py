#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
محرك الحسابات الذكي
Intelligent Calculation Engine

المحرك الأساسي لحساب العلاوات والترفيعات بشكل تلقائي
"""

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional, Tuple, Any
import calendar

from ..models.employee import Employee
from ..models.event import ProfessionalEvent, CareerEvent, EffectType
from ..database.database_manager import DatabaseManager

class CalculationEngine:
    """
    محرك الحسابات الذكي
    يقوم بحساب العلاوات والترفيعات بناءً على القواعد المعقدة
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة محرك الحسابات
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        self.db_manager = db_manager
        
        # القواعد الأساسية
        self.ALLOWANCE_PERIOD_MONTHS = 12
        self.PROMOTION_RULES = {
            # الدرجات 6-10: 3 علاوات + ترفيع
            'grades_6_10': {'allowances': 3, 'tracker_total': 4},
            # الدرجات 2-5: 4 علاوات + ترفيع
            'grades_2_5': {'allowances': 4, 'tracker_total': 5},
            # الدرجة 1: علاوات فقط حتى المرحلة 11
            'grade_1': {'max_stage': 11}
        }
    
    def calculate_employee_status(self, employee: Employee) -> Dict[str, Any]:
        """
        حساب الحالة الحالية للموظف وتحديث مساره الوظيفي
        
        Args:
            employee: بيانات الموظف
            
        Returns:
            قاموس يحتوي على الحالة المحدثة
        """
        try:
            # الحصول على الأحداث المهنية للموظف
            professional_events = self._get_employee_events(employee.id)
            
            # مسح المسار الوظيفي التلقائي السابق
            self.db_manager.clear_employee_career_history(employee.id)
            
            # حساب المسار الوظيفي الجديد
            career_timeline = self._calculate_career_timeline(employee, professional_events)
            
            # تحديث بيانات الموظف
            updated_employee = self._update_employee_from_timeline(employee, career_timeline)
            
            # حساب الاستحقاق القادم
            next_entitlement = self._calculate_next_entitlement(updated_employee, professional_events)
            
            # حساب الخدمة الفعلية
            effective_service = self._calculate_effective_service(employee, professional_events)
            
            return {
                'employee': updated_employee,
                'career_timeline': career_timeline,
                'next_entitlement': next_entitlement,
                'effective_service': effective_service,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"خطأ في حساب حالة الموظف: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_employee_events(self, employee_id: int) -> List[ProfessionalEvent]:
        """
        الحصول على الأحداث المهنية للموظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            قائمة الأحداث المهنية مرتبة حسب التاريخ
        """
        events_data = self.db_manager.get_employee_events(employee_id)
        events = []
        
        for event_data in events_data:
            event = ProfessionalEvent.from_dict(dict(event_data))
            events.append(event)
        
        # ترتيب الأحداث حسب التاريخ
        events.sort(key=lambda x: x.event_date)
        return events
    
    def _calculate_career_timeline(self, employee: Employee, 
                                 professional_events: List[ProfessionalEvent]) -> List[CareerEvent]:
        """
        حساب المسار الوظيفي الكامل للموظف
        
        Args:
            employee: بيانات الموظف
            professional_events: الأحداث المهنية
            
        Returns:
            قائمة أحداث المسار الوظيفي
        """
        career_events = []
        
        # نقطة البداية
        current_date = employee.last_allowance_date
        current_grade = employee.job_grade
        current_stage = employee.job_stage
        current_tracker, tracker_total = employee.get_promotion_tracker_parts()
        
        # التحقق من الحالة الخاصة للترفيع السريع
        is_fast_promotion = self._check_fast_promotion_eligibility(employee)
        
        today = date.today()
        
        while current_date <= today:
            # حساب تاريخ الاستحقاق التالي
            next_entitlement_date = self._calculate_next_entitlement_date(
                current_date, professional_events, current_date
            )
            
            # إذا كان التاريخ في المستقبل، توقف
            if next_entitlement_date > today:
                break
            
            # تحديد نوع الحدث
            if is_fast_promotion:
                # الترفيع السريع للموظفين الجدد
                event_type = "ترفيع"
                new_grade = current_grade - 1
                new_stage = 1
                new_tracker = 0
                is_fast_promotion = False  # يحدث مرة واحدة فقط
            elif self._is_ready_for_promotion(current_tracker, tracker_total):
                # ترفيع عادي
                event_type = "ترفيع"
                new_grade = current_grade - 1 if current_grade > 1 else 1
                new_stage = 1
                new_tracker = 0
                # تحديث tracker_total للدرجة الجديدة
                tracker_total = self._get_tracker_total_for_grade(new_grade)
            else:
                # علاوة
                event_type = "علاوة"
                new_grade = current_grade
                new_stage = current_stage + 1
                new_tracker = current_tracker + 1
            
            # إنشاء حدث المسار الوظيفي
            career_event = CareerEvent(
                employee_id=employee.id,
                event_type=event_type,
                event_date=next_entitlement_date,
                from_grade=current_grade,
                to_grade=new_grade,
                from_stage=current_stage,
                to_stage=new_stage,
                is_automatic=True
            )
            
            # إضافة الوصف
            if event_type == "علاوة":
                career_event.description = f"علاوة سنوية - انتقال من المرحلة {current_stage} إلى المرحلة {new_stage}"
            else:
                career_event.description = f"ترفيع - انتقال من الدرجة {current_grade} إلى الدرجة {new_grade}"
            
            career_events.append(career_event)
            
            # حفظ الحدث في قاعدة البيانات
            self.db_manager.add_career_event(career_event.to_dict())
            
            # تحديث الحالة الحالية
            current_date = next_entitlement_date
            current_grade = new_grade
            current_stage = new_stage
            current_tracker = new_tracker
            
            # التحقق من الوصول للحد الأقصى للدرجة الأولى
            if current_grade == 1 and current_stage >= self.PROMOTION_RULES['grade_1']['max_stage']:
                break
        
        return career_events
    
    def _check_fast_promotion_eligibility(self, employee: Employee) -> bool:
        """
        التحقق من أهلية الترفيع السريع
        
        Args:
            employee: بيانات الموظف
            
        Returns:
            True إذا كان مؤهلاً للترفيع السريع
        """
        # الشروط: تاريخ المباشرة = تاريخ آخر استحقاق، الدرجة 8 المرحلة 5، شهادة دبلوم
        return (employee.start_date == employee.last_allowance_date and
                employee.job_grade == 8 and
                employee.job_stage == 5 and
                "دبلوم" in employee.academic_degree.lower())
    
    def _is_ready_for_promotion(self, current_tracker: int, tracker_total: int) -> bool:
        """
        التحقق من استعداد الموظف للترفيع
        
        Args:
            current_tracker: العداد الحالي
            tracker_total: العداد الإجمالي
            
        Returns:
            True إذا كان مستعداً للترفيع
        """
        return current_tracker >= tracker_total - 1
    
    def _get_tracker_total_for_grade(self, grade: int) -> int:
        """
        الحصول على العداد الإجمالي للدرجة
        
        Args:
            grade: الدرجة الوظيفية
            
        Returns:
            العداد الإجمالي
        """
        if 6 <= grade <= 10:
            return self.PROMOTION_RULES['grades_6_10']['tracker_total']
        elif 2 <= grade <= 5:
            return self.PROMOTION_RULES['grades_2_5']['tracker_total']
        else:
            return 4  # افتراضي
    
    def _calculate_next_entitlement_date(self, base_date: date, 
                                       professional_events: List[ProfessionalEvent],
                                       calculation_point: date) -> date:
        """
        حساب تاريخ الاستحقاق التالي مع تطبيق تأثيرات الأحداث المهنية
        
        Args:
            base_date: التاريخ الأساسي
            professional_events: الأحداث المهنية
            calculation_point: نقطة الحساب الحالية
            
        Returns:
            تاريخ الاستحقاق التالي
        """
        # البداية: إضافة 12 شهراً
        next_date = base_date + relativedelta(months=self.ALLOWANCE_PERIOD_MONTHS)
        
        # تطبيق تأثيرات الأحداث المهنية
        for event in professional_events:
            # تطبيق الأحداث التي حدثت بعد التاريخ الأساسي وقبل نقطة الحساب
            if base_date < event.event_date <= calculation_point:
                next_date = self._apply_event_effect(next_date, event)
        
        return next_date
    
    def _apply_event_effect(self, target_date: date, event: ProfessionalEvent) -> date:
        """
        تطبيق تأثير حدث مهني على تاريخ الاستحقاق
        
        Args:
            target_date: التاريخ المستهدف
            event: الحدث المهني
            
        Returns:
            التاريخ بعد تطبيق التأثير
        """
        if event.effect_type == EffectType.REDUCE.value:
            # تقليص المدة
            return target_date - relativedelta(months=event.effect_months)
        
        elif event.effect_type == EffectType.INCREASE.value:
            # زيادة المدة
            return target_date + relativedelta(months=event.effect_months)
        
        elif event.effect_type == EffectType.FREEZE.value:
            # تجميد المدة (إضافة فترة الإجازة)
            if event.start_date and event.end_date:
                freeze_days = (event.end_date - event.start_date).days
                return target_date + timedelta(days=freeze_days)
        
        return target_date
    
    def _update_employee_from_timeline(self, employee: Employee, 
                                     career_timeline: List[CareerEvent]) -> Employee:
        """
        تحديث بيانات الموظف من المسار الوظيفي
        
        Args:
            employee: بيانات الموظف الأصلية
            career_timeline: المسار الوظيفي
            
        Returns:
            بيانات الموظف المحدثة
        """
        if not career_timeline:
            return employee
        
        # آخر حدث في المسار الوظيفي
        last_event = career_timeline[-1]
        
        # تحديث الدرجة والمرحلة
        employee.job_grade = last_event.to_grade
        employee.job_stage = last_event.to_stage
        
        # تحديث مؤشر التتبع
        if last_event.event_type == "ترفيع":
            tracker_total = self._get_tracker_total_for_grade(employee.job_grade)
            employee.update_promotion_tracker(0, tracker_total)
        else:
            current_tracker, tracker_total = employee.get_promotion_tracker_parts()
            employee.update_promotion_tracker(current_tracker + 1, tracker_total)
        
        # تحديث تاريخ آخر استحقاق
        employee.last_allowance_date = last_event.event_date
        if last_event.event_type == "ترفيع":
            employee.last_promotion_date = last_event.event_date
        
        # حفظ التحديثات في قاعدة البيانات
        update_data = {
            'job_grade': employee.job_grade,
            'job_stage': employee.job_stage,
            'promotion_tracker': employee.promotion_tracker,
            'last_allowance_date': employee.last_allowance_date,
            'last_promotion_date': employee.last_promotion_date
        }
        self.db_manager.update_employee(employee.id, update_data)
        
        return employee
    
    def _calculate_next_entitlement(self, employee: Employee, 
                                  professional_events: List[ProfessionalEvent]) -> Dict[str, Any]:
        """
        حساب الاستحقاق القادم
        
        Args:
            employee: بيانات الموظف
            professional_events: الأحداث المهنية
            
        Returns:
            معلومات الاستحقاق القادم
        """
        # التحقق من الوصول للحد الأقصى
        if (employee.job_grade == 1 and 
            employee.job_stage >= self.PROMOTION_RULES['grade_1']['max_stage']):
            return {
                'type': 'none',
                'date': None,
                'description': 'وصل الموظف للحد الأقصى من العلاوات'
            }
        
        # حساب تاريخ الاستحقاق القادم
        next_date = self._calculate_next_entitlement_date(
            employee.last_allowance_date, professional_events, date.today()
        )
        
        # تحديد نوع الاستحقاق
        current_tracker, tracker_total = employee.get_promotion_tracker_parts()
        
        if self._is_ready_for_promotion(current_tracker, tracker_total):
            event_type = "ترفيع"
            next_grade = employee.job_grade - 1 if employee.job_grade > 1 else 1
            next_stage = 1
            description = f"ترفيع إلى الدرجة {next_grade} المرحلة {next_stage}"
        else:
            event_type = "علاوة"
            next_grade = employee.job_grade
            next_stage = employee.job_stage + 1
            description = f"علاوة سنوية إلى المرحلة {next_stage}"
        
        return {
            'type': event_type,
            'date': next_date,
            'next_grade': next_grade,
            'next_stage': next_stage,
            'description': description
        }
    
    def _calculate_effective_service(self, employee: Employee, 
                                   professional_events: List[ProfessionalEvent]) -> Dict[str, Any]:
        """
        حساب الخدمة الفعلية (مع خصم فترات الإجازات الطويلة)
        
        Args:
            employee: بيانات الموظف
            professional_events: الأحداث المهنية
            
        Returns:
            معلومات الخدمة الفعلية
        """
        start_date = employee.start_date
        end_date = date.today()
        
        # حساب إجمالي الخدمة
        total_service = end_date - start_date
        
        # حساب أيام الإجازات الطويلة
        freeze_days = 0
        freeze_events = [
            "إجازة بدون راتب",
            "إجازة رعاية المعاقين", 
            "إجازة الخمس سنوات"
        ]
        
        for event in professional_events:
            if (event.effect_type == EffectType.FREEZE.value and 
                event.event_type in freeze_events and
                event.start_date and event.end_date):
                freeze_days += (event.end_date - event.start_date).days
        
        # الخدمة الفعلية
        effective_days = total_service.days - freeze_days
        
        # تحويل إلى سنوات وأشهر وأيام
        years = effective_days // 365
        remaining_days = effective_days % 365
        months = remaining_days // 30
        days = remaining_days % 30
        
        return {
            'total_days': total_service.days,
            'freeze_days': freeze_days,
            'effective_days': effective_days,
            'years': years,
            'months': months,
            'days': days,
            'formatted': f"{years} سنة، {months} شهر، {days} يوم"
        }
    
    def recalculate_all_employees(self) -> Dict[str, Any]:
        """
        إعادة حساب جميع الموظفين
        
        Returns:
            تقرير العملية
        """
        try:
            employees_data = self.db_manager.get_all_employees()
            results = {
                'total': len(employees_data),
                'success': 0,
                'errors': []
            }
            
            for emp_data in employees_data:
                employee = Employee.from_dict(dict(emp_data))
                result = self.calculate_employee_status(employee)
                
                if result['status'] == 'success':
                    results['success'] += 1
                else:
                    results['errors'].append({
                        'employee_id': employee.id,
                        'name': employee.full_name,
                        'error': result.get('message', 'خطأ غير معروف')
                    })
            
            return results
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"خطأ في إعادة حساب الموظفين: {e}"
            }

