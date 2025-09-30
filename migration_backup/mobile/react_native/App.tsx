/**
 * Ainflue Mobile App - Expo React Native Entry Point
 * 
 * Professional mobile content creation platform with AI-powered editing,
 * multi-format upload, and advanced protection features.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as Notifications from 'expo-notifications';
import * as LocalAuthentication from 'expo-local-authentication';

import AppNavigator from './src/navigation/AppNavigator';
import { AuthProvider } from './src/services/AuthContext';
import { ThemeProvider } from './src/services/ThemeContext';
import { NotificationService } from './src/services/NotificationService';

// Configure notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const App: React.FC = () => {
  React.useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize notification permissions
      await NotificationService.initialize();
      
      // Check biometric availability
      const biometricTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();
      console.log('📱 Available biometric types:', biometricTypes);
      
      // Initialize core mobile services
      console.log('✅ Ainflue mobile app initialized');
    } catch (error) {
      console.error('❌ App initialization failed:', error);
    }
  };

  return (
    <SafeAreaProvider>
      <StatusBar style="light" backgroundColor="#1f2937" />
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

export default App;