/**
 * Axios HTTP Adapter for Ainflue JavaScript SDK
 * Axios-based implementation with enterprise features and interceptors
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DevOps + Security + Lead Dev IA
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, HttpMethod, RequestOptions, HttpAdapter } from './interfaces';
import { ApiError, NetworkError, TimeoutError, RateLimitError, SecurityError } from './errors';

/**
 * Axios HTTP Adapter with enterprise-grade interceptors and monitoring
 */
export class AxiosAdapter implements HttpAdapter {
  private axiosInstance: AxiosInstance;
  private requestStartTimes: Map<string, number> = new Map();

  constructor(baseURL: string, defaultHeaders: Record<string, string> = {}, timeout: number = 30000) {
    this.axiosInstance = axios.create({
      baseURL: baseURL.replace(/\/$/, ''),
      timeout,
      headers: defaultHeaders,
      // Security configurations
      maxRedirects: 5,
      maxContentLength: 50 * 1024 * 1024, // 50MB
      maxBodyLength: 50 * 1024 * 1024, // 50MB
      validateStatus: (status) => status < 600, // Handle all HTTP responses
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors
   * Implementation: DevOps + Security + Lead Dev IA + Backend Senior
   */
  private setupInterceptors(): void {
    // Request interceptor for monitoring and security
    this.axiosInstance.interceptors.request.use(
      (config) => {
        // Generate unique request ID for tracking
        const requestId = this.generateRequestId();
        config.metadata = { requestId, startTime: Date.now() };
        this.requestStartTimes.set(requestId, performance.now());

        // Security validations
        this.validateRequestSecurity(config);

        // Add request tracing headers
        config.headers = {
          ...config.headers,
          'X-Request-ID': requestId,
          'X-SDK-Version': '1.0.0',
          'X-Request-Timestamp': new Date().toISOString(),
        };

        // Log outgoing requests (DevOps)
        this.logRequest(config);

        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(this.handleAxiosError(error));
      }
    );

    // Response interceptor for monitoring and error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        // Calculate request duration
        const requestId = response.config.metadata?.requestId;
        const startTime = this.requestStartTimes.get(requestId);
        if (startTime) {
          const duration = performance.now() - startTime;
          this.logResponseMetrics(response, duration);
          this.requestStartTimes.delete(requestId);
        }

        // Security: Validate response headers
        this.validateResponseSecurity(response);

        return response;
      },
      (error) => {
        // Handle request duration tracking for errors
        if (error.config?.metadata?.requestId) {
          this.requestStartTimes.delete(error.config.metadata.requestId);
        }

        return Promise.reject(this.handleAxiosError(error));
      }
    );
  }

  /**
   * Execute HTTP request using axios
   * Implementation: Backend Senior + DevOps
   */
  async request<T = any>(
    method: HttpMethod,
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    try {
      const config = this.buildAxiosConfig(method, endpoint, options);
      const response = await this.axiosInstance.request<T>(config);
      
      return this.transformAxiosResponse<T>(response);
    } catch (error) {
      throw this.handleAxiosError(error);
    }
  }

  /**
   * Build axios configuration from request options
   * Implementation: Backend Senior + Security
   */
  private buildAxiosConfig(
    method: HttpMethod,
    endpoint: string,
    options: RequestOptions
  ): AxiosRequestConfig {
    const config: AxiosRequestConfig = {
      method,
      url: endpoint,
      timeout: options.timeout,
      headers: options.headers,
    };

    // Handle request body based on content type
    if (options.body) {
      if (options.body instanceof FormData) {
        config.data = options.body;
        // Let axios set the correct Content-Type with boundary
        if (config.headers) {
          delete config.headers['Content-Type'];
        }
      } else {
        config.data = options.body;
      }
    }

    // Configure response type based on expected content
    if (options.responseType) {
      config.responseType = options.responseType;
    }

    // Configure upload progress tracking
    if (options.onUploadProgress) {
      config.onUploadProgress = options.onUploadProgress;
    }

    // Configure download progress tracking
    if (options.onDownloadProgress) {
      config.onDownloadProgress = options.onDownloadProgress;
    }

    return config;
  }

  /**
   * Transform axios response to SDK response format
   * Implementation: Backend Senior
   */
  private transformAxiosResponse<T>(response: AxiosResponse<T>): ApiResponse<T> {
    return {
      data: response.data,
      status: response.status,
      statusText: response.statusText,
      headers: this.normalizeHeaders(response.headers),
      success: response.status >= 200 && response.status < 300,
    };
  }

  /**
   * Handle axios errors and convert to SDK errors
   * Implementation: Backend Senior + Security + DevOps
   */
  private handleAxiosError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      // Handle timeout errors
      if (axiosError.code === 'ECONNABORTED' || axiosError.message.includes('timeout')) {
        return new TimeoutError(`Request timeout: ${axiosError.message}`);
      }

      // Handle network errors
      if (axiosError.code === 'ERR_NETWORK' || !axiosError.response) {
        return new NetworkError(`Network error: ${axiosError.message}`);
      }

      // Handle HTTP errors with response
      if (axiosError.response) {
        const { status, data, headers } = axiosError.response;
        
        // Handle rate limiting
        if (status === 429) {
          const retryAfter = headers['retry-after'] ? parseInt(headers['retry-after']) : undefined;
          const limit = headers['x-ratelimit-limit'];
          const remaining = headers['x-ratelimit-remaining'];
          
          return new RateLimitError(
            data?.message || 'Rate limit exceeded',
            retryAfter,
            limit,
            remaining
          );
        }

        // Extract error message from response
        let message = 'Request failed';
        if (typeof data === 'object' && data !== null) {
          message = data.message || data.error || data.detail || message;
        } else if (typeof data === 'string') {
          message = data;
        }

        return new ApiError(message, status, data);
      }
    }

