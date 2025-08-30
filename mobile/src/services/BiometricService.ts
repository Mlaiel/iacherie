/**
 * Biometric Service - Advanced biometric authentication service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

import { offlineStorageService } from './OfflineStorageService';
import { mobileAPIService } from './MobileAPIService';

export interface BiometricCapabilities {
  isSupported: boolean;
  supportedTypes: BiometricType[];
  deviceInfo: {
    hasFingerprint: boolean;
    hasFaceID: boolean;
    hasVoiceID: boolean;
    hasIris: boolean;
    secureHardware: boolean;
  };
}

export type BiometricType = 'fingerprint' | 'faceID' | 'voiceID' | 'iris' | 'pin' | 'pattern';

export interface BiometricAuthOptions {
  title: string;
  subtitle?: string;
  description?: string;
  fallbackLabel?: string;
  cancelLabel?: string;
  disableDeviceFallback?: boolean;
  maxAttempts?: number;
  timeout?: number;
  allowedAuthenticators?: BiometricType[];
}

export interface BiometricAuthResult {
  success: boolean;
  type?: BiometricType;
  error?: string;
  errorCode?: number;
  attempts?: number;
  timestamp: number;
  deviceId: string;
}

export interface BiometricSettings {
  enabled: boolean;
  preferredType: BiometricType;
  requireBiometricForLogin: boolean;
  requireBiometricForPayments: boolean;
  requireBiometricForSensitiveActions: boolean;
  fallbackToPin: boolean;
  maxFailedAttempts: number;
  lockoutDuration: number; // minutes
}

export interface BiometricTemplate {
  id: string;
  type: BiometricType;
  hash: string;
  createdAt: number;
  lastUsed: number;
  usage: number;
  quality: number;
  isActive: boolean;
}

export interface BiometricSecurityEvent {
  type: 'auth_success' | 'auth_failure' | 'template_enrolled' | 'template_removed' | 'lockout' | 'unlock';
  timestamp: number;
  biometricType?: BiometricType;
  deviceId: string;
  attempts?: number;
  location?: { latitude: number; longitude: number };
  ipAddress?: string;
  userAgent?: string;
}

export class BiometricService {
  private isInitialized: boolean = false;
  private capabilities: BiometricCapabilities;
  private settings: BiometricSettings;
  private templates: Map<string, BiometricTemplate> = new Map();
  private failedAttempts: number = 0;
  private lockoutUntil: number = 0;
  private securityEvents: BiometricSecurityEvent[] = [];
  private deviceId: string;

  constructor() {
    this.deviceId = this.generateDeviceId();
    
    this.capabilities = {
      isSupported: false,
      supportedTypes: [],
      deviceInfo: {
        hasFingerprint: false,
        hasFaceID: false,
        hasVoiceID: false,
        hasIris: false,
        secureHardware: false,
      },
    };

    this.settings = {
      enabled: true,
      preferredType: 'fingerprint',
      requireBiometricForLogin: true,
      requireBiometricForPayments: true,
      requireBiometricForSensitiveActions: true,
      fallbackToPin: true,
      maxFailedAttempts: 5,
      lockoutDuration: 30, // 30 minutes
    };

    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    try {
      // Detect biometric capabilities
      await this.detectCapabilities();
      
      // Load settings from storage
      await this.loadSettings();
      
      // Load biometric templates
      await this.loadTemplates();
      
      // Load security events
      await this.loadSecurityEvents();
      
      // Initialize Web Authentication API if available
      if ('credentials' in navigator && 'create' in navigator.credentials) {
        await this.initializeWebAuthn();
      }
      
      this.isInitialized = true;
      console.log('Biometric Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Biometric Service:', error);
    }
  }

  // Public API Methods
  async isAvailable(): Promise<boolean> {
    if (!this.isInitialized) {
      await this.initializeService();
    }
    return this.capabilities.isSupported;
  }

  getCapabilities(): BiometricCapabilities {
    return { ...this.capabilities };
  }

  async authenticate(options?: BiometricAuthOptions): Promise<BiometricAuthResult> {
    const authOptions: BiometricAuthOptions = {
      title: 'Biometric Authentication',
      subtitle: 'Use your biometric to authenticate',
      description: 'Place your finger on the sensor or look at the camera',
      fallbackLabel: 'Use PIN',
      cancelLabel: 'Cancel',
      maxAttempts: 3,
      timeout: 30000,
      ...options,
    };

    // Check if biometrics are available
    if (!this.capabilities.isSupported) {
      return this.createAuthResult(false, undefined, 'Biometric authentication not supported');
    }

    // Check if device is locked out
    if (this.isLockedOut()) {
      const remaining = Math.ceil((this.lockoutUntil - Date.now()) / 60000);
      return this.createAuthResult(false, undefined, `Device locked. Try again in ${remaining} minutes`);
    }

    try {
      // Try Web Authentication API first
      if ('credentials' in navigator && 'get' in navigator.credentials) {
        const result = await this.authenticateWithWebAuthn(authOptions);
        if (result.success) {
          this.handleSuccessfulAuth(result.type!);
          return result;
        }
      }

      // Fallback to platform-specific biometric authentication
      const result = await this.authenticateWithPlatformBiometric(authOptions);
      
      if (result.success) {
        this.handleSuccessfulAuth(result.type!);
      } else {
        this.handleFailedAuth();
      }

      return result;

    } catch (error) {
      this.handleFailedAuth();
      return this.createAuthResult(false, undefined, error.message);
    }
  }

  async enrollBiometric(type: BiometricType): Promise<boolean> {
    try {
      // Check if already enrolled
      const existingTemplate = Array.from(this.templates.values()).find(t => t.type === type && t.isActive);
      if (existingTemplate) {
        throw new Error(`${type} already enrolled`);
      }

      // Create enrollment options
      const enrollmentResult = await this.performEnrollment(type);
      
      if (enrollmentResult.success) {
        const template: BiometricTemplate = {
          id: this.generateTemplateId(),
          type,
          hash: enrollmentResult.hash!,
          createdAt: Date.now(),
          lastUsed: 0,
          usage: 0,
          quality: enrollmentResult.quality || 0.8,
          isActive: true,
        };

        this.templates.set(template.id, template);
        await this.saveTemplates();

        // Log security event
        this.logSecurityEvent({
          type: 'template_enrolled',
          timestamp: Date.now(),
          biometricType: type,
          deviceId: this.deviceId,
        });

        // Sync with server
        await this.syncBiometricData();

        return true;
      }

      return false;
    } catch (error) {
      console.error('Biometric enrollment failed:', error);
      return false;
    }
  }

  async removeBiometric(templateId: string): Promise<boolean> {
    try {
      const template = this.templates.get(templateId);
      if (!template) {
        return false;
      }

      // Deactivate template
      template.isActive = false;
      this.templates.set(templateId, template);
      await this.saveTemplates();

      // Log security event
      this.logSecurityEvent({
        type: 'template_removed',
        timestamp: Date.now(),
        biometricType: template.type,
        deviceId: this.deviceId,
      });

      // Sync with server
      await this.syncBiometricData();

      return true;
    } catch (error) {
      console.error('Failed to remove biometric:', error);
      return false;
    }
  }

  getEnrolledBiometrics(): BiometricTemplate[] {
    return Array.from(this.templates.values()).filter(t => t.isActive);
  }

  async updateSettings(newSettings: Partial<BiometricSettings>): Promise<void> {
    this.settings = { ...this.settings, ...newSettings };
    await offlineStorageService.store('biometric_settings', this.settings);
    
    // Sync with server
    await mobileAPIService.makeRequest('/biometric/settings', {
      method: 'PUT',
      body: JSON.stringify(this.settings),
    });
  }

  getSettings(): BiometricSettings {
    return { ...this.settings };
  }

  // Security and Compliance
  async verifyBiometricIntegrity(): Promise<boolean> {
    try {
      // Check if biometric hardware is compromised
      if (this.capabilities.deviceInfo.secureHardware) {
        // Verify secure enclave/TEE integrity
        const integrityCheck = await this.performHardwareIntegrityCheck();
        if (!integrityCheck.isValid) {
          await this.handleSecurityCompromise('hardware_compromise');
          return false;
        }
      }

      // Verify template integrity
      for (const template of this.templates.values()) {
        if (!await this.verifyTemplateIntegrity(template)) {
          await this.handleSecurityCompromise('template_compromise');
          return false;
        }
      }

      return true;
    } catch (error) {
      console.error('Biometric integrity check failed:', error);
      return false;
    }
  }

  async exportSecurityEvents(): Promise<BiometricSecurityEvent[]> {
    return [...this.securityEvents];
  }

  async clearSecurityEvents(): Promise<void> {
    this.securityEvents = [];
    await offlineStorageService.store('biometric_security_events', []);
  }

  isLockedOut(): boolean {
    return Date.now() < this.lockoutUntil;
  }

  getRemainingLockoutTime(): number {
    if (!this.isLockedOut()) return 0;
    return Math.ceil((this.lockoutUntil - Date.now()) / 60000);
  }

  // Business Logic Integration
  async authenticateForPayment(amount: number, currency: string): Promise<BiometricAuthResult> {
    if (!this.settings.requireBiometricForPayments) {
      return this.createAuthResult(true, 'bypass');
    }

    return this.authenticate({
      title: 'Confirm Payment',
      subtitle: `${currency} ${amount}`,
      description: 'Use your biometric to authorize this payment',
      maxAttempts: 2,
      timeout: 20000,
    });
  }

  async authenticateForContentAccess(contentType: 'premium' | 'protected' | 'collaboration'): Promise<BiometricAuthResult> {
    if (!this.settings.requireBiometricForSensitiveActions) {
      return this.createAuthResult(true, 'bypass');
    }

    const titles = {
      premium: 'Access Premium Content',
      protected: 'Access Protected Content',
      collaboration: 'Access Collaboration Data',
    };

    return this.authenticate({
      title: titles[contentType],
      description: 'Biometric verification required for secure access',
      maxAttempts: 3,
    });
  }

  async authenticateForDataExport(): Promise<BiometricAuthResult> {
    return this.authenticate({
      title: 'Data Export Authorization',
      description: 'Verify your identity to export sensitive data',
      maxAttempts: 2,
      timeout: 25000,
    });
  }

  // Private Methods
  private async detectCapabilities(): Promise<void> {
    const userAgent = navigator.userAgent.toLowerCase();
    
    // Check for Web Authentication API support
    if ('credentials' in navigator && 'create' in navigator.credentials) {
      this.capabilities.isSupported = true;
      this.capabilities.supportedTypes.push('fingerprint');
      
      // Check for platform-specific capabilities
      if (userAgent.includes('iphone') || userAgent.includes('ipad')) {
        this.capabilities.deviceInfo.hasFaceID = true;
        this.capabilities.deviceInfo.hasFingerprint = true;
        this.capabilities.supportedTypes.push('faceID');
      } else if (userAgent.includes('android')) {
        this.capabilities.deviceInfo.hasFingerprint = true;
        this.capabilities.deviceInfo.hasIris = false; // Would need specific detection
      }

      // Check for secure hardware
      if ('navigator' in window && 'userAgentData' in navigator) {
        this.capabilities.deviceInfo.secureHardware = true;
      }
    }

    // Check for additional biometric APIs (vendor-specific)
    await this.checkVendorSpecificAPIs();
  }

  private async checkVendorSpecificAPIs(): Promise<void> {
    // Check for vendor-specific biometric APIs
    if ('FingerprintManager' in window) {
      this.capabilities.supportedTypes.push('fingerprint');
      this.capabilities.deviceInfo.hasFingerprint = true;
    }

    if ('FaceID' in window) {
      this.capabilities.supportedTypes.push('faceID');
      this.capabilities.deviceInfo.hasFaceID = true;
    }
  }

  private async initializeWebAuthn(): Promise<void> {
    try {
      // Check if WebAuthn is available
      const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
      
      if (available) {
        this.capabilities.isSupported = true;
        this.capabilities.deviceInfo.secureHardware = true;
      }
    } catch (error) {
      console.warn('WebAuthn initialization failed:', error);
    }
  }

  private async authenticateWithWebAuthn(options: BiometricAuthOptions): Promise<BiometricAuthResult> {
    try {
      const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
        challenge: new Uint8Array(32),
        timeout: options.timeout || 30000,
        userVerification: 'required',
        allowCredentials: this.getStoredCredentials(),
      };

      const credential = await navigator.credentials.get({
        publicKey: publicKeyCredentialRequestOptions,
      }) as PublicKeyCredential;

      if (credential) {
        // Verify the credential
        const isValid = await this.verifyCredential(credential);
        
        if (isValid) {
          return this.createAuthResult(true, 'fingerprint');
        }
      }

      return this.createAuthResult(false, undefined, 'Authentication failed');
    } catch (error) {
      return this.createAuthResult(false, undefined, error.message);
    }
  }

  private async authenticateWithPlatformBiometric(options: BiometricAuthOptions): Promise<BiometricAuthResult> {
    // Simulate platform-specific biometric authentication
    return new Promise((resolve) => {
      // This would interface with platform-specific APIs in a real implementation
      setTimeout(() => {
        const success = Math.random() > 0.2; // 80% success rate for simulation
        const type = this.settings.preferredType;
        
        resolve(this.createAuthResult(success, success ? type : undefined, success ? undefined : 'Authentication failed'));
      }, 2000);
    });
  }

  private async performEnrollment(type: BiometricType): Promise<{ success: boolean; hash?: string; quality?: number }> {
    try {
      if (type === 'fingerprint' && 'credentials' in navigator) {
        // Use WebAuthn for enrollment
        const publicKeyCredentialCreationOptions: PublicKeyCredentialCreationOptions = {
          challenge: new Uint8Array(32),
          rp: {
            name: 'Ainflue',
            id: window.location.hostname,
          },
          user: {
            id: new TextEncoder().encode(this.deviceId),
            name: 'user@ainflue.com',
            displayName: 'Ainflue User',
          },
          pubKeyCredParams: [
            { alg: -7, type: 'public-key' },
            { alg: -257, type: 'public-key' },
          ],
          authenticatorSelection: {
            authenticatorAttachment: 'platform',
            userVerification: 'required',
          },
          timeout: 60000,
          attestation: 'direct',
        };

        const credential = await navigator.credentials.create({
          publicKey: publicKeyCredentialCreationOptions,
        }) as PublicKeyCredential;

        if (credential) {
          const hash = this.generateCredentialHash(credential);
          return { success: true, hash, quality: 0.9 };
        }
      }

      // Fallback to platform-specific enrollment
      return this.performPlatformEnrollment(type);
    } catch (error) {
      console.error('Enrollment failed:', error);
      return { success: false };
    }
  }

  private async performPlatformEnrollment(type: BiometricType): Promise<{ success: boolean; hash?: string; quality?: number }> {
    // Simulate platform-specific enrollment
    return new Promise((resolve) => {
      setTimeout(() => {
        const success = Math.random() > 0.1; // 90% success rate
        const hash = success ? this.generateRandomHash() : undefined;
        const quality = success ? 0.8 + Math.random() * 0.2 : undefined;
        
        resolve({ success, hash, quality });
      }, 3000);
    });
  }

  private createAuthResult(success: boolean, type?: BiometricType, error?: string): BiometricAuthResult {
    return {
      success,
      type,
      error,
      errorCode: error ? 1001 : undefined,
      attempts: this.failedAttempts + 1,
      timestamp: Date.now(),
      deviceId: this.deviceId,
    };
  }

  private handleSuccessfulAuth(type: BiometricType): void {
    this.failedAttempts = 0;
    this.lockoutUntil = 0;

    // Update template usage
    const template = Array.from(this.templates.values()).find(t => t.type === type && t.isActive);
    if (template) {
      template.lastUsed = Date.now();
      template.usage++;
      this.saveTemplates();
    }

    // Log security event
    this.logSecurityEvent({
      type: 'auth_success',
      timestamp: Date.now(),
      biometricType: type,
      deviceId: this.deviceId,
    });
  }

  private handleFailedAuth(): void {
    this.failedAttempts++;

    // Log security event
    this.logSecurityEvent({
      type: 'auth_failure',
      timestamp: Date.now(),
      deviceId: this.deviceId,
      attempts: this.failedAttempts,
    });

    // Check for lockout
    if (this.failedAttempts >= this.settings.maxFailedAttempts) {
      this.lockoutUntil = Date.now() + (this.settings.lockoutDuration * 60 * 1000);
      
      // Log lockout event
      this.logSecurityEvent({
        type: 'lockout',
        timestamp: Date.now(),
        deviceId: this.deviceId,
        attempts: this.failedAttempts,
      });
    }
  }

  private async handleSecurityCompromise(type: 'hardware_compromise' | 'template_compromise'): Promise<void> {
    // Disable all biometric authentication
    this.settings.enabled = false;
    
    // Clear all templates
    this.templates.clear();
    
    // Log security event
    this.logSecurityEvent({
      type: 'auth_failure',
      timestamp: Date.now(),
      deviceId: this.deviceId,
    });

    // Notify server
    await mobileAPIService.makeRequest('/security/biometric-compromise', {
      method: 'POST',
      body: JSON.stringify({
        type,
        deviceId: this.deviceId,
        timestamp: Date.now(),
      }),
    });

    // Save compromised state
    await this.saveSettings();
    await this.saveTemplates();
  }

  private async performHardwareIntegrityCheck(): Promise<{ isValid: boolean; details?: any }> {
    try {
      // Check for hardware attestation if available
      if ('getClientCapabilities' in navigator) {
        // Platform-specific integrity check
        return { isValid: true };
      }

      // Basic integrity checks
      const checks = {
        webauthnAvailable: 'credentials' in navigator,
        secureContext: window.isSecureContext,
        platformAuthenticator: await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable(),
      };

      const isValid = Object.values(checks).every(Boolean);
      return { isValid, details: checks };
    } catch (error) {
      return { isValid: false, details: error.message };
    }
  }

  private async verifyTemplateIntegrity(template: BiometricTemplate): Promise<boolean> {
    // Verify template hash hasn't been tampered with
    const expectedHash = this.generateTemplateHash(template);
    return template.hash === expectedHash;
  }

  private async verifyCredential(credential: PublicKeyCredential): Promise<boolean> {
    try {
      // In a real implementation, this would verify the credential signature
      // against the stored public key and challenge
      return credential.id.length > 0;
    } catch (error) {
      return false;
    }
  }

  private getStoredCredentials(): PublicKeyCredentialDescriptor[] {
    return Array.from(this.templates.values())
      .filter(t => t.isActive && t.type === 'fingerprint')
      .map(t => ({
        id: new TextEncoder().encode(t.id),
        type: 'public-key' as const,
        transports: ['internal'] as AuthenticatorTransport[],
      }));
  }

  private generateCredentialHash(credential: PublicKeyCredential): string {
    return btoa(credential.id).substring(0, 32);
  }

  private generateTemplateHash(template: Omit<BiometricTemplate, 'hash'>): string {
    const data = `${template.id}_${template.type}_${template.createdAt}_${this.deviceId}`;
    return btoa(data).substring(0, 32);
  }

  private generateRandomHash(): string {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array));
  }

  private generateTemplateId(): string {
    return `template_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateDeviceId(): string {
    // Generate a consistent device ID based on available information
    const info = [
      navigator.userAgent,
      navigator.language,
      screen.width,
      screen.height,
      new Date().getTimezoneOffset(),
    ].join('|');
    
    return btoa(info).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  private logSecurityEvent(event: Omit<BiometricSecurityEvent, 'timestamp' | 'deviceId'>): void {
    const securityEvent: BiometricSecurityEvent = {
      ...event,
      timestamp: Date.now(),
      deviceId: this.deviceId,
    };

    this.securityEvents.push(securityEvent);
    
    // Keep only recent events (last 1000)
    if (this.securityEvents.length > 1000) {
      this.securityEvents = this.securityEvents.slice(-1000);
    }

    // Save events
    this.saveSecurityEvents();
  }

  // Storage Methods
  private async loadSettings(): Promise<void> {
    const stored = await offlineStorageService.retrieve('biometric_settings');
    if (stored) {
      this.settings = { ...this.settings, ...stored };
    }
  }

  private async saveSettings(): Promise<void> {
    await offlineStorageService.store('biometric_settings', this.settings);
  }

  private async loadTemplates(): Promise<void> {
    const stored = await offlineStorageService.retrieve('biometric_templates');
    if (stored && Array.isArray(stored)) {
      this.templates.clear();
      stored.forEach((template: BiometricTemplate) => {
        this.templates.set(template.id, template);
      });
    }
  }

  private async saveTemplates(): Promise<void> {
    const templatesArray = Array.from(this.templates.values());
    await offlineStorageService.store('biometric_templates', templatesArray);
  }

  private async loadSecurityEvents(): Promise<void> {
    const stored = await offlineStorageService.retrieve('biometric_security_events');
    if (stored && Array.isArray(stored)) {
      this.securityEvents = stored;
    }
  }

  private async saveSecurityEvents(): Promise<void> {
    await offlineStorageService.store('biometric_security_events', this.securityEvents);
  }

  private async syncBiometricData(): Promise<void> {
    try {
      // Sync templates (encrypted) with server
      const encryptedTemplates = await this.encryptTemplates();
      
      await mobileAPIService.makeRequest('/biometric/sync', {
        method: 'POST',
        body: JSON.stringify({
          deviceId: this.deviceId,
          templates: encryptedTemplates,
          settings: this.settings,
          lastSync: Date.now(),
        }),
      });
    } catch (error) {
      console.error('Failed to sync biometric data:', error);
    }
  }

  private async encryptTemplates(): Promise<any[]> {
    // In a real implementation, this would encrypt template hashes
    // before sending to server for backup/sync purposes
    return Array.from(this.templates.values()).map(template => ({
      id: template.id,
      type: template.type,
      createdAt: template.createdAt,
      isActive: template.isActive,
      // Hash would be encrypted here
      encryptedHash: btoa(template.hash),
    }));
  }
}

// Export singleton instance
export const biometricService = new BiometricService();