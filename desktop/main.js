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
    
    // Platform detection and configuration
    this.platform = {
      isMac: process.platform === 'darwin',
      isWindows: process.platform === 'win32',
      isLinux: process.platform === 'linux',
      current: process.platform,
      arch: process.arch
    };
    
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

    // Platform-specific window options
    const windowOptions = {
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
      icon: path.join(__dirname, 'assets', this.platform.isWindows ? 'icon.ico' : this.platform.isMac ? 'icon.icns' : 'icon.png'),
      title: 'Ainflue Studio - Professional AI Content Creation',
      backgroundColor: '#1f2937',
      show: false
    };

    // Platform-specific configurations
    if (this.platform.isMac) {
      windowOptions.titleBarStyle = 'hiddenInset';
      windowOptions.vibrancy = 'under-window';
      windowOptions.transparent = false;
    } else if (this.platform.isWindows) {
      windowOptions.frame = true;
      windowOptions.autoHideMenuBar = true;
    } else if (this.platform.isLinux) {
      windowOptions.frame = true;
      windowOptions.autoHideMenuBar = false;
    }

    // Create main window
    this.mainWindow = new BrowserWindow(windowOptions);

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
    const template = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Project',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.mainWindow.webContents.send('menu-new-project')
          },
          {
            label: 'Open Project',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.openProject()
          },
          {
            label: 'Save Project',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.mainWindow.webContents.send('menu-save-project')
          },
          { type: 'separator' },
          {
            label: 'Import Content',
            accelerator: 'CmdOrCtrl+I',
            click: () => this.importContent()
          },
          {
            label: 'Export Project',
            accelerator: 'CmdOrCtrl+E',
            click: () => this.exportProject()
          },
          { type: 'separator' },
          { role: 'quit' }
        ]
      },
      {
        label: 'Studio',
        submenu: [
          {
            label: 'Open Advanced Studio',
            accelerator: 'CmdOrCtrl+Shift+S',
            click: () => this.createStudioWindow()
          },
          {
            label: 'AI Processing Panel',
            accelerator: 'CmdOrCtrl+Alt+A',
            click: () => this.mainWindow.webContents.send('toggle-ai-panel')
          },
          {
            label: 'Content Protection',
            accelerator: 'CmdOrCtrl+Alt+P',
            click: () => this.mainWindow.webContents.send('toggle-protection-panel')
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'About Ainflue',
            click: () => this.showAbout()
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupIpcHandlers() {
    // Platform information
    ipcMain.handle('get-platform-info', () => {
      return {
        platform: this.platform.current,
        isMac: this.platform.isMac,
        isWindows: this.platform.isWindows,
        isLinux: this.platform.isLinux,
        arch: this.platform.arch,
        version: app.getVersion(),
        name: app.getName()
      };
    });

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