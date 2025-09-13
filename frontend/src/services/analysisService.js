import api from './api';

class AnalysisService {
  constructor() {
    this.baseURL = '/interviews';
  }

  async submitConfidenceAnalysis(interviewId, analysisData) {
    try {
      const response = await api.post(`${this.baseURL}/${interviewId}/confidence-analysis`, analysisData);
      return response.data;
    } catch (error) {
      console.error('Error submitting confidence analysis:', error);
      throw error;
    }
  }

  async submitStressAnalysis(interviewId, analysisData) {
    try {
      const response = await api.post(`${this.baseURL}/${interviewId}/stress-analysis`, analysisData);
      return response.data;
    } catch (error) {
      console.error('Error submitting stress analysis:', error);
      throw error;
    }
  }

  async calculateFinalAnalysis(interviewId, analysisData) {
    try {
      const response = await api.post(`${this.baseURL}/${interviewId}/final-analysis`, analysisData);
      return response.data;
    } catch (error) {
      console.error('Error calculating final analysis:', error);
      throw error;
    }
  }

  async getFinalAnalysis(interviewId) {
    try {
      const response = await api.get(`${this.baseURL}/${interviewId}/analysis`);
      return response.data;
    } catch (error) {
      console.error('Error getting final analysis:', error);
      throw error;
    }
  }
}

export const analysisService = new AnalysisService();
