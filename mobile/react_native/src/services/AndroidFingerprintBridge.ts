/**
 * Android Native Bridge - Fingerprint Authentication Service
 * 
 * Bridges Android Kotlin fingerprint authentication with React Native
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { NativeModules, Platform } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';

interface FingerprintOptions {
  title?: string;
  subtitle?: string;
  description?: string;
  fallbackLabel?: string;
  negativeText?: string;
}

interface FingerprintResult {
  success: boolean;
  error?: string;
  authType?: string;
}

const { FingerprintAuth, PermissionManager, SyncService } = NativeModules;

class AndroidFingerprintBridge {
  static async isAvailable(): Promise<boolean> {
    if (Platform.OS !== 'android') return false;
    
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      
      // Check native Android capability
      if (FingerprintAuth) {
        const nativeSupported = await FingerprintAuth.isSupported();
        return hasHardware && isEnrolled && nativeSupported;
      }
      
      return hasHardware && isEnrolled;
    } catch (error) {
      console.error('Fingerprint availability check failed:', error);
      return false;
    }
  }

  static async authenticate(options: FingerprintOptions = {}): Promise<FingerprintResult> {
    if (Platform.OS !== 'android') {
      return { success: false, error: 'Android only feature' };
    }

    try {
      const isAvailable = await this.isAvailable();
      if (!isAvailable) {
        return { success: false, error: 'Fingerprint authentication not available' };
      }

      // Try native Android authentication first
      if (FingerprintAuth) {
        try {
          const nativeResult = await FingerprintAuth.authenticate({
            title: options.title || 'Authenticate',
            subtitle: options.subtitle || 'Use your fingerprint to verify your identity',
            description: options.description || 'Place your finger on the fingerprint sensor',
            negativeText: options.negativeText || 'Cancel',
            maxAttempts: 5,
            lockoutDuration: 30000,
          });

          if (nativeResult.success) {
            await this.recordSuccessfulAuth();
            return { 
              success: true, 
              authType: nativeResult.authType || 'fingerprint' 
            };
          } else {
            return { 
              success: false, 
              error: nativeResult.error || 'Authentication failed' 
            };
          }
        } catch (nativeError) {
          console.warn('Native fingerprint auth failed, falling back to Expo:', nativeError);
        }
      }

      // Fallback to Expo authentication
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: options.title || 'Authenticate to access Ainflue',
        fallbackLabel: options.fallbackLabel || 'Use PIN',
        disableDeviceFallback: false,
      });

      if (result.success) {
        await this.recordSuccessfulAuth();
        return { success: true, authType: 'fingerprint' };
      } else {
        return { 
          success: false, 
          error: result.success ? undefined : 'Authentication failed' 
        };
      }
    } catch (error) {
      console.error('Fingerprint authentication error:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Authentication failed' 
      };
    }
  }

  static async authenticateForUpload(): Promise<FingerprintResult> {
    return this.authenticate({
      title: 'Secure Upload',
      subtitle: 'Authenticate to upload content',
      description: 'Your content will be protected and processed with AI',
    });
  }

  static async authenticateForSensitiveAction(action: string): Promise<FingerprintResult> {
    return this.authenticate({
      title: 'Secure Action',
      subtitle: `Authenticate for ${action}`,
      description: 'This action requires verification for security',
    });
  }

  private static async recordSuccessfulAuth(): Promise<void> {
    try {
      if (FingerprintAuth) {
        await FingerprintAuth.recordAuthentication({
          timestamp: Date.now(),
          type: 'fingerprint',
          success: true,
        });
      }
    } catch (error) {
      console.warn('Failed to record authentication:', error);
    }
  }

  // Permission management through native bridge
  static async requestPermissions(): Promise<boolean> {
    if (Platform.OS !== 'android') return false;

    try {
      if (PermissionManager) {
        const permissions = await PermissionManager.requestMultiplePermissions([
          'android.permission.USE_FINGERPRINT',
          'android.permission.USE_BIOMETRIC',
          'android.permission.CAMERA',
          'android.permission.RECORD_AUDIO',
          'android.permission.READ_EXTERNAL_STORAGE',
          'android.permission.WRITE_EXTERNAL_STORAGE',
        ]);

        return permissions.allGranted;
      }
      return false;
    } catch (error) {
      console.error('Permission request failed:', error);
      return false;
    }
  }

  static async checkPermissions(): Promise<{ [key: string]: boolean }> {
    if (Platform.OS !== 'android') return {};

    try {
      if (PermissionManager) {
        return await PermissionManager.checkPermissions([
          'fingerprint',
          'biometric',
          'camera',
          'audio',
          'storage',
        ]);
      }
      return {};
    } catch (error) {
      console.error('Permission check failed:', error);
      return {};
    }
  }

  // Sync service integration
  static async enableBackgroundSync(): Promise<boolean> {
    if (Platform.OS !== 'android') return false;

    try {
      if (SyncService) {
        return await SyncService.enableBackgroundSync({
          interval: 300000, // 5 minutes
          requiresCharging: false,
          requiresWifi: false,
          batchSize: 50,
        });
      }
      return false;
    } catch (error) {
      console.error('Background sync setup failed:', error);
      return false;
    }
  }

  static async syncPendingUploads(): Promise<boolean> {
    if (Platform.OS !== 'android') return false;

    try {
      if (SyncService) {
        const result = await SyncService.syncPendingUploads();
        console.log(`Synced ${result.count} pending uploads`);
        return result.success;
      }
      return false;
    } catch (error) {
      console.error('Upload sync failed:', error);
      return false;
    }
  }

  // Secure content storage
  static async storeContentSecurely(contentId: string, data: any): Promise<boolean> {
    try {
      const authResult = await this.authenticate({
        title: 'Secure Storage',
        subtitle: 'Authenticate to store content securely',
      });

      if (!authResult.success) {
        return false;
      }

      if (FingerprintAuth) {
        return await FingerprintAuth.storeEncrypted(contentId, JSON.stringify(data));
      }

      // Fallback to Expo SecureStore
      const SecureStore = await import('expo-secure-store');
      await SecureStore.setItemAsync(contentId, JSON.stringify(data), {
        requireAuthentication: true,
      });
      
      return true;
    } catch (error) {
      console.error('Secure content storage failed:', error);
      return false;
    }
  }

  static async getSecureContent(contentId: string): Promise<any | null> {
    try {
      const authResult = await this.authenticate({
        title: 'Access Content',
        subtitle: 'Authenticate to access secure content',
      });

      if (!authResult.success) {
        return null;
      }

      if (FingerprintAuth) {
        const encrypted = await FingerprintAuth.getEncrypted(contentId);
        return encrypted ? JSON.parse(encrypted) : null;
      }

      // Fallback to Expo SecureStore
      const SecureStore = await import('expo-secure-store');
      const stored = await SecureStore.getItemAsync(contentId, {
        requireAuthentication: true,
      });
      
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Secure content retrieval failed:', error);
      return null;
    }
  }
}

export default AndroidFingerprintBridge;