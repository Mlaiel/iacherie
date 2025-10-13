/**
 * Sentry Configuration - Production Grade
 * Error tracking and performance monitoring
 * @module sentry.client.config
 */

import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN || 'https://e4d3be4623ada1b28cad9035f3b0cdd5@o4510074853457920.ingest.de.sentry.io/4510074859094096',
  
  // Performance monitoring
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  
  // Session replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Release tracking
  release: process.env.NEXT_PUBLIC_APP_VERSION,
  
  // Ignore common errors
  ignoreErrors: [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    'cancelled',
  ],
  
  // Filter breadcrumbs
  beforeBreadcrumb(breadcrumb) {
    if (breadcrumb.category === 'console') {
      return null;
    }
    return breadcrumb;
  },
  
  // Enhanced error context
  beforeSend(event, hint) {
    // Add custom context
    event.contexts = {
      ...event.contexts,
      app: {
        name: 'IA Chérie Frontend',
        version: process.env.NEXT_PUBLIC_APP_VERSION,
      },
    };
    
    return event;
  },
});
