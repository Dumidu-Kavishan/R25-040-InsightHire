import React, { createContext, useContext, useState, useEffect } from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material/styles';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Light theme configuration
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#4FC3F7',      // Light blue
      light: '#B3E5FC',     // Very light blue
      dark: '#0288D1',      // Darker blue
    },
    secondary: {
      main: '#29B6F6',      // Complementary blue
      light: '#E1F5FE',     // Extremely light blue
      dark: '#0277BD',      // Dark blue
    },
    background: {
      default: '#FAFAFA',   // Off-white
      paper: '#FFFFFF',     // Pure white
    },
    text: {
      primary: '#2C3E50',   // Dark blue-gray
      secondary: '#607D8B', // Blue-gray
    },
    navbar: {
      background: '#FFFFFF',
      text: '#2C3E50',
      hover: '#E1F5FE',
      border: '#E1F5FE',
    },
    chart: {
      background: '#FFFFFF',
      text: '#2C3E50',
      grid: '#F5F5F5',
      axis: '#999999',
    },
  },
  typography: {
    fontFamily: '"Inter", "Arial", sans-serif',
    h1: { fontWeight: 600 },
    h2: { fontWeight: 600 },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 500 },
    h5: { fontWeight: 500 },
    h6: { fontWeight: 500 },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          backgroundColor: '#4FC3F7',
          color: 'white',
          '&:hover': {
            backgroundColor: '#29B6F6',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(79, 195, 247, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(79, 195, 247, 0.1)',
          border: '1px solid #E1F5FE',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#4FC3F7',
            },
          },
          '& .MuiInputLabel-root.Mui-focused': {
            color: '#4FC3F7',
          },
        },
      },
    },
  },
});

