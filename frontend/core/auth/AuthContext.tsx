/**
 * 🔐 Authentication Context - Enterprise Security
 * 
 * @fileoverview JWT authentication with automatic token refresh
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Security Expert + Lead Dev IA + Backend Senior
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import apiClient from '../api/apiClient';

// === AUTHENTICATION INTERFACES ===

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'creator' | 'viewer' | 'moderator';
  avatar?: string;
  permissions: string[];
  createdAt: string;
  lastLogin?: string;
  emailVerified: boolean;
  twoFactorEnabled: boolean;
  subscription?: {
    plan: 'free' | 'pro' | 'enterprise';
    status: 'active' | 'cancelled' | 'expired';
    expiresAt?: string;
  };
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
  twoFactorCode?: string;
}

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<User | null>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => Promise<User | null>;
  clearError: () => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
}

// === AUTHENTICATION CONTEXT ===

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// === AUTHENTICATION PROVIDER ===

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  const login = useCallback(async (credentials: LoginCredentials): Promise<User | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      console.log('🔐 AuthProvider: Attempting login for', credentials.email);

      const response = await apiClient.post('/auth/login', {
        email: credentials.email,
        password: credentials.password,
        rememberMe: credentials.rememberMe,
        twoFactorCode: credentials.twoFactorCode
      });

      if (response.success && response.data) {
        const { access_token, refresh_token, user } = response.data;

        apiClient.setAuthToken(access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });

        console.log('✅ AuthProvider: Login successful for', user.email);
        
        window.dispatchEvent(new CustomEvent('auth:login', { 
          detail: { user } 
        }));

        return user;
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (error: any) {
      console.error('❌ AuthProvider: Login failed:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Login failed';
      
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isLoading: false
      }));

      return null;
    }
  }, []);

  const logout = useCallback(() => {
    console.log('🔐 AuthProvider: Logging out user');

    apiClient.clearAuthToken();
    localStorage.removeItem('refresh_token');
    
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });

    window.dispatchEvent(new CustomEvent('auth:logout', { 
      detail: { reason: 'manual_logout' } 
    }));

    console.log('✅ AuthProvider: Logout completed');
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) {
        console.warn('⚠️ AuthProvider: No refresh token available');
        return false;
      }

      console.log('🔄 AuthProvider: Refreshing access token');

      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshTokenValue
      });

      if (response.success && response.data) {
        const { access_token, refresh_token: newRefreshToken, user } = response.data;

        apiClient.setAuthToken(access_token);
        localStorage.setItem('refresh_token', newRefreshToken);

        if (user) {
          setState(prev => ({ ...prev, user }));
        }

        console.log('✅ AuthProvider: Token refreshed successfully');
        return true;
      }

      throw new Error('Token refresh failed');
    } catch (error: any) {
      console.error('❌ AuthProvider: Token refresh failed:', error);
      
      logout();
      return false;
    }
  }, [logout]);

  const updateUser = useCallback(async (userData: Partial<User>): Promise<User | null> => {
    try {
      console.log('🔄 AuthProvider: Updating user data');

      const response = await apiClient.patch('/auth/profile', userData);

      if (response.success && response.data) {
        const updatedUser = response.data;
        
        setState(prev => ({
          ...prev,
          user: updatedUser,
          error: null
        }));

        console.log('✅ AuthProvider: User data updated successfully');
        return updatedUser;
      }

      throw new Error(response.message || 'Profile update failed');
    } catch (error: any) {
      console.error('❌ AuthProvider: Profile update failed:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Profile update failed';
      
      setState(prev => ({ ...prev, error: errorMessage }));
      return null;
    }
  }, []);

  const hasPermission = useCallback((permission: string): boolean => {
    return state.user?.permissions?.includes(permission) || false;
  }, [state.user]);

  const hasRole = useCallback((role: string): boolean => {
    return state.user?.role === role;
  }, [state.user]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('🔐 AuthProvider: Initializing authentication');

      try {
        const accessToken = apiClient.getAuthToken();
        
        if (accessToken) {
          const response = await apiClient.get('/auth/me');
          
          if (response.success && response.data) {
            setState({
              user: response.data,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
            
            console.log('✅ AuthProvider: Authentication restored for', response.data.email);
            return;
          }
        }

        const refreshTokenValue = localStorage.getItem('refresh_token');
        if (refreshTokenValue) {
          const refreshed = await refreshToken();
          if (refreshed) {
            return;
          }
        }

        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });

        console.log('🔐 AuthProvider: No valid authentication found');
      } catch (error) {
        console.error('❌ AuthProvider: Initialization failed:', error);
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      }
    };

    initializeAuth();
  }, [refreshToken]);

  useEffect(() => {
    if (!state.isAuthenticated) return;

    const interval = setInterval(() => {
      console.log('🔄 AuthProvider: Performing automatic token refresh');
      refreshToken();
    }, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, [state.isAuthenticated, refreshToken]);

  useEffect(() => {
    const handleAuthLogout = () => {
      logout();
    };

    window.addEventListener('auth:logout', handleAuthLogout);

    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, [logout]);

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
    updateUser,
    clearError,
    hasPermission,
    hasRole
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;