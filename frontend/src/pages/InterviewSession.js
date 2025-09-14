import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Mic,
  Stop,
  PlayArrow,
  Visibility,
  VisibilityOff,
  MicOff,
  Analytics,
  Face,
  PanTool,
  RemoveRedEye,
  RecordVoiceOver
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { interviewService } from '../services/api';
import socketService from '../services/socket';
import { toast } from 'react-toastify';
import ScreenRecorder from '../components/ScreenRecorder';
import { useTheme } from '../contexts/ThemeContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const InterviewSession = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { isDarkMode } = useTheme();
  
  // Add CSS animation for real-time updates
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  const [interview, setInterview] = useState(null);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [showVideo, setShowVideo] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalysisActive, setIsAnalysisActive] = useState(false);
  
  // Screen recording states
  const [isScreenRecording, setIsScreenRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('idle'); // 'idle', 'starting', 'recording', 'stopping'
  const screenRecorderRef = useRef(null);
  
  const [analysisResults, setAnalysisResults] = useState({
    face_stress: { stress_level: 'unknown', confidence: 0 },
    hand_confidence: { confidence_level: 'unknown', confidence: 0 },
    eye_confidence: { confidence_level: 'unknown', confidence: 0 },
    voice_confidence: { confidence_level: 'unknown', confidence: 0 },
    overall: { confidence_score: 0.5, stress_score: 0.5 }
  });
  
  // Real-time analysis state for 10-second updates
  const [realtimeAnalysis, setRealtimeAnalysis] = useState({
    lastUpdate: null,
    confidence: { eye: 0, hand: 0, voice: 0, overall: 0 },
    stress: 0,
    emotion: 'neutral',
    updateCount: 0
  });

  // Track shown notifications to prevent duplicates
  const [shownNotifications, setShownNotifications] = useState(new Set());

  // Helper function to show notification only once
  const showNotificationOnce = (message, type = 'success') => {
    if (!shownNotifications.has(message)) {
      setShownNotifications(prev => new Set([...prev, message]));
      if (type === 'success') {
        toast.success(message);
      } else if (type === 'error') {
        toast.error(message);
      } else if (type === 'info') {
        toast.info(message);
      } else if (type === 'warning') {
        toast.warning(message);
      }
    }
  };
  // Separate chart data for stress and confidence
  const [stressChartData, setStressChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Face Stress Level',
        data: [],
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  });

  const [confidenceChartData, setConfidenceChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Hand Confidence',
        data: [],
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Eye Contact',
        data: [],
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Voice Confidence',
        data: [],
        borderColor: '#9333EA',
        backgroundColor: 'rgba(147, 51, 234, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  });

  useEffect(() => {
    loadInterview();
    initializeSocket();

    // Listen for analysis updates
    const handleAnalysisUpdate = async (event) => {
      const data = event.detail;
      console.log('📊 Received analysis update in component:', data);
      
      if (data.session_id === sessionId && data.analysis) {
        console.log('✅ Updating analysis results with:', data.analysis);
        setAnalysisResults(data.analysis);
        updateCharts(data.analysis);
        
        // Update real-time analysis state every 10 seconds
        const now = new Date();
        setRealtimeAnalysis(prev => ({
          lastUpdate: now,
          confidence: {
            eye: data.analysis.eye_confidence?.confidence_level === 'confident' ? 100 : 0,
            hand: data.analysis.hand_confidence?.confidence_level === 'confident' ? 100 : 0,
            voice: data.analysis.voice_confidence?.confidence_level === 'confident' ? 100 : 0,
            overall: data.analysis.overall?.confidence_score * 100 || 0
          },
          stress: data.analysis.face_stress?.stress_level === 'stress' ? 100 : 0,
          emotion: data.analysis.face_stress?.emotion || 'neutral',
          updateCount: prev.updateCount + 1
        }));
        
        // Send analysis data to backend in new format with binary values
        console.log('🔍 Interview active status:', isInterviewActive);
        
        // Only process analysis if interview is actively running
        // Remove auto-start logic to prevent unwanted restarts after session ends
        
        // DISABLED: Frontend no longer sends analysis data to backend
        // The RealTimeAnalyzer handles all database saving automatically
        // This prevents duplicate records and excessive database writes
        console.log('📊 Analysis data received - RealTimeAnalyzer will handle database saving automatically');
      }
    };

    window.addEventListener('analysisUpdate', handleAnalysisUpdate);

    // Listen for session join status
    const handleSessionJoined = (event) => {
      const data = event.detail;
      console.log('🔌 Session join status:', data);
      
      if (data.session_id === sessionId) {
        setIsAnalysisActive(data.analysis_active);
        if (data.analysis_active) {
          console.log('✅ Analysis is active for this session');
          showNotificationOnce('Real-time analysis is running!');
        } else {
          console.log('📊 Analysis is not active - no warning shown');
          // Completely removed warning notifications - no popup shown
        }
      }
    };
    window.addEventListener('sessionJoined', handleSessionJoined);
    
    // Add cleanup when user closes/refreshes browser
    const handleBeforeUnload = () => {
      console.log('🧹 Browser closing/refreshing - running cleanup...');
      cleanupInterview();
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      console.log('🧹 Component unmounting - running cleanup...');
      cleanupInterview();
      window.removeEventListener('analysisUpdate', handleAnalysisUpdate);
      window.removeEventListener('sessionJoined', handleSessionJoined);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadInterview = async () => {
    try {
      setIsLoading(true);
      const response = await interviewService.getInterview(sessionId);
      if (response.status === 'success') {
        setInterview(response.interview);
        setIsInterviewActive(response.interview.status === 'active');
      } else {
        toast.error(response.message || 'Interview not found');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error loading interview:', error);
      toast.error('Failed to load interview');
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeSocket = () => {
    socketService.connect();
    socketService.joinSession(sessionId);

    socketService.onLiveResults((data) => {
      if (data.interview_id === sessionId) {
        setAnalysisResults(data.results);
        updateCharts(data.results);
        
        // Collect analysis data for final scoring (binary classification)
        if (isInterviewActive) {
          collectAnalysisData('confidence', {
            voice_confidence: (data.results.voice_confidence?.confidence || 0) > 0.5,
            hand_confidence: (data.results.hand_confidence?.confidence || 0) > 0.5,
            eye_confidence: (data.results.eye_confidence?.confidence || 0) > 0.5
          });
          
          collectAnalysisData('stress', {
            is_stressed: (data.results.face_stress?.stress_level || 0) > 0.5
          });
        }
      }
    });

    socketService.onJoinedSession((data) => {
      console.log('Joined interview session:', data.interview_id);
    });
  };

  const updateCharts = (results) => {
    const currentTime = new Date().toLocaleTimeString();
    
    // Convert analysis results to binary values for charting
    const convertToChartValue = (analysisData, type) => {
      if (!analysisData || !analysisData[type] || analysisData[type] === 'no_data') {
        return 0.1; // analyzing state
      }
      
      const level = analysisData[type].toLowerCase();
      
      if (type === 'stress_level') {
        return level === 'stress' ? 1 : 0;
      } else if (type === 'confidence_level') {
        return level === 'confident' ? 1 : 0;
      }
      
      return 0;
    };

    // Update Stress Chart (Face Stress only)
    const faceStressValue = convertToChartValue(results.face_stress, 'stress_level');
    
    setStressChartData(prevData => {
      const newData = { ...prevData };
      
      // Keep only last 20 data points
      if (newData.labels.length >= 20) {
        newData.labels.shift();
        newData.datasets[0].data.shift();
      }

      newData.labels.push(currentTime);
      newData.datasets[0].data.push(faceStressValue);

      return newData;
    });

    // Update Confidence Chart (Hand, Eye, Voice)
    const handConfValue = convertToChartValue(results.hand_confidence, 'confidence_level');
    const eyeConfValue = convertToChartValue(results.eye_confidence, 'confidence_level');
    const voiceConfValue = convertToChartValue(results.voice_confidence, 'confidence_level');
    
    setConfidenceChartData(prevData => {
      const newData = { ...prevData };
      
      // Keep only last 20 data points
      if (newData.labels.length >= 20) {
        newData.labels.shift();
        newData.datasets[0].data.shift(); // Hand
        newData.datasets[1].data.shift(); // Eye
        newData.datasets[2].data.shift(); // Voice
      }

      newData.labels.push(currentTime);
      newData.datasets[0].data.push(handConfValue);  // Hand Confidence
      newData.datasets[1].data.push(eyeConfValue);   // Eye Contact
      newData.datasets[2].data.push(voiceConfValue); // Voice Confidence

      return newData;
    });
  };

  const startInterview = async () => {
    try {
      // Set interview as active first to enable screen recording
      setIsInterviewActive(true);
      
      // Ensure socket connection is established
      console.log('🔌 Ensuring socket connection...');
      socketService.connect();
      socketService.joinSession(sessionId);
      
      // Then start screen recording (this will prompt for screen selection)
      await startScreenRecording();
      
      // Finally start the interview session backend
      console.log('🚀 Starting interview session...');
      const response = await interviewService.startInterview(sessionId);
      if (response.status === 'success') {
        console.log('✅ Interview started successfully:', response);
        if (response.analysis_started) {
          setIsAnalysisActive(true);
          showNotificationOnce('Interview, screen recording, and analysis started successfully!');
        } else {
          showNotificationOnce('Interview and screen recording started successfully!');
        }
      } else {
        toast.error(response.message || 'Failed to start interview');
        // If interview fails, stop everything
        if (isScreenRecording && screenRecorderRef.current) {
          screenRecorderRef.current.stopRecording();
        }
        setIsInterviewActive(false);
      }
    } catch (error) {
      console.error('Error starting interview:', error);
      toast.error('Failed to start interview and screen recording');
      setRecordingStatus('idle');
      setIsScreenRecording(false);
      setIsInterviewActive(false);
    }
  };

  const [showEndSessionDialog, setShowEndSessionDialog] = useState(false);
  const [analysisData, setAnalysisData] = useState({
    confidenceData: [],
    stressData: [],
    sessionStartTime: null,
    sessionDuration: 0
  });

  const stopInterview = async () => {
    setShowEndSessionDialog(true);
  };

  const confirmEndSession = async () => {
    try {
      // Calculate session duration
      const sessionDuration = analysisData.sessionStartTime ? 
        Math.floor((Date.now() - analysisData.sessionStartTime) / 1000) : 120;
      
      // DISABLED: No longer submit analysis data from frontend
      // The RealTimeAnalyzer handles all database saving automatically
      // This prevents duplicate records and excessive database writes
      console.log('📊 Session ending - RealTimeAnalyzer has already saved all analysis data');
      
      const response = await interviewService.stopInterview(sessionId);
      if (response.status === 'success') {
        // Send audio stop signal after stopping the interview to reset voice confidence
        console.log('🛑 Sending audio stop signal after stopping interview');
        socketService.sendAudioData(sessionId, null);
        
        // Stop screen recording if it's active
        if (isScreenRecording && screenRecorderRef.current) {
          screenRecorderRef.current.stopRecording();
          setIsScreenRecording(false);
          setRecordingStatus('idle');
        }
        
        // Clean up everything to stop all backend analysis and connections
        console.log('🧹 Cleaning up all connections and stopping analysis');
        cleanupInterview();
        
        showNotificationOnce('Interview and screen recording stopped successfully!');
        
        // Navigate to dashboard after successful stop and cleanup
        navigate('/dashboard');
      } else {
        toast.error(response.message || 'Failed to stop interview');
      }
    } catch (error) {
      console.error('Error stopping interview:', error);
      toast.error('Failed to stop interview');
    } finally {
      setShowEndSessionDialog(false);
    }
  };

  const cancelEndSession = () => {
    setShowEndSessionDialog(false);
  };

  // Function to collect analysis data during interview (binary classification)
  const collectAnalysisData = (type, data) => {
    setAnalysisData(prev => {
      const newData = { ...prev };
      
      if (type === 'confidence') {
        newData.confidenceData.push({
          voice_confidence: data.voice_confidence || false,
          hand_confidence: data.hand_confidence || false,
          eye_confidence: data.eye_confidence || false
        });
      } else if (type === 'stress') {
        newData.stressData.push({
          is_stressed: data.is_stressed || false
        });
      }
      
      return newData;
    });
  };

  // Initialize session start time when interview starts
  useEffect(() => {
    if (isInterviewActive && !analysisData.sessionStartTime) {
      setAnalysisData(prev => ({
        ...prev,
        sessionStartTime: Date.now()
      }));
    }
  }, [isInterviewActive, analysisData.sessionStartTime]);

  const startScreenRecording = async () => {
    try {
      console.log('🚀 Starting screen recording from session...');
      setRecordingStatus('starting');

      // Use the ScreenRecorder component's startRecording method
      if (screenRecorderRef.current) {
        console.log('📺 ScreenRecorder ref found, calling startRecording...');
        await screenRecorderRef.current.startRecording();
        setIsScreenRecording(true);
        setRecordingStatus('recording');
        console.log('✅ Screen recording started successfully!');
        // Notification will be shown by ScreenRecorder component
      } else {
        console.error('❌ ScreenRecorder ref not available');
        throw new Error('ScreenRecorder not available');
      }

    } catch (error) {
      console.error('Error starting screen recording:', error);
      setRecordingStatus('idle');
      if (error.name === 'NotAllowedError') {
        toast.error('Screen sharing permission denied');
      } else if (error.name === 'NotFoundError') {
        toast.error('No screen available for sharing');
      } else {
        toast.error('Failed to start screen recording');
      }
      throw error; // Re-throw to handle in startInterview
    }
  };

  const handleFrameCapture = (frameData) => {
    console.log('🚀 SENDING FRAME TO BACKEND:', {
      interviewId: sessionId,
      frameDataLength: frameData.length,
      socketConnected: socketService.getConnectionStatus(),
      timestamp: new Date().toISOString()
    });
    
    socketService.sendVideoFrame(sessionId, frameData);
  };

  const handleAudioCapture = (audioData) => {
    console.log('🎤 FRONTEND: Audio captured', {
      audioDataLength: audioData ? audioData.length : 0,
      sessionId,
      audioEnabled,
      isNull: audioData === null,
      firstFewSamples: audioData ? audioData.slice(0, 5) : null
    });
    
    // Send audio data or null signal to backend
    socketService.sendAudioData(sessionId, audioData);
  };

  const cleanupInterview = () => {
    console.log('🧹 Starting comprehensive interview cleanup...');
    
    // Stop screen recording immediately
    if (screenRecorderRef.current) {
      console.log('🛑 Stopping screen recorder via cleanup');
      screenRecorderRef.current.stopRecording();
    }
    setIsScreenRecording(false);
    setRecordingStatus('idle');
    
    // Send final stop signals to backend before disconnecting
    console.log('🛑 Sending final stop signals to backend');
    socketService.sendAudioData(sessionId, null); // Send audio stop signal
    socketService.sendVideoFrame(sessionId, null); // Send video stop signal
    
    // Wait a moment for signals to be processed
    setTimeout(() => {
      // Disconnect from socket to stop all real-time communication
      console.log('🔌 Disconnecting socket connection');
      socketService.leaveSession(sessionId);
      socketService.offLiveResults();
      socketService.offJoinedSession();
      socketService.disconnect(); // Fully disconnect to stop all communication
      
      // Reset all states
      setIsInterviewActive(false);
      setIsAnalysisActive(false);
      setAnalysisResults({
        face_stress: { stress_level: 'unknown', confidence: 0 },
        hand_confidence: { confidence_level: 'unknown', confidence: 0 },
        eye_confidence: { confidence_level: 'unknown', confidence: 0 },
        voice_confidence: { confidence_level: 'unknown', confidence: 0 },
        overall: { confidence_score: 0.5, stress_score: 0.5 }
      });
      
      console.log('✅ Interview cleanup completed');
    }, 500); // Wait 500ms for stop signals to be processed
  };


  // Helper functions to convert analysis to simple binary displays
  const getStressDisplay = (faceStress) => {
    // Show idle state before interview starts
    if (!isInterviewActive) {
      return { label: 'idle', color: '#9CA3AF', progress: 0 };
    }
    
    if (!faceStress || !faceStress.stress_level || faceStress.stress_level === 'no_data') {
      return { label: 'analyzing...', color: '#9CA3AF', progress: 0 };
    }
    
    const stressLevel = faceStress.stress_level.toLowerCase();
    // Handle backend converted values: 'stress' or 'non_stress'
    if (stressLevel === 'stress') {
      return { label: 'stress', color: '#F44336', progress: 75 };
    } else if (stressLevel === 'non_stress') {
      return { label: 'non stress', color: '#4CAF50', progress: 25 };
    }
    
    // Handle original complex values as fallback
    if (stressLevel.includes('stress') && !stressLevel.includes('not') && !stressLevel.includes('low') && !stressLevel.includes('non')) {
      return { label: 'stress', color: '#F44336', progress: 75 };
    }
    return { label: 'non stress', color: '#4CAF50', progress: 25 };
  };

  const getConfidenceDisplay = (confidenceData) => {
    // Show idle state before interview starts
    if (!isInterviewActive) {
      return { label: 'idle', color: '#9CA3AF', progress: 0 };
    }
    
    if (!confidenceData || !confidenceData.confidence_level || confidenceData.confidence_level === 'no_data') {
      return { label: 'analyzing...', color: '#9CA3AF', progress: 0 };
    }
    
    const confidenceLevel = confidenceData.confidence_level.toLowerCase();
    // Handle backend converted values: 'confident' or 'not_confident'
    if (confidenceLevel === 'confident') {
      return { label: 'confidence', color: '#4CAF50', progress: 75 };
    } else if (confidenceLevel === 'not_confident') {
      return { label: 'non confidence', color: '#F44336', progress: 25 };
    }
    
    // Handle original complex values as fallback
    if (confidenceLevel.includes('confident') && !confidenceLevel.includes('not')) {
      return { label: 'confidence', color: '#4CAF50', progress: 75 };
    }
    return { label: 'non confidence', color: '#F44336', progress: 25 };
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  const stressChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: {
            size: 12,
            weight: 500
          }
        }
      },
      title: {
        display: true,
        text: 'Face Stress Level',
        font: {
          size: 16,
          weight: 600
        },
        color: '#2D3748'
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.parsed.y;
            const state = value === 1 ? 'Stress' : 'Non Stress';
            return `${context.dataset.label}: ${state}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        min: 0,
        grid: {
          color: 'rgba(226, 232, 240, 0.5)',
          lineWidth: 1
        },
        ticks: {
          stepSize: 1,
          font: {
            size: 12,
            weight: 500
          },
          color: '#64748B',
          callback: function(value) {
            if (value === 1) return 'Stress';
            if (value === 0) return 'Non Stress';
            return '';
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(226, 232, 240, 0.3)',
          lineWidth: 1
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#64748B',
          maxTicksLimit: 8
        }
      }
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6
      },
      line: {
        borderWidth: 3
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  const confidenceChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
          font: {
            size: 12,
            weight: 500
          }
        }
      },
      title: {
        display: true,
        text: 'Confidence Levels',
        font: {
          size: 16,
          weight: 600
        },
        color: '#2D3748'
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const value = context.parsed.y;
            const state = value === 1 ? 'Confident' : 'Non Confident';
            return `${context.dataset.label}: ${state}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        min: 0,
        grid: {
          color: 'rgba(226, 232, 240, 0.5)',
          lineWidth: 1
        },
        ticks: {
          stepSize: 1,
          font: {
            size: 12,
            weight: 500
          },
          color: '#64748B',
          callback: function(value) {
            if (value === 1) return 'Confident';
            if (value === 0) return 'Non Confident';
            return '';
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(226, 232, 240, 0.3)',
          lineWidth: 1
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#64748B',
          maxTicksLimit: 8
        }
      }
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6
      },
      line: {
        borderWidth: 3
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      {/* Clean Header */}
      <Box sx={{ 
        mb: 4, 
        pb: 3, 
        borderBottom: '1px solid #E8F4FD',
        background: 'linear-gradient(135deg, #F8FCFF 0%, #E3F2FD 100%)',
        borderRadius: '16px',
        p: 3
      }}>
        <Typography 
          variant="h4" 
          sx={{ 
            mb: 1, 
            color: '#1A365D', 
            fontWeight: 600,
            letterSpacing: '-0.02em'
          }}
        >
          {interview?.candidate_name}
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: '#718096',
            fontSize: '1.1rem'
          }}
        >
          {interview?.position} • {interview?.platform}
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Main Recording Section - Expanded */}
        <Grid item xs={12} lg={9}>
          {/* Screen Recording Panel */}
          <Paper 
            elevation={0}
            sx={{ 
              p: 4, 
              borderRadius: '20px',
              border: isDarkMode 
                ? '1px solid #333333'
                : '1px solid #E2E8F0',
              backgroundColor: isDarkMode 
                ? '#1F1F1F'
                : '#FFFFFF',
              color: isDarkMode ? '#F1F5F9' : 'inherit',
              mb: 3
            }}
          >
            {/* Clean Header with Subtle Controls */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              mb: 3 
            }}>
              <Box>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    color: '#2D3748', 
                    fontWeight: 600,
                    fontSize: '1.3rem',
                    mb: 0.5
                  }}
                >
                  Live Interview Analysis
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#718096'
                  }}
                >
                  Real-time behavioral and vocal pattern analysis
                </Typography>
              </Box>
              
              {/* Minimal Toggle Controls */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton
                  onClick={() => setShowVideo(!showVideo)}
                  sx={{
                    width: 44,
                    height: 44,
                    backgroundColor: showVideo ? 'rgba(59, 130, 246, 0.1)' : 'rgba(148, 163, 184, 0.1)',
                    color: showVideo ? '#3B82F6' : '#64748B',
                    border: `1px solid ${showVideo ? 'rgba(59, 130, 246, 0.2)' : 'rgba(148, 163, 184, 0.2)'}`,
                    '&:hover': {
                      backgroundColor: showVideo ? 'rgba(59, 130, 246, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                    }
                  }}
                  title="Toggle video analysis"
                >
                  {showVideo ? <Visibility fontSize="small" /> : <VisibilityOff fontSize="small" />}
                </IconButton>
                <IconButton
                  onClick={() => setAudioEnabled(!audioEnabled)}
                  sx={{
                    width: 44,
                    height: 44,
                    backgroundColor: audioEnabled ? 'rgba(16, 185, 129, 0.1)' : 'rgba(148, 163, 184, 0.1)',
                    color: audioEnabled ? '#10B981' : '#64748B',
                    border: `1px solid ${audioEnabled ? 'rgba(16, 185, 129, 0.2)' : 'rgba(148, 163, 184, 0.2)'}`,
                    '&:hover': {
                      backgroundColor: audioEnabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                    }
                  }}
                  title="Toggle audio analysis"
                >
                  {audioEnabled ? <Mic fontSize="small" /> : <MicOff fontSize="small" />}
                </IconButton>
              </Box>
            </Box>

            {/* Screen Recorder Component */}
            <ScreenRecorder
              ref={screenRecorderRef}
              onFrameCapture={handleFrameCapture}
              onAudioCapture={handleAudioCapture}
              isActive={isInterviewActive}
              enableAudio={audioEnabled}
              enableVideo={showVideo}
              captureInterval={1000}
              hideStartButton={true}
            />

            {/* Clean Session Controls */}
            <Box sx={{ 
              mt: 4, 
              display: 'flex', 
              gap: 2, 
              justifyContent: 'center',
              pt: 3,
              borderTop: '1px solid #F1F5F9'
            }}>
              {!isInterviewActive ? (
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={startInterview}
                  sx={{
                    backgroundColor: '#10B981',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: 500,
                    textTransform: 'none',
                    boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                    '&:hover': {
                      backgroundColor: '#059669',
                      boxShadow: '0 6px 16px rgba(16, 185, 129, 0.4)',
                    }
                  }}
                >
                  Start Session
                </Button>
              ) : (
                <Button
                  variant="contained"
                  startIcon={<Stop />}
                  onClick={stopInterview}
                  sx={{
                    backgroundColor: '#EF4444',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    borderRadius: '12px',
                    fontSize: '1rem',
                    fontWeight: 500,
                    textTransform: 'none',
                    boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
                    '&:hover': {
                      backgroundColor: '#DC2626',
                      boxShadow: '0 6px 16px rgba(239, 68, 68, 0.4)',
                    }
                  }}
                >
                  End Session
                </Button>
              )}
              
              <Button
                variant="outlined"
                startIcon={<Analytics />}
                onClick={() => navigate(`/interview/${sessionId}/results`)}
                sx={{
                  color: '#64748B',
                  borderColor: '#E2E8F0',
                  px: 3,
                  py: 1.5,
                  borderRadius: '12px',
                  fontSize: '1rem',
                  fontWeight: 500,
                  textTransform: 'none',
                  '&:hover': {
                    borderColor: '#CBD5E1',
                    backgroundColor: 'rgba(148, 163, 184, 0.05)',
                  }
                }}
              >
                View Results
              </Button>
            </Box>
          </Paper>

          {/* Enhanced Chart Panel */}
          <Paper 
            elevation={0}
            sx={{ 
              p: 4, 
              borderRadius: '20px',
              border: isDarkMode 
                ? '1px solid #333333'
                : '1px solid #E2E8F0',
              backgroundColor: isDarkMode 
                ? '#1F1F1F'
                : '#FFFFFF',
              color: isDarkMode ? '#F1F5F9' : 'inherit',
              boxShadow: isDarkMode 
                ? '0 4px 20px rgba(0, 0, 0, 0.3)'
                : '0 4px 20px rgba(0, 0, 0, 0.08)'
            }}
          >
            <Box sx={{ mb: 4 }}>
              <Typography 
                variant="h5" 
                sx={{ 
                  color: '#1A365D', 
                  fontWeight: 700,
                  fontSize: '1.5rem',
                  mb: 1,
                  letterSpacing: '-0.02em'
                }}
              >
                Performance Trends
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  color: '#718096',
                  fontSize: '1.1rem'
                }}
              >
                Real-time stress and confidence level monitoring
              </Typography>
            </Box>
            
            {/* Enhanced Two Charts Layout */}
            <Grid container spacing={4}>
              {/* Stress Level Chart */}
              <Grid item xs={12} lg={6}>
                <Box sx={(theme) => ({ 
                  height: 400,
                  p: 3,
                  border: theme.palette.mode === 'dark' 
                    ? '2px solid #333333' 
                    : '2px solid #FED7D7',
                  borderRadius: '16px',
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, #1F1F1F 0%, #1F1F1F 100%)'
                    : 'linear-gradient(135deg, #FEF7F7 0%, #FDF2F8 100%)',
                  backgroundColor: theme.palette.background.paper,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 25px rgba(0, 0, 0, 0.3)'
                    : '0 8px 25px rgba(239, 68, 68, 0.1)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 12px 35px rgba(0, 0, 0, 0.4)'
                      : '0 12px 35px rgba(239, 68, 68, 0.15)'
                  }
                })}>
                  <Line data={stressChartData} options={stressChartOptions} />
                </Box>
              </Grid>
              
              {/* Confidence Level Chart */}
              <Grid item xs={12} lg={6}>
                <Box sx={(theme) => ({ 
                  height: 400,
                  p: 3,
                  border: theme.palette.mode === 'dark' 
                    ? '2px solid #333333' 
                    : '2px solid #BFDBFE',
                  borderRadius: '16px',
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(135deg, #1F1F1F 0%, #1F1F1F 100%)'
                    : 'linear-gradient(135deg, #F0F9FF 0%, #EBF8FF 100%)',
                  backgroundColor: theme.palette.background.paper,
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 25px rgba(0, 0, 0, 0.3)'
                    : '0 8px 25px rgba(59, 130, 246, 0.1)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 12px 35px rgba(0, 0, 0, 0.4)'
                      : '0 12px 35px rgba(59, 130, 246, 0.15)'
                  }
                })}>
                  <Line data={confidenceChartData} options={confidenceChartOptions} />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Clean Analysis Results Sidebar - Compressed */}
        <Grid item xs={12} lg={3}>
          <Paper 
            elevation={0}
            sx={{ 
              p: 3, 
              borderRadius: '20px',
              border: isDarkMode 
                ? '1px solid #333333'
                : '1px solid #E2E8F0',
              backgroundColor: isDarkMode 
                ? '#1F1F1F'
                : '#FFFFFF',
              color: isDarkMode ? '#F1F5F9' : 'inherit',
              height: 'fit-content'
            }}
          >
            <Box sx={{ mb: 4 }}>
              <Typography 
                variant="h6" 
                sx={{ 
                  color: isDarkMode ? '#F1F5F9' : '#2D3748', 
                  fontWeight: 600,
                  fontSize: '1.3rem',
                  mb: 0.5
                }}
              >
                Live Analysis
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: isDarkMode ? '#94A3B8' : '#718096'
                }}
              >
                Real-time behavioral insights
              </Typography>

              {/* Analysis Status Indicator */}
              <Box sx={{ 
                mt: 1, 
                mb: 2, 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1 
              }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: isAnalysisActive ? '#4CAF50' : '#FF9800',
                  animation: isAnalysisActive ? 'pulse 2s infinite' : 'none'
                }} />
                <Typography variant="body2" sx={{ 
                  color: isAnalysisActive ? '#4CAF50' : '#FF9800',
                  fontWeight: 500
                }}>
                  {isAnalysisActive ? 'Analysis Active' : 'Analysis Inactive'}
                </Typography>
              </Box>
              
              {/* Real-time Analysis Status */}
              <Box sx={{ 
                mt: 2, 
                p: 2, 
                borderRadius: '12px',
                backgroundColor: isDarkMode ? '#1F1F1F' : '#F7FAFC',
                border: isDarkMode ? '1px solid #333333' : '1px solid #E2E8F0'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ color: isDarkMode ? '#E2E8F0' : '#4A5568', fontWeight: 500 }}>
                    Analysis Updates
                  </Typography>
                  <Box sx={{ 
                    width: 8, 
                    height: 8, 
                    borderRadius: '50%',
                    backgroundColor: realtimeAnalysis.lastUpdate ? '#48BB78' : '#CBD5E0',
                    animation: realtimeAnalysis.lastUpdate ? 'pulse 2s infinite' : 'none'
                  }} />
                </Box>
                <Typography variant="caption" sx={{ color: isDarkMode ? '#94A3B8' : '#718096' }}>
                  {realtimeAnalysis.lastUpdate 
                    ? `Last update: ${realtimeAnalysis.lastUpdate.toLocaleTimeString()} (${realtimeAnalysis.updateCount} updates)`
                    : 'Waiting for analysis...'
                  }
                </Typography>
                <Typography variant="caption" sx={{ color: isDarkMode ? '#94A3B8' : '#718096', display: 'block', mt: 0.5 }}>
                  Updates every 10 seconds
                </Typography>
              </Box>
            </Box>

            {/* Clean Analysis Cards - Vertical Layout */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              
              {/* Face Stress Analysis */}
              <Box sx={{ 
                p: 3, 
                borderRadius: '16px',
                backgroundColor: isDarkMode ? '#1F1F1F' : '#FEF7F7',
                border: isDarkMode ? '1px solid #333333' : '1px solid #FED7D7'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '12px',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <Face sx={{ color: '#EF4444', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: isDarkMode ? '#FFFFFF' : '#1A202C' }}>
                      Stress Level
                    </Typography>
                    <Typography variant="caption" sx={{ color: isDarkMode ? '#E2E8F0' : '#718096' }}>
                      Facial expression analysis
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={getStressDisplay(analysisResults.face_stress).label}
                    sx={{
                      backgroundColor: getStressDisplay(analysisResults.face_stress).color,
                      color: 'white',
                      fontWeight: 500,
                      borderRadius: '8px',
                      fontSize: { xs: '0.75rem', sm: '0.8rem' }
                    }}
                    size="small"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getStressDisplay(analysisResults.face_stress).progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getStressDisplay(analysisResults.face_stress).color,
                      borderRadius: 3
                    }
                  }}
                />
              </Box>

              {/* Hand Confidence Analysis */}
              <Box sx={{ 
                p: 3, 
                borderRadius: '16px',
                backgroundColor: isDarkMode ? '#1F1F1F' : '#F0F9FF',
                border: isDarkMode ? '1px solid #333333' : '1px solid #BFDBFE'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '12px',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <PanTool sx={{ color: '#3B82F6', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: isDarkMode ? '#FFFFFF' : '#1A202C' }}>
                      Gesture Confidence
                    </Typography>
                    <Typography variant="caption" sx={{ color: isDarkMode ? '#E2E8F0' : '#718096' }}>
                      Hand movement patterns
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={getConfidenceDisplay(analysisResults.hand_confidence).label}
                    sx={{
                      backgroundColor: getConfidenceDisplay(analysisResults.hand_confidence).color,
                      color: 'white',
                      fontWeight: 500,
                      borderRadius: '8px',
                      fontSize: { xs: '0.75rem', sm: '0.8rem' }
                    }}
                    size="small"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getConfidenceDisplay(analysisResults.hand_confidence).progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getConfidenceDisplay(analysisResults.hand_confidence).color,
                      borderRadius: 3
                    }
                  }}
                />
              </Box>

              {/* Eye Confidence Analysis */}
              <Box sx={{ 
                p: 3, 
                borderRadius: '16px',
                backgroundColor: isDarkMode ? '#1F1F1F' : '#F0FDF4',
                border: isDarkMode ? '1px solid #333333' : '1px solid #BBF7D0'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '12px',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <RemoveRedEye sx={{ color: '#10B981', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: isDarkMode ? '#FFFFFF' : '#1A202C' }}>
                      Eye Contact
                    </Typography>
                    <Typography variant="caption" sx={{ color: isDarkMode ? '#E2E8F0' : '#718096' }}>
                      Gaze direction analysis
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={getConfidenceDisplay(analysisResults.eye_confidence).label}
                    sx={{
                      backgroundColor: getConfidenceDisplay(analysisResults.eye_confidence).color,
                      color: 'white',
                      fontWeight: 500,
                      borderRadius: '8px',
                      fontSize: { xs: '0.75rem', sm: '0.8rem' }
                    }}
                    size="small"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getConfidenceDisplay(analysisResults.eye_confidence).progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getConfidenceDisplay(analysisResults.eye_confidence).color,
                      borderRadius: 3
                    }
                  }}
                />
              </Box>

              {/* Voice Confidence Analysis */}
              <Box sx={{ 
                p: 3, 
                borderRadius: '16px',
                backgroundColor: isDarkMode ? '#1F1F1F' : '#FAF5FF',
                border: isDarkMode ? '1px solid #333333' : '1px solid #E9D5FF'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '12px',
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}>
                    <RecordVoiceOver sx={{ color: '#9333EA', fontSize: 20 }} />
                  </Box>
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: isDarkMode ? '#FFFFFF' : '#1A202C' }}>
                      Voice Confidence
                    </Typography>
                    <Typography variant="caption" sx={{ color: isDarkMode ? '#E2E8F0' : '#718096' }}>
                      Speech pattern analysis
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={getConfidenceDisplay(analysisResults.voice_confidence).label}
                    sx={{
                      backgroundColor: getConfidenceDisplay(analysisResults.voice_confidence).color,
                      color: 'white',
                      fontWeight: 500,
                      borderRadius: '8px',
                      fontSize: { xs: '0.75rem', sm: '0.8rem' }
                    }}
                    size="small"
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={getConfidenceDisplay(analysisResults.voice_confidence).progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getConfidenceDisplay(analysisResults.voice_confidence).color,
                      borderRadius: 3
                    }
                  }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* End Session Confirmation Dialog */}
      <Dialog
        open={showEndSessionDialog}
        onClose={cancelEndSession}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ 
          textAlign: 'center', 
          fontSize: '1.5rem', 
          fontWeight: 600,
          color: '#1e293b',
          pb: 1
        }}>
          End Interview Session
        </DialogTitle>
        <DialogContent sx={{ textAlign: 'center', py: 2 }}>
          <Typography variant="body1" sx={{ mb: 2, color: '#64748b' }}>
            Are you sure you want to end this interview session?
          </Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8' }}>
            This action cannot be undone. The interview analysis will be completed and you'll be redirected to the dashboard.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', pb: 3, px: 3 }}>
          <Button
            onClick={cancelEndSession}
            variant="outlined"
            sx={{
              mr: 2,
              px: 3,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              borderColor: '#d1d5db',
              color: '#6b7280',
              '&:hover': {
                borderColor: '#9ca3af',
                backgroundColor: '#f9fafb'
              }
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={confirmEndSession}
            variant="contained"
            sx={{
              px: 3,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              backgroundColor: '#ef4444',
              '&:hover': {
                backgroundColor: '#dc2626'
              }
            }}
          >
            Yes, End Session
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default InterviewSession;
