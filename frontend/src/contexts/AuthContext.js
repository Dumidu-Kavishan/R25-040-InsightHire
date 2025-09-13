import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, updateProfile } from 'firebase/auth';
import { auth } from '../firebase';
import { authService, userService } from '../services/api';

// Create context
const AuthContext = createContext();

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  AUTH_START: 'AUTH_START',
  AUTH_SUCCESS: 'AUTH_SUCCESS',
  AUTH_ERROR: 'AUTH_ERROR',
  AUTH_LOGOUT: 'AUTH_LOGOUT',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_LOADING: 'SET_LOADING'
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.AUTH_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    case AUTH_ACTIONS.AUTH_SUCCESS:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    case AUTH_ACTIONS.AUTH_ERROR:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      };
    case AUTH_ACTIONS.AUTH_LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      };
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    default:
      return state;
  }
};

// Provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Login function
  const login = async (email, password) => {
    try {
      dispatch({ type: AUTH_ACTIONS.AUTH_START });

      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Get user token and call backend
      const token = await user.getIdToken();
      
      // Call backend login endpoint
      const response = await authService.login({ 
        email: user.email,
        uid: user.uid,
        token: token 
      });

      if (response.status === 'success') {
        // Clear any cached profile data
        localStorage.removeItem('user');
        
        // Refresh profile from Firebase Auth to get latest data
        try {
          const refreshResponse = await userService.refreshProfile();
          if (refreshResponse.status === 'success') {
            const userData = {
              uid: user.uid,
              email: user.email,
              displayName: refreshResponse.profile.displayName || user.email,
              ...refreshResponse.profile
            };

            // Store fresh user data
            localStorage.setItem('user', JSON.stringify(userData));
            
            dispatch({ 
              type: AUTH_ACTIONS.AUTH_SUCCESS, 
              payload: userData 
            });

            return { success: true, user: userData };
          }
        } catch (refreshError) {
          console.warn('Profile refresh failed, using backend response:', refreshError);
        }
        
        // Fallback to backend response if refresh fails
        const userData = {
          uid: user.uid,
          email: user.email,
          displayName: user.displayName || user.email,
          ...response.user
        };

        // Store user data
        localStorage.setItem('user', JSON.stringify(userData));
        
        dispatch({ 
          type: AUTH_ACTIONS.AUTH_SUCCESS, 
          payload: userData 
        });

        return { success: true, user: userData };
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error) {
      const errorMessage = error.message || 'Login failed';
      dispatch({ 
        type: AUTH_ACTIONS.AUTH_ERROR, 
        payload: errorMessage 
      });
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (email, password, username) => {
    try {
      dispatch({ type: AUTH_ACTIONS.AUTH_START });

      // Create user with Firebase
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Update Firebase profile with username as display name
      if (username) {
        await updateProfile(user, {
          displayName: username
        });
      }

      // Call backend register endpoint
      const response = await authService.register({
        email: email,
        password: password,
        username: username || email,  // Use email as fallback if no username provided
        uid: user.uid
      });

      if (response.status === 'success') {
        const userData = {
          uid: user.uid,
          email: user.email,
          username: username || user.displayName || user.email,
          displayName: username || user.displayName || user.email,
          ...response.user
        };

        // Store user data
        localStorage.setItem('user', JSON.stringify(userData));
        
        dispatch({ 
          type: AUTH_ACTIONS.AUTH_SUCCESS, 
          payload: userData 
        });

        return { success: true, user: userData };
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = error.message || 'Registration failed';
      dispatch({ 
        type: AUTH_ACTIONS.AUTH_ERROR, 
        payload: errorMessage 
      });
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem('user');
      dispatch({ type: AUTH_ACTIONS.AUTH_LOGOUT });
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return { success: false, error: error.message };
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Update profile function
  const updateProfile = async (profileData) => {
    try {
      const response = await authService.updateProfile(profileData);
      if (response.status === 'success') {
        const updatedUser = { ...state.user, ...response.profile };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        dispatch({ 
          type: AUTH_ACTIONS.AUTH_SUCCESS, 
          payload: updatedUser 
        });
        return { success: true, user: updatedUser };
      } else {
        throw new Error(response.message || 'Profile update failed');
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  // Check authentication state on mount
  useEffect(() => {
    // Development mode - only restore existing user, don't create new ones
    if (process.env.NODE_ENV === 'development') {
      console.log('🔧 Development mode - checking for existing authentication');
      // Check if we already have a stored user
      const storedUser = localStorage.getItem('user');
      console.log('🔍 Stored user in localStorage:', storedUser);
      
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        console.log('👤 Using existing user from localStorage:', userData);
        dispatch({ 
          type: AUTH_ACTIONS.AUTH_SUCCESS, 
          payload: userData 
        });
        return;
      } else {
        // No stored user - let user login normally
        console.log('👤 No stored user - user needs to login');
        dispatch({ 
          type: AUTH_ACTIONS.SET_LOADING, 
          payload: false 
        });
        return;
      }
    }

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        try {
          // Check if we have stored user data
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            const userData = JSON.parse(storedUser);
            // Check if stored data looks like the old format (User-xxxxx)
            if (userData.displayName && userData.displayName.startsWith('User-')) {
              // Refresh profile to get correct data
              try {
                const refreshResponse = await userService.refreshProfile();
                if (refreshResponse.status === 'success') {
                  const newUserData = {
                    uid: user.uid,
                    email: user.email,
                    displayName: refreshResponse.profile.displayName || user.email,
                    ...refreshResponse.profile
                  };
                  localStorage.setItem('user', JSON.stringify(newUserData));
                  dispatch({ 
                    type: AUTH_ACTIONS.AUTH_SUCCESS, 
                    payload: newUserData 
                  });
                  return;
                }
              } catch (refreshError) {
                console.warn('Profile refresh failed:', refreshError);
              }
            }
            
            dispatch({ 
              type: AUTH_ACTIONS.AUTH_SUCCESS, 
              payload: userData 
            });
          } else {
            // Get user profile from backend with refresh
            try {
              const refreshResponse = await userService.refreshProfile();
              if (refreshResponse.status === 'success') {
                const userData = {
                  uid: user.uid,
                  email: user.email,
                  displayName: refreshResponse.profile.displayName || user.email,
                  ...refreshResponse.profile
                };
                localStorage.setItem('user', JSON.stringify(userData));
                dispatch({ 
                  type: AUTH_ACTIONS.AUTH_SUCCESS, 
                  payload: userData 
                });
                return;
              }
            } catch (refreshError) {
              console.warn('Profile refresh failed, falling back to getProfile:', refreshError);
            }
            
            // Fallback to regular profile fetch
            const response = await userService.getProfile();
            if (response.status === 'success') {
              const userData = {
                uid: user.uid,
                email: user.email,
                displayName: user.email, // Use email as fallback display name
                ...response.profile
              };
              localStorage.setItem('user', JSON.stringify(userData));
              dispatch({ 
                type: AUTH_ACTIONS.AUTH_SUCCESS, 
                payload: userData 
              });
            } else {
              dispatch({ type: AUTH_ACTIONS.AUTH_LOGOUT });
            }
          }
        } catch (error) {
          console.error('Auth state error:', error);
          dispatch({ type: AUTH_ACTIONS.AUTH_LOGOUT });
        }
      } else {
        localStorage.removeItem('user');
        dispatch({ type: AUTH_ACTIONS.AUTH_LOGOUT });
      }
    });

    return () => unsubscribe();
  }, []);

  const value = {
    ...state,
    login,
    register,
    logout,
    clearError,
    updateProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
