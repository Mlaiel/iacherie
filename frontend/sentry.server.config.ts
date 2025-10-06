/**
 * Sentry Server Configuration
 * @module sentry.server.config
 */

import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV || 'development',
  release: process.env.NEXT_PUBLIC_APP_VERSION,
});
