# Ainflue Desktop - Development Guide

**Author:** Fahed Mlaiel (mlaiel@live.de)  
**Copyright:** (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This software and concept are the exclusive intellectual property of Fahed Mlaiel.  
Any unauthorized use, copying, distribution, or reverse engineering is strictly prohibited.  
Legal action will be taken against violators under German and international copyright law.  
Contact: mlaiel@live.de for licensing inquiries.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Debugging](#debugging)
8. [Performance Optimization](#performance-optimization)
9. [Security Guidelines](#security-guidelines)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Node.js**: 18.0.0 or higher
- **npm**: 9.0.0 or higher
- **Python**: 3.8+ (for native dependencies)
- **FFmpeg**: Latest version (for media processing)
- **Git**: 2.30.0 or higher

### Platform-Specific Requirements

#### Windows
```bash
# Install Windows Build Tools
npm install -g windows-build-tools

# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
# Install build essentials
sudo apt-get install build-essential libnss3-dev libatk-bridge2.0-dev libdrm2-dev libxss1-dev libgconf-2-4

# Install FFmpeg
sudo apt-get install ffmpeg

# Additional dependencies for Electron
sudo apt-get install libxrandr2 libasound2-dev libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0
```

---

## Development Environment Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Mlaiel/Ainflue.git
cd Ainflue/desktop

# Install dependencies
npm install

# Install native dependencies
npm run postinstall
```

### 2. Environment Configuration

Create `.env.development` file:
```env
# Development Configuration
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug

# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000

# Security
ENCRYPTION_KEY=dev-encryption-key-change-in-production
JWT_SECRET=dev-jwt-secret-change-in-production

# Media Processing
FFMPEG_PATH=/usr/local/bin/ffmpeg
TEMP_DIR=./temp
MAX_FILE_SIZE=500MB

# AI Services
AI_API_KEY=your-development-ai-api-key
AI_ENDPOINT=http://localhost:5000

# Features
ENABLE_GPU_ACCELERATION=true
ENABLE_AI_PROCESSING=true
ENABLE_REAL_TIME_COLLABORATION=true
```

### 3. Development Tools

#### Install Recommended VSCode Extensions
```json
{
  "recommendations": [
    "ms-vscode.vscode-electron",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

#### Configure VSCode Settings
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "electron.shell": true,
  "typescript.preferences.includePackageJsonAutoImports": "on"
}
```

---

## Project Structure

```
desktop/
├── main.js                          # Main Electron process
├── preload.js                       # Preload script for security
├── index.js                         # Application entry point
├── package.json                     # Dependencies and scripts
├── electron_builder_config.js       # Build configuration
├── validation.js                    # Project validation
├── 
├── src/                             # Source code organization
│   ├── main/                        # Main process components
│   │   ├── window_manager.js        # Window management
│   │   ├── menu_manager.js          # Native menus
│   │   ├── ipc_handlers.js          # IPC communication
│   │   ├── security_policies.js     # Security enforcement
│   │   └── update_manager.js        # Auto-update system
│   │
│   └── renderer/                    # Renderer process
│       ├── app_initializer.js       # App initialization
│       ├── state_manager.js         # State management
│       ├── api_client.js            # API communication
│       ├── event_dispatcher.js      # Event handling
│       ├── error_handler.js         # Error management
│       ├── ui_framework.js          # UI framework
│       ├── theme_engine.js          # Theming system
│       ├── responsive_layout.js     # Responsive design
│       ├── animation_engine.js      # Animations
│       └── accessibility_manager.js # Accessibility
│
├── components/                      # UI Components
│   ├── studio_timeline.js           # Timeline editor
│   ├── content_library.js           # Media library
│   ├── preview_monitor.js           # Content preview
│   ├── audio_mixer.js               # Audio mixing
│   ├── video_editor.js              # Video editing
│   ├── upload_interface.js          # File upload
│   ├── ai_processing_panel.js       # AI controls
│   └── analytics_dashboard.js       # Analytics
│
├── services/                        # Business logic services
│   ├── content_processor.js         # Content processing
│   ├── metadata_extractor.js        # Metadata extraction
│   ├── watermark_engine.js          # Watermarking
│   ├── format_converter.js          # Format conversion
│   ├── quality_optimizer.js         # Quality optimization
│   ├── platform_connector.js        # Platform integration
│   ├── ai_analysis_client.js        # AI analysis
│   │
│   └── ai/                          # AI services
│       ├── content_analysis.js      # Content analysis
│       ├── performance_prediction.js # Performance prediction
│       ├── optimization_engine.js   # Content optimization
│       ├── collaboration_matching.js # Collaboration matching
│       └── trend_prediction.js      # Trend analysis
│
├── security/                        # Security modules
│   ├── content_encryption.js        # Content encryption
│   ├── digital_signature.js         # Digital signatures
│   ├── access_control.js            # Access control
│   ├── secure_storage.js            # Secure storage
│   └── privacy_protection.js        # Privacy tools
│
├── ui_components/                   # Reusable UI components
│   ├── dashboard_layouts.js         # Dashboard layouts
│   ├── header_controls.js           # Header controls
│   ├── modal_manager.js             # Modal system
│   ├── notification_system.js       # Notifications
│   ├── professional_controls.js     # Professional controls
│   ├── data_visualization.js        # Data visualization
│   ├── form_builder.js              # Form builder
│   ├── media_player.js              # Media player
│   ├── drag_drop_manager.js         # Drag & drop
│   └── tooltip_system.js            # Tooltips
│
├── scripts/                         # Automation scripts
│   ├── analytics_automation.sh      # Analytics automation
│   ├── audio_processing_automation.sh # Audio processing
│   ├── collaboration_automation.sh  # Collaboration tools
│   ├── deployment_automation.sh     # Deployment
│   ├── distribution_automation.sh   # Distribution
│   ├── build_optimization.sh        # Build optimization
│   ├── testing_automation.sh        # Testing automation
│   ├── code_quality_check.sh        # Code quality
│   ├── security_scan.sh             # Security scanning
│   └── performance_benchmark.sh     # Performance benchmarking
│
├── assets/                          # Application assets
│   ├── icons/                       # Application icons
│   ├── images/                      # Images and graphics
│   ├── fonts/                       # Custom fonts
│   ├── styles/                      # CSS stylesheets
│   └── audio/                       # Audio assets
│
└── renderer/                        # Renderer HTML/CSS/JS
    ├── index.html                   # Main window HTML
    ├── styles/                      # Stylesheets
    ├── scripts/                     # Client-side scripts
    └── assets/                      # Renderer assets
```

---

## Development Workflow

### 1. Starting Development

```bash
# Start development server
npm run dev

# Start with debugging enabled
npm run dev -- --dev --debug

# Start with specific features disabled
npm run dev -- --no-ai --no-gpu
```

### 2. Code Development Cycle

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement Changes**
   - Follow code standards
   - Add comprehensive logging
   - Include error handling
   - Write unit tests

3. **Test Changes**
   ```bash
   # Run unit tests
   npm run test:unit
   
   # Run integration tests
   npm run test:integration
   
   # Run E2E tests
   npm run test:e2e
   
   # Run all tests
   npm test
   ```

4. **Validate Code Quality**
   ```bash
   # Lint code
   npm run lint
   
   # Check code formatting
   npm run format:check
   
   # Validate project structure
   npm run validate
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/new-feature-name
   ```

### 3. Release Workflow

```bash
# Build for all platforms
npm run build

# Build for specific platform
npm run build:win
npm run build:mac
npm run build:linux

# Create distribution packages
npm run dist

# Pack without distribution
npm run pack
```

---

## Code Standards

### 1. JavaScript/Node.js Standards

#### File Structure
```javascript
/**
 * Ainflue Desktop - Module Name
 * 
 * Brief description of module functionality
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const log = require('electron-log');

class ModuleName extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      defaultOption: 'defaultValue',
      ...options
    };
    
    this.initialize();
  }
  
  async initialize() {
    try {
      // Initialization logic
      log.info('Module initialized successfully');
      this.emit('initialized');
    } catch (error) {
      log.error('Module initialization failed:', error);
      this.emit('error', error);
    }
  }
  
  // Public methods
  
  // Private methods (prefix with _)
  
  // Cleanup
  destroy() {
    this.removeAllListeners();
    log.info('Module destroyed');
  }
}

module.exports = ModuleName;
```

#### Naming Conventions
- **Files**: `snake_case.js`
- **Classes**: `PascalCase`
- **Methods**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_camelCase`

#### Error Handling
```javascript
// Always use try-catch for async operations
try {
  const result = await someAsyncOperation();
  return result;
} catch (error) {
  log.error('Operation failed:', error);
  this.emit('error', error);
  throw error; // Re-throw if needed
}

// Use proper error types
throw new Error('Descriptive error message');
throw new TypeError('Invalid argument type');
throw new RangeError('Value out of range');
```

#### Logging Standards
```javascript
const log = require('electron-log');

// Log levels: error, warn, info, debug
log.error('Critical error occurred:', error);
log.warn('Warning message');
log.info('Informational message');
log.debug('Debug information');

// Include context in logs
log.info(`User ${userId} performed action ${action}`);
```

### 2. Event Handling Standards

```javascript
// Use EventEmitter for component communication
class ComponentName extends EventEmitter {
  performAction() {
    try {
      // Perform action
      this.emit('actionCompleted', result);
    } catch (error) {
      this.emit('actionFailed', error);
    }
  }
}

// Listen to events with proper cleanup
component.on('actionCompleted', this.handleSuccess.bind(this));
component.on('actionFailed', this.handleError.bind(this));

// Always remove listeners in cleanup
destroy() {
  component.removeAllListeners();
}
```

### 3. Security Standards

```javascript
// Validate all inputs
function validateInput(input, type, constraints = {}) {
  if (typeof input !== type) {
    throw new TypeError(`Expected ${type}, got ${typeof input}`);
  }
  
  if (constraints.required && !input) {
    throw new Error('Required field is missing');
  }
  
  // Additional validation based on constraints
}

// Sanitize file paths
const path = require('path');
function sanitizePath(filePath) {
  const normalized = path.normalize(filePath);
  const resolved = path.resolve(normalized);
  
  // Ensure path is within allowed directory
  if (!resolved.startsWith(allowedBaseDir)) {
    throw new Error('Path outside allowed directory');
  }
  
  return resolved;
}

// Use secure random for IDs
const crypto = require('crypto');
function generateSecureId() {
  return crypto.randomBytes(16).toString('hex');
}
```

---

## Testing Guidelines

### 1. Unit Testing

Create tests in `test_reports/desktop/` directory:

```javascript
// desktop_unit_tests.js
const assert = require('assert');
const ModuleName = require('../path/to/module');

describe('ModuleName', () => {
  let module;
  
  beforeEach(() => {
    module = new ModuleName();
  });
  
  afterEach(() => {
    if (module) {
      module.destroy();
    }
  });
  
  it('should initialize correctly', async () => {
    await module.initialize();
    assert.strictEqual(module.isInitialized, true);
  });
  
  it('should handle errors gracefully', async () => {
    try {
      await module.performInvalidOperation();
      assert.fail('Should have thrown error');
    } catch (error) {
      assert(error instanceof Error);
    }
  });
});
```

### 2. Integration Testing

```javascript
// integration_tests.js
const { app, BrowserWindow } = require('electron');

describe('Integration Tests', () => {
  let mainWindow;
  
  before(async () => {
    await app.whenReady();
    mainWindow = new BrowserWindow({
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../preload.js')
      }
    });
  });
  
  after(async () => {
    if (mainWindow) {
      mainWindow.close();
    }
    app.quit();
  });
  
  it('should load main window', (done) => {
    mainWindow.loadFile('renderer/index.html');
    mainWindow.once('ready-to-show', () => {
      assert(mainWindow.isVisible());
      done();
    });
  });
});
```

### 3. E2E Testing

```javascript
// e2e_tests.js
const { Application } = require('spectron');
const path = require('path');

describe('E2E Tests', () => {
  let app;
  
  beforeEach(async () => {
    app = new Application({
      path: electron,
      args: [path.join(__dirname, '../main.js')]
    });
    
    await app.start();
  });
  
  afterEach(async () => {
    if (app && app.isRunning()) {
      await app.stop();
    }
  });
  
  it('should start application', async () => {
    const windowCount = await app.client.getWindowCount();
    assert.strictEqual(windowCount, 1);
  });
  
  it('should have correct title', async () => {
    const title = await app.client.getTitle();
    assert.strictEqual(title, 'Ainflue Studio');
  });
});
```

### 4. Running Tests

```bash
# Run all tests
npm test

# Run specific test suite
npm run test:unit
npm run test:integration
npm run test:e2e
npm run test:performance
npm run test:security

# Run tests with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

---

## Debugging

### 1. Main Process Debugging

```bash
# Start with Node.js debugger
npm run debug

# Connect with VSCode debugger
# Add to launch.json:
{
  "type": "node",
  "request": "launch",
  "name": "Debug Main Process",
  "program": "${workspaceFolder}/main.js",
  "args": ["--dev"],
  "console": "integratedTerminal",
  "env": {
    "NODE_ENV": "development"
  }
}
```

### 2. Renderer Process Debugging

```javascript
// Enable developer tools in development
if (process.env.NODE_ENV === 'development') {
  mainWindow.webContents.openDevTools();
}

// Add debugging helpers
window.debugInfo = {
  version: app.getVersion(),
  platform: process.platform,
  node: process.versions.node,
  electron: process.versions.electron
};
```

### 3. Logging Configuration

```javascript
// Configure electron-log
const log = require('electron-log');

// Set log level
log.transports.console.level = 'debug';
log.transports.file.level = 'info';

// Custom log format
log.transports.console.format = '[{y}-{m}-{d} {h}:{i}:{s}.{ms}] [{level}] {text}';

// Log to specific file
log.transports.file.resolvePathFn = () => path.join(app.getPath('userData'), 'logs/main.log');
```

### 4. Performance Profiling

```javascript
// Profile performance
const { performance } = require('perf_hooks');

function profileFunction(fn, name) {
  return async function(...args) {
    const start = performance.now();
    try {
      const result = await fn.apply(this, args);
      const end = performance.now();
      log.debug(`${name} took ${end - start} milliseconds`);
      return result;
    } catch (error) {
      const end = performance.now();
      log.error(`${name} failed after ${end - start} milliseconds:`, error);
      throw error;
    }
  };
}
```

---

## Performance Optimization

### 1. Main Process Optimization

```javascript
// Use worker threads for CPU-intensive tasks
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
  // Main thread
  const worker = new Worker(__filename);
  worker.postMessage(data);
  worker.on('message', (result) => {
    // Handle result
  });
} else {
  // Worker thread
  parentPort.on('message', (data) => {
    const result = performCPUIntensiveTask(data);
    parentPort.postMessage(result);
  });
}
```

### 2. Memory Management

```javascript
// Implement proper cleanup
class ResourceManager {
  constructor() {
    this.resources = new Map();
  }
  
  addResource(id, resource) {
    this.resources.set(id, resource);
  }
  
  removeResource(id) {
    const resource = this.resources.get(id);
    if (resource && resource.destroy) {
      resource.destroy();
    }
    this.resources.delete(id);
  }
  
  cleanup() {
    for (const [id, resource] of this.resources) {
      this.removeResource(id);
    }
    this.resources.clear();
  }
}
```

### 3. Renderer Process Optimization

```javascript
// Use requestIdleCallback for non-critical tasks
function performNonCriticalTask(task) {
  if (window.requestIdleCallback) {
    window.requestIdleCallback((deadline) => {
      if (deadline.timeRemaining() > 0) {
        task();
      } else {
        performNonCriticalTask(task);
      }
    });
  } else {
    setTimeout(task, 100);
  }
}

// Implement virtual scrolling for large lists
class VirtualList {
  constructor(container, itemHeight, items) {
    this.container = container;
    this.itemHeight = itemHeight;
    this.items = items;
    this.visibleCount = Math.ceil(container.clientHeight / itemHeight);
    this.render();
  }
  
  render() {
    const startIndex = Math.floor(this.container.scrollTop / this.itemHeight);
    const endIndex = Math.min(startIndex + this.visibleCount, this.items.length);
    
    // Render only visible items
    this.renderItems(startIndex, endIndex);
  }
}
```

---

## Security Guidelines

### 1. IPC Security

```javascript
// Secure IPC validation
const { ipcMain } = require('electron');

ipcMain.handle('secure-operation', async (event, data) => {
  // Validate sender
  if (!isValidSender(event.sender)) {
    throw new Error('Unauthorized access');
  }
  
  // Validate input
  const validatedData = validateAndSanitize(data);
  
  // Perform operation
  return await performSecureOperation(validatedData);
});

function isValidSender(sender) {
  // Implement sender validation logic
  return sender.getURL().startsWith('file://');
}
```

### 2. Content Security Policy

```html
<!-- Add to renderer HTML -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' wss: https:;
  font-src 'self';
  object-src 'none';
  media-src 'self' https:;
">
```

### 3. Secure File Handling

```javascript
const path = require('path');
const fs = require('fs').promises;

async function secureFileOperation(filePath, operation) {
  // Validate file path
  const normalizedPath = path.normalize(filePath);
  const resolvedPath = path.resolve(normalizedPath);
  
  // Ensure path is within allowed directory
  const allowedDir = path.resolve(app.getPath('userData'));
  if (!resolvedPath.startsWith(allowedDir)) {
    throw new Error('File access denied: outside allowed directory');
  }
  
  // Check file permissions
  try {
    await fs.access(resolvedPath, fs.constants.R_OK);
  } catch (error) {
    throw new Error('File access denied: insufficient permissions');
  }
  
  // Perform operation
  return await operation(resolvedPath);
}
```

---

## Troubleshooting

### Common Issues

#### 1. Dependencies Installation Failed
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Rebuild native dependencies
npm run rebuild
```

#### 2. FFmpeg Not Found
```bash
# Install FFmpeg
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# Set FFmpeg path in environment
export FFMPEG_PATH=/usr/local/bin/ffmpeg
```

#### 3. GPU Acceleration Issues
```bash
# Disable GPU acceleration for testing
npm run dev -- --disable-gpu

# Check GPU support
npm run check-gpu
```

#### 4. Build Failures
```bash
# Clean build artifacts
npm run clean

# Rebuild with verbose output
npm run build -- --verbose

# Check build requirements
npm run check-build-deps
```

#### 5. Performance Issues
```bash
# Enable performance profiling
npm run dev -- --profile

# Check memory usage
npm run check-memory

# Analyze bundle size
npm run analyze-bundle
```

### Debug Commands

```bash
# Validate project structure
npm run validate

# Check code quality
npm run lint

# Security audit
npm audit

# Performance benchmark
npm run benchmark

# System information
npm run system-info
```

### Getting Help

1. **Check logs**: `~/Library/Logs/Ainflue/` (macOS) or `%APPDATA%/Ainflue/logs/` (Windows)
2. **Run diagnostics**: `npm run diagnose`
3. **Contact support**: mlaiel@live.de (authorized personnel only)

---

## Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Security Guidelines](https://electronjs.org/docs/tutorial/security)

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
This documentation is confidential and proprietary. Unauthorized distribution is prohibited.