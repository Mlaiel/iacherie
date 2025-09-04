/**
 * Application Constants
 */

export const APP_CONFIG = {
  NAME: 'Ainflue',
  VERSION: '1.0.0',
  DESCRIPTION: 'AI-powered Content Protection & Monetization Platform',
  AUTHOR: 'Fahed Mlaiel',
  EMAIL: 'mlaiel@live.de',
} as const;

export const API_ENDPOINTS = {
  AUTH: '/api/auth',
  USERS: '/api/users',
  CONTENT: '/api/content',
  ANALYTICS: '/api/analytics',
  PROTECTION: '/api/protection',
  UPLOAD: '/api/upload',
} as const;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

export const MEDIA_TYPES = {
  IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
  VIDEO: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
  AUDIO: ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'],
  DOCUMENT: ['pdf', 'doc', 'docx', 'txt', 'rtf'],
} as const;

export const FILE_SIZE_LIMITS = {
  IMAGE: 10 * 1024 * 1024, // 10MB
  VIDEO: 100 * 1024 * 1024, // 100MB
  AUDIO: 50 * 1024 * 1024, // 50MB
  DOCUMENT: 25 * 1024 * 1024, // 25MB
} as const;

export const ANIMATION_DURATIONS = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
} as const;

export const BREAKPOINTS = {
  XS: 0,
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536,
} as const;

export const KEYBOARD_CODES = {
  ENTER: 'Enter',
  ESCAPE: 'Escape',
  SPACE: ' ',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
} as const;

export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
} as const;

export const PROTECTION_LEVELS = {
  BASIC: 'basic',
  ADVANCED: 'advanced',
  ENTERPRISE: 'enterprise',
} as const;

export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
  MODERATOR: 'moderator',
} as const;

export const SUBSCRIPTION_PLANS = {
  FREE: 'free',
  PRO: 'pro',
  ENTERPRISE: 'enterprise',
} as const;
