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
  
  // Store operations  
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value),
    delete: (key) => ipcRenderer.invoke('store-delete', key)
  },
  
  // AI processing
  processAIContent: (contentPath, options) => ipcRenderer.invoke('process-ai-content', contentPath, options),
  
  // System info
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Menu listeners
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-new-project', callback);
    ipcRenderer.on('menu-save-project', callback);
    ipcRenderer.on('load-project', callback);
    ipcRenderer.on('import-content', callback);
    ipcRenderer.on('export-project', callback);
    ipcRenderer.on('toggle-ai-panel', callback);
    ipcRenderer.on('toggle-protection-panel', callback);
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