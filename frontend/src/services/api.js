import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout to 30 seconds
  // Don't set Content-Type globally - let axios handle it per request type
});

// Request interceptor to add user ID
api.interceptors.request.use(
  (config) => {
    const userString = localStorage.getItem('user');
    console.log('🔍 API Request interceptor - localStorage user string:', userString);
    
    if (!userString) {
      console.warn('⚠️ No user found in localStorage - user needs to login');
      // Don't create fallback user - let authentication flow handle it
      return config;
    }
    
    const user = JSON.parse(userString);
    console.log('🔍 API Request interceptor - user from localStorage:', user);
    
    if (user.uid) {
      config.headers['X-User-ID'] = user.uid;
      config.params = { ...config.params, userId: user.uid };
      console.log('✅ API Request - added user ID:', user.uid);
    } else {
      console.warn('⚠️ No user.uid found in localStorage user object');
    }
    
    // Set Content-Type only for POST/PUT/PATCH requests
    if (config.method && ['post', 'put', 'patch'].includes(config.method.toLowerCase())) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    console.log('📤 API Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      params: config.params
    });
    return config;
  },
  (error) => {
    console.error('API Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  register: async (userData) => {
    const response = await api.post('/register', userData);
    return response.data;
  },

  login: async (userData) => {
    const response = await api.post('/login', userData);
    return response.data;
  }
};

// User services  
export const userService = {
  getProfile: async () => {
    const response = await api.get('/user/profile');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/user/profile', userData);
    return response.data;
  },

  refreshProfile: async () => {
    const response = await api.post('/user/profile/refresh');
    return response.data;
  }
};

// Interview services
export const interviewService = {
  createInterview: async (interviewData) => {
    const response = await api.post('/interviews', interviewData);
    return response.data;
  },

  getInterviews: async () => {
    const response = await api.get('/interviews');
    return response.data;
  },

  getInterview: async (interviewId) => {
    const response = await api.get(`/interviews/${interviewId}`);
    return response.data;
  },

  startInterview: async (interviewId) => {
    const response = await api.post(`/interviews/${interviewId}/start`);
    return response.data;
  },

  stopInterview: async (interviewId, data = {}) => {
    const response = await api.post(`/interviews/${interviewId}/stop`, data);
    return response.data;
  },

  getInterviewAnalysis: async (interviewId) => {
    const response = await api.get(`/interviews/${interviewId}/analysis`);
    return response.data;
  },

  getInterviewSummary: async (interviewId) => {
    const response = await api.get(`/interviews/${interviewId}/summary`);
    return response.data;
  },

  saveAnalysisData: async (interviewId, analysisData) => {
    const response = await api.post(`/interviews/${interviewId}/analysis`, analysisData);
    return response.data;
  },

  getRealtimeAnalysis: async (interviewId) => {
    const response = await api.get(`/interviews/${interviewId}/realtime-analysis`);
    return response.data;
  },

  getLiveAnalysis: async (interviewId) => {
    const response = await api.get(`/interviews/${interviewId}/live-analysis`);
    return response.data;
  },

  deleteInterview: async (interviewId) => {
    const response = await api.delete(`/interviews/${interviewId}`);
    return response.data;
  }
};

// Health check
export const healthService = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export default api;
