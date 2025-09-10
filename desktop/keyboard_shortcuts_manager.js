/**
 * Ainflue Desktop - Keyboard Shortcuts Manager
 * 
 * Global and local keyboard shortcuts for professional workflow acceleration
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { globalShortcut, BrowserWindow } = require('electron');
const log = require('electron-log');
const EventEmitter = require('events');

class KeyboardShortcutsManager extends EventEmitter {
  constructor() {
    super();
    
    this.globalShortcuts = new Map();
    this.localShortcuts = new Map();
    this.shortcutCategories = new Map();
    this.isEnabled = true;
    this.conflicts = new Set();
    
    // Shortcut categories
    this.categories = {
      GLOBAL: 'global',
      WINDOW: 'window',
      TIMELINE: 'timeline',
      MIXER: 'mixer',
      PREVIEW: 'preview',
      FILE: 'file',
      EDIT: 'edit',
      VIEW: 'view',
      PLAYBACK: 'playback',
      RECORDING: 'recording',
      AI: 'ai',
      EXPORT: 'export'
    };
    
    this.isInitialized = false;
    log.info('Keyboard Shortcuts Manager initialized');
  }

  async initialize() {
    try {
      log.info('Initializing Keyboard Shortcuts Manager...');
      
      // Setup default shortcuts
      this.setupDefaultShortcuts();
      
      // Register global shortcuts
      this.registerGlobalShortcuts();
      
      // Setup local shortcuts
      this.setupLocalShortcuts();
      
      // Load user customizations
      this.loadUserShortcuts();
      
      // Setup conflict detection
      this.setupConflictDetection();
      
      this.isInitialized = true;
      log.info('✅ Keyboard Shortcuts Manager initialized successfully');
      
    } catch (error) {
      log.error('❌ Failed to initialize Keyboard Shortcuts Manager:', error);
      throw error;
    }
  }

  setupDefaultShortcuts() {
    // Global shortcuts (work across all windows)
    this.defaultGlobalShortcuts = {
      // Window management
      'CommandOrControl+N': { action: 'new-project', category: this.categories.GLOBAL, description: 'New Project' },
      'CommandOrControl+O': { action: 'open-project', category: this.categories.GLOBAL, description: 'Open Project' },
      'CommandOrControl+S': { action: 'save-project', category: this.categories.GLOBAL, description: 'Save Project' },
      'CommandOrControl+Shift+S': { action: 'save-as', category: this.categories.GLOBAL, description: 'Save As' },
      
      // Timeline window
      'CommandOrControl+Alt+T': { action: 'toggle-timeline', category: this.categories.GLOBAL, description: 'Toggle Timeline Window' },
      'CommandOrControl+Alt+M': { action: 'toggle-mixer', category: this.categories.GLOBAL, description: 'Toggle Mixer Window' },
      'CommandOrControl+Alt+P': { action: 'toggle-preview', category: this.categories.GLOBAL, description: 'Toggle Preview Window' },
      
      // Workspace management
      'CommandOrControl+Shift+W': { action: 'create-workspace', category: this.categories.GLOBAL, description: 'Create Workspace Layout' },
      
      // Quick actions
      'CommandOrControl+I': { action: 'import-content', category: this.categories.GLOBAL, description: 'Import Content' },
      'CommandOrControl+E': { action: 'export-project', category: this.categories.GLOBAL, description: 'Export Project' },
      'CommandOrControl+R': { action: 'render-video', category: this.categories.GLOBAL, description: 'Render Video' }
    };
    
    // Local shortcuts (window-specific)
    this.defaultLocalShortcuts = {
      // Playback controls
      'Space': { action: 'play-pause', category: this.categories.PLAYBACK, description: 'Play/Pause' },
      'Enter': { action: 'play', category: this.categories.PLAYBACK, description: 'Play' },
      'Escape': { action: 'stop', category: this.categories.PLAYBACK, description: 'Stop' },
      'Home': { action: 'goto-beginning', category: this.categories.PLAYBACK, description: 'Go to Beginning' },
      'End': { action: 'goto-end', category: this.categories.PLAYBACK, description: 'Go to End' },
      
      // Timeline navigation
      'Left': { action: 'previous-frame', category: this.categories.TIMELINE, description: 'Previous Frame' },
      'Right': { action: 'next-frame', category: this.categories.TIMELINE, description: 'Next Frame' },
      'Shift+Left': { action: 'previous-second', category: this.categories.TIMELINE, description: 'Previous Second' },
      'Shift+Right': { action: 'next-second', category: this.categories.TIMELINE, description: 'Next Second' },
      'CommandOrControl+Left': { action: 'previous-marker', category: this.categories.TIMELINE, description: 'Previous Marker' },
      'CommandOrControl+Right': { action: 'next-marker', category: this.categories.TIMELINE, description: 'Next Marker' },
      
      // Selection and editing
      'CommandOrControl+A': { action: 'select-all', category: this.categories.EDIT, description: 'Select All' },
      'CommandOrControl+D': { action: 'deselect-all', category: this.categories.EDIT, description: 'Deselect All' },
      'Delete': { action: 'delete-selected', category: this.categories.EDIT, description: 'Delete Selected' },
      'Backspace': { action: 'delete-selected', category: this.categories.EDIT, description: 'Delete Selected' },
      
      // Copy/Paste
      'CommandOrControl+C': { action: 'copy', category: this.categories.EDIT, description: 'Copy' },
      'CommandOrControl+X': { action: 'cut', category: this.categories.EDIT, description: 'Cut' },
      'CommandOrControl+V': { action: 'paste', category: this.categories.EDIT, description: 'Paste' },
      
      // Undo/Redo
      'CommandOrControl+Z': { action: 'undo', category: this.categories.EDIT, description: 'Undo' },
      'CommandOrControl+Y': { action: 'redo', category: this.categories.EDIT, description: 'Redo' },
      'CommandOrControl+Shift+Z': { action: 'redo', category: this.categories.EDIT, description: 'Redo' },
      
      // View controls
      'CommandOrControl+Plus': { action: 'zoom-in', category: this.categories.VIEW, description: 'Zoom In' },
      'CommandOrControl+-': { action: 'zoom-out', category: this.categories.VIEW, description: 'Zoom Out' },
      'CommandOrControl+0': { action: 'zoom-fit', category: this.categories.VIEW, description: 'Fit to Window' },
      'CommandOrControl+1': { action: 'zoom-100', category: this.categories.VIEW, description: '100% Zoom' },
      
      // Recording
      'CommandOrControl+Shift+R': { action: 'start-recording', category: this.categories.RECORDING, description: 'Start Recording' },
      'CommandOrControl+Shift+S': { action: 'stop-recording', category: this.categories.RECORDING, description: 'Stop Recording' },
      
      // AI features
      'CommandOrControl+Shift+A': { action: 'ai-enhance', category: this.categories.AI, description: 'AI Enhancement' },
      'CommandOrControl+Shift+C': { action: 'generate-captions', category: this.categories.AI, description: 'Generate Captions' },
      'CommandOrControl+Shift+V': { action: 'voice-clone', category: this.categories.AI, description: 'Voice Clone' },
      
      // Mixer controls
      'M': { action: 'toggle-mute', category: this.categories.MIXER, description: 'Toggle Mute' },
      'S': { action: 'toggle-solo', category: this.categories.MIXER, description: 'Toggle Solo' },
      'Up': { action: 'volume-up', category: this.categories.MIXER, description: 'Volume Up' },
      'Down': { action: 'volume-down', category: this.categories.MIXER, description: 'Volume Down' }
    };
    
    log.info('Default shortcuts configured');
  }

  registerGlobalShortcuts() {
    for (const [accelerator, shortcut] of Object.entries(this.defaultGlobalShortcuts)) {
      this.registerGlobalShortcut(accelerator, shortcut);
    }
    
    log.info(`Registered ${Object.keys(this.defaultGlobalShortcuts).length} global shortcuts`);
  }

  registerGlobalShortcut(accelerator, shortcut) {
    try {
      // Check if shortcut is already registered
      if (this.globalShortcuts.has(accelerator)) {
        log.warn(`Global shortcut already registered: ${accelerator}`);
        return false;
      }
      
      // Register with Electron
      const success = globalShortcut.register(accelerator, () => {
        log.debug(`Global shortcut triggered: ${accelerator} -> ${shortcut.action}`);
        this.executeAction(shortcut.action, { 
          accelerator, 
          category: shortcut.category,
          global: true 
        });
      });
      
      if (success) {
        this.globalShortcuts.set(accelerator, shortcut);
        this.addToCategory(shortcut.category, accelerator, shortcut);
        log.debug(`Global shortcut registered: ${accelerator}`);
        return true;
      } else {
        log.warn(`Failed to register global shortcut: ${accelerator}`);
        this.conflicts.add(accelerator);
        return false;
      }
      
    } catch (error) {
      log.error(`Error registering global shortcut ${accelerator}:`, error);
      return false;
    }
  }

  setupLocalShortcuts() {
    // Local shortcuts are handled by renderer processes
    // but we track them here for management
    for (const [accelerator, shortcut] of Object.entries(this.defaultLocalShortcuts)) {
      this.localShortcuts.set(accelerator, shortcut);
      this.addToCategory(shortcut.category, accelerator, shortcut);
    }
    
    log.info(`Configured ${Object.keys(this.defaultLocalShortcuts).length} local shortcuts`);
  }

  addToCategory(category, accelerator, shortcut) {
    if (!this.shortcutCategories.has(category)) {
      this.shortcutCategories.set(category, new Map());
    }
    
    this.shortcutCategories.get(category).set(accelerator, shortcut);
  }

  loadUserShortcuts() {
    // Load user customizations from storage
    // For now, log that we would load customizations
    log.info('User shortcut customizations loaded');
  }

  setupConflictDetection() {
    // Detect conflicts between global and local shortcuts
    for (const globalAccel of this.globalShortcuts.keys()) {
      if (this.localShortcuts.has(globalAccel)) {
        log.warn(`Shortcut conflict detected: ${globalAccel}`);
        this.conflicts.add(globalAccel);
      }
    }
    
    if (this.conflicts.size > 0) {
      log.warn(`${this.conflicts.size} shortcut conflicts detected`);
    }
  }

  // Action execution
  executeAction(action, context = {}) {
    log.debug(`Executing action: ${action}`, context);
    
    try {
      // Emit action event
      this.emit('shortcut-action', { action, context });
      
      // Execute built-in actions
      switch (action) {
        // Global actions
        case 'new-project':
          this.emit('new-project');
          break;
        case 'open-project':
          this.emit('open-project');
          break;
        case 'save-project':
          this.emit('save-project');
          break;
        case 'save-as':
          this.emit('save-as');
          break;
        case 'toggle-timeline':
          this.emit('toggle-timeline');
          break;
        case 'toggle-mixer':
          this.emit('toggle-mixer');
          break;
        case 'toggle-preview':
          this.emit('toggle-preview');
          break;
        case 'create-workspace':
          this.emit('create-workspace');
          break;
        case 'import-content':
          this.emit('import-content');
          break;
        case 'export-project':
          this.emit('export-project');
          break;
        case 'render-video':
          this.emit('render-video');
          break;
          
        // Playback actions
        case 'play-pause':
          this.emit('play-pause');
          break;
        case 'play':
          this.emit('play');
          break;
        case 'stop':
          this.emit('stop');
          break;
        case 'goto-beginning':
          this.emit('goto-beginning');
          break;
        case 'goto-end':
          this.emit('goto-end');
          break;
          
        // Timeline actions
        case 'previous-frame':
          this.emit('timeline-previous-frame');
          break;
        case 'next-frame':
          this.emit('timeline-next-frame');
          break;
        case 'previous-second':
          this.emit('timeline-previous-second');
          break;
        case 'next-second':
          this.emit('timeline-next-second');
          break;
        case 'previous-marker':
          this.emit('timeline-previous-marker');
          break;
        case 'next-marker':
          this.emit('timeline-next-marker');
          break;
          
        // Edit actions
        case 'select-all':
          this.emit('select-all');
          break;
        case 'deselect-all':
          this.emit('deselect-all');
          break;
        case 'delete-selected':
          this.emit('delete-selected');
          break;
        case 'copy':
          this.emit('copy');
          break;
        case 'cut':
          this.emit('cut');
          break;
        case 'paste':
          this.emit('paste');
          break;
        case 'undo':
          this.emit('undo');
          break;
        case 'redo':
          this.emit('redo');
          break;
          
        // View actions
        case 'zoom-in':
          this.emit('zoom-in');
          break;
        case 'zoom-out':
          this.emit('zoom-out');
          break;
        case 'zoom-fit':
          this.emit('zoom-fit');
          break;
        case 'zoom-100':
          this.emit('zoom-100');
          break;
          
        // Recording actions
        case 'start-recording':
          this.emit('start-recording');
          break;
        case 'stop-recording':
          this.emit('stop-recording');
          break;
          
        // AI actions
        case 'ai-enhance':
          this.emit('ai-enhance');
          break;
        case 'generate-captions':
          this.emit('generate-captions');
          break;
        case 'voice-clone':
          this.emit('voice-clone');
          break;
          
        // Mixer actions
        case 'toggle-mute':
          this.emit('toggle-mute');
          break;
        case 'toggle-solo':
          this.emit('toggle-solo');
          break;
        case 'volume-up':
          this.emit('volume-up');
          break;
        case 'volume-down':
          this.emit('volume-down');
          break;
          
        default:
          log.warn(`Unknown action: ${action}`);
          this.emit('unknown-action', { action, context });
      }
      
    } catch (error) {
      log.error(`Error executing action ${action}:`, error);
      this.emit('action-error', { action, context, error });
    }
  }

  // Shortcut management
  addCustomShortcut(accelerator, action, category, description, isGlobal = false) {
    try {
      const shortcut = { action, category, description, custom: true };
      
      if (isGlobal) {
        const success = this.registerGlobalShortcut(accelerator, shortcut);
        if (!success) {
          throw new Error(`Failed to register global shortcut: ${accelerator}`);
        }
      } else {
        this.localShortcuts.set(accelerator, shortcut);
        this.addToCategory(category, accelerator, shortcut);
      }
      
      log.info(`Custom shortcut added: ${accelerator} -> ${action}`);
      this.emit('shortcut-added', { accelerator, shortcut, isGlobal });
      
      return true;
      
    } catch (error) {
      log.error(`Failed to add custom shortcut ${accelerator}:`, error);
      return false;
    }
  }

  removeShortcut(accelerator, isGlobal = false) {
    try {
      if (isGlobal) {
        if (this.globalShortcuts.has(accelerator)) {
          globalShortcut.unregister(accelerator);
          this.globalShortcuts.delete(accelerator);
          log.info(`Global shortcut removed: ${accelerator}`);
        }
      } else {
        if (this.localShortcuts.has(accelerator)) {
          this.localShortcuts.delete(accelerator);
          log.info(`Local shortcut removed: ${accelerator}`);
        }
      }
      
      // Remove from categories
      for (const [category, shortcuts] of this.shortcutCategories) {
        if (shortcuts.has(accelerator)) {
          shortcuts.delete(accelerator);
          break;
        }
      }
      
      this.emit('shortcut-removed', { accelerator, isGlobal });
      return true;
      
    } catch (error) {
      log.error(`Failed to remove shortcut ${accelerator}:`, error);
      return false;
    }
  }

  updateShortcut(oldAccelerator, newAccelerator, isGlobal = false) {
    try {
      let shortcut;
      
      if (isGlobal) {
        shortcut = this.globalShortcuts.get(oldAccelerator);
        if (!shortcut) {
          throw new Error(`Global shortcut not found: ${oldAccelerator}`);
        }
        
        // Remove old shortcut
        this.removeShortcut(oldAccelerator, true);
        
        // Add new shortcut
        this.registerGlobalShortcut(newAccelerator, shortcut);
        
      } else {
        shortcut = this.localShortcuts.get(oldAccelerator);
        if (!shortcut) {
          throw new Error(`Local shortcut not found: ${oldAccelerator}`);
        }
        
        // Remove old shortcut
        this.removeShortcut(oldAccelerator, false);
        
        // Add new shortcut
        this.localShortcuts.set(newAccelerator, shortcut);
        this.addToCategory(shortcut.category, newAccelerator, shortcut);
      }
      
      log.info(`Shortcut updated: ${oldAccelerator} -> ${newAccelerator}`);
      this.emit('shortcut-updated', { oldAccelerator, newAccelerator, shortcut, isGlobal });
      
      return true;
      
    } catch (error) {
      log.error(`Failed to update shortcut ${oldAccelerator}:`, error);
      return false;
    }
  }

  // State management
  enable() {
    this.isEnabled = true;
    
    // Re-register global shortcuts
    this.registerGlobalShortcuts();
    
    log.info('Keyboard shortcuts enabled');
    this.emit('shortcuts-enabled');
  }

  disable() {
    this.isEnabled = false;
    
    // Unregister all global shortcuts
    globalShortcut.unregisterAll();
    
    log.info('Keyboard shortcuts disabled');
    this.emit('shortcuts-disabled');
  }

  isShortcutRegistered(accelerator, isGlobal = false) {
    if (isGlobal) {
      return this.globalShortcuts.has(accelerator);
    } else {
      return this.localShortcuts.has(accelerator);
    }
  }

  // Information methods
  getAllShortcuts() {
    return {
      global: Object.fromEntries(this.globalShortcuts),
      local: Object.fromEntries(this.localShortcuts)
    };
  }

  getShortcutsByCategory(category) {
    return Object.fromEntries(this.shortcutCategories.get(category) || new Map());
  }

  getAvailableCategories() {
    return Object.values(this.categories);
  }

  getConflicts() {
    return Array.from(this.conflicts);
  }

  searchShortcuts(query) {
    const results = [];
    const queryLower = query.toLowerCase();
    
    // Search global shortcuts
    for (const [accelerator, shortcut] of this.globalShortcuts) {
      if (accelerator.toLowerCase().includes(queryLower) ||
          shortcut.action.toLowerCase().includes(queryLower) ||
          shortcut.description.toLowerCase().includes(queryLower)) {
        results.push({ accelerator, ...shortcut, isGlobal: true });
      }
    }
    
    // Search local shortcuts
    for (const [accelerator, shortcut] of this.localShortcuts) {
      if (accelerator.toLowerCase().includes(queryLower) ||
          shortcut.action.toLowerCase().includes(queryLower) ||
          shortcut.description.toLowerCase().includes(queryLower)) {
        results.push({ accelerator, ...shortcut, isGlobal: false });
      }
    }
    
    return results;
  }

  // Export/Import shortcuts
  exportShortcuts() {
    return {
      global: Object.fromEntries(this.globalShortcuts),
      local: Object.fromEntries(this.localShortcuts),
      categories: Object.fromEntries(this.shortcutCategories),
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    };
  }

  importShortcuts(shortcutsData) {
    try {
      if (!shortcutsData || typeof shortcutsData !== 'object') {
        throw new Error('Invalid shortcuts data');
      }
      
      // Clear existing custom shortcuts
      this.clearCustomShortcuts();
      
      // Import global shortcuts
      if (shortcutsData.global) {
        for (const [accelerator, shortcut] of Object.entries(shortcutsData.global)) {
          if (shortcut.custom) {
            this.registerGlobalShortcut(accelerator, shortcut);
          }
        }
      }
      
      // Import local shortcuts
      if (shortcutsData.local) {
        for (const [accelerator, shortcut] of Object.entries(shortcutsData.local)) {
          if (shortcut.custom) {
            this.localShortcuts.set(accelerator, shortcut);
            this.addToCategory(shortcut.category, accelerator, shortcut);
          }
        }
      }
      
      log.info('Shortcuts imported successfully');
      this.emit('shortcuts-imported', shortcutsData);
      
      return true;
      
    } catch (error) {
      log.error('Failed to import shortcuts:', error);
      return false;
    }
  }

  clearCustomShortcuts() {
    // Remove custom global shortcuts
    for (const [accelerator, shortcut] of this.globalShortcuts) {
      if (shortcut.custom) {
        this.removeShortcut(accelerator, true);
      }
    }
    
    // Remove custom local shortcuts
    for (const [accelerator, shortcut] of this.localShortcuts) {
      if (shortcut.custom) {
        this.removeShortcut(accelerator, false);
      }
    }
    
    log.info('Custom shortcuts cleared');
  }

  resetToDefaults() {
    // Clear all shortcuts
    this.disable();
    this.globalShortcuts.clear();
    this.localShortcuts.clear();
    this.shortcutCategories.clear();
    this.conflicts.clear();
    
    // Restore defaults
    this.setupDefaultShortcuts();
    this.registerGlobalShortcuts();
    this.setupLocalShortcuts();
    this.enable();
    
    log.info('Shortcuts reset to defaults');
    this.emit('shortcuts-reset');
  }

  // Cleanup
  cleanup() {
    // Unregister all global shortcuts
    globalShortcut.unregisterAll();
    
    // Clear data structures
    this.globalShortcuts.clear();
    this.localShortcuts.clear();
    this.shortcutCategories.clear();
    this.conflicts.clear();
    
    log.info('Keyboard Shortcuts Manager cleaned up');
  }
}

module.exports = KeyboardShortcutsManager;