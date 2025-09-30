/**
 * HTTP Client Implementation for Ainflue JavaScript SDK
 * Provides robust HTTP communication with retry logic and error handling
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + Security + DevOps + Lead Dev IA
 */

import { AinflueConfig } from './config';
import { ApiError, NetworkError, TimeoutError } from './errors';
import { ApiResponse, HttpMethod, RequestOptions } from './interfaces';

export class HttpClient {
  private config: AinflueConfig;
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(config: AinflueConfig) {
    this.config = config;
    this.baseURL = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'User-Agent': `ainflue-js-sdk/${config.version || '1.0.0'}`,
      'Accept': 'application/json',
    };

    if (config.apiKey) {
      this.defaultHeaders['Authorization'] = `Bearer ${config.apiKey}`;
    }
  }

  /**
   * Execute HTTP request with enterprise-grade retry logic and error handling
   * Implementation: Backend Senior + DevOps + Security
   */
  async request<T = any>(
    method: HttpMethod,
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const { retries = this.config.maxRetries, timeout = this.config.timeout } = options;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await this.executeRequest<T>(method, url, options, timeout);
        return response;
      } catch (error) {
        if (attempt === retries) {
          throw error;
        }

        // Intelligent retry logic (Lead Dev IA)
        if (this.shouldRetry(error, attempt)) {
          const delay = this.calculateBackoffDelay(attempt);
          await this.sleep(delay);
          continue;
        }

        throw error;
      }
    }

    throw new Error('Maximum retries exceeded');
  }

  /**
   * Execute single HTTP request with comprehensive error handling
   * Implementation: Backend Senior + Security
   */
  private async executeRequest<T>(
    method: HttpMethod,
    url: string,
    options: RequestOptions,
    timeout: number
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout * 1000);

    try {
      const headers = {
        ...this.defaultHeaders,
        ...options.headers,
      };

      // Security: Input validation and sanitization
      this.validateRequestSecurity(url, headers, options.body);

      const fetchOptions: RequestInit = {
        method,
        headers,
        signal: controller.signal,
        body: options.body ? JSON.stringify(options.body) : undefined,
      };

      const response = await fetch(url, fetchOptions);
      clearTimeout(timeoutId);

      // Parse response with error handling
      const data = await this.parseResponse<T>(response);

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: this.parseHeaders(response.headers),
        success: response.ok,
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw this.handleRequestError(error, url);
    }
  }

  /**
   * Parse HTTP response with comprehensive error handling
   * Implementation: Backend Senior + Security
   */
  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        if (contentType?.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorMessage;
        } else {
          errorMessage = await response.text() || errorMessage;
        }
      } catch {
        // Fallback to status text if parsing fails
      }

      throw new ApiError(errorMessage, response.status, {
        url: response.url,
        headers: this.parseHeaders(response.headers),
      });
    }

    try {
      if (contentType?.includes('application/json')) {
        return await response.json();
      } else {
        return (await response.text()) as unknown as T;
      }
    } catch (error) {
      throw new ApiError('Failed to parse response body', response.status);
    }
  }

  /**
   * Intelligent retry logic based on error type and attempt count
   * Implementation: Lead Dev IA + DevOps
   */
  private shouldRetry(error: any, attempt: number): boolean {
    // Don't retry on client errors (4xx) except for specific cases
    if (error instanceof ApiError) {
      if (error.status >= 400 && error.status < 500) {
        // Retry on rate limiting and authentication issues
        return error.status === 429 || error.status === 401;
      }
      // Retry on server errors (5xx)
      return error.status >= 500;
    }

    // Retry on network and timeout errors
    return error instanceof NetworkError || error instanceof TimeoutError;
  }

  /**
   * Calculate exponential backoff delay with jitter
   * Implementation: DevOps + Lead Dev IA
   */
  private calculateBackoffDelay(attempt: number): number {
    const baseDelay = Math.min(1000 * Math.pow(2, attempt), 30000); // Max 30 seconds
    const jitter = Math.random() * 0.1 * baseDelay; // 10% jitter
    return baseDelay + jitter;
  }

  /**
   * Security validation for requests
   * Implementation: Security + Backend Senior
   */
  private validateRequestSecurity(
    url: string,
    headers: Record<string, string>,
    body?: any
  ): void {
    // Validate URL protocol
    if (!url.startsWith('https://') && !url.startsWith('http://localhost')) {
      throw new ApiError('Only HTTPS requests are allowed in production', 400);
    }

    // Validate headers for security
    const sensitiveHeaders = ['authorization', 'x-api-key', 'cookie'];
    for (const header of sensitiveHeaders) {
      if (headers[header] && headers[header].length > 1000) {
        throw new ApiError(`${header} header too long`, 400);
      }
    }

    // Validate request body size
    if (body && JSON.stringify(body).length > 10 * 1024 * 1024) { // 10MB limit
      throw new ApiError('Request body too large', 413);
    }
  }

  /**
   * Handle and classify request errors
   * Implementation: Security + DevOps
   */
  private handleRequestError(error: any, url: string): Error {
    if (error.name === 'AbortError') {
      return new TimeoutError(`Request timeout for ${url}`);
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new NetworkError(`Network error for ${url}: ${error.message}`);
    }

    if (error instanceof ApiError) {
      return error;
    }

    return new ApiError(`Request failed for ${url}: ${error.message}`, 0);
  }

  /**
   * Parse response headers into a plain object
   * Implementation: Backend Senior
   */
  private parseHeaders(headers: Headers): Record<string, string> {
    const headerObject: Record<string, string> = {};
    headers.forEach((value, key) => {
      headerObject[key.toLowerCase()] = value;
    });
    return headerObject;
  }

  /**
   * Sleep utility for retry delays
   * Implementation: DevOps
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Convenience methods for common HTTP operations
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