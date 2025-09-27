#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج الموظف
Employee Model

يحتوي على فئة الموظف وجميع العمليات المتعلقة بها
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Employee:
    """
    فئة الموظف
    تحتوي على جميع بيانات الموظف
    """
    id: Optional[int] = None
    full_name: str = ""
    start_date: date = None
    last_allowance_date: date = None
    last_promotion_date: date = None
    promotion_tracker: str = "0/4"  # مؤشر تتبع الترفيع
    academic_degree: str = ""
    job_class: str = ""
    job_title: str = ""
    job_grade: int = 10
    job_stage: int = 1
    photo_path: str = ""
    status: str = "active"
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """
        تهيئة إضافية بعد إنشاء الكائن
        """
        if self.start_date is None:
            self.start_date = date.today()
        if self.last_allowance_date is None:
            self.last_allowance_date = self.start_date
        if self.last_promotion_date is None:
            self.last_promotion_date = self.start_date
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الكائن إلى قاموس
        
        Returns:
            قاموس يحتوي على بيانات الموظف
        """
        return {
            'id': self.id,
            'full_name': self.full_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'last_allowance_date': self.last_allowance_date.isoformat() if self.last_allowance_date else None,
            'last_promotion_date': self.last_promotion_date.isoformat() if self.last_promotion_date else None,
            'promotion_tracker': self.promotion_tracker,
            'academic_degree': self.academic_degree,
            'job_class': self.job_class,
            'job_title': self.job_title,
            'job_grade': self.job_grade,
            'job_stage': self.job_stage,
            'photo_path': self.photo_path,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        """
        إنشاء كائن موظف من قاموس
        
        Args:
            data: قاموس البيانات
            
        Returns:
            كائن الموظف
        """
        employee = cls()
        
        for key, value in data.items():
            if hasattr(employee, key):
                if key in ['start_date', 'last_allowance_date', 'last_promotion_date'] and value:
                    if isinstance(value, str):
                        setattr(employee, key, datetime.fromisoformat(value).date())
                    else:
                        setattr(employee, key, value)
                elif key in ['created_at', 'updated_at'] and value:
                    if isinstance(value, str):
                        setattr(employee, key, datetime.fromisoformat(value))
                    else:
                        setattr(employee, key, value)
                else:
                    setattr(employee, key, value)
        
        return employee
    
    def get_promotion_tracker_parts(self) -> tuple:
        """
        تحليل مؤشر تتبع الترفيع
        
        Returns:
            tuple: (العدد الحالي، العدد الإجمالي)
        """
        try:
            parts = self.promotion_tracker.split('/')
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return 0, 4
    
    def update_promotion_tracker(self, current: int, total: int):
        """
        تحديث مؤشر تتبع الترفيع
        
        Args:
            current: العدد الحالي
            total: العدد الإجمالي
        """
        self.promotion_tracker = f"{current}/{total}"
    
    def is_ready_for_promotion(self) -> bool:
        """
        التحقق من استعداد الموظف للترفيع
        
        Returns:
            True إذا كان مستعداً للترفيع
        """
        current, total = self.get_promotion_tracker_parts()
        return current >= total - 1
    
    def get_next_event_type(self) -> str:
        """
        تحديد نوع الحدث القادم (علاوة أو ترفيع)
        
        Returns:
            نوع الحدث القادم
        """
        if self.is_ready_for_promotion():
            return "ترفيع"
        else:
            return "علاوة"
    
    def calculate_service_years(self) -> tuple:
        """
        حساب سنوات الخدمة الفعلية
        
        Returns:
            tuple: (السنوات، الأشهر، الأيام)
        """
        if not self.start_date:
            return 0, 0, 0
        
        today = date.today()
        years = today.year - self.start_date.year
        months = today.month - self.start_date.month
        days = today.day - self.start_date.day
        
        if days < 0:
            months -= 1
            # حساب عدد أيام الشهر السابق
            if today.month == 1:
                prev_month = 12
                prev_year = today.year - 1
            else:
                prev_month = today.month - 1
                prev_year = today.year
            
            # تقدير عدد أيام الشهر السابق
            if prev_month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_prev_month = 31
            elif prev_month in [4, 6, 9, 11]:
                days_in_prev_month = 30
            else:  # فبراير
                if prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0):
                    days_in_prev_month = 29
                else:
                    days_in_prev_month = 28
            
            days += days_in_prev_month
        
        if months < 0:
            years -= 1
            months += 12
        
        return years, months, days
    
    def get_display_name(self) -> str:
        """
        الحصول على الاسم للعرض
        
        Returns:
            الاسم مع المنصب
        """
        return f"{self.full_name} - {self.job_title}"
    
    def validate(self) -> List[str]:
        """
        التحقق من صحة بيانات الموظف
        
        Returns:
            قائمة الأخطاء (فارغة إذا كانت البيانات صحيحة)
        """
        errors = []
        
        if not self.full_name or len(self.full_name.strip()) < 2:
            errors.append("اسم الموظف مطلوب ويجب أن يكون أكثر من حرفين")
        
        if not self.start_date:
            errors.append("تاريخ المباشرة مطلوب")
        elif self.start_date > date.today():
            errors.append("تاريخ المباشرة لا يمكن أن يكون في المستقبل")
        
        if not self.academic_degree:
            errors.append("الشهادة العلمية مطلوبة")
        
        if not self.job_class:
            errors.append("صنف الوظيفة مطلوب")
        
        if not self.job_title:
            errors.append("العنوان الوظيفي مطلوب")
        
        if self.job_grade < 1 or self.job_grade > 10:
            errors.append("الدرجة الوظيفية يجب أن تكون بين 1 و 10")
        
        if self.job_stage < 1:
            errors.append("المرحلة الوظيفية يجب أن تكون أكبر من 0")
        
        return errors

class EmployeeFilter:
    """
    فئة مرشح الموظفين
    تستخدم لفلترة قوائم الموظفين
    """
    
    def __init__(self):
        self.job_class: Optional[str] = None
        self.search_name: Optional[str] = None
        self.job_grade: Optional[int] = None
        self.status: str = "active"
        self.sort_by: str = "full_name"
        self.sort_order: str = "ASC"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل المرشح إلى قاموس
        
        Returns:
            قاموس المرشح
        """
        return {
            'job_class': self.job_class,
            'search_name': self.search_name,
            'job_grade': self.job_grade,
            'status': self.status,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order
        }

