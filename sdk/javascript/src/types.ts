/**
 * TypeScript Type Definitions for Ainflue SDK
 * 
 * Comprehensive type system designed with multi-expert approach:
 * - DBA: Optimized data structures and schemas
 * - Backend Senior: Robust API interface definitions
 * - Sécurité: Security-aware type constraints
 * - Lead Dev IA: AI-enhanced type intelligence
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 */

// Base types
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
export type ContentType = 'image' | 'video' | 'audio' | 'text' | 'document' | 'other';
export type MediaFormat = 'jpg' | 'png' | 'gif' | 'mp4' | 'mov' | 'mp3' | 'wav' | 'pdf' | 'txt' | 'doc';
export type AuthProvider = 'api_key' | 'jwt' | 'oauth' | 'service_account';
export type EventType = 'upload' | 'analysis' | 'protection' | 'error' | 'auth' | 'metric';

// Configuration types
export interface AinflueClientOptions {
  apiKey?: string;
  baseUrl?: string;
  apiVersion?: string;
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  enableLogging?: boolean;
  enableCaching?: boolean;
  enableMetrics?: boolean;
  customHeaders?: Record<string, string>;
  authProvider?: AuthProvider;
  environment?: 'production' | 'staging' | 'development';
}

export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
  cache?: boolean;
  validateResponse?: boolean;
  signal?: AbortSignal;
}

// Authentication types
export interface AuthToken {
  accessToken: string;
  tokenType: 'Bearer' | 'API-Key';
  expiresAt?: Date;
  refreshToken?: string;
  scope?: string[];
}

export interface AuthConfig {
  provider: AuthProvider;
  credentials: {
    apiKey?: string;
    clientId?: string;
    clientSecret?: string;
    username?: string;
    password?: string;
  };
  options?: {
    scope?: string[];
    audience?: string;
    issuer?: string;
  };
}

// Content processing types
export interface ContentMetadata {
  id: string;
  filename: string;
  contentType: ContentType;
  format: MediaFormat;
  size: number;
  duration?: number;
  dimensions?: {
    width: number;
    height: number;
  };
  checksum: string;
  uploadedAt: Date;
  tags?: string[];
  customData?: Record<string, any>;
}

export interface AnalysisOptions {
  analysisTypes: ('fingerprint' | 'similarity' | 'content' | 'metadata')[];
  aiModels?: string[];
  confidence?: number;
  includePreview?: boolean;
  customOptions?: Record<string, any>;
}

export interface ProtectionOptions {
  platforms: string[];
  monitoringEnabled: boolean;
  takedownEnabled: boolean;
  notificationSettings: {
    email?: boolean;
    webhook?: string;
    slack?: string;
  };
  customRules?: Array<{
    condition: string;
    action: string;
  }>;
}

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  metadata?: {
    requestId: string;
    timestamp: Date;
    duration: number;
    version: string;
  };
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    statusCode: number;
  };
  requestId: string;
  timestamp: Date;
}

export interface SuccessResponse<T = any> extends ApiResponse<T> {
  success: true;
  data: T;
}

export interface PaginatedResponse<T = any> extends SuccessResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Content analysis types
export interface ContentAnalysisResult {
  contentId: string;
  analysisId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  confidence: number;
  fingerprint: {
    hash: string;
    algorithm: string;
    segments?: Array<{
      start: number;
      end: number;
      hash: string;
    }>;
  };
  aiAnalysis?: {
    categories: string[];
    sentiment?: 'positive' | 'negative' | 'neutral';
    entities?: Array<{
      type: string;
      value: string;
      confidence: number;
    }>;
    keywords?: string[];
    summary?: string;
  };
  metadata: ContentMetadata;
  createdAt: Date;
  completedAt?: Date;
}

export interface ContentProtectionResult {
  protectionId: string;
  contentId: string;
  status: 'active' | 'inactive' | 'suspended';
  platforms: Array<{
    name: string;
    enabled: boolean;
    lastCheck: Date;
    matchesFound: number;
  }>;
  totalMatches: number;
  actionsHistory: Array<{
    timestamp: Date;
    action: string;
    platform: string;
    details: Record<string, any>;
  }>;
  settings: ProtectionOptions;
  createdAt: Date;
  updatedAt: Date;
}

// Upload types
export interface UploadOptions {
  filename?: string;
  contentType?: ContentType;
  tags?: string[];
  metadata?: Record<string, any>;
  analysisOptions?: AnalysisOptions;
  protectionOptions?: ProtectionOptions;
  onProgress?: (progress: UploadProgress) => void;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
  stage: 'uploading' | 'processing' | 'analyzing' | 'complete';
}

