/**
 * Mobile Services Index - Professional Service Layer Exports
 * 
 * Centralized exports for all mobile-optimized service implementations
 * designed for professional content creation and cross-platform operations.
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

// Core Mobile API Service
export { default as MobileAPIService } from './MobileAPIService';

// Storage and Synchronization Services
export { default as OfflineStorageService } from './OfflineStorageService';
export { default as SyncService } from './SyncService';

// Notification and Communication Services
export { default as PushNotificationService } from './PushNotificationService';

// Security and Authentication Services
export { default as BiometricService } from './BiometricService';

// Media Capture and Processing Services
export { default as CameraService } from './CameraService';
export { default as AudioService } from './AudioService';

// Device and Location Services
export { default as LocationService } from './LocationService';

// Service Type Definitions
export type {
  MobileAPIConfig,
  OfflineStorageConfig,
  SyncConfiguration,
  NotificationConfig,
  BiometricConfig,
  CameraConfig,
  AudioConfig,
  LocationConfig,
  ServiceResponse,
  ServiceError
} from './types';

// Service Utilities and Helpers
export {
  createMobileServiceConfig,
  validateServiceConfiguration,
  handleServiceError,
  formatServiceResponse
} from './utils';

// Service Constants
export {
  SERVICE_ENDPOINTS,
  STORAGE_KEYS,
  NOTIFICATION_TYPES,
  MEDIA_QUALITY_PRESETS,
  SYNC_INTERVALS
} from './constants';