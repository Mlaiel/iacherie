/**
 * 📊 Real-time Analytics Service - Live Data Integration
 * 
 * @fileoverview Real-time analytics integration replacing mock data
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role ML Engineer + Lead Dev IA + Backend Senior Expert
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import { EventEmitter } from 'events';
import apiClient, { ApiResponse } from './apiClient';
import { WebSocketManager, WebSocketMessage } from './websocketManager';
import { MetricData, TimeSeriesData, AnalyticsQuery, DashboardData } from './analyticsApi';

// === REAL-TIME ANALYTICS INTERFACES ===

export interface LiveMetricUpdate {
  metricId: string;
  value: number;
  timestamp: string;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
}

export interface AnalyticsSubscription {
  id: string;
  metrics: string[];
  filters?: Record<string, any>;
  interval?: number;
  callback: (data: LiveMetricUpdate[]) => void;
}

export interface RealTimeAnalyticsConfig {
  websocketUrl: string;
  refreshInterval: number;
  enableCaching: boolean;
  cacheSize: number;
  enablePrefetching: boolean;
}

// === ANALYTICS CACHE ===

class AnalyticsCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private maxSize: number;

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }

  set(key: string, data: any, ttl: number = 300000): void { // 5 minutes default TTL
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key: string): any | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// === REAL-TIME ANALYTICS SERVICE ===

export class RealTimeAnalyticsService extends EventEmitter {
  private wsManager: WebSocketManager;
  private cache: AnalyticsCache;
  private subscriptions = new Map<string, AnalyticsSubscription>();
  private config: RealTimeAnalyticsConfig;
  private isInitialized = false;
  private authToken: string | null = null;

  constructor(config: RealTimeAnalyticsConfig) {
    super();
    
    this.config = config;
    this.cache = new AnalyticsCache(config.cacheSize);
    this.wsManager = new WebSocketManager({
      url: config.websocketUrl,
      reconnectAttempts: 5,
      heartbeatInterval: 30000,
      enableLogging: true
    });

    this.setupWebSocketListeners();
  }

  /**
   * Initialize the service with authentication
   */
  public async initialize(authToken: string): Promise<void> {
    this.authToken = authToken;
    
    try {
      await this.wsManager.connect(authToken);
      this.isInitialized = true;
      this.emit('initialized');
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Get live dashboard data (replaces mock data)
   */
  public async getLiveDashboardData(filters?: Record<string, any>): Promise<DashboardData> {
    const cacheKey = `dashboard_${JSON.stringify(filters || {})}`;
    
    // Try cache first
    if (this.config.enableCaching) {
      const cached = this.cache.get(cacheKey);
      if (cached) return cached;
    }

    try {
      const response = await apiClient.get<DashboardData>('/analytics/dashboard', {
        params: filters
      });

      const dashboardData = response.data;

      // Cache the result
      if (this.config.enableCaching) {
        this.cache.set(cacheKey, dashboardData);
      }

      // Start real-time updates for these metrics
      if (this.isInitialized) {
        this.subscribeToDashboardUpdates(dashboardData.metrics.map(m => m.id));
      }

      return dashboardData;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Get real-time metrics (replaces Math.random() mock data)
   */
  public async getLiveMetrics(metricIds: string[]): Promise<MetricData[]> {
    const cacheKey = `metrics_${metricIds.sort().join(',')}`;
    
    // Try cache first
    if (this.config.enableCaching) {
      const cached = this.cache.get(cacheKey);
      if (cached) return cached;
    }

    try {
      const response = await apiClient.post<MetricData[]>('/analytics/metrics/live', {
        metric_ids: metricIds
      });

      const metrics = response.data;

      // Cache the result
      if (this.config.enableCaching) {
        this.cache.set(cacheKey, metrics, 60000); // 1 minute TTL for live metrics
      }

      return metrics;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Get time series data for charts (replaces mock chart data)
   */
  public async getTimeSeriesData(
    metricId: string, 
    timeRange: string,
    granularity: 'minute' | 'hour' | 'day' = 'hour'
  ): Promise<TimeSeriesData[]> {
    const cacheKey = `timeseries_${metricId}_${timeRange}_${granularity}`;
    
    // Try cache first
    if (this.config.enableCaching) {
      const cached = this.cache.get(cacheKey);
      if (cached) return cached;
    }

    try {
      const response = await apiClient.get<TimeSeriesData[]>('/analytics/timeseries', {
        params: { metric_id: metricId, time_range: timeRange, granularity }
      });

      const timeSeriesData = response.data;

      // Cache the result
      if (this.config.enableCaching) {
        this.cache.set(cacheKey, timeSeriesData, 120000); // 2 minutes TTL for time series
      }

      return timeSeriesData;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Subscribe to real-time metric updates
   */
  public subscribe(
    metricIds: string[], 
    callback: (updates: LiveMetricUpdate[]) => void,
    filters?: Record<string, any>
  ): string {
    const subscriptionId = `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const subscription: AnalyticsSubscription = {
      id: subscriptionId,
      metrics: metricIds,
      filters,
      callback
    };

    this.subscriptions.set(subscriptionId, subscription);

    // Send subscription request via WebSocket
    if (this.isInitialized) {
      this.wsManager.send({
        type: 'analytics_subscribe',
        data: {
          subscription_id: subscriptionId,
          metrics: metricIds,
          filters
        }
      });
    }

    return subscriptionId;
  }

  /**
   * Unsubscribe from real-time updates
   */
  public unsubscribe(subscriptionId: string): void {
    if (this.subscriptions.has(subscriptionId)) {
      this.subscriptions.delete(subscriptionId);

      // Send unsubscription request via WebSocket
      if (this.isInitialized) {
        this.wsManager.send({
          type: 'analytics_unsubscribe',
          data: { subscription_id: subscriptionId }
        });
      }
    }
  }

  /**
   * Get system performance metrics (replaces mock system data)
   */
  public async getSystemMetrics(): Promise<{
    cpu: number;
    memory: number;
    disk: number;
    network: { in: number; out: number };
    services: Array<{ name: string; status: 'healthy' | 'warning' | 'error'; uptime: number }>;
  }> {
    const cacheKey = 'system_metrics';
    
    // Try cache first
    if (this.config.enableCaching) {
      const cached = this.cache.get(cacheKey);
      if (cached) return cached;
    }

    try {
      const response = await apiClient.get('/monitoring/system');
      const systemMetrics = response.data;

      // Cache the result
      if (this.config.enableCaching) {
        this.cache.set(cacheKey, systemMetrics, 30000); // 30 seconds TTL for system metrics
      }

      return systemMetrics;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Clear cache
   */
  public clearCache(): void {
    this.cache.clear();
    this.emit('cache_cleared');
  }

  /**
   * Disconnect and cleanup
   */
  public disconnect(): void {
    this.wsManager.disconnect();
    this.subscriptions.clear();
    this.cache.clear();
    this.isInitialized = false;
    this.removeAllListeners();
  }

  // === PRIVATE METHODS ===

  private setupWebSocketListeners(): void {
    this.wsManager.on('connected', () => {
      this.emit('connected');
      
      // Resubscribe to all active subscriptions
      for (const subscription of this.subscriptions.values()) {
        this.wsManager.send({
          type: 'analytics_subscribe',
          data: {
            subscription_id: subscription.id,
            metrics: subscription.metrics,
            filters: subscription.filters
          }
        });
      }
    });

    this.wsManager.on('disconnected', () => {
      this.emit('disconnected');
    });

    this.wsManager.on('error', (error: Error) => {
      this.emit('error', error);
    });

    this.wsManager.on('message', (message: WebSocketMessage) => {
      this.handleWebSocketMessage(message);
    });
  }

  private handleWebSocketMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'analytics_update':
        this.handleAnalyticsUpdate(message.data);
        break;
      
      case 'metric_alert':
        this.handleMetricAlert(message.data);
        break;
      
      case 'dashboard_refresh':
        this.handleDashboardRefresh(message.data);
        break;
      
      default:
        // Ignore unknown message types
        break;
    }
  }

  private handleAnalyticsUpdate(data: any): void {
    const { subscription_id, updates } = data;
    
    if (subscription_id && this.subscriptions.has(subscription_id)) {
      const subscription = this.subscriptions.get(subscription_id)!;
      subscription.callback(updates);
    }

    // Emit general update event
    this.emit('analytics_update', updates);

    // Invalidate relevant cache entries
    if (this.config.enableCaching) {
      this.invalidateCache(updates);
    }
  }

  private handleMetricAlert(data: any): void {
    this.emit('metric_alert', data);
  }

  private handleDashboardRefresh(data: any): void {
    this.emit('dashboard_refresh', data);
    
    // Clear dashboard cache to force refresh
    if (this.config.enableCaching) {
      this.cache.clear();
    }
  }

  private subscribeToDashboardUpdates(metricIds: string[]): void {
    this.wsManager.send({
      type: 'analytics_subscribe',
      data: {
        subscription_id: 'dashboard_auto',
        metrics: metricIds,
        filters: {}
      }
    });
  }

  private invalidateCache(updates: LiveMetricUpdate[]): void {
    for (const update of updates) {
      // Remove entries that might be affected by this update
      for (const [key] of this.cache['cache'].entries()) {
        if (key.includes(update.metricId)) {
          this.cache['cache'].delete(key);
        }
      }
    }
  }
}

// === REACT HOOK FOR REAL-TIME ANALYTICS ===

import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseRealTimeAnalyticsOptions {
  autoConnect?: boolean;
  enableCaching?: boolean;
  refreshInterval?: number;
}

export interface UseRealTimeAnalyticsReturn {
  service: RealTimeAnalyticsService;
  isConnected: boolean;
  isInitialized: boolean;
  getLiveDashboard: (filters?: Record<string, any>) => Promise<DashboardData>;
  getLiveMetrics: (metricIds: string[]) => Promise<MetricData[]>;
  getTimeSeriesData: (metricId: string, timeRange: string, granularity?: 'minute' | 'hour' | 'day') => Promise<TimeSeriesData[]>;
  subscribe: (metricIds: string[], callback: (updates: LiveMetricUpdate[]) => void) => string;
  unsubscribe: (subscriptionId: string) => void;
  clearCache: () => void;
}

export function useRealTimeAnalytics(
  config: RealTimeAnalyticsConfig,
  options: UseRealTimeAnalyticsOptions = {}
): UseRealTimeAnalyticsReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const serviceRef = useRef<RealTimeAnalyticsService | null>(null);

  // Initialize service
  useEffect(() => {
    serviceRef.current = new RealTimeAnalyticsService(config);
    const service = serviceRef.current;

    // Event listeners
    service.on('connected', () => setIsConnected(true));
    service.on('disconnected', () => setIsConnected(false));
    service.on('initialized', () => setIsInitialized(true));
    service.on('error', (error) => console.error('Analytics service error:', error));

    return () => {
      service.disconnect();
    };
  }, []);

  // Auto-initialize if requested
  useEffect(() => {
    if (options.autoConnect && serviceRef.current && !isInitialized) {
      // Get auth token from localStorage or context
      const authToken = localStorage.getItem('auth_token');
      if (authToken) {
        serviceRef.current.initialize(authToken).catch(console.error);
      }
    }
  }, [options.autoConnect, isInitialized]);

  const getLiveDashboard = useCallback(async (filters?: Record<string, any>) => {
    if (!serviceRef.current) throw new Error('Service not initialized');
    return serviceRef.current.getLiveDashboardData(filters);
  }, []);

  const getLiveMetrics = useCallback(async (metricIds: string[]) => {
    if (!serviceRef.current) throw new Error('Service not initialized');
    return serviceRef.current.getLiveMetrics(metricIds);
  }, []);

  const getTimeSeriesData = useCallback(async (metricId: string, timeRange: string, granularity?: 'minute' | 'hour' | 'day') => {
    if (!serviceRef.current) throw new Error('Service not initialized');
    return serviceRef.current.getTimeSeriesData(metricId, timeRange, granularity);
  }, []);

  const subscribe = useCallback((metricIds: string[], callback: (updates: LiveMetricUpdate[]) => void) => {
    if (!serviceRef.current) throw new Error('Service not initialized');
    return serviceRef.current.subscribe(metricIds, callback);
  }, []);

  const unsubscribe = useCallback((subscriptionId: string) => {
    if (!serviceRef.current) return;
    serviceRef.current.unsubscribe(subscriptionId);
  }, []);

  const clearCache = useCallback(() => {
    if (!serviceRef.current) return;
    serviceRef.current.clearCache();
  }, []);

  return {
    service: serviceRef.current!,
    isConnected,
    isInitialized,
    getLiveDashboard,
    getLiveMetrics,
    getTimeSeriesData,
    subscribe,
    unsubscribe,
    clearCache
  };
}

export default RealTimeAnalyticsService;