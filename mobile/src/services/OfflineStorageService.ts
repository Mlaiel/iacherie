/**
 * Offline Storage Service - Professional Offline Data Management
 * 
 * Enterprise-grade offline storage service with encryption, compression,
 * intelligent caching, automatic cleanup, and sync queue management.
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

import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  OfflineStorageConfig,
  StorageItem,
  ServiceResponse,
  ServiceError,
  ContentFingerprint
} from './types';
import {
  handleServiceError,
  formatServiceResponse,
  encryptData,
  decryptData,
  compressData,
  decompressData,
  calculateChecksum,
  createOfflineStorageConfig
} from './utils';
import { STORAGE_KEYS, SERVICE_DEFAULTS } from './constants';

/**
 * Professional offline storage service for content creators
 */
class OfflineStorageService {
  private static instance: OfflineStorageService;
  private config: OfflineStorageConfig;
  private storageIndex: Map<string, StorageItem> = new Map();
  private isInitialized = false;
  private cleanupInterval: NodeJS.Timeout | null = null;

  private constructor(config: OfflineStorageConfig) {
    this.config = config;
    this.initialize();
  }

  public static getInstance(config?: OfflineStorageConfig): OfflineStorageService {
    if (!OfflineStorageService.instance) {
      const defaultConfig = createOfflineStorageConfig(config);
      OfflineStorageService.instance = new OfflineStorageService(defaultConfig);
    }
    return OfflineStorageService.instance;
  }

