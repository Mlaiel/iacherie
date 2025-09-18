/**
 * ⚡ React Lazy Loading Template - Advanced Code Splitting
 * ========================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade lazy loading and code splitting implementation with
 * performance optimization, error handling, and advanced loading strategies.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { 
  Suspense, 
  lazy, 
  ReactNode, 
  ComponentType, 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef,
  memo,
  forwardRef,
  useImperativeHandle
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface LazyComponentProps {
  children?: ReactNode;
  fallback?: ReactNode;
  onLoading?: () => void;
  onLoaded?: () => void;
  onError?: (error: Error) => void;
  retry?: boolean;
  maxRetries?: number;
  timeout?: number;
  className?: string;
  testId?: string;
}

interface LazyImageProps {
  src: string;
  alt: string;
  placeholder?: string;
  className?: string;
  style?: React.CSSProperties;
  loading?: 'lazy' | 'eager';
  onLoad?: () => void;
  onError?: () => void;
  threshold?: number;
  rootMargin?: string;
}

interface LazyRouteProps extends LazyComponentProps {
  preload?: boolean;
  prefetch?: boolean;
}

interface PreloadOptions {
  prefetch?: boolean;
  priority?: 'high' | 'medium' | 'low';
  timeout?: number;
}

interface LazyModuleCache {
  [key: string]: {
    component: ComponentType<any>;
    timestamp: number;
    loading: boolean;
    error: Error | null;
  };
}

interface IntersectionObserverOptions {
  threshold?: number;
  rootMargin?: string;
  root?: Element | null;
}

// ========================================
// 🎭 ENHANCED LAZY COMPONENT WRAPPER
// ========================================

export const LazyComponent: React.FC<LazyComponentProps & {
  loader: () => Promise<{ default: ComponentType<any> }>;
  moduleId?: string;
}> = ({
  loader,
  moduleId,
  children,
  fallback = <DefaultLoadingFallback />,
  onLoading,
  onLoaded,
  onError,
  retry = true,
  maxRetries = 3,
  timeout = 10000,
  className,
  testId = 'lazy-component'
}) => {
  const [loadingState, setLoadingState] = useState<{
    loading: boolean;
    error: Error | null;
    retryCount: number;
  }>({
    loading: false,
    error: null,
    retryCount: 0
  });

  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const LazyLoadedComponent = useMemo(() => {
    return lazy(async () => {
      if (!mountedRef.current) throw new Error('Component unmounted');

      setLoadingState(prev => ({ ...prev, loading: true, error: null }));
      onLoading?.();

      // Set timeout for loading
      if (timeout > 0) {
        timeoutRef.current = setTimeout(() => {
          if (mountedRef.current) {
            const timeoutError = new Error(`Component loading timeout: ${timeout}ms`);
            setLoadingState(prev => ({ ...prev, loading: false, error: timeoutError }));
            onError?.(timeoutError);
          }
        }, timeout);
      }

      try {
        const result = await loader();
        
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        if (mountedRef.current) {
          setLoadingState(prev => ({ ...prev, loading: false, error: null }));
          onLoaded?.();
        }

        return result;
      } catch (error) {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        if (mountedRef.current) {
          const errorObj = error instanceof Error ? error : new Error(String(error));
          setLoadingState(prev => ({ ...prev, loading: false, error: errorObj }));
          onError?.(errorObj);
        }

        throw error;
      }
    });
  }, [loader, onLoading, onLoaded, onError, timeout]);

  const handleRetry = useCallback(() => {
    if (loadingState.retryCount < maxRetries) {
      setLoadingState(prev => ({
        ...prev,
        retryCount: prev.retryCount + 1,
        error: null
      }));
      
      // Force re-render to trigger lazy loading again
      window.location.reload();
    }
  }, [loadingState.retryCount, maxRetries]);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  if (loadingState.error && retry && loadingState.retryCount < maxRetries) {
    return (
      <ErrorRetryFallback 
        error={loadingState.error}
        onRetry={handleRetry}
        retryCount={loadingState.retryCount}
        maxRetries={maxRetries}
        className={className}
        testId={testId}
      />
    );
  }

  return (
    <div className={className} data-testid={testId}>
      <Suspense fallback={fallback}>
        <LazyLoadedComponent>
          {children}
        </LazyLoadedComponent>
      </Suspense>
    </div>
  );
};

// ========================================
// 🖼️ LAZY IMAGE COMPONENT
// ========================================

export const LazyImage: React.FC<LazyImageProps> = memo(({
  src,
  alt,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y0ZjRmNCIgdmlld0JveD0iMCAwIDEwMCAxMDAiPjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjZjRmNGY0Ii8+PC9zdmc+',
  className,
  style,
  loading = 'lazy',
  onLoad,
  onError,
  threshold = 0.1,
  rootMargin = '50px'
}) => {
  const [imageState, setImageState] = useState<{
    loaded: boolean;
    error: boolean;
    inView: boolean;
  }>({
    loaded: false,
    error: false,
    inView: false
  });

  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (loading === 'eager') {
      setImageState(prev => ({ ...prev, inView: true }));
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setImageState(prev => ({ ...prev, inView: true }));
          observer.disconnect();
        }
      },
      { threshold, rootMargin }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    observerRef.current = observer;

    return () => {
      observer.disconnect();
    };
  }, [threshold, rootMargin, loading]);

  const handleImageLoad = useCallback(() => {
    setImageState(prev => ({ ...prev, loaded: true, error: false }));
    onLoad?.();
  }, [onLoad]);

  const handleImageError = useCallback(() => {
    setImageState(prev => ({ ...prev, error: true, loaded: false }));
    onError?.();
  }, [onError]);

  // Preload image when in view
  useEffect(() => {
    if (imageState.inView && !imageState.loaded && !imageState.error) {
      const img = new Image();
      img.onload = handleImageLoad;
      img.onerror = handleImageError;
      img.src = src;
    }
  }, [imageState.inView, imageState.loaded, imageState.error, src, handleImageLoad, handleImageError]);

  return (
    <div 
      ref={imgRef}
      className={`lazy-image-container ${className || ''}`}
      style={{
        position: 'relative',
        overflow: 'hidden',
        ...style
      }}
    >
      {/* Placeholder */}
      {!imageState.loaded && !imageState.error && (
        <img
          src={placeholder}
          alt=""
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(5px)',
            transition: 'filter 0.3s ease'
          }}
        />
      )}

      {/* Actual Image */}
      {imageState.inView && (
        <img
          src={src}
          alt={alt}
          style={{
            position: imageState.loaded ? 'static' : 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: imageState.loaded ? 1 : 0,
            transition: 'opacity 0.3s ease'
          }}
          loading={loading}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      )}

      {/* Error State */}
      {imageState.error && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#666',
            textAlign: 'center'
          }}
        >
          <div>📷</div>
          <div style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Failed to load image
          </div>
        </div>
      )}

      {/* Loading State */}
      {imageState.inView && !imageState.loaded && !imageState.error && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#666'
          }}
        >
          <LoadingSpinner />
        </div>
      )}
    </div>
  );
});

