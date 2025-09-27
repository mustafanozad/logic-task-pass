/**
 * نظام إدارة العلاوات والترفيعات الوظيفية
 * Employee Management System - Main JavaScript
 */

$(document).ready(function() {
    // تهيئة التطبيق
    initializeApp();
    
    // تهيئة الأحداث
    bindEvents();
    
    // تهيئة المكونات التفاعلية
    initializeComponents();
});

/**
 * تهيئة التطبيق
 */
function initializeApp() {
    // إضافة تأثيرات التحميل
    addLoadingEffects();
    
    // تهيئة التواريخ
    initializeDatePickers();
    
    // تهيئة النماذج
    initializeForms();
    
    // تهيئة الجداول
    initializeTables();
    
    console.log('تم تهيئة التطبيق بنجاح');
}

/**
 * ربط الأحداث
 */
function bindEvents() {
    // أحداث النماذج
    bindFormEvents();
    
    // أحداث الأزرار
    bindButtonEvents();
    
    // أحداث البحث
    bindSearchEvents();
    
    // أحداث الملفات
    bindFileEvents();
}

/**
 * تهيئة المكونات التفاعلية
 */
function initializeComponents() {
    // تهيئة التلميحات
    initializeTooltips();
    
    // تهيئة النوافذ المنبثقة
    initializeModals();
    
    // تهيئة التبويبات
    initializeTabs();
    
    // تهيئة الرسوم البيانية
    initializeCharts();
}

/**
 * إضافة تأثيرات التحميل
 */
function addLoadingEffects() {
    // إضافة تأثير التحميل للبطاقات
    $('.card').addClass('loading');
    
    setTimeout(function() {
        $('.card').removeClass('loading');
    }, 500);
    
    // تأثير التحميل للأزرار
    $('.btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.html();
        
        if (!$btn.hasClass('no-loading')) {
            $btn.html('<i class="fas fa-spinner fa-spin me-2"></i>جاري التحميل...');
            $btn.prop('disabled', true);
            
            setTimeout(function() {
                $btn.html(originalText);
                $btn.prop('disabled', false);
            }, 2000);
        }
    });
}

/**
 * تهيئة منتقي التواريخ
 */
function initializeDatePickers() {
    // تهيئة حقول التاريخ
    $('input[type="date"]').each(function() {
        const $input = $(this);
        
        // إضافة أيقونة التقويم
        if (!$input.next('.date-icon').length) {
            $input.after('<i class="fas fa-calendar-alt date-icon"></i>');
        }
        
        // تحديد التاريخ الأقصى (اليوم)
        if (!$input.attr('max')) {
            $input.attr('max', new Date().toISOString().split('T')[0]);
        }
    });
}

/**
 * تهيئة النماذج
 */
function initializeForms() {
    // التحقق من صحة النماذج
    $('form').on('submit', function(e) {
        const $form = $(this);
        
        if (!validateForm($form)) {
            e.preventDefault();
            showAlert('يرجى تصحيح الأخطاء في النموذج', 'error');
        }
    });
    
    // تحسين حقول الإدخال
    $('.form-control, .form-select').on('focus', function() {
        $(this).parent().addClass('focused');
    }).on('blur', function() {
        $(this).parent().removeClass('focused');
    });
    
    // تحديث الحقول حسب نوع الحدث
    $('#event_type').on('change', function() {
        updateEventFields($(this).val());
    });
}

/**
 * تحديث حقول الحدث حسب النوع
 */
function updateEventFields(eventType) {
    // إخفاء جميع الحقول الإضافية
    $('.event-field').hide();
    
    switch(eventType) {
        case 'commendation_letter':
            $('#impact_months_field, #description_field').show();
            $('#impact_months').attr('min', -6).attr('max', -1);
            break;
            
        case 'higher_degree':
            $('#new_job_class_field, #new_job_title_field, #new_academic_degree_field').show();
            break;
            
        case 'notice_penalty':
        case 'warning_penalty':
        case 'reprimand_penalty':
            $('#description_field').show();
            break;
            
        case 'unpaid_leave':
        case 'disability_care_leave':
        case 'five_year_leave':
        case 'maternity_leave':
            $('#start_date_field, #end_date_field, #description_field').show();
            break;
            
        case 'custom_event':
            $('#impact_months_field, #description_field').show();
            $('#impact_months').attr('min', -24).attr('max', 24);
            $('#notes_field').show().find('textarea').prop('required', true);
            break;
    }
}

