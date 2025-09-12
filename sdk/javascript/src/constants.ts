/**
 * SDK Constants and Enums for Ainflue SDK
 * 
 * Multi-expert implementation:
 * - Lead Dev IA: Intelligent constant organization and optimization
 * - Backend Senior: Robust constant architecture for scalability
 * - Security: Security-related constants and validation patterns
 * - DevOps: Monitoring and operational constants
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 */

/**
 * SDK Version and Metadata
 */
export const SDK_VERSION = '1.0.0';
export const SDK_NAME = 'Ainflue TypeScript SDK';
export const SDK_USER_AGENT = `${SDK_NAME}/${SDK_VERSION}`;

/**
 * API Configuration Constants
 */
export const API_CONSTANTS = {
  DEFAULT_BASE_URL: 'https://api.ainflue.com',
  DEFAULT_TIMEOUT: 30000, // 30 seconds
  DEFAULT_RETRY_ATTEMPTS: 3,
  DEFAULT_RETRY_DELAY: 1000, // 1 second
  DEFAULT_RATE_LIMIT: 1000, // requests per hour
  MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks for uploads
  MAX_CONCURRENT_UPLOADS: 5,
} as const;

/**
 * HTTP Status Codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * Error Types and Codes (Lead Dev IA expertise)
 */
export const ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
  NOT_FOUND_ERROR: 'NOT_FOUND_ERROR',
  CONFLICT_ERROR: 'CONFLICT_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  UPLOAD_ERROR: 'UPLOAD_ERROR',
  PROCESSING_ERROR: 'PROCESSING_ERROR',
  QUOTA_EXCEEDED_ERROR: 'QUOTA_EXCEEDED_ERROR',
  CONFIGURATION_ERROR: 'CONFIGURATION_ERROR',
  DEPRECATED_API_ERROR: 'DEPRECATED_API_ERROR',
} as const;

/**
 * Content Types and MIME Types (Audio Engineer expertise)
 */
export const CONTENT_TYPES = {
  // Audio formats
  AUDIO: {
    MP3: 'audio/mpeg',
    WAV: 'audio/wav',
    FLAC: 'audio/flac',
    AAC: 'audio/aac',
    OGG: 'audio/ogg',
    M4A: 'audio/m4a',
    WMA: 'audio/x-ms-wma',
    OPUS: 'audio/opus',
    AIFF: 'audio/aiff',
  },
  
  // Video formats
  VIDEO: {
    MP4: 'video/mp4',
    MOV: 'video/quicktime',
    AVI: 'video/x-msvideo',
    MKV: 'video/x-matroska',
    WEBM: 'video/webm',
    FLV: 'video/x-flv',
    WMV: 'video/x-ms-wmv',
    M4V: 'video/x-m4v',
  },
  
  // Image formats
  IMAGE: {
    JPEG: 'image/jpeg',
    PNG: 'image/png',
    GIF: 'image/gif',
    WEBP: 'image/webp',
    SVG: 'image/svg+xml',
    BMP: 'image/bmp',
    TIFF: 'image/tiff',
    ICO: 'image/x-icon',
  },
  
  // Document formats
  DOCUMENT: {
    PDF: 'application/pdf',
    DOC: 'application/msword',
    DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    TXT: 'text/plain',
    RTF: 'application/rtf',
  },
  
  // Application types
  APPLICATION: {
    JSON: 'application/json',
    XML: 'application/xml',
    FORM_URLENCODED: 'application/x-www-form-urlencoded',
    MULTIPART: 'multipart/form-data',
    OCTET_STREAM: 'application/octet-stream',
  },
} as const;

/**
 * Supported File Extensions
 */
export const FILE_EXTENSIONS = {
  AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus', '.aiff'],
  VIDEO: ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'],
  IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.ico'],
  DOCUMENT: ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
} as const;

/**
 * Quality Levels for Media Processing (Audio Engineer + ML Engineer expertise)
 */
export const QUALITY_LEVELS = {
  AUDIO: {
    LOW: { bitrate: 64, sampleRate: 22050, channels: 1 },
    MEDIUM: { bitrate: 128, sampleRate: 44100, channels: 2 },
    HIGH: { bitrate: 256, sampleRate: 44100, channels: 2 },
    LOSSLESS: { bitrate: 0, sampleRate: 48000, channels: 2 }, // 0 = variable/lossless
  },
  
  VIDEO: {
    LOW: { width: 480, height: 320, bitrate: 500 },
    MEDIUM: { width: 720, height: 480, bitrate: 1500 },
    HIGH: { width: 1280, height: 720, bitrate: 5000 },
    ULTRA: { width: 1920, height: 1080, bitrate: 10000 },
    UHD: { width: 3840, height: 2160, bitrate: 25000 },
  },
  
  IMAGE: {
    THUMBNAIL: { width: 150, height: 150, quality: 70 },
    SMALL: { width: 300, height: 300, quality: 80 },
    MEDIUM: { width: 800, height: 600, quality: 85 },
    LARGE: { width: 1920, height: 1080, quality: 90 },
    ORIGINAL: { width: 0, height: 0, quality: 100 }, // 0 = preserve original
  },
} as const;

