/**
 * 📊 Monitoring System Enterprise - Performance & Health Monitoring
 * 
 * @fileoverview Advanced monitoring system for enterprise performance tracking
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

export interface PerformanceMetrics {
  cpuUsage: number;
  memoryUsage: number;
  networkLatency: number;
  responseTime: number;
  throughput: number;
  errorRate: number;
  uptime: number;
}

export interface ErrorTracking {
  errorId: string;
  type: 'javascript' | 'network' | 'api' | 'ui' | 'security';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  stack?: string;
  timestamp: number;
  userId?: string;
  sessionId: string;
  userAgent: string;
  url: string;
  metadata: Record<string, any>;
}

export interface AnalyticsEvent {
  eventId: string;
  type: string;
  category: string;
  action: string;
  label?: string;
  value?: number;
  timestamp: number;
  userId?: string;
  sessionId: string;
  properties: Record<string, any>;
}

export interface RealtimeMetrics {
  activeUsers: number;
  pageViews: number;
  apiCalls: number;
  errors: number;
  conversions: number;
  revenue: number;
  timestamp: number;
}

export class MonitoringSystem {
  private metrics: PerformanceMetrics[] = [];
  private errors: ErrorTracking[] = [];
  private events: AnalyticsEvent[] = [];
  private realtimeData: RealtimeMetrics | null = null;

  /**
   * Track performance metrics
   */
  trackPerformance(metrics: Partial<PerformanceMetrics>): void {
    const fullMetrics: PerformanceMetrics = {
      cpuUsage: metrics.cpuUsage || 0,
      memoryUsage: metrics.memoryUsage || 0,
      networkLatency: metrics.networkLatency || 0,
      responseTime: metrics.responseTime || 0,
      throughput: metrics.throughput || 0,
      errorRate: metrics.errorRate || 0,
      uptime: metrics.uptime || 100
    };

    this.metrics.push(fullMetrics);
    this.sendToAnalytics('performance', fullMetrics);
  }

  /**
   * Track errors with detailed context
   */
  trackError(error: Partial<ErrorTracking>): void {
    const errorEvent: ErrorTracking = {
      errorId: error.errorId || this.generateId(),
      type: error.type || 'javascript',
      severity: error.severity || 'medium',
      message: error.message || 'Unknown error',
      stack: error.stack,
      timestamp: error.timestamp || Date.now(),
      userId: error.userId,
      sessionId: error.sessionId || this.getSessionId(),
      userAgent: error.userAgent || navigator.userAgent,
      url: error.url || window.location.href,
      metadata: error.metadata || {}
    };

    this.errors.push(errorEvent);
    this.sendToAnalytics('error', errorEvent);
    
    // Auto-escalate critical errors
    if (errorEvent.severity === 'critical') {
      this.escalateError(errorEvent);
    }
  }

  /**
   * Track analytics events
   */
  trackEvent(event: Partial<AnalyticsEvent>): void {
    const analyticsEvent: AnalyticsEvent = {
      eventId: event.eventId || this.generateId(),
      type: event.type || 'interaction',
      category: event.category || 'general',
      action: event.action || 'click',
      label: event.label,
      value: event.value,
      timestamp: event.timestamp || Date.now(),
      userId: event.userId,
      sessionId: event.sessionId || this.getSessionId(),
      properties: event.properties || {}
    };

    this.events.push(analyticsEvent);
    this.sendToAnalytics('event', analyticsEvent);
  }

  /**
   * Update realtime metrics
   */
  updateRealtimeMetrics(metrics: Partial<RealtimeMetrics>): void {
    this.realtimeData = {
      activeUsers: metrics.activeUsers || 0,
      pageViews: metrics.pageViews || 0,
      apiCalls: metrics.apiCalls || 0,
      errors: metrics.errors || 0,
      conversions: metrics.conversions || 0,
      revenue: metrics.revenue || 0,
      timestamp: Date.now()
    };

    this.broadcastRealtimeData();
  }

  /**
   * Get performance summary
   */
  getPerformanceSummary(): {
    average: PerformanceMetrics;
    trend: 'improving' | 'stable' | 'declining';
    alerts: string[];
  } {
    if (this.metrics.length === 0) {
      return {
        average: { cpuUsage: 0, memoryUsage: 0, networkLatency: 0, responseTime: 0, throughput: 0, errorRate: 0, uptime: 100 },
        trend: 'stable',
        alerts: []
      };
    }

    const recent = this.metrics.slice(-10);
    const average: PerformanceMetrics = {
      cpuUsage: recent.reduce((sum, m) => sum + m.cpuUsage, 0) / recent.length,
      memoryUsage: recent.reduce((sum, m) => sum + m.memoryUsage, 0) / recent.length,
      networkLatency: recent.reduce((sum, m) => sum + m.networkLatency, 0) / recent.length,
      responseTime: recent.reduce((sum, m) => sum + m.responseTime, 0) / recent.length,
      throughput: recent.reduce((sum, m) => sum + m.throughput, 0) / recent.length,
      errorRate: recent.reduce((sum, m) => sum + m.errorRate, 0) / recent.length,
      uptime: recent.reduce((sum, m) => sum + m.uptime, 0) / recent.length
    };

    const alerts: string[] = [];
    if (average.cpuUsage > 80) alerts.push('High CPU usage detected');
    if (average.memoryUsage > 85) alerts.push('High memory usage detected');
    if (average.errorRate > 5) alerts.push('High error rate detected');
    if (average.responseTime > 2000) alerts.push('Slow response times detected');

    return { average, trend: 'stable', alerts };
  }

  /**
   * Send data to analytics service
   */
  private sendToAnalytics(type: string, data: any): void {
    // Implementation would send to actual analytics service
    console.log(`[Monitoring] ${type}:`, data);
  }

  /**
   * Escalate critical errors
   */
  private escalateError(error: ErrorTracking): void {
    // Implementation would notify operations team
    console.error(`[CRITICAL ERROR] ${error.message}`, error);
  }

  /**
   * Broadcast realtime data via WebSocket
   */
  private broadcastRealtimeData(): void {
    if (this.realtimeData) {
      // Implementation would broadcast via WebSocket
      console.log('[Realtime] Broadcasting metrics:', this.realtimeData);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get current session ID
   */
  private getSessionId(): string {
    return sessionStorage.getItem('sessionId') || this.generateId();
  }
}

// Singleton instance
export const monitoringSystem = new MonitoringSystem();

// React hooks for monitoring
export function usePerformanceMonitoring() {
  const trackPerformance = (metrics: Partial<PerformanceMetrics>) => {
    monitoringSystem.trackPerformance(metrics);
  };

  const trackError = (error: Partial<ErrorTracking>) => {
    monitoringSystem.trackError(error);
  };

  const trackEvent = (event: Partial<AnalyticsEvent>) => {
    monitoringSystem.trackEvent(event);
  };

  return { trackPerformance, trackError, trackEvent };
}

export default MonitoringSystem;