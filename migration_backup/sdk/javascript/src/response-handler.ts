/**
 * Response Handler for Ainflue JavaScript SDK
 * Enterprise-grade response processing with analytics and error recovery
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DevOps + Lead Dev IA + Security + ML Engineer
 */

import { ApiResponse, ResponseHandlerConfig, ResponseContext, CacheConfig } from './interfaces';
import { ApiError, SecurityError, ErrorHandler } from './errors';

/**
 * Intelligent Response Handler with enterprise features
 */
export class ResponseHandler {
  private config: ResponseHandlerConfig;
  private cache: ResponseCache;
  private analytics: ResponseAnalytics;
  private transformer: DataTransformer;

  constructor(config: ResponseHandlerConfig = {}) {
    this.config = {
      enableCaching: true,
      enableAnalytics: true,
      enableTransformation: true,
      enableSecurityValidation: true,
      cacheConfig: {
        defaultTTL: 300000, // 5 minutes
        maxSize: 100,
      },
      ...config,
    };

    this.cache = new ResponseCache(this.config.cacheConfig);
    this.analytics = new ResponseAnalytics();
    this.transformer = new DataTransformer();
  }

  /**
   * Process HTTP response with enterprise features
   * Implementation: Backend Senior + Lead Dev IA + DevOps
   */
  async handleResponse<T = any>(
    response: Response | any,
    context: ResponseContext
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    
    try {
      // Security validation
      if (this.config.enableSecurityValidation) {
        this.validateResponseSecurity(response, context);
      }

      // Extract base response data
      const baseResponse = await this.extractResponseData<T>(response, context);

      // Apply data transformations
      if (this.config.enableTransformation) {
        baseResponse.data = await this.transformer.transform<T>(
          baseResponse.data,
          context.transformationRules
        );
      }

      // Cache successful responses
      if (this.config.enableCaching && this.shouldCache(baseResponse, context)) {
        await this.cache.set(context.cacheKey!, baseResponse, context.cacheTTL);
      }

      // Collect analytics
      if (this.config.enableAnalytics) {
        const processingTime = performance.now() - startTime;
        this.analytics.recordResponse(baseResponse, context, processingTime);
      }

      return baseResponse;

    } catch (error) {
      // Handle processing errors
      const apiError = ErrorHandler.parseError(error);
      
      if (this.config.enableAnalytics) {
        const processingTime = performance.now() - startTime;
        this.analytics.recordError(apiError, context, processingTime);
      }

      throw apiError;
    }
  }

  /**
   * Check if response exists in cache
   * Implementation: DevOps + Backend Senior
   */
  async getCachedResponse<T = any>(cacheKey: string): Promise<ApiResponse<T> | null> {
    if (!this.config.enableCaching) {
      return null;
    }

    return this.cache.get<T>(cacheKey);
  }

  /**
   * Extract response data with intelligent parsing
   * Implementation: Backend Senior + Lead Dev IA
   */
  private async extractResponseData<T>(
    response: Response | any,
    context: ResponseContext
  ): Promise<ApiResponse<T>> {
    let status: number;
    let statusText: string;
    let headers: Record<string, string>;
    let data: T;

    // Handle different response types (fetch Response vs axios response)
    if (response instanceof Response) {
      status = response.status;
      statusText = response.statusText;
      headers = this.parseHeaders(response.headers);
      data = await this.parseResponseBody<T>(response);
    } else {
      // Axios-style response
      status = response.status;
      statusText = response.statusText || '';
      headers = response.headers || {};
      data = response.data;
    }

    // Validate successful response
    if (status >= 400) {
      const errorMessage = this.extractErrorMessage(data, status, statusText);
      throw new ApiError(errorMessage, status, data);
    }

    return {
      data,
      status,
      statusText,
      headers,
      success: status >= 200 && status < 300,
    };
  }

