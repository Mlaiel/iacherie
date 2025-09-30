/**
 * Ainflue Desktop - Studio Workspace Manager
 * 
 * Professional multi-monitor workspace management for content creation studios
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { BrowserWindow, screen } = require('electron');
const log = require('electron-log');
const EventEmitter = require('events');

class StudioWorkspaceManager extends EventEmitter {
  constructor() {
    super();
    
    this.displays = [];
    this.windows = new Map();
    this.workspaces = new Map();
    this.currentWorkspace = null;
    this.workspaceLayouts = new Map();
    this.panelStates = new Map();
    
    // Workspace types
    this.workspaceTypes = {
      SINGLE_MONITOR: 'single-monitor',
      DUAL_HORIZONTAL: 'dual-horizontal', 
      DUAL_VERTICAL: 'dual-vertical',
      TRIPLE_MONITOR: 'triple-monitor',
      QUAD_MONITOR: 'quad-monitor',
      CUSTOM: 'custom'
    };
    
    // Window types for professional studio
    this.windowTypes = {
      MAIN: 'main',
      TIMELINE: 'timeline',
      MIXER: 'mixer',
      PREVIEW: 'preview',
      PROPERTIES: 'properties',
      LIBRARY: 'library',
      EFFECTS: 'effects',
      MONITOR: 'monitor',
      SCOPES: 'scopes'
    };
    
    // Panel configurations
    this.defaultPanels = {
      timeline: { position: 'bottom', size: { width: '100%', height: 400 }, resizable: true },
      mixer: { position: 'right', size: { width: 300, height: '100%' }, resizable: true },
      preview: { position: 'center-right', size: { width: 600, height: 400 }, resizable: true },
      properties: { position: 'right', size: { width: 280, height: 300 }, resizable: true },
      library: { position: 'left', size: { width: 250, height: '100%' }, resizable: true },
      effects: { position: 'left', size: { width: 280, height: 350 }, resizable: true }
    };
    
    this.isInitialized = false;
    log.info('Studio Workspace Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Studio Workspace Manager...');
      
      // Detect available displays
      this.detectDisplays();
      
      // Setup display change monitoring
      this.setupDisplayMonitoring();
      
      // Load workspace configurations
      this.loadWorkspaceConfigurations();
      
      // Create default workspace
      await this.createDefaultWorkspace();
      
      // Setup window management
      this.setupWindowManagement();
      
      this.isInitialized = true;
      log.info('✅ Studio Workspace Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Studio Workspace Manager:', error);
      throw error;
    }
  }

  detectDisplays() {
    this.displays = screen.getAllDisplays();
    
    log.info(`Detected ${this.displays.length} display(s):`);
    this.displays.forEach((display, index) => {
      log.info(`  Display ${index + 1}: ${display.bounds.width}x${display.bounds.height} at (${display.bounds.x}, ${display.bounds.y})`);
    });
    
    // Determine optimal workspace type
    this.recommendedWorkspaceType = this.getRecommendedWorkspaceType();
    
    this.emit('displays-detected', { 
      displays: this.displays, 
      count: this.displays.length,
      recommended: this.recommendedWorkspaceType 
    });
  }

  getRecommendedWorkspaceType() {
    const displayCount = this.displays.length;
    
    if (displayCount >= 4) {
      return this.workspaceTypes.QUAD_MONITOR;
    } else if (displayCount === 3) {
      return this.workspaceTypes.TRIPLE_MONITOR;
    } else if (displayCount === 2) {
      // Determine orientation based on display positions
      const display1 = this.displays[0];
      const display2 = this.displays[1];
      
      if (Math.abs(display1.bounds.x - display2.bounds.x) > Math.abs(display1.bounds.y - display2.bounds.y)) {
        return this.workspaceTypes.DUAL_HORIZONTAL;
      } else {
        return this.workspaceTypes.DUAL_VERTICAL;
      }
    } else {
      return this.workspaceTypes.SINGLE_MONITOR;
    }
  }

  setupDisplayMonitoring() {
    screen.on('display-added', (event, newDisplay) => {
      log.info('Display added:', newDisplay.id);
      this.detectDisplays();
      this.adaptToDisplayChanges();
    });

    screen.on('display-removed', (event, oldDisplay) => {
      log.info('Display removed:', oldDisplay.id);
      this.detectDisplays();
      this.adaptToDisplayChanges();
    });

    screen.on('display-metrics-changed', (event, display, changedMetrics) => {
      log.debug('Display metrics changed:', display.id, changedMetrics);
      this.detectDisplays();
    });
    
    log.info('Display monitoring configured');
  }

  loadWorkspaceConfigurations() {
    // Define professional workspace layouts
    this.workspaceLayouts.set(this.workspaceTypes.SINGLE_MONITOR, {
      name: 'Single Monitor Studio',
      description: 'Optimized layout for single monitor workflow',
      windows: [
        {
          type: this.windowTypes.MAIN,
          display: 0,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['timeline', 'mixer', 'properties']
        }
      ]
    });

    this.workspaceLayouts.set(this.workspaceTypes.DUAL_HORIZONTAL, {
      name: 'Dual Monitor Horizontal',
      description: 'Timeline and tools on primary, preview and mixer on secondary',
      windows: [
        {
          type: this.windowTypes.MAIN,
          display: 0,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['timeline', 'library', 'properties']
        },
        {
          type: this.windowTypes.PREVIEW,
          display: 1,
          bounds: { x: 0, y: 0, width: '60%', height: '100%' },
          panels: ['preview', 'scopes']
        },
        {
          type: this.windowTypes.MIXER,
          display: 1,
          bounds: { x: '60%', y: 0, width: '40%', height: '100%' },
          panels: ['mixer', 'effects']
        }
      ]
    });

    this.workspaceLayouts.set(this.workspaceTypes.TRIPLE_MONITOR, {
      name: 'Triple Monitor Professional',
      description: 'Full professional studio layout with dedicated preview monitor',
      windows: [
        {
          type: this.windowTypes.MAIN,
          display: 0,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['timeline', 'library']
        },
        {
          type: this.windowTypes.PREVIEW,
          display: 1,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['preview', 'monitor', 'scopes']
        },
        {
          type: this.windowTypes.MIXER,
          display: 2,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['mixer', 'effects', 'properties']
        }
      ]
    });

    this.workspaceLayouts.set(this.workspaceTypes.QUAD_MONITOR, {
      name: 'Quad Monitor Master Studio',
      description: 'Ultimate professional studio layout',
      windows: [
        {
          type: this.windowTypes.MAIN,
          display: 0,
          bounds: { x: 0, y: 0, width: '100%', height: '70%' },
          panels: ['library', 'properties']
        },
        {
          type: this.windowTypes.TIMELINE,
          display: 0,
          bounds: { x: 0, y: '70%', width: '100%', height: '30%' },
          panels: ['timeline']
        },
        {
          type: this.windowTypes.PREVIEW,
          display: 1,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['preview', 'monitor']
        },
        {
          type: this.windowTypes.MIXER,
          display: 2,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['mixer']
        },
        {
          type: this.windowTypes.EFFECTS,
          display: 3,
          bounds: { x: 0, y: 0, width: '100%', height: '100%' },
          panels: ['effects', 'scopes']
        }
      ]
    });
    
    log.info('Workspace configurations loaded');
  }

  async createDefaultWorkspace() {
    const workspaceType = this.recommendedWorkspaceType;
    const workspaceId = `default-${workspaceType}`;
    
    const workspace = {
      id: workspaceId,
      name: `Default ${workspaceType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} Workspace`,
      type: workspaceType,
      layout: this.workspaceLayouts.get(workspaceType),
      createdAt: new Date(),
      isActive: true,
      windows: new Map(),
      panels: new Map()
    };
    
    this.workspaces.set(workspaceId, workspace);
    this.currentWorkspace = workspace;
    
    log.info(`Default workspace created: ${workspace.name}`);
    this.emit('workspace-created', workspace);
    
    return workspace;
  }

  async createWorkspace(name, type = null) {
    const workspaceType = type || this.recommendedWorkspaceType;
    const workspaceId = `workspace-${Date.now()}`;
    
    if (!this.workspaceLayouts.has(workspaceType)) {
      throw new Error(`Unknown workspace type: ${workspaceType}`);
    }
    
    const workspace = {
      id: workspaceId,
      name,
      type: workspaceType,
      layout: this.workspaceLayouts.get(workspaceType),
      createdAt: new Date(),
      isActive: false,
      windows: new Map(),
      panels: new Map()
    };
    
    this.workspaces.set(workspaceId, workspace);
    
    log.info(`Workspace created: ${name} (${workspaceType})`);
    this.emit('workspace-created', workspace);
    
    return workspace;
  }

  async activateWorkspace(workspaceId) {
    const workspace = this.workspaces.get(workspaceId);
    
    if (!workspace) {
      throw new Error(`Workspace not found: ${workspaceId}`);
    }
    
    // Deactivate current workspace
    if (this.currentWorkspace) {
      this.currentWorkspace.isActive = false;
      await this.saveWorkspaceState(this.currentWorkspace);
    }
    
    // Activate new workspace
    workspace.isActive = true;
    this.currentWorkspace = workspace;
    
    // Apply workspace layout
    await this.applyWorkspaceLayout(workspace);
    
    log.info(`Workspace activated: ${workspace.name}`);
    this.emit('workspace-activated', workspace);
    
    return workspace;
  }

  async applyWorkspaceLayout(workspace) {
    try {
      // Close existing windows that are not part of the new layout
      await this.closeUnnecessaryWindows(workspace);
      
      // Create/update windows according to layout
      for (const windowConfig of workspace.layout.windows) {
        await this.createOrUpdateStudioWindow(workspace, windowConfig);
      }
      
      // Apply panel configurations
      await this.applyPanelConfigurations(workspace);
      
      log.info(`Workspace layout applied: ${workspace.name}`);
      this.emit('workspace-layout-applied', workspace);
      
    } catch (error) {
      log.error(`Failed to apply workspace layout for ${workspace.name}:`, error);
      throw error;
    }
  }

  async createOrUpdateStudioWindow(workspace, windowConfig) {
    const windowId = `${workspace.id}-${windowConfig.type}`;
    
    // Check if window already exists
    let window = this.windows.get(windowId);
    
    if (window && !window.isDestroyed()) {
      // Update existing window
      await this.updateWindowBounds(window, windowConfig);
    } else {
      // Create new window
      window = await this.createStudioWindow(windowId, windowConfig);
      this.windows.set(windowId, window);
      workspace.windows.set(windowConfig.type, window);
    }
    
    // Setup window event handlers
    this.setupStudioWindowEvents(window, workspace, windowConfig);
    
    return window;
  }

  async createStudioWindow(windowId, windowConfig) {
    const display = this.displays[windowConfig.display] || this.displays[0];
    const bounds = this.calculateWindowBounds(display, windowConfig.bounds);
    
    const windowOptions = {
      x: bounds.x,
      y: bounds.y,
      width: bounds.width,
      height: bounds.height,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: require('path').join(__dirname, 'preload.js'),
        backgroundThrottling: false
      },
      title: this.getWindowTitle(windowConfig.type),
      backgroundColor: '#1f2937',
      show: false,
      resizable: true,
      movable: true,
      frame: true
    };
    
    // Platform-specific optimizations
    if (process.platform === 'darwin') {
      windowOptions.titleBarStyle = 'hiddenInset';
      windowOptions.vibrancy = 'under-window';
    } else if (process.platform === 'win32') {
      windowOptions.autoHideMenuBar = true;
    }
    
    const window = new BrowserWindow(windowOptions);
    
    // Load appropriate content for window type
    const htmlFile = this.getWindowHtmlFile(windowConfig.type);
    await window.loadFile(htmlFile);
    
    // Show window when ready
    window.once('ready-to-show', () => {
      window.show();
    });
    
    log.debug(`Studio window created: ${windowId} (${windowConfig.type})`);
    
    return window;
  }

  calculateWindowBounds(display, boundsConfig) {
    const displayBounds = display.workArea;
    
    const bounds = {
      x: displayBounds.x,
      y: displayBounds.y,
      width: displayBounds.width,
      height: displayBounds.height
    };
    
    // Handle percentage-based positioning
    if (typeof boundsConfig.x === 'string' && boundsConfig.x.endsWith('%')) {
      bounds.x += displayBounds.width * (parseFloat(boundsConfig.x) / 100);
    } else if (typeof boundsConfig.x === 'number') {
      bounds.x += boundsConfig.x;
    }
    
    if (typeof boundsConfig.y === 'string' && boundsConfig.y.endsWith('%')) {
      bounds.y += displayBounds.height * (parseFloat(boundsConfig.y) / 100);
    } else if (typeof boundsConfig.y === 'number') {
      bounds.y += boundsConfig.y;
    }
    
    if (typeof boundsConfig.width === 'string' && boundsConfig.width.endsWith('%')) {
      bounds.width = displayBounds.width * (parseFloat(boundsConfig.width) / 100);
    } else if (typeof boundsConfig.width === 'number') {
      bounds.width = boundsConfig.width;
    }
    
    if (typeof boundsConfig.height === 'string' && boundsConfig.height.endsWith('%')) {
      bounds.height = displayBounds.height * (parseFloat(boundsConfig.height) / 100);
    } else if (typeof boundsConfig.height === 'number') {
      bounds.height = boundsConfig.height;
    }
    
    return bounds;
  }

  getWindowTitle(windowType) {
    const titles = {
      [this.windowTypes.MAIN]: 'Ainflue Studio - Main',
      [this.windowTypes.TIMELINE]: 'Ainflue Studio - Timeline',
      [this.windowTypes.MIXER]: 'Ainflue Studio - Audio Mixer',
      [this.windowTypes.PREVIEW]: 'Ainflue Studio - Preview Monitor',
      [this.windowTypes.PROPERTIES]: 'Ainflue Studio - Properties',
      [this.windowTypes.LIBRARY]: 'Ainflue Studio - Media Library',
      [this.windowTypes.EFFECTS]: 'Ainflue Studio - Effects',
      [this.windowTypes.MONITOR]: 'Ainflue Studio - Video Monitor',
      [this.windowTypes.SCOPES]: 'Ainflue Studio - Audio Scopes'
    };
    
    return titles[windowType] || 'Ainflue Studio';
  }

  getWindowHtmlFile(windowType) {
    const htmlFiles = {
      [this.windowTypes.MAIN]: 'renderer/index.html',
      [this.windowTypes.TIMELINE]: 'renderer/timeline.html',
      [this.windowTypes.MIXER]: 'renderer/mixer.html',
      [this.windowTypes.PREVIEW]: 'renderer/preview.html',
      [this.windowTypes.PROPERTIES]: 'renderer/properties.html',
      [this.windowTypes.LIBRARY]: 'renderer/library.html',
      [this.windowTypes.EFFECTS]: 'renderer/effects.html',
      [this.windowTypes.MONITOR]: 'renderer/monitor.html',
      [this.windowTypes.SCOPES]: 'renderer/scopes.html'
    };
    
    return htmlFiles[windowType] || 'renderer/index.html';
  }

  setupStudioWindowEvents(window, workspace, windowConfig) {
    window.on('closed', () => {
      const windowId = `${workspace.id}-${windowConfig.type}`;
      this.windows.delete(windowId);
      workspace.windows.delete(windowConfig.type);
      
      log.debug(`Studio window closed: ${windowId}`);
      this.emit('studio-window-closed', { workspace, windowConfig });
    });
    
    window.on('resize', () => {
      this.saveWindowState(window, workspace, windowConfig);
    });
    
    window.on('move', () => {
      this.saveWindowState(window, workspace, windowConfig);
    });
  }

  async updateWindowBounds(window, windowConfig) {
    const display = this.displays[windowConfig.display] || this.displays[0];
    const bounds = this.calculateWindowBounds(display, windowConfig.bounds);
    
    window.setBounds(bounds);
    
    log.debug(`Window bounds updated: ${windowConfig.type}`);
  }

  async closeUnnecessaryWindows(workspace) {
    const requiredWindowTypes = new Set(workspace.layout.windows.map(w => w.type));
    
    for (const [windowId, window] of this.windows) {
      if (windowId.startsWith(workspace.id)) {
        const windowType = windowId.split('-').pop();
        if (!requiredWindowTypes.has(windowType) && !window.isDestroyed()) {
          window.close();
        }
      }
    }
  }

  async applyPanelConfigurations(workspace) {
    // This would configure panels within windows
    // For now, just emit event for renderer processes
    for (const windowConfig of workspace.layout.windows) {
      const window = workspace.windows.get(windowConfig.type);
      if (window && !window.isDestroyed()) {
        window.webContents.send('configure-panels', {
          panels: windowConfig.panels,
          workspace: workspace.id
        });
      }
    }
    
    log.debug(`Panel configurations applied for workspace: ${workspace.name}`);
  }

  setupWindowManagement() {
    // Setup global window management events
    this.on('workspace-activated', (workspace) => {
      // Notify all windows about workspace change
      for (const window of workspace.windows.values()) {
        if (!window.isDestroyed()) {
          window.webContents.send('workspace-changed', {
            workspaceId: workspace.id,
            workspaceName: workspace.name,
            workspaceType: workspace.type
          });
        }
      }
    });
    
    log.info('Window management configured');
  }

  // Workspace state management
  async saveWorkspaceState(workspace) {
    const state = {
      id: workspace.id,
      name: workspace.name,
      type: workspace.type,
      windows: {},
      panels: Object.fromEntries(workspace.panels),
      timestamp: new Date().toISOString()
    };
    
    // Save window states
    for (const [windowType, window] of workspace.windows) {
      if (!window.isDestroyed()) {
        state.windows[windowType] = {
          bounds: window.getBounds(),
          maximized: window.isMaximized(),
          minimized: window.isMinimized(),
          visible: window.isVisible()
        };
      }
    }
    
    // Store state (would be persisted to disk in real implementation)
    this.emit('workspace-state-saved', { workspace, state });
    
    log.debug(`Workspace state saved: ${workspace.name}`);
  }

  async saveWindowState(window, workspace, windowConfig) {
    if (window.isDestroyed()) return;
    
    const state = {
      bounds: window.getBounds(),
      maximized: window.isMaximized(),
      minimized: window.isMinimized(),
      visible: window.isVisible(),
      timestamp: new Date().toISOString()
    };
    
    this.emit('window-state-saved', { window, workspace, windowConfig, state });
  }

  // Adaptation methods
  async adaptToDisplayChanges() {
    const newRecommendedType = this.getRecommendedWorkspaceType();
    
    if (newRecommendedType !== this.recommendedWorkspaceType) {
      log.info(`Display configuration changed, recommending: ${newRecommendedType}`);
      this.recommendedWorkspaceType = newRecommendedType;
      
      // Offer to adapt current workspace
      this.emit('workspace-adaptation-suggested', {
        currentType: this.currentWorkspace?.type,
        recommendedType: newRecommendedType,
        displayCount: this.displays.length
      });
    }
  }

  async adaptCurrentWorkspace() {
    if (this.currentWorkspace) {
      const newType = this.recommendedWorkspaceType;
      
      if (newType !== this.currentWorkspace.type && this.workspaceLayouts.has(newType)) {
        // Update workspace type and layout
        this.currentWorkspace.type = newType;
        this.currentWorkspace.layout = this.workspaceLayouts.get(newType);
        
        // Apply new layout
        await this.applyWorkspaceLayout(this.currentWorkspace);
        
        log.info(`Workspace adapted to: ${newType}`);
        this.emit('workspace-adapted', this.currentWorkspace);
      }
    }
  }

  // Public API methods
  getAvailableWorkspaces() {
    return Array.from(this.workspaces.values());
  }

  getCurrentWorkspace() {
    return this.currentWorkspace;
  }

  getWorkspaceTypes() {
    return Object.values(this.workspaceTypes);
  }

  getDisplayInfo() {
    return {
      displays: this.displays,
      count: this.displays.length,
      recommended: this.recommendedWorkspaceType
    };
  }

  getActiveWindows() {
    return Array.from(this.windows.values()).filter(window => !window.isDestroyed());
  }

  // Cleanup
  async cleanup() {
    // Save current workspace state
    if (this.currentWorkspace) {
      await this.saveWorkspaceState(this.currentWorkspace);
    }
    
    // Close all studio windows
    for (const window of this.windows.values()) {
      if (!window.isDestroyed()) {
        window.close();
      }
    }
    
    // Clear data structures
    this.windows.clear();
    this.workspaces.clear();
    
    log.info('Studio Workspace Manager cleaned up');
  }
}

module.exports = StudioWorkspaceManager;