/**
 * Mobile Services Constants - Professional Service Configuration Constants
 * 
 * Centralized configuration constants for all mobile services including
 * endpoints, storage keys, intervals, and quality presets for professional
 * content creation and cross-platform operations.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

// API Service Endpoints
export const SERVICE_ENDPOINTS = {
  // Authentication and User Management
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
    VERIFY: '/auth/verify',
    BIOMETRIC: '/auth/biometric',
    RESET_PASSWORD: '/auth/reset-password'
  },

  // Content Management
  CONTENT: {
    UPLOAD: '/content/upload',
    LIST: '/content/list',
    DETAILS: '/content/:id',
    UPDATE: '/content/:id',
    DELETE: '/content/:id',
    SEARCH: '/content/search',
    FINGERPRINT: '/content/:id/fingerprint',
    PROTECTION: '/content/:id/protection'
  },

  // AI Processing
  AI: {
    ANALYZE: '/ai/analyze',
    ENHANCE: '/ai/enhance',
    GENERATE: '/ai/generate',
    CLASSIFY: '/ai/classify',
    FINGERPRINT: '/ai/fingerprint',
    SIMILARITY: '/ai/similarity'
  },

  // Synchronization
  SYNC: {
    PUSH: '/sync/push',
    PULL: '/sync/pull',
    STATUS: '/sync/status',
    CONFLICTS: '/sync/conflicts',
    RESOLVE: '/sync/resolve'
  },

  // Push Notifications
  NOTIFICATIONS: {
    REGISTER: '/notifications/register',
    SEND: '/notifications/send',
    HISTORY: '/notifications/history',
    SETTINGS: '/notifications/settings',
    ANALYTICS: '/notifications/analytics'
  },

  // Monetization
  MONETIZATION: {
    REVENUE: '/monetization/revenue',
    LICENSING: '/monetization/licensing',
    PAYMENTS: '/monetization/payments',
    ANALYTICS: '/monetization/analytics',
    CONTRACTS: '/monetization/contracts'
  },

  // Collaboration
  COLLABORATION: {
    PROJECTS: '/collaboration/projects',
    SESSIONS: '/collaboration/sessions',
    PARTICIPANTS: '/collaboration/participants',
    MESSAGES: '/collaboration/messages',
    MATCHING: '/collaboration/matching'
  },

  // Analytics and Monitoring
  ANALYTICS: {
    EVENTS: '/analytics/events',
    METRICS: '/analytics/metrics',
    PERFORMANCE: '/analytics/performance',
    USAGE: '/analytics/usage'
  }
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  // Authentication
  AUTH_TOKEN: 'ainflue_auth_token',
  REFRESH_TOKEN: 'ainflue_refresh_token',
  USER_SESSION: 'ainflue_user_session',
  BIOMETRIC_KEY: 'ainflue_biometric_key',
  DEVICE_ID: 'ainflue_device_id',

  // Content and Media
  CONTENT_CACHE: 'ainflue_content_cache',
  MEDIA_CACHE: 'ainflue_media_cache',
  UPLOAD_QUEUE: 'ainflue_upload_queue',
  FINGERPRINTS: 'ainflue_fingerprints',
  DRAFTS: 'ainflue_drafts',

  // Synchronization
  SYNC_QUEUE: 'ainflue_sync_queue',
  SYNC_STATUS: 'ainflue_sync_status',
  CONFLICT_QUEUE: 'ainflue_conflict_queue',
  DELTA_SYNC: 'ainflue_delta_sync',

  // Offline Storage
  OFFLINE_DATA: 'ainflue_offline_data',
  OFFLINE_QUEUE: 'ainflue_offline_queue',
  CACHE_INDEX: 'ainflue_cache_index',
  STORAGE_MANIFEST: 'ainflue_storage_manifest',

  // Notifications
  NOTIFICATION_TOKENS: 'ainflue_notification_tokens',
  NOTIFICATION_SETTINGS: 'ainflue_notification_settings',
  NOTIFICATION_HISTORY: 'ainflue_notification_history',
  NOTIFICATION_ANALYTICS: 'ainflue_notification_analytics',

  // User Preferences
  USER_PREFERENCES: 'ainflue_user_preferences',
  APP_SETTINGS: 'ainflue_app_settings',
  PRIVACY_SETTINGS: 'ainflue_privacy_settings',
  ACCESSIBILITY_SETTINGS: 'ainflue_accessibility_settings',

  // Location and Geography
  LOCATION_CACHE: 'ainflue_location_cache',
  GEOFENCES: 'ainflue_geofences',
  LOCATION_HISTORY: 'ainflue_location_history',

  // Performance and Analytics
  PERFORMANCE_METRICS: 'ainflue_performance_metrics',
  USAGE_ANALYTICS: 'ainflue_usage_analytics',
  ERROR_LOGS: 'ainflue_error_logs',
  DEBUG_INFO: 'ainflue_debug_info'
} as const;

// Notification Types
export const NOTIFICATION_TYPES = {
  // Content Related
  CONTENT_UPLOADED: 'content_uploaded',
  CONTENT_PROTECTED: 'content_protected',
  CONTENT_VIOLATION: 'content_violation',
  CONTENT_APPROVED: 'content_approved',

  // Collaboration
  COLLABORATION_INVITE: 'collaboration_invite',
  COLLABORATION_REQUEST: 'collaboration_request',
  COLLABORATION_ACCEPTED: 'collaboration_accepted',
  COLLABORATION_MESSAGE: 'collaboration_message',

  // Monetization
  REVENUE_MILESTONE: 'revenue_milestone',
  PAYMENT_RECEIVED: 'payment_received',
  LICENSING_OPPORTUNITY: 'licensing_opportunity',
  CONTRACT_SIGNED: 'contract_signed',

  // Security and Protection
  SECURITY_ALERT: 'security_alert',
  UNAUTHORIZED_ACCESS: 'unauthorized_access',
  PROTECTION_BREACH: 'protection_breach',
  BIOMETRIC_FAILURE: 'biometric_failure',

  // System and Updates
  SYSTEM_UPDATE: 'system_update',
  FEATURE_ANNOUNCEMENT: 'feature_announcement',
  MAINTENANCE_SCHEDULE: 'maintenance_schedule',
  SYNC_COMPLETED: 'sync_completed',

  // Marketing and Engagement
  PROMOTIONAL: 'promotional',
  ACHIEVEMENT: 'achievement',
  REMINDER: 'reminder',
  RECOMMENDATION: 'recommendation'
} as const;

// Media Quality Presets
export const MEDIA_QUALITY_PRESETS = {
  // Video Quality Presets
  VIDEO: {
    LOW: {
      resolution: '480p',
      bitrate: 1000,
      fps: 24,
      codec: 'h264',
      profile: 'baseline'
    },
    MEDIUM: {
      resolution: '720p',
      bitrate: 2500,
      fps: 30,
      codec: 'h264',
      profile: 'main'
    },
    HIGH: {
      resolution: '1080p',
      bitrate: 5000,
      fps: 60,
      codec: 'h264',
      profile: 'high'
    },
    ULTRA: {
      resolution: '4K',
      bitrate: 15000,
      fps: 60,
      codec: 'h265',
      profile: 'main10'
    }
  },

  // Audio Quality Presets
  AUDIO: {
    LOW: {
      sampleRate: 22050,
      bitRate: 64,
      channels: 1,
      format: 'mp3'
    },
    MEDIUM: {
      sampleRate: 44100,
      bitRate: 128,
      channels: 2,
      format: 'mp3'
    },
    HIGH: {
      sampleRate: 48000,
      bitRate: 256,
      channels: 2,
      format: 'aac'
    },
    ULTRA: {
      sampleRate: 96000,
      bitRate: 320,
      channels: 2,
      format: 'flac'
    }
  },

  // Photo Quality Presets
  PHOTO: {
    LOW: {
      resolution: '1080x720',
      quality: 70,
      format: 'jpeg'
    },
    MEDIUM: {
      resolution: '1920x1080',
      quality: 85,
      format: 'jpeg'
    },
    HIGH: {
      resolution: '3840x2160',
      quality: 95,
      format: 'jpeg'
    },
    ULTRA: {
      resolution: '7680x4320',
      quality: 100,
      format: 'png'
    }
  }
} as const;

// Synchronization Intervals
export const SYNC_INTERVALS = {
  // Regular Sync Intervals (milliseconds)
  REAL_TIME: 1000,        // 1 second
  FREQUENT: 5000,         // 5 seconds
  NORMAL: 30000,          // 30 seconds
  MODERATE: 60000,        // 1 minute
  SLOW: 300000,           // 5 minutes
  BACKGROUND: 900000,     // 15 minutes
  DAILY: 86400000,        // 24 hours

  // Special Intervals
  HEARTBEAT: 10000,       // 10 seconds
  RETRY_BASE: 1000,       // 1 second (exponential backoff base)
  TIMEOUT: 30000,         // 30 seconds
  KEEP_ALIVE: 60000      // 1 minute
} as const;

// Service Configuration Defaults
export const SERVICE_DEFAULTS = {
  // API Service
  API: {
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
    CACHE_TTL: 300000,
    MAX_CACHE_SIZE: 50 * 1024 * 1024 // 50MB
  },

  // Offline Storage
  STORAGE: {
    MAX_SIZE: 100 * 1024 * 1024, // 100MB
    CLEANUP_THRESHOLD: 0.9,
    COMPRESSION_LEVEL: 6,
    ENCRYPTION_KEY_SIZE: 32
  },

  // Synchronization
  SYNC: {
    BATCH_SIZE: 50,
    MAX_RETRIES: 5,
    CONFLICT_RESOLUTION: 'server',
    DELTA_SYNC_THRESHOLD: 10
  },

  // Notifications
  NOTIFICATIONS: {
    MAX_RETRIES: 3,
    BATCH_SIZE: 100,
    RATE_LIMIT: 1000, // per hour
    TTL: 86400 // 24 hours
  },

  // Biometric Authentication
  BIOMETRIC: {
    MAX_ATTEMPTS: 5,
    TIMEOUT: 30,
    FALLBACK_ENABLED: true,
    ENCRYPTION_STRENGTH: 'high'
  },

  // Camera Service
  CAMERA: {
    DEFAULT_QUALITY: 'high',
    MAX_DURATION: 300, // 5 minutes
    STABILIZATION: true,
    HDR: true,
    AI_ENHANCEMENT: true
  },

  // Audio Service
  AUDIO: {
    SAMPLE_RATE: 48000,
    BIT_RATE: 256,
    CHANNELS: 2,
    FORMAT: 'aac',
    MAX_DURATION: 600, // 10 minutes
    NOISE_REDUCTION: true
  },

  // Location Service
  LOCATION: {
    HIGH_ACCURACY: true,
    TIMEOUT: 15000,
    MAXIMUM_AGE: 60000,
    DISTANCE_FILTER: 10,
    BACKGROUND_ENABLED: false
  }
} as const;

// Error Codes
export const ERROR_CODES = {
  // Network Errors
  NETWORK_UNAVAILABLE: 'NETWORK_UNAVAILABLE',
  REQUEST_TIMEOUT: 'REQUEST_TIMEOUT',
  SERVER_ERROR: 'SERVER_ERROR',
  RATE_LIMITED: 'RATE_LIMITED',

  // Authentication Errors
  UNAUTHORIZED: 'UNAUTHORIZED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  BIOMETRIC_FAILED: 'BIOMETRIC_FAILED',
  PERMISSION_DENIED: 'PERMISSION_DENIED',

  // Storage Errors
  STORAGE_FULL: 'STORAGE_FULL',
  ENCRYPTION_FAILED: 'ENCRYPTION_FAILED',
  DATA_CORRUPTED: 'DATA_CORRUPTED',
  SYNC_CONFLICT: 'SYNC_CONFLICT',

  // Media Errors
  CAMERA_UNAVAILABLE: 'CAMERA_UNAVAILABLE',
  AUDIO_PERMISSION_DENIED: 'AUDIO_PERMISSION_DENIED',
  MEDIA_PROCESSING_FAILED: 'MEDIA_PROCESSING_FAILED',
  QUALITY_TOO_LOW: 'QUALITY_TOO_LOW',

  // Location Errors
  LOCATION_UNAVAILABLE: 'LOCATION_UNAVAILABLE',
  GPS_DISABLED: 'GPS_DISABLED',
  GEOFENCE_ERROR: 'GEOFENCE_ERROR',

  // General Errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  CONFIGURATION_ERROR: 'CONFIGURATION_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
} as const;

// Content Types
export const CONTENT_TYPES = {
  // Media Types
  IMAGE: 'image',
  VIDEO: 'video',
  AUDIO: 'audio',
  TEXT: 'text',
  DOCUMENT: 'document',

  // Creator Types
  MUSICIAN: 'musician',
  BLOGGER: 'blogger',
  PHOTOGRAPHER: 'photographer',
  INFLUENCER: 'influencer',
  COMEDIAN: 'comedian',
  ARTIST: 'artist',

  // Content Categories
  ENTERTAINMENT: 'entertainment',
  EDUCATIONAL: 'educational',
  PROMOTIONAL: 'promotional',
  ARTISTIC: 'artistic',
  COMMERCIAL: 'commercial',
  PERSONAL: 'personal'
} as const;

// Platform Identifiers
export const PLATFORMS = {
  // Social Media
  YOUTUBE: 'youtube',
  INSTAGRAM: 'instagram',
  TIKTOK: 'tiktok',
  FACEBOOK: 'facebook',
  TWITTER: 'twitter',
  LINKEDIN: 'linkedin',
  PINTEREST: 'pinterest',
  SNAPCHAT: 'snapchat',

  // Music Platforms
  SPOTIFY: 'spotify',
  APPLE_MUSIC: 'apple_music',
  SOUNDCLOUD: 'soundcloud',
  BANDCAMP: 'bandcamp',
  DEEZER: 'deezer',

  // Video Platforms
  VIMEO: 'vimeo',
  DAILYMOTION: 'dailymotion',
  TWITCH: 'twitch',

  // E-commerce
  AMAZON: 'amazon',
  ETSY: 'etsy',
  EBAY: 'ebay'
} as const;

// Feature Flags
export const FEATURE_FLAGS = {
  // Core Features
  ENABLE_OFFLINE_MODE: true,
  ENABLE_REAL_TIME_SYNC: true,
  ENABLE_AI_ENHANCEMENT: true,
  ENABLE_BIOMETRIC_AUTH: true,

  // Advanced Features
  ENABLE_VOICE_COMMANDS: false,
  ENABLE_AR_FILTERS: false,
  ENABLE_BLOCKCHAIN_PROTECTION: false,
  ENABLE_QUANTUM_ENCRYPTION: false,

  // Beta Features
  ENABLE_COLLABORATIVE_EDITING: true,
  ENABLE_PREDICTIVE_ANALYTICS: true,
  ENABLE_AUTOMATED_LICENSING: true,
  ENABLE_CROSS_PLATFORM_SYNC: true,

  // Debug Features
  ENABLE_PERFORMANCE_MONITORING: true,
  ENABLE_CRASH_REPORTING: true,
  ENABLE_ANALYTICS_TRACKING: true,
  ENABLE_DEBUG_LOGGING: false
} as const;

// Business Logic Constants
export const BUSINESS_RULES = {
  // Revenue Sharing
  PLATFORM_COMMISSION: 0.15, // 15%
  CREATOR_SHARE: 0.85,       // 85%
  
  // Protection Thresholds
  SIMILARITY_THRESHOLD: 0.85,
  RISK_THRESHOLD: 0.7,
  
  // Collaboration Limits
  MAX_COLLABORATORS: 10,
  MAX_PROJECT_SIZE: 1024 * 1024 * 1024, // 1GB
  
  // Content Limits
  MAX_UPLOAD_SIZE: 500 * 1024 * 1024, // 500MB
  MAX_DAILY_UPLOADS: 100,
  
  // Monetization Thresholds
  MIN_PAYOUT: 50, // $50
  MAX_REVENUE_PREDICTION_DAYS: 90
} as const;