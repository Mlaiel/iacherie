/**
 * Push Notification Service - Advanced mobile push notification management
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

export interface NotificationPayload {
  id: string;
  title: string;
  body: string;
  type: 'protection' | 'collaboration' | 'revenue' | 'content' | 'system' | 'marketing';
  priority: 'low' | 'normal' | 'high' | 'critical';
  data?: Record<string, any>;
  image?: string;
  icon?: string;
  badge?: number;
  sound?: string;
  clickAction?: string;
  deepLink?: string;
  scheduledAt?: number;
  expiresAt?: number;
}

export interface NotificationPreferences {
  enabled: boolean;
  types: {
    protection: boolean;
    collaboration: boolean;
    revenue: boolean;
    content: boolean;
    system: boolean;
    marketing: boolean;
  };
  schedule: {
    startHour: number;
    endHour: number;
    timezone: string;
    weekdays: boolean[];
  };
  sound: boolean;
  vibration: boolean;
  badge: boolean;
  preview: boolean;
}

export interface NotificationTemplate {
  id: string;
  type: string;
  title: string;
  body: string;
  variables: string[];
  localization: Record<string, { title: string; body: string }>;
}

export interface NotificationAnalytics {
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  dismissed: number;
  deliveryRate: number;
  openRate: number;
  clickRate: number;
  avgDeliveryTime: number;
}

export interface PushToken {
  token: string;
  platform: 'ios' | 'android' | 'web';
  userId: string;
  deviceId: string;
  appVersion: string;
  registeredAt: number;
  lastUsed: number;
  isActive: boolean;
}

export interface NotificationAction {
  id: string;
  title: string;
  icon?: string;
  input?: boolean;
  destructive?: boolean;
}

export interface RichNotification extends NotificationPayload {
  actions?: NotificationAction[];
  category?: string;
  attachments?: {
    url: string;
    type: 'image' | 'video' | 'audio';
    thumbnail?: string;
  }[];
  customData?: Record<string, any>;
}

export class PushNotificationService {
  private isInitialized: boolean = false;
  private pushToken: string | null = null;
  private preferences: NotificationPreferences;
  private templates: Map<string, NotificationTemplate> = new Map();
  private pendingNotifications: Map<string, NotificationPayload> = new Map();
  private notificationHistory: NotificationPayload[] = [];
  private analytics: NotificationAnalytics;
  private serviceWorkerRegistration: ServiceWorkerRegistration | null = null;

  constructor() {
    this.preferences = {
      enabled: true,
      types: {
        protection: true,
        collaboration: true,
        revenue: true,
        content: true,
        system: true,
        marketing: false,
      },
      schedule: {
        startHour: 8,
        endHour: 22,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        weekdays: [true, true, true, true, true, true, true],
      },
      sound: true,
      vibration: true,
      badge: true,
      preview: true,
    };

    this.analytics = {
      sent: 0,
      delivered: 0,
      opened: 0,
      clicked: 0,
      dismissed: 0,
      deliveryRate: 0,
      openRate: 0,
      clickRate: 0,
      avgDeliveryTime: 0,
    };

    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    try {
      // Load preferences from storage
      await this.loadPreferences();
      
      // Load notification templates
      await this.loadTemplates();
      
      // Initialize push messaging
      await this.initializePushMessaging();
      
      // Load analytics
      await this.loadAnalytics();
      
      // Set up notification handlers
      this.setupNotificationHandlers();
      
      // Start background sync for pending notifications
      this.startBackgroundSync();
      
      this.isInitialized = true;
      console.log('Push Notification Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Push Notification Service:', error);
    }
  }

  // Public API Methods
  async requestPermission(): Promise<'granted' | 'denied' | 'default'> {
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return 'denied';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    const permission = await Notification.requestPermission();
    
    if (permission === 'granted') {
      await this.registerPushToken();
    }
    
    return permission;
  }

  async registerPushToken(): Promise<string | null> {
    try {
      if (!this.serviceWorkerRegistration) {
        this.serviceWorkerRegistration = await navigator.serviceWorker.ready;
      }

      const subscription = await this.serviceWorkerRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: await this.getVAPIDKey(),
      });

      const token = btoa(JSON.stringify(subscription));
      this.pushToken = token;

      // Register token with backend
      await this.registerTokenWithServer(token);
      
      // Store token locally
      await offlineStorageService.store('push_token', {
        token,
        platform: this.detectPlatform(),
        registeredAt: Date.now(),
        isActive: true,
      });

      return token;
    } catch (error) {
      console.error('Failed to register push token:', error);
      return null;
    }
  }

  async updatePreferences(newPreferences: Partial<NotificationPreferences>): Promise<void> {
    this.preferences = { ...this.preferences, ...newPreferences };
    await offlineStorageService.store('notification_preferences', this.preferences);
    
    // Update server preferences
    await mobileAPIService.makeRequest('/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify(this.preferences),
    });
  }

  getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  // Notification Display Methods
  async showLocalNotification(notification: NotificationPayload): Promise<void> {
    if (!this.shouldShowNotification(notification)) {
      return;
    }

    const options: NotificationOptions = {
      body: notification.body,
      icon: notification.icon || '/icons/notification-icon.png',
      badge: '/icons/badge-icon.png',
      image: notification.image,
      data: {
        ...notification.data,
        id: notification.id,
        clickAction: notification.clickAction,
        deepLink: notification.deepLink,
      },
      timestamp: Date.now(),
      requireInteraction: notification.priority === 'critical',
      silent: !this.preferences.sound,
      tag: notification.type,
    };

    // Add actions for rich notifications
    if (notification.type === 'collaboration') {
      options.actions = [
        { action: 'accept', title: 'Accept', icon: '/icons/accept.png' },
        { action: 'decline', title: 'Decline', icon: '/icons/decline.png' },
        { action: 'view', title: 'View Details' },
      ];
    } else if (notification.type === 'protection') {
      options.actions = [
        { action: 'takedown', title: 'Send Takedown', icon: '/icons/takedown.png' },
        { action: 'ignore', title: 'Ignore' },
        { action: 'review', title: 'Review' },
      ];
    }

    const displayedNotification = new Notification(notification.title, options);
    
    // Track notification display
    this.trackNotificationEvent('displayed', notification.id);
    
    // Add to history
    this.notificationHistory.unshift(notification);
    this.limitHistorySize();
    
    // Set up click handler
    displayedNotification.onclick = (event) => {
      this.handleNotificationClick(event, notification);
    };

    // Auto-dismiss for low priority notifications
    if (notification.priority === 'low') {
      setTimeout(() => {
        displayedNotification.close();
      }, 5000);
    }
  }

  async scheduleNotification(notification: NotificationPayload): Promise<void> {
    if (!notification.scheduledAt) {
      await this.showLocalNotification(notification);
      return;
    }

    const delay = notification.scheduledAt - Date.now();
    
    if (delay <= 0) {
      await this.showLocalNotification(notification);
      return;
    }

    // Store pending notification
    this.pendingNotifications.set(notification.id, notification);
    
    // Schedule for display
    setTimeout(async () => {
      const pendingNotification = this.pendingNotifications.get(notification.id);
      if (pendingNotification && !this.isExpired(pendingNotification)) {
        await this.showLocalNotification(pendingNotification);
        this.pendingNotifications.delete(notification.id);
      }
    }, delay);
  }

  // Template Management
  async loadTemplate(templateId: string): Promise<NotificationTemplate | null> {
    let template = this.templates.get(templateId);
    
    if (!template) {
      // Load from server
      try {
        const response = await mobileAPIService.makeRequest(`/notifications/templates/${templateId}`);
        template = response.data;
        
        if (template) {
          this.templates.set(templateId, template);
        }
      } catch (error) {
        console.error('Failed to load template:', error);
        return null;
      }
    }
    
    return template || null;
  }

  async createNotificationFromTemplate(
    templateId: string,
    variables: Record<string, string>,
    options?: Partial<NotificationPayload>
  ): Promise<NotificationPayload | null> {
    const template = await this.loadTemplate(templateId);
    if (!template) return null;

    const locale = navigator.language.split('-')[0];
    const localizedTemplate = template.localization[locale] || template;

    let title = localizedTemplate.title;
    let body = localizedTemplate.body;

    // Replace variables
    template.variables.forEach(variable => {
      const value = variables[variable] || '';
      title = title.replace(new RegExp(`{{${variable}}}`, 'g'), value);
      body = body.replace(new RegExp(`{{${variable}}}`, 'g'), value);
    });

    const notification: NotificationPayload = {
      id: `template_${templateId}_${Date.now()}`,
      title,
      body,
      type: template.type as any,
      priority: 'normal',
      ...options,
    };

    return notification;
  }

  // Business Logic Integration
  async handleProtectionAlert(violationData: {
    contentId: string;
    platform: string;
    violationType: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    url: string;
  }): Promise<void> {
    const notification = await this.createNotificationFromTemplate('protection_alert', {
      platform: violationData.platform,
      violationType: violationData.violationType,
      contentTitle: violationData.contentId,
    }, {
      type: 'protection',
      priority: violationData.severity === 'critical' ? 'critical' : 'high',
      data: {
        contentId: violationData.contentId,
        violationUrl: violationData.url,
        action: 'protection_alert',
      },
      clickAction: 'PROTECTION_DETAIL',
      deepLink: `ainflue://protection/violations/${violationData.contentId}`,
    });

    if (notification) {
      await this.showLocalNotification(notification);
    }
  }

  async handleCollaborationRequest(requestData: {
    fromUserId: string;
    fromUserName: string;
    projectType: string;
    message: string;
    budget?: number;
    deadline?: number;
  }): Promise<void> {
    const notification = await this.createNotificationFromTemplate('collaboration_request', {
      userName: requestData.fromUserName,
      projectType: requestData.projectType,
      budget: requestData.budget ? `$${requestData.budget}` : 'Not specified',
    }, {
      type: 'collaboration',
      priority: 'high',
      data: {
        fromUserId: requestData.fromUserId,
        action: 'collaboration_request',
      },
      clickAction: 'COLLABORATION_DETAIL',
      deepLink: `ainflue://collaborations/requests/${requestData.fromUserId}`,
    });

    if (notification) {
      await this.showLocalNotification(notification);
    }
  }

  async handleRevenueUpdate(revenueData: {
    amount: number;
    currency: string;
    source: string;
    type: 'payment' | 'milestone' | 'bonus';
  }): Promise<void> {
    const notification = await this.createNotificationFromTemplate('revenue_update', {
      amount: `${revenueData.currency} ${revenueData.amount}`,
      source: revenueData.source,
      type: revenueData.type,
    }, {
      type: 'revenue',
      priority: 'normal',
      data: {
        amount: revenueData.amount,
        currency: revenueData.currency,
        action: 'revenue_update',
      },
      clickAction: 'REVENUE_DETAIL',
      deepLink: 'ainflue://monetization/dashboard',
    });

    if (notification) {
      await this.showLocalNotification(notification);
    }
  }

  async handleContentProcessingUpdate(contentData: {
    contentId: string;
    status: 'processing' | 'completed' | 'failed' | 'protected';
    progress?: number;
  }): Promise<void> {
    const notification = await this.createNotificationFromTemplate('content_update', {
      contentId: contentData.contentId,
      status: contentData.status,
      progress: contentData.progress ? `${contentData.progress}%` : '',
    }, {
      type: 'content',
      priority: contentData.status === 'failed' ? 'high' : 'normal',
      data: {
        contentId: contentData.contentId,
        action: 'content_update',
      },
      clickAction: 'CONTENT_DETAIL',
      deepLink: `ainflue://content/library/${contentData.contentId}`,
    });

    if (notification) {
      await this.showLocalNotification(notification);
    }
  }

  // Analytics and History
  getNotificationHistory(): NotificationPayload[] {
    return [...this.notificationHistory];
  }

  getAnalytics(): NotificationAnalytics {
    return { ...this.analytics };
  }

  async trackNotificationEvent(event: 'displayed' | 'clicked' | 'dismissed', notificationId: string): Promise<void> {
    // Update local analytics
    switch (event) {
      case 'displayed':
        this.analytics.delivered++;
        break;
      case 'clicked':
        this.analytics.clicked++;
        this.analytics.openRate = this.analytics.clicked / this.analytics.delivered;
        break;
      case 'dismissed':
        this.analytics.dismissed++;
        break;
    }

    // Send to analytics service
    await mobileAPIService.trackUserEngagement('notification_' + event, {
      notificationId,
      timestamp: Date.now(),
    });

    // Store analytics
    await this.saveAnalytics();
  }

  // Utility Methods
  async clearNotificationHistory(): Promise<void> {
    this.notificationHistory = [];
    await offlineStorageService.store('notification_history', []);
  }

  async clearAllNotifications(): Promise<void> {
    if ('serviceWorker' in navigator && this.serviceWorkerRegistration) {
      const notifications = await this.serviceWorkerRegistration.getNotifications();
      notifications.forEach(notification => notification.close());
    }
  }

  isNotificationSupported(): boolean {
    return 'Notification' in window && 'serviceWorker' in navigator;
  }

  getPermissionStatus(): NotificationPermission {
    return Notification.permission;
  }

  // Private Methods
  private async initializePushMessaging(): Promise<void> {
    if ('serviceWorker' in navigator) {
      try {
        // Register service worker
        const registration = await navigator.serviceWorker.register('/sw.js');
        this.serviceWorkerRegistration = registration;

        // Listen for push messages
        navigator.serviceWorker.addEventListener('message', (event) => {
          this.handleServiceWorkerMessage(event);
        });

      } catch (error) {
        console.error('Service worker registration failed:', error);
      }
    }
  }

  private setupNotificationHandlers(): void {
    // Handle notification permissions change
    if ('permissions' in navigator) {
      navigator.permissions.query({ name: 'notifications' as PermissionName }).then((result) => {
        result.onchange = () => {
          if (result.state === 'denied') {
            this.preferences.enabled = false;
            this.updatePreferences({});
          }
        };
      });
    }

    // Handle visibility change
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        // Clear notifications when app becomes visible
        this.clearAllNotifications();
      }
    });
  }

  private handleServiceWorkerMessage(event: MessageEvent): void {
    const { type, data } = event.data;

    switch (type) {
      case 'NOTIFICATION_CLICKED':
        this.handleNotificationClick(null, data.notification);
        break;
      case 'NOTIFICATION_RECEIVED':
        this.handlePushMessage(data.notification);
        break;
    }
  }

  private async handlePushMessage(payload: NotificationPayload): Promise<void> {
    if (this.shouldShowNotification(payload)) {
      await this.showLocalNotification(payload);
    }
  }

  private handleNotificationClick(event: Event | null, notification: NotificationPayload): void {
    // Track click
    this.trackNotificationEvent('clicked', notification.id);

    // Handle deep linking
    if (notification.deepLink) {
      this.handleDeepLink(notification.deepLink);
    } else if (notification.clickAction) {
      this.handleClickAction(notification.clickAction, notification.data);
    }

    // Close notification
    if (event?.target && 'close' in event.target) {
      (event.target as Notification).close();
    }
  }

  private handleDeepLink(deepLink: string): void {
    // Parse deep link and navigate
    try {
      const url = new URL(deepLink);
      
      if (url.protocol === 'ainflue:') {
        // Handle internal deep links
        this.navigateToScreen(url.pathname, url.searchParams);
      } else {
        // Handle external links
        window.open(deepLink, '_blank');
      }
    } catch (error) {
      console.error('Invalid deep link:', deepLink);
    }
  }

  private handleClickAction(action: string, data?: Record<string, any>): void {
    switch (action) {
      case 'PROTECTION_DETAIL':
        this.navigateToScreen('/protection/violations', new URLSearchParams(data));
        break;
      case 'COLLABORATION_DETAIL':
        this.navigateToScreen('/collaborations/requests', new URLSearchParams(data));
        break;
      case 'REVENUE_DETAIL':
        this.navigateToScreen('/monetization/dashboard', new URLSearchParams(data));
        break;
      case 'CONTENT_DETAIL':
        this.navigateToScreen('/content/library', new URLSearchParams(data));
        break;
      default:
        console.warn('Unknown click action:', action);
    }
  }

  private navigateToScreen(path: string, params?: URLSearchParams): void {
    // This would integrate with your app's navigation system
    const url = params ? `${path}?${params.toString()}` : path;
    
    // For web apps
    if (typeof window !== 'undefined' && window.history) {
      window.history.pushState({}, '', url);
      window.dispatchEvent(new PopStateEvent('popstate'));
    }
  }

  private shouldShowNotification(notification: NotificationPayload): boolean {
    // Check if notifications are enabled
    if (!this.preferences.enabled) return false;

    // Check if this notification type is enabled
    if (!this.preferences.types[notification.type]) return false;

    // Check scheduled time
    if (!this.isWithinScheduledHours()) return false;

    // Check if notification is expired
    if (this.isExpired(notification)) return false;

    return true;
  }

  private isWithinScheduledHours(): boolean {
    const now = new Date();
    const currentHour = now.getHours();
    const currentDay = now.getDay();

    // Check if current day is enabled
    if (!this.preferences.schedule.weekdays[currentDay]) return false;

    // Check if current hour is within scheduled hours
    const { startHour, endHour } = this.preferences.schedule;
    
    if (startHour <= endHour) {
      return currentHour >= startHour && currentHour < endHour;
    } else {
      // Handles cases where schedule crosses midnight
      return currentHour >= startHour || currentHour < endHour;
    }
  }

  private isExpired(notification: NotificationPayload): boolean {
    if (!notification.expiresAt) return false;
    return Date.now() > notification.expiresAt;
  }

  private detectPlatform(): 'ios' | 'android' | 'web' {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (/iphone|ipad|ipod/.test(userAgent)) return 'ios';
    if (/android/.test(userAgent)) return 'android';
    
    return 'web';
  }

  private async getVAPIDKey(): Promise<Uint8Array> {
    // In a real app, this would be your VAPID public key
    const vapidKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI0GcllOQ0PElV7MQM0JsLJHgOWOJa9uMsQoB3GXlHUk3_fRe-FQjG1LkM';
    
    return new Uint8Array(
      atob(vapidKey.replace(/-/g, '+').replace(/_/g, '/'))
        .split('')
        .map(char => char.charCodeAt(0))
    );
  }

  private async registerTokenWithServer(token: string): Promise<void> {
    try {
      await mobileAPIService.makeRequest('/notifications/register-token', {
        method: 'POST',
        body: JSON.stringify({
          token,
          platform: this.detectPlatform(),
          deviceInfo: {
            userAgent: navigator.userAgent,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          },
        }),
      });
    } catch (error) {
      console.error('Failed to register token with server:', error);
    }
  }

  private async loadPreferences(): Promise<void> {
    const stored = await offlineStorageService.retrieve('notification_preferences');
    if (stored) {
      this.preferences = { ...this.preferences, ...stored };
    }
  }

  private async loadTemplates(): Promise<void> {
    try {
      const response = await mobileAPIService.makeRequest('/notifications/templates');
      const templates = response.data;
      
      templates.forEach((template: NotificationTemplate) => {
        this.templates.set(template.id, template);
      });
    } catch (error) {
      console.error('Failed to load notification templates:', error);
    }
  }

  private async loadAnalytics(): Promise<void> {
    const stored = await offlineStorageService.retrieve('notification_analytics');
    if (stored) {
      this.analytics = { ...this.analytics, ...stored };
    }
  }

  private async saveAnalytics(): Promise<void> {
    await offlineStorageService.store('notification_analytics', this.analytics);
  }

  private limitHistorySize(): void {
    const maxHistory = 100;
    if (this.notificationHistory.length > maxHistory) {
      this.notificationHistory = this.notificationHistory.slice(0, maxHistory);
    }
  }

  private startBackgroundSync(): void {
    setInterval(async () => {
      // Sync analytics with server
      try {
        await mobileAPIService.makeRequest('/notifications/analytics', {
          method: 'POST',
          body: JSON.stringify(this.analytics),
        });
      } catch (error) {
        console.error('Failed to sync notification analytics:', error);
      }
    }, 300000); // Every 5 minutes
  }
}

// Export singleton instance
export const pushNotificationService = new PushNotificationService();