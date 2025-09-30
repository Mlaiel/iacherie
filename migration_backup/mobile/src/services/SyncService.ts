/**
 * Sync Service - Professional Data Synchronization Management
 * 
 * Enterprise-grade synchronization service with real-time capabilities,
 * conflict resolution, delta sync, batch processing, and intelligent queuing.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import {
  SyncConfiguration,
  SyncItem,
  ServiceResponse,
  ServiceError,
  ContentFingerprint
} from './types';
import {
  handleServiceError,
  formatServiceResponse,
  generateCorrelationId,
  calculateChecksum,
  retryWithBackoff,
  createSyncConfiguration
} from './utils';
import { SERVICE_ENDPOINTS, SYNC_INTERVALS, STORAGE_KEYS } from './constants';
import MobileAPIService from './MobileAPIService';
import OfflineStorageService from './OfflineStorageService';

/**
 * Professional synchronization service for content creators
 */
class SyncService {
  private static instance: SyncService;
  private config: SyncConfiguration;
  private apiService: MobileAPIService;
  private storageService: OfflineStorageService;
  private syncQueue: SyncItem[] = [];
  private conflictQueue: SyncItem[] = [];
  private isOnline = true;
  private syncInterval: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastSyncTimestamp = 0;
  private activeSyncs = new Set<string>();
  private syncCallbacks = new Map<string, Function>();

  private constructor(config: SyncConfiguration) {
    this.config = config;
    this.apiService = MobileAPIService.getInstance();
    this.storageService = OfflineStorageService.getInstance();
    this.initialize();
  }

  public static getInstance(config?: SyncConfiguration): SyncService {
    if (!SyncService.instance) {
      const defaultConfig = createSyncConfiguration(config);
      SyncService.instance = new SyncService(defaultConfig);
    }
    return SyncService.instance;
  }

