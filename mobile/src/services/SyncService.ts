/**
 * Sync Service - Advanced data synchronization service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

import { offlineStorageService, SyncQueueItem, OfflineContent } from './OfflineStorageService';
import { mobileAPIService } from './MobileAPIService';

export interface SyncStatus {
  isOnline: boolean;
  isSyncing: boolean;
  lastSync: number;
  pendingItems: number;
  conflictItems: number;
  errorItems: number;
  progress: number;
}

export interface SyncConflict {
  id: string;
  type: 'data' | 'content' | 'metadata';
  localVersion: any;
  remoteVersion: any;
  timestamp: number;
  resolution?: 'local' | 'remote' | 'merge' | 'manual';
}

export interface SyncPolicy {
  mode: 'auto' | 'manual' | 'wifi-only' | 'scheduled';
  interval: number; // minutes
  retryAttempts: number;
  conflictResolution: 'local-wins' | 'remote-wins' | 'newest-wins' | 'manual';
  batchSize: number;
  priorityOrder: string[];
}

export interface SyncEvent {
  type: 'started' | 'progress' | 'completed' | 'failed' | 'conflict' | 'paused';
  data?: any;
  timestamp: number;
  error?: string;
}

export interface DataDelta {
  operation: 'create' | 'update' | 'delete';
  table: string;
  id: string;
  data?: any;
  timestamp: number;
  hash: string;
}

export interface SyncCheckpoint {
  timestamp: number;
  lastSyncedId: string;
  version: number;
  conflicts: SyncConflict[];
  metadata: Record<string, any>;
}

export class SyncService {
  private syncStatus: SyncStatus;
  private syncPolicy: SyncPolicy;
  private eventListeners: Map<string, Function[]>;
  private syncTimer?: NodeJS.Timeout;
  private isInitialized: boolean = false;
  private conflictQueue: SyncConflict[] = [];
  private syncLock: boolean = false;

  constructor() {
    this.syncStatus = {
      isOnline: navigator.onLine,
      isSyncing: false,
      lastSync: 0,
      pendingItems: 0,
      conflictItems: 0,
      errorItems: 0,
      progress: 0,
    };

    this.syncPolicy = {
      mode: 'auto',
      interval: 5, // 5 minutes
      retryAttempts: 3,
      conflictResolution: 'newest-wins',
      batchSize: 50,
      priorityOrder: ['critical', 'high', 'normal', 'low'],
    };

    this.eventListeners = new Map();
    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    // Monitor network status
    window.addEventListener('online', () => {
      this.syncStatus.isOnline = true;
      this.emitEvent('network-online');
      if (this.syncPolicy.mode === 'auto') {
        this.performSync();
      }
    });

    window.addEventListener('offline', () => {
      this.syncStatus.isOnline = false;
      this.pauseSync();
      this.emitEvent('network-offline');
    });

    // Load previous sync state
    await this.loadSyncState();
    
    // Start automatic sync if enabled
    if (this.syncPolicy.mode === 'auto') {
      this.startAutoSync();
    }

    this.isInitialized = true;
  }

  // Public API Methods
  async startSync(): Promise<void> {
    if (!this.isInitialized) {
      await this.initializeService();
    }

    if (this.syncLock) {
      console.warn('Sync already in progress');
      return;
    }

    await this.performSync();
  }

  async pauseSync(): Promise<void> {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = undefined;
    }
    
    this.syncStatus.isSyncing = false;
    this.emitEvent('paused');
  }

  async resumeSync(): Promise<void> {
    if (this.syncPolicy.mode === 'auto') {
      this.startAutoSync();
    }
  }

  getSyncStatus(): SyncStatus {
    return { ...this.syncStatus };
  }

  setSyncPolicy(policy: Partial<SyncPolicy>): void {
    this.syncPolicy = { ...this.syncPolicy, ...policy };
    
    // Restart auto sync if mode changed
    if (this.syncTimer) {
      this.pauseSync();
      if (this.syncPolicy.mode === 'auto') {
        this.startAutoSync();
      }
    }
  }

  // Event Management
  addEventListener(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  removeEventListener(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  // Conflict Management
  getConflicts(): SyncConflict[] {
    return [...this.conflictQueue];
  }

  async resolveConflict(conflictId: string, resolution: 'local' | 'remote' | 'merge'): Promise<boolean> {
    const conflict = this.conflictQueue.find(c => c.id === conflictId);
    if (!conflict) return false;

    try {
      conflict.resolution = resolution;
      
      switch (resolution) {
        case 'local':
          await this.applyLocalVersion(conflict);
          break;
        case 'remote':
          await this.applyRemoteVersion(conflict);
          break;
        case 'merge':
          await this.mergeVersions(conflict);
          break;
      }

      // Remove from conflict queue
      this.conflictQueue = this.conflictQueue.filter(c => c.id !== conflictId);
      this.syncStatus.conflictItems = this.conflictQueue.length;
      
      this.emitEvent('conflict-resolved', { conflictId, resolution });
      return true;
    } catch (error) {
      console.error('Error resolving conflict:', error);
      return false;
    }
  }

  // Data Operations
  async queueDataChange(
    operation: 'create' | 'update' | 'delete',
    table: string,
    data: any,
    priority: number = 1
  ): Promise<string> {
    const changeId = await offlineStorageService.addToSyncQueue({
      operation,
      table,
      data,
      retries: 0,
      priority,
    });

    this.updatePendingCount();
    
    // Trigger immediate sync for high priority items
    if (priority >= 3 && this.syncStatus.isOnline && this.syncPolicy.mode === 'auto') {
      setTimeout(() => this.performSync(), 1000);
    }

    return changeId;
  }

  async getDataDeltas(lastSync: number): Promise<DataDelta[]> {
    const syncQueue = await offlineStorageService.getSyncQueue();
    
    return syncQueue
      .filter(item => item.timestamp > lastSync)
      .map(item => ({
        operation: item.operation,
        table: item.table,
        id: item.id,
        data: item.data,
        timestamp: item.timestamp,
        hash: this.generateHash(item),
      }));
  }

  // Content Synchronization
  async syncContent(): Promise<void> {
    const offlineContent = await offlineStorageService.getAllOfflineContent();
    const pendingContent = offlineContent.filter(c => c.syncStatus === 'pending');

    for (const content of pendingContent) {
      try {
        await this.syncSingleContent(content);
      } catch (error) {
        console.error(`Failed to sync content ${content.contentId}:`, error);
        await this.markContentError(content.contentId);
      }
    }
  }

  async downloadContent(contentId: string, url: string): Promise<boolean> {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const blob = await response.blob();
      const localPath = await this.saveContentLocally(contentId, blob);

      const offlineContent: OfflineContent = {
        contentId,
        type: this.detectContentType(url),
        localPath,
        originalUrl: url,
        size: blob.size,
        downloadedAt: Date.now(),
        lastAccessed: Date.now(),
        syncStatus: 'synced',
        metadata: {
          mimeType: blob.type,
          downloadedSize: blob.size,
        },
      };

      await offlineStorageService.storeContent(offlineContent);
      return true;
    } catch (error) {
      console.error('Content download failed:', error);
      return false;
    }
  }

  // Analytics Synchronization
  async syncAnalytics(): Promise<void> {
    const pendingAnalytics = await offlineStorageService.getPendingAnalytics();
    if (pendingAnalytics.length === 0) return;

    try {
      const batchSize = Math.min(this.syncPolicy.batchSize, pendingAnalytics.length);
      const batch = pendingAnalytics.slice(0, batchSize);

      const response = await mobileAPIService.makeRequest('/analytics/batch', {
        method: 'POST',
        body: JSON.stringify({ events: batch }),
      });

      if (response.status === 200) {
        const syncedIds = batch.map(item => item.id);
        await offlineStorageService.markAnalyticsSynced(syncedIds);
      }
    } catch (error) {
      console.error('Analytics sync failed:', error);
    }
  }

  // User Data Synchronization
  async syncUserData(userId: string): Promise<void> {
    try {
      // Get local user data
      const localData = await offlineStorageService.getUserData(userId);
      
      // Get remote user data
      const remoteResponse = await mobileAPIService.makeRequest(`/user/${userId}/sync-data`);
      const remoteData = remoteResponse.data;

      // Check for conflicts
      if (this.hasDataConflict(localData, remoteData)) {
        await this.handleUserDataConflict(userId, localData, remoteData);
      } else {
        // Merge and update
        const mergedData = this.mergeUserData(localData, remoteData);
        await offlineStorageService.storeUserData(userId, mergedData);
        
        // Push changes to server
        await mobileAPIService.makeRequest(`/user/${userId}/sync-data`, {
          method: 'PUT',
          body: JSON.stringify(mergedData),
        });
      }
    } catch (error) {
      console.error('User data sync failed:', error);
    }
  }

  // Private Methods
  private async performSync(): Promise<void> {
    if (this.syncLock || !this.syncStatus.isOnline) return;

    this.syncLock = true;
    this.syncStatus.isSyncing = true;
    this.syncStatus.progress = 0;
    
    this.emitEvent('started');

    try {
      // Phase 1: Sync critical data changes
      await this.syncDataChanges();
      this.syncStatus.progress = 25;
      this.emitEvent('progress', { phase: 'data', progress: 25 });

      // Phase 2: Sync content
      await this.syncContent();
      this.syncStatus.progress = 50;
      this.emitEvent('progress', { phase: 'content', progress: 50 });

      // Phase 3: Sync analytics
      await this.syncAnalytics();
      this.syncStatus.progress = 75;
      this.emitEvent('progress', { phase: 'analytics', progress: 75 });

      // Phase 4: Sync user data
      const userData = await offlineStorageService.retrieveFromDB('userData', 'current_user');
      if (userData) {
        await this.syncUserData(userData.userId);
      }
      
      this.syncStatus.progress = 100;
      this.syncStatus.lastSync = Date.now();
      
      await this.saveSyncState();
      this.emitEvent('completed');

    } catch (error) {
      console.error('Sync failed:', error);
      this.emitEvent('failed', { error: error.message });
    } finally {
      this.syncStatus.isSyncing = false;
      this.syncStatus.progress = 0;
      this.syncLock = false;
      await this.updatePendingCount();
    }
  }

  private async syncDataChanges(): Promise<void> {
    const syncQueue = await offlineStorageService.getSyncQueue();
    const sortedQueue = this.sortByPriority(syncQueue);

    for (const item of sortedQueue) {
      try {
        await this.syncSingleItem(item);
        await offlineStorageService.removeSyncItem(item.id);
      } catch (error) {
        console.error(`Failed to sync item ${item.id}:`, error);
        
        if (item.retries < this.syncPolicy.retryAttempts) {
          // Increment retry count
          item.retries++;
          await offlineStorageService.addToSyncQueue(item);
        } else {
          // Mark as error after max retries
          this.syncStatus.errorItems++;
        }
      }
    }
  }

  private async syncSingleItem(item: SyncQueueItem): Promise<void> {
    const endpoint = this.getEndpointForTable(item.table);
    
    switch (item.operation) {
      case 'create':
        await mobileAPIService.makeRequest(endpoint, {
          method: 'POST',
          body: JSON.stringify(item.data),
        });
        break;
        
      case 'update':
        await mobileAPIService.makeRequest(`${endpoint}/${item.data.id}`, {
          method: 'PUT',
          body: JSON.stringify(item.data),
        });
        break;
        
      case 'delete':
        await mobileAPIService.makeRequest(`${endpoint}/${item.data.id}`, {
          method: 'DELETE',
        });
        break;
    }
  }

  private async syncSingleContent(content: OfflineContent): Promise<void> {
    // Check if content exists on server
    const response = await mobileAPIService.makeRequest(`/content/${content.contentId}/status`);
    
    if (response.status === 404) {
      // Content doesn't exist on server, upload it
      await this.uploadContentToServer(content);
    } else {
      // Content exists, check for updates
      const remoteData = response.data;
      if (this.needsContentUpdate(content, remoteData)) {
        await this.updateContentOnServer(content, remoteData);
      }
    }
    
    // Mark as synced
    content.syncStatus = 'synced';
    await offlineStorageService.storeContent(content);
  }

  private async uploadContentToServer(content: OfflineContent): Promise<void> {
    // Read local file
    const fileBlob = await this.readLocalFile(content.localPath);
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fileBlob);
    formData.append('metadata', JSON.stringify(content.metadata));
    
    // Upload to server
    await mobileAPIService.makeRequest('/content/upload', {
      method: 'POST',
      body: formData,
    });
  }

  private async updateContentOnServer(content: OfflineContent, remoteData: any): Promise<void> {
    // Compare versions and update if needed
    const updateData = {
      metadata: content.metadata,
      lastModified: content.lastAccessed,
    };
    
    await mobileAPIService.makeRequest(`/content/${content.contentId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  private async handleUserDataConflict(userId: string, localData: any, remoteData: any): Promise<void> {
    const conflict: SyncConflict = {
      id: `user_data_${userId}_${Date.now()}`,
      type: 'data',
      localVersion: localData,
      remoteVersion: remoteData,
      timestamp: Date.now(),
    };

    if (this.syncPolicy.conflictResolution === 'manual') {
      this.conflictQueue.push(conflict);
      this.syncStatus.conflictItems++;
      this.emitEvent('conflict', conflict);
    } else {
      // Auto-resolve based on policy
      await this.resolveConflict(conflict.id, this.getAutoResolution(conflict));
    }
  }

  private getAutoResolution(conflict: SyncConflict): 'local' | 'remote' | 'merge' {
    switch (this.syncPolicy.conflictResolution) {
      case 'local-wins':
        return 'local';
      case 'remote-wins':
        return 'remote';
      case 'newest-wins':
        return conflict.localVersion.timestamp > conflict.remoteVersion.timestamp ? 'local' : 'remote';
      default:
        return 'merge';
    }
  }

  private async applyLocalVersion(conflict: SyncConflict): Promise<void> {
    // Upload local version to server
    await mobileAPIService.makeRequest('/sync/resolve-conflict', {
      method: 'POST',
      body: JSON.stringify({
        conflictId: conflict.id,
        resolution: 'local',
        data: conflict.localVersion,
      }),
    });
  }

  private async applyRemoteVersion(conflict: SyncConflict): Promise<void> {
    // Save remote version locally
    await offlineStorageService.store(conflict.id, conflict.remoteVersion);
  }

  private async mergeVersions(conflict: SyncConflict): Promise<void> {
    const merged = this.performMerge(conflict.localVersion, conflict.remoteVersion);
    
    // Save merged version locally
    await offlineStorageService.store(conflict.id, merged);
    
    // Upload merged version to server
    await mobileAPIService.makeRequest('/sync/resolve-conflict', {
      method: 'POST',
      body: JSON.stringify({
        conflictId: conflict.id,
        resolution: 'merge',
        data: merged,
      }),
    });
  }

  private performMerge(local: any, remote: any): any {
    // Simple merge strategy - can be enhanced based on data structure
    return {
      ...remote,
      ...local,
      _mergedAt: Date.now(),
      _versions: {
        local: local.timestamp || Date.now(),
        remote: remote.timestamp || Date.now(),
      },
    };
  }

  private sortByPriority(items: SyncQueueItem[]): SyncQueueItem[] {
    const priorityMap = { critical: 4, high: 3, normal: 2, low: 1 };
    
    return items.sort((a, b) => {
      const aPriority = a.priority || 1;
      const bPriority = b.priority || 1;
      return bPriority - aPriority;
    });
  }

  private getEndpointForTable(table: string): string {
    const endpoints: Record<string, string> = {
      users: '/users',
      content: '/content',
      collaborations: '/collaborations',
      analytics: '/analytics',
      notifications: '/notifications',
    };
    
    return endpoints[table] || `/data/${table}`;
  }

  private hasDataConflict(local: any, remote: any): boolean {
    if (!local || !remote) return false;
    
    const localTime = local.lastModified || local.timestamp || 0;
    const remoteTime = remote.lastModified || remote.timestamp || 0;
    
    // Consider it a conflict if both have been modified recently
    return Math.abs(localTime - remoteTime) < 60000; // 1 minute threshold
  }

  private mergeUserData(local: any, remote: any): any {
    return {
      ...remote,
      ...local,
      preferences: { ...remote.preferences, ...local.preferences },
      settings: { ...remote.settings, ...local.settings },
      lastMerged: Date.now(),
    };
  }

  private needsContentUpdate(content: OfflineContent, remoteData: any): boolean {
    return content.lastAccessed > remoteData.lastModified;
  }

  private detectContentType(url: string): 'audio' | 'video' | 'image' | 'document' {
    const extension = url.split('.').pop()?.toLowerCase();
    
    if (['mp3', 'wav', 'flac', 'aac', 'm4a'].includes(extension || '')) return 'audio';
    if (['mp4', 'avi', 'mov', 'mkv', 'webm'].includes(extension || '')) return 'video';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension || '')) return 'image';
    
    return 'document';
  }

  private async saveContentLocally(contentId: string, blob: Blob): Promise<string> {
    // In a real implementation, this would use File System API or similar
    const path = `content/${contentId}`;
    
    // Store blob in IndexedDB for now
    await offlineStorageService.store(`content_blob_${contentId}`, blob);
    
    return path;
  }

  private async readLocalFile(path: string): Promise<Blob> {
    const contentId = path.split('/').pop();
    const blob = await offlineStorageService.retrieve(`content_blob_${contentId}`);
    return blob || new Blob();
  }

  private async markContentError(contentId: string): Promise<void> {
    const content = await offlineStorageService.getOfflineContent(contentId);
    if (content) {
      content.syncStatus = 'error';
      await offlineStorageService.storeContent(content);
    }
  }

  private generateHash(data: any): string {
    return btoa(JSON.stringify(data)).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  private emitEvent(type: string, data?: any): void {
    const event: SyncEvent = {
      type: type as any,
      data,
      timestamp: Date.now(),
    };

    const listeners = this.eventListeners.get(type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error('Event listener error:', error);
        }
      });
    }
  }

  private startAutoSync(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }
    
    this.syncTimer = setInterval(() => {
      if (this.syncStatus.isOnline && !this.syncStatus.isSyncing) {
        this.performSync();
      }
    }, this.syncPolicy.interval * 60 * 1000);
  }

  private async updatePendingCount(): Promise<void> {
    const syncQueue = await offlineStorageService.getSyncQueue();
    this.syncStatus.pendingItems = syncQueue.length;
  }

  private async loadSyncState(): Promise<void> {
    const state = await offlineStorageService.retrieve('sync_state');
    if (state) {
      this.syncStatus.lastSync = state.lastSync || 0;
      this.conflictQueue = state.conflicts || [];
      this.syncStatus.conflictItems = this.conflictQueue.length;
    }
  }

  private async saveSyncState(): Promise<void> {
    const state = {
      lastSync: this.syncStatus.lastSync,
      conflicts: this.conflictQueue,
      version: 1,
    };
    
    await offlineStorageService.store('sync_state', state);
  }
}

// Export singleton instance
export const syncService = new SyncService();