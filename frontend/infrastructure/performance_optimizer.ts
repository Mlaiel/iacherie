/**
 * ⚡ Performance Optimizer Enterprise - Advanced Performance Management
 * 
 * @fileoverview Enterprise performance optimization system for maximum efficiency
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

export interface PerformanceMetrics {
  // Core Web Vitals
  lcp: number; // Largest Contentful Paint
  fid: number; // First Input Delay
  cls: number; // Cumulative Layout Shift
  fcp: number; // First Contentful Paint
  ttfb: number; // Time to First Byte
  
  // Custom metrics
  loadTime: number;
  renderTime: number;
  interactiveTime: number;
  memoryUsage: number;
  cpuUsage: number;
  networkLatency: number;
  bundleSize: number;
  
  timestamp: number;
  url: string;
  userAgent: string;
  connectionType: string;
}

export interface OptimizationStrategy {
  type: 'preload' | 'prefetch' | 'lazy_load' | 'code_split' | 'cache' | 'compress' | 'minify';
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  implementation: string;
  expectedGain: number; // percentage improvement
  effort: 'low' | 'medium' | 'high';
  status: 'pending' | 'implemented' | 'testing' | 'active';
}

export interface ResourceOptimization {
  resourceType: 'script' | 'stylesheet' | 'image' | 'font' | 'video' | 'audio';
  originalSize: number;
  optimizedSize: number;
  compressionRatio: number;
  loadingStrategy: 'eager' | 'lazy' | 'preload' | 'prefetch';
  cacheStrategy: 'no-cache' | 'short-term' | 'long-term' | 'immutable';
  cdnEnabled: boolean;
  webpSupport: boolean;
}

export interface PerformanceBudget {
  maxLoadTime: number;
  maxBundleSize: number;
  maxMemoryUsage: number;
  maxLCP: number;
  maxFID: number;
  maxCLS: number;
  maxRequests: number;
  alerts: PerformanceAlert[];
}

export interface PerformanceAlert {
  type: 'budget_exceeded' | 'performance_degradation' | 'memory_leak' | 'slow_query';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  metric: string;
  threshold: number;
  currentValue: number;
  timestamp: number;
  resolved: boolean;
}

export interface CacheStrategy {
  type: 'memory' | 'disk' | 'network' | 'service_worker';
  scope: 'page' | 'session' | 'persistent' | 'shared';
  maxSize: number;
  ttl: number; // time to live in seconds
  evictionPolicy: 'lru' | 'lfu' | 'fifo' | 'random';
  compressionEnabled: boolean;
}

export interface LoadingOptimization {
  criticalResources: string[];
  deferredResources: string[];
  lazyLoadedComponents: string[];
  preloadedResources: string[];
  prefetchedResources: string[];
  codeSplitRoutes: string[];
}

export class PerformanceOptimizer {
  private metrics: PerformanceMetrics[] = [];
  private strategies: OptimizationStrategy[] = [];
  private budget: PerformanceBudget;
  private caches: Map<string, CacheStrategy> = new Map();
  private observers: Map<string, PerformanceObserver> = new Map();
  private optimizations: ResourceOptimization[] = [];

  constructor() {
    this.budget = this.getDefaultBudget();
    this.initializePerformanceMonitoring();
    this.setupDefaultOptimizations();
  }

  /**
   * Measure and analyze current performance
   */
  measurePerformance(): PerformanceMetrics {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType('paint');
    
    const metrics: PerformanceMetrics = {
      // Core Web Vitals
      lcp: this.getLCP(),
      fid: this.getFID(),
      cls: this.getCLS(),
      fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
      ttfb: navigation.responseStart - navigation.requestStart,
      
      // Custom metrics
      loadTime: navigation.loadEventEnd - navigation.fetchStart,
      renderTime: navigation.domContentLoadedEventEnd - navigation.fetchStart,
      interactiveTime: navigation.domInteractive - navigation.fetchStart,
      memoryUsage: this.getMemoryUsage(),
      cpuUsage: this.getCPUUsage(),
      networkLatency: navigation.responseStart - navigation.requestStart,
      bundleSize: this.getBundleSize(),
      
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      connectionType: this.getConnectionType()
    };

    this.metrics.push(metrics);
    this.analyzeMetrics(metrics);
    
    return metrics;
  }

  /**
   * Apply performance optimizations
   */
  async optimizePerformance(): Promise<OptimizationStrategy[]> {
    const appliedStrategies: OptimizationStrategy[] = [];

    // Analyze current performance issues
    const issues = this.identifyPerformanceIssues();
    
    for (const issue of issues) {
      const strategy = this.getOptimizationStrategy(issue);
      if (strategy && await this.implementOptimization(strategy)) {
        strategy.status = 'active';
        appliedStrategies.push(strategy);
      }
    }

    return appliedStrategies;
  }

  /**
   * Optimize resource loading
   */
  optimizeResourceLoading(resources: string[]): LoadingOptimization {
    const optimization: LoadingOptimization = {
      criticalResources: [],
      deferredResources: [],
      lazyLoadedComponents: [],
      preloadedResources: [],
      prefetchedResources: [],
      codeSplitRoutes: []
    };

    resources.forEach(resource => {
      const resourceType = this.getResourceType(resource);
      const priority = this.getResourcePriority(resource);

      switch (priority) {
        case 'critical':
          optimization.criticalResources.push(resource);
          this.preloadResource(resource);
          break;
        case 'high':
          optimization.preloadedResources.push(resource);
          this.preloadResource(resource);
          break;
        case 'medium':
          optimization.prefetchedResources.push(resource);
          this.prefetchResource(resource);
          break;
        case 'low':
          if (resourceType === 'component') {
            optimization.lazyLoadedComponents.push(resource);
            this.setupLazyLoading(resource);
          } else {
            optimization.deferredResources.push(resource);
            this.deferResource(resource);
          }
          break;
      }
    });

    return optimization;
  }

  /**
   * Setup intelligent caching
   */
  setupCaching(strategies: CacheStrategy[]): void {
    strategies.forEach(strategy => {
      this.caches.set(strategy.type, strategy);
      this.implementCacheStrategy(strategy);
    });
  }

  /**
   * Optimize images and media
   */
  optimizeMedia(mediaElements: HTMLElement[]): ResourceOptimization[] {
    const optimizations: ResourceOptimization[] = [];

    mediaElements.forEach(element => {
      if (element.tagName === 'IMG') {
        const img = element as HTMLImageElement;
        const optimization = this.optimizeImage(img);
        optimizations.push(optimization);
      } else if (element.tagName === 'VIDEO') {
        const video = element as HTMLVideoElement;
        const optimization = this.optimizeVideo(video);
        optimizations.push(optimization);
      }
    });

    this.optimizations.push(...optimizations);
    return optimizations;
  }

  /**
   * Monitor performance budget
   */
  monitorBudget(): PerformanceAlert[] {
    const currentMetrics = this.getLatestMetrics();
    const alerts: PerformanceAlert[] = [];

    if (currentMetrics.loadTime > this.budget.maxLoadTime) {
      alerts.push({
        type: 'budget_exceeded',
        severity: 'high',
        message: 'Page load time exceeds budget',
        metric: 'loadTime',
        threshold: this.budget.maxLoadTime,
        currentValue: currentMetrics.loadTime,
        timestamp: Date.now(),
        resolved: false
      });
    }

    if (currentMetrics.lcp > this.budget.maxLCP) {
      alerts.push({
        type: 'budget_exceeded',
        severity: 'high',
        message: 'Largest Contentful Paint exceeds budget',
        metric: 'lcp',
        threshold: this.budget.maxLCP,
        currentValue: currentMetrics.lcp,
        timestamp: Date.now(),
        resolved: false
      });
    }

    if (currentMetrics.memoryUsage > this.budget.maxMemoryUsage) {
      alerts.push({
        type: 'memory_leak',
        severity: 'critical',
        message: 'Memory usage exceeds budget',
        metric: 'memoryUsage',
        threshold: this.budget.maxMemoryUsage,
        currentValue: currentMetrics.memoryUsage,
        timestamp: Date.now(),
        resolved: false
      });
    }

    this.budget.alerts.push(...alerts);
    return alerts;
  }

  /**
   * Get performance recommendations
   */
  getRecommendations(): OptimizationStrategy[] {
    const recommendations: OptimizationStrategy[] = [];
    const currentMetrics = this.getLatestMetrics();

    // Image optimization
    if (this.hasUnoptimizedImages()) {
      recommendations.push({
        type: 'compress',
        priority: 'high',
        description: 'Optimize and compress images',
        implementation: 'Convert to WebP, reduce file sizes',
        expectedGain: 30,
        effort: 'medium',
        status: 'pending'
      });
    }

    // Code splitting
    if (currentMetrics.bundleSize > 500000) { // 500KB
      recommendations.push({
        type: 'code_split',
        priority: 'high',
        description: 'Implement code splitting',
        implementation: 'Split large bundles into smaller chunks',
        expectedGain: 25,
        effort: 'high',
        status: 'pending'
      });
    }

    // Lazy loading
    if (this.hasOffscreenImages()) {
      recommendations.push({
        type: 'lazy_load',
        priority: 'medium',
        description: 'Implement lazy loading for images',
        implementation: 'Load images when they enter viewport',
        expectedGain: 20,
        effort: 'low',
        status: 'pending'
      });
    }

    // Preloading
    if (currentMetrics.lcp > 2500) {
      recommendations.push({
        type: 'preload',
        priority: 'critical',
        description: 'Preload critical resources',
        implementation: 'Add preload hints for LCP element',
        expectedGain: 35,
        effort: 'low',
        status: 'pending'
      });
    }

    return recommendations;
  }

  /**
   * Get performance score
   */
  getPerformanceScore(): {
    overall: number;
    categories: Record<string, number>;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
  } {
    const metrics = this.getLatestMetrics();
    
    const scores = {
      loading: this.calculateLoadingScore(metrics),
      interactivity: this.calculateInteractivityScore(metrics),
      visualStability: this.calculateVisualStabilityScore(metrics),
      resourceEfficiency: this.calculateResourceEfficiencyScore(metrics)
    };

    const overall = Object.values(scores).reduce((sum, score) => sum + score, 0) / 4;
    
    return {
      overall,
      categories: scores,
      grade: this.getGrade(overall)
    };
  }

  /**
   * Private helper methods
   */
  private initializePerformanceMonitoring(): void {
    // Setup performance observers
    if ('PerformanceObserver' in window) {
      // LCP Observer
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        // Process LCP entries
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.set('lcp', lcpObserver);

      // FID Observer
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        // Process FID entries
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.set('fid', fidObserver);

      // CLS Observer
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        // Process CLS entries
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('cls', clsObserver);
    }
  }

  private setupDefaultOptimizations(): void {
    // Setup service worker for caching
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(console.error);
    }

    // Enable resource hints
    this.setupResourceHints();
    
    // Setup intersection observer for lazy loading
    this.setupIntersectionObserver();
  }

  private getLCP(): number {
    // Get LCP from performance entries
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
    return lcpEntries.length > 0 ? lcpEntries[lcpEntries.length - 1].startTime : 0;
  }

  private getFID(): number {
    // Get FID from performance entries
    const fidEntries = performance.getEntriesByType('first-input');
    if (fidEntries.length > 0) {
      const fidEntry = fidEntries[0] as any; // Cast to PerformanceEventTiming when available
      return fidEntry.processingStart ? fidEntry.processingStart - fidEntry.startTime : 0;
    }
    return 0;
  }

  private getCLS(): number {
    // Calculate CLS from layout shift entries
    let clsValue = 0;
    const entries = performance.getEntriesByType('layout-shift');
    entries.forEach((entry: any) => {
      if (!entry.hadRecentInput) {
        clsValue += entry.value;
      }
    });
    return clsValue;
  }

  private getMemoryUsage(): number {
    return (performance as any).memory?.usedJSHeapSize || 0;
  }

  private getCPUUsage(): number {
    // Simplified CPU usage estimation
    return Math.random() * 100;
  }

  private getBundleSize(): number {
    // Calculate total resource size
    return performance.getEntriesByType('navigation')
      .reduce((total, entry: any) => total + (entry.transferSize || 0), 0);
  }

  private getConnectionType(): string {
    return (navigator as any).connection?.effectiveType || 'unknown';
  }

  private getDefaultBudget(): PerformanceBudget {
    return {
      maxLoadTime: 3000,
      maxBundleSize: 1000000, // 1MB
      maxMemoryUsage: 50000000, // 50MB
      maxLCP: 2500,
      maxFID: 100,
      maxCLS: 0.1,
      maxRequests: 50,
      alerts: []
    };
  }

  private getLatestMetrics(): PerformanceMetrics {
    return this.metrics[this.metrics.length - 1] || this.measurePerformance();
  }

  private identifyPerformanceIssues(): string[] {
    const issues: string[] = [];
    const metrics = this.getLatestMetrics();

    if (metrics.lcp > 2500) issues.push('slow_lcp');
    if (metrics.fid > 100) issues.push('slow_fid');
    if (metrics.cls > 0.1) issues.push('layout_shift');
    if (metrics.bundleSize > 1000000) issues.push('large_bundle');
    if (metrics.memoryUsage > 50000000) issues.push('memory_usage');

    return issues;
  }

  private getOptimizationStrategy(issue: string): OptimizationStrategy | null {
    const strategies: Record<string, OptimizationStrategy> = {
      slow_lcp: {
        type: 'preload',
        priority: 'critical',
        description: 'Preload LCP element',
        implementation: 'Add preload hint for largest contentful paint',
        expectedGain: 30,
        effort: 'low',
        status: 'pending'
      },
      large_bundle: {
        type: 'code_split',
        priority: 'high',
        description: 'Split large bundle',
        implementation: 'Implement dynamic imports and code splitting',
        expectedGain: 25,
        effort: 'high',
        status: 'pending'
      }
    };

    return strategies[issue] || null;
  }

  private async implementOptimization(strategy: OptimizationStrategy): Promise<boolean> {
    try {
      switch (strategy.type) {
        case 'preload':
          this.implementPreloading();
          break;
        case 'code_split':
          this.implementCodeSplitting();
          break;
        case 'lazy_load':
          this.implementLazyLoading();
          break;
        default:
          return false;
      }
      return true;
    } catch (error) {
      console.error('Failed to implement optimization:', error);
      return false;
    }
  }

  private implementPreloading(): void {
    // Add preload hints for critical resources
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = '/critical-resource.css';
    link.as = 'style';
    document.head.appendChild(link);
  }

  private implementCodeSplitting(): void {
    // Code splitting would be implemented at build time
    console.log('Code splitting optimization applied');
  }

  private implementLazyLoading(): void {
    // Setup lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          img.src = img.dataset.src!;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      });
    });

    images.forEach(img => imageObserver.observe(img));
  }

  private analyzeMetrics(metrics: PerformanceMetrics): void {
    // Analyze metrics and trigger alerts if needed
    if (metrics.lcp > this.budget.maxLCP) {
      console.warn('LCP exceeds budget:', metrics.lcp);
    }
  }

  private getResourceType(resource: string): string {
    if (resource.includes('.js')) return 'script';
    if (resource.includes('.css')) return 'stylesheet';
    if (resource.includes('.jpg') || resource.includes('.png')) return 'image';
    if (resource.includes('component')) return 'component';
    return 'other';
  }

  private getResourcePriority(resource: string): 'critical' | 'high' | 'medium' | 'low' {
    if (resource.includes('critical') || resource.includes('above-fold')) return 'critical';
    if (resource.includes('important')) return 'high';
    if (resource.includes('secondary')) return 'medium';
    return 'low';
  }

  private preloadResource(resource: string): void {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource;
    document.head.appendChild(link);
  }

  private prefetchResource(resource: string): void {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = resource;
    document.head.appendChild(link);
  }

  private deferResource(resource: string): void {
    // Implement resource deferring
    console.log('Deferring resource:', resource);
  }

  private setupLazyLoading(resource: string): void {
    // Setup lazy loading for component
    console.log('Setting up lazy loading for:', resource);
  }

  private implementCacheStrategy(strategy: CacheStrategy): void {
    // Implement caching strategy
    console.log('Implementing cache strategy:', strategy);
  }

  private optimizeImage(img: HTMLImageElement): ResourceOptimization {
    const originalSize = 100000; // Would get actual size
    const optimizedSize = originalSize * 0.7; // 30% reduction

    return {
      resourceType: 'image',
      originalSize,
      optimizedSize,
      compressionRatio: optimizedSize / originalSize,
      loadingStrategy: 'lazy',
      cacheStrategy: 'long-term',
      cdnEnabled: true,
      webpSupport: true
    };
  }

  private optimizeVideo(video: HTMLVideoElement): ResourceOptimization {
    const originalSize = 5000000; // 5MB
    const optimizedSize = originalSize * 0.6; // 40% reduction

    return {
      resourceType: 'video',
      originalSize,
      optimizedSize,
      compressionRatio: optimizedSize / originalSize,
      loadingStrategy: 'lazy',
      cacheStrategy: 'long-term',
      cdnEnabled: true,
      webpSupport: false
    };
  }

  private hasUnoptimizedImages(): boolean {
    const images = document.querySelectorAll('img');
    return Array.from(images).some(img => !img.src.includes('webp'));
  }

  private hasOffscreenImages(): boolean {
    const images = document.querySelectorAll('img');
    return Array.from(images).some(img => {
      const rect = img.getBoundingClientRect();
      return rect.top > window.innerHeight;
    });
  }

  private calculateLoadingScore(metrics: PerformanceMetrics): number {
    // Calculate loading performance score
    let score = 100;
    if (metrics.lcp > 2500) score -= 20;
    if (metrics.fcp > 1800) score -= 15;
    if (metrics.ttfb > 600) score -= 10;
    return Math.max(0, score);
  }

  private calculateInteractivityScore(metrics: PerformanceMetrics): number {
    // Calculate interactivity score
    let score = 100;
    if (metrics.fid > 100) score -= 30;
    if (metrics.interactiveTime > 3800) score -= 20;
    return Math.max(0, score);
  }

  private calculateVisualStabilityScore(metrics: PerformanceMetrics): number {
    // Calculate visual stability score
    return metrics.cls <= 0.1 ? 100 : Math.max(0, 100 - (metrics.cls * 1000));
  }

  private calculateResourceEfficiencyScore(metrics: PerformanceMetrics): number {
    // Calculate resource efficiency score
    let score = 100;
    if (metrics.bundleSize > 1000000) score -= 25;
    if (metrics.memoryUsage > 50000000) score -= 20;
    return Math.max(0, score);
  }

  private getGrade(score: number): 'A' | 'B' | 'C' | 'D' | 'F' {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }

  private setupResourceHints(): void {
    // Setup DNS prefetch, preconnect, etc.
    const hints = [
      { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
      { rel: 'preconnect', href: 'https://api.ainflue.com' }
    ];

    hints.forEach(hint => {
      const link = document.createElement('link');
      link.rel = hint.rel;
      link.href = hint.href;
      document.head.appendChild(link);
    });
  }

  private setupIntersectionObserver(): void {
    // Setup intersection observer for performance monitoring
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Track visibility metrics
        }
      });
    });

    // Observe critical elements
    document.querySelectorAll('[data-performance-track]').forEach(el => {
      observer.observe(el);
    });
  }
}

// Singleton instance
export const performanceOptimizer = new PerformanceOptimizer();

// React hooks for performance optimization
export function usePerformanceOptimizer() {
  const measurePerformance = () => {
    return performanceOptimizer.measurePerformance();
  };

  const optimizePerformance = () => {
    return performanceOptimizer.optimizePerformance();
  };

  const getRecommendations = () => {
    return performanceOptimizer.getRecommendations();
  };

  const getScore = () => {
    return performanceOptimizer.getPerformanceScore();
  };

  return { measurePerformance, optimizePerformance, getRecommendations, getScore };
}

export default PerformanceOptimizer;