LazyImage.displayName = 'LazyImage';

// ========================================
// 🛣️ LAZY ROUTE COMPONENT
// ========================================

export const LazyRoute: React.FC<LazyRouteProps & {
  component: () => Promise<{ default: ComponentType<any> }>;
  routeName?: string;
}> = ({
  component,
  routeName,
  preload = false,
  prefetch = false,
  ...lazyProps
}) => {
  const [preloaded, setPreloaded] = useState(false);

  // Preload component on hover or focus
  const handlePreload = useCallback(async () => {
    if (!preloaded) {
      try {
        await component();
        setPreloaded(true);
      } catch (error) {
        console.error(`Failed to preload route ${routeName}:`, error);
      }
    }
  }, [component, routeName, preloaded]);

  // Prefetch on mount
  useEffect(() => {
    if (prefetch) {
      handlePreload();
    }
  }, [prefetch, handlePreload]);

  return (
    <div onMouseEnter={preload ? handlePreload : undefined}>
      <LazyComponent
        loader={component}
        moduleId={routeName}
        {...lazyProps}
      />
    </div>
  );
};

// ========================================
// 📦 LAZY MODULE MANAGER
// ========================================

class LazyModuleManager {
  private cache: LazyModuleCache = {};
  private preloadQueue: Set<string> = new Set();

