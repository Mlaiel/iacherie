/**
 * 🎣 React Custom Hook Template - Advanced Hook Collection
 * ========================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade custom React hooks collection with TypeScript support,
 * performance optimization, and advanced patterns.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import { 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef,
  useReducer,
  useLayoutEffect,
  DependencyList,
  RefObject,
  MutableRefObject
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  cancel: () => void;
}

interface LocalStorageState<T> {
  value: T;
  setValue: (value: T | ((prev: T) => T)) => void;
  remove: () => void;
}

interface AsyncState<T, E = Error> {
  data: T | null;
  loading: boolean;
  error: E | null;
  execute: (...args: any[]) => Promise<T | void>;
  reset: () => void;
}

interface GeolocationState {
  coordinates: GeolocationCoordinates | null;
  loading: boolean;
  error: GeolocationPositionError | null;
  refresh: () => void;
}

interface NetworkState {
  online: boolean;
  downlink?: number;
  effectiveType?: string;
  rtt?: number;
  saveData?: boolean;
}

interface MediaQueryState {
  matches: boolean;
  media: string;
}

interface IntersectionState {
  isIntersecting: boolean;
  intersectionRatio: number;
  entry: IntersectionObserverEntry | null;
}

// ========================================
// 🌐 useApi - Advanced API Hook
// ========================================

interface UseApiOptions<T> {
  immediate?: boolean;
  transform?: (data: any) => T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retryCount?: number;
  retryDelay?: number;
  cacheKey?: string;
  cacheDuration?: number;
}

export const useApi = <T = any>(
  url: string,
  options: RequestInit & UseApiOptions<T> = {}
): ApiResponse<T> => {
  const {
    immediate = true,
    transform,
    onSuccess,
    onError,
    retryCount = 3,
    retryDelay = 1000,
    cacheKey,
    cacheDuration = 5 * 60 * 1000, // 5 minutes
    ...fetchOptions
  } = options;

  const [state, setState] = useState<Omit<ApiResponse<T>, 'refetch' | 'cancel'>>({
    data: null,
    loading: false,
    error: null
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  const fetchData = useCallback(async (retries = retryCount): Promise<void> => {
    if (!mountedRef.current) return;

    // Check cache first
    if (cacheKey) {
      try {
        const cached = localStorage.getItem(`api_cache_${cacheKey}`);
        if (cached) {
          const { data, timestamp } = JSON.parse(cached);
          if (Date.now() - timestamp < cacheDuration) {
            setState(prev => ({ ...prev, data: transform ? transform(data) : data, loading: false }));
            return;
          }
        }
      } catch (e) {
        localStorage.removeItem(`api_cache_${cacheKey}`);
      }
    }

    abortControllerRef.current = new AbortController();

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const response = await fetch(url, {
        ...fetchOptions,
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const rawData = await response.json();
      const processedData = transform ? transform(rawData) : rawData;

      // Cache the response
      if (cacheKey) {
        localStorage.setItem(`api_cache_${cacheKey}`, JSON.stringify({
          data: rawData,
          timestamp: Date.now()
        }));
      }

      if (mountedRef.current) {
        setState({ data: processedData, loading: false, error: null });
        onSuccess?.(processedData);
      }

    } catch (error: any) {
      if (error.name === 'AbortError') return;

      if (retries > 0 && mountedRef.current) {
        setTimeout(() => fetchData(retries - 1), retryDelay);
        return;
      }

      if (mountedRef.current) {
        const errorObj = error instanceof Error ? error : new Error(error);
        setState(prev => ({ ...prev, loading: false, error: errorObj }));
        onError?.(errorObj);
      }
    }
  }, [url, fetchOptions, transform, onSuccess, onError, retryCount, retryDelay, cacheKey, cacheDuration]);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    return () => {
      mountedRef.current = false;
      cancel();
    };
  }, [immediate, fetchData, cancel]);

  return {
    ...state,
    refetch: fetchData,
    cancel
  };
};

// ========================================
// 💾 useLocalStorage - Enhanced Local Storage Hook
// ========================================

export const useLocalStorage = <T>(
  key: string,
  defaultValue: T,
  options: { 
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
    syncAcrossTabs?: boolean;
  } = {}
): LocalStorageState<T> => {
  const {
    serialize = JSON.stringify,
    deserialize = JSON.parse,
    syncAcrossTabs = true
  } = options;

  const [state, setState] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? deserialize(item) : defaultValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return defaultValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(state) : value;
      setState(valueToStore);
      localStorage.setItem(key, serialize(valueToStore));
      
      // Dispatch custom event for cross-tab sync
      if (syncAcrossTabs) {
        window.dispatchEvent(new CustomEvent(`localStorage-${key}`, {
          detail: valueToStore
        }));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, serialize, state, syncAcrossTabs]);

  const remove = useCallback(() => {
    try {
      setState(defaultValue);
      localStorage.removeItem(key);
      
      if (syncAcrossTabs) {
        window.dispatchEvent(new CustomEvent(`localStorage-${key}`, {
          detail: undefined
        }));
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, defaultValue, syncAcrossTabs]);

  // Listen for changes from other tabs
  useEffect(() => {
    if (!syncAcrossTabs) return;

    const handleStorageChange = (e: CustomEvent) => {
      if (e.detail !== undefined) {
        setState(e.detail);
      } else {
        setState(defaultValue);
      }
    };

    const handleNativeStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setState(deserialize(e.newValue));
        } catch (error) {
          console.warn(`Error deserializing localStorage value for key "${key}":`, error);
        }
      }
    };

    window.addEventListener(`localStorage-${key}` as any, handleStorageChange);
    window.addEventListener('storage', handleNativeStorageChange);

    return () => {
      window.removeEventListener(`localStorage-${key}` as any, handleStorageChange);
      window.removeEventListener('storage', handleNativeStorageChange);
    };
  }, [key, defaultValue, deserialize, syncAcrossTabs]);

  return { value: state, setValue, remove };
};

// ========================================
// ⚡ useAsync - Advanced Async Operations Hook
// ========================================

export const useAsync = <T, E = Error>(
  asyncFunction: (...args: any[]) => Promise<T>,
  immediate = false
): AsyncState<T, E> => {
  const [state, setState] = useState<Omit<AsyncState<T, E>, 'execute' | 'reset'>>({
    data: null,
    loading: false,
    error: null
  });

  const mountedRef = useRef(true);

  const execute = useCallback(async (...args: any[]): Promise<T | void> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await asyncFunction(...args);
      
      if (mountedRef.current) {
        setState({ data: result, loading: false, error: null });
      }
      
      return result;
    } catch (error) {
      if (mountedRef.current) {
        setState(prev => ({ 
          ...prev, 
          loading: false, 
          error: error as E 
        }));
      }
      throw error;
    }
  }, [asyncFunction]);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    reset
  };
};

// ========================================
// 🎯 useIntersectionObserver - Visibility Detection Hook
// ========================================

export const useIntersectionObserver = (
  options: IntersectionObserverInit = {},
  targetRef?: RefObject<Element>
): [RefObject<Element>, IntersectionState] => {
  const defaultRef = useRef<Element>(null);
  const ref = targetRef || defaultRef;
  
  const [state, setState] = useState<IntersectionState>({
    isIntersecting: false,
    intersectionRatio: 0,
    entry: null
  });

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setState({
        isIntersecting: entry.isIntersecting,
        intersectionRatio: entry.intersectionRatio,
        entry
      });
    }, options);

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [ref, options]);

  return [ref, state];
};

// ========================================
// 📱 useMediaQuery - Responsive Breakpoints Hook
// ========================================

export const useMediaQuery = (query: string): MediaQueryState => {
  const [state, setState] = useState<MediaQueryState>({
    matches: false,
    media: query
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    setState({
      matches: mediaQuery.matches,
      media: query
    });

    const handler = (event: MediaQueryListEvent) => {
      setState({
        matches: event.matches,
        media: query
      });
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handler);
      return () => mediaQuery.removeListener(handler);
    }
  }, [query]);

  return state;
};

// ========================================
// 🌍 useGeolocation - Location Services Hook
// ========================================

export const useGeolocation = (
  options: PositionOptions = {}
): GeolocationState => {
  const [state, setState] = useState<GeolocationState>({
    coordinates: null,
    loading: false,
    error: null,
    refresh: () => {}
  });

  const watchIdRef = useRef<number | null>(null);

  const getCurrentPosition = useCallback(() => {
    if (!navigator.geolocation) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: { 
          code: 0, 
          message: 'Geolocation is not supported', 
          PERMISSION_DENIED: 1,
          POSITION_UNAVAILABLE: 2,
          TIMEOUT: 3
        } as GeolocationPositionError
      }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    const onSuccess = (position: GeolocationPosition) => {
      setState(prev => ({
        ...prev,
        coordinates: position.coords,
        loading: false,
        error: null
      }));
    };

    const onError = (error: GeolocationPositionError) => {
      setState(prev => ({
        ...prev,
        coordinates: null,
        loading: false,
        error
      }));
    };

    navigator.geolocation.getCurrentPosition(onSuccess, onError, options);
  }, [options]);

  const refresh = useCallback(() => {
    getCurrentPosition();
  }, [getCurrentPosition]);

  useEffect(() => {
    getCurrentPosition();

    // Watch position changes
    if (navigator.geolocation && options.enableHighAccuracy) {
      watchIdRef.current = navigator.geolocation.watchPosition(
        (position) => {
          setState(prev => ({
            ...prev,
            coordinates: position.coords,
            loading: false,
            error: null
          }));
        },
        (error) => {
          setState(prev => ({
            ...prev,
            error,
            loading: false
          }));
        },
        options
      );
    }

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, [getCurrentPosition, options]);

  return {
    ...state,
    refresh
  };
};

// ========================================
// 🌐 useNetworkState - Network Status Hook
// ========================================

export const useNetworkState = (): NetworkState => {
  const [state, setState] = useState<NetworkState>({
    online: navigator.onLine
  });

  useEffect(() => {
    const updateNetworkState = () => {
      const connection = (navigator as any).connection || 
                        (navigator as any).mozConnection || 
                        (navigator as any).webkitConnection;

      setState({
        online: navigator.onLine,
        downlink: connection?.downlink,
        effectiveType: connection?.effectiveType,
        rtt: connection?.rtt,
        saveData: connection?.saveData
      });
    };

    const handleOnline = () => updateNetworkState();
    const handleOffline = () => updateNetworkState();
    const handleConnectionChange = () => updateNetworkState();

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const connection = (navigator as any).connection;
    if (connection) {
      connection.addEventListener('change', handleConnectionChange);
    }

    // Initial update
    updateNetworkState();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if (connection) {
        connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, []);

  return state;
};

// ========================================
// ⏰ useInterval - Enhanced Interval Hook
// ========================================

export const useInterval = (
  callback: () => void,
  delay: number | null,
  options: {
    immediate?: boolean;
    pauseOnInvisible?: boolean;
  } = {}
): {
  start: () => void;
  stop: () => void;
  toggle: () => void;
  isActive: boolean;
} => {
  const { immediate = false, pauseOnInvisible = true } = options;
  const callbackRef = useRef(callback);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [isActive, setIsActive] = useState(false);

  // Update callback ref
  useLayoutEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const start = useCallback(() => {
    if (delay !== null && !intervalRef.current) {
      if (immediate) {
        callbackRef.current();
      }
      intervalRef.current = setInterval(() => callbackRef.current(), delay);
      setIsActive(true);
    }
  }, [delay, immediate]);

  const stop = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      setIsActive(false);
    }
  }, []);

  const toggle = useCallback(() => {
    if (isActive) {
      stop();
    } else {
      start();
    }
  }, [isActive, start, stop]);

  // Auto start/stop based on delay
  useEffect(() => {
    if (delay !== null) {
      start();
    } else {
      stop();
    }

    return stop;
  }, [delay, start, stop]);

  // Pause on page visibility change
  useEffect(() => {
    if (!pauseOnInvisible) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        stop();
      } else if (delay !== null) {
        start();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [pauseOnInvisible, delay, start, stop]);

  return { start, stop, toggle, isActive };
};

// ========================================
// 🔄 useUpdateEffect - Skip First Render Effect
// ========================================

export const useUpdateEffect = (
  effect: React.EffectCallback,
  deps?: DependencyList
): void => {
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    return effect();
  }, deps);
};

// ========================================
// 🎭 useToggle - Boolean State Toggle Hook
// ========================================

export const useToggle = (
  initialValue = false
): [boolean, (value?: boolean) => void, { setTrue: () => void; setFalse: () => void }] => {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback((newValue?: boolean) => {
    setValue(current => newValue !== undefined ? newValue : !current);
  }, []);

  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return [value, toggle, { setTrue, setFalse }];
};

// ========================================
// 📋 useClipboard - Clipboard Operations Hook
// ========================================

interface ClipboardState {
  value: string | null;
  copy: (text: string) => Promise<boolean>;
  paste: () => Promise<string | null>;
  isSupported: boolean;
}

export const useClipboard = (): ClipboardState => {
  const [value, setValue] = useState<string | null>(null);
  const isSupported = useMemo(() => 
    typeof navigator !== 'undefined' && 'clipboard' in navigator
  , []);

  const copy = useCallback(async (text: string): Promise<boolean> => {
    if (!isSupported) {
      // Fallback for older browsers
      try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          setValue(text);
        }
        return successful;
      } catch (error) {
        console.error('Failed to copy text:', error);
        return false;
      }
    }

    try {
      await navigator.clipboard.writeText(text);
      setValue(text);
      return true;
    } catch (error) {
      console.error('Failed to copy text:', error);
      return false;
    }
  }, [isSupported]);

  const paste = useCallback(async (): Promise<string | null> => {
    if (!isSupported) {
      console.warn('Clipboard API not supported');
      return null;
    }

    try {
      const text = await navigator.clipboard.readText();
      setValue(text);
      return text;
    } catch (error) {
      console.error('Failed to paste text:', error);
      return null;
    }
  }, [isSupported]);

  return { value, copy, paste, isSupported };
};

// ========================================
// 🔍 useDebounce - Debounced Values Hook
// ========================================

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// ========================================
// 🎮 useKeyPress - Keyboard Event Hook
// ========================================

export const useKeyPress = (
  targetKey: string | string[],
  options: {
    event?: 'keydown' | 'keyup';
    element?: HTMLElement | Document;
    preventDefault?: boolean;
  } = {}
): boolean => {
  const { event = 'keydown', element = document, preventDefault = false } = options;
  const [keyPressed, setKeyPressed] = useState(false);

  useEffect(() => {
    const keys = Array.isArray(targetKey) ? targetKey : [targetKey];

    const handleKeyEvent = (event: KeyboardEvent) => {
      if (keys.includes(event.key)) {
        if (preventDefault) {
          event.preventDefault();
        }
        setKeyPressed(true);
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (keys.includes(event.key)) {
        setKeyPressed(false);
      }
    };

    element.addEventListener(event, handleKeyEvent);
    if (event === 'keydown') {
      element.addEventListener('keyup', handleKeyUp);
    }

    return () => {
      element.removeEventListener(event, handleKeyEvent);
      if (event === 'keydown') {
        element.removeEventListener('keyup', handleKeyUp);
      }
    };
  }, [targetKey, event, element, preventDefault]);

  return keyPressed;
};

// ========================================
// 🎨 useDarkMode - Dark Mode Toggle Hook
// ========================================

export const useDarkMode = (
  initialValue?: boolean
): [boolean, (value?: boolean) => void, { 
  toggle: () => void; 
  enable: () => void; 
  disable: () => void;
}] => {
  const [isDarkMode, setIsDarkMode] = useLocalStorage('darkMode', initialValue ?? false);

  const setValue = useCallback((value?: boolean) => {
    setIsDarkMode(prev => value !== undefined ? value : !prev);
  }, [setIsDarkMode]);

  const toggle = useCallback(() => setValue(), [setValue]);
  const enable = useCallback(() => setValue(true), [setValue]);
  const disable = useCallback(() => setValue(false), [setValue]);

  // Apply dark mode class to document
  useEffect(() => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Listen for system preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      if (initialValue === undefined) {
        setIsDarkMode(e.matches);
      }
    };

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, [initialValue, setIsDarkMode]);

  return [isDarkMode, setValue, { toggle, enable, disable }];
};

// ========================================
// 📦 EXPORTS
// ========================================

export {
  useApi,
  useLocalStorage,
  useAsync,
  useIntersectionObserver,
  useMediaQuery,
  useGeolocation,
  useNetworkState,
  useInterval,
  useUpdateEffect,
  useToggle,
  useClipboard,
  useDebounce,
  useKeyPress,
  useDarkMode
};

export type {
  ApiResponse,
  LocalStorageState,
  AsyncState,
  GeolocationState,
  NetworkState,
  MediaQueryState,
  IntersectionState,
  ClipboardState
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// useApi Example
const { data, loading, error, refetch } = useApi<User[]>('/api/users', {
  immediate: true,
  transform: (response) => response.data.users,
  onSuccess: (users) => console.log('Users loaded:', users),
  cacheKey: 'users',
  retryCount: 3
});

// useLocalStorage Example
const [user, setUser] = useLocalStorage('user', null, {
  syncAcrossTabs: true
});

// useAsync Example
const { data, loading, error, execute, reset } = useAsync(
  async (userId: string) => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  }
);

// useIntersectionObserver Example
const [ref, { isIntersecting, intersectionRatio }] = useIntersectionObserver({
  threshold: 0.5,
  rootMargin: '100px'
});

// useMediaQuery Example
const { matches: isMobile } = useMediaQuery('(max-width: 768px)');

// useGeolocation Example
const { coordinates, loading, error, refresh } = useGeolocation({
  enableHighAccuracy: true,
  timeout: 10000
});

// useNetworkState Example
const { online, effectiveType, saveData } = useNetworkState();

// useInterval Example
const { start, stop, toggle, isActive } = useInterval(() => {
  console.log('Interval tick');
}, 1000, { immediate: true });

// useToggle Example
const [isOpen, toggle, { setTrue: open, setFalse: close }] = useToggle(false);

// useClipboard Example
const { copy, paste, isSupported } = useClipboard();

// useDebounce Example
const debouncedSearchTerm = useDebounce(searchTerm, 300);

// useKeyPress Example
const isEscapePressed = useKeyPress('Escape', {
  preventDefault: true
});

// useDarkMode Example
const [isDark, setDarkMode, { toggle: toggleDark }] = useDarkMode();
*/