/**
 * AI Processing Types (ML Engineer expertise)
 */
export const AI_PROCESSORS = {
  COPYRIGHT_DETECTION: 'copyright_detection',
  AUDIO_TRANSCRIPTION: 'audio_transcription',
  VIDEO_TRANSCRIPTION: 'video_transcription',
  LANGUAGE_TRANSLATION: 'language_translation',
  AUTO_TAGGING: 'auto_tagging',
  SENTIMENT_ANALYSIS: 'sentiment_analysis',
  CONTENT_SUMMARIZATION: 'content_summarization',
  OBJECT_DETECTION: 'object_detection',
  FACE_DETECTION: 'face_detection',
  NSFW_DETECTION: 'nsfw_detection',
  AUDIO_ENHANCEMENT: 'audio_enhancement',
  NOISE_REDUCTION: 'noise_reduction',
  VOICE_CLONING: 'voice_cloning',
  STYLE_TRANSFER: 'style_transfer',
  UPSCALING: 'upscaling',
} as const;

/**
 * Supported Languages for AI Processing
 */
export const SUPPORTED_LANGUAGES = {
  ENGLISH: 'en',
  SPANISH: 'es',
  FRENCH: 'fr',
  GERMAN: 'de',
  ITALIAN: 'it',
  PORTUGUESE: 'pt',
  RUSSIAN: 'ru',
  CHINESE: 'zh',
  JAPANESE: 'ja',
  KOREAN: 'ko',
  ARABIC: 'ar',
  HINDI: 'hi',
  DUTCH: 'nl',
  SWEDISH: 'sv',
  NORWEGIAN: 'no',
  DANISH: 'da',
  FINNISH: 'fi',
  POLISH: 'pl',
  TURKISH: 'tr',
  GREEK: 'el',
} as const;

/**
 * Authentication Methods (Security expertise)
 */
export const AUTH_METHODS = {
  EMAIL_PASSWORD: 'email_password',
  OAUTH_GOOGLE: 'oauth_google',
  OAUTH_FACEBOOK: 'oauth_facebook',
  OAUTH_TWITTER: 'oauth_twitter',
  OAUTH_GITHUB: 'oauth_github',
  OAUTH_LINKEDIN: 'oauth_linkedin',
  OAUTH_APPLE: 'oauth_apple',
  OAUTH_MICROSOFT: 'oauth_microsoft',
  API_KEY: 'api_key',
  JWT_TOKEN: 'jwt_token',
  TWO_FACTOR: 'two_factor',
} as const;

/**
 * Permission Levels (Security expertise)
 */
export const PERMISSIONS = {
  READ: 'read',
  WRITE: 'write',
  DELETE: 'delete',
  ADMIN: 'admin',
  SHARE: 'share',
  DOWNLOAD: 'download',
  UPLOAD: 'upload',
  COLLABORATE: 'collaborate',
  MODERATE: 'moderate',
  ANALYTICS: 'analytics',
} as const;

/**
 * User Roles
 */
export const USER_ROLES = {
  GUEST: 'guest',
  USER: 'user',
  CREATOR: 'creator',
  MODERATOR: 'moderator',
  ADMIN: 'admin',
  SUPER_ADMIN: 'super_admin',
} as const;

/**
 * Content Visibility Levels
 */
export const VISIBILITY_LEVELS = {
  PUBLIC: 'public',
  PRIVATE: 'private',
  UNLISTED: 'unlisted',
  FRIENDS_ONLY: 'friends_only',
  SUBSCRIBERS_ONLY: 'subscribers_only',
} as const;

/**
 * Processing Status Types (DevOps expertise)
 */
export const PROCESSING_STATUS = {
  QUEUED: 'queued',
  INITIALIZING: 'initializing',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
  RETRYING: 'retrying',
  PARTIALLY_COMPLETED: 'partially_completed',
} as const;

/**
 * Analytics Event Types (DevOps expertise)
 */