  /**
   * Parse response body with intelligent content type detection
   * Implementation: Backend Senior + Lead Dev IA
   */
  private async parseResponseBody<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type') || '';
    const contentLength = response.headers.get('content-length');

    // Handle empty responses
    if (contentLength === '0' || response.status === 204) {
      return null as unknown as T;
    }

    try {
      if (contentType.includes('application/json')) {
        return await response.json();
      } else if (contentType.includes('text/')) {
        return (await response.text()) as unknown as T;
      } else if (contentType.includes('application/octet-stream') || 
                 contentType.includes('image/') || 
                 contentType.includes('video/') || 
                 contentType.includes('audio/')) {
        return (await response.blob()) as unknown as T;
      } else if (contentType.includes('application/pdf')) {
        return (await response.arrayBuffer()) as unknown as T;
      } else {
        // Try JSON first, fallback to text
        const text = await response.text();
        try {
          return JSON.parse(text);
        } catch {
          return text as unknown as T;
        }
      }
    } catch (parseError) {
      throw new ApiError(
        `Failed to parse response body: ${parseError.message}`,
        response.status
      );
    }
  }

  /**
   * Extract error message from response data
   * Implementation: Backend Senior + Security
   */
  private extractErrorMessage(data: any, status: number, statusText: string): string {
    if (typeof data === 'string') {
      return data || statusText || `HTTP ${status}`;
    }

    if (typeof data === 'object' && data !== null) {
      // Try common error message fields
      const messageFields = ['message', 'error', 'detail', 'errorMessage', 'msg'];
      
      for (const field of messageFields) {
        if (data[field] && typeof data[field] === 'string') {
          return data[field];
        }
      }

      // Check for validation errors
      if (data.errors && Array.isArray(data.errors)) {
        return data.errors.map((err: any) => err.message || err).join(', ');
      }
    }

    return statusText || `HTTP ${status}`;
  }

  /**
   * Parse response headers into a plain object
   * Implementation: Backend Senior
   */
  private parseHeaders(headers: Headers | Record<string, string>): Record<string, string> {
    const headerObject: Record<string, string> = {};

    if (headers instanceof Headers) {
      headers.forEach((value, key) => {
        headerObject[key.toLowerCase()] = value;
      });
    } else {
      for (const [key, value] of Object.entries(headers)) {
        headerObject[key.toLowerCase()] = String(value);
      }
    }

    return headerObject;
  }

  /**
   * Validate response security
   * Implementation: Security + DevOps
   */
  private validateResponseSecurity(response: Response | any, context: ResponseContext): void {
    const headers = response.headers instanceof Headers 
      ? this.parseHeaders(response.headers)
      : response.headers || {};

    // Check for security headers
    const securityChecks = [
      {
        header: 'x-content-type-options',
        expected: 'nosniff',
        severity: 'warning',
      },
      {
        header: 'x-frame-options',
        expected: ['DENY', 'SAMEORIGIN'],
        severity: 'warning',
      },
      {
        header: 'strict-transport-security',
        required: true,
        severity: 'warning',
      },
    ];

    const securityIssues: string[] = [];

    for (const check of securityChecks) {
      const headerValue = headers[check.header];
      
      if (check.required && !headerValue) {
        securityIssues.push(`Missing required security header: ${check.header}`);
      } else if (check.expected && headerValue) {
        const expectedValues = Array.isArray(check.expected) ? check.expected : [check.expected];
        if (!expectedValues.includes(headerValue.toUpperCase())) {
          securityIssues.push(`Invalid ${check.header} value: ${headerValue}`);
        }
      }
    }

    // Log security issues
    if (securityIssues.length > 0) {
      console.warn(`Security header issues for ${context.url}:`, securityIssues);
    }

    // Check for potential security vulnerabilities
    if (headers['access-control-allow-origin'] === '*' && headers['access-control-allow-credentials'] === 'true') {
      console.error('Security vulnerability: Dangerous CORS configuration detected');
    }
  }

  /**
   * Determine if response should be cached
   * Implementation: DevOps + Backend Senior
   */
  private shouldCache(response: ApiResponse<any>, context: ResponseContext): boolean {
    // Don't cache error responses
    if (!response.success) {
      return false;
    }

    // Don't cache if explicitly disabled
    if (context.disableCache) {
      return false;
    }

    // Don't cache if no cache key provided
    if (!context.cacheKey) {
      return false;
    }

    // Check cache-control headers
    const cacheControl = response.headers['cache-control'];
    if (cacheControl) {
      if (cacheControl.includes('no-cache') || cacheControl.includes('no-store')) {
        return false;
      }
    }

    // Cache GET requests by default
    if (context.method === 'GET') {
      return true;
    }

    // Don't cache mutating operations
    return false;
  }
}

