import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Avatar,
  Chip,
  Fab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Menu,
  Tooltip,
  InputAdornment
} from '@mui/material';
import {
  Add,
  PlayArrow,
  Visibility,
  Assessment,
  CheckCircle,
  Schedule,
  AccessTime,
  Delete,
  MoreVert,
  PersonAdd,
  Person,
  Badge,
  Work,
  Close
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { interviewService } from '../services/api';
import { jobRoleService } from '../services/jobRoleService';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import InterviewAnalysisPopup from '../components/InterviewAnalysisPopup';
import InterviewScoreDisplay from '../components/InterviewScoreDisplay';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Add keyframes styles
  const keyframes = `
    @keyframes slideInRight {
      0% {
        opacity: 0;
        transform: translateX(20px);
      }
      100% {
        opacity: 1;
        transform: translateX(0);
      }
    }
    @keyframes shimmer {
      0% {
        background-position: -200% 0;
      }
      100% {
        background-position: 200% 0;
      }
    }
    @keyframes float {
      0%, 100% {
        transform: translateY(0px) rotate(0deg);
      }
      50% {
        transform: translateY(-20px) rotate(180deg);
      }
    }
    @keyframes pulse {
      0%, 100% {
        transform: scale(1);
        opacity: 1;
      }
      50% {
        transform: scale(1.05);
        opacity: 0.8;
      }
    }
    @keyframes slideInUp {
      0% {
        opacity: 0;
        transform: translateY(30px);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }
    @keyframes fadeIn {
      0% {
        opacity: 0;
      }
      100% {
        opacity: 1;
      }
    }
    @keyframes scaleIn {
      0% {
        opacity: 0;
        transform: scale(0.9);
      }
      100% {
        opacity: 1;
        transform: scale(1);
      }
    }
    @keyframes bounce {
      0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
      }
      40% {
        transform: translateY(-10px);
      }
      60% {
        transform: translateY(-5px);
      }
    }
    @keyframes glow {
      0%, 100% {
        box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
      }
      50% {
        box-shadow: 0 0 30px rgba(79, 195, 247, 0.6);
      }
    }
    @keyframes wiggle {
      0%, 100% {
        transform: rotate(0deg);
      }
      25% {
        transform: rotate(5deg);
      }
      75% {
        transform: rotate(-5deg);
      }
    }
    @keyframes sparkle {
      0%, 100% {
        opacity: 0;
        transform: scale(0);
      }
      50% {
        opacity: 1;
        transform: scale(1);
      }
    }
  `;
  const [interviews, setInterviews] = useState([]);
  const [jobRoles, setJobRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newInterviewData, setNewInterviewData] = useState({
    candidate_name: '',
    candidate_nic_passport: '',
    job_role_id: ''
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [showValidation, setShowValidation] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [interviewToDelete, setInterviewToDelete] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [analysisPopupOpen, setAnalysisPopupOpen] = useState(false);
  const [selectedInterviewId, setSelectedInterviewId] = useState(null);
  const [scoreDisplayOpen, setScoreDisplayOpen] = useState(false);
  const [selectedScoreSessionId, setSelectedScoreSessionId] = useState(null);
  const [selectedScoreJobRoleId, setSelectedScoreJobRoleId] = useState(null);
  const [preloadedScores, setPreloadedScores] = useState(null);
  const [loadingScores, setLoadingScores] = useState(false);
  const [expandedMenuId, setExpandedMenuId] = useState(null);

  useEffect(() => {
    if (user) {
      console.log('👤 User loaded, loading data:', user);
      loadData();
    } else {
      console.log('⏳ Waiting for user to load...');
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  // Inject CSS animations
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = keyframes;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Close expanded menu when clicking outside or pressing Escape
  useEffect(() => {
    const handleClickOutside = (event) => {
      // Don't close if clicking on the expanded menu buttons
      if (event.target.closest('.expanded-menu-buttons')) {
        return;
      }
      
      if (expandedMenuId) {
        setExpandedMenuId(null);
      }
    };

    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && expandedMenuId) {
        setExpandedMenuId(null);
      }
    };

    if (expandedMenuId) {
      // Use a small delay to prevent immediate closing
      setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleEscapeKey);
      }, 100);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [expandedMenuId]);

  const loadData = async () => {
    await Promise.all([
      loadInterviews(),
      loadJobRoles()
    ]);
  };

  // Debug: Log interviews state changes
  useEffect(() => {
    console.log('Interviews state updated:', interviews);
  }, [interviews]);

  const loadInterviews = async () => {
    try {
      setIsLoading(true);
      console.log('Loading interviews...');
      
      // Direct test call
      console.log('User from localStorage:', JSON.parse(localStorage.getItem('user') || '{}'));
      
      const response = await interviewService.getInterviews();
      console.log('Interview response:', response);
      if (response.status === 'success') {
        console.log('Setting interviews:', response.interviews);
        setInterviews(response.interviews || []);
      } else {
        console.error('API returned error:', response);
      }
    } catch (error) {
      console.error('Error loading interviews:', error);
      console.error('Error details:', error.response);
      toast.error('Failed to load interviews');
    } finally {
      setIsLoading(false);
    }
  };

  const loadJobRoles = async () => {
    try {
      console.log('Loading job roles...');
      console.log('User from localStorage:', JSON.parse(localStorage.getItem('user') || '{}'));
      
      const response = await jobRoleService.getJobRoles();
      console.log('Job roles response:', response);
      if (response.status === 'success') {
        setJobRoles(response.job_roles || []);
      }
    } catch (error) {
      console.error('Error loading job roles:', error);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!newInterviewData.candidate_name.trim()) {
      errors.candidate_name = 'Candidate name is required';
    }
    
    if (!newInterviewData.candidate_nic_passport.trim()) {
      errors.candidate_nic_passport = 'NIC or Passport number is required';
    }
    
    if (!newInterviewData.job_role_id) {
      errors.job_role_id = 'Please select a job role';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreateInterview = async () => {
    setShowValidation(true);
    
    if (!validateForm()) {
      return;
    }
    
    try {
      const response = await interviewService.createInterview(newInterviewData);
      if (response.status === 'success') {
        toast.success('Interview created successfully!');
        setCreateDialogOpen(false);
        setNewInterviewData({
          candidate_name: '',
          candidate_nic_passport: '',
          job_role_id: ''
        });
        setValidationErrors({});
        setShowValidation(false);
        loadData();
      }
    } catch (error) {
      console.error('Error creating interview:', error);
      toast.error('Failed to create interview');
    }
  };

  const handleCloseDialog = () => {
    setCreateDialogOpen(false);
    setValidationErrors({});
    setShowValidation(false);
    setNewInterviewData({
      candidate_name: '',
      candidate_nic_passport: '',
      job_role_id: ''
    });
  };

  const handleMenuOpen = (event, interviewId) => {
    setAnchorEl(event.currentTarget);
    setOpenMenuId(interviewId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setOpenMenuId(null);
  };

  const handleMenuToggle = (event, interviewId) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Toggle the expanded state
    if (expandedMenuId === interviewId) {
      setExpandedMenuId(null);
    } else {
      setExpandedMenuId(interviewId);
    }
  };

  const handleDeleteClick = (interview) => {
    setExpandedMenuId(null);
    setInterviewToDelete(interview);
    setDeleteDialogOpen(true);
    handleMenuClose();
  };

  const handleDeleteConfirm = async () => {
    if (!interviewToDelete) return;
    
    try {
      const response = await interviewService.deleteInterview(interviewToDelete.id);
      if (response.status === 'success') {
        toast.success('Interview deleted successfully!');
        setDeleteDialogOpen(false);
        setInterviewToDelete(null);
        loadData(); // Reload the interviews list
      } else {
        toast.error(response.message || 'Failed to delete interview');
      }
    } catch (error) {
      console.error('Error deleting interview:', error);
      toast.error('Failed to delete interview');
    }
  };

  const handleViewAnalysis = (interviewId) => {
    setSelectedInterviewId(interviewId);
    setAnalysisPopupOpen(true);
  };

  const handleViewScores = async (sessionId, jobRoleId) => {
    try {
      // Show loading state
      setLoadingScores(true);
      
      // First, load the scores data
      console.log('🔄 Loading scores before showing modal for sessionId:', sessionId);
      
      const response = await fetch(`http://localhost:5000/api/interviews/${sessionId}/calculate-final-scores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.uid,
          job_role_id: jobRoleId
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Scores loaded successfully:', result);
        
        // Check if the response indicates no records found
        if (result.status === 'error' && result.message && result.message.includes('No interview records found')) {
          console.log('📊 No interview records found for this session');
          toast.error('No interview records found for Candidate');
          return; // Don't open the modal
        } else if (result.status === 'success') {
          // Store the pre-loaded scores
          setPreloadedScores(result.data.final_scores);
          
          // Set the data and open modal
          setSelectedScoreSessionId(sessionId);
          setSelectedScoreJobRoleId(jobRoleId);
          setScoreDisplayOpen(true);
        } else {
          // For other error cases, show toast and don't open modal
          toast.error('Candidate Analysis Data Empty');
          return; // Don't open the modal
        }
      } else if (response.status === 404) {
        // Show toast notification instead of opening modal
        toast.error('Candidate Analysis Data Empty');
        return; // Don't open the modal
      } else {
        // Handle other error responses
        const errorResult = await response.json();
        console.log('❌ API Error Response:', errorResult);
        
        if (errorResult.message && errorResult.message.includes('No interview records found')) {
          toast.error('No interview records found for Candidate');
        } else {
          toast.error('Candidate Analysis Data Empty');
        }
        return; // Don't open the modal
      }
    } catch (error) {
      console.error('Error loading scores:', error);
      toast.error('Failed to load scores');
    } finally {
      // Hide loading state
      setLoadingScores(false);
    }
  };

  const handleCloseAnalysisPopup = () => {
    setAnalysisPopupOpen(false);
    setSelectedInterviewId(null);
  };

  const handleCloseScoreDisplay = () => {
    setScoreDisplayOpen(false);
    setSelectedScoreSessionId(null);
    setSelectedScoreJobRoleId(null);
    setPreloadedScores(null);
    setLoadingScores(false);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setInterviewToDelete(null);
  };

  const handleViewInterview = (interviewId) => {
    navigate(`/interview/${interviewId}`);
  };


  const getCandidateName = (interview) => {
    return interview.candidate_name || interview.candidateName || interview.name || 'Unknown Candidate';
  };

  const getCandidateInitials = (name) => {
    if (!name) return 'UN';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const getAvatarColor = (name) => {
    if (!name) return '#667eea';
    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#4facfe', 
      '#43e97b', '#38f9d7', '#f5576c', '#00f2fe'
    ];
    const index = name.length % colors.length;
    return colors[index];
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'info';
      case 'active': return 'warning';
      case 'completed': return 'success';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled': return <Schedule />;
      case 'active': return <PlayArrow />;
      case 'completed': return <CheckCircle />;
      default: return <AccessTime />;
    }
  };

  const getDisplayName = () => {
    if (!user) return 'User';
    if (user.username) return user.username;
    if (user.displayName) return user.displayName;
    if (user.firstName && user.lastName) return `${user.firstName} ${user.lastName}`;
    if (user.name) return user.name;
    if (user.email) return user.email; // Show full email instead of just username part
    return 'User';
  };

  // Stats calculations
  const totalInterviews = interviews.length;
  const activeInterviews = interviews.filter(interview => interview.status === 'active').length;
  const completedInterviews = interviews.filter(interview => interview.status === 'completed').length;

  return (
    <>
      <style>{keyframes}</style>
      <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          sx={(theme) => ({ 
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1
          })}
        >
          Welcome back, {getDisplayName()}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage your interviews and track candidate progress
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={(theme) => ({ 
            p: 3, 
            textAlign: 'center', 
            backgroundColor: theme.palette.primary.main, 
            color: 'white',
            borderRadius: 2,
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 4px 20px rgba(79, 195, 247, 0.3)' 
              : '0 4px 20px rgba(79, 195, 247, 0.2)'
          })}>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{totalInterviews}</Typography>
            <Typography variant="subtitle2">Total Interviews</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={(theme) => ({ 
            p: 3, 
            textAlign: 'center', 
            backgroundColor: theme.palette.secondary.main, 
            color: 'white',
            borderRadius: 2,
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 4px 20px rgba(41, 182, 246, 0.3)' 
              : '0 4px 20px rgba(41, 182, 246, 0.2)'
          })}>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{activeInterviews}</Typography>
            <Typography variant="subtitle2">Active Interviews</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={(theme) => ({ 
            p: 3, 
            textAlign: 'center', 
            backgroundColor: theme.palette.mode === 'dark' ? '#37474F' : '#B3E5FC',
            color: theme.palette.mode === 'dark' ? 'white' : '#2C3E50',
            borderRadius: 2,
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 4px 20px rgba(55, 71, 79, 0.4)' 
              : '0 4px 20px rgba(179, 229, 252, 0.3)'
          })}>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>{completedInterviews}</Typography>
            <Typography variant="subtitle2">Completed</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Interviews Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" sx={(theme) => ({ 
          fontWeight: 600, 
          color: theme.palette.text.primary 
        })}>
          Recent Interviews
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
          sx={(theme) => ({
            backgroundColor: theme.palette.primary.main,
            borderRadius: 2,
            px: 3,
            '&:hover': {
              backgroundColor: theme.palette.secondary.main,
            }
          })}
        >
          Create Interview
        </Button>
      </Box>

      {/* Interviews List */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : interviews.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <Assessment sx={{ fontSize: 60, color: '#667eea', opacity: 0.7, mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No interviews yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create your first interview to get started with candidate evaluation
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Interview
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {interviews.map((interview) => {
            const candidateName = getCandidateName(interview);
            const candidateInitials = getCandidateInitials(candidateName);
            const avatarColor = getAvatarColor(candidateName);
            
            return (
              <Grid item xs={12} md={6} lg={4} key={interview.id}>
                <Card sx={(theme) => ({ 
                  height: '100%', 
                  transition: 'all 0.3s ease',
                  borderRadius: 3,
                  backgroundColor: theme.palette.background.paper,
                  border: theme.palette.mode === 'dark' 
                    ? '1px solid rgba(255, 255, 255, 0.1)'
                    : '1px solid rgba(102, 126, 234, 0.1)',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: theme.palette.mode === 'dark'
                      ? '0 8px 30px rgba(0, 0, 0, 0.4)'
                      : '0 8px 30px rgba(102, 126, 234, 0.15)',
                  }
                })}>
                  <CardContent sx={{ p: 3 }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar 
                        sx={{ 
                          bgcolor: avatarColor,
                          mr: 2,
                          width: 48,
                          height: 48,
                        }}
                      >
                        {candidateInitials}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                          {candidateName}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {interview.position || 'Position not specified'}
                        </Typography>
                      </Box>
                       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                         <Chip
                           label={interview.status || 'scheduled'}
                           color={getStatusColor(interview.status)}
                           icon={getStatusIcon(interview.status)}
                           size="small"
                         />
                         {expandedMenuId === interview.id ? (
                           <Box className="expanded-menu-buttons" sx={{ display: 'flex', gap: 1 }}>
                             <IconButton
                               onClick={(e) => handleDeleteClick(interview)}
                               size="small"
                               sx={(theme) => ({
                                 color: theme.palette.error.main,
                                 backgroundColor: 'rgba(244, 67, 54, 0.1)',
                                 borderRadius: 2,
                                 width: 36,
                                 height: 36,
                                 transition: 'all 0.3s ease',
                                 animation: 'slideInRight 0.3s ease 0.1s both',
                                 '&:hover': {
                                   backgroundColor: 'rgba(244, 67, 54, 0.2)',
                                   transform: 'scale(1.1)',
                                   boxShadow: '0 4px 12px rgba(244, 67, 54, 0.3)',
                                 },
                                 '&:active': {
                                   transform: 'scale(0.95)',
                                 }
                               })}
                             >
                               <Delete sx={{ fontSize: 18 }} />
                             </IconButton>
                           </Box>
                         ) : (
                           <Tooltip title="More options">
                             <IconButton
                               onClick={(e) => handleMenuToggle(e, interview.id)}
                               size="small"
                               sx={(theme) => ({
                                 color: theme.palette.text.secondary,
                                 borderRadius: 2,
                                 position: 'relative',
                                 transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                 '&:hover': {
                                   color: theme.palette.primary.main,
                                   backgroundColor: 'rgba(100, 181, 246, 0.08)',
                                   transform: 'scale(1.1) rotate(90deg)',
                                   boxShadow: '0 4px 12px rgba(100, 181, 246, 0.4)',
                                 },
                                 '&:active': {
                                   transform: 'scale(0.95) rotate(90deg)',
                                 }
                               })}
                             >
                               <MoreVert sx={{ fontSize: 20, transition: 'transform 0.3s ease' }} />
                             </IconButton>
                           </Tooltip>
                         )}
                       </Box>
                    </Box>

                    {/* Details */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Created: {new Date(interview.created_at).toLocaleDateString()}
                      </Typography>
                      {interview.platform && (
                        <Typography variant="body2" color="text.secondary">
                          Platform: {interview.platform}
                        </Typography>
                      )}
                    </Box>

                    {/* Actions */}
                    <Box sx={(theme) => ({ 
                      display: 'flex', 
                      gap: 1, 
                      pt: 2, 
                      borderTop: theme.palette.mode === 'dark' 
                        ? '1px solid rgba(255, 255, 255, 0.1)' 
                        : '1px solid #f0f0f0' 
                    })}>
                      {interview.status === 'scheduled' && (
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<Visibility />}
                          onClick={() => handleViewInterview(interview.id)}
                          sx={{ flex: 1 }}
                        >
                          View
                        </Button>
                      )}
                      {interview.status === 'completed' && (
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<Assessment />}
                          onClick={() => handleViewScores(interview.id, interview.job_role_id)}
                          sx={{ flex: 1 }}
                        >
                          View Scores
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        onClick={() => setCreateDialogOpen(true)}
        sx={(theme) => ({
          position: 'fixed',
          bottom: 24,
          right: 24,
          backgroundColor: theme.palette.primary.main,
          '&:hover': {
            backgroundColor: theme.palette.secondary.main,
          },
          display: { xs: 'flex', md: 'none' }
        })}
      >
        <Add />
      </Fab>

      {/* Create Interview Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={handleCloseDialog} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
            overflow: 'hidden',
            position: 'relative',
            animation: 'scaleIn 0.4s ease-out',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, #4FC3F7 0%, #29B6F6 50%, #0288D1 100%)',
              backgroundSize: '200% 100%',
              animation: 'shimmer 3s ease-in-out infinite'
            }
          }
        }}
      >
        {/* Header with Gradient */}
        <DialogTitle sx={(theme) => ({
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          py: 3,
          px: 4,
          position: 'relative',
          overflow: 'hidden',
          animation: 'slideInUp 0.5s ease-out 0.1s both',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
            animation: 'float 6s ease-in-out infinite'
          }
        })}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              animation: 'bounce 2s ease-in-out infinite, glow 3s ease-in-out infinite',
              position: 'relative',
              zIndex: 1,
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -2,
                left: -2,
                right: -2,
                bottom: -2,
                borderRadius: '50%',
                background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.3))',
                zIndex: -1,
                animation: 'pulse 2s ease-in-out infinite'
              }
            }}>
              <PersonAdd sx={{ fontSize: 24, filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
            </Box>
            <Box sx={{ position: 'relative', zIndex: 1 }}>
              <Typography variant="h5" sx={{ 
                fontWeight: 700, 
                mb: 0.5,
                animation: 'fadeIn 0.6s ease-out 0.2s both',
                textShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                Create New Interview
              </Typography>
              <Typography variant="body2" sx={{ 
                opacity: 0.9,
                animation: 'fadeIn 0.6s ease-out 0.4s both'
              }}>
                Set up a new candidate interview session
              </Typography>
            </Box>
          </Box>
          <IconButton 
            onClick={handleCloseDialog} 
            sx={{ 
              color: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              transition: 'all 0.3s ease',
              animation: 'fadeIn 0.6s ease-out 0.3s both',
              position: 'relative',
              zIndex: 1,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                transform: 'scale(1.1) rotate(90deg)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
              }
            }}
          >
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ 
          p: 4, 
          pt: 3,
          position: 'relative',
          animation: 'slideInUp 0.6s ease-out 0.2s both',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 80% 20%, rgba(79, 195, 247, 0.05) 0%, transparent 50%)',
            pointerEvents: 'none',
            zIndex: 0
          }
        }}>
          <Box sx={{ mb: 3, position: 'relative', zIndex: 1 }}>
            <Typography variant="body2" sx={(theme) => ({ 
              color: theme.palette.text.secondary,
              mb: 3,
              textAlign: 'center',
              animation: 'fadeIn 0.7s ease-out 0.3s both',
              fontSize: '1.1rem',
              fontWeight: 500
            })}>
              Fill in the candidate details to start a new interview session
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {/* Candidate Name */}
            <Grid item xs={12} sx={{ animation: 'slideInUp 0.7s ease-out 0.4s both' }}>
              <Box sx={{ position: 'relative', zIndex: 1 }}>
                <TextField
                  fullWidth
                  label="Candidate Name"
                  value={newInterviewData.candidate_name}
                  onChange={(e) => setNewInterviewData({ ...newInterviewData, candidate_name: e.target.value })}
                  required
                  error={showValidation && !!validationErrors.candidate_name}
                  helperText={showValidation && validationErrors.candidate_name}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person sx={(theme) => ({ color: theme.palette.primary.main })} />
                      </InputAdornment>
                    ),
                  }}
                   sx={(theme) => ({
                     '& .MuiOutlinedInput-root': {
                       borderRadius: 3,
                       backgroundColor: theme.palette.background.paper,
                       color: theme.palette.text.primary,
                       transition: 'all 0.3s ease',
                       boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                       '&:hover': {
                         '& .MuiOutlinedInput-notchedOutline': {
                           borderColor: 'primary.main',
                           borderWidth: 2,
                         },
                         transform: 'translateY(-2px)',
                         boxShadow: '0 4px 16px rgba(79, 195, 247, 0.15)',
                       },
                       '&.Mui-focused': {
                         '& .MuiOutlinedInput-notchedOutline': {
                           borderColor: 'primary.main',
                           borderWidth: 2,
                         },
                         transform: 'translateY(-2px)',
                         boxShadow: '0 6px 20px rgba(79, 195, 247, 0.2)',
                         animation: 'glow 2s ease-in-out infinite'
                       },
                     },
                     '& .MuiInputLabel-root': {
                       color: theme.palette.text.secondary,
                       transition: 'color 0.3s ease',
                       '&.Mui-focused': {
                         color: 'primary.main',
                       },
                     },
                     '& .MuiInputBase-input': {
                       color: theme.palette.text.primary,
                     },
                   })}
                />
              </Box>
            </Grid>

            {/* NIC or Passport */}
            <Grid item xs={12} sx={{ animation: 'slideInUp 0.7s ease-out 0.5s both' }}>
              <TextField
                fullWidth
                label="NIC or Passport Number"
                value={newInterviewData.candidate_nic_passport}
                onChange={(e) => setNewInterviewData({ ...newInterviewData, candidate_nic_passport: e.target.value })}
                required
                error={showValidation && !!validationErrors.candidate_nic_passport}
                helperText={showValidation && validationErrors.candidate_nic_passport}
                placeholder="Enter NIC or Passport number"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Badge sx={(theme) => ({ color: theme.palette.primary.main })} />
                    </InputAdornment>
                  ),
                }}
                sx={(theme) => ({
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: theme.palette.background.paper,
                    color: theme.palette.text.primary,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                        borderWidth: 2,
                      },
                    },
                    '&.Mui-focused': {
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                        borderWidth: 2,
                      },
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: theme.palette.text.secondary,
                    '&.Mui-focused': {
                      color: 'primary.main',
                    },

                  },
                  '& .MuiInputBase-input': {
                    color: theme.palette.text.primary,
                  },
                })}
              />
            </Grid>

            {/* Job Role Selection */}
            <Grid item xs={12} sx={{ animation: 'slideInUp 0.7s ease-out 0.6s both' }}>
              <FormControl 
                fullWidth 
                required 
                error={showValidation && !!validationErrors.job_role_id}
                sx={(theme) => ({
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    backgroundColor: theme.palette.background.paper,
                    color: theme.palette.text.primary,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                        borderWidth: 2,
                      },
                    },
                    '&.Mui-focused': {
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                        borderWidth: 2,
                      },
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: theme.palette.text.secondary,
                    '&.Mui-focused': {
                      color: 'primary.main',
                    },
                  },
                  '& .MuiSelect-select': {
                    color: theme.palette.text.primary,
                  },
                })}
              >
                <InputLabel>Position (Job Role)</InputLabel>
                <Select
                  value={newInterviewData.job_role_id}
                  onChange={(e) => setNewInterviewData({ ...newInterviewData, job_role_id: e.target.value })}
                  label="Position (Job Role)"
                  startAdornment={
                    <InputAdornment position="start" sx={{ ml: 1 }}>
                      <Work sx={(theme) => ({ color: theme.palette.primary.main })} />
                    </InputAdornment>
                  }
                >
                  {jobRoles.map((jobRole) => (
                    <MenuItem key={jobRole.id} value={jobRole.id}>
                      {jobRole.name}
                    </MenuItem>
                  ))}
                </Select>
                {showValidation && validationErrors.job_role_id && (
                  <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                    {validationErrors.job_role_id}
                  </Typography>
                )}
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ 
          p: 4, 
          pt: 2, 
          gap: 2,
          position: 'relative',
          zIndex: 1,
          animation: 'slideInUp 0.8s ease-out 0.7s both'
        }}>
          <Button 
            onClick={handleCloseDialog}
            variant="outlined"
            sx={{
              borderRadius: 3,
              px: 4,
              py: 1.5,
              textTransform: 'none',
              fontWeight: 600,
              borderWidth: 2,
              transition: 'all 0.3s ease',
              '&:hover': {
                borderWidth: 2,
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleCreateInterview}
            startIcon={<Add />}
            sx={{
              borderRadius: 3,
              px: 4,
              py: 1.5,
              textTransform: 'none',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%)',
              boxShadow: '0 4px 15px rgba(79, 195, 247, 0.4)',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
                transition: 'left 0.5s ease',
              },
              '&:hover': {
                background: 'linear-gradient(135deg, #29B6F6 0%, #0288D1 100%)',
                boxShadow: '0 6px 20px rgba(79, 195, 247, 0.6)',
                transform: 'translateY(-2px) scale(1.02)',
                '&::before': {
                  left: '100%',
                },
              },
              '&:active': {
                transform: 'translateY(0) scale(0.98)',
              },
              transition: 'all 0.3s ease'
            }}
          >
            Create Interview
          </Button>
        </DialogActions>
      </Dialog>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: (theme) => ({
            borderRadius: 3,
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 8px 32px rgba(0,0,0,0.4)' 
              : '0 8px 32px rgba(0,0,0,0.12)',
            border: theme.palette.mode === 'dark' 
              ? '1px solid rgba(255, 255, 255, 0.1)' 
              : '1px solid rgba(66, 165, 245, 0.1)',
            mt: 1
          })
        }}
      >
        <MenuItem 
          onClick={() => handleDeleteClick(interviews.find(interview => interview.id === openMenuId))}
          sx={{
            '&:hover': {
              backgroundColor: 'rgba(244, 67, 54, 0.08)'
            }
          }}
        >
          <Delete sx={{ mr: 2, color: '#F44336' }} />
          <Typography sx={{ fontWeight: 500 }}>Delete Interview</Typography>
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel} maxWidth="sm" fullWidth>
        <DialogActions sx={(theme) => ({ 
          p: 3, 
          background: theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #1A1A1A 0%, #2C2C2C 100%)'
            : 'linear-gradient(135deg, #FAFAFA 0%, #F0F0F0 100%)',
          borderTop: '1px solid rgba(0,0,0,0.1)',
          gap: 2,
          justifyContent: 'center'
        })}>
          <Button 
            onClick={handleDeleteCancel}
            sx={{
              px: 3,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              color: '#666',
              border: '1px solid rgba(102, 102, 102, 0.2)',
              '&:hover': {
                backgroundColor: 'rgba(102, 102, 102, 0.08)',
                border: '1px solid rgba(102, 102, 102, 0.3)'
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            variant="contained"
            onClick={handleDeleteConfirm}
            sx={{
              background: 'linear-gradient(135deg, #F44336 0%, #D32F2F 100%)',
              borderRadius: 2,
              px: 3,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 600,
              textTransform: 'none',
              boxShadow: '0 4px 20px rgba(244, 67, 54, 0.3)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 30px rgba(244, 67, 54, 0.4)',
                background: 'linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%)',
              }
            }}
          >
            Delete Interview
          </Button>
        </DialogActions>
      </Dialog>

      {/* Interview Analysis Popup */}
      <InterviewAnalysisPopup
        open={analysisPopupOpen}
        onClose={handleCloseAnalysisPopup}
        interviewId={selectedInterviewId}
      />

      {/* Interview Score Display */}
      <InterviewScoreDisplay
        open={scoreDisplayOpen}
        onClose={handleCloseScoreDisplay}
        sessionId={selectedScoreSessionId}
        jobRoleId={selectedScoreJobRoleId}
        preloadedScores={preloadedScores}
      />

      {/* Loading Overlay for Scores */}
      <Dialog
        open={loadingScores}
        disableEscapeKeyDown
        disableBackdropClick
        maxWidth="sm"
        fullWidth
        sx={{
          '& .MuiDialog-paper': {
            borderRadius: 3,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          }
        }}
      >
        <DialogContent sx={{ 
          p: 4, 
          textAlign: 'center',
          minHeight: 200,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <Box sx={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 3,
            animation: 'pulse 2s infinite',
            '@keyframes pulse': {
              '0%': {
                transform: 'scale(1)',
                opacity: 1,
              },
              '50%': {
                transform: 'scale(1.1)',
                opacity: 0.8,
              },
              '100%': {
                transform: 'scale(1)',
                opacity: 1,
              },
            }
          }}>
            <Assessment sx={{ fontSize: 40, color: 'white' }} />
          </Box>
          
          <Typography variant="h5" sx={{ 
            fontWeight: 600, 
            color: '#1E293B',
            mb: 2
          }}>
            Loading Analysis Results
          </Typography>
          
          <Typography variant="body1" sx={{ 
            color: '#64748B',
            mb: 3
          }}>
            Calculating interview scores and confidence metrics...
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress 
              size={24} 
              sx={{ 
                color: '#60A5FA',
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                }
              }} 
            />
            <Typography variant="body2" sx={{ color: '#64748B' }}>
              Please wait...
            </Typography>
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
    </>
  );
};

export default Dashboard;