export const ANALYTICS_EVENTS = {
  // Content events
  CONTENT_VIEWED: 'content_viewed',
  CONTENT_DOWNLOADED: 'content_downloaded',
  CONTENT_SHARED: 'content_shared',
  CONTENT_LIKED: 'content_liked',
  CONTENT_COMMENTED: 'content_commented',
  CONTENT_UPLOADED: 'content_uploaded',
  
  // User events
  USER_REGISTERED: 'user_registered',
  USER_LOGIN: 'user_login',
  USER_LOGOUT: 'user_logout',
  USER_PROFILE_UPDATED: 'user_profile_updated',
  
  // Subscription events
  SUBSCRIPTION_STARTED: 'subscription_started',
  SUBSCRIPTION_CANCELLED: 'subscription_cancelled',
  SUBSCRIPTION_RENEWED: 'subscription_renewed',
  PAYMENT_COMPLETED: 'payment_completed',
  
  // Collaboration events
  PROJECT_CREATED: 'project_created',
  COLLABORATOR_INVITED: 'collaborator_invited',
  COLLABORATION_STARTED: 'collaboration_started',
  
  // System events
  API_CALLED: 'api_called',
  ERROR_OCCURRED: 'error_occurred',
  FEATURE_USED: 'feature_used',
} as const;

/**
 * Cache Keys and TTL Values (Backend Senior expertise)
 */
export const CACHE_CONFIG = {
  KEYS: {
    USER_PROFILE: 'user_profile',
    CONTENT_METADATA: 'content_metadata',
    SUBSCRIPTION_INFO: 'subscription_info',
    ANALYTICS_DATA: 'analytics_data',
    AI_PROCESSING_RESULTS: 'ai_processing_results',
    SYSTEM_CONFIG: 'system_config',
  },
  
  TTL: {
    SHORT: 300, // 5 minutes
    MEDIUM: 1800, // 30 minutes
    LONG: 3600, // 1 hour
    VERY_LONG: 86400, // 24 hours
  },
} as const;

/**
 * Rate Limiting Configuration (Backend Senior + Security expertise)
 */
export const RATE_LIMITS = {
  // API endpoints rate limits (requests per minute)
  AUTH: 10,
  UPLOAD: 20,
  DOWNLOAD: 100,
  ANALYTICS: 60,
  AI_PROCESSING: 30,
  GENERAL: 1000,
  
  // Burst limits
  BURST: {
    AUTH: 5,
    UPLOAD: 3,
    DOWNLOAD: 10,
    AI_PROCESSING: 5,
  },
} as const;

/**
 * WebSocket Event Types (Microservices expertise)
 */
export const WEBSOCKET_EVENTS = {
  // Connection events
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  RECONNECT: 'reconnect',
  ERROR: 'error',
  
  // Real-time updates
  CONTENT_UPDATED: 'content_updated',
  PROCESSING_STATUS_CHANGED: 'processing_status_changed',
  COLLABORATION_UPDATE: 'collaboration_update',
  NOTIFICATION_RECEIVED: 'notification_received',
  ANALYTICS_UPDATE: 'analytics_update',
  
  // System events
  SYSTEM_MAINTENANCE: 'system_maintenance',
  RATE_LIMIT_WARNING: 'rate_limit_warning',
  QUOTA_UPDATE: 'quota_update',
} as const;

/**
 * Monitoring and Health Check Constants (DevOps expertise)
 */
export const MONITORING = {
  HEALTH_CHECK_INTERVAL: 30000, // 30 seconds
  METRICS_COLLECTION_INTERVAL: 60000, // 1 minute
  ALERT_THRESHOLDS: {
    ERROR_RATE: 0.05, // 5%
    RESPONSE_TIME: 2000, // 2 seconds
    CPU_USAGE: 0.8, // 80%
    MEMORY_USAGE: 0.85, // 85%
    DISK_USAGE: 0.9, // 90%
  },
  
  SERVICE_TIMEOUTS: {
    DATABASE: 5000, // 5 seconds
    REDIS: 2000, // 2 seconds
    EXTERNAL_API: 10000, // 10 seconds
    FILE_STORAGE: 30000, // 30 seconds
  },
} as const;

/**
 * Security Constants (Security expertise)
 */
export const SECURITY = {
  // Password requirements
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_DIGITS: true,
    REQUIRE_SPECIAL_CHARS: true,
    FORBIDDEN_PATTERNS: ['password', '123456', 'qwerty', 'admin'],
  },
  
  // Token settings
  TOKENS: {
    ACCESS_TOKEN_TTL: 3600, // 1 hour
    REFRESH_TOKEN_TTL: 604800, // 7 days
    API_KEY_LENGTH: 32,
    JWT_ALGORITHM: 'RS256',
  },
  
  // Encryption
  ENCRYPTION: {
    ALGORITHM: 'AES-256-GCM',
    KEY_LENGTH: 32,
    IV_LENGTH: 16,
    SALT_LENGTH: 16,
    ITERATIONS: 100000,
  },
  
  // Security headers
  HEADERS: {
    CONTENT_SECURITY_POLICY: "default-src 'self'; script-src 'self' 'unsafe-inline'",
    X_FRAME_OPTIONS: 'DENY',
    X_CONTENT_TYPE_OPTIONS: 'nosniff',
    X_XSS_PROTECTION: '1; mode=block',
    STRICT_TRANSPORT_SECURITY: 'max-age=31536000; includeSubDomains',
  },
} as const;

