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
      {/* Header */}
      <Box sx={{ mb: 4 }}>
            <Typography 
          variant="h4" 
              sx={{ 
            color: '#1e293b',
            fontWeight: 700,
            fontSize: '2.5rem',
            mb: 1
          }}
        >
          Settings
            </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{
            borderRadius: 2,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0',
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
                },
                '& .Mui-selected': {
                  backgroundColor: '#f1f5f9',
                  color: '#1e293b',
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
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            border: '1px solid #e2e8f0',
            minHeight: 500,
          }}>
            {/* Profile Settings */}
            <TabPanel value={activeTab} index={0}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#1e293b' }}>
                Profile Information
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
                        bgcolor: '#3b82f6',
                        fontSize: '1.8rem',
                      }}
                    >
                      {displayName?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                    </Avatar>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<CloudUpload />}
                      sx={{ borderRadius: 2 }}
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
                            color: '#666', 
                            mb: 1, 
                            fontWeight: 500 
                          }}
                        >
                          Display Name
                        </Typography>
                        <input
                          key={inputKey}
                          ref={displayNameRef}
                          type="text"
                          value={displayName}
                          onChange={handleDisplayNameChange}
                          onFocus={(e) => {
                            e.target.style.borderColor = '#3b82f6';
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
                            border: `1px solid ${theme.palette.divider}`,
                            backgroundColor: profileLoading ? theme.palette.action.disabledBackground : theme.palette.background.paper,
                            color: theme.palette.text.primary,
                            outline: 'none',
                            transition: 'border-color 0.2s ease',
                            boxSizing: 'border-box',
                            cursor: profileLoading ? 'not-allowed' : 'text',
                          }}
                          onBlur={(e) => {
                            e.target.style.borderColor = theme.palette.divider;
                          }}
                          onMouseEnter={(e) => {
                            if (!profileLoading) {
                              e.target.style.borderColor = theme.palette.action.hover;
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!e.target.matches(':focus')) {
                              e.target.style.borderColor = theme.palette.divider;
                            }
                          }}
                        />
                        <Typography 
                          variant="caption" 
                          sx={(theme) => ({ 
                            color: theme.palette.text.secondary, 
                            mt: 0.5, 
                            display: 'block' 
                          })}
                        >
                          {profileLoading ? "Loading profile..." : "You can edit this field"}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Box sx={{ mb: 1 }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: '#374151', 
                            mb: 1, 
                            fontWeight: 500 
                          }}
                        >
                          Email
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
                            border: `1px solid ${theme.palette.divider}`,
                            backgroundColor: theme.palette.action.disabledBackground,
                            outline: 'none',
                            boxSizing: 'border-box',
                            cursor: 'not-allowed',
                            color: theme.palette.text.disabled,
                          }}
                        />
                      </Box>
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </TabPanel>

            {/* Notification Settings */}
            <TabPanel value={activeTab} index={1}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
                Notification Preferences
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Notifications color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email Notifications"
                    secondary="Receive updates via email"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.emailNotifications}
                      onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <VolumeUp color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Push Notifications"
                    secondary="Browser notifications for real-time updates"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.pushNotifications}
                      onChange={(e) => handleSettingChange('pushNotifications', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <Schedule color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Session Reminders"
                    secondary="Get notified about upcoming interviews"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.sessionReminders}
                      onChange={(e) => handleSettingChange('sessionReminders', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <Analytics color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Weekly Reports"
                    secondary="Receive weekly analytics summaries"
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
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 'bold' }}>
                Privacy & Security
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Visibility color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Profile Visibility"
                    secondary="Make your profile visible to other users"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.profileVisible}
                      onChange={(e) => handleSettingChange('profileVisible', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <InsertChart color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Share Analytics"
                    secondary="Allow anonymous analytics data sharing"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={settings.shareAnalytics}
                      onChange={(e) => handleSettingChange('shareAnalytics', e.target.checked)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <Storage color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Data Retention"
                    secondary="How long to keep your data"
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label="12 months"
                      color="primary"
                      variant="outlined"
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
                  backgroundColor: '#3b82f6',
                  '&:hover': {
                    backgroundColor: '#2563eb',
                  },
                  '&:disabled': {
                    backgroundColor: '#9ca3af',
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