/**
 * Response Cache implementation with TTL and size limits
 * Implementation: DevOps + Backend Senior + DBA
 */
class ResponseCache {
  private cache: Map<string, CacheEntry> = new Map();
  private config: CacheConfig;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(config: CacheConfig = {}) {
    this.config = {
      defaultTTL: 300000, // 5 minutes
      maxSize: 100,
      cleanupInterval: 60000, // 1 minute
      ...config,
    };

    this.startCleanupTimer();
  }

  async get<T>(key: string): Promise<ApiResponse<T> | null> {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    // Update access time for LRU
    entry.lastAccessed = Date.now();
    
    return entry.data as ApiResponse<T>;
  }

  async set<T>(key: string, data: ApiResponse<T>, ttl?: number): Promise<void> {
    const expiresAt = Date.now() + (ttl || this.config.defaultTTL!);
    
    // Ensure cache size limit
    if (this.cache.size >= this.config.maxSize!) {
      this.evictOldest();
    }

    this.cache.set(key, {
      data,
      expiresAt,
      lastAccessed: Date.now(),
    });
  }

  private evictOldest(): void {
    let oldestKey: string | null = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  private startCleanupTimer(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }

    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  private cleanup(): void {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => this.cache.delete(key));
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    this.cache.clear();
  }
}

/**
 * Response Analytics for monitoring and insights
 * Implementation: ML Engineer + DevOps + Lead Dev IA
 */
class ResponseAnalytics {
  private metrics: ResponseMetrics[] = [];
  private readonly maxMetrics = 1000;

  recordResponse<T>(
    response: ApiResponse<T>,
    context: ResponseContext,
    processingTime: number
  ): void {
    const metric: ResponseMetrics = {
      timestamp: new Date().toISOString(),
      method: context.method || 'UNKNOWN',
      url: this.sanitizeUrl(context.url || ''),
      status: response.status,
      success: response.success,
      processingTime,
      responseSize: this.estimateResponseSize(response.data),
      cacheHit: context.cacheHit || false,
    };

    this.addMetric(metric);
    this.analyzePerformance(metric);
  }

  recordError(error: any, context: ResponseContext, processingTime: number): void {
    const metric: ResponseMetrics = {
      timestamp: new Date().toISOString(),
      method: context.method || 'UNKNOWN',
      url: this.sanitizeUrl(context.url || ''),
      status: error.status || 0,
      success: false,
      processingTime,
      error: error.name || 'UnknownError',
      cacheHit: false,
    };

    this.addMetric(metric);
  }

  getMetrics(): ResponseMetrics[] {
    return [...this.metrics];
  }

  getPerformanceInsights(): any {
    if (this.metrics.length === 0) {
      return { averageResponseTime: 0, errorRate: 0, cacheHitRate: 0 };
    }

    const totalRequests = this.metrics.length;
    const successfulRequests = this.metrics.filter(m => m.success).length;
    const cachedRequests = this.metrics.filter(m => m.cacheHit).length;
    const avgResponseTime = this.metrics.reduce((sum, m) => sum + m.processingTime, 0) / totalRequests;

    return {
      totalRequests,
      successfulRequests,
      errorRate: ((totalRequests - successfulRequests) / totalRequests) * 100,
      averageResponseTime: avgResponseTime,
      cacheHitRate: (cachedRequests / totalRequests) * 100,
      slowestRequests: this.metrics
        .filter(m => m.success)
        .sort((a, b) => b.processingTime - a.processingTime)
        .slice(0, 5),
    };
  }

