/**
 * @fileoverview Error Handler - Comprehensive Error Management System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/error_handler
 * @description Professional error handling with logging, recovery, and user feedback
 */

class ErrorHandler {
  constructor() {
    this.errors = [];
    this.maxErrors = 100;
    this.errorCounts = new Map();
    this.suppressedErrors = new Set();
    this.errorHandlers = new Map();
    this.recoveryStrategies = new Map();
    
    this.config = {
      logToConsole: true,
      logToFile: true,
      showUserNotifications: true,
      enableRecovery: true,
      enableMetrics: true,
      maxErrorsPerType: 10,
      suppressDuplicates: true,
      reportToServer: false
    };

    this.initializeErrorHandling();
    console.log('Error Handler initialized');
  }

  /**
   * Initialize comprehensive error handling
   */
  initializeErrorHandling() {
    // Handle uncaught exceptions
    window.addEventListener('error', (event) => {
      this.handleError({
        type: 'javascript_error',
        message: event.error?.message || event.message,
        stack: event.error?.stack,
        filename: event.filename,
        line: event.lineno,
        column: event.colno,
        source: 'window.error'
      });
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError({
        type: 'unhandled_promise',
        message: event.reason?.message || String(event.reason),
        stack: event.reason?.stack,
        source: 'unhandled_promise'
      });
    });

    // Setup default error handlers
    this.setupDefaultHandlers();
    
    // Setup recovery strategies
    this.setupRecoveryStrategies();
  }

  /**
   * Setup default error handlers for different error types
   */
  setupDefaultHandlers() {
    // Network errors
    this.registerHandler('network_error', (error) => {
      this.showUserNotification('Network Error', 
        'Connection issue detected. Please check your internet connection.', 
        'warning'
      );
      
      return {
        handled: true,
        recovery: 'retry_with_delay',
        userMessage: 'Network connection issue. Will retry automatically.'
      };
    });

    // File system errors
    this.registerHandler('filesystem_error', (error) => {
      this.showUserNotification('File Error', 
        'File operation failed. Please check file permissions.', 
        'error'
      );
      
      return {
        handled: true,
        recovery: 'fallback_location',
        userMessage: 'File access issue. Trying alternative location.'
      };
    });

    // API errors
    this.registerHandler('api_error', (error) => {
      let message = 'API request failed.';
      let recovery = 'retry';
      
      if (error.status === 401) {
        message = 'Authentication required. Please log in again.';
        recovery = 'reauthenticate';
      } else if (error.status === 429) {
        message = 'Rate limit exceeded. Please wait a moment.';
        recovery = 'rate_limit_backoff';
      } else if (error.status >= 500) {
        message = 'Server error. Will retry automatically.';
        recovery = 'exponential_backoff';
      }
      
      return {
        handled: true,
        recovery,
        userMessage: message
      };
    });

    // Content processing errors
    this.registerHandler('content_processing_error', (error) => {
      this.showUserNotification('Processing Error', 
        'Content processing failed. Please try with a different file.', 
        'error'
      );
      
      return {
        handled: true,
        recovery: 'alternative_processor',
        userMessage: 'Processing failed. Trying alternative method.'
      };
    });

    // Memory errors
    this.registerHandler('memory_error', (error) => {
      this.showUserNotification('Memory Warning', 
        'Low memory detected. Some features may be limited.', 
        'warning'
      );
      
      return {
        handled: true,
        recovery: 'memory_cleanup',
        userMessage: 'Optimizing memory usage...'
      };
    });

    // Security errors
    this.registerHandler('security_error', (error) => {
      this.showUserNotification('Security Alert', 
        'Security violation detected. Action blocked for protection.', 
        'error'
      );
      
      return {
        handled: true,
        recovery: 'security_lockdown',
        userMessage: 'Security protection activated.'
      };
    });
  }

