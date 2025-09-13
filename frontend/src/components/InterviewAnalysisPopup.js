import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Paper,
  Avatar,
  Chip,
  LinearProgress,
  Divider,
  IconButton,
  Tabs,
  Tab,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Close,
  Person,
  Work,
  Schedule,
  TrendingUp,
  TrendingDown,
  Psychology,
  Mic,
  Visibility,
  Gesture,
  CheckCircle,
  Warning,
  Lightbulb,
  Timeline,
  Assessment
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { analyticsService } from '../services/analyticsService';
import { useTheme } from '../contexts/ThemeContext';

const InterviewAnalysisPopup = ({ open, onClose, interviewId }) => {
  const { isDarkMode } = useTheme();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (open && interviewId) {
      loadAnalysisData();
    }
  }, [open, interviewId]);

  const loadAnalysisData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await analyticsService.getInterviewAnalysis(interviewId);
      setAnalysisData(response.data);
    } catch (error) {
      console.error('Error loading analysis data:', error);
      setError('Failed to load interview analysis data');
    } finally {
      setLoading(false);
    }
  };

  const generateSampleData = async () => {
    try {
      setLoading(true);
      setError(null);
      await analyticsService.generateSampleAnalysis(interviewId);
      // Reload the analysis data
      await loadAnalysisData();
    } catch (error) {
      console.error('Error generating sample data:', error);
      setError('Failed to generate sample analysis data');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setAnalysisData(null);
    setError(null);
    setActiveTab(0);
    onClose();
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#F44336';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const renderOverviewTab = () => {
    if (!analysisData) return null;

    const { interview_info, overall_scores } = analysisData;

    return (
      <Box>
        {/* Candidate Info Header */}
        <Paper sx={(theme) => ({ 
          p: 3, 
          mb: 3, 
          background: isDarkMode 
            ? 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)'
            : 'linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%)', 
          color: 'white',
          backgroundColor: theme.palette.background.paper
        })}>
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <Avatar sx={{ width: 80, height: 80, bgcolor: 'rgba(255,255,255,0.2)' }}>
                <Person sx={{ fontSize: 40 }} />
              </Avatar>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {interview_info.candidate_name}
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, mb: 1 }}>
                {interview_info.position}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip 
                  icon={<Schedule />} 
                  label={`${interview_info.duration_minutes} minutes`}
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
                <Chip 
                  icon={<Work />} 
                  label={interview_info.status}
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
                <Chip 
                  icon={<Assessment />} 
                  label={`ID: ${interview_info.id}`}
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Overall Scores */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Typography variant="h6" sx={(theme) => ({ 
                  mb: 2, 
                  color: theme.palette.primary.main 
                })}>
                  Overall Confidence
                </Typography>
                <Typography variant="h2" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.confidence.overall) }}>
                  {overall_scores.confidence.overall}%
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', mt: 1 }}>
                  {getScoreLabel(overall_scores.confidence.overall)}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.confidence.overall} 
                  sx={{ mt: 2, height: 8, borderRadius: 4 }}
                  color={overall_scores.confidence.overall >= 80 ? 'success' : overall_scores.confidence.overall >= 60 ? 'warning' : 'error'}
                />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Typography variant="h6" sx={(theme) => ({ 
                  mb: 2, 
                  color: theme.palette.primary.main 
                })}>
                  Stress Level
                </Typography>
                <Typography variant="h2" sx={{ fontWeight: 'bold', color: getScoreColor(100 - overall_scores.stress_level) }}>
                  {overall_scores.stress_level}%
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', mt: 1 }}>
                  {overall_scores.stress_level < 30 ? 'Low Stress' : overall_scores.stress_level < 60 ? 'Moderate Stress' : 'High Stress'}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.stress_level} 
                  sx={{ mt: 2, height: 8, borderRadius: 4 }}
                  color={overall_scores.stress_level < 30 ? 'success' : overall_scores.stress_level < 60 ? 'warning' : 'error'}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Typography variant="h6" sx={(theme) => ({ 
                  mb: 2, 
                  color: theme.palette.primary.main 
                })}>
                  Performance Rating
                </Typography>
                <Typography variant="h2" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.performance_rating) }}>
                  {overall_scores.performance_rating}/10
                </Typography>
                <Typography variant="body2" sx={{ color: '#666', mt: 1 }}>
                  {overall_scores.performance_rating >= 8 ? 'Outstanding' : overall_scores.performance_rating >= 6 ? 'Good' : 'Needs Work'}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(overall_scores.performance_rating / 10) * 100} 
                  sx={{ mt: 2, height: 8, borderRadius: 4 }}
                  color={overall_scores.performance_rating >= 8 ? 'success' : overall_scores.performance_rating >= 6 ? 'warning' : 'error'}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Confidence Breakdown */}
        <Paper sx={(theme) => ({ 
          p: 3, 
          mb: 3,
          backgroundColor: theme.palette.background.paper
        })}>
          <Typography variant="h6" sx={(theme) => ({ 
            mb: 3, 
            fontWeight: 'bold', 
            color: theme.palette.primary.main 
          })}>
            Confidence Breakdown
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>Voice</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.confidence.voice) }}>
                  {overall_scores.confidence.voice}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.confidence.voice} 
                  sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  color={overall_scores.confidence.voice >= 80 ? 'success' : overall_scores.confidence.voice >= 60 ? 'warning' : 'error'}
                />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>Hand Gestures</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.confidence.hand) }}>
                  {overall_scores.confidence.hand}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.confidence.hand} 
                  sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  color={overall_scores.confidence.hand >= 80 ? 'success' : overall_scores.confidence.hand >= 60 ? 'warning' : 'error'}
                />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>Eye Contact</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.confidence.eye) }}>
                  {overall_scores.confidence.eye}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.confidence.eye} 
                  sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  color={overall_scores.confidence.eye >= 80 ? 'success' : overall_scores.confidence.eye >= 60 ? 'warning' : 'error'}
                />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" sx={{ color: '#666', mb: 1 }}>Overall</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(overall_scores.confidence.overall) }}>
                  {overall_scores.confidence.overall}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={overall_scores.confidence.overall} 
                  sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  color={overall_scores.confidence.overall >= 80 ? 'success' : overall_scores.confidence.overall >= 60 ? 'warning' : 'error'}
                />
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Box>
    );
  };

  const renderTimelineTab = () => {
    if (!analysisData) return null;

    const { timeline_analysis } = analysisData;
    
    // Transform data for the chart
    const chartData = timeline_analysis.time_points.map((timePoint, index) => ({
      timePoint,
      confidence: timeline_analysis.confidence_progression[index],
      stress: timeline_analysis.stress_progression[index],
      emotion: timeline_analysis.emotion_progression[index]
    }));

    return (
      <Box>
        <Typography variant="h6" sx={(theme) => ({ 
          mb: 3, 
          fontWeight: 'bold', 
          color: theme.palette.primary.main 
        })}>
          Interview Timeline Analysis
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
            Confidence & Stress Progression
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timePoint" />
              <YAxis yAxisId="left" domain={[0, 100]} />
              <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
              <Tooltip 
                formatter={(value, name) => [`${value}%`, name]}
                labelFormatter={(label) => `Interview Progress: ${label}`}
              />
              <Legend />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="confidence"
                stackId="1"
                stroke="#4CAF50"
                fill="#4CAF50"
                fillOpacity={0.3}
                name="Confidence"
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey="stress"
                stackId="2"
                stroke="#F44336"
                fill="#F44336"
                fillOpacity={0.3}
                name="Stress"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Paper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold', color: '#667eea' }}>
                Emotion Timeline
              </Typography>
              <List>
                {timeline_analysis.emotion_progression.map((emotion, index) => (
                  <ListItem key={index} sx={{ py: 1 }}>
                    <ListItemIcon>
                      <Psychology sx={{ color: '#667eea' }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={emotion}
                      secondary={`${timeline_analysis.time_points[index]} of interview`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold', color: '#667eea' }}>
                Key Moments
              </Typography>
              <List>
                <ListItem sx={{ py: 1 }}>
                  <ListItemIcon>
                    <TrendingUp sx={{ color: '#4CAF50' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Peak Confidence"
                    secondary={`${Math.max(...timeline_analysis.confidence_progression)}% at ${timeline_analysis.time_points[timeline_analysis.confidence_progression.indexOf(Math.max(...timeline_analysis.confidence_progression))]}`}
                  />
                </ListItem>
                <ListItem sx={{ py: 1 }}>
                  <ListItemIcon>
                    <TrendingDown sx={{ color: '#F44336' }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Highest Stress"
                    secondary={`${Math.max(...timeline_analysis.stress_progression)}% at ${timeline_analysis.time_points[timeline_analysis.stress_progression.indexOf(Math.max(...timeline_analysis.stress_progression))]}`}
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderDetailedTab = () => {
    if (!analysisData) return null;

    const { detailed_metrics } = analysisData;

    return (
      <Box>
        <Typography variant="h6" sx={(theme) => ({ 
          mb: 3, 
          fontWeight: 'bold', 
          color: theme.palette.primary.main 
        })}>
          Detailed Analysis Metrics
        </Typography>
        
        <Grid container spacing={3}>
          {/* Voice Analysis */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Mic sx={(theme) => ({ color: theme.palette.primary.main, mr: 1 })} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Voice Analysis
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Confidence</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.voice_analysis.confidence} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.voice_analysis.confidence >= 80 ? 'success' : detailed_metrics.voice_analysis.confidence >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.voice_analysis.confidence}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Clarity</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.voice_analysis.clarity} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.voice_analysis.clarity >= 80 ? 'success' : detailed_metrics.voice_analysis.clarity >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.voice_analysis.clarity}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Pace</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.voice_analysis.pace} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.voice_analysis.pace >= 80 ? 'success' : detailed_metrics.voice_analysis.pace >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.voice_analysis.pace}%
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ color: '#666' }}>Tone</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.voice_analysis.tone} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.voice_analysis.tone >= 80 ? 'success' : detailed_metrics.voice_analysis.tone >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.voice_analysis.tone}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Facial Analysis */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Visibility sx={(theme) => ({ color: theme.palette.primary.main, mr: 1 })} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Facial Analysis
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Confidence</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.facial_analysis.confidence} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.facial_analysis.confidence >= 80 ? 'success' : detailed_metrics.facial_analysis.confidence >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.facial_analysis.confidence}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Engagement</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.facial_analysis.engagement} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.facial_analysis.engagement >= 80 ? 'success' : detailed_metrics.facial_analysis.engagement >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.facial_analysis.engagement}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Eye Contact</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.facial_analysis.eye_contact} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.facial_analysis.eye_contact >= 80 ? 'success' : detailed_metrics.facial_analysis.eye_contact >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.facial_analysis.eye_contact}%
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ color: '#666' }}>Stress Level</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.facial_analysis.stress_level} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.facial_analysis.stress_level < 30 ? 'success' : detailed_metrics.facial_analysis.stress_level < 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.facial_analysis.stress_level}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Gesture Analysis */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
                : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Gesture sx={(theme) => ({ color: theme.palette.primary.main, mr: 1 })} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Gesture Analysis
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Confidence</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.gesture_analysis.confidence} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.gesture_analysis.confidence >= 80 ? 'success' : detailed_metrics.gesture_analysis.confidence >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.gesture_analysis.confidence}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Hand Movements</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.gesture_analysis.hand_movements} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.gesture_analysis.hand_movements >= 80 ? 'success' : detailed_metrics.gesture_analysis.hand_movements >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.gesture_analysis.hand_movements}%
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#666' }}>Posture</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.gesture_analysis.posture} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.gesture_analysis.posture >= 80 ? 'success' : detailed_metrics.gesture_analysis.posture >= 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.gesture_analysis.posture}%
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ color: '#666' }}>Nervous Gestures</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={detailed_metrics.gesture_analysis.nervous_gestures} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={detailed_metrics.gesture_analysis.nervous_gestures < 30 ? 'success' : detailed_metrics.gesture_analysis.nervous_gestures < 60 ? 'warning' : 'error'}
                  />
                  <Typography variant="body2" sx={{ textAlign: 'right', mt: 0.5 }}>
                    {detailed_metrics.gesture_analysis.nervous_gestures}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderInsightsTab = () => {
    if (!analysisData) return null;

    const { performance_insights } = analysisData;

    return (
      <Box>
        <Typography variant="h6" sx={(theme) => ({ 
          mb: 3, 
          fontWeight: 'bold', 
          color: theme.palette.primary.main 
        })}>
          Performance Insights & Recommendations
        </Typography>
        
        <Grid container spacing={3}>
          {/* Strengths */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1B5E20 0%, #2E7D32 100%)'
                : 'linear-gradient(145deg, #e8f5e8 0%, #f1f8e9 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CheckCircle sx={{ color: '#4CAF50', mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#4CAF50' }}>
                    Strengths
                  </Typography>
                </Box>
                <List>
                  {performance_insights.strengths.map((strength, index) => (
                    <ListItem key={index} sx={{ py: 1 }}>
                      <ListItemIcon>
                        <CheckCircle sx={{ color: '#4CAF50', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText primary={strength} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Areas for Improvement */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #E65100 0%, #FF8F00 100%)'
                : 'linear-gradient(145deg, #fff3e0 0%, #fce4ec 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Warning sx={{ color: '#FF9800', mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    Areas for Improvement
                  </Typography>
                </Box>
                <List>
                  {performance_insights.areas_for_improvement.map((area, index) => (
                    <ListItem key={index} sx={{ py: 1 }}>
                      <ListItemIcon>
                        <Warning sx={{ color: '#FF9800', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText primary={area} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12} md={4}>
            <Card sx={(theme) => ({ 
              height: '100%', 
              background: isDarkMode 
                ? 'linear-gradient(145deg, #1565C0 0%, #0D47A1 100%)'
                : 'linear-gradient(145deg, #e3f2fd 0%, #f3e5f5 100%)',
              backgroundColor: theme.palette.background.paper
            })}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Lightbulb sx={{ color: '#2196F3', mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#2196F3' }}>
                    Recommendations
                  </Typography>
                </Box>
                <List>
                  {performance_insights.recommendations.map((recommendation, index) => (
                    <ListItem key={index} sx={{ py: 1 }}>
                      <ListItemIcon>
                        <Lightbulb sx={{ color: '#2196F3', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText primary={recommendation} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          minHeight: '80vh'
        }
      }}
    >
      <DialogTitle sx={(theme) => ({ 
        background: isDarkMode 
          ? 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)'
          : 'linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%)', 
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      })}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Assessment sx={{ mr: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Interview Analysis Report
          </Typography>
        </Box>
        <IconButton onClick={handleClose} sx={{ color: 'white' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
            <CircularProgress size={60} />
          </Box>
        ) : error ? (
          <Box sx={{ p: 3 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        ) : analysisData ? (
          <Box>
            <Tabs 
              value={activeTab} 
              onChange={(e, newValue) => setActiveTab(newValue)}
              sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                px: 3,
                pt: 2
              }}
            >
              <Tab label="Overview" icon={<Assessment />} />
              <Tab label="Timeline" icon={<Timeline />} />
              <Tab label="Detailed Metrics" icon={<Psychology />} />
              <Tab label="Insights" icon={<Lightbulb />} />
            </Tabs>

            <Box sx={{ p: 3 }}>
              {activeTab === 0 && renderOverviewTab()}
              {activeTab === 1 && renderTimelineTab()}
              {activeTab === 2 && renderDetailedTab()}
              {activeTab === 3 && renderInsightsTab()}
            </Box>
          </Box>
        ) : null}
      </DialogContent>

      <DialogActions sx={{ p: 3, background: '#f8f9ff' }}>
        {analysisData && analysisData.overall_scores?.confidence?.overall === 0 && (
          <Button 
            onClick={generateSampleData} 
            variant="outlined" 
            sx={{ 
              borderColor: '#667eea',
              color: '#667eea',
              '&:hover': {
                borderColor: '#5a6fd8',
                backgroundColor: 'rgba(102, 126, 234, 0.08)'
              }
            }}
          >
            Generate Sample Data
          </Button>
        )}
        <Button 
          onClick={handleClose} 
          variant="contained" 
          sx={(theme) => ({ 
            background: isDarkMode 
              ? 'linear-gradient(135deg, #1565C0 0%, #0D47A1 100%)'
              : 'linear-gradient(135deg, #4FC3F7 0%, #29B6F6 100%)',
            '&:hover': {
              background: isDarkMode 
                ? 'linear-gradient(135deg, #0D47A1 0%, #1A237E 100%)'
                : 'linear-gradient(135deg, #29B6F6 0%, #1976D2 100%)'
            }
          })}
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InterviewAnalysisPopup;
