/**
 * @fileoverview State Manager - Application State Management
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/state_manager
 * @description Professional state management for desktop application with persistence and sync
 */

class StateManager {
  constructor() {
    this.state = new Map();
    this.subscribers = new Map();
    this.middleware = [];
    this.history = [];
    this.maxHistorySize = 50;
    this.persistentKeys = new Set();
    this.syncEnabled = false;
    
    this.initializeState();
    console.log('State Manager initialized');
  }

  /**
   * Initialize default application state
   */
  initializeState() {
    // Application state
    this.setState('app', {
      version: '1.0.0',
      initialized: false,
      loading: false,
      error: null,
      theme: 'dark',
      language: 'en',
      fullscreen: false,
      windowState: 'normal'
    });

    // User state
    this.setState('user', {
      authenticated: false,
      profile: null,
      permissions: [],
      preferences: {},
      sessionId: null
    });

    // Project state
    this.setState('project', {
      current: null,
      recent: [],
      saved: true,
      modified: false,
      autoSave: true,
      backupEnabled: true
    });

    // Content state
    this.setState('content', {
      library: [],
      selected: [],
      processing: new Map(),
      uploads: new Map(),
      exports: new Map(),
      filters: {
        type: 'all',
        date: 'all',
        status: 'all'
      }
    });

    // Studio state
    this.setState('studio', {
      workspace: 'default',
      timeline: {
        tracks: [],
        currentTime: 0,
        duration: 0,
        zoom: 1,
        playing: false
      },
      mixer: {
        channels: [],
        masterVolume: 0.8,
        muted: false
      },
      preview: {
        visible: true,
        fullscreen: false,
        quality: 'high'
      }
    });

    // AI state
    this.setState('ai', {
      analyzing: false,
      recommendations: [],
      processing: new Map(),
      models: {
        audio: 'advanced',
        video: 'advanced',
        image: 'advanced',
        text: 'advanced'
      },
      suggestions: []
    });

    // Security state
    this.setState('security', {
      encryption: {
        enabled: true,
        level: 'high'
      },
      backup: {
        enabled: true,
        frequency: 'hourly',
        location: 'cloud'
      },
      watermark: {
        enabled: true,
        type: 'invisible',
        strength: 'medium'
      }
    });

    // Collaboration state
    this.setState('collaboration', {
      connected: false,
      sessions: new Map(),
      activeUsers: [],
      permissions: {},
      sharing: {
        enabled: false,
        link: null,
        expiry: null
      }
    });

    // Analytics state
    this.setState('analytics', {
      performance: {
        cpu: 0,
        memory: 0,
        gpu: 0,
        disk: 0
      },
      content: {
        views: {},
        engagement: {},
        revenue: {}
      },
      trends: []
    });

    // Platform integration state
    this.setState('platforms', {
      connected: new Map(),
      scheduled: [],
      publishing: new Map(),
      analytics: new Map(),
      configurations: new Map()
    });

    // UI state
    this.setState('ui', {
      sidebar: {
        visible: true,
        width: 250,
        activeTab: 'library'
      },
      panels: {
        properties: { visible: true, width: 300 },
        timeline: { visible: true, height: 200 },
        mixer: { visible: true, height: 150 },
        preview: { visible: true }
      },
      modals: {
        active: null,
        stack: []
      },
      notifications: [],
      tooltips: {
        enabled: true,
        delay: 500
      }
    });

    // Mark persistent keys
    this.markAsPersistent([
      'user.preferences',
      'project.recent',
      'ui.sidebar',
      'ui.panels',
      'security',
      'platforms.configurations'
    ]);
  }

  /**
   * Get state value by key path
   */
  getState(keyPath) {
    if (!keyPath) return this.getFullState();
    
    const keys = keyPath.split('.');
    let current = this.state;
    
    for (const key of keys) {
      if (current instanceof Map) {
        current = current.get(key);
      } else if (current && typeof current === 'object') {
        current = current[key];
      } else {
        return undefined;
      }
      
      if (current === undefined) break;
    }
    
    return current;
  }

  /**
   * Set state value by key path
   */
  setState(keyPath, value, options = {}) {
    const { silent = false, persist = false, broadcast = true } = options;
    
    if (!keyPath) {
      throw new Error('State key path is required');
    }

    const oldValue = this.getState(keyPath);
    const keys = keyPath.split('.');
    const lastKey = keys.pop();
    
    // Navigate to parent object
    let current = this.state;
    for (const key of keys) {
      if (!current.has(key)) {
        current.set(key, new Map());
      }
      current = current.get(key);
    }
    
    // Apply middleware
    const processedValue = this.applyMiddleware('SET_STATE', {
      keyPath,
      oldValue,
      newValue: value,
      options
    });

    // Set the value
    if (current instanceof Map) {
      current.set(lastKey, processedValue.newValue);
    } else if (current && typeof current === 'object') {
      current[lastKey] = processedValue.newValue;
    } else {
      throw new Error(`Cannot set property on non-object: ${keyPath}`);
    }

    // Add to history
    this.addToHistory({
      type: 'SET_STATE',
      keyPath,
      oldValue,
      newValue: processedValue.newValue,
      timestamp: Date.now()
    });

    // Persist if marked as persistent or explicitly requested
    if (persist || this.isPersistent(keyPath)) {
      this.persistState(keyPath);
    }

    // Notify subscribers
    if (!silent) {
      this.notifySubscribers(keyPath, processedValue.newValue, oldValue);
    }

    // Broadcast to other instances if enabled
    if (broadcast && this.syncEnabled) {
      this.broadcastStateChange(keyPath, processedValue.newValue);
    }

    return processedValue.newValue;
  }

