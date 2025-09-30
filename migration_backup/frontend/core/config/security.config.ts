/**
 * @fileoverview Security configuration settings
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

export const SECURITY_CONFIG = {
  // Authentication settings
  auth: {
    tokenExpiry: 3600000, // 1 hour in milliseconds
    refreshTokenExpiry: 86400000, // 24 hours in milliseconds
    maxLoginAttempts: 5,
    lockoutDuration: 900000, // 15 minutes in milliseconds
  },
  
  // Session settings
  session: {
    name: 'ainflue-session',
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict' as const,
  },
  
  // Encryption settings
  encryption: {
    algorithm: 'AES-256-GCM',
    keyDerivation: 'PBKDF2',
    iterations: 100000,
  },
  
  // Content Security Policy
  csp: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", 'data:', 'https:'],
    'connect-src': ["'self'", process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'],
  },
} as const;