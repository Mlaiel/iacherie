/**
 * 🔧 REACT HOC TEMPLATE - HIGHER-ORDER COMPONENTS
 * ===============================================
 * 
 * Enterprise-grade Higher-Order Component templates with:
 * - TypeScript support and strict typing
 * - Performance optimizations
 * - Error handling and validation
 * - Authentication and authorization
 * - Creator Economy features
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { ComponentType, forwardRef, useEffect, useState, useMemo } from 'react';

// Generic HOC type
export type HOC<InjectedProps, OriginalProps = {}> = <Props extends OriginalProps>(
  Component: ComponentType<Props & InjectedProps>
) => ComponentType<Omit<Props, keyof InjectedProps> & OriginalProps>;

// Loading HOC
export interface WithLoadingProps {
  isLoading?: boolean;
  loadingComponent?: React.ComponentType;
}

export function withLoading<P extends object>(
  LoadingComponent: React.ComponentType = () => <div>Loading...</div>
): HOC<WithLoadingProps, P> {
  return function WithLoadingHOC(WrappedComponent: ComponentType<P & WithLoadingProps>) {
    const WithLoadingComponent = forwardRef<any, P & WithLoadingProps>((props, ref) => {
      const { isLoading, loadingComponent, ...restProps } = props;
      
      if (isLoading) {
        const LoadingToRender = loadingComponent || LoadingComponent;
        return React.createElement(LoadingToRender);
      }
      
      return React.createElement(WrappedComponent, { 
        ...restProps as P & WithLoadingProps, 
        ref 
      });
    });

    WithLoadingComponent.displayName = `withLoading(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithLoadingComponent;
  };
}

// Error Boundary HOC
export interface WithErrorBoundaryProps {
  fallbackComponent?: React.ComponentType<{ error: Error; resetError: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export function withErrorBoundary<P extends object>(
  FallbackComponent: React.ComponentType<{ error: Error; resetError: () => void }> = ({ error, resetError }) => (
    <div style={{ padding: '20px', border: '2px solid red', borderRadius: '8px' }}>
      <h2>Something went wrong:</h2>
      <pre>{error.message}</pre>
      <button onClick={resetError}>Try again</button>
    </div>
  )
): HOC<WithErrorBoundaryProps, P> {
  return function WithErrorBoundaryHOC(WrappedComponent: ComponentType<P & WithErrorBoundaryProps>) {
    class ErrorBoundary extends React.Component<
      P & WithErrorBoundaryProps,
      { hasError: boolean; error?: Error }
    > {
      constructor(props: P & WithErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
      }

      static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
      }

      componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        this.props.onError?.(error, errorInfo);
        console.error('Error caught by HOC:', error, errorInfo);
      }

      resetError = () => {
        this.setState({ hasError: false, error: undefined });
      };

      render() {
        if (this.state.hasError && this.state.error) {
          const FallbackToRender = this.props.fallbackComponent || FallbackComponent;
          return React.createElement(FallbackToRender, {
            error: this.state.error,
            resetError: this.resetError
          });
        }

        const { fallbackComponent, onError, ...restProps } = this.props;
        return React.createElement(WrappedComponent, restProps as P & WithErrorBoundaryProps);
      }
    }

    ErrorBoundary.displayName = `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;
    return ErrorBoundary;
  };
}

// Authentication HOC
export interface WithAuthProps {
  user?: { id: string; name: string; role: string } | null;
  isAuthenticated?: boolean;
  requiredRole?: string;
  redirectTo?: string;
}

export function withAuth<P extends object>(
  options: {
    redirectTo?: string;
    requiredRole?: string;
    loadingComponent?: React.ComponentType;
  } = {}
): HOC<WithAuthProps, P> {
  return function WithAuthHOC(WrappedComponent: ComponentType<P & WithAuthProps>) {
    const WithAuthComponent = forwardRef<any, P & WithAuthProps>((props, ref) => {
      const [isLoading, setIsLoading] = useState(true);
      const [user, setUser] = useState<any>(null);

      useEffect(() => {
        // Simulate auth check
        const checkAuth = async () => {
          try {
            // Mock auth check
            const mockUser = { id: '1', name: 'John Doe', role: 'creator' };
            setUser(mockUser);
          } catch (error) {
            console.error('Auth check failed:', error);
          } finally {
            setIsLoading(false);
          }
        };

        checkAuth();
      }, []);

      if (isLoading) {
        const LoadingComponent = options.loadingComponent || (() => <div>Authenticating...</div>);
        return React.createElement(LoadingComponent);
      }

      const isAuthenticated = !!user;
      const hasRequiredRole = !options.requiredRole || user?.role === options.requiredRole;

      if (!isAuthenticated || !hasRequiredRole) {
        return React.createElement('div', {
          style: { padding: '20px', textAlign: 'center' }
        }, 'Access denied. Please log in.');
      }

      return React.createElement(WrappedComponent, {
        ...props as P & WithAuthProps,
        user,
        isAuthenticated,
        ref
      });
    });

    WithAuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithAuthComponent;
  };
}

// Performance HOC with memoization
export interface WithPerformanceProps {
  enableProfiling?: boolean;
  memoDependencies?: any[];
}

export function withPerformance<P extends object>(): HOC<WithPerformanceProps, P> {
  return function WithPerformanceHOC(WrappedComponent: ComponentType<P & WithPerformanceProps>) {
    const WithPerformanceComponent = React.memo(
      forwardRef<any, P & WithPerformanceProps>((props, ref) => {
        const { enableProfiling, memoDependencies, ...restProps } = props;
        const [renderCount, setRenderCount] = useState(0);
        const [renderTime, setRenderTime] = useState(0);

        const startTime = useMemo(() => performance.now(), [memoDependencies]);

        useEffect(() => {
          setRenderCount(prev => prev + 1);
          const endTime = performance.now();
          setRenderTime(endTime - startTime);

          if (enableProfiling) {
            console.log(`🔍 Performance Stats for ${WrappedComponent.displayName}:`, {
              renderCount: renderCount + 1,
              renderTime: `${(endTime - startTime).toFixed(2)}ms`
            });
          }
        });

        return React.createElement(WrappedComponent, {
          ...restProps as P & WithPerformanceProps,
          ref
        });
      }),
      (prevProps, nextProps) => {
        // Custom comparison for memoization
        const { memoDependencies: prevDeps } = prevProps;
        const { memoDependencies: nextDeps } = nextProps;
        
        if (prevDeps && nextDeps) {
          return JSON.stringify(prevDeps) === JSON.stringify(nextDeps);
        }
        
        return false; // Re-render if no dependencies specified
      }
    );

    WithPerformanceComponent.displayName = `withPerformance(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithPerformanceComponent;
  };
}

// Creator Economy HOC for content creators
export interface WithCreatorProps {
  creator?: {
    id: string;
    name: string;
    tier: 'basic' | 'pro' | 'enterprise';
    verified: boolean;
    subscriptions: number;
    revenue: number;
  };
  isCreator?: boolean;
  hasActiveSubscription?: boolean;
}

export function withCreator<P extends object>(): HOC<WithCreatorProps, P> {
  return function WithCreatorHOC(WrappedComponent: ComponentType<P & WithCreatorProps>) {
    const WithCreatorComponent = forwardRef<any, P & WithCreatorProps>((props, ref) => {
      const [creator, setCreator] = useState<any>(null);
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        // Mock creator data fetch
        const fetchCreatorData = async () => {
          try {
            const mockCreator = {
              id: '1',
              name: 'Jane Creator',
              tier: 'pro' as const,
              verified: true,
              subscriptions: 1250,
              revenue: 5400
            };
            setCreator(mockCreator);
          } catch (error) {
            console.error('Failed to fetch creator data:', error);
          } finally {
            setLoading(false);
          }
        };

        fetchCreatorData();
      }, []);

      if (loading) {
        return React.createElement('div', {}, 'Loading creator data...');
      }

      const isCreator = !!creator;
      const hasActiveSubscription = creator?.subscriptions > 0;

      return React.createElement(WrappedComponent, {
        ...props as P & WithCreatorProps,
        creator,
        isCreator,
        hasActiveSubscription,
        ref
      });
    });

    WithCreatorComponent.displayName = `withCreator(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithCreatorComponent;
  };
}

// Theme HOC
export interface WithThemeProps {
  theme?: {
    mode: 'light' | 'dark';
    colors: Record<string, string>;
    spacing: Record<string, string>;
  };
}

export function withTheme<P extends object>(
  defaultTheme: WithThemeProps['theme'] = {
    mode: 'light',
    colors: {
      primary: '#007bff',
      secondary: '#6c757d',
      background: '#ffffff',
      text: '#333333'
    },
    spacing: {
      sm: '8px',
      md: '16px',
      lg: '24px'
    }
  }
): HOC<WithThemeProps, P> {
  return function WithThemeHOC(WrappedComponent: ComponentType<P & WithThemeProps>) {
    const WithThemeComponent = forwardRef<any, P & WithThemeProps>((props, ref) => {
      const [theme, setTheme] = useState(defaultTheme);

      useEffect(() => {
        // Check for system theme preference
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (e: MediaQueryListEvent) => {
          setTheme(prev => prev ? {
            ...prev,
            mode: e.matches ? 'dark' : 'light'
          } : defaultTheme);
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
      }, []);

      return React.createElement(WrappedComponent, {
        ...props as P & WithThemeProps,
        theme,
        ref
      });
    });

    WithThemeComponent.displayName = `withTheme(${WrappedComponent.displayName || WrappedComponent.name})`;
    return WithThemeComponent;
  };
}

// Compose HOCs utility
export function compose<T>(...hocs: Array<(component: ComponentType<any>) => ComponentType<any>>) {
  return (component: ComponentType<T>) => hocs.reduceRight((acc, hoc) => hoc(acc), component);
}

// Example usage of composed HOCs
export const withAllEnhancements = compose(
  withLoading(),
  withErrorBoundary(),
  withAuth(),
  withPerformance(),
  withCreator(),
  withTheme()
);

// Export all HOCs
export const ReactHOCTemplates = {
  withLoading,
  withErrorBoundary,
  withAuth,
  withPerformance,
  withCreator,
  withTheme,
  compose,
  withAllEnhancements
};

export default ReactHOCTemplates;