  async loadModule<T = any>(
    moduleId: string,
    loader: () => Promise<{ default: ComponentType<T> }>,
    options: PreloadOptions = {}
  ): Promise<ComponentType<T>> {
    // Check cache first
    if (this.cache[moduleId]?.component && !this.cache[moduleId]?.error) {
      return this.cache[moduleId].component;
    }

    // Check if already loading
    if (this.cache[moduleId]?.loading) {
      return new Promise((resolve, reject) => {
        const checkLoading = () => {
          const cached = this.cache[moduleId];
          if (cached && !cached.loading) {
            if (cached.error) {
              reject(cached.error);
            } else {
              resolve(cached.component);
            }
          } else {
            setTimeout(checkLoading, 100);
          }
        };
        checkLoading();
      });
    }

    // Start loading
    this.cache[moduleId] = {
      component: null as any,
      timestamp: Date.now(),
      loading: true,
      error: null
    };

    try {
      const { timeout = 10000 } = options;
      
      const loadPromise = loader();
      const timeoutPromise = new Promise<never>((_, reject) => 
        setTimeout(() => reject(new Error(`Module ${moduleId} loading timeout`)), timeout)
      );

      const result = await Promise.race([loadPromise, timeoutPromise]);

      this.cache[moduleId] = {
        component: result.default,
        timestamp: Date.now(),
        loading: false,
        error: null
      };

      return result.default;

    } catch (error) {
      const errorObj = error instanceof Error ? error : new Error(String(error));
      
      this.cache[moduleId] = {
        component: null as any,
        timestamp: Date.now(),
        loading: false,
        error: errorObj
      };

      throw errorObj;
    }
  }

  preloadModule(
    moduleId: string, 
    loader: () => Promise<{ default: ComponentType<any> }>,
    options: PreloadOptions = {}
  ): void {
    if (this.preloadQueue.has(moduleId) || this.cache[moduleId]?.component) {
      return;
    }

    this.preloadQueue.add(moduleId);

    const { priority = 'low' } = options;

    const preloadWithPriority = () => {
      this.loadModule(moduleId, loader, options)
        .then(() => {
          console.log(`Module ${moduleId} preloaded successfully`);
        })
        .catch((error) => {
          console.error(`Failed to preload module ${moduleId}:`, error);
        })
        .finally(() => {
          this.preloadQueue.delete(moduleId);
        });
    };

    // Schedule based on priority
    switch (priority) {
      case 'high':
        preloadWithPriority();
        break;
      case 'medium':
        setTimeout(preloadWithPriority, 100);
        break;
      case 'low':
      default:
        requestIdleCallback ? 
          requestIdleCallback(preloadWithPriority) : 
          setTimeout(preloadWithPriority, 1000);
        break;
    }
  }

  clearCache(moduleId?: string): void {
    if (moduleId) {
      delete this.cache[moduleId];
    } else {
      this.cache = {};
    }
  }

  getCacheInfo(): LazyModuleCache {
    return { ...this.cache };
  }
}

export const lazyModuleManager = new LazyModuleManager();

// ========================================
// 🎣 LAZY LOADING HOOKS
// ========================================

export const useLazyLoad = <T>(
  loader: () => Promise<T>,
  deps: React.DependencyList = []
): {
  data: T | null;
  loading: boolean;
  error: Error | null;
  reload: () => void;
} => {
  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null
  });

  const mountedRef = useRef(true);

  const load = useCallback(async () => {
    if (!mountedRef.current) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await loader();
      
      if (mountedRef.current) {
        setState({ data: result, loading: false, error: null });
      }
    } catch (error) {
      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error : new Error(String(error))
        }));
      }
    }
  }, deps);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    ...state,
    reload: load
  };
};

export const useIntersectionObserver = (
  options: IntersectionObserverOptions = {}
): [React.RefCallback<Element>, boolean] => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [element, setElement] = useState<Element | null>(null);

  const ref = useCallback((node: Element | null) => {
    setElement(node);
  }, []);

  useEffect(() => {
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      options
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [element, options]);

  return [ref, isIntersecting];
};

// ========================================
// 🎨 FALLBACK COMPONENTS
// ========================================

const DefaultLoadingFallback: React.FC = () => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      color: '#666'
    }}
  >
    <LoadingSpinner />
    <span style={{ marginLeft: '0.5rem' }}>Loading...</span>
  </div>
);

