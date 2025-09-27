#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النافذة الرئيسية للتطبيق
Main Application Window

النافذة الرئيسية التي تحتوي على جميع المكونات الأساسية للتطبيق
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .styles import StyleManager
from ..database.database_manager import DatabaseManager

class MainWindow:
    """
    فئة النافذة الرئيسية
    تدير الواجهة الرئيسية للتطبيق
    """
    
    def __init__(self, root):
        """
        تهيئة النافذة الرئيسية
        
        Args:
            root: النافذة الجذر
        """
        self.root = root
        self.db_manager = DatabaseManager()
        self.style_manager = StyleManager(root)
        
        # متغيرات الحالة
        self.current_view = None
        self.sidebar_buttons = {}
        
        self._setup_window()
        self._create_layout()
        self._show_dashboard()
    
    def _setup_window(self):
        """
        إعداد النافذة الرئيسية
        """
        # إعدادات النافذة
        self.root.title("نظام إدارة شؤون الموظفين")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        self.root.configure(bg=self.style_manager.get_color('bg_primary'))
        
        # وضع النافذة في المنتصف
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        # إعداد الأيقونة (إذا كانت متوفرة)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # إعداد إغلاق النافذة
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_layout(self):
        """
        إنشاء تخطيط النافذة الرئيسية
        """
        # الإطار الرئيسي
        self.main_frame = tk.Frame(
            self.root,
            bg=self.style_manager.get_color('bg_primary')
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # إنشاء الشريط الجانبي
        self._create_sidebar()
        
        # إنشاء منطقة المحتوى الرئيسي
        self._create_main_content()
    
    def _create_sidebar(self):
        """
        إنشاء الشريط الجانبي
        """
        # إطار الشريط الجانبي
        self.sidebar = tk.Frame(
            self.main_frame,
            bg=self.style_manager.get_color('bg_sidebar'),
            width=self.style_manager.styles.DIMENSIONS['sidebar_width']
        )
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # شعار التطبيق
        self._create_logo_section()
        
        # فاصل
        separator1 = tk.Frame(
            self.sidebar,
            bg=self.style_manager.get_color('primary_dark'),
            height=2
        )
        separator1.pack(fill=tk.X, pady=10)
        
        # أزرار القائمة الرئيسية
        self._create_menu_buttons()
        
        # فاصل
        separator2 = tk.Frame(
            self.sidebar,
            bg=self.style_manager.get_color('primary_dark'),
            height=2
        )
        separator2.pack(fill=tk.X, pady=10)
        
        # معلومات النظام
        self._create_system_info()
    
    def _create_logo_section(self):
        """
        إنشاء قسم الشعار
        """
        logo_frame = tk.Frame(
            self.sidebar,
            bg=self.style_manager.get_color('bg_sidebar'),
            pady=20
        )
        logo_frame.pack(fill=tk.X)
        
        # عنوان التطبيق
        title_label = tk.Label(
            logo_frame,
            text="نظام إدارة\nشؤون الموظفين",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_sidebar'),
            fg=self.style_manager.get_color('text_light'),
            justify=tk.CENTER
        )
        title_label.pack()
        
        # نسخة التطبيق
        version_label = tk.Label(
            logo_frame,
            text="الإصدار 1.0.0",
            font=self.style_manager.get_font('small'),
            bg=self.style_manager.get_color('bg_sidebar'),
            fg=self.style_manager.get_color('text_muted'),
            justify=tk.CENTER
        )
        version_label.pack(pady=(5, 0))
    
    def _create_menu_buttons(self):
        """
        إنشاء أزرار القائمة
        """
        # قائمة الأزرار
        menu_items = [
            {
                'text': '🏠  لوحة التحكم',
                'command': self._show_dashboard,
                'key': 'dashboard'
            },
            {
                'text': '👥  إدارة الموظفين',
                'command': self._show_employees,
                'key': 'employees'
            },
            {
                'text': '➕  إضافة موظف',
                'command': self._show_add_employee,
                'key': 'add_employee'
            },
            {
                'text': '📋  الأحداث المهنية',
                'command': self._show_events,
                'key': 'events'
            },
            {
                'text': '📊  التقارير',
                'command': self._show_reports,
                'key': 'reports'
            },
            {
                'text': '⚙️  الإعدادات',
                'command': self._show_settings,
                'key': 'settings'
            }
        ]
        
        # إنشاء الأزرار
        for item in menu_items:
            button = self.style_manager.create_sidebar_button(
                self.sidebar,
                text=item['text'],
                command=item['command']
            )
            button.pack(fill=tk.X, padx=10, pady=2)
            self.sidebar_buttons[item['key']] = button
    
    def _create_system_info(self):
        """
        إنشاء معلومات النظام
        """
        info_frame = tk.Frame(
            self.sidebar,
            bg=self.style_manager.get_color('bg_sidebar')
        )
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        # معلومات قاعدة البيانات
        try:
            employees_count = len(self.db_manager.get_all_employees())
            db_info = f"عدد الموظفين: {employees_count}"
        except:
            db_info = "قاعدة البيانات: غير متصلة"
        
        db_label = tk.Label(
            info_frame,
            text=db_info,
            font=self.style_manager.get_font('small'),
            bg=self.style_manager.get_color('bg_sidebar'),
            fg=self.style_manager.get_color('text_muted'),
            justify=tk.CENTER
        )
        db_label.pack()
        
        # معلومات التطوير
        dev_label = tk.Label(
            info_frame,
            text="تم التطوير بواسطة\nنظام الذكاء الاصطناعي",
            font=self.style_manager.get_font('small'),
            bg=self.style_manager.get_color('bg_sidebar'),
            fg=self.style_manager.get_color('text_muted'),
            justify=tk.CENTER
        )
        dev_label.pack(pady=(10, 0))
    
    def _create_main_content(self):
        """
        إنشاء منطقة المحتوى الرئيسي
        """
        # إطار المحتوى الرئيسي
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=self.style_manager.get_color('bg_secondary')
        )
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # شريط العنوان
        self._create_header()
        
        # منطقة المحتوى القابل للتغيير
        self.dynamic_content = tk.Frame(
            self.content_frame,
            bg=self.style_manager.get_color('bg_secondary')
        )
        self.dynamic_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _create_header(self):
        """
        إنشاء شريط العنوان
        """
        header_frame = tk.Frame(
            self.content_frame,
            bg=self.style_manager.get_color('bg_primary'),
            height=self.style_manager.styles.DIMENSIONS['header_height']
        )
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # عنوان الصفحة الحالية
        self.page_title = tk.Label(
            header_frame,
            text="لوحة التحكم",
            font=self.style_manager.get_font('title'),
            bg=self.style_manager.get_color('bg_primary'),
            fg=self.style_manager.get_color('text_primary')
        )
        self.page_title.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # معلومات إضافية
        self.page_info = tk.Label(
            header_frame,
            text="مرحباً بك في نظام إدارة شؤون الموظفين",
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_primary'),
            fg=self.style_manager.get_color('text_secondary')
        )
        self.page_info.pack(side=tk.RIGHT, padx=20, pady=(40, 0))
    
    def _clear_content(self):
        """
        مسح المحتوى الحالي
        """
        for widget in self.dynamic_content.winfo_children():
            widget.destroy()
    
    def _update_active_button(self, active_key):
        """
        تحديث الزر النشط
        
        Args:
            active_key: مفتاح الزر النشط
        """
        for key, button in self.sidebar_buttons.items():
            if key == active_key:
                button.config(bg=self.style_manager.get_color('primary_dark'))
            else:
                button.config(bg=self.style_manager.get_color('bg_sidebar'))
    
    # وظائف عرض الصفحات المختلفة
    def _show_dashboard(self):
        """
        عرض لوحة التحكم
        """
        self._clear_content()
        self.page_title.config(text="لوحة التحكم")
        self.page_info.config(text="نظرة عامة على النظام والإحصائيات")
        self._update_active_button('dashboard')
        
        # إنشاء لوحة التحكم
        self._create_dashboard()
    
    def _create_dashboard(self):
        """
        إنشاء محتوى لوحة التحكم
        """
        # إحصائيات سريعة
        stats_frame = tk.Frame(
            self.dynamic_content,
            bg=self.style_manager.get_color('bg_secondary')
        )
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # الحصول على الإحصائيات
        try:
            total_employees = len(self.db_manager.get_all_employees())
            # يمكن إضافة المزيد من الإحصائيات هنا
        except:
            total_employees = 0
        
        # بطاقات الإحصائيات
        stats = [
            {'title': 'إجمالي الموظفين', 'value': total_employees, 'color': 'primary'},
            {'title': 'الموظفين النشطين', 'value': total_employees, 'color': 'success'},
            {'title': 'العلاوات هذا الشهر', 'value': 0, 'color': 'warning'},
            {'title': 'الترفيعات هذا الشهر', 'value': 0, 'color': 'info'}
        ]
        
        for i, stat in enumerate(stats):
            card = self.style_manager.create_metric_card(
                stats_frame,
                title=stat['title'],
                value=stat['value'],
                color=stat['color']
            )
            card.grid(row=0, column=i, padx=10, sticky='ew')
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # الأنشطة الأخيرة
        activities_frame = self.style_manager.create_card_frame(self.dynamic_content)
        activities_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        activities_title = tk.Label(
            activities_frame,
            text="الأنشطة الأخيرة",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        activities_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        # قائمة الأنشطة (مؤقتة)
        activities_list = tk.Label(
            activities_frame,
            text="لا توجد أنشطة حديثة",
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_muted')
        )
        activities_list.pack(anchor='w', padx=20, pady=(0, 20))
        
        # أزرار سريعة
        quick_actions_frame = tk.Frame(
            self.dynamic_content,
            bg=self.style_manager.get_color('bg_secondary')
        )
        quick_actions_frame.pack(fill=tk.X)
        
        quick_title = tk.Label(
            quick_actions_frame,
            text="إجراءات سريعة",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        quick_title.pack(anchor='w', pady=(0, 10))
        
        buttons_frame = tk.Frame(
            quick_actions_frame,
            bg=self.style_manager.get_color('bg_secondary')
        )
        buttons_frame.pack(fill=tk.X)
        
        # الأزرار السريعة
        quick_buttons = [
            {'text': 'إضافة موظف جديد', 'command': self._show_add_employee, 'style': 'Primary.TButton'},
            {'text': 'عرض الموظفين', 'command': self._show_employees, 'style': 'Secondary.TButton'},
            {'text': 'إضافة حدث مهني', 'command': self._show_events, 'style': 'Success.TButton'},
        ]
        
        for i, btn in enumerate(quick_buttons):
            button = ttk.Button(
                buttons_frame,
                text=btn['text'],
                command=btn['command'],
                style=btn['style']
            )
            button.grid(row=0, column=i, padx=10, sticky='ew')
            buttons_frame.grid_columnconfigure(i, weight=1)
    
    def _show_employees(self):
        """
        عرض قائمة الموظفين
        """
        self._clear_content()
        self.page_title.config(text="إدارة الموظفين")
        self.page_info.config(text="عرض وإدارة جميع الموظفين")
        self._update_active_button('employees')
        
        # رسالة مؤقتة
        temp_label = tk.Label(
            self.dynamic_content,
            text="قائمة الموظفين - قيد التطوير",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        temp_label.pack(expand=True)
    
    def _show_add_employee(self):
        """
        عرض نموذج إضافة موظف
        """
        self._clear_content()
        self.page_title.config(text="إضافة موظف جديد")
        self.page_info.config(text="إدخال بيانات موظف جديد")
        self._update_active_button('add_employee')
        
        # رسالة مؤقتة
        temp_label = tk.Label(
            self.dynamic_content,
            text="نموذج إضافة موظف - قيد التطوير",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        temp_label.pack(expand=True)
    
    def _show_events(self):
        """
        عرض الأحداث المهنية
        """
        self._clear_content()
        self.page_title.config(text="الأحداث المهنية")
        self.page_info.config(text="إدارة الأحداث المهنية للموظفين")
        self._update_active_button('events')
        
        # رسالة مؤقتة
        temp_label = tk.Label(
            self.dynamic_content,
            text="الأحداث المهنية - قيد التطوير",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        temp_label.pack(expand=True)
    
    def _show_reports(self):
        """
        عرض التقارير
        """
        self._clear_content()
        self.page_title.config(text="التقارير")
        self.page_info.config(text="تقارير وإحصائيات النظام")
        self._update_active_button('reports')
        
        # رسالة مؤقتة
        temp_label = tk.Label(
            self.dynamic_content,
            text="التقارير - قيد التطوير",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        temp_label.pack(expand=True)
    
    def _show_settings(self):
        """
        عرض الإعدادات
        """
        self._clear_content()
        self.page_title.config(text="الإعدادات")
        self.page_info.config(text="إعدادات النظام والتخصيص")
        self._update_active_button('settings')
        
        # رسالة مؤقتة
        temp_label = tk.Label(
            self.dynamic_content,
            text="الإعدادات - قيد التطوير",
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_secondary'),
            fg=self.style_manager.get_color('text_primary')
        )
        temp_label.pack(expand=True)
    
    def _on_closing(self):
        """
        معالج إغلاق النافذة
        """
        if messagebox.askokcancel("إغلاق التطبيق", "هل تريد إغلاق التطبيق؟"):
            # إغلاق قاعدة البيانات
            if self.db_manager:
                self.db_manager.close_connection()
            
            # إغلاق التطبيق
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """
        تشغيل التطبيق
        """
        self.root.deiconify()  # إظهار النافذة
        self.root.mainloop()

