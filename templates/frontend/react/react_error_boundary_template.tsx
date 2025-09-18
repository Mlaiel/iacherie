/**
 * 🎨 REACT ERROR BOUNDARY TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ==================================================================
 * 
 * Enterprise-grade React error boundary template with:
 * - TypeScript support with strict typing
 * - Error logging and reporting
 * - Fallback UI components
 * - Error recovery mechanisms
 * - Development vs production modes
 * - Integration with monitoring services
 * - Accessibility compliance
 * 
 * ⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
 * ==========================================
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 * 
 * Author: Frontend Expert - Fahed Mlaiel
 * Version: 1.0.0
 */

import React, { 
  Component, 
  ErrorInfo, 
  ReactNode, 
  ComponentType,
  createElement
} from 'react';
import { motion } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
  retryCount: number;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ComponentType<ErrorFallbackProps> | ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
  isolate?: boolean;
  level?: 'page' | 'component' | 'feature';
  enableRetry?: boolean;
  maxRetries?: number;
  showErrorDetails?: boolean;
}

interface ErrorFallbackProps {
  error: Error;
  errorInfo: ErrorInfo;
  resetError: () => void;
  retryCount: number;
  canRetry: boolean;
  errorId: string;
}

interface ErrorLogEntry {
  timestamp: Date;
  error: Error;
  errorInfo: ErrorInfo;
  userAgent: string;
  url: string;
  userId?: string;
  sessionId?: string;
  buildVersion?: string;
  environment: string;
}

// ============================================================================
// ERROR LOGGING SERVICE
// ============================================================================

class ErrorLogger {
  private static instance: ErrorLogger;
  private logs: ErrorLogEntry[] = [];
  private maxLogs = 100;

  static getInstance(): ErrorLogger {
    if (!ErrorLogger.instance) {
      ErrorLogger.instance = new ErrorLogger();
    }
    return ErrorLogger.instance;
  }

  log(error: Error, errorInfo: ErrorInfo, additionalData?: Record<string, any>) {
    const entry: ErrorLogEntry = {
      timestamp: new Date(),
      error,
      errorInfo,
      userAgent: navigator.userAgent,
      url: window.location.href,
      environment: process.env.NODE_ENV || 'development',
      ...additionalData
    };

    this.logs.unshift(entry);
    
    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🚨 Error Boundary Caught Error');
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.error('Additional Data:', additionalData);
      console.groupEnd();
    }

    // Send to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToMonitoring(entry);
    }
  }

  private async sendToMonitoring(entry: ErrorLogEntry) {
    try {
      // Example integration with monitoring services
      // Replace with your actual monitoring service
      await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: entry.error.message,
          stack: entry.error.stack,
          componentStack: entry.errorInfo.componentStack,
          timestamp: entry.timestamp,
          url: entry.url,
          userAgent: entry.userAgent,
          environment: entry.environment
        })
      });
    } catch (monitoringError) {
      console.error('Failed to send error to monitoring:', monitoringError);
    }
  }

  getLogs(): ErrorLogEntry[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }
}

// ============================================================================
// DEFAULT ERROR FALLBACK COMPONENTS
// ============================================================================

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  retryCount,
  canRetry,
  errorId
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="error-boundary-fallback"
      style={{
        padding: '2rem',
        margin: '1rem',
        border: '2px solid #ff6b6b',
        borderRadius: '8px',
        backgroundColor: '#fff5f5',
        color: '#c53030',
        textAlign: 'center',
        maxWidth: '600px',
        marginLeft: 'auto',
        marginRight: 'auto'
      }}
      role="alert"
      aria-live="assertive"
    >
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
      
      <h2 style={{ marginBottom: '1rem', color: '#c53030' }}>
        Something went wrong
      </h2>
      
      <p style={{ marginBottom: '1.5rem', color: '#744210' }}>
        We encountered an unexpected error. Our team has been notified.
      </p>

      {isDevelopment && (
        <details style={{ 
          marginBottom: '1.5rem', 
          textAlign: 'left',
          backgroundColor: '#f7f7f7',
          padding: '1rem',
          borderRadius: '4px'
        }}>
          <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            Error Details (Development Mode)
          </summary>
          <p><strong>Error:</strong> {error.message}</p>
          <p><strong>Error ID:</strong> {errorId}</p>
          <p><strong>Retry Count:</strong> {retryCount}</p>
          {error.stack && (
            <pre style={{ 
              fontSize: '0.8rem', 
              overflow: 'auto',
              backgroundColor: '#fff',
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}>
              {error.stack}
            </pre>
          )}
        </details>
      )}

      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        {canRetry && (
          <button
            onClick={resetError}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#3182ce',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Try Again
          </button>
        )}
        
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#38a169',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Reload Page
        </button>
      </div>
    </motion.div>
  );
};

