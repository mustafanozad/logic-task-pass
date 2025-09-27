#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة العلاوات والترفيعات الوظيفية
Employee Promotion and Allowance Management System

تطبيق شامل لأتمتة وحوسبة العمليات المعقدة المتعلقة بحساب العلاوات السنوية والترفيعات الوظيفية
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images/employees'

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# استيراد النماذج
from backend.models import Employee, ProfessionalEvent, CareerHistory
from backend.calculation_engine import CalculationEngine
from backend.forms import EmployeeForm, EventForm

# إنشاء مجلد الصور إذا لم يكن موجوداً
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(status='active').count()
    
    # إحصائيات سريعة
    stats = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'pending_promotions': 0,  # سيتم حسابها لاحقاً
        'recent_events': ProfessionalEvent.query.order_by(ProfessionalEvent.event_date.desc()).limit(5).all()
    }
    
    return render_template('index.html', stats=stats)

@app.route('/employees')
def employees_list():
    """قائمة الموظفين"""
    # فلترة حسب المعايير
    job_class = request.args.get('job_class', '')
    sort_by = request.args.get('sort_by', 'name')
    search = request.args.get('search', '')
    
    query = Employee.query
    
    if job_class:
        query = query.filter(Employee.job_class.contains(job_class))
    
    if search:
        query = query.filter(Employee.full_name.contains(search))
    
    # ترتيب النتائج
    if sort_by == 'name':
        query = query.order_by(Employee.full_name)
    elif sort_by == 'start_date':
        query = query.order_by(Employee.start_date.desc())
    elif sort_by == 'job_class':
        query = query.order_by(Employee.job_class)
    
    employees = query.all()
    
    # حساب الخدمة الفعلية لكل موظف
    for employee in employees:
        employee.effective_service = calculate_effective_service(employee)
    
    return render_template('employees/list.html', 
                         employees=employees,
                         current_filters={'job_class': job_class, 'sort_by': sort_by, 'search': search})

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    """إضافة موظف جديد"""
    form = EmployeeForm()
    
    if form.validate_on_submit():
        employee = Employee(
            full_name=form.full_name.data,
            start_date=form.start_date.data,
            last_allowance_date=form.last_allowance_date.data,
            last_promotion_date=form.last_promotion_date.data,
            promotion_tracker=form.promotion_tracker.data,
            academic_degree=form.academic_degree.data,
            job_class=form.job_class.data,
            job_title=form.job_title.data,
            job_grade=form.job_grade.data,
            current_stage=1,  # المرحلة الابتدائية
            status='active'
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash('تم إضافة الموظف بنجاح! ✅', 'success')
        return redirect(url_for('employees_list'))
    
    return render_template('employees/add.html', form=form)

@app.route('/employee/<int:employee_id>')
def employee_profile(employee_id):
    """ملف الموظف الشخصي"""
    employee = Employee.query.get_or_404(employee_id)
    
    # تشغيل المحرك الذكي لحساب الاستحقاقات
    engine = CalculationEngine(employee)
    engine.process_all_entitlements()
    
    # تحديث بيانات الموظف
    db.session.commit()
    
    # جلب السجلات التاريخية
    career_history = CareerHistory.query.filter_by(employee_id=employee_id).order_by(CareerHistory.event_date.desc()).all()
    professional_events = ProfessionalEvent.query.filter_by(employee_id=employee_id).order_by(ProfessionalEvent.event_date.desc()).all()
    
    # حساب الاستحقاق القادم
    next_entitlement = engine.get_next_entitlement()
    
    # حساب الخدمة الفعلية
    effective_service = calculate_effective_service(employee)
    
    return render_template('employees/profile.html',
                         employee=employee,
                         career_history=career_history,
                         professional_events=professional_events,
                         next_entitlement=next_entitlement,
                         effective_service=effective_service)

@app.route('/employee/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """تعديل بيانات الموظف"""
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)
    
    if form.validate_on_submit():
        # تحديث البيانات الأساسية
        employee.full_name = form.full_name.data
        employee.job_class = form.job_class.data
        employee.job_title = form.job_title.data
        employee.academic_degree = form.academic_degree.data
        
        db.session.commit()
        flash('تم تحديث بيانات الموظف بنجاح! ✅', 'success')
        return redirect(url_for('employee_profile', employee_id=employee_id))
    
    return render_template('employees/edit.html', form=form, employee=employee)

@app.route('/events')
def events_list():
    """قائمة الأحداث المهنية"""
    events = ProfessionalEvent.query.order_by(ProfessionalEvent.event_date.desc()).all()
    return render_template('events/list.html', events=events)

@app.route('/event/add', methods=['GET', 'POST'])
def add_event():
    """إضافة حدث مهني جديد"""
    form = EventForm()
    
    if form.validate_on_submit():
        # معالجة الموظفين المحددين
        selected_employees = request.form.getlist('selected_employees')
        
        for employee_id in selected_employees:
            event = ProfessionalEvent(
                employee_id=int(employee_id),
                event_type=form.event_type.data,
                event_date=form.event_date.data,
                document_number=form.document_number.data,
                document_date=form.document_date.data,
                description=form.description.data,
                impact_months=form.impact_months.data if hasattr(form, 'impact_months') else 0,
                notes=form.notes.data
            )
            db.session.add(event)
        
        db.session.commit()
        flash(f'تم إضافة الحدث المهني لـ {len(selected_employees)} موظف بنجاح! ✅', 'success')
        return redirect(url_for('events_list'))
    
    # جلب قائمة الموظفين
    employees = Employee.query.filter_by(status='active').order_by(Employee.full_name).all()
    return render_template('events/add.html', form=form, employees=employees)

def calculate_effective_service(employee):
    """حساب الخدمة الفعلية للموظف"""
    start_date = employee.start_date
    current_date = datetime.now().date()
    
    # حساب الفترة الأساسية
    total_days = (current_date - start_date).days
    
    # طرح فترات الإجازات الطويلة
    freeze_events = ProfessionalEvent.query.filter_by(
        employee_id=employee.id,
        event_type__in=['unpaid_leave', 'five_year_leave', 'disability_care_leave', 'maternity_leave']
    ).all()
    
    frozen_days = 0
    for event in freeze_events:
        if event.start_date and event.end_date:
            frozen_days += (event.end_date - event.start_date).days
    
    effective_days = total_days - frozen_days
    
    # تحويل إلى سنوات وشهور وأيام
    years = effective_days // 365
    remaining_days = effective_days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    return {
        'years': years,
        'months': months,
        'days': days,
        'total_days': effective_days
    }

@app.route('/api/employee/<int:employee_id>/calculate')
def api_calculate_entitlements(employee_id):
    """API لحساب الاستحقاقات"""
    employee = Employee.query.get_or_404(employee_id)
    engine = CalculationEngine(employee)
    
    # تشغيل المحرك
    results = engine.process_all_entitlements()
    
    return jsonify({
        'success': True,
        'results': results,
        'next_entitlement': engine.get_next_entitlement()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
