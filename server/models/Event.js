const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
  employeeId: { type: mongoose.Schema.Types.ObjectId, ref: 'Employee', required: true },
  type: {
    type: String,
    enum: [
      'commendation', // كتاب شكر
      'warning_penalty', // عقوبة إنذار
      'reprimand_penalty', // عقوبة توبيخ
      'notice_penalty', // عقوبة لفت نظر
      'degree_upgrade', // الحصول على شهادة أعلى
      'leave_no_pay', // إجازة بدون راتب
      'leave_disabled', // إجازة رعاية المعاقين
      'leave_5_years', // إجازة 5 سنوات
      'leave_maternity', // إجازة أمومة
      'custom' // حدث مخصص
    ],
    required: true
  },
  documentNumber: { type: String, required: true },
  documentDate: { type: Date, required: true },
  notes: { type: String },
  reductionPeriod: { type: Number }, // للكتب الشكر (بالأشهر)
  startDate: { type: Date }, // للإجازات
  endDate: { type: Date }, // للإجازات
  adjustmentType: { type: String, enum: ['add', 'subtract'] }, // للأحداث المخصصة
  adjustmentMonths: { type: Number }, // للأحداث المخصصة
  impact: { type: String }, // وصف التأثير على الحسابات
  applied: { type: Boolean, default: false } // هل تم تطبيق التأثير على الحسابات
}, { timestamps: true });

module.exports = mongoose.model('Event', eventSchema);
