import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Button,
  Switch,
  Avatar,
  Chip,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  CircularProgress
} from '@mui/material';
import {
  AccountCircle,
  Notifications,
  Security,
  Analytics,
  Save,
  CloudUpload,
  VolumeUp,
  Storage,
  Visibility,
  Schedule,
  InsertChart
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '@mui/material/styles';
import { toast } from 'react-toastify';
import { userProfileService } from '../services/userProfileService';

const Settings = () => {
  const { user } = useAuth();
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);
  const [, setUserProfile] = useState(null);
  const [displayName, setDisplayName] = useState('');
  const [username, setUsername] = useState('');
  const displayNameRef = useRef(null);
  const [inputKey, setInputKey] = useState(0);
  const [settings, setSettings] = useState({
    // Profile settings
    username: user?.username || '',
    displayName: user?.displayName || '',
    email: user?.email || '',
    avatar: '',
    
    // Notification settings
    emailNotifications: true,
    pushNotifications: true,
    sessionReminders: true,
    weeklyReports: false,
    
    // Privacy settings
    profileVisible: true,
    shareAnalytics: false,
    dataRetention: '12months',
    
    // Application settings
    theme: 'light',
    language: 'en',
  });

  const loadUserProfile = useCallback(async () => {
    try {
      setProfileLoading(true);
      const response = await userProfileService.getProfile();
      
      if (response.status === 'success') {
        const profile = response.data;
        setUserProfile(profile);
        const profileDisplayName = profile.username || profile.display_name || user?.email || '';
        setDisplayName(profileDisplayName);
        setUsername(profile.username || profileDisplayName);
        setInputKey(prev => prev + 1); // Force re-render
        setSettings(prev => ({
          ...prev,
          username: profile.username || profileDisplayName,
          displayName: profileDisplayName,
          email: profile.email || user?.email || '',
          avatar: profile.avatar_url || ''
        }));
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      // Fallback to user data if profile loading fails
      // But prioritize username from user context if available
      const fallbackDisplayName = user?.username || user?.displayName || user?.email || '';
      setDisplayName(fallbackDisplayName);
      setUsername(user?.username || fallbackDisplayName);
      setInputKey(prev => prev + 1); // Force re-render
      setSettings(prev => ({
        ...prev,
        username: user?.username || fallbackDisplayName,
        displayName: fallbackDisplayName,
        email: user?.email || ''
      }));
    } finally {
      setProfileLoading(false);
    }
  }, [user]);

  // Load user profile on component mount
  useEffect(() => {
    // Don't set initial values from user context - let loadUserProfile handle it
    // This ensures we always get the latest data from the database
    loadUserProfile();
  }, [user, loadUserProfile]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleDisplayNameChange = (event) => {
    const value = event.target.value;
    setDisplayName(value);
    setUsername(value); // Also update username state
    setSettings(prev => ({
      ...prev,
      username: value, // Update username in settings
      displayName: value
    }));
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      const response = await userProfileService.updateProfile({
        username: settings.username,
        display_name: settings.displayName,
        avatar_url: settings.avatar
      });
      
      if (response.status === 'success') {
        setUserProfile(response.data);
        
        // Update localStorage with new user data
        const updatedUserData = {
          ...user,
          username: settings.username,
          displayName: settings.displayName
        };
        localStorage.setItem('user', JSON.stringify(updatedUserData));
        
        toast.success('Profile updated successfully!');
        
        // Show a message that the page will refresh to update the header
        setTimeout(() => {
          toast.info('Refreshing page to update header...');
          window.location.reload();
        }, 1500);
        
      } else {
        toast.error(response.message || 'Failed to update profile');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      toast.error('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      // Here you would normally save to the backend
      console.log('Saving settings:', settings);
      toast.success('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{
            borderRadius: 2,
            boxShadow: theme.palette.mode === 'dark' ? '0 4px 12px rgba(0,0,0,0.3)' : '0 4px 12px rgba(0,0,0,0.1)',
            border: theme.palette.mode === 'dark' ? '1px solid #374151' : '1px solid #e0e0e0',
            overflow: 'hidden',
            backgroundColor: theme.palette.mode === 'dark' ? '#1f2937' : '#ffffff'
          }}>
            <Tabs
              orientation="vertical"
              value={activeTab}
              onChange={handleTabChange}
              sx={{
                '& .MuiTab-root': {
                  alignItems: 'flex-start',
                  justifyContent: 'flex-start',
                  textAlign: 'left',
                  minHeight: 50,
                  px: 2,
                  py: 1.5,
                  fontSize: '0.9rem',
                  color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666',
                  transition: 'all 0.2s ease-in-out',
                  borderRight: '3px solid transparent',
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' ? '#374151' : '#f5f5f5',
                    color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#333333',
                  },
                },
                '& .Mui-selected': {
                  backgroundColor: theme.palette.mode === 'dark' ? '#1e40af' : '#e3f2fd',
                  color: theme.palette.mode === 'dark' ? '#ffffff' : '#1976d2',
                  fontWeight: 600,
                  borderRight: theme.palette.mode === 'dark' ? '3px solid #3b82f6' : '3px solid #2196f3',
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' ? '#1e40af' : '#e3f2fd',
                    color: theme.palette.mode === 'dark' ? '#ffffff' : '#1976d2',
                  },
                },
                '& .MuiTabs-indicator': {
                  display: 'none',
                },
              }}
            >
              <Tab
                icon={<AccountCircle />}
                label="Profile"
                iconPosition="start"
              />
              <Tab
                icon={<Notifications />}
                label="Notifications"
                iconPosition="start"
              />
              <Tab
                icon={<Security />}
                label="Privacy & Security"
                iconPosition="start"
              />
            </Tabs>
          </Paper>
        </Grid>

        {/* Content */}
        <Grid item xs={12} md={9}>
          <Paper sx={{
            p: 3,
            borderRadius: 2,
            boxShadow: theme.palette.mode === 'dark' ? '0 4px 12px rgba(0,0,0,0.3)' : '0 4px 12px rgba(0,0,0,0.1)',
            border: theme.palette.mode === 'dark' ? '1px solid #374151' : '1px solid #e0e0e0',
            minHeight: 500,
            backgroundColor: theme.palette.mode === 'dark' ? '#1f2937' : '#ffffff',
          }}>
            {/* Profile Settings */}
            <TabPanel value={activeTab} index={0}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a' }}>
                👤 Profile Information
              </Typography>
              
              {profileLoading && (
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <CircularProgress size={20} sx={{ mr: 2 }} />
                  <Typography variant="body2" color="textSecondary">
                    Loading profile...
                  </Typography>
                </Box>
              )}
              
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Avatar
                      sx={{
                        width: 100,
                        height: 100,
                        mx: 'auto',
                        mb: 2,
                        bgcolor: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                        fontSize: '1.8rem',
                        fontWeight: 'bold',
                        color: '#ffffff',
                        boxShadow: theme.palette.mode === 'dark' ? '0 4px 12px rgba(59, 130, 246, 0.3)' : '0 4px 12px rgba(33, 150, 243, 0.3)',
                      }}
                    >
                      {displayName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                    </Avatar>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<CloudUpload />}
                      sx={{ 
                        borderRadius: 2,
                        borderColor: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                        color: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                        fontWeight: 600,
                        '&:hover': {
                          backgroundColor: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                          color: '#ffffff',
                          borderColor: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                        },
                      }}
                    >
                      Upload Photo
                    </Button>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={8}>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Box sx={{ mb: 1 }}>
                        <Typography 
                          variant="body2" 
                          sx={{
                            color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#333333', 
                            mb: 1, 
                            fontWeight: 600 
                          }}
                        >
                          ✏️ Display Name
                        </Typography>
                        <input
                          key={inputKey}
                          ref={displayNameRef}
                          type="text"
                          value={displayName}
                          onChange={handleDisplayNameChange}
                          onFocus={(e) => {
                            const focusColor = theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3';
                            e.target.style.borderColor = focusColor;
                            e.target.style.boxShadow = `0 0 0 2px ${theme.palette.mode === 'dark' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(33, 150, 243, 0.2)'}`;
                            // Restore cursor to end of text
                            setTimeout(() => {
                              e.target.setSelectionRange(e.target.value.length, e.target.value.length);
                            }, 0);
                          }}
                          disabled={profileLoading}
                          placeholder="Enter your display name"
                          autoComplete="off"
                          style={{
                            width: '100%',
                            padding: '12px 16px',
                            fontSize: '16px',
                            borderRadius: '8px',
                            border: theme.palette.mode === 'dark' ? '2px solid #374151' : '2px solid #e0e0e0',
                            backgroundColor: profileLoading 
                              ? (theme.palette.mode === 'dark' ? '#374151' : '#f5f5f5')
                              : (theme.palette.mode === 'dark' ? '#111827' : '#ffffff'),
                            color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a',
                            outline: 'none',
                            transition: 'all 0.2s ease',
                            boxSizing: 'border-box',
                            cursor: profileLoading ? 'not-allowed' : 'text',
                            fontWeight: '500',
                          }}
                          onBlur={(e) => {
                            e.target.style.borderColor = theme.palette.mode === 'dark' ? '#374151' : '#e0e0e0';
                            e.target.style.boxShadow = 'none';
                          }}
                          onMouseEnter={(e) => {
                            if (!profileLoading) {
                              e.target.style.borderColor = theme.palette.mode === 'dark' ? '#4b5563' : '#bdbdbd';
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!e.target.matches(':focus')) {
                              e.target.style.borderColor = theme.palette.mode === 'dark' ? '#374151' : '#e0e0e0';
                            }
                          }}
                        />
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', 
                            mt: 0.5, 
                            display: 'block',
                            fontSize: '0.85rem'
                          }}
                        >
                          💡 {profileLoading ? "Loading profile..." : "You can edit this field"}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Box sx={{ mb: 1 }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#333333', 
                            mb: 1, 
                            fontWeight: 600 
                          }}
                        >
                          📧 Email Address
                        </Typography>
                        <input
                          type="text"
                          value={settings.email}
                          disabled
                          style={{
                            width: '100%',
                            padding: '12px 16px',
                            fontSize: '16px',
                            borderRadius: '8px',
                            border: theme.palette.mode === 'dark' ? '2px solid #374151' : '2px solid #e0e0e0',
                            backgroundColor: theme.palette.mode === 'dark' ? '#374151' : '#f5f5f5',
                            outline: 'none',
                            boxSizing: 'border-box',
                            cursor: 'not-allowed',
                            color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666',
                            fontWeight: '500',
                          }}
                        />
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: theme.palette.mode === 'dark' ? '#6b7280' : '#999999', 
                            mt: 0.5, 
                            display: 'block',
                            fontSize: '0.85rem'
                          }}
                        >
                          🔒 This field cannot be edited
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </TabPanel>

            {/* Notification Settings */}
            <TabPanel value={activeTab} index={1}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a' }}>
                🔔 Notification Preferences
              </Typography>
              
              <List>
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Notifications sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Email Notifications
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Receive updates via email
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.emailNotifications}
                      onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <VolumeUp sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Push Notifications
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Browser notifications for real-time updates
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.pushNotifications}
                      onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Schedule sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Session Reminders
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Get notified about upcoming interviews
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.sessionReminders}
                      onChange={(e) => handleSettingChange('sessionReminders', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Analytics sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Weekly Reports
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Receive weekly analytics summaries
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.weeklyReports}
                      onChange={(e) => handleSettingChange('weeklyReports', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </TabPanel>

            {/* Privacy & Security */}
            <TabPanel value={activeTab} index={2}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a' }}>
                🔒 Privacy & Security
              </Typography>
              
              <List>
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Visibility sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Profile Visibility
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Make your profile visible to other users
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.profileVisible}
                      onChange={(e) => handleSettingChange('profileVisible', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <InsertChart sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Share Analytics
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        Allow anonymous analytics data sharing
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.shareAnalytics}
                      onChange={(e) => handleSettingChange('shareAnalytics', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem sx={{ py: 2 }}>
                  <ListItemIcon>
                    <Storage sx={{ color: '#2196f3' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#f3f4f6' : '#1a1a1a', fontWeight: 600, fontSize: '1rem' }}>
                        Data Retention
                      </Typography>
                    }
                    secondary={
                      <Typography sx={{ color: theme.palette.mode === 'dark' ? '#9ca3af' : '#666666', fontSize: '0.9rem' }}>
                        How long to keep your data
                      </Typography>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label="12 months"
                      sx={{
                        backgroundColor: '#3b82f6',
                        color: '#ffffff',
                        fontWeight: 600,
                        '&:hover': {
                          backgroundColor: '#2563eb',
                        }
                      }}
                      clickable
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
              
              <Alert severity="info" sx={{ mt: 3 }}>
                Your privacy is important to us. We only collect data necessary for improving your interview experience.
              </Alert>
            </TabPanel>



            {/* Save Button */}
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Save />}
                onClick={activeTab === 0 ? handleSaveProfile : handleSaveSettings}
                disabled={loading || profileLoading}
                sx={{
                  borderRadius: 2,
                  px: 3,
                  py: 1.5,
                  backgroundColor: theme.palette.mode === 'dark' ? '#3b82f6' : '#2196f3',
                  color: '#ffffff',
                  fontWeight: 600,
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' ? '#2563eb' : '#1976d2',
                  },
                  '&:disabled': {
                    backgroundColor: theme.palette.mode === 'dark' ? '#6b7280' : '#bdbdbd',
                    color: '#ffffff',
                  },
                }}
              >
                {activeTab === 0 ? 'Save Profile' : 'Save Settings'}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Settings;
