/**
 * 📊 PERFORMANCE MONITOR - ENTERPRISE MONITORING SYSTEM
 * =====================================================
 * 
 * Advanced Performance Monitoring for Frontend Templates
 * Real-time metrics, Web Vitals, Component performance
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

// Web Vitals Interfaces
export interface WebVitalsMetric {
  name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB' | 'INP';
  value: number;
  delta: number;
  id: string;
  rating: 'good' | 'needs-improvement' | 'poor';
  navigationType: 'navigate' | 'reload' | 'back-forward' | 'back-forward-cache';
}

export interface ComponentMetric {
  name: string;
  renderTime: number;
  mountTime: number;
  updateCount: number;
  lastUpdate: number;
  memoryUsage?: number;
  errors: PerformanceError[];
}

export interface PerformanceError {
  message: string;
  stack?: string;
  timestamp: number;
  component?: string;
  type: 'render' | 'mount' | 'update' | 'runtime';
}

export interface NetworkMetric {
  url: string;
  method: string;
  status: number;
  duration: number;
  size: number;
  timestamp: number;
  type: 'fetch' | 'xhr' | 'beacon';
}

export interface BundleMetric {
  name: string;
  size: number;
  loadTime: number;
  cacheStatus: 'hit' | 'miss' | 'stale';
  compression: 'gzip' | 'brotli' | 'none';
}

export interface PerformanceReport {
  timestamp: number;
  sessionId: string;
  webVitals: WebVitalsMetric[];
  components: ComponentMetric[];
  network: NetworkMetric[];
  bundles: BundleMetric[];
  runtime: {
    heapUsed: number;
    heapTotal: number;
    heapLimit: number;
    jsHeapSizeLimit?: number;
  };
  device: {
    userAgent: string;
    viewport: { width: number; height: number };
    connection?: {
      effectiveType: string;
      downlink: number;
      rtt: number;
    };
  };
}

// Performance Monitor Class
export class PerformanceMonitor {
  private metrics: Map<string, ComponentMetric> = new Map();
  private webVitals: WebVitalsMetric[] = [];
  private networkMetrics: NetworkMetric[] = [];
  private bundleMetrics: BundleMetric[] = [];
  private errors: PerformanceError[] = [];
  private observers: Map<string, PerformanceObserver> = new Map();
  private sessionId: string = this.generateSessionId();
  private isEnabled: boolean = true;
  private thresholds = {
    renderTime: 16, // 60fps threshold
    componentSize: 1000000, // 1MB component threshold
    bundleSize: 5000000, // 5MB bundle threshold
    lcp: 2500, // Good LCP threshold
    fid: 100, // Good FID threshold
    cls: 0.1, // Good CLS threshold
  };

  constructor(options?: {
    enabled?: boolean;
    thresholds?: Partial<typeof PerformanceMonitor.prototype.thresholds>;
    reportInterval?: number;
  }) {
    if (options?.enabled !== undefined) {
      this.isEnabled = options.enabled;
    }
    
    if (options?.thresholds) {
      this.thresholds = { ...this.thresholds, ...options.thresholds };
    }

    if (this.isEnabled && typeof window !== 'undefined') {
      this.initializeObservers();
      this.initializeWebVitals();
      this.initializeNetworkMonitoring();
      this.startReporting(options?.reportInterval || 30000);
    }
  }

  private generateSessionId(): string {
    return `perf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeObservers(): void {
    if (!window.PerformanceObserver) return;

    // Paint Observer
    try {
      const paintObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'paint') {
            this.recordPaintMetric(entry as PerformancePaintTiming);
          }
        }
      });
      paintObserver.observe({ entryTypes: ['paint'] });
      this.observers.set('paint', paintObserver);
    } catch (error) {
      console.warn('Paint observer not supported:', error);
    }

    // Layout Shift Observer
    try {
      const layoutShiftObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
            this.recordLayoutShift(entry as any);
          }
        }
      });
      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('layout-shift', layoutShiftObserver);
    } catch (error) {
      console.warn('Layout shift observer not supported:', error);
    }

    // Long Task Observer
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'longtask') {
            this.recordLongTask(entry as PerformanceEntry);
          }
        }
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      this.observers.set('longtask', longTaskObserver);
    } catch (error) {
      console.warn('Long task observer not supported:', error);
    }

    // Resource Observer
    try {
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'resource') {
            this.recordResourceMetric(entry as PerformanceResourceTiming);
          }
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });
      this.observers.set('resource', resourceObserver);
    } catch (error) {
      console.warn('Resource observer not supported:', error);
    }
  }

  private initializeWebVitals(): void {
    // Import web-vitals dynamically to avoid SSR issues
    if (typeof window !== 'undefined') {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(this.onWebVital.bind(this));
        getFID(this.onWebVital.bind(this));
        getFCP(this.onWebVital.bind(this));
        getLCP(this.onWebVital.bind(this));
        getTTFB(this.onWebVital.bind(this));
      }).catch(() => {
        console.warn('Web Vitals library not available');
      });
    }
  }

  private initializeNetworkMonitoring(): void {
    if (typeof window === 'undefined') return;

    // Monitor fetch requests
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      const url = typeof args[0] === 'string' ? args[0] : args[0].url;
      
      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        
        this.recordNetworkMetric({
          url,
          method: args[1]?.method || 'GET',
          status: response.status,
          duration: endTime - startTime,
          size: parseInt(response.headers.get('content-length') || '0'),
          timestamp: startTime,
          type: 'fetch',
        });
        
        return response;
      } catch (error) {
        this.recordError({
          message: `Network error: ${error}`,
          timestamp: Date.now(),
          type: 'runtime',
        });
        throw error;
      }
    };

    // Monitor XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = class extends originalXHR {
      private _startTime?: number;
      private _url?: string;
      private _method?: string;

      open(method: string, url: string, ...args: any[]) {
        this._method = method;
        this._url = url;
        this._startTime = performance.now();
        return super.open(method, url, ...args);
      }

      send(body?: any) {
        this.addEventListener('loadend', () => {
          if (this._startTime && this._url && this._method) {
            const endTime = performance.now();
            const performanceMonitor = PerformanceMonitor.getInstance();
            performanceMonitor.recordNetworkMetric({
              url: this._url,
              method: this._method,
              status: this.status,
              duration: endTime - this._startTime,
              size: parseInt(this.getResponseHeader('content-length') || '0'),
              timestamp: this._startTime,
              type: 'xhr',
            });
          }
        });
        return super.send(body);
      }
    };
  }

  private onWebVital(metric: any): void {
    this.webVitals.push(metric);
    
    // Check thresholds and warn if needed
    if (metric.name === 'LCP' && metric.value > this.thresholds.lcp) {
      console.warn(`Poor LCP detected: ${metric.value}ms (threshold: ${this.thresholds.lcp}ms)`);
    }
    
    if (metric.name === 'FID' && metric.value > this.thresholds.fid) {
      console.warn(`Poor FID detected: ${metric.value}ms (threshold: ${this.thresholds.fid}ms)`);
    }
    
    if (metric.name === 'CLS' && metric.value > this.thresholds.cls) {
      console.warn(`Poor CLS detected: ${metric.value} (threshold: ${this.thresholds.cls})`);
    }
  }

  private recordPaintMetric(entry: PerformancePaintTiming): void {
    console.debug(`Paint metric: ${entry.name} at ${entry.startTime}ms`);
  }

  private recordLayoutShift(entry: any): void {
    if (entry.value > this.thresholds.cls / 10) {
      console.warn(`Layout shift detected: ${entry.value}`);
    }
  }

  private recordLongTask(entry: PerformanceEntry): void {
    console.warn(`Long task detected: ${entry.duration}ms`);
    this.recordError({
      message: `Long task: ${entry.duration}ms`,
      timestamp: Date.now(),
      type: 'runtime',
    });
  }

  private recordResourceMetric(entry: PerformanceResourceTiming): void {
    if (entry.transferSize > this.thresholds.bundleSize) {
      console.warn(`Large resource detected: ${entry.name} (${entry.transferSize} bytes)`);
    }
  }

  public recordNetworkMetric(metric: NetworkMetric): void {
    this.networkMetrics.push(metric);
    
    // Keep only last 100 network metrics
    if (this.networkMetrics.length > 100) {
      this.networkMetrics = this.networkMetrics.slice(-100);
    }
  }

  public recordComponentMetric(name: string, metric: Partial<ComponentMetric>): void {
    const existing = this.metrics.get(name) || {
      name,
      renderTime: 0,
      mountTime: 0,
      updateCount: 0,
      lastUpdate: 0,
      errors: [],
    };

    const updated: ComponentMetric = {
      ...existing,
      ...metric,
      lastUpdate: Date.now(),
    };

    this.metrics.set(name, updated);

    // Check render time threshold
    if (updated.renderTime > this.thresholds.renderTime) {
      console.warn(`Slow component render: ${name} took ${updated.renderTime}ms`);
    }
  }

  public recordError(error: PerformanceError): void {
    this.errors.push(error);
    
    // Keep only last 50 errors
    if (this.errors.length > 50) {
      this.errors = this.errors.slice(-50);
    }
  }

  public startMeasurement(name: string): () => void {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      performance.mark(`${name}-start`);
      performance.mark(`${name}-end`);
      performance.measure(name, `${name}-start`, `${name}-end`);
      
      return duration;
    };
  }

  public measureComponent<T>(name: string, fn: () => T): T {
    const endMeasurement = this.startMeasurement(`component-${name}`);
    const startTime = performance.now();
    
    try {
      const result = fn();
      const renderTime = performance.now() - startTime;
      
      this.recordComponentMetric(name, { renderTime });
      
      return result;
    } catch (error) {
      this.recordError({
        message: `Component error in ${name}: ${error}`,
        timestamp: Date.now(),
        component: name,
        type: 'render',
      });
      throw error;
    } finally {
      endMeasurement();
    }
  }

  public async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const endMeasurement = this.startMeasurement(`async-${name}`);
    const startTime = performance.now();
    
    try {
      const result = await fn();
      const duration = performance.now() - startTime;
      
      console.debug(`Async operation ${name} completed in ${duration}ms`);
      
      return result;
    } catch (error) {
      this.recordError({
        message: `Async error in ${name}: ${error}`,
        timestamp: Date.now(),
        type: 'runtime',
      });
      throw error;
    } finally {
      endMeasurement();
    }
  }

  public getReport(): PerformanceReport {
    const memory = (performance as any).memory;
    
    return {
      timestamp: Date.now(),
      sessionId: this.sessionId,
      webVitals: [...this.webVitals],
      components: Array.from(this.metrics.values()),
      network: [...this.networkMetrics],
      bundles: [...this.bundleMetrics],
      runtime: {
        heapUsed: memory?.usedJSHeapSize || 0,
        heapTotal: memory?.totalJSHeapSize || 0,
        heapLimit: memory?.jsHeapSizeLimit || 0,
      },
      device: {
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        connection: (navigator as any).connection ? {
          effectiveType: (navigator as any).connection.effectiveType,
          downlink: (navigator as any).connection.downlink,
          rtt: (navigator as any).connection.rtt,
        } : undefined,
      },
    };
  }

  public clearMetrics(): void {
    this.metrics.clear();
    this.webVitals.length = 0;
    this.networkMetrics.length = 0;
    this.bundleMetrics.length = 0;
    this.errors.length = 0;
  }

  public destroy(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.clearMetrics();
  }

  private startReporting(interval: number): void {
    setInterval(() => {
      if (this.isEnabled) {
        const report = this.getReport();
        this.sendReport(report);
      }
    }, interval);
  }

  private sendReport(report: PerformanceReport): void {
    // Send to analytics service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'performance_metrics', {
        custom_parameter: {
          session_id: report.sessionId,
          lcp: report.webVitals.find(m => m.name === 'LCP')?.value,
          fid: report.webVitals.find(m => m.name === 'FID')?.value,
          cls: report.webVitals.find(m => m.name === 'CLS')?.value,
          components_count: report.components.length,
          errors_count: this.errors.length,
        },
      });
    }

    // Send to monitoring service
    fetch('/api/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(report),
    }).catch(() => {
      // Silently fail if monitoring endpoint is not available
    });
  }

  // Singleton pattern
  private static instance: PerformanceMonitor;
  
  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }
}

// React Hook for Performance Monitoring
export const usePerformanceMonitor = () => {
  const monitor = PerformanceMonitor.getInstance();
  
  return {
    measureComponent: monitor.measureComponent.bind(monitor),
    measureAsync: monitor.measureAsync.bind(monitor),
    startMeasurement: monitor.startMeasurement.bind(monitor),
    recordComponentMetric: monitor.recordComponentMetric.bind(monitor),
    recordError: monitor.recordError.bind(monitor),
    getReport: monitor.getReport.bind(monitor),
  };
};

// Performance Decorator for React Components
export const withPerformanceMonitoring = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
) => {
  const displayName = componentName || WrappedComponent.displayName || WrappedComponent.name || 'Component';
  
  const PerformanceWrappedComponent: React.FC<P> = (props) => {
    const monitor = PerformanceMonitor.getInstance();
    
    React.useEffect(() => {
      const mountTime = Date.now();
      monitor.recordComponentMetric(displayName, { mountTime });
      
      return () => {
        // Component unmount
      };
    }, []);
    
    return React.useMemo(() => {
      return monitor.measureComponent(displayName, () => 
        React.createElement(WrappedComponent, props)
      );
    }, [props]);
  };
  
  PerformanceWrappedComponent.displayName = `withPerformanceMonitoring(${displayName})`;
  
  return PerformanceWrappedComponent;
};

export default PerformanceMonitor;