#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات المحسّنة
Enhanced Database Models for Employee Management System

تم تطوير هذه النماذج لتدعم جميع المتطلبات المحددة:
- إدارة شاملة للموظفين
- تتبع دقيق للعلاوات والترفيعات
- إدارة الأحداث المهنية المعقدة
- دعم مؤشرات التتبع المختلفة
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

db = SQLAlchemy()

class EmployeeStatus(enum.Enum):
    """حالات الموظف"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"
    ON_LEAVE = "on_leave"

class EventType(enum.Enum):
    """أنواع الأحداث المهنية"""
    COMMENDATION = "commendation"  # كتاب شكر
    HIGHER_DEGREE = "higher_degree"  # شهادة أعلى
    NOTICE_PENALTY = "notice_penalty"  # عقوبة لفت نظر
    WARNING_PENALTY = "warning_penalty"  # عقوبة إنذار
    REPRIMAND_PENALTY = "reprimand_penalty"  # عقوبة توبيخ
    UNPAID_LEAVE = "unpaid_leave"  # إجازة بدون راتب
    DISABILITY_CARE_LEAVE = "disability_care_leave"  # إجازة رعاية المعاقين
    FIVE_YEAR_LEAVE = "five_year_leave"  # إجازة الخمس سنوات
    MATERNITY_LEAVE = "maternity_leave"  # إجازة أمومة
    CUSTOM_EVENT = "custom_event"  # حدث مخصص

class CareerEventType(enum.Enum):
    """أنواع أحداث المسار الوظيفي"""
    ALLOWANCE = "allowance"  # علاوة
    PROMOTION = "promotion"  # ترفيع
    INITIAL_APPOINTMENT = "initial_appointment"  # تعيين أولي

class Employee(db.Model):
    """نموذج الموظف المحسّن"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    
    # البيانات الأساسية - Basic Information
    full_name = Column(String(200), nullable=False, index=True, comment="الاسم الرباعي واللقب")
    photo_path = Column(String(500), nullable=True, comment="مسار صورة الموظف")
    
    # التواريخ المهمة - Important Dates
    start_date = Column(Date, nullable=False, index=True, comment="تاريخ المباشرة بالوظيفة")
    last_allowance_date = Column(Date, nullable=False, comment="تاريخ آخر استحقاق للعلاوة")
    last_promotion_date = Column(Date, nullable=True, comment="آخر تاريخ استحقاق للترفيع")
    
    # مؤشر تتبع الترفيع - Promotion Tracker
    promotion_tracker = Column(String(10), nullable=False, default='0/4', comment="مؤشر تتبع العلاوة")
    
    # المؤهلات والوظيفة - Qualifications and Job
    academic_degree = Column(String(100), nullable=False, comment="الشهادة العلمية")
    job_class = Column(String(100), nullable=False, index=True, comment="صنف الوظيفة")
    job_title = Column(String(200), nullable=False, comment="العنوان الوظيفي")
    job_grade = Column(Integer, nullable=False, comment="الدرجة الوظيفية")
    current_stage = Column(Integer, nullable=False, default=1, comment="المرحلة الحالية")
    
    # الحالة - Status
    status = Column(Enum(EmployeeStatus), nullable=False, default=EmployeeStatus.ACTIVE, comment="حالة الموظف")
    
    # معلومات إضافية - Additional Information
    notes = Column(Text, nullable=True, comment="ملاحظات")
    
    # التواريخ التقنية - Technical Dates
    created_at = Column(DateTime, default=datetime.utcnow, comment="تاريخ الإنشاء")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="تاريخ آخر تحديث")
    
    # العلاقات - Relationships
    professional_events = relationship('ProfessionalEvent', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    career_history = relationship('CareerHistory', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.full_name}>'
    
    @property
    def effective_service_years(self):
        """حساب سنوات الخدمة الفعلية"""
        from backend.enhanced_calculation_engine import EnhancedCalculationEngine
        engine = EnhancedCalculationEngine(self)
        return engine.calculate_effective_service()
    
    @property
    def next_entitlement(self):
        """الاستحقاق القادم"""
        from backend.enhanced_calculation_engine import EnhancedCalculationEngine
        engine = EnhancedCalculationEngine(self)
        return engine.get_next_entitlement()
    
    @property
    def current_grade_stage(self):
        """الدرجة والمرحلة الحالية"""
        return f"الدرجة {self.job_grade} - المرحلة {self.current_stage}"

class ProfessionalEvent(db.Model):
    """نموذج الأحداث المهنية المحسّن"""
    __tablename__ = 'professional_events'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True)
    
    # معلومات الحدث - Event Information
    event_type = Column(Enum(EventType), nullable=False, comment="نوع الحدث")
    event_date = Column(Date, nullable=False, index=True, comment="تاريخ الحدث")
    
    # معلومات الكتاب الرسمي - Official Document Information
    document_number = Column(String(100), nullable=True, comment="رقم الكتاب الرسمي")
    document_date = Column(Date, nullable=True, comment="تاريخ الكتاب الرسمي")
    
    # تفاصيل التأثير - Impact Details
    impact_months = Column(Integer, nullable=True, comment="تأثير الحدث بالأشهر (+ أو -)")
    reduction_months = Column(Integer, nullable=True, comment="مدة التقليص للأحداث الإيجابية")
    
    # تفاصيل الإجازات - Leave Details
    leave_start_date = Column(Date, nullable=True, comment="تاريخ الانفكاك للإجازات")
    leave_end_date = Column(Date, nullable=True, comment="تاريخ المباشرة للإجازات")
    
    # معلومات إضافية - Additional Information
    notes = Column(Text, nullable=True, comment="ملاحظات")
    description = Column(Text, nullable=True, comment="وصف تفصيلي للحدث")
    
    # معلومات التحديث للشهادات - Update Information for Degrees
    new_job_class = Column(String(100), nullable=True, comment="الصنف الوظيفي الجديد")
    new_job_title = Column(String(200), nullable=True, comment="العنوان الوظيفي الجديد")
    new_academic_degree = Column(String(100), nullable=True, comment="الشهادة العلمية الجديدة")
    
    # التواريخ التقنية - Technical Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProfessionalEvent {self.event_type.value} for {self.employee.full_name}>'
    
    @property
    def event_type_arabic(self):
        """ترجمة نوع الحدث للعربية"""
        translations = {
            EventType.COMMENDATION: "كتاب شكر وتقدير",
            EventType.HIGHER_DEGREE: "الحصول على شهادة أعلى",
            EventType.NOTICE_PENALTY: "عقوبة لفت نظر",
            EventType.WARNING_PENALTY: "عقوبة إنذار",
            EventType.REPRIMAND_PENALTY: "عقوبة توبيخ",
            EventType.UNPAID_LEAVE: "إجازة بدون راتب",
            EventType.DISABILITY_CARE_LEAVE: "إجازة رعاية المعاقين",
            EventType.FIVE_YEAR_LEAVE: "إجازة الخمس سنوات",
            EventType.MATERNITY_LEAVE: "إجازة أمومة",
            EventType.CUSTOM_EVENT: "حدث مخصص"
        }
        return translations.get(self.event_type, self.event_type.value)

