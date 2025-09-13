import React, { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  ScreenShare,
  StopScreenShare,
  Monitor,
  Mic,
  MicOff,
  Videocam,
  Fullscreen,
  FullscreenExit,
  Refresh
} from '@mui/icons-material';
import { toast } from 'react-toastify';

// Add CSS animations
const styles = `
  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
  
  @keyframes glow {
    0% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.5); }
    50% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.8); }
    100% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.5); }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
    to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  }
  
  .recording-border {
    animation: glow 2s ease-in-out infinite;
  }
  
  .pulse-dot {
    animation: pulse 2s infinite;
  }
  
  .video-overlay {
    backdrop-filter: blur(10px);
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.type = 'text/css';
  styleSheet.innerText = styles;
  if (!document.head.querySelector('[data-screen-recorder-styles]')) {
    styleSheet.setAttribute('data-screen-recorder-styles', 'true');
    document.head.appendChild(styleSheet);
  }
}

const ScreenRecorder = forwardRef(({ 
  onFrameCapture, 
  onAudioCapture, 
  isActive = false,
  enableAudio = true,
  enableVideo = true,
  captureInterval = 10000, // Capture frame every 10 seconds to match analysis interval
  hideStartButton = false 
}, ref) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const audioContextRef = useRef(null);
  const intervalRef = useRef(null);
  const audioTimeoutRef = useRef(null);
  const isRecordingRef = useRef(false);

  const [isRecording, setIsRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('stopped');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [streamInfo, setStreamInfo] = useState({
    hasVideo: false,
    hasAudio: false,
    resolution: null
  });

  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  useEffect(() => {
    if (!isActive && isRecording) {
      stopRecording();
    }
  }, [isActive, isRecording]);

  const startRecording = async () => {
    try {
      console.log('🚀 START RECORDING BUTTON CLICKED!');
      setRecordingStatus('starting');

      // Request screen capture with specified options
      const screenConstraints = {
        video: {
          mediaSource: 'screen',
          width: { ideal: 1280, max: 1920 },
          height: { ideal: 720, max: 1080 },
          frameRate: { ideal: 15, max: 30 },
          cursor: 'always',
          displaySurface: 'monitor'
        }
      };

      // Add system audio constraints if enabled
      if (enableAudio) {
        screenConstraints.audio = {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        };
      }

      console.log('📺 Requesting screen share with constraints:', screenConstraints);
      const screenStream = await navigator.mediaDevices.getDisplayMedia(screenConstraints);
      console.log('✅ Screen share granted! Stream:', screenStream);

      // NOTE: We'll use SYSTEM AUDIO from screen recording for voice analysis
      console.log('🔊 Using system audio from screen recording for voice analysis...');
      // No need for separate microphone stream - we'll use the system audio from screen capture

      // Use screen stream as primary stream for display
      streamRef.current = screenStream;
      
      // No separate microphone stream - using system audio from screen recording

      // Get stream information
      const videoTrack = screenStream.getVideoTracks()[0];
      const systemAudioTrack = screenStream.getAudioTracks()[0];
      
      const settings = videoTrack.getSettings();
      setStreamInfo({
        hasVideo: !!videoTrack,
        hasAudio: !!systemAudioTrack,
        resolution: settings.width && settings.height ? `${settings.width}x${settings.height}` : null
      });

      console.log('🎬 Stream info:', {
        hasVideo: !!videoTrack,
        hasSystemAudio: !!systemAudioTrack,
        systemAudioSettings: systemAudioTrack?.getSettings()
      });

      // Display the stream in video element
      if (videoRef.current) {
        console.log('🎥 Setting video stream:', {
          streamActive: screenStream.active,
          videoTracks: screenStream.getVideoTracks().length,
          audioTracks: screenStream.getAudioTracks().length
        });
        
        videoRef.current.srcObject = screenStream;
        
        // Force video element to refresh and play
        setTimeout(() => {
          if (videoRef.current) {
            console.log('🔄 Force refreshing video element...');
            videoRef.current.load();
            videoRef.current.play().then(() => {
              console.log('✅ Video force play successful');
            }).catch(e => {
              console.log('⚠️ Video force play failed, but stream should still work for capture:', e);
            });
          }
        }, 100);
        
        // Set video properties
        videoRef.current.muted = true;
        videoRef.current.autoplay = true;
        videoRef.current.playsInline = true;
        
        // Set video as loaded immediately since we have the stream
        setVideoLoaded(true);
        
        // Add event listeners for debugging
        videoRef.current.onloadedmetadata = () => {
          console.log('✅ Video metadata loaded:', {
            videoWidth: videoRef.current.videoWidth,
            videoHeight: videoRef.current.videoHeight,
            duration: videoRef.current.duration,
            readyState: videoRef.current.readyState,
            srcObject: !!videoRef.current.srcObject
          });
          setVideoLoaded(true);
        };
        
        videoRef.current.onloadeddata = () => {
          console.log('Video data loaded');
          setVideoLoaded(true);
        };
        
        videoRef.current.onerror = (e) => {
          console.error('Video error:', e);
          console.log('Trying canvas fallback due to video error');
          startCanvasDisplay();
        };
        
        videoRef.current.onplay = () => {
          console.log('Video playing');
          setVideoLoaded(true);
        };
        
        videoRef.current.oncanplay = () => {
          console.log('Video can play');
          setVideoLoaded(true);
        };
        
        // Force play with better error handling
        const playVideo = async () => {
          try {
            console.log('🎬 Attempting to play video...');
            await videoRef.current.play();
            console.log('✅ Video play successful');
            setVideoLoaded(true);
          } catch (error) {
            console.error('❌ Video play failed:', error);
            console.log('🔄 Trying alternative approach...');
            // Try alternative approach
            setTimeout(() => {
              if (videoRef.current && streamRef.current) {
                console.log('🔄 Reloading video element...');
                videoRef.current.load();
                videoRef.current.play().catch(e => {
                  console.error('❌ Second play attempt failed:', e);
                  console.log('🎨 Falling back to canvas display...');
                  startCanvasDisplay();
                });
              }
            }, 500);
          }
        };
        
        playVideo();
        
        // Note: Canvas fallback will only be triggered by video error events now
      }

      // Start frame capture for video analysis
      if (enableVideo && onFrameCapture) {
        console.log('🎬 Starting frame capture interval...');
        intervalRef.current = setInterval(() => {
          captureFrame();
        }, captureInterval);
      }

      // Set recording state to true (needed for frame capture)
      setIsRecording(true);
      isRecordingRef.current = true;

      // Start audio analysis with SYSTEM AUDIO from screen recording
      if (enableAudio && systemAudioTrack && onAudioCapture) {
        console.log('🔊 Starting audio analysis with system audio from screen recording...');
        setupAudioAnalysis(screenStream);
      } else if (enableAudio && !systemAudioTrack) {
        console.warn('⚠️ No system audio available for voice analysis');
        toast.warning('No system audio captured - enable audio sharing when prompted');
      }

      // Handle stream end
      videoTrack.addEventListener('ended', () => {
        stopRecording();
        toast.info('Screen sharing ended');
      });

      setRecordingStatus('recording');
      console.log('✅ Recording started successfully! isRecording set to true');
      console.log('🔊 Voice analysis status:', {
        systemAudioAvailable: !!systemAudioTrack,
        audioEnabled: enableAudio,
        onAudioCapture: !!onAudioCapture
      });
      toast.success('Screen recording started successfully!');

    } catch (error) {
      console.error('Error starting screen recording:', error);
      setRecordingStatus('stopped');
      handleRecordingError(error);
    }
  };

  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    
    // Immediately stop recording state to prevent new frame captures
    setIsRecording(false);
    isRecordingRef.current = false;
    
    // Notify backend that audio has stopped
    if (onAudioCapture) {
      console.log('🎤 Sending audio stop signal to backend');
      onAudioCapture(null); // Send null to indicate audio stopped
    }
    
    // Stop frame capture immediately
    if (intervalRef.current) {
      console.log('🛑 Stopping frame capture interval');
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    // Stop screen stream tracks (includes system audio)
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        console.log('🛑 Stopping screen track:', track.kind);
        track.stop();
      });
      streamRef.current = null;
    }

    // Clear video element
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    // Stop audio analysis
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    // Clear audio analysis timeout
    if (audioTimeoutRef.current) {
      console.log('🛑 Clearing audio analysis timeout');
      clearTimeout(audioTimeoutRef.current);
      audioTimeoutRef.current = null;
    }

    setRecordingStatus('stopped');
    setIsFullscreen(false);
    setVideoLoaded(false);
    setStreamInfo({
      hasVideo: false,
      hasAudio: false,
      resolution: null
    });
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const refreshVideoStream = () => {
    if (videoRef.current && streamRef.current) {
      console.log('🔄 Refreshing video stream...');
      
      // Reset video loaded state
      setVideoLoaded(false);
      
      // Re-assign the stream to the video element
      videoRef.current.srcObject = null;
      
      setTimeout(() => {
        if (videoRef.current && streamRef.current) {
          console.log('🎥 Re-assigning stream to video element...');
          videoRef.current.srcObject = streamRef.current;
          videoRef.current.muted = true;
          videoRef.current.autoplay = true;
          videoRef.current.playsInline = true;
          
          // Force load and play
          videoRef.current.load();
          videoRef.current.play().then(() => {
            console.log('✅ Video refresh successful - video should now be visible');
            setVideoLoaded(true);
            toast.success('Video display refreshed successfully!');
          }).catch(e => {
            console.error('❌ Error replaying video after refresh:', e);
            console.log('🎨 Trying canvas fallback...');
            startCanvasDisplay();
          });
        }
      }, 200);
    } else {
      console.warn('⚠️ Cannot refresh - video ref or stream ref not available');
      toast.warning('Cannot refresh video - please restart screen recording');
    }
  };

  const startCanvasDisplay = () => {
    if (!canvasRef.current || !streamRef.current) return;
    
    console.log('Starting canvas fallback display');
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Create a video element for canvas rendering
    const hiddenVideo = document.createElement('video');
    hiddenVideo.srcObject = streamRef.current;
    hiddenVideo.muted = true;
    hiddenVideo.autoplay = true;
    hiddenVideo.playsInline = true;
    
    hiddenVideo.onloadedmetadata = () => {
      canvas.width = hiddenVideo.videoWidth || 1920;
      canvas.height = hiddenVideo.videoHeight || 1080;
      canvas.style.display = 'block';
      canvas.style.width = '100%';
      canvas.style.height = 'auto';
      canvas.style.maxHeight = '600px';
      canvas.style.objectFit = 'contain';
      canvas.style.backgroundColor = '#000';
      
      setVideoLoaded(true);
      
      const drawFrame = () => {
        if (isRecordingRef.current && hiddenVideo.readyState >= 2) {
          ctx.drawImage(hiddenVideo, 0, 0, canvas.width, canvas.height);
        }
        if (isRecordingRef.current) {
          requestAnimationFrame(drawFrame);
        }
      };
      
      hiddenVideo.play().then(() => {
        drawFrame();
      });
    };
  };

  const captureFrame = () => {
    // Check if recording is active - let the parent manage session state
    if (videoRef.current && canvasRef.current && isRecordingRef.current && onFrameCapture) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      console.log('🎥 FRAME CAPTURE DEBUG:', {
        isRecording: isRecordingRef.current,
        isActive: isActive,
        hasVideo: !!video,
        hasCanvas: !!canvas,
        videoWidth: video.videoWidth,
        videoHeight: video.videoHeight,
        videoReadyState: video.readyState,
        onFrameCapture: !!onFrameCapture
      });

      // Set canvas size to match video
      canvas.width = video.videoWidth || 1920;
      canvas.height = video.videoHeight || 1080;

      // Draw current frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert to base64 and send for analysis
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      console.log('📸 Frame captured and sending to backend:', {
        dataLength: imageData.length,
        timestamp: new Date().toISOString()
      });
      
      onFrameCapture(imageData);
    } else {
      console.log('❌ Frame capture skipped:', {
        hasVideoRef: !!videoRef.current,
        hasCanvasRef: !!canvasRef.current,
        isRecording: isRecordingRef.current,
        hasOnFrameCapture: !!onFrameCapture
      });
    }
  };

  const setupAudioAnalysis = (stream) => {
    try {
      console.log('🎵 Setting up audio analysis with stream:', stream);
      console.log('🎵 Stream tracks:', stream.getTracks());
      console.log('🎵 Audio tracks:', stream.getAudioTracks());
      
      if (stream.getAudioTracks().length === 0) {
        console.error('❌ No audio tracks found in stream!');
        toast.error('No audio tracks available for analysis');
        return;
      }
      
      audioContextRef.current = new AudioContext();
      console.log('🎵 AudioContext created:', audioContextRef.current.state);
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      
      source.connect(analyser);
      analyser.fftSize = 256;
      
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      console.log('🎵 Audio analyser setup complete, buffer length:', bufferLength);

      const analyzeAudio = () => {
        if (isRecordingRef.current && audioContextRef.current && onAudioCapture) {
          analyser.getByteFrequencyData(dataArray);
          const audioData = Array.from(dataArray);
          console.log('🎵 Audio data captured, length:', audioData.length, 'first 5 values:', audioData.slice(0, 5));
          onAudioCapture(audioData);
          audioTimeoutRef.current = setTimeout(analyzeAudio, 10000); // Analyze every 10 seconds to match analysis interval
        } else {
          console.log('🎵 Audio analysis stopped - recording:', isRecordingRef.current, 'context:', !!audioContextRef.current, 'callback:', !!onAudioCapture);
        }
      };

      console.log('🎵 Starting audio analysis loop...');
      analyzeAudio();
    } catch (error) {
      console.error('❌ Error setting up audio analysis:', error);
      toast.error(`Audio analysis setup failed: ${error.message}`);
    }
  };

  const handleRecordingError = (error) => {
    switch (error.name) {
      case 'NotAllowedError':
        toast.error('Screen sharing permission denied. Please allow screen access.');
        break;
      case 'NotSupportedError':
        toast.error('Screen sharing not supported. Please use Chrome, Firefox, or Edge.');
        break;
      case 'AbortError':
        toast.info('Screen sharing was cancelled.');
        break;
      default:
        toast.error(`Failed to start screen recording: ${error.message}`);
    }
  };

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    startRecording,
    stopRecording,
    setStream: (stream) => {
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    }
  }));

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        {/* Recording Display */}
        <Box sx={{ position: 'relative', borderRadius: 2, overflow: 'hidden', mb: 2 }}>
          {isRecording ? (
            <>
              <Box
                sx={{
                  position: 'relative',
                  border: '3px solid #4CAF50',
                  borderRadius: 2,
                  overflow: 'hidden',
                  boxShadow: '0 4px 20px rgba(76, 175, 80, 0.3)',
                  ...(isFullscreen && {
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    zIndex: 9999,
                    borderRadius: 0
                    // Removed bgcolor: '#000' to prevent double black layers
                  })
                }}
                className="recording-border"
              >
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  controls={false}
                  style={{
                    width: '100%',
                    height: isFullscreen ? '100vh' : 'auto',
                    minHeight: isFullscreen ? '100vh' : '400px',
                    maxHeight: isFullscreen ? '100vh' : '600px',
                    objectFit: 'contain',
                    display: 'block'
                  }}
                  onPlay={() => console.log('🎥 Video started playing')}
                  onError={(e) => console.error('❌ Video element error:', e)}
                  onCanPlay={() => {
                    console.log('✅ Video can play');
                    setVideoLoaded(true);
                  }}
                />

                {/* Video Loading Overlay - Only show when starting, not during recording */}
                {recordingStatus === 'starting' && !videoLoaded && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(0, 0, 0, 0.8)',
                      color: 'white',
                      zIndex: 5
                    }}
                  >
                    <CircularProgress sx={{ mb: 2, color: '#4CAF50' }} />
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      Loading Screen Preview...
                    </Typography>
                    <Typography variant="body2" sx={{ textAlign: 'center', maxWidth: 300 }}>
                      Please wait while we initialize the screen capture display
                    </Typography>
                  </Box>
                )}

                {/* Video Error Overlay - Only show if stream is actually missing */}
                {isRecording && recordingStatus === 'recording' && !streamRef.current && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(0, 0, 0, 0.9)',
                      color: 'white',
                      zIndex: 5
                    }}
                  >
                    <Typography variant="h6" sx={{ mb: 2, color: '#FF9800' }}>
                      📺 Video Preview Loading...
                    </Typography>
                    <Typography variant="body2" sx={{ textAlign: 'center', maxWidth: 400, mb: 2 }}>
                      Screen recording is active! If the preview doesn't appear:
                    </Typography>
                    <Typography variant="body2" sx={{ textAlign: 'center', maxWidth: 400, mb: 2 }}>
                      • Try clicking "Refresh Video" below<br/>
                      • Some browsers need a moment to display screen content<br/>
                      • Check if you selected the correct screen/window
                    </Typography>
                    <Typography variant="body2" sx={{ textAlign: 'center', maxWidth: 400, color: '#4CAF50' }}>
                      <strong>✅ AI analysis is working regardless of preview status</strong>
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={refreshVideoStream}
                      sx={{ mt: 2, bgcolor: '#FF9800' }}
                    >
                      Refresh Video Display
                    </Button>
                  </Box>
                )}
                
                {/* Live Preview Label */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 12,
                    left: 12,
                    bgcolor: 'rgba(255, 255, 255, 0.95)',
                    color: '#666',
                    px: 1.5,
                    py: 0.5,
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    border: '1px solid rgba(0,0,0,0.1)',
                    backdropFilter: 'blur(8px)',
                    zIndex: 10
                  }}
                >
                  Live Preview
                </Box>

                {/* Fullscreen Toggle */}
                                {/* Fullscreen Toggle */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 12,
                    right: 100,
                    bgcolor: 'rgba(255, 255, 255, 0.95)',
                    color: '#666',
                    width: 32,
                    height: 32,
                    borderRadius: '16px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    border: '1px solid rgba(0,0,0,0.1)',
                    backdropFilter: 'blur(8px)',
                    zIndex: 10,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      bgcolor: 'rgba(245, 245, 245, 0.95)',
                      transform: 'scale(1.05)'
                    }
                  }}
                  onClick={toggleFullscreen}
                >
                  {isFullscreen ? <FullscreenExit sx={{ fontSize: '16px' }} /> : <Fullscreen sx={{ fontSize: '16px' }} />}
                </Box>

                {/* Recording Indicator */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 12,
                    right: 12,
                    bgcolor: 'rgba(255, 255, 255, 0.95)',
                    color: '#d32f2f',
                    px: 1.5,
                    py: 0.5,
                    borderRadius: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5,
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    border: '1px solid rgba(211, 47, 47, 0.2)',
                    backdropFilter: 'blur(8px)',
                    zIndex: 10
                  }}
                >
                  <Box
                    sx={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      bgcolor: '#d32f2f'
                    }}
                    className="pulse-dot"
                  />
                  REC
                </Box>

                {/* Stream Info */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 12,
                    left: 12,
                    display: 'flex',
                    gap: 0.5,
                    zIndex: 10
                  }}
                >
                  {streamInfo.hasVideo && (
                    <Box 
                      sx={{ 
                        bgcolor: 'rgba(255, 255, 255, 0.95)', 
                        color: '#666',
                        px: 1,
                        py: 0.25,
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: 500,
                        border: '1px solid rgba(0,0,0,0.1)',
                        backdropFilter: 'blur(8px)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5
                      }}
                    >
                      <Videocam sx={{ fontSize: '12px' }} />
                      {streamInfo.resolution || 'Video'}
                    </Box>
                  )}
                  {streamInfo.hasAudio && (
                    <Box 
                      sx={{ 
                        bgcolor: 'rgba(255, 255, 255, 0.95)', 
                        color: '#666',
                        px: 1,
                        py: 0.25,
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: 500,
                        border: '1px solid rgba(0,0,0,0.1)',
                        backdropFilter: 'blur(8px)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5
                      }}
                    >
                      <Mic sx={{ fontSize: '12px' }} />
                      Audio
                    </Box>
                  )}
                  {!streamInfo.hasAudio && (
                    <Box 
                      sx={{ 
                        bgcolor: 'rgba(255, 255, 255, 0.95)', 
                        color: '#999',
                        px: 1,
                        py: 0.25,
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: 500,
                        border: '1px solid rgba(0,0,0,0.1)',
                        backdropFilter: 'blur(8px)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5
                      }}
                    >
                      <MicOff sx={{ fontSize: '12px' }} />
                      No Audio
                    </Box>
                  )}
                </Box>

                {/* AI Analysis Indicator */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 12,
                    right: 12,
                    bgcolor: 'rgba(255, 255, 255, 0.95)',
                    color: '#666',
                    px: 1.5,
                    py: 0.5,
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    border: '1px solid rgba(0,0,0,0.1)',
                    backdropFilter: 'blur(8px)',
                    zIndex: 10,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.5
                  }}
                >
                  <Box 
                    sx={{ 
                      width: 6, 
                      height: 6, 
                      borderRadius: '50%', 
                      bgcolor: '#4caf50',
                      animation: 'pulse 2s infinite'
                    }} 
                  />
                  AI Analyzing
                </Box>

                {/* Refresh Video Button - Only show when recording but video is not displaying properly */}
                {isRecording && !isFullscreen && !videoLoaded && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      zIndex: 8
                    }}
                  >
                    <Button
                      variant="contained"
                      startIcon={<Refresh />}
                      onClick={refreshVideoStream}
                      sx={{
                        bgcolor: 'rgba(33, 150, 243, 0.9)',
                        color: 'white',
                        backdropFilter: 'blur(8px)',
                        '&:hover': {
                          bgcolor: 'rgba(33, 150, 243, 1)',
                        }
                      }}
                    >
                      Refresh Video Display
                    </Button>
                  </Box>
                )}

                {/* Fullscreen Instructions */}
                {isFullscreen && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      bgcolor: 'rgba(0, 0, 0, 0.7)',
                      color: 'white',
                      p: 3,
                      borderRadius: 2,
                      textAlign: 'center',
                      zIndex: 10,
                      opacity: 0,
                      animation: 'fadeIn 0.5s ease-in-out forwards'
                    }}
                  >
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      Fullscreen Mode
                    </Typography>
                    <Typography variant="body2">
                      Click the fullscreen icon to exit
                    </Typography>
                  </Box>
                )}
              </Box>
              
              <canvas
                ref={canvasRef}
                style={{ 
                  display: 'none', // Hide canvas by default, only show when explicitly needed
                  width: '100%',
                  height: 'auto',
                  maxHeight: '600px',
                  objectFit: 'contain',
                  backgroundColor: '#000'
                }}
              />
            </>
          ) : (
            <Box
              sx={{
                height: 300,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: '#F5F5F5',
                borderRadius: 2,
                border: '2px dashed #BDBDBD'
              }}
            >
              <Monitor sx={{ fontSize: 80, color: '#BDBDBD', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" sx={{ mb: 1 }}>
                Screen Recording Ready
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center', maxWidth: 400 }}>
                Click the button below to start capturing the interview screen for AI analysis
              </Typography>
            </Box>
          )}
        </Box>

        {/* Controls */}
        {!isFullscreen && !hideStartButton && (
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            {!isRecording ? (
              <Button
                variant="contained"
                startIcon={recordingStatus === 'starting' ? <CircularProgress size={20} /> : <ScreenShare />}
                onClick={startRecording}
                disabled={recordingStatus === 'starting'}
                sx={{
                  backgroundColor: '#4FC3F7',
                  '&:hover': {
                    backgroundColor: '#29B6F6',
                  },
                  minWidth: 200,
                  fontSize: '1rem',
                  py: 1.5
                }}
              >
                {recordingStatus === 'starting' ? 'Starting...' : 'Start Screen Recording'}
              </Button>
            ) : (
              <>
                <Button
                  variant="contained"
                  startIcon={<StopScreenShare />}
                  onClick={stopRecording}
                  sx={{
                    backgroundColor: '#FF9800',
                    '&:hover': {
                      backgroundColor: '#F57C00',
                    },
                    minWidth: 180,
                    fontSize: '1rem',
                    py: 1.5
                  }}
                >
                  Stop Recording
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                  onClick={toggleFullscreen}
                  sx={{
                    borderColor: '#4CAF50',
                    color: '#4CAF50',
                    minWidth: 140,
                    '&:hover': {
                      borderColor: '#45A049',
                      bgcolor: 'rgba(76, 175, 80, 0.1)'
                    }
                  }}
                >
                  {isFullscreen ? 'Exit Full' : 'Fullscreen'}
                </Button>

                {!videoLoaded && (
                  <Button
                    variant="outlined"
                    onClick={refreshVideoStream}
                    sx={{
                      borderColor: '#FF9800',
                      color: '#FF9800',
                      minWidth: 120,
                      '&:hover': {
                        borderColor: '#F57C00',
                        bgcolor: 'rgba(255, 152, 0, 0.1)'
                      }
                    }}
                  >
                    Refresh Video
                  </Button>
                )}
              </>
            )}
          </Box>
        )}

        {/* Fullscreen Exit Button */}
        {isFullscreen && (
          <Box
            sx={{
              position: 'fixed',
              bottom: 20,
              right: 20,
              zIndex: 10000
            }}
          >
            <Button
              variant="contained"
              startIcon={<FullscreenExit />}
              onClick={toggleFullscreen}
              sx={{
                bgcolor: 'rgba(0, 0, 0, 0.8)',
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(0, 0, 0, 0.9)'
                }
              }}
            >
              Exit Fullscreen
            </Button>
          </Box>
        )}

        {/* Instructions */}
        {!isRecording && !isFullscreen && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>How to use Screen Recording:</strong>
              <br />
              • Click "Start Screen Recording" below
              <br />
              • Select the screen/window containing the video interview
              <br />
              • The live preview will appear above with AI analysis indicators
              <br />
              • Use fullscreen mode for better monitoring
              <br />
              • AI analyzes facial expressions, gestures, and voice patterns in real-time
            </Typography>
          </Alert>
        )}

        {/* Recording Status */}
        {isRecording && !isFullscreen && (
          <Box sx={{ mt: 2, p: 2, bgcolor: '#E8F5E8', borderRadius: 1, border: '1px solid #4CAF50' }}>
            <Typography variant="body1" sx={{ fontWeight: 'bold', color: '#2E7D32', mb: 1 }}>
              ✅ Screen Recording Active - Live Preview Above
            </Typography>
            <Typography variant="body2" color="textSecondary">
              The captured screen is displayed in the video player above. AI analysis is running on both video frames and audio.
              {streamInfo.resolution && ` Recording at ${streamInfo.resolution}.`}
              {!streamInfo.hasAudio && ' Audio not available from this source.'}
              <br />
              <strong>Tip:</strong> Use fullscreen mode for better monitoring of the interview screen.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
});

export default ScreenRecorder;