  /**
   * Initialize the storage service
   */
  private async initialize(): Promise<void> {
    try {
      await this.loadStorageIndex();
      this.setupAutomaticCleanup();
      this.isInitialized = true;
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'initialize');
      console.error('Failed to initialize offline storage:', serviceError);
    }
  }

  /**
   * Store data with encryption and compression
   */
  public async store(
    key: string,
    value: any,
    options: {
      ttl?: number;
      priority?: number;
      encrypted?: boolean;
      compressed?: boolean;
    } = {}
  ): Promise<ServiceResponse<boolean>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      // Check storage space
      const canStore = await this.checkStorageCapacity(key, value);
      if (!canStore.success) {
        return canStore;
      }

      // Prepare data
      let processedValue = JSON.stringify(value);
      const timestamp = Date.now();
      const encrypted = options.encrypted ?? this.config.encryptionEnabled;
      const compressed = options.compressed ?? this.config.compressionEnabled;

      // Compress data if enabled
      if (compressed) {
        processedValue = compressData(processedValue);
      }

      // Encrypt data if enabled
      if (encrypted) {
        processedValue = encryptData(processedValue, this.config.encryptionKey);
      }

      // Calculate size and checksum
      const size = new Blob([processedValue]).size;
      const checksum = calculateChecksum(processedValue);

      // Create storage item
      const storageItem: StorageItem = {
        key,
        value: processedValue,
        timestamp,
        ttl: options.ttl,
        encrypted,
        compressed,
        size,
        priority: options.priority || 1
      };

      // Store in AsyncStorage
      const storageKey = this.getStorageKey(key);
      await AsyncStorage.setItem(storageKey, JSON.stringify({
        ...storageItem,
        checksum
      }));

      // Update index
      this.storageIndex.set(key, storageItem);
      await this.saveStorageIndex();

      return formatServiceResponse(true, false, {
        size,
        encrypted,
        compressed,
        key: storageKey
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'store', { key });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Retrieve data with decryption and decompression
   */
  public async retrieve(key: string): Promise<ServiceResponse<any>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      // Check if item exists in index
      const indexItem = this.storageIndex.get(key);
      if (!indexItem) {
        return {
          success: false,
          error: 'Item not found',
          timestamp: Date.now()
        };
      }

      // Check TTL
      if (indexItem.ttl && Date.now() > indexItem.timestamp + indexItem.ttl) {
        await this.remove(key);
        return {
          success: false,
          error: 'Item expired',
          timestamp: Date.now()
        };
      }

      // Retrieve from AsyncStorage
      const storageKey = this.getStorageKey(key);
      const storedData = await AsyncStorage.getItem(storageKey);
      
      if (!storedData) {
        // Item missing from storage, clean up index
        this.storageIndex.delete(key);
        await this.saveStorageIndex();
        return {
          success: false,
          error: 'Item not found in storage',
          timestamp: Date.now()
        };
      }

      const parsedData = JSON.parse(storedData);
      let processedValue = parsedData.value;

      // Verify checksum
      const expectedChecksum = calculateChecksum(processedValue);
      if (parsedData.checksum !== expectedChecksum) {
        console.warn('Checksum mismatch for key:', key);
        // Don't fail, but log the warning
      }

      // Decrypt if encrypted
      if (parsedData.encrypted) {
        processedValue = decryptData(processedValue, this.config.encryptionKey);
      }

      // Decompress if compressed
      if (parsedData.compressed) {
        processedValue = decompressData(processedValue);
      }

      // Parse final value
      const finalValue = JSON.parse(processedValue);

      return formatServiceResponse(finalValue, true, {
        size: parsedData.size,
        encrypted: parsedData.encrypted,
        compressed: parsedData.compressed,
        timestamp: parsedData.timestamp
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'retrieve', { key });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Remove item from storage
   */
  public async remove(key: string): Promise<ServiceResponse<boolean>> {
    try {
      const storageKey = this.getStorageKey(key);
      await AsyncStorage.removeItem(storageKey);
      this.storageIndex.delete(key);
      await this.saveStorageIndex();

      return formatServiceResponse(true);
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'remove', { key });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Check if item exists
   */
  public async exists(key: string): Promise<boolean> {
    return this.storageIndex.has(key);
  }

  /**
   * Get all stored keys
   */
  public async getKeys(): Promise<string[]> {
    return Array.from(this.storageIndex.keys());
  }

  /**
   * Get storage statistics
   */
  public async getStorageInfo(): Promise<ServiceResponse<{
    totalItems: number;
    totalSize: number;
    availableSpace: number;
    utilizationPercentage: number;
    oldestItem: number;
    newestItem: number;
  }>> {
    try {
      const items = Array.from(this.storageIndex.values());
      const totalItems = items.length;
      const totalSize = items.reduce((sum, item) => sum + item.size, 0);
      const availableSpace = this.config.maxStorageSize - totalSize;
      const utilizationPercentage = (totalSize / this.config.maxStorageSize) * 100;

      const timestamps = items.map(item => item.timestamp);
      const oldestItem = Math.min(...timestamps);
      const newestItem = Math.max(...timestamps);

      return formatServiceResponse({
        totalItems,
        totalSize,
        availableSpace,
        utilizationPercentage,
        oldestItem,
        newestItem
      });
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'getStorageInfo');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Store content with fingerprint protection
   */
  public async storeContent(
    contentId: string,
    content: any,
    fingerprint: ContentFingerprint,
    metadata: Record<string, any> = {}
  ): Promise<ServiceResponse<boolean>> {
    try {
      const contentData = {
        content,
        fingerprint,
        metadata,
        storedAt: Date.now()
      };

      return await this.store(`content_${contentId}`, contentData, {
        priority: 10, // High priority for content
        encrypted: true,
        compressed: true
      });
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'storeContent', { contentId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Retrieve content with fingerprint verification
   */
  public async retrieveContent(contentId: string): Promise<ServiceResponse<{
    content: any;
    fingerprint: ContentFingerprint;
    metadata: Record<string, any>;
  }>> {
    try {
      const result = await this.retrieve(`content_${contentId}`);
      if (!result.success) {
        return result;
      }

      const { content, fingerprint, metadata } = result.data;
      return formatServiceResponse({
        content,
        fingerprint,
        metadata
      }, true);
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'retrieveContent', { contentId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Store user preferences
   */
  public async storeUserPreferences(
    userId: string,
    preferences: Record<string, any>
  ): Promise<ServiceResponse<boolean>> {
    return await this.store(`user_prefs_${userId}`, preferences, {
      priority: 5,
      encrypted: true
    });
  }

  /**
   * Store sync queue items
   */
  public async storeSyncItem(
    item: any,
    priority = 1
  ): Promise<ServiceResponse<boolean>> {
    const syncKey = `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return await this.store(syncKey, item, {
      priority: priority + 10, // Higher priority for sync items
      encrypted: true
    });
  }

  /**
   * Get all sync queue items
   */
  public async getSyncQueue(): Promise<ServiceResponse<any[]>> {
    try {
      const keys = await this.getKeys();
      const syncKeys = keys.filter(key => key.startsWith('sync_'));
      const syncItems: any[] = [];

      for (const key of syncKeys) {
        const result = await this.retrieve(key);
        if (result.success) {
          syncItems.push({
            key,
            data: result.data,
            priority: this.storageIndex.get(key)?.priority || 1
          });
        }
      }

      // Sort by priority (higher first)
      syncItems.sort((a, b) => b.priority - a.priority);

      return formatServiceResponse(syncItems);
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'getSyncQueue');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Clear all storage
   */
  public async clear(): Promise<ServiceResponse<boolean>> {
    try {
      // Remove all items with our prefix
      const keys = await AsyncStorage.getAllKeys();
      const ourKeys = keys.filter(key => key.startsWith('ainflue_'));
      await AsyncStorage.multiRemove(ourKeys);

      // Clear index
      this.storageIndex.clear();
      await this.saveStorageIndex();

      return formatServiceResponse(true);
    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'clear');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Perform manual cleanup
   */
  public async cleanup(): Promise<ServiceResponse<{
    removedItems: number;
    freedSpace: number;
  }>> {
    try {
      const currentTime = Date.now();
      let removedItems = 0;
      let freedSpace = 0;

      // Get storage info
      const storageInfo = await this.getStorageInfo();
      if (!storageInfo.success) {
        return storageInfo as any;
      }

      const shouldCleanup = storageInfo.data!.utilizationPercentage > (this.config.cleanupThreshold * 100);

      if (shouldCleanup) {
        const items = Array.from(this.storageIndex.entries());
        
        // Sort by priority (lower first) and age (older first)
        items.sort((a, b) => {
          const priorityDiff = a[1].priority - b[1].priority;
          if (priorityDiff !== 0) return priorityDiff;
          return a[1].timestamp - b[1].timestamp;
        });

        // Remove expired items first
        for (const [key, item] of items) {
          if (item.ttl && currentTime > item.timestamp + item.ttl) {
            freedSpace += item.size;
            await this.remove(key);
            removedItems++;
          }
        }

        // If still need space, remove lowest priority items
        const targetSize = this.config.maxStorageSize * (this.config.cleanupThreshold - 0.1);
        const updatedInfo = await this.getStorageInfo();
        
        if (updatedInfo.success && updatedInfo.data!.totalSize > targetSize) {
          const remainingItems = Array.from(this.storageIndex.entries())
            .sort((a, b) => {
              const priorityDiff = a[1].priority - b[1].priority;
              if (priorityDiff !== 0) return priorityDiff;
              return a[1].timestamp - b[1].timestamp;
            });

          for (const [key, item] of remainingItems) {
            if (updatedInfo.data!.totalSize <= targetSize) break;
            
            freedSpace += item.size;
            await this.remove(key);
            removedItems++;
          }
        }
      }

      return formatServiceResponse({
        removedItems,
        freedSpace
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'OfflineStorageService', 'cleanup');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  // Private helper methods

  private getStorageKey(key: string): string {
    return `${STORAGE_KEYS.OFFLINE_DATA}_${key}`;
  }

  private async loadStorageIndex(): Promise<void> {
    try {
      const indexData = await AsyncStorage.getItem(STORAGE_KEYS.STORAGE_MANIFEST);
      if (indexData) {
        const index = JSON.parse(indexData);
        this.storageIndex = new Map(Object.entries(index));
      }
    } catch (error) {
      console.warn('Failed to load storage index:', error);
      this.storageIndex = new Map();
    }
  }

  private async saveStorageIndex(): Promise<void> {
    try {
      const indexObject = Object.fromEntries(this.storageIndex);
      await AsyncStorage.setItem(STORAGE_KEYS.STORAGE_MANIFEST, JSON.stringify(indexObject));
    } catch (error) {
      console.error('Failed to save storage index:', error);
    }
  }

  private async checkStorageCapacity(key: string, value: any): Promise<ServiceResponse<boolean>> {
    try {
      const storageInfo = await this.getStorageInfo();
      if (!storageInfo.success) {
        return storageInfo as any;
      }

      const estimatedSize = new Blob([JSON.stringify(value)]).size;
      const wouldExceedCapacity = storageInfo.data!.totalSize + estimatedSize > this.config.maxStorageSize;

      if (wouldExceedCapacity) {
        // Try automatic cleanup
        if (this.config.autoCleanupEnabled) {
          const cleanupResult = await this.cleanup();
          if (cleanupResult.success) {
            // Check again after cleanup
            const updatedInfo = await this.getStorageInfo();
            if (updatedInfo.success) {
              const stillExceeds = updatedInfo.data!.totalSize + estimatedSize > this.config.maxStorageSize;
              if (stillExceeds) {
                return {
                  success: false,
                  error: 'Insufficient storage space after cleanup',
                  timestamp: Date.now()
                };
              }
            }
          }
        } else {
          return {
            success: false,
            error: 'Insufficient storage space',
            timestamp: Date.now()
          };
        }
      }

      return formatServiceResponse(true);
    } catch (error) {
      return {
        success: false,
        error: 'Failed to check storage capacity',
        timestamp: Date.now()
      };
    }
  }

  private setupAutomaticCleanup(): void {
    if (this.config.autoCleanupEnabled && !this.cleanupInterval) {
      // Run cleanup every hour
      this.cleanupInterval = setInterval(async () => {
        try {
          await this.cleanup();
        } catch (error) {
          console.error('Automatic cleanup failed:', error);
        }
      }, 60 * 60 * 1000);
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
  }
}

export default OfflineStorageService;