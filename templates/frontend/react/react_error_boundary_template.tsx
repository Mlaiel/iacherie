/**
 * 🛡️ React Error Boundary Template - Advanced Error Handling
 * ===========================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade error boundary components with comprehensive error handling,
 * logging, recovery mechanisms, and user-friendly error UI.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { 
  Component, 
  ErrorInfo, 
  ReactNode, 
  useState, 
  useEffect,
  useCallback,
  createContext,
  useContext,
  useMemo
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface ErrorInfo {
  componentStack: string;
  errorBoundary?: string;
  errorBoundaryStack?: string;
}

interface ErrorDetails {
  error: Error;
  errorInfo: ErrorInfo;
  timestamp: number;
  userAgent: string;
  url: string;
  userId?: string;
  sessionId?: string;
  buildVersion?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
  retryCount: number;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: ErrorInfo, retry: () => void) => ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo, errorDetails: ErrorDetails) => void;
  enableRetry?: boolean;
  maxRetries?: number;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
  logLevel?: 'error' | 'warn' | 'info' | 'debug' | 'none';
  sendToAnalytics?: boolean;
  showErrorDetails?: boolean;
  className?: string;
  testId?: string;
}

interface ErrorRecoveryAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
}

interface GlobalErrorContextType {
  reportError: (error: Error, context?: string) => void;
  clearErrors: () => void;
  errors: ErrorDetails[];
  errorCount: number;
}

// ========================================
// 🌐 GLOBAL ERROR CONTEXT
// ========================================

const GlobalErrorContext = createContext<GlobalErrorContextType | null>(null);

export const useErrorHandler = () => {
  const context = useContext(GlobalErrorContext);
  if (!context) {
    throw new Error('useErrorHandler must be used within an ErrorProvider');
  }
  return context;
};

export const ErrorProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [errors, setErrors] = useState<ErrorDetails[]>([]);

  const reportError = useCallback((error: Error, context?: string) => {
    const errorDetails: ErrorDetails = {
      error,
      errorInfo: {
        componentStack: context || 'Global error handler',
      },
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: generateSessionId(),
    };

    setErrors(prev => [...prev, errorDetails]);
    
    // Send to analytics/logging service
    logError(errorDetails);
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const value = useMemo(() => ({
    reportError,
    clearErrors,
    errors,
    errorCount: errors.length
  }), [reportError, clearErrors, errors]);

  return (
    <GlobalErrorContext.Provider value={value}>
      {children}
    </GlobalErrorContext.Provider>
  );
};

// ========================================
// 🛡️ BASE ERROR BOUNDARY CLASS
// ========================================

class BaseErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private retryTimeoutId: number | null = null;

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
      errorId: generateErrorId()
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const { onError, logLevel = 'error', sendToAnalytics = true } = this.props;

    this.setState({ errorInfo });

    const errorDetails: ErrorDetails = {
      error,
      errorInfo,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: generateSessionId(),
    };

    // Log error based on log level
    this.logError(errorDetails, logLevel);

    // Send to analytics service
    if (sendToAnalytics) {
      this.sendToAnalytics(errorDetails);
    }

    // Call custom error handler
    if (onError) {
      onError(error, errorInfo, errorDetails);
    }
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetOnPropsChange, resetKeys } = this.props;
    const { hasError } = this.state;

    // Reset error state when specified props change
    if (hasError && resetOnPropsChange && resetKeys) {
      const hasResetKeyChanged = resetKeys.some(
        (key, index) => prevProps.resetKeys?.[index] !== key
      );

      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  componentWillUnmount() {
    if (this.retryTimeoutId) {
      clearTimeout(this.retryTimeoutId);
    }
  }

  private logError = (errorDetails: ErrorDetails, logLevel: string) => {
    const logMessage = `Error Boundary: ${errorDetails.error.message}`;
    
    switch (logLevel) {
      case 'error':
        console.error(logMessage, errorDetails);
        break;
      case 'warn':
        console.warn(logMessage, errorDetails);
        break;
      case 'info':
        console.info(logMessage, errorDetails);
        break;
      case 'debug':
        console.debug(logMessage, errorDetails);
        break;
      case 'none':
      default:
        break;
    }
  };

  private sendToAnalytics = (errorDetails: ErrorDetails) => {
    // Send error to analytics service (e.g., Sentry, LogRocket, etc.)
    try {
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'exception', {
          description: errorDetails.error.message,
          fatal: true,
          custom_map: {
            error_id: errorDetails.timestamp.toString(),
            component_stack: errorDetails.errorInfo.componentStack
          }
        });
      }

      // Example: Send to custom analytics endpoint
      fetch('/api/analytics/error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorDetails)
      }).catch(console.error);

    } catch (analyticsError) {
      console.error('Failed to send error to analytics:', analyticsError);
    }
  };

  private resetErrorBoundary = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    });
  };

  private handleRetry = () => {
    const { maxRetries = 3 } = this.props;
    const { retryCount } = this.state;

    if (retryCount < maxRetries) {
      this.setState(prevState => ({
        ...prevState,
        retryCount: prevState.retryCount + 1
      }));

      // Add delay before retry
      this.retryTimeoutId = window.setTimeout(() => {
        this.resetErrorBoundary();
      }, 1000 * (retryCount + 1));
    }
  };

  render() {
    const { 
      children, 
      fallback, 
      enableRetry = true, 
      maxRetries = 3, 
      showErrorDetails = false,
      className,
      testId = 'error-boundary'
    } = this.props;
    
    const { hasError, error, errorInfo, errorId, retryCount } = this.state;

    if (hasError && error && errorInfo) {
      // Custom fallback component
      if (fallback) {
        return (
          <div className={className} data-testid={testId}>
            {fallback(error, errorInfo, this.handleRetry)}
          </div>
        );
      }

      // Default error UI
      return (
        <DefaultErrorFallback
          error={error}
          errorInfo={errorInfo}
          errorId={errorId}
          retryCount={retryCount}
          maxRetries={maxRetries}
          onRetry={enableRetry ? this.handleRetry : undefined}
          showErrorDetails={showErrorDetails}
          className={className}
          testId={testId}
        />
      );
    }

    return children;
  }
}

// ========================================
// 🎨 DEFAULT ERROR FALLBACK COMPONENT
// ========================================

interface DefaultErrorFallbackProps {
  error: Error;
  errorInfo: ErrorInfo;
  errorId: string | null;
  retryCount: number;
  maxRetries: number;
  onRetry?: () => void;
  showErrorDetails: boolean;
  className?: string;
  testId?: string;
}

const DefaultErrorFallback: React.FC<DefaultErrorFallbackProps> = ({
  error,
  errorInfo,
  errorId,
  retryCount,
  maxRetries,
  onRetry,
  showErrorDetails,
  className,
  testId
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyError = useCallback(async () => {
    const errorText = `
Error ID: ${errorId}
Message: ${error.message}
Stack: ${error.stack}
Component Stack: ${errorInfo.componentStack}
Timestamp: ${new Date().toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}
    `.trim();

    try {
      await navigator.clipboard.writeText(errorText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy error details:', err);
    }
  }, [error, errorInfo, errorId]);

  const recoveryActions: ErrorRecoveryAction[] = [
    {
      label: 'Reload Page',
      action: () => window.location.reload(),
      variant: 'primary'
    },
    {
      label: 'Go to Home',
      action: () => window.location.href = '/',
      variant: 'secondary'
    },
    {
      label: 'Report Issue',
      action: () => {
        const subject = encodeURIComponent(`Error Report - ${errorId}`);
        const body = encodeURIComponent(`Error ID: ${errorId}\nMessage: ${error.message}`);
        window.open(`mailto:support@example.com?subject=${subject}&body=${body}`);
      },
      variant: 'secondary'
    }
  ];

  return (
    <div 
      className={`error-boundary-fallback ${className || ''}`}
      data-testid={testId}
      style={{
        padding: '2rem',
        margin: '1rem',
        border: '2px solid #ef4444',
        borderRadius: '8px',
        backgroundColor: '#fef2f2',
        color: '#991b1b',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}
    >
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ margin: '0 0 0.5rem 0', fontSize: '1.5rem', fontWeight: 'bold' }}>
          🚨 Something went wrong
        </h2>
        
        {errorId && (
          <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', opacity: 0.8 }}>
            Error ID: <code style={{ backgroundColor: '#fee2e2', padding: '0.25rem', borderRadius: '4px' }}>
              {errorId}
            </code>
          </p>
        )}

        <p style={{ margin: '0', fontSize: '1rem', lineHeight: '1.5' }}>
          An unexpected error occurred while rendering this component. 
          We apologize for the inconvenience.
        </p>
      </div>

      {/* Retry Section */}
      {onRetry && retryCount < maxRetries && (
        <div style={{ marginBottom: '1.5rem' }}>
          <button
            onClick={onRetry}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500'
            }}
          >
            🔄 Try Again {retryCount > 0 && `(${retryCount}/${maxRetries})`}
          </button>
        </div>
      )}

      {/* Recovery Actions */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.125rem', fontWeight: '600' }}>
          Recovery Options
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {recoveryActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: action.variant === 'primary' ? '#059669' : 
                               action.variant === 'danger' ? '#dc2626' : '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: '500'
              }}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error Details */}
      {showErrorDetails && (
        <div style={{ marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <button
              onClick={() => setShowDetails(!showDetails)}
              style={{
                padding: '0.25rem 0.5rem',
                backgroundColor: 'transparent',
                color: '#991b1b',
                border: '1px solid #991b1b',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              {showDetails ? '🔽 Hide' : '🔼 Show'} Technical Details
            </button>
            
            <button
              onClick={handleCopyError}
              style={{
                padding: '0.25rem 0.5rem',
                backgroundColor: copied ? '#059669' : 'transparent',
                color: copied ? 'white' : '#991b1b',
                border: `1px solid ${copied ? '#059669' : '#991b1b'}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              {copied ? '✅ Copied!' : '📋 Copy Error'}
            </button>
          </div>

          {showDetails && (
            <div style={{
              backgroundColor: '#fee2e2',
              border: '1px solid #fca5a5',
              borderRadius: '4px',
              padding: '1rem',
              fontSize: '0.875rem',
              fontFamily: 'monospace',
              overflowX: 'auto'
            }}>
              <div style={{ marginBottom: '0.75rem' }}>
                <strong>Error Message:</strong>
                <pre style={{ margin: '0.25rem 0', whiteSpace: 'pre-wrap' }}>{error.message}</pre>
              </div>
              
              <div style={{ marginBottom: '0.75rem' }}>
                <strong>Stack Trace:</strong>
                <pre style={{ margin: '0.25rem 0', whiteSpace: 'pre-wrap', fontSize: '0.75rem' }}>
                  {error.stack}
                </pre>
              </div>
              
              <div>
                <strong>Component Stack:</strong>
                <pre style={{ margin: '0.25rem 0', whiteSpace: 'pre-wrap', fontSize: '0.75rem' }}>
                  {errorInfo.componentStack}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Help Section */}
      <div style={{ 
        fontSize: '0.875rem', 
        color: '#7c2d12', 
        borderTop: '1px solid #fca5a5', 
        paddingTop: '1rem' 
      }}>
        <p style={{ margin: '0' }}>
          If this problem persists, please contact our support team with the error ID above.
        </p>
      </div>
    </div>
  );
};

// ========================================
// 🎭 FUNCTIONAL ERROR BOUNDARY WRAPPER
// ========================================

export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Partial<ErrorBoundaryProps>
) => {
  const WrappedComponent = (props: P) => (
    <BaseErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </BaseErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

// ========================================
// 🚨 ASYNC ERROR BOUNDARY
// ========================================

export const AsyncErrorBoundary: React.FC<ErrorBoundaryProps & {
  fallbackComponent?: React.ComponentType<{
    error: Error;
    retry: () => void;
    isRetrying: boolean;
  }>;
}> = ({ fallbackComponent: FallbackComponent, ...props }) => {
  const [isRetrying, setIsRetrying] = useState(false);

  const handleAsyncError = useCallback((error: Error, errorInfo: ErrorInfo) => {
    // Handle async errors (e.g., from promises, async/await)
    console.error('Async Error caught by Error Boundary:', error);
    
    if (props.onError) {
      const errorDetails: ErrorDetails = {
        error,
        errorInfo,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: generateSessionId(),
      };
      props.onError(error, errorInfo, errorDetails);
    }
  }, [props]);

  const customFallback = useCallback((error: Error, errorInfo: ErrorInfo, retry: () => void) => {
    if (FallbackComponent) {
      return (
        <FallbackComponent 
          error={error} 
          retry={() => {
            setIsRetrying(true);
            retry();
            setTimeout(() => setIsRetrying(false), 1000);
          }}
          isRetrying={isRetrying}
        />
      );
    }
    
    return null;
  }, [FallbackComponent, isRetrying]);

  useEffect(() => {
    // Global promise rejection handler
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const error = new Error(event.reason?.message || 'Unhandled Promise Rejection');
      handleAsyncError(error, { componentStack: 'Promise rejection' });
      event.preventDefault();
    };

    // Global error handler
    const handleGlobalError = (event: ErrorEvent) => {
      const error = new Error(event.message);
      error.stack = `${event.filename}:${event.lineno}:${event.colno}`;
      handleAsyncError(error, { componentStack: 'Global error' });
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleGlobalError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleGlobalError);
    };
  }, [handleAsyncError]);

  return (
    <BaseErrorBoundary 
      {...props}
      fallback={FallbackComponent ? customFallback : props.fallback}
      onError={handleAsyncError}
    />
  );
};

// ========================================
// 🎯 ROUTE ERROR BOUNDARY
// ========================================

export const RouteErrorBoundary: React.FC<ErrorBoundaryProps & {
  routeName?: string;
  redirectTo?: string;
}> = ({ routeName, redirectTo = '/', ...props }) => {
  const handleRouteError = useCallback((error: Error, errorInfo: ErrorInfo) => {
    console.error(`Route Error in ${routeName}:`, error);
    
    // Log route-specific error details
    logError({
      error,
      errorInfo: {
        ...errorInfo,
        componentStack: `Route: ${routeName}\n${errorInfo.componentStack}`
      },
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: generateSessionId(),
    });

    if (props.onError) {
      props.onError(error, errorInfo, {
        error,
        errorInfo,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: generateSessionId(),
      });
    }
  }, [routeName, props]);

  const routeFallback = useCallback((error: Error, errorInfo: ErrorInfo, retry: () => void) => (
    <div style={{ 
      padding: '2rem', 
      textAlign: 'center',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <h2>🚧 Route Error</h2>
      <p>There was an error loading this page.</p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1rem' }}>
        <button
          onClick={retry}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔄 Retry
        </button>
        <button
          onClick={() => window.location.href = redirectTo}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🏠 Go Home
        </button>
      </div>
    </div>
  ), [redirectTo]);

  return (
    <BaseErrorBoundary 
      {...props}
      fallback={props.fallback || routeFallback}
      onError={handleRouteError}
    />
  );
};

// ========================================
// 🔧 UTILITY FUNCTIONS
// ========================================

function generateErrorId(): string {
  return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateSessionId(): string {
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function logError(errorDetails: ErrorDetails): void {
  // Implementation would send to your logging service
  console.error('Error logged:', errorDetails);
}

// ========================================
// 📦 EXPORTS
// ========================================

export {
  BaseErrorBoundary as ErrorBoundary,
  ErrorProvider,
  useErrorHandler,
  withErrorBoundary,
  AsyncErrorBoundary,
  RouteErrorBoundary,
  DefaultErrorFallback
};

export type {
  ErrorBoundaryProps,
  ErrorBoundaryState,
  ErrorDetails,
  ErrorRecoveryAction,
  GlobalErrorContextType
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Error Boundary
<ErrorBoundary
  onError={(error, errorInfo, errorDetails) => {
    console.log('Error caught:', error);
    // Send to monitoring service
  }}
  enableRetry={true}
  maxRetries={3}
  showErrorDetails={true}
>
  <MyComponent />
</ErrorBoundary>

// Custom Error Fallback
<ErrorBoundary
  fallback={(error, errorInfo, retry) => (
    <div>
      <h2>Custom Error UI</h2>
      <p>{error.message}</p>
      <button onClick={retry}>Try Again</button>
    </div>
  )}
>
  <MyComponent />
</ErrorBoundary>

// HOC Usage
const SafeComponent = withErrorBoundary(MyComponent, {
  enableRetry: true,
  maxRetries: 2,
  onError: (error) => console.log('HOC Error:', error)
});

// Async Error Boundary
<AsyncErrorBoundary
  fallbackComponent={({ error, retry, isRetrying }) => (
    <div>
      <h2>Async Error: {error.message}</h2>
      <button onClick={retry} disabled={isRetrying}>
        {isRetrying ? 'Retrying...' : 'Retry'}
      </button>
    </div>
  )}
>
  <AsyncComponent />
</AsyncErrorBoundary>

// Route Error Boundary
<RouteErrorBoundary
  routeName="User Profile"
  redirectTo="/dashboard"
  onError={(error) => analytics.track('route_error', { route: 'profile' })}
>
  <UserProfilePage />
</RouteErrorBoundary>

// Global Error Provider
function App() {
  return (
    <ErrorProvider>
      <Router>
        <Routes>
          <Route path="/profile" element={
            <RouteErrorBoundary routeName="Profile">
              <ProfilePage />
            </RouteErrorBoundary>
          } />
        </Routes>
      </Router>
    </ErrorProvider>
  );
}

// Using Error Handler Hook
function MyComponent() {
  const { reportError } = useErrorHandler();
  
  const handleAsyncOperation = async () => {
    try {
      await riskyAsyncOperation();
    } catch (error) {
      reportError(error, 'Async operation failed');
    }
  };
  
  return <button onClick={handleAsyncOperation}>Do Risky Thing</button>;
}
*/