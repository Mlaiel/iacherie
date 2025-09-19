// React Hooks for API Integration - Ainflue Platform
// Author: Fahed Mlaiel (mlaiel@live.de)
// Role: Lead Dev IA + Backend Senior
// Purpose: Custom React hooks for seamless API integration

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, MetricsData, AnalyticsData, WebSocketMessage, ApiResponse, UserProfile } from './client';

// Custom hook for WebSocket connections
export function useWebSocket(endpoint: string, autoConnect: boolean = true) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      const ws = apiClient.connectWebSocket(endpoint, (message) => {
        setLastMessage(message);
        setError(null);
      });

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Auto-reconnect after 3 seconds
        if (autoConnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };

      ws.onerror = () => {
        setError('WebSocket connection error');
        setIsConnected(false);
      };

      wsRef.current = ws;
    } catch (err) {
      setError('Failed to establish WebSocket connection');
    }
  }, [endpoint, autoConnect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      setError('WebSocket not connected');
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect, autoConnect]);

  return {
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    sendMessage
  };
}

// Custom hook for live metrics
export function useLiveMetrics() {
  const [metrics, setMetrics] = useState<MetricsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { lastMessage } = useWebSocket('/ws/metrics');

  // Fetch initial metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getLiveMetrics();
        if (response.success) {
          setMetrics(response.data);
        } else {
          setError('Failed to load metrics');
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  // Update metrics from WebSocket
  useEffect(() => {
    if (lastMessage?.type === 'metrics_update') {
      setMetrics(lastMessage.data);
    }
  }, [lastMessage]);

  return { metrics, loading, error };
}

// Custom hook for analytics data
export function useAnalytics(contentId?: string, dateRange?: string) {
  const [analytics, setAnalytics] = useState<AnalyticsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.getDashboardAnalytics(contentId, dateRange);
      if (response.success) {
        setAnalytics(response.data);
        setError(null);
      } else {
        setError('Failed to load analytics');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [contentId, dateRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return { 
    analytics, 
    loading, 
    error, 
    refetch: fetchAnalytics 
  };
}

// Custom hook for authentication
export function useAuth() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setLoading(true);
      const response = await apiClient.login(email, password);
      if (response.success) {
        setUser(response.data.user);
        setError(null);
        return response.data.user;
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
    apiClient.disconnectAllWebSockets();
    setUser(null);
    setError(null);
  }, []);

  const updateProfile = useCallback(async (profileData: Partial<UserProfile>) => {
    try {
      const response = await apiClient.updateProfile(profileData);
      if (response.success) {
        setUser(response.data);
        return response.data;
      } else {
        setError('Profile update failed');
        return null;
      }
    } catch (err: any) {
      setError(err.message);
      return null;
    }
  }, []);

  // Check for existing authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await apiClient.getCurrentUser();
        if (response.success) {
          setUser(response.data);
        }
      } catch (err) {
        // User not authenticated
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
    updateProfile,
    isAuthenticated: !!user
  };
}

// Custom hook for API calls with loading states
export function useApi<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiCall();
      if (response.success) {
        setData(response.data);
      } else {
        setError(response.message || 'API call failed');
      }
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

// Custom hook for health monitoring
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

    // Check immediately
    checkHealth();

    // Then check every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  return { isHealthy, lastCheck };
}

// Custom hook for notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState<WebSocketMessage[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const { lastMessage } = useWebSocket('/ws/notifications');

  useEffect(() => {
    if (lastMessage?.type === 'notification') {
      setNotifications(prev => [lastMessage, ...prev]);
      setUnreadCount(prev => prev + 1);
    }
  }, [lastMessage]);

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.data.id === notificationId 
          ? { ...notif, data: { ...notif.data, read: true } }
          : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, data: { ...notif.data, read: true } }))
    );
    setUnreadCount(0);
  }, []);

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead
  };
}

// Export all hooks
export {
  apiClient
};