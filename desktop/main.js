/**
 * Ainflue Desktop - Main Electron Process
 * 
 * Advanced AI-powered content creation studio with professional editing capabilities,
 * multi-monitor support, and system integration features.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { app, BrowserWindow, Menu, ipcMain, dialog, shell, screen } = require('electron');
const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');
const log = require('electron-log');
const path = require('path');
const fs = require('fs');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;

// Initialize secure store
const store = new Store({
  encryptionKey: 'ainflue-desktop-secure-key-2025',
  name: 'ainflue-preferences'
});

class AinflueMasterStudio {
  constructor() {
    this.mainWindow = null;
    this.studioWindow = null;
    this.isProduction = !process.argv.includes('--dev');
    this.displays = [];
    
    this.initializeApp();
  }

  initializeApp() {
    // App event handlers
    app.whenReady().then(() => this.createMainWindow());
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') app.quit();
    });
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) this.createMainWindow();
    });

    // IPC handlers
    this.setupIpcHandlers();
    
    // Auto-updater
    if (this.isProduction) {
      app.on('ready', () => {
        autoUpdater.checkForUpdatesAndNotify();
      });
    }
  }

  createMainWindow() {
    // Get primary display
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    // Create main window
    this.mainWindow = new BrowserWindow({
      width: Math.min(1400, width - 100),
      height: Math.min(900, height - 100),
      minWidth: 1200,
      minHeight: 800,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: this.isProduction
      },
      icon: path.join(__dirname, 'assets', 'icon.png'),
      title: 'Ainflue Studio - Professional AI Content Creation',
      titleBarStyle: 'hiddenInset',
      backgroundColor: '#1f2937',
      show: false
    });

    // Load application
    if (this.isProduction) {
      this.mainWindow.loadFile('renderer/index.html');
    } else {
      this.mainWindow.loadURL('http://localhost:3000');
      this.mainWindow.webContents.openDevTools();
    }

    // Window events
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      this.setupApplicationMenu();
      this.detectDisplays();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  setupApplicationMenu() {
    const isMac = process.platform === 'darwin';
    
    const template = [
      // macOS app menu
      ...(isMac ? [{
        label: app.getName(),
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideothers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' }
        ]
      }] : []),
      
      // File menu
      {
        label: 'File',
        submenu: [
          {
            label: 'New Project',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.mainWindow.webContents.send('menu-new-project')
          },
          {
            label: 'New Template',
            accelerator: 'CmdOrCtrl+Shift+N',
            click: () => this.mainWindow.webContents.send('menu-new-template')
          },
          {
            label: 'Open Project',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.openProject()
          },
          {
            label: 'Open Recent',
            submenu: [
              {
                label: 'Clear Recent',
                click: () => this.mainWindow.webContents.send('clear-recent')
              }
            ]
          },
          { type: 'separator' },
          {
            label: 'Save Project',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.mainWindow.webContents.send('menu-save-project')
          },
          {
            label: 'Save As...',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => this.mainWindow.webContents.send('menu-save-as')
          },
          {
            label: 'Save Template',
            accelerator: 'CmdOrCtrl+Alt+S',
            click: () => this.mainWindow.webContents.send('menu-save-template')
          },
          { type: 'separator' },
          {
            label: 'Import Content',
            accelerator: 'CmdOrCtrl+I',
            click: () => this.importContent()
          },
          {
            label: 'Import Audio',
            accelerator: 'CmdOrCtrl+Shift+I',
            click: () => this.importAudio()
          },
          {
            label: 'Import Video',
            accelerator: 'CmdOrCtrl+Alt+I',
            click: () => this.importVideo()
          },
          { type: 'separator' },
          {
            label: 'Export Project',
            accelerator: 'CmdOrCtrl+E',
            click: () => this.exportProject()
          },
          {
            label: 'Export Audio',
            accelerator: 'CmdOrCtrl+Shift+E',
            click: () => this.mainWindow.webContents.send('export-audio')
          },
          {
            label: 'Export Video',
            accelerator: 'CmdOrCtrl+Alt+E',
            click: () => this.mainWindow.webContents.send('export-video')
          },
          { type: 'separator' },
          ...(!isMac ? [{ role: 'quit' }] : [])
        ]
      },
      
      // Edit menu
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectall' },
          { type: 'separator' },
          {
            label: 'Find',
            accelerator: 'CmdOrCtrl+F',
            click: () => this.mainWindow.webContents.send('toggle-find')
          },
          {
            label: 'Find and Replace',
            accelerator: 'CmdOrCtrl+H',
            click: () => this.mainWindow.webContents.send('toggle-replace')
          },
          { type: 'separator' },
          {
            label: 'Preferences',
            accelerator: isMac ? 'Cmd+,' : 'Ctrl+,',
            click: () => this.showPreferences()
          }
        ]
      },
      
      // View menu
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' },
          { type: 'separator' },
          { role: 'togglefullscreen' },
          { type: 'separator' },
          {
            label: 'Timeline View',
            accelerator: 'CmdOrCtrl+1',
            click: () => this.mainWindow.webContents.send('switch-view', 'timeline')
          },
          {
            label: 'Library View',
            accelerator: 'CmdOrCtrl+2',
            click: () => this.mainWindow.webContents.send('switch-view', 'library')
          },
          {
            label: 'Inspector View',
            accelerator: 'CmdOrCtrl+3',
            click: () => this.mainWindow.webContents.send('switch-view', 'inspector')
          },
          { type: 'separator' },
          {
            label: 'Show Toolbar',
            accelerator: 'CmdOrCtrl+Alt+T',
            click: () => this.mainWindow.webContents.send('toggle-toolbar')
          },
          {
            label: 'Show Sidebar',
            accelerator: 'CmdOrCtrl+\\',
            click: () => this.mainWindow.webContents.send('toggle-sidebar')
          }
        ]
      },
      
      // Studio menu
      {
        label: 'Studio',
        submenu: [
          {
            label: 'Open Advanced Studio',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => this.createStudioWindow()
          },
          {
            label: 'Multi-Monitor Setup',
            accelerator: 'CmdOrCtrl+M',
            click: () => this.setupMultiMonitor()
          },
          { type: 'separator' },
          {
            label: 'AI Processing Panel',
            accelerator: 'CmdOrCtrl+Alt+A',
            click: () => this.mainWindow.webContents.send('toggle-ai-panel')
          },
          {
            label: 'Content Protection',
            accelerator: 'CmdOrCtrl+Alt+P',
            click: () => this.mainWindow.webContents.send('toggle-protection-panel')
          },
          {
            label: 'Analytics Dashboard',
            accelerator: 'CmdOrCtrl+Alt+D',
            click: () => this.mainWindow.webContents.send('toggle-analytics')
          },
          { type: 'separator' },
          {
            label: 'Audio Processor',
            accelerator: 'CmdOrCtrl+Shift+A',
            click: () => this.mainWindow.webContents.send('open-audio-processor')
          },
          {
            label: 'Video Editor',
            accelerator: 'CmdOrCtrl+Shift+V',
            click: () => this.mainWindow.webContents.send('open-video-editor')
          },
          {
            label: 'Effects Library',
            accelerator: 'CmdOrCtrl+Shift+F',
            click: () => this.mainWindow.webContents.send('open-effects-library')
          }
        ]
      },
      
      // Tools menu
      {
        label: 'Tools',
        submenu: [
          {
            label: 'Content Analyzer',
            accelerator: 'CmdOrCtrl+T',
            click: () => this.mainWindow.webContents.send('open-analyzer')
          },
          {
            label: 'Batch Processor',
            accelerator: 'CmdOrCtrl+B',
            click: () => this.mainWindow.webContents.send('open-batch-processor')
          },
          {
            label: 'Watermark Generator',
            accelerator: 'CmdOrCtrl+W',
            click: () => this.mainWindow.webContents.send('open-watermark-generator')
          },
          { type: 'separator' },
          {
            label: 'System Information',
            accelerator: 'CmdOrCtrl+Alt+I',
            click: () => this.showSystemInfo()
          },
          {
            label: 'Performance Monitor',
            accelerator: 'CmdOrCtrl+Alt+M',
            click: () => this.mainWindow.webContents.send('toggle-performance-monitor')
          }
        ]
      },
      
      // Window menu
      {
        label: 'Window',
        submenu: [
          { role: 'minimize' },
          { role: 'close' },
          ...(isMac ? [
            { type: 'separator' },
            { role: 'front' },
            { type: 'separator' },
            { role: 'window' }
          ] : [])
        ]
      },
      
      // Help menu
      {
        role: 'help',
        submenu: [
          {
            label: 'Learning Resources',
            click: async () => {
              const { shell } = require('electron');
              await shell.openExternal('https://ainflue.com/docs');
            }
          },
          {
            label: 'Keyboard Shortcuts',
            accelerator: 'CmdOrCtrl+/',
            click: () => this.showKeyboardShortcuts()
          },
          {
            label: 'Report Issue',
            click: async () => {
              const { shell } = require('electron');
              await shell.openExternal('https://github.com/Mlaiel/Ainflue/issues');
            }
          },
          { type: 'separator' },
          ...(!isMac ? [{
            label: 'About Ainflue',
            click: () => this.showAbout()
          }] : [])
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupIpcHandlers() {
    // File operations
    ipcMain.handle('select-file', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow, {
        properties: ['openFile', 'multiSelections'],
        filters: [
          { name: 'All Supported', extensions: ['mp3', 'wav', 'flac', 'mp4', 'mov', 'avi', 'jpg', 'png', 'pdf'] },
          { name: 'Audio', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] },
          { name: 'Video', extensions: ['mp4', 'mov', 'avi', 'mkv'] },
          { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'svg'] },
          { name: 'Documents', extensions: ['pdf', 'doc', 'docx', 'txt'] }
        ]
      });
      return result.filePaths;
    });

    // Store operations
    ipcMain.handle('store-get', (event, key) => store.get(key));
    ipcMain.handle('store-set', (event, key, value) => store.set(key, value));
    ipcMain.handle('store-delete', (event, key) => store.delete(key));
    ipcMain.handle('store-clear', () => store.clear());

    // System information
    ipcMain.handle('get-system-info', () => this.getSystemInfo());
    ipcMain.handle('get-displays', () => screen.getAllDisplays());
    ipcMain.handle('get-primary-display', () => screen.getPrimaryDisplay());

    // Display operations
    ipcMain.handle('detect-displays', () => {
      this.detectDisplays();
      return this.displays;
    });

    // Window operations
    ipcMain.handle('minimize-window', () => this.mainWindow.minimize());
    ipcMain.handle('maximize-window', () => {
      if (this.mainWindow.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow.maximize();
      }
    });
    ipcMain.handle('close-window', () => this.mainWindow.close());

    // Studio window operations
    ipcMain.handle('open-studio', () => this.createStudioWindow());
    ipcMain.handle('close-studio', () => {
      if (this.studioWindow) {
        this.studioWindow.close();
      }
    });

    // Application operations
    ipcMain.handle('show-message-box', async (event, options) => {
      return await dialog.showMessageBox(this.mainWindow, options);
    });

    ipcMain.handle('show-save-dialog', async (event, options) => {
      return await dialog.showSaveDialog(this.mainWindow, options);
    });

    ipcMain.handle('show-open-dialog', async (event, options) => {
      return await dialog.showOpenDialog(this.mainWindow, options);
    });

    // External operations
    ipcMain.handle('open-external', async (event, url) => {
      await shell.openExternal(url);
    });

    ipcMain.handle('show-item-in-folder', (event, fullPath) => {
      shell.showItemInFolder(fullPath);
    });

    // AI processing simulation
    ipcMain.handle('process-ai-content', async (event, contentPath, options) => {
      // Simulate AI processing
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            processedPath: contentPath,
            analysis: {
              quality: Math.floor(Math.random() * 30) + 70,
              suggestions: [
                'Enhanced audio clarity',
                'Optimized compression applied',
                'Watermark protection added'
              ],
              processingTime: Math.floor(Math.random() * 5000) + 1000
            }
          });
        }, 2000);
      });
    });

    // Content processing
    ipcMain.handle('process-batch-content', async (event, contentList, options) => {
      const results = [];
      for (const content of contentList) {
        const result = await new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              success: true,
              originalPath: content,
              processedPath: content.replace(/\.[^/.]+$/, '_processed$&'),
              progress: (results.length + 1) / contentList.length * 100
            });
          }, 1000);
        });
        results.push(result);
        
        // Send progress update
        event.sender.send('batch-progress', {
          completed: results.length,
          total: contentList.length,
          currentFile: content
        });
      }
      return results;
    });

    // Performance monitoring
    ipcMain.handle('get-performance-metrics', () => {
      const usage = process.cpuUsage();
      const memUsage = process.memoryUsage();
      
      return {
        cpu: {
          user: usage.user,
          system: usage.system
        },
        memory: {
          rss: Math.round(memUsage.rss / 1024 / 1024),
          heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024),
          heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024),
          external: Math.round(memUsage.external / 1024 / 1024)
        },
        platform: process.platform,
        arch: process.arch,
        version: process.version
      };
    });

    // Multi-platform clipboard operations
    ipcMain.handle('write-clipboard-text', (event, text) => {
      require('electron').clipboard.writeText(text);
    });

    ipcMain.handle('read-clipboard-text', () => {
      return require('electron').clipboard.readText();
    });

    // Notification operations
    ipcMain.handle('show-notification', (event, options) => {
      const { Notification } = require('electron');
      
      if (Notification.isSupported()) {
        const notification = new Notification({
          title: options.title || 'Ainflue Studio',
          body: options.body || '',
          icon: path.join(__dirname, 'assets', 'icon.png'),
          sound: options.sound || false
        });
        
        if (options.onClick) {
          notification.on('click', () => {
            event.sender.send('notification-clicked', options.onClick);
          });
        }
        
        notification.show();
        return true;
      }
      return false;
    });
  }

  async openProject() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Ainflue Project', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled && result.filePaths[0]) {
      const projectData = fs.readFileSync(result.filePaths[0], 'utf8');
      this.mainWindow.webContents.send('load-project', JSON.parse(projectData));
    }
  }

  async importContent() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Media Files', extensions: ['mp3', 'wav', 'mp4', 'mov', 'jpg', 'png'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled) {
      this.mainWindow.webContents.send('import-content', result.filePaths);
    }
  }

  detectDisplays() {
    this.displays = screen.getAllDisplays();
    log.info(`Detected ${this.displays.length} displays:`, this.displays.map(d => ({
      id: d.id,
      bounds: d.bounds,
      size: d.size,
      scaleFactor: d.scaleFactor,
      primary: d === screen.getPrimaryDisplay()
    })));
    
    // Store display information
    store.set('displays', this.displays);
    
    // Send display info to renderer
    if (this.mainWindow) {
      this.mainWindow.webContents.send('displays-detected', this.displays);
    }
  }

  createStudioWindow() {
    if (this.studioWindow) {
      this.studioWindow.focus();
      return;
    }

    // Get secondary display if available for multi-monitor setup
    const displays = screen.getAllDisplays();
    const secondaryDisplay = displays.find(display => display !== screen.getPrimaryDisplay());
    const targetDisplay = secondaryDisplay || screen.getPrimaryDisplay();
    
    const { x, y, width, height } = targetDisplay.bounds;

    this.studioWindow = new BrowserWindow({
      x: x + 50,
      y: y + 50,
      width: Math.min(1600, width - 100),
      height: Math.min(1000, height - 100),
      minWidth: 1400,
      minHeight: 900,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: this.isProduction
      },
      icon: path.join(__dirname, 'assets', 'icon.png'),
      title: 'Ainflue Advanced Studio - Professional Content Creation',
      titleBarStyle: 'hiddenInset',
      backgroundColor: '#0f172a',
      show: false,
      parent: this.mainWindow,
      modal: false
    });

    // Load studio interface
    if (this.isProduction) {
      this.studioWindow.loadFile('renderer/studio.html');
    } else {
      this.studioWindow.loadURL('http://localhost:3000/studio');
      this.studioWindow.webContents.openDevTools();
    }

    this.studioWindow.once('ready-to-show', () => {
      this.studioWindow.show();
      
      // Send display and system info to studio
      this.studioWindow.webContents.send('studio-init', {
        displays: this.displays,
        currentDisplay: targetDisplay,
        systemInfo: this.getSystemInfo()
      });
    });

    this.studioWindow.on('closed', () => {
      this.studioWindow = null;
    });

    // Handle window move between displays
    this.studioWindow.on('moved', () => {
      const currentDisplay = screen.getDisplayNearestPoint(this.studioWindow.getBounds());
      this.studioWindow.webContents.send('display-changed', currentDisplay);
    });
  }

  setupMultiMonitor() {
    this.detectDisplays();
    
    if (this.displays.length < 2) {
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Multi-Monitor Setup',
        message: 'Single Display Detected',
        detail: 'Multi-monitor features require at least 2 displays. Please connect additional monitors and try again.',
        buttons: ['OK']
      });
      return;
    }

    // Show multi-monitor configuration window
    const configWindow = new BrowserWindow({
      width: 800,
      height: 600,
      modal: true,
      parent: this.mainWindow,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      title: 'Multi-Monitor Configuration'
    });

    if (this.isProduction) {
      configWindow.loadFile('renderer/multi-monitor-config.html');
    } else {
      configWindow.loadURL('http://localhost:3000/multi-monitor-config');
    }

    configWindow.webContents.send('displays-info', this.displays);
  }

  getSystemInfo() {
    const os = require('os');
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      electronVersion: process.versions.electron,
      chromeVersion: process.versions.chrome,
      cpus: os.cpus().length,
      totalMemory: Math.round(os.totalmem() / (1024 * 1024 * 1024)) + ' GB',
      freeMemory: Math.round(os.freemem() / (1024 * 1024 * 1024)) + ' GB',
      uptime: Math.round(os.uptime() / 3600) + ' hours',
      hostname: os.hostname(),
      displays: this.displays.length
    };
  }

  showSystemInfo() {
    const systemInfo = this.getSystemInfo();
    
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'System Information',
      message: 'Ainflue Studio System Information',
      detail: `Platform: ${systemInfo.platform}
Architecture: ${systemInfo.arch}
Node.js: ${systemInfo.nodeVersion}
Electron: ${systemInfo.electronVersion}
Chrome: ${systemInfo.chromeVersion}

Hardware:
CPU Cores: ${systemInfo.cpus}
Total Memory: ${systemInfo.totalMemory}
Free Memory: ${systemInfo.freeMemory}
System Uptime: ${systemInfo.uptime}

Displays: ${systemInfo.displays}
Hostname: ${systemInfo.hostname}`,
      buttons: ['OK', 'Copy to Clipboard']
    }).then((result) => {
      if (result.response === 1) {
        require('electron').clipboard.writeText(JSON.stringify(systemInfo, null, 2));
      }
    });
  }

  showPreferences() {
    // Show preferences window
    const prefsWindow = new BrowserWindow({
      width: 800,
      height: 600,
      modal: true,
      parent: this.mainWindow,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      title: 'Preferences'
    });

    if (this.isProduction) {
      prefsWindow.loadFile('renderer/preferences.html');
    } else {
      prefsWindow.loadURL('http://localhost:3000/preferences');
    }
  }

  showKeyboardShortcuts() {
    const shortcuts = `
Ainflue Studio Keyboard Shortcuts

File Operations:
Ctrl/Cmd + N          New Project
Ctrl/Cmd + Shift + N  New Template
Ctrl/Cmd + O          Open Project
Ctrl/Cmd + S          Save Project
Ctrl/Cmd + Shift + S  Save As
Ctrl/Cmd + I          Import Content
Ctrl/Cmd + E          Export Project

Studio:
Ctrl/Cmd + Shift + S  Advanced Studio
Ctrl/Cmd + M          Multi-Monitor Setup
Ctrl/Cmd + Alt + A    AI Processing Panel
Ctrl/Cmd + Alt + P    Content Protection

View:
Ctrl/Cmd + 1          Timeline View
Ctrl/Cmd + 2          Library View
Ctrl/Cmd + 3          Inspector View
Ctrl/Cmd + \\          Toggle Sidebar

Tools:
Ctrl/Cmd + T          Content Analyzer
Ctrl/Cmd + B          Batch Processor
Ctrl/Cmd + W          Watermark Generator
Ctrl/Cmd + Alt + I    System Information

Other:
Ctrl/Cmd + F          Find
Ctrl/Cmd + H          Find & Replace
Ctrl/Cmd + /          Show Shortcuts
    `;

    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'Keyboard Shortcuts',
      message: 'Ainflue Studio Keyboard Shortcuts',
      detail: shortcuts,
      buttons: ['OK']
    });
  }

  async importAudio() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled) {
      this.mainWindow.webContents.send('import-audio', result.filePaths);
    }
  }

  async importVideo() {
    const result = await dialog.showOpenDialog(this.mainWindow, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Video Files', extensions: ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled) {
      this.mainWindow.webContents.send('import-video', result.filePaths);
    }
  }

  async exportProject() {
    const result = await dialog.showSaveDialog(this.mainWindow, {
      filters: [
        { name: 'Ainflue Project', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });

    if (!result.canceled) {
      this.mainWindow.webContents.send('export-project', result.filePath);
    }
  }

  showAbout() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'About Ainflue Studio',
      message: 'Ainflue Desktop Studio v1.0.0',
      detail: `Professional AI-powered content creation platform\n\nDeveloped by: Fahed Mlaiel\nEmail: mlaiel@live.de\n\n© 2025 Fahed Mlaiel. All rights reserved.`,
      buttons: ['OK']
    });
  }
}

// Initialize application
new AinflueMasterStudio();