export interface UploadResult {
  uploadId: string;
  contentId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  url?: string;
  metadata: ContentMetadata;
  analysisResult?: ContentAnalysisResult;
  protectionResult?: ContentProtectionResult;
  errors?: string[];
}

// User and account types
export interface UserProfile {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  plan: 'free' | 'pro' | 'enterprise';
  quota: {
    uploads: {
      used: number;
      limit: number;
    };
    storage: {
      used: number;
      limit: number;
    };
    analysis: {
      used: number;
      limit: number;
    };
  };
  settings: {
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
    };
    privacy: {
      publicProfile: boolean;
      shareAnalytics: boolean;
    };
  };
  createdAt: Date;
  updatedAt: Date;
}

// Analytics types
export interface AnalyticsData {
  period: {
    start: Date;
    end: Date;
  };
  metrics: {
    uploads: {
      total: number;
      successful: number;
      failed: number;
      byType: Record<ContentType, number>;
    };
    protection: {
      activeProtections: number;
      matchesDetected: number;
      actionsPerformed: number;
      platforms: Record<string, number>;
    };
    usage: {
      storageUsed: number;
      analysisRequests: number;
      apiCalls: number;
      bandwidth: number;
    };
    performance: {
      averageUploadTime: number;
      averageAnalysisTime: number;
      successRate: number;
      errorRate: number;
    };
  };
  trends: Array<{
    date: Date;
    uploads: number;
    matches: number;
    actions: number;
  }>;
}

// Event system types
export interface EventData {
  type: EventType;
  timestamp: Date;
  data: Record<string, any>;
  metadata?: {
    source: string;
    userId?: string;
    sessionId?: string;
  };
}

export type EventHandler<T = EventData> = (event: T) => void | Promise<void>;

// Webhook types
export interface WebhookEvent {
  id: string;
  type: string;
  data: Record<string, any>;
  timestamp: Date;
  signature: string;
}

export interface WebhookConfig {
  url: string;
  events: string[];
  secret: string;
  active: boolean;
  retryPolicy?: {
    maxRetries: number;
    backoffMultiplier: number;
  };
}

// Cache types
export interface CacheOptions {
  ttl?: number;
  maxSize?: number;
  strategy?: 'lru' | 'fifo' | 'lfu';
}

export interface CacheEntry<T = any> {
  key: string;
  value: T;
  expiresAt: Date;
  createdAt: Date;
  accessCount: number;
  lastAccessed: Date;
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// API endpoint types
export type ApiEndpoint = 
  | '/auth/login'
  | '/auth/logout'
  | '/auth/refresh'
  | '/content/upload'
  | '/content/analyze'
  | '/content/protect'
  | '/content/search'
  | '/user/profile'
  | '/user/settings'
  | '/analytics/data'
  | '/analytics/reports'
  | '/webhooks/create'
  | '/webhooks/list'
  | '/health'
  | '/metrics';

// Error types
export type ErrorCode = 
  | 'AUTHENTICATION_FAILED'
  | 'AUTHORIZATION_DENIED'
  | 'VALIDATION_ERROR'
  | 'RATE_LIMIT_EXCEEDED'
  | 'QUOTA_EXCEEDED'
  | 'CONTENT_NOT_FOUND'
  | 'ANALYSIS_FAILED'
  | 'UPLOAD_FAILED'
  | 'NETWORK_ERROR'
  | 'SERVER_ERROR'
  | 'UNKNOWN_ERROR';

// SDK internal types
export interface SdkConfig {
  version: string;
  apiVersion: string;
  userAgent: string;
  endpoints: Record<string, string>;
  limits: {
    maxFileSize: number;
    maxUploadRetries: number;
    maxRequestRetries: number;
    requestTimeout: number;
  };
}

export interface SdkMetrics {
  requests: {
    total: number;
    successful: number;
    failed: number;
    byEndpoint: Record<string, number>;
  };
  performance: {
    averageResponseTime: number;
    totalResponseTime: number;
    slowestRequest: number;
    fastestRequest: number;
  };
  errors: {
    byType: Record<ErrorCode, number>;
    lastError?: {
      code: ErrorCode;
      message: string;
      timestamp: Date;
    };
  };
  uptime: {
    startTime: Date;
    totalUptime: number;
  };
}