// API service for candidate management
const API_BASE_URL = 'http://localhost:5000';

class CandidateService {
  // Get all candidates
  async getCandidates() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching candidates:', error);
      throw error;
    }
  }

  // Create a new candidate
  async createCandidate(candidateData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(candidateData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating candidate:', error);
      throw error;
    }
  }

  // Get candidate by ID
  async getCandidateById(candidateId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching candidate:', error);
      throw error;
    }
  }

  // Update candidate
  async updateCandidate(candidateId, candidateData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(candidateData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating candidate:', error);
      throw error;
    }
  }

  // Delete candidate
  async deleteCandidate(candidateId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error deleting candidate:', error);
      throw error;
    }
  }

  // Get candidate interviews
  async getCandidateInterviews(candidateId) {
    try {
      // For now, get all interviews and filter by candidate_id on frontend
      // This could be optimized with a backend endpoint later
      const response = await fetch(`${API_BASE_URL}/api/interviews?userId=${this.getUserId()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      const interviews = result.interviews || [];
      
      // Filter by candidate_id
      const candidateInterviews = interviews.filter(interview => 
        interview.candidate_id === candidateId
      );
      
      return { status: 'success', interviews: candidateInterviews };
    } catch (error) {
      console.error('Error fetching candidate interviews:', error);
      throw error;
    }
  }

  // Create and start interview (replaces startInterviewSession)
  async createInterview(candidateData, interviewData = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews?userId=${this.getUserId()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidate_name: candidateData.name,
          candidate_email: candidateData.email,
          position: candidateData.position || 'Not Specified',
          phone: candidateData.phone || '',
          experience_years: candidateData.experience_years || 0,
          skills: candidateData.skills || [],
          education: candidateData.education || '',
          candidate_notes: candidateData.notes || '',
          interview_type: interviewData.type || 'technical',
          platform: interviewData.platform || 'browser',
          duration_minutes: interviewData.duration || 60,
          scheduled_at: interviewData.scheduled_at || new Date().toISOString(),
          interview_notes: interviewData.notes || '',
          questions: interviewData.questions || [],
          evaluation_criteria: interviewData.criteria || []
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating interview:', error);
      throw error;
    }
  }

  // Save interview analysis data
  async saveInterviewAnalysis(interviewId, analysisData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/analysis?userId=${this.getUserId()}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          ...analysisData,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error saving interview analysis:', error);
      throw error;
    }
  }

  // Get interview analysis
  async getInterviewAnalysis(interviewId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/analysis?userId=${this.getUserId()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching interview analysis:', error);
      throw error;
    }
  }

  // Helper method to get user ID
  getUserId() {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.uid || 'default-user';
    } catch {
      return 'default-user';
    }
  }

  // Test API connection
  async testConnection() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/test`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error testing connection:', error);
      throw error;
    }
  }

  // Search candidates
  async searchCandidates(query, filters = {}) {
    try {
      const params = new URLSearchParams({
        q: query,
        ...filters,
      });
      
      const response = await fetch(`${API_BASE_URL}/api/candidates/search?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error searching candidates:', error);
      throw error;
    }
  }

  // Get dashboard statistics
  async getDashboardStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  }
}

// Export singleton instance
const candidateService = new CandidateService();
export default candidateService;

// Named exports for specific functions
export const {
  getCandidates,
  createCandidate,
  getCandidateById,
  updateCandidate,
  deleteCandidate,
  getCandidateInterviews,    // Updated from getCandidateSessions
  createInterview,           // Updated from startInterviewSession
  saveInterviewAnalysis,     // Updated from saveAnalysisData
  getInterviewAnalysis,      // Updated from getSessionAnalysis
  testConnection,
  searchCandidates,
  getDashboardStats,
} = candidateService;
