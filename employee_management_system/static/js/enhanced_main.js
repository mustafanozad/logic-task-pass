/**
 * نظام إدارة العلاوات والترفيعات - JavaScript الرئيسي
 * Enhanced Employee Management System - Main JavaScript
 */

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
});

/**
 * تهيئة النظام
 */
function initializeSystem() {
    // تفعيل التلميحات
    initializeTooltips();
    
    // تفعيل النوافذ المنبثقة
    initializeModals();
    
    // تفعيل الرسوم المتحركة
    initializeAnimations();
    
    // تفعيل التحقق من النماذج
    initializeFormValidation();
    
    // تفعيل البحث التلقائي
    initializeAutoSearch();
    
    console.log('تم تهيئة النظام بنجاح');
}

/**
 * تفعيل التلميحات
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * تفعيل النوافذ المنبثقة
 */
function initializeModals() {
    const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.map(function (modalTriggerEl) {
        return new bootstrap.Modal(modalTriggerEl);
    });
}

/**
 * تفعيل الرسوم المتحركة
 */
function initializeAnimations() {
    // إضافة تأثير الظهور التدريجي للبطاقات
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // تأثير التمرير السلس
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * تفعيل التحقق من النماذج
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // إظهار رسالة خطأ
                showAlert('يرجى ملء جميع الحقول المطلوبة بشكل صحيح', 'error');
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * تفعيل البحث التلقائي
 */
function initializeAutoSearch() {
    const searchInputs = document.querySelectorAll('.auto-search');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this.dataset.target);
            }, 500);
        });
    });
}

/**
 * تنفيذ البحث
 */
function performSearch(query, target) {
    if (!query || query.length < 2) return;
    
    const targetElement = document.querySelector(target);
    if (!targetElement) return;
    
    // إظهار مؤشر التحميل
    showLoadingIndicator(targetElement);
    
    // تنفيذ البحث (يمكن تخصيصه حسب الحاجة)
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data, targetElement);
        })
        .catch(error => {
            console.error('خطأ في البحث:', error);
            hideLoadingIndicator(targetElement);
        });
}

/**
 * عرض نتائج البحث
 */
function displaySearchResults(data, targetElement) {
    hideLoadingIndicator(targetElement);
    
    if (data.results && data.results.length > 0) {
        let html = '';
        data.results.forEach(result => {
            html += createSearchResultItem(result);
        });
        targetElement.innerHTML = html;
    } else {
        targetElement.innerHTML = '<div class="text-center text-muted py-3">لا توجد نتائج</div>';
    }
}

/**
 * إنشاء عنصر نتيجة البحث
 */
function createSearchResultItem(result) {
    return `
        <div class="search-result-item p-3 border-bottom">
            <h6 class="mb-1">${result.title}</h6>
            <p class="mb-1 text-muted">${result.description}</p>
            <small class="text-muted">${result.category}</small>
        </div>
    `;
}

/**
 * إظهار مؤشر التحميل
 */
function showLoadingIndicator(element) {
    element.innerHTML = `
        <div class="text-center py-3">
            <i class="fas fa-spinner fa-spin fa-2x text-primary"></i>
            <p class="mt-2 text-muted">جاري البحث...</p>
        </div>
    `;
}

/**
 * إخفاء مؤشر التحميل
 */
function hideLoadingIndicator(element) {
    const loadingIndicator = element.querySelector('.fa-spinner');
    if (loadingIndicator) {
        loadingIndicator.closest('.text-center').remove();
    }
}

/**
 * إظهار تنبيه
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertClass = type === 'error' ? 'alert-danger' : 
                     type === 'success' ? 'alert-success' : 
                     type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alertIcon = type === 'error' ? 'fa-exclamation-triangle' : 
                     type === 'success' ? 'fa-check-circle' : 
                     type === 'warning' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    const alertHTML = `
        <div id="${alertId}" class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${alertIcon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // إزالة التنبيه تلقائياً بعد المدة المحددة
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, duration);
}

/**
 * إنشاء حاوي التنبيهات
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * تأكيد الحذف
 */
