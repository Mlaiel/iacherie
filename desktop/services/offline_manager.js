/**
 * Ainflue Desktop - Offline Manager Service
 * 
 * Comprehensive offline functionality manager with intelligent caching,
 * queue management, conflict resolution, and seamless online/offline transitions.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class OfflineManager {
    constructor() {
        this.isOffline = !navigator.onLine;
        this.offlineQueue = [];
        this.offlineCache = new Map();
        this.offlineAssets = new Map();
        this.syncQueue = [];
        this.storageUsage = { used: 0, available: 0, quota: 0 };
        this.offlineCapabilities = new Set();
        
        this.config = {
            maxCacheSize: 500 * 1024 * 1024, // 500MB
            maxQueueSize: 1000,
            assetCacheDuration: 7 * 24 * 60 * 60 * 1000, // 7 days
            dataCacheDuration: 24 * 60 * 60 * 1000, // 24 hours
            compressionEnabled: true,
            smartCaching: true,
            preloadCriticalAssets: true
        };

        // Define offline capabilities
        this.offlineFeatures = {
            'content-editing': {
                enabled: true,
                description: 'Edit content locally',
                dependencies: ['local-storage', 'file-system']
            },
            'project-management': {
                enabled: true,
                description: 'Manage projects offline',
                dependencies: ['local-storage']
            },
            'audio-processing': {
                enabled: true,
                description: 'Process audio locally',
                dependencies: ['web-audio-api', 'file-system']
            },
            'video-preview': {
                enabled: true,
                description: 'Preview video content',
                dependencies: ['video-codec-support']
            },
            'ai-analysis': {
                enabled: false,
                description: 'AI content analysis',
                dependencies: ['cloud-services'],
                fallback: 'basic-local-analysis'
            },
            'collaboration': {
                enabled: false,
                description: 'Real-time collaboration',
                dependencies: ['websocket', 'cloud-services'],
                fallback: 'queue-for-sync'
            },
            'publishing': {
                enabled: false,
                description: 'Publish to platforms',
                dependencies: ['api-access'],
                fallback: 'queue-for-publishing'
            }
        };
    }

    async initialize() {
        console.log('📴 Initializing Offline Manager...');

        // Set up network status monitoring
        this.setupNetworkMonitoring();

        // Initialize offline storage
        await this.initializeOfflineStorage();

        // Check offline capabilities
        await this.checkOfflineCapabilities();

        // Load cached data
        await this.loadOfflineData();

        // Preload critical assets if enabled
        if (this.config.preloadCriticalAssets) {
            await this.preloadCriticalAssets();
        }

        // Set up storage management
        this.setupStorageManagement();

        console.log('✅ Offline Manager initialized');
        this.logOfflineStatus();
    }

    setupNetworkMonitoring() {
        // Network status event listeners
        window.addEventListener('online', () => {
            console.log('🌐 Back online');
            this.isOffline = false;
            this.handleOnlineEvent();
        });

        window.addEventListener('offline', () => {
            console.log('📴 Gone offline');
            this.isOffline = true;
            this.handleOfflineEvent();
        });

        // Periodic connectivity check (in case events don't fire)
        setInterval(() => {
            this.verifyConnectivity();
        }, 30000); // Check every 30 seconds
    }

    async verifyConnectivity() {
        try {
            // Try to fetch a small resource to verify real connectivity
            const response = await fetch('/api/ping', { 
                method: 'HEAD',
                cache: 'no-cache',
                timeout: 5000
            });
            
            const actuallyOnline = response.ok;
            
            if (actuallyOnline !== !this.isOffline) {
                this.isOffline = !actuallyOnline;
                if (actuallyOnline) {
                    this.handleOnlineEvent();
                } else {
                    this.handleOfflineEvent();
                }
            }
        } catch (error) {
            if (!this.isOffline) {
                this.isOffline = true;
                this.handleOfflineEvent();
            }
        }
    }

    async initializeOfflineStorage() {
        try {
            // Initialize IndexedDB for offline storage
            if ('indexedDB' in window) {
                await this.initializeIndexedDB();
            }

            // Check storage quota and usage
            if ('storage' in navigator && 'estimate' in navigator.storage) {
                const estimate = await navigator.storage.estimate();
                this.storageUsage = {
                    used: estimate.usage || 0,
                    available: (estimate.quota || 0) - (estimate.usage || 0),
                    quota: estimate.quota || 0
                };
            }

            console.log('💾 Offline storage initialized:', this.storageUsage);
        } catch (error) {
            console.error('Failed to initialize offline storage:', error);
        }
    }

    async initializeIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('AinfluuOfflineDB', 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.offlineDB = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores
                if (!db.objectStoreNames.contains('cache')) {
                    const cacheStore = db.createObjectStore('cache', { keyPath: 'key' });
                    cacheStore.createIndex('timestamp', 'timestamp');
                    cacheStore.createIndex('type', 'type');
                }

                if (!db.objectStoreNames.contains('queue')) {
                    const queueStore = db.createObjectStore('queue', { keyPath: 'id', autoIncrement: true });
                    queueStore.createIndex('priority', 'priority');
                    queueStore.createIndex('timestamp', 'timestamp');
                }

                if (!db.objectStoreNames.contains('assets')) {
                    const assetsStore = db.createObjectStore('assets', { keyPath: 'url' });
                    assetsStore.createIndex('lastAccessed', 'lastAccessed');
                    assetsStore.createIndex('size', 'size');
                }
            };
        });
    }

    async checkOfflineCapabilities() {
        this.offlineCapabilities.clear();

        for (const [feature, config] of Object.entries(this.offlineFeatures)) {
            const isSupported = await this.checkFeatureSupport(feature, config);
            if (isSupported) {
                this.offlineCapabilities.add(feature);
            }
        }

        console.log('🔧 Offline capabilities:', Array.from(this.offlineCapabilities));
    }

    async checkFeatureSupport(feature, config) {
        if (!config.enabled) return false;

        // Check feature dependencies
        for (const dependency of config.dependencies) {
            if (!await this.checkDependency(dependency)) {
                console.warn(`Feature ${feature} disabled: missing ${dependency}`);
                return false;
            }
        }

        return true;
    }

    async checkDependency(dependency) {
        switch (dependency) {
            case 'local-storage':
                return typeof Storage !== 'undefined';
            
            case 'file-system':
                return 'showOpenFilePicker' in window || window.electronAPI;
            
            case 'web-audio-api':
                return typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined';
            
            case 'video-codec-support':
                const video = document.createElement('video');
                return video.canPlayType('video/mp4') !== '';
            
            case 'websocket':
                return typeof WebSocket !== 'undefined';
            
            case 'cloud-services':
                return !this.isOffline;
            
            case 'api-access':
                return !this.isOffline;
            
            default:
                return true;
        }
    }

    async loadOfflineData() {
        try {
            // Load cached data from IndexedDB
            await this.loadFromIndexedDB('cache');
            await this.loadFromIndexedDB('queue');
            await this.loadFromIndexedDB('assets');

            // Load data from localStorage as fallback
            await this.loadFromLocalStorage();

            console.log(`📦 Loaded offline data: ${this.offlineCache.size} cached items, ${this.offlineQueue.length} queued actions`);
        } catch (error) {
            console.error('Failed to load offline data:', error);
        }
    }

    async loadFromIndexedDB(storeName) {
        if (!this.offlineDB) return;

        return new Promise((resolve, reject) => {
            const transaction = this.offlineDB.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => {
                const items = request.result;
                
                switch (storeName) {
                    case 'cache':
                        items.forEach(item => {
                            if (this.isCacheItemValid(item)) {
                                this.offlineCache.set(item.key, item);
                            }
                        });
                        break;
                    
                    case 'queue':
                        this.offlineQueue.push(...items);
                        break;
                    
                    case 'assets':
                        items.forEach(asset => {
                            if (this.isAssetValid(asset)) {
                                this.offlineAssets.set(asset.url, asset);
                            }
                        });
                        break;
                }
                
                resolve();
            };

            request.onerror = () => reject(request.error);
        });
    }

    async loadFromLocalStorage() {
        try {
            // Load queue from localStorage as backup
            const queueData = localStorage.getItem('ainflue-offline-queue');
            if (queueData) {
                const queue = JSON.parse(queueData);
                this.offlineQueue.push(...queue);
            }

            // Load cache keys from localStorage
            const cacheKeys = localStorage.getItem('ainflue-offline-cache-keys');
            if (cacheKeys) {
                const keys = JSON.parse(cacheKeys);
                for (const key of keys) {
                    const data = localStorage.getItem(`ainflue-cache-${key}`);
                    if (data) {
                        this.offlineCache.set(key, JSON.parse(data));
                    }
                }
            }
        } catch (error) {
            console.warn('Failed to load from localStorage:', error);
        }
    }

    async preloadCriticalAssets() {
        const criticalAssets = [
            '/renderer/index.html',
            '/renderer/styles/main.css',
            '/renderer/scripts/core.js',
            '/assets/icons/icon-192.png',
            '/assets/sounds/notification.mp3'
        ];

        console.log('⬇️ Preloading critical assets...');

        for (const asset of criticalAssets) {
            try {
                await this.cacheAsset(asset, 'critical');
            } catch (error) {
                console.warn(`Failed to preload asset ${asset}:`, error);
            }
        }

        console.log('✅ Critical assets preloaded');
    }

    async cacheAsset(url, priority = 'normal') {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const blob = await response.blob();
            const asset = {
                url,
                data: blob,
                type: response.headers.get('content-type'),
                size: blob.size,
                priority,
                cached: Date.now(),
                lastAccessed: Date.now()
            };

            this.offlineAssets.set(url, asset);
            await this.saveAssetToIndexedDB(asset);

            console.log(`📦 Cached asset: ${url} (${this.formatBytes(blob.size)})`);
            return asset;
        } catch (error) {
            console.error(`Failed to cache asset ${url}:`, error);
            throw error;
        }
    }

    setupStorageManagement() {
        // Monitor storage usage
        setInterval(() => {
            this.checkStorageUsage();
        }, 60000); // Check every minute

        // Clean up expired cache periodically
        setInterval(() => {
            this.cleanupExpiredCache();
        }, 5 * 60 * 1000); // Every 5 minutes
    }

    async checkStorageUsage() {
        try {
            if ('storage' in navigator && 'estimate' in navigator.storage) {
                const estimate = await navigator.storage.estimate();
                this.storageUsage = {
                    used: estimate.usage || 0,
                    available: (estimate.quota || 0) - (estimate.usage || 0),
                    quota: estimate.quota || 0
                };

                // Clean up if approaching quota
                const usagePercentage = (this.storageUsage.used / this.storageUsage.quota) * 100;
                if (usagePercentage > 80) {
                    console.warn('⚠️ Storage usage high:', usagePercentage.toFixed(1) + '%');
                    await this.cleanupOldCache();
                }
            }
        } catch (error) {
            console.error('Failed to check storage usage:', error);
        }
    }

    async cleanupExpiredCache() {
        const now = Date.now();
        let cleaned = 0;

        // Clean expired cache entries
        for (const [key, item] of this.offlineCache) {
            if (this.isCacheExpired(item, now)) {
                this.offlineCache.delete(key);
                await this.removeFromIndexedDB('cache', key);
                cleaned++;
            }
        }

        // Clean expired assets
        for (const [url, asset] of this.offlineAssets) {
            if (this.isAssetExpired(asset, now)) {
                this.offlineAssets.delete(url);
                await this.removeFromIndexedDB('assets', url);
                cleaned++;
            }
        }

        if (cleaned > 0) {
            console.log(`🧹 Cleaned up ${cleaned} expired cache entries`);
        }
    }

    async cleanupOldCache() {
        console.log('🧹 Starting aggressive cache cleanup...');

        // Sort assets by last accessed time and size
        const sortedAssets = Array.from(this.offlineAssets.entries())
            .sort(([,a], [,b]) => {
                // Prioritize by last accessed time, then by size
                const timeDiff = a.lastAccessed - b.lastAccessed;
                if (timeDiff !== 0) return timeDiff;
                return b.size - a.size; // Larger files first for removal
            });

        // Remove oldest/largest assets until we free up 25% of quota
        const targetSize = this.storageUsage.quota * 0.25;
        let freedSpace = 0;
        let removed = 0;

        for (const [url, asset] of sortedAssets) {
            if (asset.priority === 'critical') continue; // Don't remove critical assets
            
            this.offlineAssets.delete(url);
            await this.removeFromIndexedDB('assets', url);
            
            freedSpace += asset.size;
            removed++;
            
            if (freedSpace >= targetSize) break;
        }

        console.log(`🧹 Aggressive cleanup completed: removed ${removed} assets, freed ${this.formatBytes(freedSpace)}`);
    }

    handleOnlineEvent() {
        console.log('🔄 Processing offline queue...');
        
        // Process queued actions
        this.processOfflineQueue();
        
        // Sync pending changes
        this.syncPendingChanges();
        
        // Notify listeners
        this.notifyStatusChange('online');
    }

    handleOfflineEvent() {
        console.log('📴 Switched to offline mode');
        
        // Notify listeners
        this.notifyStatusChange('offline');
        
        // Show offline notification
        this.showOfflineNotification();
    }

    async processOfflineQueue() {
        if (this.offlineQueue.length === 0) return;

        console.log(`🔄 Processing ${this.offlineQueue.length} queued actions`);

        // Sort queue by priority and timestamp
        this.offlineQueue.sort((a, b) => {
            const priorityOrder = { high: 3, normal: 2, low: 1 };
            const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
            if (priorityDiff !== 0) return priorityDiff;
            return a.timestamp - b.timestamp;
        });

        const processed = [];
        const failed = [];

        for (const action of this.offlineQueue) {
            try {
                await this.processQueuedAction(action);
                processed.push(action);
            } catch (error) {
                console.error(`Failed to process queued action:`, error);
                action.retries = (action.retries || 0) + 1;
                
                if (action.retries >= 3) {
                    failed.push(action);
                } else {
                    // Keep in queue for retry
                    continue;
                }
            }
        }

        // Remove processed and failed actions from queue
        this.offlineQueue = this.offlineQueue.filter(action => 
            !processed.includes(action) && !failed.includes(action)
        );

        console.log(`✅ Processed ${processed.length} actions, ${failed.length} failed, ${this.offlineQueue.length} remaining`);
        
        // Save updated queue
        await this.saveOfflineQueue();
    }

    async processQueuedAction(action) {
        switch (action.type) {
            case 'api-call':
                return await this.retryAPICall(action);
            
            case 'file-upload':
                return await this.retryFileUpload(action);
            
            case 'publish-content':
                return await this.retryPublishContent(action);
            
            case 'sync-data':
                return await this.retrySyncData(action);
            
            default:
                console.warn(`Unknown action type: ${action.type}`);
        }
    }

    // Public API methods
    async queueAction(type, data, priority = 'normal') {
        const action = {
            id: Date.now() + Math.random(),
            type,
            data,
            priority,
            timestamp: Date.now(),
            retries: 0
        };

        this.offlineQueue.push(action);
        await this.saveOfflineQueue();

        console.log(`📝 Queued action: ${type} (priority: ${priority})`);

        // If online, try to process immediately
        if (!this.isOffline) {
            try {
                await this.processQueuedAction(action);
                this.offlineQueue = this.offlineQueue.filter(a => a.id !== action.id);
                await this.saveOfflineQueue();
            } catch (error) {
                console.warn('Failed to process action immediately:', error);
            }
        }

        return action.id;
    }

    async cacheData(key, data, options = {}) {
        const cacheItem = {
            key,
            data,
            timestamp: Date.now(),
            type: options.type || 'generic',
            priority: options.priority || 'normal',
            expires: options.expires || (Date.now() + this.config.dataCacheDuration)
        };

        this.offlineCache.set(key, cacheItem);
        await this.saveCacheToIndexedDB(cacheItem);

        console.log(`💾 Cached data: ${key}`);
    }

    getCachedData(key) {
        const item = this.offlineCache.get(key);
        if (!item) return null;

        if (this.isCacheExpired(item)) {
            this.offlineCache.delete(key);
            this.removeFromIndexedDB('cache', key);
            return null;
        }

        return item.data;
    }

    isFeatureAvailable(feature) {
        return this.offlineCapabilities.has(feature);
    }

    getAvailableFeatures() {
        return Array.from(this.offlineCapabilities);
    }

    getUnavailableFeatures() {
        const unavailable = [];
        for (const [feature, config] of Object.entries(this.offlineFeatures)) {
            if (!this.offlineCapabilities.has(feature)) {
                unavailable.push({
                    feature,
                    description: config.description,
                    fallback: config.fallback || null
                });
            }
        }
        return unavailable;
    }

    // Helper methods
    isCacheItemValid(item) {
        return item && item.timestamp && !this.isCacheExpired(item);
    }

    isCacheExpired(item, now = Date.now()) {
        return item.expires && now > item.expires;
    }

    isAssetValid(asset) {
        return asset && asset.cached && !this.isAssetExpired(asset);
    }

    isAssetExpired(asset, now = Date.now()) {
        return (now - asset.cached) > this.config.assetCacheDuration;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async saveOfflineQueue() {
        try {
            if (this.offlineDB) {
                await this.saveToIndexedDB('queue', this.offlineQueue);
            }
            localStorage.setItem('ainflue-offline-queue', JSON.stringify(this.offlineQueue));
        } catch (error) {
            console.error('Failed to save offline queue:', error);
        }
    }

    async saveCacheToIndexedDB(item) {
        if (!this.offlineDB) return;
        
        return new Promise((resolve, reject) => {
            const transaction = this.offlineDB.transaction(['cache'], 'readwrite');
            const store = transaction.objectStore('cache');
            const request = store.put(item);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async saveAssetToIndexedDB(asset) {
        if (!this.offlineDB) return;
        
        return new Promise((resolve, reject) => {
            const transaction = this.offlineDB.transaction(['assets'], 'readwrite');
            const store = transaction.objectStore('assets');
            const request = store.put(asset);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async removeFromIndexedDB(storeName, key) {
        if (!this.offlineDB) return;
        
        return new Promise((resolve, reject) => {
            const transaction = this.offlineDB.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    notifyStatusChange(status) {
        window.dispatchEvent(new CustomEvent('offline-status-changed', {
            detail: { status, capabilities: this.getAvailableFeatures() }
        }));
    }

    showOfflineNotification() {
        const notification = {
            title: 'Offline Mode',
            message: 'Working offline. Some features are limited.',
            type: 'info',
            persistent: true
        };

        window.dispatchEvent(new CustomEvent('show-notification', { detail: notification }));
    }

    logOfflineStatus() {
        console.log('📴 Offline Manager Status:');
        console.log(`  • Network: ${this.isOffline ? 'Offline' : 'Online'}`);
        console.log(`  • Cache size: ${this.offlineCache.size} items`);
        console.log(`  • Queue size: ${this.offlineQueue.length} actions`);
        console.log(`  • Assets: ${this.offlineAssets.size} cached`);
        console.log(`  • Storage: ${this.formatBytes(this.storageUsage.used)} / ${this.formatBytes(this.storageUsage.quota)}`);
        console.log(`  • Available features: ${this.getAvailableFeatures().join(', ')}`);
    }

    // Status and health methods
    getOfflineStatus() {
        return {
            isOffline: this.isOffline,
            queueSize: this.offlineQueue.length,
            cacheSize: this.offlineCache.size,
            assetsCount: this.offlineAssets.size,
            storageUsage: this.storageUsage,
            availableFeatures: this.getAvailableFeatures(),
            unavailableFeatures: this.getUnavailableFeatures()
        };
    }

    isHealthy() {
        return this.offlineCapabilities.size > 0 && this.storageUsage.available > 10 * 1024 * 1024; // 10MB minimum
    }
}

export default OfflineManager;