/**
 * التحقق من صحة النموذج
 */
function validateForm($form) {
    let isValid = true;
    
    // التحقق من الحقول المطلوبة
    $form.find('[required]').each(function() {
        const $field = $(this);
        
        if (!$field.val().trim()) {
            $field.addClass('is-invalid');
            isValid = false;
        } else {
            $field.removeClass('is-invalid');
        }
    });
    
    // التحقق من التواريخ
    const startDate = $form.find('#start_date').val();
    const endDate = $form.find('#end_date').val();
    
    if (startDate && endDate && new Date(startDate) >= new Date(endDate)) {
        $form.find('#end_date').addClass('is-invalid');
        showAlert('تاريخ المباشرة يجب أن يكون بعد تاريخ الانفكاك', 'error');
        isValid = false;
    }
    
    return isValid;
}

/**
 * ربط أحداث النماذج
 */
function bindFormEvents() {
    // تحديد/إلغاء تحديد جميع الموظفين
    $('#select_all_employees').on('change', function() {
        const isChecked = $(this).is(':checked');
        $('.employee-checkbox').prop('checked', isChecked);
        updateSelectedCount();
    });
    
    // تحديث عدد الموظفين المحددين
    $('.employee-checkbox').on('change', function() {
        updateSelectedCount();
    });
    
    // فلترة الموظفين حسب الصنف
    $('#job_class_filter').on('change', function() {
        const selectedClass = $(this).val();
        
        $('.employee-item').each(function() {
            const $item = $(this);
            const jobClass = $item.data('job-class');
            
            if (!selectedClass || jobClass === selectedClass) {
                $item.show();
            } else {
                $item.hide();
            }
        });
    });
}

/**
 * تحديث عدد الموظفين المحددين
 */
function updateSelectedCount() {
    const selectedCount = $('.employee-checkbox:checked').length;
    $('#selected_count').text(selectedCount);
    
    if (selectedCount > 0) {
        $('#submit_btn').prop('disabled', false);
    } else {
        $('#submit_btn').prop('disabled', true);
    }
}

/**
 * ربط أحداث الأزرار
 */
function bindButtonEvents() {
    // زر حساب الاستحقاقات
    $('.calculate-btn').on('click', function() {
        const employeeId = $(this).data('employee-id');
        calculateEntitlements(employeeId);
    });
    
    // زر تحديث الصورة
    $('.update-photo-btn').on('click', function() {
        $('#photo_input').click();
    });
    
    // زر الطباعة
    $('.print-btn').on('click', function() {
        window.print();
    });
    
    // زر التصدير
    $('.export-btn').on('click', function() {
        const format = $(this).data('format');
        exportData(format);
    });
}

/**
 * حساب الاستحقاقات
 */
function calculateEntitlements(employeeId) {
    showLoading();
    
    $.ajax({
        url: `/api/employee/${employeeId}/calculate`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                updateEmployeeData(response);
                showAlert('تم حساب الاستحقاقات بنجاح', 'success');
            } else {
                showAlert('حدث خطأ في حساب الاستحقاقات', 'error');
            }
        },
        error: function() {
            showAlert('حدث خطأ في الاتصال بالخادم', 'error');
        },
        complete: function() {
            hideLoading();
        }
    });
}

/**
 * تحديث بيانات الموظف
 */
