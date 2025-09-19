/**
 * 🔐 Enhanced Authentication Context - Enterprise Security Integration
 * 
 * @fileoverview Secure authentication with WebSocket and real-time integration
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Security Expert + Lead Dev IA + Backend Senior
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback, useRef } from 'react';
import apiClient from '../api/apiClient';
import { WebSocketManager } from '../api/websocketManager';
import RealTimeAnalyticsService from '../api/realTimeAnalytics';

// === AUTHENTICATION INTERFACES ===

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'creator' | 'viewer' | 'moderator';
  permissions: string[];
  avatar?: string;
  preferences: Record<string, any>;
  subscription_tier: 'free' | 'premium' | 'enterprise';
  verified: boolean;
  last_login: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: 'Bearer';
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
  two_factor_code?: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role?: string;
  terms_accepted: boolean;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  isRefreshing: boolean;
  sessionTimeout: Date | null;
  permissions: Set<string>;
}

export interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateUser: (updates: Partial<User>) => Promise<void>;
  checkPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  extendSession: () => void;
  isSessionExpired: () => boolean;
}

// === AUTH REDUCER ===

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; tokens: AuthTokens } }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'TOKEN_REFRESH_START' }
  | { type: 'TOKEN_REFRESH_SUCCESS'; payload: AuthTokens }
  | { type: 'TOKEN_REFRESH_ERROR'; payload: string }
  | { type: 'UPDATE_USER'; payload: Partial<User> }
  | { type: 'SESSION_TIMEOUT'; payload: Date }
  | { type: 'EXTEND_SESSION' };

const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  isRefreshing: false,
  sessionTimeout: null,
  permissions: new Set()
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        permissions: new Set(action.payload.user.permissions),
        sessionTimeout: new Date(Date.now() + (action.payload.tokens.expires_in * 1000))
      };

    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        tokens: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
        permissions: new Set()
      };

    case 'AUTH_LOGOUT':
      return {
        ...initialState,
        isLoading: false
      };

    case 'TOKEN_REFRESH_START':
      return {
        ...state,
        isRefreshing: true,
        error: null
      };

    case 'TOKEN_REFRESH_SUCCESS':
      return {
        ...state,
        tokens: action.payload,
        isRefreshing: false,
        sessionTimeout: new Date(Date.now() + (action.payload.expires_in * 1000))
      };

    case 'TOKEN_REFRESH_ERROR':
      return {
        ...state,
        isRefreshing: false,
        error: action.payload
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
        permissions: action.payload.permissions 
          ? new Set(action.payload.permissions) 
          : state.permissions
      };

    case 'SESSION_TIMEOUT':
      return {
        ...state,
        sessionTimeout: action.payload
      };

    case 'EXTEND_SESSION':
      return {
        ...state,
        sessionTimeout: state.tokens 
          ? new Date(Date.now() + (state.tokens.expires_in * 1000))
          : null
      };

    default:
      return state;
  }
}

// === AUTHENTICATION CONTEXT ===

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// === SECURE STORAGE UTILITY ===

class SecureStorage {
  private static readonly ACCESS_TOKEN_KEY = 'ainflue_access_token';
  private static readonly REFRESH_TOKEN_KEY = 'ainflue_refresh_token';
  private static readonly USER_KEY = 'ainflue_user';

  static setTokens(tokens: AuthTokens): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh_token);
  }

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  static getUser(): User | null {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  static clearAll(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }
}

// === AUTH PROVIDER COMPONENT ===

interface AuthProviderProps {
  children: React.ReactNode;
  wsConfig?: {
    url: string;
    enableRealtimeAnalytics?: boolean;
  };
}

export function AuthProvider({ children, wsConfig }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const wsManagerRef = useRef<WebSocketManager | null>(null);
  const analyticsServiceRef = useRef<RealTimeAnalyticsService | null>(null);

  // Initialize WebSocket services
  useEffect(() => {
    if (wsConfig) {
      wsManagerRef.current = new WebSocketManager({
        url: wsConfig.url,
        reconnectAttempts: 5,
        heartbeatInterval: 30000
      });

      if (wsConfig.enableRealtimeAnalytics) {
        analyticsServiceRef.current = new RealTimeAnalyticsService({
          websocketUrl: wsConfig.url,
          refreshInterval: 5000,
          enableCaching: true,
          cacheSize: 1000,
          enablePrefetching: true
        });
      }
    }
  }, [wsConfig]);

  // Initialize authentication on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = SecureStorage.getAccessToken();
      const refreshToken = SecureStorage.getRefreshToken();
      const user = SecureStorage.getUser();

      if (accessToken && refreshToken && user) {
        try {
          // Verify token validity
          apiClient.setAuthToken(accessToken);
          const response = await apiClient.get('/auth/verify');
          
          if (response.status === 200) {
            const tokens: AuthTokens = {
              access_token: accessToken,
              refresh_token: refreshToken,
              expires_in: 3600, // Default 1 hour
              token_type: 'Bearer'
            };

            dispatch({ 
              type: 'AUTH_SUCCESS', 
              payload: { user, tokens } 
            });

            // Initialize WebSocket connections
            await initializeWebSocketServices(accessToken);
            setupTokenRefresh(tokens.expires_in);
          } else {
            // Token invalid, try refresh
            await handleRefreshToken();
          }
        } catch (error) {
          // Clear invalid tokens
          SecureStorage.clearAll();
          dispatch({ type: 'AUTH_LOGOUT' });
        }
      } else {
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    };

    initializeAuth();
  }, []);

  // Session timeout management
  useEffect(() => {
    if (state.sessionTimeout) {
      if (sessionTimeoutRef.current) {
        clearTimeout(sessionTimeoutRef.current);
      }

      const timeUntilExpiry = state.sessionTimeout.getTime() - Date.now();
      
      if (timeUntilExpiry > 0) {
        sessionTimeoutRef.current = setTimeout(() => {
          dispatch({ type: 'AUTH_ERROR', payload: 'Session expired' });
          handleLogout();
        }, timeUntilExpiry);
      }
    }

    return () => {
      if (sessionTimeoutRef.current) {
        clearTimeout(sessionTimeoutRef.current);
      }
    };
  }, [state.sessionTimeout]);

  // Initialize WebSocket services
  const initializeWebSocketServices = async (token: string) => {
    try {
      if (wsManagerRef.current) {
        await wsManagerRef.current.connect(token);
      }

      if (analyticsServiceRef.current) {
        await analyticsServiceRef.current.initialize(token);
      }
    } catch (error) {
      console.error('WebSocket initialization error:', error);
    }
  };

  // Setup automatic token refresh
  const setupTokenRefresh = (expiresIn: number) => {
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }

    // Refresh token 5 minutes before expiry
    const refreshTime = (expiresIn - 300) * 1000;
    
    if (refreshTime > 0) {
      refreshTimeoutRef.current = setTimeout(() => {
        handleRefreshToken();
      }, refreshTime);
    }
  };

  // Handle login
  const handleLogin = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });

    try {
      const response = await apiClient.post('/auth/login', credentials);
      const { user, tokens } = response.data;

      // Store tokens securely
      SecureStorage.setTokens(tokens);
      SecureStorage.setUser(user);
      
      // Set API client token
      apiClient.setAuthToken(tokens.access_token);

      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { user, tokens } 
      });

      // Initialize WebSocket services
      await initializeWebSocketServices(tokens.access_token);
      setupTokenRefresh(tokens.expires_in);

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
    }
  };

  // Handle registration
  const handleRegister = async (data: RegisterData) => {
    dispatch({ type: 'AUTH_START' });

    try {
      const response = await apiClient.post('/auth/register', data);
      const { user, tokens } = response.data;

      // Store tokens securely
      SecureStorage.setTokens(tokens);
      SecureStorage.setUser(user);
      
      // Set API client token
      apiClient.setAuthToken(tokens.access_token);

      dispatch({ 
        type: 'AUTH_SUCCESS', 
        payload: { user, tokens } 
      });

      // Initialize WebSocket services
      await initializeWebSocketServices(tokens.access_token);
      setupTokenRefresh(tokens.expires_in);

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Registration failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
    }
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      if (state.tokens?.access_token) {
        await apiClient.post('/auth/logout');
      }
    } catch (error) {
      // Continue with logout even if API call fails
    }

    // Disconnect WebSocket services
    if (wsManagerRef.current) {
      wsManagerRef.current.disconnect();
    }
    if (analyticsServiceRef.current) {
      analyticsServiceRef.current.disconnect();
    }

    // Clear storage and state
    SecureStorage.clearAll();
    apiClient.setAuthToken(null);
    
    // Clear timeouts
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
    }

    dispatch({ type: 'AUTH_LOGOUT' });
  };

  // Handle token refresh
  const handleRefreshToken = async () => {
    const refreshToken = SecureStorage.getRefreshToken();
    
    if (!refreshToken) {
      dispatch({ type: 'AUTH_LOGOUT' });
      return;
    }

    dispatch({ type: 'TOKEN_REFRESH_START' });

    try {
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const tokens: AuthTokens = response.data;
      
      SecureStorage.setTokens(tokens);
      apiClient.setAuthToken(tokens.access_token);

      dispatch({ 
        type: 'TOKEN_REFRESH_SUCCESS', 
        payload: tokens 
      });

      setupTokenRefresh(tokens.expires_in);

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Token refresh failed';
      dispatch({ type: 'TOKEN_REFRESH_ERROR', payload: errorMessage });
      handleLogout();
    }
  };

  // Update user data
  const handleUpdateUser = async (updates: Partial<User>) => {
    try {
      const response = await apiClient.patch('/auth/user', updates);
      const updatedUser = response.data;

      SecureStorage.setUser(updatedUser);
      dispatch({ type: 'UPDATE_USER', payload: updatedUser });

    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'User update failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
    }
  };

  // Check user permissions
  const checkPermission = useCallback((permission: string): boolean => {
    return state.permissions.has(permission);
  }, [state.permissions]);

  // Check user role
  const hasRole = useCallback((role: string): boolean => {
    return state.user?.role === role;
  }, [state.user?.role]);

  // Extend session
  const extendSession = useCallback(() => {
    dispatch({ type: 'EXTEND_SESSION' });
  }, []);

  // Check if session is expired
  const isSessionExpired = useCallback((): boolean => {
    return state.sessionTimeout ? state.sessionTimeout.getTime() < Date.now() : false;
  }, [state.sessionTimeout]);

  const contextValue: AuthContextValue = {
    ...state,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    refreshToken: handleRefreshToken,
    updateUser: handleUpdateUser,
    checkPermission,
    hasRole,
    extendSession,
    isSessionExpired
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// === PROTECTED ROUTE COMPONENT ===

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  requiredRole?: string;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ 
  children, 
  requiredPermission, 
  requiredRole, 
  fallback 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, checkPermission, hasRole } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return fallback || <div>Please log in to access this content.</div>;
  }

  if (requiredPermission && !checkPermission(requiredPermission)) {
    return fallback || <div>You don't have permission to access this content.</div>;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return fallback || <div>You don't have the required role to access this content.</div>;
  }

  return <>{children}</>;
}

export default AuthContext;