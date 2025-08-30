/**
 * Offline Storage Service - Intelligent Local Data Management
 * 
 * Advanced offline storage service providing encrypted local storage,
 * intelligent caching, and seamless data synchronization capabilities.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { StorageOptions, StorageItem, BaseService, ServiceEventListener, ServiceEvent } from './types';

class OfflineStorageService implements BaseService {
  private initialized: boolean = false;
  private listeners: Map<string, ServiceEventListener[]> = new Map();
  private encryptionKey: string | null = null;

  async initialize(): Promise<void> {
    try {
      await this.initializeEncryption();
      this.initialized = true;
      this.emit('initialized', { success: true });
    } catch (error) {
      this.emit('error', { error: error.message });
      throw error;
    }
  }

  async destroy(): Promise<void> {
    this.listeners.clear();
    this.initialized = false;
    this.emit('destroyed', { success: true });
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  addEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(listener as ServiceEventListener);
  }

  removeEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener as ServiceEventListener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit<T>(type: string, data: T): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const event: ServiceEvent<T> = {
        type,
        data,
        timestamp: new Date(),
        source: 'OfflineStorageService',
      };
      listeners.forEach(listener => listener(event));
    }
  }

  // Storage Methods
  async setItem<T>(key: string, value: T, options: StorageOptions = {}): Promise<void> {
    try {
      const storageItem: StorageItem<T> = {
        key,
        value,
        timestamp: Date.now(),
        size: this.calculateSize(value),
        encrypted: options.encrypt || false,
        compressed: options.compress || false,
        expiresAt: options.ttl ? Date.now() + (options.ttl * 1000) : undefined,
      };

      let processedValue = value;
      
      if (options.compress) {
        processedValue = await this.compress(processedValue);
      }
      
      if (options.encrypt) {
        processedValue = await this.encrypt(processedValue);
      }

      await AsyncStorage.setItem(key, JSON.stringify({
        ...storageItem,
        value: processedValue,
      }));

      this.emit('itemStored', { key, size: storageItem.size });
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'setItem', key });
      throw error;
    }
  }

  async getItem<T>(key: string): Promise<T | null> {
    try {
      const itemStr = await AsyncStorage.getItem(key);
      if (!itemStr) return null;

      const storageItem: StorageItem<T> = JSON.parse(itemStr);
      
      // Check expiration
      if (storageItem.expiresAt && Date.now() > storageItem.expiresAt) {
        await this.removeItem(key);
        return null;
      }

      let value = storageItem.value;
      
      if (storageItem.encrypted) {
        value = await this.decrypt(value);
      }
      
      if (storageItem.compressed) {
        value = await this.decompress(value);
      }

      this.emit('itemRetrieved', { key, size: storageItem.size });
      return value;
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'getItem', key });
      return null;
    }
  }

  async removeItem(key: string): Promise<void> {
    try {
      await AsyncStorage.removeItem(key);
      this.emit('itemRemoved', { key });
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'removeItem', key });
      throw error;
    }
  }

  async getAllKeys(): Promise<string[]> {
    try {
      return await AsyncStorage.getAllKeys();
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'getAllKeys' });
      return [];
    }
  }

  async clear(): Promise<void> {
    try {
      await AsyncStorage.clear();
      this.emit('storageCleared', {});
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'clear' });
      throw error;
    }
  }

  async getStorageInfo(): Promise<{ totalSize: number; itemCount: number }> {
    try {
      const keys = await this.getAllKeys();
      let totalSize = 0;
      
      for (const key of keys) {
        const item = await this.getStorageItemInfo(key);
        if (item) {
          totalSize += item.size;
        }
      }

      return {
        totalSize,
        itemCount: keys.length,
      };
    } catch (error) {
      this.emit('error', { error: error.message, operation: 'getStorageInfo' });
      return { totalSize: 0, itemCount: 0 };
    }
  }

  // Business Logic Methods
  async cacheContent(contentId: string, content: any, ttl: number = 3600): Promise<void> {
    await this.setItem(`content:${contentId}`, content, { ttl, compress: true });
  }

  async getCachedContent(contentId: string): Promise<any> {
    return this.getItem(`content:${contentId}`);
  }

  async cacheUserProfile(userId: string, profile: any): Promise<void> {
    await this.setItem(`profile:${userId}`, profile, { encrypt: true });
  }

  async getCachedUserProfile(userId: string): Promise<any> {
    return this.getItem(`profile:${userId}`);
  }

  async cacheAnalytics(timeframe: string, data: any): Promise<void> {
    await this.setItem(`analytics:${timeframe}`, data, { ttl: 1800 }); // 30 minutes
  }

  async getCachedAnalytics(timeframe: string): Promise<any> {
    return this.getItem(`analytics:${timeframe}`);
  }

  async storeOfflineAction(action: any): Promise<void> {
    const actions = await this.getItem<any[]>('offline_actions') || [];
    actions.push({
      ...action,
      id: Date.now().toString(),
      timestamp: new Date(),
    });
    await this.setItem('offline_actions', actions);
  }

  async getOfflineActions(): Promise<any[]> {
    return this.getItem<any[]>('offline_actions') || [];
  }

  async clearOfflineActions(): Promise<void> {
    await this.removeItem('offline_actions');
  }

  // Private Methods
  private async initializeEncryption(): Promise<void> {
    // In a real implementation, this would use react-native-keychain
    // or react-native-encrypted-storage for secure key storage
    this.encryptionKey = 'mock-encryption-key-12345';
  }

  private async getStorageItemInfo(key: string): Promise<StorageItem | null> {
    try {
      const itemStr = await AsyncStorage.getItem(key);
      if (!itemStr) return null;
      return JSON.parse(itemStr);
    } catch {
      return null;
    }
  }

  private calculateSize(value: any): number {
    return JSON.stringify(value).length;
  }

  private async encrypt(value: any): Promise<any> {
    // Mock encryption - in real implementation use react-native-crypto
    return `encrypted:${JSON.stringify(value)}`;
  }

  private async decrypt(value: any): Promise<any> {
    // Mock decryption
    if (typeof value === 'string' && value.startsWith('encrypted:')) {
      return JSON.parse(value.replace('encrypted:', ''));
    }
    return value;
  }

  private async compress(value: any): Promise<any> {
    // Mock compression - in real implementation use a compression library
    return `compressed:${JSON.stringify(value)}`;
  }

  private async decompress(value: any): Promise<any> {
    // Mock decompression
    if (typeof value === 'string' && value.startsWith('compressed:')) {
      return JSON.parse(value.replace('compressed:', ''));
    }
    return value;
  }
}

export default new OfflineStorageService();