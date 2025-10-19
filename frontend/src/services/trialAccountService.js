// Trial Account Service for InsightHire Frontend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class TrialAccountService {
  /**
   * Create a new trial account
   * @returns {Promise<Object>} - Trial account creation result
   */
  async createTrialAccount() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trial/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error creating trial account:', error);
      return {
        status: 'error',
        message: 'Error creating trial account'
      };
    }
  }

  /**
   * Get trial account status
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - Trial status
   */
  async getTrialStatus(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trial/status?userId=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting trial status:', error);
      return {
        status: 'error',
        message: 'Error getting trial status'
      };
    }
  }

  /**
   * Check interview limit
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - Interview limit check result
   */
  async checkInterviewLimit(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trial/check-interview-limit?userId=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error checking interview limit:', error);
      return {
        status: 'error',
        message: 'Error checking interview limit'
      };
    }
  }

  /**
   * Check job role limit
   * @param {string} userId - User ID
   * @returns {Promise<Object>} - Job role limit check result
   */
  async checkJobRoleLimit(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trial/check-job-role-limit?userId=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error checking job role limit:', error);
      return {
        status: 'error',
        message: 'Error checking job role limit'
      };
    }
  }
}

// Create and export a singleton instance
const trialAccountService = new TrialAccountService();
export default trialAccountService;
