/**
 * Notification Manager - Central push notification management service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { FirebaseService } from './firebase_service';
import { APNSService } from './apns_service';
import { AnalyticsService } from './analytics_service';
import { TokenManager } from '../utils/token_manager';
import { DeliveryTracker } from '../utils/delivery_tracker';
import { RetryHandler } from '../utils/retry_handler';
import { 
  NotificationPayload, 
  NotificationResult, 
  UserPreferences,
  NotificationAnalytics,
  HealthStatus
} from '../types/notification_types';

export class NotificationManager {
  private static instance: NotificationManager;
  private firebaseService: FirebaseService;
  private apnsService: APNSService;
  private analyticsService: AnalyticsService;
  private tokenManager: TokenManager;
  private deliveryTracker: DeliveryTracker;
  private retryHandler: RetryHandler;
  private isInitialized: boolean = false;
  private debugMode: boolean = false;

  private constructor() {
    this.firebaseService = new FirebaseService();
    this.apnsService = new APNSService();
    this.analyticsService = new AnalyticsService();
    this.tokenManager = new TokenManager();
    this.deliveryTracker = new DeliveryTracker();
    this.retryHandler = new RetryHandler();
  }

  public static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager();
    }
    return NotificationManager.instance;
  }

  /**
   * Initialize the notification system
   */
  public async initialize(): Promise<void> {
    try {
      if (this.isInitialized) {
        return;
      }

      // Initialize services
      await this.firebaseService.initialize();
      await this.apnsService.initialize();
      await this.analyticsService.initialize();
      await this.tokenManager.initialize();

      // Set up event listeners
      this.setupEventListeners();

      this.isInitialized = true;
      this.log('NotificationManager initialized successfully');
    } catch (error) {
      this.log('Failed to initialize NotificationManager:', error);
      throw error;
    }
  }

  /**
   * Request notification permissions from the user
   */
  public async requestPermissions(): Promise<boolean> {
    try {
      const firebasePermission = await this.firebaseService.requestPermissions();
      const apnsPermission = await this.apnsService.requestPermissions();
      
      const hasPermissions = firebasePermission || apnsPermission;
      
      if (hasPermissions) {
        await this.registerDeviceToken();
      }

      return hasPermissions;
    } catch (error) {
      this.log('Failed to request permissions:', error);
      return false;
    }
  }

  /**
   * Send a single notification
   */
  public async sendNotification(payload: NotificationPayload): Promise<NotificationResult> {
    try {
      this.validatePayload(payload);

      const startTime = Date.now();
      let result: NotificationResult;

      // Determine which service to use based on target platform
      if (payload.platform === 'ios') {
        result = await this.apnsService.send(payload);
      } else if (payload.platform === 'android') {
        result = await this.firebaseService.send(payload);
      } else {
        // Send to both platforms for cross-platform support
        const [firebaseResult, apnsResult] = await Promise.allSettled([
          this.firebaseService.send(payload),
          this.apnsService.send(payload)
        ]);

        result = {
          success: firebaseResult.status === 'fulfilled' || apnsResult.status === 'fulfilled',
          messageId: this.generateMessageId(),
          timestamp: new Date().toISOString(),
          platform: 'cross-platform',
          details: {
            firebase: firebaseResult.status === 'fulfilled' ? firebaseResult.value : null,
            apns: apnsResult.status === 'fulfilled' ? apnsResult.value : null
          }
        };
      }

      // Track delivery
      await this.deliveryTracker.track({
        messageId: result.messageId,
        userId: payload.userId,
        notificationType: payload.type,
        platform: payload.platform || 'cross-platform',
        sent: true,
        deliveryTime: Date.now() - startTime
      });

      // Record analytics
      await this.analyticsService.recordNotification({
        userId: payload.userId,
        type: payload.type,
        platform: payload.platform || 'cross-platform',
        success: result.success,
        timestamp: new Date()
      });

      // Handle retry if failed
      if (!result.success && payload.retryOnFailure !== false) {
        await this.retryHandler.scheduleRetry(payload, result);
      }

      return result;
    } catch (error) {
      this.log('Failed to send notification:', error);
      
      const failureResult: NotificationResult = {
        success: false,
        messageId: this.generateMessageId(),
        timestamp: new Date().toISOString(),
        platform: payload.platform || 'unknown',
        error: error instanceof Error ? error.message : 'Unknown error'
      };

      // Still track the failure
      await this.analyticsService.recordNotification({
        userId: payload.userId,
        type: payload.type,
        platform: payload.platform || 'unknown',
        success: false,
        timestamp: new Date(),
        error: failureResult.error
      });

      return failureResult;
    }
  }

  /**
   * Send bulk notifications
   */
  public async sendBulkNotifications(payloads: NotificationPayload[]): Promise<NotificationResult[]> {
    const results: NotificationResult[] = [];
    const batchSize = 100; // Process in batches to avoid overwhelming the services

    for (let i = 0; i < payloads.length; i += batchSize) {
      const batch = payloads.slice(i, i + batchSize);
      const batchPromises = batch.map(payload => this.sendNotification(payload));
      const batchResults = await Promise.allSettled(batchPromises);

      batchResults.forEach(result => {
        if (result.status === 'fulfilled') {
          results.push(result.value);
        } else {
          results.push({
            success: false,
            messageId: this.generateMessageId(),
            timestamp: new Date().toISOString(),
            platform: 'unknown',
            error: result.reason?.message || 'Batch processing failed'
          });
        }
      });

      // Add small delay between batches to respect rate limits
      if (i + batchSize < payloads.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    return results;
  }

  /**
   * Subscribe user to notification topic
   */
  public async subscribeToTopic(userId: string, topic: string): Promise<boolean> {
    try {
      const tokens = await this.tokenManager.getUserTokens(userId);
      
      const firebaseResults = await Promise.allSettled(
        tokens.firebase.map(token => this.firebaseService.subscribeToTopic(token, topic))
      );

      const apnsResults = await Promise.allSettled(
        tokens.apns.map(token => this.apnsService.subscribeToTopic(token, topic))
      );

      const successCount = [
        ...firebaseResults.filter(r => r.status === 'fulfilled'),
        ...apnsResults.filter(r => r.status === 'fulfilled')
      ].length;

      return successCount > 0;
    } catch (error) {
      this.log('Failed to subscribe to topic:', error);
      return false;
    }
  }

  /**
   * Unsubscribe user from notification topic
   */
  public async unsubscribeFromTopic(userId: string, topic: string): Promise<boolean> {
    try {
      const tokens = await this.tokenManager.getUserTokens(userId);
      
      const firebaseResults = await Promise.allSettled(
        tokens.firebase.map(token => this.firebaseService.unsubscribeFromTopic(token, topic))
      );

      const apnsResults = await Promise.allSettled(
        tokens.apns.map(token => this.apnsService.unsubscribeFromTopic(token, topic))
      );

      const successCount = [
        ...firebaseResults.filter(r => r.status === 'fulfilled'),
        ...apnsResults.filter(r => r.status === 'fulfilled')
      ].length;

      return successCount > 0;
    } catch (error) {
      this.log('Failed to unsubscribe from topic:', error);
      return false;
    }
  }

  /**
   * Update user notification preferences
   */
  public async updateUserPreferences(userId: string, preferences: UserPreferences): Promise<boolean> {
    try {
      await this.tokenManager.updateUserPreferences(userId, preferences);
      
      // Update topic subscriptions based on preferences
      const topics = this.getTopicsFromPreferences(preferences);
      
      for (const topic of topics.subscribe) {
        await this.subscribeToTopic(userId, topic);
      }
      
      for (const topic of topics.unsubscribe) {
        await this.unsubscribeFromTopic(userId, topic);
      }

      return true;
    } catch (error) {
      this.log('Failed to update user preferences:', error);
      return false;
    }
  }

  /**
   * Get notification analytics
   */
  public async getAnalytics(options: {
    userId?: string;
    dateRange?: string;
    notificationType?: string;
  }): Promise<NotificationAnalytics> {
    return await this.analyticsService.getAnalytics(options);
  }

  /**
   * Get system health status
   */
  public async healthCheck(): Promise<HealthStatus> {
    try {
      const [firebaseHealth, apnsHealth] = await Promise.allSettled([
        this.firebaseService.healthCheck(),
        this.apnsService.healthCheck()
      ]);

      const analytics = await this.analyticsService.getRecentMetrics();

      return {
        firebase: firebaseHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
        apns: apnsHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
        deliveryRate: analytics.deliveryRate,
        avgDeliveryTime: analytics.avgDeliveryTime,
        lastChecked: new Date().toISOString()
      };
    } catch (error) {
      this.log('Health check failed:', error);
      return {
        firebase: 'unknown',
        apns: 'unknown',
        deliveryRate: 0,
        avgDeliveryTime: '0s',
        lastChecked: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Enable or disable debug mode
   */
  public setDebugMode(enabled: boolean): void {
    this.debugMode = enabled;
    this.firebaseService.setDebugMode(enabled);
    this.apnsService.setDebugMode(enabled);
  }

  /**
   * Register device token for notifications
   */
  private async registerDeviceToken(): Promise<void> {
    try {
      const firebaseToken = await this.firebaseService.getToken();
      const apnsToken = await this.apnsService.getToken();

      if (firebaseToken) {
        await this.tokenManager.registerToken('firebase', firebaseToken);
      }

      if (apnsToken) {
        await this.tokenManager.registerToken('apns', apnsToken);
      }
    } catch (error) {
      this.log('Failed to register device token:', error);
    }
  }

  /**
   * Set up event listeners for notification events
   */
  private setupEventListeners(): void {
    // Token refresh handlers
    this.firebaseService.onTokenRefresh(async (token) => {
      await this.tokenManager.registerToken('firebase', token);
    });

    this.apnsService.onTokenRefresh(async (token) => {
      await this.tokenManager.registerToken('apns', token);
    });

    // Message handlers
    this.firebaseService.onMessage((message) => {
      this.handleIncomingMessage('firebase', message);
    });

    this.apnsService.onMessage((message) => {
      this.handleIncomingMessage('apns', message);
    });
  }

  /**
   * Handle incoming notification messages
   */
  private async handleIncomingMessage(platform: string, message: any): Promise<void> {
    try {
      // Track message reception
      await this.deliveryTracker.trackDelivery({
        messageId: message.messageId || this.generateMessageId(),
        platform,
        delivered: true,
        timestamp: new Date()
      });

      // Update analytics
      await this.analyticsService.recordDelivery({
        messageId: message.messageId,
        platform,
        delivered: true,
        opened: false, // Will be updated when user opens the notification
        timestamp: new Date()
      });

      this.log(`Received message on ${platform}:`, message);
    } catch (error) {
      this.log('Failed to handle incoming message:', error);
    }
  }

  /**
   * Validate notification payload
   */
  private validatePayload(payload: NotificationPayload): void {
    if (!payload.userId) {
      throw new Error('User ID is required');
    }

    if (!payload.title && !payload.body) {
      throw new Error('Either title or body is required');
    }

    if (!payload.type) {
      throw new Error('Notification type is required');
    }
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get topics to subscribe/unsubscribe based on preferences
   */
  private getTopicsFromPreferences(preferences: UserPreferences): {
    subscribe: string[];
    unsubscribe: string[];
  } {
    const allTopics = [
      'protection_alerts',
      'revenue_updates',
      'collaboration_requests',
      'content_updates',
      'system_notifications'
    ];

    const subscribe: string[] = [];
    const unsubscribe: string[] = [];

    allTopics.forEach(topic => {
      const key = topic as keyof UserPreferences;
      if (preferences[key]) {
        subscribe.push(topic);
      } else {
        unsubscribe.push(topic);
      }
    });

    return { subscribe, unsubscribe };
  }

  /**
   * Log debug messages
   */
  private log(...args: any[]): void {
    if (this.debugMode) {
      console.log('[NotificationManager]', ...args);
    }
  }
}

// Export singleton instance
export default NotificationManager.getInstance();