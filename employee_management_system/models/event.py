#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج الأحداث المهنية
Professional Events Model

يحتوي على فئات الأحداث المهنية وأنواعها المختلفة
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """
    أنواع الأحداث المهنية
    """
    COMMENDATION = "كتاب شكر وتقدير"
    HIGHER_DEGREE = "الحصول على شهادة أعلى"
    NOTICE_PENALTY = "عقوبة لفت نظر"
    WARNING_PENALTY = "عقوبة إنذار"
    REPRIMAND_PENALTY = "عقوبة توبيخ"
    UNPAID_LEAVE = "إجازة بدون راتب"
    DISABILITY_CARE_LEAVE = "إجازة رعاية المعاقين"
    FIVE_YEAR_LEAVE = "إجازة الخمس سنوات"
    MATERNITY_LEAVE = "إجازة أمومة"
    CUSTOM_EVENT = "حدث مخصص"

class EffectType(Enum):
    """
    أنواع التأثير على المدة الزمنية
    """
    NONE = "none"  # لا يوجد تأثير
    REDUCE = "reduce"  # تقليص المدة
    INCREASE = "increase"  # زيادة المدة
    FREEZE = "freeze"  # تجميد المدة

@dataclass
class ProfessionalEvent:
    """
    فئة الحدث المهني
    """
    id: Optional[int] = None
    employee_id: int = 0
    event_type: str = ""
    event_date: date = None
    document_number: str = ""
    document_date: Optional[date] = None
    description: str = ""
    effect_months: int = 0
    effect_type: str = EffectType.NONE.value
    start_date: Optional[date] = None  # للإجازات
    end_date: Optional[date] = None    # للإجازات
    notes: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        """
        تهيئة إضافية بعد إنشاء الكائن
        """
        if self.event_date is None:
            self.event_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الكائن إلى قاموس
        
        Returns:
            قاموس يحتوي على بيانات الحدث
        """
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'event_type': self.event_type,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'document_number': self.document_number,
            'document_date': self.document_date.isoformat() if self.document_date else None,
            'description': self.description,
            'effect_months': self.effect_months,
            'effect_type': self.effect_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfessionalEvent':
        """
        إنشاء كائن حدث من قاموس
        
        Args:
            data: قاموس البيانات
            
        Returns:
            كائن الحدث
        """
        event = cls()
        
        for key, value in data.items():
            if hasattr(event, key):
                if key in ['event_date', 'document_date', 'start_date', 'end_date'] and value:
                    if isinstance(value, str):
                        setattr(event, key, datetime.fromisoformat(value).date())
                    else:
                        setattr(event, key, value)
                elif key == 'created_at' and value:
                    if isinstance(value, str):
                        setattr(event, key, datetime.fromisoformat(value))
                    else:
                        setattr(event, key, value)
                else:
                    setattr(event, key, value)
        
        return event
    
    def get_effect_description(self) -> str:
        """
        الحصول على وصف التأثير
        
        Returns:
            وصف التأثير
        """
        if self.effect_type == EffectType.REDUCE.value:
            return f"تقليص {self.effect_months} شهر"
        elif self.effect_type == EffectType.INCREASE.value:
            return f"زيادة {self.effect_months} شهر"
        elif self.effect_type == EffectType.FREEZE.value:
            if self.start_date and self.end_date:
                days = (self.end_date - self.start_date).days
                return f"تجميد {days} يوم"
            return "تجميد المدة"
        else:
            return "لا يوجد تأثير"
    
    def validate(self) -> List[str]:
        """
        التحقق من صحة بيانات الحدث
        
        Returns:
            قائمة الأخطاء
        """
        errors = []
        
        if self.employee_id <= 0:
            errors.append("معرف الموظف مطلوب")
        
        if not self.event_type:
            errors.append("نوع الحدث مطلوب")
        
        if not self.event_date:
            errors.append("تاريخ الحدث مطلوب")
        elif self.event_date > date.today():
            errors.append("تاريخ الحدث لا يمكن أن يكون في المستقبل")
        
        # التحقق من الأحداث التي تتطلب تواريخ إضافية
        freeze_events = [
            EventType.UNPAID_LEAVE.value,
            EventType.DISABILITY_CARE_LEAVE.value,
            EventType.FIVE_YEAR_LEAVE.value,
            EventType.MATERNITY_LEAVE.value
        ]
        
        if self.event_type in freeze_events:
            if not self.start_date:
                errors.append("تاريخ الانفكاك مطلوب لهذا النوع من الأحداث")
            if not self.end_date:
                errors.append("تاريخ المباشرة مطلوب لهذا النوع من الأحداث")
            if self.start_date and self.end_date and self.start_date >= self.end_date:
                errors.append("تاريخ المباشرة يجب أن يكون بعد تاريخ الانفكاك")
        
        return errors

@dataclass
class CareerEvent:
    """
    فئة حدث المسار الوظيفي (علاوة أو ترفيع)
    """
    id: Optional[int] = None
    employee_id: int = 0
    event_type: str = ""  # "علاوة" أو "ترفيع"
    event_date: date = None
    from_grade: Optional[int] = None
    to_grade: Optional[int] = None
    from_stage: Optional[int] = None
    to_stage: Optional[int] = None
    description: str = ""
    is_automatic: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        """
        تهيئة إضافية بعد إنشاء الكائن
        """
        if self.event_date is None:
            self.event_date = date.today()
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تحويل الكائن إلى قاموس
        
        Returns:
            قاموس يحتوي على بيانات الحدث
        """
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'event_type': self.event_type,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'from_grade': self.from_grade,
            'to_grade': self.to_grade,
            'from_stage': self.from_stage,
            'to_stage': self.to_stage,
            'description': self.description,
            'is_automatic': self.is_automatic
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CareerEvent':
        """
        إنشاء كائن حدث مسار وظيفي من قاموس
        
        Args:
            data: قاموس البيانات
            
        Returns:
            كائن الحدث
        """
        event = cls()
        
        for key, value in data.items():
            if hasattr(event, key):
                if key == 'event_date' and value:
                    if isinstance(value, str):
                        setattr(event, key, datetime.fromisoformat(value).date())
                    else:
                        setattr(event, key, value)
                elif key == 'created_at' and value:
                    if isinstance(value, str):
                        setattr(event, key, datetime.fromisoformat(value))
                    else:
                        setattr(event, key, value)
                else:
                    setattr(event, key, value)
        
        return event
    
    def get_description(self) -> str:
        """
        الحصول على وصف الحدث
        
        Returns:
            وصف الحدث
        """
        if self.event_type == "علاوة":
            return f"علاوة سنوية - انتقال من المرحلة {self.from_stage} إلى المرحلة {self.to_stage}"
        elif self.event_type == "ترفيع":
            return f"ترفيع - انتقال من الدرجة {self.from_grade} إلى الدرجة {self.to_grade}"
        else:
            return self.description