  /**
   * Initialize the sync service
   */
  private async initialize(): Promise<void> {
    try {
      // Load pending sync queue from storage
      await this.loadSyncQueue();
      await this.loadConflictQueue();

      // Setup network monitoring
      this.setupNetworkMonitoring();

      // Start sync intervals if real-time is enabled
      if (this.config.enableRealTime) {
        this.startRealTimeSync();
      } else {
        this.startPeriodicSync();
      }

      // Start heartbeat
      this.startHeartbeat();

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'initialize');
      console.error('Failed to initialize sync service:', serviceError);
    }
  }

  /**
   * Add item to sync queue
   */
  public async addToSyncQueue(
    type: 'content' | 'metadata' | 'preferences' | 'analytics',
    action: 'create' | 'update' | 'delete',
    data: any,
    priority = 1
  ): Promise<ServiceResponse<string>> {
    try {
      const syncItem: SyncItem = {
        id: generateCorrelationId(),
        type,
        action,
        data,
        timestamp: Date.now(),
        checksum: calculateChecksum(JSON.stringify(data)),
        priority,
        retryCount: 0
      };

      this.syncQueue.push(syncItem);
      await this.saveSyncQueue();

      // Trigger immediate sync for high priority items
      if (priority >= 5 && this.isOnline) {
        this.processSync();
      }

      return formatServiceResponse(syncItem.id, false, {
        queuePosition: this.syncQueue.length,
        estimatedSync: this.getEstimatedSyncTime()
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'addToSyncQueue', { type, action });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Process sync queue
   */
  public async processSync(): Promise<ServiceResponse<{
    processed: number;
    succeeded: number;
    failed: number;
    conflicts: number;
  }>> {
    try {
      if (!this.isOnline || this.syncQueue.length === 0) {
        return formatServiceResponse({
          processed: 0,
          succeeded: 0,
          failed: 0,
          conflicts: 0
        });
      }

      // Sort queue by priority and timestamp
      this.syncQueue.sort((a, b) => {
        if (a.priority !== b.priority) {
          return b.priority - a.priority; // Higher priority first
        }
        return a.timestamp - b.timestamp; // Older first
      });

      const batchSize = this.config.batchSize;
      const batch = this.syncQueue.splice(0, batchSize);
      
      let processed = 0;
      let succeeded = 0;
      let failed = 0;
      let conflicts = 0;

      // Process batch
      for (const item of batch) {
        try {
          if (this.activeSyncs.has(item.id)) {
            continue; // Skip items already being processed
          }

          this.activeSyncs.add(item.id);
          processed++;

          const result = await this.syncItem(item);
          
          if (result.success) {
            succeeded++;
            // Execute callback if exists
            const callback = this.syncCallbacks.get(item.id);
            if (callback) {
              callback(result);
              this.syncCallbacks.delete(item.id);
            }
          } else if (result.error?.includes('conflict')) {
            conflicts++;
            this.conflictQueue.push(item);
          } else {
            failed++;
            // Retry logic
            if (item.retryCount < this.config.maxRetries) {
              item.retryCount++;
              this.syncQueue.push(item);
            } else {
              console.error('Max retries exceeded for sync item:', item.id);
            }
          }

        } catch (error) {
          failed++;
          console.error('Error processing sync item:', item.id, error);
        } finally {
          this.activeSyncs.delete(item.id);
        }
      }

      // Save updated queues
      await this.saveSyncQueue();
      await this.saveConflictQueue();

      // Update last sync timestamp
      this.lastSyncTimestamp = Date.now();

      return formatServiceResponse({
        processed,
        succeeded,
        failed,
        conflicts
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'processSync');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Sync individual item
   */
  private async syncItem(item: SyncItem): Promise<ServiceResponse<any>> {
    try {
      let endpoint: string;
      let method: 'GET' | 'POST' | 'PUT' | 'DELETE';
      let requestData = item.data;

      // Determine endpoint and method based on type and action
      switch (item.type) {
        case 'content':
          endpoint = item.action === 'create' ? SERVICE_ENDPOINTS.CONTENT.UPLOAD : 
                    item.action === 'update' ? SERVICE_ENDPOINTS.CONTENT.UPDATE.replace(':id', item.data.id) :
                    SERVICE_ENDPOINTS.CONTENT.DELETE.replace(':id', item.data.id);
          method = item.action === 'create' ? 'POST' : 
                  item.action === 'update' ? 'PUT' : 'DELETE';
          break;

        case 'metadata':
          endpoint = SERVICE_ENDPOINTS.SYNC.PUSH;
          method = 'POST';
          requestData = { type: 'metadata', action: item.action, data: item.data };
          break;

        case 'preferences':
          endpoint = SERVICE_ENDPOINTS.SYNC.PUSH;
          method = 'POST';
          requestData = { type: 'preferences', action: item.action, data: item.data };
          break;

        case 'analytics':
          endpoint = SERVICE_ENDPOINTS.ANALYTICS.EVENTS;
          method = 'POST';
          break;

        default:
          throw new Error(`Unknown sync type: ${item.type}`);
      }

      // Add sync metadata
      const syncData = {
        ...requestData,
        syncId: item.id,
        timestamp: item.timestamp,
        checksum: item.checksum,
        clientVersion: '1.0.0'
      };

      // Encrypt data if enabled
      if (this.config.encryptionEnabled) {
        // Encryption would be handled by the API service
      }

      // Compress data if enabled
      if (this.config.compressionEnabled) {
        // Compression would be handled by the API service
      }

      // Make API request with retry
      const result = await retryWithBackoff(async () => {
        return await this.apiService.request({
          method,
          endpoint,
          data: syncData,
          requiresAuth: true,
          priority: item.priority >= 5 ? 'high' : 'normal'
        });
      }, this.config.maxRetries);

      // Handle conflicts
      if (result.status === 409) {
        return {
          success: false,
          error: 'conflict',
          timestamp: Date.now(),
          metadata: {
            serverData: result.data,
            clientData: item.data
          }
        };
      }

      return formatServiceResponse(result.data, false, {
        syncId: item.id,
        endpoint,
        method
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'syncItem', { itemId: item.id });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Pull updates from server
   */
  public async pullUpdates(
    since?: number
  ): Promise<ServiceResponse<{
    updates: any[];
    conflicts: any[];
    lastSync: number;
  }>> {
    try {
      const sinceTimestamp = since || this.lastSyncTimestamp;

      const result = await this.apiService.request({
        method: 'GET',
        endpoint: SERVICE_ENDPOINTS.SYNC.PULL,
        data: {
          since: sinceTimestamp,
          clientId: this.getClientId(),
          enableDelta: this.config.enableDeltaSync
        },
        requiresAuth: true
      });

      if (!result.success) {
        return result as any;
      }

      const { updates, conflicts, serverTimestamp } = result.data;

      // Process updates
      for (const update of updates) {
        await this.applyServerUpdate(update);
      }

      // Handle conflicts
      for (const conflict of conflicts) {
        await this.handleConflict(conflict);
      }

      this.lastSyncTimestamp = serverTimestamp;

      return formatServiceResponse({
        updates,
        conflicts,
        lastSync: serverTimestamp
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'pullUpdates');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Handle sync conflicts
   */
  public async resolveConflict(
    conflictId: string,
    resolution: 'server' | 'client' | 'merge',
    mergedData?: any
  ): Promise<ServiceResponse<boolean>> {
    try {
      const conflict = this.conflictQueue.find(item => item.id === conflictId);
      if (!conflict) {
        return {
          success: false,
          error: 'Conflict not found',
          timestamp: Date.now()
        };
      }

      let resolvedData: any;

      switch (resolution) {
        case 'server':
          // Accept server version (do nothing, server data already applied)
          resolvedData = null;
          break;

        case 'client':
          // Use client version
          resolvedData = conflict.data;
          break;

        case 'merge':
          // Use provided merged data
          if (!mergedData) {
            return {
              success: false,
              error: 'Merged data required for merge resolution',
              timestamp: Date.now()
            };
          }
          resolvedData = mergedData;
          break;

        default:
          return {
            success: false,
            error: 'Invalid resolution type',
            timestamp: Date.now()
          };
      }

      // Apply resolution if needed
      if (resolvedData) {
        await this.addToSyncQueue(
          conflict.type,
          conflict.action,
          resolvedData,
          10 // High priority for conflict resolution
        );
      }

      // Remove from conflict queue
      this.conflictQueue = this.conflictQueue.filter(item => item.id !== conflictId);
      await this.saveConflictQueue();

      // Notify server of resolution
      await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.SYNC.RESOLVE,
        data: {
          conflictId,
          resolution,
          resolvedData
        },
        requiresAuth: true
      });

      return formatServiceResponse(true);

    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'resolveConflict', { conflictId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get sync status
   */
  public async getSyncStatus(): Promise<ServiceResponse<{
    isOnline: boolean;
    queueSize: number;
    conflictCount: number;
    lastSync: number;
    nextSync: number;
    activeSyncs: number;
  }>> {
    try {
      const nextSync = this.config.enableRealTime ? 
        Date.now() + SYNC_INTERVALS.REAL_TIME :
        this.lastSyncTimestamp + this.config.syncInterval;

      return formatServiceResponse({
        isOnline: this.isOnline,
        queueSize: this.syncQueue.length,
        conflictCount: this.conflictQueue.length,
        lastSync: this.lastSyncTimestamp,
        nextSync,
        activeSyncs: this.activeSyncs.size
      });
    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'getSyncStatus');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Force immediate sync
   */
  public async forceSync(): Promise<ServiceResponse<any>> {
    try {
      // Pull updates first
      const pullResult = await this.pullUpdates();
      
      // Then push pending changes
      const pushResult = await this.processSync();

      return formatServiceResponse({
        pull: pullResult.data,
        push: pushResult.data
      });
    } catch (error) {
      const serviceError = handleServiceError(error, 'SyncService', 'forceSync');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Register sync callback
   */
  public onSyncComplete(syncId: string, callback: Function): void {
    this.syncCallbacks.set(syncId, callback);
  }

  // Private helper methods

  private async loadSyncQueue(): Promise<void> {
    try {
      const result = await this.storageService.retrieve(STORAGE_KEYS.SYNC_QUEUE);
      if (result.success) {
        this.syncQueue = result.data || [];
      }
    } catch (error) {
      console.warn('Failed to load sync queue:', error);
      this.syncQueue = [];
    }
  }

  private async saveSyncQueue(): Promise<void> {
    try {
      await this.storageService.store(STORAGE_KEYS.SYNC_QUEUE, this.syncQueue);
    } catch (error) {
      console.error('Failed to save sync queue:', error);
    }
  }

  private async loadConflictQueue(): Promise<void> {
    try {
      const result = await this.storageService.retrieve(STORAGE_KEYS.CONFLICT_QUEUE);
      if (result.success) {
        this.conflictQueue = result.data || [];
      }
    } catch (error) {
      console.warn('Failed to load conflict queue:', error);
      this.conflictQueue = [];
    }
  }

  private async saveConflictQueue(): Promise<void> {
    try {
      await this.storageService.store(STORAGE_KEYS.CONFLICT_QUEUE, this.conflictQueue);
    } catch (error) {
      console.error('Failed to save conflict queue:', error);
    }
  }

  private setupNetworkMonitoring(): void {
    // In a real React Native app, this would use NetInfo
    this.isOnline = navigator.onLine;
    
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processSync(); // Sync when coming back online
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  private startRealTimeSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(async () => {
      if (this.isOnline && this.syncQueue.length > 0) {
        await this.processSync();
      }
    }, SYNC_INTERVALS.REAL_TIME);
  }

  private startPeriodicSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(async () => {
      if (this.isOnline) {
        await this.pullUpdates();
        if (this.syncQueue.length > 0) {
          await this.processSync();
        }
      }
    }, this.config.syncInterval);
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(async () => {
      if (this.isOnline) {
        try {
          await this.apiService.request({
            method: 'GET',
            endpoint: SERVICE_ENDPOINTS.SYNC.STATUS,
            requiresAuth: true,
            priority: 'low'
          });
        } catch (error) {
          // Heartbeat failed, but don't error out
          console.warn('Heartbeat failed:', error);
        }
      }
    }, SYNC_INTERVALS.HEARTBEAT);
  }

  private async applyServerUpdate(update: any): Promise<void> {
    try {
      // Apply server update to local storage
      switch (update.type) {
        case 'content':
          await this.storageService.storeContent(
            update.data.id,
            update.data,
            update.data.fingerprint,
            { serverUpdate: true }
          );
          break;

        case 'metadata':
        case 'preferences':
          await this.storageService.store(
            `${update.type}_${update.data.id}`,
            update.data,
            { priority: 5 }
          );
          break;
      }
    } catch (error) {
      console.error('Failed to apply server update:', error);
    }
  }

  private async handleConflict(conflict: any): Promise<void> {
    // Add to conflict queue for manual resolution
    const conflictItem: SyncItem = {
      id: conflict.id,
      type: conflict.type,
      action: conflict.action,
      data: conflict.clientData,
      timestamp: conflict.timestamp,
      checksum: conflict.checksum,
      priority: 10,
      retryCount: 0
    };

    this.conflictQueue.push(conflictItem);
    await this.saveConflictQueue();

    // Auto-resolve based on configuration
    if (this.config.conflictResolution !== 'manual') {
      await this.resolveConflict(conflict.id, this.config.conflictResolution);
    }
  }

  private getEstimatedSyncTime(): number {
    const avgSyncTime = 2000; // 2 seconds per item on average
    return this.syncQueue.length * avgSyncTime;
  }

  private getClientId(): string {
    // In a real app, this would be a unique device identifier
    return 'client_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    this.syncCallbacks.clear();
    this.activeSyncs.clear();
  }
}

export default SyncService;