# نظام إدارة العلاوات والترفيعات الوظيفية
## Employee Promotion and Allowance Management System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

نظام شامل ومتطور لأتمتة وحوسبة العمليات المعقدة المتعلقة بحساب العلاوات السنوية والترفيعات الوظيفية للموظفين من الكادر التدريسي والإداري.

## 🌟 المميزات الرئيسية

### 📊 إدارة شاملة للموظفين
- إضافة وتعديل بيانات الموظفين
- تتبع المسار الوظيفي الكامل
- إدارة الصور الشخصية
- فلترة وبحث متقدم

### 🧮 محرك ذكي للحسابات
- حساب تلقائي للعلاوات والترفيعات
- تطبيق تأثير الأحداث المهنية
- معالجة القواعد المعقدة للترفيع
- إعادة حساب تلقائية عند إضافة أحداث بتواريخ قديمة

### 📈 تتبع الأحداث المهنية
- كتب الشكر والتقدير
- العقوبات الإدارية
- الإجازات الطويلة
- الحصول على شهادات عليا
- الأحداث المخصصة

### 🎨 واجهة عصرية وجميلة
- تصميم متجاوب يعمل على جميع الأجهزة
- أيقونات كبيرة وواضحة
- ألوان وتأثيرات جذابة
- تجربة مستخدم ممتازة

## 🚀 التقنيات المستخدمة

### Backend
- **Python 3.8+** - لغة البرمجة الأساسية
- **Flask 2.3** - إطار العمل الرئيسي
- **SQLAlchemy** - ORM لقاعدة البيانات
- **Flask-WTF** - معالجة النماذج والتحقق
- **Python-dateutil** - معالجة التواريخ المتقدمة

### Frontend
- **Bootstrap 5.3 RTL** - إطار العمل للواجهة
- **Font Awesome 6** - الأيقونات
- **jQuery 3.7** - التفاعل والـ AJAX
- **Cairo Font** - الخط العربي

### Database
- **SQLite** - قاعدة البيانات (قابلة للتطوير لـ PostgreSQL/MySQL)

## 📋 متطلبات النظام

- Python 3.8 أو أحدث
- pip (مدير الحزم)
- متصفح ويب حديث

## ⚙️ التثبيت والتشغيل

### 1. استنساخ المشروع
```bash
git clone https://github.com/your-username/employee-management-system.git
cd employee-management-system
```

### 2. إنشاء بيئة افتراضية
```bash
python -m venv venv

# على Windows
venv\Scripts\activate

# على macOS/Linux
source venv/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. تهيئة قاعدة البيانات
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 5. تشغيل التطبيق
```bash
python app.py
```

سيكون التطبيق متاحاً على: `http://localhost:5000`

## 📖 دليل الاستخدام

### إضافة موظف جديد
1. انتقل إلى "إضافة موظف جديد"
2. املأ البيانات الأساسية والوظيفية
3. حدد التواريخ المهمة
4. اختر مؤشر تتبع الترفيع المناسب
5. احفظ البيانات

### إدارة الأحداث المهنية
1. انتقل إلى "الأحداث المهنية" > "إضافة حدث مهني"
2. اختر الموظفين المستهدفين
3. حدد نوع الحدث وتفاصيله
4. احفظ الحدث

### عرض ملف الموظف
1. انتقل إلى قائمة الموظفين
2. اضغط على "عرض الملف" بجانب اسم الموظف
3. ستظهر جميع التفاصيل والمسار الوظيفي

## 🔧 قواعد النظام

### قواعد الترفيع
- **الدرجات 10-6**: 3 علاوات + 1 ترفيع (مؤشر X/4)
- **الدرجات 5-2**: 4 علاوات + 1 ترفيع (مؤشر X/5)
- **الدرجة الأولى**: علاوات فقط بدون ترفيع

### قواعد كتب الشكر
- حد أقصى 3 كتب شكر عادية في السنة
- يمكن إضافة كتاب رابع إذا كان بـ 6 أشهر
- حد أقصى كتابين بـ 6 أشهر طوال المسيرة الوظيفية

### تأثير العقوبات
- **لفت نظر**: +3 أشهر
- **إنذار**: +6 أشهر
- **توبيخ**: +12 شهر

## 🏗️ هيكل المشروع

```
employee_management_system/
├── app.py                 # التطبيق الرئيسي
├── requirements.txt       # المتطلبات
├── README.md             # التوثيق
├── backend/              # الكود الخلفي
│   ├── models.py         # نماذج قاعدة البيانات
│   ├── forms.py          # نماذج الإدخال
│   └── calculation_engine.py  # المحرك الذكي
├── templates/            # قوالب HTML
│   ├── base.html         # القالب الأساسي
│   ├── index.html        # الصفحة الرئيسية
│   └── employees/        # صفحات الموظفين
└── static/               # الملفات الثابتة
    ├── css/              # ملفات الأنماط
    ├── js/               # ملفات JavaScript
    └── images/           # الصور
```

## 🔄 API Endpoints

### الموظفين
- `GET /` - الصفحة الرئيسية
- `GET /employees` - قائمة الموظفين
- `GET /employee/add` - إضافة موظف جديد
- `POST /employee/add` - حفظ موظف جديد
- `GET /employee/<id>` - ملف الموظف
- `GET /employee/<id>/edit` - تعديل الموظف

### الأحداث المهنية
- `GET /events` - قائمة الأحداث
- `GET /event/add` - إضافة حدث جديد
- `POST /event/add` - حفظ حدث جديد

### API
- `GET /api/employee/<id>/calculate` - حساب الاستحقاقات

## 🧪 الاختبار

```bash
# تشغيل الاختبارات (عند توفرها)
python -m pytest tests/
```

## 📝 المساهمة

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المشروع
2. إنشاء فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push للفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## 🐛 الإبلاغ عن الأخطاء

إذا وجدت خطأ، يرجى فتح Issue جديد مع:
- وصف مفصل للخطأ
- خطوات إعادة الإنتاج
- لقطات شاشة (إن أمكن)
- معلومات البيئة (نظام التشغيل، إصدار Python، إلخ)

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 👥 الفريق

- **المطور الرئيسي**: [اسمك هنا]
- **التصميم**: [اسم المصمم]
- **الاختبار**: [اسم المختبر]

## 🙏 شكر وتقدير

- [Flask](https://flask.palletsprojects.com/) - إطار العمل الرائع
- [Bootstrap](https://getbootstrap.com/) - للواجهة الجميلة
- [Font Awesome](https://fontawesome.com/) - للأيقونات الرائعة
- [Cairo Font](https://fonts.google.com/specimen/Cairo) - للخط العربي الجميل

## 📞 التواصل

- البريد الإلكتروني: [your-email@example.com]
- LinkedIn: [your-linkedin-profile]
- Twitter: [@your-twitter-handle]

---

<div align="center">
  <p>صُنع بـ ❤️ في العراق</p>
  <p>Made with ❤️ in Iraq</p>
</div>
