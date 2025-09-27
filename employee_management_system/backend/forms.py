#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج الإدخال والتحقق
Forms and Validation for Employee Management System
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DateField, SelectField, IntegerField, TextAreaField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget
from datetime import date, datetime
from backend.models import ProfessionalEvent

class MultiCheckboxField(SelectMultipleField):
    """حقل متعدد الاختيارات مع مربعات تحديد"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class EmployeeForm(FlaskForm):
    """نموذج إضافة/تعديل الموظف"""
    
    # البيانات الأساسية
    full_name = StringField(
        'الاسم الرباعي واللقب',
        validators=[DataRequired(message='الاسم مطلوب'), Length(min=2, max=200, message='الاسم يجب أن يكون بين 2-200 حرف')],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'أدخل الاسم الرباعي واللقب'}
    )
    
    # التواريخ المهمة
    start_date = DateField(
        'تاريخ المباشرة بالوظيفة',
        validators=[DataRequired(message='تاريخ المباشرة مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    last_allowance_date = DateField(
        'تاريخ آخر استحقاق للعلاوة',
        validators=[DataRequired(message='تاريخ آخر استحقاق مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    last_promotion_date = DateField(
        'آخر تاريخ استحقاق للترفيع',
        validators=[Optional()],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    # مؤشر تتبع العلاوة
    promotion_tracker = SelectField(
        'مؤشر تتبع العلاوة',
        choices=[
            ('0/4', '0/4'), ('1/4', '1/4'), ('2/4', '2/4'), ('3/4', '3/4'),
            ('0/5', '0/5'), ('1/5', '1/5'), ('2/5', '2/5'), ('3/5', '3/5'), ('4/5', '4/5')
        ],
        validators=[DataRequired(message='مؤشر التتبع مطلوب')],
        render_kw={'class': 'form-select form-select-lg'}
    )
    
    # المؤهلات والوظيفة
    academic_degree = StringField(
        'الشهادة العلمية',
        validators=[DataRequired(message='الشهادة العلمية مطلوبة'), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'مثل: بكالوريوس، دبلوم، ماجستير'}
    )
    
    job_class = StringField(
        'صنف الوظيفة',
        validators=[DataRequired(message='صنف الوظيفة مطلوب'), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'مثل: تدريسي، إداري، فني'}
    )
    
    job_title = StringField(
        'العنوان الوظيفي',
        validators=[DataRequired(message='العنوان الوظيفي مطلوب'), Length(max=200)],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'مثل: مدرس، محاسب، مهندس'}
    )
    
    job_grade = IntegerField(
        'الدرجة الوظيفية',
        validators=[DataRequired(message='الدرجة الوظيفية مطلوبة'), NumberRange(min=1, max=15, message='الدرجة يجب أن تكون بين 1-15')],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'أدخل رقم الدرجة'}
    )
    
    # صورة الموظف
    photo = FileField(
        'صورة الموظف',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'الصور فقط!')],
        render_kw={'class': 'form-control form-control-lg', 'accept': 'image/*'}
    )
    
    def validate_start_date(self, field):
        """التحقق من صحة تاريخ المباشرة"""
        if field.data and field.data > date.today():
            raise ValidationError('تاريخ المباشرة لا يمكن أن يكون في المستقبل')
    
    def validate_last_allowance_date(self, field):
        """التحقق من صحة تاريخ آخر استحقاق"""
        if field.data and self.start_date.data:
            if field.data < self.start_date.data:
                raise ValidationError('تاريخ آخر استحقاق لا يمكن أن يكون قبل تاريخ المباشرة')

class EventForm(FlaskForm):
    """نموذج إضافة حدث مهني"""
    
    # نوع الحدث
    event_type = SelectField(
        'نوع الحدث',
        choices=[
            ('', 'اختر نوع الحدث'),
            # الأحداث الإيجابية
            ('commendation_letter', 'كتاب شكر وتقدير'),
            ('higher_degree', 'الحصول على شهادة أعلى'),
            # الأحداث السلبية
            ('notice_penalty', 'عقوبة لفت نظر'),
            ('warning_penalty', 'عقوبة إنذار'),
            ('reprimand_penalty', 'عقوبة توبيخ'),
            # أحداث تجميد الخدمة
            ('unpaid_leave', 'إجازة بدون راتب'),
            ('disability_care_leave', 'إجازة رعاية المعاقين'),
            ('five_year_leave', 'إجازة الخمس سنوات'),
            ('maternity_leave', 'إجازة أمومة'),
            # حدث مخصص
            ('custom_event', 'حدث مخصص')
        ],
        validators=[DataRequired(message='نوع الحدث مطلوب')],
        render_kw={'class': 'form-select form-select-lg', 'onchange': 'updateEventFields()'}
    )
    
    # تاريخ الحدث
    event_date = DateField(
        'تاريخ الحدث',
        validators=[DataRequired(message='تاريخ الحدث مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    # الوثائق الرسمية
    document_number = StringField(
        'رقم الكتاب الرسمي',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'رقم الكتاب أو القرار'}
    )
    
    document_date = DateField(
        'تاريخ الكتاب الرسمي',
        validators=[Optional()],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    # التأثير على المدة (لكتب الشكر والأحداث المخصصة)
    impact_months = IntegerField(
        'مدة التأثير (بالشهور)',
        validators=[Optional(), NumberRange(min=-24, max=24, message='المدة يجب أن تكون بين -24 و 24 شهر')],
        render_kw={'class': 'form-control form-control-lg', 'placeholder': 'موجب للإضافة، سالب للتقليص'}
    )
    
    # تواريخ الإجازات (للإجازات الطويلة)
    start_date = DateField(
        'تاريخ الانفكاك',
        validators=[Optional()],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    end_date = DateField(
        'تاريخ المباشرة',
        validators=[Optional()],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    # الوصف والملاحظات
    description = TextAreaField(
        'وصف الحدث',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف تفصيلي للحدث'}
    )
    
    notes = TextAreaField(
        'ملاحظات',
        validators=[Optional(), Length(max=1000)],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'ملاحظات إضافية'}
    )
    
    # معلومات إضافية للشهادات
    new_job_class = StringField(
        'صنف الموظف الجديد',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    new_job_title = StringField(
        'العنوان الوظيفي الجديد',
        validators=[Optional(), Length(max=200)],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    new_academic_degree = StringField(
        'الشهادة العلمية الجديدة',
        validators=[Optional(), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    def validate_event_date(self, field):
        """التحقق من صحة تاريخ الحدث"""
        if field.data and field.data > date.today():
            raise ValidationError('تاريخ الحدث لا يمكن أن يكون في المستقبل')
    
    def validate_start_date(self, field):
        """التحقق من تاريخ الانفكاك"""
        if field.data and self.end_date.data:
            if field.data >= self.end_date.data:
                raise ValidationError('تاريخ الانفكاك يجب أن يكون قبل تاريخ المباشرة')
    
    def validate_impact_months(self, field):
        """التحقق من مدة التأثير حسب نوع الحدث"""
        if self.event_type.data == 'commendation_letter' and field.data:
            if field.data not in [-6, -5, -4, -3, -2, -1]:
                raise ValidationError('مدة تقليص كتاب الشكر يجب أن تكون بين 1-6 أشهر')
        
        elif self.event_type.data == 'custom_event' and not field.data:
            raise ValidationError('مدة التأثير مطلوبة للأحداث المخصصة')

class CommendationForm(FlaskForm):
    """نموذج خاص لكتب الشكر مع التحقق من القيود"""
    
    # الحقول الأساسية
    event_date = DateField(
        'تاريخ كتاب الشكر',
        validators=[DataRequired(message='تاريخ كتاب الشكر مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    document_number = StringField(
        'رقم كتاب الشكر',
        validators=[DataRequired(message='رقم كتاب الشكر مطلوب'), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    document_date = DateField(
        'تاريخ كتاب الشكر الرسمي',
        validators=[DataRequired(message='تاريخ الكتاب الرسمي مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    # مدة التقليص
    reduction_months = SelectField(
        'مدة التقليص',
        choices=[
            ('1', '1 شهر'),
            ('2', '2 شهر'),
            ('3', '3 أشهر'),
            ('4', '4 أشهر'),
            ('5', '5 أشهر'),
            ('6', '6 أشهر')
        ],
        validators=[DataRequired(message='مدة التقليص مطلوبة')],
        render_kw={'class': 'form-select form-select-lg'}
    )
    
    description = TextAreaField(
        'سبب كتاب الشكر',
        validators=[DataRequired(message='سبب كتاب الشكر مطلوب'), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': 3}
    )
    
    notes = TextAreaField(
        'ملاحظات إضافية',
        validators=[Optional(), Length(max=1000)],
        render_kw={'class': 'form-control', 'rows': 2}
    )

class LeaveForm(FlaskForm):
    """نموذج خاص للإجازات الطويلة"""
    
    leave_type = SelectField(
        'نوع الإجازة',
        choices=[
            ('unpaid_leave', 'إجازة بدون راتب'),
            ('disability_care_leave', 'إجازة رعاية المعاقين'),
            ('five_year_leave', 'إجازة الخمس سنوات'),
            ('maternity_leave', 'إجازة أمومة')
        ],
        validators=[DataRequired(message='نوع الإجازة مطلوب')],
        render_kw={'class': 'form-select form-select-lg'}
    )
    
    document_number = StringField(
        'رقم قرار الإجازة',
        validators=[DataRequired(message='رقم قرار الإجازة مطلوب'), Length(max=100)],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    document_date = DateField(
        'تاريخ قرار الإجازة',
        validators=[DataRequired(message='تاريخ قرار الإجازة مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    start_date = DateField(
        'تاريخ الانفكاك',
        validators=[DataRequired(message='تاريخ الانفكاك مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    end_date = DateField(
        'تاريخ المباشرة',
        validators=[DataRequired(message='تاريخ المباشرة مطلوب')],
        render_kw={'class': 'form-control form-control-lg'}
    )
    
    description = TextAreaField(
        'تفاصيل الإجازة',
        validators=[Optional(), Length(max=500)],
        render_kw={'class': 'form-control', 'rows': 3}
    )
    
    def validate_start_date(self, field):
        """التحقق من تاريخ الانفكاك"""
        if field.data and self.end_date.data:
            if field.data >= self.end_date.data:
                raise ValidationError('تاريخ الانفكاك يجب أن يكون قبل تاريخ المباشرة')
        
        if field.data and field.data > date.today():
            raise ValidationError('تاريخ الانفكاك لا يمكن أن يكون في المستقبل')

class SearchForm(FlaskForm):
    """نموذج البحث والفلترة"""
    
    search_query = StringField(
        'البحث',
        validators=[Optional(), Length(max=200)],
        render_kw={'class': 'form-control', 'placeholder': 'ابحث عن موظف...'}
    )
    
    job_class_filter = SelectField(
        'فلترة حسب الصنف',
        choices=[('', 'جميع الأصناف')],  # سيتم ملؤها ديناميكياً
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    sort_by = SelectField(
        'ترتيب حسب',
        choices=[
            ('name', 'الاسم'),
            ('start_date', 'تاريخ المباشرة'),
            ('job_class', 'الصنف الوظيفي'),
            ('job_grade', 'الدرجة الوظيفية')
        ],
        default='name',
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    status_filter = SelectField(
        'فلترة حسب الحالة',
        choices=[
            ('', 'جميع الحالات'),
            ('active', 'نشط'),
            ('inactive', 'غير نشط'),
            ('retired', 'متقاعد')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
