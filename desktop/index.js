/**
 * Ainflue Desktop - Application Entry Point
 * 
 * Professional AI content creation studio with advanced architecture
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { app, powerMonitor } = require('electron');
const log = require('electron-log');
const path = require('path');

// Import configuration and lifecycle managers
const DesktopConfigurationManager = require('./desktop_configuration_manager');
const ApplicationLifecycleManager = require('./application_lifecycle_manager');
const DesktopSecurityManager = require('./desktop_security_manager');
const AutoUpdaterManager = require('./auto_updater_manager');

class AinflueMasterApplication {
  constructor() {
    this.appName = 'Ainflue Desktop Studio';
    this.version = '1.0.0';
    this.author = 'Fahed Mlaiel';
    this.isProduction = !process.argv.includes('--dev');
    
    // Initialize managers
    this.configManager = new DesktopConfigurationManager();
    this.lifecycleManager = new ApplicationLifecycleManager();
    this.securityManager = new DesktopSecurityManager();
    this.autoUpdater = new AutoUpdaterManager();
    
    this.initializeLogging();
    this.setupApplicationEvents();
    this.enforceSecurityPolicies();
  }

  initializeLogging() {
    // Configure professional logging
    log.transports.file.level = this.isProduction ? 'info' : 'debug';
    log.transports.file.maxSize = 10 * 1024 * 1024; // 10MB
    log.transports.file.format = '[{y}-{m}-{d} {h}:{i}:{s}.{ms}] [{level}] {text}';
    
    log.info(`🎵 Initializing ${this.appName} v${this.version}`);
    log.info(`Platform: ${process.platform} ${process.arch}`);
    log.info(`Node: ${process.version}, Electron: ${process.versions.electron}`);
    log.info(`Production Mode: ${this.isProduction}`);
    log.info(`Created by: ${this.author} (mlaiel@live.de)`);
  }

  setupApplicationEvents() {
    // Configure app metadata
    app.setName(this.appName);
    app.setVersion(this.version);
    
    // Set app user model ID for Windows
    if (process.platform === 'win32') {
      app.setAppUserModelId('com.ainflue.desktop');
    }

    // Handle application ready event
    app.whenReady().then(async () => {
      log.info('Application ready - starting initialization sequence');
      
      try {
        // Load configuration first
        await this.configManager.initialize();
        
        // Setup security policies
        await this.securityManager.enforceSecurityPolicies();
        
        // Initialize lifecycle manager
        await this.lifecycleManager.initialize();
        
        // Setup auto-updater in production
        if (this.isProduction) {
          await this.autoUpdater.initialize();
        }
        
        log.info('✅ Application initialization completed successfully');
        
      } catch (error) {
        log.error('❌ Failed to initialize application:', error);
        app.quit();
      }
    });

    // Application window events
    app.on('window-all-closed', () => {
      log.info('All windows closed');
      if (process.platform !== 'darwin') {
        this.gracefulShutdown();
      }
    });

    app.on('activate', async () => {
      log.info('Application activated');
      if (this.lifecycleManager) {
        await this.lifecycleManager.handleActivation();
      }
    });

    // Handle before quit
    app.on('before-quit', (event) => {
      log.info('Application preparing to quit');
      
      if (!this.lifecycleManager.isReadyToQuit()) {
        event.preventDefault();
        this.prepareShutdown();
      }
    });

    // Handle will quit
    app.on('will-quit', (event) => {
      if (!this.lifecycleManager.canQuit()) {
        event.preventDefault();
        log.info('Quit prevented - cleanup in progress');
      }
    });

    // Certificate error handling for security
    app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
      log.warn('Certificate error for URL:', url, error);
      
      if (this.isProduction) {
        // In production, be strict about certificates
        callback(false);
      } else {
        // In development, allow self-signed certificates
        event.preventDefault();
        callback(true);
      }
    });

    // Web contents creation security
    app.on('web-contents-created', (event, contents) => {
      this.securityManager.secureWebContents(contents);
    });

    // Handle protocol schemes
    if (process.defaultApp) {
      if (process.argv.length >= 2) {
        app.setAsDefaultProtocolClient('ainflue', process.execPath, [path.resolve(process.argv[1])]);
      }
    } else {
      app.setAsDefaultProtocolClient('ainflue');
    }

    // Power monitoring for professional workflows
    if (powerMonitor) {
      powerMonitor.on('suspend', () => {
        log.info('System suspending - pausing workflows');
        this.lifecycleManager.handleSystemSuspend();
      });

      powerMonitor.on('resume', () => {
        log.info('System resumed - restoring workflows');
        this.lifecycleManager.handleSystemResume();
      });

      powerMonitor.on('on-ac', () => {
        log.info('System on AC power - enabling high performance mode');
        this.configManager.setPerformanceMode('high');
      });

      powerMonitor.on('on-battery', () => {
        log.info('System on battery power - enabling power saving mode');
        this.configManager.setPerformanceMode('balanced');
      });
    }
  }

  enforceSecurityPolicies() {
    // Disable node integration in renderer processes
    app.commandLine.appendSwitch('disable-node-integration');
    
    // Enable context isolation
    app.commandLine.appendSwitch('enable-context-isolation');
    
    // Disable web security in development only
    if (!this.isProduction) {
      app.commandLine.appendSwitch('disable-web-security');
    }
    
    // Enable hardware acceleration for professional video editing
    if (this.configManager.get('hardware.acceleration.enabled', true)) {
      log.info('Hardware acceleration enabled for professional workflows');
    } else {
      app.disableHardwareAcceleration();
      log.info('Hardware acceleration disabled by user preference');
    }
  }

  async prepareShutdown() {
    log.info('Preparing application shutdown...');
    
    try {
      // Save application state
      await this.lifecycleManager.saveApplicationState();
      
      // Close all non-essential windows
      await this.lifecycleManager.closeNonEssentialWindows();
      
      // Stop background processes
      await this.lifecycleManager.stopBackgroundProcesses();
      
      // Mark ready for quit
      this.lifecycleManager.markReadyToQuit();
      
      // Attempt quit again
      app.quit();
      
    } catch (error) {
      log.error('Error during shutdown preparation:', error);
      app.exit(1);
    }
  }

  gracefulShutdown() {
    log.info('Initiating graceful shutdown...');
    
    // Save user preferences
    this.configManager.saveConfiguration();
    
    // Clean up temporary files
    this.lifecycleManager.cleanupTemporaryFiles();
    
    // Log shutdown
    log.info('✅ Application shutdown completed');
    
    app.quit();
  }

  // Public API for external access
  getConfigManager() {
    return this.configManager;
  }

  getLifecycleManager() {
    return this.lifecycleManager;
  }

  getSecurityManager() {
    return this.securityManager;
  }

  getAutoUpdater() {
    return this.autoUpdater;
  }
}

// Global error handling
process.on('uncaughtException', (error) => {
  log.error('Uncaught Exception:', error);
  if (log.transports.file) {
    log.transports.file.getFile().write(`FATAL ERROR: ${error.stack}\n`);
  }
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  log.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Initialize application
const masterApp = new AinflueMasterApplication();

// Export for external access
module.exports = masterApp;

// Legal notice
log.info('© 2025 Fahed Mlaiel. All rights reserved.');
log.info('This software is protected by international copyright law.');
log.info('Contact: mlaiel@live.de for licensing inquiries.');