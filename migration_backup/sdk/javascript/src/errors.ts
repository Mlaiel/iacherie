/**
 * Error Classes for Ainflue JavaScript SDK
 * Comprehensive error handling with enterprise security considerations
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Security + Backend Senior + DevOps
 */

/**
 * Base SDK Error Class
 * Implementation: Security + Backend Senior
 */
export class AinflueSdkError extends Error {
  public readonly timestamp: Date;
  public readonly errorId: string;

  constructor(message: string, public readonly code?: string) {
    super(message);
    this.name = this.constructor.name;
    this.timestamp = new Date();
    this.errorId = this.generateErrorId();
    
    // Maintain proper stack trace (Security best practice)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      timestamp: this.timestamp.toISOString(),
      errorId: this.errorId,
    };
  }
}

/**
 * API Error - HTTP API related errors
 * Implementation: Backend Senior + Security
 */
export class ApiError extends AinflueSdkError {
  constructor(
    message: string,
    public readonly status: number,
    public readonly response?: any,
    code?: string
  ) {
    super(message, code || `API_ERROR_${status}`);
    this.name = 'ApiError';
  }

  get isClientError(): boolean {
    return this.status >= 400 && this.status < 500;
  }

  get isServerError(): boolean {
    return this.status >= 500;
  }

  get isRetryable(): boolean {
    // Retryable server errors and specific client errors
    return this.isServerError || this.status === 429 || this.status === 408;
  }
}

/**
 * Authentication Error - Auth related failures
 * Implementation: Security + Backend Senior
 */
export class AuthenticationError extends AinflueSdkError {
  constructor(message: string, public readonly authType?: string) {
    super(message, 'AUTHENTICATION_ERROR');
    this.name = 'AuthenticationError';
  }
}

/**
 * Authorization Error - Permission related failures
 * Implementation: Security
 */
export class AuthorizationError extends AinflueSdkError {
  constructor(message: string, public readonly resource?: string) {
    super(message, 'AUTHORIZATION_ERROR');
    this.name = 'AuthorizationError';
  }
}

/**
 * Network Error - Network connectivity issues
 * Implementation: DevOps + Backend Senior
 */
