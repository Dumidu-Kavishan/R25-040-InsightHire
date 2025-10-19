import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Paper,
  IconButton,
  Divider,
  Alert,
  Chip,
  Grid,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Person,
  Lock,
  Email,
  CopyAll,
  Star,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { toast } from 'react-toastify';

const TrialAccountPopup = ({ open, onClose, trialAccount }) => {
  const [showPassword, setShowPassword] = useState(false);
  
  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  if (!trialAccount) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 50,
                height: 50,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 8px 25px rgba(76, 175, 80, 0.3)',
              }}
            >
              <CheckCircle sx={{ color: 'white', fontSize: 30 }} />
            </Box>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#2E7D32', fontSize: '1.5rem' }}>
                Free Trial Account Created!
              </Typography>
              <Typography variant="body2" sx={{ color: '#333', fontSize: '1rem', fontWeight: 500 }}>
                Your trial account is ready to use
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} sx={{ color: '#666' }}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        <Alert 
          severity="warning" 
          sx={{ 
            mb: 3, 
            borderRadius: 2,
            '& .MuiAlert-icon': {
              fontSize: '1.2rem',
            },
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '1rem', color: '#333' }}>
            <strong>Important:</strong> Please note down your login credentials. You won't be able to retrieve them later!
          </Typography>
        </Alert>

        <Grid container spacing={3}>
          {/* Account Details */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                borderRadius: 3,
                background: 'rgba(255, 255, 255, 0.9)',
                border: '2px solid #4CAF50',
              }}
            >
              <Typography variant="h6" sx={{ mb: 2, color: '#2E7D32', fontWeight: 600, fontSize: '1.2rem' }}>
                Account Details
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Username"
                  value={trialAccount.username}
                  InputProps={{
                    readOnly: true,
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={{ color: '#2E7D32', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => copyToClipboard(trialAccount.username, 'Username')}
                          size="small"
                        >
                          <CopyAll sx={{ fontSize: 18, color: '#666' }} />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#ffffff',
                      border: '1px solid #e0e0e0',
                      '&:hover': {
                        backgroundColor: '#f8f9fa',
                        borderColor: '#4CAF50',
                      },
                    },
                    '& .MuiInputBase-input': {
                      color: '#1a1a1a',
                      fontSize: '1rem',
                      fontWeight: 500,
                    },
                    '& .MuiInputLabel-root': {
                      color: '#666',
                      '&.Mui-focused': {
                        color: '#4CAF50',
                      },
                    },
                  }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Email"
                  value={trialAccount.email}
                  InputProps={{
                    readOnly: true,
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email sx={{ color: '#2E7D32', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => copyToClipboard(trialAccount.email, 'Email')}
                          size="small"
                        >
                          <CopyAll sx={{ fontSize: 18, color: '#666' }} />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#ffffff',
                      border: '1px solid #e0e0e0',
                      '&:hover': {
                        backgroundColor: '#f8f9fa',
                        borderColor: '#4CAF50',
                      },
                    },
                    '& .MuiInputBase-input': {
                      color: '#1a1a1a',
                      fontSize: '1rem',
                      fontWeight: 500,
                    },
                    '& .MuiInputLabel-root': {
                      color: '#666',
                      '&.Mui-focused': {
                        color: '#4CAF50',
                      },
                    },
                  }}
                />
              </Box>

              <Box>
                <TextField
                  fullWidth
                  label="Password"
                  value={trialAccount.password}
                  type={showPassword ? 'text' : 'password'}
                  InputProps={{
                    readOnly: true,
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: '#2E7D32', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          size="small"
                          sx={{ mr: 0.5 }}
                        >
                          {showPassword ? <VisibilityOff sx={{ fontSize: 18, color: '#666' }} /> : <Visibility sx={{ fontSize: 18, color: '#666' }} />}
                        </IconButton>
                        <IconButton
                          onClick={() => copyToClipboard(trialAccount.password, 'Password')}
                          size="small"
                        >
                          <CopyAll sx={{ fontSize: 18, color: '#666' }} />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: '#ffffff',
                      border: '1px solid #e0e0e0',
                      '&:hover': {
                        backgroundColor: '#f8f9fa',
                        borderColor: '#4CAF50',
                      },
                    },
                    '& .MuiInputBase-input': {
                      color: '#1a1a1a',
                      fontSize: '1rem',
                      fontWeight: 500,
                    },
                    '& .MuiInputLabel-root': {
                      color: '#666',
                      '&.Mui-focused': {
                        color: '#4CAF50',
                      },
                    },
                  }}
                />
              </Box>
            </Paper>
          </Grid>

          {/* Trial Limits */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                borderRadius: 3,
                background: 'rgba(255, 255, 255, 0.9)',
                border: '2px solid #2196F3',
              }}
            >
              <Typography variant="h6" sx={{ mb: 2, color: '#1976D2', fontWeight: 600, fontSize: '1.2rem' }}>
                Trial Limits
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Star sx={{ color: '#FF9800', fontSize: 20 }} />
                  <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '1rem', color: '#333' }}>
                    Interviews
                  </Typography>
                </Box>
                <Chip
                  label={`${trialAccount.interview_limit} interviews allowed`}
                  color="primary"
                  variant="outlined"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" sx={{ color: '#666', fontSize: '0.9rem', fontWeight: 500 }}>
                  You can conduct up to {trialAccount.interview_limit} interview sessions
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Star sx={{ color: '#FF9800', fontSize: 20 }} />
                  <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '1rem', color: '#333' }}>
                    Job Roles
                  </Typography>
                </Box>
                <Chip
                  label={`${trialAccount.job_role_limit} job roles allowed`}
                  color="primary"
                  variant="outlined"
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" sx={{ color: '#666', fontSize: '0.9rem', fontWeight: 500 }}>
                  You can create up to {trialAccount.job_role_limit} job role profiles
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box>
                <Typography variant="body2" sx={{ color: '#333', textAlign: 'center', fontSize: '0.9rem', fontWeight: 600 }}>
                  <strong>Trial expires:</strong> {new Date(trialAccount.expires_at).toLocaleDateString()}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: '#333', mb: 2, fontSize: '1rem', fontWeight: 500 }}>
            Use these credentials to login and start your free trial experience!
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button
          onClick={onClose}
          variant="contained"
          sx={{
            borderRadius: 3,
            textTransform: 'none',
            fontWeight: 600,
            background: 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%)',
            },
          }}
        >
          Got it! Let's Login
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TrialAccountPopup;
