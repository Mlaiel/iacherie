/**
 * 📊 Analytics API Service - Business Intelligence Integration
 * 
 * @fileoverview Analytics API integration with real-time metrics
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role ML Engineer + Backend Senior Expert
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import apiClient, { ApiResponse } from './apiClient';

// === ANALYTICS INTERFACES ===

export interface MetricData {
  id: string;
  name: string;
  value: number;
  unit: 'currency' | 'percentage' | 'count' | 'time' | 'bytes' | 'rate';
  timestamp: string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'stable';
  category: 'revenue' | 'engagement' | 'performance' | 'content' | 'user' | 'technical';
  metadata?: Record<string, any>;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}

export interface AnalyticsQuery {
  metrics: string[];
  timeRange: string;
  granularity?: 'minute' | 'hour' | 'day' | 'week' | 'month';
  filters?: Record<string, any>;
  aggregation?: 'sum' | 'avg' | 'max' | 'min' | 'count';
}

export interface DashboardData {
  metrics: MetricData[];
  timeSeries: Record<string, TimeSeriesData[]>;
  summary: {
    totalRevenue: number;
    totalViews: number;
    activeUsers: number;
    conversionRate: number;
  };
  alerts: AlertData[];
}

export interface AlertData {
  id: string;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  actionRequired?: boolean;
}

export interface PerformanceMetrics {
  cpu: number;
  memory: number;
  network: number;
  responseTime: number;
  errorRate: number;
  throughput: number;
}

export interface ContentAnalytics {
  contentId: string;
  views: number;
  engagement: number;
  revenue: number;
  distribution: {
    platform: string;
    views: number;
    engagement: number;
  }[];
  demographics: {
    ageGroup: string;
    percentage: number;
  }[];
}

// === ANALYTICS API SERVICE ===

class AnalyticsApiService {
  private baseUrl = '/analytics';

  // === METRICS ===

  /**
   * Get live metrics for dashboard
   */
  async getLiveMetrics(): Promise<MetricData[]> {
    try {
      const response = await apiClient.get<MetricData[]>(`${this.baseUrl}/metrics/live`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch live metrics:', error);
      // Return mock data as fallback for development
      return this.getMockMetrics();
    }
  }

  /**
   * Get specific metric by ID
   */
  async getMetric(metricId: string, timeRange: string = '24h'): Promise<MetricData> {
    try {
      const response = await apiClient.get<MetricData>(`${this.baseUrl}/metrics/${metricId}`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch metric ${metricId}:`, error);
      throw error;
    }
  }

  /**
   * Get metrics by category
   */
  async getMetricsByCategory(category: string, timeRange: string = '24h'): Promise<MetricData[]> {
    try {
      const response = await apiClient.get<MetricData[]>(`${this.baseUrl}/metrics/category/${category}`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch metrics for category ${category}:`, error);
      return [];
    }
  }

  // === TIME SERIES ===

  /**
   * Get time series data for metrics
   */
  async getTimeSeries(metricIds: string[], timeRange: string = '24h'): Promise<Record<string, TimeSeriesData[]>> {
    try {
      const response = await apiClient.post<Record<string, TimeSeriesData[]>>(`${this.baseUrl}/timeseries`, {
        metricIds,
        timeRange
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch time series data:', error);
      return {};
    }
  }

  // === DASHBOARD ===

  /**
   * Get complete dashboard data
   */
  async getDashboardData(dashboardType: string = 'overview'): Promise<DashboardData> {
    try {
      const response = await apiClient.get<DashboardData>(`${this.baseUrl}/dashboard/${dashboardType}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch dashboard data for ${dashboardType}:`, error);
      return this.getMockDashboardData();
    }
  }

  // === PERFORMANCE ===

  /**
   * Get system performance metrics
   */
  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    try {
      const response = await apiClient.get<PerformanceMetrics>(`${this.baseUrl}/performance`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
      return this.getMockPerformanceMetrics();
    }
  }

  // === CONTENT ANALYTICS ===

  /**
   * Get content analytics
   */
  async getContentAnalytics(contentId: string): Promise<ContentAnalytics> {
    try {
      const response = await apiClient.get<ContentAnalytics>(`${this.baseUrl}/content/${contentId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch content analytics for ${contentId}:`, error);
      throw error;
    }
  }

  // === CUSTOM QUERIES ===

  /**
   * Execute custom analytics query
   */
  async executeQuery(query: AnalyticsQuery): Promise<any> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/query`, query);
      return response.data;
    } catch (error) {
      console.error('Failed to execute analytics query:', error);
      throw error;
    }
  }

  // === MOCK DATA (FALLBACK FOR DEVELOPMENT) ===

  private getMockMetrics(): MetricData[] {
    return [
      {
        id: 'total_revenue',
        name: 'Total Revenue',
        value: 45750.80,
        unit: 'currency',
        timestamp: new Date().toISOString(),
        change: 12.5,
        changeType: 'increase',
        category: 'revenue',
        metadata: { currency: 'EUR' }
      },
      {
        id: 'active_users',
        name: 'Active Users',
        value: 1247,
        unit: 'count',
        timestamp: new Date().toISOString(),
        change: 8.3,
        changeType: 'increase',
        category: 'user'
      },
      {
        id: 'content_views',
        name: 'Content Views',
        value: 89634,
        unit: 'count',
        timestamp: new Date().toISOString(),
        change: -2.1,
        changeType: 'decrease',
        category: 'engagement'
      },
      {
        id: 'api_response_time',
        name: 'API Response Time',
        value: 145,
        unit: 'time',
        timestamp: new Date().toISOString(),
        change: 0.5,
        changeType: 'stable',
        category: 'performance',
        metadata: { unit: 'ms' }
      }
    ];
  }

  private getMockDashboardData(): DashboardData {
    return {
      metrics: this.getMockMetrics(),
      timeSeries: {
        revenue: Array.from({ length: 24 }, (_, i) => ({
          timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
          value: Math.random() * 1000 + 500
        })),
        users: Array.from({ length: 24 }, (_, i) => ({
          timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
          value: Math.random() * 100 + 50
        }))
      },
      summary: {
        totalRevenue: 45750.80,
        totalViews: 89634,
        activeUsers: 1247,
        conversionRate: 3.2
      },
      alerts: [
        {
          id: 'alert_1',
          type: 'warning',
          title: 'High API Response Time',
          message: 'API response time has increased by 15% in the last hour',
          timestamp: new Date().toISOString(),
          isRead: false,
          actionRequired: true
        }
      ]
    };
  }

  private getMockPerformanceMetrics(): PerformanceMetrics {
    return {
      cpu: Math.random() * 50 + 25,
      memory: Math.random() * 40 + 30,
      network: Math.random() * 100 + 50,
      responseTime: Math.random() * 100 + 100,
      errorRate: Math.random() * 2,
      throughput: Math.random() * 1000 + 500
    };
  }
}

// === SINGLETON INSTANCE ===

const analyticsApi = new AnalyticsApiService();

export default analyticsApi;
export { AnalyticsApiService };

// Types are already exported with their declarations above