export class NetworkError extends AinflueSdkError {
  constructor(message: string, public readonly originalError?: Error) {
    super(message, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

/**
 * Timeout Error - Request timeout failures
 * Implementation: DevOps + Backend Senior
 */
export class TimeoutError extends AinflueSdkError {
  constructor(message: string, public readonly timeoutMs?: number) {
    super(message, 'TIMEOUT_ERROR');
    this.name = 'TimeoutError';
  }
}

/**
 * Rate Limit Error - API rate limiting
 * Implementation: DevOps + Security
 */
export class RateLimitError extends ApiError {
  constructor(
    message: string,
    public readonly retryAfter?: number,
    public readonly limit?: number,
    public readonly remaining?: number
  ) {
    super(message, 429, null, 'RATE_LIMIT_ERROR');
    this.name = 'RateLimitError';
  }
}

/**
 * Validation Error - Input validation failures
 * Implementation: Security + Backend Senior
 */
export class ValidationError extends AinflueSdkError {
  constructor(
    message: string,
    public readonly field?: string,
    public readonly value?: any
  ) {
    super(message, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

/**
 * Configuration Error - SDK configuration issues
 * Implementation: DevOps + Security
 */
export class ConfigurationError extends AinflueSdkError {
  constructor(message: string, public readonly configKey?: string) {
    super(message, 'CONFIGURATION_ERROR');
    this.name = 'ConfigurationError';
  }
}

/**
 * Streaming Error - Real-time streaming failures
 * Implementation: Audio Engineer + Backend Senior + DevOps
 */
export class StreamingError extends AinflueSdkError {
  constructor(
    message: string,
    public readonly streamType?: string,
    public readonly connectionId?: string
  ) {
    super(message, 'STREAMING_ERROR');
    this.name = 'StreamingError';
  }
}

/**
 * AI Processing Error - AI/ML related failures
 * Implementation: ML Engineer + Lead Dev IA
 */
export class AIProcessingError extends AinflueSdkError {
  constructor(
    message: string,
    public readonly modelType?: string,
    public readonly processingId?: string
  ) {
    super(message, 'AI_PROCESSING_ERROR');
    this.name = 'AIProcessingError';
  }
}

/**
 * Security Error - Security violation detection
 * Implementation: Security + DevOps
 */
export class SecurityError extends AinflueSdkError {
  constructor(message: string, public readonly securityType?: string) {
    super(message, 'SECURITY_ERROR');
    this.name = 'SecurityError';
  }
}

/**
 * Service Unavailable Error - Service dependency failures
 * Implementation: Microservices + DevOps
 */
export class ServiceUnavailableError extends ApiError {
  constructor(
    message: string,
    public readonly serviceName?: string,
    public readonly estimatedRecoveryTime?: number
  ) {
    super(message, 503, null, 'SERVICE_UNAVAILABLE');
    this.name = 'ServiceUnavailableError';
  }
}

/**
 * Error Handler Utility Class
 * Implementation: DevOps + Security + Backend Senior
 */
export class ErrorHandler {
  /**
   * Parse and classify errors from various sources
   */
  static parseError(error: any): AinflueSdkError {
    if (error instanceof AinflueSdkError) {
      return error;
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new NetworkError('Network connection failed', error);
    }

    if (error.name === 'AbortError') {
      return new TimeoutError('Request was aborted due to timeout');
    }

    if (error.response) {
      const status = error.response.status || error.status || 0;
      const message = error.response.data?.message || error.message || 'Unknown API error';
      
      if (status === 401) {
        return new AuthenticationError(message);
      }
      
      if (status === 403) {
        return new AuthorizationError(message);
      }
      
      if (status === 429) {
        return new RateLimitError(
          message,
          error.response.headers?.['retry-after'],
          error.response.headers?.['x-ratelimit-limit'],
          error.response.headers?.['x-ratelimit-remaining']
        );
      }
      
      if (status === 503) {
        return new ServiceUnavailableError(message);
      }
      
      return new ApiError(message, status, error.response.data);
    }

    // Default to generic SDK error
    return new AinflueSdkError(error.message || 'Unknown error occurred');
  }

  /**
   * Check if error is retryable
   */
  static isRetryable(error: AinflueSdkError): boolean {
    if (error instanceof ApiError) {
      return error.isRetryable;
    }
    
    return error instanceof NetworkError || 
           error instanceof TimeoutError ||
           error instanceof ServiceUnavailableError;
  }

  /**
   * Get retry delay for error (exponential backoff)
   */
  static getRetryDelay(error: AinflueSdkError, attempt: number): number {
    if (error instanceof RateLimitError && error.retryAfter) {
      return error.retryAfter * 1000; // Convert to milliseconds
    }

    // Exponential backoff with jitter
    const baseDelay = Math.min(1000 * Math.pow(2, attempt), 30000);
    const jitter = Math.random() * 0.1 * baseDelay;
    return baseDelay + jitter;
  }

  /**
   * Log error with appropriate level and security filtering
   * Implementation: Security + DevOps
   */
  static logError(error: AinflueSdkError, context?: Record<string, any>): void {
    // Filter sensitive information before logging
    const safeContext = this.sanitizeContext(context);
    
    const logData = {
      ...error.toJSON(),
      context: safeContext,
    };

    // Use appropriate log level based on error type
    if (error instanceof SecurityError) {
      console.error('[SECURITY]', logData);
    } else if (error instanceof NetworkError || error instanceof TimeoutError) {
      console.warn('[NETWORK]', logData);
    } else if (error instanceof ValidationError) {
      console.warn('[VALIDATION]', logData);
    } else {
      console.error('[SDK]', logData);
    }
  }

  /**
   * Sanitize context object to remove sensitive information
   * Implementation: Security
   */
  private static sanitizeContext(context?: Record<string, any>): Record<string, any> {
    if (!context) return {};

    const sensitiveKeys = ['password', 'token', 'apikey', 'secret', 'authorization', 'cookie'];
    const sanitized: Record<string, any> = {};

    for (const [key, value] of Object.entries(context)) {
      const keyLower = key.toLowerCase();
      if (sensitiveKeys.some(sensitive => keyLower.includes(sensitive))) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = value;
      }
    }

    return sanitized;
  }
}