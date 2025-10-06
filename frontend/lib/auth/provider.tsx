/**
 * Authentication Provider - Production Grade
 * Handles JWT tokens, refresh logic, session management
 * @module lib/auth/provider
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api/client';

/**
 * User role types
 */
export enum UserRole {
  ADMIN = 'ADMIN',
  ENTERPRISE = 'ENTERPRISE',
  PROFESSIONAL = 'PROFESSIONAL',
  ESSENTIAL = 'ESSENTIAL',
  GUEST = 'GUEST',
}

/**
 * User subscription tier
 */
export enum SubscriptionTier {
  ENTERPRISE = 'ENTERPRISE',
  PROFESSIONAL = 'PROFESSIONAL',
  ESSENTIAL = 'ESSENTIAL',
  FREE = 'FREE',
}

/**
 * User entity
 */
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  subscription: SubscriptionTier;
  avatar?: string;
  permissions: string[];
  metadata: Record<string, any>;
  createdAt: string;
  lastLoginAt: string;
}

/**
 * Authentication tokens
 */
interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

/**
 * Authentication context
 */
interface AuthContextValue {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  refreshTokens: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Local storage keys
 */
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth.accessToken',
  REFRESH_TOKEN: 'auth.refreshToken',
  EXPIRES_AT: 'auth.expiresAt',
  USER: 'auth.user',
} as const;

/**
 * Authentication Provider Component
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  /**
   * Load auth state from storage
   */
  useEffect(() => {
    const loadAuthState = () => {
      try {
        const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        const expiresAt = localStorage.getItem(STORAGE_KEYS.EXPIRES_AT);
        const userData = localStorage.getItem(STORAGE_KEYS.USER);
        
        if (accessToken && refreshToken && expiresAt && userData) {
          const parsedTokens: AuthTokens = {
            accessToken,
            refreshToken,
            expiresAt: parseInt(expiresAt, 10),
          };
          
          setTokens(parsedTokens);
          setUser(JSON.parse(userData));
          apiClient.setTokens(accessToken, refreshToken);
          
          // Check if token is expired
          if (parsedTokens.expiresAt < Date.now()) {
            refreshTokens();
          }
        }
      } catch (error) {
        console.error('Failed to load auth state:', error);
        clearAuthState();
      } finally {
        setIsLoading(false);
      }
    };
    
    loadAuthState();
  }, []);
  
  /**
   * Save auth state to storage
   */
  const saveAuthState = useCallback((tokens: AuthTokens, user: User) => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.accessToken);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refreshToken);
    localStorage.setItem(STORAGE_KEYS.EXPIRES_AT, tokens.expiresAt.toString());
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  }, []);
  
  /**
   * Clear auth state from storage
   */
  const clearAuthState = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.EXPIRES_AT);
    localStorage.removeItem(STORAGE_KEYS.USER);
    setTokens(null);
    setUser(null);
    apiClient.clearTokens();
  }, []);
  
  /**
   * Login user
   */
  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await apiClient.post<{
        user: User;
        accessToken: string;
        refreshToken: string;
        expiresIn: number;
      }>('/api/v1/auth/login', { email, password });
      
      const authTokens: AuthTokens = {
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + response.expiresIn * 1000,
      };
      
      setTokens(authTokens);
      setUser(response.user);
      saveAuthState(authTokens, response.user);
      apiClient.setTokens(authTokens.accessToken, authTokens.refreshToken);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, [saveAuthState]);
  
  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      clearAuthState();
    }
  }, [clearAuthState]);
  
  /**
   * Register new user
   */
  const register = useCallback(async (email: string, password: string, name: string) => {
    try {
      const response = await apiClient.post<{
        user: User;
        accessToken: string;
        refreshToken: string;
        expiresIn: number;
      }>('/api/v1/auth/register', { email, password, name });
      
      const authTokens: AuthTokens = {
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + response.expiresIn * 1000,
      };
      
      setTokens(authTokens);
      setUser(response.user);
      saveAuthState(authTokens, response.user);
      apiClient.setTokens(authTokens.accessToken, authTokens.refreshToken);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }, [saveAuthState]);
  
  /**
   * Refresh authentication tokens
   */
  const refreshTokens = useCallback(async () => {
    if (!tokens?.refreshToken) {
      clearAuthState();
      return;
    }
    
    try {
      const response = await apiClient.post<{
        accessToken: string;
        refreshToken: string;
        expiresIn: number;
      }>('/api/v1/auth/refresh', {
        refreshToken: tokens.refreshToken,
      });
      
      const newTokens: AuthTokens = {
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        expiresAt: Date.now() + response.expiresIn * 1000,
      };
      
      setTokens(newTokens);
      if (user) {
        saveAuthState(newTokens, user);
      }
      apiClient.setTokens(newTokens.accessToken, newTokens.refreshToken);
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuthState();
    }
  }, [tokens, user, saveAuthState, clearAuthState]);
  
  /**
   * Auto-refresh tokens before expiry
   */
  useEffect(() => {
    if (!tokens || !user) return;
    
    const timeUntilExpiry = tokens.expiresAt - Date.now();
    const refreshTime = timeUntilExpiry - 5 * 60 * 1000; // 5 minutes before expiry
    
    if (refreshTime > 0) {
      const timer = setTimeout(() => {
        refreshTokens();
      }, refreshTime);
      
      return () => clearTimeout(timer);
    } else {
      refreshTokens();
    }
  }, [tokens, user, refreshTokens]);
  
  /**
   * Update user data
   */
  const updateUser = useCallback((updates: Partial<User>) => {
    setUser((prev) => {
      if (!prev) return null;
      const updated = { ...prev, ...updates };
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updated));
      return updated;
    });
  }, []);
  
  /**
   * Check if user has permission
   */
  const hasPermission = useCallback(
    (permission: string): boolean => {
      return user?.permissions.includes(permission) ?? false;
    },
    [user]
  );
  
  /**
   * Check if user has role
   */
  const hasRole = useCallback(
    (role: UserRole): boolean => {
      return user?.role === role;
    },
    [user]
  );
  
  const value: AuthContextValue = {
    user,
    tokens,
    isAuthenticated: !!user && !!tokens,
    isLoading,
    login,
    logout,
    register,
    refreshTokens,
    updateUser,
    hasPermission,
    hasRole,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use authentication context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