// Dark theme configuration - Enhanced with creative colors
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#64B5F6',      // Bright blue for dark mode
      light: '#90CAF9',     // Lighter blue
      dark: '#1976D2',      // Darker blue
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#81C784',      // Green accent
      light: '#A5D6A7',     // Light green
      dark: '#388E3C',      // Dark green
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#F44336',
      light: '#E57373',
      dark: '#D32F2F',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
      contrastText: '#FFFFFF',
    },
    info: {
      main: '#29B6F6',
      light: '#4FC3F7',
      dark: '#0288D1',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#66BB6A',
      light: '#81C784',
      dark: '#388E3C',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#0D1117',   // GitHub dark background
      paper: '#161B22',     // Slightly lighter for cards
      elevated: '#21262D',  // For elevated elements
    },
    text: {
      primary: '#F0F6FC',   // Bright white text
      secondary: '#8B949E', // Muted gray text
      disabled: '#6E7681',  // Disabled text
      hint: '#7C3AED',      // Purple accent for hints
    },
    divider: '#30363D',     // Subtle dividers
    navbar: {
      background: '#0D1117',
      text: '#F0F6FC',
      hover: '#21262D',
      border: '#30363D',
      active: '#64B5F6',
    },
    chart: {
      background: '#161B22',
      text: '#F0F6FC',
      grid: '#30363D',
      axis: '#8B949E',
      tooltip: '#21262D',
    },
    card: {
      background: '#161B22',
      border: '#30363D',
      hover: '#21262D',
      shadow: 'rgba(0, 0, 0, 0.4)',
    },
    button: {
      primary: '#64B5F6',
      secondary: '#81C784',
      danger: '#F44336',
      text: '#F0F6FC',
    },
    input: {
      background: '#0D1117',
      border: '#30363D',
      focus: '#64B5F6',
      text: '#F0F6FC',
      placeholder: '#8B949E',
    },
    status: {
      success: '#66BB6A',
      warning: '#FF9800',
      error: '#F44336',
      info: '#29B6F6',
    },
  },
  typography: {
    fontFamily: '"Inter", "Arial", sans-serif',
    h1: { fontWeight: 600 },
    h2: { fontWeight: 600 },
    h3: { fontWeight: 600 },
    h4: { fontWeight: 500 },
    h5: { fontWeight: 500 },
    h6: { fontWeight: 500 },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          overflowX: 'hidden !important',
          width: '100%',
          maxWidth: '100%',
          margin: 0,
          padding: 0,
        },
        body: {
          backgroundColor: '#0D1117',
          color: '#F0F6FC',
          margin: 0,
          padding: 0,
          overflowX: 'hidden !important',
          width: '100%',
          maxWidth: '100%',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: '#0D1117',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#30363D',
            borderRadius: '4px',
            '&:hover': {
              background: '#484F58',
            },
          },
        },
        '#root': {
          width: '100%',
          maxWidth: '100%',
          overflowX: 'hidden !important',
        },
        '*': {
          boxSizing: 'border-box',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '8px 16px',
          transition: 'all 0.2s ease-in-out',
        },
        contained: {
          backgroundColor: '#64B5F6',
          color: '#FFFFFF',
          boxShadow: '0 2px 8px rgba(100, 181, 246, 0.3)',
          '&:hover': {
            backgroundColor: '#90CAF9',
            boxShadow: '0 4px 12px rgba(100, 181, 246, 0.4)',
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        outlined: {
          borderColor: '#30363D',
          color: '#F0F6FC',
          '&:hover': {
            borderColor: '#64B5F6',
            backgroundColor: 'rgba(100, 181, 246, 0.1)',
          },
        },
        text: {
          color: '#F0F6FC',
          '&:hover': {
            backgroundColor: 'rgba(100, 181, 246, 0.1)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          backgroundColor: '#161B22',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
          border: '1px solid #30363D',
        },
        elevation1: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        },
        elevation2: {
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
        },
        elevation3: {
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          backgroundColor: '#161B22',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
          border: '1px solid #30363D',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
            borderColor: '#64B5F6',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: '#0D1117',
            color: '#F0F6FC',
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#64B5F6',
              borderWidth: '2px',
            },
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#30363D',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#484F58',
            },
            '&.MuiInputBase-multiline': {
              backgroundColor: '#0D1117',
            },
          },
          '& .MuiInputLabel-root.Mui-focused': {
            color: '#64B5F6',
          },
          '& .MuiInputLabel-root': {
            color: '#8B949E',
          },
          '& .MuiInputBase-input::placeholder': {
            color: '#8B949E',
            opacity: 1,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#0D1117',
          borderBottom: '1px solid #30363D',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#0D1117',
          borderRight: '1px solid #30363D',
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          backgroundColor: '#161B22',
          border: '1px solid #30363D',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
          borderRadius: 12,
        },
        list: {
          padding: '8px',
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 0',
          color: '#F0F6FC',
          '&:hover': {
            backgroundColor: '#21262D',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(100, 181, 246, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(100, 181, 246, 0.2)',
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: '#161B22',
          border: '1px solid #30363D',
          borderRadius: 16,
          boxShadow: '0 16px 48px rgba(0, 0, 0, 0.6)',
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          color: '#F0F6FC',
          borderBottom: '1px solid #30363D',
          paddingBottom: '16px',
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          color: '#F0F6FC',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backgroundColor: '#21262D',
          color: '#F0F6FC',
          border: '1px solid #30363D',
          '&:hover': {
            backgroundColor: '#30363D',
          },
        },
        colorPrimary: {
          backgroundColor: 'rgba(100, 181, 246, 0.2)',
          color: '#64B5F6',
          border: '1px solid #64B5F6',
        },
        colorSecondary: {
          backgroundColor: 'rgba(129, 199, 132, 0.2)',
          color: '#81C784',
          border: '1px solid #81C784',
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: '#64B5F6',
        },
        thumb: {
          '&:hover': {
            boxShadow: '0 0 0 8px rgba(100, 181, 246, 0.16)',
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          color: '#8B949E',
          '&.Mui-checked': {
            color: '#64B5F6',
            '& + .MuiSwitch-track': {
              backgroundColor: '#64B5F6',
            },
          },
        },
        track: {
          backgroundColor: '#30363D',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#21262D',
          color: '#F0F6FC',
          border: '1px solid #30363D',
          fontSize: '0.875rem',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: '#161B22',
          border: '1px solid #30363D',
        },
        standardSuccess: {
          backgroundColor: 'rgba(102, 187, 106, 0.1)',
          border: '1px solid #66BB6A',
          color: '#66BB6A',
        },
        standardError: {
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          border: '1px solid #F44336',
          color: '#F44336',
        },
        standardWarning: {
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          border: '1px solid #FF9800',
          color: '#FF9800',
        },
        standardInfo: {
          backgroundColor: 'rgba(41, 182, 246, 0.1)',
          border: '1px solid #29B6F6',
          color: '#29B6F6',
        },
      },
    },
  },
});

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme !== null) {
      setIsDarkMode(JSON.parse(savedTheme));
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
    }
  }, []);

  // Update body data attribute for CSS targeting
  useEffect(() => {
    document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
  };

  const currentTheme = isDarkMode ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      <MuiThemeProvider theme={currentTheme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
