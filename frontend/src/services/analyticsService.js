import api from './api';

class AnalyticsService {
  constructor() {
    this.baseURL = '/analytics';
  }

  /**
   * Get detailed candidate analytics data with filtering
   * @param {Object} filters - Filter options
   * @returns {Promise<Object>} Filtered candidate data
   */
  async getCandidates(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      // Add filter parameters
      if (filters.min_confidence !== undefined) {
        params.append('min_confidence', filters.min_confidence);
      }
      if (filters.max_confidence !== undefined) {
        params.append('max_confidence', filters.max_confidence);
      }
      if (filters.min_stress !== undefined) {
        params.append('min_stress', filters.min_stress);
      }
      if (filters.max_stress !== undefined) {
        params.append('max_stress', filters.max_stress);
      }
      if (filters.job_role_id) {
        params.append('job_role_id', filters.job_role_id);
      }
      if (filters.status) {
        params.append('status', filters.status);
      }
      if (filters.date_from) {
        params.append('date_from', filters.date_from);
      }
      if (filters.date_to) {
        params.append('date_to', filters.date_to);
      }

      const response = await api.get(`${this.baseURL}/candidates?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error getting analytics candidates:', error);
      throw error;
    }
  }

  /**
   * Get analytics overview statistics
   * @returns {Promise<Object>} Overview statistics
   */
  async getOverview() {
    try {
      const response = await api.get(`${this.baseURL}/overview`);
      return response.data;
    } catch (error) {
      console.error('Error getting analytics overview:', error);
      throw error;
    }
  }

  /**
   * Get session trends data
   * @param {string} timeRange - Time range (7days, 30days, etc.)
   * @returns {Promise<Object>} Session trends data
   */
  async getSessionTrends(timeRange = '7days') {
    try {
      // For now, return mock data. This can be connected to real backend later
      const mockData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        sessions: [12, 19, 15, 25, 22, 18, 14],
        confidence: [75, 82, 78, 85, 88, 80, 76]
      };
      
      return {
        status: 'success',
        data: mockData
      };
    } catch (error) {
      console.error('Error getting session trends:', error);
      throw error;
    }
  }

  /**
   * Get emotion distribution data
   * @returns {Promise<Object>} Emotion distribution data
   */
  async getEmotionDistribution() {
    try {
      // For now, return mock data. This can be connected to real backend later
      const mockData = {
        emotions: [
          { name: 'Confident', value: 45, color: '#4CAF50' },
          { name: 'Nervous', value: 25, color: '#FF9800' },
          { name: 'Calm', value: 20, color: '#2196F3' },
          { name: 'Stressed', value: 10, color: '#F44336' }
        ]
      };
      
      return {
        status: 'success',
        data: mockData
      };
    } catch (error) {
      console.error('Error getting emotion distribution:', error);
      throw error;
    }
  }

  /**
   * Get candidate trends data (latest 3 candidates stress and confidence progression)
   * @returns {Promise<Object>} Candidate trends data
   */
  async getCandidateTrends() {
    try {
      const response = await api.get(`${this.baseURL}/candidate-trends`);
      return response.data;
    } catch (error) {
      console.error('Error fetching candidate trends:', error);
      throw error;
    }
  }

  /**
   * Get detailed analysis data for a specific interview
   * @param {string} interviewId - Interview ID
   * @returns {Promise<Object>} Detailed interview analysis data
   */
  async getInterviewAnalysis(interviewId) {
    try {
      const response = await api.get(`/interviews/${interviewId}/analysis`);
      return response.data;
    } catch (error) {
      console.error('Error fetching interview analysis:', error);
      throw error;
    }
  }

  /**
   * Generate sample analysis data for testing
   * @param {string} interviewId - Interview ID
   * @returns {Promise<Object>} Sample analysis data
   */
  async generateSampleAnalysis(interviewId) {
    try {
      const response = await api.post(`/interviews/${interviewId}/generate-sample-analysis`);
      return response.data;
    } catch (error) {
      console.error('Error generating sample analysis:', error);
      throw error;
    }
  }

  /**
   * Debug analysis data for a specific interview
   * @param {string} interviewId - Interview ID
   * @returns {Promise<Object>} Debug analysis data
   */
  async debugAnalysis(interviewId) {
    try {
      const response = await api.get(`/interviews/${interviewId}/debug-analysis`);
      return response.data;
    } catch (error) {
      console.error('Error debugging analysis:', error);
      throw error;
    }
  }
}

export const analyticsService = new AnalyticsService();