const MinimalErrorFallback: React.FC<ErrorFallbackProps> = ({ resetError, canRetry }) => (
  <div
    style={{
      padding: '1rem',
      backgroundColor: '#fed7d7',
      border: '1px solid #feb2b2',
      borderRadius: '4px',
      color: '#c53030',
      textAlign: 'center'
    }}
    role="alert"
  >
    <p>Unable to load this component.</p>
    {canRetry && (
      <button
        onClick={resetError}
        style={{
          marginTop: '0.5rem',
          padding: '0.5rem 1rem',
          backgroundColor: '#3182ce',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Retry
      </button>
    )}
  </div>
);

const FeatureErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError, canRetry }) => (
  <motion.div
    initial={{ scale: 0.9, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    style={{
      padding: '2rem',
      backgroundColor: '#f7fafc',
      border: '2px dashed #cbd5e0',
      borderRadius: '8px',
      textAlign: 'center',
      color: '#4a5568'
    }}
    role="alert"
  >
    <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔧</div>
    <h3 style={{ marginBottom: '0.5rem' }}>Feature Temporarily Unavailable</h3>
    <p style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
      This feature is experiencing issues and will be restored shortly.
    </p>
    {canRetry && (
      <button
        onClick={resetError}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#4299e1',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Try Again
      </button>
    )}
  </motion.div>
);

// ============================================================================
// MAIN ERROR BOUNDARY COMPONENT
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private errorLogger = ErrorLogger.getInstance();
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    
    // Log the error
    this.errorLogger.log(error, errorInfo, {
      level: this.props.level,
      retryCount: this.state.retryCount,
      errorId: this.state.errorId
    });

    // Call the onError callback if provided
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetOnPropsChange, resetKeys } = this.props;
    
    if (this.state.hasError && resetOnPropsChange) {
      if (resetKeys) {
        const hasResetKeyChanged = resetKeys.some(
          (resetKey, idx) => prevProps.resetKeys?.[idx] !== resetKey
        );
        
        if (hasResetKeyChanged) {
          this.resetError();
        }
      }
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  resetError = () => {
    const { maxRetries = 3 } = this.props;
    
    if (this.state.retryCount < maxRetries) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null,
        retryCount: this.state.retryCount + 1
      });
    }
  };

  getFallbackComponent(): ComponentType<ErrorFallbackProps> {
    const { fallback, level } = this.props;
    
    if (fallback) {
      if (typeof fallback === 'function') {
        return fallback;
      }
      // If fallback is a ReactNode, wrap it in a component
      return () => fallback as ReactElement;
    }
    
    // Default fallbacks based on level
    switch (level) {
      case 'page':
        return DefaultErrorFallback;
      case 'component':
        return MinimalErrorFallback;
      case 'feature':
        return FeatureErrorFallback;
      default:
        return DefaultErrorFallback;
    }
  }

  render() {
    const { children, enableRetry = true, maxRetries = 3 } = this.props;
    const { hasError, error, errorInfo, errorId, retryCount } = this.state;

    if (hasError && error && errorInfo) {
      const FallbackComponent = this.getFallbackComponent();
      const canRetry = enableRetry && retryCount < maxRetries;

      return createElement(FallbackComponent, {
        error,
        errorInfo,
        resetError: this.resetError,
        retryCount,
        canRetry,
        errorId: errorId || 'unknown'
      });
    }

    return children;
  }
}

// ============================================================================
// HIGHER-ORDER COMPONENT FOR ERROR BOUNDARIES
// ============================================================================