  /**
   * Setup recovery strategies
   */
  setupRecoveryStrategies() {
    // Retry with delay
    this.registerRecoveryStrategy('retry_with_delay', async (error, context) => {
      const delay = Math.min(1000 * Math.pow(2, error.attempts || 0), 10000);
      await this.delay(delay);
      
      if (context.retryFunction) {
        return await context.retryFunction();
      }
      
      return { success: false, message: 'No retry function provided' };
    });

    // Exponential backoff
    this.registerRecoveryStrategy('exponential_backoff', async (error, context) => {
      const attempts = error.attempts || 0;
      const maxAttempts = 5;
      
      if (attempts >= maxAttempts) {
        return { success: false, message: 'Maximum retry attempts exceeded' };
      }
      
      const delay = Math.min(1000 * Math.pow(2, attempts), 30000);
      await this.delay(delay);
      
      if (context.retryFunction) {
        return await context.retryFunction();
      }
      
      return { success: false, message: 'No retry function provided' };
    });

    // Memory cleanup
    this.registerRecoveryStrategy('memory_cleanup', async (error, context) => {
      try {
        // Clear caches
        if (window.apiClient) {
          window.apiClient.clearCache();
        }
        
        // Force garbage collection if available
        if (window.gc) {
          window.gc();
        }
        
        // Clear temporary data
        this.clearTemporaryData();
        
        return { success: true, message: 'Memory cleanup completed' };
      } catch (cleanupError) {
        return { success: false, message: 'Memory cleanup failed' };
      }
    });

    // Fallback location
    this.registerRecoveryStrategy('fallback_location', async (error, context) => {
      try {
        const fallbackPath = context.fallbackPath || 
          (window.electronAPI ? await window.electronAPI.getDefaultPath() : null);
        
        if (fallbackPath && context.retryWithPath) {
          return await context.retryWithPath(fallbackPath);
        }
        
        return { success: false, message: 'No fallback location available' };
      } catch (fallbackError) {
        return { success: false, message: 'Fallback location failed' };
      }
    });

    // Re-authentication
    this.registerRecoveryStrategy('reauthenticate', async (error, context) => {
      try {
        if (window.stateManager) {
          window.stateManager.setState('user.authenticated', false);
          window.stateManager.setState('app.requiresAuth', true);
        }
        
        return { success: true, message: 'Re-authentication initiated' };
      } catch (authError) {
        return { success: false, message: 'Re-authentication failed' };
      }
    });
  }

  /**
   * Main error handling method
   */
  async handleError(error, context = {}) {
    try {
      // Normalize error object
      const normalizedError = this.normalizeError(error);
      
      // Check if error should be suppressed
      if (this.shouldSuppressError(normalizedError)) {
        return { handled: true, suppressed: true };
      }
      
      // Log the error
      this.logError(normalizedError);
      
      // Add to error collection
      this.addError(normalizedError);
      
      // Find appropriate handler
      const handler = this.findHandler(normalizedError.type);
      
      let result = { handled: false };
      
      if (handler) {
        try {
          result = await handler(normalizedError, context);
        } catch (handlerError) {
          console.error('Error handler failed:', handlerError);
          result = { handled: false, handlerError: handlerError.message };
        }
      }
      
      // Attempt recovery if enabled and strategy is provided
      if (this.config.enableRecovery && result.recovery) {
        const recoveryResult = await this.attemptRecovery(
          normalizedError, 
          result.recovery, 
          context
        );
        
        result.recoveryResult = recoveryResult;
      }
      
      // Show user notification if not handled or if specified
      if ((!result.handled || result.showNotification) && this.config.showUserNotifications) {
        this.showErrorToUser(normalizedError, result);
      }
      
      // Report to analytics/monitoring
      if (this.config.enableMetrics) {
        this.recordErrorMetrics(normalizedError, result);
      }
      
      // Report to server if enabled
      if (this.config.reportToServer) {
        this.reportToServer(normalizedError, result);
      }
      
      return result;
      
    } catch (handlingError) {
      console.error('Critical error in error handling:', handlingError);
      return { handled: false, critical: true };
    }
  }

  /**
   * Normalize error object
   */
  normalizeError(error) {
    const normalized = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      type: 'unknown_error',
      message: 'Unknown error occurred',
      stack: null,
      source: 'unknown',
      severity: 'medium',
      attempts: 0,
      metadata: {}
    };

    if (typeof error === 'string') {
      normalized.message = error;
      normalized.type = 'string_error';
    } else if (error instanceof Error) {
      normalized.message = error.message;
      normalized.stack = error.stack;
      normalized.type = error.name || 'javascript_error';
    } else if (typeof error === 'object' && error !== null) {
      Object.assign(normalized, error);
    }

    // Determine severity
    normalized.severity = this.determineSeverity(normalized);
    
    // Add context information
    normalized.metadata = {
      ...normalized.metadata,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };

