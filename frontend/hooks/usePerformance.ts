import { useEffect, useCallback, useRef } from 'react';

export const usePerformance = (name: string) => {
  const startTimeRef = useRef<number>();

  const start = useCallback(() => {
    startTimeRef.current = performance.now();
  }, []);

  const end = useCallback(() => {
    if (startTimeRef.current) {
      const duration = performance.now() - startTimeRef.current;
      console.log(`${name} took ${duration.toFixed(2)}ms`);
      return duration;
    }
    return 0;
  }, [name]);

  return { start, end };
};
