import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Link,
  InputAdornment,
  IconButton,
  Fade,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Slide,
  Zoom,
  Chip,
  Divider
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon,
  TrendingUp,
  Analytics,
  Psychology,
  Security,
  Star
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link as RouterLink, useSearchParams } from 'react-router-dom';
import trialAccountService from '../services/trialAccountService';
import TrialAccountPopup from '../components/TrialAccountPopup';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [isCreatingTrial, setIsCreatingTrial] = useState(false);
  const [trialAccount, setTrialAccount] = useState(null);
  const [showTrialPopup, setShowTrialPopup] = useState(false);

  const { login, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  // Check if user came from trial button
  const isTrialMode = searchParams.get('trial') === 'true';

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(formData.email, formData.password);

      if (result.success) {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleCreateTrialAccount = async () => {
    setIsCreatingTrial(true);
    clearError();

    try {
      const result = await trialAccountService.createTrialAccount();
      
      if (result.status === 'success') {
        setTrialAccount(result.trial_account);
        setShowTrialPopup(true);
      } else {
        setErrors({ general: result.message || 'Failed to create trial account' });
      }
    } catch (err) {
      setErrors({ general: 'Error creating trial account' });
      console.error('Trial account creation error:', err);
    } finally {
      setIsCreatingTrial(false);
    }
  };

  const handleTrialPopupClose = () => {
    setShowTrialPopup(false);
    // Auto-fill the login form with trial credentials
    if (trialAccount) {
      setFormData({
        email: trialAccount.email,
        password: trialAccount.password
      });
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%)
          `,
          zIndex: 1,
        },
      }}
    >
      {/* Floating Background Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          animation: 'float 6s ease-in-out infinite',
          zIndex: 1,
          '@keyframes float': {
            '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
            '50%': { transform: 'translateY(-20px) rotate(180deg)' },
          },
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '20%',
          right: '15%',
          width: 60,
          height: 60,
          borderRadius: '50%',
          background: 'rgba(79, 195, 247, 0.2)',
          animation: 'float 8s ease-in-out infinite reverse',
          zIndex: 1,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '20%',
          left: '20%',
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: 'rgba(33, 150, 243, 0.15)',
          animation: 'float 10s ease-in-out infinite',
          zIndex: 1,
        }}
      />

      <Container 
        component="main" 
        maxWidth={isMobile ? 'sm' : isTablet ? 'md' : 'lg'}
        sx={{ position: 'relative', zIndex: 2 }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', lg: 'row' },
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            py: 2,
            gap: 6,
          }}
        >
          {/* Left Side - Features */}
          {!isMobile && (
            <Slide direction="right" in={true} timeout={1000}>
              <Box
                sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  color: 'white',
                  pr: { lg: 6 },
                }}
              >
                <Typography 
                  variant="h3" 
                  sx={{ 
                    fontWeight: 'bold', 
                    mb: 2,
                    background: 'linear-gradient(45deg, #fff, #4FC3F7)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  InsightHire
                </Typography>
                <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                  AI-Powered Interview Analytics
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
                  {[
                    { icon: <Analytics />, text: 'Real-time candidate analysis' },
                    { icon: <Psychology />, text: 'Emotion & confidence detection' },
                    { icon: <TrendingUp />, text: 'Performance insights' },
                    { icon: <Security />, text: 'Secure & confidential' },
                  ].map((feature, index) => (
                    <Zoom in={true} timeout={1200 + index * 200} key={index}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 2,
                          p: 2,
                          borderRadius: 2,
                          background: 'rgba(255, 255, 255, 0.1)',
                          backdropFilter: 'blur(10px)',
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                        }}
                      >
                        <Box
                          sx={{
                            p: 1,
                            borderRadius: '50%',
                            background: 'rgba(79, 195, 247, 0.3)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          {feature.icon}
                        </Box>
                        <Typography variant="body1">{feature.text}</Typography>
                      </Box>
                    </Zoom>
                  ))}
                </Box>
              </Box>
            </Slide>
          )}

          {/* Right Side - Login Form */}
          <Slide direction="left" in={true} timeout={1000}>
            <Box sx={{ flex: { xs: 1, lg: 1.2 }, maxWidth: 500, width: '100%' }}>
              <Fade in={true} timeout={1200}>
                <Paper
                  elevation={24}
                  sx={{
                    p: { xs: 4, sm: 5, md: 6 },
                    borderRadius: 4,
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 4,
                      background: 'linear-gradient(90deg, #4FC3F7, #2196F3, #1976D2)',
                    },
                  }}
                >
                  {/* Logo/Header */}
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <Zoom in={true} timeout={1400}>
                      <Box
                        sx={{
                          width: 80,
                          height: 80,
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #4FC3F7 0%, #2196F3 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 2,
                          boxShadow: '0 10px 30px rgba(79, 195, 247, 0.3)',
                          animation: 'pulse 2s infinite',
                          '@keyframes pulse': {
                            '0%': { transform: 'scale(1)' },
                            '50%': { transform: 'scale(1.05)' },
                            '100%': { transform: 'scale(1)' },
                          },
                        }}
                      >
                        <LoginIcon sx={{ color: 'white', fontSize: 40 }} />
                      </Box>
                    </Zoom>

                    <Typography 
                      component="h1" 
                      variant={isMobile ? 'h4' : 'h3'} 
                      sx={{ 
                        mb: 1, 
                        color: '#2C3E50', 
                        fontWeight: 700,
                        background: 'linear-gradient(45deg, #2C3E50, #2196F3)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                      }}
                    >
                      Welcome Back
                    </Typography>

                    <Typography 
                      variant="body1" 
                      sx={{ 
                        color: '#6B7280', 
                        textAlign: 'center',
                        lineHeight: 1.6,
                      }}
                    >
                      Sign in to your InsightHire account to continue monitoring candidate interviews
                    </Typography>
                  </Box>

                  {error && (
                    <Fade in={true}>
                      <Alert 
                        severity="error" 
                        sx={{ 
                          mb: 3, 
                          borderRadius: 2,
                          '& .MuiAlert-icon': {
                            fontSize: '1.2rem',
                          },
                        }}
                      >
                        {error}
                      </Alert>
                    </Fade>
                  )}

                  {isTrialMode ? (
                    // Trial Mode - Show only trial account creation
                    <Box sx={{ width: '100%' }}>
                      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center', color: '#2E7D32', fontWeight: 'bold' }}>
                        Create Free Trial Account
                      </Typography>

                      <Typography variant="body1" sx={{ mb: 3, textAlign: 'center', color: '#666' }}>
                        Get instant access to InsightHire with a free trial account
                      </Typography>

                      {errors.general && (
                        <Fade in={true}>
                          <Alert 
                            severity="error" 
                            sx={{ 
                              mb: 3, 
                              borderRadius: 2,
                              '& .MuiAlert-icon': {
                                fontSize: '1.2rem',
                              },
                            }}
                          >
                            {errors.general}
                          </Alert>
                        </Fade>
                      )}

                      <Button
                        fullWidth
                        variant="contained"
                        onClick={handleCreateTrialAccount}
                        disabled={isCreatingTrial}
                        sx={{
                          py: 3,
                          mb: 3,
                          borderRadius: 3,
                          fontSize: '1.2rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                          boxShadow: '0 8px 25px rgba(76, 175, 80, 0.3)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)',
                            boxShadow: '0 12px 35px rgba(76, 175, 80, 0.4)',
                            transform: 'translateY(-2px)',
                          },
                          '&:active': {
                            transform: 'translateY(0px)',
                          },
                          '&:disabled': {
                            background: '#BBBBBB',
                            boxShadow: 'none',
                            transform: 'none',
                          },
                        }}
                      >
                        {isCreatingTrial ? (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CircularProgress size={20} color="inherit" />
                            <Typography>Creating Trial Account...</Typography>
                          </Box>
                        ) : (
                          <>
                            <Star sx={{ mr: 1 }} />
                            Create Free Trial Account
                          </>
                        )}
                      </Button>

                      <Box sx={{ textAlign: 'center', mb: 2 }}>
                        <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>
                          What you get with your free trial:
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
                          <Chip 
                            label="2 Interviews" 
                            color="primary" 
                            variant="outlined"
                            sx={{ fontSize: '0.8rem' }}
                          />
                          <Chip 
                            label="2 Job Roles" 
                            color="primary" 
                            variant="outlined"
                            sx={{ fontSize: '0.8rem' }}
                          />
                          <Chip 
                            label="7 Days Free" 
                            color="primary" 
                            variant="outlined"
                            sx={{ fontSize: '0.8rem' }}
                          />
                        </Box>
                      </Box>

                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" sx={{ color: '#6B7280', mb: 1 }}>
                          Already have an account?
                        </Typography>
                        <Link
                          component={RouterLink}
                          to="/login"
                          sx={{
                            color: '#2196F3',
                            textDecoration: 'none',
                            fontWeight: 600,
                            fontSize: '1rem',
                            position: 'relative',
                            '&::after': {
                              content: '""',
                              position: 'absolute',
                              bottom: -2,
                              left: 0,
                              width: 0,
                              height: 2,
                              background: 'linear-gradient(90deg, #4FC3F7, #2196F3)',
                              transition: 'width 0.3s ease',
                            },
                            '&:hover::after': {
                              width: '100%',
                            },
                            '&:hover': {
                              color: '#1976D2',
                            },
                          }}
                        >
                          Sign In Instead
                        </Link>
                      </Box>
                    </Box>
                  ) : (
                    // Regular Login Mode - Show normal login form
                    <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                      <Box sx={{ mb: 3 }}>
                        <TextField
                          fullWidth
                          id="email"
                          label="Email Address"
                          name="email"
                          autoComplete="email"
                          autoFocus
                          value={formData.email}
                          onChange={handleChange}
                          error={!!errors.email}
                          helperText={errors.email}
                          variant="outlined"
                          InputProps={{
                            startAdornment: (
                              <InputAdornment position="start">
                                <Email sx={{ color: '#2196F3' }} />
                              </InputAdornment>
                            ),
                          }}
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: 3,
                              backgroundColor: '#FAFBFD',
                              transition: 'all 0.3s ease',
                              '&:hover': {
                                backgroundColor: '#F8FCFF',
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#4FC3F7',
                                  borderWidth: 2,
                                },
                              },
                              '&.Mui-focused': {
                                backgroundColor: '#F8FCFF',
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#2196F3',
                                  borderWidth: 2,
                                },
                              },
                              '&.Mui-error': {
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#f44336',
                                },
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: '#6B7280',
                              '&.Mui-focused': {
                                color: '#2196F3',
                              },
                            },
                            '& .MuiInputBase-input': {
                              color: '#1a1a1a',
                            },
                          }}
                        />
                      </Box>

                      <Box sx={{ mb: 4 }}>
                        <TextField
                          fullWidth
                          name="password"
                          label="Password"
                          type={showPassword ? 'text' : 'password'}
                          id="password"
                          autoComplete="current-password"
                          value={formData.password}
                          onChange={handleChange}
                          error={!!errors.password}
                          helperText={errors.password}
                          variant="outlined"
                          InputProps={{
                            startAdornment: (
                              <InputAdornment position="start">
                                <Lock sx={{ color: '#2196F3' }} />
                              </InputAdornment>
                            ),
                            endAdornment: (
                              <InputAdornment position="end">
                                <IconButton
                                  aria-label="toggle password visibility"
                                  onClick={() => setShowPassword(!showPassword)}
                                  edge="end"
                                  sx={{ color: '#6B7280' }}
                                >
                                  {showPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                              </InputAdornment>
                            ),
                          }}
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: 3,
                              backgroundColor: '#FAFBFD',
                              transition: 'all 0.3s ease',
                              '&:hover': {
                                backgroundColor: '#F8FCFF',
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#4FC3F7',
                                  borderWidth: 2,
                                },
                              },
                              '&.Mui-focused': {
                                backgroundColor: '#F8FCFF',
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#2196F3',
                                  borderWidth: 2,
                                },
                              },
                              '&.Mui-error': {
                                '& .MuiOutlinedInput-notchedOutline': {
                                  borderColor: '#f44336',
                                },
                              },
                            },
                            '& .MuiInputLabel-root': {
                              color: '#6B7280',
                              '&.Mui-focused': {
                                color: '#2196F3',
                              },
                            },
                            '& .MuiInputBase-input': {
                              color: '#1a1a1a',
                            },
                          }}
                        />
                      </Box>

                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      disabled={isLoading}
                      sx={{
                        py: 2,
                        mb: 3,
                        borderRadius: 3,
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        textTransform: 'none',
                        background: 'linear-gradient(135deg, #4FC3F7 0%, #2196F3 100%)',
                        boxShadow: '0 8px 25px rgba(79, 195, 247, 0.3)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #29B6F6 0%, #1976D2 100%)',
                          boxShadow: '0 12px 35px rgba(79, 195, 247, 0.4)',
                          transform: 'translateY(-2px)',
                        },
                        '&:active': {
                          transform: 'translateY(0px)',
                        },
                        '&:disabled': {
                          background: '#BBBBBB',
                          boxShadow: 'none',
                          transform: 'none',
                        },
                      }}
                    >
                      {isLoading ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CircularProgress size={20} color="inherit" />
                          <Typography>Signing In...</Typography>
                        </Box>
                      ) : (
                        'Sign In'
                      )}
                    </Button>

                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" sx={{ color: '#6B7280', mb: 1 }}>
                          Don't have an account?
                        </Typography>
                        <Link
                          component={RouterLink}
                          to="/register"
                          sx={{
                            color: '#2196F3',
                            textDecoration: 'none',
                            fontWeight: 600,
                            fontSize: '1rem',
                            position: 'relative',
                            '&::after': {
                              content: '""',
                              position: 'absolute',
                              bottom: -2,
                              left: 0,
                              width: 0,
                              height: 2,
                              background: 'linear-gradient(90deg, #4FC3F7, #2196F3)',
                              transition: 'width 0.3s ease',
                            },
                            '&:hover::after': {
                              width: '100%',
                            },
                            '&:hover': {
                              color: '#1976D2',
                            },
                          }}
                        >
                          Create Account
                        </Link>
                      </Box>

                      <Divider sx={{ my: 3 }}>
                        <Chip label="OR" />
                      </Divider>

                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => {
                          // Navigate to login page with trial option
                          navigate('/login?trial=true');
                        }}
                        sx={{
                          py: 2,
                          mb: 2,
                          borderRadius: 3,
                          fontSize: '1.1rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                          boxShadow: '0 8px 25px rgba(76, 175, 80, 0.3)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)',
                            boxShadow: '0 12px 35px rgba(76, 175, 80, 0.4)',
                            transform: 'translateY(-2px)',
                          },
                          '&:active': {
                            transform: 'translateY(0px)',
                          },
                          '&:disabled': {
                            background: '#BBBBBB',
                            boxShadow: 'none',
                            transform: 'none',
                          },
                        }}
                      >
                        <Star sx={{ mr: 1 }} />
                        Start Free Trial
                      </Button>

                      <Typography variant="body2" sx={{ color: '#666', textAlign: 'center', mb: 2 }}>
                        Get 2 free interviews and 2 job roles to try InsightHire
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Fade>
            </Box>
          </Slide>
        </Box>
      </Container>

      {/* Trial Account Popup */}
      <TrialAccountPopup
        open={showTrialPopup}
        onClose={handleTrialPopupClose}
        trialAccount={trialAccount}
      />
    </Box>
  );
};

export default Login;


