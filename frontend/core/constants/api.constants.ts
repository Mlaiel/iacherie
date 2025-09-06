/**
 * @fileoverview API constants
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

// HTTP status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
} as const;

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
    PROFILE: '/auth/profile',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  
  CONTENT: {
    LIST: '/content',
    UPLOAD: '/content/upload',
    PROCESS: '/content/process',
    METADATA: '/content/:id/metadata',
    DOWNLOAD: '/content/:id/download',
    DELETE: '/content/:id',
  },
  
  PROTECTION: {
    FINGERPRINT: '/protection/fingerprint',
    COPYRIGHT: '/protection/copyright',
    DETECT_INFRINGEMENT: '/protection/detect',
    REPORT_VIOLATION: '/protection/report',
  },
  
  MONETIZATION: {
    REVENUE_STREAMS: '/monetization/revenue',
    MARKETPLACE: '/monetization/marketplace',
    PRODUCTS: '/monetization/products',
    ANALYTICS: '/monetization/analytics',
    PAYOUTS: '/monetization/payouts',
  },
  
  COLLABORATION: {
    PROJECTS: '/collaboration/projects',
    MATCHING: '/collaboration/matching',
    INVITATIONS: '/collaboration/invitations',
    MESSAGES: '/collaboration/messages',
  },
  
  ANALYTICS: {
    OVERVIEW: '/analytics/overview',
    CONTENT_PERFORMANCE: '/analytics/content',
    USER_ENGAGEMENT: '/analytics/engagement',
    REVENUE_METRICS: '/analytics/revenue',
  },
} as const;

// Request configuration
export const REQUEST_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
  MAX_RETRY_DELAY: 5000, // 5 seconds
  
  HEADERS: {
    DEFAULT: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    MULTIPART: {
      'Content-Type': 'multipart/form-data',
    },
  },
} as const;