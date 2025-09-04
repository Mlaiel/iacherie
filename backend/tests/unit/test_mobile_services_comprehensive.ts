/**
 * Mobile Services Unit Tests - Professional Testing Suite
 * 
 * Comprehensive unit tests for all mobile services including offline storage,
 * synchronization, notifications, biometrics, camera, audio, and location services.
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

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';

// Import all mobile services
import OfflineStorageService from '../mobile/src/services/OfflineStorageService';
import SyncService from '../mobile/src/services/SyncService';
import PushNotificationService from '../mobile/src/services/PushNotificationService';
import BiometricService from '../mobile/src/services/BiometricService';
import CameraService from '../mobile/src/services/CameraService';
import AudioService from '../mobile/src/services/AudioService';
import LocationService from '../mobile/src/services/LocationService';

// Import types and utilities
import {
  OfflineStorageConfig,
  SyncConfiguration,
  NotificationConfig,
  BiometricConfig,
  CameraConfig,
  AudioConfig,
  LocationConfig
} from '../mobile/src/services/types';

// Mock AsyncStorage
const mockAsyncStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  getAllKeys: jest.fn(),
  multiRemove: jest.fn()
};

// Mock Navigator APIs
const mockNavigator = {
  onLine: true,
  geolocation: {
    getCurrentPosition: jest.fn(),
    watchPosition: jest.fn(() => 1),
    clearWatch: jest.fn()
  },
  mediaDevices: {
    getUserMedia: jest.fn()
  }
};

// Mock global objects
global.navigator = mockNavigator as any;
global.AsyncStorage = mockAsyncStorage as any;

describe('Mobile Services Professional Test Suite', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Setup default mock responses
    mockAsyncStorage.getItem.mockResolvedValue(null);
    mockAsyncStorage.setItem.mockResolvedValue(undefined);
    mockAsyncStorage.removeItem.mockResolvedValue(undefined);
    mockAsyncStorage.clear.mockResolvedValue(undefined);
    mockAsyncStorage.getAllKeys.mockResolvedValue([]);
    
    mockNavigator.geolocation.getCurrentPosition.mockImplementation((success) => {
      success({
        coords: {
          latitude: 40.7128,
          longitude: -74.0060,
          accuracy: 10,
          altitude: null,
          altitudeAccuracy: null,
          heading: null,
          speed: null
        },
        timestamp: Date.now()
      });
    });
    
    mockNavigator.mediaDevices.getUserMedia.mockResolvedValue({
      getTracks: () => [{ stop: jest.fn() }]
    } as any);
  });

  afterEach(() => {
    // Cleanup services
    jest.restoreAllMocks();
  });

  describe('OfflineStorageService', () => {
    let storageService: OfflineStorageService;
    
    beforeEach(() => {
      const config: OfflineStorageConfig = {
        encryptionEnabled: true,
        encryptionKey: 'test-encryption-key-32-characters',
        maxStorageSize: 100 * 1024 * 1024, // 100MB
        compressionEnabled: true,
        autoCleanupEnabled: true,
        cleanupThreshold: 0.9,
        syncPriority: 'normal'
      };
      storageService = OfflineStorageService.getInstance(config);
    });

    test('should initialize with default configuration', () => {
      expect(storageService).toBeDefined();
    });

    test('should store and retrieve data successfully', async () => {
      const testData = { message: 'Hello World', timestamp: Date.now() };
      
      // Store data
      const storeResult = await storageService.store('test-key', testData);
      expect(storeResult.success).toBe(true);
      
      // Retrieve data
      const retrieveResult = await storageService.retrieve('test-key');
      expect(retrieveResult.success).toBe(true);
      expect(retrieveResult.data).toEqual(testData);
    });

    test('should handle storage capacity limits', async () => {
      const largeData = 'x'.repeat(200 * 1024 * 1024); // 200MB
      
      const result = await storageService.store('large-data', largeData);
      expect(result.success).toBe(false);
      expect(result.error).toContain('storage space');
    });

    test('should store content with fingerprint protection', async () => {
      const contentData = { title: 'Test Content', body: 'Content body' };
      const fingerprint = {
        audioFingerprint: 'audio-fp-123',
        videoFingerprint: 'video-fp-456',
        metadata: {
          algorithm: 'test-algo',
          version: '1.0',
          timestamp: Date.now(),
          confidence: 0.95,
          features: ['audio', 'video']
        }
      };
      
      const result = await storageService.storeContent('content-123', contentData, fingerprint);
      expect(result.success).toBe(true);
      
      const retrieveResult = await storageService.retrieveContent('content-123');
      expect(retrieveResult.success).toBe(true);
      expect(retrieveResult.data.content).toEqual(contentData);
      expect(retrieveResult.data.fingerprint).toEqual(fingerprint);
    });

    test('should perform cleanup when storage is full', async () => {
      // Fill storage with test data
      for (let i = 0; i < 10; i++) {
        await storageService.store(`test-${i}`, `data-${i}`, { priority: i });
      }
      
      const cleanupResult = await storageService.cleanup();
      expect(cleanupResult.success).toBe(true);
      expect(cleanupResult.data.removedItems).toBeGreaterThanOrEqual(0);
    });

    test('should handle sync queue operations', async () => {
      const syncItem = { type: 'content', action: 'create', data: { id: '123' } };
      
      const storeResult = await storageService.storeSyncItem(syncItem, 5);
      expect(storeResult.success).toBe(true);
      
      const queueResult = await storageService.getSyncQueue();
      expect(queueResult.success).toBe(true);
      expect(queueResult.data.length).toBeGreaterThan(0);
    });
  });

  describe('SyncService', () => {
    let syncService: SyncService;
    
    beforeEach(() => {
      const config: SyncConfiguration = {
        enableRealTime: true,
        batchSize: 10,
        syncInterval: 30000,
        maxRetries: 3,
        conflictResolution: 'server',
        enableDeltaSync: true,
        compressionEnabled: true,
        encryptionEnabled: true
      };
      syncService = SyncService.getInstance(config);
    });

    test('should add items to sync queue', async () => {
      const result = await syncService.addToSyncQueue(
        'content',
        'create',
        { id: '123', title: 'Test Content' },
        5
      );
      
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(typeof result.data).toBe('string'); // sync ID
    });

    test('should get sync status', async () => {
      const statusResult = await syncService.getSyncStatus();
      
      expect(statusResult.success).toBe(true);
      expect(statusResult.data).toHaveProperty('isOnline');
      expect(statusResult.data).toHaveProperty('queueSize');
      expect(statusResult.data).toHaveProperty('conflictCount');
      expect(statusResult.data).toHaveProperty('lastSync');
    });

    test('should process sync queue', async () => {
      // Add items to queue
      await syncService.addToSyncQueue('content', 'create', { id: '1' }, 1);
      await syncService.addToSyncQueue('metadata', 'update', { id: '2' }, 2);
      
      const processResult = await syncService.processSync();
      expect(processResult.success).toBe(true);
      expect(processResult.data).toHaveProperty('processed');
      expect(processResult.data).toHaveProperty('succeeded');
      expect(processResult.data).toHaveProperty('failed');
    });

    test('should handle conflict resolution', async () => {
      const conflictId = 'conflict-123';
      
      const resolveResult = await syncService.resolveConflict(
        conflictId,
        'server'
      );
      
      // Since conflict doesn't exist, should return error
      expect(resolveResult.success).toBe(false);
      expect(resolveResult.error).toContain('not found');
    });

    test('should force immediate sync', async () => {
      const forceResult = await syncService.forceSync();
      expect(forceResult.success).toBe(true);
      expect(forceResult.data).toHaveProperty('pull');
      expect(forceResult.data).toHaveProperty('push');
    });
  });

  describe('PushNotificationService', () => {
    let notificationService: PushNotificationService;
    
    beforeEach(() => {
      const config: NotificationConfig = {
        enableFCM: true,
        enableAPNS: true,
        fcmServerKey: 'test-fcm-key',
        apnsCertificate: 'test-apns-cert',
        enableAnalytics: true,
        enableScheduling: true,
        maxRetries: 3,
        batchSize: 50
      };
      notificationService = PushNotificationService.getInstance(config);
    });

    test('should send notification successfully', async () => {
      const payload = {
        title: 'Test Notification',
        body: 'This is a test notification',
        icon: 'test-icon',
        data: { key: 'value' }
      };
      
      const result = await notificationService.sendNotification(payload);
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('notificationId');
      expect(result.data).toHaveProperty('estimatedDelivery');
    });

    test('should send template notification', async () => {
      const variables = {
        contentTitle: 'My Amazing Content',
        inviterName: 'John Doe',
        projectName: 'Cool Project'
      };
      
      const result = await notificationService.sendTemplateNotification(
        'content_protected',
        variables
      );
      expect(result.success).toBe(true);
    });

    test('should schedule notification', async () => {
      const payload = {
        title: 'Scheduled Notification',
        body: 'This will be sent later'
      };
      
      const scheduledAt = Date.now() + 60000; // 1 minute from now
      
      const result = await notificationService.scheduleNotification(
        payload,
        scheduledAt,
        { maxRepeats: 1 }
      );
      
      expect(result.success).toBe(true);
      expect(typeof result.data).toBe('string'); // notification ID
    });

    test('should get notification analytics', async () => {
      const analyticsResult = await notificationService.getAnalytics('week');
      
      expect(analyticsResult.success).toBe(true);
      expect(analyticsResult.data).toHaveProperty('sent');
      expect(analyticsResult.data).toHaveProperty('delivered');
      expect(analyticsResult.data).toHaveProperty('opened');
      expect(analyticsResult.data).toHaveProperty('trends');
    });

    test('should register device token', async () => {
      const token = 'test-device-token-123';
      
      const result = await notificationService.registerDeviceToken(token);
      expect(result.success).toBe(true);
    });
  });

  describe('BiometricService', () => {
    let biometricService: BiometricService;
    
    beforeEach(() => {
      const config: BiometricConfig = {
        enableFaceID: true,
        enableTouchID: true,
        enableVoice: false,
        fallbackToPin: true,
        maxAttempts: 5,
        timeoutSeconds: 30,
        encryptionStrength: 'high'
      };
      biometricService = BiometricService.getInstance(config);
    });

    test('should check biometric availability', async () => {
      const availabilityResult = await biometricService.isAvailable();
      
      expect(availabilityResult.success).toBe(true);
      expect(availabilityResult.data).toHaveProperty('available');
      expect(availabilityResult.data).toHaveProperty('capabilities');
      expect(Array.isArray(availabilityResult.data.capabilities)).toBe(true);
    });

    test('should authenticate with biometrics', async () => {
      const authResult = await biometricService.authenticate(
        'Please authenticate to continue'
      );
      
      expect(authResult.success).toBe(true);
      expect(authResult.data).toHaveProperty('success');
      expect(authResult.data).toHaveProperty('biometricType');
      expect(authResult.data).toHaveProperty('confidence');
    });

    test('should enroll biometric data', async () => {
      const enrollResult = await biometricService.enrollBiometric('touchID');
      
      expect(enrollResult.success).toBe(true);
      expect(enrollResult.data).toHaveProperty('enrolled');
      expect(enrollResult.data).toHaveProperty('confidence');
      expect(enrollResult.data).toHaveProperty('backupToken');
    });

    test('should verify backup token', async () => {
      // First enroll to get a backup token
      const enrollResult = await biometricService.enrollBiometric('faceID');
      expect(enrollResult.success).toBe(true);
      
      const backupToken = enrollResult.data.backupToken;
      
      // Then verify the backup token
      const verifyResult = await biometricService.verifyBackupToken(backupToken);
      expect(verifyResult.success).toBe(true);
    });

    test('should get security audit log', async () => {
      const auditResult = await biometricService.getSecurityAuditLog(10);
      
      expect(auditResult.success).toBe(true);
      expect(Array.isArray(auditResult.data)).toBe(true);
    });

    test('should get security context', async () => {
      const contextResult = await biometricService.getSecurityContext();
      
      expect(contextResult.success).toBe(true);
      expect(contextResult.data).toHaveProperty('userId');
      expect(contextResult.data).toHaveProperty('deviceId');
      expect(contextResult.data).toHaveProperty('riskScore');
    });
  });

  describe('CameraService', () => {
    let cameraService: CameraService;
    
    beforeEach(() => {
      const config: CameraConfig = {
        defaultQuality: 'high',
        maxDuration: 300,
        enableStabilization: true,
        enableHDR: true,
        enableNightMode: true,
        enableAIEnhancement: true,
        enableWatermark: true,
        supportedFormats: ['jpeg', 'png', 'mp4']
      };
      cameraService = CameraService.getInstance(config);
    });

    test('should get camera capabilities', async () => {
      const capabilitiesResult = await cameraService.getCapabilities();
      
      expect(capabilitiesResult.success).toBe(true);
      expect(capabilitiesResult.data).toHaveProperty('capabilities');
      expect(capabilitiesResult.data).toHaveProperty('currentConfig');
      expect(capabilitiesResult.data).toHaveProperty('supportedQualities');
    });

    test('should start photo capture session', async () => {
      const sessionResult = await cameraService.startCaptureSession('photo', {
        quality: 'high',
        enableAI: true,
        watermark: true
      });
      
      expect(sessionResult.success).toBe(true);
      expect(typeof sessionResult.data).toBe('string'); // session ID
    });

    test('should capture photo', async () => {
      // Start session first
      await cameraService.startCaptureSession('photo');
      
      const captureResult = await cameraService.capturePhoto({
        flash: 'auto',
        timer: 0
      });
      
      expect(captureResult.success).toBe(true);
      expect(captureResult.data).toHaveProperty('id');
      expect(captureResult.data).toHaveProperty('uri');
      expect(captureResult.data).toHaveProperty('type');
      expect(captureResult.data.type).toBe('photo');
    });

    test('should start video recording session', async () => {
      // Start video session
      await cameraService.startCaptureSession('video');
      
      const recordingResult = await cameraService.startVideoRecording({
        maxDuration: 30000,
        stabilization: true
      });
      
      expect(recordingResult.success).toBe(true);
      expect(typeof recordingResult.data).toBe('string'); // recording ID
    });

    test('should get capture history', async () => {
      const historyResult = await cameraService.getCaptureHistory({
        type: 'photo',
        limit: 10
      });
      
      expect(historyResult.success).toBe(true);
      expect(historyResult.data).toHaveProperty('captures');
      expect(historyResult.data).toHaveProperty('totalCount');
      expect(Array.isArray(historyResult.data.captures)).toBe(true);
    });

    test('should end capture session', async () => {
      // Start and end session
      await cameraService.startCaptureSession('photo');
      
      const endResult = await cameraService.endCaptureSession();
      expect(endResult.success).toBe(true);
      expect(endResult.data).toHaveProperty('sessionId');
      expect(endResult.data).toHaveProperty('captureCount');
    });
  });

  describe('AudioService', () => {
    let audioService: AudioService;
    
    beforeEach(() => {
      const config: AudioConfig = {
        sampleRate: 48000,
        bitRate: 256,
        channels: 2,
        format: 'aac',
        enableNoiseReduction: true,
        enableEcho: false,
        enableRealTimeProcessing: true,
        maxDuration: 600
      };
      audioService = AudioService.getInstance(config);
    });

    test('should get audio capabilities', async () => {
      const capabilitiesResult = await audioService.getCapabilities();
      
      expect(capabilitiesResult.success).toBe(true);
      expect(capabilitiesResult.data).toHaveProperty('capabilities');
      expect(capabilitiesResult.data).toHaveProperty('currentConfig');
      expect(capabilitiesResult.data).toHaveProperty('supportedFormats');
      expect(capabilitiesResult.data).toHaveProperty('processingFeatures');
    });

    test('should start recording session', async () => {
      const sessionResult = await audioService.startRecordingSession({
        quality: 'high',
        enableRealTimeProcessing: true,
        maxDuration: 60000
      });
      
      expect(sessionResult.success).toBe(true);
      expect(typeof sessionResult.data).toBe('string'); // session ID
    });

    test('should start and stop recording', async () => {
      // Start session first
      await audioService.startRecordingSession();
      
      // Start recording
      const startResult = await audioService.startRecording();
      expect(startResult.success).toBe(true);
      
      // Simulate recording for a bit
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Stop recording
      const stopResult = await audioService.stopRecording();
      expect(stopResult.success).toBe(true);
      expect(stopResult.data).toHaveProperty('id');
      expect(stopResult.data).toHaveProperty('uri');
      expect(stopResult.data).toHaveProperty('duration');
    });

    test('should get recording history', async () => {
      const historyResult = await audioService.getRecordingHistory({
        format: 'aac',
        limit: 10
      });
      
      expect(historyResult.success).toBe(true);
      expect(historyResult.data).toHaveProperty('recordings');
      expect(historyResult.data).toHaveProperty('totalCount');
      expect(historyResult.data).toHaveProperty('totalDuration');
    });

    test('should analyze audio quality', async () => {
      // First create a recording
      await audioService.startRecordingSession();
      const recordingResult = await audioService.startRecording();
      await new Promise(resolve => setTimeout(resolve, 100));
      const recording = await audioService.stopRecording();
      
      // Then analyze quality
      const analysisResult = await audioService.analyzeAudioQuality(recording.data.id);
      expect(analysisResult.success).toBe(true);
      expect(analysisResult.data).toHaveProperty('overall');
      expect(analysisResult.data).toHaveProperty('technical');
      expect(analysisResult.data).toHaveProperty('recommendations');
    });

    test('should end recording session', async () => {
      await audioService.startRecordingSession();
      
      const endResult = await audioService.endRecordingSession();
      expect(endResult.success).toBe(true);
      expect(endResult.data).toHaveProperty('sessionId');
      expect(endResult.data).toHaveProperty('recordingCount');
    });
  });

  describe('LocationService', () => {
    let locationService: LocationService;
    
    beforeEach(() => {
      const config: LocationConfig = {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 60000,
        enableBackground: false,
        enableGeofencing: true,
        distanceFilter: 10,
        enableCaching: true
      };
      locationService = LocationService.getInstance(config);
    });

    test('should get current position', async () => {
      const positionResult = await locationService.getCurrentPosition();
      
      expect(positionResult.success).toBe(true);
      expect(positionResult.data).toHaveProperty('latitude');
      expect(positionResult.data).toHaveProperty('longitude');
      expect(positionResult.data).toHaveProperty('accuracy');
      expect(positionResult.data).toHaveProperty('timestamp');
    });

    test('should start location tracking', async () => {
      const trackingResult = await locationService.startLocationTracking(
        'content_creation',
        'private'
      );
      
      expect(trackingResult.success).toBe(true);
      expect(typeof trackingResult.data).toBe('string'); // tracking ID
    });

    test('should create geofence', async () => {
      const geofenceResult = await locationService.createGeofence(
        'Test Geofence',
        { latitude: 40.7128, longitude: -74.0060 },
        100,
        {
          triggerEvents: ['enter', 'exit'],
          metadata: { purpose: 'content_location' }
        }
      );
      
      expect(geofenceResult.success).toBe(true);
      expect(typeof geofenceResult.data).toBe('string'); // geofence ID
    });

    test('should reverse geocode coordinates', async () => {
      const geocodeResult = await locationService.reverseGeocode(40.7128, -74.0060);
      
      expect(geocodeResult.success).toBe(true);
      expect(geocodeResult.data).toHaveProperty('formatted');
    });

    test('should get location history', async () => {
      const historyResult = await locationService.getLocationHistory({
        limit: 10
      });
      
      expect(historyResult.success).toBe(true);
      expect(historyResult.data).toHaveProperty('history');
      expect(historyResult.data).toHaveProperty('totalCount');
      expect(historyResult.data).toHaveProperty('averageAccuracy');
    });

    test('should get location statistics', async () => {
      const statsResult = await locationService.getLocationStatistics();
      
      expect(statsResult.success).toBe(true);
      expect(statsResult.data).toHaveProperty('totalLocations');
      expect(statsResult.data).toHaveProperty('trackingSessions');
      expect(statsResult.data).toHaveProperty('averageAccuracy');
      expect(statsResult.data).toHaveProperty('geofenceCount');
    });

    test('should update privacy settings', async () => {
      const privacyResult = await locationService.updatePrivacySettings({
        enableLocationTracking: true,
        precisionLevel: 'approximate',
        retentionDays: 7
      });
      
      expect(privacyResult.success).toBe(true);
    });

    test('should stop location tracking', async () => {
      // Start tracking first
      await locationService.startLocationTracking();
      
      const stopResult = await locationService.stopLocationTracking();
      expect(stopResult.success).toBe(true);
      expect(stopResult.data).toHaveProperty('trackingId');
      expect(stopResult.data).toHaveProperty('duration');
      expect(stopResult.data).toHaveProperty('locationCount');
    });
  });

  describe('Integration Tests', () => {
    test('should integrate storage and sync services', async () => {
      const storageService = OfflineStorageService.getInstance();
      const syncService = SyncService.getInstance();
      
      // Store content
      const contentData = { title: 'Integration Test', body: 'Test content' };
      const storeResult = await storageService.store('integration-test', contentData);
      expect(storeResult.success).toBe(true);
      
      // Add to sync queue
      const syncResult = await syncService.addToSyncQueue(
        'content',
        'create',
        contentData,
        5
      );
      expect(syncResult.success).toBe(true);
    });

    test('should integrate camera and location services', async () => {
      const cameraService = CameraService.getInstance();
      const locationService = LocationService.getInstance();
      
      // Get current location
      const locationResult = await locationService.getCurrentPosition();
      expect(locationResult.success).toBe(true);
      
      // Start camera session with location
      const sessionResult = await cameraService.startCaptureSession('photo', {
        enableLocation: true
      });
      expect(sessionResult.success).toBe(true);
    });

    test('should integrate notification and biometric services', async () => {
      const notificationService = PushNotificationService.getInstance();
      const biometricService = BiometricService.getInstance();
      
      // Check biometric availability
      const biometricResult = await biometricService.isAvailable();
      expect(biometricResult.success).toBe(true);
      
      // Send security notification
      const notificationResult = await notificationService.sendTemplateNotification(
        'security_alert',
        { reason: 'biometric_setup' }
      );
      expect(notificationResult.success).toBe(true);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    test('should handle network offline scenarios', async () => {
      // Simulate offline
      mockNavigator.onLine = false;
      
      const syncService = SyncService.getInstance();
      const syncResult = await syncService.processSync();
      
      expect(syncResult.success).toBe(true);
      expect(syncResult.data.processed).toBe(0); // No processing when offline
    });

    test('should handle storage quota exceeded', async () => {
      const storageService = OfflineStorageService.getInstance();
      
      // Try to store very large data
      const largeData = 'x'.repeat(1000 * 1024 * 1024); // 1GB
      const result = await storageService.store('too-large', largeData);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('storage');
    });

    test('should handle permission denied scenarios', async () => {
      // Mock permission denied
      mockNavigator.geolocation.getCurrentPosition.mockImplementation((_, error) => {
        error({ code: 1, message: 'Permission denied' });
      });
      
      const locationService = LocationService.getInstance();
      const result = await locationService.getCurrentPosition();
      
      // Should use cached location or handle gracefully
      expect(result.success || result.data).toBeTruthy();
    });

    test('should handle invalid biometric authentication', async () => {
      const biometricService = BiometricService.getInstance();
      
      // Test with invalid backup token
      const result = await biometricService.verifyBackupToken('invalid-token');
      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid backup token');
    });

    test('should handle media device not available', async () => {
      // Mock media device unavailable
      mockNavigator.mediaDevices.getUserMedia.mockRejectedValue(
        new Error('Media device not available')
      );
      
      const audioService = AudioService.getInstance();
      await audioService.startRecordingSession();
      
      const result = await audioService.startRecording();
      expect(result.success).toBe(false);
    });
  });

  describe('Performance Tests', () => {
    test('should handle concurrent storage operations', async () => {
      const storageService = OfflineStorageService.getInstance();
      
      // Create multiple concurrent operations
      const operations = Array.from({ length: 10 }, (_, i) =>
        storageService.store(`concurrent-${i}`, { index: i, data: `test-${i}` })
      );
      
      const results = await Promise.all(operations);
      
      // All operations should succeed
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
    });

    test('should handle large sync queue efficiently', async () => {
      const syncService = SyncService.getInstance();
      
      // Add many items to sync queue
      const operations = Array.from({ length: 100 }, (_, i) =>
        syncService.addToSyncQueue('content', 'create', { id: i }, Math.floor(Math.random() * 10))
      );
      
      const results = await Promise.all(operations);
      
      // All additions should succeed
      results.forEach(result => {
        expect(result.success).toBe(true);
      });
      
      // Check queue status
      const statusResult = await syncService.getSyncStatus();
      expect(statusResult.success).toBe(true);
      expect(statusResult.data.queueSize).toBeGreaterThan(0);
    });
  });
});

export default describe;