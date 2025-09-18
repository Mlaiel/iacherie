/**
 * 🎣 REACT HOOK TEMPLATE - ENTERPRISE CUSTOM HOOKS
 * =================================================
 * 
 * Enterprise-grade React custom hook template with:
 * - TypeScript support and strict typing
 * - Performance optimization
 * - Error handling and validation
 * - Cleanup and memory management
 * - Testing utilities
 * - Creator Economy specialized hooks
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import { useState, useEffect, useCallback, useMemo, useRef, DependencyList } from 'react';

// Type definitions
export interface HookOptions {
  enableLogging?: boolean;
  enableProfiling?: boolean;
  enableErrorHandling?: boolean;
  debounceMs?: number;
  throttleMs?: number;
}

export interface HookResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retry: () => void;
  reset: () => void;
}

export interface AsyncHookOptions extends HookOptions {
  immediate?: boolean;
  deps?: DependencyList;
}

// Generic async hook for API calls
export function useAsyncOperation<T>(
  asyncFunction: () => Promise<T>,
  options: AsyncHookOptions = {}
): HookResult<T> {
  const {
    enableLogging = true,
    enableErrorHandling = true,
    immediate = true,
    deps = []
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  
  const isMountedRef = useRef<boolean>(true);
  const retryCountRef = useRef<number>(0);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async () => {
    if (!isMountedRef.current) return;

    setLoading(true);
    setError(null);

    try {
      if (enableLogging) {
        console.log(`🔄 Executing async operation (attempt ${retryCountRef.current + 1})`);
      }

      const result = await asyncFunction();
      
      if (isMountedRef.current) {
        setData(result);
        retryCountRef.current = 0;
        
        if (enableLogging) {
          console.log(`✅ Async operation completed successfully`);
        }
      }
    } catch (err) {
      if (isMountedRef.current) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        retryCountRef.current++;
        
        if (enableErrorHandling && enableLogging) {
          console.error(`❌ Async operation failed:`, error);
        }
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [asyncFunction, enableLogging, enableErrorHandling]);

  const retry = useCallback(() => {
    execute();
  }, [execute]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    retryCountRef.current = 0;
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate, ...deps]);

  return { data, loading, error, retry, reset };
}

// Debounced value hook
export function useDebounce<T>(value: T, delay: number): T {
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
}

// Local storage hook with SSR support
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // Get value from localStorage or use initial value
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that persists to localStorage
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        // Allow value to be a function so we have the same API as useState
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        
        // Save to localStorage
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        console.error(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Remove from localStorage
  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

// Previous value hook
export function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
}

// Media query hook
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const media = window.matchMedia(query);
    
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);

  return matches;
}

// Intersection Observer hook
export function useIntersectionObserver(
  ref: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
): IntersectionObserverEntry | null {
  const [intersectionObserverEntry, setIntersectionObserverEntry] = useState<IntersectionObserverEntry | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => setIntersectionObserverEntry(entry),
      options
    );

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
    };
  }, [ref, options]);

  return intersectionObserverEntry;
}

// Creator Economy specialized hook for content upload
export function useContentUpload() {
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const uploadFile = useCallback(async (file: File, onProgress?: (progress: number) => void) => {
    setIsUploading(true);
    setErrors([]);

    try {
      // Simulate file upload with progress
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadProgress(i);
        onProgress?.(i);
      }

      setUploadedFiles(prev => [...prev, file]);
      setUploadProgress(0);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setErrors(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const removeFile = useCallback((fileIndex: number) => {
    setUploadedFiles(prev => prev.filter((_, index) => index !== fileIndex));
  }, []);

  const clearAll = useCallback(() => {
    setUploadedFiles([]);
    setErrors([]);
    setUploadProgress(0);
  }, []);

  return {
    uploadFile,
    removeFile,
    clearAll,
    uploadProgress,
    isUploading,
    uploadedFiles,
    errors
  };
}

// Hook for managing creator collaboration
export function useCreatorCollaboration(creatorId: string) {
  const [collaborators, setCollaborators] = useState<any[]>([]);
  const [invitations, setInvitations] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const inviteCollaborator = useCallback(async (email: string, role: string) => {
    setLoading(true);
    try {
      // API call to invite collaborator
      const invitation = {
        id: Date.now().toString(),
        email,
        role,
        status: 'pending',
        createdAt: new Date()
      };
      setInvitations(prev => [...prev, invitation]);
    } catch (error) {
      console.error('Failed to invite collaborator:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const removeCollaborator = useCallback(async (collaboratorId: string) => {
    setCollaborators(prev => prev.filter(c => c.id !== collaboratorId));
  }, []);

  return {
    collaborators,
    invitations,
    loading,
    inviteCollaborator,
    removeCollaborator
  };
}

// Performance monitoring hook
export function usePerformanceMonitor(componentName: string) {
  const renderCountRef = useRef<number>(0);
  const renderTimesRef = useRef<number[]>([]);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    renderCountRef.current++;
    startTimeRef.current = performance.now();
  });

  useEffect(() => {
    const endTime = performance.now();
    const renderTime = endTime - startTimeRef.current;
    renderTimesRef.current.push(renderTime);

    // Keep only last 100 render times
    if (renderTimesRef.current.length > 100) {
      renderTimesRef.current.shift();
    }
  });

  const getStats = useMemo(() => ({
    renderCount: renderCountRef.current,
    averageRenderTime: renderTimesRef.current.length > 0 
      ? renderTimesRef.current.reduce((sum, time) => sum + time, 0) / renderTimesRef.current.length 
      : 0,
    lastRenderTime: renderTimesRef.current[renderTimesRef.current.length - 1] || 0
  }), []);

  return getStats;
}

// Export all hooks
export const ReactHookTemplates = {
  useAsyncOperation,
  useDebounce,
  useLocalStorage,
  usePrevious,
  useMediaQuery,
  useIntersectionObserver,
  useContentUpload,
  useCreatorCollaboration,
  usePerformanceMonitor
};

export default ReactHookTemplates;