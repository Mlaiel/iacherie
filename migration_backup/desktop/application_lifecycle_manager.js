/**
 * Ainflue Desktop - Application Lifecycle Manager
 * 
 * Professional lifecycle management with graceful shutdown and state persistence
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { BrowserWindow, app, screen } = require('electron');
const log = require('electron-log');
const path = require('path');
const fs = require('fs');
const EventEmitter = require('events');

class ApplicationLifecycleManager extends EventEmitter {
  constructor() {
    super();
    
    this.windows = new Map();
    this.backgroundProcesses = new Set();
    this.temporaryFiles = new Set();
    this.applicationState = {};
    this.isShuttingDown = false;
    this.readyToQuit = false;
    this.lastSaveTime = Date.now();
    
    // Lifecycle phases
    this.phases = {
      INITIALIZING: 'initializing',
      READY: 'ready',
      ACTIVE: 'active',
      SUSPENDING: 'suspending',
      SUSPENDED: 'suspended',
      RESUMING: 'resuming',
      SHUTTING_DOWN: 'shutting_down',
      SHUTDOWN: 'shutdown'
    };
    
    this.currentPhase = this.phases.INITIALIZING;
    
    log.info('Application Lifecycle Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Application Lifecycle Manager...');
      
      // Load previous application state
      await this.loadApplicationState();
      
      // Setup auto-save interval
      this.setupAutoSave();
      
      // Initialize main window
      await this.createMainWindow();
      
      // Setup window management
      this.setupWindowManagement();
      
      // Setup cleanup handlers
      this.setupCleanupHandlers();
      
      this.setPhase(this.phases.READY);
      log.info('✅ Application Lifecycle Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Application Lifecycle Manager:', error);
      throw error;
    }
  }

  async createMainWindow() {
    if (this.windows.has('main')) {
      return this.windows.get('main');
    }

    // Get display configuration
    const displays = screen.getAllDisplays();
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    // Calculate window dimensions
    const windowWidth = Math.min(1400, width - 100);
    const windowHeight = Math.min(900, height - 100);

    // Create main window
    const mainWindow = new BrowserWindow({
      width: windowWidth,
      height: windowHeight,
      minWidth: 1200,
      minHeight: 800,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: process.env.NODE_ENV === 'production',
        spellcheck: false,
        backgroundThrottling: false
      },
      icon: this.getApplicationIcon(),
      title: 'Ainflue Studio - Professional AI Content Creation',
      backgroundColor: '#1f2937',
      show: false,
      resizable: true,
      maximizable: true,
      fullscreenable: true,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      autoHideMenuBar: process.platform === 'win32'
    });

    // Load application content
    await mainWindow.loadFile('renderer/index.html');

    // Setup window events
    this.setupMainWindowEvents(mainWindow);

    // Register window
    this.registerWindow('main', mainWindow);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      this.setPhase(this.phases.ACTIVE);
      this.emit('main-window-ready', mainWindow);
    });

    return mainWindow;
  }

  setupMainWindowEvents(window) {
    // Window state events
    window.on('minimize', () => {
      log.debug('Main window minimized');
      this.emit('window-state-changed', { type: 'minimize', window: 'main' });
    });

    window.on('maximize', () => {
      log.debug('Main window maximized');
      this.emit('window-state-changed', { type: 'maximize', window: 'main' });
    });

    window.on('unmaximize', () => {
      log.debug('Main window unmaximized');
      this.emit('window-state-changed', { type: 'unmaximize', window: 'main' });
    });

    window.on('enter-full-screen', () => {
      log.debug('Main window entered full screen');
      this.emit('window-state-changed', { type: 'enter-fullscreen', window: 'main' });
    });

    window.on('leave-full-screen', () => {
      log.debug('Main window left full screen');
      this.emit('window-state-changed', { type: 'leave-fullscreen', window: 'main' });
    });

    // Focus events
    window.on('focus', () => {
      this.emit('window-focus-changed', { focused: true, window: 'main' });
    });

    window.on('blur', () => {
      this.emit('window-focus-changed', { focused: false, window: 'main' });
    });

    // Close event
    window.on('close', (event) => {
      if (!this.readyToQuit && !this.isShuttingDown) {
        event.preventDefault();
        this.handleMainWindowClose(window);
      }
    });

    window.on('closed', () => {
      this.unregisterWindow('main');
      log.info('Main window closed');
    });

    // Handle external link clicks
    window.webContents.setWindowOpenHandler(({ url }) => {
      require('electron').shell.openExternal(url);
      return { action: 'deny' };
    });

    // Setup web contents events
    this.setupWebContentsEvents(window.webContents);
  }

  setupWebContentsEvents(webContents) {
    webContents.on('did-finish-load', () => {
      log.debug('Web contents finished loading');
      this.emit('content-loaded');
    });

    webContents.on('dom-ready', () => {
      log.debug('DOM ready');
      this.emit('dom-ready');
    });

    webContents.on('console-message', (event, level, message, line, sourceId) => {
      if (level >= 2) { // Warning or error
        log.warn(`Renderer console [${level}]: ${message} (${sourceId}:${line})`);
      }
    });

    webContents.on('crashed', (event, killed) => {
      log.error('Web contents crashed, killed:', killed);
      this.handleWebContentsCrash(webContents);
    });
  }

  async handleMainWindowClose(window) {
    log.info('Main window close requested - preparing for shutdown');
    
    try {
      // Save current state
      await this.saveApplicationState();
      
      // Show minimized state instead of closing if configured
      if (this.shouldMinimizeToTray()) {
        window.hide();
        return;
      }
      
      // Start shutdown process
      this.initiateShutdown();
      
    } catch (error) {
      log.error('Error handling main window close:', error);
      this.forceQuit();
    }
  }

  async handleWebContentsCrash(webContents) {
    log.error('Web contents crashed - attempting recovery');
    
    try {
      // Find the window that crashed
      const crashedWindow = BrowserWindow.fromWebContents(webContents);
      if (crashedWindow) {
        // Reload the window
        await crashedWindow.reload();
        log.info('Successfully reloaded crashed window');
      }
    } catch (error) {
      log.error('Failed to recover from web contents crash:', error);
      // Create new main window if main crashed
      if (webContents === this.getMainWindow()?.webContents) {
        await this.createMainWindow();
      }
    }
  }

  setupWindowManagement() {
    // Monitor display changes
    screen.on('display-added', (event, newDisplay) => {
      log.info('Display added:', newDisplay.id);
      this.emit('display-changed', { type: 'added', display: newDisplay });
    });

    screen.on('display-removed', (event, oldDisplay) => {
      log.info('Display removed:', oldDisplay.id);
      this.emit('display-changed', { type: 'removed', display: oldDisplay });
    });

    screen.on('display-metrics-changed', (event, display, changedMetrics) => {
      log.debug('Display metrics changed:', display.id, changedMetrics);
      this.emit('display-changed', { type: 'metrics', display, changedMetrics });
    });
  }

  setupAutoSave() {
    // Auto-save every 5 minutes
    this.autoSaveInterval = setInterval(async () => {
      if (this.currentPhase === this.phases.ACTIVE) {
        await this.saveApplicationState();
      }
    }, 5 * 60 * 1000);

    log.info('Auto-save enabled (5 minute intervals)');
  }

  setupCleanupHandlers() {
    // Cleanup temp files every hour
    this.cleanupInterval = setInterval(() => {
      this.cleanupTemporaryFiles();
    }, 60 * 60 * 1000);

    log.info('Cleanup handlers initialized');
  }

  // Window management methods
  registerWindow(name, window) {
    this.windows.set(name, window);
    log.debug(`Window registered: ${name}`);
    this.emit('window-registered', { name, window });
  }

  unregisterWindow(name) {
    if (this.windows.has(name)) {
      this.windows.delete(name);
      log.debug(`Window unregistered: ${name}`);
      this.emit('window-unregistered', { name });
    }
  }

  getWindow(name) {
    return this.windows.get(name);
  }

  getMainWindow() {
    return this.windows.get('main');
  }

  getAllWindows() {
    return Array.from(this.windows.values());
  }

  // Background process management
  registerBackgroundProcess(name, process) {
    this.backgroundProcesses.add({ name, process });
    log.debug(`Background process registered: ${name}`);
  }

  async stopBackgroundProcesses() {
    log.info('Stopping background processes...');
    
    for (const { name, process } of this.backgroundProcesses) {
      try {
        if (process.kill) {
          process.kill();
        } else if (process.stop) {
          await process.stop();
        } else if (process.terminate) {
          await process.terminate();
        }
        log.debug(`Background process stopped: ${name}`);
      } catch (error) {
        log.error(`Failed to stop background process ${name}:`, error);
      }
    }
    
    this.backgroundProcesses.clear();
  }

  // File management
  registerTemporaryFile(filePath) {
    this.temporaryFiles.add(filePath);
    log.debug(`Temporary file registered: ${filePath}`);
  }

  cleanupTemporaryFiles() {
    let cleanedCount = 0;
    
    for (const filePath of this.temporaryFiles) {
      try {
        if (fs.existsSync(filePath)) {
          fs.unlinkSync(filePath);
          cleanedCount++;
        }
        this.temporaryFiles.delete(filePath);
      } catch (error) {
        log.error(`Failed to cleanup temporary file ${filePath}:`, error);
      }
    }
    
    if (cleanedCount > 0) {
      log.info(`Cleaned up ${cleanedCount} temporary files`);
    }
  }

  // State management
  async saveApplicationState() {
    try {
      const state = {
        windows: this.getWindowStates(),
        workspace: this.getWorkspaceState(),
        preferences: this.getPreferencesState(),
        projects: this.getProjectsState(),
        timestamp: new Date().toISOString(),
        version: app.getVersion()
      };

      this.applicationState = state;
      this.lastSaveTime = Date.now();
      
      // Save to file
      const statePath = this.getStatePath();
      fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
      
      log.debug('Application state saved');
      this.emit('state-saved', state);
      
    } catch (error) {
      log.error('Failed to save application state:', error);
      throw error;
    }
  }

  async loadApplicationState() {
    try {
      const statePath = this.getStatePath();
      
      if (fs.existsSync(statePath)) {
        const stateData = fs.readFileSync(statePath, 'utf8');
        this.applicationState = JSON.parse(stateData);
        
        log.info('Application state loaded from previous session');
        this.emit('state-loaded', this.applicationState);
      } else {
        log.info('No previous application state found - starting fresh');
        this.applicationState = {};
      }
      
    } catch (error) {
      log.error('Failed to load application state:', error);
      this.applicationState = {};
    }
  }

  getWindowStates() {
    const states = {};
    
    for (const [name, window] of this.windows) {
      if (window && !window.isDestroyed()) {
        const bounds = window.getBounds();
        states[name] = {
          bounds,
          maximized: window.isMaximized(),
          minimized: window.isMinimized(),
          fullscreen: window.isFullScreen(),
          visible: window.isVisible()
        };
      }
    }
    
    return states;
  }

  getWorkspaceState() {
    // Get workspace state from renderer if available
    const mainWindow = this.getMainWindow();
    if (mainWindow && !mainWindow.isDestroyed()) {
      // This would be implemented to get workspace state from renderer
      return { layout: 'default' };
    }
    return {};
  }

  getPreferencesState() {
    // Get preferences from configuration manager
    return { theme: 'dark', language: 'en' };
  }

  getProjectsState() {
    // Get current project state
    return { activeProject: null, recentProjects: [] };
  }

  // Lifecycle phase management
  setPhase(phase) {
    if (this.currentPhase !== phase) {
      const previousPhase = this.currentPhase;
      this.currentPhase = phase;
      
      log.info(`Application phase changed: ${previousPhase} → ${phase}`);
      this.emit('phase-changed', { from: previousPhase, to: phase });
    }
  }

  getCurrentPhase() {
    return this.currentPhase;
  }

  // System event handlers
  async handleActivation() {
    log.info('Application activation requested');
    
    if (this.currentPhase === this.phases.SUSPENDED) {
      this.setPhase(this.phases.RESUMING);
      await this.resumeFromSuspension();
    }
    
    const mainWindow = this.getMainWindow();
    if (mainWindow) {
      if (mainWindow.isMinimized()) {
        mainWindow.restore();
      }
      mainWindow.show();
      mainWindow.focus();
    } else {
      await this.createMainWindow();
    }
    
    this.setPhase(this.phases.ACTIVE);
  }

  async handleSystemSuspend() {
    log.info('System suspension detected');
    this.setPhase(this.phases.SUSPENDING);
    
    // Save current state
    await this.saveApplicationState();
    
    // Pause background processes
    this.pauseBackgroundProcesses();
    
    this.setPhase(this.phases.SUSPENDED);
  }

  async handleSystemResume() {
    log.info('System resume detected');
    this.setPhase(this.phases.RESUMING);
    
    // Resume background processes
    this.resumeBackgroundProcesses();
    
    // Reload application state if needed
    await this.loadApplicationState();
    
    this.setPhase(this.phases.ACTIVE);
  }

  pauseBackgroundProcesses() {
    // Implementation for pausing background processes
    log.debug('Background processes paused');
  }

  resumeBackgroundProcesses() {
    // Implementation for resuming background processes
    log.debug('Background processes resumed');
  }

  async resumeFromSuspension() {
    // Implementation for resuming from suspension
    log.debug('Resuming from suspension');
  }

  // Shutdown management
  async initiateShutdown() {
    if (this.isShuttingDown) {
      return;
    }
    
    this.isShuttingDown = true;
    this.setPhase(this.phases.SHUTTING_DOWN);
    
    log.info('Initiating graceful shutdown...');
    
    try {
      // Save application state
      await this.saveApplicationState();
      
      // Close non-essential windows
      await this.closeNonEssentialWindows();
      
      // Stop background processes
      await this.stopBackgroundProcesses();
      
      // Cleanup temporary files
      this.cleanupTemporaryFiles();
      
      // Clear intervals
      if (this.autoSaveInterval) {
        clearInterval(this.autoSaveInterval);
      }
      if (this.cleanupInterval) {
        clearInterval(this.cleanupInterval);
      }
      
      this.readyToQuit = true;
      this.setPhase(this.phases.SHUTDOWN);
      
      log.info('✅ Graceful shutdown completed');
      app.quit();
      
    } catch (error) {
      log.error('Error during shutdown:', error);
      this.forceQuit();
    }
  }

  async closeNonEssentialWindows() {
    const mainWindow = this.getMainWindow();
    
    for (const [name, window] of this.windows) {
      if (name !== 'main' && window && !window.isDestroyed()) {
        try {
          window.close();
          log.debug(`Closed window: ${name}`);
        } catch (error) {
          log.error(`Failed to close window ${name}:`, error);
        }
      }
    }
  }

  forceQuit() {
    log.warn('Force quitting application');
    this.readyToQuit = true;
    app.exit(1);
  }

  isReadyToQuit() {
    return this.readyToQuit;
  }

  canQuit() {
    return this.readyToQuit || this.currentPhase === this.phases.SHUTDOWN;
  }

  markReadyToQuit() {
    this.readyToQuit = true;
  }

  shouldMinimizeToTray() {
    // Configuration would determine this
    return false;
  }

  // Utility methods
  getApplicationIcon() {
    const platform = process.platform;
    const iconPath = path.join(__dirname, 'assets');
    
    switch (platform) {
      case 'win32':
        return path.join(iconPath, 'icon.ico');
      case 'darwin':
        return path.join(iconPath, 'icon.icns');
      default:
        return path.join(iconPath, 'icon.png');
    }
  }

  getStatePath() {
    const userDataPath = app.getPath('userData');
    return path.join(userDataPath, 'application-state.json');
  }

  // Performance monitoring
  getPerformanceMetrics() {
    const mainWindow = this.getMainWindow();
    const memUsage = process.memoryUsage();
    
    return {
      memory: memUsage,
      windows: this.windows.size,
      backgroundProcesses: this.backgroundProcesses.size,
      temporaryFiles: this.temporaryFiles.size,
      phase: this.currentPhase,
      uptime: process.uptime(),
      lastSave: this.lastSaveTime,
      mainWindowVisible: mainWindow ? mainWindow.isVisible() : false
    };
  }
}

module.exports = ApplicationLifecycleManager;