class EventValidator:
    """
    فئة التحقق من صحة الأحداث وتطبيق القواعد
    """
    
    @staticmethod
    def validate_commendation_limits(employee_id: int, year: int, 
                                   reduction_months: int, 
                                   existing_events: List[ProfessionalEvent]) -> List[str]:
        """
        التحقق من حدود كتب الشكر
        
        Args:
            employee_id: معرف الموظف
            year: السنة
            reduction_months: أشهر التقليص
            existing_events: الأحداث الموجودة
            
        Returns:
            قائمة الأخطاء
        """
        errors = []
        
        # حساب كتب الشكر في نفس السنة
        year_commendations = [
            event for event in existing_events
            if (event.event_type == EventType.COMMENDATION.value and
                event.event_date.year == year)
        ]
        
        # حساب كتب الشكر 6 أشهر في المسيرة الوظيفية
        career_6month_commendations = [
            event for event in existing_events
            if (event.event_type == EventType.COMMENDATION.value and
                event.effect_months == 6)
        ]
        
        # التحقق من القيد السنوي
        if len(year_commendations) >= 3:
            if reduction_months != 6:
                errors.append("تم الوصول للحد الأقصى من كتب الشكر في هذه السنة (3 كتب)")
            elif len(year_commendations) >= 4:
                errors.append("تم الوصول للحد الأقصى من كتب الشكر في هذه السنة (4 كتب مع كتاب 6 أشهر)")
        
        # التحقق من القيد الوظيفي لكتب الشكر 6 أشهر
        if reduction_months == 6 and len(career_6month_commendations) >= 2:
            errors.append("تم الوصول للحد الأقصى من كتب الشكر 6 أشهر في المسيرة الوظيفية (2 كتب)")
        
        return errors
    
    @staticmethod
    def get_event_effect(event_type: str, **kwargs) -> tuple:
        """
        الحصول على تأثير الحدث
        
        Args:
            event_type: نوع الحدث
            **kwargs: معاملات إضافية
            
        Returns:
            tuple: (نوع التأثير، عدد الأشهر)
        """
        if event_type == EventType.COMMENDATION.value:
            reduction_months = kwargs.get('reduction_months', 1)
            return EffectType.REDUCE.value, reduction_months
        
        elif event_type == EventType.HIGHER_DEGREE.value:
            return EffectType.REDUCE.value, 12  # Step كامل
        
        elif event_type == EventType.NOTICE_PENALTY.value:
            return EffectType.INCREASE.value, 3
        
        elif event_type == EventType.WARNING_PENALTY.value:
            return EffectType.INCREASE.value, 6
        
        elif event_type == EventType.REPRIMAND_PENALTY.value:
            return EffectType.INCREASE.value, 12
        
        elif event_type in [
            EventType.UNPAID_LEAVE.value,
            EventType.DISABILITY_CARE_LEAVE.value,
            EventType.FIVE_YEAR_LEAVE.value,
            EventType.MATERNITY_LEAVE.value
        ]:
            return EffectType.FREEZE.value, 0
        
        elif event_type == EventType.CUSTOM_EVENT.value:
            effect_type = kwargs.get('effect_type', EffectType.NONE.value)
            effect_months = kwargs.get('effect_months', 0)
            return effect_type, effect_months
        
        else:
            return EffectType.NONE.value, 0

