#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تحكم الموظفين
Employee Controller

يدير جميع العمليات المتعلقة بالموظفين
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, date

from ..models.employee import Employee, EmployeeFilter
from ..database.database_manager import DatabaseManager
from .calculation_engine import CalculationEngine

class EmployeeController:
    """
    فئة تحكم الموظفين
    تدير جميع العمليات المتعلقة بالموظفين
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        تهيئة تحكم الموظفين
        
        Args:
            db_manager: مدير قاعدة البيانات
        """
        self.db_manager = db_manager
        self.calculation_engine = CalculationEngine(db_manager)
    
    def add_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إضافة موظف جديد
        
        Args:
            employee_data: بيانات الموظف
            
        Returns:
            نتيجة العملية
        """
        try:
            # إنشاء كائن الموظف
            employee = Employee.from_dict(employee_data)
            
            # التحقق من صحة البيانات
            validation_errors = employee.validate()
            if validation_errors:
                return {
                    'success': False,
                    'message': 'خطأ في البيانات',
                    'errors': validation_errors
                }
            
            # إضافة الموظف إلى قاعدة البيانات
            employee_id = self.db_manager.add_employee(employee.to_dict())
            
            if employee_id:
                employee.id = employee_id
                
                # حساب المسار الوظيفي الأولي
                self.calculation_engine.calculate_employee_status(employee)
                
                return {
                    'success': True,
                    'message': 'تم إضافة الموظف بنجاح',
                    'employee_id': employee_id
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في إضافة الموظف إلى قاعدة البيانات'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في إضافة الموظف: {str(e)}'
            }
    
    def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحديث بيانات موظف
        
        Args:
            employee_id: معرف الموظف
            employee_data: البيانات الجديدة
            
        Returns:
            نتيجة العملية
        """
        try:
            # الحصول على الموظف الحالي
            current_employee = self.get_employee(employee_id)
            if not current_employee['success']:
                return current_employee
            
            # تحديث البيانات
            updated_data = current_employee['employee'].to_dict()
            updated_data.update(employee_data)
            
            # إنشاء كائن الموظف المحدث
            updated_employee = Employee.from_dict(updated_data)
            updated_employee.id = employee_id
            
            # التحقق من صحة البيانات
            validation_errors = updated_employee.validate()
            if validation_errors:
                return {
                    'success': False,
                    'message': 'خطأ في البيانات',
                    'errors': validation_errors
                }
            
            # تحديث قاعدة البيانات
            success = self.db_manager.update_employee(employee_id, employee_data)
            
            if success:
                # إعادة حساب المسار الوظيفي
                self.calculation_engine.calculate_employee_status(updated_employee)
                
                return {
                    'success': True,
                    'message': 'تم تحديث بيانات الموظف بنجاح'
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في تحديث بيانات الموظف'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في تحديث الموظف: {str(e)}'
            }
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """
        الحصول على بيانات موظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            بيانات الموظف
        """
        try:
            employee_data = self.db_manager.get_employee(employee_id)
            
            if employee_data:
                employee = Employee.from_dict(dict(employee_data))
                return {
                    'success': True,
                    'employee': employee
                }
            else:
                return {
                    'success': False,
                    'message': 'الموظف غير موجود'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الحصول على بيانات الموظف: {str(e)}'
            }
    
    def get_all_employees(self, filters: EmployeeFilter = None) -> Dict[str, Any]:
        """
        الحصول على جميع الموظفين
        
        Args:
            filters: مرشحات البحث
            
        Returns:
            قائمة الموظفين
        """
        try:
            filter_dict = filters.to_dict() if filters else {}
            employees_data = self.db_manager.get_all_employees(filter_dict)
            
            employees = []
            for emp_data in employees_data:
                employee = Employee.from_dict(dict(emp_data))
                employees.append(employee)
            
            return {
                'success': True,
                'employees': employees,
                'count': len(employees)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الحصول على قائمة الموظفين: {str(e)}',
                'employees': [],
                'count': 0
            }
    
    def get_employee_profile(self, employee_id: int) -> Dict[str, Any]:
        """
        الحصول على الملف الشخصي الكامل للموظف
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            الملف الشخصي الكامل
        """
        try:
            # الحصول على بيانات الموظف
            employee_result = self.get_employee(employee_id)
            if not employee_result['success']:
                return employee_result
            
            employee = employee_result['employee']
            
            # حساب الحالة الحالية
            status_result = self.calculation_engine.calculate_employee_status(employee)
            
            if status_result['status'] == 'success':
                # الحصول على الأحداث المهنية
                professional_events = self.db_manager.get_employee_events(employee_id)
                
                # الحصول على المسار الوظيفي
                career_history = self.db_manager.get_employee_career_history(employee_id)
                
                return {
                    'success': True,
                    'employee': status_result['employee'],
                    'next_entitlement': status_result['next_entitlement'],
                    'effective_service': status_result['effective_service'],
                    'career_timeline': status_result['career_timeline'],
                    'professional_events': professional_events,
                    'career_history': career_history
                }
            else:
                return {
                    'success': False,
                    'message': status_result.get('message', 'خطأ في حساب حالة الموظف')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الحصول على الملف الشخصي: {str(e)}'
            }
    
    def delete_employee(self, employee_id: int) -> Dict[str, Any]:
        """
        حذف موظف (تعطيل الحساب)
        
        Args:
            employee_id: معرف الموظف
            
        Returns:
            نتيجة العملية
        """
        try:
            # تعطيل الموظف بدلاً من الحذف
            success = self.db_manager.update_employee(
                employee_id, 
                {'status': 'inactive'}
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'تم تعطيل حساب الموظف بنجاح'
                }
            else:
                return {
                    'success': False,
                    'message': 'فشل في تعطيل حساب الموظف'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في حذف الموظف: {str(e)}'
            }
    
    def search_employees(self, search_term: str) -> Dict[str, Any]:
        """
        البحث في الموظفين
        
        Args:
            search_term: مصطلح البحث
            
        Returns:
            نتائج البحث
        """
        try:
            filters = EmployeeFilter()
            filters.search_name = search_term
            
            return self.get_all_employees(filters)
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في البحث: {str(e)}',
                'employees': [],
                'count': 0
            }
    
    def get_employees_by_class(self, job_class: str) -> Dict[str, Any]:
        """
        الحصول على الموظفين حسب الصنف الوظيفي
        
        Args:
            job_class: الصنف الوظيفي
            
        Returns:
            قائمة الموظفين
        """
        try:
            filters = EmployeeFilter()
            filters.job_class = job_class
            
            return self.get_all_employees(filters)
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في الحصول على الموظفين: {str(e)}',
                'employees': [],
                'count': 0
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الموظفين
        
        Returns:
            الإحصائيات
        """
        try:
            all_employees = self.get_all_employees()
            
            if not all_employees['success']:
                return all_employees
            
            employees = all_employees['employees']
            
            # حساب الإحصائيات
            stats = {
                'total_employees': len(employees),
                'active_employees': len([e for e in employees if e.status == 'active']),
                'by_class': {},
                'by_grade': {},
                'upcoming_allowances': 0,
                'upcoming_promotions': 0
            }
            
            # إحصائيات حسب الصنف
            for employee in employees:
                job_class = employee.job_class
                if job_class in stats['by_class']:
                    stats['by_class'][job_class] += 1
                else:
                    stats['by_class'][job_class] = 1
            
            # إحصائيات حسب الدرجة
            for employee in employees:
                grade = employee.job_grade
                if grade in stats['by_grade']:
                    stats['by_grade'][grade] += 1
                else:
                    stats['by_grade'][grade] = 1
            
            # حساب الاستحقاقات القادمة (يمكن تطويرها لاحقاً)
            for employee in employees:
                next_event = employee.get_next_event_type()
                if next_event == "علاوة":
                    stats['upcoming_allowances'] += 1
                elif next_event == "ترفيع":
                    stats['upcoming_promotions'] += 1
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في حساب الإحصائيات: {str(e)}'
            }
    
    def recalculate_all_employees(self) -> Dict[str, Any]:
        """
        إعادة حساب جميع الموظفين
        
        Returns:
            تقرير العملية
        """
        try:
            return self.calculation_engine.recalculate_all_employees()
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطأ في إعادة الحساب: {str(e)}'
            }