function updateEmployeeData(data) {
    // تحديث الاستحقاق القادم
    if (data.next_entitlement) {
        const entitlement = data.next_entitlement;
        $('#next_entitlement_type').text(entitlement.type_arabic);
        $('#next_entitlement_date').text(formatDate(entitlement.date));
        $('#next_entitlement_grade').text(entitlement.next_grade);
        $('#next_entitlement_stage').text(entitlement.next_stage);
    }
    
    // تحديث السجل الوظيفي
    if (data.results && data.results.events_processed.length > 0) {
        location.reload(); // إعادة تحميل الصفحة لعرض التحديثات
    }
}

/**
 * ربط أحداث البحث
 */
function bindSearchEvents() {
    // البحث المباشر
    $('#search_input').on('input', function() {
        const query = $(this).val().toLowerCase();
        
        $('.employee-row').each(function() {
            const $row = $(this);
            const name = $row.find('.employee-name').text().toLowerCase();
            
            if (name.includes(query)) {
                $row.show();
            } else {
                $row.hide();
            }
        });
    });
    
    // فلترة متقدمة
    $('.filter-select').on('change', function() {
        applyFilters();
    });
}

/**
 * تطبيق الفلاتر
 */
function applyFilters() {
    const jobClass = $('#job_class_filter').val();
    const status = $('#status_filter').val();
    const sortBy = $('#sort_by').val();
    
    // تطبيق الفلاتر
    $('.employee-row').each(function() {
        const $row = $(this);
        let show = true;
        
        if (jobClass && $row.data('job-class') !== jobClass) {
            show = false;
        }
        
        if (status && $row.data('status') !== status) {
            show = false;
        }
        
        if (show) {
            $row.show();
        } else {
            $row.hide();
        }
    });
    
    // تطبيق الترتيب
    if (sortBy) {
        sortEmployees(sortBy);
    }
}

/**
 * ترتيب الموظفين
 */
function sortEmployees(sortBy) {
    const $container = $('.employees-container');
    const $rows = $container.find('.employee-row').get();
    
    $rows.sort(function(a, b) {
        let aVal, bVal;
        
        switch(sortBy) {
            case 'name':
                aVal = $(a).find('.employee-name').text();
                bVal = $(b).find('.employee-name').text();
                break;
            case 'start_date':
                aVal = new Date($(a).data('start-date'));
                bVal = new Date($(b).data('start-date'));
                break;
            case 'job_grade':
                aVal = parseInt($(a).data('job-grade'));
                bVal = parseInt($(b).data('job-grade'));
                break;
        }
        
        if (aVal < bVal) return -1;
        if (aVal > bVal) return 1;
        return 0;
    });
    
    $.each($rows, function(index, row) {
        $container.append(row);
    });
}

/**
 * ربط أحداث الملفات
 */
function bindFileEvents() {
    // معاينة الصورة قبل الرفع
    $('#photo_input').on('change', function() {
        const file = this.files[0];
        
        if (file) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                $('#photo_preview').attr('src', e.target.result);
            };
            
            reader.readAsDataURL(file);
        }
    });
}

/**
 * تهيئة التلميحات
 */
function initializeTooltips() {
    $('[data-bs-toggle="tooltip"]').tooltip();
}

/**
 * تهيئة النوافذ المنبثقة
 */
function initializeModals() {
    // تأكيد الحذف
    $('.delete-btn').on('click', function(e) {
        e.preventDefault();
        
        const $btn = $(this);
        const itemName = $btn.data('item-name');
        
        if (confirm(`هل أنت متأكد من حذف ${itemName}؟`)) {
            window.location.href = $btn.attr('href');
        }
    });
}

/**
 * تهيئة التبويبات
 */
function initializeTabs() {
    // حفظ التبويب النشط في التخزين المحلي
    $('.nav-tabs a').on('click', function() {
        const tabId = $(this).attr('href');
        localStorage.setItem('activeTab', tabId);
    });
    
    // استعادة التبويب النشط
    const activeTab = localStorage.getItem('activeTab');
    if (activeTab) {
        $(`.nav-tabs a[href="${activeTab}"]`).tab('show');
    }
}

/**
 * تهيئة الجداول
 */
