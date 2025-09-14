import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  CircularProgress,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Visibility,
  RecordVoiceOver,
  PanTool,
  Close,
  Assessment,
  Refresh
} from '@mui/icons-material';
import { interviewScoringService } from '../services/interviewScoringService';

const InterviewScoreDisplay = ({ sessionId, jobRoleId, open, onClose, preloadedScores }) => {
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open && sessionId) {
      // Use preloaded scores if available, otherwise load them
      if (preloadedScores) {
        console.log('📊 Using preloaded scores:', preloadedScores);
        if (preloadedScores === 'no_data') {
          setError('Candidate Analysis Data Empty');
        } else {
          setScores(preloadedScores);
        }
      } else if (!scores) {
        loadScores();
      }
    }
  }, [open, sessionId, preloadedScores, scores]);

  const loadScores = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('📊 Loading scores for sessionId:', sessionId);
      const finalScores = await interviewScoringService.getFinalScores(sessionId);
      console.log('✅ Loaded scores:', finalScores);
      setScores(finalScores.final_scores);
    } catch (err) {
      console.error('❌ Error loading scores:', err);
      // Check if it's a 404 error (no analysis data available)
      if (err.message && err.message.includes('404')) {
        setError('Candidate Analysis Data Empty');
      } else {
        setError('Failed to load interview scores');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔄 Recalculating scores for sessionId:', sessionId, 'jobRoleId:', jobRoleId);
      const result = await interviewScoringService.processAndSaveFinalScores(sessionId, jobRoleId);
      console.log('✅ Recalculation successful:', result);
      setScores(result.final_scores);
    } catch (err) {
      console.error('❌ Error recalculating scores:', err);
      // Check if it's a 404 error (no analysis data available)
      if (err.message && err.message.includes('404')) {
        setError('Candidate Analysis Data Empty');
      } else {
        setError('Failed to recalculate scores');
      }
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50'; // Green
    if (score >= 60) return '#8BC34A'; // Light Green
    if (score >= 40) return '#FF9800'; // Orange
    if (score >= 20) return '#FF5722'; // Red Orange
    return '#F44336'; // Red
  };

  const getStressColor = (stress) => {
    if (stress <= 20) return '#4CAF50'; // Green (low stress is good)
    if (stress <= 40) return '#8BC34A'; // Light Green
    if (stress <= 60) return '#FF9800'; // Orange
    if (stress <= 80) return '#FF5722'; // Red Orange
    return '#F44336'; // Red
  };

  const ScoreCard = ({ title, score, icon, color, subtitle }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            backgroundColor: `${color}20`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mr: 2
          }}>
            {icon}
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {title}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {subtitle}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="h4" sx={{ fontWeight: 700, color }}>
              {score.toFixed(1)}%
            </Typography>
            <Chip 
              label={score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : score >= 40 ? 'Fair' : 'Poor'}
              size="small"
              sx={{ 
                backgroundColor: `${color}20`,
                color: color,
                fontWeight: 600
              }}
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: `${color}20`,
              '& .MuiLinearProgress-bar': {
                backgroundColor: color,
                borderRadius: 4
              }
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );

  const ComponentBreakdown = ({ component, data, weight }) => (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {component.replace('_', ' ').toUpperCase()}
          </Typography>
          <Chip 
            label={`${weight}% Weight`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
        
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Component Score
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 600, color: getScoreColor(data.percentage) }}>
              {data.percentage.toFixed(1)}%
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Weighted Score
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 600, color: 'primary.main' }}>
              {data.weighted_score.toFixed(2)}
            </Typography>
          </Grid>
        </Grid>
        
        <LinearProgress
          variant="determinate"
          value={data.percentage}
          sx={{
            height: 6,
            borderRadius: 3,
            mt: 2,
            backgroundColor: `${getScoreColor(data.percentage)}20`,
            '& .MuiLinearProgress-bar': {
              backgroundColor: getScoreColor(data.percentage),
              borderRadius: 3
            }
          }}
        />
      </CardContent>
    </Card>
  );

  if (loading && !scores) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Interview Score Analysis</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Loading interview scores...
            </Typography>
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Assessment sx={{ mr: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Interview Score Analysis
          </Typography>
        </Box>
        <Box>
          <Tooltip title="Recalculate Scores">
            <IconButton onClick={handleRecalculate} sx={{ color: 'white', mr: 1 }}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <IconButton onClick={onClose} sx={{ color: 'white' }}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {scores && (
          <>
            {/* Overall Scores */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={6}>
                <ScoreCard
                  title="Overall Confidence"
                  score={scores.confidence.overall_confidence}
                  icon={<TrendingUp sx={{ color: getScoreColor(scores.confidence.overall_confidence) }} />}
                  color={getScoreColor(scores.confidence.overall_confidence)}
                  subtitle={scores.analysis_summary.confidence_level}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <ScoreCard
                  title="Overall Stress"
                  score={scores.stress.overall_stress}
                  icon={<Psychology sx={{ color: getStressColor(scores.stress.overall_stress) }} />}
                  color={getStressColor(scores.stress.overall_stress)}
                  subtitle={scores.analysis_summary.stress_level}
                />
              </Grid>
            </Grid>

            {/* Component Breakdown */}
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              Component Breakdown
            </Typography>
            
            <ComponentBreakdown
              component="Hand Confidence"
              data={scores.confidence.hand_confidence}
              weight={scores.analysis_summary.job_weights?.hand_confidence || 33.33}
            />
            
            <ComponentBreakdown
              component="Eye Confidence"
              data={scores.confidence.eye_confidence}
              weight={scores.analysis_summary.job_weights?.eye_confidence || 33.33}
            />
            
            <ComponentBreakdown
              component="Voice Confidence"
              data={scores.confidence.voice_confidence}
              weight={scores.analysis_summary.job_weights?.voice_confidence || 33.33}
            />

            {/* Analysis Summary */}
            <Card sx={{ mt: 3, backgroundColor: 'background.paper' }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                  Analysis Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Total Records
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {scores.confidence.total_records}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Stress Records
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {scores.stress.stress_records}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Calculated At
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {new Date(scores.calculated_at).toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Job Role
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {scores.analysis_summary.job_role_name || 'Unknown'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence Level
                    </Typography>
                    <Chip 
                      label={scores.analysis_summary.confidence_level}
                      color={scores.confidence.overall_confidence >= 60 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={onClose} variant="outlined">
          Close
        </Button>
        <Button 
          onClick={handleRecalculate} 
          variant="contained"
          startIcon={<Refresh />}
          disabled={loading}
        >
          {loading ? 'Recalculating...' : 'Recalculate Scores'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InterviewScoreDisplay;
