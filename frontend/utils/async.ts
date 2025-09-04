/**
 * Async Utilities
 */

export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

export const retry = async <T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  delay = 1000
): Promise<T> => {
  let lastError: Error;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt === maxAttempts) break;
      await sleep(delay * attempt);
    }
  }
  
  throw lastError!;
};

export const timeout = <T>(promise: Promise<T>, ms: number): Promise<T> => {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Operation timed out')), ms)
    )
  ]);
};

export const promisePool = async <T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  concurrency = 3
): Promise<R[]> => {
  const results: R[] = [];
  const executing: Promise<void>[] = [];
  
  for (const item of items) {
    const promise = processor(item).then(result => {
      results.push(result);
    });
    
    executing.push(promise);
    
    if (executing.length >= concurrency) {
      await Promise.race(executing);
      const finishedIndex = executing.findIndex(p => 
        p === Promise.resolve(p).then(() => p)
      );
      if (finishedIndex >= 0) {
        executing.splice(finishedIndex, 1);
      }
    }
  }
  
  await Promise.all(executing);
  return results;
};

export const memoizeAsync = <T extends any[], R>(
  fn: (...args: T) => Promise<R>,
  ttl = 5 * 60 * 1000 // 5 minutes
) => {
  const cache = new Map<string, { value: R; expiry: number }>();
  
  return async (...args: T): Promise<R> => {
    const key = JSON.stringify(args);
    const cached = cache.get(key);
    
    if (cached && Date.now() < cached.expiry) {
      return cached.value;
    }
    
    const result = await fn(...args);
    cache.set(key, { value: result, expiry: Date.now() + ttl });
    
    return result;
  };
};
