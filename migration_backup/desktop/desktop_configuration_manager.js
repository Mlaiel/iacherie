/**
 * Ainflue Desktop - Configuration Management System
 * 
 * Professional configuration management with platform-specific optimizations
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const Store = require('electron-store');
const log = require('electron-log');
const os = require('os');
const path = require('path');
const fs = require('fs');

class DesktopConfigurationManager {
  constructor() {
    this.store = new Store({
      name: 'ainflue-config',
      encryptionKey: 'ainflue-desktop-config-2025',
      defaults: this.getDefaultConfiguration()
    });
    
    this.platformInfo = {
      platform: process.platform,
      arch: process.arch,
      release: os.release(),
      totalmem: os.totalmem(),
      cpus: os.cpus().length,
      homeDir: os.homedir(),
      tmpDir: os.tmpdir()
    };
    
    this.configPath = this.store.path;
    this.performanceMode = 'balanced'; // 'low', 'balanced', 'high', 'maximum'
    
    log.info('Configuration Manager initialized');
    log.info(`Configuration file: ${this.configPath}`);
  }

  async initialize() {
    try {
      // Detect system capabilities
      await this.detectSystemCapabilities();
      
      // Apply platform-specific optimizations
      this.applyPlatformOptimizations();
      
      // Setup performance monitoring
      this.setupPerformanceMonitoring();
      
      // Migrate old configurations if needed
      await this.migrateConfiguration();
      
      log.info('✅ Configuration Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Configuration Manager:', error);
      throw error;
    }
  }

  getDefaultConfiguration() {
    return {
      // Application Settings
      app: {
        version: '1.0.0',
        firstRun: true,
        language: 'en',
        theme: 'dark',
        autoSave: true,
        autoSaveInterval: 300000, // 5 minutes
        maxRecentProjects: 10,
        enableAnalytics: true
      },
      
      // Window Management
      window: {
        defaultWidth: 1400,
        defaultHeight: 900,
        minWidth: 1200,
        minHeight: 800,
        rememberSize: true,
        rememberPosition: true,
        openMaximized: false,
        enableFrameless: false
      },
      
      // Workspace Configuration
      workspace: {
        multiMonitorSupport: true,
        defaultLayout: 'single-monitor',
        timelineWindowEnabled: true,
        mixerWindowEnabled: true,
        previewWindowEnabled: true,
        autoCreateWorkspace: true,
        savePanelStates: true
      },
      
      // Performance Settings
      performance: {
        mode: 'balanced',
        hardwareAcceleration: true,
        gpuAcceleration: true,
        maxMemoryUsage: 0.7, // 70% of total RAM
        backgroundThrottling: false,
        enableFrameRate: 60,
        renderQuality: 'high'
      },
      
      // Audio Processing
      audio: {
        sampleRate: 48000,
        bitDepth: 24,
        bufferSize: 512,
        enableNoiseReduction: true,
        enableEcho: false,
        masterVolume: 0.8,
        inputDevice: 'default',
        outputDevice: 'default'
      },
      
      // Video Processing
      video: {
        defaultFormat: 'mp4',
        defaultCodec: 'h264',
        defaultResolution: '1920x1080',
        defaultFrameRate: 30,
        enableHardwareEncoding: true,
        previewQuality: 'high',
        exportQuality: 'high'
      },
      
      // AI Processing
      ai: {
        enableGPUAcceleration: true,
        modelCacheSize: 2048, // MB
        maxConcurrentTasks: 2,
        autoEnhancement: true,
        voiceCloningQuality: 'high',
        captionLanguage: 'en',
        processingTimeout: 300000 // 5 minutes
      },
      
      // Security Settings
      security: {
        enableEncryption: true,
        autoLockTimer: 1800000, // 30 minutes
        enableWatermarking: true,
        protectExports: true,
        secureFileHandling: true,
        enableLogging: true
      },
      
      // Network Configuration
      network: {
        enableProxy: false,
        proxyHost: '',
        proxyPort: 8080,
        connectionTimeout: 30000,
        retryAttempts: 3,
        enableSSL: true
      },
      
      // Developer Settings
      developer: {
        enableDevTools: false,
        enableDebugLogging: false,
        enableExperimentalFeatures: false,
        showPerformanceMetrics: false,
        enableBetaFeatures: false
      },
      
      // File Handling
      files: {
        defaultProjectPath: '',
        defaultExportPath: '',
        autoCleanupTemp: true,
        maxTempFileAge: 86400000, // 24 hours
        enableVersioning: true,
        maxVersions: 5
      },
      
      // Collaboration
      collaboration: {
        enableRealTime: true,
        autoSync: true,
        conflictResolution: 'manual',
        shareByDefault: false,
        notifyOnChanges: true
      }
    };
  }

  async detectSystemCapabilities() {
    log.info('Detecting system capabilities...');
    
    // Memory detection
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const memoryUsagePercent = (totalMemory - freeMemory) / totalMemory;
    
    // CPU detection
    const cpuInfo = os.cpus();
    const cpuModel = cpuInfo[0]?.model || 'Unknown';
    const cpuCores = cpuInfo.length;
    
    // Platform-specific optimizations
    let recommendedSettings = {};
    
    if (totalMemory < 4 * 1024 * 1024 * 1024) { // Less than 4GB
      recommendedSettings = {
        performance: { mode: 'low', maxMemoryUsage: 0.5 },
        ai: { maxConcurrentTasks: 1, modelCacheSize: 512 },
        video: { previewQuality: 'medium', enableHardwareEncoding: false }
      };
    } else if (totalMemory < 8 * 1024 * 1024 * 1024) { // Less than 8GB
      recommendedSettings = {
        performance: { mode: 'balanced', maxMemoryUsage: 0.6 },
        ai: { maxConcurrentTasks: 1, modelCacheSize: 1024 }
      };
    } else { // 8GB or more
      recommendedSettings = {
        performance: { mode: 'high', maxMemoryUsage: 0.7 },
        ai: { maxConcurrentTasks: 2, modelCacheSize: 2048 }
      };
    }
    
    // Apply recommended settings
    this.updateSettings(recommendedSettings);
    
    // Store system info
    this.set('system.detected', {
      memory: { total: totalMemory, free: freeMemory, usage: memoryUsagePercent },
      cpu: { model: cpuModel, cores: cpuCores },
      platform: this.platformInfo,
      detectedAt: new Date().toISOString()
    });
    
    log.info(`System: ${cpuModel}, ${cpuCores} cores, ${Math.round(totalMemory / 1024 / 1024 / 1024)}GB RAM`);
  }

  applyPlatformOptimizations() {
    const platform = process.platform;
    
    switch (platform) {
      case 'darwin': // macOS
        this.updateSettings({
          window: { enableFrameless: true },
          performance: { hardwareAcceleration: true },
          audio: { sampleRate: 48000, bufferSize: 256 }
        });
        break;
        
      case 'win32': // Windows
        this.updateSettings({
          performance: { enableFrameRate: 60 },
          video: { enableHardwareEncoding: true },
          audio: { bufferSize: 512 }
        });
        break;
        
      case 'linux': // Linux
        this.updateSettings({
          performance: { hardwareAcceleration: false }, // More compatible
          audio: { bufferSize: 1024 }, // Larger buffer for stability
          video: { enableHardwareEncoding: false }
        });
        break;
    }
    
    log.info(`Applied ${platform} platform optimizations`);
  }

  setupPerformanceMonitoring() {
    // Monitor memory usage every 30 seconds
    setInterval(() => {
      const memUsage = process.memoryUsage();
      const systemMem = {
        total: os.totalmem(),
        free: os.freemem()
      };
      
      // Check if memory usage is too high
      const memoryUsagePercent = memUsage.heapUsed / (1024 * 1024 * 1024); // GB
      const maxMemory = this.get('performance.maxMemoryUsage', 0.7) * (systemMem.total / 1024 / 1024 / 1024);
      
      if (memoryUsagePercent > maxMemory) {
        log.warn(`High memory usage detected: ${memoryUsagePercent.toFixed(2)}GB / ${maxMemory.toFixed(2)}GB`);
        // Trigger garbage collection if available
        if (global.gc) {
          global.gc();
        }
      }
      
      // Store performance metrics
      this.set('performance.metrics.lastUpdate', {
        memory: memUsage,
        system: systemMem,
        timestamp: Date.now()
      });
      
    }, 30000);
  }

  async migrateConfiguration() {
    const currentVersion = this.get('app.version', '0.0.0');
    const targetVersion = '1.0.0';
    
    if (currentVersion !== targetVersion) {
      log.info(`Migrating configuration from ${currentVersion} to ${targetVersion}`);
      
      // Migration logic would go here
      // For now, just update the version
      this.set('app.version', targetVersion);
      
      log.info('Configuration migration completed');
    }
  }

  // Configuration methods
  get(key, defaultValue = undefined) {
    return this.store.get(key, defaultValue);
  }

  set(key, value) {
    this.store.set(key, value);
    log.debug(`Configuration updated: ${key}`);
  }

  delete(key) {
    this.store.delete(key);
    log.debug(`Configuration deleted: ${key}`);
  }

  has(key) {
    return this.store.has(key);
  }

  clear() {
    this.store.clear();
    log.info('Configuration cleared');
  }

  updateSettings(newSettings) {
    const deepMerge = (target, source) => {
      for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
          if (!target[key]) target[key] = {};
          deepMerge(target[key], source[key]);
        } else {
          target[key] = source[key];
        }
      }
    };
    
    const currentSettings = this.store.store;
    deepMerge(currentSettings, newSettings);
    this.store.store = currentSettings;
    
    log.debug('Settings updated with new configuration');
  }

  // Performance mode management
  setPerformanceMode(mode) {
    const modes = {
      low: {
        performance: { hardwareAcceleration: false, enableFrameRate: 30 },
        ai: { maxConcurrentTasks: 1, enableGPUAcceleration: false },
        video: { previewQuality: 'low', enableHardwareEncoding: false }
      },
      balanced: {
        performance: { hardwareAcceleration: true, enableFrameRate: 60 },
        ai: { maxConcurrentTasks: 1, enableGPUAcceleration: true },
        video: { previewQuality: 'medium', enableHardwareEncoding: true }
      },
      high: {
        performance: { hardwareAcceleration: true, enableFrameRate: 60 },
        ai: { maxConcurrentTasks: 2, enableGPUAcceleration: true },
        video: { previewQuality: 'high', enableHardwareEncoding: true }
      },
      maximum: {
        performance: { hardwareAcceleration: true, enableFrameRate: 120 },
        ai: { maxConcurrentTasks: 4, enableGPUAcceleration: true },
        video: { previewQuality: 'ultra', enableHardwareEncoding: true }
      }
    };
    
    if (modes[mode]) {
      this.performanceMode = mode;
      this.updateSettings(modes[mode]);
      this.set('performance.mode', mode);
      log.info(`Performance mode set to: ${mode}`);
    }
  }

  getPerformanceMode() {
    return this.performanceMode;
  }

  // Project-specific settings
  getProjectSettings(projectId) {
    return this.get(`projects.${projectId}`, {});
  }

  setProjectSettings(projectId, settings) {
    this.set(`projects.${projectId}`, settings);
  }

  // Export/Import configuration
  exportConfiguration() {
    const config = { ...this.store.store };
    
    // Remove sensitive data
    delete config.security;
    delete config.network;
    
    return config;
  }

  importConfiguration(config) {
    // Validate configuration structure
    if (typeof config !== 'object') {
      throw new Error('Invalid configuration format');
    }
    
    // Merge with existing configuration
    this.updateSettings(config);
    log.info('Configuration imported successfully');
  }

  // Save configuration (for graceful shutdown)
  saveConfiguration() {
    try {
      // Force write to disk
      this.store.store = this.store.store;
      log.info('Configuration saved to disk');
    } catch (error) {
      log.error('Failed to save configuration:', error);
    }
  }

  // Backup and restore
  createBackup() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(path.dirname(this.configPath), `ainflue-config-backup-${timestamp}.json`);
    
    try {
      fs.writeFileSync(backupPath, JSON.stringify(this.store.store, null, 2));
      log.info(`Configuration backup created: ${backupPath}`);
      return backupPath;
    } catch (error) {
      log.error('Failed to create configuration backup:', error);
      throw error;
    }
  }

  restoreFromBackup(backupPath) {
    try {
      if (!fs.existsSync(backupPath)) {
        throw new Error('Backup file not found');
      }
      
      const backupData = JSON.parse(fs.readFileSync(backupPath, 'utf8'));
      this.store.store = backupData;
      log.info(`Configuration restored from backup: ${backupPath}`);
    } catch (error) {
      log.error('Failed to restore configuration from backup:', error);
      throw error;
    }
  }

  // Reset to defaults
  resetToDefaults() {
    const defaults = this.getDefaultConfiguration();
    this.store.store = defaults;
    log.info('Configuration reset to defaults');
  }

  // Get configuration summary for debugging
  getConfigurationSummary() {
    return {
      path: this.configPath,
      performanceMode: this.performanceMode,
      platform: this.platformInfo,
      keyCount: Object.keys(this.store.store).length,
      size: JSON.stringify(this.store.store).length
    };
  }
}

module.exports = DesktopConfigurationManager;