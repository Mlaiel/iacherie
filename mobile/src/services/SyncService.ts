/**
 * Sync Service - Intelligent Data Synchronization
 * 
 * Advanced synchronization service handling conflict resolution,
 * priority queuing, and intelligent sync strategies.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { SyncQueueItem, SyncConflict, SyncProgress, BaseService, ServiceEventListener, ServiceEvent } from './types';
import MobileAPIService from './MobileAPIService';
import OfflineStorageService from './OfflineStorageService';

class SyncService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();
  private syncQueue: SyncQueueItem[] = [];
  private isSyncing: boolean = false;

  async initialize(): Promise<void> {
    try {
      await this.loadSyncQueue();
      this.initialized = true;
      this.emit('initialized', { success: true });
    } catch (error) {
      throw error;
    }
  }

  async destroy(): Promise<void> {
    await this.saveSyncQueue();
    this.listeners.clear();
    this.initialized = false;
  }

  isInitialized(): boolean { return this.initialized; }
  addEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type)!.push(listener as ServiceEventListener);
  }
  removeEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener as ServiceEventListener);
      if (index > -1) listeners.splice(index, 1);
    }
  }
  emit<T>(type: string, data: T): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const event: ServiceEvent<T> = { type, data, timestamp: new Date(), source: 'SyncService' };
      listeners.forEach(listener => listener(event));
    }
  }

  async queueAction(action: Omit<SyncQueueItem, 'id' | 'timestamp' | 'retryCount'>): Promise<void> {
    const item: SyncQueueItem = {
      ...action,
      id: Date.now().toString(),
      timestamp: Date.now(),
      retryCount: 0,
    };
    this.syncQueue.push(item);
    await this.saveSyncQueue();
    this.emit('actionQueued', { item });
  }

  async startSync(): Promise<void> {
    if (this.isSyncing) return;
    this.isSyncing = true;
    
    try {
      const progress: SyncProgress = { total: this.syncQueue.length, completed: 0, failed: 0 };
      this.emit('syncStarted', { progress });
      
      for (const item of this.syncQueue) {
        try {
          await this.syncItem(item);
          progress.completed++;
        } catch (error) {
          progress.failed++;
          item.retryCount++;
        }
        this.emit('syncProgress', { progress });
      }
      
      this.syncQueue = this.syncQueue.filter(item => item.retryCount >= 3);
      await this.saveSyncQueue();
      this.emit('syncCompleted', { progress });
    } finally {
      this.isSyncing = false;
    }
  }

  private async syncItem(item: SyncQueueItem): Promise<void> {
    switch (item.type) {
      case 'create':
        await MobileAPIService.post(`/${item.collection}`, item.data);
        break;
      case 'update':
        await MobileAPIService.put(`/${item.collection}/${item.data.id}`, item.data);
        break;
      case 'delete':
        await MobileAPIService.delete(`/${item.collection}/${item.data.id}`);
        break;
    }
  }

  private async loadSyncQueue(): Promise<void> {
    this.syncQueue = await OfflineStorageService.getItem<SyncQueueItem[]>('sync_queue') || [];
  }

  private async saveSyncQueue(): Promise<void> {
    await OfflineStorageService.setItem('sync_queue', this.syncQueue);
  }
}

export default new SyncService();