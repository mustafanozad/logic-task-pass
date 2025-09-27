#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل نظام إدارة العلاوات والترفيعات المحسّن
Enhanced Employee Management System Launcher

هذا الملف يقوم بتشغيل النظام مع التحقق من المتطلبات وتهيئة قاعدة البيانات
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """التحقق من إصدار Python"""
    if sys.version_info < (3, 8):
        print("❌ خطأ: يتطلب النظام Python 3.8 أو أحدث")
        print(f"الإصدار الحالي: {sys.version}")
        return False
    print(f"✅ إصدار Python مناسب: {sys.version}")
    return True

def check_requirements():
    """التحقق من المتطلبات المثبتة"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_migrate',
        'sqlalchemy',
        'dateutil',
        'PIL',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'dateutil':
                import dateutil
            else:
                __import__(package)
            print(f"✅ {package} مثبت")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} غير مثبت")
    
    return missing_packages

def install_requirements():
    """تثبيت المتطلبات المفقودة"""
    print("\n🔧 تثبيت المتطلبات...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'enhanced_requirements.txt'
        ])
        print("✅ تم تثبيت جميع المتطلبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = [
        'static/images/employees',
        'static/css',
        'static/js',
        'templates/employees',
        'templates/events',
        'backend'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ تم إنشاء المجلد: {directory}")

def check_database():
    """التحقق من قاعدة البيانات وإنشائها إذا لم تكن موجودة"""
    db_path = 'enhanced_employee_management.db'
    
    if not os.path.exists(db_path):
        print("🗄️ إنشاء قاعدة البيانات...")
        try:
            # إنشاء قاعدة بيانات فارغة
            conn = sqlite3.connect(db_path)
            conn.close()
            print("✅ تم إنشاء قاعدة البيانات")
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
            return False
    else:
        print("✅ قاعدة البيانات موجودة")
    
    return True

def initialize_database():
    """تهيئة قاعدة البيانات بالجداول والبيانات الأساسية"""
    print("🔧 تهيئة قاعدة البيانات...")
    try:
        # استيراد النماذج وإنشاء الجداول
        from backend.enhanced_models import db, create_tables, init_default_settings
        from enhanced_app import app
        
        with app.app_context():
            create_tables(app)
            init_default_settings(app)
        
        print("✅ تم تهيئة قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
        return False

def run_system():
    """تشغيل النظام"""
    print("\n🚀 تشغيل نظام إدارة العلاوات والترفيعات...")
    print("=" * 60)
    print("🌐 سيتم فتح النظام على: http://localhost:5000")
    print("⏹️  لإيقاف النظام: اضغط Ctrl+C")
    print("=" * 60)
    
    try:
        from enhanced_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n⏹️  تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل النظام: {e}")

def main():
    """الدالة الرئيسية"""
    print("🏢 نظام إدارة العلاوات والترفيعات المحسّن")
    print("Enhanced Employee Management System")
    print("=" * 60)
    
    # التحقق من إصدار Python
    if not check_python_version():
        return
    
    # إنشاء المجلدات المطلوبة
    print("\n📁 إنشاء المجلدات...")
    create_directories()
    
    # التحقق من المتطلبات
    print("\n📦 التحقق من المتطلبات...")
    missing_packages = check_requirements()
    
    if missing_packages:
        print(f"\n⚠️  المتطلبات المفقودة: {', '.join(missing_packages)}")
        response = input("هل تريد تثبيت المتطلبات المفقودة؟ (y/n): ")
        if response.lower() in ['y', 'yes', 'نعم']:
            if not install_requirements():
                return
        else:
            print("❌ لا يمكن تشغيل النظام بدون المتطلبات المطلوبة")
            return
    
    # التحقق من قاعدة البيانات
    print("\n🗄️ التحقق من قاعدة البيانات...")
    if not check_database():
        return
    
    # تهيئة قاعدة البيانات
    if not initialize_database():
        return
    
    # تشغيل النظام
    run_system()

if __name__ == '__main__':
    main()

