/**
 * Ainflue Desktop - Electron Builder Configuration
 * 
 * Professional build configuration for multi-platform distribution
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const path = require('path');
const fs = require('fs');

class ElectronBuilderConfig {
  constructor() {
    this.baseConfig = {
      appId: 'com.ainflue.desktop',
      productName: 'Ainflue Studio',
      copyright: '© 2025 Fahed Mlaiel. All rights reserved.',
      
      directories: {
        output: 'dist',
        buildResources: 'build'
      },
      
      files: [
        'main.js',
        'index.js',
        'preload.js',
        'desktop_configuration_manager.js',
        'application_lifecycle_manager.js',
        'desktop_security_manager.js',
        'auto_updater_manager.js',
        'platform_detector.js',
        'native_integration_manager.js',
        'file_system_manager.js',
        'notification_manager.js',
        'keyboard_shortcuts_manager.js',
        'renderer/**/*',
        'src/**/*',
        'components/**/*',
        'services/**/*',
        'security/**/*',
        'scripts/**/*',
        'assets/**/*',
        'node_modules/**/*',
        '!node_modules/electron-builder/**/*',
        '!node_modules/app-builder-lib/**/*',
        '!node_modules/.cache/**/*',
        '!**/node_modules/.cache/**/*'
      ],
      
      extraMetadata: {
        main: 'main.js',
        author: 'Fahed Mlaiel <mlaiel@live.de>',
        homepage: 'https://ainflue.com',
        license: 'PROPRIETARY'
      },
      
      publish: {
        provider: 'github',
        owner: 'Mlaiel',
        repo: 'Ainflue',
        private: false
      },
      
      // Code signing configuration
      forceCodeSigning: false, // Set to true for production
      
      // Compression
      compression: 'maximum',
      
      // Package dependencies
      includeSubNodeModules: true,
      
      // Remove dev dependencies
      removePackageScripts: true,
      removePackageKeywords: true
    };
  }

  // macOS Configuration
  getMacOSConfig() {
    return {
      ...this.baseConfig,
      
      mac: {
        category: 'public.app-category.productivity',
        icon: 'assets/icons/icon.icns',
        hardenedRuntime: true,
        gatekeeperAssess: false,
        notarize: false, // Set to true for App Store distribution
        
        entitlements: 'build/entitlements.mac.plist',
        entitlementsInherit: 'build/entitlements.mac.plist',
        
        // Code signing
        identity: null, // Will be set from environment or keychain
        
        // Bundle information
        bundleVersion: '1.0.0',
        bundleShortVersion: '1.0.0',
        
        // macOS version requirements
        minimumSystemVersion: '10.14.0',
        
        // Target architectures
        target: [
          {
            target: 'dmg',
            arch: ['x64', 'arm64']
          },
          {
            target: 'zip',
            arch: ['x64', 'arm64']
          },
          {
            target: 'pkg',
            arch: ['x64', 'arm64']
          }
        ],
        
        // File associations
        fileAssociations: [
          {
            ext: 'ainproj',
            name: 'Ainflue Project',
            description: 'Ainflue Studio Project File',
            icon: 'assets/icons/project.icns',
            role: 'Editor'
          }
        ],
        
        // URL protocol handlers
        protocols: [
          {
            name: 'ainflue',
            schemes: ['ainflue'],
            role: 'Editor'
          }
        ]
      },
      
      dmg: {
        artifactName: '${productName}-${version}-mac.${ext}',
        title: '${productName} ${version}',
        icon: 'assets/icons/volume.icns',
        background: 'assets/dmg/background.png',
        window: {
          width: 540,
          height: 380
        },
        contents: [
          {
            x: 140,
            y: 250,
            type: 'file'
          },
          {
            x: 400,
            y: 250,
            type: 'link',
            path: '/Applications'
          }
        ],
        sign: false, // Set to true for signed builds
        internetEnabled: true
      },
      
      pkg: {
        allowAnywhere: false,
        allowCurrentUserHome: false,
        allowRootDirectory: false,
        identity: null,
        installLocation: '/Applications',
        mustClose: [
          'com.ainflue.desktop'
        ]
      }
    };
  }

  // Windows Configuration  
  getWindowsConfig() {
    return {
      ...this.baseConfig,
      
      win: {
        target: [
          {
            target: 'nsis',
            arch: ['x64', 'ia32']
          },
          {
            target: 'portable',
            arch: ['x64', 'ia32']
          },
          {
            target: 'zip',
            arch: ['x64', 'ia32']
          },
          {
            target: 'msi',
            arch: ['x64']
          }
        ],
        
        icon: 'assets/icons/icon.ico',
        
        // Windows specific settings
        requestedExecutionLevel: 'asInvoker',
        publisherName: 'Fahed Mlaiel',
        verifyUpdateCodeSignature: false,
        
        // File associations
        fileAssociations: [
          {
            ext: 'ainproj',
            name: 'Ainflue Project',
            description: 'Ainflue Studio Project File',
            icon: 'assets/icons/project.ico',
            perMachine: false
          }
        ],
        
        // URL protocol handlers
        protocols: [
          {
            name: 'ainflue',
            schemes: ['ainflue']
          }
        ],
        
        // Sign tool configuration (for code signing)
        signtoolOptions: {
          subject: 'Fahed Mlaiel',
          algorithm: 'sha256'
        }
      },
      
      nsis: {
        oneClick: false,
        allowToChangeInstallationDirectory: true,
        allowElevation: true,
        createDesktopShortcut: true,
        createStartMenuShortcut: true,
        shortcutName: 'Ainflue Studio',
        runAfterFinish: true,
        artifactName: '${productName}-${version}-Setup.${ext}',
        deleteAppDataOnUninstall: false,
        
        // Installer customization
        installerIcon: 'assets/icons/installer.ico',
        uninstallerIcon: 'assets/icons/uninstaller.ico',
        installerHeaderIcon: 'assets/icons/header.ico',
        installerSidebar: 'assets/nsis/sidebar.bmp',
        uninstallerSidebar: 'assets/nsis/sidebar.bmp',
        
        // License
        license: 'LICENSE',
        
        // Languages
        language: '1033', // English
        
        // Include
        include: 'build/installer.nsh',
        
        // Custom script
        script: 'build/installer.nsi'
      },
      
      portable: {
        artifactName: '${productName}-${version}-Portable.${ext}',
        requestExecutionLevel: 'user'
      },
      
      msi: {
        artifactName: '${productName}-${version}.${ext}',
        warningsAsErrors: false,
        upgradeCode: '{12345678-1234-1234-1234-123456789ABC}'
      }
    };
  }

  // Linux Configuration
  getLinuxConfig() {
    return {
      ...this.baseConfig,
      
      linux: {
        target: [
          {
            target: 'AppImage',
            arch: ['x64']
          },
          {
            target: 'deb',
            arch: ['x64']
          },
          {
            target: 'rpm',
            arch: ['x64']
          },
          {
            target: 'tar.gz',
            arch: ['x64']
          },
          {
            target: 'snap',
            arch: ['x64']
          }
        ],
        
        icon: 'assets/icons/icon.png',
        category: 'AudioVideo',
        synopsis: 'Professional AI Content Creation Studio',
        description: 'Advanced AI-powered content creation platform with professional editing, protection, and monetization features for modern creators.',
        
        desktop: {
          Name: 'Ainflue Studio',
          Comment: 'Professional AI Content Creation Studio',
          GenericName: 'Content Creation Studio',
          Keywords: 'audio;video;editing;ai;content;creation;studio',
          StartupWMClass: 'Ainflue Studio',
          MimeType: 'application/x-ainflue-project',
          Categories: 'AudioVideo;Audio;Video;Player;Recorder;AudioVideoEditing'
        },
        
        // File associations
        fileAssociations: [
          {
            ext: 'ainproj',
            name: 'Ainflue Project',
            description: 'Ainflue Studio Project File',
            mimeType: 'application/x-ainflue-project'
          }
        ]
      },
      
      appImage: {
        artifactName: '${productName}-${version}.${ext}',
        include: [
          'assets/appimage/AppRun',
          'assets/appimage/ainflue.desktop',
          'assets/appimage/icon.png'
        ]
      },
      
      deb: {
        artifactName: '${productName}_${version}_${arch}.${ext}',
        packageName: 'ainflue-studio',
        
        // Debian package information
        maintainer: 'Fahed Mlaiel <mlaiel@live.de>',
        vendor: 'Fahed Mlaiel',
        priority: 'optional',
        
        // Dependencies
        depends: [
          'gconf2',
          'gconf-service',
          'libxss1',
          'libappindicator1',
          'libasound2',
          'libxtst6',
          'xdg-utils'
        ],
        
        // Recommends
        recommends: [
          'pulseaudio',
          'ffmpeg'
        ],
        
        // Package control
        compression: 'xz',
        
        // Post install script
        afterInstall: 'build/deb-postinst.sh',
        afterRemove: 'build/deb-postrm.sh'
      },
      
      rpm: {
        artifactName: '${productName}-${version}.${arch}.${ext}',
        packageName: 'ainflue-studio',
        
        // RPM package information
        vendor: 'Fahed Mlaiel',
        license: 'Proprietary',
        group: 'Applications/Multimedia',
        
        // Dependencies
        depends: [
          'gtk3',
          'libXScrnSaver',
          'alsa-lib'
        ],
        
        // Scripts
        afterInstall: 'build/rpm-postinst.sh',
        afterRemove: 'build/rpm-postrm.sh'
      },
      
      snap: {
        artifactName: '${productName}_${version}_${arch}.${ext}',
        
        // Snap configuration
        grade: 'stable',
        confinement: 'strict',
        base: 'core20',
        
        // Snap metadata
        summary: 'Professional AI Content Creation Studio',
        description: 'Advanced AI-powered content creation platform with professional editing, protection, and monetization features for modern creators.',
        
        // Plugs (permissions)
        plugs: [
          'desktop',
          'desktop-legacy',
          'home',
          'x11',
          'unity7',
          'browser-support',
          'network',
          'gsettings',
          'audio-playback',
          'audio-record',
          'camera',
          'removable-media'
        ],
        
        // Environment
        environment: {
          'TMPDIR': '$XDG_RUNTIME_DIR'
        }
      }
    };
  }

  // Development Configuration
  getDevelopmentConfig() {
    return {
      ...this.baseConfig,
      
      // Development specific settings
      compression: 'store',
      removePackageScripts: false,
      
      // Include source maps
      files: [
        ...this.baseConfig.files,
        '**/*.map'
      ],
      
      // Skip signing in development
      forceCodeSigning: false,
      
      mac: {
        identity: null,
        notarize: false
      },
      
      win: {
        certificateFile: null,
        certificatePassword: null
      }
    };
  }

  // Production Configuration
  getProductionConfig() {
    const config = this.getDefaultConfig();
    
    return {
      ...config,
      
      // Production optimizations
      compression: 'maximum',
      removePackageScripts: true,
      removePackageKeywords: true,
      
      // Enable signing
      forceCodeSigning: true,
      
      // Exclude development files
      files: [
        ...this.baseConfig.files,
        '!**/*.map',
        '!**/test/**/*',
        '!**/tests/**/*',
        '!**/*.test.js',
        '!**/*.spec.js'
      ]
    };
  }

  // Get configuration based on platform
  getConfigForPlatform(platform) {
    switch (platform) {
      case 'mac':
      case 'darwin':
        return this.getMacOSConfig();
      case 'win':
      case 'win32':
        return this.getWindowsConfig();
      case 'linux':
        return this.getLinuxConfig();
      default:
        return this.getDefaultConfig();
    }
  }

  // Get configuration based on environment
  getConfigForEnvironment(environment) {
    switch (environment) {
      case 'development':
        return this.getDevelopmentConfig();
      case 'production':
        return this.getProductionConfig();
      default:
        return this.getDefaultConfig();
    }
  }

  // Default configuration (all platforms)
  getDefaultConfig() {
    return {
      ...this.getMacOSConfig(),
      ...this.getWindowsConfig(),
      ...this.getLinuxConfig()
    };
  }

  // Generate build scripts
  generateBuildScripts() {
    const scripts = {
      // Platform-specific builds
      'build:mac': 'electron-builder --mac',
      'build:win': 'electron-builder --win',
      'build:linux': 'electron-builder --linux',
      
      // Architecture-specific builds
      'build:mac-intel': 'electron-builder --mac --x64',
      'build:mac-apple': 'electron-builder --mac --arm64',
      'build:win-64': 'electron-builder --win --x64',
      'build:win-32': 'electron-builder --win --ia32',
      'build:linux-64': 'electron-builder --linux --x64',
      
      // Distribution-specific builds
      'build:dmg': 'electron-builder --mac dmg',
      'build:pkg': 'electron-builder --mac pkg',
      'build:nsis': 'electron-builder --win nsis',
      'build:portable': 'electron-builder --win portable',
      'build:msi': 'electron-builder --win msi',
      'build:appimage': 'electron-builder --linux AppImage',
      'build:deb': 'electron-builder --linux deb',
      'build:rpm': 'electron-builder --linux rpm',
      'build:snap': 'electron-builder --linux snap',
      
      // Multi-platform builds
      'build:all': 'electron-builder --mac --win --linux',
      'build:all-64': 'electron-builder --mac --win --linux --x64',
      
      // Development builds
      'build:dev': 'electron-builder --dir',
      'build:dev-mac': 'electron-builder --mac --dir',
      'build:dev-win': 'electron-builder --win --dir',
      'build:dev-linux': 'electron-builder --linux --dir',
      
      // Publish builds
      'publish:mac': 'electron-builder --mac --publish=always',
      'publish:win': 'electron-builder --win --publish=always',
      'publish:linux': 'electron-builder --linux --publish=always',
      'publish:all': 'electron-builder --mac --win --linux --publish=always'
    };
    
    return scripts;
  }

  // Generate configuration file
  generateConfigFile(platform = 'all', environment = 'production') {
    let config;
    
    if (platform === 'all') {
      config = this.getDefaultConfig();
    } else {
      config = this.getConfigForPlatform(platform);
    }
    
    if (environment) {
      const envConfig = this.getConfigForEnvironment(environment);
      config = { ...config, ...envConfig };
    }
    
    return config;
  }

  // Save configuration to file
  saveConfigToFile(config, filename = 'electron-builder.json') {
    const configJson = JSON.stringify(config, null, 2);
    fs.writeFileSync(filename, configJson);
    return filename;
  }

  // Load configuration from file
  loadConfigFromFile(filename = 'electron-builder.json') {
    if (fs.existsSync(filename)) {
      const configJson = fs.readFileSync(filename, 'utf8');
      return JSON.parse(configJson);
    }
    return null;
  }

  // Validate configuration
  validateConfig(config) {
    const required = ['appId', 'productName', 'directories'];
    const missing = required.filter(key => !config[key]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required configuration keys: ${missing.join(', ')}`);
    }
    
    return true;
  }

  // Create build directories
  createBuildDirectories() {
    const dirs = ['build', 'dist', 'assets/icons', 'assets/dmg', 'assets/nsis', 'assets/appimage'];
    
    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  // Get build status
  getBuildStatus() {
    return {
      hasIcons: fs.existsSync('assets/icons/icon.ico') && fs.existsSync('assets/icons/icon.icns') && fs.existsSync('assets/icons/icon.png'),
      hasLicense: fs.existsSync('LICENSE'),
      hasBuildDir: fs.existsSync('build'),
      hasDistDir: fs.existsSync('dist'),
      configValid: true // Would implement actual validation
    };
  }
}

module.exports = ElectronBuilderConfig;