import api from './api';

class UserProfileService {
  constructor() {
    this.baseURL = '/user';
  }

  /**
   * Get user profile information
   * @returns {Promise<Object>} User profile data
   */
  async getProfile() {
    try {
      console.log('Fetching profile from:', `${this.baseURL}/profile`);
      const response = await api.get(`${this.baseURL}/profile`);
      console.log('Profile fetch response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      throw error;
    }
  }

  /**
   * Test API connectivity
   * @returns {Promise<Object>} Health check response
   */
  async testConnection() {
    try {
      console.log('Testing API connection...');
      const response = await api.get('/health');
      console.log('Health check response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Update user profile information
   * @param {Object} profileData - Profile data to update
   * @returns {Promise<Object>} Updated profile data
   */
  async updateProfile(profileData) {
    // Add a timestamp to help with debugging
    const startTime = Date.now();
    
    try {
      console.log('Updating profile with data:', profileData);
      console.log('API URL:', `${this.baseURL}/profile`);
      console.log('Full URL will be:', `http://localhost:5000/api/user/profile`);
      console.log('Request started at:', new Date().toISOString());
      
      const response = await api.put(`${this.baseURL}/profile`, profileData);
      
      const endTime = Date.now();
      console.log('Request completed in:', endTime - startTime, 'ms');
      console.log('Profile update response:', response.data);
      return response.data;
    } catch (error) {
      const endTime = Date.now();
      console.error('Request failed after:', endTime - startTime, 'ms');
      console.error('Error updating user profile:', error);
      console.error('Error details:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          timeout: error.config?.timeout,
          baseURL: error.config?.baseURL
        }
      });
      throw error;
    }
  }

  /**
   * Update display name
   * @param {string} displayName - New display name
   * @returns {Promise<Object>} Updated profile data
   */
  async updateDisplayName(displayName) {
    try {
      const response = await api.put(`${this.baseURL}/profile`, {
        display_name: displayName
      });
      return response.data;
    } catch (error) {
      console.error('Error updating display name:', error);
      throw error;
    }
  }

  /**
   * Update avatar URL
   * @param {string} avatarUrl - New avatar URL
   * @returns {Promise<Object>} Updated profile data
   */
  async updateAvatar(avatarUrl) {
    try {
      const response = await api.put(`${this.baseURL}/profile`, {
        avatar_url: avatarUrl
      });
      return response.data;
    } catch (error) {
      console.error('Error updating avatar:', error);
      throw error;
    }
  }
}

export const userProfileService = new UserProfileService();
