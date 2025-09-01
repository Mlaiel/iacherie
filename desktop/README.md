# 🖥️ Ainflue Desktop - Electron Application

## Overview

The Ainflue Desktop application is a professional AI-powered content creation studio built with Electron. It provides advanced editing capabilities, multi-monitor support, and comprehensive system integration features.

## 🚀 Features

### Core Capabilities
- **Advanced AI Content Processing**: Intelligent audio/video analysis and enhancement
- **Multi-Monitor Support**: Professional studio workflow across multiple displays
- **Platform Detection**: Adaptive UI and features based on operating system
- **Secure File Operations**: Protected file system access with proper permissions
- **Professional Menu System**: Native application menus for all platforms
- **Auto-Updates**: Seamless application updates via electron-updater

### Platform-Specific Features

#### macOS
- **Native Title Bar**: Integrated with macOS design guidelines
- **Vibrancy Effects**: Modern translucent window effects
- **Code Signing Ready**: Proper entitlements for App Store distribution
- **DMG Installer**: Professional disk image packaging

#### Windows
- **NSIS Installer**: Full-featured Windows installer
- **Portable Version**: No-installation portable executable
- **Auto-Start Integration**: Windows startup integration
- **Native Frame**: Windows-style window decorations

#### Linux
- **AppImage**: Universal Linux application format
- **DEB Package**: Debian/Ubuntu package installation
- **RPM Package**: Red Hat/SUSE package installation
- **TAR.GZ Archive**: Manual installation option

## 📦 Build Configuration

### Dependencies
- **Runtime**: Production dependencies for the running application
- **Development**: Build tools and development utilities properly separated

### Build Targets
```bash
# Development
npm run dev              # Start in development mode
npm start               # Start in production mode

# Packaging
npm run pack            # Create unpacked directory (fastest)
npm run build           # Build for current platform
npm run build:win       # Build Windows installers
npm run build:mac       # Build macOS packages
npm run build:linux     # Build Linux packages
```

### Output Formats

#### Windows
- **NSIS Installer** (`Setup.exe`): Full installer with registry integration
- **Portable** (`Portable.exe`): Self-contained executable
- **ZIP Archive**: Compressed archive for manual extraction

#### macOS
- **DMG Image**: Drag-and-drop installer with custom background
- **ZIP Archive**: Compressed application bundle

#### Linux
- **AppImage**: Universal Linux executable
- **DEB Package**: Debian/Ubuntu installation package
- **RPM Package**: Red Hat/SUSE installation package
- **TAR.GZ Archive**: Manual installation archive

## 🔧 Configuration

### Environment Variables
- `NODE_ENV`: Development/production environment
- `DEBUG`: Enable debug logging

### Build Customization
The build configuration in `package.json` supports:
- Custom app icons for each platform
- Code signing certificates
- Auto-update server configuration
- Platform-specific installer options

## 🛡️ Security

### Code Signing
- **macOS**: Ready for Apple Developer Program signing
- **Windows**: Prepared for Authenticode signing
- **Entitlements**: Proper permission declarations for all features

### Sandboxing
- **Context Isolation**: Renderer processes are properly isolated
- **Preload Scripts**: Secure IPC communication bridge
- **No Node Integration**: Renderer processes don't have direct Node.js access

## 🔍 Validation

Run the validation script to ensure everything is properly configured:

```bash
./scripts/validate-build.sh
```

This script verifies:
- ✅ Package.json configuration
- ✅ Asset files presence
- ✅ Build system functionality
- ✅ Platform-specific configurations

## 📁 Project Structure

```
desktop/
├── main.js                 # Main Electron process
├── preload.js              # Secure IPC bridge
├── package.json            # Dependencies and build config
├── assets/                 # Application icons and resources
│   ├── icon.png            # Linux icon
│   ├── icon.ico            # Windows icon
│   ├── icon.icns           # macOS icon
│   └── dmg-background.png  # macOS DMG background
├── build/                  # Build configuration
│   └── entitlements.mac.plist  # macOS permissions
├── renderer/               # UI and frontend code
│   └── index.html          # Main application window
└── scripts/                # Utility scripts
    └── validate-build.sh   # Build validation
```

## 🚀 Deployment

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Platform-specific build tools (Xcode for macOS, etc.)

### Quick Start
```bash
# Install dependencies
npm install

# Validate setup
./scripts/validate-build.sh

# Development
npm run dev

# Production build
npm run build:linux    # or build:win, build:mac
```

### Distribution
1. **Code Signing**: Configure certificates for each platform
2. **Build**: Run platform-specific build commands
3. **Test**: Verify installers on target platforms
4. **Deploy**: Distribute via website, app stores, or package managers

## 📊 Build Results

Recent validation shows successful builds:
- **Linux AppImage**: ~137MB (Universal executable)
- **Linux DEB**: ~95MB (Debian package)
- **Linux TAR.GZ**: ~130MB (Archive)

All builds include:
- Complete Electron runtime
- Application code and assets
- Native dependencies (Sharp, FFmpeg)
- Proper metadata and desktop integration

## 🛠️ Development

### Adding Features
1. Update `main.js` for main process features
2. Modify `preload.js` for secure IPC
3. Enhance `renderer/` for UI components
4. Test across all target platforms

### Platform Detection
The application includes comprehensive platform detection:
```javascript
// Available in main process
this.platform.isMac     // macOS detection
this.platform.isWindows // Windows detection  
this.platform.isLinux   // Linux detection
this.platform.arch      // CPU architecture

// Available in renderer via IPC
const platformInfo = await electronAPI.getPlatformInfo();
```

This enables adaptive UI and platform-specific functionality throughout the application.