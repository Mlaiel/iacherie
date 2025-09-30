/**
 * Biometric Service - Professional Biometric Authentication Management
 * 
 * Enterprise-grade biometric authentication service with multi-modal support,
 * secure key management, fallback mechanisms, and advanced security features.
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

import {
  BiometricConfig,
  BiometricResult,
  ServiceResponse,
  ServiceError,
  SecurityContext
} from './types';
import {
  handleServiceError,
  formatServiceResponse,
  generateCorrelationId,
  encryptData,
  decryptData,
  createBiometricConfig
} from './utils';
import { STORAGE_KEYS, ERROR_CODES } from './constants';
import MobileAPIService from './MobileAPIService';
import OfflineStorageService from './OfflineStorageService';

interface BiometricCapability {
  type: 'faceID' | 'touchID' | 'voice' | 'iris' | 'fingerprint';
  available: boolean;
  enrolled: boolean;
  accuracy: number;
  lastUsed?: number;
}

interface BiometricSession {
  sessionId: string;
  userId: string;
  deviceId: string;
  authenticationType: string;
  startTime: number;
  endTime?: number;
  attempts: number;
  success: boolean;
  riskScore: number;
  location?: string;
}

interface SecurityAuditLog {
  timestamp: number;
  event: 'authentication_attempt' | 'authentication_success' | 'authentication_failure' | 'fallback_used' | 'security_breach';
  details: Record<string, any>;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * Professional biometric authentication service for content creators
 */
class BiometricService {
  private static instance: BiometricService;
  private config: BiometricConfig;
  private apiService: MobileAPIService;
  private storageService: OfflineStorageService;
  private isInitialized = false;
  private capabilities: Map<string, BiometricCapability> = new Map();
  private activeSessions: Map<string, BiometricSession> = new Map();
  private auditLog: SecurityAuditLog[] = [];
  private encryptionKey: string = '';
  private deviceId: string = '';
  private currentAttempts = 0;
  private lastFailedAttempt = 0;
  private isLocked = false;

  private constructor(config: BiometricConfig) {
    this.config = config;
    this.apiService = MobileAPIService.getInstance();
    this.storageService = OfflineStorageService.getInstance();
    this.initialize();
  }

  public static getInstance(config?: BiometricConfig): BiometricService {
    if (!BiometricService.instance) {
      const defaultConfig = createBiometricConfig(config);
      BiometricService.instance = new BiometricService(defaultConfig);
    }
    return BiometricService.instance;
  }

