import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Grid, TextField, Button, FormControl,
  InputLabel, Select, MenuItem, Checkbox, FormControlLabel,
  Alert, Chip, ListItemText, Dialog, DialogTitle, DialogContent,
  IconButton, Autocomplete
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ar } from 'date-fns/locale';
import { Close, Add } from '@mui/icons-material';
import axios from 'axios';

const EVENT_TYPES = {
  commendation: { label: 'كتاب شكر وتقدير', reductionRequired: true },
  warning_penalty: { label: 'عقوبة إنذار', impact: 'إضافة 6 أشهر' },
  reprimand_penalty: { label: 'عقوبة توبيخ', impact: 'إضافة 12 شهر' },
  notice_penalty: { label: 'عقوبة لفت نظر', impact: 'إضافة 3 أشهر' },
  degree_upgrade: { label: 'الحصول على شهادة أعلى', impact: 'تقليل 12 شهر' },
  leave_no_pay: { label: 'إجازة بدون راتب', datesRequired: true },
  leave_disabled: { label: 'إجازة رعاية المعاقين', datesRequired: true },
  leave_5_years: { label: 'إجازة 5 سنوات', datesRequired: true },
  leave_maternity: { label: 'إجازة أمومة', datesRequired: true },
  custom: { label: 'حدث مخصص', customFields: true }
};

