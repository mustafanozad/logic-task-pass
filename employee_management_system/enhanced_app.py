#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة العلاوات والترفيعات الوظيفية المحسّن
Enhanced Employee Promotion and Allowance Management System

تطبيق شامل ومتكامل لأتمتة وحوسبة العمليات المعقدة المتعلقة بحساب العلاوات السنوية والترفيعات الوظيفية
مع واجهة عصرية جميلة وأيقونات كبيرة وألوان جذابة
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import os
import json
from werkzeug.utils import secure_filename
from PIL import Image
import uuid

# إنشاء التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'enhanced-employee-management-system-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enhanced_employee_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images/employees'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# إنشاء مجلدات الرفع إذا لم تكن موجودة
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# تهيئة قاعدة البيانات
from backend.enhanced_models import db, Employee, ProfessionalEvent, CareerHistory, SystemSettings, EventType, CareerEventType, EmployeeStatus
from backend.enhanced_calculation_engine import EnhancedCalculationEngine, recalculate_employee_entitlements

db.init_app(app)
migrate = Migrate(app, db)

# دوال مساعدة
def allowed_file(filename):
    """التحقق من امتدادات الملفات المسموحة"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(300, 300)):
    """تغيير حجم الصورة"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        print(f"خطأ في تغيير حجم الصورة: {e}")

def get_system_setting(key, default=None):
    """الحصول على إعداد النظام"""
    setting = SystemSettings.query.filter_by(setting_key=key).first()
    return setting.setting_value if setting else default

# المسارات الرئيسية
@app.route('/')
def index():
    """الصفحة الرئيسية مع لوحة التحكم"""
    # إحصائيات عامة
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(status=EmployeeStatus.ACTIVE).count()
    
    # إحصائيات الأحداث
    recent_events = ProfessionalEvent.query.order_by(
        ProfessionalEvent.event_date.desc()
    ).limit(10).all()
    
    # إحصائيات العلاوات والترفيعات الحديثة
    recent_career_events = CareerHistory.query.order_by(
        CareerHistory.event_date.desc()
    ).limit(10).all()
    
    # حساب الاستحقاقات القادمة
    upcoming_entitlements = []
    employees = Employee.query.filter_by(status=EmployeeStatus.ACTIVE).all()
    
    for employee in employees[:10]:  # أول 10 موظفين فقط للعرض السريع
        try:
            engine = EnhancedCalculationEngine(employee)
            next_entitlement = engine.get_next_entitlement()
            if next_entitlement['days_remaining'] <= 30:  # الاستحقاقات خلال 30 يوم
                upcoming_entitlements.append({
                    'employee': employee,
                    'entitlement': next_entitlement
                })
        except Exception as e:
            print(f"خطأ في حساب الاستحقاق للموظف {employee.full_name}: {e}")
    
    # ترتيب الاستحقاقات القادمة حسب التاريخ
    upcoming_entitlements.sort(key=lambda x: x['entitlement']['date'])
    
    stats = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': total_employees - active_employees,
        'recent_events': recent_events,
        'recent_career_events': recent_career_events,
        'upcoming_entitlements': upcoming_entitlements[:5],  # أول 5 فقط
        'system_name': get_system_setting('system_name', 'نظام إدارة العلاوات والترفيعات'),
        'organization_name': get_system_setting('organization_name', 'المؤسسة التعليمية')
    }
    
    return render_template('enhanced_index.html', stats=stats)

