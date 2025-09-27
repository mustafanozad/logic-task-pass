#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار التطبيق
Test Application

ملف بسيط لاختبار النظام والتأكد من عمله
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """
    اختبار استيراد الوحدات
    """
    try:
        print("اختبار استيراد الوحدات...")
        
        # اختبار استيراد قاعدة البيانات
        from employee_management_system.database.database_manager import DatabaseManager
        print("✓ تم استيراد مدير قاعدة البيانات")
        
        # اختبار استيراد النماذج
        from employee_management_system.models.employee import Employee
        from employee_management_system.models.event import ProfessionalEvent
        print("✓ تم استيراد النماذج")
        
        # اختبار استيراد المحرك
        from employee_management_system.controllers.calculation_engine import CalculationEngine
        print("✓ تم استيراد محرك الحسابات")
        
        # اختبار استيراد الواجهات
        from employee_management_system.views.main_window import MainWindow
        from employee_management_system.views.styles import StyleManager
        print("✓ تم استيراد الواجهات")
        
        return True
        
    except ImportError as e:
        print(f"✗ خطأ في الاستيراد: {e}")
        return False
    except Exception as e:
        print(f"✗ خطأ عام: {e}")
        return False

def test_database():
    """
    اختبار قاعدة البيانات
    """
    try:
        print("\nاختبار قاعدة البيانات...")
        
        from employee_management_system.database.database_manager import DatabaseManager
        
        # إنشاء مدير قاعدة البيانات
        db_manager = DatabaseManager("test_db.db")
        
        # تهيئة قاعدة البيانات
        if db_manager.initialize_database():
            print("✓ تم إنشاء قاعدة البيانات بنجاح")
        else:
            print("✗ فشل في إنشاء قاعدة البيانات")
            return False
        
        # اختبار إضافة موظف تجريبي
        test_employee = {
            'full_name': 'أحمد محمد علي حسن',
            'start_date': '2020-01-01',
            'last_allowance_date': '2020-01-01',
            'last_promotion_date': '2020-01-01',
            'promotion_tracker': '0/4',
            'academic_degree': 'بكالوريوس',
            'job_class': 'كادر إداري',
            'job_title': 'موظف إداري',
            'job_grade': 8,
            'job_stage': 1,
            'photo_path': ''
        }
        
        employee_id = db_manager.add_employee(test_employee)
        if employee_id:
            print(f"✓ تم إضافة موظف تجريبي برقم: {employee_id}")
            
            # اختبار استرجاع الموظف
            employee = db_manager.get_employee(employee_id)
            if employee:
                print(f"✓ تم استرجاع بيانات الموظف: {employee['full_name']}")
            else:
                print("✗ فشل في استرجاع بيانات الموظف")
        else:
            print("✗ فشل في إضافة الموظف التجريبي")
        
        # إغلاق الاتصال
        db_manager.close_connection()
        
        # حذف قاعدة البيانات التجريبية
        if os.path.exists("test_db.db"):
            os.remove("test_db.db")
            print("✓ تم حذف قاعدة البيانات التجريبية")
        
        return True
        
    except Exception as e:
        print(f"✗ خطأ في اختبار قاعدة البيانات: {e}")
        return False

def test_gui():
    """
    اختبار الواجهة الرسومية
    """
    try:
        print("\nاختبار الواجهة الرسومية...")
        
        # إنشاء نافذة تجريبية
        root = tk.Tk()
        root.title("اختبار الواجهة")
        root.geometry("400x300")
        
        # اختبار الخطوط العربية
        label = tk.Label(
            root,
            text="مرحباً بك في نظام إدارة شؤون الموظفين",
            font=('Arial', 14),
            justify=tk.CENTER
        )
        label.pack(expand=True)
        
        # زر الإغلاق
        close_button = tk.Button(
            root,
            text="إغلاق",
            command=root.destroy,
            font=('Arial', 12)
        )
        close_button.pack(pady=20)
        
        print("✓ تم إنشاء نافذة تجريبية")
        print("سيتم عرض النافذة لمدة 3 ثوانٍ...")
        
        # عرض النافذة لفترة قصيرة
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✓ تم إغلاق النافذة التجريبية")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في اختبار الواجهة: {e}")
        return False

def main():
    """
    الدالة الرئيسية للاختبار
    """
    print("=" * 50)
    print("اختبار نظام إدارة شؤون الموظفين")
    print("=" * 50)
    
    # اختبار الاستيرادات
    if not test_imports():
        print("\n❌ فشل في اختبار الاستيرادات")
        return
    
    # اختبار قاعدة البيانات
    if not test_database():
        print("\n❌ فشل في اختبار قاعدة البيانات")
        return
    
    # اختبار الواجهة
    if not test_gui():
        print("\n❌ فشل في اختبار الواجهة")
        return
    
    print("\n" + "=" * 50)
    print("✅ تم اجتياز جميع الاختبارات بنجاح!")
    print("النظام جاهز للاستخدام")
    print("=" * 50)
    
    # سؤال المستخدم عن تشغيل التطبيق الكامل
    try:
        response = input("\nهل تريد تشغيل التطبيق الكامل؟ (y/n): ")
        if response.lower() in ['y', 'yes', 'نعم']:
            print("تشغيل التطبيق الكامل...")
            os.system("python main.py")
    except KeyboardInterrupt:
        print("\nتم إلغاء التشغيل")

if __name__ == "__main__":
    main()

