import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #E3F2FD 0%, #FFFFFF 100%)',
      }}
    >
      <CircularProgress
        size={60}
        sx={{
          color: '#2196F3',
          mb: 2,
        }}
      />
      <Typography
        variant="h6"
        sx={{
          color: '#1976D2',
          fontWeight: 500,
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default LoadingSpinner;