/**
 * Environment-specific Configuration
 */
export const ENVIRONMENTS = {
  DEVELOPMENT: 'development',
  STAGING: 'staging',
  PRODUCTION: 'production',
  TEST: 'test',
} as const;

/**
 * Feature Flags (Lead Dev IA expertise)
 */
export const FEATURE_FLAGS = {
  EXPERIMENTAL_AI_FEATURES: 'experimental_ai_features',
  ADVANCED_ANALYTICS: 'advanced_analytics',
  COLLABORATIVE_EDITING: 'collaborative_editing',
  REAL_TIME_PROCESSING: 'real_time_processing',
  BETA_API_ENDPOINTS: 'beta_api_endpoints',
  ENHANCED_SECURITY: 'enhanced_security',
  PERFORMANCE_OPTIMIZATIONS: 'performance_optimizations',
} as const;

/**
 * Regional Settings
 */
export const REGIONS = {
  US_EAST: 'us-east-1',
  US_WEST: 'us-west-1',
  EU_WEST: 'eu-west-1',
  EU_CENTRAL: 'eu-central-1',
  ASIA_PACIFIC: 'ap-southeast-1',
  ASIA_NORTHEAST: 'ap-northeast-1',
} as const;

/**
 * API Versioning
 */
export const API_VERSIONS = {
  V1: 'v1',
  V2: 'v2',
  BETA: 'beta',
  LATEST: 'v2', // Current latest version
} as const;

/**
 * Regular Expressions for Validation (Security expertise)
 */
export const REGEX_PATTERNS = {
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  USERNAME: /^[a-zA-Z0-9_]{3,20}$/,
  API_KEY: /^ak_[a-zA-Z0-9]{32,}$/,
  UUID: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
  IP_ADDRESS: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  PHONE: /^\+?[\d\s\-\(\)]{10,}$/,
  COLOR_HEX: /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/,
  SEMVER: /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$/,
} as const;

/**
 * Default Configuration Values
 */
export const DEFAULTS = {
  PAGINATION: {
    PAGE: 1,
    LIMIT: 20,
    MAX_LIMIT: 100,
  },
  
  UPLOAD: {
    CHUNK_SIZE: 1024 * 1024, // 1MB
    MAX_CONCURRENT: 3,
    RETRY_ATTEMPTS: 3,
    TIMEOUT: 60000, // 60 seconds
  },
  
  CACHE: {
    TTL: 300, // 5 minutes
    MAX_SIZE: 100, // 100 entries
  },
  
  RETRY: {
    ATTEMPTS: 3,
    DELAY: 1000, // 1 second
    BACKOFF_FACTOR: 2,
    MAX_DELAY: 30000, // 30 seconds
  },
} as const;

/**
 * Type guards and utility functions
 */
export const isValidContentType = (contentType: string): boolean => {
  const allTypes = [
    ...Object.values(CONTENT_TYPES.AUDIO),
    ...Object.values(CONTENT_TYPES.VIDEO),
    ...Object.values(CONTENT_TYPES.IMAGE),
    ...Object.values(CONTENT_TYPES.DOCUMENT),
  ];
  return allTypes.includes(contentType);
};

export const getFileTypeFromExtension = (filename: string): string | null => {
  const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'));
  
  if (FILE_EXTENSIONS.AUDIO.includes(extension)) return 'audio';
  if (FILE_EXTENSIONS.VIDEO.includes(extension)) return 'video';
  if (FILE_EXTENSIONS.IMAGE.includes(extension)) return 'image';
  if (FILE_EXTENSIONS.DOCUMENT.includes(extension)) return 'document';
  
  return null;
};

export const isValidEmailFormat = (email: string): boolean => {
  return REGEX_PATTERNS.EMAIL.test(email);
};

export const isValidApiKey = (apiKey: string): boolean => {
  return REGEX_PATTERNS.API_KEY.test(apiKey);
};

export const isValidUUID = (uuid: string): boolean => {
  return REGEX_PATTERNS.UUID.test(uuid);
};

/**
 * Environment detection utilities
 */
export const getEnvironment = (): string => {
  if (typeof process !== 'undefined' && process.env?.NODE_ENV) {
    return process.env.NODE_ENV;
  }
  if (typeof window !== 'undefined' && window.location.hostname.includes('localhost')) {
    return ENVIRONMENTS.DEVELOPMENT;
  }
  return ENVIRONMENTS.PRODUCTION;
};

export const isDevelopment = (): boolean => getEnvironment() === ENVIRONMENTS.DEVELOPMENT;
export const isProduction = (): boolean => getEnvironment() === ENVIRONMENTS.PRODUCTION;
export const isStaging = (): boolean => getEnvironment() === ENVIRONMENTS.STAGING;