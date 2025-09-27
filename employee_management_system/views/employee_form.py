#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج إضافة وتعديل الموظف
Employee Form

واجهة إضافة وتعديل بيانات الموظفين مع جميع الحقول المطلوبة
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime, date
import os
import shutil

from .styles import StyleManager
from ..models.employee import Employee
from ..database.database_manager import DatabaseManager

class EmployeeForm:
    """
    فئة نموذج الموظف
    تحتوي على جميع حقول إدخال بيانات الموظف
    """
    
    def __init__(self, parent, db_manager, style_manager, employee=None, callback=None):
        """
        تهيئة نموذج الموظف
        
        Args:
            parent: العنصر الأب
            db_manager: مدير قاعدة البيانات
            style_manager: مدير الأنماط
            employee: بيانات الموظف للتعديل (اختياري)
            callback: دالة الاستدعاء بعد الحفظ
        """
        self.parent = parent
        self.db_manager = db_manager
        self.style_manager = style_manager
        self.employee = employee
        self.callback = callback
        self.is_edit_mode = employee is not None
        
        # متغيرات النموذج
        self.form_vars = {}
        self.photo_path = ""
        
        self._create_form()
        
        # تعبئة البيانات في حالة التعديل
        if self.is_edit_mode:
            self._populate_form()
    
    def _create_form(self):
        """
        إنشاء النموذج
        """
        # إطار النموذج الرئيسي
        self.form_frame = self.style_manager.create_card_frame(self.parent)
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # عنوان النموذج
        title_text = "تعديل بيانات الموظف" if self.is_edit_mode else "إضافة موظف جديد"
        title_label = tk.Label(
            self.form_frame,
            text=title_text,
            font=self.style_manager.get_font('heading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        title_label.pack(anchor='w', padx=20, pady=(20, 10))
        
        # إطار المحتوى مع شريط التمرير
        self._create_scrollable_content()
        
        # أزرار الإجراءات
        self._create_action_buttons()
    
    def _create_scrollable_content(self):
        """
        إنشاء محتوى قابل للتمرير
        """
        # إطار التمرير
        canvas = tk.Canvas(
            self.form_frame,
            bg=self.style_manager.get_color('bg_card'),
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(self.form_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.style_manager.get_color('bg_card'))
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # إنشاء حقول النموذج
        self._create_form_fields()
    
    def _create_form_fields(self):
        """
        إنشاء حقول النموذج
        """
        # قسم المعلومات الأساسية
        self._create_basic_info_section()
        
        # فاصل
        self._create_separator()
        
        # قسم المعلومات الوظيفية
        self._create_job_info_section()
        
        # فاصل
        self._create_separator()
        
        # قسم التواريخ المهمة
        self._create_dates_section()
        
        # فاصل
        self._create_separator()
        
        # قسم الصورة الشخصية
        self._create_photo_section()
    
    def _create_basic_info_section(self):
        """
        إنشاء قسم المعلومات الأساسية
        """
        section_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # عنوان القسم
        section_title = tk.Label(
            section_frame,
            text="المعلومات الأساسية",
            font=self.style_manager.get_font('subheading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('primary')
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        # الاسم الرباعي واللقب
        self._create_field(
            section_frame,
            "full_name",
            "الاسم الرباعي واللقب *",
            "entry",
            required=True
        )
        
        # الشهادة العلمية
        self._create_field(
            section_frame,
            "academic_degree",
            "الشهادة العلمية *",
            "combobox",
            values=[
                "دبلوم",
                "بكالوريوس",
                "ماجستير",
                "دكتوراه",
                "شهادة عليا أخرى"
            ],
            required=True
        )
    
    def _create_job_info_section(self):
        """
        إنشاء قسم المعلومات الوظيفية
        """
        section_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # عنوان القسم
        section_title = tk.Label(
            section_frame,
            text="المعلومات الوظيفية",
            font=self.style_manager.get_font('subheading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('primary')
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        # صنف الوظيفة
        self._create_field(
            section_frame,
            "job_class",
            "صنف الوظيفة *",
            "combobox",
            values=[
                "كادر تدريسي",
                "كادر إداري",
                "كادر فني",
                "كادر خدمي"
            ],
            required=True
        )
        
        # العنوان الوظيفي
        self._create_field(
            section_frame,
            "job_title",
            "العنوان الوظيفي *",
            "entry",
            required=True
        )
        
        # إطار الدرجة والمرحلة
        grade_frame = tk.Frame(
            section_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        grade_frame.pack(fill=tk.X, pady=5)
        
        # الدرجة الوظيفية
        grade_label = tk.Label(
            grade_frame,
            text="الدرجة الوظيفية *",
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        grade_label.pack(anchor='w')
        
        self.form_vars['job_grade'] = tk.StringVar()
        grade_spinbox = tk.Spinbox(
            grade_frame,
            from_=1,
            to=10,
            textvariable=self.form_vars['job_grade'],
            font=self.style_manager.get_font('body'),
            width=10
        )
        grade_spinbox.pack(anchor='w', pady=(5, 10))
        
        # المرحلة الوظيفية
        stage_label = tk.Label(
            grade_frame,
            text="المرحلة الوظيفية *",
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        stage_label.pack(anchor='w')
        
        self.form_vars['job_stage'] = tk.StringVar()
        stage_spinbox = tk.Spinbox(
            grade_frame,
            from_=1,
            to=11,
            textvariable=self.form_vars['job_stage'],
            font=self.style_manager.get_font('body'),
            width=10
        )
        stage_spinbox.pack(anchor='w', pady=(5, 10))
        
        # مؤشر تتبع العلاوة
        self._create_field(
            section_frame,
            "promotion_tracker",
            "مؤشر تتبع العلاوة *",
            "combobox",
            values=[
                "0/4", "1/4", "2/4", "3/4",
                "0/5", "1/5", "2/5", "3/5", "4/5"
            ],
            required=True
        )
    
    def _create_dates_section(self):
        """
        إنشاء قسم التواريخ المهمة
        """
        section_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # عنوان القسم
        section_title = tk.Label(
            section_frame,
            text="التواريخ المهمة",
            font=self.style_manager.get_font('subheading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('primary')
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        # تاريخ المباشرة بالوظيفة
        self._create_date_field(
            section_frame,
            "start_date",
            "تاريخ المباشرة بالوظيفة *",
            required=True
        )
        
        # تاريخ آخر استحقاق للعلاوة
        self._create_date_field(
            section_frame,
            "last_allowance_date",
            "تاريخ آخر استحقاق للعلاوة *",
            required=True
        )
        
        # آخر تاريخ استحقاق للترفيع
        self._create_date_field(
            section_frame,
            "last_promotion_date",
            "آخر تاريخ استحقاق للترفيع *",
            required=True
        )
    
    def _create_photo_section(self):
        """
        إنشاء قسم الصورة الشخصية
        """
        section_frame = tk.Frame(
            self.scrollable_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # عنوان القسم
        section_title = tk.Label(
            section_frame,
            text="الصورة الشخصية",
            font=self.style_manager.get_font('subheading'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('primary')
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        # إطار الصورة
        photo_frame = tk.Frame(
            section_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        photo_frame.pack(fill=tk.X)
        
        # عرض الصورة
        self.photo_label = tk.Label(
            photo_frame,
            text="لا توجد صورة",
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('gray'),
            fg=self.style_manager.get_color('text_muted'),
            width=20,
            height=8,
            relief='solid',
            bd=1
        )
        self.photo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # أزرار الصورة
        photo_buttons_frame = tk.Frame(
            photo_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        photo_buttons_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        upload_button = ttk.Button(
            photo_buttons_frame,
            text="اختيار صورة",
            command=self._select_photo,
            style='Secondary.TButton'
        )
        upload_button.pack(pady=(0, 5))
        
        remove_button = ttk.Button(
            photo_buttons_frame,
            text="إزالة الصورة",
            command=self._remove_photo,
            style='Warning.TButton'
        )
        remove_button.pack()
    
    def _create_field(self, parent, field_name, label_text, field_type, 
                     values=None, required=False):
        """
        إنشاء حقل إدخال
        
        Args:
            parent: العنصر الأب
            field_name: اسم الحقل
            label_text: نص التسمية
            field_type: نوع الحقل
            values: القيم للقائمة المنسدلة
            required: هل الحقل مطلوب
        """
        field_frame = tk.Frame(
            parent,
            bg=self.style_manager.get_color('bg_card')
        )
        field_frame.pack(fill=tk.X, pady=5)
        
        # التسمية
        label = tk.Label(
            field_frame,
            text=label_text,
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        label.pack(anchor='w')
        
        # الحقل
        self.form_vars[field_name] = tk.StringVar()
        
        if field_type == "entry":
            widget = tk.Entry(
                field_frame,
                textvariable=self.form_vars[field_name],
                font=self.style_manager.get_font('body'),
                relief='solid',
                bd=1
            )
        elif field_type == "combobox":
            widget = ttk.Combobox(
                field_frame,
                textvariable=self.form_vars[field_name],
                values=values or [],
                font=self.style_manager.get_font('body'),
                state='readonly'
            )
        
        widget.pack(fill=tk.X, pady=(5, 10))
    
    def _create_date_field(self, parent, field_name, label_text, required=False):
        """
        إنشاء حقل تاريخ
        
        Args:
            parent: العنصر الأب
            field_name: اسم الحقل
            label_text: نص التسمية
            required: هل الحقل مطلوب
        """
        field_frame = tk.Frame(
            parent,
            bg=self.style_manager.get_color('bg_card')
        )
        field_frame.pack(fill=tk.X, pady=5)
        
        # التسمية
        label = tk.Label(
            field_frame,
            text=label_text,
            font=self.style_manager.get_font('body'),
            bg=self.style_manager.get_color('bg_card'),
            fg=self.style_manager.get_color('text_primary')
        )
        label.pack(anchor='w')
        
        # حقل التاريخ
        date_entry = DateEntry(
            field_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            font=self.style_manager.get_font('body'),
            date_pattern='dd/mm/yyyy'
        )
        date_entry.pack(anchor='w', pady=(5, 10))
        
        # حفظ المرجع
        self.form_vars[field_name] = date_entry
    
    def _create_separator(self):
        """
        إنشاء فاصل
        """
        separator = tk.Frame(
            self.scrollable_frame,
            bg=self.style_manager.get_color('gray'),
            height=1
        )
        separator.pack(fill=tk.X, padx=20, pady=10)
    
    def _create_action_buttons(self):
        """
        إنشاء أزرار الإجراءات
        """
        buttons_frame = tk.Frame(
            self.form_frame,
            bg=self.style_manager.get_color('bg_card')
        )
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # زر الحفظ
        save_text = "تحديث البيانات" if self.is_edit_mode else "حفظ الموظف"
        save_button = ttk.Button(
            buttons_frame,
            text=save_text,
            command=self._save_employee,
            style='Success.TButton'
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # زر الإلغاء
        cancel_button = ttk.Button(
            buttons_frame,
            text="إلغاء",
            command=self._cancel,
            style='Secondary.TButton'
        )
        cancel_button.pack(side=tk.LEFT)
        
        # زر المسح (في حالة التعديل)
        if self.is_edit_mode:
            clear_button = ttk.Button(
                buttons_frame,
                text="مسح البيانات",
                command=self._clear_form,
                style='Warning.TButton'
            )
            clear_button.pack(side=tk.RIGHT)
    
    def _select_photo(self):
        """
        اختيار صورة للموظف
        """
        file_types = [
            ('صور', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('جميع الملفات', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="اختيار صورة الموظف",
            filetypes=file_types
        )
        
        if filename:
            try:
                # إنشاء مجلد الصور إذا لم يكن موجوداً
                photos_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'photos')
                os.makedirs(photos_dir, exist_ok=True)
                
                # نسخ الصورة إلى مجلد الموارد
                file_extension = os.path.splitext(filename)[1]
                new_filename = f"employee_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                new_path = os.path.join(photos_dir, new_filename)
                
                shutil.copy2(filename, new_path)
                self.photo_path = new_path
                
                # تحديث عرض الصورة
                self.photo_label.config(text="تم اختيار الصورة")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تحميل الصورة:\n{str(e)}")
    
    def _remove_photo(self):
        """
        إزالة صورة الموظف
        """
        self.photo_path = ""
        self.photo_label.config(text="لا توجد صورة")
    
    def _populate_form(self):
        """
        تعبئة النموذج ببيانات الموظف (في حالة التعديل)
        """
        if not self.employee:
            return
        
        # تعبئة الحقول النصية
        text_fields = [
            'full_name', 'academic_degree', 'job_class', 'job_title', 'promotion_tracker'
        ]
        
        for field in text_fields:
            if hasattr(self.employee, field) and field in self.form_vars:
                value = getattr(self.employee, field, '')
                self.form_vars[field].set(str(value))
        
        # تعبئة الحقول الرقمية
        if hasattr(self.employee, 'job_grade'):
            self.form_vars['job_grade'].set(str(self.employee.job_grade))
        
        if hasattr(self.employee, 'job_stage'):
            self.form_vars['job_stage'].set(str(self.employee.job_stage))
        
        # تعبئة حقول التاريخ
        date_fields = ['start_date', 'last_allowance_date', 'last_promotion_date']
        
        for field in date_fields:
            if hasattr(self.employee, field) and field in self.form_vars:
                date_value = getattr(self.employee, field)
                if date_value:
                    self.form_vars[field].set_date(date_value)
        
        # تعبئة الصورة
        if hasattr(self.employee, 'photo_path') and self.employee.photo_path:
            self.photo_path = self.employee.photo_path
            if os.path.exists(self.photo_path):
                self.photo_label.config(text="توجد صورة")
    
    def _validate_form(self):
        """
        التحقق من صحة بيانات النموذج
        
        Returns:
            قائمة الأخطاء
        """
        errors = []
        
        # التحقق من الحقول المطلوبة
        required_fields = {
            'full_name': 'الاسم الرباعي واللقب',
            'academic_degree': 'الشهادة العلمية',
            'job_class': 'صنف الوظيفة',
            'job_title': 'العنوان الوظيفي',
            'job_grade': 'الدرجة الوظيفية',
            'job_stage': 'المرحلة الوظيفية',
            'promotion_tracker': 'مؤشر تتبع العلاوة'
        }
        
        for field, label in required_fields.items():
            if field in self.form_vars:
                value = self.form_vars[field].get().strip()
                if not value:
                    errors.append(f"{label} مطلوب")
        
        # التحقق من التواريخ
        date_fields = ['start_date', 'last_allowance_date', 'last_promotion_date']
        for field in date_fields:
            if field in self.form_vars:
                try:
                    date_value = self.form_vars[field].get_date()
                    if date_value > date.today():
                        field_labels = {
                            'start_date': 'تاريخ المباشرة',
                            'last_allowance_date': 'تاريخ آخر استحقاق للعلاوة',
                            'last_promotion_date': 'تاريخ آخر استحقاق للترفيع'
                        }
                        errors.append(f"{field_labels[field]} لا يمكن أن يكون في المستقبل")
                except:
                    errors.append(f"تاريخ غير صحيح في حقل {field}")
        
        # التحقق من الدرجة والمرحلة
        try:
            grade = int(self.form_vars['job_grade'].get())
            if grade < 1 or grade > 10:
                errors.append("الدرجة الوظيفية يجب أن تكون بين 1 و 10")
        except ValueError:
            errors.append("الدرجة الوظيفية يجب أن تكون رقماً")
        
        try:
            stage = int(self.form_vars['job_stage'].get())
            if stage < 1:
                errors.append("المرحلة الوظيفية يجب أن تكون أكبر من 0")
        except ValueError:
            errors.append("المرحلة الوظيفية يجب أن تكون رقماً")
        
        return errors
    
    def _save_employee(self):
        """
        حفظ بيانات الموظف
        """
        # التحقق من صحة البيانات
        errors = self._validate_form()
        if errors:
            messagebox.showerror("خطأ في البيانات", "\n".join(errors))
            return
        
        try:
            # إنشاء كائن الموظف
            employee_data = {
                'full_name': self.form_vars['full_name'].get().strip(),
                'academic_degree': self.form_vars['academic_degree'].get(),
                'job_class': self.form_vars['job_class'].get(),
                'job_title': self.form_vars['job_title'].get().strip(),
                'job_grade': int(self.form_vars['job_grade'].get()),
                'job_stage': int(self.form_vars['job_stage'].get()),
                'promotion_tracker': self.form_vars['promotion_tracker'].get(),
                'start_date': self.form_vars['start_date'].get_date(),
                'last_allowance_date': self.form_vars['last_allowance_date'].get_date(),
                'last_promotion_date': self.form_vars['last_promotion_date'].get_date(),
                'photo_path': self.photo_path
            }
            
            if self.is_edit_mode:
                # تحديث الموظف الموجود
                success = self.db_manager.update_employee(self.employee.id, employee_data)
                message = "تم تحديث بيانات الموظف بنجاح"
            else:
                # إضافة موظف جديد
                employee_id = self.db_manager.add_employee(employee_data)
                success = employee_id is not None
                message = "تم إضافة الموظف بنجاح"
            
            if success:
                messagebox.showinfo("نجح", message)
                if self.callback:
                    self.callback()
                self._cancel()
            else:
                messagebox.showerror("خطأ", "فشل في حفظ بيانات الموظف")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ:\n{str(e)}")
    
    def _clear_form(self):
        """
        مسح بيانات النموذج
        """
        if messagebox.askyesno("تأكيد", "هل تريد مسح جميع البيانات؟"):
            for var in self.form_vars.values():
                if hasattr(var, 'set'):
                    var.set('')
                elif hasattr(var, 'set_date'):
                    var.set_date(date.today())
            
            self._remove_photo()
    
    def _cancel(self):
        """
        إلغاء النموذج
        """
        self.form_frame.destroy()

