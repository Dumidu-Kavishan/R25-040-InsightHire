import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress
} from '@mui/material';
import {
  Work,
  MoreVert,
  Edit,
  Delete,
  Add
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { jobRoleService } from '../services/jobRoleService';
import JobRoleManagement from '../components/JobRoleManagement';

const HRAnalytics = () => {
  const { } = useAuth();
  
  // Add keyframes styles
  const keyframes = `
    @keyframes pulse {
      0% {
        transform: translate(-50%, -50%) scale(1.5);
        opacity: 1;
      }
      100% {
        transform: translate(-50%, -50%) scale(2);
        opacity: 0;
      }
    }
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
  `;
  const [jobRoles, setJobRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedJobRole, setSelectedJobRole] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [anchorPosition, setAnchorPosition] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [jobRoleToDelete, setJobRoleToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [expandedMenuId, setExpandedMenuId] = useState(null);

  useEffect(() => {
    loadData();
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
    try {
      setIsLoading(true);
      await loadJobRoles();
    } catch (error) {
      console.error('Error loading data:', error);
      showSnackbar('Failed to load data', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const loadJobRoles = async () => {
    try {
      const response = await jobRoleService.getJobRoles();
      if (response.status === 'success') {
        setJobRoles(response.job_roles || []);
      }
    } catch (error) {
      console.error('Error loading job roles:', error);
    }
  };


  const handleCreateJobRole = () => {
    setSelectedJobRole(null);
    setCreateDialogOpen(true);
  };

  const handleEditJobRole = (jobRole) => {
    setSelectedJobRole(jobRole);
    setEditDialogOpen(true);
    setAnchorEl(null);
    setOpenMenuId(null);
  };

  const handleDeleteJobRole = (jobRoleId) => {
    const jobRole = jobRoles.find(role => role.id === jobRoleId);
    setJobRoleToDelete(jobRole);
    setDeleteDialogOpen(true);
    setAnchorPosition(null);
    setOpenMenuId(null);
  };

  const handleDeleteConfirm = async () => {
    if (!jobRoleToDelete) return;
    
    try {
      const response = await jobRoleService.deleteJobRole(jobRoleToDelete.id);
      if (response.status === 'success') {
        showSnackbar('Job role deleted successfully', 'success');
        loadJobRoles();
      } else {
        showSnackbar('Failed to delete job role', 'error');
      }
    } catch (error) {
      console.error('Error deleting job role:', error);
      showSnackbar('Failed to delete job role', 'error');
    }
    
    setDeleteDialogOpen(false);
    setJobRoleToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setJobRoleToDelete(null);
  };

  const handleMenuToggle = (event, jobRoleId) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Toggle the expanded state
    if (expandedMenuId === jobRoleId) {
      setExpandedMenuId(null);
    } else {
      setExpandedMenuId(jobRoleId);
    }
  };

  const handleMenuClose = () => {
    setExpandedMenuId(null);
    setAnchorEl(null);
    setOpenMenuId(null);
    setAnchorPosition(null);
  };

  const handleEditClick = (jobRole) => {
    setExpandedMenuId(null);
    setIsEditing(true);
    setTimeout(() => {
      handleEditJobRole(jobRole);
      setIsEditing(false);
    }, 300);
  };

  const handleDeleteClick = (jobRoleId) => {
    setExpandedMenuId(null);
    setIsDeleting(true);
    setTimeout(() => {
      handleDeleteJobRole(jobRoleId);
      setIsDeleting(false);
    }, 300);
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleJobRoleCreated = () => {
    setCreateDialogOpen(false);
    loadJobRoles();
    showSnackbar('Job role created successfully', 'success');
  };

  const handleJobRoleUpdated = () => {
    setEditDialogOpen(false);
    loadJobRoles();
    showSnackbar('Job role updated successfully', 'success');
  };

  const getJobRoleInitials = (name) => {
    if (!name) return 'JR';
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



  return (
    <>
      <style>{keyframes}</style>
      <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={(theme) => ({ 
            fontWeight: 700,
            color: theme.palette.text.primary,
            mb: 1
          })}
        >
          Job Role Management
        </Typography>
      </Box>

      {/* Job Role Management Section */}
      <Box>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateJobRole}
            sx={(theme) => ({
              backgroundColor: theme.palette.primary.main,
              borderRadius: 2,
              px: 3,
              '&:hover': {
                backgroundColor: theme.palette.primary.dark,
              }
            })}
          >
            Create Job Role
          </Button>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : jobRoles.length === 0 ? (
          <Paper sx={{ p: 6, textAlign: 'center' }}>
            <Work sx={{ fontSize: 60, color: '#667eea', opacity: 0.7, mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No job roles yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create your first job role to define confidence level requirements for different positions
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateJobRole}
            >
              Create Job Role
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {jobRoles.map((jobRole) => {
              const jobRoleInitials = getJobRoleInitials(jobRole.name);
              const avatarColor = getAvatarColor(jobRole.name);
              const confidenceLevels = jobRole.confidence_levels || {};
              
              return (
                <Grid item xs={12} md={6} lg={4} key={jobRole.id}>
                <Card 
                  className="job-role-card"
                  sx={(theme) => ({ 
                    height: '100%', 
                    transition: 'all 0.3s ease',
                    borderRadius: 3,
                    border: `1px solid ${theme.palette.divider}`,
                    backgroundColor: theme.palette.background.paper,
                    '&:hover': { 
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
                      borderColor: theme.palette.primary.main,
                    }
                  })}
                >
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
                          {jobRoleInitials}
                        </Avatar>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" sx={(theme) => ({ fontWeight: 'bold', mb: 0.5, color: theme.palette.text.primary })}>
                            {jobRole.name}
                          </Typography>
                          <Typography variant="body2" sx={(theme) => ({ color: theme.palette.text.secondary })}>
                            {jobRole.description || 'No description'}
                          </Typography>
                        </Box>
                        {expandedMenuId === jobRole.id ? (
                          <Box className="expanded-menu-buttons" sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              onClick={(e) => handleEditClick(jobRole)}
                              size="small"
                              disabled={isEditing}
                              sx={(theme) => ({
                                color: theme.palette.primary.main,
                                backgroundColor: 'rgba(100, 181, 246, 0.1)',
                                borderRadius: 2,
                                width: 36,
                                height: 36,
                                transition: 'all 0.3s ease',
                                animation: 'slideInRight 0.3s ease',
                                '&:hover': {
                                  backgroundColor: 'rgba(100, 181, 246, 0.2)',
                                  transform: 'scale(1.1)',
                                  boxShadow: '0 4px 12px rgba(100, 181, 246, 0.3)',
                                },
                                '&:active': {
                                  transform: 'scale(0.95)',
                                },
                                '&.Mui-disabled': {
                                  opacity: 0.6,
                                }
                              })}
                            >
                              {isEditing ? (
                                <CircularProgress size={16} sx={(theme) => ({ color: theme.palette.primary.main })} />
                              ) : (
                                <Edit sx={{ fontSize: 18 }} />
                              )}
                            </IconButton>
                            <IconButton
                              onClick={(e) => handleDeleteClick(jobRole.id)}
                              size="small"
                              disabled={isDeleting}
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
                                },
                                '&.Mui-disabled': {
                                  opacity: 0.6,
                                }
                              })}
                            >
                              {isDeleting ? (
                                <CircularProgress size={16} sx={(theme) => ({ color: theme.palette.error.main })} />
                              ) : (
                                <Delete sx={{ fontSize: 18 }} />
                              )}
                            </IconButton>
                          </Box>
                        ) : (
                          <IconButton
                            onClick={(e) => handleMenuToggle(e, jobRole.id)}
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
                              },
                            })}
                          >
                            <MoreVert sx={{ fontSize: 20, transition: 'transform 0.3s ease' }} />
                          </IconButton>
                        )}
                      </Box>

                      {/* Confidence Levels */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                          Confidence Requirements
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          {/* Voice Confidence */}
                          <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="body2">Voice</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: '#2196F3' }}>
                                {confidenceLevels.voice_confidence || 0}%
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={confidenceLevels.voice_confidence || 0} 
                              sx={{ 
                                height: 6, 
                                borderRadius: 3,
                                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#2196F3'
                                }
                              }} 
                            />
                          </Box>

                          {/* Hand Confidence */}
                          <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="body2">Hand</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: '#9C27B0' }}>
                                {confidenceLevels.hand_confidence || 0}%
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={confidenceLevels.hand_confidence || 0} 
                              sx={{ 
                                height: 6, 
                                borderRadius: 3,
                                backgroundColor: 'rgba(156, 39, 176, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#9C27B0'
                                }
                              }} 
                            />
                          </Box>

                          {/* Eye Confidence */}
                          <Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="body2">Eye</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: '#4CAF50' }}>
                                {confidenceLevels.eye_confidence || 0}%
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={confidenceLevels.eye_confidence || 0} 
                              sx={{ 
                                height: 6, 
                                borderRadius: 3,
                                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#4CAF50'
                                }
                              }} 
                            />
                          </Box>
                        </Box>
                      </Box>

                      {/* Status */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pt: 2, borderTop: '1px solid #f0f0f0' }}>
                        <Chip
                          label={jobRole.is_active !== false ? 'Active' : 'Inactive'}
                          color={jobRole.is_active !== false ? 'success' : 'default'}
                          size="small"
                        />
                        <Typography variant="caption" color="text.secondary">
                          Created: {new Date(jobRole.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
      </Box>


      {/* Create Job Role Dialog */}
      <JobRoleManagement
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={handleJobRoleCreated}
        mode="create"
      />

      {/* Edit Job Role Dialog */}
      <JobRoleManagement
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        onSuccess={handleJobRoleUpdated}
        mode="edit"
        jobRole={selectedJobRole}
      />

      {/* Cute & Compact Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        maxWidth="xs"
        sx={(theme) => ({
          '& .MuiDialog-paper': {
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            background: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            overflow: 'hidden',
          }
        })}
      >
        <DialogContent sx={{ textAlign: 'center', py: 3, px: 4 }}>
          {/* Cute Delete Icon */}
          <Box sx={{ mb: 2 }}>
            <Typography sx={{ fontSize: '2.5rem', mb: 1 }}>🗑️</Typography>
            <Typography 
              variant="h6" 
              sx={(theme) => ({ 
                fontWeight: 600, 
                color: theme.palette.text.primary,
                mb: 1
              })}
            >
              Delete "{jobRoleToDelete?.name || 'Job Role'}"?
            </Typography>
            <Typography 
              variant="body2" 
              sx={(theme) => ({ 
                color: theme.palette.text.secondary,
                fontSize: '0.875rem'
              })}
            >
              This action cannot be undone
            </Typography>
          </Box>
          
          {/* Compact Job Role Info */}
          <Box
            sx={(theme) => ({
              background: theme.palette.background.paper,
              borderRadius: 2,
              p: 2,
              mb: 3,
              border: `1px solid ${theme.palette.divider}`,
            })}
          >
            <Typography 
              variant="body2" 
              sx={(theme) => ({ 
                color: theme.palette.text.secondary,
                fontSize: '0.8rem',
                lineHeight: 1.4,
              })}
            >
              {jobRoleToDelete?.description || 'No description available'}
            </Typography>
          </Box>
          
          {/* Cute Warning */}
          <Box
            sx={(theme) => ({
              background: 'rgba(244, 67, 54, 0.1)',
              borderRadius: 2,
              p: 2,
              border: '1px solid rgba(244, 67, 54, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              mb: 3,
            })}
          >
            <Typography sx={{ fontSize: '1rem' }}>⚠️</Typography>
            <Typography 
              variant="body2" 
              sx={(theme) => ({ 
                color: theme.palette.error.main, 
                fontWeight: 500,
                fontSize: '0.8rem'
              })}
            >
              All data will be lost
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ justifyContent: 'center', gap: 2, pb: 3, px: 4 }}>
          <Button
            onClick={handleDeleteCancel}
            variant="outlined"
            size="small"
            sx={(theme) => ({ 
              px: 3, 
              py: 1,
              borderRadius: 2,
              borderColor: theme.palette.divider,
              color: theme.palette.text.secondary,
              fontSize: '0.875rem',
              fontWeight: 500,
              minWidth: 80,
              '&:hover': {
                borderColor: theme.palette.text.secondary,
                backgroundColor: theme.palette.background.paper,
              },
            })}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            size="small"
            sx={(theme) => ({ 
              px: 3, 
              py: 1,
              borderRadius: 2,
              backgroundColor: theme.palette.error.main,
              fontSize: '0.875rem',
              fontWeight: 600,
              minWidth: 80,
              '&:hover': {
                backgroundColor: theme.palette.error.dark,
              },
            })}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
    </>
  );
};

export default HRAnalytics;
