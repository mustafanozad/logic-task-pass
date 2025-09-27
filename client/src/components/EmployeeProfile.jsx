import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Avatar, Button, Grid, Card, CardContent,
  Tabs, Tab, Timeline, TimelineItem, TimelineSeparator, TimelineConnector,
  TimelineContent, TimelineDot, TimelineOppositeContent, Chip, Dialog,
  DialogTitle, DialogContent, TextField, Alert, IconButton
} from '@mui/material';
import {
  Person, Star, Event, HourglassEmpty, TrendingUp, BookOpen,
  Edit, PhotoCamera, Close
} from '@mui/icons-material';
import axios from 'axios';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';

const EmployeeProfile = ({ employeeId, onClose }) => {
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [editDialog, setEditDialog] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    if (employeeId) {
      fetchEmployeeProfile();
    }
  }, [employeeId]);

  const fetchEmployeeProfile = async () => {
    try {
      const response = await axios.get(`/api/employees/${employeeId}`);
      setEmployee(response.data);
      setEditData({
        jobClass: response.data.jobClass,
        jobTitle: response.data.jobTitle,
        degree: response.data.degree
      });
    } catch (error) {
      console.error('Error fetching employee profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditSave = async () => {
    try {
      await axios.put(`/api/employees/${employeeId}`, editData);
      setEditDialog(false);
      fetchEmployeeProfile(); // إعادة تحميل البيانات
    } catch (error) {
      console.error('Error updating employee:', error);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('profileImage', file);

      try {
        await axios.post(`/api/employees/${employeeId}/upload-image`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        fetchEmployeeProfile();
      } catch (error) {
        console.error('Error uploading image:', error);
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>جاري تحميل الملف الشخصي...</Typography>
      </Box>
    );
  }

  if (!employee) {
    return (
      <Box textAlign="center" py={4}>
        <Typography>لم يتم العثور على الموظف</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* رأس الملف الشخصي */}
      <Paper elevation={4} sx={{ p: 4, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={3} textAlign="center">
            <Box position="relative" display="inline-block">
              <Avatar
                src={employee.profileImage}
                sx={{ width: 120, height: 120, border: '4px solid white' }}
              >
                <Person sx={{ fontSize: 60 }} />
              </Avatar>
              <IconButton
                component="label"
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                  backgroundColor: 'white',
                  '&:hover': { backgroundColor: 'grey.100' }
                }}
              >
                <input
                  hidden
                  accept="image/*"
                  type="file"
                  onChange={handleImageUpload}
                />
                <PhotoCamera />
              </IconButton>
            </Box>
          </Grid>

          <Grid item xs={12} md={6} textAlign="center">
            <Typography variant="h3" component="h1" gutterBottom>
              {employee.fullName}
            </Typography>
            <Typography variant="h6">
              {employee.jobClass} - {employee.jobTitle}
            </Typography>
            <Typography variant="body1">
              {employee.degree}
            </Typography>
            <Chip
              label={employee.status === 'active' ? 'في الخدمة' : 'في إجازة'}
              color={employee.status === 'active' ? 'success' : 'warning'}
              sx={{ mt: 1 }}
            />
          </Grid>

          <Grid item xs={12} md={3} textAlign="center">
            <Button
              variant="contained"
              startIcon={<Edit />}
              onClick={() => setEditDialog(true)}
              sx={{ backgroundColor: 'rgba(255,255,255,0.2)', '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' } }}
            >
              تعديل البيانات
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* المؤشرات الرئيسية */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Star sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="h6" color="primary">الدرجة والمرحلة</Typography>
              <Typography variant="h4">
                الدرجة {employee.grade} - المرحلة {employee.stage}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                تاريخ الاستحقاق: {employee.nextEntitlement?.date ?
                  format(new Date(employee.nextEntitlement.date), 'dd/MM/yyyy', { locale: ar }) :
                  'غير محدد'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Event sx={{ fontSize: 48, color: 'secondary.main', mb: 1 }} />
              <Typography variant="h6" color="secondary">الاستحقاق القادم</Typography>
              <Typography variant="h4">
                {employee.nextEntitlement?.type === 'allowance' ? 'علاوة' : 'ترفيع'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                بتاريخ: {employee.nextEntitlement?.date ?
                  format(new Date(employee.nextEntitlement.date), 'dd/MM/yyyy', { locale: ar }) :
                  'غير محدد'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardContent sx={{ textAlign: 'center' }}>
              <HourglassEmpty sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
              <Typography variant="h6" color="info">الخدمة الفعلية</Typography>
              <Typography variant="h4">
                {employee.serviceYears} سنة، {employee.serviceMonths} شهر، {employee.serviceDays} يوم
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* التبويبات */}
      <Paper elevation={3}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<TrendingUp />} label="المسار الوظيفي" />
          <Tab icon={<BookOpen />} label="الأحداث المهنية" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 && (
            <Timeline position="alternate">
              {employee.careerHistory?.map((event, index) => (
                <TimelineItem key={index}>
                  <TimelineOppositeContent color="text.secondary">
                    {format(new Date(event.date), 'dd/MM/yyyy', { locale: ar })}
                  </TimelineOppositeContent>
                  <TimelineSeparator>
                    <TimelineDot color={event.type === 'promotion' ? 'primary' : 'secondary'}>
                      {event.type === 'promotion' ? <Star /> : <TrendingUp />}
                    </TimelineDot>
                    {index < employee.careerHistory.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Paper elevation={2} sx={{ p: 2 }}>
                      <Typography variant="h6">
                        {event.type === 'promotion' ? 'ترفيع' : 'علاوة سنوية'}
                      </Typography>
                      <Typography>{event.description}</Typography>
                    </Paper>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          )}

          {activeTab === 1 && (
            <Box>
              {employee.professionalEvents?.map((event, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6">{event.type}</Typography>
                    <Typography color="text.secondary">
                      التاريخ: {format(new Date(event.date), 'dd/MM/yyyy', { locale: ar })}
                    </Typography>
                    <Typography>رقم الكتاب: {event.documentNumber}</Typography>
                    <Typography>{event.description}</Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      </Paper>

      {/* نافذة التعديل */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          تعديل البيانات الأساسية
          <IconButton
            onClick={() => setEditDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="صنف الوظيفة"
            value={editData.jobClass || ''}
            onChange={(e) => setEditData({...editData, jobClass: e.target.value})}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="العنوان الوظيفي"
            type="number"
            value={editData.jobTitle || ''}
            onChange={(e) => setEditData({...editData, jobTitle: e.target.value})}
            sx={{ mt: 2 }}
          />
          <TextField
            fullWidth
            label="الشهادة العلمية"
            value={editData.degree || ''}
            onChange={(e) => setEditData({...editData, degree: e.target.value})}
            sx={{ mt: 2 }}
          />
          <Button
            fullWidth
            variant="contained"
            onClick={handleEditSave}
            sx={{ mt: 3 }}
          >
            حفظ التغييرات
          </Button>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default EmployeeProfile;
