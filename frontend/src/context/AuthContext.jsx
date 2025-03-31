import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';

// Create Authentication Context
const AuthContext = createContext();

// Authentication Provider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    
    if (token) {
      authService.getCurrentUser()
        .then(user => {
          setCurrentUser(user);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to get current user:', err);
          localStorage.removeItem('token');
          setCurrentUser(null);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  // Login function
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const { access_token, token_type } = await authService.login(email, password);
      
      // Store token in localStorage
      localStorage.setItem('token', access_token);
      
      // Get user data
      const userData = await authService.getCurrentUser();
      setCurrentUser(userData);
      
      return { success: true };
    } catch (err) {
      setError(err.message || 'Failed to login');
      return { success: false, error: err.message || 'Failed to login' };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
  };

  // Check if user is authenticated
  const isAuthenticated = () => {
    return !!currentUser;
  };

  // Check if user is an attorney (using role or fallback to is_attorney = 1)
  const isAttorney = () => {
    return currentUser && (currentUser.role === 'ATTORNEY' || currentUser.is_attorney === 1);
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    logout,
    isAuthenticated,
    isAttorney
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;