/**
 * iOS Native Bridge - Biometric Authentication Service
 * 
 * Bridges iOS Swift biometric authentication with React Native
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { NativeModules, Platform } from 'react-native';
import * as LocalAuthentication from 'expo-local-authentication';

interface BiometricOptions {
  promptMessage?: string;
  fallbackLabel?: string;
  disableDeviceFallback?: boolean;
}

interface BiometricResult {
  success: boolean;
  error?: string;
  biometryType?: string;
}

const { BiometricAuthService } = NativeModules;

class iOSBiometricBridge {
  static async isAvailable(): Promise<boolean> {
    if (Platform.OS !== 'ios') return false;
    
    try {
      const hasHardware = await LocalAuthentication.hasHardwareAsync();
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();
      return hasHardware && isEnrolled;
    } catch (error) {
      console.error('Biometric availability check failed:', error);
      return false;
    }
  }

  static async getSupportedTypes(): Promise<string[]> {
    if (Platform.OS !== 'ios') return [];
    
    try {
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      return types.map(type => {
        switch (type) {
          case LocalAuthentication.AuthenticationType.FINGERPRINT:
            return 'TouchID';
          case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
            return 'FaceID';
          default:
            return 'Unknown';
        }
      });
    } catch (error) {
      console.error('Failed to get biometric types:', error);
      return [];
    }
  }

  static async authenticate(options: BiometricOptions = {}): Promise<BiometricResult> {
    if (Platform.OS !== 'ios') {
      return { success: false, error: 'iOS only feature' };
    }

    try {
      const isAvailable = await this.isAvailable();
      if (!isAvailable) {
        return { success: false, error: 'Biometric authentication not available' };
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: options.promptMessage || 'Authenticate to access Ainflue',
        fallbackLabel: options.fallbackLabel || 'Use Passcode',
        disableDeviceFallback: options.disableDeviceFallback || false,
      });

      if (result.success) {
        // Call native iOS service for additional security features
        if (BiometricAuthService) {
          try {
            await BiometricAuthService.recordSuccessfulAuthentication();
          } catch (nativeError) {
            console.warn('Native authentication recording failed:', nativeError);
          }
        }

        return { 
          success: true, 
          biometryType: await this.getPrimaryBiometryType() 
        };
      } else {
        return { 
          success: false, 
          error: result.success ? undefined : 'Authentication failed' 
        };
      }
    } catch (error) {
      console.error('Biometric authentication error:', error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Authentication failed' 
      };
    }
  }

  static async authenticateForContent(contentId: string): Promise<BiometricResult> {
    const result = await this.authenticate({
      promptMessage: `Authenticate to access protected content: ${contentId}`,
      disableDeviceFallback: false,
    });

    if (result.success && BiometricAuthService) {
      try {
        await BiometricAuthService.recordContentAccess(contentId);
      } catch (error) {
        console.warn('Failed to record content access:', error);
      }
    }

    return result;
  }

  static async authenticateForUpload(): Promise<BiometricResult> {
    return this.authenticate({
      promptMessage: 'Authenticate to upload and process content',
      disableDeviceFallback: false,
    });
  }

  private static async getPrimaryBiometryType(): Promise<string> {
    try {
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      
      if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        return 'FaceID';
      } else if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        return 'TouchID';
      } else {
        return 'Passcode';
      }
    } catch (error) {
      return 'Unknown';
    }
  }

  // Secure storage with biometric protection
  static async storeSecureData(key: string, data: string): Promise<boolean> {
    try {
      const authResult = await this.authenticate({
        promptMessage: 'Authenticate to securely store data'
      });

      if (!authResult.success) {
        return false;
      }

      if (BiometricAuthService) {
        return await BiometricAuthService.storeSecureData(key, data);
      }

      // Fallback to Expo SecureStore
      const SecureStore = await import('expo-secure-store');
      await SecureStore.setItemAsync(key, data, {
        requireAuthentication: true,
        authenticationPrompt: 'Authenticate to access secure data'
      });
      
      return true;
    } catch (error) {
      console.error('Secure storage failed:', error);
      return false;
    }
  }

  static async getSecureData(key: string): Promise<string | null> {
    try {
      const authResult = await this.authenticate({
        promptMessage: 'Authenticate to access secure data'
      });

      if (!authResult.success) {
        return null;
      }

      if (BiometricAuthService) {
        return await BiometricAuthService.getSecureData(key);
      }

      // Fallback to Expo SecureStore
      const SecureStore = await import('expo-secure-store');
      return await SecureStore.getItemAsync(key, {
        requireAuthentication: true,
        authenticationPrompt: 'Authenticate to access secure data'
      });
    } catch (error) {
      console.error('Secure data retrieval failed:', error);
      return null;
    }
  }
}

export default iOSBiometricBridge;