  /**
   * Update state with partial values
   */
  updateState(keyPath, partialValue, options = {}) {
    const currentValue = this.getState(keyPath);
    
    let newValue;
    if (currentValue instanceof Map) {
      newValue = new Map(currentValue);
      if (partialValue instanceof Map) {
        for (const [key, value] of partialValue) {
          newValue.set(key, value);
        }
      } else {
        Object.entries(partialValue).forEach(([key, value]) => {
          newValue.set(key, value);
        });
      }
    } else if (Array.isArray(currentValue)) {
      newValue = [...currentValue, ...partialValue];
    } else if (currentValue && typeof currentValue === 'object') {
      newValue = { ...currentValue, ...partialValue };
    } else {
      newValue = partialValue;
    }
    
    return this.setState(keyPath, newValue, options);
  }

  /**
   * Subscribe to state changes
   */
  subscribe(keyPath, callback, options = {}) {
    const { immediate = false, deep = false } = options;
    
    if (!this.subscribers.has(keyPath)) {
      this.subscribers.set(keyPath, new Set());
    }
    
    const subscription = {
      callback,
      options,
      id: crypto.randomUUID()
    };
    
    this.subscribers.get(keyPath).add(subscription);
    
    // Call immediately with current value if requested
    if (immediate) {
      const currentValue = this.getState(keyPath);
      callback(currentValue, undefined, keyPath);
    }
    
    // Return unsubscribe function
    return () => {
      const subscribers = this.subscribers.get(keyPath);
      if (subscribers) {
        subscribers.delete(subscription);
        if (subscribers.size === 0) {
          this.subscribers.delete(keyPath);
        }
      }
    };
  }

  /**
   * Unsubscribe from state changes
   */
  unsubscribe(keyPath, callbackOrId) {
    const subscribers = this.subscribers.get(keyPath);
    if (!subscribers) return false;
    
    if (typeof callbackOrId === 'string') {
      // Unsubscribe by ID
      for (const subscription of subscribers) {
        if (subscription.id === callbackOrId) {
          subscribers.delete(subscription);
          return true;
        }
      }
    } else {
      // Unsubscribe by callback function
      for (const subscription of subscribers) {
        if (subscription.callback === callbackOrId) {
          subscribers.delete(subscription);
          return true;
        }
      }
    }
    
    return false;
  }

  /**
   * Add middleware for state operations
   */
  addMiddleware(middleware) {
    if (typeof middleware !== 'function') {
      throw new Error('Middleware must be a function');
    }
    
    this.middleware.push(middleware);
    return () => {
      const index = this.middleware.indexOf(middleware);
      if (index > -1) {
        this.middleware.splice(index, 1);
      }
    };
  }

  /**
   * Apply middleware to state operations
   */
  applyMiddleware(action, payload) {
    let processedPayload = payload;
    
    for (const middleware of this.middleware) {
      try {
        const result = middleware(action, processedPayload);
        if (result !== undefined) {
          processedPayload = result;
        }
      } catch (error) {
        console.error('Middleware error:', error);
      }
    }
    
    return processedPayload;
  }

  /**
   * Mark keys as persistent
   */
  markAsPersistent(keyPaths) {
    if (Array.isArray(keyPaths)) {
      keyPaths.forEach(keyPath => this.persistentKeys.add(keyPath));
    } else {
      this.persistentKeys.add(keyPaths);
    }
  }

  /**
   * Check if key is persistent
   */
  isPersistent(keyPath) {
    return this.persistentKeys.has(keyPath) || 
           Array.from(this.persistentKeys).some(persistentKey => 
             keyPath.startsWith(persistentKey)
           );
  }

  /**
   * Persist state to localStorage
   */
  persistState(keyPath) {
    try {
      const value = this.getState(keyPath);
      const serialized = this.serializeValue(value);
      localStorage.setItem(`ainflue_state_${keyPath}`, serialized);
    } catch (error) {
      console.error('Failed to persist state:', error);
    }
  }

