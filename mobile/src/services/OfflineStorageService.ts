/**
 * Offline Storage Service - Advanced offline data management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

export interface StorageItem<T = any> {
  key: string;
  value: T;
  timestamp: number;
  expiresAt?: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  metadata?: Record<string, any>;
}

export interface StorageConfig {
  maxSize: number; // bytes
  defaultTTL: number; // milliseconds
  compressionEnabled: boolean;
  encryptionEnabled: boolean;
  autoCleanup: boolean;
}

export interface CacheStrategy {
  type: 'LRU' | 'LFU' | 'FIFO' | 'TTL';
  maxItems: number;
  evictionThreshold: number;
}

export interface StorageMetrics {
  totalSize: number;
  itemCount: number;
  hitRate: number;
  lastCleanup: number;
  compressionRatio: number;
  errorCount: number;
}

export interface OfflineContent {
  contentId: string;
  type: 'audio' | 'video' | 'image' | 'document';
  localPath: string;
  originalUrl: string;
  size: number;
  downloadedAt: number;
  lastAccessed: number;
  syncStatus: 'synced' | 'pending' | 'conflict' | 'error';
  metadata: Record<string, any>;
}

export interface SyncQueueItem {
  id: string;
  operation: 'create' | 'update' | 'delete';
  table: string;
  data: any;
  timestamp: number;
  retries: number;
  priority: number;
  dependencies?: string[];
}

export class OfflineStorageService {
  private db: IDBDatabase | null = null;
  private config: StorageConfig;
  private cacheStrategy: CacheStrategy;
  private metrics: StorageMetrics;
  private memoryCache: Map<string, StorageItem>;
  private compressionWorker?: Worker;
  private encryptionKey?: CryptoKey;

  constructor(config?: Partial<StorageConfig>) {
    this.config = {
      maxSize: 500 * 1024 * 1024, // 500MB default
      defaultTTL: 7 * 24 * 60 * 60 * 1000, // 7 days
      compressionEnabled: true,
      encryptionEnabled: true,
      autoCleanup: true,
      ...config,
    };

    this.cacheStrategy = {
      type: 'LRU',
      maxItems: 10000,
      evictionThreshold: 0.8,
    };

    this.metrics = {
      totalSize: 0,
      itemCount: 0,
      hitRate: 0,
      lastCleanup: 0,
      compressionRatio: 1,
      errorCount: 0,
    };

    this.memoryCache = new Map();
    this.initializeDatabase();
    this.initializeWorkers();
    
    if (this.config.autoCleanup) {
      this.startCleanupScheduler();
    }
  }

  private async initializeDatabase(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('AinflueMobileStorage', 3);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Main storage store
        if (!db.objectStoreNames.contains('storage')) {
          const storageStore = db.createObjectStore('storage', { keyPath: 'key' });
          storageStore.createIndex('timestamp', 'timestamp');
          storageStore.createIndex('priority', 'priority');
          storageStore.createIndex('expiresAt', 'expiresAt');
        }

        // Content cache store
        if (!db.objectStoreNames.contains('content')) {
          const contentStore = db.createObjectStore('content', { keyPath: 'contentId' });
          contentStore.createIndex('type', 'type');
          contentStore.createIndex('downloadedAt', 'downloadedAt');
          contentStore.createIndex('syncStatus', 'syncStatus');
        }

        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
          syncStore.createIndex('timestamp', 'timestamp');
          syncStore.createIndex('priority', 'priority');
          syncStore.createIndex('operation', 'operation');
        }

        // User data store
        if (!db.objectStoreNames.contains('userData')) {
          const userStore = db.createObjectStore('userData', { keyPath: 'userId' });
          userStore.createIndex('lastLogin', 'lastLogin');
        }

        // Analytics queue store
        if (!db.objectStoreNames.contains('analytics')) {
          const analyticsStore = db.createObjectStore('analytics', { keyPath: 'id', autoIncrement: true });
          analyticsStore.createIndex('timestamp', 'timestamp');
          analyticsStore.createIndex('synced', 'synced');
        }
      };
    });
  }

  private initializeWorkers(): void {
    // Initialize compression worker for large data
    if (this.config.compressionEnabled && 'Worker' in window) {
      const compressionScript = `
        self.onmessage = function(e) {
          const { data, compress } = e.data;
          
          if (compress) {
            // Simulate compression (in real implementation, use actual compression library)
            const compressed = new TextEncoder().encode(JSON.stringify(data));
            self.postMessage({ compressed: Array.from(compressed) });
          } else {
            // Decompress
            const decompressed = JSON.parse(new TextDecoder().decode(new Uint8Array(data)));
            self.postMessage({ decompressed });
          }
        };
      `;
      
      const blob = new Blob([compressionScript], { type: 'application/javascript' });
      this.compressionWorker = new Worker(URL.createObjectURL(blob));
    }

    // Initialize encryption if needed
    if (this.config.encryptionEnabled) {
      this.initializeEncryption();
    }
  }

  private async initializeEncryption(): Promise<void> {
    try {
      // Generate or retrieve encryption key
      const keyData = await window.crypto.subtle.generateKey(
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt', 'decrypt']
      );
      this.encryptionKey = keyData;
    } catch (error) {
      console.warn('Encryption initialization failed:', error);
      this.config.encryptionEnabled = false;
    }
  }

  // Core Storage Operations
  async store<T>(key: string, value: T, options?: {
    ttl?: number;
    priority?: 'low' | 'normal' | 'high' | 'critical';
    metadata?: Record<string, any>;
  }): Promise<boolean> {
    try {
      const now = Date.now();
      const item: StorageItem<T> = {
        key,
        value,
        timestamp: now,
        expiresAt: options?.ttl ? now + options.ttl : now + this.config.defaultTTL,
        priority: options?.priority || 'normal',
        metadata: options?.metadata,
      };

      // Store in memory cache for fast access
      this.memoryCache.set(key, item);

      // Process data (compression/encryption if enabled)
      let processedValue = value;
      if (this.config.compressionEnabled) {
        processedValue = await this.compressData(value);
      }
      if (this.config.encryptionEnabled) {
        processedValue = await this.encryptData(processedValue);
      }

      // Store in IndexedDB
      await this.storeInDB('storage', { ...item, value: processedValue });
      
      this.updateMetrics('store', item);
      this.checkStorageLimit();
      
      return true;
    } catch (error) {
      this.metrics.errorCount++;
      console.error('Storage error:', error);
      return false;
    }
  }

  async retrieve<T>(key: string): Promise<T | null> {
    try {
      // Check memory cache first
      const cached = this.memoryCache.get(key);
      if (cached && !this.isExpired(cached)) {
        this.updateMetrics('hit');
        return cached.value as T;
      }

      // Retrieve from IndexedDB
      const item = await this.retrieveFromDB<StorageItem<T>>('storage', key);
      if (!item || this.isExpired(item)) {
        this.updateMetrics('miss');
        return null;
      }

      // Process data (decrypt/decompress if needed)
      let processedValue = item.value;
      if (this.config.encryptionEnabled) {
        processedValue = await this.decryptData(processedValue);
      }
      if (this.config.compressionEnabled) {
        processedValue = await this.decompressData(processedValue);
      }

      // Update memory cache
      const processedItem = { ...item, value: processedValue };
      this.memoryCache.set(key, processedItem);
      
      this.updateMetrics('hit');
      return processedValue as T;
    } catch (error) {
      this.metrics.errorCount++;
      console.error('Retrieval error:', error);
      return null;
    }
  }

  async remove(key: string): Promise<boolean> {
    try {
      this.memoryCache.delete(key);
      await this.removeFromDB('storage', key);
      this.updateMetrics('remove');
      return true;
    } catch (error) {
      this.metrics.errorCount++;
      return false;
    }
  }

  async clear(): Promise<boolean> {
    try {
      this.memoryCache.clear();
      await this.clearDB('storage');
      this.resetMetrics();
      return true;
    } catch (error) {
      this.metrics.errorCount++;
      return false;
    }
  }

  // Content Management
  async storeContent(content: OfflineContent): Promise<boolean> {
    try {
      await this.storeInDB('content', content);
      return true;
    } catch (error) {
      console.error('Content storage error:', error);
      return false;
    }
  }

  async getOfflineContent(contentId: string): Promise<OfflineContent | null> {
    return this.retrieveFromDB<OfflineContent>('content', contentId);
  }

  async getAllOfflineContent(type?: string): Promise<OfflineContent[]> {
    const transaction = this.db?.transaction(['content'], 'readonly');
    const store = transaction?.objectStore('content');
    
    if (!store) return [];

    return new Promise((resolve, reject) => {
      const request = type 
        ? store.index('type').getAll(type)
        : store.getAll();

      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  async cleanupExpiredContent(): Promise<number> {
    const allContent = await this.getAllOfflineContent();
    const now = Date.now();
    const expiredThreshold = 30 * 24 * 60 * 60 * 1000; // 30 days
    
    let cleanedCount = 0;
    
    for (const content of allContent) {
      if (now - content.lastAccessed > expiredThreshold) {
        await this.removeFromDB('content', content.contentId);
        cleanedCount++;
      }
    }
    
    return cleanedCount;
  }

  // Sync Queue Management
  async addToSyncQueue(item: Omit<SyncQueueItem, 'id' | 'timestamp'>): Promise<string> {
    const syncItem: SyncQueueItem = {
      ...item,
      id: `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
    };

    await this.storeInDB('syncQueue', syncItem);
    return syncItem.id;
  }

  async getSyncQueue(): Promise<SyncQueueItem[]> {
    const transaction = this.db?.transaction(['syncQueue'], 'readonly');
    const store = transaction?.objectStore('syncQueue');
    
    if (!store) return [];

    return new Promise((resolve, reject) => {
      const request = store.index('priority').getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  async removeSyncItem(id: string): Promise<boolean> {
    try {
      await this.removeFromDB('syncQueue', id);
      return true;
    } catch (error) {
      return false;
    }
  }

  // User Data Management
  async storeUserData(userId: string, data: any): Promise<boolean> {
    const userData = {
      userId,
      data,
      lastLogin: Date.now(),
      version: 1,
    };

    try {
      await this.storeInDB('userData', userData);
      return true;
    } catch (error) {
      return false;
    }
  }

  async getUserData(userId: string): Promise<any> {
    const userData = await this.retrieveFromDB('userData', userId);
    return userData?.data || null;
  }

  // Analytics Queue
  async queueAnalytics(event: any): Promise<void> {
    const analyticsItem = {
      ...event,
      timestamp: Date.now(),
      synced: false,
    };

    await this.storeInDB('analytics', analyticsItem);
  }

  async getPendingAnalytics(): Promise<any[]> {
    const transaction = this.db?.transaction(['analytics'], 'readonly');
    const store = transaction?.objectStore('analytics');
    
    if (!store) return [];

    return new Promise((resolve, reject) => {
      const request = store.index('synced').getAll(false);
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  async markAnalyticsSynced(ids: number[]): Promise<void> {
    const transaction = this.db?.transaction(['analytics'], 'readwrite');
    const store = transaction?.objectStore('analytics');
    
    if (!store) return;

    for (const id of ids) {
      const request = store.get(id);
      request.onsuccess = () => {
        const record = request.result;
        if (record) {
          record.synced = true;
          store.put(record);
        }
      };
    }
  }

  // Storage Management
  async getStorageInfo(): Promise<StorageMetrics & { availableSpace: number }> {
    let availableSpace = 0;
    
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      availableSpace = (estimate.quota || 0) - (estimate.usage || 0);
    }

    return {
      ...this.metrics,
      availableSpace,
    };
  }

  async cleanupStorage(): Promise<{ itemsRemoved: number; spaceFreed: number }> {
    let itemsRemoved = 0;
    let spaceFreed = 0;
    const now = Date.now();

    // Clean expired items
    const transaction = this.db?.transaction(['storage'], 'readwrite');
    const store = transaction?.objectStore('storage');
    
    if (!store) return { itemsRemoved: 0, spaceFreed: 0 };

    return new Promise((resolve, reject) => {
      const request = store.openCursor();
      
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        
        if (cursor) {
          const item = cursor.value as StorageItem;
          
          if (this.isExpired(item) || this.shouldEvict(item)) {
            const size = this.estimateSize(item);
            cursor.delete();
            itemsRemoved++;
            spaceFreed += size;
          }
          
          cursor.continue();
        } else {
          this.metrics.lastCleanup = now;
          resolve({ itemsRemoved, spaceFreed });
        }
      };
      
      request.onerror = () => reject(request.error);
    });
  }

  // Private Helper Methods
  private async storeInDB(storeName: string, data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db?.transaction([storeName], 'readwrite');
      const store = transaction?.objectStore(storeName);
      
      if (!store) {
        reject(new Error('Store not available'));
        return;
      }

      const request = store.put(data);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async retrieveFromDB<T>(storeName: string, key: string): Promise<T | null> {
    return new Promise((resolve, reject) => {
      const transaction = this.db?.transaction([storeName], 'readonly');
      const store = transaction?.objectStore(storeName);
      
      if (!store) {
        resolve(null);
        return;
      }

      const request = store.get(key);
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  private async removeFromDB(storeName: string, key: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db?.transaction([storeName], 'readwrite');
      const store = transaction?.objectStore(storeName);
      
      if (!store) {
        reject(new Error('Store not available'));
        return;
      }

      const request = store.delete(key);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async clearDB(storeName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db?.transaction([storeName], 'readwrite');
      const store = transaction?.objectStore(storeName);
      
      if (!store) {
        reject(new Error('Store not available'));
        return;
      }

      const request = store.clear();
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async compressData(data: any): Promise<any> {
    if (!this.compressionWorker) return data;
    
    return new Promise((resolve) => {
      this.compressionWorker!.onmessage = (e) => {
        resolve(e.data.compressed);
      };
      this.compressionWorker!.postMessage({ data, compress: true });
    });
  }

  private async decompressData(data: any): Promise<any> {
    if (!this.compressionWorker) return data;
    
    return new Promise((resolve) => {
      this.compressionWorker!.onmessage = (e) => {
        resolve(e.data.decompressed);
      };
      this.compressionWorker!.postMessage({ data, compress: false });
    });
  }

  private async encryptData(data: any): Promise<any> {
    if (!this.encryptionKey) return data;
    
    try {
      const encoded = new TextEncoder().encode(JSON.stringify(data));
      const iv = window.crypto.getRandomValues(new Uint8Array(12));
      
      const encrypted = await window.crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        this.encryptionKey,
        encoded
      );
      
      return {
        encrypted: Array.from(new Uint8Array(encrypted)),
        iv: Array.from(iv),
      };
    } catch (error) {
      console.warn('Encryption failed:', error);
      return data;
    }
  }

  private async decryptData(data: any): Promise<any> {
    if (!this.encryptionKey || !data.encrypted) return data;
    
    try {
      const decrypted = await window.crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: new Uint8Array(data.iv) },
        this.encryptionKey,
        new Uint8Array(data.encrypted)
      );
      
      const decoded = new TextDecoder().decode(decrypted);
      return JSON.parse(decoded);
    } catch (error) {
      console.warn('Decryption failed:', error);
      return data;
    }
  }

  private isExpired(item: StorageItem): boolean {
    return item.expiresAt ? Date.now() > item.expiresAt : false;
  }

  private shouldEvict(item: StorageItem): boolean {
    // Implement LRU/LFU logic based on cache strategy
    return false; // Simplified for now
  }

  private estimateSize(item: StorageItem): number {
    return JSON.stringify(item).length * 2; // Rough estimate
  }

  private updateMetrics(operation: 'store' | 'hit' | 'miss' | 'remove', item?: StorageItem): void {
    switch (operation) {
      case 'store':
        this.metrics.itemCount++;
        if (item) {
          this.metrics.totalSize += this.estimateSize(item);
        }
        break;
      case 'hit':
        this.metrics.hitRate = (this.metrics.hitRate * 0.9) + (1 * 0.1);
        break;
      case 'miss':
        this.metrics.hitRate = this.metrics.hitRate * 0.9;
        break;
      case 'remove':
        this.metrics.itemCount = Math.max(0, this.metrics.itemCount - 1);
        break;
    }
  }

  private resetMetrics(): void {
    this.metrics = {
      totalSize: 0,
      itemCount: 0,
      hitRate: 0,
      lastCleanup: Date.now(),
      compressionRatio: 1,
      errorCount: 0,
    };
  }

  private checkStorageLimit(): void {
    if (this.metrics.totalSize > this.config.maxSize) {
      this.cleanupStorage();
    }
  }

  private startCleanupScheduler(): void {
    setInterval(() => {
      this.cleanupStorage();
      this.cleanupExpiredContent();
    }, 24 * 60 * 60 * 1000); // Daily cleanup
  }
}

// Export singleton instance
export const offlineStorageService = new OfflineStorageService();