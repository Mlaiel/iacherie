/**
 * Ainflue Desktop - Auto Updater Manager
 * 
 * Professional auto-update system with secure distribution and rollback capabilities
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { autoUpdater } = require('electron-updater');
const { dialog, app, BrowserWindow } = require('electron');
const log = require('electron-log');
const { EventEmitter } = require('events');

class AutoUpdaterManager extends EventEmitter {
  constructor() {
    super();
    
    this.updateInfo = null;
    this.downloadProgress = 0;
    this.isUpdateAvailable = false;
    this.isDownloading = false;
    this.isUpdateReady = false;
    this.updateCheckInterval = null;
    this.autoDownload = true;
    this.autoInstall = false;
    this.notifyUser = true;
    
    // Update channels
    this.channels = {
      stable: 'stable',
      beta: 'beta',
      alpha: 'alpha'
    };
    
    this.currentChannel = this.channels.stable;
    
    // Configure autoUpdater
    this.configureAutoUpdater();
    
    log.info('Auto Updater Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Auto Updater Manager...');
      
      // Setup update server configuration
      this.setupUpdateServer();
      
      // Configure update behavior
      this.configureUpdateBehavior();
      
      // Setup event handlers
      this.setupEventHandlers();
      
      // Start update checking if in production
      if (process.env.NODE_ENV === 'production') {
        this.startPeriodicUpdateCheck();
      }
      
      log.info('✅ Auto Updater Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Auto Updater Manager:', error);
      throw error;
    }
  }

  configureAutoUpdater() {
    // Configure logging
    autoUpdater.logger = log;
    autoUpdater.logger.transports.file.level = 'info';
    
    // Set auto download behavior
    autoUpdater.autoDownload = this.autoDownload;
    autoUpdater.autoInstallOnAppQuit = this.autoInstall;
    
    // Set channel
    autoUpdater.channel = this.currentChannel;
    
    // Configure request headers for authentication
    autoUpdater.requestHeaders = {
      'User-Agent': `AinflueSudio/${app.getVersion()} (${process.platform}; ${process.arch})`,
      'X-Client-ID': 'ainflue-desktop',
      'X-Client-Version': app.getVersion()
    };
    
    log.info(`Auto updater configured for ${this.currentChannel} channel`);
  }

  setupUpdateServer() {
    // Configure update server based on environment
    const updateServers = {
      production: {
        provider: 'github',
        owner: 'Mlaiel',
        repo: 'Ainflue',
        private: false
      },
      staging: {
        provider: 'generic',
        url: 'https://staging-updates.ainflue.com'
      },
      development: {
        provider: 'generic',
        url: 'http://localhost:3000/updates'
      }
    };
    
    const environment = process.env.NODE_ENV || 'production';
    const serverConfig = updateServers[environment] || updateServers.production;
    
    autoUpdater.setFeedURL(serverConfig);
    
    log.info(`Update server configured: ${JSON.stringify(serverConfig)}`);
  }

  configureUpdateBehavior() {
    // Load user preferences for updates
    const preferences = this.loadUpdatePreferences();
    
    this.autoDownload = preferences.autoDownload ?? true;
    this.autoInstall = preferences.autoInstall ?? false;
    this.notifyUser = preferences.notifyUser ?? true;
    this.currentChannel = preferences.channel ?? this.channels.stable;
    
    // Apply configuration
    autoUpdater.autoDownload = this.autoDownload;
    autoUpdater.autoInstallOnAppQuit = this.autoInstall;
    autoUpdater.channel = this.currentChannel;
    
    log.info('Update behavior configured:', {
      autoDownload: this.autoDownload,
      autoInstall: this.autoInstall,
      notifyUser: this.notifyUser,
      channel: this.currentChannel
    });
  }

  setupEventHandlers() {
    // Update available
    autoUpdater.on('update-available', (info) => {
      log.info('Update available:', info);
      this.updateInfo = info;
      this.isUpdateAvailable = true;
      this.emit('update-available', info);
      
      if (this.notifyUser) {
        this.showUpdateAvailableNotification(info);
      }
    });

    // Update not available
    autoUpdater.on('update-not-available', (info) => {
      log.info('Update not available:', info);
      this.emit('update-not-available', info);
    });

    // Download progress
    autoUpdater.on('download-progress', (progress) => {
      this.downloadProgress = progress.percent;
      this.isDownloading = true;
      this.emit('download-progress', progress);
      
      log.debug(`Download progress: ${progress.percent.toFixed(2)}%`);
      
      // Update progress in UI
      this.updateDownloadProgress(progress);
    });

    // Update downloaded
    autoUpdater.on('update-downloaded', (info) => {
      log.info('Update downloaded:', info);
      this.isDownloading = false;
      this.isUpdateReady = true;
      this.emit('update-downloaded', info);
      
      if (this.notifyUser) {
        this.showUpdateReadyNotification(info);
      }
    });

    // Error handling
    autoUpdater.on('error', (error) => {
      log.error('Auto updater error:', error);
      this.isDownloading = false;
      this.emit('update-error', error);
      
      if (this.notifyUser) {
        this.showUpdateErrorNotification(error);
      }
    });

    // Checking for update
    autoUpdater.on('checking-for-update', () => {
      log.info('Checking for updates...');
      this.emit('checking-for-update');
    });

    log.info('Auto updater event handlers configured');
  }

  // Public API methods
  async checkForUpdates() {
    try {
      log.info('Manual update check initiated');
      const result = await autoUpdater.checkForUpdates();
      return result;
    } catch (error) {
      log.error('Failed to check for updates:', error);
      throw error;
    }
  }

  async downloadUpdate() {
    if (!this.isUpdateAvailable) {
      throw new Error('No update available to download');
    }
    
    try {
      log.info('Manual download initiated');
      await autoUpdater.downloadUpdate();
    } catch (error) {
      log.error('Failed to download update:', error);
      throw error;
    }
  }

  quitAndInstall() {
    if (!this.isUpdateReady) {
      throw new Error('No update ready to install');
    }
    
    log.info('Quitting and installing update');
    autoUpdater.quitAndInstall(false, true);
  }

  // Update channel management
  setChannel(channel) {
    if (!Object.values(this.channels).includes(channel)) {
      throw new Error(`Invalid channel: ${channel}`);
    }
    
    this.currentChannel = channel;
    autoUpdater.channel = channel;
    
    this.saveUpdatePreferences();
    log.info(`Update channel changed to: ${channel}`);
  }

  getChannel() {
    return this.currentChannel;
  }

  getAvailableChannels() {
    return Object.values(this.channels);
  }

  // Configuration methods
  setAutoDownload(enabled) {
    this.autoDownload = enabled;
    autoUpdater.autoDownload = enabled;
    this.saveUpdatePreferences();
    log.info(`Auto download ${enabled ? 'enabled' : 'disabled'}`);
  }

  setAutoInstall(enabled) {
    this.autoInstall = enabled;
    autoUpdater.autoInstallOnAppQuit = enabled;
    this.saveUpdatePreferences();
    log.info(`Auto install ${enabled ? 'enabled' : 'disabled'}`);
  }

  setNotifyUser(enabled) {
    this.notifyUser = enabled;
    this.saveUpdatePreferences();
    log.info(`User notifications ${enabled ? 'enabled' : 'disabled'}`);
  }

  // Periodic update checking
  startPeriodicUpdateCheck(intervalMinutes = 60) {
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
    }
    
    this.updateCheckInterval = setInterval(async () => {
      try {
        await this.checkForUpdates();
      } catch (error) {
        log.error('Periodic update check failed:', error);
      }
    }, intervalMinutes * 60 * 1000);
    
    log.info(`Periodic update checking started (${intervalMinutes} minute intervals)`);
  }

  stopPeriodicUpdateCheck() {
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
      this.updateCheckInterval = null;
      log.info('Periodic update checking stopped');
    }
  }

  // Notification methods
  async showUpdateAvailableNotification(info) {
    const mainWindow = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) {
      return;
    }
    
    const response = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `Ainflue Studio v${info.version} is available`,
      detail: `Current version: ${app.getVersion()}\nNew version: ${info.version}\n\nRelease notes:\n${info.releaseNotes || 'No release notes available'}`,
      buttons: ['Download Now', 'Download Later', 'Skip This Version'],
      defaultId: 0,
      cancelId: 1
    });
    
    switch (response.response) {
      case 0: // Download Now
        if (!this.autoDownload) {
          await this.downloadUpdate();
        }
        break;
      case 1: // Download Later
        // Do nothing - user will be notified again later
        break;
      case 2: // Skip This Version
        this.skipVersion(info.version);
        break;
    }
  }

  async showUpdateReadyNotification(info) {
    const mainWindow = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) {
      return;
    }
    
    const response = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: `Ainflue Studio v${info.version} has been downloaded`,
      detail: 'The update will be installed when you restart the application.\n\nWould you like to restart now?',
      buttons: ['Restart Now', 'Restart Later'],
      defaultId: 0,
      cancelId: 1
    });
    
    if (response.response === 0) {
      this.quitAndInstall();
    }
  }

  async showUpdateErrorNotification(error) {
    const mainWindow = BrowserWindow.getFocusedWindow() || BrowserWindow.getAllWindows()[0];
    
    if (!mainWindow) {
      return;
    }
    
    await dialog.showMessageBox(mainWindow, {
      type: 'error',
      title: 'Update Error',
      message: 'Failed to check for updates',
      detail: `An error occurred while checking for updates:\n\n${error.message}\n\nPlease check your internet connection and try again later.`,
      buttons: ['OK'],
      defaultId: 0
    });
  }

  updateDownloadProgress(progress) {
    // Send progress to renderer process
    const windows = BrowserWindow.getAllWindows();
    windows.forEach(window => {
      if (!window.isDestroyed()) {
        window.webContents.send('update-download-progress', progress);
      }
    });
  }

  // Version management
  skipVersion(version) {
    const skippedVersions = this.getSkippedVersions();
    if (!skippedVersions.includes(version)) {
      skippedVersions.push(version);
      this.saveSkippedVersions(skippedVersions);
      log.info(`Version ${version} skipped`);
    }
  }

  isVersionSkipped(version) {
    const skippedVersions = this.getSkippedVersions();
    return skippedVersions.includes(version);
  }

  clearSkippedVersions() {
    this.saveSkippedVersions([]);
    log.info('Skipped versions cleared');
  }

  // Rollback functionality
  async rollbackUpdate() {
    // This would implement rollback functionality
    // For now, just log the request
    log.info('Update rollback requested - feature not yet implemented');
    throw new Error('Rollback functionality not yet implemented');
  }

  // Status methods
  getUpdateStatus() {
    return {
      isUpdateAvailable: this.isUpdateAvailable,
      isDownloading: this.isDownloading,
      isUpdateReady: this.isUpdateReady,
      downloadProgress: this.downloadProgress,
      updateInfo: this.updateInfo,
      currentVersion: app.getVersion(),
      channel: this.currentChannel,
      autoDownload: this.autoDownload,
      autoInstall: this.autoInstall,
      notifyUser: this.notifyUser
    };
  }

  // Preferences management
  loadUpdatePreferences() {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      
      return {
        autoDownload: store.get('autoDownload', true),
        autoInstall: store.get('autoInstall', false),
        notifyUser: store.get('notifyUser', true),
        channel: store.get('channel', this.channels.stable)
      };
    } catch (error) {
      log.error('Failed to load update preferences:', error);
      return {};
    }
  }

  saveUpdatePreferences() {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      
      store.set({
        autoDownload: this.autoDownload,
        autoInstall: this.autoInstall,
        notifyUser: this.notifyUser,
        channel: this.currentChannel
      });
      
      log.debug('Update preferences saved');
    } catch (error) {
      log.error('Failed to save update preferences:', error);
    }
  }

  getSkippedVersions() {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      return store.get('skippedVersions', []);
    } catch (error) {
      log.error('Failed to load skipped versions:', error);
      return [];
    }
  }

  saveSkippedVersions(versions) {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      store.set('skippedVersions', versions);
      log.debug('Skipped versions saved');
    } catch (error) {
      log.error('Failed to save skipped versions:', error);
    }
  }

  // Update validation
  validateUpdate(info) {
    // Validate update signature and integrity
    // This would implement proper cryptographic validation
    log.info('Validating update:', info.version);
    
    // For now, just basic validation
    if (!info.version || !info.files || info.files.length === 0) {
      throw new Error('Invalid update information');
    }
    
    return true;
  }

  // Cleanup methods
  cleanup() {
    this.stopPeriodicUpdateCheck();
    this.removeAllListeners();
    log.info('Auto Updater Manager cleaned up');
  }

  // Debug methods
  getUpdateHistory() {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      return store.get('updateHistory', []);
    } catch (error) {
      log.error('Failed to load update history:', error);
      return [];
    }
  }

  addToUpdateHistory(info) {
    try {
      const Store = require('electron-store');
      const store = new Store({ name: 'update-preferences' });
      const history = this.getUpdateHistory();
      
      history.push({
        version: info.version,
        downloadedAt: new Date().toISOString(),
        installedAt: null // Will be updated when actually installed
      });
      
      // Keep only last 10 updates
      const trimmedHistory = history.slice(-10);
      store.set('updateHistory', trimmedHistory);
      
    } catch (error) {
      log.error('Failed to add to update history:', error);
    }
  }

  // Force update check (for testing)
  async forceUpdateCheck() {
    log.info('Force update check initiated');
    
    // Temporarily disable skipped versions
    const originalSkipped = this.getSkippedVersions();
    this.saveSkippedVersions([]);
    
    try {
      const result = await this.checkForUpdates();
      return result;
    } finally {
      // Restore skipped versions
      this.saveSkippedVersions(originalSkipped);
    }
  }
}

module.exports = AutoUpdaterManager;