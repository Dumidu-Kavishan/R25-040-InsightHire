import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, Box } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Contexts
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

// Components
import Navbar from './components/Navbar';
import LoadingSpinner from './components/LoadingSpinner';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import InterviewSession from './pages/InterviewSession';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import HRAnalytics from './pages/HRAnalytics';
import HRDashboard from './pages/HRDashboard';


// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

// App Layout
const AppLayout = ({ children }) => {
  const { isAuthenticated } = useAuth();

  return (
    <Box sx={(theme) => ({ 
      minHeight: '100vh', 
      backgroundColor: theme.palette.background.default,
    })}>
      {isAuthenticated && <Navbar />}
      <Box sx={{ paddingTop: isAuthenticated ? '64px' : '0' }}>
        {children}
      </Box>
    </Box>
  );
};

// App Routes
const AppContent = () => {
  const { isDarkMode } = useTheme();
  
  return (
    <AppLayout>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/hr-analytics" element={<ProtectedRoute><HRAnalytics /></ProtectedRoute>} />
        <Route path="/hr-dashboard" element={<ProtectedRoute><HRDashboard /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path="/interview/:sessionId" element={<ProtectedRoute><InterviewSession /></ProtectedRoute>} />
        <Route path="/session/:sessionId" element={<ProtectedRoute><InterviewSession /></ProtectedRoute>} />

        {/* Redirects */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        closeOnClick
        pauseOnHover
        theme={isDarkMode ? "dark" : "light"}
      />
    </AppLayout>
  );
};

// Main App Component
const App = () => (
  <ThemeProvider>
    <AuthProvider>
      <Router>
        <CssBaseline />
        <AppContent />
      </Router>
    </AuthProvider>
  </ThemeProvider>
);

export default App;
