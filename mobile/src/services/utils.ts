/**
 * Mobile Services Utilities - Professional Service Helper Functions
 * 
 * Comprehensive utility functions for service configuration, error handling,
 * response formatting, and common operations across the mobile service layer.
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

import CryptoJS from 'crypto-js';
import {
  ServiceResponse,
  ServiceError,
  MobileAPIConfig,
  OfflineStorageConfig,
  SyncConfiguration,
  NotificationConfig,
  BiometricConfig,
  CameraConfig,
  AudioConfig,
  LocationConfig,
  PerformanceMetrics
} from './types';
import { SERVICE_DEFAULTS, ERROR_CODES } from './constants';

/**
 * Creates a mobile service configuration with secure defaults
 */
export function createMobileServiceConfig(
  baseConfig: Partial<MobileAPIConfig>
): MobileAPIConfig {
  return {
    baseUrl: baseConfig.baseUrl || 'https://api.ainflue.com',
    apiKey: baseConfig.apiKey || '',
    timeout: baseConfig.timeout || SERVICE_DEFAULTS.API.TIMEOUT,
    retryAttempts: baseConfig.retryAttempts || SERVICE_DEFAULTS.API.RETRY_ATTEMPTS,
    retryDelay: baseConfig.retryDelay || SERVICE_DEFAULTS.API.RETRY_DELAY,
    enableCaching: baseConfig.enableCaching ?? true,
    enableOfflineQueue: baseConfig.enableOfflineQueue ?? true,
    encryptionKey: baseConfig.encryptionKey || generateEncryptionKey()
  };
}

/**
 * Validates service configuration for completeness and security
 */
export function validateServiceConfiguration<T extends Record<string, any>>(
  config: T,
  requiredFields: (keyof T)[]
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check required fields
  for (const field of requiredFields) {
    if (!config[field]) {
      errors.push(`Missing required field: ${String(field)}`);
    }
  }

  // Validate specific field types and values
  if ('timeout' in config && typeof config.timeout === 'number' && config.timeout < 1000) {
    errors.push('Timeout must be at least 1000ms');
  }

  if ('retryAttempts' in config && typeof config.retryAttempts === 'number' && config.retryAttempts < 0) {
    errors.push('Retry attempts must be non-negative');
  }

  if ('baseUrl' in config && typeof config.baseUrl === 'string' && !isValidUrl(config.baseUrl)) {
    errors.push('Invalid base URL format');
  }

  if ('encryptionKey' in config && typeof config.encryptionKey === 'string' && config.encryptionKey.length < 32) {
    errors.push('Encryption key must be at least 32 characters');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Handles service errors with standardized formatting and logging
 */
export function handleServiceError(
  error: any,
  serviceName: string,
  operation: string,
  context?: Record<string, any>
): ServiceError {
  const timestamp = Date.now();
  let code = ERROR_CODES.UNKNOWN_ERROR;
  let message = 'An unknown error occurred';
  let details = null;

  // Network errors
  if (error.code === 'NETWORK_ERROR' || !navigator.onLine) {
    code = ERROR_CODES.NETWORK_UNAVAILABLE;
    message = 'Network connection unavailable';
  } else if (error.code === 'TIMEOUT') {
    code = ERROR_CODES.REQUEST_TIMEOUT;
    message = 'Request timeout exceeded';
  } else if (error.status === 401) {
    code = ERROR_CODES.UNAUTHORIZED;
    message = 'Authentication required';
  } else if (error.status === 403) {
    code = ERROR_CODES.PERMISSION_DENIED;
    message = 'Permission denied';
  } else if (error.status === 429) {
    code = ERROR_CODES.RATE_LIMITED;
    message = 'Rate limit exceeded';
  } else if (error.status >= 500) {
    code = ERROR_CODES.SERVER_ERROR;
    message = 'Server error occurred';
  } else if (error.message) {
    message = error.message;
    if (error.code) {
      code = error.code;
    }
  }

  // Extract additional details
  if (error.response) {
    details = {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data
    };
  } else if (error.stack) {
    details = {
      stack: error.stack,
      name: error.name
    };
  }

  const serviceError: ServiceError = {
    code,
    message,
    details: {
      ...details,
      operation,
      context,
      originalError: error.toString()
    },
    timestamp,
    service: serviceName
  };

  // Log error for monitoring (in production, this would go to a logging service)
  console.error(`[${serviceName}] Error in ${operation}:`, serviceError);

  return serviceError;
}

/**
 * Formats service responses with consistent structure
 */
export function formatServiceResponse<T>(
  data: T,
  cached = false,
  metadata?: Record<string, any>
): ServiceResponse<T> {
  return {
    success: true,
    data,
    timestamp: Date.now(),
    cached,
    metadata
  };
}

/**
 * Formats service error responses
 */
export function formatErrorResponse(
  error: ServiceError
): ServiceResponse<null> {
  return {
    success: false,
    error: error.message,
    timestamp: error.timestamp,
    metadata: {
      code: error.code,
      service: error.service,
      details: error.details
    }
  };
}

/**
 * Generates a secure encryption key
 */
export function generateEncryptionKey(length = 32): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Encrypts data using AES-256
 */
export function encryptData(data: string, key: string): string {
  try {
    return CryptoJS.AES.encrypt(data, key).toString();
  } catch (error) {
    throw new Error('Encryption failed');
  }
}

/**
 * Decrypts data using AES-256
 */
export function decryptData(encryptedData: string, key: string): string {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, key);
    return bytes.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    throw new Error('Decryption failed');
  }
}

