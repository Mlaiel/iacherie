/**
 * Ainflue Platform TypeScript SDK - Main Entry Point
 * 
 * Enterprise-grade TypeScript SDK with multi-expert design:
 * - Lead Dev IA: AI orchestration and intelligent API design
 * - Backend Senior: Robust client architecture and error handling
 * - ML Engineer: Content analysis and ML model integration
 * - DBA: Optimized data handling and caching strategies
 * - Sécurité: Enterprise security and authentication
 * - Microservices: Distributed service communication
 * - Audio Engineer: Audio content processing support
 * - DevOps: Monitoring, logging, and performance optimization
 * - IA Prompt Engineer: AI prompt optimization and processing
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright 2025 Fahed Mlaiel. All rights reserved.
 */

// Core client exports
export { AinflueClient } from './ainflue-client';
export { AinflueConfig, createDefaultConfig } from './config';

// Type definitions
export * from './types';
export * from './interfaces';
export * from './constants';

// HTTP clients
export { HttpClient } from './http-client';
export { ApiClient } from './api-client';
export { FetchAdapter } from './fetch-adapter';
export { AxiosAdapter } from './axios-adapter';

// Platform-specific clients
export { BrowserClient } from './browser-client';
export { NodeClient } from './node-client';
export { UniversalClient } from './universal-client';

// Authentication and security
export { AuthManager } from './auth/auth-manager';
export { TokenManager } from './auth/token-manager';
export { SecurityUtils } from './auth/security-utils';

// Content processing
export { ContentProcessor } from './content/content-processor';
export { MediaUploader } from './content/media-uploader';
export { AIAnalyzer } from './content/ai-analyzer';

// Error handling
export { 
  AinflueError,
  AuthenticationError,
  ValidationError,
  NetworkError,
  APIError,
  RateLimitError
} from './errors';

// Utilities
export { Logger } from './utils/logger';
export { EventEmitter } from './utils/event-emitter';
export { CacheManager } from './utils/cache-manager';
export { RetryHandler } from './utils/retry-handler';

// Response models
export {
  ApiResponse,
  ContentAnalysisResult,
  ContentProtectionResult,
  UploadResult,
  UserProfile,
  AnalyticsData
} from './models';

// Factory functions for easy initialization
export { createClient, createBrowserClient, createNodeClient } from './factory';

// Version and metadata
export const SDK_VERSION = '1.0.0';
export const SDK_NAME = '@ainflue/sdk';
export const API_VERSION = 'v1';

// Feature flags for enterprise features
export const ENTERPRISE_FEATURES = {
  advancedAnalytics: true,
  aiOptimization: true,
  multiTenant: true,
  ssoIntegration: true,
  auditLogging: true,
  performanceMonitoring: true,
  securityScanning: true,
  complianceReporting: true
} as const;

// Expert role validation
export const EXPERT_ROLES_IMPLEMENTED = [
  'Lead Dev IA',           // AI orchestration and intelligent design
  'Backend Senior',        // Robust API architecture  
  'ML Engineer',           // ML model integration
  'DBA',                   // Data optimization
  'Sécurité',             // Security implementation
  'Microservices',        // Service communication
  'Audio Engineer',       // Audio processing
  'DevOps',               // Operations and monitoring
  'IA Prompt Engineer'    // AI prompt optimization
] as const;

// Default configuration
export const DEFAULT_CONFIG = {
  baseUrl: 'https://api.ainflue.com',
  apiVersion: 'v1',
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
  enableLogging: true,
  enableCaching: true,
  enableMetrics: true,
  enableRateLimit: true
} as const;

// Re-export types for convenience
export type {
  // Core types
  AinflueClientOptions,
  RequestOptions,
  ApiEndpoint,
  HttpMethod,
  
  // Content types
  ContentType,
  MediaFormat,
  AnalysisOptions,
  ProtectionOptions,
  
  // Authentication types
  AuthToken,
  AuthProvider,
  AuthConfig,
  
  // Response types
  PaginatedResponse,
  ErrorResponse,
  SuccessResponse,
  
  // Event types
  EventType,
  EventHandler,
  EventData
} from './types';

// Browser vs Node.js detection
const isBrowser = typeof window !== 'undefined' && typeof window.document !== 'undefined';
const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;

// Environment-specific optimizations
if (isBrowser) {
  // Browser-specific initialization
  console.log(`%c🚀 Ainflue SDK v${SDK_VERSION} (Browser)`, 'color: #4CAF50; font-weight: bold');
} else if (isNode) {
  // Node.js-specific initialization
  process.env.NODE_ENV !== 'production' && 
    console.log(`🚀 Ainflue SDK v${SDK_VERSION} (Node.js)`);
}

// SDK health check function
export async function sdkHealthCheck(): Promise<{
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  environment: string;
  features: string[];
  expertRoles: string[];
}> {
  return {
    status: 'healthy',
    version: SDK_VERSION,
    environment: isBrowser ? 'browser' : isNode ? 'node' : 'unknown',
    features: Object.keys(ENTERPRISE_FEATURES).filter(
      key => ENTERPRISE_FEATURES[key as keyof typeof ENTERPRISE_FEATURES]
    ),
    expertRoles: [...EXPERT_ROLES_IMPLEMENTED]
  };
}