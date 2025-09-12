/**
 * Fetch API Adapter for Ainflue JavaScript SDK
 * Native browser fetch implementation with enterprise-grade features
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DevOps + Security + Lead Dev IA
 */

import { ApiResponse, HttpMethod, RequestOptions, HttpAdapter } from './interfaces';
import { ApiError, NetworkError, TimeoutError, SecurityError } from './errors';

/**
 * Fetch API Adapter with enterprise security and performance optimizations
 */
export class FetchAdapter implements HttpAdapter {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private defaultTimeout: number;

  constructor(baseURL: string, defaultHeaders: Record<string, string> = {}, timeout: number = 30000) {
    this.baseURL = baseURL.replace(/\/$/, '');
    this.defaultHeaders = defaultHeaders;
    this.defaultTimeout = timeout;
  }

  /**
   * Execute HTTP request using native fetch API
   * Implementation: Backend Senior + Security + DevOps
   */
  async request<T = any>(
    method: HttpMethod,
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeout = options.timeout || this.defaultTimeout;
    
    // Set request timeout
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      // Security: Validate and sanitize request
      this.validateRequest(url, options);

      const fetchOptions = this.buildFetchOptions(method, options, controller.signal);
      
      // Execute request with performance monitoring
      const startTime = performance.now();
      const response = await fetch(url, fetchOptions);
      const endTime = performance.now();
      
      clearTimeout(timeoutId);

      // Log performance metrics (DevOps)
      this.logRequestMetrics(method, url, endTime - startTime, response.status);

      // Parse and return response
      return await this.parseResponse<T>(response, url);

    } catch (error) {
      clearTimeout(timeoutId);
      throw this.handleError(error, url, method);
    }
  }

  /**
   * Build fetch options with security hardening
   * Implementation: Security + Backend Senior
   */
  private buildFetchOptions(
    method: HttpMethod,
    options: RequestOptions,
    signal: AbortSignal
  ): RequestInit {
    const headers = {
      ...this.defaultHeaders,
      ...options.headers,
    };

    // Security: Remove sensitive headers from logs
    this.sanitizeHeadersForLogging(headers);

    const fetchOptions: RequestInit = {
      method,
      headers,
      signal,
      // Security: Configure CORS and credentials
      mode: 'cors',
      credentials: 'same-origin',
      // Security: Disable cache for sensitive requests
      cache: this.shouldCache(options) ? 'default' : 'no-cache',
      // Security: Enable redirect following with limits
      redirect: 'follow',
    };

    // Add request body if present
    if (options.body) {
      if (options.body instanceof FormData) {
        // Don't set Content-Type for FormData, let browser set it
        delete headers['Content-Type'];
        fetchOptions.body = options.body;
      } else if (typeof options.body === 'object') {
        fetchOptions.body = JSON.stringify(options.body);
      } else {
        fetchOptions.body = options.body;
      }
    }

    return fetchOptions;
  }

  /**
   * Parse HTTP response with comprehensive error handling
   * Implementation: Backend Senior + Security
   */
  private async parseResponse<T>(response: Response, url: string): Promise<ApiResponse<T>> {
    const headers = this.parseResponseHeaders(response.headers);
    
    // Check for security headers (Security)
    this.validateSecurityHeaders(headers, url);

    if (!response.ok) {
      const errorData = await this.extractErrorData(response);
      throw new ApiError(
        errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    const contentType = response.headers.get('content-type') || '';
    let data: T;

    try {
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else if (contentType.includes('text/')) {
        data = (await response.text()) as unknown as T;
      } else if (contentType.includes('application/octet-stream') || contentType.includes('image/') || contentType.includes('video/')) {
        data = (await response.blob()) as unknown as T;
      } else {
        // Default to JSON parsing
        const text = await response.text();
        try {
          data = JSON.parse(text);
        } catch {
          data = text as unknown as T;
        }
      }
    } catch (parseError) {
      throw new ApiError(
        `Failed to parse response: ${parseError.message}`,
        response.status,
        { parseError: parseError.message }
      );
    }

    return {
      data,
      status: response.status,
      statusText: response.statusText,
      headers,
      success: true,
    };
  }

  /**
   * Extract error data from failed response
   * Implementation: Backend Senior + Security
   */
  private async extractErrorData(response: Response): Promise<any> {
    try {
      const contentType = response.headers.get('content-type') || '';
      
      if (contentType.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return { message: text || response.statusText };
      }
    } catch {
      return { message: response.statusText || 'Unknown error' };
    }
  }

  /**
   * Handle and classify errors
   * Implementation: DevOps + Security + Backend Senior
   */
  private handleError(error: any, url: string, method: HttpMethod): Error {
    // Handle abort errors (timeout)
    if (error.name === 'AbortError') {
      return new TimeoutError(`Request timeout for ${method} ${url}`);
    }

    // Handle network errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new NetworkError(`Network error for ${method} ${url}: ${error.message}`);
    }

    // Handle security errors
    if (error.name === 'SecurityError') {
      return new SecurityError(`Security error for ${method} ${url}: ${error.message}`);
    }

    // Pass through existing SDK errors
    if (error instanceof ApiError || error instanceof NetworkError || error instanceof TimeoutError) {
      return error;
    }

    // Default error handling
    return new ApiError(`Request failed for ${method} ${url}: ${error.message}`, 0);
  }

  /**
   * Validate request for security compliance
   * Implementation: Security + Lead Dev IA
   */
  private validateRequest(url: string, options: RequestOptions): void {
    // Protocol validation
    if (!url.startsWith('https://') && !url.includes('localhost')) {
      throw new SecurityError('Only HTTPS requests are allowed in production');
    }

    // Request size validation
    if (options.body) {
      const bodySize = this.calculateBodySize(options.body);
      if (bodySize > 50 * 1024 * 1024) { // 50MB limit
        throw new ApiError('Request body too large', 413);
      }
    }

    // Header validation
    if (options.headers) {
      for (const [key, value] of Object.entries(options.headers)) {
        if (typeof value === 'string' && value.length > 8192) { // 8KB header limit
          throw new SecurityError(`Header ${key} too large`);
        }
      }
    }
  }

  /**
   * Validate security headers in response
   * Implementation: Security + DevOps
   */
  private validateSecurityHeaders(headers: Record<string, string>, url: string): void {
    const requiredSecurityHeaders = [
      'x-content-type-options',
      'x-frame-options',
      'strict-transport-security'
    ];

    // Log missing security headers for monitoring
    const missingHeaders = requiredSecurityHeaders.filter(header => !headers[header]);
    if (missingHeaders.length > 0) {
      console.warn(`Missing security headers for ${url}:`, missingHeaders);
    }

    // Check for security violations
    const contentType = headers['content-type'] || '';
    if (contentType.includes('text/html') && !headers['x-content-type-options']) {
      console.warn(`Potential MIME sniffing vulnerability for ${url}`);
    }
  }

  /**
   * Parse response headers into plain object
   * Implementation: Backend Senior
   */
  private parseResponseHeaders(headers: Headers): Record<string, string> {
    const headerObject: Record<string, string> = {};
    headers.forEach((value, key) => {
      headerObject[key.toLowerCase()] = value;
    });
    return headerObject;
  }

  /**
   * Calculate request body size for validation
   * Implementation: Security + Backend Senior
   */
  private calculateBodySize(body: any): number {
    if (body instanceof FormData) {
      // Approximate size calculation for FormData
      let size = 0;
      for (const [, value] of body.entries()) {
        if (value instanceof File) {
          size += value.size;
        } else {
          size += new Blob([value]).size;
        }
      }
      return size;
    } else if (typeof body === 'string') {
      return new Blob([body]).size;
    } else if (body instanceof Blob) {
      return body.size;
    } else if (typeof body === 'object') {
      return new Blob([JSON.stringify(body)]).size;
    }
    return 0;
  }

  /**
   * Sanitize headers for logging (remove sensitive data)
   * Implementation: Security
   */
  private sanitizeHeadersForLogging(headers: Record<string, string>): void {
    const sensitiveHeaders = ['authorization', 'x-api-key', 'cookie', 'x-auth-token'];
    
    for (const key of Object.keys(headers)) {
      if (sensitiveHeaders.includes(key.toLowerCase())) {
        // Keep header present but hide value in logs
        console.debug(`Request header ${key}: [REDACTED]`);
      }
    }
  }

  /**
   * Determine if request should be cached
   * Implementation: DevOps + Backend Senior
   */
  private shouldCache(options: RequestOptions): boolean {
    // Don't cache requests with authentication or sensitive data
    if (options.headers?.authorization || options.headers?.['x-api-key']) {
      return false;
    }

    // Don't cache POST, PUT, DELETE requests
    return false; // Conservative approach for SDK
  }

  /**
   * Log request performance metrics
   * Implementation: DevOps + Lead Dev IA
   */
  private logRequestMetrics(method: HttpMethod, url: string, duration: number, status: number): void {
    const metrics = {
      method,
      url: url.replace(/\/\d+/g, '/:id'), // Normalize URLs with IDs
      duration: Math.round(duration),
      status,
      timestamp: new Date().toISOString(),
    };

    // Log slow requests for monitoring
    if (duration > 5000) { // 5 seconds
      console.warn('Slow request detected:', metrics);
    } else if (duration > 1000) { // 1 second
      console.info('Request metrics:', metrics);
    }
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