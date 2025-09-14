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
    // Temporarily use mock data to test chart display
    console.log('Using mock data for candidate trends');
    const mockData = {
        status: 'success',
        data: {
          candidates: [
            {
              candidate_name: 'John Smith',
              position: 'Software Engineer',
              interview_id: '1',
              created_at: '2024-01-15T10:00:00Z',
              duration_minutes: 45,
              time_points: ['Start', '25%', '50%', '75%', 'End'],
              confidence_progression: [65, 70, 75, 80, 85],
              stress_progression: [40, 45, 50, 35, 25],
              final_confidence: 85,
              final_stress: 25,
              confidence_breakdown: {
                voice: 80,
                hand: 85,
                eye: 90,
                overall: 85
              }
            },
            {
              candidate_name: 'Sarah Johnson',
              position: 'Data Analyst',
              interview_id: '2',
              created_at: '2024-01-14T14:30:00Z',
              duration_minutes: 38,
              time_points: ['Start', '25%', '50%', '75%', 'End'],
              confidence_progression: [55, 60, 65, 70, 75],
              stress_progression: [60, 55, 45, 40, 30],
              final_confidence: 75,
              final_stress: 30,
              confidence_breakdown: {
                voice: 70,
                hand: 75,
                eye: 80,
                overall: 75
              }
            },
            {
              candidate_name: 'Mike Chen',
              position: 'Product Manager',
              interview_id: '3',
              created_at: '2024-01-13T09:15:00Z',
              duration_minutes: 52,
              time_points: ['Start', '25%', '50%', '75%', 'End'],
              confidence_progression: [70, 75, 80, 85, 90],
              stress_progression: [30, 35, 40, 35, 20],
              final_confidence: 90,
              final_stress: 20,
              confidence_breakdown: {
                voice: 85,
                hand: 90,
                eye: 95,
                overall: 90
              }
            }
          ],
          total_candidates: 3
        }
      };
      
      return mockData;
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
