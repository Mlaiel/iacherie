# Ainflue Desktop - Build & Deployment Guide

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This software and concept are the exclusive intellectual property of Fahed Mlaiel.  
Any unauthorized use, copying, distribution, or reverse engineering is strictly prohibited.  
Legal action will be taken against violators under German and international copyright law.  
Contact: mlaiel@live.de for licensing inquiries.

---

## Table of Contents

1. [Build System Overview](#build-system-overview)
2. [Prerequisites](#prerequisites)
3. [Build Configuration](#build-configuration)
4. [Development Builds](#development-builds)
5. [Production Builds](#production-builds)
6. [Platform-Specific Builds](#platform-specific-builds)
7. [Distribution](#distribution)
8. [Auto-Updates](#auto-updates)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Troubleshooting](#troubleshooting)

---

## Build System Overview

Ainflue Desktop uses **Electron Builder** for creating distributable packages across Windows, macOS, and Linux platforms. The build system supports:

- **Multi-platform builds** from any platform
- **Code signing** for security and trust
- **Auto-updates** with differential downloads
- **Custom installers** with branding
- **Portable applications** for easy deployment
- **Store distributions** (Microsoft Store, Mac App Store)

### Build Targets

| Platform | Formats | Architectures |
|----------|---------|---------------|
| Windows  | NSIS, Portable, MSI, AppX | x64, ia32, arm64 |
| macOS    | DMG, ZIP, PKG | x64, arm64 (Apple Silicon) |
| Linux    | AppImage, DEB, RPM, TAR.GZ | x64, arm64 |

---

## Prerequisites

### System Requirements

#### All Platforms
- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Git**: 2.30.0 or higher
- **Python**: 3.8+ (for native dependencies)

#### Windows Builds
```bash
# Install Windows Build Tools
npm install -g windows-build-tools

# Install Visual Studio Build Tools 2019 or later
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# For Windows Store (AppX) packages
# Windows 10 SDK (latest version)
```

#### macOS Builds
```bash
# Install Xcode Command Line Tools
xcode-select --install

# For Mac App Store builds
# Xcode 12.0 or later
# Valid Apple Developer Account

# For code signing
# Apple Developer certificates in Keychain
```

#### Linux Builds
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential libnss3-dev libatk-bridge2.0-dev libdrm2-dev libxss1-dev libgconf-2-4

# For AppImage builds
sudo apt-get install fuse

# For RPM builds on Debian/Ubuntu
sudo apt-get install rpm
```

### Code Signing Certificates

#### Windows (Required for production)
- **Authenticode Certificate** (.p12 or .pfx file)
- **Certificate password**
- **Timestamp server** (optional but recommended)

#### macOS (Required for distribution)
- **Developer ID Application Certificate**
- **Developer ID Installer Certificate** (for PKG)
- **Apple Account** for notarization

#### Linux
- **GPG key** for DEB/RPM signing (optional)

---

## Build Configuration

### Electron Builder Configuration

The build configuration is in `electron_builder_config.js`:

```javascript
/**
 * Electron Builder Configuration
 * Complete build settings for all platforms
 */

const config = {
  appId: "com.ainflue.desktop",
  productName: "Ainflue Studio",
  
  // Directories
  directories: {
    output: "dist",
    buildResources: "build"
  },
  
  // Files to include
  files: [
    "main.js",
    "preload.js",
    "renderer/**/*",
    "src/**/*",
    "services/**/*",
    "components/**/*",
    "ui_components/**/*",
    "security/**/*",
    "assets/**/*",
    "node_modules/**/*",
    "!node_modules/electron-builder/**/*",
    "!node_modules/app-builder-lib/**/*",
    "!**/*.{iml,o,hprof,orig,pyc,pyo,rbc,swp,csproj,sln,xproj}",
    "!.editorconfig",
    "!**/._*",
    "!**/{.DS_Store,.git,.hg,.svn,CVS,RCS,SCCS,.gitignore,.gitattributes}",
    "!**/{__pycache__,thumbs.db,.flowconfig,.idea,.vs,.nyc_output}",
    "!**/{appveyor.yml,.travis.yml,circle.yml}",
    "!**/{npm-debug.log,yarn.lock,.yarn-integrity,.yarn-metadata.json}"
  ],
  
  // Extra metadata
  extraMetadata: {
    main: "main.js"
  },
  
  // Compression
  compression: "maximum",
  
  // Platform configurations
  ...platformConfigs
};
```

### Environment-Specific Builds

#### Development Build
```javascript
// package.json scripts
{
  "build:dev": "electron-builder --config.compression=store --config.nsis.oneClick=false",
  "build:dev:win": "electron-builder --win --config.compression=store",
  "build:dev:mac": "electron-builder --mac --config.compression=store",
  "build:dev:linux": "electron-builder --linux --config.compression=store"
}
```

#### Production Build
```javascript
{
  "build": "electron-builder",
  "build:win": "electron-builder --win",
  "build:mac": "electron-builder --mac", 
  "build:linux": "electron-builder --linux",
  "build:all": "electron-builder -mwl"
}
```

---

## Development Builds

### Quick Development Build

```bash
# Build for current platform (development mode)
npm run build:dev

# Pack without creating installer
npm run pack

# Pack for specific platform
npm run pack:win
npm run pack:mac
npm run pack:linux
```

### Development Build Options

```bash
# Build with specific configuration
npx electron-builder --config.productName="Ainflue Studio Dev" --config.appId="com.ainflue.desktop.dev"

# Skip code signing (faster builds)
npx electron-builder --config.win.certificateFile="" --config.mac.identity=""

# Include development dependencies
npx electron-builder --config.includeSubNodeModules=true
```

---

## Production Builds

### Pre-Build Checklist

1. **Update version number** in `package.json`
2. **Set production environment** variables
3. **Verify code signing certificates**
4. **Test on clean environment**
5. **Run security audit**
6. **Validate build configuration**

```bash
# Pre-build validation
npm run validate
npm audit --audit-level moderate
npm run test:all
npm run lint
```

### Building for Production

#### Single Platform
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

#### All Platforms
```bash
# Build for all platforms (requires appropriate environment)
npm run build:all

# Or step by step
npm run build:win && npm run build:mac && npm run build:linux
```

### Production Build with Code Signing

#### Windows
```bash
# Set environment variables
export CSC_LINK="path/to/certificate.p12"
export CSC_KEY_PASSWORD="certificate_password"
export WIN_CSC_LINK="path/to/certificate.p12"
export WIN_CSC_KEY_PASSWORD="certificate_password"

# Build with signing
npm run build:win
```

#### macOS
```bash
# Set environment variables
export CSC_LINK="Developer ID Application: Fahed Mlaiel"
export CSC_KEY_PASSWORD="keychain_password"
export APPLE_ID="mlaiel@live.de"
export APPLE_ID_PASSWORD="app_specific_password"

# Build with signing and notarization
npm run build:mac
```

#### Linux
```bash
# Set GPG key for signing
export GPG_PRIVATE_KEY="path/to/private.key"
export GPG_PASSPHRASE="gpg_passphrase"

# Build with signing
npm run build:linux
```

---

## Platform-Specific Builds

### Windows Configuration

```javascript
// Windows build configuration
win: {
  target: [
    {
      target: "nsis",
      arch: ["x64", "ia32"]
    },
    {
      target: "portable", 
      arch: ["x64", "ia32"]
    },
    {
      target: "msi",
      arch: ["x64"]
    }
  ],
  icon: "assets/icon.ico",
  requestedExecutionLevel: "asInvoker",
  
  // Code signing
  certificateFile: "certs/windows.p12",
  certificatePassword: process.env.WIN_CSC_KEY_PASSWORD,
  
  // Windows specific settings
  verifyUpdateCodeSignature: true,
  publisherName: ["Fahed Mlaiel"],
  
  // File associations
  fileAssociations: [
    {
      ext: "ainproj",
      name: "Ainflue Project",
      description: "Ainflue Studio Project File",
      icon: "assets/project.ico"
    }
  ]
}
```

#### NSIS Installer Options
```javascript
nsis: {
  oneClick: false,
  allowToChangeInstallationDirectory: true,
  allowElevation: true,
  createDesktopShortcut: true,
  createStartMenuShortcut: true,
  shortcutName: "Ainflue Studio",
  runAfterFinish: true,
  license: "LICENSE.txt",
  installerIcon: "assets/installer.ico",
  uninstallerIcon: "assets/uninstaller.ico",
  installerHeaderIcon: "assets/header.ico",
  installerSidebar: "assets/installer-sidebar.bmp",
  uninstallerSidebar: "assets/uninstaller-sidebar.bmp",
  artifactName: "${productName}-${version}-Setup.${ext}",
  deleteAppDataOnUninstall: false,
  
  // Custom NSIS script
  include: "build/installer.nsh"
}
```

### macOS Configuration

```javascript
// macOS build configuration
mac: {
  category: "public.app-category.productivity",
  icon: "assets/icon.icns",
  hardenedRuntime: true,
  gatekeeperAssess: false,
  entitlements: "build/entitlements.mac.plist",
  entitlementsInherit: "build/entitlements.mac.plist",
  
  // Code signing
  identity: "Developer ID Application: Fahed Mlaiel",
  
  // Notarization
  notarize: {
    teamId: "TEAM_ID",
    appleId: "mlaiel@live.de",
    appleIdPassword: process.env.APPLE_ID_PASSWORD
  },
  
  target: [
    {
      target: "dmg",
      arch: ["x64", "arm64"]
    },
    {
      target: "zip",
      arch: ["x64", "arm64"]
    },
    {
      target: "pkg",
      arch: ["x64", "arm64"]
    }
  ]
}
```

#### DMG Configuration
```javascript
dmg: {
  artifactName: "${productName}-${version}.${ext}",
  title: "${productName} ${version}",
  icon: "assets/icon.icns",
  background: "assets/dmg-background.png",
  window: {
    width: 540,
    height: 380
  },
  contents: [
    {
      x: 140,
      y: 250,
      type: "file"
    },
    {
      x: 400,
      y: 250,
      type: "link",
      path: "/Applications"
    }
  ],
  internetEnabled: true,
  sign: true
}
```

### Linux Configuration

```javascript
// Linux build configuration
linux: {
  target: [
    {
      target: "AppImage",
      arch: ["x64", "arm64"]
    },
    {
      target: "deb",
      arch: ["x64", "arm64"]
    },
    {
      target: "rpm",
      arch: ["x64", "arm64"]
    },
    {
      target: "tar.gz",
      arch: ["x64", "arm64"]
    }
  ],
  icon: "assets/icon.png",
  category: "AudioVideo",
  
  // Desktop entry
  desktop: {
    Name: "Ainflue Studio",
    Comment: "AI-Powered Content Creation Studio",
    Exec: "ainflue-studio %U",
    Icon: "ainflue-studio",
    Type: "Application",
    Categories: "AudioVideo;Video;Audio;Graphics;Photography;",
    MimeType: "application/x-ainflue-project;",
    StartupWMClass: "Ainflue Studio"
  },
  
  // File associations
  fileAssociations: [
    {
      ext: "ainproj",
      name: "Ainflue Project",
      mimeType: "application/x-ainflue-project"
    }
  ]
}
```

---

## Distribution

### Distribution Strategies

#### 1. Direct Download
```bash
# Build and prepare for direct download
npm run build
npm run package:direct
```

#### 2. Auto-Update Distribution
```bash
# Build with auto-update metadata
npm run build:publish
```

#### 3. Store Distribution

##### Microsoft Store (Windows)
```javascript
// AppX configuration for Microsoft Store
appx: {
  applicationId: "FahedMlaiel.AinfluStudio",
  backgroundColor: "#1a1a1a",
  showNameOnTiles: true,
  identityName: "FahedMlaiel.AinfluStudio",
  publisher: "CN=Fahed Mlaiel",
  publisherDisplayName: "Fahed Mlaiel",
  languages: ["en-US", "de-DE", "fr-FR", "ar-SA"]
}
```

##### Mac App Store
```javascript
// Mac App Store configuration
mas: {
  category: "public.app-category.productivity",
  entitlements: "build/entitlements.mas.plist",
  entitlementsInherit: "build/entitlements.mas.inherit.plist",
  provisioningProfile: "build/embedded.provisionprofile",
  identity: "3rd Party Mac Developer Application: Fahed Mlaiel"
}
```

### Release Preparation

#### 1. Version Management
```bash
# Update version
npm version patch  # 1.0.0 -> 1.0.1
npm version minor  # 1.0.0 -> 1.1.0
npm version major  # 1.0.0 -> 2.0.0

# Custom version
npm version 1.2.3
```

#### 2. Release Notes
Create `RELEASE_NOTES.md`:
```markdown
# Ainflue Studio v1.2.3

## New Features
- Advanced AI content optimization
- Real-time collaboration improvements
- Enhanced audio processing

## Bug Fixes
- Fixed memory leak in video processing
- Resolved crash on large file uploads
- Improved startup performance

## Security Updates
- Updated dependencies with security patches
- Enhanced content encryption
```

#### 3. Build Release
```bash
# Create release build
npm run build:release

# Sign and notarize (if configured)
npm run build:release:signed

# Generate checksums
npm run generate:checksums
```

---

## Auto-Updates

### Auto-Update Configuration

```javascript
// Auto-update configuration
publish: {
  provider: "github",
  owner: "Mlaiel",
  repo: "Ainflue",
  private: true,
  token: process.env.GITHUB_TOKEN,
  releaseType: "release"
}
```

### Update Server Setup

#### GitHub Releases
```bash
# Set GitHub token
export GITHUB_TOKEN="github_personal_access_token"

# Build and publish
npm run build:publish
```

#### Custom Update Server
```javascript
// Custom update server configuration
publish: {
  provider: "generic",
  url: "https://updates.ainflue.com/desktop/",
  channel: "latest"
}
```

### Update Implementation

#### Main Process
```javascript
// Auto-updater setup in main process
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('checking-for-update', () => {
  log.info('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  log.info('Update available.');
});

autoUpdater.on('update-not-available', (info) => {
  log.info('Update not available.');
});

autoUpdater.on('error', (err) => {
  log.error('Error in auto-updater:', err);
});

autoUpdater.on('download-progress', (progressObj) => {
  let log_message = "Download speed: " + progressObj.bytesPerSecond;
  log_message = log_message + ' - Downloaded ' + progressObj.percent + '%';
  log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
  log.info(log_message);
});

autoUpdater.on('update-downloaded', (info) => {
  log.info('Update downloaded');
  autoUpdater.quitAndInstall();
});
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: |
        cd desktop
        npm ci
    
    - name: Run tests
      run: |
        cd desktop
        npm test
    
    - name: Build application
      env:
        CSC_LINK: ${{ secrets.CSC_LINK }}
        CSC_KEY_PASSWORD: ${{ secrets.CSC_KEY_PASSWORD }}
        APPLE_ID: ${{ secrets.APPLE_ID }}
        APPLE_ID_PASSWORD: ${{ secrets.APPLE_ID_PASSWORD }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        cd desktop
        npm run build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.os }}-build
        path: desktop/dist/
```

### Build Scripts

#### Pre-build Script
```bash
#!/bin/bash
# scripts/pre-build.sh

echo "Running pre-build checks..."

# Validate environment
node -e "console.log('Node version:', process.version)"
npm -v

# Check certificates
if [[ "$OSTYPE" == "darwin"* ]]; then
  security find-identity -v -p codesigning
fi

# Run tests
npm test

# Security audit
npm audit --audit-level high

echo "Pre-build checks completed successfully"
```

#### Post-build Script
```bash
#!/bin/bash
# scripts/post-build.sh

echo "Running post-build tasks..."

# Generate checksums
cd dist
for file in *.{exe,dmg,AppImage,deb,rpm}; do
  if [ -f "$file" ]; then
    shasum -a 256 "$file" > "$file.sha256"
  fi
done

# Upload to CDN (if configured)
if [ ! -z "$CDN_UPLOAD_URL" ]; then
  echo "Uploading to CDN..."
  # Upload logic here
fi

echo "Post-build tasks completed"
```

---

## Troubleshooting

### Common Build Issues

#### 1. Code Signing Failures

**Windows:**
```bash
# Check certificate
certutil -dump certificate.p12

# Verify certificate is valid
signtool verify /pa your-app.exe
```

**macOS:**
```bash
# Check certificate
security find-identity -v -p codesigning

# Verify app signature
codesign -vvv --deep --strict /path/to/app.app
spctl -a -vvv -t install /path/to/app.app
```

#### 2. Native Dependencies Issues
```bash
# Rebuild native dependencies
npm run rebuild

# Or manually
./node_modules/.bin/electron-rebuild

# For specific modules
npm rebuild sharp --platform=win32 --arch=x64
```

#### 3. Memory Issues During Build
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build

# Or in package.json
"build": "node --max-old-space-size=8192 ./node_modules/.bin/electron-builder"
```

#### 4. Build Size Optimization
```bash
# Analyze bundle size
npm run analyze-bundle

# Remove unnecessary files
npm run clean:deps

# Optimize assets
npm run optimize:assets
```

### Debug Build Process

```bash
# Enable verbose logging
DEBUG=electron-builder npm run build

# Build with debug info
npm run build -- --config.compression=store --config.debug=true

# Check build configuration
npx electron-builder --help
```

### Platform-Specific Issues

#### Windows
- Ensure Windows SDK is installed
- Check PowerShell execution policy
- Verify certificate chain

#### macOS
- Update Xcode command line tools
- Check Apple Developer account status
- Verify entitlements configuration

#### Linux
- Install missing system dependencies
- Check desktop file validation
- Verify AppImage requirements

---

## Performance Optimization

### Build Performance

```bash
# Parallel builds (if building multiple platforms)
npm run build:win & npm run build:mac & npm run build:linux & wait

# Skip unnecessary compression for development
npm run build:dev

# Use build cache
npm run build -- --config.buildCacheDir=.build-cache
```

### Bundle Size Optimization

```javascript
// Exclude unnecessary files
files: [
  "!node_modules/*/test/**/*",
  "!node_modules/*/docs/**/*",
  "!node_modules/*/*.md",
  "!node_modules/*/LICENSE*",
  "!**/*.{map,d.ts}"
]
```

---

## Security Considerations

### Code Signing Best Practices

1. **Store certificates securely**
2. **Use timestamping servers**
3. **Verify signatures after build**
4. **Implement certificate rotation**
5. **Monitor certificate expiration**

### Build Environment Security

```bash
# Use environment variables for secrets
export CSC_LINK="$HOME/.certificates/certificate.p12"
export CSC_KEY_PASSWORD="$(cat ~/.cert-password)"

# Never commit certificates or passwords
echo "*.p12" >> .gitignore
echo "*.pem" >> .gitignore
echo ".env.local" >> .gitignore
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
This documentation contains proprietary build and deployment procedures. Unauthorized use is prohibited.