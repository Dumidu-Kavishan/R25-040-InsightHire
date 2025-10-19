import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Stepper,
  Step,
  StepLabel,
  InputAdornment,
  IconButton,
  Fade,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Slide,
  Zoom,
  Chip,
  Divider,
  Grid,
} from '@mui/material';
import {
  VpnKey,
  CreditCard,
  CheckCircle,
  CopyAll,
  Star,
  Security,
  Payment,
  Visibility,
  VisibilityOff,
  Close,
  Diamond,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { usePremiumCode } from '../contexts/PremiumCodeContext';

const PremiumCodeEntry = ({ onCodeValidated, onClose }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [premiumCode, setPremiumCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [paymentData, setPaymentData] = useState({
    cardNumber: '',
    cardHolder: '',
    expiryDate: '',
    cvv: '',
    amount: 99.99
  });
  const [showCvv, setShowCvv] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { validateAndUsePremiumCode, purchasePremiumCode } = usePremiumCode();

  const steps = ['Enter Premium Code', 'Payment Details', 'Get Your Code'];

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const validatePremiumCode = async () => {
    if (!premiumCode.trim()) {
      setError('Please enter a premium code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await validateAndUsePremiumCode(premiumCode);
      
      if (result.success) {
        toast.success(result.message);
        onCodeValidated(premiumCode);
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('Error validating premium code');
      console.error('Validation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const processPayment = async () => {
    setIsLoading(true);
    setError('');

    // Client-side validation
    if (!paymentData.cardNumber.trim()) {
      setError('Card Number is required');
      setIsLoading(false);
      return;
    }
    if (!paymentData.cardHolder.trim()) {
      setError('Card Holder Name is required');
      setIsLoading(false);
      return;
    }
    if (!paymentData.expiryDate.trim()) {
      setError('Expiry Date is required');
      setIsLoading(false);
      return;
    }
    if (!paymentData.cvv.trim()) {
      setError('CVV is required');
      setIsLoading(false);
      return;
    }

    try {
      // Convert camelCase to snake_case for backend API
      const apiPaymentData = {
        card_number: paymentData.cardNumber,
        card_holder: paymentData.cardHolder,
        expiry_date: paymentData.expiryDate,
        cvv: paymentData.cvv,
        amount: paymentData.amount
      };

      const result = await purchasePremiumCode(apiPaymentData);

      if (result.status === 'success') {
        setGeneratedCode(result.premium_code);
        setActiveStep(2);
        toast.success('Payment processed successfully!');
      } else {
        setError(result.message || 'Payment failed');
      }
    } catch (err) {
      setError('Error processing payment');
      console.error('Payment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedCode);
    toast.success('Premium code copied to clipboard!');
  };

  const handlePaymentDataChange = (field) => (event) => {
    setPaymentData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const formatExpiryDate = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  return (
    <Box
      sx={{
        height: '100vh',
        width: '100vw',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'fixed',
        top: 0,
        left: 0,
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
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
      {/* Enhanced Floating Background Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.15)',
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
          width: 80,
          height: 80,
          borderRadius: '50%',
          background: 'rgba(79, 195, 247, 0.25)',
          animation: 'float 8s ease-in-out infinite reverse',
          zIndex: 1,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '20%',
          left: '20%',
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: 'rgba(33, 150, 243, 0.2)',
          animation: 'float 10s ease-in-out infinite',
          zIndex: 1,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: '60%',
          right: '30%',
          width: 60,
          height: 60,
          borderRadius: '50%',
          background: 'rgba(255, 215, 0, 0.2)',
          animation: 'float 7s ease-in-out infinite reverse',
          zIndex: 1,
        }}
      />

      <Container 
        component="main" 
        maxWidth={isMobile ? 'sm' : 'md'}
        sx={{ 
          position: 'relative', 
          zIndex: 2, 
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 2,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            maxHeight: '90vh',
            gap: 3,
          }}
        >
          {/* Header */}
          <Slide direction="down" in={true} timeout={1000}>
            <Box sx={{ textAlign: 'center', color: 'white', mb: 2 }}>
              <Zoom in={true} timeout={1200}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2,
                    boxShadow: '0 15px 35px rgba(255, 215, 0, 0.4)',
                    animation: 'pulse 2s infinite',
                    '@keyframes pulse': {
                      '0%': { transform: 'scale(1)' },
                      '50%': { transform: 'scale(1.05)' },
                      '100%': { transform: 'scale(1)' },
                    },
                  }}
                >
                  <Diamond sx={{ color: 'white', fontSize: 40 }} />
                </Box>
              </Zoom>

              <Typography 
                variant="h4" 
                sx={{ 
                  fontWeight: 'bold', 
                  mb: 1,
                  background: 'linear-gradient(45deg, #fff, #FFD700)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Premium Access
              </Typography>
              <Typography variant="h6" sx={{ mb: 0, opacity: 0.9 }}>
                Unlock the full potential of InsightHire
              </Typography>
            </Box>
          </Slide>

          {/* Main Content */}
          <Slide direction="up" in={true} timeout={1000}>
            <Box sx={{ width: '100%', maxWidth: 600, maxHeight: isMobile ? '70vh' : '75vh', overflow: 'hidden' }}>
              <Fade in={true} timeout={1200}>
                <Paper
                  elevation={24}
                  sx={{
                    p: { xs: 3, sm: 4, md: 4 },
                    borderRadius: 4,
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    maxHeight: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 4,
                      background: 'linear-gradient(90deg, #FFD700, #FFA500, #FF8C00)',
                    },
                  }}
                >
                  {/* Close Button */}
                  <IconButton
                    onClick={onClose}
                    sx={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      color: '#666',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                      },
                    }}
                  >
                    <Close />
                  </IconButton>

                  {/* Stepper */}
                  <Box sx={{ mb: 2 }}>
                    <Stepper activeStep={activeStep} alternativeLabel>
                      {steps.map((label) => (
                        <Step key={label}>
                          <StepLabel
                            sx={{
                              '& .MuiStepLabel-label': {
                                color: '#333',
                                fontWeight: 600,
                                fontSize: '0.8rem',
                                '&.Mui-active': {
                                  color: '#1976D2',
                                  fontWeight: 700,
                                },
                                '&.Mui-completed': {
                                  color: '#2E7D32',
                                  fontWeight: 700,
                                },
                              },
                              '& .MuiStepLabel-iconContainer': {
                                '& .MuiSvgIcon-root': {
                                  fontSize: '1.2rem',
                                  '&.Mui-active': {
                                    color: '#1976D2',
                                  },
                                  '&.Mui-completed': {
                                    color: '#2E7D32',
                                  },
                                },
                              },
                            }}
                          >
                            {label}
                          </StepLabel>
                        </Step>
                      ))}
                    </Stepper>
                  </Box>

                  {/* Step 0: Premium Code Entry */}
                  {activeStep === 0 && (
                    <Box sx={{ 
                      flex: 1, 
                      display: 'flex', 
                      flexDirection: 'column',
                      overflow: 'auto',
                      maxHeight: isMobile ? 'calc(60vh - 120px)' : 'calc(65vh - 150px)',
                      paddingRight: '8px',
                      '&::-webkit-scrollbar': {
                        width: '6px',
                        marginRight: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '3px',
                        margin: '8px 8px 8px 0px',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        background: 'rgba(0,0,0,0.7)',
                        borderRadius: '3px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        '&:hover': {
                          background: 'rgba(0,0,0,0.8)',
                        },
                      },
                    }}>
                      <Typography variant="h6" sx={{ mb: 2, textAlign: 'center', color: '#2C3E50' }}>
                        Enter Your Premium Code
                      </Typography>

                      {error && (
                        <Fade in={true}>
                          <Alert 
                            severity="error" 
                            sx={{ 
                              mb: 3, 
                              borderRadius: 2,
                            }}
                          >
                            {error}
                          </Alert>
                        </Fade>
                      )}

                      <TextField
                        fullWidth
                        label="Premium Code"
                        value={premiumCode}
                        onChange={(e) => setPremiumCode(e.target.value.toUpperCase())}
                        placeholder="PREM-XXXX-YYYY-ZZZZ"
                        variant="outlined"
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <VpnKey sx={{ color: '#FFD700' }} />
                            </InputAdornment>
                          ),
                        }}
                        sx={{
                          mb: 3,
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 3,
                            backgroundColor: '#FAFBFD',
                            '&:hover': {
                              backgroundColor: '#F8FCFF',
                              '& .MuiOutlinedInput-notchedOutline': {
                                borderColor: '#FFD700',
                                borderWidth: 2,
                              },
                            },
                            '&.Mui-focused': {
                              backgroundColor: '#F8FCFF',
                              '& .MuiOutlinedInput-notchedOutline': {
                                borderColor: '#FFA500',
                                borderWidth: 2,
                              },
                            },
                          },
                          '& .MuiInputBase-input': {
                            color: '#1a1a1a',
                            fontSize: '1rem',
                            fontWeight: 500,
                          },
                          '& .MuiInputLabel-root': {
                            color: '#6B7280',
                            '&.Mui-focused': {
                              color: '#FFA500',
                            },
                          },
                        }}
                      />

                      <Button
                        fullWidth
                        variant="contained"
                        onClick={validatePremiumCode}
                        disabled={isLoading}
                        sx={{
                          py: 2,
                          mb: 3,
                          borderRadius: 3,
                          fontSize: '1.1rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                          boxShadow: '0 8px 25px rgba(255, 215, 0, 0.3)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #FFA500 0%, #FF8C00 100%)',
                            boxShadow: '0 12px 35px rgba(255, 215, 0, 0.4)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        {isLoading ? (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CircularProgress size={20} color="inherit" />
                            <Typography>Validating...</Typography>
                          </Box>
                        ) : (
                          'Validate Code'
                        )}
                      </Button>

                      <Divider sx={{ my: 2 }}>
                        <Chip label="OR" />
                      </Divider>

                      <Button
                        fullWidth
                        variant="outlined"
                        onClick={() => setActiveStep(1)}
                        sx={{
                          py: 2,
                          mb: 2,
                          borderRadius: 3,
                          fontSize: '1.1rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          borderColor: '#FFD700',
                          color: '#FFA500',
                          '&:hover': {
                            borderColor: '#FFA500',
                            backgroundColor: 'rgba(255, 215, 0, 0.1)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        <Payment sx={{ mr: 1 }} />
                        Buy Premium Code
                      </Button>

                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => {
                          // Navigate to login page with trial option
                          navigate('/login?trial=true');
                        }}
                        sx={{
                          py: 2,
                          borderRadius: 3,
                          fontSize: '1.1rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                          boxShadow: '0 8px 25px rgba(76, 175, 80, 0.3)',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)',
                            boxShadow: '0 12px 35px rgba(76, 175, 80, 0.4)',
                            transform: 'translateY(-2px)',
                          },
                        }}
                      >
                        <Star sx={{ mr: 1 }} />
                        Start Free Trial
                      </Button>
                    </Box>
                  )}

                  {/* Step 1: Payment Form */}
                  {activeStep === 1 && (
                    <Box sx={{ 
                      flex: 1, 
                      display: 'flex', 
                      flexDirection: 'column',
                      overflow: 'auto',
                      maxHeight: isMobile ? 'calc(60vh - 120px)' : 'calc(65vh - 150px)',
                      paddingRight: '8px',
                      '&::-webkit-scrollbar': {
                        width: '6px',
                        marginRight: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '3px',
                        margin: '8px 8px 8px 0px',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        background: 'rgba(0,0,0,0.7)',
                        borderRadius: '3px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        '&:hover': {
                          background: 'rgba(0,0,0,0.8)',
                        },
                      },
                    }}>
                      <Typography variant="h6" sx={{ mb: 2, textAlign: 'center', color: '#2C3E50' }}>
                        Payment Details
                      </Typography>

                      {error && (
                        <Fade in={true}>
                          <Alert 
                            severity="error" 
                            sx={{ 
                              mb: 3, 
                              borderRadius: 2,
                            }}
                          >
                            {error}
                          </Alert>
                        </Fade>
                      )}

                      <Grid container spacing={2}>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Card Number"
                            value={paymentData.cardNumber}
                            onChange={(e) => setPaymentData(prev => ({
                              ...prev,
                              cardNumber: formatCardNumber(e.target.value)
                            }))}
                            placeholder="1234 5678 9012 3456"
                            InputProps={{
                              startAdornment: (
                                <InputAdornment position="start">
                                  <CreditCard sx={{ color: '#FFD700' }} />
                                </InputAdornment>
                              ),
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 3,
                                backgroundColor: '#FAFBFD',
                                '&:hover': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFD700',
                                    borderWidth: 2,
                                  },
                                },
                                '&.Mui-focused': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFA500',
                                    borderWidth: 2,
                                  },
                                },
                              },
                              '& .MuiInputBase-input': {
                                color: '#1a1a1a',
                                fontSize: '1rem',
                                fontWeight: 500,
                              },
                              '& .MuiInputLabel-root': {
                                color: '#6B7280',
                                '&.Mui-focused': {
                                  color: '#FFA500',
                                },
                              },
                            }}
                          />
                        </Grid>

                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Card Holder Name"
                            value={paymentData.cardHolder}
                            onChange={handlePaymentDataChange('cardHolder')}
                            placeholder="John Doe"
                            InputProps={{
                              startAdornment: (
                                <InputAdornment position="start">
                                  <Security sx={{ color: '#FFD700' }} />
                                </InputAdornment>
                              ),
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 3,
                                backgroundColor: '#FAFBFD',
                                '&:hover': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFD700',
                                    borderWidth: 2,
                                  },
                                },
                                '&.Mui-focused': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFA500',
                                    borderWidth: 2,
                                  },
                                },
                              },
                              '& .MuiInputBase-input': {
                                color: '#1a1a1a',
                                fontSize: '1rem',
                                fontWeight: 500,
                              },
                              '& .MuiInputLabel-root': {
                                color: '#6B7280',
                                '&.Mui-focused': {
                                  color: '#FFA500',
                                },
                              },
                            }}
                          />
                        </Grid>

                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            label="Expiry Date"
                            value={paymentData.expiryDate}
                            onChange={(e) => setPaymentData(prev => ({
                              ...prev,
                              expiryDate: formatExpiryDate(e.target.value)
                            }))}
                            placeholder="MM/YY"
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 3,
                                backgroundColor: '#FAFBFD',
                                '&:hover': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFD700',
                                    borderWidth: 2,
                                  },
                                },
                                '&.Mui-focused': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFA500',
                                    borderWidth: 2,
                                  },
                                },
                              },
                              '& .MuiInputBase-input': {
                                color: '#1a1a1a',
                                fontSize: '1rem',
                                fontWeight: 500,
                              },
                              '& .MuiInputLabel-root': {
                                color: '#6B7280',
                                '&.Mui-focused': {
                                  color: '#FFA500',
                                },
                              },
                            }}
                          />
                        </Grid>

                        <Grid item xs={6}>
                          <TextField
                            fullWidth
                            label="CVV"
                            type={showCvv ? 'text' : 'password'}
                            value={paymentData.cvv}
                            onChange={handlePaymentDataChange('cvv')}
                            placeholder="123"
                            InputProps={{
                              endAdornment: (
                                <InputAdornment position="end">
                                  <IconButton
                                    onClick={() => setShowCvv(!showCvv)}
                                    edge="end"
                                  >
                                    {showCvv ? <VisibilityOff /> : <Visibility />}
                                  </IconButton>
                                </InputAdornment>
                              ),
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                borderRadius: 3,
                                backgroundColor: '#FAFBFD',
                                '&:hover': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFD700',
                                    borderWidth: 2,
                                  },
                                },
                                '&.Mui-focused': {
                                  backgroundColor: '#F8FCFF',
                                  '& .MuiOutlinedInput-notchedOutline': {
                                    borderColor: '#FFA500',
                                    borderWidth: 2,
                                  },
                                },
                              },
                              '& .MuiInputBase-input': {
                                color: '#1a1a1a',
                                fontSize: '1rem',
                                fontWeight: 500,
                              },
                              '& .MuiInputLabel-root': {
                                color: '#6B7280',
                                '&.Mui-focused': {
                                  color: '#FFA500',
                                },
                              },
                            }}
                          />
                        </Grid>
                      </Grid>

                      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                        <Button
                          variant="outlined"
                          onClick={() => setActiveStep(0)}
                          sx={{
                            flex: 1,
                            py: 2,
                            borderRadius: 3,
                            textTransform: 'none',
                            borderColor: '#666',
                            color: '#333',
                            fontWeight: 600,
                            fontSize: '1rem',
                            '&:hover': {
                              borderColor: '#333',
                              backgroundColor: 'rgba(0, 0, 0, 0.04)',
                              color: '#000',
                            },
                          }}
                        >
                          Back
                        </Button>
                        <Button
                          variant="contained"
                          onClick={processPayment}
                          disabled={isLoading}
                          sx={{
                            flex: 1,
                            py: 2,
                            borderRadius: 3,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            textTransform: 'none',
                            background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #FFA500 0%, #FF8C00 100%)',
                            },
                          }}
                        >
                          {isLoading ? (
                            <CircularProgress size={20} color="inherit" />
                          ) : (
                            <>
                              <Payment sx={{ mr: 1 }} />
                              Pay $99.99
                            </>
                          )}
                        </Button>
                      </Box>
                    </Box>
                  )}

                  {/* Step 2: Generated Code */}
                  {activeStep === 2 && (
                    <Box sx={{ 
                      flex: 1, 
                      display: 'flex', 
                      flexDirection: 'column', 
                      textAlign: 'center',
                      overflow: 'auto',
                      maxHeight: isMobile ? 'calc(60vh - 120px)' : 'calc(65vh - 150px)',
                      '&::-webkit-scrollbar': {
                        width: '6px',
                        marginRight: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '3px',
                        margin: '8px 8px 8px 0px',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        background: 'rgba(0,0,0,0.7)',
                        borderRadius: '3px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        '&:hover': {
                          background: 'rgba(0,0,0,0.8)',
                        },
                      },
                    }}>
                      <Zoom in={true}>
                        <Box
                          sx={{
                            width: 80,
                            height: 80,
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mx: 'auto',
                            mb: 3,
                            boxShadow: '0 10px 30px rgba(76, 175, 80, 0.3)',
                          }}
                        >
                          <CheckCircle sx={{ color: 'white', fontSize: 40 }} />
                        </Box>
                      </Zoom>

                      <Typography variant="h6" sx={{ mb: 2, color: '#2C3E50' }}>
                        Payment Successful!
                      </Typography>

                      <Typography variant="body1" sx={{ mb: 2, color: '#666' }}>
                        Your premium code has been generated:
                      </Typography>

                      <Paper
                        elevation={3}
                        sx={{
                          p: 2,
                          mb: 2,
                          borderRadius: 3,
                          backgroundColor: '#F5F5F5',
                          border: '2px dashed #4CAF50',
                        }}
                      >
                        <Typography
                          variant="h6"
                          sx={{
                            fontFamily: 'monospace',
                            fontWeight: 'bold',
                            color: '#2E7D32',
                            letterSpacing: 2,
                          }}
                        >
                          {generatedCode}
                        </Typography>
                      </Paper>

                      <Button
                        variant="contained"
                        onClick={copyToClipboard}
                        sx={{
                          mb: 2,
                          borderRadius: 3,
                          textTransform: 'none',
                          backgroundColor: '#4CAF50',
                          '&:hover': {
                            backgroundColor: '#2E7D32',
                          },
                        }}
                      >
                        <CopyAll sx={{ mr: 1 }} />
                        Copy Code
                      </Button>

                      <Typography variant="body2" sx={{ color: '#666', mb: 2 }}>
                        Save this code securely. You can use it to access premium features.
                      </Typography>

                      <Button
                        variant="outlined"
                        onClick={() => {
                          setPremiumCode(generatedCode);
                          setActiveStep(0);
                        }}
                        sx={{
                          borderRadius: 3,
                          textTransform: 'none',
                          borderColor: '#FFD700',
                          color: '#FFA500',
                        }}
                      >
                        Use This Code
                      </Button>
                    </Box>
                  )}
                </Paper>
              </Fade>
            </Box>
          </Slide>
        </Box>
      </Container>
    </Box>
  );
};

export default PremiumCodeEntry;
