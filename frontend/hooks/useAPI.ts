/**
 * 🎯 CUSTOM HOOKS POUR API INTEGRATION
 * Hooks réutilisables pour la gestion des APIs des 57 modules
 * 
 * @author Fahed Mlaiel - Expert Multi-Role Implementation
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

// Types principaux
export interface APIResponse<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
  status: number | null;
}

export interface APIConfig {
  baseURL?: string;
  timeout?: number;
  retryCount?: number;
  retryDelay?: number;
  headers?: Record<string, string>;
}

export interface WebSocketConfig {
  url: string;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

// Configuration par défaut
const DEFAULT_API_CONFIG: APIConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retryCount: 3,
  retryDelay: 1000,
  headers: {
    'Content-Type': 'application/json',
  }
};

/**
 * Hook principal pour les appels API
 */
export const useAPI = <T = any>(
  endpoint: string,
  options: {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    body?: any;
    dependencies?: any[];
    enabled?: boolean;
    config?: Partial<APIConfig>;
  } = {}
): APIResponse<T> & { refetch: () => Promise<void> } => {
  const {
    method = 'GET',
    body,
    dependencies = [],
    enabled = true,
    config = {}
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<number | null>(null);

  const apiConfig = { ...DEFAULT_API_CONFIG, ...config };
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) return;

    // Annuler la requête précédente si elle existe
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setLoading(true);
    setError(null);

    let retryCount = 0;
    const maxRetries = apiConfig.retryCount || 3;

    while (retryCount <= maxRetries) {
      try {
        const url = `${apiConfig.baseURL}${endpoint}`;
        const requestOptions: RequestInit = {
          method,
          headers: {
            ...apiConfig.headers,
            'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`,
          },
          signal: abortControllerRef.current.signal,
        };

        if (body && method !== 'GET') {
          requestOptions.body = JSON.stringify(body);
        }

        // Timeout personnalisé
        const timeoutId = setTimeout(() => {
          if (abortControllerRef.current) {
            abortControllerRef.current.abort();
          }
        }, apiConfig.timeout);

        const response = await fetch(url, requestOptions);
        clearTimeout(timeoutId);

        setStatus(response.status);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const contentType = response.headers.get('content-type');
        let responseData;

        if (contentType && contentType.includes('application/json')) {
          responseData = await response.json();
        } else {
          responseData = await response.text();
        }

        setData(responseData);
        setError(null);
        break;

      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          break; // Requête annulée, ne pas retry
        }

        retryCount++;
        if (retryCount > maxRetries) {
          const errorMessage = err instanceof Error ? err.message : 'Une erreur est survenue';
          setError(errorMessage);
          setData(null);
        } else {
          // Attendre avant le prochain essai
          await new Promise(resolve => setTimeout(resolve, apiConfig.retryDelay! * retryCount));
        }
      }
    }

    setLoading(false);
  }, [endpoint, method, body, enabled, JSON.stringify(apiConfig), ...dependencies]);

  useEffect(() => {
    fetchData();

    // Cleanup
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  return { data, loading, error, status, refetch: fetchData };
};

/**
 * Hook pour les WebSockets en temps réel
 */
export const useWebSocket = <T = any>(
  config: WebSocketConfig,
  options: {
    onMessage?: (data: T) => void;
    onError?: (error: Event) => void;
    onOpen?: () => void;
    onClose?: () => void;
    enabled?: boolean;
  } = {}
) => {
  const {
    onMessage,
    onError,
    onOpen,
    onClose,
    enabled = true
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    try {
      const ws = new WebSocket(config.url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (err) {
          console.error('Erreur parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        setError('Erreur de connexion WebSocket');
        onError?.(event);
      };

      ws.onclose = () => {
        setIsConnected(false);
        onClose?.();

        // Reconnexion automatique si configurée
        if (config.reconnect && reconnectAttemptsRef.current < (config.maxReconnectAttempts || 5)) {
          reconnectAttemptsRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, config.reconnectInterval || 5000);
        }
      };

    } catch (err) {
      setError('Erreur lors de la création de la connexion WebSocket');
    }
  }, [config, enabled, onMessage, onError, onOpen, onClose]);

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
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    reconnect: connect,
    disconnect
  };
};

/**
 * Hook spécialisé pour les services AI
 */
