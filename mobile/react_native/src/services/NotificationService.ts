/**
 * Notification Service - Expo-powered Push Notifications
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

export class NotificationService {
  private static expoPushToken: string | null = null;

  static async initialize(): Promise<void> {
    try {
      if (Device.isDevice) {
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;
        
        if (existingStatus !== 'granted') {
          const { status } = await Notifications.requestPermissionsAsync();
          finalStatus = status;
        }
        
        if (finalStatus !== 'granted') {
          console.warn('Failed to get push token for push notifications!');
          return;
        }
        
        this.expoPushToken = (await Notifications.getExpoPushTokenAsync()).data;
        console.log('📱 Push token:', this.expoPushToken);
      } else {
        console.warn('Must use physical device for Push Notifications');
      }

      if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('default', {
          name: 'Ainflue Notifications',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#3B82F6',
        });
      }
    } catch (error) {
      console.error('Notification service initialization failed:', error);
    }
  }

  static async sendUploadComplete(fileName: string): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🎉 Upload Complete!',
        body: `${fileName} has been processed with AI enhancement`,
        data: { type: 'upload_complete', fileName },
        sound: true,
      },
      trigger: { seconds: 1 },
    });
  }

  static async sendAIProcessingComplete(fileName: string, qualityScore: number): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🤖 AI Processing Complete',
        body: `${fileName} - Quality Score: ${qualityScore}%`,
        data: { type: 'ai_complete', fileName, qualityScore },
        sound: true,
      },
      trigger: { seconds: 1 },
    });
  }

  static async sendContentProtected(fileName: string): Promise<void> {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🛡️ Content Protected',
        body: `${fileName} is now secured with watermark and fingerprinting`,
        data: { type: 'content_protected', fileName },
        sound: true,
      },
      trigger: { seconds: 1 },
    });
  }

  static getExpoPushToken(): string | null {
    return this.expoPushToken;
  }
}