#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير قاعدة البيانات
Database Manager

يدير جميع العمليات المتعلقة بقاعدة البيانات SQLite
"""

import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Tuple

class DatabaseManager:
    """
    فئة إدارة قاعدة البيانات
    تتولى جميع العمليات المتعلقة بقاعدة البيانات
    """
    
    def __init__(self, db_path: str = "employee_management.db"):
        """
        تهيئة مدير قاعدة البيانات
        
        Args:
            db_path: مسار ملف قاعدة البيانات
        """
        self.db_path = db_path
        self.connection = None
    
    def get_connection(self) -> sqlite3.Connection:
        """
        الحصول على اتصال بقاعدة البيانات
        
        Returns:
            اتصال قاعدة البيانات
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
        return self.connection
    
    def close_connection(self):
        """
        إغلاق اتصال قاعدة البيانات
        """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self) -> bool:
        """
        إنشاء قاعدة البيانات والجداول
        
        Returns:
            True إذا تم الإنشاء بنجاح، False في حالة الفشل
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # إنشاء جدول الموظفين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    last_allowance_date DATE NOT NULL,
                    last_promotion_date DATE NOT NULL,
                    promotion_tracker TEXT NOT NULL,
                    academic_degree TEXT NOT NULL,
                    job_class TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    job_grade INTEGER NOT NULL,
                    job_stage INTEGER NOT NULL,
                    photo_path TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء جدول الأحداث المهنية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS professional_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_date DATE NOT NULL,
                    document_number TEXT,
                    document_date DATE,
                    description TEXT,
                    effect_months INTEGER DEFAULT 0,
                    effect_type TEXT DEFAULT 'none',
                    start_date DATE,
                    end_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')
            
            # إنشاء جدول العلاوات والترفيعات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_date DATE NOT NULL,
                    from_grade INTEGER,
                    to_grade INTEGER,
                    from_stage INTEGER,
                    to_stage INTEGER,
                    description TEXT,
                    is_automatic BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')
            
            # إنشاء جدول الإعدادات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء فهارس لتحسين الأداء
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_id ON professional_events(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_career_employee_id ON career_history(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_date ON professional_events(event_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_career_date ON career_history(event_date)')
            
            # إدراج الإعدادات الافتراضية
            self._insert_default_settings(cursor)
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"خطأ في إنشاء قاعدة البيانات: {e}")
            return False
    
    def _insert_default_settings(self, cursor: sqlite3.Cursor):
        """
        إدراج الإعدادات الافتراضية
        
        Args:
            cursor: مؤشر قاعدة البيانات
        """
        default_settings = [
            ('allowance_period_months', '12', 'عدد الأشهر للعلاوة السنوية'),
            ('promotion_allowances_6_10', '3', 'عدد العلاوات المطلوبة للترفيع للدرجات 6-10'),
            ('promotion_allowances_2_5', '4', 'عدد العلاوات المطلوبة للترفيع للدرجات 2-5'),
            ('max_commendations_per_year', '3', 'الحد الأقصى لكتب الشكر في السنة'),
            ('max_6month_commendations_career', '2', 'الحد الأقصى لكتب الشكر 6 أشهر في المسيرة'),
            ('notice_penalty_months', '3', 'أشهر العقوبة للفت النظر'),
            ('warning_penalty_months', '6', 'أشهر العقوبة للإنذار'),
            ('reprimand_penalty_months', '12', 'أشهر العقوبة للتوبيخ'),
        ]
        
        for key, value, desc in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, desc))
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        تنفيذ استعلام SELECT
        
        Args:
            query: الاستعلام
            params: المعاملات
            
        Returns:
            قائمة النتائج
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"خطأ في تنفيذ الاستعلام: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        تنفيذ استعلام UPDATE/INSERT/DELETE
        
        Args:
            query: الاستعلام
            params: المعاملات
            
        Returns:
            True إذا تم التنفيذ بنجاح
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"خطأ في تنفيذ التحديث: {e}")
            return False
    
    def get_last_insert_id(self) -> int:
        """
        الحصول على معرف آخر إدراج
        
        Returns:
            معرف آخر إدراج
        """
        conn = self.get_connection()
        return conn.lastrowid
    
    # وظائف خاصة بالموظفين
    def add_employee(self, employee_data: Dict[str, Any]) -> Optional[int]:
        """
        إضافة موظف جديد
        
        Args:
            employee_data: بيانات الموظف
            
        Returns:
            معرف الموظف الجديد أو None في حالة الفشل
        """
        query = '''
            INSERT INTO employees (
                full_name, start_date, last_allowance_date, last_promotion_date,
                promotion_tracker, academic_degree, job_class, job_title,
                job_grade, job_stage, photo_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            employee_data['full_name'],
            employee_data['start_date'],
            employee_data['last_allowance_date'],
            employee_data['last_promotion_date'],
            employee_data['promotion_tracker'],
            employee_data['academic_degree'],
            employee_data['job_class'],
            employee_data['job_title'],
            employee_data['job_grade'],
            employee_data['job_stage'],
            employee_data.get('photo_path', '')
        )
        
        if self.execute_update(query, params):
            return self.get_last_insert_id()
        return None
    
    def get_employee(self, employee_id: int) -> Optional[sqlite3.Row]:
        """
        الحصول على بيانات موظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            بيانات الموظف أو None
        """
        query = "SELECT * FROM employees WHERE id = ?"
        results = self.execute_query(query, (employee_id,))
        return results[0] if results else None
    
    def get_all_employees(self, filters: Dict[str, Any] = None) -> List[sqlite3.Row]:
        """
        الحصول على جميع الموظفين
        
        Args:
            filters: مرشحات البحث
            
        Returns:
            قائمة الموظفين
        """
        query = "SELECT * FROM employees WHERE status = 'active'"
        params = []
        
        if filters:
            if 'job_class' in filters and filters['job_class']:
                query += " AND job_class = ?"
                params.append(filters['job_class'])
            
            if 'search_name' in filters and filters['search_name']:
                query += " AND full_name LIKE ?"
                params.append(f"%{filters['search_name']}%")
        
        query += " ORDER BY full_name"
        return self.execute_query(query, tuple(params))
    
    def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> bool:
        """
        تحديث بيانات موظف
        
        Args:
            employee_id: معرف الموظف
            employee_data: البيانات الجديدة
            
        Returns:
            True إذا تم التحديث بنجاح
        """
        # بناء الاستعلام ديناميكياً
        fields = []
        params = []
        
        for key, value in employee_data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                params.append(value)
        
        if not fields:
            return False
        
        # إضافة تاريخ التحديث
        fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(employee_id)
        
        query = f"UPDATE employees SET {', '.join(fields)} WHERE id = ?"
        return self.execute_update(query, tuple(params))
    
    # وظائف خاصة بالأحداث المهنية
    def add_professional_event(self, event_data: Dict[str, Any]) -> Optional[int]:
        """
        إضافة حدث مهني
        
        Args:
            event_data: بيانات الحدث
            
        Returns:
            معرف الحدث الجديد أو None
        """
        query = '''
            INSERT INTO professional_events (
                employee_id, event_type, event_date, document_number,
                document_date, description, effect_months, effect_type,
                start_date, end_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            event_data['employee_id'],
            event_data['event_type'],
            event_data['event_date'],
            event_data.get('document_number', ''),
            event_data.get('document_date'),
            event_data.get('description', ''),
            event_data.get('effect_months', 0),
            event_data.get('effect_type', 'none'),
            event_data.get('start_date'),
            event_data.get('end_date'),
            event_data.get('notes', '')
        )
        
        if self.execute_update(query, params):
            return self.get_last_insert_id()
        return None
    
    def get_employee_events(self, employee_id: int) -> List[sqlite3.Row]:
        """
        الحصول على أحداث موظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            قائمة الأحداث
        """
        query = '''
            SELECT * FROM professional_events 
            WHERE employee_id = ? 
            ORDER BY event_date DESC
        '''
        return self.execute_query(query, (employee_id,))
    
    # وظائف خاصة بالمسار الوظيفي
    def add_career_event(self, career_data: Dict[str, Any]) -> Optional[int]:
        """
        إضافة حدث في المسار الوظيفي
        
        Args:
            career_data: بيانات الحدث الوظيفي
            
        Returns:
            معرف الحدث الجديد أو None
        """
        query = '''
            INSERT INTO career_history (
                employee_id, event_type, event_date, from_grade, to_grade,
                from_stage, to_stage, description, is_automatic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            career_data['employee_id'],
            career_data['event_type'],
            career_data['event_date'],
            career_data.get('from_grade'),
            career_data.get('to_grade'),
            career_data.get('from_stage'),
            career_data.get('to_stage'),
            career_data.get('description', ''),
            career_data.get('is_automatic', True)
        )
        
        if self.execute_update(query, params):
            return self.get_last_insert_id()
        return None
    
    def get_employee_career_history(self, employee_id: int) -> List[sqlite3.Row]:
        """
        الحصول على المسار الوظيفي للموظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            قائمة أحداث المسار الوظيفي
        """
        query = '''
            SELECT * FROM career_history 
            WHERE employee_id = ? 
            ORDER BY event_date DESC
        '''
        return self.execute_query(query, (employee_id,))
    
    def clear_employee_career_history(self, employee_id: int) -> bool:
        """
        مسح المسار الوظيفي للموظف (للإعادة الحساب)
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            True إذا تم المسح بنجاح
        """
        query = "DELETE FROM career_history WHERE employee_id = ? AND is_automatic = TRUE"
        return self.execute_update(query, (employee_id,))
    
    # وظائف الإعدادات
    def get_setting(self, key: str) -> Optional[str]:
        """
        الحصول على قيمة إعداد
        
        Args:
            key: مفتاح الإعداد
            
        Returns:
            قيمة الإعداد أو None
        """
        query = "SELECT setting_value FROM settings WHERE setting_key = ?"
        results = self.execute_query(query, (key,))
        return results[0]['setting_value'] if results else None
    
    def set_setting(self, key: str, value: str) -> bool:
        """
        تعيين قيمة إعداد
        
        Args:
            key: مفتاح الإعداد
            value: القيمة الجديدة
            
        Returns:
            True إذا تم التعيين بنجاح
        """
        query = '''
            INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        '''
        return self.execute_update(query, (key, value))
    
    def __del__(self):
        """
        تنظيف الموارد عند حذف الكائن
        """
        self.close_connection()

