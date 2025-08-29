/**
 * Notification Types - TypeScript type definitions for push notifications
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

// Base notification payload interface
export interface NotificationPayload {
  userId: string;
  title?: string;
  body?: string;
  type: NotificationType;
  platform?: 'ios' | 'android' | 'web';
  data?: Record<string, any>;
  priority?: 'low' | 'normal' | 'high';
  ttl?: number; // Time to live in seconds
  badge?: number;
  sound?: string;
  icon?: string;
  color?: string;
  tag?: string;
  deepLink?: string;
  actions?: NotificationAction[];
  scheduledTime?: Date;
  retryOnFailure?: boolean;
  analytics?: boolean;
}

// Notification action interface
export interface NotificationAction {
  id: string;
  title: string;
  icon?: string;
  type?: 'button' | 'input';
  placeholder?: string; // For input type
  deepLink?: string;
}

// Notification types enum
export type NotificationType = 
  | 'protection_alert'
  | 'revenue_update'
  | 'collaboration_request'
  | 'content_status'
  | 'system_notification'
  | 'marketing'
  | 'reminder'
  | 'security_alert';

// Notification result interface
export interface NotificationResult {
  success: boolean;
  messageId: string;
  timestamp: string;
  platform: string;
  error?: string;
  details?: Record<string, any>;
}

// User notification preferences
export interface UserPreferences {
  protection_alerts: boolean;
  revenue_updates: boolean;
  collaboration_requests: boolean;
  content_updates: boolean;
  system_notifications: boolean;
  marketing: boolean;
  reminders: boolean;
  security_alerts: boolean;
  quiet_hours?: {
    enabled: boolean;
    start: string; // HH:MM format
    end: string;   // HH:MM format
    timezone: string;
  };
  delivery_method?: {
    push: boolean;
    email: boolean;
    sms: boolean;
  };
  frequency?: {
    immediate: boolean;
    daily_digest: boolean;
    weekly_digest: boolean;
  };
}

// Device token information
export interface DeviceToken {
  token: string;
  platform: 'firebase' | 'apns' | 'web';
  userId: string;
  deviceId: string;
  lastUsed: Date;
  isActive: boolean;
  appVersion?: string;
  osVersion?: string;
  deviceModel?: string;
}

// Notification analytics interface
export interface NotificationAnalytics {
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  failed: number;
  deliveryRate: number;
  openRate: number;
  clickRate: number;
  conversionRate: number;
  avgDeliveryTime: string;
  period: {
    start: Date;
    end: Date;
  };
  breakdown?: {
    byType: Record<NotificationType, NotificationMetrics>;
    byPlatform: Record<string, NotificationMetrics>;
    byHour: Array<{ hour: number; metrics: NotificationMetrics }>;
  };
}

// Individual notification metrics
export interface NotificationMetrics {
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  failed: number;
  deliveryRate: number;
  openRate: number;
  clickRate: number;
}

// Health status interface
export interface HealthStatus {
  firebase: 'healthy' | 'unhealthy' | 'unknown';
  apns: 'healthy' | 'unhealthy' | 'unknown';
  deliveryRate: number;
  avgDeliveryTime: string;
  lastChecked: string;
  error?: string;
}

// Delivery tracking interface
export interface DeliveryTrackingEvent {
  messageId: string;
  userId?: string;
  notificationType?: NotificationType;
  platform: string;
  sent?: boolean;
  delivered?: boolean;
  opened?: boolean;
  clicked?: boolean;
  failed?: boolean;
  error?: string;
  timestamp: Date;
  deliveryTime?: number; // Milliseconds
  userAgent?: string;
  ipAddress?: string;
}

// Topic subscription interface
export interface TopicSubscription {
  userId: string;
  topic: string;
  platform: 'firebase' | 'apns' | 'web';
  subscribed: boolean;
  timestamp: Date;
}

// Template variables interface
export interface TemplateVariables {
  userName?: string;
  contentName?: string;
  platform?: string;
  amount?: number;
  currency?: string;
  milestone?: number;
  violationType?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  projectName?: string;
  inviterName?: string;
  role?: string;
  expiryDate?: Date;
  actionUrl?: string;
  supportUrl?: string;
  [key: string]: any;
}

// Notification template interface
export interface NotificationTemplate {
  id: string;
  name: string;
  type: NotificationType;
  title: string;
  body: string;
  variables: string[];
  platforms: {
    android?: AndroidSpecific;
    ios?: IOSSpecific;
    web?: WebSpecific;
  };
  actions?: NotificationAction[];
  defaultSettings?: {
    priority?: 'low' | 'normal' | 'high';
    ttl?: number;
    badge?: number;
    sound?: string;
    icon?: string;
    color?: string;
  };
}

// Platform-specific configurations
export interface AndroidSpecific {
  channelId?: string;
  priority?: 'min' | 'low' | 'default' | 'high' | 'max';
  visibility?: 'private' | 'public' | 'secret';
  category?: string;
  ledColor?: string;
  vibrationPattern?: number[];
  largeIcon?: string;
  bigPicture?: string;
  bigText?: string;
  group?: string;
  groupSummary?: boolean;
}

export interface IOSSpecific {
  badge?: number;
  sound?: string | {
    name: string;
    critical?: boolean;
    volume?: number;
  };
  threadId?: string;
  category?: string;
  targetContentId?: string;
  interruptionLevel?: 'passive' | 'active' | 'timeSensitive' | 'critical';
  relevanceScore?: number;
  mutableContent?: boolean;
  attachments?: Array<{
    id: string;
    url: string;
    type: 'image' | 'video' | 'audio';
  }>;
}

export interface WebSpecific {
  icon?: string;
  badge?: string;
  image?: string;
  vibrate?: number[];
  timestamp?: number;
  renotify?: boolean;
  requireInteraction?: boolean;
  actions?: NotificationAction[];
  silent?: boolean;
}

// Configuration interfaces
export interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
  measurementId?: string;
  serverKey?: string;
}

export interface APNSConfig {
  keyId: string;
  teamId: string;
  keyFile: string;
  production: boolean;
  bundleId: string;
  defaultTopic?: string;
}

// Error interfaces
export interface NotificationError {
  code: string;
  message: string;
  details?: Record<string, any>;
  retryable: boolean;
  timestamp: Date;
}

// Batch operation interfaces
export interface BatchOperation {
  id: string;
  type: 'send' | 'subscribe' | 'unsubscribe';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: {
    total: number;
    processed: number;
    successful: number;
    failed: number;
  };
  startTime: Date;
  endTime?: Date;
  errors?: NotificationError[];
}

// Scheduling interfaces
export interface ScheduledNotification {
  id: string;
  payload: NotificationPayload;
  scheduledTime: Date;
  timezone: string;
  status: 'scheduled' | 'sent' | 'cancelled' | 'failed';
  createdAt: Date;
  sentAt?: Date;
  result?: NotificationResult;
}

// A/B Testing interfaces
export interface ABTestVariant {
  id: string;
  name: string;
  weight: number; // Percentage of traffic (0-100)
  template: NotificationTemplate;
  isControl: boolean;
}

export interface ABTest {
  id: string;
  name: string;
  type: NotificationType;
  status: 'draft' | 'active' | 'paused' | 'completed';
  variants: ABTestVariant[];
  targetAudience: {
    userSegments: string[];
    platforms: string[];
    countries?: string[];
  };
  startDate: Date;
  endDate?: Date;
  metrics: {
    totalSent: number;
    results: Record<string, NotificationMetrics>;
  };
}

// Segmentation interfaces
export interface UserSegment {
  id: string;
  name: string;
  description: string;
  criteria: {
    userType?: string[];
    platforms?: string[];
    countries?: string[];
    languages?: string[];
    createdAfter?: Date;
    createdBefore?: Date;
    lastActiveAfter?: Date;
    lastActiveBefore?: Date;
    hasContent?: boolean;
    revenueRange?: {
      min: number;
      max: number;
    };
    customAttributes?: Record<string, any>;
  };
  userCount: number;
  lastUpdated: Date;
}

// Rate limiting interfaces
export interface RateLimit {
  userId?: string;
  platform?: string;
  notificationType?: NotificationType;
  maxPerMinute: number;
  maxPerHour: number;
  maxPerDay: number;
  currentCounts: {
    minute: number;
    hour: number;
    day: number;
  };
  resetTimes: {
    minute: Date;
    hour: Date;
    day: Date;
  };
}

// Export all types
export * from './payload_schemas';