#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات
Database Models for Employee Management System
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Employee(db.Model):
    """نموذج الموظف - Employee Model"""
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    
    # البيانات الأساسية - Basic Information
    full_name = Column(String(200), nullable=False, index=True)
    photo_path = Column(String(500), nullable=True)
    
    # التواريخ المهمة - Important Dates
    start_date = Column(Date, nullable=False, index=True)
    last_allowance_date = Column(Date, nullable=False)
    last_promotion_date = Column(Date, nullable=True)
    
    # مؤشر تتبع الترفيع - Promotion Tracker
    promotion_tracker = Column(String(10), nullable=False, default='0/4')  # مثل 3/4 أو 4/5
    
    # المؤهلات والوظيفة - Qualifications and Job
    academic_degree = Column(String(100), nullable=False)
    job_class = Column(String(100), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    job_grade = Column(Integer, nullable=False)
    current_stage = Column(Integer, nullable=False, default=1)
    
    # الحالة - Status
    status = Column(String(20), nullable=False, default='active')  # active, inactive, retired
    
    # التواريخ التقنية - Technical Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات - Relationships
    professional_events = relationship('ProfessionalEvent', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    career_history = relationship('CareerHistory', backref='employee', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.full_name}>'
    
    def get_current_promotion_status(self):
        """الحصول على حالة الترفيع الحالية"""
        parts = self.promotion_tracker.split('/')
        current = int(parts[0])
        total = int(parts[1])
        return {'current': current, 'total': total, 'is_ready_for_promotion': current == total - 1}
    
    def get_next_entitlement_type(self):
        """تحديد نوع الاستحقاق القادم"""
        status = self.get_current_promotion_status()
        if status['is_ready_for_promotion']:
            return 'promotion'
        else:
            return 'allowance'
    
    def is_fast_track_eligible(self):
        """التحقق من أهلية الترفيع السريع"""
        # قاعدة الترفيع السريع للموظفين الجدد بدبلوم على الدرجة 8/5
        return (self.start_date == self.last_allowance_date and 
                'دبلوم' in self.academic_degree and 
                self.job_grade == 8 and 
                self.current_stage == 5)

class ProfessionalEvent(db.Model):
    """نموذج الأحداث المهنية - Professional Events Model"""
    __tablename__ = 'professional_events'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True)
    
    # تفاصيل الحدث - Event Details
    event_type = Column(String(50), nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    
    # الوثائق الرسمية - Official Documents
    document_number = Column(String(100), nullable=True)
    document_date = Column(Date, nullable=True)
    
    # التأثير على المدة - Impact on Duration
    impact_months = Column(Integer, default=0)  # موجب للإضافة، سالب للتقليص
    
    # تواريخ الإجازات - Leave Dates (للإجازات الطويلة)
    start_date = Column(Date, nullable=True)  # تاريخ الانفكاك
    end_date = Column(Date, nullable=True)    # تاريخ المباشرة
    
    # الوصف والملاحظات - Description and Notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # معلومات إضافية للشهادات - Additional Info for Degrees
    new_job_class = Column(String(100), nullable=True)
    new_job_title = Column(String(200), nullable=True)
    new_academic_degree = Column(String(100), nullable=True)
    
    # التواريخ التقنية - Technical Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProfessionalEvent {self.event_type} for {self.employee.full_name}>'
    
    @staticmethod
    def get_event_types():
        """قائمة أنواع الأحداث المهنية"""
        return {
            # الأحداث الإيجابية
            'commendation_letter': 'كتاب شكر وتقدير',
            'higher_degree': 'الحصول على شهادة أعلى',
            
            # الأحداث السلبية
            'notice_penalty': 'عقوبة لفت نظر',
            'warning_penalty': 'عقوبة إنذار',
            'reprimand_penalty': 'عقوبة توبيخ',
            
            # أحداث تجميد الخدمة
            'unpaid_leave': 'إجازة بدون راتب',
            'disability_care_leave': 'إجازة رعاية المعاقين',
            'five_year_leave': 'إجازة الخمس سنوات',
            'maternity_leave': 'إجازة أمومة',
            
            # حدث مخصص
            'custom_event': 'حدث مخصص'
        }
    
    def get_impact_description(self):
        """وصف تأثير الحدث"""
        if self.impact_months > 0:
            return f'إضافة {self.impact_months} شهر للاستحقاق'
        elif self.impact_months < 0:
            return f'تقليص {abs(self.impact_months)} شهر من الاستحقاق'
        elif self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            return f'تجميد الخدمة لمدة {days} يوم'
        else:
            return 'لا يوجد تأثير مباشر'

class CareerHistory(db.Model):
    """نموذج السجل الوظيفي - Career History Model"""
    __tablename__ = 'career_history'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True)
    
    # تفاصيل الحدث - Event Details
    event_type = Column(String(20), nullable=False)  # 'allowance' or 'promotion'
    event_date = Column(Date, nullable=False, index=True)
    
    # التفاصيل الوظيفية - Job Details
    from_grade = Column(Integer, nullable=True)
    to_grade = Column(Integer, nullable=True)
    from_stage = Column(Integer, nullable=True)
    to_stage = Column(Integer, nullable=True)
    
    # الوصف - Description
    description = Column(Text, nullable=True)
    
    # معلومات إضافية - Additional Info
    is_automatic = Column(Boolean, default=True)  # تلقائي أم يدوي
    calculation_date = Column(DateTime, default=datetime.utcnow)  # تاريخ الحساب
    
    def __repr__(self):
        return f'<CareerHistory {self.event_type} for {self.employee.full_name}>'
    
    def get_event_description(self):
        """وصف الحدث الوظيفي"""
        if self.event_type == 'allowance':
            return f'علاوة سنوية - انتقال من المرحلة {self.from_stage} إلى المرحلة {self.to_stage}'
        elif self.event_type == 'promotion':
            return f'ترفيع - انتقال من الدرجة {self.from_grade} إلى الدرجة {self.to_grade}'
        else:
            return self.description or 'حدث وظيفي'

class SystemSettings(db.Model):
    """إعدادات النظام - System Settings Model"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        """الحصول على إعداد"""
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """تعيين إعداد"""
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.session.add(setting)
        return setting

# فهارس إضافية لتحسين الأداء
# Additional indexes for performance optimization
from sqlalchemy import Index

# فهرس مركب للبحث السريع في الموظفين
Index('idx_employee_search', Employee.full_name, Employee.job_class, Employee.status)

# فهرس مركب للأحداث المهنية
Index('idx_professional_events', ProfessionalEvent.employee_id, ProfessionalEvent.event_date, ProfessionalEvent.event_type)

# فهرس مركب للسجل الوظيفي
Index('idx_career_history', CareerHistory.employee_id, CareerHistory.event_date, CareerHistory.event_type)
