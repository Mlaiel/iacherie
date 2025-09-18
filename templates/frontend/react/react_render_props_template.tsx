/**
 * 🎭 React Render Props Template - Enterprise Component Pattern
 * =============================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Advanced render props pattern implementation with TypeScript support,
 * performance optimization, and enterprise-grade features.
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
  ReactNode, 
  ComponentType, 
  useState, 
  useEffect, 
  useCallback, 
  useMemo,
  ErrorInfo 
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface BaseRenderPropsProps<T = any> {
  children: (data: T) => ReactNode;
  fallback?: ReactNode;
  errorFallback?: (error: Error) => ReactNode;
  loadingComponent?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  className?: string;
  testId?: string;
}

interface MouseTrackerData {
  x: number;
  y: number;
  isMoving: boolean;
  velocity: { x: number; y: number };
}

interface FetchData<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  cancel: () => void;
}

interface FormData<T> {
  values: T;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isValid: boolean;
  isDirty: boolean;
  handleChange: (field: string, value: any) => void;
  handleBlur: (field: string) => void;
  handleSubmit: (onSubmit: (values: T) => void) => void;
  reset: () => void;
}

interface ValidationConfig<T> {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any, values: T) => string | null;
}

// ========================================
// 🖱️ MOUSE TRACKER RENDER PROPS
// ========================================

interface MouseTrackerProps extends BaseRenderPropsProps<MouseTrackerData> {
  throttleMs?: number;
  trackVelocity?: boolean;
  boundingElement?: HTMLElement | null;
}

export const MouseTracker: React.FC<MouseTrackerProps> = ({
  children,
  fallback = null,
  throttleMs = 16,
  trackVelocity = true,
  boundingElement = null,
  className,
  testId = 'mouse-tracker'
}) => {
  const [mouseData, setMouseData] = useState<MouseTrackerData>({
    x: 0,
    y: 0,
    isMoving: false,
    velocity: { x: 0, y: 0 }
  });

  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });
  const [lastTimestamp, setLastTimestamp] = useState(Date.now());

  const handleMouseMove = useCallback((event: MouseEvent) => {
    const now = Date.now();
    const element = boundingElement || document.body;
    const rect = element.getBoundingClientRect();
    
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    let velocity = { x: 0, y: 0 };
    
    if (trackVelocity && now - lastTimestamp > 0) {
      const deltaTime = now - lastTimestamp;
      velocity = {
        x: (x - lastPosition.x) / deltaTime,
        y: (y - lastPosition.y) / deltaTime
      };
    }

    setMouseData({
      x,
      y,
      isMoving: true,
      velocity
    });

    setLastPosition({ x, y });
    setLastTimestamp(now);
  }, [boundingElement, trackVelocity, lastPosition, lastTimestamp]);

  const handleMouseLeave = useCallback(() => {
    setMouseData(prev => ({ ...prev, isMoving: false }));
  }, []);

  useEffect(() => {
    const element = boundingElement || document;
    let timeoutId: NodeJS.Timeout;

    const throttledMouseMove = (event: MouseEvent) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => handleMouseMove(event), throttleMs);
    };

    element.addEventListener('mousemove', throttledMouseMove);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mousemove', throttledMouseMove);
      element.removeEventListener('mouseleave', handleMouseLeave);
      clearTimeout(timeoutId);
    };
  }, [handleMouseMove, handleMouseLeave, throttleMs, boundingElement]);

  try {
    return (
      <div className={className} data-testid={testId}>
        {children(mouseData)}
      </div>
    );
  } catch (error) {
    console.error('MouseTracker Error:', error);
    return <>{fallback}</>;
  }
};

// ========================================
// 🌐 DATA FETCHER RENDER PROPS
// ========================================

interface DataFetcherProps<T> extends BaseRenderPropsProps<FetchData<T>> {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  transform?: (data: any) => T;
  refetchInterval?: number;
  retryCount?: number;
  cacheKey?: string;
}

export const DataFetcher = <T,>({
  children,
  url,
  method = 'GET',
  headers = {},
  body,
  transform,
  refetchInterval,
  retryCount = 3,
  cacheKey,
  fallback = null,
  errorFallback,
  className,
  testId = 'data-fetcher'
}: DataFetcherProps<T>) => {
  const [fetchData, setFetchData] = useState<FetchData<T>>({
    data: null,
    loading: true,
    error: null,
    refetch: () => {},
    cancel: () => {}
  });

  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const fetchRequest = useCallback(async (retries = retryCount) => {
    const controller = new AbortController();
    setAbortController(controller);

    try {
      setFetchData(prev => ({ ...prev, loading: true, error: null }));

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const rawData = await response.json();
      const processedData = transform ? transform(rawData) : rawData;

      if (cacheKey) {
        localStorage.setItem(`cache_${cacheKey}`, JSON.stringify({
          data: processedData,
          timestamp: Date.now()
        }));
      }

      setFetchData(prev => ({
        ...prev,
        data: processedData,
        loading: false,
        error: null
      }));

    } catch (error: any) {
      if (error.name === 'AbortError') return;

      if (retries > 0) {
        setTimeout(() => fetchRequest(retries - 1), 1000 * (retryCount - retries + 1));
        return;
      }

      setFetchData(prev => ({
        ...prev,
        data: null,
        loading: false,
        error: error as Error
      }));
    }
  }, [url, method, headers, body, transform, retryCount, cacheKey]);

  const refetch = useCallback(() => {
    fetchRequest();
  }, [fetchRequest]);

  const cancel = useCallback(() => {
    if (abortController) {
      abortController.abort();
    }
  }, [abortController]);

  useEffect(() => {
    // Check cache first
    if (cacheKey) {
      const cached = localStorage.getItem(`cache_${cacheKey}`);
      if (cached) {
        try {
          const { data, timestamp } = JSON.parse(cached);
          const maxAge = 5 * 60 * 1000; // 5 minutes
          if (Date.now() - timestamp < maxAge) {
            setFetchData(prev => ({
              ...prev,
              data,
              loading: false
            }));
            return;
          }
        } catch (e) {
          localStorage.removeItem(`cache_${cacheKey}`);
        }
      }
    }

    fetchRequest();

    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [fetchRequest, cacheKey]);

  useEffect(() => {
    if (refetchInterval && refetchInterval > 0) {
      const interval = setInterval(refetch, refetchInterval);
      return () => clearInterval(interval);
    }
  }, [refetch, refetchInterval]);

  const enhancedFetchData = useMemo(() => ({
    ...fetchData,
    refetch,
    cancel
  }), [fetchData, refetch, cancel]);

  try {
    if (fetchData.error && errorFallback) {
      return <>{errorFallback(fetchData.error)}</>;
    }

    return (
      <div className={className} data-testid={testId}>
        {children(enhancedFetchData)}
      </div>
    );
  } catch (error) {
    console.error('DataFetcher Error:', error);
    return <>{fallback}</>;
  }
};

// ========================================
// 📝 FORM MANAGER RENDER PROPS
// ========================================

interface FormManagerProps<T> extends BaseRenderPropsProps<FormData<T>> {
  initialValues: T;
  validationConfig?: Record<keyof T, ValidationConfig<T>>;
  onSubmit?: (values: T) => void | Promise<void>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
}

export const FormManager = <T extends Record<string, any>>({
  children,
  initialValues,
  validationConfig = {},
  onSubmit,
  validateOnChange = true,
  validateOnBlur = true,
  fallback = null,
  className,
  testId = 'form-manager'
}: FormManagerProps<T>) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateField = useCallback((field: string, value: any, allValues: T): string | null => {
    const config = validationConfig[field as keyof T];
    if (!config) return null;

    if (config.required && (!value || value.toString().trim() === '')) {
      return `${field} is required`;
    }

    if (config.minLength && value.toString().length < config.minLength) {
      return `${field} must be at least ${config.minLength} characters`;
    }

    if (config.maxLength && value.toString().length > config.maxLength) {
      return `${field} must be no more than ${config.maxLength} characters`;
    }

    if (config.pattern && !config.pattern.test(value.toString())) {
      return `${field} has invalid format`;
    }

    if (config.custom) {
      return config.custom(value, allValues);
    }

    return null;
  }, [validationConfig]);

  const validateAllFields = useCallback((fieldsToValidate: T): Record<string, string> => {
    const newErrors: Record<string, string> = {};

    Object.keys(fieldsToValidate).forEach(field => {
      const error = validateField(field, fieldsToValidate[field as keyof T], fieldsToValidate);
      if (error) {
        newErrors[field] = error;
      }
    });

    return newErrors;
  }, [validateField]);

  const handleChange = useCallback((field: string, value: any) => {
    const newValues = { ...values, [field]: value };
    setValues(newValues);

    if (validateOnChange) {
      const error = validateField(field, value, newValues);
      setErrors(prev => ({
        ...prev,
        [field]: error || ''
      }));
    }
  }, [values, validateOnChange, validateField]);

  const handleBlur = useCallback((field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));

    if (validateOnBlur) {
      const error = validateField(field, values[field as keyof T], values);
      setErrors(prev => ({
        ...prev,
        [field]: error || ''
      }));
    }
  }, [values, validateOnBlur, validateField]);

  const handleSubmit = useCallback((submitHandler: (values: T) => void) => {
    const newErrors = validateAllFields(values);
    setErrors(newErrors);
    setTouched(Object.keys(values).reduce((acc, key) => ({
      ...acc,
      [key]: true
    }), {}));

    if (Object.keys(newErrors).length === 0) {
      submitHandler(values);
      if (onSubmit) {
        onSubmit(values);
      }
    }
  }, [values, validateAllFields, onSubmit]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const formData = useMemo((): FormData<T> => ({
    values,
    errors,
    touched,
    isValid: Object.keys(errors).length === 0,
    isDirty: JSON.stringify(values) !== JSON.stringify(initialValues),
    handleChange,
    handleBlur,
    handleSubmit,
    reset
  }), [values, errors, touched, initialValues, handleChange, handleBlur, handleSubmit, reset]);

  try {
    return (
      <div className={className} data-testid={testId}>
        {children(formData)}
      </div>
    );
  } catch (error) {
    console.error('FormManager Error:', error);
    return <>{fallback}</>;
  }
};

// ========================================
// 🎯 VISIBILITY TRACKER RENDER PROPS
// ========================================

interface VisibilityData {
  isVisible: boolean;
  intersectionRatio: number;
  boundingClientRect: DOMRectReadOnly | null;
}

interface VisibilityTrackerProps extends BaseRenderPropsProps<VisibilityData> {
  threshold?: number | number[];
  rootMargin?: string;
  triggerOnce?: boolean;
  root?: Element | null;
}

export const VisibilityTracker: React.FC<VisibilityTrackerProps> = ({
  children,
  threshold = 0.1,
  rootMargin = '0px',
  triggerOnce = false,
  root = null,
  fallback = null,
  className,
  testId = 'visibility-tracker'
}) => {
  const [visibilityData, setVisibilityData] = useState<VisibilityData>({
    isVisible: false,
    intersectionRatio: 0,
    boundingClientRect: null
  });

  const [elementRef, setElementRef] = useState<Element | null>(null);
  const [hasTriggered, setHasTriggered] = useState(false);

  useEffect(() => {
    if (!elementRef || (triggerOnce && hasTriggered)) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isVisible = entry.isIntersecting;
        
        setVisibilityData({
          isVisible,
          intersectionRatio: entry.intersectionRatio,
          boundingClientRect: entry.boundingClientRect
        });

        if (isVisible && triggerOnce) {
          setHasTriggered(true);
        }
      },
      {
        threshold,
        rootMargin,
        root
      }
    );

    observer.observe(elementRef);

    return () => {
      observer.unobserve(elementRef);
    };
  }, [elementRef, threshold, rootMargin, root, triggerOnce, hasTriggered]);

  const containerRef = useCallback((node: Element | null) => {
    setElementRef(node);
  }, []);

  try {
    return (
      <div ref={containerRef} className={className} data-testid={testId}>
        {children(visibilityData)}
      </div>
    );
  } catch (error) {
    console.error('VisibilityTracker Error:', error);
    return <>{fallback}</>;
  }
};

// ========================================
// 📱 RESPONSIVE BREAKPOINT RENDER PROPS
// ========================================

interface BreakpointData {
  breakpoint: string;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isLargeDesktop: boolean;
  width: number;
  height: number;
}

interface BreakpointTrackerProps extends BaseRenderPropsProps<BreakpointData> {
  breakpoints?: Record<string, number>;
  debounceMs?: number;
}

const defaultBreakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1440,
  largeDesktop: 1920
};

export const BreakpointTracker: React.FC<BreakpointTrackerProps> = ({
  children,
  breakpoints = defaultBreakpoints,
  debounceMs = 100,
  fallback = null,
  className,
  testId = 'breakpoint-tracker'
}) => {
  const [breakpointData, setBreakpointData] = useState<BreakpointData>(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1024;
    const height = typeof window !== 'undefined' ? window.innerHeight : 768;
    
    return {
      breakpoint: getCurrentBreakpoint(width, breakpoints),
      isMobile: width < breakpoints.mobile,
      isTablet: width >= breakpoints.mobile && width < breakpoints.tablet,
      isDesktop: width >= breakpoints.tablet && width < breakpoints.desktop,
      isLargeDesktop: width >= breakpoints.desktop,
      width,
      height
    };
  });

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const handleResize = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        setBreakpointData({
          breakpoint: getCurrentBreakpoint(width, breakpoints),
          isMobile: width < breakpoints.mobile,
          isTablet: width >= breakpoints.mobile && width < breakpoints.tablet,
          isDesktop: width >= breakpoints.tablet && width < breakpoints.desktop,
          isLargeDesktop: width >= breakpoints.desktop,
          width,
          height
        });
      }, debounceMs);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(timeoutId);
    };
  }, [breakpoints, debounceMs]);

  try {
    return (
      <div className={className} data-testid={testId}>
        {children(breakpointData)}
      </div>
    );
  } catch (error) {
    console.error('BreakpointTracker Error:', error);
    return <>{fallback}</>;
  }
};

function getCurrentBreakpoint(width: number, breakpoints: Record<string, number>): string {
  const sortedBreakpoints = Object.entries(breakpoints).sort(([,a], [,b]) => a - b);
  
  for (let i = sortedBreakpoints.length - 1; i >= 0; i--) {
    const [name, minWidth] = sortedBreakpoints[i];
    if (width >= minWidth) {
      return name;
    }
  }
  
  return sortedBreakpoints[0]?.[0] || 'mobile';
}

// ========================================
// 🔄 ASYNC STATE RENDER PROPS
// ========================================

interface AsyncState<T, E = Error> {
  data: T | null;
  loading: boolean;
  error: E | null;
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

interface AsyncHandlerProps<T, E = Error> extends BaseRenderPropsProps<AsyncState<T, E>> {
  asyncFunction: (...args: any[]) => Promise<T>;
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: E) => void;
}

export const AsyncHandler = <T, E = Error>({
  children,
  asyncFunction,
  immediate = false,
  onSuccess,
  onError,
  fallback = null,
  className,
  testId = 'async-handler'
}: AsyncHandlerProps<T, E>) => {
  const [asyncState, setAsyncState] = useState<AsyncState<T, E>>({
    data: null,
    loading: false,
    error: null,
    execute: async () => {},
    reset: () => {}
  });

  const execute = useCallback(async (...args: any[]) => {
    try {
      setAsyncState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await asyncFunction(...args);
      
      setAsyncState(prev => ({ ...prev, data: result, loading: false }));
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (error) {
      const err = error as E;
      setAsyncState(prev => ({ ...prev, error: err, loading: false }));
      
      if (onError) {
        onError(err);
      }
    }
  }, [asyncFunction, onSuccess, onError]);

  const reset = useCallback(() => {
    setAsyncState(prev => ({
      ...prev,
      data: null,
      loading: false,
      error: null
    }));
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  const enhancedAsyncState = useMemo(() => ({
    ...asyncState,
    execute,
    reset
  }), [asyncState, execute, reset]);

  try {
    return (
      <div className={className} data-testid={testId}>
        {children(enhancedAsyncState)}
      </div>
    );
  } catch (error) {
    console.error('AsyncHandler Error:', error);
    return <>{fallback}</>;
  }
};

// ========================================
// 📦 EXPORTS
// ========================================

export {
  MouseTracker,
  DataFetcher,
  FormManager,
  VisibilityTracker,
  BreakpointTracker,
  AsyncHandler
};

export type {
  BaseRenderPropsProps,
  MouseTrackerData,
  FetchData,
  FormData,
  VisibilityData,
  BreakpointData,
  AsyncState,
  ValidationConfig
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Mouse Tracker Example
<MouseTracker>
  {({ x, y, isMoving, velocity }) => (
    <div>
      Mouse: ({x}, {y}) - Moving: {isMoving ? 'Yes' : 'No'}
      {isMoving && <p>Velocity: {velocity.x.toFixed(2)}, {velocity.y.toFixed(2)}</p>}
    </div>
  )}
</MouseTracker>

// Data Fetcher Example
<DataFetcher<User[]> 
  url="/api/users" 
  refetchInterval={30000}
  transform={(data) => data.users}
>
  {({ data, loading, error, refetch }) => (
    <div>
      {loading && <Spinner />}
      {error && <ErrorMessage error={error} />}
      {data && <UserList users={data} onRefresh={refetch} />}
    </div>
  )}
</DataFetcher>

// Form Manager Example
<FormManager
  initialValues={{ name: '', email: '', age: 0 }}
  validationConfig={{
    name: { required: true, minLength: 2 },
    email: { required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    age: { required: true, custom: (value) => value < 18 ? 'Must be 18+' : null }
  }}
>
  {({ values, errors, handleChange, handleSubmit, isValid }) => (
    <form onSubmit={() => handleSubmit(console.log)}>
      <input 
        value={values.name}
        onChange={(e) => handleChange('name', e.target.value)}
        placeholder="Name"
      />
      {errors.name && <span>{errors.name}</span>}
      
      <button type="submit" disabled={!isValid}>
        Submit
      </button>
    </form>
  )}
</FormManager>

// Visibility Tracker Example
<VisibilityTracker threshold={0.5} triggerOnce>
  {({ isVisible, intersectionRatio }) => (
    <div className={`fade-in ${isVisible ? 'visible' : 'hidden'}`}>
      <h2>Intersection Ratio: {(intersectionRatio * 100).toFixed(1)}%</h2>
      <p>This content fades in when 50% visible</p>
    </div>
  )}
</VisibilityTracker>

// Breakpoint Tracker Example
<BreakpointTracker>
  {({ isMobile, isTablet, isDesktop, width }) => (
    <div>
      <h3>Current Device: {isMobile ? 'Mobile' : isTablet ? 'Tablet' : 'Desktop'}</h3>
      <p>Screen Width: {width}px</p>
      {isMobile && <MobileLayout />}
      {isTablet && <TabletLayout />}
      {isDesktop && <DesktopLayout />}
    </div>
  )}
</BreakpointTracker>

// Async Handler Example
<AsyncHandler
  asyncFunction={(userId) => fetchUserProfile(userId)}
  onSuccess={(profile) => console.log('Profile loaded:', profile)}
  onError={(error) => console.error('Failed to load profile:', error)}
>
  {({ data, loading, error, execute }) => (
    <div>
      <button onClick={() => execute('123')}>Load Profile</button>
      {loading && <Spinner />}
      {error && <ErrorMessage error={error} />}
      {data && <UserProfile profile={data} />}
    </div>
  )}
</AsyncHandler>
*/