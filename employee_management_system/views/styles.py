#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أنماط التصميم
Styles and Themes

يحتوي على جميع الألوان والخطوط والأنماط المستخدمة في التطبيق
"""

import tkinter as tk
from tkinter import ttk
import os

class AppStyles:
    """
    فئة أنماط التطبيق
    تحتوي على جميع الألوان والخطوط والأنماط
    """
    
    # الألوان الأساسية
    COLORS = {
        # الألوان الرئيسية
        'primary': '#2E86AB',      # أزرق رئيسي
        'primary_dark': '#1B5E7A', # أزرق داكن
        'primary_light': '#A8DADC', # أزرق فاتح
        
        # الألوان الثانوية
        'secondary': '#457B9D',     # أزرق ثانوي
        'accent': '#F1FAEE',        # أبيض مائل للأزرق
        
        # ألوان الحالة
        'success': '#06D6A0',       # أخضر للنجاح
        'warning': '#FFD166',       # أصفر للتحذير
        'error': '#EF476F',         # أحمر للخطأ
        'info': '#118AB2',          # أزرق للمعلومات
        
        # الألوان المحايدة
        'white': '#FFFFFF',
        'light_gray': '#F8F9FA',
        'gray': '#E9ECEF',
        'dark_gray': '#6C757D',
        'black': '#212529',
        
        # ألوان الخلفية
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'bg_sidebar': '#2E86AB',
        'bg_card': '#FFFFFF',
        
        # ألوان النص
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'text_light': '#FFFFFF',
        'text_muted': '#ADB5BD',
    }
    
    # الخطوط
    FONTS = {
        'title': ('Arial', 24, 'bold'),
        'heading': ('Arial', 18, 'bold'),
        'subheading': ('Arial', 14, 'bold'),
        'body': ('Arial', 12, 'normal'),
        'body_bold': ('Arial', 12, 'bold'),
        'small': ('Arial', 10, 'normal'),
        'button': ('Arial', 12, 'bold'),
        'menu': ('Arial', 14, 'normal'),
    }
    
    # أحجام الأيقونات
    ICON_SIZES = {
        'small': 16,
        'medium': 24,
        'large': 32,
        'xlarge': 48,
        'menu': 32,
    }
    
    # المسافات والأبعاد
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }
    
    # أبعاد المكونات
    DIMENSIONS = {
        'sidebar_width': 280,
        'header_height': 80,
        'card_min_height': 120,
        'button_height': 40,
        'input_height': 35,
    }
    
    # تأثيرات الظل
    SHADOWS = {
        'light': '1px 1px 3px rgba(0,0,0,0.1)',
        'medium': '2px 2px 8px rgba(0,0,0,0.15)',
        'heavy': '4px 4px 16px rgba(0,0,0,0.2)',
    }

class StyleManager:
    """
    مدير الأنماط
    يطبق الأنماط على المكونات المختلفة
    """
    
    def __init__(self, root):
        """
        تهيئة مدير الأنماط
        
        Args:
            root: النافذة الجذر
        """
        self.root = root
        self.styles = AppStyles()
        self._setup_ttk_styles()
    
    def _setup_ttk_styles(self):
        """
        إعداد أنماط ttk
        """
        style = ttk.Style()
        
        # تكوين الأنماط المخصصة
        
        # أسلوب الأزرار الرئيسية
        style.configure(
            'Primary.TButton',
            background=self.styles.COLORS['primary'],
            foreground=self.styles.COLORS['white'],
            font=self.styles.FONTS['button'],
            padding=(20, 10),
            relief='flat'
        )
        
        style.map(
            'Primary.TButton',
            background=[('active', self.styles.COLORS['primary_dark']),
                       ('pressed', self.styles.COLORS['primary_dark'])]
        )
        
        # أسلوب الأزرار الثانوية
        style.configure(
            'Secondary.TButton',
            background=self.styles.COLORS['gray'],
            foreground=self.styles.COLORS['text_primary'],
            font=self.styles.FONTS['button'],
            padding=(20, 10),
            relief='flat'
        )
        
        # أسلوب أزرار النجاح
        style.configure(
            'Success.TButton',
            background=self.styles.COLORS['success'],
            foreground=self.styles.COLORS['white'],
            font=self.styles.FONTS['button'],
            padding=(20, 10),
            relief='flat'
        )
        
        # أسلوب أزرار التحذير
        style.configure(
            'Warning.TButton',
            background=self.styles.COLORS['warning'],
            foreground=self.styles.COLORS['text_primary'],
            font=self.styles.FONTS['button'],
            padding=(20, 10),
            relief='flat'
        )
        
        # أسلوب أزرار الخطر
        style.configure(
            'Danger.TButton',
            background=self.styles.COLORS['error'],
            foreground=self.styles.COLORS['white'],
            font=self.styles.FONTS['button'],
            padding=(20, 10),
            relief='flat'
        )
        
        # أسلوب حقول الإدخال
        style.configure(
            'Custom.TEntry',
            fieldbackground=self.styles.COLORS['white'],
            borderwidth=1,
            relief='solid',
            padding=(10, 8),
            font=self.styles.FONTS['body']
        )
        
        # أسلوب القوائم المنسدلة
        style.configure(
            'Custom.TCombobox',
            fieldbackground=self.styles.COLORS['white'],
            borderwidth=1,
            relief='solid',
            padding=(10, 8),
            font=self.styles.FONTS['body']
        )
        
        # أسلوب الإطارات
        style.configure(
            'Card.TFrame',
            background=self.styles.COLORS['bg_card'],
            relief='flat',
            borderwidth=1
        )
        
        # أسلوب التسميات
        style.configure(
            'Heading.TLabel',
            background=self.styles.COLORS['bg_primary'],
            foreground=self.styles.COLORS['text_primary'],
            font=self.styles.FONTS['heading']
        )
        
        style.configure(
            'Body.TLabel',
            background=self.styles.COLORS['bg_primary'],
            foreground=self.styles.COLORS['text_primary'],
            font=self.styles.FONTS['body']
        )
        
        style.configure(
            'Muted.TLabel',
            background=self.styles.COLORS['bg_primary'],
            foreground=self.styles.COLORS['text_muted'],
            font=self.styles.FONTS['small']
        )
    
    def create_card_frame(self, parent, **kwargs):
        """
        إنشاء إطار بطاقة
        
        Args:
            parent: العنصر الأب
            **kwargs: معاملات إضافية
            
        Returns:
            إطار البطاقة
        """
        frame = tk.Frame(
            parent,
            bg=self.styles.COLORS['bg_card'],
            relief='solid',
            bd=1,
            **kwargs
        )
        return frame
    
    def create_sidebar_button(self, parent, text, icon=None, command=None):
        """
        إنشاء زر الشريط الجانبي
        
        Args:
            parent: العنصر الأب
            text: نص الزر
            icon: الأيقونة (اختياري)
            command: الأمر عند النقر
            
        Returns:
            الزر
        """
        button = tk.Button(
            parent,
            text=text,
            font=self.styles.FONTS['menu'],
            bg=self.styles.COLORS['bg_sidebar'],
            fg=self.styles.COLORS['text_light'],
            activebackground=self.styles.COLORS['primary_dark'],
            activeforeground=self.styles.COLORS['text_light'],
            relief='flat',
            bd=0,
            pady=15,
            anchor='w',
            command=command
        )
        
        # تأثيرات التفاعل
        def on_enter(e):
            button.config(bg=self.styles.COLORS['primary_dark'])
        
        def on_leave(e):
            button.config(bg=self.styles.COLORS['bg_sidebar'])
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def create_metric_card(self, parent, title, value, icon=None, color='primary'):
        """
        إنشاء بطاقة مؤشر
        
        Args:
            parent: العنصر الأب
            title: عنوان المؤشر
            value: قيمة المؤشر
            icon: الأيقونة (اختياري)
            color: لون البطاقة
            
        Returns:
            إطار البطاقة
        """
        # اختيار اللون
        if color == 'success':
            bg_color = self.styles.COLORS['success']
        elif color == 'warning':
            bg_color = self.styles.COLORS['warning']
        elif color == 'error':
            bg_color = self.styles.COLORS['error']
        else:
            bg_color = self.styles.COLORS['primary']
        
        # إنشاء الإطار الرئيسي
        card = tk.Frame(
            parent,
            bg=bg_color,
            relief='flat',
            bd=0,
            padx=20,
            pady=15
        )
        
        # عنوان المؤشر
        title_label = tk.Label(
            card,
            text=title,
            font=self.styles.FONTS['body'],
            bg=bg_color,
            fg=self.styles.COLORS['white']
        )
        title_label.pack(anchor='w')
        
        # قيمة المؤشر
        value_label = tk.Label(
            card,
            text=str(value),
            font=self.styles.FONTS['title'],
            bg=bg_color,
            fg=self.styles.COLORS['white']
        )
        value_label.pack(anchor='w', pady=(5, 0))
        
        return card
    
    def apply_hover_effect(self, widget, hover_color=None):
        """
        تطبيق تأثير التمرير
        
        Args:
            widget: العنصر
            hover_color: لون التمرير
        """
        original_color = widget.cget('bg')
        if hover_color is None:
            hover_color = self.styles.COLORS['primary_light']
        
        def on_enter(e):
            widget.config(bg=hover_color)
        
        def on_leave(e):
            widget.config(bg=original_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def create_separator(self, parent, orient='horizontal'):
        """
        إنشاء فاصل
        
        Args:
            parent: العنصر الأب
            orient: اتجاه الفاصل
            
        Returns:
            الفاصل
        """
        separator = ttk.Separator(parent, orient=orient)
        return separator
    
    def get_color(self, color_name):
        """
        الحصول على لون
        
        Args:
            color_name: اسم اللون
            
        Returns:
            قيمة اللون
        """
        return self.styles.COLORS.get(color_name, '#000000')
    
    def get_font(self, font_name):
        """
        الحصول على خط
        
        Args:
            font_name: اسم الخط
            
        Returns:
            معلومات الخط
        """
        return self.styles.FONTS.get(font_name, ('Arial', 12, 'normal'))

