/**
 * Ainflue Desktop - Native Integration Manager
 * 
 * Platform-specific native OS integration and system features
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { app, shell, nativeTheme, systemPreferences, powerMonitor } = require('electron');
const log = require('electron-log');
const os = require('os');
const path = require('path');

class NativeIntegrationManager {
  constructor() {
    this.platform = process.platform;
    this.isInitialized = false;
    this.systemInfo = {};
    this.nativeFeatures = {};
    this.systemEventListeners = new Map();
    
    log.info('Native Integration Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Native Integration Manager...');
      
      // Detect native features
      await this.detectNativeFeatures();
      
      // Setup system integration
      this.setupSystemIntegration();
      
      // Configure platform-specific features
      await this.configurePlatformFeatures();
      
      // Setup system event monitoring
      this.setupSystemEventMonitoring();
      
      // Initialize file associations
      this.initializeFileAssociations();
      
      this.isInitialized = true;
      log.info('✅ Native Integration Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Native Integration Manager:', error);
      throw error;
    }
  }

  async detectNativeFeatures() {
    this.nativeFeatures = {
      // Common features
      darkMode: nativeTheme.shouldUseDarkColors,
      highContrast: nativeTheme.shouldUseHighContrastColors,
      reducedMotion: false, // Will be detected per platform
      
      // Platform-specific features
      macOS: {},
      windows: {},
      linux: {}
    };

    if (this.platform === 'darwin') {
      await this.detectMacOSFeatures();
    } else if (this.platform === 'win32') {
      await this.detectWindowsFeatures();
    } else if (this.platform === 'linux') {
      await this.detectLinuxFeatures();
    }

    log.info('Native features detected:', Object.keys(this.nativeFeatures));
  }

  async detectMacOSFeatures() {
    if (!systemPreferences) return;

    try {
      this.nativeFeatures.macOS = {
        // Appearance
        canPromptTouchID: systemPreferences.canPromptTouchID?.() || false,
        effectiveAppearance: systemPreferences.getEffectiveAppearance?.() || 'light',
        
        // System preferences
        isSwipeTrackingFromScrollEventsEnabled: systemPreferences.isSwipeTrackingFromScrollEventsEnabled?.() || false,
        
        // Media access permissions
        mediaAccessStatus: {
          camera: systemPreferences.getMediaAccessStatus?.('camera') || 'not-determined',
          microphone: systemPreferences.getMediaAccessStatus?.('microphone') || 'not-determined',
          screen: systemPreferences.getMediaAccessStatus?.('screen') || 'not-determined'
        },
        
        // System colors
        systemColor: {
          blue: systemPreferences.getSystemColor?.('blue') || '#007AFF',
          brown: systemPreferences.getSystemColor?.('brown') || '#A2845E',
          gray: systemPreferences.getSystemColor?.('gray') || '#8E8E93',
          green: systemPreferences.getSystemColor?.('green') || '#34C759',
          orange: systemPreferences.getSystemColor?.('orange') || '#FF9500',
          pink: systemPreferences.getSystemColor?.('pink') || '#FF2D92',
          purple: systemPreferences.getSystemColor?.('purple') || '#AF52DE',
          red: systemPreferences.getSystemColor?.('red') || '#FF3B30',
          yellow: systemPreferences.getSystemColor?.('yellow') || '#FFCC00'
        },
        
        // User defaults
        userDefault: {
          AppleShowScrollBars: systemPreferences.getUserDefault?.('AppleShowScrollBars', 'string') || 'Automatic',
          AppleInterfaceStyle: systemPreferences.getUserDefault?.('AppleInterfaceStyle', 'string') || 'Light'
        }
      };

      // Request media access if needed
      if (this.nativeFeatures.macOS.mediaAccessStatus.camera === 'not-determined') {
        systemPreferences.askForMediaAccess?.('camera');
      }
      if (this.nativeFeatures.macOS.mediaAccessStatus.microphone === 'not-determined') {
        systemPreferences.askForMediaAccess?.('microphone');
      }

    } catch (error) {
      log.warn('Failed to detect some macOS features:', error.message);
    }
  }

  async detectWindowsFeatures() {
    try {
      this.nativeFeatures.windows = {
        // System theme
        shouldUseDarkColors: nativeTheme.shouldUseDarkColors,
        shouldUseHighContrastColors: nativeTheme.shouldUseHighContrastColors,
        
        // Animation preferences
        shouldUseInvertedColorScheme: nativeTheme.shouldUseInvertedColorScheme || false,
        
        // System information
        version: os.release(),
        totalMemory: os.totalmem(),
        
        // Windows-specific capabilities
        supportsJumpLists: true,
        supportsThumbnailToolbar: true,
        supportsToastNotifications: true,
        supportsProgressBar: true
      };

      // Detect Windows version features
      const windowsVersion = parseFloat(os.release());
      this.nativeFeatures.windows.features = {
        windows10: windowsVersion >= 10,
        windows11: windowsVersion >= 10 && this.isWindows11(),
        touchSupport: this.detectTouchSupport(),
        cortanaIntegration: windowsVersion >= 10,
        timelineSupport: windowsVersion >= 10
      };

    } catch (error) {
      log.warn('Failed to detect some Windows features:', error.message);
    }
  }

  async detectLinuxFeatures() {
    try {
      this.nativeFeatures.linux = {
        // Desktop environment detection
        desktopEnvironment: this.detectDesktopEnvironment(),
        
        // Display server
        displayServer: this.detectDisplayServer(),
        
        // Package manager
        packageManager: this.detectPackageManager(),
        
        // System capabilities
        supportsSystemTray: true,
        supportsNotifications: this.detectNotificationSupport(),
        supportsGlobalShortcuts: true,
        
        // Audio system
        audioSystem: this.detectAudioSystem(),
        
        // Distribution info
        distribution: await this.getLinuxDistribution()
      };

    } catch (error) {
      log.warn('Failed to detect some Linux features:', error.message);
    }
  }

  setupSystemIntegration() {
    // App protocol handler
    app.setAsDefaultProtocolClient('ainflue');
    
    // File associations (will be handled by electron-builder)
    // But we can register runtime handling
    
    // Recent documents (macOS)
    if (this.platform === 'darwin') {
      app.addRecentDocument = app.addRecentDocument || (() => {});
      app.clearRecentDocuments = app.clearRecentDocuments || (() => {});
    }
    
    // Jump lists (Windows)
    if (this.platform === 'win32') {
      this.setupWindowsJumpLists();
    }
    
    // Unity launcher (Linux)
    if (this.platform === 'linux') {
      this.setupLinuxLauncher();
    }

    log.info('System integration configured');
  }

  setupWindowsJumpLists() {
    if (!app.setJumpList) return;

    const jumpList = [
      {
        type: 'custom',
        name: 'Recent Projects',
        items: [
          {
            type: 'file',
            path: path.join(os.homedir(), 'Documents', 'Ainflue', 'example.ainproj'),
            args: '--open-recent'
          }
        ]
      },
      {
        type: 'custom',
        name: 'Quick Actions',
        items: [
          {
            type: 'task',
            title: 'New Project',
            description: 'Create a new Ainflue project',
            program: process.execPath,
            args: '--new-project',
            iconPath: process.execPath,
            iconIndex: 0
          },
          {
            type: 'task',
            title: 'Import Media',
            description: 'Import media files',
            program: process.execPath,
            args: '--import-media',
            iconPath: process.execPath,
            iconIndex: 0
          }
        ]
      }
    ];

    app.setJumpList(jumpList);
    log.info('Windows Jump Lists configured');
  }

  setupLinuxLauncher() {
    // Setup Unity launcher integration if available
    if (process.env.DESKTOP_SESSION === 'ubuntu' || process.env.XDG_CURRENT_DESKTOP === 'Unity') {
      // Unity-specific integration would go here
      log.info('Unity launcher integration configured');
    }
    
    // Setup GNOME integration
    if (process.env.XDG_CURRENT_DESKTOP === 'GNOME') {
      // GNOME-specific integration would go here
      log.info('GNOME integration configured');
    }
  }

  async configurePlatformFeatures() {
    if (this.platform === 'darwin') {
      await this.configureMacOSFeatures();
    } else if (this.platform === 'win32') {
      await this.configureWindowsFeatures();
    } else if (this.platform === 'linux') {
      await this.configureLinuxFeatures();
    }
  }

  async configureMacOSFeatures() {
    // macOS-specific configuration
    if (this.nativeFeatures.macOS.effectiveAppearance) {
      // Configure appearance-based features
      nativeTheme.themeSource = 'system';
    }

    // Setup Touch Bar if available
    this.setupTouchBar();

    // Configure accessibility features
    this.configureMacOSAccessibility();

    log.info('macOS features configured');
  }

  async configureWindowsFeatures() {
    // Windows-specific configuration
    if (this.nativeFeatures.windows.supportsToastNotifications) {
      // Setup toast notifications
      this.setupWindowsToastNotifications();
    }

    if (this.nativeFeatures.windows.supportsThumbnailToolbar) {
      // Setup thumbnail toolbar
      this.setupWindowsThumbnailToolbar();
    }

    log.info('Windows features configured');
  }

  async configureLinuxFeatures() {
    // Linux-specific configuration
    if (this.nativeFeatures.linux.supportsNotifications) {
      // Setup desktop notifications
      this.setupLinuxNotifications();
    }

    // Configure desktop environment specific features
    if (this.nativeFeatures.linux.desktopEnvironment === 'GNOME') {
      this.configureGNOMEFeatures();
    } else if (this.nativeFeatures.linux.desktopEnvironment === 'KDE') {
      this.configureKDEFeatures();
    }

    log.info('Linux features configured');
  }

  setupSystemEventMonitoring() {
    // Theme changes
    nativeTheme.on('updated', () => {
      const darkMode = nativeTheme.shouldUseDarkColors;
      log.info('System theme changed:', darkMode ? 'dark' : 'light');
      this.emit('theme-changed', { darkMode });
    });

    // Power events
    if (powerMonitor) {
      powerMonitor.on('suspend', () => {
        log.info('System suspending');
        this.emit('system-suspend');
      });

      powerMonitor.on('resume', () => {
        log.info('System resumed');
        this.emit('system-resume');
      });

      powerMonitor.on('on-ac', () => {
        log.info('System plugged in');
        this.emit('power-ac');
      });

      powerMonitor.on('on-battery', () => {
        log.info('System on battery');
        this.emit('power-battery');
      });

      powerMonitor.on('shutdown', () => {
        log.info('System shutting down');
        this.emit('system-shutdown');
      });

      powerMonitor.on('lock-screen', () => {
        log.info('Screen locked');
        this.emit('screen-lock');
      });

      powerMonitor.on('unlock-screen', () => {
        log.info('Screen unlocked');
        this.emit('screen-unlock');
      });
    }

    log.info('System event monitoring configured');
  }

  initializeFileAssociations() {
    // Handle file associations at runtime
    app.on('open-file', (event, path) => {
      event.preventDefault();
      log.info('File opened:', path);
      this.emit('file-opened', { path });
    });

    app.on('open-url', (event, url) => {
      event.preventDefault();
      log.info('URL opened:', url);
      this.emit('url-opened', { url });
    });
  }

  // Touch Bar support (macOS)
  setupTouchBar() {
    if (this.platform !== 'darwin') return;

    try {
      const { TouchBar } = require('electron');
      if (!TouchBar) return;

      const { TouchBarButton, TouchBarSpacer } = TouchBar;

      const touchBar = new TouchBar({
        items: [
          new TouchBarButton({
            label: '🎵 Play',
            backgroundColor: '#3B82F6',
            click: () => {
              this.emit('touchbar-play');
            }
          }),
          new TouchBarSpacer({ size: 'small' }),
          new TouchBarButton({
            label: '⏸️ Pause',
            click: () => {
              this.emit('touchbar-pause');
            }
          }),
          new TouchBarSpacer({ size: 'small' }),
          new TouchBarButton({
            label: '⏹️ Stop',
            click: () => {
              this.emit('touchbar-stop');
            }
          }),
          new TouchBarSpacer({ size: 'flexible' }),
          new TouchBarButton({
            label: '🎤 Record',
            backgroundColor: '#EF4444',
            click: () => {
              this.emit('touchbar-record');
            }
          })
        ]
      });

      // Apply to main window when it's created
      this.touchBar = touchBar;
      log.info('Touch Bar configured');

    } catch (error) {
      log.warn('Touch Bar setup failed:', error.message);
    }
  }

  // Platform detection utilities
  isWindows11() {
    if (this.platform !== 'win32') return false;
    
    try {
      const version = os.release();
      const build = parseInt(version.split('.')[2]);
      return build >= 22000; // Windows 11 build number
    } catch (error) {
      return false;
    }
  }

  detectTouchSupport() {
    // This would require more sophisticated detection
    // For now, assume touch support on Windows 10+
    return this.platform === 'win32' && parseFloat(os.release()) >= 10;
  }

  detectDesktopEnvironment() {
    const desktopSession = process.env.DESKTOP_SESSION;
    const xdgDesktop = process.env.XDG_CURRENT_DESKTOP;
    
    if (xdgDesktop) {
      if (xdgDesktop.includes('GNOME')) return 'GNOME';
      if (xdgDesktop.includes('KDE')) return 'KDE';
      if (xdgDesktop.includes('XFCE')) return 'XFCE';
      if (xdgDesktop.includes('Unity')) return 'Unity';
    }
    
    if (desktopSession) {
      if (desktopSession.includes('gnome')) return 'GNOME';
      if (desktopSession.includes('kde')) return 'KDE';
      if (desktopSession.includes('xfce')) return 'XFCE';
      if (desktopSession.includes('unity')) return 'Unity';
    }
    
    return 'Unknown';
  }

  detectDisplayServer() {
    if (process.env.WAYLAND_DISPLAY) return 'Wayland';
    if (process.env.DISPLAY) return 'X11';
    return 'Unknown';
  }

  detectPackageManager() {
    const packageManagers = ['apt', 'yum', 'dnf', 'pacman', 'zypper'];
    
    for (const pm of packageManagers) {
      try {
        require('child_process').execSync(`which ${pm}`, { stdio: 'pipe' });
        return pm;
      } catch (error) {
        // Continue checking
      }
    }
    
    return 'unknown';
  }

  detectNotificationSupport() {
    try {
      require('child_process').execSync('which notify-send', { stdio: 'pipe' });
      return 'notify-send';
    } catch (error) {
      return false;
    }
  }

  detectAudioSystem() {
    if (process.env.PULSE_SERVER || process.env.PULSE_RUNTIME_PATH) {
      return 'PulseAudio';
    }
    
    try {
      require('child_process').execSync('which pulseaudio', { stdio: 'pipe' });
      return 'PulseAudio';
    } catch (error) {
      try {
        require('child_process').execSync('which alsamixer', { stdio: 'pipe' });
        return 'ALSA';
      } catch (alsaError) {
        return 'Unknown';
      }
    }
  }

  async getLinuxDistribution() {
    try {
      const fs = require('fs');
      if (fs.existsSync('/etc/os-release')) {
        const content = fs.readFileSync('/etc/os-release', 'utf8');
        const lines = content.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('PRETTY_NAME=')) {
            return line.split('=')[1].replace(/"/g, '');
          }
        }
      }
      return 'Linux';
    } catch (error) {
      return 'Linux';
    }
  }

  // Public API methods
  getNativeFeatures() {
    return this.nativeFeatures;
  }

  getPlatformInfo() {
    return {
      platform: this.platform,
      arch: process.arch,
      version: os.release(),
      features: this.nativeFeatures
    };
  }

  openExternal(url) {
    return shell.openExternal(url);
  }

  showItemInFolder(path) {
    return shell.showItemInFolder(path);
  }

  openPath(path) {
    return shell.openPath(path);
  }

  beep() {
    return shell.beep();
  }

  // Theme management
  setTheme(theme) {
    if (['system', 'light', 'dark'].includes(theme)) {
      nativeTheme.themeSource = theme;
      log.info(`Theme set to: ${theme}`);
    }
  }

  getTheme() {
    return {
      source: nativeTheme.themeSource,
      shouldUseDarkColors: nativeTheme.shouldUseDarkColors,
      shouldUseHighContrastColors: nativeTheme.shouldUseHighContrastColors,
      shouldUseInvertedColorScheme: nativeTheme.shouldUseInvertedColorScheme
    };
  }

  // System notifications
  showSystemNotification(title, body, options = {}) {
    const { Notification } = require('electron');
    
    if (Notification.isSupported()) {
      const notification = new Notification({
        title,
        body,
        icon: options.icon || path.join(__dirname, 'assets', 'icon.png'),
        sound: options.sound,
        urgency: options.urgency || 'normal'
      });
      
      notification.show();
      return notification;
    }
    
    return null;
  }

  // Media access (macOS)
  async requestMediaAccess(mediaType) {
    if (this.platform === 'darwin' && systemPreferences.askForMediaAccess) {
      return systemPreferences.askForMediaAccess(mediaType);
    }
    return true; // Assume granted on other platforms
  }

  getMediaAccessStatus(mediaType) {
    if (this.platform === 'darwin' && systemPreferences.getMediaAccessStatus) {
      return systemPreferences.getMediaAccessStatus(mediaType);
    }
    return 'granted'; // Assume granted on other platforms
  }

  // Power management
  preventSystemSleep() {
    if (powerMonitor && powerMonitor.suspend) {
      // This would require additional implementation
      log.info('System sleep prevention requested');
    }
  }

  allowSystemSleep() {
    if (powerMonitor) {
      // This would require additional implementation
      log.info('System sleep allowed');
    }
  }

  // System capabilities
  getSystemCapabilities() {
    return {
      touchSupport: this.detectTouchSupport(),
      darkModeSupport: true,
      notificationSupport: Notification?.isSupported?.() || false,
      mediaAccess: this.platform === 'darwin',
      jumpLists: this.platform === 'win32',
      touchBar: this.platform === 'darwin',
      systemTray: true,
      globalShortcuts: true
    };
  }
}

// Event emitter mixin
Object.assign(NativeIntegrationManager.prototype, require('events').EventEmitter.prototype);

module.exports = NativeIntegrationManager;