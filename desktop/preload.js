/**
 * Ainflue Desktop - Preload Script
 * 
 * Secure bridge between main process and renderer process
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose secure API to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectFile: () => ipcRenderer.invoke('select-file'),
  saveFile: (data, defaultName) => ipcRenderer.invoke('save-file', data, defaultName),
  
  // Project management
  createNewProject: () => ipcRenderer.invoke('create-new-project'),
  getActiveProject: () => ipcRenderer.invoke('get-active-project'),
  saveProject: (projectData) => ipcRenderer.invoke('save-project', projectData),
  
  // Workspace and display management
  getPlatformInfo: () => ipcRenderer.invoke('get-platform-info'),
  getDisplays: () => ipcRenderer.invoke('get-displays'),
  createWorkspaceLayout: () => ipcRenderer.invoke('create-workspace-layout'),
  toggleTimelineWindow: () => ipcRenderer.invoke('toggle-timeline-window'),
  
  // Store operations  
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value),
    delete: (key) => ipcRenderer.invoke('store-delete', key)
  },
  
  // AI processing with professional options
  processAIContent: (contentPath, options) => ipcRenderer.invoke('process-ai-content', contentPath, options),
  
  // System info for performance monitoring
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Menu listeners for professional features
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-new-project', callback);
    ipcRenderer.on('menu-save-project', callback);
    ipcRenderer.on('menu-save-as', callback);
    ipcRenderer.on('menu-render-video', callback);
    ipcRenderer.on('load-project', callback);
    ipcRenderer.on('import-content', callback);
    ipcRenderer.on('export-project', callback);
    ipcRenderer.on('toggle-ai-panel', callback);
    ipcRenderer.on('toggle-protection-panel', callback);
    ipcRenderer.on('toggle-audio-enhancement', callback);
    ipcRenderer.on('auto-generate-captions', callback);
    ipcRenderer.on('voice-clone', callback);
    ipcRenderer.on('audio-cleanup', callback);
    ipcRenderer.on('open-preferences', callback);
    ipcRenderer.on('show-shortcuts', callback);
    ipcRenderer.on('displays-changed', callback);
    ipcRenderer.on('workspace-layout-created', callback);
    ipcRenderer.on('window-state-changed', callback);
  },
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Expose version info
contextBridge.exposeInMainWorld('appVersion', {
  node: process.versions.node,
  chrome: process.versions.chrome,
  electron: process.versions.electron
});