    return normalized;
  }

  /**
   * Determine error severity
   */
  determineSeverity(error) {
    const { type, message } = error;
    
    // Critical errors
    if (type.includes('security') || 
        type.includes('corruption') ||
        message.includes('critical')) {
      return 'critical';
    }
    
    // High severity
    if (type.includes('data_loss') ||
        type.includes('authentication') ||
        message.includes('failed to save')) {
      return 'high';
    }
    
    // Low severity
    if (type.includes('warning') ||
        type.includes('cosmetic') ||
        message.includes('temporary')) {
      return 'low';
    }
    
    return 'medium';
  }

  /**
   * Check if error should be suppressed
   */
  shouldSuppressError(error) {
    if (!this.config.suppressDuplicates) {
      return false;
    }
    
    const errorKey = `${error.type}:${error.message}`;
    
    if (this.suppressedErrors.has(errorKey)) {
      return true;
    }
    
    const count = this.errorCounts.get(errorKey) || 0;
    
    if (count >= this.config.maxErrorsPerType) {
      this.suppressedErrors.add(errorKey);
      return true;
    }
    
    return false;
  }

  /**
   * Log error to various outputs
   */
  logError(error) {
    const logMessage = this.formatErrorForLogging(error);
    
    // Console logging
    if (this.config.logToConsole) {
      switch (error.severity) {
        case 'critical':
          console.error('CRITICAL:', logMessage);
          break;
        case 'high':
          console.error('ERROR:', logMessage);
          break;
        case 'medium':
          console.warn('WARNING:', logMessage);
          break;
        case 'low':
          console.info('INFO:', logMessage);
          break;
      }
    }
    
    // File logging (if Electron API available)
    if (this.config.logToFile && window.electronAPI) {
      window.electronAPI.logError(error);
    }
  }

  /**
   * Format error for logging
   */
  formatErrorForLogging(error) {
    return `[${error.type}] ${error.message} (${error.source})${error.stack ? '\n' + error.stack : ''}`;
  }

  /**
   * Add error to collection
   */
  addError(error) {
    this.errors.unshift(error);
    
    // Maintain max errors limit
    if (this.errors.length > this.maxErrors) {
      this.errors = this.errors.slice(0, this.maxErrors);
    }
    
    // Update error counts
    const errorKey = `${error.type}:${error.message}`;
    this.errorCounts.set(errorKey, (this.errorCounts.get(errorKey) || 0) + 1);
  }

  /**
   * Find appropriate error handler
   */
  findHandler(errorType) {
    // Exact match
    if (this.errorHandlers.has(errorType)) {
      return this.errorHandlers.get(errorType);
    }
    
    // Partial match
    for (const [type, handler] of this.errorHandlers) {
      if (errorType.includes(type) || type.includes(errorType)) {
        return handler;
      }
    }
    
    // Default handler
    return this.errorHandlers.get('default');
  }

  /**
   * Attempt error recovery
   */
  async attemptRecovery(error, strategyName, context) {
    const strategy = this.recoveryStrategies.get(strategyName);
    
    if (!strategy) {
      return { success: false, message: `Recovery strategy '${strategyName}' not found` };
    }
    
    try {
      const result = await strategy(error, context);
      
      if (result.success) {
        console.log(`Recovery successful for ${error.type} using ${strategyName}`);
      } else {
        console.warn(`Recovery failed for ${error.type} using ${strategyName}:`, result.message);
      }
      
      return result;
    } catch (recoveryError) {
      console.error(`Recovery strategy '${strategyName}' threw error:`, recoveryError);
      return { success: false, message: recoveryError.message };
    }
  }

  /**
   * Show error to user
   */
  showErrorToUser(error, result) {
    const userMessage = result.userMessage || this.generateUserMessage(error);
    
    let notificationType;
    switch (error.severity) {
      case 'critical':
        notificationType = 'error';
        break;
      case 'high':
        notificationType = 'error';
        break;
      case 'medium':
        notificationType = 'warning';
        break;
      case 'low':
        notificationType = 'info';
        break;
      default:
        notificationType = 'warning';
    }
    
    this.showUserNotification(
      this.getErrorTitle(error.type),
      userMessage,
      notificationType
    );
  }

  /**
   * Generate user-friendly error message
   */
  generateUserMessage(error) {
    const messages = {
      network_error: 'Network connection issue. Please check your internet connection.',
      filesystem_error: 'File access error. Please check file permissions.',
      api_error: 'Service temporarily unavailable. Please try again later.',
      content_processing_error: 'Content processing failed. Please try with a different file.',
      memory_error: 'Low memory detected. Please close unnecessary applications.',
      security_error: 'Security protection activated. Action blocked for safety.',
      authentication_error: 'Authentication required. Please log in again.',
      validation_error: 'Invalid input detected. Please check your data.',
      timeout_error: 'Operation timed out. Please try again.',
      permission_error: 'Insufficient permissions. Please contact administrator.'
    };
    
    return messages[error.type] || 'An unexpected error occurred. Please try again.';
  }

  /**
   * Get error title for notifications
   */
  getErrorTitle(errorType) {
    const titles = {
      network_error: 'Network Error',
      filesystem_error: 'File Error',
      api_error: 'Service Error',
      content_processing_error: 'Processing Error',
      memory_error: 'Memory Warning',
      security_error: 'Security Alert',
      authentication_error: 'Authentication Required',
      validation_error: 'Validation Error',
      timeout_error: 'Timeout Error',
      permission_error: 'Permission Error'
    };
    
    return titles[errorType] || 'Error';
  }

  /**
   * Show user notification
   */
  showUserNotification(title, message, type = 'error') {
    // Use event dispatcher if available
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('ui.notification-shown', {
        title,
        message,
        type,
        source: 'error_handler'
      });
    }
    
    // Fallback to console
    console.log(`Notification [${type.toUpperCase()}]: ${title} - ${message}`);
  }

  /**
   * Record error metrics
   */
  recordErrorMetrics(error, result) {
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('performance.error-recorded', {
        errorType: error.type,
        severity: error.severity,
        handled: result.handled,
        recovered: result.recoveryResult?.success || false,
        timestamp: error.timestamp
      });
    }
  }

  /**
   * Report error to server
   */
  async reportToServer(error, result) {
    try {
      if (window.apiClient) {
        await window.apiClient.post('/errors/report', {
          error,
          result,
          clientInfo: {
            version: '1.0.0',
            platform: navigator.platform,
            userAgent: navigator.userAgent
          }
        });
      }
    } catch (reportError) {
      console.warn('Failed to report error to server:', reportError);
    }
  }

  /**
   * Register error handler
   */
  registerHandler(errorType, handler) {
    if (typeof handler !== 'function') {
      throw new Error('Error handler must be a function');
    }
    
    this.errorHandlers.set(errorType, handler);
  }

  /**
   * Register recovery strategy
   */
  registerRecoveryStrategy(name, strategy) {
    if (typeof strategy !== 'function') {
      throw new Error('Recovery strategy must be a function');
    }
    
    this.recoveryStrategies.set(name, strategy);
  }

  /**
   * Clear temporary data for memory cleanup
   */
  clearTemporaryData() {
    // Clear old errors
    this.errors = this.errors.slice(0, Math.floor(this.maxErrors / 2));
    
    // Clear suppressed errors
    this.suppressedErrors.clear();
    
    // Clear old error counts
    for (const [key, count] of this.errorCounts) {
      if (count < 2) {
        this.errorCounts.delete(key);
      }
    }
  }

  /**
   * Generate unique error ID
   */
  generateErrorId() {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Utility delay function
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get error statistics
   */
  getErrorStatistics() {
    const stats = {
      total: this.errors.length,
      bySeverity: { critical: 0, high: 0, medium: 0, low: 0 },
      byType: {},
      recent: this.errors.slice(0, 10),
      mostCommon: [],
      suppressedCount: this.suppressedErrors.size
    };
    
    // Count by severity and type
    for (const error of this.errors) {
      stats.bySeverity[error.severity]++;
      stats.byType[error.type] = (stats.byType[error.type] || 0) + 1;
    }
    
    // Most common errors
    stats.mostCommon = Array.from(this.errorCounts.entries())
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([key, count]) => ({ error: key, count }));
    
    return stats;
  }

  /**
   * Clear all errors
   */
  clearErrors() {
    this.errors.length = 0;
    this.errorCounts.clear();
    this.suppressedErrors.clear();
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Export errors for analysis
   */
  exportErrors() {
    return {
      errors: this.errors,
      statistics: this.getErrorStatistics(),
      config: this.config,
      exportedAt: new Date().toISOString()
    };
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.clearErrors();
    this.errorHandlers.clear();
    this.recoveryStrategies.clear();
    console.log('Error Handler cleaned up');
  }
}

// Create and export singleton instance
const errorHandler = new ErrorHandler();

// Export both class and instance
window.ErrorHandler = ErrorHandler;
window.errorHandler = errorHandler;

export { ErrorHandler, errorHandler };
export default errorHandler;