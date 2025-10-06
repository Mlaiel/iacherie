/**
 * Type-Safe API Client - Production Grade
 * Handles authentication, retry logic, circuit breaker
 * @module lib/api/client
 */

import { retryWithBackoff } from '@/lib/utils';

/**
 * API Client Configuration
 */
interface APIClientConfig {
  baseURL: string;
  timeout: number;
  maxRetries: number;
  headers?: Record<string, string>;
}

/**
 * API Response wrapper
 */
interface APIResponse<T> {
  data: T;
  status: number;
  headers: Headers;
}

/**
 * API Error with detailed information
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Circuit Breaker for API resilience
 */
class CircuitBreaker {
  private failures = 0;
  private lastFailureTime = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  
  constructor(
    private threshold: number = 5,
    private timeout: number = 60000
  ) {}
  
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }
  
  private onFailure() {
    this.failures++;
    this.lastFailureTime = Date.now();
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}

/**
 * Production-Grade API Client
 */
export class APIClient {
  private config: APIClientConfig;
  private circuitBreaker: CircuitBreaker;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  
  constructor(config: Partial<APIClientConfig> = {}) {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
      timeout: 30000,
      maxRetries: 3,
      ...config,
    };
    this.circuitBreaker = new CircuitBreaker();
  }
  
  /**
   * Set authentication tokens
   */
  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }
  
  /**
   * Clear authentication
   */
  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
  }
  
  /**
   * Build request headers
   */
  private buildHeaders(customHeaders?: Record<string, string>): HeadersInit {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.config.headers,
      ...customHeaders,
    };
    
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }
    
    return headers;
  }
  
  /**
   * Execute HTTP request with retry and circuit breaker
   */
  private async request<T>(
    method: string,
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.config.baseURL}${endpoint}`;
    
    const executeRequest = async (): Promise<APIResponse<T>> => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
      
      try {
        const response = await fetch(url, {
          method,
          headers: this.buildHeaders(options.headers as Record<string, string>),
          body: options.body,
          signal: controller.signal,
          ...options,
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new APIError(
            error.message || `HTTP ${response.status}`,
            response.status,
            error.code,
            error.details
          );
        }
        
        const data = await response.json();
        
        return {
          data,
          status: response.status,
          headers: response.headers,
        };
      } catch (error: any) {
        if (error.name === 'AbortError') {
          throw new APIError('Request timeout', 408);
        }
        throw error;
      } finally {
        clearTimeout(timeoutId);
      }
    };
    
    return this.circuitBreaker.execute(() =>
      retryWithBackoff(executeRequest, this.config.maxRetries)
    );
  }
  
  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const queryString = params
      ? '?' + new URLSearchParams(params).toString()
      : '';
    const { data } = await this.request<T>('GET', `${endpoint}${queryString}`);
    return data;
  }
  
  /**
   * POST request
   */
  async post<T>(endpoint: string, body?: any): Promise<T> {
    const { data } = await this.request<T>('POST', endpoint, {
      body: JSON.stringify(body),
    });
    return data;
  }
  
  /**
   * PUT request
   */
  async put<T>(endpoint: string, body?: any): Promise<T> {
    const { data } = await this.request<T>('PUT', endpoint, {
      body: JSON.stringify(body),
    });
    return data;
  }
  
  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, body?: any): Promise<T> {
    const { data } = await this.request<T>('PATCH', endpoint, {
      body: JSON.stringify(body),
    });
    return data;
  }
  
  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    const { data } = await this.request<T>('DELETE', endpoint);
    return data;
  }
  
  /**
   * Upload file with progress
   */
  async uploadFile<T>(
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            onProgress((e.loaded / e.total) * 100);
          }
        });
      }
      
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new APIError('Upload failed', xhr.status));
        }
      });
      
      xhr.addEventListener('error', () => {
        reject(new APIError('Network error', 0));
      });
      
      xhr.open('POST', `${this.config.baseURL}${endpoint}`);
      if (this.accessToken) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.accessToken}`);
      }
      xhr.send(formData);
    });
  }
}

/**
 * Singleton API client instance
 */
export const apiClient = new APIClient();