const AddEvent = ({ open, onClose, onEventAdded }) => {
  const [employees, setEmployees] = useState([]);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [eventData, setEventData] = useState({
    type: '',
    documentNumber: '',
    documentDate: null,
    notes: '',
    reductionPeriod: '',
    startDate: null,
    endDate: null,
    adjustmentType: 'add',
    adjustmentMonths: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (open) {
      fetchEmployees();
      resetForm();
    }
  }, [open]);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('/api/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const resetForm = () => {
    setSelectedEmployees([]);
    setSelectAll(false);
    setEventData({
      type: '',
      documentNumber: '',
      documentDate: null,
      notes: '',
      reductionPeriod: '',
      startDate: null,
      endDate: null,
      adjustmentType: 'add',
      adjustmentMonths: ''
    });
    setError('');
    setSuccess('');
  };

  const handleEmployeeToggle = (employeeId) => {
    setSelectedEmployees(prev =>
      prev.includes(employeeId)
        ? prev.filter(id => id !== employeeId)
        : [...prev, employeeId]
    );
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedEmployees([]);
    } else {
      setSelectedEmployees(employees.map(emp => emp._id));
    }
    setSelectAll(!selectAll);
  };

  const validateForm = () => {
    if (selectedEmployees.length === 0) {
      setError('يجب اختيار موظف واحد على الأقل');
      return false;
    }
    if (!eventData.type) {
      setError('يجب اختيار نوع الحدث');
      return false;
    }
    if (!eventData.documentNumber) {
      setError('يجب إدخال رقم الكتاب الرسمي');
      return false;
    }
    if (!eventData.documentDate) {
      setError('يجب إدخال تاريخ الكتاب الرسمي');
      return false;
    }

    const eventType = EVENT_TYPES[eventData.type];
    if (eventType?.reductionRequired && !eventData.reductionPeriod) {
      setError('يجب إدخال مدة التقليص لكتب الشكر');
      return false;
    }
    if (eventType?.datesRequired && (!eventData.startDate || !eventData.endDate)) {
      setError('يجب إدخال تاريخي الانفكاك والمباشرة للإجازات');
      return false;
    }
    if (eventType?.customFields && !eventData.adjustmentMonths) {
      setError('يجب إدخال عدد الأشهر للحدث المخصص');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const eventsToCreate = selectedEmployees.map(employeeId => ({
        employeeId,
        ...eventData
      }));

      await Promise.all(
        eventsToCreate.map(event =>
          axios.post('/api/events', event)
        )
      );

      setSuccess(`تم إضافة الحدث لـ ${selectedEmployees.length} موظف بنجاح`);
      onEventAdded && onEventAdded();

      // تشغيل المحرك الذكي لكل موظف
      await Promise.all(
        selectedEmployees.map(employeeId =>
          axios.post(`/api/employees/${employeeId}/process`)
        )
      );

      setTimeout(() => {
        onClose();
      }, 2000);

    } catch (err) {
      setError(err.response?.data?.message || 'حدث خطأ في إضافة الحدث');
    } finally {
      setLoading(false);
    }
  };

  const renderAdditionalFields = () => {
    const eventType = EVENT_TYPES[eventData.type];
    if (!eventType) return null;

    return (
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {eventType.reductionRequired && (
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>مدة التقليص</InputLabel>
              <Select
                value={eventData.reductionPeriod}
                onChange={(e) => setEventData({...eventData, reductionPeriod: e.target.value})}
              >
                <MenuItem value="1">شهر واحد</MenuItem>
                <MenuItem value="2">شهرين</MenuItem>
                <MenuItem value="3">3 أشهر</MenuItem>
                <MenuItem value="4">4 أشهر</MenuItem>
                <MenuItem value="5">5 أشهر</MenuItem>
                <MenuItem value="6">6 أشهر</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        )}

        {eventType.datesRequired && (
          <>
            <Grid item xs={12} md={6}>
              <DatePicker
                label="تاريخ الانفكاك"
                value={eventData.startDate}
                onChange={(date) => setEventData({...eventData, startDate: date})}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <DatePicker
                label="تاريخ المباشرة"
                value={eventData.endDate}
                onChange={(date) => setEventData({...eventData, endDate: date})}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>
          </>
        )}

        {eventType.customFields && (
          <>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>نوع التعديل</InputLabel>
                <Select
                  value={eventData.adjustmentType}
                  onChange={(e) => setEventData({...eventData, adjustmentType: e.target.value})}
                >
                  <MenuItem value="add">إضافة مدة</MenuItem>
                  <MenuItem value="subtract">طرح مدة</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="عدد الأشهر"
                type="number"
                value={eventData.adjustmentMonths}
                onChange={(e) => setEventData({...eventData, adjustmentMonths: e.target.value})}
              />
            </Grid>
          </>
        )}
      </Grid>
    );
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ar}>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          إضافة حدث مهني جديد
          <IconButton
            onClick={onClose}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

            {/* اختيار الموظفين */}
            <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>اختيار الموظفين</Typography>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectAll}
                    onChange={handleSelectAll}
                  />
                }
                label="تحديد الكل"
              />
              <Box sx={{ maxHeight: 200, overflow: 'auto', mt: 1 }}>
                {employees.map(employee => (
                  <FormControlLabel
                    key={employee._id}
                    control={
                      <Checkbox
                        checked={selectedEmployees.includes(employee._id)}
                        onChange={() => handleEmployeeToggle(employee._id)}
                      />
                    }
                    label={`${employee.fullName} - ${employee.jobClass}`}
                  />
                ))}
              </Box>
              {selectedEmployees.length > 0 && (
                <Chip
                  label={`تم اختيار ${selectedEmployees.length} موظف`}
                  color="primary"
                  sx={{ mt: 1 }}
                />
              )}
            </Paper>

            {/* بيانات الحدث */}
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>نوع الحدث</InputLabel>
                  <Select
                    value={eventData.type}
                    onChange={(e) => setEventData({...eventData, type: e.target.value})}
                  >
                    {Object.entries(EVENT_TYPES).map(([key, value]) => (
                      <MenuItem key={key} value={key}>
                        {value.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="رقم الكتاب الرسمي"
                  value={eventData.documentNumber}
                  onChange={(e) => setEventData({...eventData, documentNumber: e.target.value})}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <DatePicker
                  label="تاريخ الكتاب الرسمي"
                  value={eventData.documentDate}
                  onChange={(date) => setEventData({...eventData, documentDate: date})}
                  renderInput={(params) => <TextField {...params} fullWidth required />}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="ملاحظات"
                  multiline
                  rows={3}
                  value={eventData.notes}
                  onChange={(e) => setEventData({...eventData, notes: e.target.value})}
                />
              </Grid>
            </Grid>

            {/* الحقول الإضافية */}
            {renderAdditionalFields()}

            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              fullWidth
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? 'جاري الحفظ...' : 'حفظ الحدث'}
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </LocalizationProvider>
  );
};

export default AddEvent;