function confirmDelete(message = 'هل أنت متأكد من الحذف؟') {
    return new Promise((resolve) => {
        const modal = createConfirmModal(message);
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.querySelector('.btn-danger').addEventListener('click', () => {
            resolve(true);
            bsModal.hide();
        });
        
        modal.querySelector('.btn-secondary').addEventListener('click', () => {
            resolve(false);
            bsModal.hide();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    });
}

/**
 * إنشاء نافذة التأكيد
 */
function createConfirmModal(message) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        تأكيد العملية
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p class="mb-0">${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                    <button type="button" class="btn btn-danger">تأكيد</button>
                </div>
            </div>
        </div>
    `;
    return modal;
}

/**
 * تحميل البيانات بشكل غير متزامن
 */
async function loadData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('خطأ في تحميل البيانات:', error);
        showAlert('خطأ في تحميل البيانات', 'error');
        throw error;
    }
}

/**
 * حفظ البيانات
 */
async function saveData(url, data, method = 'POST') {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('تم الحفظ بنجاح', 'success');
        } else {
            showAlert(result.message || 'خطأ في الحفظ', 'error');
        }
        
        return result;
    } catch (error) {
        console.error('خطأ في حفظ البيانات:', error);
        showAlert('خطأ في حفظ البيانات', 'error');
        throw error;
    }
}

/**
 * تنسيق التاريخ
 */
function formatDate(date, format = 'YYYY-MM-DD') {
    if (!date) return '';
    
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    
    switch (format) {
        case 'YYYY-MM-DD':
            return `${year}-${month}-${day}`;
        case 'DD/MM/YYYY':
            return `${day}/${month}/${year}`;
        case 'DD-MM-YYYY':
            return `${day}-${month}-${year}`;
        default:
            return `${year}-${month}-${day}`;
    }
}

/**
 * تنسيق الأرقام
 */
function formatNumber(number, decimals = 0) {
    if (isNaN(number)) return '0';
    
    return new Intl.NumberFormat('ar-SA', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(number);
}

/**
 * التحقق من صحة البريد الإلكتروني
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * التحقق من صحة رقم الهاتف
 */
function validatePhone(phone) {
    const re = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return re.test(phone);
}

/**
 * نسخ النص إلى الحافظة
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('تم نسخ النص', 'success', 2000);
    } catch (error) {
        console.error('خطأ في النسخ:', error);
        showAlert('خطأ في نسخ النص', 'error');
    }
}

/**
 * طباعة الصفحة
 */
function printPage() {
    window.print();
}

/**
 * تصدير البيانات إلى CSV
 */
function exportToCSV(data, filename = 'data.csv') {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * تحويل البيانات إلى CSV
 */
function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

/**
 * تحديث الوقت الحالي
 */
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleString('ar-SA');
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

// تحديث الوقت كل ثانية
setInterval(updateCurrentTime, 1000);

/**
 * إدارة الوضع المظلم
 */
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.contains('dark-mode');
    
    if (isDark) {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
    } else {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
    }
}

// تطبيق الوضع المظلم المحفوظ
document.addEventListener('DOMContentLoaded', function() {
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'true') {
        document.body.classList.add('dark-mode');
    }
});

/**
 * إدارة الإشعارات
 */
class NotificationManager {
    constructor() {
        this.notifications = [];
        this.container = this.createContainer();
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    show(message, type = 'info', duration = 5000) {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);
        this.notifications.push(notification);
        
        // إزالة الإشعار بعد المدة المحددة
        setTimeout(() => {
            this.remove(notification);
        }, duration);
        
        return notification;
    }
    
    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show mb-2`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="notificationManager.remove(this.parentElement)"></button>
        `;
        return notification;
    }
    
    remove(notification) {
        if (notification && notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 150);
        }
    }
    
    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
}

// إنشاء مدير الإشعارات العام
const notificationManager = new NotificationManager();

// تصدير الدوال للاستخدام العام
window.showAlert = showAlert;
window.confirmDelete = confirmDelete;
window.loadData = loadData;
window.saveData = saveData;
window.formatDate = formatDate;
window.formatNumber = formatNumber;
window.validateEmail = validateEmail;
window.validatePhone = validatePhone;
window.copyToClipboard = copyToClipboard;
window.printPage = printPage;
window.exportToCSV = exportToCSV;
window.toggleDarkMode = toggleDarkMode;
window.notificationManager = notificationManager;