export function withErrorBoundary<P extends object>(
  Component: ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

// ============================================================================
// ERROR BOUNDARY HOOK
// ============================================================================

export function useErrorHandler() {
  return (error: Error, errorInfo?: ErrorInfo) => {
    const errorLogger = ErrorLogger.getInstance();
    errorLogger.log(error, errorInfo || { componentStack: '' });
    
    // Re-throw the error to trigger the nearest error boundary
    throw error;
  };
}

// ============================================================================
// SPECIALIZED ERROR BOUNDARIES
// ============================================================================

export const AsyncErrorBoundary: React.FC<{
  children: ReactNode;
  fallback?: ReactNode;
}> = ({ children, fallback }) => (
  <ErrorBoundary
    level="component"
    fallback={fallback || MinimalErrorFallback}
    enableRetry={true}
    maxRetries={2}
  >
    {children}
  </ErrorBoundary>
);

export const FeatureErrorBoundary: React.FC<{
  children: ReactNode;
  featureName?: string;
}> = ({ children, featureName }) => (
  <ErrorBoundary
    level="feature"
    fallback={FeatureErrorFallback}
    enableRetry={true}
    maxRetries={1}
    onError={(error, errorInfo) => {
      console.error(`Feature error in ${featureName}:`, error, errorInfo);
    }}
  >
    {children}
  </ErrorBoundary>
);

export const PageErrorBoundary: React.FC<{
  children: ReactNode;
}> = ({ children }) => (
  <ErrorBoundary
    level="page"
    fallback={DefaultErrorFallback}
    enableRetry={true}
    maxRetries={1}
    onError={(error, errorInfo) => {
      // Log to analytics/monitoring service
      console.error('Page-level error:', error, errorInfo);
    }}
  >
    {children}
  </ErrorBoundary>
);

// ============================================================================
// ERROR BOUNDARY CONTEXT
// ============================================================================

const ErrorBoundaryContext = React.createContext<{
  reportError: (error: Error, errorInfo?: ErrorInfo) => void;
  clearErrors: () => void;
  errorLogs: ErrorLogEntry[];
} | null>(null);

export const ErrorBoundaryProvider: React.FC<{
  children: ReactNode;
}> = ({ children }) => {
  const errorLogger = ErrorLogger.getInstance();

  const reportError = (error: Error, errorInfo?: ErrorInfo) => {
    errorLogger.log(error, errorInfo || { componentStack: '' });
  };

  const clearErrors = () => {
    errorLogger.clearLogs();
  };

  const errorLogs = errorLogger.getLogs();

  return (
    <ErrorBoundaryContext.Provider value={{ reportError, clearErrors, errorLogs }}>
      {children}
    </ErrorBoundaryContext.Provider>
  );
};

export function useErrorBoundaryContext() {
  const context = React.useContext(ErrorBoundaryContext);
  if (!context) {
    throw new Error('useErrorBoundaryContext must be used within ErrorBoundaryProvider');
  }
  return context;
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const ErrorBoundaryExamples: React.FC = () => {
  const ThrowErrorComponent = () => {
    const [shouldThrow, setShouldThrow] = React.useState(false);
    
    if (shouldThrow) {
      throw new Error('This is a test error!');
    }
    
    return (
      <button onClick={() => setShouldThrow(true)}>
        Throw Test Error
      </button>
    );
  };

  return (
    <div className="error-boundary-examples">
      <h2>Error Boundary Examples</h2>
      
      {/* Page-level error boundary */}
      <PageErrorBoundary>
        <div>
          <h3>Page Content</h3>
          <p>This content is protected by a page-level error boundary.</p>
        </div>
      </PageErrorBoundary>

      {/* Feature-level error boundary */}
      <FeatureErrorBoundary featureName="User Dashboard">
        <div>
          <h3>User Dashboard Feature</h3>
          <ThrowErrorComponent />
        </div>
      </FeatureErrorBoundary>

      {/* Component-level error boundary */}
      <AsyncErrorBoundary fallback={<div>Loading failed...</div>}>
        <div>
          <h3>Async Component</h3>
          <p>This component might fail to load.</p>
        </div>
      </AsyncErrorBoundary>

      {/* Custom error boundary with HOC */}
      {React.createElement(
        withErrorBoundary(ThrowErrorComponent, {
          level: 'component',
          enableRetry: true,
          maxRetries: 2,
          onError: (error) => console.log('Custom boundary caught:', error.message)
        })
      )}
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export {
  ErrorLogger,
  DefaultErrorFallback,
  MinimalErrorFallback,
  FeatureErrorFallback
};

export type {
  ErrorBoundaryProps,
  ErrorFallbackProps,
  ErrorLogEntry
};

export default ErrorBoundary;