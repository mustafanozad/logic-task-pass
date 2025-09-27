import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Button, TextField, FormControl, InputLabel, Select,
  MenuItem, Chip, Avatar, IconButton, Tooltip
} from '@mui/material';
import { Person, FilterList, Sort } from '@mui/icons-material';
import axios from 'axios';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';

const EmployeeList = ({ onViewProfile }) => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    jobClass: '',
    hireDateSort: '',
    nameSearch: ''
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [employees, filters]);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('/api/employees');
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...employees];

    // فلترة حسب صنف الوظيفة
    if (filters.jobClass) {
      filtered = filtered.filter(emp => emp.jobClass === filters.jobClass);
    }

    // فلترة حسب البحث في الاسم
    if (filters.nameSearch) {
      filtered = filtered.filter(emp =>
        emp.fullName.toLowerCase().includes(filters.nameSearch.toLowerCase())
      );
    }

    // ترتيب حسب تاريخ المباشرة
    if (filters.hireDateSort) {
      filtered.sort((a, b) => {
        const dateA = new Date(a.hireDate);
        const dateB = new Date(b.hireDate);
        return filters.hireDateSort === 'asc' ? dateA - dateB : dateB - dateA;
      });
    }

    setFilteredEmployees(filtered);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getUniqueJobClasses = () => {
    return [...new Set(employees.map(emp => emp.jobClass))];
  };

  const calculateService = (hireDate) => {
    const hire = new Date(hireDate);
    const today = new Date();
    const diffTime = Math.abs(today - hire);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const years = Math.floor(diffDays / 365);
    const months = Math.floor((diffDays % 365) / 30);
    const days = diffDays % 30;

    return `${years} سنة، ${months} شهر، ${days} يوم`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>جاري تحميل البيانات...</Typography>
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 4 }}>
      <Typography variant="h5" component="h2" gutterBottom color="primary">
        قائمة الموظفين
      </Typography>

      {/* شريط الفلاتر */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          label="البحث في الاسم"
          variant="outlined"
          size="small"
          value={filters.nameSearch}
          onChange={(e) => handleFilterChange('nameSearch', e.target.value)}
          sx={{ minWidth: 200 }}
        />

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>صنف الوظيفة</InputLabel>
          <Select
            value={filters.jobClass}
            onChange={(e) => handleFilterChange('jobClass', e.target.value)}
          >
            <MenuItem value="">الكل</MenuItem>
            {getUniqueJobClasses().map(jobClass => (
              <MenuItem key={jobClass} value={jobClass}>{jobClass}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>ترتيب تاريخ المباشرة</InputLabel>
          <Select
            value={filters.hireDateSort}
            onChange={(e) => handleFilterChange('hireDateSort', e.target.value)}
          >
            <MenuItem value="">بدون ترتيب</MenuItem>
            <MenuItem value="asc">من الأقدم للأحدث</MenuItem>
            <MenuItem value="desc">من الأحدث للأقدم</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'grey.100' }}>
              <TableCell>الصورة</TableCell>
              <TableCell>الاسم الرباعي</TableCell>
              <TableCell>العنوان الوظيفي</TableCell>
              <TableCell>صنف الوظيفة</TableCell>
              <TableCell>تاريخ المباشرة</TableCell>
              <TableCell>الخدمة الفعلية</TableCell>
              <TableCell>الحالة</TableCell>
              <TableCell>الإجراءات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredEmployees.map((employee) => (
              <TableRow key={employee._id} hover>
                <TableCell>
                  <Avatar src={employee.profileImage}>
                    <Person />
                  </Avatar>
                </TableCell>
                <TableCell>{employee.fullName}</TableCell>
                <TableCell>{employee.jobTitle}</TableCell>
                <TableCell>{employee.jobClass}</TableCell>
                <TableCell>
                  {format(new Date(employee.hireDate), 'dd/MM/yyyy', { locale: ar })}
                </TableCell>
                <TableCell>{calculateService(employee.hireDate)}</TableCell>
                <TableCell>
                  <Chip
                    label={employee.status === 'active' ? 'في الخدمة' : 'في إجازة'}
                    color={employee.status === 'active' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="عرض الملف الشخصي">
                    <IconButton
                      color="primary"
                      onClick={() => onViewProfile(employee._id)}
                    >
                      <Person />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredEmployees.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">
            لا توجد موظفين مطابقين للفلاتر المحددة
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default EmployeeList;
