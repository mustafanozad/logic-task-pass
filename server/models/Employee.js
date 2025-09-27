const mongoose = require('mongoose');

const employeeSchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  hireDate: { type: Date, required: true },
  lastAllowanceDate: { type: Date, required: true },
  lastPromotionDate: { type: Date, required: true },
  promotionTracker: { type: String, enum: ['4/0', '4/1', '4/2', '4/3', '5/0', '5/1', '5/2', '5/3', '5/4'], required: true },
  degree: { type: String, required: true },
  jobClass: { type: String, required: true },
  jobTitle: { type: Number, required: true },
  grade: { type: Number, required: true },
  stage: { type: Number, required: true },
  profileImage: { type: String },
  status: { type: String, enum: ['active', 'on_leave'], default: 'active' },
  serviceYears: { type: Number, default: 0 },
  serviceMonths: { type: Number, default: 0 },
  serviceDays: { type: Number, default: 0 },
  nextEntitlement: {
    type: { type: String, enum: ['allowance', 'promotion'] },
    date: { type: Date },
    newGrade: { type: Number },
    newStage: { type: Number }
  },
  careerHistory: [{
    type: { type: String, enum: ['allowance', 'promotion'] },
    date: { type: Date },
    description: { type: String },
    grade: { type: Number },
    stage: { type: Number }
  }],
  professionalEvents: [{
    type: { type: String, enum: ['commendation', 'penalty', 'leave', 'degree_upgrade', 'custom'] },
    date: { type: Date },
    documentNumber: { type: String },
    description: { type: String },
    impact: { type: String } // تأثير على المدة
  }]
}, { timestamps: true });

module.exports = mongoose.model('Employee', employeeSchema);
