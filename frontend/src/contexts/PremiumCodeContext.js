import React, { createContext, useContext, useState, useEffect } from 'react';
import premiumCodeService from '../services/premiumCodeService';

const PremiumCodeContext = createContext();

export const usePremiumCode = () => {
  const context = useContext(PremiumCodeContext);
  if (!context) {
    throw new Error('usePremiumCode must be used within a PremiumCodeProvider');
  }
  return context;
};

export const PremiumCodeProvider = ({ children }) => {
  const [hasPremiumAccess, setHasPremiumAccess] = useState(false);
  const [isCheckingAccess, setIsCheckingAccess] = useState(false);
  const [premiumCode, setPremiumCode] = useState(null);
  const [usedAt, setUsedAt] = useState(null);

  // Check premium access when component mounts
  useEffect(() => {
    checkPremiumAccess();
  }, []);

  const checkPremiumAccess = async (userId = null) => {
    setIsCheckingAccess(true);
    try {
      // If no userId provided, try to get from localStorage or auth context
      if (!userId) {
        const storedUserId = localStorage.getItem('userId');
        if (storedUserId) {
          userId = storedUserId;
        }
      }

      if (!userId) {
        setHasPremiumAccess(false);
        return;
      }

      const result = await premiumCodeService.checkPremiumAccess(userId);
      
      if (result.status === 'success') {
        setHasPremiumAccess(result.has_premium);
        setPremiumCode(result.premium_code);
        setUsedAt(result.used_at);
      } else {
        setHasPremiumAccess(false);
      }
    } catch (error) {
      console.error('Error checking premium access:', error);
      setHasPremiumAccess(false);
    } finally {
      setIsCheckingAccess(false);
    }
  };

  const validateAndUsePremiumCode = async (code, userId = null) => {
    try {
      // First validate the code
      const validationResult = await premiumCodeService.validatePremiumCode(code);
      
      if (!validationResult.valid) {
        return {
          success: false,
          message: validationResult.message || 'Invalid premium code'
        };
      }

      // If no userId provided, try to get from localStorage
      if (!userId) {
        const storedUserId = localStorage.getItem('userId');
        if (storedUserId) {
          userId = storedUserId;
        }
      }

      // For now, just mark as having premium access without requiring user ID
      // In a real implementation, you might want to require user registration first
      setHasPremiumAccess(true);
      setPremiumCode(code);
      setUsedAt(new Date().toISOString());
      
      // Store in localStorage for persistence
      localStorage.setItem('hasPremiumAccess', 'true');
      localStorage.setItem('premiumCode', code);
      localStorage.setItem('premiumUsedAt', new Date().toISOString());
      
      // If we have a userId, also mark the code as used in the database
      if (userId) {
        try {
          await premiumCodeService.usePremiumCode(code, userId);
        } catch (error) {
          console.warn('Failed to mark code as used in database:', error);
          // Don't fail the entire operation if this fails
        }
      }
      
      return {
        success: true,
        message: 'Premium code activated successfully!'
      };
    } catch (error) {
      console.error('Error validating and using premium code:', error);
      return {
        success: false,
        message: 'Error processing premium code'
      };
    }
  };

  const purchasePremiumCode = async (paymentData) => {
    try {
      const result = await premiumCodeService.purchasePremiumCode(paymentData);
      return result;
    } catch (error) {
      console.error('Error purchasing premium code:', error);
      return {
        status: 'error',
        message: 'Error processing payment'
      };
    }
  };

  const clearPremiumAccess = () => {
    setHasPremiumAccess(false);
    setPremiumCode(null);
    setUsedAt(null);
    localStorage.removeItem('hasPremiumAccess');
    localStorage.removeItem('premiumCode');
    localStorage.removeItem('premiumUsedAt');
  };

  // Load premium access from localStorage on mount
  useEffect(() => {
    const storedAccess = localStorage.getItem('hasPremiumAccess');
    const storedCode = localStorage.getItem('premiumCode');
    const storedUsedAt = localStorage.getItem('premiumUsedAt');
    
    if (storedAccess === 'true' && storedCode) {
      setHasPremiumAccess(true);
      setPremiumCode(storedCode);
      setUsedAt(storedUsedAt);
    } else {
      // Ensure state is cleared if localStorage is empty
      setHasPremiumAccess(false);
      setPremiumCode(null);
      setUsedAt(null);
    }
  }, []);

  // Listen for storage changes (e.g., when cleared during logout)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'hasPremiumAccess' && !e.newValue) {
        setHasPremiumAccess(false);
        setPremiumCode(null);
        setUsedAt(null);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const value = {
    hasPremiumAccess,
    isCheckingAccess,
    premiumCode,
    usedAt,
    checkPremiumAccess,
    validateAndUsePremiumCode,
    purchasePremiumCode,
    clearPremiumAccess
  };

  return (
    <PremiumCodeContext.Provider value={value}>
      {children}
    </PremiumCodeContext.Provider>
  );
};
