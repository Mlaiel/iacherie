/**
 * 🎨 REACT CUSTOM HOOK TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ==============================================================
 * 
 * Enterprise-grade React custom hooks collection with:
 * - TypeScript support with strict typing
 * - Performance optimization
 * - Reusable logic patterns
 * - State management hooks
 * - Side effect management
 * - Accessibility hooks
 * - Testing utilities
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

import { 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef,
  useReducer,
  useLayoutEffect,
  RefObject,
  DependencyList
} from 'react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

interface UseLocalStorageOptions {
  serialize?: (value: any) => string;
  deserialize?: (value: string) => any;
}

interface UseDebounceOptions {
  leading?: boolean;
  trailing?: boolean;
}

interface UseIntersectionObserverOptions extends IntersectionObserverInit {
  freezeOnceVisible?: boolean;
}

interface UseAsyncOptions {
  immediate?: boolean;
  resetOnExecute?: boolean;
}

interface UsePaginationOptions {
  initialPage?: number;
  pageSize?: number;
  total?: number;
}

interface PaginationState {
  currentPage: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

interface PaginationActions {
  goToPage: (page: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  setPageSize: (size: number) => void;
  setTotal: (total: number) => void;
}

// ============================================================================
// ASYNC DATA FETCHING HOOK
// ============================================================================

export function useApi<T>(
  fetcher: () => Promise<T>,
  dependencies: DependencyList = []
): ApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await fetcher();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error as Error 
      }));
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...state,
    refetch: fetchData
  };
}

// ============================================================================
// LOCAL STORAGE HOOK
// ============================================================================

export function useLocalStorage<T>(
  key: string,
  initialValue: T,
  options: UseLocalStorageOptions = {}
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  const {
    serialize = JSON.stringify,
    deserialize = JSON.parse
  } = options;

  // Get from local storage then parse stored json or return initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that persists the new value to localStorage
  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // Save state
      setStoredValue(valueToStore);
      
      // Save to local storage
      window.localStorage.setItem(key, serialize(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, serialize, storedValue]);

  // Remove from local storage
  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

// ============================================================================
// DEBOUNCE HOOK
// ============================================================================

export function useDebounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number,
  options: UseDebounceOptions = {}
): T {
  const { leading = false, trailing = true } = options;
  const timeoutRef = useRef<NodeJS.Timeout>();
  const funcRef = useRef(func);
  const lastCallRef = useRef<number>(0);

  // Keep function reference fresh
  useEffect(() => {
    funcRef.current = func;
  });

  return useCallback(
    ((...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastCall = now - lastCallRef.current;

      const executeFunc = () => {
        lastCallRef.current = now;
        return funcRef.current(...args);
      };

      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Leading edge execution
      if (leading && timeSinceLastCall >= delay) {
        return executeFunc();
      }

      // Trailing edge execution
      if (trailing) {
        timeoutRef.current = setTimeout(executeFunc, delay);
      }
    }) as T,
    [delay, leading, trailing]
  );
}

// ============================================================================
// INTERSECTION OBSERVER HOOK
// ============================================================================

export function useIntersectionObserver(
  elementRef: RefObject<Element>,
  options: UseIntersectionObserverOptions = {}
): IntersectionObserverEntry | undefined {
  const { freezeOnceVisible = false, ...observerOptions } = options;
  const [entry, setEntry] = useState<IntersectionObserverEntry>();

  const frozen = entry?.isIntersecting && freezeOnceVisible;

  const updateEntry = ([entry]: IntersectionObserverEntry[]): void => {
    setEntry(entry);
  };

  useEffect(() => {
    const node = elementRef?.current;
    const hasIOSupport = !!window.IntersectionObserver;

    if (!hasIOSupport || frozen || !node) return;

    const observerParams = { threshold: 0, ...observerOptions };
    const observer = new IntersectionObserver(updateEntry, observerParams);

    observer.observe(node);

    return () => observer.disconnect();
  }, [elementRef, JSON.stringify(observerOptions), frozen]);

  return entry;
}

// ============================================================================
// ASYNC STATE HOOK
// ============================================================================

export function useAsync<T, Args extends any[] = []>(
  asyncFunction: (...args: Args) => Promise<T>,
  options: UseAsyncOptions = {}
) {
  const { immediate = true, resetOnExecute = true } = options;
  
  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(
    async (...args: Args) => {
      if (resetOnExecute) {
        setState({ data: null, loading: true, error: null });
      } else {
        setState(prev => ({ ...prev, loading: true, error: null }));
      }

      try {
        const data = await asyncFunction(...args);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        setState(prev => ({ 
          ...prev, 
          loading: false, 
          error: error as Error 
        }));
        throw error;
      }
    },
    [asyncFunction, resetOnExecute]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return {
    ...state,
    execute
  };
}

// ============================================================================
// PREVIOUS VALUE HOOK
// ============================================================================

export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
}

// ============================================================================
// WINDOW SIZE HOOK
// ============================================================================

export function useWindowSize() {
  const [windowSize, setWindowSize] = useState(() => ({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0
  }));

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

// ============================================================================
// CLICK OUTSIDE HOOK
// ============================================================================

export function useClickOutside<T extends HTMLElement = HTMLElement>(
  handler: () => void
): RefObject<T> {
  const ref = useRef<T>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [handler]);

  return ref;
}

// ============================================================================
// PAGINATION HOOK
// ============================================================================

export function usePagination(
  options: UsePaginationOptions = {}
): PaginationState & PaginationActions {
  const {
    initialPage = 1,
    pageSize: initialPageSize = 10,
    total: initialTotal = 0
  } = options;

  const [state, setState] = useState({
    currentPage: initialPage,
    pageSize: initialPageSize,
    total: initialTotal
  });

  const computed = useMemo(() => {
    const totalPages = Math.ceil(state.total / state.pageSize);
    return {
      totalPages,
      hasNext: state.currentPage < totalPages,
      hasPrevious: state.currentPage > 1
    };
  }, [state.currentPage, state.pageSize, state.total]);

  const goToPage = useCallback((page: number) => {
    setState(prev => ({
      ...prev,
      currentPage: Math.max(1, Math.min(page, computed.totalPages))
    }));
  }, [computed.totalPages]);

  const nextPage = useCallback(() => {
    if (computed.hasNext) {
      setState(prev => ({ ...prev, currentPage: prev.currentPage + 1 }));
    }
  }, [computed.hasNext]);

  const previousPage = useCallback(() => {
    if (computed.hasPrevious) {
      setState(prev => ({ ...prev, currentPage: prev.currentPage - 1 }));
    }
  }, [computed.hasPrevious]);

  const setPageSize = useCallback((size: number) => {
    setState(prev => ({
      ...prev,
      pageSize: Math.max(1, size),
      currentPage: 1 // Reset to first page when changing page size
    }));
  }, []);

  const setTotal = useCallback((total: number) => {
    setState(prev => ({ ...prev, total: Math.max(0, total) }));
  }, []);

  return {
    ...state,
    ...computed,
    goToPage,
    nextPage,
    previousPage,
    setPageSize,
    setTotal
  };
}

// ============================================================================
// COPY TO CLIPBOARD HOOK
// ============================================================================

export function useCopyToClipboard(): [
  boolean,
  (text: string) => Promise<boolean>
] {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async (text: string): Promise<boolean> => {
    if (!navigator?.clipboard) {
      console.warn('Clipboard not supported');
      return false;
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      
      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000);
      
      return true;
    } catch (error) {
      console.error('Failed to copy text: ', error);
      setCopied(false);
      return false;
    }
  }, []);

  return [copied, copy];
}

// ============================================================================
// TOGGLE HOOK
// ============================================================================

export function useToggle(
  initialValue: boolean = false
): [boolean, () => void, (value?: boolean) => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  const setToggle = useCallback((newValue?: boolean) => {
    setValue(newValue ?? !value);
  }, [value]);

  return [value, toggle, setToggle];
}

// ============================================================================
// INTERVAL HOOK
// ============================================================================

export function useInterval(
  callback: () => void,
  delay: number | null
) {
  const savedCallback = useRef(callback);

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    if (delay !== null) {
      const id = setInterval(() => savedCallback.current(), delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

// ============================================================================
// MEDIA QUERY HOOK
// ============================================================================

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches);
    
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

// ============================================================================
// FORM VALIDATION HOOK
// ============================================================================

export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: Partial<Record<keyof T, (value: any) => string | undefined>>
) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const setValue = useCallback((field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  const setFieldTouched = useCallback((field: keyof T, isTouched: boolean = true) => {
    setTouched(prev => ({ ...prev, [field]: isTouched }));
  }, []);

  const validateField = useCallback((field: keyof T) => {
    const rule = validationRules[field];
    if (rule) {
      const error = rule(values[field]);
      setErrors(prev => ({ ...prev, [field]: error }));
      return !error;
    }
    return true;
  }, [values, validationRules]);

  const validateAll = useCallback(() => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach(field => {
      const rule = validationRules[field as keyof T];
      if (rule) {
        const error = rule(values[field as keyof T]);
        if (error) {
          newErrors[field as keyof T] = error;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [values, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0;
  }, [errors]);

  return {
    values,
    errors,
    touched,
    setValue,
    setFieldTouched,
    validateField,
    validateAll,
    reset,
    isValid
  };
}

// ============================================================================
// FOCUS TRAP HOOK
// ============================================================================

export function useFocusTrap<T extends HTMLElement = HTMLElement>(): RefObject<T> {
  const ref = useRef<T>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    // Get all focusable elements
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    element.addEventListener('keydown', handleTabKey);
    firstElement?.focus();

    return () => {
      element.removeEventListener('keydown', handleTabKey);
    };
  }, []);

  return ref;
}

// ============================================================================
// EXPORT ALL HOOKS
// ============================================================================

export default {
  useApi,
  useLocalStorage,
  useDebounce,
  useIntersectionObserver,
  useAsync,
  usePrevious,
  useWindowSize,
  useClickOutside,
  usePagination,
  useCopyToClipboard,
  useToggle,
  useInterval,
  useMediaQuery,
  useFormValidation,
  useFocusTrap
};