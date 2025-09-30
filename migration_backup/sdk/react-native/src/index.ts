/**
 * Ainflue React Native SDK - Main Entry Point
 * 
 * Enterprise mobile SDK with multi-expert design:
 * - Lead Dev IA: AI-powered mobile content processing
 * - Backend Senior: Robust mobile API architecture
 * - ML Engineer: On-device ML capabilities
 * - Sécurité: Mobile security and secure storage
 * - DevOps: Mobile performance monitoring
 * - Audio Engineer: Mobile audio processing
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright 2025 Fahed Mlaiel. All rights reserved.
 */

// Core client exports
export { AinflueClient } from './client';
export { AinflueProvider, useAinflue } from './provider';

// Platform-specific clients
export { AndroidClient } from './android-client';
export { IOSClient } from './ios-client';
export { WebClient } from './web-client';
export { NativeClient } from './native-client';

// React hooks
export {
  useUpload,
  useAnalysis,
  useProtection,
  useAuth,
  useUser,
  useAnalytics,
  useNetworkInfo,
  usePermissions
} from './hooks';

// React components
export {
  AinflueUploader,
  AinfluePlayer,
  AinflueAnalytics,
  AinflueProtection,
  AinflueAuth
} from './components';

// Storage and caching
export { StorageManager } from './storage-manager';
export { NetworkManager } from './network-manager';

// Types and interfaces
export * from './types';
export * from './interfaces';

// Utilities
export { Logger } from './utils/logger';
export { EventEmitter } from './utils/event-emitter';
export { PermissionManager } from './utils/permission-manager';
export { DeviceInfo } from './utils/device-info';

// Constants
export * from './constants';

// Configuration
export type { AinflueConfig } from './config';
export { createDefaultConfig } from './config';

// Error handling
export {
  AinflueError,
  NetworkError,
  PermissionError,
  StorageError,
  UploadError
} from './errors';

// Version and metadata
export const SDK_VERSION = '1.0.0';
export const PLATFORM = 'react-native';

// Expert roles implemented for mobile
export const MOBILE_EXPERT_ROLES = [
  'Lead Dev IA',         // AI mobile orchestration
  'Backend Senior',      // Mobile API architecture
  'ML Engineer',         // On-device ML
  'Sécurité',           // Mobile security
  'DevOps',             // Mobile monitoring
  'Audio Engineer'      // Mobile audio processing
] as const;

// Mobile-specific features
export const MOBILE_FEATURES = {
  cameraIntegration: true,
  audioRecording: true,
  backgroundUpload: true,
  offlineSync: true,
  biometricAuth: true,
  pushNotifications: true,
  fileSystemAccess: true,
  deviceMetrics: true
} as const;