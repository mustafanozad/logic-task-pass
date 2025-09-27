#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
المحرك الذكي للحسابات
Intelligent Calculation Engine for Employee Promotions and Allowances

هذا المحرك مسؤول عن:
- حساب العلاوات والترفيعات التلقائية
- تطبيق تأثير الأحداث المهنية على المدد الزمنية
- إدارة منطق مؤشر تتبع الترفيع
- معالجة الحالات الخاصة مثل الترفيع السريع
"""

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from backend.models import Employee, ProfessionalEvent, CareerHistory, db
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculationEngine:
    """المحرك الذكي لحساب العلاوات والترفيعات"""
    
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
        
        logger.info(f"تم تهيئة المحرك للموظف: {employee.full_name}")
    
    def process_all_entitlements(self):
        """
        معالجة جميع الاستحقاقات من آخر تاريخ استحقاق حتى اليوم
        
        Returns:
            dict: نتائج المعالجة
        """
        logger.info(f"بدء معالجة الاستحقاقات للموظف: {self.employee.full_name}")
        
        results = {
            'processed_allowances': 0,
            'processed_promotions': 0,
            'events_processed': [],
            'next_entitlement': None
        }
        
        # نقطة البداية: آخر تاريخ استحقاق
        current_anchor_date = self.employee.last_allowance_date
        
        # حلقة المعالجة الرئيسية
        while True:
            # حساب تاريخ الاستحقاق التالي
            next_entitlement_date = self._calculate_next_entitlement_date(current_anchor_date)
            
            # التحقق من وصول تاريخ الاستحقاق
            if next_entitlement_date > self.current_date:
                # الاستحقاق في المستقبل - توقف الحلقة
                results['next_entitlement'] = {
                    'type': self.employee.get_next_entitlement_type(),
                    'date': next_entitlement_date,
                    'grade': self.employee.job_grade,
                    'stage': self.employee.current_stage
                }
                break
            
            # تنفيذ الاستحقاق
            entitlement_result = self._execute_entitlement(next_entitlement_date)
            
            if entitlement_result['type'] == 'allowance':
                results['processed_allowances'] += 1
            elif entitlement_result['type'] == 'promotion':
                results['processed_promotions'] += 1
            
            results['events_processed'].append(entitlement_result)
            
            # تحديث نقطة الارتكاز
            current_anchor_date = next_entitlement_date
            
            # تحديث آخر تاريخ استحقاق في قاعدة البيانات
            self.employee.last_allowance_date = next_entitlement_date
        
        logger.info(f"انتهت معالجة الاستحقاقات. العلاوات: {results['processed_allowances']}, الترفيعات: {results['processed_promotions']}")
        return results
    
    def _calculate_next_entitlement_date(self, anchor_date):
        """
        حساب تاريخ الاستحقاق التالي مع تطبيق تأثير الأحداث المهنية
        
        Args:
            anchor_date: تاريخ نقطة الارتكاز
            
        Returns:
            date: تاريخ الاستحقاق التالي
        """
        # البداية: إضافة 12 شهر للتاريخ الأساسي
        base_next_date = anchor_date + relativedelta(months=self.base_entitlement_months)
        
        # تطبيق تأثير الأحداث المهنية
        total_impact_months = 0
        total_freeze_days = 0
        
        # معالجة الأحداث التي تؤثر على هذا الاستحقاق
        relevant_events = [
            event for event in self.professional_events 
            if anchor_date <= event.event_date <= base_next_date
        ]
        
        for event in relevant_events:
            if event.event_type in ['commendation_letter', 'higher_degree']:
                # الأحداث الإيجابية - تقليص المدة
                total_impact_months -= abs(event.impact_months or 0)
                
            elif event.event_type in ['notice_penalty', 'warning_penalty', 'reprimand_penalty']:
                # الأحداث السلبية - زيادة المدة
                penalty_months = self._get_penalty_months(event.event_type)
                total_impact_months += penalty_months
                
            elif event.event_type in ['unpaid_leave', 'five_year_leave', 'disability_care_leave', 'maternity_leave']:
                # أحداث تجميد الخدمة
                if event.start_date and event.end_date:
                    freeze_days = (event.end_date - event.start_date).days
                    total_freeze_days += freeze_days
                    
            elif event.event_type == 'custom_event':
                # الأحداث المخصصة
                total_impact_months += (event.impact_months or 0)
        
        # تطبيق التأثيرات
        adjusted_date = base_next_date + relativedelta(months=total_impact_months)
        adjusted_date = adjusted_date + relativedelta(days=total_freeze_days)
        
        logger.debug(f"حساب الاستحقاق: الأساسي={base_next_date}, التأثير={total_impact_months} شهر, التجميد={total_freeze_days} يوم, النهائي={adjusted_date}")
        
        return adjusted_date
    
    def _execute_entitlement(self, entitlement_date):
        """
        تنفيذ الاستحقاق (علاوة أو ترفيع)
        
        Args:
            entitlement_date: تاريخ الاستحقاق
            
        Returns:
            dict: تفاصيل الاستحقاق المنفذ
        """
        # تحديد نوع الاستحقاق
        entitlement_type = self.employee.get_next_entitlement_type()
        
        if entitlement_type == 'allowance':
            return self._execute_allowance(entitlement_date)
        elif entitlement_type == 'promotion':
            return self._execute_promotion(entitlement_date)
        else:
            raise ValueError(f"نوع استحقاق غير معروف: {entitlement_type}")
    
    def _execute_allowance(self, entitlement_date):
        """
        تنفيذ علاوة سنوية
        
        Args:
            entitlement_date: تاريخ العلاوة
            
        Returns:
            dict: تفاصيل العلاوة
        """
        # حفظ الحالة السابقة
        old_stage = self.employee.current_stage
        old_tracker = self.employee.promotion_tracker
        
        # تحديث المرحلة
        self.employee.current_stage += 1
        
        # تحديث مؤشر التتبع
        tracker_parts = self.employee.promotion_tracker.split('/')
        current_count = int(tracker_parts[0])
        total_count = int(tracker_parts[1])
        
        self.employee.promotion_tracker = f"{current_count + 1}/{total_count}"
        
        # إنشاء سجل في التاريخ الوظيفي
        career_record = CareerHistory(
            employee_id=self.employee.id,
            event_type='allowance',
            event_date=entitlement_date,
            from_grade=self.employee.job_grade,
            to_grade=self.employee.job_grade,
            from_stage=old_stage,
            to_stage=self.employee.current_stage,
            description=f'علاوة سنوية - انتقال من المرحلة {old_stage} إلى المرحلة {self.employee.current_stage}',
            is_automatic=True
        )
        
        db.session.add(career_record)
        
        logger.info(f"تم تنفيذ علاوة للموظف {self.employee.full_name}: {old_stage} -> {self.employee.current_stage}")
        
        return {
            'type': 'allowance',
            'date': entitlement_date,
            'from_stage': old_stage,
            'to_stage': self.employee.current_stage,
            'tracker_change': f"{old_tracker} -> {self.employee.promotion_tracker}"
        }
    
    def _execute_promotion(self, entitlement_date):
        """
        تنفيذ ترفيع وظيفي
        
        Args:
            entitlement_date: تاريخ الترفيع
            
        Returns:
            dict: تفاصيل الترفيع
        """
        # حفظ الحالة السابقة
        old_grade = self.employee.job_grade
        old_stage = self.employee.current_stage
        
        # تحديث الدرجة والمرحلة
        self.employee.job_grade -= 1  # الدرجة تقل بالترفيع
        self.employee.current_stage = 1  # العودة للمرحلة الأولى
        
        # إعادة تعيين مؤشر التتبع
        tracker_parts = self.employee.promotion_tracker.split('/')
        total_count = int(tracker_parts[1])
        self.employee.promotion_tracker = f"0/{total_count}"
        
        # تحديث تاريخ آخر ترفيع
        self.employee.last_promotion_date = entitlement_date
        
        # إنشاء سجل في التاريخ الوظيفي
        career_record = CareerHistory(
            employee_id=self.employee.id,
            event_type='promotion',
            event_date=entitlement_date,
            from_grade=old_grade,
            to_grade=self.employee.job_grade,
            from_stage=old_stage,
            to_stage=self.employee.current_stage,
            description=f'ترفيع وظيفي - انتقال من الدرجة {old_grade} إلى الدرجة {self.employee.job_grade}',
            is_automatic=True
        )
        
        db.session.add(career_record)
        
        logger.info(f"تم تنفيذ ترفيع للموظف {self.employee.full_name}: الدرجة {old_grade} -> {self.employee.job_grade}")
        
        return {
            'type': 'promotion',
            'date': entitlement_date,
            'from_grade': old_grade,
            'to_grade': self.employee.job_grade,
            'tracker_reset': self.employee.promotion_tracker
        }
    
    def _get_penalty_months(self, penalty_type):
        """
        الحصول على عدد الشهور المضافة للعقوبة
        
        Args:
            penalty_type: نوع العقوبة
            
        Returns:
            int: عدد الشهور
        """
        penalty_months = {
            'notice_penalty': 3,      # لفت نظر
            'warning_penalty': 6,     # إنذار
            'reprimand_penalty': 12   # توبيخ
        }
        
        return penalty_months.get(penalty_type, 0)
    
    def get_next_entitlement(self):
        """
        الحصول على تفاصيل الاستحقاق القادم
        
        Returns:
            dict: تفاصيل الاستحقاق القادم
        """
        # حساب تاريخ الاستحقاق القادم
        next_date = self._calculate_next_entitlement_date(self.employee.last_allowance_date)
        
        # تحديد نوع الاستحقاق
        entitlement_type = self.employee.get_next_entitlement_type()
        
        # تحديد التفاصيل المستقبلية
        if entitlement_type == 'allowance':
            next_stage = self.employee.current_stage + 1
            next_grade = self.employee.job_grade
        else:  # promotion
            next_stage = 1
            next_grade = self.employee.job_grade - 1
        
        return {
            'type': entitlement_type,
            'type_arabic': 'علاوة سنوية' if entitlement_type == 'allowance' else 'ترفيع وظيفي',
            'date': next_date,
            'current_grade': self.employee.job_grade,
            'current_stage': self.employee.current_stage,
            'next_grade': next_grade,
            'next_stage': next_stage,
            'days_remaining': (next_date - self.current_date).days,
            'is_overdue': next_date <= self.current_date
        }
    
    def validate_commendation_limits(self, employee_id, year, reduction_months):
        """
        التحقق من قيود كتب الشكر السنوية
        
        Args:
            employee_id: معرف الموظف
            year: السنة
            reduction_months: مدة التقليص المطلوبة
            
        Returns:
            dict: نتيجة التحقق
        """
        # جلب كتب الشكر في السنة المحددة
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        
        commendations = ProfessionalEvent.query.filter(
            and_(
                ProfessionalEvent.employee_id == employee_id,
                ProfessionalEvent.event_type == 'commendation_letter',
                ProfessionalEvent.event_date >= year_start,
                ProfessionalEvent.event_date <= year_end
            )
        ).all()
        
        # حساب الإحصائيات
        total_commendations = len(commendations)
        six_month_commendations = len([c for c in commendations if c.impact_months == 6])
        
        # التحقق من القيود
        validation_result = {
            'is_valid': True,
            'message': '',
            'current_count': total_commendations,
            'six_month_count': six_month_commendations
        }
        
        # القيد السنوي: لا أكثر من 3 كتب شكر عادية
        if reduction_months < 6 and total_commendations >= 3:
            validation_result['is_valid'] = False
            validation_result['message'] = f'تم الوصول للحد الأقصى من كتب الشكر العادية في عام {year} (3 كتب)'
        
        # القيد السنوي: يمكن إضافة كتاب رابع إذا كان 6 أشهر
        elif reduction_months == 6 and total_commendations >= 4:
            validation_result['is_valid'] = False
            validation_result['message'] = f'تم الوصول للحد الأقصى من كتب الشكر في عام {year} (4 كتب)'
        
        # القيد الوظيفي: لا أكثر من كتابين بـ 6 أشهر طوال المسيرة
        if reduction_months == 6:
            lifetime_six_month = ProfessionalEvent.query.filter(
                and_(
                    ProfessionalEvent.employee_id == employee_id,
                    ProfessionalEvent.event_type == 'commendation_letter',
                    ProfessionalEvent.impact_months == 6
                )
            ).count()
            
            if lifetime_six_month >= 2:
                validation_result['is_valid'] = False
                validation_result['message'] = 'تم الوصول للحد الأقصى من كتب الشكر بـ 6 أشهر طوال المسيرة الوظيفية (2 كتب)'
        
        return validation_result
    
    def recalculate_from_scratch(self):
        """
        إعادة حساب كامل للمسار الوظيفي من البداية
        يستخدم عند إضافة أحداث مهنية بتواريخ قديمة
        """
        logger.info(f"بدء إعادة الحساب الكامل للموظف: {self.employee.full_name}")
        
        # حذف السجل الوظيفي التلقائي السابق
        CareerHistory.query.filter(
            and_(
                CareerHistory.employee_id == self.employee.id,
                CareerHistory.is_automatic == True
            )
        ).delete()
        
        # إعادة تعيين الحالة للبداية
        # (يجب الاحتفاظ بالبيانات الأساسية كما أدخلها المستخدم)
        
        # تشغيل المحرك من جديد
        results = self.process_all_entitlements()
        
        logger.info(f"انتهت إعادة الحساب الكامل للموظف: {self.employee.full_name}")
        return results
