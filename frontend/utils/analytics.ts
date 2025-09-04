/**
 * Analytics Utilities
 */

interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  timestamp?: number;
}

interface PageView {
  path: string;
  title?: string;
  referrer?: string;
  timestamp?: number;
}

class AnalyticsTracker {
  private events: AnalyticsEvent[] = [];
  private pageViews: PageView[] = [];
  private sessionId: string;
  private userId?: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.trackPageView();
    this.setupAutoTracking();
  }

  setUserId(userId: string): void {
    this.userId = userId;
  }

  trackEvent(name: string, properties?: Record<string, any>): void {
    const event: AnalyticsEvent = {
      name,
      properties: {
        ...properties,
        sessionId: this.sessionId,
        userId: this.userId,
        url: window.location.href,
        userAgent: navigator.userAgent,
      },
      timestamp: Date.now(),
    };

    this.events.push(event);
    this.sendEvent(event);
  }

  trackPageView(path?: string, title?: string): void {
    const pageView: PageView = {
      path: path || window.location.pathname,
      title: title || document.title,
      referrer: document.referrer,
      timestamp: Date.now(),
    };

    this.pageViews.push(pageView);
    this.sendPageView(pageView);
  }

  trackError(error: Error, context?: Record<string, any>): void {
    this.trackEvent('error', {
      message: error.message,
      stack: error.stack,
      name: error.name,
      ...context,
    });
  }

  trackTiming(name: string, startTime: number, endTime?: number): void {
    const duration = (endTime || Date.now()) - startTime;
    this.trackEvent('timing', {
      name,
      duration,
      startTime,
      endTime: endTime || Date.now(),
    });
  }

  getEvents(): AnalyticsEvent[] {
    return [...this.events];
  }

  getPageViews(): PageView[] {
    return [...this.pageViews];
  }

  clearData(): void {
    this.events = [];
    this.pageViews = [];
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private setupAutoTracking(): void {
    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.trackEvent('page_visibility_change', {
        hidden: document.hidden,
      });
    });

    // Track clicks on external links
    document.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.hostname !== window.location.hostname) {
        this.trackEvent('external_link_click', {
          url: link.href,
          text: link.textContent?.trim(),
        });
      }
    });

    // Track unload
    window.addEventListener('beforeunload', () => {
      this.trackEvent('page_unload');
    });
  }

  private sendEvent(event: AnalyticsEvent): void {
    // In a real implementation, this would send to your analytics service
    console.log('Analytics Event:', event);
  }

  private sendPageView(pageView: PageView): void {
    // In a real implementation, this would send to your analytics service
    console.log('Page View:', pageView);
  }
}

// Global analytics instance
const analytics = new AnalyticsTracker();

export { AnalyticsTracker, analytics };
export type { AnalyticsEvent, PageView };
