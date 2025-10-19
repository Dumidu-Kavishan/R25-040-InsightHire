// Premium Code Service for InsightHire
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class PremiumCodeService {
  /**
   * Validate a premium code
   * @param {string} premiumCode - The premium code to validate
   * @returns {Promise<Object>} - Validation result
   */
  async validatePremiumCode(premiumCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/premium/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ premium_code: premiumCode }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error validating premium code:', error);
      return {
        status: 'error',
        message: 'Error validating premium code',
        valid: false
      };
    }
  }

  /**
   * Use a premium code (mark as used)
   * @param {string} premiumCode - The premium code to use
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} - Usage result
   */
  async usePremiumCode(premiumCode, userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/premium/use`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          premium_code: premiumCode,
          user_id: userId 
        }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error using premium code:', error);
      return {
        status: 'error',
        message: 'Error using premium code'
      };
    }
  }

  /**
   * Purchase a premium code
   * @param {Object} paymentData - Payment information
   * @returns {Promise<Object>} - Purchase result
   */
  async purchasePremiumCode(paymentData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/premium/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(paymentData),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error purchasing premium code:', error);
      return {
        status: 'error',
        message: 'Error processing payment'
      };
    }
  }

  /**
   * Check if user has premium access
   * @param {string} userId - The user ID
   * @returns {Promise<Object>} - Access information
   */
  async checkPremiumAccess(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/premium/check-access?userId=${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error checking premium access:', error);
      return {
        status: 'error',
        message: 'Error checking premium access',
        has_premium: false
      };
    }
  }

  /**
   * Generate a premium code (admin function)
   * @param {Object} paymentData - Optional payment data
   * @returns {Promise<Object>} - Generation result
   */
  async generatePremiumCode(paymentData = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/premium/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ payment_data: paymentData }),
      });

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error generating premium code:', error);
      return {
        status: 'error',
        message: 'Error generating premium code'
      };
    }
  }
}

// Create and export a singleton instance
const premiumCodeService = new PremiumCodeService();
export default premiumCodeService;
