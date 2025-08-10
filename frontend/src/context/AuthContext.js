import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, getCurrentUser, verifyUserEmail, resendVerificationEmail } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        try {
          setToken(storedToken);
          const userData = await getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Token validation failed:', error);
          localStorage.removeItem('authToken');
          setToken(null);
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    try {
      setIsLoading(true);
      const response = await loginUser(email, password);
      const { access_token } = response;
      
      setToken(access_token);
      localStorage.setItem('authToken', access_token);
      
      // Get user data after successful login
      const userData = await getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true, data: response };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.message || 'Login failed. Please check your credentials.' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email, password) => {
    try {
      setIsLoading(true);
      const response = await registerUser(email, password);
      
      // Note: In production with email verification, we don't auto-login
      // The user needs to verify their email first
      return { 
        success: true, 
        data: response,
        message: 'Registration successful! Please check your email to verify your account.' 
      };
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.message || 'Registration failed. Please try again.' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const verifyEmail = async (token) => {
    try {
      const response = await verifyUserEmail(token);
      return { success: true, data: response };
    } catch (error) {
      console.error('Email verification failed:', error);
      return { 
        success: false, 
        error: error.message || 'Email verification failed.' 
      };
    }
  };

  const resendVerification = async (email) => {
    try {
      const response = await resendVerificationEmail(email);
      return { success: true, data: response };
    } catch (error) {
      console.error('Resend verification failed:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to resend verification email.' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('authToken');
  };

  const value = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    verifyEmail,
    resendVerification,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
