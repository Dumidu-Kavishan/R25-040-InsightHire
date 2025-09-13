/**
 * Interview Scoring Service
 * Handles calculation of confidence and stress scores based on interview data
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class InterviewScoringService {
  constructor() {
    this.getUserId = () => {
      const user = JSON.parse(localStorage.getItem('user'));
      return user?.uid || user?.id;
    };
  }

  /**
   * Calculate confidence percentage for a specific component
   * @param {Array} records - Array of interview records
   * @param {string} component - Component name (hand_confidence, eye_confidence, voice_confidence)
   * @param {number} weight - Weight percentage for this component
   * @returns {number} Calculated percentage
   */
  calculateComponentConfidence(records, component, weight) {
    if (!records || records.length === 0) return 0;
    
    const confidentRecords = records.filter(record => {
      const componentData = record[component];
      return componentData && componentData.confidence === 1;
    });
    
    const confidenceRatio = confidentRecords.length / records.length;
    return (confidenceRatio * weight) / 100;
  }

  /**
   * Calculate overall confidence score
   * @param {Array} records - Array of interview records
   * @param {Object} jobRole - Job role object with confidence_levels
   * @returns {Object} Confidence breakdown and overall score
   */
  calculateOverallConfidence(records, jobRole = null) {
    // Use job-specific weights if available, otherwise use default
    let weights;
    if (jobRole && jobRole.confidence_levels) {
      weights = {
        hand_confidence: jobRole.confidence_levels.hand_confidence || 33.33,
        eye_confidence: jobRole.confidence_levels.eye_confidence || 33.33,
        voice_confidence: jobRole.confidence_levels.voice_confidence || 33.33
      };
    } else {
      // Default weights if no job role provided
      weights = {
        hand_confidence: 33.33,
        eye_confidence: 33.33,
        voice_confidence: 33.33
      };
    }

    const handConfidence = this.calculateComponentConfidence(records, 'hand_confidence', weights.hand_confidence);
    const eyeConfidence = this.calculateComponentConfidence(records, 'eye_confidence', weights.eye_confidence);
    const voiceConfidence = this.calculateComponentConfidence(records, 'voice_confidence', weights.voice_confidence);

    const overallConfidence = handConfidence + eyeConfidence + voiceConfidence;

    return {
      hand_confidence: {
        percentage: (handConfidence / weights.hand_confidence) * 100,
        weighted_score: handConfidence
      },
      eye_confidence: {
        percentage: (eyeConfidence / weights.eye_confidence) * 100,
        weighted_score: eyeConfidence
      },
      voice_confidence: {
        percentage: (voiceConfidence / weights.voice_confidence) * 100,
        weighted_score: voiceConfidence
      },
      overall_confidence: overallConfidence * 100,
      total_records: records.length,
      job_weights: weights
    };
  }

  /**
   * Calculate overall stress score
   * @param {Array} records - Array of interview records
   * @returns {Object} Stress breakdown and overall score
   */
  calculateOverallStress(records) {
    if (!records || records.length === 0) return { overall_stress: 0, total_records: 0 };

    const stressRecords = records.filter(record => {
      const faceStress = record.face_stress;
      return faceStress && faceStress.stress === 1;
    });

    const stressRatio = stressRecords.length / records.length;
    const overallStress = stressRatio * 100;

    return {
      overall_stress: overallStress,
      total_records: records.length,
      stress_records: stressRecords.length
    };
  }

  /**
   * Calculate final interview scores
   * @param {Array} records - Array of interview records
   * @param {Object} jobRole - Job role object with confidence_levels
   * @returns {Object} Complete scoring analysis
   */
  calculateFinalScores(records, jobRole = null) {
    const confidenceAnalysis = this.calculateOverallConfidence(records, jobRole);
    const stressAnalysis = this.calculateOverallStress(records);

    return {
      confidence: confidenceAnalysis,
      stress: stressAnalysis,
      calculated_at: new Date().toISOString(),
      analysis_summary: {
        total_records_analyzed: records.length,
        confidence_level: this.getConfidenceLevel(confidenceAnalysis.overall_confidence),
        stress_level: this.getStressLevel(stressAnalysis.overall_stress),
        job_role_name: jobRole ? jobRole.name : 'Unknown',
        job_weights: confidenceAnalysis.job_weights
      }
    };
  }

  /**
   * Get confidence level description
   * @param {number} confidence - Confidence percentage
   * @returns {string} Confidence level description
   */
  getConfidenceLevel(confidence) {
    if (confidence >= 80) return 'Very High';
    if (confidence >= 60) return 'High';
    if (confidence >= 40) return 'Medium';
    if (confidence >= 20) return 'Low';
    return 'Very Low';
  }

  /**
   * Get stress level description
   * @param {number} stress - Stress percentage
   * @returns {string} Stress level description
   */
  getStressLevel(stress) {
    if (stress >= 80) return 'Very High';
    if (stress >= 60) return 'High';
    if (stress >= 40) return 'Medium';
    if (stress >= 20) return 'Low';
    return 'Very Low';
  }

  /**
   * Save final scores to database
   * @param {string} sessionId - Interview session ID
   * @param {string} jobRoleId - Job role ID
   * @param {Object} scores - Calculated scores
   * @returns {Promise} API response
   */
  async saveFinalScores(sessionId, jobRoleId, scores) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/final-scores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: this.getUserId(),
          job_role_id: jobRoleId,
          final_scores: scores,
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving final scores:', error);
      throw error;
    }
  }

  /**
   * Get final scores for a session
   * @param {string} sessionId - Interview session ID
   * @returns {Promise} Final scores data
   */
  async getFinalScores(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/final-scores/${sessionId}`, {
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
      console.error('Error fetching final scores:', error);
      throw error;
    }
  }

  /**
   * Get all final scores for a user
   * @returns {Promise} Array of final scores
   */
  async getAllFinalScores() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/final-scores/user/${this.getUserId()}`, {
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
      console.error('Error fetching all final scores:', error);
      throw error;
    }
  }

  /**
   * Get interview records for scoring calculation
   * @param {string} sessionId - Interview session ID
   * @returns {Promise} Array of interview records
   */
  async getInterviewRecords(sessionId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/interviews/records/${sessionId}`, {
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
      console.error('Error fetching interview records:', error);
      throw error;
    }
  }

  /**
   * Process and save final scores for an interview session
   * @param {string} sessionId - Interview session ID
   * @param {string} jobRoleId - Job role ID
   * @returns {Promise} Final scores data
   */
  async processAndSaveFinalScores(sessionId, jobRoleId) {
    try {
      // Use the backend endpoint to calculate and save scores
      const response = await fetch(`${API_BASE_URL}/api/interviews/${sessionId}/calculate-final-scores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.getUserId(),
          job_role_id: jobRoleId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        return {
          success: true,
          final_scores: result.data.final_scores,
          saved_data: result.data.saved_data
        };
      } else {
        throw new Error(result.message || 'Failed to calculate final scores');
      }
    } catch (error) {
      console.error('Error processing final scores:', error);
      throw error;
    }
  }
}

export const interviewScoringService = new InterviewScoringService();