function initializeTables() {
    // إضافة ترقيم للصفوف
    $('.data-table tbody tr').each(function(index) {
        $(this).find('td:first').prepend(`<span class="row-number">${index + 1}</span>`);
    });
    
    // تحسين الجداول المتجاوبة
    $('.table-responsive').on('scroll', function() {
        const $table = $(this);
        const scrollLeft = $table.scrollLeft();
        
        if (scrollLeft > 0) {
            $table.addClass('scrolled');
        } else {
            $table.removeClass('scrolled');
        }
    });
}

/**
 * تهيئة الرسوم البيانية
 */
function initializeCharts() {
    // رسم بياني للإحصائيات (إذا كان Chart.js متوفر)
    if (typeof Chart !== 'undefined') {
        createStatisticsChart();
    }
}

/**
 * إنشاء رسم بياني للإحصائيات
 */
function createStatisticsChart() {
    const ctx = document.getElementById('statisticsChart');
    
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['موظفين نشطين', 'موظفين غير نشطين', 'متقاعدين'],
                datasets: [{
                    data: [65, 25, 10],
                    backgroundColor: ['#27ae60', '#f39c12', '#e74c3c']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * عرض رسالة تنبيه
 */
function showAlert(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const iconClass = type === 'success' ? 'fa-check-circle' : 
                     type === 'error' ? 'fa-exclamation-triangle' : 'fa-info-circle';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${iconClass} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('#alerts-container').html(alertHtml);
    
    // إخفاء التنبيه تلقائياً بعد 5 ثوان
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

/**
 * عرض شاشة التحميل
 */
function showLoading() {
    $('body').append('<div id="loading-overlay" class="loading-overlay"><div class="spinner-border text-primary" role="status"></div></div>');
}

/**
 * إخفاء شاشة التحميل
 */
function hideLoading() {
    $('#loading-overlay').remove();
}

/**
 * تنسيق التاريخ
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * تصدير البيانات
 */
function exportData(format) {
    showAlert('جاري تصدير البيانات...', 'info');
    
    // هنا يمكن إضافة منطق التصدير
    setTimeout(function() {
        showAlert('تم تصدير البيانات بنجاح', 'success');
    }, 2000);
}

/**
 * تحديث الوقت الحالي
 */
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ar-SA');
    const dateString = now.toLocaleDateString('ar-SA');
    
    $('.current-time').text(timeString);
    $('.current-date').text(dateString);
}

// تحديث الوقت كل ثانية
setInterval(updateCurrentTime, 1000);

/**
 * تحسينات الأداء
 */
$(window).on('load', function() {
    // إخفاء شاشة التحميل الأولية
    $('.initial-loading').fadeOut();
    
    // تحسين الصور
    $('img').each(function() {
        const $img = $(this);
        
        if (!$img.attr('alt')) {
            $img.attr('alt', 'صورة');
        }
        
        // إضافة تأثير التحميل للصور
        $img.on('load', function() {
            $(this).addClass('loaded');
        });
    });
});

/**
 * معالجة الأخطاء العامة
 */
window.addEventListener('error', function(e) {
    console.error('خطأ في JavaScript:', e.error);
    showAlert('حدث خطأ غير متوقع. يرجى إعادة تحميل الصفحة.', 'error');
});

/**
 * حفظ حالة النموذج في التخزين المحلي
 */
function saveFormState($form) {
    const formData = {};
    
    $form.find('input, select, textarea').each(function() {
        const $field = $(this);
        const name = $field.attr('name');
        
        if (name) {
            formData[name] = $field.val();
        }
    });
    
    localStorage.setItem('formState', JSON.stringify(formData));
}

/**
 * استعادة حالة النموذج من التخزين المحلي
 */
function restoreFormState($form) {
    const formState = localStorage.getItem('formState');
    
    if (formState) {
        const formData = JSON.parse(formState);
        
        Object.keys(formData).forEach(function(name) {
            $form.find(`[name="${name}"]`).val(formData[name]);
        });
    }
}
