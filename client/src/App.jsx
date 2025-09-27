import React, { useState } from 'react';
import {
  ThemeProvider, createTheme, CssBaseline, AppBar, Toolbar,
  Typography, Button, Container, Box, Fab
} from '@mui/material';
import { Add, People, Event } from '@mui/icons-material';
import { arSD } from '@mui/material/locale';
import AddEmployee from './components/AddEmployee';
import EmployeeList from './components/EmployeeList';
import EmployeeProfile from './components/EmployeeProfile';
import AddEvent from './components/AddEvent';

// إنشاء ثيم عربي مع ألوان عصرية
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Cairo, Arial, sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  direction: 'rtl',
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#f1f1f1',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#888',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: '#555',
          },
        },
      },
    },
  },
}, arSD);

const App = () => {
  const [currentView, setCurrentView] = useState('list'); // 'list', 'add-employee', 'profile'
  const [selectedEmployeeId, setSelectedEmployeeId] = useState(null);
  const [addEventOpen, setAddEventOpen] = useState(false);

  const handleViewProfile = (employeeId) => {
    setSelectedEmployeeId(employeeId);
    setCurrentView('profile');
  };

  const handleBackToList = () => {
    setCurrentView('list');
    setSelectedEmployeeId(null);
  };

  const handleAddEmployee = () => {
    setCurrentView('add-employee');
  };

  const handleEmployeeAdded = () => {
    setCurrentView('list');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'add-employee':
        return <AddEmployee onEmployeeAdded={handleEmployeeAdded} />;
      case 'profile':
        return (
          <EmployeeProfile
            employeeId={selectedEmployeeId}
            onClose={handleBackToList}
          />
        );
      default:
        return <EmployeeList onViewProfile={handleViewProfile} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: 'background.default' }}>
        {/* شريط التنقل العلوي */}
        <AppBar position="static" elevation={2}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              نظام إدارة الموظفين
            </Typography>
            <Button
              color="inherit"
              startIcon={<People />}
              onClick={() => setCurrentView('list')}
              sx={{ mx: 1 }}
            >
              قائمة الموظفين
            </Button>
            <Button
              color="inherit"
              startIcon={<Add />}
              onClick={handleAddEmployee}
              sx={{ mx: 1 }}
            >
              إضافة موظف
            </Button>
          </Toolbar>
        </AppBar>

        {/* المحتوى الرئيسي */}
        <Container maxWidth="xl" sx={{ py: 4 }}>
          {renderCurrentView()}
        </Container>

        {/* زر إضافة حدث عائم */}
        {currentView === 'list' && (
          <Fab
            color="secondary"
            aria-label="add event"
            sx={{
              position: 'fixed',
              bottom: 16,
              left: 16,
              zIndex: 1000
            }}
            onClick={() => setAddEventOpen(true)}
          >
            <Event />
          </Fab>
        )}

        {/* نافذة إضافة الحدث */}
        <AddEvent
          open={addEventOpen}
          onClose={() => setAddEventOpen(false)}
          onEventAdded={() => {
            setAddEventOpen(false);
            // يمكن إضافة تحديث للقائمة هنا إذا لزم الأمر
          }}
        />
      </Box>
    </ThemeProvider>
  );
};

export default App;
