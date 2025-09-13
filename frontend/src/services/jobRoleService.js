import api from './api';

class JobRoleService {
  constructor() {
    this.baseURL = '/job-roles';
  }

  /**
   * Create a new job role
   * @param {Object} jobRoleData - Job role data
   * @returns {Promise<Object>} Created job role
   */
  async createJobRole(jobRoleData) {
    try {
      const response = await api.post(this.baseURL, jobRoleData);
      return response.data;
    } catch (error) {
      console.error('Error creating job role:', error);
      throw error;
    }
  }

  /**
   * Get all job roles for the current user
   * @returns {Promise<Array>} List of job roles
   */
  async getJobRoles() {
    try {
      const response = await api.get(this.baseURL);
      return response.data;
    } catch (error) {
      console.error('Error getting job roles:', error);
      throw error;
    }
  }

  /**
   * Get a specific job role by ID
   * @param {string} jobRoleId - Job role ID
   * @returns {Promise<Object>} Job role data
   */
  async getJobRole(jobRoleId) {
    try {
      const response = await api.get(`${this.baseURL}/${jobRoleId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting job role:', error);
      throw error;
    }
  }

  /**
   * Update a job role
   * @param {string} jobRoleId - Job role ID
   * @param {Object} updateData - Update data
   * @returns {Promise<Object>} Updated job role
   */
  async updateJobRole(jobRoleId, updateData) {
    try {
      const response = await api.put(`${this.baseURL}/${jobRoleId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Error updating job role:', error);
      throw error;
    }
  }

  /**
   * Delete a job role
   * @param {string} jobRoleId - Job role ID
   * @returns {Promise<Object>} Deletion result
   */
  async deleteJobRole(jobRoleId) {
    try {
      const response = await api.delete(`${this.baseURL}/${jobRoleId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting job role:', error);
      throw error;
    }
  }

  /**
   * Assign a job role to an interview
   * @param {string} jobRoleId - Job role ID
   * @param {string} interviewId - Interview ID
   * @returns {Promise<Object>} Assignment result
   */
  async assignJobRoleToInterview(jobRoleId, interviewId) {
    try {
      const response = await api.post(`${this.baseURL}/${jobRoleId}/assign`, {
        interview_id: interviewId
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning job role to interview:', error);
      throw error;
    }
  }

  /**
   * Get default confidence levels for a job role type
   * @param {string} jobType - Type of job (e.g., 'software_engineer', 'data_scientist')
   * @returns {Object} Default confidence levels
   */
  getDefaultConfidenceLevels(jobType) {
    const defaults = {
      'software_engineer': {
        voice_confidence: 20,
        hand_confidence: 30,
        eye_confidence: 50
      },
      'data_scientist': {
        voice_confidence: 25,
        hand_confidence: 25,
        eye_confidence: 50
      },
      'product_manager': {
        voice_confidence: 40,
        hand_confidence: 20,
        eye_confidence: 40
      },
      'designer': {
        voice_confidence: 15,
        hand_confidence: 45,
        eye_confidence: 40
      },
      'sales': {
        voice_confidence: 50,
        hand_confidence: 20,
        eye_confidence: 30
      },
      'marketing': {
        voice_confidence: 35,
        hand_confidence: 25,
        eye_confidence: 40
      }
    };

    return defaults[jobType] || {
      voice_confidence: 20,
      hand_confidence: 30,
      eye_confidence: 50
    };
  }

  /**
   * Validate confidence levels
   * @param {Object} confidenceLevels - Confidence levels object
   * @returns {Object} Validation result
   */
  validateConfidenceLevels(confidenceLevels) {
    const { voice_confidence, hand_confidence, eye_confidence } = confidenceLevels;
    const total = voice_confidence + hand_confidence + eye_confidence;

    if (total > 100) {
      return {
        isValid: false,
        message: 'Total confidence levels cannot exceed 100%'
      };
    }

    if (total < 100) {
      return {
        isValid: false,
        message: 'Total confidence levels must equal 100%'
      };
    }

    return {
      isValid: true,
      message: 'Confidence levels are valid'
    };
  }

  /**
   * Auto-calculate eye confidence based on voice and hand confidence
   * @param {number} voiceConfidence - Voice confidence percentage
   * @param {number} handConfidence - Hand confidence percentage
   * @returns {number} Calculated eye confidence
   */
  calculateEyeConfidence(voiceConfidence, handConfidence) {
    const remaining = 100 - voiceConfidence - handConfidence;
    return Math.max(0, Math.min(100, remaining));
  }
}

export const jobRoleService = new JobRoleService();
