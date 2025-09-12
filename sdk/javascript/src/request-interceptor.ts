/**
 * Request Interceptor for Ainflue JavaScript SDK
 * Enterprise-grade request preprocessing with security and monitoring
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Security + DevOps + Lead Dev IA + Backend Senior
 */

import { RequestOptions, InterceptorConfig, RequestContext } from './interfaces';
import { SecurityError, ValidationError, ConfigurationError } from './errors';

/**
 * Request Interceptor for preprocessing and security validation
 */
export class RequestInterceptor {
  private config: InterceptorConfig;
  private metricsCollector: MetricsCollector;
  private securityValidator: SecurityValidator;

  constructor(config: InterceptorConfig = {}) {
    this.config = {
      enableSecurity: true,
      enableMetrics: true,
      enableRetryLogic: true,
      enableRateLimiting: false,
      ...config,
    };
    
    this.metricsCollector = new MetricsCollector(this.config);
    this.securityValidator = new SecurityValidator(this.config);
  }

  /**
   * Intercept and process outgoing requests
   * Implementation: Lead Dev IA + Security + DevOps
   */
  async intercept(
    method: string,
    url: string,
    options: RequestOptions,
    context: RequestContext = {}
  ): Promise<RequestOptions> {
    const startTime = performance.now();
    const requestId = this.generateRequestId();
    
    try {
      // Create enhanced context
      const enhancedContext: RequestContext = {
        ...context,
        requestId,
        startTime,
        method: method.toUpperCase(),
        url,
      };

      // Security validation
      if (this.config.enableSecurity) {
        await this.securityValidator.validateRequest(method, url, options, enhancedContext);
      }

      // Apply request transformations
      const processedOptions = await this.processRequest(options, enhancedContext);

      // Collect metrics
      if (this.config.enableMetrics) {
        this.metricsCollector.recordRequestStart(enhancedContext);
      }

      // Apply rate limiting if enabled
      if (this.config.enableRateLimiting) {
        await this.applyRateLimiting(enhancedContext);
      }

      return processedOptions;

    } catch (error) {
      // Log interception errors
      console.error(`Request interception failed for ${method} ${url}:`, error);
      throw error;
    }
  }

  /**
   * Process request options with intelligent enhancements
   * Implementation: Lead Dev IA + Backend Senior + DevOps
   */
  private async processRequest(options: RequestOptions, context: RequestContext): Promise<RequestOptions> {
    const processed: RequestOptions = { ...options };

    // Enhance headers with tracking and security information
    processed.headers = {
      ...processed.headers,
      'X-Request-ID': context.requestId,
      'X-Timestamp': new Date().toISOString(),
      'X-SDK-Version': '1.0.0',
      'X-Client-ID': this.generateClientFingerprint(),
    };

    // Add authentication headers if available
    if (this.config.apiKey && !processed.headers.authorization) {
      processed.headers.authorization = `Bearer ${this.config.apiKey}`;
    }

    // Apply compression headers for large payloads
    if (this.shouldCompress(processed.body)) {
      processed.headers['Accept-Encoding'] = 'gzip, deflate, br';
    }

    // Set appropriate Content-Type if not specified
    if (processed.body && !processed.headers['Content-Type']) {
      processed.headers['Content-Type'] = this.detectContentType(processed.body);
    }

    // Apply request timeout optimization
    processed.timeout = this.optimizeTimeout(context.method, processed.timeout);

    // Apply intelligent retry configuration
    if (this.config.enableRetryLogic) {
      processed.retries = processed.retries || this.calculateOptimalRetries(context);
    }

    return processed;
  }