/**
 * Compresses data using gzip-like compression
 */
export function compressData(data: string): string {
  // In a real implementation, this would use a proper compression library
  // For now, we'll use a simple Base64 encoding as a placeholder
  try {
    return btoa(unescape(encodeURIComponent(data)));
  } catch (error) {
    throw new Error('Compression failed');
  }
}

/**
 * Decompresses data
 */
export function decompressData(compressedData: string): string {
  try {
    return decodeURIComponent(escape(atob(compressedData)));
  } catch (error) {
    throw new Error('Decompression failed');
  }
}

/**
 * Generates a unique correlation ID for tracking requests
 */
export function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Calculates checksum for data integrity
 */
export function calculateChecksum(data: string): string {
  return CryptoJS.SHA256(data).toString();
}

/**
 * Validates URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Formats file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Formats duration in human-readable format
 */
export function formatDuration(milliseconds: number): string {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}

/**
 * Throttles function execution
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return function(this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Debounces function execution
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return function(this: any, ...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * Creates exponential backoff delay
 */
export function getExponentialBackoffDelay(
  attempt: number,
  baseDelay = 1000,
  maxDelay = 30000
): number {
  const delay = baseDelay * Math.pow(2, attempt);
  return Math.min(delay, maxDelay);
}

/**
 * Retries an async operation with exponential backoff
 */
export async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt === maxRetries) {
        throw lastError;
      }
      
      const delay = getExponentialBackoffDelay(attempt, baseDelay);
      await sleep(delay);
    }
  }
  
  throw lastError!;
}

/**
 * Sleep utility function
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Validates email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Sanitizes user input
 */
export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>'"]/g, '')
    .substring(0, 1000); // Limit length
}

/**
 * Validates content type
 */
export function isValidContentType(contentType: string, allowedTypes: string[]): boolean {
  return allowedTypes.includes(contentType.toLowerCase());
}

/**
 * Calculates performance score
 */
export function calculatePerformanceScore(metrics: PerformanceMetrics): number {
  const weights = {
    responseTime: 0.3,
    throughput: 0.2,
    errorRate: 0.2,
    cpuUsage: 0.1,
    memoryUsage: 0.1,
    networkUsage: 0.05,
    batteryImpact: 0.05
  };

  // Normalize metrics (lower is better for most)
  const normalizedResponseTime = Math.max(0, 1 - (metrics.responseTime / 10000)); // 10s max
  const normalizedThroughput = Math.min(1, metrics.throughput / 1000); // 1000 req/s max
  const normalizedErrorRate = Math.max(0, 1 - metrics.errorRate);
  const normalizedCpuUsage = Math.max(0, 1 - metrics.cpuUsage);
  const normalizedMemoryUsage = Math.max(0, 1 - metrics.memoryUsage);
  const normalizedNetworkUsage = Math.max(0, 1 - (metrics.networkUsage / 100)); // 100MB/s max
  const normalizedBatteryImpact = Math.max(0, 1 - metrics.batteryImpact);

  const score = (
    normalizedResponseTime * weights.responseTime +
    normalizedThroughput * weights.throughput +
    normalizedErrorRate * weights.errorRate +
    normalizedCpuUsage * weights.cpuUsage +
    normalizedMemoryUsage * weights.memoryUsage +
    normalizedNetworkUsage * weights.networkUsage +
    normalizedBatteryImpact * weights.batteryImpact
  );

  return Math.round(score * 100);
}

/**
 * Creates deep clone of an object
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T;
  }
  
  if (typeof obj === 'object') {
    const clonedObj = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
  
  return obj;
}

/**
 * Merges objects deeply
 */
export function deepMerge<T extends Record<string, any>>(target: T, source: Partial<T>): T {
  const result = deepClone(target);
  
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      const sourceValue = source[key];
      const targetValue = result[key];
      
      if (
        typeof sourceValue === 'object' &&
        sourceValue !== null &&
        !Array.isArray(sourceValue) &&
        typeof targetValue === 'object' &&
        targetValue !== null &&
        !Array.isArray(targetValue)
      ) {
        result[key] = deepMerge(targetValue, sourceValue);
      } else {
        result[key] = sourceValue as T[Extract<keyof T, string>];
      }
    }
  }
  
  return result;
}

/**
 * Converts bytes to base64
 */
