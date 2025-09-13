import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Avatar,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Alert,
  Snackbar,
  LinearProgress
} from '@mui/material';
import {
  Add,
  MoreVert,
  Edit,
  Delete,
  Work
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { jobRoleService } from '../services/jobRoleService';
import JobRoleManagement from '../components/JobRoleManagement';

const HRDashboard = () => {
  const { user } = useAuth();
  const [jobRoles, setJobRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedJobRole, setSelectedJobRole] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadJobRoles();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadJobRoles = async () => {
    try {
      setIsLoading(true);
      const response = await jobRoleService.getJobRoles();
      if (response.status === 'success') {
        setJobRoles(response.job_roles || []);
      } else {
        console.error('API returned error:', response);
        showSnackbar('Failed to load job roles', 'error');
      }
    } catch (error) {
      console.error('Error loading job roles:', error);
      showSnackbar('Failed to load job roles', 'error');
    } finally {
      setIsLoading(false);
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

  const handleDeleteJobRole = async (jobRoleId) => {
    if (window.confirm('Are you sure you want to delete this job role?')) {
      try {
        const response = await jobRoleService.deleteJobRole(jobRoleId);
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
    }
    setAnchorEl(null);
    setOpenMenuId(null);
  };

  const handleMenuOpen = (event, jobRoleId) => {
    setAnchorEl(event.currentTarget);
    setOpenMenuId(jobRoleId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setOpenMenuId(null);
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
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Main Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 700,
            color: '#2C3E50',
            mb: 1
          }}
        >
          Job Role Management
        </Typography>
      </Box>

      {/* Job Roles Header with Create Button */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#2C3E50' }}>
          Job Role Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateJobRole}
          sx={{
            backgroundColor: '#4FC3F7',
            borderRadius: 2,
            px: 3,
            '&:hover': {
              backgroundColor: '#29B6F6',
            }
          }}
        >
          + Create Job Role
        </Button>
      </Box>

      {/* Job Roles List */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : jobRoles.length === 0 ? (
        <Box sx={{ 
          textAlign: 'center', 
          py: 8,
          px: 4,
          backgroundColor: '#f8f9fa',
          borderRadius: 4,
          border: '2px dashed #dee2e6'
        }}>
          <Work sx={{ fontSize: 80, color: '#667eea', opacity: 0.7, mb: 3 }} />
          <Typography variant="h5" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
            No job roles yet
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: '500px', mx: 'auto' }}>
            Create your first job role to define confidence level requirements for different positions
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateJobRole}
            size="large"
            sx={{
              backgroundColor: '#4FC3F7',
              borderRadius: 3,
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: '#29B6F6',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(79, 195, 247, 0.3)',
              },
              transition: 'all 0.3s ease'
            }}
          >
            Create Your First Job Role
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {jobRoles.map((jobRole) => {
            const jobRoleInitials = getJobRoleInitials(jobRole.name);
            const avatarColor = getAvatarColor(jobRole.name);
            const confidenceLevels = jobRole.confidence_levels || {};
            
            return (
              <Grid item xs={12} md={6} lg={4} key={jobRole.id}>
                <Card sx={{ 
                  height: '100%', 
                  transition: 'all 0.3s ease',
                  borderRadius: 3,
                  border: '1px solid rgba(102, 126, 234, 0.1)',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 30px rgba(102, 126, 234, 0.15)',
                  }
                }}>
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
                        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                          {jobRole.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {jobRole.description || 'No description'}
                        </Typography>
                      </Box>
                      <IconButton
                        onClick={(e) => handleMenuOpen(e, jobRole.id)}
                        size="small"
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>

                    {/* Confidence Levels */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        Confidence Requirements
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
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

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => handleEditJobRole(jobRoles.find(role => role.id === openMenuId))}>
          <Edit sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem onClick={() => handleDeleteJobRole(openMenuId)}>
          <Delete sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>

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
  );
};

export default HRDashboard;