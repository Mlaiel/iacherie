/**
 * Ainflue Desktop - Window Manager
 * 
 * Advanced window management for multi-monitor desktop environments
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { BrowserWindow, screen, shell } = require('electron');
const path = require('path');
const log = require('electron-log');

class WindowManager {
  constructor() {
    this.windows = new Map();
    this.windowTypes = {
      main: 'Main Studio Window',
      timeline: 'Timeline Editor',
      mixer: 'Audio Mixer',
      preview: 'Content Preview',
      analytics: 'Analytics Dashboard',
      collaboration: 'Collaboration Hub',
      settings: 'Settings Panel'
    };
    this.defaultWindowSettings = {
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, '..', '..', 'preload.js')
      }
    };
  }

  async createMainWindow() {
    const displays = screen.getAllDisplays();
    const primaryDisplay = screen.getPrimaryDisplay();
    
    const windowConfig = {
      ...this.defaultWindowSettings,
      width: Math.min(1400, primaryDisplay.workAreaSize.width - 100),
      height: Math.min(900, primaryDisplay.workAreaSize.height - 100),
      x: primaryDisplay.workArea.x + 50,
      y: primaryDisplay.workArea.y + 50,
      title: 'Ainflue Studio',
      icon: path.join(__dirname, '..', '..', 'assets', 'icon.png'),
      show: false,
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--main-window']
      }
    };

    const mainWindow = new BrowserWindow(windowConfig);
    
    // Setup window event handlers
    this.setupWindowEventHandlers(mainWindow, 'main');
    
    // Load main interface
    await mainWindow.loadFile(path.join(__dirname, '..', '..', 'renderer', 'index.html'));
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
      }
    });

    this.windows.set('main', mainWindow);
    log.info('Main window created successfully');
    
    return mainWindow;
  }

  async createTimelineWindow() {
    const timelineConfig = {
      ...this.defaultWindowSettings,
      width: 1600,
      height: 400,
      title: 'Timeline Editor',
      parent: this.windows.get('main'),
      modal: false,
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--timeline-window']
      }
    };

    const timelineWindow = new BrowserWindow(timelineConfig);
    this.setupWindowEventHandlers(timelineWindow, 'timeline');
    
    await timelineWindow.loadFile(path.join(__dirname, '..', '..', 'renderer', 'timeline.html'));
    
    this.windows.set('timeline', timelineWindow);
    log.info('Timeline window created');
    
    return timelineWindow;
  }

  async createMixerWindow() {
    const mixerConfig = {
      ...this.defaultWindowSettings,
      width: 800,
      height: 600,
      title: 'Audio Mixer',
      resizable: true,
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--mixer-window']
      }
    };

    const mixerWindow = new BrowserWindow(mixerConfig);
    this.setupWindowEventHandlers(mixerWindow, 'mixer');
    
    await mixerWindow.loadURL('data:text/html,<h1>Audio Mixer - Coming Soon</h1>');
    
    this.windows.set('mixer', mixerWindow);
    log.info('Mixer window created');
    
    return mixerWindow;
  }

  async createPreviewWindow() {
    const previewConfig = {
      ...this.defaultWindowSettings,
      width: 640,
      height: 480,
      title: 'Content Preview',
      alwaysOnTop: true,
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--preview-window']
      }
    };

    const previewWindow = new BrowserWindow(previewConfig);
    this.setupWindowEventHandlers(previewWindow, 'preview');
    
    await previewWindow.loadURL('data:text/html,<h1>Preview Window</h1>');
    
    this.windows.set('preview', previewWindow);
    log.info('Preview window created');
    
    return previewWindow;
  }

  async createAnalyticsWindow() {
    const analyticsConfig = {
      ...this.defaultWindowSettings,
      width: 1200,
      height: 800,
      title: 'Analytics Dashboard',
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--analytics-window']
      }
    };

    const analyticsWindow = new BrowserWindow(analyticsConfig);
    this.setupWindowEventHandlers(analyticsWindow, 'analytics');
    
    await analyticsWindow.loadURL('data:text/html,<h1>Analytics Dashboard - Coming Soon</h1>');
    
    this.windows.set('analytics', analyticsWindow);
    log.info('Analytics window created');
    
    return analyticsWindow;
  }

  async createCollaborationWindow() {
    const collaborationConfig = {
      ...this.defaultWindowSettings,
      width: 1000,
      height: 700,
      title: 'Collaboration Hub',
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--collaboration-window']
      }
    };

    const collaborationWindow = new BrowserWindow(collaborationConfig);
    this.setupWindowEventHandlers(collaborationWindow, 'collaboration');
    
    await collaborationWindow.loadURL('data:text/html,<h1>Collaboration Hub - Coming Soon</h1>');
    
    this.windows.set('collaboration', collaborationWindow);
    log.info('Collaboration window created');
    
    return collaborationWindow;
  }

  async createSettingsWindow() {
    const settingsConfig = {
      ...this.defaultWindowSettings,
      width: 800,
      height: 600,
      title: 'Settings',
      parent: this.windows.get('main'),
      modal: true,
      resizable: false,
      webPreferences: {
        ...this.defaultWindowSettings.webPreferences,
        additionalArguments: ['--settings-window']
      }
    };

    const settingsWindow = new BrowserWindow(settingsConfig);
    this.setupWindowEventHandlers(settingsWindow, 'settings');
    
    await settingsWindow.loadURL('data:text/html,<h1>Settings Panel - Coming Soon</h1>');
    
    this.windows.set('settings', settingsWindow);
    log.info('Settings window created');
    
    return settingsWindow;
  }

  setupWindowEventHandlers(window, windowType) {
    window.on('closed', () => {
      this.windows.delete(windowType);
      log.info(`${windowType} window closed`);
    });

    window.on('resize', () => {
      this.saveWindowState(windowType, window);
    });

    window.on('move', () => {
      this.saveWindowState(windowType, window);
    });

    window.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    window.webContents.on('did-finish-load', () => {
      log.debug(`${windowType} window loaded successfully`);
    });
  }

  saveWindowState(windowType, window) {
    const bounds = window.getBounds();
    // In a real implementation, this would save to persistent storage
    log.debug(`Saved window state for ${windowType}:`, bounds);
  }

  restoreWindowState(windowType) {
    // In a real implementation, this would restore from persistent storage
    return null;
  }

  getWindow(windowType) {
    return this.windows.get(windowType);
  }

  getAllWindows() {
    return Array.from(this.windows.entries());
  }

  closeWindow(windowType) {
    const window = this.windows.get(windowType);
    if (window && !window.isDestroyed()) {
      window.close();
      return true;
    }
    return false;
  }

  closeAllWindows() {
    for (const [windowType, window] of this.windows) {
      if (!window.isDestroyed()) {
        window.close();
      }
    }
    this.windows.clear();
  }

  focusWindow(windowType) {
    const window = this.windows.get(windowType);
    if (window && !window.isDestroyed()) {
      if (window.isMinimized()) {
        window.restore();
      }
      window.focus();
      return true;
    }
    return false;
  }

  minimizeAllWindows() {
    for (const [windowType, window] of this.windows) {
      if (!window.isDestroyed() && !window.isMinimized()) {
        window.minimize();
      }
    }
  }

  restoreAllWindows() {
    for (const [windowType, window] of this.windows) {
      if (!window.isDestroyed() && window.isMinimized()) {
        window.restore();
      }
    }
  }

  // Multi-monitor support
  moveWindowToDisplay(windowType, displayId) {
    const window = this.windows.get(windowType);
    if (!window || window.isDestroyed()) {
      return false;
    }

    const displays = screen.getAllDisplays();
    const targetDisplay = displays.find(d => d.id === displayId);
    
    if (!targetDisplay) {
      log.warn(`Display ${displayId} not found`);
      return false;
    }

    const bounds = window.getBounds();
    const newX = targetDisplay.workArea.x + (targetDisplay.workAreaSize.width - bounds.width) / 2;
    const newY = targetDisplay.workArea.y + (targetDisplay.workAreaSize.height - bounds.height) / 2;
    
    window.setBounds({
      x: Math.round(newX),
      y: Math.round(newY),
      width: bounds.width,
      height: bounds.height
    });

    log.info(`Moved ${windowType} window to display ${displayId}`);
    return true;
  }

  getDisplayInfo() {
    return screen.getAllDisplays().map(display => ({
      id: display.id,
      bounds: display.bounds,
      workArea: display.workArea,
      scaleFactor: display.scaleFactor,
      isPrimary: display === screen.getPrimaryDisplay()
    }));
  }

  // Window arrangement presets
  arrangeStudioLayout() {
    const displays = screen.getAllDisplays();
    const primaryDisplay = screen.getPrimaryDisplay();
    
    // Main window on primary display
    const mainWindow = this.windows.get('main');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setBounds({
        x: primaryDisplay.workArea.x,
        y: primaryDisplay.workArea.y,
        width: Math.floor(primaryDisplay.workAreaSize.width * 0.7),
        height: Math.floor(primaryDisplay.workAreaSize.height * 0.8)
      });
    }
    
    // Timeline window below main
    const timelineWindow = this.windows.get('timeline');
    if (timelineWindow && !timelineWindow.isDestroyed()) {
      timelineWindow.setBounds({
        x: primaryDisplay.workArea.x,
        y: primaryDisplay.workArea.y + Math.floor(primaryDisplay.workAreaSize.height * 0.8),
        width: Math.floor(primaryDisplay.workAreaSize.width * 0.7),
        height: Math.floor(primaryDisplay.workAreaSize.height * 0.2)
      });
    }
    
    // Mixer on the right
    const mixerWindow = this.windows.get('mixer');
    if (mixerWindow && !mixerWindow.isDestroyed()) {
      mixerWindow.setBounds({
        x: primaryDisplay.workArea.x + Math.floor(primaryDisplay.workAreaSize.width * 0.7),
        y: primaryDisplay.workArea.y,
        width: Math.floor(primaryDisplay.workAreaSize.width * 0.3),
        height: Math.floor(primaryDisplay.workAreaSize.height * 0.5)
      });
    }
    
    log.info('Applied studio layout arrangement');
  }

  arrangeCollaborationLayout() {
    const displays = screen.getAllDisplays();
    const primaryDisplay = screen.getPrimaryDisplay();
    
    // Main window takes 60% of screen
    const mainWindow = this.windows.get('main');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.setBounds({
        x: primaryDisplay.workArea.x,
        y: primaryDisplay.workArea.y,
        width: Math.floor(primaryDisplay.workAreaSize.width * 0.6),
        height: primaryDisplay.workAreaSize.height
      });
    }
    
    // Collaboration window on the right
    const collaborationWindow = this.windows.get('collaboration');
    if (collaborationWindow && !collaborationWindow.isDestroyed()) {
      collaborationWindow.setBounds({
        x: primaryDisplay.workArea.x + Math.floor(primaryDisplay.workAreaSize.width * 0.6),
        y: primaryDisplay.workArea.y,
        width: Math.floor(primaryDisplay.workAreaSize.width * 0.4),
        height: primaryDisplay.workAreaSize.height
      });
    }
    
    log.info('Applied collaboration layout arrangement');
  }
}

module.exports = WindowManager;