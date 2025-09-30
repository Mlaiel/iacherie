/**
 * Ainflue Android Application - Main Entry Point
 * 
 * Advanced mobile content creation platform for multi-format creators
 * Integrates AI-powered protection, monetization, and collaboration features
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited under
 * German and international copyright law.
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  Alert,
  BackHandler,
  AppState,
  AppStateStatus,
  Permission,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import NetInfo from '@react-native-community/netinfo';

// Import native Android modules
import { AudioRecorder } from './AudioRecorder';
import { CameraManager } from './CameraManager';
import { FingerprintAuth } from './FingerprintAuth';
import { NotificationService } from './NotificationService';
import { SyncService } from './SyncService';
import { PermissionManager } from './PermissionManager';

// Import React Native components
import AppNavigator from '../react_native/src/navigation/AppNavigator';
import { AuthProvider } from '../react_native/src/services/AuthContext';
import { ThemeProvider } from '../react_native/src/services/ThemeContext';
import ApiService from '../react_native/src/services/ApiService';

interface AppState {
  isInitialized: boolean;
  hasPermissions: boolean;
  isAuthenticated: boolean;
  networkStatus: boolean;
  syncStatus: 'idle' | 'syncing' | 'complete' | 'error';
}

interface NativeServiceStatus {
  audioRecorder: boolean;
  cameraManager: boolean;
  fingerprintAuth: boolean;
  notifications: boolean;
  syncService: boolean;
  permissions: boolean;
}

const AinflueMobileApp: React.FC = () => {
  const [appState, setAppState] = useState<AppState>({
    isInitialized: false,
    hasPermissions: false,
    isAuthenticated: false,
    networkStatus: false,
    syncStatus: 'idle',
  });

  const [nativeServices, setNativeServices] = useState<NativeServiceStatus>({
    audioRecorder: false,
    cameraManager: false,
    fingerprintAuth: false,
    notifications: false,
    syncService: false,
    permissions: false,
  });

  useEffect(() => {
    initializeApplication();
    setupAppStateListener();
    setupBackHandler();
    setupNetworkListener();

    return () => {
      cleanupApplication();
    };
  }, []);

  /**
   * Initialize the entire application with all native services
   */
  const initializeApplication = async (): Promise<void> => {
    try {
      console.log('🚀 Initializing Ainflue Mobile Application...');

      // Step 1: Initialize permissions
      const permissionsGranted = await initializePermissions();
      if (!permissionsGranted) {
        throw new Error('Required permissions not granted');
      }

      // Step 2: Initialize native services
      await initializeNativeServices();

      // Step 3: Initialize authentication
      await initializeAuthentication();

      // Step 4: Setup synchronization
      await initializeSynchronization();

      // Step 5: Final initialization
      setAppState(prev => ({
        ...prev,
        isInitialized: true,
        hasPermissions: true,
      }));

      console.log('✅ Application initialization complete');

    } catch (error) {
      console.error('❌ Application initialization failed:', error);
      handleInitializationError(error);
    }
  };

  /**
   * Initialize and request all required permissions
   */
  const initializePermissions = async (): Promise<boolean> => {
    try {
      console.log('📱 Initializing permissions...');

      const permissionResults = await PermissionManager.requestAllPermissions();
      
      const requiredPermissions = [
        'camera',
        'microphone',
        'storage',
        'notifications',
        'location',
        'contacts'
      ];

      const allGranted = requiredPermissions.every(
        permission => permissionResults[permission] === 'granted'
      );

      setNativeServices(prev => ({ ...prev, permissions: allGranted }));
      
      if (!allGranted) {
        Alert.alert(
          'Permissions Required',
          'Ainflue requires certain permissions to function properly. Please grant all permissions in settings.',
          [
            { text: 'Settings', onPress: () => PermissionManager.openSettings() },
            { text: 'Exit', onPress: () => BackHandler.exitApp() }
          ]
        );
        return false;
      }

      console.log('✅ All permissions granted');
      return true;

    } catch (error) {
      console.error('❌ Permission initialization failed:', error);
      return false;
    }
  };

  /**
   * Initialize all native Android services
   */
  const initializeNativeServices = async (): Promise<void> => {
    try {
      console.log('🔧 Initializing native services...');

      // Initialize Audio Recorder
      const audioInitialized = await AudioRecorder.initialize({
        sampleRate: 44100,
        channels: 2,
        bitsPerSample: 16,
        audioSource: 'MIC',
        outputFormat: 'MPEG_4',
        audioEncoder: 'AAC',
        enableNoiseReduction: true,
        enableEchoCancellation: true
      });

      // Initialize Camera Manager
      const cameraInitialized = await CameraManager.initialize({
        preferredResolution: '1920x1080',
        enableImageStabilization: true,
        enableAutoFocus: true,
        enableFlash: true,
        captureMode: 'photo_video'
      });

      // Initialize Fingerprint Authentication
      const fingerprintInitialized = await FingerprintAuth.initialize({
        enableFallbackPassword: true,
        maxAttempts: 5,
        lockoutDuration: 300000,
        requireSecureLockScreen: true
      });

      // Initialize Notification Service
      const notificationsInitialized = await NotificationService.initialize({
        projectId: 'ainflue-mobile',
        senderId: '123456789',
        enableAnalytics: true,
        enableMessaging: true,
        enableRemoteNotifications: true
      });

      // Initialize Sync Service
      const syncInitialized = await SyncService.initialize({
        syncInterval: 300000, // 5 minutes
        batchSize: 100,
        enableBackgroundSync: true,
        enableCompression: true,
        maxRetries: 3
      });

      setNativeServices({
        audioRecorder: audioInitialized,
        cameraManager: cameraInitialized,
        fingerprintAuth: fingerprintInitialized,
        notifications: notificationsInitialized,
        syncService: syncInitialized,
        permissions: true
      });

      console.log('✅ Native services initialized');

    } catch (error) {
      console.error('❌ Native services initialization failed:', error);
      throw error;
    }
  };

  /**
   * Initialize authentication services
   */
  const initializeAuthentication = async (): Promise<void> => {
    try {
      console.log('🔐 Initializing authentication...');

      // Check for existing authentication
      const isAuthenticated = await ApiService.getUserProfile()
        .then(() => true)
        .catch(() => false);

      if (isAuthenticated) {
        // Setup biometric authentication if available
        const biometricAvailable = await FingerprintAuth.isBiometricAvailable();
        if (biometricAvailable) {
          await FingerprintAuth.enableBiometricAuth();
        }
      }

      setAppState(prev => ({ ...prev, isAuthenticated }));
      console.log(`✅ Authentication status: ${isAuthenticated ? 'authenticated' : 'not authenticated'}`);

    } catch (error) {
      console.error('❌ Authentication initialization failed:', error);
    }
  };

  /**
   * Initialize synchronization services
   */
  const initializeSynchronization = async (): Promise<void> => {
    try {
      console.log('🔄 Initializing synchronization...');

      setAppState(prev => ({ ...prev, syncStatus: 'syncing' }));

      // Start initial sync
      await SyncService.performInitialSync();

      // Setup periodic sync
      SyncService.startPeriodicSync();

      setAppState(prev => ({ ...prev, syncStatus: 'complete' }));
      console.log('✅ Synchronization initialized');

    } catch (error) {
      console.error('❌ Synchronization initialization failed:', error);
      setAppState(prev => ({ ...prev, syncStatus: 'error' }));
    }
  };

  /**
   * Setup app state change listener
   */
  const setupAppStateListener = (): void => {
    const handleAppStateChange = (nextAppState: AppStateStatus) => {
      if (nextAppState === 'active') {
        // App became active
        console.log('📱 App became active');
        SyncService.resumeSync();
      } else if (nextAppState === 'background') {
        // App went to background
        console.log('📱 App went to background');
        SyncService.pauseSync();
      }
    };

    AppState.addEventListener('change', handleAppStateChange);
  };

  /**
   * Setup back button handler
   */
  const setupBackHandler = (): void => {
    const backAction = () => {
      Alert.alert('Hold on!', 'Are you sure you want to exit Ainflue?', [
        { text: 'Cancel', onPress: () => null, style: 'cancel' },
        { text: 'YES', onPress: () => BackHandler.exitApp() },
      ]);
      return true;
    };

    const backHandler = BackHandler.addEventListener('hardwareBackPress', backAction);
    return () => backHandler.remove();
  };

  /**
   * Setup network connectivity listener
   */
  const setupNetworkListener = (): void => {
    const unsubscribe = NetInfo.addEventListener(state => {
      const isConnected = state.isConnected || false;
      setAppState(prev => ({ ...prev, networkStatus: isConnected }));

      if (isConnected) {
        console.log('🌐 Network connected - resuming sync');
        SyncService.resumeSync();
      } else {
        console.log('🌐 Network disconnected - pausing sync');
        SyncService.pauseSync();
      }
    });
  };

  /**
   * Handle initialization errors
   */
  const handleInitializationError = (error: any): void => {
    Alert.alert(
      'Initialization Error',
      'Failed to initialize Ainflue. Please restart the application.',
      [
        { text: 'Retry', onPress: () => initializeApplication() },
        { text: 'Exit', onPress: () => BackHandler.exitApp() }
      ]
    );
  };

  /**
   * Cleanup application resources
   */
  const cleanupApplication = async (): Promise<void> => {
    try {
      console.log('🧹 Cleaning up application resources...');

      await Promise.all([
        AudioRecorder.cleanup(),
        CameraManager.cleanup(),
        SyncService.cleanup(),
        NotificationService.cleanup()
      ]);

      console.log('✅ Application cleanup complete');

    } catch (error) {
      console.error('❌ Application cleanup failed:', error);
    }
  };

  // Show loading screen while initializing
  if (!appState.isInitialized) {
    return (
      <SafeAreaProvider>
        <StatusBar barStyle="light-content" backgroundColor="#1f2937" />
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingTitle}>Ainflue</Text>
          <Text style={styles.loadingSubtitle}>Initializing...</Text>
          <View style={styles.servicesStatus}>
            {Object.entries(nativeServices).map(([service, status]) => (
              <Text key={service} style={[styles.serviceStatus, { color: status ? '#10b981' : '#f59e0b' }]}>
                {service}: {status ? '✅' : '⏳'}
              </Text>
            ))}
          </View>
        </View>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="light-content" backgroundColor="#1f2937" />
      <ThemeProvider>
        <AuthProvider>
          <NavigationContainer>
            <AppNavigator />
          </NavigationContainer>
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1f2937',
    padding: 20,
  },
  loadingTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
  },
  loadingSubtitle: {
    fontSize: 16,
    color: '#9ca3af',
    marginBottom: 30,
  },
  servicesStatus: {
    alignItems: 'center',
  },
  serviceStatus: {
    fontSize: 14,
    marginVertical: 2,
    fontFamily: 'monospace',
  },
});

export default AinflueMobileApp;