  /**
   * Generate unique request ID for tracking
   * Implementation: DevOps + Lead Dev IA
   */
  private generateRequestId(): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `req_${timestamp}_${random}`;
  }

  /**
   * Generate client fingerprint for security tracking
   * Implementation: Security + DevOps
   */
  private generateClientFingerprint(): string {
    // Create a simple fingerprint based on available browser/environment info
    const userAgent = typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown';
    const platform = typeof navigator !== 'undefined' ? navigator.platform : 'unknown';
    const language = typeof navigator !== 'undefined' ? navigator.language : 'unknown';
    
    const fingerprint = `${userAgent}-${platform}-${language}`;
    return btoa(fingerprint).substr(0, 16);
  }

  /**
   * Detect content type for request body
   * Implementation: Backend Senior + Lead Dev IA
   */
  private detectContentType(body: any): string {
    if (body instanceof FormData) {
      return 'multipart/form-data';
    } else if (body instanceof URLSearchParams) {
      return 'application/x-www-form-urlencoded';
    } else if (typeof body === 'string') {
      // Try to detect if it's JSON
      try {
        JSON.parse(body);
        return 'application/json';
      } catch {
        return 'text/plain';
      }
    } else if (typeof body === 'object' && body !== null) {
      return 'application/json';
    }
    
    return 'application/octet-stream';
  }

  /**
   * Determine if request body should be compressed
   * Implementation: DevOps + Backend Senior
   */
  private shouldCompress(body: any): boolean {
    if (!body) return false;
    
    const bodySize = this.estimateBodySize(body);
    return bodySize > 1024; // Compress bodies larger than 1KB
  }

  /**
   * Estimate body size for compression decision
   * Implementation: Backend Senior
   */
  private estimateBodySize(body: any): number {
    if (typeof body === 'string') {
      return body.length;
    } else if (body instanceof Blob) {
      return body.size;
    } else if (body instanceof FormData) {
      // Rough estimation for FormData
      return 1024; // Default assumption
    } else if (typeof body === 'object' && body !== null) {
      return JSON.stringify(body).length;
    }
    
    return 0;
  }

  /**
   * Optimize timeout based on request characteristics
   * Implementation: DevOps + Lead Dev IA
   */
  private optimizeTimeout(method: string, currentTimeout?: number): number {
    const defaultTimeouts = {
      GET: 30000,     // 30 seconds
      POST: 60000,    // 60 seconds
      PUT: 60000,     // 60 seconds
      DELETE: 30000,  // 30 seconds
      PATCH: 45000,   // 45 seconds
    };

    const optimizedTimeout = defaultTimeouts[method as keyof typeof defaultTimeouts] || 30000;
    
    // Use provided timeout if it's reasonable, otherwise use optimized
    if (currentTimeout && currentTimeout > 0 && currentTimeout <= 300000) { // Max 5 minutes
      return currentTimeout;
    }
    
    return optimizedTimeout;
  }

  /**
   * Calculate optimal retry count based on request characteristics
   * Implementation: Lead Dev IA + DevOps
   */
  private calculateOptimalRetries(context: RequestContext): number {
    // Higher retries for idempotent operations
    if (context.method === 'GET' || context.method === 'HEAD') {
      return 3;
    }
    
    // Lower retries for mutating operations
    if (context.method === 'POST' || context.method === 'PUT') {
      return 2;
    }
    
    // Minimal retries for delete operations
    if (context.method === 'DELETE') {
      return 1;
    }
    
    return 2; // Default
  }

  /**
   * Apply rate limiting logic
   * Implementation: DevOps + Security + Lead Dev IA
   */
  private async applyRateLimiting(context: RequestContext): Promise<void> {
    if (!this.config.rateLimitConfig) {
      return;
    }

    const { requestsPerSecond, burstLimit } = this.config.rateLimitConfig;
    
    // Simple in-memory rate limiting (for production, use Redis or similar)
    const now = Date.now();
    const windowStart = now - 1000; // 1-second window
    
    // This is a simplified implementation
    // In production, you'd want a more sophisticated rate limiting strategy
    const recentRequests = this.getRecentRequests(windowStart);
    
    if (recentRequests.length >= requestsPerSecond) {
      const waitTime = 1000 - (now - recentRequests[0]);
      if (waitTime > 0) {
        await this.sleep(waitTime);
      }
    }
    
    this.recordRequest(now);
  }

  /**
   * Get recent requests for rate limiting
   * Implementation: DevOps
   */
  private getRecentRequests(windowStart: number): number[] {
    // This would be implemented with a proper sliding window in production
    return []; // Simplified for demo
  }

  /**
   * Record request timestamp for rate limiting
   * Implementation: DevOps
   */
  private recordRequest(timestamp: number): void {
    // This would be implemented with proper storage in production
  }

  /**
   * Sleep utility for rate limiting
   * Implementation: DevOps
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Metrics Collector for request monitoring
 * Implementation: DevOps + Lead Dev IA
 */
