// Frontend API Client - IA Chéries Platform
// Author: Fahed Mlaiel (mlaiel@live.de)
// Role: Backend Senior + Lead Dev IA 
// Purpose: Enterprise API client with authentication and WebSocket support

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Types for API responses
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: string[];
  timestamp: string;
}

export interface MetricsData {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number;
  timestamp: string;
}

export interface AnalyticsData {
  content_id: string;
  date: string;
  metrics: {
    views: number;
    unique_views: number;
    likes: number;
    comments: number;
    shares: number;
    watch_time_seconds: number;
    click_through_rate: number;
    bounce_rate: number;
  };
  demographics: {
    age_groups: Record<string, number>;
    gender: Record<string, number>;
    top_countries: Array<{country: string; percentage: number}>;
  };
  revenue: {
    ad_revenue: number;
    subscription_revenue: number;
    merchandise_revenue: number;
    sponsorship_revenue: number;
  };
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name: string;
  bio: string;
  creator_type: string;
  verified: boolean;
  followers_count: number;
  following_count: number;
  content_count: number;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

class ApiClient {
  private axiosInstance: AxiosInstance;
  private wsConnections: Map<string, WebSocket> = new Map();
  private authToken: string | null = null;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          await this.refreshToken();
          return this.axiosInstance.request(error.config);
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<ApiResponse<{token: string; user: UserProfile}>> {
    try {
      const response = await this.axiosInstance.post('/auth/login', {
        email,
        password
      });
      
      if (response.data.success && response.data.data.token) {
        this.setAuthToken(response.data.data.token);
      }
      
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async refreshToken(): Promise<void> {
    try {
      const response = await this.axiosInstance.post('/auth/refresh');
      if (response.data.success && response.data.data.token) {
        this.setAuthToken(response.data.data.token);
      }
    } catch (error) {
      // Refresh failed, clear token and redirect to login
      this.clearAuthToken();
      window.location.href = '/login';
    }
  }

  setAuthToken(token: string) {
    this.authToken = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('ainflue_auth_token', token);
    }
  }

  clearAuthToken() {
    this.authToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('ainflue_auth_token');
    }
  }

  loadAuthToken() {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('ainflue_auth_token');
      if (token) {
        this.authToken = token;
      }
    }
  }

  // Analytics API
  async getMetrics(metricId: string, timeRange: string = '24h'): Promise<ApiResponse<MetricsData[]>> {
    try {
      const response = await this.axiosInstance.get(`/analytics/metrics/${metricId}`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getLiveMetrics(): Promise<ApiResponse<MetricsData[]>> {
    try {
      const response = await this.axiosInstance.get('/analytics/metrics/live');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async getDashboardAnalytics(contentId?: string, dateRange?: string): Promise<ApiResponse<AnalyticsData[]>> {
    try {
      const params: any = {};
      if (contentId) params.content_id = contentId;
      if (dateRange) params.date_range = dateRange;

      const response = await this.axiosInstance.get('/analytics/dashboard', { params });
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // User API
  async getCurrentUser(): Promise<ApiResponse<UserProfile>> {
    try {
      const response = await this.axiosInstance.get('/users/me');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  async updateProfile(profileData: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    try {
      const response = await this.axiosInstance.put('/users/me', profileData);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // WebSocket connections
  connectWebSocket(endpoint: string, onMessage?: (message: WebSocketMessage) => void): WebSocket {
    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765') + endpoint;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log(`WebSocket connected: ${endpoint}`);
      
      // Send authentication if token available
      if (this.authToken) {
        ws.send(JSON.stringify({
          type: 'authenticate',
          token: this.authToken
        }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        if (onMessage) {
          onMessage(message);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${endpoint}:`, error);
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected: ${endpoint}`);
      // Auto-reconnect after 3 seconds
      setTimeout(() => {
        if (!this.wsConnections.has(endpoint)) {
          this.connectWebSocket(endpoint, onMessage);
        }
      }, 3000);
    };

    this.wsConnections.set(endpoint, ws);
    return ws;
  }

  disconnectWebSocket(endpoint: string) {
    const ws = this.wsConnections.get(endpoint);
    if (ws) {
      ws.close();
      this.wsConnections.delete(endpoint);
    }
  }

  disconnectAllWebSockets() {
    this.wsConnections.forEach((ws, endpoint) => {
      ws.close();
    });
    this.wsConnections.clear();
  }

  // Error handling
  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || `HTTP ${error.response.status}: ${error.response.statusText}`;
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Network error: Please check your connection');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred');
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{status: string; timestamp: string}>> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Load auth token on initialization
if (typeof window !== 'undefined') {
  apiClient.loadAuthToken();
}

export default apiClient;