import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
  Divider,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  Analytics,
  Settings,
  Logout,
  Work,
  DarkMode,
  LightMode,
  Diamond,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { usePremiumCode } from '../contexts/PremiumCodeContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const { hasPremiumAccess } = usePremiumCode();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = React.useState(null);

  // Debug: Log the current theme state
  console.log('Navbar - isDarkMode:', isDarkMode);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    // Redirect to root path to trigger premium code gate
    navigate('/');
    handleClose();
  };


  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  const getDisplayName = () => {
    if (user?.username) return user.username;
    if (user?.displayName) return user.displayName;
    if (user?.name) return user.name;
    if (user?.email) return user.email; // Show full email instead of just username part
    return 'User';
  };

  const getUserInitials = () => {
    const name = getDisplayName();
    
    // If it's an email address, use the first 2 characters of the username part
    if (name.includes('@')) {
      const username = name.split('@')[0];
      return username.substring(0, 2).toUpperCase();
    }
    
    // If it's a regular name, use first letter of each word
    return name.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <AppBar
      position="fixed"
      sx={(theme) => ({
        backgroundColor: theme.palette.navbar.background,
        color: theme.palette.navbar.text,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        borderBottom: `1px solid ${theme.palette.navbar.border}`,
        '& .MuiToolbar-root': {
          backgroundColor: theme.palette.navbar.background,
          color: theme.palette.navbar.text,
        }
      })}
    >
      <Toolbar>
        {/* Logo/Brand */}
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mr: 4, 
            cursor: 'pointer',
            gap: 1,
          }}
          onClick={() => handleNavigation('/dashboard')}
        >
          <Typography
            variant="h6"
            component="div"
            sx={(theme) => ({
              fontWeight: 600,
              color: theme.palette.primary.main,
            })}
          >
            InsightHire
          </Typography>
          {hasPremiumAccess && (
            <Tooltip title="Premium Access Active">
              <Chip
                icon={<Diamond />}
                label="Premium"
                size="small"
                sx={{
                  backgroundColor: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  height: 24,
                  '& .MuiChip-icon': {
                    color: 'white',
                    fontSize: '1rem',
                  },
                }}
              />
            </Tooltip>
          )}
        </Box>

        {/* Navigation Links */}
        <Box sx={{ flexGrow: 1, display: 'flex', gap: 1 }}>
          <Button
            startIcon={<Dashboard />}
            onClick={() => handleNavigation('/dashboard')}
            sx={(theme) => ({
              color: isActive('/dashboard') ? theme.palette.primary.main : theme.palette.navbar.text,
              backgroundColor: isActive('/dashboard') ? theme.palette.navbar.hover : 'transparent',
              fontWeight: isActive('/dashboard') ? 600 : 400,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: theme.palette.navbar.hover,
                color: theme.palette.navbar.text,
              },
            })}
          >
            Dashboard
          </Button>
          
          <Button
            startIcon={<Analytics />}
            onClick={() => handleNavigation('/analytics')}
            sx={(theme) => ({
              color: isActive('/analytics') ? theme.palette.primary.main : theme.palette.navbar.text,
              backgroundColor: isActive('/analytics') ? theme.palette.navbar.hover : 'transparent',
              fontWeight: isActive('/analytics') ? 600 : 400,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: theme.palette.navbar.hover,
                color: theme.palette.navbar.text,
              },
            })}
          >
            Analytics
          </Button>

          <Button
            startIcon={<Work />}
            onClick={() => handleNavigation('/hr-analytics')}
            sx={(theme) => ({
              color: isActive('/hr-analytics') ? theme.palette.primary.main : theme.palette.navbar.text,
              backgroundColor: isActive('/hr-analytics') ? theme.palette.navbar.hover : 'transparent',
              fontWeight: isActive('/hr-analytics') ? 600 : 400,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: theme.palette.navbar.hover,
                color: theme.palette.navbar.text,
              },
            })}
          >
            HR Management
          </Button>
        </Box>

        {/* User Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Dark Mode Toggle */}
          <Tooltip title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
            <IconButton
              onClick={toggleTheme}
              sx={(theme) => ({
                color: theme.palette.navbar.text,
                borderRadius: 2,
                '&:hover': {
                  backgroundColor: theme.palette.navbar.hover,
                },
              })}
            >
              {isDarkMode ? <LightMode /> : <DarkMode />}
            </IconButton>
          </Tooltip>

          <Typography variant="body2" sx={(theme) => ({ 
            color: theme.palette.text.secondary,
            fontWeight: 500,
          })}>
            {getDisplayName()}
          </Typography>

          <IconButton
            onClick={handleMenu}
            sx={(theme) => ({
              borderRadius: 2,
              '&:hover': {
                backgroundColor: theme.palette.navbar.hover,
              },
            })}
          >
            {user?.photoURL ? (
              <Avatar 
                src={user.photoURL} 
                sx={{ width: 32, height: 32 }} 
              />
            ) : (
              <Avatar 
                sx={(theme) => ({ 
                  width: 32, 
                  height: 32, 
                  bgcolor: theme.palette.primary.main,
                  fontSize: '0.875rem',
                  fontWeight: 600,
                })}
              >
                {getUserInitials()}
              </Avatar>
            )}
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            sx={(theme) => ({
              '& .MuiPaper-root': {
                borderRadius: 2,
                minWidth: 200,
                backgroundColor: theme.palette.background.paper,
                boxShadow: isDarkMode 
                  ? '0 2px 10px rgba(0, 0, 0, 0.3)' 
                  : '0 2px 10px rgba(0, 0, 0, 0.1)',
                border: `1px solid ${theme.palette.navbar.border}`,
                mt: 1,
                '& .MuiMenuItem-root': {
                  px: 2,
                  py: 1.5,
                  fontSize: '0.875rem',
                  color: theme.palette.text.primary,
                  '&:hover': {
                    backgroundColor: theme.palette.navbar.hover,
                  },
                  '&.Mui-disabled': {
                    opacity: 0.7,
                  },
                },
                '& .MuiDivider-root': {
                  my: 0.5,
                  borderColor: theme.palette.navbar.border,
                },
              },
            })}
          >
            <MenuItem onClick={() => { handleClose(); handleNavigation('/settings'); }}>
              <Settings sx={(theme) => ({ mr: 2, color: theme.palette.primary.main, fontSize: 20 })} />
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout sx={(theme) => ({ mr: 2, color: theme.palette.text.secondary, fontSize: 20 })} />
              Sign Out
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
