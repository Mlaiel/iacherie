/**
 * Ainflue Desktop - Platform Detector
 * 
 * Cross-platform detection and optimization system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const os = require('os');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const log = require('electron-log');

class PlatformDetector {
  constructor() {
    this.platformInfo = null;
    this.systemCapabilities = null;
    this.hardwareInfo = null;
    this.isInitialized = false;
    
    log.info('Platform Detector initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Platform Detector...');
      
      // Detect basic platform information
      await this.detectPlatformInfo();
      
      // Detect system capabilities
      await this.detectSystemCapabilities();
      
      // Detect hardware information
      await this.detectHardwareInfo();
      
      // Apply platform-specific optimizations
      this.applyPlatformOptimizations();
      
      this.isInitialized = true;
      log.info('✅ Platform Detector initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Platform Detector:', error);
      throw error;
    }
  }

  async detectPlatformInfo() {
    this.platformInfo = {
      // Basic platform information
      platform: process.platform,
      arch: process.arch,
      release: os.release(),
      type: os.type(),
      version: os.version ? os.version() : 'Unknown',
      
      // Node.js and Electron versions
      nodeVersion: process.version,
      electronVersion: process.versions.electron,
      chromeVersion: process.versions.chrome,
      v8Version: process.versions.v8,
      
      // Environment
      isProduction: process.env.NODE_ENV === 'production',
      isDevelopment: process.env.NODE_ENV === 'development',
      
      // Specific platform flags
      isMacOS: process.platform === 'darwin',
      isWindows: process.platform === 'win32',
      isLinux: process.platform === 'linux',
      
      // Architecture flags
      is64Bit: process.arch === 'x64',
      isARM: process.arch === 'arm64' || process.arch === 'arm',
      isIntel: process.arch === 'x64' || process.arch === 'ia32',
      
      // System paths
      homeDir: os.homedir(),
      tmpDir: os.tmpdir(),
      currentWorkingDir: process.cwd(),
      
      // Process information
      pid: process.pid,
      execPath: process.execPath,
      argv: process.argv
    };

    // Detect specific macOS version
    if (this.platformInfo.isMacOS) {
      await this.detectMacOSVersion();
    }
    
    // Detect specific Windows version
    if (this.platformInfo.isWindows) {
      await this.detectWindowsVersion();
    }
    
    // Detect specific Linux distribution
    if (this.platformInfo.isLinux) {
      await this.detectLinuxDistribution();
    }

    log.info('Platform info detected:', {
      platform: this.platformInfo.platform,
      arch: this.platformInfo.arch,
      release: this.platformInfo.release,
      nodeVersion: this.platformInfo.nodeVersion,
      electronVersion: this.platformInfo.electronVersion
    });
  }

  async detectMacOSVersion() {
    try {
      const versionInfo = await this.executeCommand('sw_vers');
      const lines = versionInfo.split('\n');
      
      const versionData = {};
      lines.forEach(line => {
        const [key, ...valueParts] = line.split(':');
        if (key && valueParts.length > 0) {
          const cleanKey = key.trim().toLowerCase().replace(' ', '');
          versionData[cleanKey] = valueParts.join(':').trim();
        }
      });
      
      this.platformInfo.macOS = {
        productName: versionData.productname || 'macOS',
        productVersion: versionData.productversion || 'Unknown',
        buildVersion: versionData.buildversion || 'Unknown'
      };
      
      // Detect macOS version features
      const version = versionData.productversion;
      if (version) {
        const majorVersion = parseInt(version.split('.')[0]);
        this.platformInfo.macOS.features = {
          supportsNotarization: majorVersion >= 10,
          supportsHardwareAcceleration: true,
          supportsDarkMode: majorVersion >= 10,
          supportsVibrancy: true,
          supportsNativeFullscreen: true
        };
      }
      
    } catch (error) {
      log.warn('Failed to detect macOS version details:', error.message);
      this.platformInfo.macOS = { productName: 'macOS', features: {} };
    }
  }

  async detectWindowsVersion() {
    try {
      const versionInfo = await this.executeCommand('ver');
      this.platformInfo.windows = {
        version: versionInfo.trim(),
        features: {
          supportsWindowsStore: true,
          supportsNotifications: true,
          supportsHardwareAcceleration: true,
          supportsJumpLists: true,
          supportsThumbnailToolbar: true
        }
      };
      
      // Try to get more detailed Windows info
      try {
        const systemInfo = await this.executeCommand('systeminfo | findstr /C:"OS Name" /C:"OS Version"');
        this.platformInfo.windows.systemInfo = systemInfo;
      } catch (sysError) {
        log.debug('Could not get detailed Windows system info');
      }
      
    } catch (error) {
      log.warn('Failed to detect Windows version details:', error.message);
      this.platformInfo.windows = { version: 'Windows', features: {} };
    }
  }

  async detectLinuxDistribution() {
    try {
      let distroInfo = {};
      
      // Try to read /etc/os-release
      if (fs.existsSync('/etc/os-release')) {
        const osReleaseContent = fs.readFileSync('/etc/os-release', 'utf8');
        const lines = osReleaseContent.split('\n');
        
        lines.forEach(line => {
          const [key, value] = line.split('=');
          if (key && value) {
            distroInfo[key.toLowerCase()] = value.replace(/"/g, '');
          }
        });
      }
      
      // Try lsb_release as fallback
      if (!distroInfo.name) {
        try {
          const lsbInfo = await this.executeCommand('lsb_release -a 2>/dev/null');
          // Parse lsb_release output
          const lines = lsbInfo.split('\n');
          lines.forEach(line => {
            if (line.includes('Description:')) {
              distroInfo.name = line.split(':')[1].trim();
            }
          });
        } catch (lsbError) {
          log.debug('lsb_release not available');
        }
      }
      
      this.platformInfo.linux = {
        distribution: distroInfo.name || distroInfo.pretty_name || 'Linux',
        version: distroInfo.version || 'Unknown',
        id: distroInfo.id || 'linux',
        features: {
          supportsNotifications: this.detectLinuxNotificationSupport(),
          supportsHardwareAcceleration: true,
          supportsSystemTray: true,
          supportsGlobalShortcuts: true,
          packageManager: this.detectPackageManager()
        }
      };
      
    } catch (error) {
      log.warn('Failed to detect Linux distribution details:', error.message);
      this.platformInfo.linux = { distribution: 'Linux', features: {} };
    }
  }

  detectLinuxNotificationSupport() {
    // Check for common notification systems
    const notificationSystems = ['notify-send', 'dunst', 'notification-daemon'];
    
    for (const system of notificationSystems) {
      try {
        require('child_process').execSync(`which ${system}`, { stdio: 'pipe' });
        return system;
      } catch (error) {
        // System not found, continue checking
      }
    }
    
    return false;
  }

  detectPackageManager() {
    const packageManagers = [
      { name: 'apt', command: 'apt' },
      { name: 'yum', command: 'yum' },
      { name: 'dnf', command: 'dnf' },
      { name: 'pacman', command: 'pacman' },
      { name: 'zypper', command: 'zypper' },
      { name: 'snap', command: 'snap' },
      { name: 'flatpak', command: 'flatpak' }
    ];
    
    for (const pm of packageManagers) {
      try {
        require('child_process').execSync(`which ${pm.command}`, { stdio: 'pipe' });
        return pm.name;
      } catch (error) {
        // Package manager not found, continue checking
      }
    }
    
    return 'unknown';
  }

  async detectSystemCapabilities() {
    this.systemCapabilities = {
      // Memory information
      memory: {
        total: os.totalmem(),
        free: os.freemem(),
        usage: os.totalmem() - os.freemem(),
        usagePercent: ((os.totalmem() - os.freemem()) / os.totalmem()) * 100
      },
      
      // CPU information
      cpu: {
        model: os.cpus()[0]?.model || 'Unknown',
        cores: os.cpus().length,
        speed: os.cpus()[0]?.speed || 0,
        architecture: process.arch
      },
      
      // Network interfaces
      network: os.networkInterfaces(),
      
      // System uptime
      uptime: os.uptime(),
      
      // Load average (Unix only)
      loadAverage: os.loadavg(),
      
      // User info
      userInfo: os.userInfo(),
      
      // System features
      features: {
        hasCamera: await this.detectCamera(),
        hasMicrophone: await this.detectMicrophone(),
        hasGPU: await this.detectGPU(),
        hasHardwareAcceleration: await this.detectHardwareAcceleration(),
        supportedAudioFormats: this.detectAudioSupport(),
        supportedVideoFormats: this.detectVideoSupport()
      }
    };

    log.info('System capabilities detected:', {
      memory: `${Math.round(this.systemCapabilities.memory.total / 1024 / 1024 / 1024)}GB total`,
      cpu: `${this.systemCapabilities.cpu.cores} cores`,
      uptime: `${Math.round(this.systemCapabilities.uptime / 3600)}h`
    });
  }

  async detectCamera() {
    try {
      // Check for camera devices
      const devices = await navigator.mediaDevices?.enumerateDevices?.() || [];
      return devices.some(device => device.kind === 'videoinput');
    } catch (error) {
      return false;
    }
  }

  async detectMicrophone() {
    try {
      // Check for microphone devices
      const devices = await navigator.mediaDevices?.enumerateDevices?.() || [];
      return devices.some(device => device.kind === 'audioinput');
    } catch (error) {
      return false;
    }
  }

  async detectGPU() {
    try {
      // Platform-specific GPU detection
      if (this.platformInfo.isWindows) {
        const wmic = await this.executeCommand('wmic path win32_VideoController get name');
        return wmic.includes('NVIDIA') || wmic.includes('AMD') || wmic.includes('Intel');
      } else if (this.platformInfo.isMacOS) {
        const system_profiler = await this.executeCommand('system_profiler SPDisplaysDataType');
        return system_profiler.includes('Chipset Model:');
      } else if (this.platformInfo.isLinux) {
        const lspci = await this.executeCommand('lspci | grep -i vga');
        return lspci.length > 0;
      }
      return false;
    } catch (error) {
      return false;
    }
  }

  async detectHardwareAcceleration() {
    // Check if hardware acceleration is available
    // This is a simplified check - in real implementation would test WebGL/GPU features
    return this.systemCapabilities?.features?.hasGPU || false;
  }

  detectAudioSupport() {
    // Detect supported audio formats
    const audio = new Audio();
    const formats = ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a'];
    const supported = [];
    
    formats.forEach(format => {
      const canPlay = audio.canPlayType(`audio/${format}`);
      if (canPlay === 'probably' || canPlay === 'maybe') {
        supported.push(format);
      }
    });
    
    return supported;
  }

  detectVideoSupport() {
    // Detect supported video formats
    const video = document.createElement('video');
    const formats = ['mp4', 'webm', 'ogg', 'avi', 'mov'];
    const supported = [];
    
    formats.forEach(format => {
      const canPlay = video.canPlayType(`video/${format}`);
      if (canPlay === 'probably' || canPlay === 'maybe') {
        supported.push(format);
      }
    });
    
    return supported;
  }

  async detectHardwareInfo() {
    this.hardwareInfo = {
      // Display information
      displays: await this.detectDisplays(),
      
      // Audio devices
      audioDevices: await this.detectAudioDevices(),
      
      // Storage information
      storage: await this.detectStorageInfo(),
      
      // USB devices
      usbDevices: await this.detectUSBDevices(),
      
      // Sensors (if available)
      sensors: await this.detectSensors()
    };

    log.info('Hardware info detected');
  }

  async detectDisplays() {
    try {
      const { screen } = require('electron');
      const displays = screen.getAllDisplays();
      
      return displays.map(display => ({
        id: display.id,
        bounds: display.bounds,
        workArea: display.workArea,
        size: display.size,
        workAreaSize: display.workAreaSize,
        scaleFactor: display.scaleFactor,
        rotation: display.rotation,
        touchSupport: display.touchSupport,
        primary: display === screen.getPrimaryDisplay()
      }));
    } catch (error) {
      log.warn('Failed to detect displays:', error.message);
      return [];
    }
  }

  async detectAudioDevices() {
    try {
      // This would require additional implementation for detailed audio device detection
      return {
        inputDevices: [],
        outputDevices: [],
        supported: this.systemCapabilities?.features?.supportedAudioFormats || []
      };
    } catch (error) {
      return { inputDevices: [], outputDevices: [], supported: [] };
    }
  }

  async detectStorageInfo() {
    try {
      if (this.platformInfo.isWindows) {
        const drives = await this.executeCommand('wmic logicaldisk get size,freespace,caption');
        return { drives: drives, totalSpace: 0, freeSpace: 0 };
      } else if (this.platformInfo.isLinux || this.platformInfo.isMacOS) {
        const df = await this.executeCommand('df -h');
        return { drives: df, totalSpace: 0, freeSpace: 0 };
      }
      return {};
    } catch (error) {
      return {};
    }
  }

  async detectUSBDevices() {
    try {
      if (this.platformInfo.isLinux) {
        const lsusb = await this.executeCommand('lsusb');
        return lsusb.split('\n').filter(line => line.trim());
      } else if (this.platformInfo.isMacOS) {
        const system_profiler = await this.executeCommand('system_profiler SPUSBDataType');
        return [system_profiler];
      }
      return [];
    } catch (error) {
      return [];
    }
  }

  async detectSensors() {
    // Detect available sensors (accelerometer, gyroscope, etc.)
    // This is a placeholder for future sensor detection
    return {
      accelerometer: false,
      gyroscope: false,
      magnetometer: false,
      temperature: false
    };
  }

  applyPlatformOptimizations() {
    const optimizations = this.getPlatformOptimizations();
    
    log.info('Applied platform optimizations:', Object.keys(optimizations));
    return optimizations;
  }

  getPlatformOptimizations() {
    const optimizations = {};
    
    if (this.platformInfo.isMacOS) {
      optimizations.macOS = {
        enableVibrancy: true,
        enableTitleBarInset: true,
        enableHardwareAcceleration: true,
        audioLatency: 'low',
        preferMetalRendering: true
      };
    }
    
    if (this.platformInfo.isWindows) {
      optimizations.windows = {
        enableJumpLists: true,
        enableThumbnailToolbar: true,
        enableToastNotifications: true,
        audioLatency: 'medium',
        preferDirectXRendering: true
      };
    }
    
    if (this.platformInfo.isLinux) {
      optimizations.linux = {
        enableSystemTray: true,
        preferPulseAudio: true,
        audioLatency: 'medium',
        preferOpenGLRendering: true
      };
    }
    
    return optimizations;
  }

  // Utility methods
  async executeCommand(command) {
    return new Promise((resolve, reject) => {
      exec(command, { timeout: 5000 }, (error, stdout, stderr) => {
        if (error) {
          reject(error);
        } else {
          resolve(stdout.trim());
        }
      });
    });
  }

  // Public API
  getPlatformInfo() {
    return this.platformInfo;
  }

  getSystemCapabilities() {
    return this.systemCapabilities;
  }

  getHardwareInfo() {
    return this.hardwareInfo;
  }

  getAllInfo() {
    return {
      platform: this.platformInfo,
      system: this.systemCapabilities,
      hardware: this.hardwareInfo,
      timestamp: new Date().toISOString()
    };
  }

  // Feature detection methods
  supportsFeature(feature) {
    const featureMap = {
      'hardware-acceleration': this.systemCapabilities?.features?.hasHardwareAcceleration,
      'camera': this.systemCapabilities?.features?.hasCamera,
      'microphone': this.systemCapabilities?.features?.hasMicrophone,
      'gpu': this.systemCapabilities?.features?.hasGPU,
      'notifications': this.platformInfo?.linux?.features?.supportsNotifications !== false,
      'system-tray': !this.platformInfo?.isLinux || this.platformInfo?.linux?.features?.supportsSystemTray,
      'global-shortcuts': true, // Most platforms support this
      'vibrancy': this.platformInfo?.isMacOS,
      'jump-lists': this.platformInfo?.isWindows,
      'dark-mode': true // Most modern platforms support this
    };
    
    return featureMap[feature] ?? false;
  }

  getRecommendedSettings() {
    const settings = {};
    
    // Memory-based recommendations
    const totalMemoryGB = this.systemCapabilities.memory.total / (1024 * 1024 * 1024);
    
    if (totalMemoryGB < 4) {
      settings.performance = 'low';
      settings.maxConcurrentTasks = 1;
      settings.enableHardwareAcceleration = false;
    } else if (totalMemoryGB < 8) {
      settings.performance = 'medium';
      settings.maxConcurrentTasks = 2;
      settings.enableHardwareAcceleration = true;
    } else {
      settings.performance = 'high';
      settings.maxConcurrentTasks = 4;
      settings.enableHardwareAcceleration = true;
    }
    
    // CPU-based recommendations
    if (this.systemCapabilities.cpu.cores >= 8) {
      settings.enableMultiThreading = true;
      settings.maxConcurrentTasks = Math.min(settings.maxConcurrentTasks * 2, 8);
    }
    
    // Platform-specific recommendations
    if (this.platformInfo.isMacOS) {
      settings.enableVibrancy = true;
      settings.audioFormat = 'aac';
    } else if (this.platformInfo.isWindows) {
      settings.enableToastNotifications = true;
      settings.audioFormat = 'mp3';
    } else if (this.platformInfo.isLinux) {
      settings.enableSystemTray = true;
      settings.audioFormat = 'ogg';
    }
    
    return settings;
  }

  // Monitoring methods
  startPerformanceMonitoring() {
    setInterval(() => {
      const currentMemory = {
        total: os.totalmem(),
        free: os.freemem(),
        usage: os.totalmem() - os.freemem()
      };
      
      this.systemCapabilities.memory = currentMemory;
      
      // Log performance warnings
      const usagePercent = (currentMemory.usage / currentMemory.total) * 100;
      if (usagePercent > 85) {
        log.warn(`High memory usage: ${usagePercent.toFixed(1)}%`);
      }
      
    }, 30000); // Check every 30 seconds
  }
}

module.exports = PlatformDetector;