/**
 * 🔧 IA Chéries API Client - Enterprise HTTP Client
 * 
 * @fileoverview Configured HTTP client for backend API integration
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Backend Senior + Lead Dev IA Expert
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// === API CLIENT CONFIGURATION ===

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  withCredentials: boolean;
  headers: Record<string, string>;
}

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
  timestamp: string;
  success: boolean;
}

export interface ApiError {
  error: boolean;
  status_code: number;
  message: string;
  timestamp: string;
  path: string;
  service: string;
}

// === API CLIENT CLASS ===

class ApiClient {
  private instance: AxiosInstance;
  private authToken: string | null = null;

  constructor(config: Partial<ApiClientConfig> = {}) {
    const defaultConfig: ApiClientConfig = {
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Client-Version': '2.0.0',
        'X-Client-Platform': 'web',
      },
    };

    const finalConfig = { ...defaultConfig, ...config };

    this.instance = axios.create(finalConfig);
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for authentication
    this.instance.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        // Add request timestamp
        config.headers['X-Request-Timestamp'] = new Date().toISOString();
        
        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await this.refreshToken();
            return this.instance(originalRequest);
          } catch (refreshError) {
            console.error('❌ Token refresh failed:', refreshError);
            this.handleAuthenticationError();
            return Promise.reject(refreshError);
          }
        }

        // Handle 429 errors (rate limiting)
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          console.warn(`⏰ Rate limited. Retry after: ${retryAfter} seconds`);
        }

        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private formatError(error: any): ApiError {
    if (error.response?.data) {
      return error.response.data as ApiError;
    }

    return {
      error: true,
      status_code: error.response?.status || 500,
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString(),
      path: error.config?.url || 'unknown',
      service: 'api_client'
    };
  }

  private async refreshToken(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await this.instance.post('/auth/refresh', {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      this.setAuthToken(access_token);
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', newRefreshToken);
      
      console.log('✅ Token refreshed successfully');
    } catch (error) {
      console.error('❌ Token refresh failed:', error);
      throw error;
    }
  }

  private handleAuthenticationError(): void {
    this.clearAuthToken();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Redirect to login or trigger auth event
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:logout', { 
        detail: { reason: 'token_expired' } 
      }));
    }
  }

  // === PUBLIC METHODS ===

  public setAuthToken(token: string): void {
    this.authToken = token;
    localStorage.setItem('access_token', token);
  }

  public clearAuthToken(): void {
    this.authToken = null;
    localStorage.removeItem('access_token');
  }

  public getAuthToken(): string | null {
    return this.authToken || localStorage.getItem('access_token');
  }

  // === HTTP METHODS ===

  public async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.get(url, config);
    return response.data;
  }

  public async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.post(url, data, config);
    return response.data;
  }

  public async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.put(url, data, config);
    return response.data;
  }

  public async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.patch(url, data, config);
    return response.data;
  }

  public async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.instance.delete(url, config);
    return response.data;
  }

  // === FILE UPLOAD ===

  public async uploadFile<T = any>(
    url: string, 
    file: File, 
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.instance.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });

    return response.data;
  }

  // === HEALTH CHECK ===

  public async healthCheck(): Promise<ApiResponse<any>> {
    return this.get('/health');
  }

  public async detailedHealthCheck(): Promise<ApiResponse<any>> {
    return this.get('/health/detailed');
  }
}

// === SINGLETON INSTANCE ===

const apiClient = new ApiClient();

// Initialize auth token from localStorage
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('access_token');
  if (token) {
    apiClient.setAuthToken(token);
  }
}

export default apiClient;
export { ApiClient };

// Types are already exported with their declarations above