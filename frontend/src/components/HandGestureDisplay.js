import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  CircularProgress,
  Grid,
  Avatar,
  LinearProgress
} from '@mui/material';
import {
  PanTool,
  ThumbUp,
  RecordVoiceOver,
  TouchApp,
  Gesture
} from '@mui/icons-material';

const HandGestureDisplay = ({ handConfidenceData, isDarkMode }) => {
  const [lastUpdate, setLastUpdate] = useState(null);

  // Gesture icon mapping
  const getGestureIcon = (gesture) => {
    const iconMap = {
      'peace': <Gesture />,
      'thumbs_left': <ThumbUp />,
      'thumbs_right': <ThumbUp />,
      'like': <ThumbUp />,
      'ok': <TouchApp />,
      'grip': <PanTool />,
      'palm': <PanTool />,
      'fist': <PanTool />,
      'pointing': <TouchApp />,
      'call': <RecordVoiceOver />
    };
    return iconMap[gesture] || <Gesture />;
  };

  // Gesture color mapping
  const getGestureColor = (gesture) => {
    const colorMap = {
      'peace': 'success',
      'thumbs_left': 'primary',
      'thumbs_right': 'primary', 
      'like': 'success',
      'ok': 'info',
      'grip': 'warning',
      'palm': 'secondary',
      'fist': 'error',
      'pointing': 'info',
      'call': 'primary'
    };
    return colorMap[gesture] || 'default';
  };

  // Update timestamp when new data is received
  useEffect(() => {
    if (handConfidenceData) {
      setLastUpdate(new Date().toLocaleTimeString());
    }
  }, [handConfidenceData]);

  if (!handConfidenceData) {
    return (
      <Paper 
        elevation={3} 
        sx={{ 
          p: 2, 
          textAlign: 'center',
          backgroundColor: isDarkMode ? '#2c2c2c' : '#ffffff',
          border: isDarkMode ? '1px solid #444' : '1px solid #e0e0e0'
        }}
      >
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <PanTool sx={{ fontSize: 48, opacity: 0.3, mb: 1 }} />
          <Typography variant="body2" sx={{ opacity: 0.7 }}>
            Waiting for hand gesture data...
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 2,
        backgroundColor: isDarkMode ? '#2c2c2c' : '#ffffff',
        border: isDarkMode ? '1px solid #444' : '1px solid #e0e0e0',
        borderRadius: 2
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <PanTool sx={{ mr: 1, color: '#1976d2' }} />
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Hand Gestures
        </Typography>
        {lastUpdate && (
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            Updated: {lastUpdate}
          </Typography>
        )}
      </Box>

      {/* Hand Data Display */}
      <Box>
        {/* Confidence Level */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Confidence Level:
          </Typography>
          <Chip
            label={handConfidenceData.confidence_level || 'unknown'}
            color={
              handConfidenceData.confidence_level === 'confident' ? 'success' :
              handConfidenceData.confidence_level === 'somewhat_confident' ? 'warning' : 'error'
            }
            variant="filled"
            sx={{ fontWeight: 'bold' }}
          />
        </Box>

        {/* Confidence Score */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Confidence Score: {(handConfidenceData.confidence * 100).toFixed(1)}%
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={handConfidenceData.confidence * 100}
                sx={{
                  height: 8,
                  borderRadius: 5,
                  backgroundColor: isDarkMode ? '#444' : '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: handConfidenceData.confidence > 0.7 ? '#4caf50' : 
                                   handConfidenceData.confidence > 0.4 ? '#ff9800' : '#f44336'
                  }
                }}
              />
            </Box>
          </Box>
        </Box>

        {/* Detected Gestures */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Detected Gestures:
          </Typography>
          {handConfidenceData.gestures_detected && handConfidenceData.gestures_detected.length > 0 ? (
            <Grid container spacing={1}>
              {handConfidenceData.gestures_detected.map((gesture, index) => (
                <Grid item xs="auto" key={index}>
                  <Chip
                    icon={getGestureIcon(gesture)}
                    label={gesture}
                    color={getGestureColor(gesture)}
                    variant="outlined"
                    sx={{
                      animation: 'pulse 2s infinite',
                      fontWeight: 'bold',
                      textTransform: 'capitalize'
                    }}
                  />
                </Grid>
              ))}
            </Grid>
          ) : (
            <Typography variant="body2" sx={{ fontStyle: 'italic', opacity: 0.7 }}>
              No gestures detected
            </Typography>
          )}
        </Box>

        {/* Hands Detected Count */}
        <Box sx={{ mb: 1 }}>
          <Typography variant="body2">
            Hands Detected: {handConfidenceData.hands_detected || 0}
          </Typography>
        </Box>

        {/* Method */}
        <Box sx={{ mb: 1 }}>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            Method: {handConfidenceData.method || 'unknown'}
          </Typography>
        </Box>

        {/* Timestamp */}
        {handConfidenceData.timestamp && (
          <Box>
            <Typography variant="caption" sx={{ opacity: 0.7 }}>
              Last Detection: {new Date(handConfidenceData.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default HandGestureDisplay;