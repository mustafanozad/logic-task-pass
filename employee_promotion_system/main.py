#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة العلاوات والترفيعات الشامل
Employee Promotion Management System

الملف الرئيسي لتشغيل التطبيق
Main application entry point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

# إضافة مسار المشروع إلى sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# إعداد نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_directories():
    """إنشاء المجلدات المطلوبة للنظام"""
    directories = [
        'database',
        'logs',
        'assets/icons',
        'assets/images',
        'exports',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("تم إنشاء المجلدات المطلوبة")

def check_dependencies():
    """فحص المكتبات المطلوبة"""
    required_modules = [
        'tkinter',
        'sqlite3',
        'datetime',
        'dateutil'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"المكتبات المفقودة: {', '.join(missing_modules)}")
        messagebox.showerror(
            "خطأ في المكتبات",
            f"المكتبات التالية مفقودة:\n{chr(10).join(missing_modules)}\n\nيرجى تثبيتها باستخدام pip"
        )
        return False
    
    return True

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    try:
        # إنشاء المجلدات المطلوبة
        create_directories()
        
        # فحص المكتبات المطلوبة
        if not check_dependencies():
            sys.exit(1)
        
        # استيراد الواجهة الرئيسية
        from ui.main_window import MainApplication
        
        # إنشاء وتشغيل التطبيق
        app = MainApplication()
        
        logger.info("تم بدء تشغيل نظام إدارة العلاوات والترفيعات")
        
        # تشغيل حلقة الأحداث الرئيسية
        app.run()
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل التطبيق: {str(e)}")
        messagebox.showerror(
            "خطأ في النظام",
            f"حدث خطأ في تشغيل التطبيق:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
