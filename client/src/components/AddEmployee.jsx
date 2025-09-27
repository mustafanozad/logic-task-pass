import React, { useState } from 'react';
import {
  Box, TextField, Button, Typography, Paper, Grid,
  FormControl, InputLabel, Select, MenuItem, Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ar } from 'date-fns/locale';
import axios from 'axios';

const AddEmployee = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    hireDate: null,
    lastAllowanceDate: null,
    lastPromotionDate: null,
    promotionTracker: '',
    degree: '',
    jobClass: '',
    jobTitle: '',
    grade: '',
    stage: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post('/api/employees', formData);
      setSuccess('تم إضافة الموظف بنجاح!');
      setFormData({
        fullName: '',
        hireDate: null,
        lastAllowanceDate: null,
        lastPromotionDate: null,
        promotionTracker: '',
        degree: '',
        jobClass: '',
        jobTitle: '',
        grade: '',
        stage: ''
      });
    } catch (err) {
      setError(err.response?.data?.message || 'حدث خطأ في إضافة الموظف');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ar}>
      <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" color="primary">
          إضافة موظف جديد
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="الاسم الرباعي"
                value={formData.fullName}
                onChange={(e) => handleChange('fullName', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <DatePicker
                label="تاريخ المباشرة بالوظيفة"
                value={formData.hireDate}
                onChange={(date) => handleChange('hireDate', date)}
                renderInput={(params) => <TextField {...params} fullWidth required />}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <DatePicker
                label="تاريخ آخر استحقاق للعلاوة"
                value={formData.lastAllowanceDate}
                onChange={(date) => handleChange('lastAllowanceDate', date)}
                renderInput={(params) => <TextField {...params} fullWidth required />}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <DatePicker
                label="تاريخ آخر استحقاق للترفيع"
                value={formData.lastPromotionDate}
                onChange={(date) => handleChange('lastPromotionDate', date)}
                renderInput={(params) => <TextField {...params} fullWidth required />}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth required>
                <InputLabel>مؤشر تتبع العلاوة</InputLabel>
                <Select
                  value={formData.promotionTracker}
                  onChange={(e) => handleChange('promotionTracker', e.target.value)}
                >
                  <MenuItem value="4/0">4/0</MenuItem>
                  <MenuItem value="4/1">4/1</MenuItem>
                  <MenuItem value="4/2">4/2</MenuItem>
                  <MenuItem value="4/3">4/3</MenuItem>
                  <MenuItem value="5/0">5/0</MenuItem>
                  <MenuItem value="5/1">5/1</MenuItem>
                  <MenuItem value="5/2">5/2</MenuItem>
                  <MenuItem value="5/3">5/3</MenuItem>
                  <MenuItem value="5/4">5/4</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="الشهادة العلمية"
                value={formData.degree}
                onChange={(e) => handleChange('degree', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="صنف الوظيفة"
                value={formData.jobClass}
                onChange={(e) => handleChange('jobClass', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="العنوان الوظيفي"
                type="number"
                value={formData.jobTitle}
                onChange={(e) => handleChange('jobTitle', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="الدرجة الوظيفية"
                type="number"
                value={formData.grade}
                onChange={(e) => handleChange('grade', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="المرحلة"
                type="number"
                value={formData.stage}
                onChange={(e) => handleChange('stage', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                fullWidth
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? 'جاري الحفظ...' : 'حفظ الموظف'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </LocalizationProvider>
  );
};

export default AddEmployee;
