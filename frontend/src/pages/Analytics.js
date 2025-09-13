import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  IconButton,
  Select,
  FormControl,
  InputLabel,
  Button,
  MenuItem,
  CircularProgress,
  Alert,
  TextField,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  People,
  Assessment,
  Visibility,
  FileDownload,
  ShowChart,
  FilterList,
  ExpandMore,
  Search,
  Clear
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { analyticsService } from '../services/analyticsService';
import { jobRoleService } from '../services/jobRoleService';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7days');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // New state for enhanced analytics
  const [candidates, setCandidates] = useState([]);
  const [jobRoles, setJobRoles] = useState([]);
  const [filters, setFilters] = useState({
    min_confidence: 0,
    max_confidence: 100,
    min_stress: 0,
    max_stress: 100,
    job_role_id: '',
    status: '',
    date_from: '',
    date_to: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [analyticsData, setAnalyticsData] = useState({
    overview: {
      totalSessions: 0,
      totalCandidates: 0,
      trends: {
        sessions: 0,
        candidates: 0
      }
    },
    sessionTrends: [],
    emotionDistribution: [],
    topCandidates: [],
    candidateTrends: []
  });

  useEffect(() => {
    loadAnalyticsData();
    loadJobRoles();
  }, [timeRange]);

  useEffect(() => {
    loadCandidates();
  }, [filters]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load overview data using the analytics service
      const overviewResponse = await analyticsService.getOverview();
      const overviewData = overviewResponse.data;

      // Load session trends data
      const trendsResponse = await analyticsService.getSessionTrends(timeRange);
      const trendsData = trendsResponse.data;

      // Load emotion distribution data
      const emotionResponse = await analyticsService.getEmotionDistribution();
      const emotionData = emotionResponse.data;

      // Load candidate trends data
      const candidateTrendsResponse = await analyticsService.getCandidateTrends();
      const candidateTrendsData = candidateTrendsResponse.data;

      setAnalyticsData({
        overview: {
          totalSessions: overviewData.totalSessions || 0,
          totalCandidates: overviewData.totalCandidates || 0,
          trends: {
            sessions: overviewData.trends?.sessions || 0,
            candidates: overviewData.trends?.candidates || 0
          }
        },
        sessionTrends: trendsData.labels?.map((label, index) => ({
          date: label,
          sessions: trendsData.sessions[index] || 0
        })) || [],
        emotionDistribution: emotionData.emotions || [
          { name: 'Confident', value: 35, color: '#4CAF50' },
          { name: 'Neutral', value: 40, color: '#2196F3' },
          { name: 'Nervous', value: 20, color: '#FF9800' },
          { name: 'Stressed', value: 5, color: '#F44336' },
        ],
        topCandidates: [], // This will be populated by the candidates table
        candidateTrends: candidateTrendsData.candidates || []
      });
    } catch (error) {
      console.error('Error loading analytics data:', error);
      setError('Failed to load analytics data. Using fallback data.');
      
      // Fallback data with only the required fields (no average score or completion rate)
      setAnalyticsData({
        overview: {
          totalSessions: 0,
          totalCandidates: 0,
          trends: {
            sessions: 0,
            candidates: 0
          }
        },
        sessionTrends: [
          { date: 'Mon', sessions: 0 },
          { date: 'Tue', sessions: 0 },
          { date: 'Wed', sessions: 0 },
          { date: 'Thu', sessions: 0 },
          { date: 'Fri', sessions: 0 },
          { date: 'Sat', sessions: 0 },
          { date: 'Sun', sessions: 0 }
        ],
        emotionDistribution: [
          { name: 'Confident', value: 0, color: '#4CAF50' },
          { name: 'Neutral', value: 0, color: '#2196F3' },
          { name: 'Nervous', value: 0, color: '#FF9800' },
          { name: 'Stressed', value: 0, color: '#F44336' },
        ],
        topCandidates: [],
        candidateTrends: []
      });
    } finally {
      setLoading(false);
    }
  };

  const loadJobRoles = async () => {
    try {
      const response = await jobRoleService.getJobRoles();
      setJobRoles(response.data || []);
    } catch (error) {
      console.error('Error loading job roles:', error);
    }
  };

  const loadCandidates = async () => {
    try {
      const response = await analyticsService.getCandidates(filters);
      setCandidates(response.data || []);
    } catch (error) {
      console.error('Error loading candidates:', error);
    }
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      min_confidence: 0,
      max_confidence: 100,
      min_stress: 0,
      max_stress: 100,
      job_role_id: '',
      status: '',
      date_from: '',
      date_to: ''
    });
    setSearchTerm('');
  };

  const filteredCandidates = candidates.filter(candidate => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        candidate.candidate_name.toLowerCase().includes(searchLower) ||
        candidate.position.toLowerCase().includes(searchLower) ||
        candidate.candidate_nic.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const StatCard = ({ title, value, trend, icon, color }) => (
    <Card sx={{
      height: 160,
      background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
      border: `1px solid ${color}20`,
      borderRadius: 3,
      transition: 'all 0.3s ease',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: `0 8px 25px ${color}20`,
      }
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{
            p: 1.5,
            borderRadius: 2,
            backgroundColor: `${color}15`,
            display: 'flex',
            alignItems: 'center',
          }}>
            {icon}
          </Box>
          <Chip
            label={trend > 0 ? `+${trend}%` : `${trend}%`}
            size="small"
            icon={trend > 0 ? <TrendingUp /> : <TrendingDown />}
            color={trend > 0 ? "success" : "error"}
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5, color: color }}>
          {value}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress size={60} sx={{ color: '#667eea' }} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 6 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box>
            <Typography 
              variant="h3" 
              sx={(theme) => ({ 
                mb: 1, 
                color: theme.palette.text.primary,
                fontWeight: 700,
                fontSize: '2.5rem'
              })}
            >
              Analytics Dashboard
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                label="Time Range"
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <MenuItem value="7days">Last 7 days</MenuItem>
                <MenuItem value="30days">Last 30 days</MenuItem>
                <MenuItem value="90days">Last 3 months</MenuItem>
                <MenuItem value="1year">Last year</MenuItem>
              </Select>
            </FormControl>
            <Button
              variant="outlined"
              startIcon={<FileDownload />}
              sx={{ borderRadius: 3 }}
            >
              Export
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {error} - Showing fallback data
          </Alert>
        )}
      </Box>

      {/* Overview Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={6}>
          <StatCard
            title="Total Sessions"
            value={analyticsData.overview.totalSessions}
            trend={analyticsData.overview.trends.sessions}
            icon={<Assessment sx={{ color: '#667eea' }} />}
            color="#667eea"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={6}>
          <StatCard
            title="Total Candidates"
            value={analyticsData.overview.totalCandidates}
            trend={analyticsData.overview.trends.candidates}
            icon={<People sx={{ color: '#4CAF50' }} />}
            color="#4CAF50"
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={4} sx={{ mb: 4 }}>
        {/* Session Trends Chart */}
        <Grid item xs={12}>
          <Paper sx={(theme) => ({
            p: 4,
            borderRadius: 4,
            background: theme.palette.mode === 'dark' 
              ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
              : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
            backgroundColor: theme.palette.background.paper,
            boxShadow: theme.palette.mode === 'dark'
              ? '0 8px 32px rgba(0, 0, 0, 0.3)'
              : '0 8px 32px rgba(102, 126, 234, 0.1)',
            border: theme.palette.mode === 'dark'
              ? '1px solid rgba(255, 255, 255, 0.1)'
              : '1px solid rgba(102, 126, 234, 0.1)',
          })}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Latest 3 Candidates: Stress & Confidence Trends
              </Typography>
              <ShowChart sx={{ color: '#667eea' }} />
            </Box>
            {analyticsData.candidateTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={(() => {
                  // Combine all candidate data into a single dataset
                  const timePoints = analyticsData.candidateTrends[0]?.time_points || [];
                  return timePoints.map((timePoint, i) => {
                    const dataPoint = { timePoint };
                    analyticsData.candidateTrends.forEach((candidate, candidateIndex) => {
                      dataPoint[`${candidate.candidate_name} - Confidence`] = candidate.confidence_progression[i] || 0;
                      dataPoint[`${candidate.candidate_name} - Stress`] = candidate.stress_progression[i] || 0;
                    });
                    return dataPoint;
                  });
                })()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timePoint" 
                    tick={{ fontSize: 12 }}
                    tickLine={{ stroke: '#666' }}
                  />
                  <YAxis 
                    yAxisId="confidence"
                    orientation="left"
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    tickLine={{ stroke: '#666' }}
                    label={{ value: 'Confidence %', angle: -90, position: 'insideLeft' }}
                  />
                  <YAxis 
                    yAxisId="stress"
                    orientation="right"
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    tickLine={{ stroke: '#666' }}
                    label={{ value: 'Stress %', angle: 90, position: 'insideRight' }}
                  />
                  <Tooltip 
                    formatter={(value, name) => [`${value}%`, name]}
                    labelFormatter={(label) => `Interview Progress: ${label}`}
                  />
                  <Legend />
                  {analyticsData.candidateTrends.map((candidate, index) => {
                    const colors = ['#4CAF50', '#2196F3', '#FF9800'];
                    const color = colors[index % colors.length];
                    
                    return (
                      <g key={candidate.candidate_name}>
                        <Line
                          yAxisId="confidence"
                          type="monotone"
                          dataKey={`${candidate.candidate_name} - Confidence`}
                          stroke={color}
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          name={`${candidate.candidate_name} - Confidence`}
                        />
                        <Line
                          yAxisId="stress"
                          type="monotone"
                          dataKey={`${candidate.candidate_name} - Stress`}
                          stroke={color}
                          strokeWidth={2}
                          name={`${candidate.candidate_name} - Stress`}
                        />
                      </g>
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ 
                height: 300, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#666',
                fontSize: '1.1rem'
              }}>
                No candidate data available
              </Box>
            )}
          </Paper>
        </Grid>

      </Grid>

      {/* Enhanced Candidate Analytics Table */}
      <Paper sx={(theme) => ({
        p: 4,
        borderRadius: 4,
        background: theme.palette.mode === 'dark' 
          ? 'linear-gradient(145deg, #1e1e1e 0%, #2a2a2a 100%)'
          : 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
        backgroundColor: theme.palette.background.paper,
        boxShadow: theme.palette.mode === 'dark'
          ? '0 8px 32px rgba(0, 0, 0, 0.3)'
          : '0 8px 32px rgba(102, 126, 234, 0.1)',
        border: theme.palette.mode === 'dark'
          ? '1px solid rgba(255, 255, 255, 0.1)'
          : '1px solid rgba(102, 126, 234, 0.1)',
      })}>
        {/* Header with Search and Filters */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" sx={(theme) => ({ fontWeight: 'bold', color: theme.palette.text.primary })}>
            Candidate Interview Analytics
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Search candidates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={(theme) => ({ mr: 1, color: theme.palette.text.secondary })} />
              }}
              sx={{ minWidth: 250 }}
            />
            <Button
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => setShowFilters(!showFilters)}
              sx={{ borderRadius: 2 }}
            >
              Filters
            </Button>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={clearFilters}
              sx={{ borderRadius: 2 }}
            >
              Clear
            </Button>
          </Box>
        </Box>

        {/* Advanced Filters */}
        {showFilters && (
          <Accordion expanded={showFilters} sx={{ mb: 3, boxShadow: 'none' }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Advanced Filters
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                    Confidence Score Range
                  </Typography>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={[filters.min_confidence, filters.max_confidence]}
                      onChange={(e, newValue) => {
                        setFilters(prev => ({
                          ...prev,
                          min_confidence: newValue[0],
                          max_confidence: newValue[1]
                        }));
                      }}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ color: '#4CAF50' }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      <Typography variant="caption">{filters.min_confidence}%</Typography>
                      <Typography variant="caption">{filters.max_confidence}%</Typography>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
                    Stress Level Range
                  </Typography>
                  <Box sx={{ px: 2 }}>
                    <Slider
                      value={[filters.min_stress, filters.max_stress]}
                      onChange={(e, newValue) => {
                        setFilters(prev => ({
                          ...prev,
                          min_stress: newValue[0],
                          max_stress: newValue[1]
                        }));
                      }}
                      valueLabelDisplay="auto"
                      min={0}
                      max={100}
                      sx={{ color: '#F44336' }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      <Typography variant="caption">{filters.min_stress}%</Typography>
                      <Typography variant="caption">{filters.max_stress}%</Typography>
                    </Box>
                  </Box>
                </Grid>

                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Job Role</InputLabel>
                    <Select
                      value={filters.job_role_id}
                      onChange={(e) => handleFilterChange('job_role_id', e.target.value)}
                      label="Job Role"
                    >
                      <MenuItem value="">All Roles</MenuItem>
                      {jobRoles.map((role) => (
                        <MenuItem key={role.id} value={role.id}>
                          {role.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filters.status}
                      onChange={(e) => handleFilterChange('status', e.target.value)}
                      label="Status"
                    >
                      <MenuItem value="">All Status</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="active">Active</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Enhanced Candidate Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'rgba(102, 126, 234, 0.05)' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Candidate</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Position</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Confidence Scores</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Stress Level</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Session Duration</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Interview Date</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="center" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCandidates.map((candidate) => (
                <TableRow key={candidate.interview_id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar
                        sx={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          mr: 2,
                          width: 40,
                          height: 40,
                          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
                        }}
                      >
                        {candidate.candidate_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {candidate.candidate_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {candidate.candidate_nic}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={candidate.position}
                      size="small"
                      sx={{ 
                        bgcolor: 'rgba(33, 150, 243, 0.1)', 
                        color: '#1976d2',
                        fontWeight: 600
                      }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                        <Chip 
                          label={`V:${candidate.confidence_scores.voice}%`} 
                          size="small" 
                          sx={{ bgcolor: 'rgba(76, 175, 80, 0.1)', color: '#388E3C', fontSize: '0.7rem' }}
                        />
                        <Chip 
                          label={`H:${candidate.confidence_scores.hand}%`} 
                          size="small" 
                          sx={{ bgcolor: 'rgba(33, 150, 243, 0.1)', color: '#1976D2', fontSize: '0.7rem' }}
                        />
                        <Chip 
                          label={`E:${candidate.confidence_scores.eye}%`} 
                          size="small" 
                          sx={{ bgcolor: 'rgba(255, 152, 0, 0.1)', color: '#F57C00', fontSize: '0.7rem' }}
                        />
                      </Box>
                      <Typography variant="caption" sx={(theme) => ({ fontWeight: 'bold', color: theme.palette.success.main })}>
                        Overall: {candidate.confidence_scores.overall}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <LinearProgress
                        variant="determinate"
                        value={candidate.stress_level}
                        sx={{
                          width: 60,
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: 'rgba(244, 67, 54, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: candidate.stress_level > 70 ? '#F44336' : 
                                           candidate.stress_level > 40 ? '#FF9800' : '#4CAF50'
                          }
                        }}
                      />
                      <Typography variant="caption" sx={{ ml: 1, fontWeight: 'bold' }}>
                        {candidate.stress_level}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {candidate.duration_minutes} min
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(candidate.created_at).toLocaleDateString()}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(candidate.created_at).toLocaleTimeString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={candidate.status}
                      size="small"
                      color={
                        candidate.status === 'completed' ? 'success' :
                        candidate.status === 'active' ? 'warning' : 'default'
                      }
                      sx={{ fontWeight: 600 }}
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="View Details">
                      <IconButton size="small" sx={{ color: '#667eea' }}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {filteredCandidates.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No candidates found matching your criteria
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try adjusting your filters or search terms
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Analytics;
