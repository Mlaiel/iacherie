/**
 * Mobile Services Type Definitions - Professional Service Interface Types
 * 
 * Comprehensive type definitions for all mobile service configurations,
 * responses, and data structures used across the professional content
 * creation and cross-platform operations ecosystem.
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

// Common Service Types
export interface ServiceResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
  cached?: boolean;
  metadata?: Record<string, any>;
}

export interface ServiceError {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
  service: string;
}

// Mobile API Service Configuration
export interface MobileAPIConfig {
  baseUrl: string;
  apiKey: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableCaching: boolean;
  enableOfflineQueue: boolean;
  encryptionKey: string;
}

// Offline Storage Service Configuration
export interface OfflineStorageConfig {
  encryptionEnabled: boolean;
  encryptionKey: string;
  maxStorageSize: number;
  compressionEnabled: boolean;
  autoCleanupEnabled: boolean;
  cleanupThreshold: number;
  syncPriority: 'low' | 'normal' | 'high';
}

export interface StorageItem {
  key: string;
  value: any;
  timestamp: number;
  ttl?: number;
  encrypted: boolean;
  compressed: boolean;
  size: number;
  priority: number;
}

// Synchronization Service Configuration
export interface SyncConfiguration {
  enableRealTime: boolean;
  batchSize: number;
  syncInterval: number;
  maxRetries: number;
  conflictResolution: 'server' | 'client' | 'merge' | 'manual';
  enableDeltaSync: boolean;
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
}

export interface SyncItem {
  id: string;
  type: 'content' | 'metadata' | 'preferences' | 'analytics';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  checksum: string;
  priority: number;
  retryCount: number;
}

// Push Notification Service Configuration
export interface NotificationConfig {
  enableFCM: boolean;
  enableAPNS: boolean;
  fcmServerKey: string;
  apnsCertificate: string;
  enableAnalytics: boolean;
  enableScheduling: boolean;
  maxRetries: number;
  batchSize: number;
}

export interface NotificationPayload {
  title: string;
  body: string;
  icon?: string;
  image?: string;
  badge?: number;
  sound?: string;
  category?: string;
  data?: Record<string, any>;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  id: string;
  title: string;
  icon?: string;
  foreground?: boolean;
  destructive?: boolean;
}

// Biometric Service Configuration
export interface BiometricConfig {
  enableFaceID: boolean;
  enableTouchID: boolean;
  enableVoice: boolean;
  fallbackToPin: boolean;
  maxAttempts: number;
  timeoutSeconds: number;
  encryptionStrength: 'standard' | 'high' | 'military';
}

export interface BiometricResult {
  success: boolean;
  biometricType: 'faceID' | 'touchID' | 'voice' | 'pin';
  confidence: number;
  timestamp: number;
  deviceId: string;
  error?: string;
}

// Camera Service Configuration
export interface CameraConfig {
  defaultQuality: 'low' | 'medium' | 'high' | 'ultra';
  maxDuration: number;
  enableStabilization: boolean;
  enableHDR: boolean;
  enableNightMode: boolean;
  enableAIEnhancement: boolean;
  enableWatermark: boolean;
  supportedFormats: string[];
}

export interface CameraCapture {
  id: string;
  uri: string;
  type: 'photo' | 'video';
  format: string;
  quality: string;
  duration?: number;
  size: number;
  dimensions: { width: number; height: number };
  metadata: CameraMetadata;
  aiAnalysis?: AIAnalysisResult;
}

export interface CameraMetadata {
  timestamp: number;
  location?: GeolocationPosition;
  device: string;
  settings: Record<string, any>;
  fingerprint?: string;
}

// Audio Service Configuration
export interface AudioConfig {
  sampleRate: number;
  bitRate: number;
  channels: 1 | 2;
  format: 'wav' | 'mp3' | 'aac' | 'flac';
  enableNoiseReduction: boolean;
  enableEcho: boolean;
  enableRealTimeProcessing: boolean;
  maxDuration: number;
}

export interface AudioRecording {
  id: string;
  uri: string;
  format: string;
  duration: number;
  size: number;
  sampleRate: number;
  bitRate: number;
  channels: number;
  metadata: AudioMetadata;
  fingerprint?: string;
  aiAnalysis?: AIAnalysisResult;
}

export interface AudioMetadata {
  timestamp: number;
  device: string;
  settings: AudioConfig;
  location?: GeolocationPosition;
  noiseLevel: number;
  qualityScore: number;
}

// Location Service Configuration
export interface LocationConfig {
  enableHighAccuracy: boolean;
  timeout: number;
  maximumAge: number;
  enableBackground: boolean;
  enableGeofencing: boolean;
  distanceFilter: number;
  enableCaching: boolean;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy: number;
  timestamp: number;
  address?: AddressData;
  metadata?: LocationMetadata;
}

export interface AddressData {
  street?: string;
  city?: string;
  state?: string;
  country?: string;
  postalCode?: string;
  formatted: string;
}

export interface LocationMetadata {
  provider: string;
  speed?: number;
  heading?: number;
  cached: boolean;
  batteryOptimized: boolean;
}

// AI Analysis Results
export interface AIAnalysisResult {
  contentType: 'image' | 'video' | 'audio' | 'text';
  confidence: number;
  tags: string[];
  description: string;
  entities: AIEntity[];
  emotions?: EmotionAnalysis[];
  quality: QualityAssessment;
  protection: ProtectionAnalysis;
}

export interface AIEntity {
  type: 'person' | 'object' | 'scene' | 'brand' | 'location';
  name: string;
  confidence: number;
  boundingBox?: BoundingBox;
}

export interface EmotionAnalysis {
  emotion: string;
  confidence: number;
  intensity: number;
}

export interface QualityAssessment {
  overall: number;
  technical: number;
  aesthetic: number;
  composition: number;
  recommendations: string[];
}

export interface ProtectionAnalysis {
  isOriginal: boolean;
  confidence: number;
  similarContent: SimilarContent[];
  fingerprint: string;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface SimilarContent {
  platform: string;
  url: string;
  similarity: number;
  timestamp: number;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// Content Protection Types
export interface ContentFingerprint {
  audioFingerprint?: string;
  videoFingerprint?: string;
  imageFingerprint?: string;
  textFingerprint?: string;
  metadata: FingerprintMetadata;
}

export interface FingerprintMetadata {
  algorithm: string;
  version: string;
  timestamp: number;
  confidence: number;
  features: string[];
}

// Monetization Types
export interface MonetizationConfig {
  enableRevenuTracking: boolean;
  enableAutomaticLicensing: boolean;
  defaultLicenseType: string;
  revenueSharePercentage: number;
  paymentThreshold: number;
  enablePredictiveAnalytics: boolean;
}

export interface RevenueData {
  totalRevenue: number;
  periodRevenue: number;
  predictedRevenue: number;
  sources: RevenueSource[];
  trends: RevenueTrend[];
}

export interface RevenueSource {
  platform: string;
  amount: number;
  percentage: number;
  growthRate: number;
}

export interface RevenueTrend {
  period: string;
  revenue: number;
  growth: number;
  prediction: number;
}

// Collaboration Types
export interface CollaborationConfig {
  enableRealTimeEditing: boolean;
  maxCollaborators: number;
  enableVersionControl: boolean;
  enableComments: boolean;
  enableLiveChat: boolean;
  permissionLevels: string[];
}

export interface CollaborationSession {
  id: string;
  projectId: string;
  participants: Participant[];
  status: 'active' | 'paused' | 'completed';
  createdAt: number;
  updatedAt: number;
  metadata: SessionMetadata;
}

export interface Participant {
  userId: string;
  role: 'owner' | 'editor' | 'viewer' | 'commenter';
  joinedAt: number;
  lastActive: number;
  permissions: string[];
}

export interface SessionMetadata {
  totalChanges: number;
  activeTime: number;
  messagesCount: number;
  filesShared: number;
}

// Event System Types
export interface ServiceEvent {
  type: string;
  source: string;
  data: any;
  timestamp: number;
  correlationId: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
}

// Performance Monitoring Types
export interface PerformanceMetrics {
  responseTime: number;
  throughput: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
  networkUsage: number;
  batteryImpact: number;
}

// Security Types
export interface SecurityContext {
  userId: string;
  deviceId: string;
  sessionId: string;
  permissions: string[];
  riskScore: number;
  lastVerified: number;
}

export interface EncryptionConfig {
  algorithm: 'AES-256' | 'ChaCha20' | 'RSA-2048';
  keyDerivation: 'PBKDF2' | 'Argon2' | 'scrypt';
  iterations: number;
  saltLength: number;
}