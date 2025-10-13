/**
 * 🔌 Enhanced API Hooks - Real-time Integration
 * 
 * @fileoverview Enhanced React hooks for API and WebSocket integration
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Lead Dev IA + Backend Senior + Microservices Expert
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import apiClient from './apiClient';
import analyticsApi, { MetricData, DashboardData } from './analyticsApi';

// === ENHANCED WEBSOCKET INTERFACES ===

export interface WebSocketOptions {
  autoReconnect?: boolean;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  heartbeatInterval?: number;
  authToken?: string;
  protocols?: string[];
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: any;
  connectionAttempts: number;
}

export interface NotificationMessage {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  userId?: string;
  actionUrl?: string;
  persistent?: boolean;
  isRead?: boolean;
}

// === ENHANCED WEBSOCKET HOOK WITH AUTHENTICATION ===

export function useWebSocket(url: string, options: WebSocketOptions = {}) {
  const {
    autoReconnect = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    heartbeatInterval = 30000,
    authToken,
    protocols = []
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    lastMessage: null,
    connectionAttempts: 0
  });

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimer = useRef<NodeJS.Timeout | null>(null);
  const messageQueue = useRef<any[]>([]);

  const connect = useCallback(() => {
    if (state.isConnecting || state.isConnected) return;

    setState(prev => ({ 
      ...prev, 
      isConnecting: true, 
      error: null,
      connectionAttempts: prev.connectionAttempts + 1 
    }));

    try {
      const wsUrl = new URL(url);
      
      // ✅ ENHANCED AUTHENTICATION - Add auth token to WebSocket URL
      const currentAuthToken = authToken || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null);
      if (currentAuthToken) {
        wsUrl.searchParams.set('token', currentAuthToken);
      }

      console.log(`🔌 Connecting to authenticated WebSocket: ${wsUrl.toString()}`);
      
      ws.current = new WebSocket(wsUrl.toString(), protocols);

      ws.current.onopen = () => {
        console.log('✅ WebSocket connected with authentication');
        setState(prev => ({ 
          ...prev, 
          isConnected: true, 
          isConnecting: false, 
          error: null,
          connectionAttempts: 0
        }));

        // Send queued messages
        messageQueue.current.forEach(message => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
          }
        });
        messageQueue.current = [];

        // Start heartbeat
        if (heartbeatInterval > 0) {
          startHeartbeat();
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          // ✅ ENHANCED SECURITY - Handle authentication errors
          if (message.type === 'auth_error' || message.type === 'unauthorized') {
            console.error('❌ WebSocket authentication failed:', message);
            setState(prev => ({ 
              ...prev, 
              error: 'Authentication failed',
              isConnected: false,
              isConnecting: false 
            }));
            
            // Trigger logout event
            window.dispatchEvent(new CustomEvent('auth:logout', { 
              detail: { reason: 'websocket_auth_failed' } 
            }));
            return;
          }

          setState(prev => ({ ...prev, lastMessage: message }));
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log(`🔌 WebSocket closed: ${event.code} ${event.reason}`);
        setState(prev => ({ 
          ...prev, 
          isConnected: false, 
          isConnecting: false 
        }));

        stopHeartbeat();

        // Handle authentication-related closures
        if (event.code === 1008 || event.code === 4001) {
          console.error('❌ WebSocket closed due to authentication failure');
          window.dispatchEvent(new CustomEvent('auth:logout', { 
            detail: { reason: 'websocket_auth_expired' } 
          }));
          return;
        }

        if (autoReconnect && event.code !== 1000 && state.connectionAttempts < reconnectAttempts) {
          scheduleReconnect();
        }
      };

      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setState(prev => ({ 
          ...prev, 
          error: 'WebSocket connection error',
          isConnecting: false 
        }));
      };

    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
      setState(prev => ({ 
        ...prev, 
        error: 'Failed to create WebSocket connection',
        isConnecting: false 
      }));
    }
  }, [url, authToken, protocols, autoReconnect, reconnectAttempts, state.isConnecting, state.isConnected, state.connectionAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    stopHeartbeat();

    if (ws.current) {
      ws.current.close(1000, 'Manual disconnect');
      ws.current = null;
    }

    setState(prev => ({ 
      ...prev, 
      isConnected: false, 
      isConnecting: false,
      connectionAttempts: 0
    }));
  }, []);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimer.current) return;

    const delay = Math.min(reconnectInterval * Math.pow(2, state.connectionAttempts), 30000);
    console.log(`⏰ Scheduling authenticated reconnect in ${delay}ms`);

    reconnectTimer.current = setTimeout(() => {
      reconnectTimer.current = null;
      connect();
    }, delay);
  }, [reconnectInterval, state.connectionAttempts, connect]);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) return;

    heartbeatTimer.current = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ 
          type: 'ping', 
          timestamp: Date.now(),
          authenticated: true 
        }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimer.current) {
      clearInterval(heartbeatTimer.current);
      heartbeatTimer.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      // ✅ ENHANCED SECURITY - Add authentication info to messages
      const authenticatedMessage = {
        ...message,
        timestamp: Date.now(),
        authenticated: true
      };
      ws.current.send(JSON.stringify(authenticatedMessage));
      return true;
    } else {
      messageQueue.current.push(message);
      return false;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [url]);

  // ✅ ENHANCED AUTHENTICATION - Reconnect when auth token changes
  useEffect(() => {
    if (state.isConnected) {
      console.log('🔄 Auth token changed, reconnecting WebSocket...');
      disconnect();
      setTimeout(() => connect(), 1000); // Brief delay before reconnecting
    }
  }, [authToken]);

  return {
    ...state,
    connect,
    disconnect,
    sendMessage
  };
}

// === ENHANCED LIVE METRICS HOOK ===

export function useLiveMetrics() {
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const url = process.env.NEXT_PUBLIC_METRICS_WS || 'ws://localhost:8000/ws/metrics';
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const { isConnected, lastMessage } = useWebSocket(url, {
    authToken: authToken || undefined,
    autoReconnect: true,
    heartbeatInterval: 10000
  });

  // Fetch initial metrics from API
  useEffect(() => {
    const fetchInitialMetrics = async () => {
      try {
        setLoading(true);
        const data = await analyticsApi.getLiveMetrics();
        setMetrics(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error('Failed to fetch initial metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialMetrics();
  }, []);

  // Update metrics from WebSocket
  useEffect(() => {
    if (lastMessage?.type === 'metrics_update') {
      setMetrics(lastMessage.metrics || []);
      setError(null);
    }
  }, [lastMessage]);

  return { 
    metrics, 
    loading, 
    error, 
    isConnected 
  };
}

// === ENHANCED ANALYTICS HOOK ===

export function useAnalytics(dashboardType: string = 'overview') {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const url = `${process.env.NEXT_PUBLIC_ANALYTICS_WS || 'ws://localhost:8000/ws/dashboards'}/${dashboardType}`;
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const { isConnected, lastMessage } = useWebSocket(url, {
    authToken: authToken || undefined,
    autoReconnect: true,
    heartbeatInterval: 15000
  });

  // Fetch initial dashboard data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const data = await analyticsApi.getDashboardData(dashboardType);
        setDashboardData(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
        console.error('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [dashboardType]);

  // Update from WebSocket
  useEffect(() => {
    if (lastMessage?.type === 'dashboard_update') {
      setDashboardData(lastMessage.data);
      setError(null);
    }
  }, [lastMessage]);

  return {
    dashboardData,
    loading,
    error,
    isConnected
  };
}

// === ENHANCED NOTIFICATIONS HOOK ===

export function useNotifications() {
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const url = process.env.NEXT_PUBLIC_NOTIFICATIONS_WS || 'ws://localhost:8000/ws/notifications';
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const { isConnected, lastMessage } = useWebSocket(url, {
    authToken: authToken || undefined,
    autoReconnect: true,
    heartbeatInterval: 30000
  });

  useEffect(() => {
    if (lastMessage?.type === 'notification') {
      const notification: NotificationMessage = lastMessage.data;
      setNotifications(prev => [notification, ...prev].slice(0, 100));
      setUnreadCount(prev => prev + 1);
    }
  }, [lastMessage]);

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
    setUnreadCount(0);
  }, []);

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead
  };
}

// === ENHANCED AUTH HOOK ===

export function useAuth() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true);
      const response = await apiClient.post('/auth/login', { email, password });
      
      if (response.success) {
        const { access_token, refresh_token, user } = response.data;
        apiClient.setAuthToken(access_token);
        localStorage.setItem('refresh_token', refresh_token);
        setUser(user);
        setError(null);
        return user;
      } else {
        setError('Login failed');
        return null;
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    apiClient.clearAuthToken();
    localStorage.removeItem('refresh_token');
    setUser(null);
    setError(null);
  }, []);

  // Check for existing authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = apiClient.getAuthToken();
        if (token) {
          const response = await apiClient.get('/auth/me');
          if (response.success) {
            setUser(response.data);
          } else {
            apiClient.clearAuthToken();
          }
        }
      } catch (err) {
        apiClient.clearAuthToken();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user
  };
}

// === HEALTH MONITOR HOOK ===

export function useHealthMonitor() {
  const [isHealthy, setIsHealthy] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiClient.healthCheck();
        setIsHealthy(true);
      } catch (error) {
        setIsHealthy(false);
      }
      setLastCheck(new Date());
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  return { isHealthy, lastCheck };
}

// === API HOOK WITH LOADING STATES ===

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    execute();
  }, [execute]);

  return {
    data,
    loading,
    error,
    refetch: execute
  };
}

// Export enhanced API client and services
export { apiClient, analyticsApi };

// Types are already exported with their declarations above