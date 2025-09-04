/**
 * Performance Utilities
 */

export const measureTime = async <T>(fn: () => Promise<T> | T): Promise<{ result: T; time: number }> => {
  const start = performance.now();
  const result = await fn();
  const time = performance.now() - start;
  return { result, time };
};

export const createPerformanceMonitor = () => {
  const metrics: { [key: string]: number[] } = {};
  
  return {
    start: (name: string) => {
      performance.mark(`${name}-start`);
    },
    
    end: (name: string) => {
      performance.mark(`${name}-end`);
      performance.measure(name, `${name}-start`, `${name}-end`);
      
      const measure = performance.getEntriesByName(name)[0];
      if (!metrics[name]) metrics[name] = [];
      metrics[name].push(measure.duration);
      
      performance.clearMarks(`${name}-start`);
      performance.clearMarks(`${name}-end`);
      performance.clearMeasures(name);
    },
    
    getMetrics: (name: string) => {
      const times = metrics[name] || [];
      if (times.length === 0) return null;
      
      const avg = times.reduce((sum, time) => sum + time, 0) / times.length;
      const min = Math.min(...times);
      const max = Math.max(...times);
      
      return { avg, min, max, count: times.length };
    },
    
    clear: (name?: string) => {
      if (name) {
        delete metrics[name];
      } else {
        Object.keys(metrics).forEach(key => delete metrics[key]);
      }
    },
  };
};

export const fps = (() => {
  let lastTime = 0;
  let frameCount = 0;
  let fps = 0;
  
  const update = (currentTime: number) => {
    frameCount++;
    
    if (currentTime - lastTime >= 1000) {
      fps = frameCount;
      frameCount = 0;
      lastTime = currentTime;
    }
    
    requestAnimationFrame(update);
  };
  
  requestAnimationFrame(update);
  
  return () => fps;
})();