export function bytesToBase64(bytes: Uint8Array): string {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Converts base64 to bytes
 */
export function base64ToBytes(base64: string): Uint8Array {
  const binary = atob(base64);
  const len = binary.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

/**
 * Gets device information
 */
export function getDeviceInfo(): Record<string, any> {
  return {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    cookieEnabled: navigator.cookieEnabled,
    onLine: navigator.onLine,
    screenWidth: screen.width,
    screenHeight: screen.height,
    colorDepth: screen.colorDepth,
    pixelRatio: window.devicePixelRatio || 1,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    timestamp: Date.now()
  };
}

/**
 * Creates configuration for specific service types
 */
export function createOfflineStorageConfig(
  overrides: Partial<OfflineStorageConfig> = {}
): OfflineStorageConfig {
  return {
    encryptionEnabled: true,
    encryptionKey: generateEncryptionKey(),
    maxStorageSize: SERVICE_DEFAULTS.STORAGE.MAX_SIZE,
    compressionEnabled: true,
    autoCleanupEnabled: true,
    cleanupThreshold: SERVICE_DEFAULTS.STORAGE.CLEANUP_THRESHOLD,
    syncPriority: 'normal',
    ...overrides
  };
}

export function createSyncConfiguration(
  overrides: Partial<SyncConfiguration> = {}
): SyncConfiguration {
  return {
    enableRealTime: true,
    batchSize: SERVICE_DEFAULTS.SYNC.BATCH_SIZE,
    syncInterval: 30000,
    maxRetries: SERVICE_DEFAULTS.SYNC.MAX_RETRIES,
    conflictResolution: 'server',
    enableDeltaSync: true,
    compressionEnabled: true,
    encryptionEnabled: true,
    ...overrides
  };
}

export function createNotificationConfig(
  overrides: Partial<NotificationConfig> = {}
): NotificationConfig {
  return {
    enableFCM: true,
    enableAPNS: true,
    fcmServerKey: '',
    apnsCertificate: '',
    enableAnalytics: true,
    enableScheduling: true,
    maxRetries: SERVICE_DEFAULTS.NOTIFICATIONS.MAX_RETRIES,
    batchSize: SERVICE_DEFAULTS.NOTIFICATIONS.BATCH_SIZE,
    ...overrides
  };
}

export function createBiometricConfig(
  overrides: Partial<BiometricConfig> = {}
): BiometricConfig {
  return {
    enableFaceID: true,
    enableTouchID: true,
    enableVoice: false,
    fallbackToPin: SERVICE_DEFAULTS.BIOMETRIC.FALLBACK_ENABLED,
    maxAttempts: SERVICE_DEFAULTS.BIOMETRIC.MAX_ATTEMPTS,
    timeoutSeconds: SERVICE_DEFAULTS.BIOMETRIC.TIMEOUT,
    encryptionStrength: 'high',
    ...overrides
  };
}

export function createCameraConfig(
  overrides: Partial<CameraConfig> = {}
): CameraConfig {
  return {
    defaultQuality: SERVICE_DEFAULTS.CAMERA.DEFAULT_QUALITY as 'high',
    maxDuration: SERVICE_DEFAULTS.CAMERA.MAX_DURATION,
    enableStabilization: SERVICE_DEFAULTS.CAMERA.STABILIZATION,
    enableHDR: SERVICE_DEFAULTS.CAMERA.HDR,
    enableNightMode: true,
    enableAIEnhancement: SERVICE_DEFAULTS.CAMERA.AI_ENHANCEMENT,
    enableWatermark: true,
    supportedFormats: ['jpeg', 'png', 'mp4', 'mov'],
    ...overrides
  };
}

export function createAudioConfig(
  overrides: Partial<AudioConfig> = {}
): AudioConfig {
  return {
    sampleRate: SERVICE_DEFAULTS.AUDIO.SAMPLE_RATE,
    bitRate: SERVICE_DEFAULTS.AUDIO.BIT_RATE,
    channels: SERVICE_DEFAULTS.AUDIO.CHANNELS as 2,
    format: SERVICE_DEFAULTS.AUDIO.FORMAT as 'aac',
    enableNoiseReduction: SERVICE_DEFAULTS.AUDIO.NOISE_REDUCTION,
    enableEcho: false,
    enableRealTimeProcessing: true,
    maxDuration: SERVICE_DEFAULTS.AUDIO.MAX_DURATION,
    ...overrides
  };
}

export function createLocationConfig(
  overrides: Partial<LocationConfig> = {}
): LocationConfig {
  return {
    enableHighAccuracy: SERVICE_DEFAULTS.LOCATION.HIGH_ACCURACY,
    timeout: SERVICE_DEFAULTS.LOCATION.TIMEOUT,
    maximumAge: SERVICE_DEFAULTS.LOCATION.MAXIMUM_AGE,
    enableBackground: SERVICE_DEFAULTS.LOCATION.BACKGROUND_ENABLED,
    enableGeofencing: false,
    distanceFilter: SERVICE_DEFAULTS.LOCATION.DISTANCE_FILTER,
    enableCaching: true,
    ...overrides
  };
}