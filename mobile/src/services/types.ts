/**
 * Mobile Services Types - TypeScript Definitions
 * 
 * Comprehensive type definitions for mobile services
 * used throughout the Ainflue mobile application.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Storage Types
export interface StorageOptions {
  encrypt?: boolean;
  compress?: boolean;
  ttl?: number; // Time to live in seconds
}

export interface StorageItem<T = any> {
  key: string;
  value: T;
  timestamp: number;
  size: number;
  encrypted: boolean;
  compressed: boolean;
  expiresAt?: number;
}

// Sync Types
export interface SyncQueueItem {
  id: string;
  type: 'create' | 'update' | 'delete';
  collection: string;
  data: any;
  timestamp: number;
  retryCount: number;
  priority: 'low' | 'medium' | 'high';
  dependencies?: string[];
}

export interface SyncConflict {
  id: string;
  localData: any;
  remoteData: any;
  conflictFields: string[];
  resolution?: 'local' | 'remote' | 'merge';
}

export interface SyncProgress {
  total: number;
  completed: number;
  failed: number;
  currentItem?: string;
}

// Biometric Types
export interface BiometricOptions {
  promptMessage?: string;
  fallbackEnabled?: boolean;
  requireConfirmation?: boolean;
  allowDeviceCredentials?: boolean;
}

export interface BiometricResult {
  success: boolean;
  biometryType?: 'TouchID' | 'FaceID' | 'Fingerprint' | 'Iris';
  error?: string;
  userCancel?: boolean;
  userFallback?: boolean;
}

// Camera Types
export interface CameraPermissions {
  camera: boolean;
  microphone: boolean;
  storage: boolean;
}

export interface CameraConfiguration {
  quality: 'low' | 'medium' | 'high' | '4k';
  flashMode: 'auto' | 'on' | 'off' | 'torch';
  focusMode: 'auto' | 'manual' | 'continuous';
  whiteBalance: 'auto' | 'cloudy' | 'daylight' | 'fluorescent' | 'incandescent';
  orientation: 'portrait' | 'landscape';
  stabilization: boolean;
  geotagging: boolean;
}

export interface MediaMetadata {
  width: number;
  height: number;
  duration?: number;
  fileSize: number;
  format: string;
  orientation: number;
  location?: {
    latitude: number;
    longitude: number;
    altitude?: number;
  };
  timestamp: Date;
  deviceInfo: {
    make: string;
    model: string;
    os: string;
  };
}

export interface CapturedMedia {
  uri: string;
  type: 'image' | 'video';
  metadata: MediaMetadata;
  thumbnail?: string;
}

// Audio Types
export interface AudioConfiguration {
  sampleRate: 44100 | 48000 | 96000;
  bitRate: 128 | 256 | 320 | 1411; // kbps
  channels: 1 | 2;
  format: 'mp3' | 'wav' | 'aac' | 'flac';
  quality: 'low' | 'medium' | 'high' | 'lossless';
  noiseReduction: boolean;
  autoGainControl: boolean;
  echoCancellation: boolean;
}

export interface AudioRecording {
  uri: string;
  duration: number;
  fileSize: number;
  format: string;
  metadata: {
    sampleRate: number;
    bitRate: number;
    channels: number;
    peakLevel: number;
    averageLevel: number;
    timestamp: Date;
  };
  waveform?: number[];
}

export interface AudioLevel {
  peak: number;
  average: number;
  timestamp: number;
}

// Location Types
export interface LocationOptions {
  accuracy: 'low' | 'balanced' | 'high' | 'best';
  timeout: number;
  maximumAge: number;
  enableHighAccuracy: boolean;
  distanceFilter: number;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy: number;
  altitudeAccuracy?: number;
  heading?: number;
  speed?: number;
  timestamp: Date;
  address?: {
    street?: string;
    city?: string;
    region?: string;
    country?: string;
    postalCode?: string;
  };
}

export interface GeofenceRegion {
  id: string;
  latitude: number;
  longitude: number;
  radius: number;
  notifyOnEntry: boolean;
  notifyOnExit: boolean;
}

// Push Notification Types
export interface PushNotificationConfig {
  senderId?: string;
  appId?: string;
  apiKey?: string;
  vapidKey?: string;
}

export interface NotificationPayload {
  title: string;
  body: string;
  badge?: number;
  sound?: string;
  category?: string;
  userInfo?: Record<string, any>;
  image?: string;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  id: string;
  title: string;
  destructive?: boolean;
  authenticationRequired?: boolean;
  foreground?: boolean;
  icon?: string;
}

export interface NotificationPermissions {
  alert: boolean;
  badge: boolean;
  sound: boolean;
  provisional?: boolean;
  announcement?: boolean;
  carPlay?: boolean;
  criticalAlert?: boolean;
}

// API Types
export interface APIRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  endpoint: string;
  data?: any;
  headers?: Record<string, string>;
  timeout?: number;
  retryCount?: number;
}

export interface APIResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  timestamp: Date;
}

export interface APIError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
  timestamp: Date;
}

export interface NetworkStatus {
  isConnected: boolean;
  connectionType: 'wifi' | 'cellular' | 'ethernet' | 'other' | 'none';
  isInternetReachable: boolean;
  strength?: number;
}

// Service Events
export interface ServiceEvent<T = any> {
  type: string;
  data: T;
  timestamp: Date;
  source: string;
}

export type ServiceEventListener<T = any> = (event: ServiceEvent<T>) => void;

// Base Service Interface
export interface BaseService {
  initialize(): Promise<void>;
  destroy(): Promise<void>;
  isInitialized(): boolean;
  addEventListener<T>(type: string, listener: ServiceEventListener<T>): void;
  removeEventListener<T>(type: string, listener: ServiceEventListener<T>): void;
  emit<T>(type: string, data: T): void;
}

// Device Information
export interface DeviceInfo {
  platform: 'ios' | 'android';
  version: string;
  buildNumber: string;
  model: string;
  manufacturer: string;
  deviceId: string;
  systemVersion: string;
  appVersion: string;
  bundleId: string;
  isEmulator: boolean;
  hasNotch: boolean;
  screenDimensions: {
    width: number;
    height: number;
    scale: number;
  };
  storage: {
    total: number;
    free: number;
    used: number;
  };
  memory: {
    total: number;
    used: number;
  };
  battery: {
    level: number;
    isCharging: boolean;
    lowPowerMode: boolean;
  };
}

// Security Types
export interface SecurityToken {
  value: string;
  type: 'bearer' | 'basic' | 'api_key';
  expiresAt?: Date;
  refreshToken?: string;
  scope?: string[];
}

export interface EncryptionConfig {
  algorithm: 'AES' | 'RSA';
  keySize: 128 | 256 | 512 | 1024 | 2048 | 4096;
  iv?: string;
  salt?: string;
}

// Background Task Types
export interface BackgroundTask {
  id: string;
  type: 'sync' | 'upload' | 'download' | 'processing';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  startTime: Date;
  endTime?: Date;
  data: any;
  result?: any;
  error?: string;
}