    // Handle other error types
    if (error.name === 'SecurityError') {
      return new SecurityError(error.message);
    }

    // Default error handling
    return new ApiError(error.message || 'Unknown error occurred', 0);
  }

  /**
   * Validate request security
   * Implementation: Security + Lead Dev IA
   */
  private validateRequestSecurity(config: AxiosRequestConfig): void {
    // Protocol validation
    const url = config.url || '';
    const baseURL = config.baseURL || '';
    const fullUrl = url.startsWith('http') ? url : `${baseURL}${url}`;
    
    if (!fullUrl.startsWith('https://') && !fullUrl.includes('localhost')) {
      throw new SecurityError('Only HTTPS requests are allowed in production');
    }

    // Header validation
    if (config.headers) {
      for (const [key, value] of Object.entries(config.headers)) {
        if (typeof value === 'string' && value.length > 8192) {
          throw new SecurityError(`Header ${key} exceeds maximum length`);
        }
      }
    }

    // Data size validation
    if (config.data && this.calculateDataSize(config.data) > 50 * 1024 * 1024) {
      throw new ApiError('Request data too large', 413);
    }
  }

  /**
   * Validate response security headers
   * Implementation: Security + DevOps
   */
  private validateResponseSecurity(response: AxiosResponse): void {
    const headers = response.headers;
    const url = response.config.url || '';

    // Check for security headers
    const securityHeaders = {
      'x-content-type-options': 'nosniff',
      'x-frame-options': ['DENY', 'SAMEORIGIN'],
      'strict-transport-security': true,
    };

    const warnings: string[] = [];

    for (const [header, expectedValue] of Object.entries(securityHeaders)) {
      const headerValue = headers[header];
      
      if (!headerValue) {
        warnings.push(`Missing security header: ${header}`);
      } else if (Array.isArray(expectedValue)) {
        if (!expectedValue.includes(headerValue.toUpperCase())) {
          warnings.push(`Invalid ${header} value: ${headerValue}`);
        }
      } else if (typeof expectedValue === 'string' && headerValue !== expectedValue) {
        warnings.push(`Invalid ${header} value: ${headerValue}`);
      }
    }

    if (warnings.length > 0) {
      console.warn(`Security header warnings for ${url}:`, warnings);
    }
  }

  /**
   * Calculate data size for validation
   * Implementation: Security + Backend Senior
   */
  private calculateDataSize(data: any): number {
    if (data instanceof FormData) {
      // FormData size estimation
      let size = 0;
      try {
        for (const [, value] of data.entries()) {
          if (value instanceof File) {
            size += value.size;
          } else {
            size += new Blob([value.toString()]).size;
          }
        }
      } catch {
        // Fallback estimation
        size = 1024; // Assume 1KB for FormData that can't be measured
      }
      return size;
    } else if (typeof data === 'string') {
      return new Blob([data]).size;
    } else if (data instanceof Blob) {
      return data.size;
    } else if (typeof data === 'object' && data !== null) {
      return new Blob([JSON.stringify(data)]).size;
    }
    return 0;
  }

  /**
   * Generate unique request ID for tracking
   * Implementation: DevOps + Lead Dev IA
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Log request for monitoring
   * Implementation: DevOps + Security
   */
  private logRequest(config: AxiosRequestConfig): void {
    const sanitizedConfig = {
      method: config.method?.toUpperCase(),
      url: config.url,
      headers: this.sanitizeHeaders(config.headers || {}),
      requestId: config.metadata?.requestId,
    };

    console.debug('Outgoing request:', sanitizedConfig);
  }

  /**
   * Log response metrics for monitoring
   * Implementation: DevOps + Lead Dev IA
   */
  private logResponseMetrics(response: AxiosResponse, duration: number): void {
    const metrics = {
      requestId: response.config.metadata?.requestId,
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      duration: Math.round(duration),
      size: this.calculateResponseSize(response),
      timestamp: new Date().toISOString(),
    };

    // Log performance warnings
    if (duration > 10000) { // 10 seconds
      console.warn('Very slow request detected:', metrics);
    } else if (duration > 5000) { // 5 seconds
      console.warn('Slow request detected:', metrics);
    } else {
      console.debug('Response metrics:', metrics);
    }
  }

  /**
   * Calculate response size for monitoring
   * Implementation: DevOps
   */
  private calculateResponseSize(response: AxiosResponse): number {
    const contentLength = response.headers['content-length'];
    if (contentLength) {
      return parseInt(contentLength, 10);
    }
    
    // Estimate size from data
    if (typeof response.data === 'string') {
      return response.data.length;
    } else if (typeof response.data === 'object') {
      return JSON.stringify(response.data).length;
    }
    
    return 0;
  }

  /**
   * Sanitize headers for logging (remove sensitive data)
   * Implementation: Security
   */
  private sanitizeHeaders(headers: Record<string, any>): Record<string, string> {
    const sensitiveHeaders = ['authorization', 'x-api-key', 'cookie', 'x-auth-token'];
    const sanitized: Record<string, string> = {};

    for (const [key, value] of Object.entries(headers)) {
      if (sensitiveHeaders.includes(key.toLowerCase())) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = String(value);
      }
    }

    return sanitized;
  }

  /**
   * Normalize response headers to lowercase keys
   * Implementation: Backend Senior
   */
  private normalizeHeaders(headers: any): Record<string, string> {
    const normalized: Record<string, string> = {};
    
    for (const [key, value] of Object.entries(headers)) {
      normalized[key.toLowerCase()] = String(value);
    }
    
    return normalized;
  }

  // Convenience methods
  async get<T = any>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, options);
  }

  async post<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, { ...options, body: data });
  }

  async put<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, { ...options, body: data });
  }

  async delete<T = any>(endpoint: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint, options);
  }

  async patch<T = any>(endpoint: string, data?: any, options?: RequestOptions): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', endpoint, { ...options, body: data });
  }
}