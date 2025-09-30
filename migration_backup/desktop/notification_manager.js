/**
 * Ainflue Desktop - Notification Manager
 * 
 * Cross-platform notification system with rich media support
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { Notification, nativeImage } = require('electron');
const log = require('electron-log');
const path = require('path');
const EventEmitter = require('events');

class NotificationManager extends EventEmitter {
  constructor() {
    super();
    
    this.isSupported = Notification.isSupported();
    this.isEnabled = true;
    this.notificationQueue = [];
    this.activeNotifications = new Map();
    this.notificationHistory = [];
    this.maxHistorySize = 100;
    
    // Notification categories
    this.categories = {
      SYSTEM: 'system',
      PROCESSING: 'processing', 
      COLLABORATION: 'collaboration',
      EXPORT: 'export',
      ERROR: 'error',
      WARNING: 'warning',
      SUCCESS: 'success',
      INFO: 'info'
    };
    
    // Default settings
    this.settings = {
      playSound: true,
      showBadge: true,
      urgency: 'normal',
      persistent: false,
      maxActiveNotifications: 5,
      autoHideDelay: 5000,
      enableRichNotifications: true
    };
    
    this.isInitialized = false;
    log.info('Notification Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Notification Manager...');
      
      if (!this.isSupported) {
        log.warn('System notifications not supported on this platform');
        return;
      }
      
      // Load user preferences
      this.loadSettings();
      
      // Setup notification icons
      this.setupIcons();
      
      // Configure platform-specific features
      this.configurePlatformFeatures();
      
      // Setup notification cleanup
      this.setupNotificationCleanup();
      
      this.isInitialized = true;
      log.info('✅ Notification Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Notification Manager:', error);
      throw error;
    }
  }

  loadSettings() {
    // Load from electron-store or configuration manager
    // For now, use defaults
    log.info('Notification settings loaded');
  }

  setupIcons() {
    this.icons = {
      default: this.createIcon('icon.png'),
      success: this.createIcon('success.png'),
      error: this.createIcon('error.png'),
      warning: this.createIcon('warning.png'),
      info: this.createIcon('info.png'),
      processing: this.createIcon('processing.png'),
      collaboration: this.createIcon('collaboration.png'),
      export: this.createIcon('export.png')
    };
    
    log.info('Notification icons configured');
  }

  createIcon(iconName) {
    try {
      const iconPath = path.join(__dirname, 'assets', 'notifications', iconName);
      return nativeImage.createFromPath(iconPath);
    } catch (error) {
      // Fallback to default icon
      const defaultIconPath = path.join(__dirname, 'assets', 'icon.png');
      return nativeImage.createFromPath(defaultIconPath);
    }
  }

  configurePlatformFeatures() {
    if (process.platform === 'darwin') {
      this.configureMacOSFeatures();
    } else if (process.platform === 'win32') {
      this.configureWindowsFeatures();
    } else if (process.platform === 'linux') {
      this.configureLinuxFeatures();
    }
  }

  configureMacOSFeatures() {
    // macOS specific notification features
    this.platformFeatures = {
      actionButtons: true,
      richMedia: true,
      grouping: true,
      scheduling: true,
      criticalAlerts: true
    };
    
    log.info('macOS notification features configured');
  }

  configureWindowsFeatures() {
    // Windows specific notification features
    this.platformFeatures = {
      toastNotifications: true,
      actionButtons: true,
      progressBar: true,
      adaptiveCards: true,
      scheduling: false
    };
    
    log.info('Windows notification features configured');
  }

  configureLinuxFeatures() {
    // Linux specific notification features
    this.platformFeatures = {
      desktopNotifications: true,
      urgencyLevels: true,
      categories: true,
      persistence: true,
      customIcons: true
    };
    
    log.info('Linux notification features configured');
  }

  setupNotificationCleanup() {
    // Clean up old notifications every 30 minutes
    this.cleanupInterval = setInterval(() => {
      this.cleanupOldNotifications();
    }, 30 * 60 * 1000);
    
    // Clean up expired notifications every 5 minutes
    this.expiredCleanupInterval = setInterval(() => {
      this.cleanupExpiredNotifications();
    }, 5 * 60 * 1000);
    
    log.info('Notification cleanup configured');
  }

  // Main notification methods
  async showNotification(options = {}) {
    if (!this.isSupported || !this.isEnabled) {
      log.debug('Notifications disabled or not supported');
      return null;
    }
    
    // Validate and normalize options
    const normalizedOptions = this.normalizeOptions(options);
    
    // Check rate limiting
    if (this.activeNotifications.size >= this.settings.maxActiveNotifications) {
      this.queueNotification(normalizedOptions);
      return null;
    }
    
    try {
      const notification = this.createNotification(normalizedOptions);
      const notificationId = this.generateNotificationId();
      
      // Store active notification
      this.activeNotifications.set(notificationId, {
        notification,
        options: normalizedOptions,
        createdAt: new Date(),
        id: notificationId
      });
      
      // Setup event handlers
      this.setupNotificationEvents(notification, notificationId, normalizedOptions);
      
      // Show notification
      notification.show();
      
      // Add to history
      this.addToHistory(normalizedOptions, notificationId);
      
      // Auto-hide if not persistent
      if (!normalizedOptions.persistent && this.settings.autoHideDelay > 0) {
        setTimeout(() => {
          this.hideNotification(notificationId);
        }, this.settings.autoHideDelay);
      }
      
      log.debug(`Notification shown: ${normalizedOptions.title}`);
      this.emit('notification-shown', { id: notificationId, options: normalizedOptions });
      
      return notificationId;
      
    } catch (error) {
      log.error('Failed to show notification:', error);
      this.emit('notification-error', { error, options: normalizedOptions });
      return null;
    }
  }

  normalizeOptions(options) {
    return {
      title: options.title || 'Ainflue Studio',
      body: options.body || '',
      subtitle: options.subtitle,
      icon: options.icon || this.getIconForCategory(options.category),
      sound: options.sound !== false && this.settings.playSound,
      urgency: options.urgency || this.settings.urgency,
      category: options.category || this.categories.INFO,
      persistent: options.persistent || this.settings.persistent,
      silent: options.silent || false,
      timeoutType: options.timeoutType || 'default',
      actions: options.actions || [],
      data: options.data || {},
      tag: options.tag,
      renotify: options.renotify || false,
      requireInteraction: options.requireInteraction || false
    };
  }

  createNotification(options) {
    const notificationOptions = {
      title: options.title,
      body: options.body,
      icon: options.icon,
      silent: options.silent,
      urgency: options.urgency,
      timeoutType: options.timeoutType,
      actions: options.actions,
      sound: options.sound ? undefined : null // Let system handle default sound
    };
    
    // Add platform-specific options
    if (process.platform === 'darwin') {
      if (options.subtitle) {
        notificationOptions.subtitle = options.subtitle;
      }
    } else if (process.platform === 'linux') {
      notificationOptions.urgency = this.mapUrgencyLevel(options.urgency);
    }
    
    return new Notification(notificationOptions);
  }

  setupNotificationEvents(notification, notificationId, options) {
    notification.on('show', () => {
      log.debug(`Notification displayed: ${notificationId}`);
      this.emit('notification-displayed', { id: notificationId });
    });
    
    notification.on('click', () => {
      log.debug(`Notification clicked: ${notificationId}`);
      this.emit('notification-clicked', { id: notificationId, data: options.data });
      
      // Auto-close on click unless persistent
      if (!options.persistent) {
        this.hideNotification(notificationId);
      }
    });
    
    notification.on('close', () => {
      log.debug(`Notification closed: ${notificationId}`);
      this.activeNotifications.delete(notificationId);
      this.emit('notification-closed', { id: notificationId });
      
      // Process queued notifications
      this.processNotificationQueue();
    });
    
    notification.on('action', (index) => {
      log.debug(`Notification action clicked: ${notificationId}, action: ${index}`);
      this.emit('notification-action', { 
        id: notificationId, 
        actionIndex: index, 
        action: options.actions[index],
        data: options.data 
      });
    });
    
    notification.on('failed', (error) => {
      log.error(`Notification failed: ${notificationId}`, error);
      this.activeNotifications.delete(notificationId);
      this.emit('notification-failed', { id: notificationId, error });
    });
  }

  // Convenience methods for different notification types
  showSuccess(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.SUCCESS,
      urgency: 'normal'
    });
  }

  showError(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.ERROR,
      urgency: 'critical',
      persistent: true,
      requireInteraction: true
    });
  }

  showWarning(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.WARNING,
      urgency: 'normal'
    });
  }

  showInfo(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.INFO,
      urgency: 'low'
    });
  }

  showProcessing(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.PROCESSING,
      persistent: true,
      silent: true
    });
  }

  showCollaboration(title, body, options = {}) {
    return this.showNotification({
      ...options,
      title,
      body,
      category: this.categories.COLLABORATION,
      urgency: 'normal',
      actions: [
        { type: 'button', text: 'View' },
        { type: 'button', text: 'Dismiss' }
      ]
    });
  }

  showExportComplete(filePath, options = {}) {
    return this.showNotification({
      ...options,
      title: 'Export Complete',
      body: `File exported: ${path.basename(filePath)}`,
      category: this.categories.EXPORT,
      actions: [
        { type: 'button', text: 'Open Folder' },
        { type: 'button', text: 'Open File' }
      ],
      data: { filePath }
    });
  }

  // Progress notifications
  showProgress(title, progress, options = {}) {
    const progressText = `${Math.round(progress * 100)}%`;
    
    if (process.platform === 'win32' && this.platformFeatures.progressBar) {
      // Windows progress notification
      return this.showNotification({
        ...options,
        title,
        body: `Progress: ${progressText}`,
        category: this.categories.PROCESSING,
        persistent: true,
        silent: true,
        progress: progress
      });
    } else {
      // Standard progress notification
      return this.showNotification({
        ...options,
        title,
        body: `Progress: ${progressText}`,
        category: this.categories.PROCESSING,
        persistent: true,
        silent: true
      });
    }
  }

  updateProgress(notificationId, progress) {
    const activeNotification = this.activeNotifications.get(notificationId);
    if (activeNotification) {
      const progressText = `${Math.round(progress * 100)}%`;
      
      // Update notification body
      if (activeNotification.notification.body) {
        activeNotification.notification.body = activeNotification.notification.body.replace(
          /Progress: \d+%/,
          `Progress: ${progressText}`
        );
      }
      
      this.emit('notification-progress-updated', { id: notificationId, progress });
    }
  }

  // Notification management
  hideNotification(notificationId) {
    const activeNotification = this.activeNotifications.get(notificationId);
    if (activeNotification) {
      try {
        activeNotification.notification.close();
      } catch (error) {
        log.warn(`Failed to close notification ${notificationId}:`, error.message);
      }
    }
  }

  hideAllNotifications() {
    for (const [id, notification] of this.activeNotifications) {
      this.hideNotification(id);
    }
  }

  queueNotification(options) {
    this.notificationQueue.push({
      options,
      queuedAt: new Date()
    });
    
    log.debug('Notification queued');
  }

  processNotificationQueue() {
    if (this.notificationQueue.length > 0 && 
        this.activeNotifications.size < this.settings.maxActiveNotifications) {
      
      const queuedNotification = this.notificationQueue.shift();
      this.showNotification(queuedNotification.options);
    }
  }

  // History and cleanup
  addToHistory(options, notificationId) {
    this.notificationHistory.unshift({
      id: notificationId,
      title: options.title,
      body: options.body,
      category: options.category,
      timestamp: new Date(),
      clicked: false,
      dismissed: false
    });
    
    // Limit history size
    if (this.notificationHistory.length > this.maxHistorySize) {
      this.notificationHistory = this.notificationHistory.slice(0, this.maxHistorySize);
    }
  }

  cleanupOldNotifications() {
    const cutoffTime = new Date(Date.now() - (24 * 60 * 60 * 1000)); // 24 hours ago
    
    this.notificationHistory = this.notificationHistory.filter(
      notification => notification.timestamp > cutoffTime
    );
    
    log.debug('Old notifications cleaned up');
  }

  cleanupExpiredNotifications() {
    const now = new Date();
    const expiredIds = [];
    
    for (const [id, notification] of this.activeNotifications) {
      const age = now - notification.createdAt;
      if (age > this.settings.autoHideDelay && !notification.options.persistent) {
        expiredIds.push(id);
      }
    }
    
    expiredIds.forEach(id => this.hideNotification(id));
    
    if (expiredIds.length > 0) {
      log.debug(`Cleaned up ${expiredIds.length} expired notifications`);
    }
  }

  // Utility methods
  generateNotificationId() {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getIconForCategory(category) {
    switch (category) {
      case this.categories.SUCCESS:
        return this.icons.success;
      case this.categories.ERROR:
        return this.icons.error;
      case this.categories.WARNING:
        return this.icons.warning;
      case this.categories.PROCESSING:
        return this.icons.processing;
      case this.categories.COLLABORATION:
        return this.icons.collaboration;
      case this.categories.EXPORT:
        return this.icons.export;
      default:
        return this.icons.default;
    }
  }

  mapUrgencyLevel(urgency) {
    // Map urgency levels for Linux
    switch (urgency) {
      case 'low':
        return 'low';
      case 'normal':
        return 'normal';
      case 'critical':
        return 'critical';
      default:
        return 'normal';
    }
  }

  // Settings and configuration
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
    log.info('Notification settings updated');
  }

  enable() {
    this.isEnabled = true;
    log.info('Notifications enabled');
  }

  disable() {
    this.isEnabled = false;
    this.hideAllNotifications();
    log.info('Notifications disabled');
  }

  // Public API
  getActiveNotifications() {
    return Array.from(this.activeNotifications.values()).map(notification => ({
      id: notification.id,
      title: notification.options.title,
      body: notification.options.body,
      category: notification.options.category,
      createdAt: notification.createdAt
    }));
  }

  getNotificationHistory() {
    return [...this.notificationHistory];
  }

  getSettings() {
    return { ...this.settings };
  }

  isNotificationSupported() {
    return this.isSupported;
  }

  getQueueLength() {
    return this.notificationQueue.length;
  }

  // Cleanup
  cleanup() {
    // Hide all active notifications
    this.hideAllNotifications();
    
    // Clear intervals
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    if (this.expiredCleanupInterval) {
      clearInterval(this.expiredCleanupInterval);
    }
    
    // Clear queues and history
    this.notificationQueue = [];
    this.notificationHistory = [];
    
    log.info('Notification Manager cleaned up');
  }
}

module.exports = NotificationManager;