@app.route('/employees')
def employee_list():
    """قائمة الموظفين مع الفلترة"""
    # معاملات الفلترة
    job_class_filter = request.args.get('job_class', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')  # name, start_date, grade
    
    # بناء الاستعلام
    query = Employee.query
    
    if job_class_filter:
        query = query.filter(Employee.job_class.contains(job_class_filter))
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(Employee.full_name.contains(search_query))
    
    # الترتيب
    if sort_by == 'start_date':
        query = query.order_by(Employee.start_date.desc())
    elif sort_by == 'grade':
        query = query.order_by(Employee.job_grade.asc(), Employee.current_stage.asc())
    else:  # name
        query = query.order_by(Employee.full_name.asc())
    
    employees = query.all()
    
    # الحصول على قائمة الأصناف الوظيفية للفلترة
    job_classes = db.session.query(Employee.job_class).distinct().all()
    job_classes = [jc[0] for jc in job_classes]
    
    return render_template('employees/enhanced_employee_list.html', 
                         employees=employees,
                         job_classes=job_classes,
                         current_filters={
                             'job_class': job_class_filter,
                             'status': status_filter,
                             'search': search_query,
                             'sort': sort_by
                         })

@app.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    """إضافة موظف جديد"""
    if request.method == 'POST':
        try:
            # جمع البيانات من النموذج
            full_name = request.form.get('full_name')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            last_allowance_date = datetime.strptime(request.form.get('last_allowance_date'), '%Y-%m-%d').date()
            last_promotion_date_str = request.form.get('last_promotion_date')
            last_promotion_date = datetime.strptime(last_promotion_date_str, '%Y-%m-%d').date() if last_promotion_date_str else None
            
            promotion_tracker = request.form.get('promotion_tracker')
            academic_degree = request.form.get('academic_degree')
            job_class = request.form.get('job_class')
            job_title = request.form.get('job_title')
            job_grade = int(request.form.get('job_grade'))
            current_stage = int(request.form.get('current_stage', 1))
            
            # معالجة رفع الصورة
            photo_path = None
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    # إنشاء اسم ملف فريد
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # تغيير حجم الصورة
                    resize_image(file_path)
                    photo_path = f'images/employees/{filename}'
            
            # إنشاء الموظف الجديد
            employee = Employee(
                full_name=full_name,
                photo_path=photo_path,
                start_date=start_date,
                last_allowance_date=last_allowance_date,
                last_promotion_date=last_promotion_date,
                promotion_tracker=promotion_tracker,
                academic_degree=academic_degree,
                job_class=job_class,
                job_title=job_title,
                job_grade=job_grade,
                current_stage=current_stage,
                status=EmployeeStatus.ACTIVE
            )
            
            db.session.add(employee)
            db.session.commit()
            
            # إنشاء سجل أولي في المسار الوظيفي
            initial_record = CareerHistory(
                employee_id=employee.id,
                event_type=CareerEventType.INITIAL_APPOINTMENT,
                event_date=start_date,
                to_grade=job_grade,
                to_stage=current_stage,
                tracker_after=promotion_tracker,
                description=f"تعيين أولي - الدرجة {job_grade} المرحلة {current_stage}",
                is_automatic=False
            )
            
            db.session.add(initial_record)
            db.session.commit()
            
            flash('تم إضافة الموظف بنجاح!', 'success')
            return redirect(url_for('employee_profile', employee_id=employee.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة الموظف: {str(e)}', 'error')
    
    return render_template('employees/enhanced_add_employee.html')

@app.route('/employees/<int:employee_id>')
def employee_profile(employee_id):
    """ملف الموظف التفاعلي"""
    employee = Employee.query.get_or_404(employee_id)
    
    # تشغيل المحرك الحسابي لضمان تحديث البيانات
    try:
        engine = EnhancedCalculationEngine(employee)
        engine.process_all_entitlements()
        
        # الحصول على معلومات الاستحقاق القادم
        next_entitlement = engine.get_next_entitlement()
        
        # حساب الخدمة الفعلية
        effective_service = engine.calculate_effective_service()
        
    except Exception as e:
        print(f"خطأ في المحرك الحسابي: {e}")
        next_entitlement = {'type_arabic': 'غير محدد', 'date': None, 'details': 'خطأ في الحساب'}
        effective_service = {'formatted': 'غير محدد'}
    
    # جلب المسار الوظيفي
    career_history = CareerHistory.query.filter_by(
        employee_id=employee_id
    ).order_by(CareerHistory.event_date.desc()).all()
    
    # جلب الأحداث المهنية
    professional_events = ProfessionalEvent.query.filter_by(
        employee_id=employee_id
    ).order_by(ProfessionalEvent.event_date.desc()).all()
    
    return render_template('employees/enhanced_employee_profile.html',
                         employee=employee,
                         next_entitlement=next_entitlement,
                         effective_service=effective_service,
                         career_history=career_history,
                         professional_events=professional_events)

@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """تعديل بيانات الموظف"""
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        try:
            # تحديث البيانات الأساسية
            employee.full_name = request.form.get('full_name')
            employee.academic_degree = request.form.get('academic_degree')
            employee.job_class = request.form.get('job_class')
            employee.job_title = request.form.get('job_title')
            
            # معالجة رفع صورة جديدة
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    # حذف الصورة القديمة
                    if employee.photo_path:
                        old_path = os.path.join('static', employee.photo_path)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    
                    # حفظ الصورة الجديدة
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    resize_image(file_path)
                    employee.photo_path = f'images/employees/{filename}'
            
            db.session.commit()
            flash('تم تحديث بيانات الموظف بنجاح!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تحديث البيانات: {str(e)}', 'error')
    
    return render_template('employees/enhanced_edit_employee.html', employee=employee)

@app.route('/events')
def event_list():
    """قائمة الأحداث المهنية"""
    events = ProfessionalEvent.query.order_by(
        ProfessionalEvent.event_date.desc()
    ).all()
    
    return render_template('events/enhanced_event_list.html', events=events)

@app.route('/events/add', methods=['GET', 'POST'])
def add_event():
    """إضافة حدث مهني"""
    if request.method == 'POST':
        try:
            # جمع البيانات الأساسية
            employee_ids = request.form.getlist('employee_ids')
            event_type = EventType(request.form.get('event_type'))
            event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date()
            document_number = request.form.get('document_number')
            document_date_str = request.form.get('document_date')
            document_date = datetime.strptime(document_date_str, '%Y-%m-%d').date() if document_date_str else None
            notes = request.form.get('notes')
            
            # معالجة البيانات الخاصة بكل نوع حدث
            events_created = []
            
            for employee_id in employee_ids:
                employee = Employee.query.get(int(employee_id))
                if not employee:
                    continue
                
                # إنشاء الحدث الأساسي
                event = ProfessionalEvent(
                    employee_id=employee.id,
                    event_type=event_type,
                    event_date=event_date,
                    document_number=document_number,
                    document_date=document_date,
                    notes=notes
                )
                
                # معالجة البيانات الخاصة بكل نوع
                if event_type == EventType.COMMENDATION:
                    event.reduction_months = int(request.form.get('reduction_months', 0))
                    event.description = f"كتاب شكر وتقدير - تقليص {event.reduction_months} أشهر"
                
                elif event_type == EventType.HIGHER_DEGREE:
                    event.impact_months = -12  # تقليص سنة كاملة
                    event.new_job_class = request.form.get('new_job_class')
                    event.new_job_title = request.form.get('new_job_title')
                    event.new_academic_degree = request.form.get('new_academic_degree')
                    event.description = f"الحصول على شهادة أعلى: {event.new_academic_degree}"
                    
                    # تحديث بيانات الموظف
                    if event.new_job_class:
                        employee.job_class = event.new_job_class
                    if event.new_job_title:
                        employee.job_title = event.new_job_title
                    if event.new_academic_degree:
                        employee.academic_degree = event.new_academic_degree
                
                elif event_type == EventType.NOTICE_PENALTY:
                    event.impact_months = 3
                    event.description = "عقوبة لفت نظر - إضافة 3 أشهر"
                
                elif event_type == EventType.WARNING_PENALTY:
                    event.impact_months = 6
                    event.description = "عقوبة إنذار - إضافة 6 أشهر"
                
                elif event_type == EventType.REPRIMAND_PENALTY:
                    event.impact_months = 12
                    event.description = "عقوبة توبيخ - إضافة 12 شهر"
                
                elif event_type in [EventType.UNPAID_LEAVE, EventType.DISABILITY_CARE_LEAVE, 
                                  EventType.FIVE_YEAR_LEAVE, EventType.MATERNITY_LEAVE]:
                    leave_start = datetime.strptime(request.form.get('leave_start_date'), '%Y-%m-%d').date()
                    leave_end = datetime.strptime(request.form.get('leave_end_date'), '%Y-%m-%d').date()
                    event.leave_start_date = leave_start
                    event.leave_end_date = leave_end
                    
                    leave_days = (leave_end - leave_start).days
                    event.description = f"{event.event_type_arabic} - من {leave_start} إلى {leave_end} ({leave_days} يوم)"
                
                elif event_type == EventType.CUSTOM_EVENT:
                    adjustment_type = request.form.get('adjustment_type')
                    months = int(request.form.get('custom_months', 0))
                    event.impact_months = months if adjustment_type == 'add' else -months
                    event.description = f"حدث مخصص - {adjustment_type} {months} أشهر"
                
                db.session.add(event)
                events_created.append(event)
            
            db.session.commit()
            
            # إعادة حساب الاستحقاقات للموظفين المتأثرين
            for employee_id in employee_ids:
                try:
                    recalculate_employee_entitlements(int(employee_id))
                except Exception as e:
                    print(f"خطأ في إعادة حساب الاستحقاقات للموظف {employee_id}: {e}")
            
            flash(f'تم إضافة {len(events_created)} حدث مهني بنجاح!', 'success')
            return redirect(url_for('event_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة الحدث: {str(e)}', 'error')
    
    # جلب قائمة الموظفين للنموذج
    employees = Employee.query.filter_by(status=EmployeeStatus.ACTIVE).order_by(Employee.full_name).all()
    
    # تجميع الموظفين حسب الصنف الوظيفي
    employees_by_class = {}
    for employee in employees:
        if employee.job_class not in employees_by_class:
            employees_by_class[employee.job_class] = []
        employees_by_class[employee.job_class].append(employee)
    
    return render_template('events/enhanced_add_event.html', 
                         employees_by_class=employees_by_class,
                         event_types=EventType)

@app.route('/api/employees/<int:employee_id>/recalculate', methods=['POST'])
def api_recalculate_employee(employee_id):
    """API لإعادة حساب استحقاقات موظف"""
    try:
        result = recalculate_employee_entitlements(employee_id)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>/next-entitlement')
def api_employee_next_entitlement(employee_id):
    """API للحصول على الاستحقاق القادم للموظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        engine = EnhancedCalculationEngine(employee)
        next_entitlement = engine.get_next_entitlement()
        
        # تحويل التاريخ لنص للـ JSON
        if next_entitlement['date']:
            next_entitlement['date'] = next_entitlement['date'].isoformat()
        
        return jsonify({'success': True, 'entitlement': next_entitlement})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reports')
def reports():
    """تقارير النظام"""
    # تقرير الاستحقاقات القادمة
    upcoming_entitlements = []
    employees = Employee.query.filter_by(status=EmployeeStatus.ACTIVE).all()
    
    for employee in employees:
        try:
            engine = EnhancedCalculationEngine(employee)
            next_entitlement = engine.get_next_entitlement()
            upcoming_entitlements.append({
                'employee': employee,
                'entitlement': next_entitlement
            })
        except Exception as e:
            print(f"خطأ في حساب الاستحقاق للموظف {employee.full_name}: {e}")
    
    # ترتيب حسب التاريخ
    upcoming_entitlements.sort(key=lambda x: x['entitlement']['date'])
    
    # إحصائيات الأحداث المهنية
    event_stats = {}
    for event_type in EventType:
        count = ProfessionalEvent.query.filter_by(event_type=event_type).count()
        event_stats[event_type.value] = {
            'count': count,
            'arabic_name': ProfessionalEvent(event_type=event_type).event_type_arabic
        }
    
    return render_template('reports/enhanced_reports.html',
                         upcoming_entitlements=upcoming_entitlements,
                         event_stats=event_stats)

@app.route('/settings')
def settings():
    """إعدادات النظام"""
    system_settings = SystemSettings.query.all()
    return render_template('settings/enhanced_settings.html', settings=system_settings)

# معالج الأخطاء
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# تهيئة قاعدة البيانات
@app.before_first_request
def create_tables():
    """إنشاء الجداول عند أول تشغيل"""
    db.create_all()
    
    # تهيئة الإعدادات الافتراضية
    from backend.enhanced_models import init_default_settings
    init_default_settings(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from backend.enhanced_models import init_default_settings
        init_default_settings(app)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

