#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة شؤون الموظفين المتكامل
Employee Management System

نظام شامل لإدارة الموظفين وحساب العلاوات والترفيعات
تم تطويره باللغة العربية مع واجهة عصرية وجميلة

المطور: نظام الذكاء الاصطناعي
التاريخ: 2025
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import sqlite3

# إضافة مسار المشروع إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from employee_management_system.views.main_window import MainWindow
    from employee_management_system.database.database_manager import DatabaseManager
except ImportError as e:
    print(f"خطأ في استيراد الوحدات: {e}")
    sys.exit(1)

def main():
    """
    الدالة الرئيسية لتشغيل التطبيق
    """
    try:
        # إنشاء النافذة الجذر
        root = tk.Tk()
        
        # إعداد الترميز للغة العربية
        root.option_add('*Font', 'Arial 12')
        
        # إخفاء النافذة الجذر
        root.withdraw()
        
        # التحقق من قاعدة البيانات وإنشاؤها إذا لم تكن موجودة
        db_manager = DatabaseManager()
        if not db_manager.initialize_database():
            messagebox.showerror("خطأ", "فشل في إنشاء قاعدة البيانات")
            return
        
        # إنشاء النافذة الرئيسية
        app = MainWindow(root)
        
        # تشغيل التطبيق
        app.run()
        
    except Exception as e:
        messagebox.showerror("خطأ في التطبيق", f"حدث خطأ غير متوقع:\n{str(e)}")
        print(f"خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

