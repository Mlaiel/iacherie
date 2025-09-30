/**
 * @fileoverview API configuration settings
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  version: 'v1',
  timeout: 30000,
  
  endpoints: {
    auth: '/auth',
    content: '/content',
    protection: '/protection',
    monetization: '/monetization',
    collaboration: '/collaboration',
    analytics: '/analytics',
    distribution: '/distribution',
  },
  
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Client-Version': '2.0.0',
  },
  
  retryConfig: {
    attempts: 3,
    delay: 1000,
  },
} as const;