  private addMetric(metric: ResponseMetrics): void {
    this.metrics.push(metric);
    
    // Maintain maximum metrics limit
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }
  }

  private analyzePerformance(metric: ResponseMetrics): void {
    // Alert on slow responses
    if (metric.processingTime > 10000) { // 10 seconds
      console.warn('Very slow response detected:', {
        url: metric.url,
        method: metric.method,
        duration: metric.processingTime,
      });
    } else if (metric.processingTime > 5000) { // 5 seconds
      console.info('Slow response detected:', {
        url: metric.url,
        method: metric.method,
        duration: metric.processingTime,
      });
    }

    // Alert on large responses
    if (metric.responseSize && metric.responseSize > 10 * 1024 * 1024) { // 10MB
      console.warn('Large response detected:', {
        url: metric.url,
        size: metric.responseSize,
      });
    }
  }

  private sanitizeUrl(url: string): string {
    // Remove query parameters and replace IDs with placeholders
    return url.split('?')[0].replace(/\/\d+/g, '/:id');
  }

  private estimateResponseSize(data: any): number {
    if (typeof data === 'string') {
      return data.length;
    } else if (data instanceof Blob) {
      return data.size;
    } else if (typeof data === 'object' && data !== null) {
      return JSON.stringify(data).length;
    }
    return 0;
  }
}

/**
 * Data Transformer for response data processing
 * Implementation: ML Engineer + Lead Dev IA + Backend Senior
 */
class DataTransformer {
  async transform<T>(data: any, rules?: any): Promise<T> {
    if (!rules || !data) {
      return data;
    }

    // Apply transformation rules
    try {
      if (rules.dateFields) {
        data = this.transformDates(data, rules.dateFields);
      }

      if (rules.numberFields) {
        data = this.transformNumbers(data, rules.numberFields);
      }

      if (rules.customTransformers) {
        data = await this.applyCustomTransformers(data, rules.customTransformers);
      }

      return data;
    } catch (error) {
      console.warn('Data transformation failed:', error);
      return data; // Return original data on transformation failure
    }
  }

  private transformDates(data: any, dateFields: string[]): any {
    if (typeof data !== 'object' || data === null) {
      return data;
    }

    const transformed = { ...data };

    for (const field of dateFields) {
      if (transformed[field] && typeof transformed[field] === 'string') {
        try {
          transformed[field] = new Date(transformed[field]);
        } catch {
          // Keep original value if date parsing fails
        }
      }
    }

    return transformed;
  }

  private transformNumbers(data: any, numberFields: string[]): any {
    if (typeof data !== 'object' || data === null) {
      return data;
    }

    const transformed = { ...data };

    for (const field of numberFields) {
      if (transformed[field] && typeof transformed[field] === 'string') {
        const num = parseFloat(transformed[field]);
        if (!isNaN(num)) {
          transformed[field] = num;
        }
      }
    }

    return transformed;
  }

  private async applyCustomTransformers(data: any, transformers: Function[]): Promise<any> {
    let transformed = data;

    for (const transformer of transformers) {
      if (typeof transformer === 'function') {
        try {
          transformed = await transformer(transformed);
        } catch (error) {
          console.warn('Custom transformer failed:', error);
        }
      }
    }

    return transformed;
  }
}

interface CacheEntry {
  data: any;
  expiresAt: number;
  lastAccessed: number;
}

interface ResponseMetrics {
  timestamp: string;
  method: string;
  url: string;
  status: number;
  success: boolean;
  processingTime: number;
  responseSize?: number;
  error?: string;
  cacheHit: boolean;
}