class MetricsCollector {
  private config: InterceptorConfig;
  private metrics: Map<string, any> = new Map();

  constructor(config: InterceptorConfig) {
    this.config = config;
  }

  recordRequestStart(context: RequestContext): void {
    this.metrics.set(context.requestId!, {
      method: context.method,
      url: context.url,
      startTime: context.startTime,
      timestamp: new Date().toISOString(),
    });
  }

  recordRequestEnd(requestId: string, status: number, error?: any): void {
    const requestMetrics = this.metrics.get(requestId);
    if (requestMetrics) {
      const endTime = performance.now();
      const duration = endTime - requestMetrics.startTime;
      
      const finalMetrics = {
        ...requestMetrics,
        endTime,
        duration,
        status,
        error: error ? error.message : null,
      };

      // Log metrics based on configuration
      if (this.config.enableMetrics) {
        this.logMetrics(finalMetrics);
      }

      this.metrics.delete(requestId);
    }
  }

  private logMetrics(metrics: any): void {
    if (metrics.error) {
      console.error('Request failed:', metrics);
    } else if (metrics.duration > 5000) {
      console.warn('Slow request detected:', metrics);
    } else {
      console.debug('Request completed:', metrics);
    }
  }
}

/**
 * Security Validator for request validation
 * Implementation: Security + Lead Dev IA
 */
class SecurityValidator {
  private config: InterceptorConfig;

  constructor(config: InterceptorConfig) {
    this.config = config;
  }

  async validateRequest(
    method: string,
    url: string,
    options: RequestOptions,
    context: RequestContext
  ): Promise<void> {
    // URL validation
    this.validateUrl(url);
    
    // Headers validation
    this.validateHeaders(options.headers || {});
    
    // Body validation
    this.validateBody(options.body);
    
    // Method validation
    this.validateMethod(method);
    
    // Rate limiting validation
    await this.validateRateLimit(context);
  }

  private validateUrl(url: string): void {
    try {
      const parsedUrl = new URL(url);
      
      // Protocol validation
      if (!['https:', 'http:'].includes(parsedUrl.protocol)) {
        throw new SecurityError('Invalid protocol. Only HTTP and HTTPS are allowed.');
      }
      
      // Production HTTPS enforcement
      if (parsedUrl.protocol === 'http:' && !parsedUrl.hostname.includes('localhost')) {
        throw new SecurityError('HTTPS is required for non-localhost requests.');
      }
      
    } catch (error) {
      if (error instanceof SecurityError) throw error;
      throw new ValidationError('Invalid URL format');
    }
  }

  private validateHeaders(headers: Record<string, string>): void {
    const sensitiveHeaders = ['authorization', 'x-api-key', 'cookie'];
    
    for (const [key, value] of Object.entries(headers)) {
      // Header size validation
      if (value.length > 8192) { // 8KB limit
        throw new SecurityError(`Header ${key} exceeds maximum length`);
      }
      
      // Sensitive header validation
      if (sensitiveHeaders.includes(key.toLowerCase())) {
        if (value.length > 1000) { // 1KB limit for sensitive headers
          throw new SecurityError(`Sensitive header ${key} too long`);
        }
      }
    }
  }

  private validateBody(body: any): void {
    if (!body) return;
    
    // Size validation
    const bodySize = this.estimateBodySize(body);
    if (bodySize > 50 * 1024 * 1024) { // 50MB limit
      throw new ValidationError('Request body too large');
    }
    
    // Content validation for JSON
    if (typeof body === 'object' && body !== null && !(body instanceof FormData) && !(body instanceof Blob)) {
      try {
        JSON.stringify(body);
      } catch {
        throw new ValidationError('Invalid JSON body');
      }
    }
  }

  private validateMethod(method: string): void {
    const allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
    if (!allowedMethods.includes(method.toUpperCase())) {
      throw new ValidationError(`HTTP method ${method} not allowed`);
    }
  }

  private async validateRateLimit(context: RequestContext): Promise<void> {
    // Custom rate limiting validation logic
    // This would integrate with your rate limiting system
  }

  private estimateBodySize(body: any): number {
    if (typeof body === 'string') {
      return body.length;
    } else if (body instanceof Blob) {
      return body.size;
    } else if (typeof body === 'object' && body !== null) {
      return JSON.stringify(body).length;
    }
    return 0;
  }
}