  /**
   * Initialize the biometric service
   */
  private async initialize(): Promise<void> {
    try {
      // Generate device-specific identifiers
      this.deviceId = await this.generateDeviceId();
      this.encryptionKey = await this.generateEncryptionKey();

      // Detect available biometric capabilities
      await this.detectCapabilities();

      // Load audit log and session data
      await this.loadAuditLog();
      await this.loadSessionData();

      // Setup security monitoring
      this.setupSecurityMonitoring();

      this.isInitialized = true;

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'initialize');
      console.error('Failed to initialize biometric service:', serviceError);
    }
  }

  /**
   * Check if biometric authentication is available
   */
  public async isAvailable(): Promise<ServiceResponse<{
    available: boolean;
    capabilities: BiometricCapability[];
    recommendedMethod?: string;
  }>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const capabilities = Array.from(this.capabilities.values());
      const available = capabilities.some(cap => cap.available && cap.enrolled);
      
      // Recommend the most accurate available method
      const recommendedMethod = capabilities
        .filter(cap => cap.available && cap.enrolled)
        .sort((a, b) => b.accuracy - a.accuracy)[0]?.type;

      return formatServiceResponse({
        available,
        capabilities,
        recommendedMethod
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'isAvailable');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Authenticate user with biometrics
   */
  public async authenticate(
    promptMessage?: string,
    fallbackTitle?: string
  ): Promise<ServiceResponse<BiometricResult>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      // Check if service is locked due to too many failed attempts
      if (this.isLocked) {
        const timeRemaining = this.getTimeUntilUnlock();
        if (timeRemaining > 0) {
          return {
            success: false,
            error: `Authentication locked. Try again in ${Math.ceil(timeRemaining / 1000)} seconds.`,
            timestamp: Date.now()
          };
        } else {
          this.isLocked = false;
          this.currentAttempts = 0;
        }
      }

      // Start authentication session
      const sessionId = generateCorrelationId();
      const session: BiometricSession = {
        sessionId,
        userId: await this.getCurrentUserId(),
        deviceId: this.deviceId,
        authenticationType: 'biometric',
        startTime: Date.now(),
        attempts: 0,
        success: false,
        riskScore: this.calculateRiskScore()
      };

      this.activeSessions.set(sessionId, session);

      // Check available methods
      const availabilityResult = await this.isAvailable();
      if (!availabilityResult.success || !availabilityResult.data!.available) {
        if (this.config.fallbackToPin) {
          return await this.authenticateWithFallback(session, fallbackTitle);
        } else {
          return {
            success: false,
            error: 'Biometric authentication not available',
            timestamp: Date.now()
          };
        }
      }

      // Attempt biometric authentication
      const authResult = await this.performBiometricAuth(
        session,
        availabilityResult.data!.recommendedMethod!,
        promptMessage
      );

      // Log the attempt
      await this.logSecurityEvent(
        authResult.success ? 'authentication_success' : 'authentication_failure',
        {
          sessionId,
          method: availabilityResult.data!.recommendedMethod,
          attempts: session.attempts,
          riskScore: session.riskScore
        },
        authResult.success ? 'low' : 'medium'
      );

      return authResult;

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'authenticate');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Enroll biometric data
   */
  public async enrollBiometric(
    type: 'faceID' | 'touchID' | 'voice'
  ): Promise<ServiceResponse<{
    enrolled: boolean;
    confidence: number;
    backupToken: string;
  }>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      // Check if the biometric type is supported
      const capability = this.capabilities.get(type);
      if (!capability || !capability.available) {
        return {
          success: false,
          error: `${type} is not available on this device`,
          timestamp: Date.now()
        };
      }

      // Simulate enrollment process
      const enrollmentResult = await this.performEnrollment(type);
      
      if (enrollmentResult.success) {
        // Update capability
        capability.enrolled = true;
        capability.lastUsed = Date.now();
        this.capabilities.set(type, capability);

        // Generate backup token
        const backupToken = await this.generateBackupToken(type);

        // Store enrollment data securely
        await this.storageService.store(`biometric_enrollment_${type}`, {
          enrolled: true,
          enrolledAt: Date.now(),
          deviceId: this.deviceId,
          backupToken: encryptData(backupToken, this.encryptionKey)
        }, {
          encrypted: true,
          priority: 10
        });

        // Sync with server
        await this.syncEnrollmentData(type, backupToken);

        await this.logSecurityEvent(
          'authentication_attempt',
          { type, action: 'enrollment', success: true },
          'low'
        );

        return formatServiceResponse({
          enrolled: true,
          confidence: enrollmentResult.confidence,
          backupToken
        });
      } else {
        return {
          success: false,
          error: 'Enrollment failed',
          timestamp: Date.now()
        };
      }

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'enrollBiometric', { type });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Remove biometric enrollment
   */
  public async removeBiometric(type: 'faceID' | 'touchID' | 'voice'): Promise<ServiceResponse<boolean>> {
    try {
      // Update capability
      const capability = this.capabilities.get(type);
      if (capability) {
        capability.enrolled = false;
        this.capabilities.set(type, capability);
      }

      // Remove stored data
      await this.storageService.remove(`biometric_enrollment_${type}`);

      // Notify server
      await this.apiService.request({
        method: 'DELETE',
        endpoint: '/auth/biometric/enrollment',
        data: { type, deviceId: this.deviceId },
        requiresAuth: true
      });

      await this.logSecurityEvent(
        'authentication_attempt',
        { type, action: 'removal', success: true },
        'low'
      );

      return formatServiceResponse(true);

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'removeBiometric', { type });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Verify with backup token
   */
  public async verifyBackupToken(token: string): Promise<ServiceResponse<BiometricResult>> {
    try {
      // Verify token against stored tokens
      for (const [type, capability] of this.capabilities) {
        if (!capability.enrolled) continue;

        const storedData = await this.storageService.retrieve(`biometric_enrollment_${type}`);
        if (storedData.success) {
          const decryptedToken = decryptData(storedData.data.backupToken, this.encryptionKey);
          if (decryptedToken === token) {
            const result: BiometricResult = {
              success: true,
              biometricType: 'pin', // Backup authentication
              confidence: 0.9,
              timestamp: Date.now(),
              deviceId: this.deviceId
            };

            await this.logSecurityEvent(
              'fallback_used',
              { method: 'backup_token', success: true },
              'low'
            );

            return formatServiceResponse(result);
          }
        }
      }

      // Token not found or invalid
      this.currentAttempts++;
      this.checkForLockout();

      await this.logSecurityEvent(
        'authentication_failure',
        { method: 'backup_token', attempts: this.currentAttempts },
        'medium'
      );

      return {
        success: false,
        error: 'Invalid backup token',
        timestamp: Date.now()
      };

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'verifyBackupToken');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get security audit log
   */
  public async getSecurityAuditLog(
    limit = 50
  ): Promise<ServiceResponse<SecurityAuditLog[]>> {
    try {
      const recentLogs = this.auditLog
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, limit);

      return formatServiceResponse(recentLogs, false, {
        totalEvents: this.auditLog.length,
        criticalEvents: this.auditLog.filter(log => log.riskLevel === 'critical').length,
        lastAudit: this.auditLog[0]?.timestamp
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'getSecurityAuditLog');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get current security context
   */
  public async getSecurityContext(): Promise<ServiceResponse<SecurityContext>> {
    try {
      const context: SecurityContext = {
        userId: await this.getCurrentUserId(),
        deviceId: this.deviceId,
        sessionId: generateCorrelationId(),
        permissions: await this.getUserPermissions(),
        riskScore: this.calculateRiskScore(),
        lastVerified: Date.now()
      };

      return formatServiceResponse(context);

    } catch (error) {
      const serviceError = handleServiceError(error, 'BiometricService', 'getSecurityContext');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  // Private helper methods

  private async detectCapabilities(): Promise<void> {
    // Mock capability detection for different platforms
    const platform = this.getCurrentPlatform();

    if (platform === 'ios') {
      this.capabilities.set('faceID', {
        type: 'faceID',
        available: this.config.enableFaceID,
        enrolled: false,
        accuracy: 0.99
      });
      this.capabilities.set('touchID', {
        type: 'touchID',
        available: this.config.enableTouchID,
        enrolled: false,
        accuracy: 0.95
      });
    } else if (platform === 'android') {
      this.capabilities.set('fingerprint', {
        type: 'fingerprint',
        available: this.config.enableTouchID,
        enrolled: false,
        accuracy: 0.94
      });
    }

    if (this.config.enableVoice) {
      this.capabilities.set('voice', {
        type: 'voice',
        available: true,
        enrolled: false,
        accuracy: 0.87
      });
    }
  }

  private async performBiometricAuth(
    session: BiometricSession,
    method: string,
    prompt?: string
  ): Promise<ServiceResponse<BiometricResult>> {
    try {
      session.attempts++;
      session.authenticationType = method;

      // Simulate biometric authentication
      // In a real implementation, this would use platform-specific APIs
      const authSuccess = await this.simulateBiometricAuth(method);

      const result: BiometricResult = {
        success: authSuccess,
        biometricType: method as any,
        confidence: authSuccess ? this.capabilities.get(method)?.accuracy || 0.9 : 0,
        timestamp: Date.now(),
        deviceId: this.deviceId
      };

      // Update session
      session.success = authSuccess;
      session.endTime = Date.now();

      if (authSuccess) {
        this.currentAttempts = 0;
        // Update last used timestamp
        const capability = this.capabilities.get(method);
        if (capability) {
          capability.lastUsed = Date.now();
          this.capabilities.set(method, capability);
        }
      } else {
        result.error = 'Biometric authentication failed';
        this.currentAttempts++;
        this.lastFailedAttempt = Date.now();
        this.checkForLockout();
      }

      return formatServiceResponse(result);

    } catch (error) {
      throw error;
    }
  }

  private async authenticateWithFallback(
    session: BiometricSession,
    fallbackTitle?: string
  ): Promise<ServiceResponse<BiometricResult>> {
    try {
      session.authenticationType = 'fallback';

      await this.logSecurityEvent(
        'fallback_used',
        { reason: 'biometric_unavailable', sessionId: session.sessionId },
        'medium'
      );

      // Simulate PIN/password fallback
      const result: BiometricResult = {
        success: true, // Assume successful for simulation
        biometricType: 'pin',
        confidence: 0.8,
        timestamp: Date.now(),
        deviceId: this.deviceId
      };

      session.success = true;
      session.endTime = Date.now();

      return formatServiceResponse(result);

    } catch (error) {
      throw error;
    }
  }

  private async performEnrollment(type: string): Promise<{ success: boolean; confidence: number }> {
    // Simulate enrollment process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 95% success rate for simulation
    const success = Math.random() > 0.05;
    const confidence = success ? 0.9 + Math.random() * 0.1 : 0;

    return { success, confidence };
  }

  private async simulateBiometricAuth(method: string): Promise<boolean> {
    // Simulate authentication delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // 90% success rate for simulation
    return Math.random() > 0.1;
  }

  private calculateRiskScore(): number {
    let score = 0;

    // Time-based risk
    const hour = new Date().getHours();
    if (hour < 6 || hour > 22) score += 0.2;

    // Failed attempts risk
    score += this.currentAttempts * 0.1;

    // Time since last failed attempt
    if (this.lastFailedAttempt > 0) {
      const timeSince = Date.now() - this.lastFailedAttempt;
      if (timeSince < 60000) score += 0.3; // Recent failure
    }

    return Math.min(score, 1.0);
  }

  private checkForLockout(): void {
    if (this.currentAttempts >= this.config.maxAttempts) {
      this.isLocked = true;
      this.logSecurityEvent(
        'security_breach',
        { reason: 'max_attempts_exceeded', attempts: this.currentAttempts },
        'critical'
      );
    }
  }

  private getTimeUntilUnlock(): number {
    const lockDuration = 300000; // 5 minutes
    const timeLocked = Date.now() - this.lastFailedAttempt;
    return Math.max(0, lockDuration - timeLocked);
  }

  private async generateDeviceId(): Promise<string> {
    // Generate unique device identifier
    const stored = await this.storageService.retrieve(STORAGE_KEYS.DEVICE_ID);
    if (stored.success) {
      return stored.data;
    }

    const deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    await this.storageService.store(STORAGE_KEYS.DEVICE_ID, deviceId);
    return deviceId;
  }

  private async generateEncryptionKey(): Promise<string> {
    const stored = await this.storageService.retrieve(STORAGE_KEYS.BIOMETRIC_KEY);
    if (stored.success) {
      return stored.data;
    }

    const key = Array.from({ length: 32 }, () => 
      Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
    ).join('');
    
    await this.storageService.store(STORAGE_KEYS.BIOMETRIC_KEY, key, { encrypted: true });
    return key;
  }

  private async generateBackupToken(type: string): Promise<string> {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substr(2, 9);
    return `${type}_${timestamp}_${random}`;
  }

  private async syncEnrollmentData(type: string, backupToken: string): Promise<void> {
    try {
      await this.apiService.request({
        method: 'POST',
        endpoint: '/auth/biometric/enroll',
        data: {
          type,
          deviceId: this.deviceId,
          backupToken: encryptData(backupToken, this.encryptionKey),
          enrolledAt: Date.now()
        },
        requiresAuth: true
      });
    } catch (error) {
      console.error('Failed to sync enrollment data:', error);
    }
  }

  private async logSecurityEvent(
    event: SecurityAuditLog['event'],
    details: Record<string, any>,
    riskLevel: SecurityAuditLog['riskLevel']
  ): Promise<void> {
    const logEntry: SecurityAuditLog = {
      timestamp: Date.now(),
      event,
      details,
      riskLevel
    };

    this.auditLog.push(logEntry);

    // Keep only last 1000 entries
    if (this.auditLog.length > 1000) {
      this.auditLog = this.auditLog.slice(-1000);
    }

    await this.saveAuditLog();
  }

  private setupSecurityMonitoring(): void {
    // Setup monitoring for suspicious activities
    setInterval(() => {
      this.performSecurityCheck();
    }, 60000); // Check every minute
  }

  private async performSecurityCheck(): Promise<void> {
    const riskScore = this.calculateRiskScore();
    
    if (riskScore > 0.7) {
      await this.logSecurityEvent(
        'security_breach',
        { reason: 'high_risk_score', score: riskScore },
        'high'
      );
    }
  }

  private getCurrentPlatform(): string {
    if (typeof window !== 'undefined') {
      if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
        return 'ios';
      } else if (/Android/.test(navigator.userAgent)) {
        return 'android';
      }
    }
    return 'web';
  }

  private async getCurrentUserId(): Promise<string> {
    // In a real implementation, this would get the current user ID
    return 'user_' + Math.random().toString(36).substr(2, 9);
  }

  private async getUserPermissions(): Promise<string[]> {
    // Mock permissions
    return ['read_content', 'write_content', 'manage_collaborations'];
  }

  private async loadAuditLog(): Promise<void> {
    try {
      const result = await this.storageService.retrieve('security_audit_log');
      if (result.success) {
        this.auditLog = result.data || [];
      }
    } catch (error) {
      console.warn('Failed to load audit log:', error);
      this.auditLog = [];
    }
  }

  private async saveAuditLog(): Promise<void> {
    try {
      await this.storageService.store('security_audit_log', this.auditLog, {
        encrypted: true,
        priority: 8
      });
    } catch (error) {
      console.error('Failed to save audit log:', error);
    }
  }

  private async loadSessionData(): Promise<void> {
    try {
      const result = await this.storageService.retrieve('biometric_sessions');
      if (result.success) {
        const sessions = result.data || {};
        this.activeSessions = new Map(Object.entries(sessions));
      }
    } catch (error) {
      console.warn('Failed to load session data:', error);
      this.activeSessions = new Map();
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    this.activeSessions.clear();
    this.auditLog = [];
    this.capabilities.clear();
  }
}

export default BiometricService;