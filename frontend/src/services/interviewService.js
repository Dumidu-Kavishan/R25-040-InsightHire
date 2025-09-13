import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include user ID
api.interceptors.request.use((config) => {
  // Get user from localStorage or context
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (user && user.uid) {
    config.params = { ...config.params, userId: user.uid };
  }
  return config;
});

// ==================== INTERVIEW MANAGEMENT ====================

export const createInterview = async (interviewData) => {
  try {
    console.log('🎯 Creating interview:', interviewData);
    const response = await api.post('/interviews', interviewData);
    
    if (response.data.status === 'success') {
      console.log('✅ Interview created successfully:', response.data.interview);
      return {
        success: true,
        data: response.data.interview,
        candidate: response.data.candidate
      };
    } else {
      console.error('❌ Failed to create interview:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to create interview'
      };
    }
  } catch (error) {
    console.error('❌ Error creating interview:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

export const getInterviews = async () => {
  try {
    console.log('📋 Fetching interviews...');
    const response = await api.get('/interviews');
    
    if (response.data.status === 'success') {
      console.log('✅ Interviews fetched successfully:', response.data.interviews.length, 'interviews');
      return {
        success: true,
        data: response.data.interviews || []
      };
    } else {
      console.error('❌ Failed to fetch interviews:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to fetch interviews'
      };
    }
  } catch (error) {
    console.error('❌ Error fetching interviews:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error',
      data: []
    };
  }
};

export const getInterview = async (interviewId) => {
  try {
    console.log('🔍 Fetching interview:', interviewId);
    const response = await api.get(`/interviews/${interviewId}`);
    
    if (response.data.status === 'success') {
      console.log('✅ Interview fetched successfully:', response.data.interview);
      return {
        success: true,
        data: response.data.interview
      };
    } else {
      console.error('❌ Failed to fetch interview:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Interview not found'
      };
    }
  } catch (error) {
    console.error('❌ Error fetching interview:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

export const startInterview = async (interviewId) => {
  try {
    console.log('▶️ Starting interview:', interviewId);
    const response = await api.post(`/interviews/${interviewId}/start`);
    
    if (response.data.status === 'success') {
      console.log('✅ Interview started successfully');
      return {
        success: true,
        data: response.data
      };
    } else {
      console.error('❌ Failed to start interview:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to start interview'
      };
    }
  } catch (error) {
    console.error('❌ Error starting interview:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

export const stopInterview = async (interviewId, data = {}) => {
  try {
    console.log('⏹️ Stopping interview:', interviewId);
    const response = await api.post(`/interviews/${interviewId}/stop`, data);
    
    if (response.data.status === 'success') {
      console.log('✅ Interview stopped successfully');
      return {
        success: true,
        data: response.data
      };
    } else {
      console.error('❌ Failed to stop interview:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to stop interview'
      };
    }
  } catch (error) {
    console.error('❌ Error stopping interview:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

// ==================== ANALYSIS & RESULTS ====================

export const saveAnalysisData = async (interviewId, analysisData) => {
  try {
    console.log('💾 Saving analysis data for interview:', interviewId);
    const response = await api.post(`/interviews/${interviewId}/analysis`, analysisData);
    
    if (response.data.status === 'success') {
      console.log('✅ Analysis data saved successfully');
      return {
        success: true,
        data: response.data
      };
    } else {
      console.error('❌ Failed to save analysis data:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to save analysis data'
      };
    }
  } catch (error) {
    console.error('❌ Error saving analysis data:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

export const getInterviewAnalysis = async (interviewId) => {
  try {
    console.log('📊 Fetching interview analysis:', interviewId);
    const response = await api.get(`/interviews/${interviewId}/analysis`);
    
    if (response.data.status === 'success') {
      console.log('✅ Analysis data fetched successfully');
      return {
        success: true,
        data: response.data.analysis || []
      };
    } else {
      console.error('❌ Failed to fetch analysis data:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to fetch analysis data',
        data: []
      };
    }
  } catch (error) {
    console.error('❌ Error fetching analysis data:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error',
      data: []
    };
  }
};

export const getInterviewSummary = async (interviewId) => {
  try {
    console.log('📈 Fetching interview summary:', interviewId);
    const response = await api.get(`/interviews/${interviewId}/summary`);
    
    if (response.data.status === 'success') {
      console.log('✅ Interview summary fetched successfully');
      return {
        success: true,
        data: response.data.summary
      };
    } else {
      console.error('❌ Failed to fetch interview summary:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to fetch interview summary'
      };
    }
  } catch (error) {
    console.error('❌ Error fetching interview summary:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error'
    };
  }
};

// ==================== REAL-TIME ANALYSIS ====================

export const getRealtimeAnalysis = async (interviewId) => {
  try {
    console.log('🔄 Fetching real-time analysis:', interviewId);
    const response = await api.get(`/interviews/${interviewId}/realtime-analysis`);
    
    if (response.data.status === 'success') {
      console.log('✅ Real-time analysis fetched successfully');
      return {
        success: true,
        data: response.data.analysis_data || []
      };
    } else {
      console.error('❌ Failed to fetch real-time analysis:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to fetch real-time analysis',
        data: []
      };
    }
  } catch (error) {
    console.error('❌ Error fetching real-time analysis:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error',
      data: []
    };
  }
};

export const getLiveAnalysis = async (interviewId) => {
  try {
    console.log('⚡ Fetching live analysis:', interviewId);
    const response = await api.get(`/interviews/${interviewId}/live-analysis`);
    
    if (response.data.status === 'success') {
      console.log('✅ Live analysis fetched successfully');
      return {
        success: true,
        data: response.data.live_analysis || {},
        isLive: response.data.is_live || false
      };
    } else {
      console.error('❌ Failed to fetch live analysis:', response.data.message);
      return {
        success: false,
        error: response.data.message || 'Failed to fetch live analysis',
        data: {},
        isLive: false
      };
    }
  } catch (error) {
    console.error('❌ Error fetching live analysis:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error',
      data: {},
      isLive: false
    };
  }
};

// ==================== HELPER FUNCTIONS ====================

export const validateInterviewData = (data) => {
  const errors = [];
  
  if (!data.candidate_name || data.candidate_name.trim() === '') {
    errors.push('Candidate name is required');
  }
  
  if (!data.candidate_email || data.candidate_email.trim() === '') {
    errors.push('Candidate email is required');
  }
  
  if (!data.position || data.position.trim() === '') {
    errors.push('Position is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const formatInterviewData = (rawData) => {
  return {
    candidate_name: rawData.candidateName || rawData.candidate_name || '',
    candidate_email: rawData.candidateEmail || rawData.candidate_email || '',
    position: rawData.position || '',
    phone: rawData.phone || '',
    experience_years: parseInt(rawData.experienceYears || rawData.experience_years || 0),
    skills: Array.isArray(rawData.skills) ? rawData.skills : (rawData.skills || '').split(',').map(s => s.trim()).filter(s => s),
    education: rawData.education || '',
    candidate_notes: rawData.candidateNotes || rawData.candidate_notes || '',
    interview_type: rawData.interviewType || rawData.interview_type || 'technical',
    platform: rawData.platform || 'browser',
    duration_minutes: parseInt(rawData.durationMinutes || rawData.duration_minutes || 60),
    scheduled_at: rawData.scheduledAt || rawData.scheduled_at || new Date().toISOString(),
    interview_notes: rawData.interviewNotes || rawData.interview_notes || '',
    questions: Array.isArray(rawData.questions) ? rawData.questions : [],
    evaluation_criteria: Array.isArray(rawData.evaluationCriteria) ? rawData.evaluationCriteria : []
  };
};

export default {
  createInterview,
  getInterviews,
  getInterview,
  startInterview,
  stopInterview,
  saveAnalysisData,
  getInterviewAnalysis,
  getInterviewSummary,
  getRealtimeAnalysis,
  getLiveAnalysis,
  validateInterviewData,
  formatInterviewData
};