class CareerHistory(db.Model):
    """نموذج المسار الوظيفي المحسّن"""
    __tablename__ = 'career_history'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True)
    
    # معلومات الحدث الوظيفي - Career Event Information
    event_type = Column(Enum(CareerEventType), nullable=False, comment="نوع الحدث الوظيفي")
    event_date = Column(Date, nullable=False, index=True, comment="تاريخ الحدث")
    
    # معلومات الدرجة والمرحلة - Grade and Stage Information
    from_grade = Column(Integer, nullable=True, comment="من الدرجة")
    to_grade = Column(Integer, nullable=True, comment="إلى الدرجة")
    from_stage = Column(Integer, nullable=True, comment="من المرحلة")
    to_stage = Column(Integer, nullable=True, comment="إلى المرحلة")
    
    # معلومات مؤشر التتبع - Tracker Information
    tracker_before = Column(String(10), nullable=True, comment="مؤشر التتبع قبل الحدث")
    tracker_after = Column(String(10), nullable=True, comment="مؤشر التتبع بعد الحدث")
    
    # وصف الحدث - Event Description
    description = Column(Text, nullable=True, comment="وصف الحدث")
    
    # معلومات إضافية - Additional Information
    is_automatic = Column(Boolean, default=True, comment="هل الحدث تلقائي")
    notes = Column(Text, nullable=True, comment="ملاحظات")
    
    # التواريخ التقنية - Technical Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CareerHistory {self.event_type.value} for {self.employee.full_name}>'
    
    @property
    def event_type_arabic(self):
        """ترجمة نوع الحدث للعربية"""
        translations = {
            CareerEventType.ALLOWANCE: "علاوة سنوية",
            CareerEventType.PROMOTION: "ترفيع",
            CareerEventType.INITIAL_APPOINTMENT: "تعيين أولي"
        }
        return translations.get(self.event_type, self.event_type.value)
    
    @property
    def change_description(self):
        """وصف التغيير"""
        if self.event_type == CareerEventType.ALLOWANCE:
            return f"انتقل من المرحلة {self.from_stage} إلى المرحلة {self.to_stage}"
        elif self.event_type == CareerEventType.PROMOTION:
            return f"تم ترفيعه من الدرجة {self.from_grade} إلى الدرجة {self.to_grade}"
        else:
            return self.description or "حدث وظيفي"

class SystemSettings(db.Model):
    """إعدادات النظام"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), nullable=False, unique=True, comment="مفتاح الإعداد")
    setting_value = Column(Text, nullable=True, comment="قيمة الإعداد")
    setting_type = Column(String(50), nullable=False, default='string', comment="نوع الإعداد")
    description = Column(Text, nullable=True, comment="وصف الإعداد")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.setting_key}>'

# دوال مساعدة لإنشاء الجداول
def create_tables(app):
    """إنشاء جميع الجداول"""
    with app.app_context():
        db.create_all()
        print("تم إنشاء جميع الجداول بنجاح!")

def init_default_settings(app):
    """تهيئة الإعدادات الافتراضية"""
    with app.app_context():
        default_settings = [
            ('base_entitlement_months', '12', 'integer', 'المدة الأساسية للاستحقاق بالأشهر'),
            ('max_commendations_per_year', '3', 'integer', 'الحد الأقصى لكتب الشكر سنوياً'),
            ('max_six_month_commendations', '2', 'integer', 'الحد الأقصى لكتب الشكر 6 أشهر طوال المسيرة'),
            ('system_name', 'نظام إدارة العلاوات والترفيعات', 'string', 'اسم النظام'),
            ('organization_name', 'المؤسسة التعليمية', 'string', 'اسم المؤسسة')
        ]
        
        for key, value, type_val, desc in default_settings:
            existing = SystemSettings.query.filter_by(setting_key=key).first()
            if not existing:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    setting_type=type_val,
                    description=desc
                )
                db.session.add(setting)
        
        db.session.commit()
        print("تم تهيئة الإعدادات الافتراضية!")

