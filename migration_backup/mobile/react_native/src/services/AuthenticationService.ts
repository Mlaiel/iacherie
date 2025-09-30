/**
 * Unified Authentication Service
 * 
 * Cross-platform authentication service that automatically selects
 * the appropriate biometric authentication method based on platform
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { Platform } from 'react-native';
import iOSBiometricBridge from './iOSBiometricBridge';
import AndroidFingerprintBridge from './AndroidFingerprintBridge';

interface AuthenticationOptions {
  promptMessage?: string;
  subtitle?: string;
  fallbackLabel?: string;
  purpose?: 'upload' | 'access' | 'settings' | 'general';
}

interface AuthenticationResult {
  success: boolean;
  error?: string;
  authType?: string;
  platform?: string;
}

interface AuthenticationCapabilities {
  isAvailable: boolean;
  supportedTypes: string[];
  platform: string;
  nativeBridgeAvailable: boolean;
}

export class AuthenticationService {
  private static instance: AuthenticationService;
  private initialized = false;

  static getInstance(): AuthenticationService {
    if (!AuthenticationService.instance) {
      AuthenticationService.instance = new AuthenticationService();
    }
    return AuthenticationService.instance;
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    console.log('🔐 Initializing Authentication Service...');
    
    try {
      // Initialize platform-specific services
      if (Platform.OS === 'android') {
        const permissionsGranted = await AndroidFingerprintBridge.requestPermissions();
        if (!permissionsGranted) {
          console.warn('⚠️ Not all Android permissions granted');
        }
        
        // Enable background sync for authenticated content
        await AndroidFingerprintBridge.enableBackgroundSync();
      }

      this.initialized = true;
      console.log('✅ Authentication Service initialized');
    } catch (error) {
      console.error('❌ Authentication Service initialization failed:', error);
      throw error;
    }
  }

  async getCapabilities(): Promise<AuthenticationCapabilities> {
    const platform = Platform.OS;
    
    if (platform === 'ios') {
      const isAvailable = await iOSBiometricBridge.isAvailable();
      const supportedTypes = await iOSBiometricBridge.getSupportedTypes();
      
      return {
        isAvailable,
        supportedTypes,
        platform: 'iOS',
        nativeBridgeAvailable: true,
      };
    } else if (platform === 'android') {
      const isAvailable = await AndroidFingerprintBridge.isAvailable();
      const permissions = await AndroidFingerprintBridge.checkPermissions();
      
      return {
        isAvailable,
        supportedTypes: ['Fingerprint', 'Biometric'],
        platform: 'Android',
        nativeBridgeAvailable: permissions.fingerprint && permissions.biometric,
      };
    } else {
      return {
        isAvailable: false,
        supportedTypes: [],
        platform: platform || 'Unknown',
        nativeBridgeAvailable: false,
      };
    }
  }

  async authenticate(options: AuthenticationOptions = {}): Promise<AuthenticationResult> {
    try {
      await this.initialize();

      const capabilities = await this.getCapabilities();
      
      if (!capabilities.isAvailable) {
        return {
          success: false,
          error: 'Biometric authentication not available on this device',
          platform: capabilities.platform,
        };
      }

      let result: any;
      
      if (Platform.OS === 'ios') {
        result = await iOSBiometricBridge.authenticate({
          promptMessage: this.getPromptMessage(options),
          fallbackLabel: options.fallbackLabel,
          disableDeviceFallback: false,
        });
      } else if (Platform.OS === 'android') {
        result = await AndroidFingerprintBridge.authenticate({
          title: this.getPromptTitle(options),
          subtitle: options.subtitle || this.getPromptMessage(options),
          fallbackLabel: options.fallbackLabel,
        });
      } else {
        return {
          success: false,
          error: 'Platform not supported',
          platform: Platform.OS,
        };
      }

      return {
        ...result,
        platform: capabilities.platform,
      };
    } catch (error) {
      console.error('Authentication failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Authentication failed',
        platform: Platform.OS,
      };
    }
  }

  async authenticateForUpload(): Promise<AuthenticationResult> {
    if (Platform.OS === 'ios') {
      const result = await iOSBiometricBridge.authenticateForUpload();
      return { ...result, platform: 'iOS' };
    } else if (Platform.OS === 'android') {
      const result = await AndroidFingerprintBridge.authenticateForUpload();
      return { ...result, platform: 'Android' };
    } else {
      return {
        success: false,
        error: 'Platform not supported',
        platform: Platform.OS,
      };
    }
  }

  async authenticateForContentAccess(contentId: string): Promise<AuthenticationResult> {
    if (Platform.OS === 'ios') {
      const result = await iOSBiometricBridge.authenticateForContent(contentId);
      return { ...result, platform: 'iOS' };
    } else if (Platform.OS === 'android') {
      const result = await AndroidFingerprintBridge.authenticateForSensitiveAction('content access');
      return { ...result, platform: 'Android' };
    } else {
      return {
        success: false,
        error: 'Platform not supported',
        platform: Platform.OS,
      };
    }
  }

  async storeSecureData(key: string, data: string): Promise<boolean> {
    try {
      if (Platform.OS === 'ios') {
        return await iOSBiometricBridge.storeSecureData(key, data);
      } else if (Platform.OS === 'android') {
        return await AndroidFingerprintBridge.storeContentSecurely(key, data);
      }
      return false;
    } catch (error) {
      console.error('Secure storage failed:', error);
      return false;
    }
  }

  async getSecureData(key: string): Promise<string | null> {
    try {
      if (Platform.OS === 'ios') {
        return await iOSBiometricBridge.getSecureData(key);
      } else if (Platform.OS === 'android') {
        const data = await AndroidFingerprintBridge.getSecureContent(key);
        return typeof data === 'string' ? data : JSON.stringify(data);
      }
      return null;
    } catch (error) {
      console.error('Secure data retrieval failed:', error);
      return null;
    }
  }

  // Platform-specific background operations
  async syncOfflineContent(): Promise<boolean> {
    if (Platform.OS === 'android') {
      return await AndroidFingerprintBridge.syncPendingUploads();
    }
    
    // iOS would use background app refresh and sync through the backend
    console.log('iOS background sync triggered');
    return true;
  }

  private getPromptMessage(options: AuthenticationOptions): string {
    if (options.promptMessage) return options.promptMessage;
    
    switch (options.purpose) {
      case 'upload':
        return 'Authenticate to upload and process your content securely';
      case 'access':
        return 'Authenticate to access your protected content';
      case 'settings':
        return 'Authenticate to modify security settings';
      default:
        return 'Authenticate to access Ainflue';
    }
  }

  private getPromptTitle(options: AuthenticationOptions): string {
    switch (options.purpose) {
      case 'upload':
        return 'Secure Upload';
      case 'access':
        return 'Content Access';
      case 'settings':
        return 'Security Settings';
      default:
        return 'Ainflue Authentication';
    }
  }

  // Utility methods for checking authentication state
  async isAuthenticationRequired(): Promise<boolean> {
    // Check app settings to see if authentication is required
    try {
      const capabilities = await this.getCapabilities();
      return capabilities.isAvailable;
    } catch {
      return false;
    }
  }

  async canAuthenticateWithBiometrics(): Promise<boolean> {
    try {
      const capabilities = await this.getCapabilities();
      return capabilities.isAvailable && capabilities.nativeBridgeAvailable;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export default AuthenticationService.getInstance();