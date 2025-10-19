import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, Box } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Contexts
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { PremiumCodeProvider, usePremiumCode } from './contexts/PremiumCodeContext';

// Components
import Navbar from './components/Navbar';
import LoadingSpinner from './components/LoadingSpinner';
import PremiumCodeEntry from './components/PremiumCodeEntry';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import InterviewSession from './pages/InterviewSession';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import HRAnalytics from './pages/HRAnalytics';
import HRDashboard from './pages/HRDashboard';


// Premium Code Gate Component
const PremiumCodeGate = ({ children }) => {
  const { hasPremiumAccess, isCheckingAccess } = usePremiumCode();
  const [showPremiumEntry, setShowPremiumEntry] = React.useState(false);

  React.useEffect(() => {
    // If user doesn't have premium access and we're not checking, show premium entry
    if (!hasPremiumAccess && !isCheckingAccess) {
      setShowPremiumEntry(true);
    }
  }, [hasPremiumAccess, isCheckingAccess]);

  const handleCodeValidated = (code) => {
    setShowPremiumEntry(false);
    // The PremiumCodeContext will handle updating the state
  };

  const handleClosePremiumEntry = () => {
    // Don't allow closing without premium access
    // Users must enter a valid premium code to proceed
  };

  if (isCheckingAccess) {
    return <LoadingSpinner />;
  }

  if (!hasPremiumAccess) {
    return (
      <PremiumCodeEntry 
        onCodeValidated={handleCodeValidated}
        onClose={handleClosePremiumEntry}
      />
    );
  }

  return children;
};

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
        {/* Public Routes - Protected by Premium Code Gate */}
        <Route path="/login" element={
          <PremiumCodeGate>
            <PublicRoute><Login /></PublicRoute>
          </PremiumCodeGate>
        } />
        <Route path="/register" element={
          <PremiumCodeGate>
            <PublicRoute><Register /></PublicRoute>
          </PremiumCodeGate>
        } />

        {/* Protected Routes - Also Protected by Premium Code Gate */}
        <Route path="/dashboard" element={
          <PremiumCodeGate>
            <ProtectedRoute><Dashboard /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/analytics" element={
          <PremiumCodeGate>
            <ProtectedRoute><Analytics /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/hr-analytics" element={
          <PremiumCodeGate>
            <ProtectedRoute><HRAnalytics /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/hr-dashboard" element={
          <PremiumCodeGate>
            <ProtectedRoute><HRDashboard /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/settings" element={
          <PremiumCodeGate>
            <ProtectedRoute><Settings /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/interview/:sessionId" element={
          <PremiumCodeGate>
            <ProtectedRoute><InterviewSession /></ProtectedRoute>
          </PremiumCodeGate>
        } />
        <Route path="/session/:sessionId" element={
          <PremiumCodeGate>
            <ProtectedRoute><InterviewSession /></ProtectedRoute>
          </PremiumCodeGate>
        } />

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
    <PremiumCodeProvider>
      <AuthProvider>
        <Router>
          <CssBaseline />
          <AppContent />
        </Router>
      </AuthProvider>
    </PremiumCodeProvider>
  </ThemeProvider>
);

export default App;