export const useAIServices = () => {
  const { data, loading, error, refetch } = useAPI('/api/ai-services/status');
  
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  
  // WebSocket pour les métriques temps réel
  const { lastMessage } = useWebSocket({
    url: `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/ai-services`
  }, {
    onMessage: (data) => setRealTimeMetrics(data)
  });

  const startService = useCallback(async (serviceId: string) => {
    const { data } = await useAPI(`/api/ai-services/${serviceId}/start`, {
      method: 'POST',
      enabled: false
    });
    await refetch();
    return data;
  }, [refetch]);

  const stopService = useCallback(async (serviceId: string) => {
    const { data } = await useAPI(`/api/ai-services/${serviceId}/stop`, {
      method: 'POST',
      enabled: false
    });
    await refetch();
    return data;
  }, [refetch]);

  return {
    services: data,
    loading,
    error,
    realTimeMetrics,
    startService,
    stopService,
    refetch
  };
};

/**
 * Hook spécialisé pour Analytics
 */
export const useAnalytics = (timeRange: string = '1h') => {
  const { data, loading, error, refetch } = useAPI(`/api/analytics/dashboard?range=${timeRange}`, {
    dependencies: [timeRange]
  });

  return {
    analytics: data,
    loading,
    error,
    refetch
  };
};

/**
 * Hook pour la gestion des modules
 */
// Types pour les modules
interface ModuleStatus {
  id: string;
  name: string;
  enabled: boolean;
  status: 'active' | 'inactive' | 'error' | 'maintenance';
  health: number;
}

export const useModules = () => {
  const [modules, setModules] = useState<ModuleStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Récupération de tous les modules
  const { data: modulesData, loading: modulesLoading, error: modulesError } = 
    useAPI('/api/modules/status');

  useEffect(() => {
    if (modulesData) {
      setModules(modulesData);
    }
    setLoading(modulesLoading);
    setError(modulesError);
  }, [modulesData, modulesLoading, modulesError]);

  const enableModule = useCallback(async (moduleId: string) => {
    try {
      const response = await fetch(`/api/modules/${moduleId}/enable`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`,
        }
      });
      
      if (response.ok) {
        // Mettre à jour l'état local
        setModules(prev => prev.map(m => 
          m.id === moduleId ? { ...m, enabled: true } : m
        ));
      }
    } catch (err) {
      console.error('Erreur activation module:', err);
    }
  }, []);

  const disableModule = useCallback(async (moduleId: string) => {
    try {
      const response = await fetch(`/api/modules/${moduleId}/disable`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`,
        }
      });
      
      if (response.ok) {
        setModules(prev => prev.map(m => 
          m.id === moduleId ? { ...m, enabled: false } : m
        ));
      }
    } catch (err) {
      console.error('Erreur désactivation module:', err);
    }
  }, []);

  return {
    modules,
    loading,
    error,
    enableModule,
    disableModule
  };
};

/**
 * Hook pour les métriques système
 */
export const useSystemMetrics = (refreshInterval: number = 5000) => {
  const [metrics, setMetrics] = useState(null);

  // WebSocket pour les métriques en temps réel
  const { lastMessage, isConnected } = useWebSocket({
    url: `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/system-metrics`,
    reconnect: true
  }, {
    onMessage: (data) => setMetrics(data)
  });

  // Fallback avec polling si WebSocket non disponible
  const { data: pollingData } = useAPI('/api/system/metrics', {
    enabled: !isConnected,
    dependencies: [refreshInterval]
  });

  useEffect(() => {
    if (!isConnected && pollingData) {
      setMetrics(pollingData);
    }
  }, [isConnected, pollingData]);

  return {
    metrics: metrics || pollingData,
    isRealTime: isConnected
  };
};

/**
 * Hook pour la gestion d'état global des dashboards
 */
// Types pour les notifications
interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  duration?: number;
}

export const useDashboardState = () => {
  const [activeModule, setActiveModule] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notification: {
    id?: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message?: string;
    duration?: number;
  }) => {
    const id = notification.id || Date.now().toString();
    const newNotification = { ...notification, id };
    
    setNotifications(prev => [...prev, newNotification]);

    // Auto-remove après duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      }, notification.duration || 5000);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return {
    activeModule,
    setActiveModule,
    sidebarOpen,
    setSidebarOpen,
    theme,
    setTheme,
    notifications,
    addNotification,
    removeNotification
  };
};

export default {
  useAPI,
  useWebSocket,
  useAIServices,
  useAnalytics,
  useModules,
  useSystemMetrics,
  useDashboardState
};