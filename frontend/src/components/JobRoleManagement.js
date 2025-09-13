import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Slider,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider
} from '@mui/material';
import {
  Mic,
  Gesture,
  Visibility,
  Work,
  TrendingUp
} from '@mui/icons-material';
import { jobRoleService } from '../services/jobRoleService';
import { toast } from 'react-toastify';

const JobRoleManagement = ({ open, onClose, onSuccess, mode = 'create', jobRole = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    confidence_levels: {
      voice_confidence: 20,
      hand_confidence: 30,
      eye_confidence: 50
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [jobType, setJobType] = useState('');

  // Predefined job types with default confidence levels
  const jobTypes = [
    { value: 'software_engineer', label: 'Software Engineer', icon: '💻' },
    { value: 'data_scientist', label: 'Data Scientist', icon: '📊' },
    { value: 'product_manager', label: 'Product Manager', icon: '📋' },
    { value: 'designer', label: 'UI/UX Designer', icon: '🎨' },
    { value: 'sales', label: 'Sales Representative', icon: '💼' },
    { value: 'marketing', label: 'Marketing Specialist', icon: '📢' },
    { value: 'custom', label: 'Custom Role', icon: '⚙️' }
  ];

  useEffect(() => {
    if (mode === 'edit' && jobRole) {
      setFormData({
        name: jobRole.name || '',
        description: jobRole.description || '',
        confidence_levels: jobRole.confidence_levels || {
          voice_confidence: 20,
          hand_confidence: 30,
          eye_confidence: 50
        }
      });
    } else {
      // Reset form for create mode
      setFormData({
        name: '',
        description: '',
        confidence_levels: {
          voice_confidence: 20,
          hand_confidence: 30,
          eye_confidence: 50
        }
      });
      setJobType('');
    }
    setErrors({});
  }, [open, mode, jobRole]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleConfidenceChange = (type, value) => {
    const newConfidenceLevels = { ...formData.confidence_levels };
    newConfidenceLevels[type] = value;
    
    // Auto-calculate eye confidence if voice and hand are set
    if (type !== 'eye_confidence') {
      const voice = type === 'voice_confidence' ? value : newConfidenceLevels.voice_confidence;
      const hand = type === 'hand_confidence' ? value : newConfidenceLevels.hand_confidence;
      const eye = jobRoleService.calculateEyeConfidence(voice, hand);
      newConfidenceLevels.eye_confidence = eye;
    }
    
    setFormData(prev => ({
      ...prev,
      confidence_levels: newConfidenceLevels
    }));
  };

  const handleJobTypeChange = (selectedJobType) => {
    setJobType(selectedJobType);
    
    if (selectedJobType !== 'custom') {
      const defaultLevels = jobRoleService.getDefaultConfidenceLevels(selectedJobType);
      setFormData(prev => ({
        ...prev,
        confidence_levels: defaultLevels
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Job role name is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    const validation = jobRoleService.validateConfidenceLevels(formData.confidence_levels);
    if (!validation.isValid) {
      newErrors.confidence_levels = validation.message;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      let response;
      if (mode === 'create') {
        response = await jobRoleService.createJobRole(formData);
      } else {
        response = await jobRoleService.updateJobRole(jobRole.id, formData);
      }
      
      if (response.status === 'success') {
        toast.success(mode === 'create' ? 'Job role created successfully!' : 'Job role updated successfully!');
        onSuccess();
      } else {
        toast.error(response.message || 'Operation failed');
      }
    } catch (error) {
      console.error('Error saving job role:', error);
      toast.error('Failed to save job role');
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalConfidence = () => {
    const { voice_confidence, hand_confidence, eye_confidence } = formData.confidence_levels;
    return voice_confidence + hand_confidence + eye_confidence;
  };

  const getConfidenceColor = (value) => {
    if (value < 20) return 'error';
    if (value < 40) return 'warning';
    return 'success';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Work />
          {mode === 'create' ? 'Create New Job Role' : 'Edit Job Role'}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          {/* Job Type Selection */}
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Job Type</InputLabel>
            <Select
              value={jobType}
              onChange={(e) => handleJobTypeChange(e.target.value)}
              label="Job Type"
              disabled={mode === 'edit'}
            >
              {jobTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>{type.icon}</span>
                    {type.label}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Basic Information */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Job Role Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                error={!!errors.name}
                helperText={errors.name}
                placeholder="e.g., Software Engineer, Data Scientist"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                error={!!errors.description}
                helperText={errors.description}
                multiline
                rows={3}
                placeholder="Describe the role and its key responsibilities..."
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Confidence Level Configuration */}
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp />
            Confidence Level Requirements
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Set the required confidence levels for this job role. The total must equal 100%.
          </Typography>

          {/* Total Confidence Display */}
          <Box sx={{ mb: 3 }}>
            <Alert 
              severity={getTotalConfidence() === 100 ? 'success' : 'warning'}
              sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
            >
              <Typography variant="body2">
                Total Confidence: <strong>{getTotalConfidence()}%</strong>
                {getTotalConfidence() !== 100 && ' (Must equal 100%)'}
              </Typography>
            </Alert>
          </Box>

          {/* Confidence Level Sliders */}
          <Grid container spacing={3}>
            {/* Voice Confidence */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Mic sx={{ mr: 1, color: '#2196F3' }} />
                    <Typography variant="h6">Voice Confidence</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Communication and speaking confidence
                  </Typography>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={formData.confidence_levels.voice_confidence}
                      onChange={(e, value) => handleConfidenceChange('voice_confidence', value)}
                      min={0}
                      max={100}
                      step={5}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' }
                      ]}
                      valueLabelDisplay="auto"
                      color="primary"
                    />
                  </Box>
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Chip 
                      label={`${formData.confidence_levels.voice_confidence}%`} 
                      color={getConfidenceColor(formData.confidence_levels.voice_confidence)}
                      size="large"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Hand Confidence */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Gesture sx={{ mr: 1, color: '#9C27B0' }} />
                    <Typography variant="h6">Hand Confidence</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Gesture and body language confidence
                  </Typography>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={formData.confidence_levels.hand_confidence}
                      onChange={(e, value) => handleConfidenceChange('hand_confidence', value)}
                      min={0}
                      max={100}
                      step={5}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' }
                      ]}
                      valueLabelDisplay="auto"
                      color="secondary"
                    />
                  </Box>
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Chip 
                      label={`${formData.confidence_levels.hand_confidence}%`} 
                      color={getConfidenceColor(formData.confidence_levels.hand_confidence)}
                      size="large"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Eye Confidence */}
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Visibility sx={{ mr: 1, color: '#4CAF50' }} />
                    <Typography variant="h6">Eye Confidence</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Eye contact and visual engagement
                  </Typography>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={formData.confidence_levels.eye_confidence}
                      onChange={(e, value) => handleConfidenceChange('eye_confidence', value)}
                      min={0}
                      max={100}
                      step={5}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' }
                      ]}
                      valueLabelDisplay="auto"
                      color="success"
                    />
                  </Box>
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Chip 
                      label={`${formData.confidence_levels.eye_confidence}%`} 
                      color={getConfidenceColor(formData.confidence_levels.eye_confidence)}
                      size="large"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Error Display */}
          {errors.confidence_levels && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {errors.confidence_levels}
            </Alert>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={isLoading || getTotalConfidence() !== 100}
          sx={{
            backgroundColor: '#4FC3F7',
            '&:hover': {
              backgroundColor: '#29B6F6',
            }
          }}
        >
          {isLoading ? 'Saving...' : (mode === 'create' ? 'Create Job Role' : 'Update Job Role')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default JobRoleManagement;