  /**
   * Load persisted state
   */
  loadPersistedState() {
    try {
      for (const keyPath of this.persistentKeys) {
        const stored = localStorage.getItem(`ainflue_state_${keyPath}`);
        if (stored) {
          const value = this.deserializeValue(stored);
          this.setState(keyPath, value, { silent: true, broadcast: false });
        }
      }
      console.log('Persisted state loaded');
    } catch (error) {
      console.error('Failed to load persisted state:', error);
    }
  }

  /**
   * Serialize value for storage
   */
  serializeValue(value) {
    if (value instanceof Map) {
      return JSON.stringify({
        __type: 'Map',
        data: Array.from(value.entries())
      });
    } else if (value instanceof Set) {
      return JSON.stringify({
        __type: 'Set',
        data: Array.from(value)
      });
    } else {
      return JSON.stringify(value);
    }
  }

  /**
   * Deserialize value from storage
   */
  deserializeValue(serialized) {
    const parsed = JSON.parse(serialized);
    
    if (parsed && typeof parsed === 'object' && parsed.__type) {
      switch (parsed.__type) {
        case 'Map':
          return new Map(parsed.data);
        case 'Set':
          return new Set(parsed.data);
        default:
          return parsed.data;
      }
    }
    
    return parsed;
  }

  /**
   * Notify subscribers of state changes
   */
  notifySubscribers(keyPath, newValue, oldValue) {
    // Notify exact path subscribers
    const subscribers = this.subscribers.get(keyPath);
    if (subscribers) {
      subscribers.forEach(subscription => {
        try {
          subscription.callback(newValue, oldValue, keyPath);
        } catch (error) {
          console.error('Subscriber callback error:', error);
        }
      });
    }

    // Notify parent path subscribers with deep option
    for (const [subscribedPath, pathSubscribers] of this.subscribers) {
      if (keyPath.startsWith(subscribedPath + '.')) {
        pathSubscribers.forEach(subscription => {
          if (subscription.options.deep) {
            try {
              const parentValue = this.getState(subscribedPath);
              subscription.callback(parentValue, undefined, subscribedPath);
            } catch (error) {
              console.error('Deep subscriber callback error:', error);
            }
          }
        });
      }
    }
  }

  /**
   * Add action to history
   */
  addToHistory(action) {
    this.history.push(action);
    
    // Keep history size manageable
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    }
  }

  /**
   * Get state history
   */
  getHistory() {
    return [...this.history];
  }

  /**
   * Undo last state change
   */
  undo() {
    const lastAction = this.history.pop();
    if (lastAction && lastAction.type === 'SET_STATE') {
      this.setState(lastAction.keyPath, lastAction.oldValue, { 
        silent: true, 
        broadcast: false 
      });
      return lastAction;
    }
    return null;
  }

  /**
   * Enable state synchronization
   */
  enableSync() {
    this.syncEnabled = true;
    console.log('State synchronization enabled');
  }

  /**
   * Disable state synchronization
   */
  disableSync() {
    this.syncEnabled = false;
    console.log('State synchronization disabled');
  }

  /**
   * Broadcast state change to other instances
   */
  broadcastStateChange(keyPath, value) {
    if (window.electronAPI) {
      window.electronAPI.broadcastStateChange({ keyPath, value });
    }
  }

  /**
   * Reset state to initial values
   */
  reset() {
    this.state.clear();
    this.subscribers.clear();
    this.history.length = 0;
    this.initializeState();
    console.log('State reset to initial values');
  }

  /**
   * Get full state object
   */
  getFullState() {
    const result = {};
    for (const [key, value] of this.state) {
      result[key] = this.convertMapToObject(value);
    }
    return result;
  }

  /**
   * Convert Map to plain object for serialization
   */
  convertMapToObject(value) {
    if (value instanceof Map) {
      const obj = {};
      for (const [k, v] of value) {
        obj[k] = this.convertMapToObject(v);
      }
      return obj;
    } else if (Array.isArray(value)) {
      return value.map(item => this.convertMapToObject(item));
    } else if (value && typeof value === 'object') {
      const obj = {};
      for (const [k, v] of Object.entries(value)) {
        obj[k] = this.convertMapToObject(v);
      }
      return obj;
    }
    return value;
  }

  /**
   * Debug method to log current state
   */
  debug() {
    console.group('State Manager Debug');
    console.log('Full State:', this.getFullState());
    console.log('Subscribers:', Object.fromEntries(this.subscribers));
    console.log('Persistent Keys:', Array.from(this.persistentKeys));
    console.log('History:', this.history);
    console.log('Sync Enabled:', this.syncEnabled);
    console.groupEnd();
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.subscribers.clear();
    this.middleware.length = 0;
    this.history.length = 0;
    this.persistentKeys.clear();
    console.log('State Manager cleaned up');
  }
}

// Create and export singleton instance
const stateManager = new StateManager();

// Load persisted state on initialization
stateManager.loadPersistedState();

// Export both class and instance
window.StateManager = StateManager;
window.stateManager = stateManager;

export { StateManager, stateManager };
export default stateManager;