const ErrorRetryFallback: React.FC<{
  error: Error;
  onRetry: () => void;
  retryCount: number;
  maxRetries: number;
  className?: string;
  testId?: string;
}> = ({ error, onRetry, retryCount, maxRetries, className, testId }) => (
  <div 
    className={className}
    data-testid={testId}
    style={{
      padding: '2rem',
      textAlign: 'center',
      color: '#e53e3e',
      border: '1px solid #fed7d7',
      borderRadius: '8px',
      backgroundColor: '#fef5f5'
    }}
  >
    <h3 style={{ margin: '0 0 1rem 0' }}>⚠️ Loading Error</h3>
    <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem' }}>
      {error.message}
    </p>
    
    {retryCount < maxRetries && (
      <button
        onClick={onRetry}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#3182ce',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '0.875rem'
        }}
      >
        🔄 Retry ({retryCount + 1}/{maxRetries})
      </button>
    )}
    
    {retryCount >= maxRetries && (
      <p style={{ margin: '1rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
        Max retries exceeded. Please refresh the page.
      </p>
    )}
  </div>
);

const LoadingSpinner: React.FC = () => (
  <div
    style={{
      width: '20px',
      height: '20px',
      border: '2px solid #f3f3f3',
      borderTop: '2px solid #3498db',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite'
    }}
  />
);

// Add CSS animation for spinner
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);
}

// ========================================
// 🔧 UTILITY FUNCTIONS
// ========================================

export const createLazyComponent = <P extends object>(
  loader: () => Promise<{ default: ComponentType<P> }>,
  options: {
    fallback?: ReactNode;
    onError?: (error: Error) => void;
    moduleId?: string;
  } = {}
): ComponentType<P> => {
  const LazyComponentWrapper = (props: P) => (
    <LazyComponent
      loader={loader}
      moduleId={options.moduleId}
      fallback={options.fallback}
      onError={options.onError}
    >
      {props.children}
    </LazyComponent>
  );

  LazyComponentWrapper.displayName = `Lazy(${options.moduleId || 'Component'})`;
  
  return LazyComponentWrapper as ComponentType<P>;
};

export const preloadComponent = (
  loader: () => Promise<{ default: ComponentType<any> }>,
  moduleId: string,
  options: PreloadOptions = {}
): void => {
  lazyModuleManager.preloadModule(moduleId, loader, options);
};

// ========================================
// 📦 EXPORTS
// ========================================

export {
  LazyComponent,
  LazyImage,
  LazyRoute,
  lazyModuleManager,
  useLazyLoad,
  useIntersectionObserver,
  createLazyComponent,
  preloadComponent,
  DefaultLoadingFallback,
  ErrorRetryFallback,
  LoadingSpinner
};

export type {
  LazyComponentProps,
  LazyImageProps,
  LazyRouteProps,
  PreloadOptions,
  LazyModuleCache,
  IntersectionObserverOptions
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Lazy Component
const LazyDashboard = lazy(() => import('./Dashboard'));

<Suspense fallback={<div>Loading...</div>}>
  <LazyDashboard />
</Suspense>

// Enhanced Lazy Component
<LazyComponent
  loader={() => import('./HeavyComponent')}
  fallback={<CustomLoadingSpinner />}
  onLoading={() => console.log('Loading started')}
  onLoaded={() => console.log('Loading completed')}
  onError={(error) => console.error('Loading failed:', error)}
  retry={true}
  maxRetries={3}
  timeout={5000}
>
  <HeavyComponent />
</LazyComponent>

// Lazy Image with Intersection Observer
<LazyImage
  src="/large-image.jpg"
  alt="Description"
  placeholder="/placeholder.jpg"
  onLoad={() => console.log('Image loaded')}
  threshold={0.5}
  rootMargin="100px"
/>

// Lazy Route with Preloading
<LazyRoute
  component={() => import('./ProfilePage')}
  routeName="Profile"
  preload={true}
  prefetch={true}
  fallback={<PageLoadingSkeleton />}
/>

// Using Lazy Load Hook
function MyComponent() {
  const { data, loading, error, reload } = useLazyLoad(
    () => import('./ExpensiveModule'),
    []
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return <data.default />;
}

// Using Intersection Observer Hook
function LazySection() {
  const [ref, isVisible] = useIntersectionObserver({
    threshold: 0.5,
    rootMargin: '100px'
  });

  return (
    <div ref={ref}>
      {isVisible && <ExpensiveComponent />}
    </div>
  );
}

// Creating Lazy Component with Factory
const LazyChart = createLazyComponent(
  () => import('./Chart'),
  {
    fallback: <ChartSkeleton />,
    moduleId: 'chart',
    onError: (error) => analytics.track('lazy_load_error', { module: 'chart' })
  }
);

// Preloading Components
preloadComponent(
  () => import('./Dashboard'),
  'dashboard',
  { priority: 'high', timeout: 5000 }
);

// Using Module Manager
const dashboard = await lazyModuleManager.loadModule(
  'dashboard',
  () => import('./Dashboard')
);
*/