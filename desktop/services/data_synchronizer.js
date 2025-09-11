/**
 * Ainflue Desktop - Data Synchronizer Service
 * 
 * Handles real-time data synchronization between desktop app and cloud services,
 * offline support, conflict resolution, and data integrity management.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class DataSynchronizer {
    constructor() {
        this.syncQueue = [];
        this.isOnline = navigator.onLine;
        this.isSyncing = false;
        this.lastSyncTime = null;
        this.syncInterval = 30000; // 30 seconds
        this.conflicts = [];
        this.pendingChanges = new Map();
        this.watchedCollections = new Set();
        this.syncListeners = new Map();
        
        this.config = {
            maxRetries: 3,
            batchSize: 10,
            syncTimeout: 30000,
            conflictResolution: 'client-wins', // 'client-wins', 'server-wins', 'manual'
            enableRealTime: true,
            compressionEnabled: true
        };

        // Data collections that need synchronization
        this.collections = {
            projects: {
                local: 'desktop-projects',
                remote: 'projects',
                priority: 'high',
                syncDirection: 'bidirectional',
                conflictFields: ['title', 'content', 'settings'],
                lastModified: null
            },
            content: {
                local: 'desktop-content',
                remote: 'content',
                priority: 'high',
                syncDirection: 'bidirectional',
                conflictFields: ['metadata', 'tags', 'processing_status'],
                lastModified: null
            },
            analytics: {
                local: 'desktop-analytics',
                remote: 'analytics',
                priority: 'medium',
                syncDirection: 'download',
                conflictFields: [],
                lastModified: null
            },
            preferences: {
                local: 'desktop-preferences',
                remote: 'user_preferences',
                priority: 'low',
                syncDirection: 'upload',
                conflictFields: ['theme', 'shortcuts', 'workspace'],
                lastModified: null
            },
            collaboration: {
                local: 'desktop-collaboration',
                remote: 'collaboration',
                priority: 'high',
                syncDirection: 'bidirectional',
                conflictFields: ['comments', 'reviews', 'shared_projects'],
                lastModified: null
            }
        };
    }

    async initialize() {
        console.log('🔄 Initializing Data Synchronizer...');

        // Set up online/offline detection
        this.setupNetworkListeners();

        // Load pending changes from storage
        await this.loadPendingChanges();

        // Initialize watched collections
        this.initializeWatchedCollections();

        // Start sync scheduler
        this.startSyncScheduler();

        // Set up real-time sync if enabled
        if (this.config.enableRealTime) {
            await this.setupRealTimeSync();
        }

        // Perform initial sync if online
        if (this.isOnline) {
            await this.performFullSync();
        }

        console.log('✅ Data Synchronizer initialized');
    }

    setupNetworkListeners() {
        window.addEventListener('online', () => {
            console.log('🌐 Back online - resuming sync');
            this.isOnline = true;
            this.resumeSync();
        });

        window.addEventListener('offline', () => {
            console.log('📴 Gone offline - queuing changes');
            this.isOnline = false;
            this.pauseSync();
        });
    }

    async loadPendingChanges() {
        try {
            if (window.electronAPI) {
                const pending = await window.electronAPI.invoke('store-get', 'pending-sync-changes');
                if (pending) {
                    this.pendingChanges = new Map(Object.entries(pending));
                    console.log(`📋 Loaded ${this.pendingChanges.size} pending changes`);
                }
            }
        } catch (error) {
            console.warn('Failed to load pending changes:', error);
        }
    }

    async savePendingChanges() {
        try {
            if (window.electronAPI) {
                const pendingObject = Object.fromEntries(this.pendingChanges);
                await window.electronAPI.invoke('store-set', 'pending-sync-changes', pendingObject);
            }
        } catch (error) {
            console.error('Failed to save pending changes:', error);
        }
    }

    initializeWatchedCollections() {
        for (const collectionName of Object.keys(this.collections)) {
            this.watchCollection(collectionName);
        }
    }

    watchCollection(collectionName) {
        if (this.watchedCollections.has(collectionName)) return;

        this.watchedCollections.add(collectionName);
        
        // Set up change detection for the collection
        const collection = this.collections[collectionName];
        if (collection) {
            // Mock change detection - in production this would use proper observers
            console.log(`👁️ Watching collection: ${collectionName}`);
        }
    }

    startSyncScheduler() {
        if (this.syncScheduler) return;

        this.syncScheduler = setInterval(async () => {
            if (this.isOnline && !this.isSyncing) {
                await this.performIncrementalSync();
            }
        }, this.syncInterval);

        console.log('⏰ Sync scheduler started');
    }

    stopSyncScheduler() {
        if (this.syncScheduler) {
            clearInterval(this.syncScheduler);
            this.syncScheduler = null;
            console.log('⏸️ Sync scheduler stopped');
        }
    }

    async setupRealTimeSync() {
        try {
            // Mock WebSocket setup for real-time sync
            console.log('🔄 Setting up real-time sync...');
            
            // In production, this would establish WebSocket connection
            this.realTimeConnection = {
                connected: true,
                lastPing: Date.now()
            };

            console.log('✅ Real-time sync established');
        } catch (error) {
            console.warn('Failed to setup real-time sync:', error);
        }
    }

    async performFullSync() {
        if (this.isSyncing) {
            console.log('⏳ Sync already in progress');
            return;
        }

        console.log('🔄 Starting full synchronization...');
        this.isSyncing = true;

        try {
            // Sync all collections by priority
            const sortedCollections = Object.entries(this.collections)
                .sort(([,a], [,b]) => this.getPriorityOrder(a.priority) - this.getPriorityOrder(b.priority));

            for (const [name, config] of sortedCollections) {
                await this.syncCollection(name, config);
            }

            // Process pending changes
            await this.processPendingChanges();

            this.lastSyncTime = new Date();
            console.log('✅ Full synchronization completed');

            // Notify listeners
            this.notifySyncListeners('full-sync-complete', { timestamp: this.lastSyncTime });

        } catch (error) {
            console.error('❌ Full sync failed:', error);
            throw error;
        } finally {
            this.isSyncing = false;
        }
    }

    async performIncrementalSync() {
        if (this.isSyncing) return;

        console.log('🔄 Starting incremental sync...');
        this.isSyncing = true;

        try {
            // Only sync collections with changes
            const changedCollections = this.getChangedCollections();
            
            for (const collectionName of changedCollections) {
                const config = this.collections[collectionName];
                await this.syncCollection(collectionName, config, true);
            }

            // Process any pending changes
            if (this.pendingChanges.size > 0) {
                await this.processPendingChanges();
            }

            this.lastSyncTime = new Date();
            console.log('✅ Incremental sync completed');

        } catch (error) {
            console.warn('⚠️ Incremental sync failed:', error);
        } finally {
            this.isSyncing = false;
        }
    }

    async syncCollection(collectionName, config, incremental = false) {
        console.log(`🔄 Syncing collection: ${collectionName}`);

        try {
            switch (config.syncDirection) {
                case 'bidirectional':
                    await this.syncBidirectional(collectionName, config, incremental);
                    break;
                case 'upload':
                    await this.syncUpload(collectionName, config, incremental);
                    break;
                case 'download':
                    await this.syncDownload(collectionName, config, incremental);
                    break;
            }

            config.lastModified = new Date();
            console.log(`✅ Synced collection: ${collectionName}`);

        } catch (error) {
            console.error(`❌ Failed to sync collection ${collectionName}:`, error);
            throw error;
        }
    }

    async syncBidirectional(collectionName, config, incremental) {
        // Get local and remote data
        const localData = await this.getLocalData(config.local, incremental);
        const remoteData = await this.getRemoteData(config.remote, incremental);

        // Detect conflicts
        const conflicts = this.detectConflicts(localData, remoteData, config.conflictFields);
        
        if (conflicts.length > 0) {
            await this.resolveConflicts(collectionName, conflicts);
        }

        // Merge and sync data
        const mergedData = this.mergeData(localData, remoteData);
        
        // Upload local changes
        const localChanges = this.getLocalChanges(localData, remoteData);
        if (localChanges.length > 0) {
            await this.uploadChanges(config.remote, localChanges);
        }

        // Download remote changes
        const remoteChanges = this.getRemoteChanges(remoteData, localData);
        if (remoteChanges.length > 0) {
            await this.downloadChanges(config.local, remoteChanges);
        }
    }

    async syncUpload(collectionName, config, incremental) {
        const localData = await this.getLocalData(config.local, incremental);
        const localChanges = this.getLocalChanges(localData, []);
        
        if (localChanges.length > 0) {
            await this.uploadChanges(config.remote, localChanges);
        }
    }

    async syncDownload(collectionName, config, incremental) {
        const remoteData = await this.getRemoteData(config.remote, incremental);
        const remoteChanges = this.getRemoteChanges(remoteData, []);
        
        if (remoteChanges.length > 0) {
            await this.downloadChanges(config.local, remoteChanges);
        }
    }

    async getLocalData(collection, incremental = false) {
        try {
            if (window.electronAPI) {
                const data = await window.electronAPI.invoke('store-get', collection);
                return data || [];
            }
            return [];
        } catch (error) {
            console.error(`Failed to get local data for ${collection}:`, error);
            return [];
        }
    }

    async getRemoteData(collection, incremental = false) {
        try {
            // Mock remote data fetch - in production this would use APIAggregator
            const mockData = [
                {
                    id: 'remote-1',
                    name: 'Remote Item 1',
                    lastModified: new Date(Date.now() - 60000).toISOString(),
                    data: { content: 'remote content 1' }
                },
                {
                    id: 'remote-2',
                    name: 'Remote Item 2',
                    lastModified: new Date().toISOString(),
                    data: { content: 'remote content 2' }
                }
            ];

            return mockData;
        } catch (error) {
            console.error(`Failed to get remote data for ${collection}:`, error);
            return [];
        }
    }

    detectConflicts(localData, remoteData, conflictFields) {
        const conflicts = [];
        
        // Create lookup maps
        const localMap = new Map(localData.map(item => [item.id, item]));
        const remoteMap = new Map(remoteData.map(item => [item.id, item]));

        // Check for conflicts
        for (const [id, localItem] of localMap) {
            const remoteItem = remoteMap.get(id);
            if (remoteItem) {
                const hasConflict = this.hasFieldConflicts(localItem, remoteItem, conflictFields);
                if (hasConflict) {
                    conflicts.push({
                        id,
                        localItem,
                        remoteItem,
                        conflictFields: this.getConflictingFields(localItem, remoteItem, conflictFields)
                    });
                }
            }
        }

        return conflicts;
    }

    hasFieldConflicts(localItem, remoteItem, conflictFields) {
        const localModified = new Date(localItem.lastModified);
        const remoteModified = new Date(remoteItem.lastModified);
        
        // If modification times are very close (within 1 second), consider no conflict
        if (Math.abs(localModified - remoteModified) < 1000) {
            return false;
        }

        // Check specific fields for conflicts
        for (const field of conflictFields) {
            if (this.getNestedValue(localItem, field) !== this.getNestedValue(remoteItem, field)) {
                return true;
            }
        }

        return false;
    }

    getConflictingFields(localItem, remoteItem, conflictFields) {
        const conflicting = [];
        
        for (const field of conflictFields) {
            if (this.getNestedValue(localItem, field) !== this.getNestedValue(remoteItem, field)) {
                conflicting.push(field);
            }
        }

        return conflicting;
    }

    async resolveConflicts(collectionName, conflicts) {
        console.log(`⚔️ Resolving ${conflicts.length} conflicts for ${collectionName}`);

        for (const conflict of conflicts) {
            const resolution = await this.resolveConflict(conflict);
            await this.applyConflictResolution(collectionName, conflict, resolution);
        }
    }

    async resolveConflict(conflict) {
        switch (this.config.conflictResolution) {
            case 'client-wins':
                return { winner: 'local', data: conflict.localItem };
            
            case 'server-wins':
                return { winner: 'remote', data: conflict.remoteItem };
            
            case 'manual':
                return await this.requestManualResolution(conflict);
            
            default:
                // Default to newer timestamp
                const localTime = new Date(conflict.localItem.lastModified);
                const remoteTime = new Date(conflict.remoteItem.lastModified);
                
                if (localTime > remoteTime) {
                    return { winner: 'local', data: conflict.localItem };
                } else {
                    return { winner: 'remote', data: conflict.remoteItem };
                }
        }
    }

    async requestManualResolution(conflict) {
        // In production, this would show a UI for manual conflict resolution
        console.log('🤔 Manual conflict resolution required:', conflict);
        
        // For now, return the newer item
        const localTime = new Date(conflict.localItem.lastModified);
        const remoteTime = new Date(conflict.remoteItem.lastModified);
        
        return localTime > remoteTime 
            ? { winner: 'local', data: conflict.localItem }
            : { winner: 'remote', data: conflict.remoteItem };
    }

    async applyConflictResolution(collectionName, conflict, resolution) {
        // Store conflict resolution for audit trail
        this.conflicts.push({
            timestamp: new Date(),
            collection: collectionName,
            conflictId: conflict.id,
            resolution: resolution.winner,
            resolvedData: resolution.data
        });

        console.log(`✅ Resolved conflict for ${conflict.id}: ${resolution.winner} wins`);
    }

    mergeData(localData, remoteData) {
        const merged = new Map();
        
        // Add all local items
        for (const item of localData) {
            merged.set(item.id, { ...item, source: 'local' });
        }

        // Add or update with remote items
        for (const item of remoteData) {
            const existing = merged.get(item.id);
            if (!existing || new Date(item.lastModified) > new Date(existing.lastModified)) {
                merged.set(item.id, { ...item, source: 'remote' });
            }
        }

        return Array.from(merged.values());
    }

    getLocalChanges(localData, remoteData) {
        const remoteMap = new Map(remoteData.map(item => [item.id, item]));
        const changes = [];

        for (const localItem of localData) {
            const remoteItem = remoteMap.get(localItem.id);
            
            if (!remoteItem || new Date(localItem.lastModified) > new Date(remoteItem.lastModified)) {
                changes.push({
                    operation: remoteItem ? 'update' : 'create',
                    data: localItem
                });
            }
        }

        return changes;
    }

    getRemoteChanges(remoteData, localData) {
        const localMap = new Map(localData.map(item => [item.id, item]));
        const changes = [];

        for (const remoteItem of remoteData) {
            const localItem = localMap.get(remoteItem.id);
            
            if (!localItem || new Date(remoteItem.lastModified) > new Date(localItem.lastModified)) {
                changes.push({
                    operation: localItem ? 'update' : 'create',
                    data: remoteItem
                });
            }
        }

        return changes;
    }

    async uploadChanges(remoteCollection, changes) {
        console.log(`⬆️ Uploading ${changes.length} changes to ${remoteCollection}`);

        for (const change of changes) {
            try {
                // Mock upload - in production this would use APIAggregator
                console.log(`⬆️ ${change.operation}: ${change.data.id}`);
                await this.sleep(100); // Simulate network delay
            } catch (error) {
                console.error(`Failed to upload change:`, error);
                // Add to pending changes for retry
                this.addToPendingChanges(`upload-${change.data.id}`, change);
            }
        }
    }

    async downloadChanges(localCollection, changes) {
        console.log(`⬇️ Downloading ${changes.length} changes to ${localCollection}`);

        for (const change of changes) {
            try {
                // Mock download - in production this would update local storage
                console.log(`⬇️ ${change.operation}: ${change.data.id}`);
                await this.sleep(100); // Simulate processing delay
            } catch (error) {
                console.error(`Failed to download change:`, error);
            }
        }
    }

    async processPendingChanges() {
        if (this.pendingChanges.size === 0) return;

        console.log(`🔄 Processing ${this.pendingChanges.size} pending changes`);

        const toRemove = [];

        for (const [changeId, change] of this.pendingChanges) {
            try {
                await this.processPendingChange(change);
                toRemove.push(changeId);
            } catch (error) {
                console.warn(`Failed to process pending change ${changeId}:`, error);
                // Increment retry count
                change.retries = (change.retries || 0) + 1;
                
                if (change.retries >= this.config.maxRetries) {
                    console.error(`Giving up on pending change ${changeId} after ${change.retries} retries`);
                    toRemove.push(changeId);
                }
            }
        }

        // Remove processed changes
        for (const changeId of toRemove) {
            this.pendingChanges.delete(changeId);
        }

        if (toRemove.length > 0) {
            await this.savePendingChanges();
        }
    }

    async processPendingChange(change) {
        // Process the pending change based on its type
        console.log(`🔄 Processing pending change: ${change.operation}`);
        await this.sleep(100); // Simulate processing
    }

    addToPendingChanges(changeId, change) {
        this.pendingChanges.set(changeId, {
            ...change,
            timestamp: new Date(),
            retries: 0
        });
        this.savePendingChanges();
    }

    getChangedCollections() {
        // Mock implementation - in production this would track actual changes
        return Object.keys(this.collections);
    }

    getPriorityOrder(priority) {
        const order = { high: 1, medium: 2, low: 3 };
        return order[priority] || 999;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }

    // Public API methods
    async queueChange(collection, operation, data) {
        const changeId = `${collection}-${operation}-${Date.now()}`;
        const change = {
            collection,
            operation,
            data,
            timestamp: new Date()
        };

        if (this.isOnline) {
            // Process immediately if online
            try {
                await this.processPendingChange(change);
            } catch (error) {
                this.addToPendingChanges(changeId, change);
            }
        } else {
            // Queue for later if offline
            this.addToPendingChanges(changeId, change);
        }
    }

    async forcSync() {
        if (this.isOnline) {
            await this.performFullSync();
        } else {
            throw new Error('Cannot sync while offline');
        }
    }

    subscribeSyncEvents(callback) {
        const listenerId = Date.now().toString();
        this.syncListeners.set(listenerId, callback);
        return () => this.syncListeners.delete(listenerId);
    }

    notifySyncListeners(event, data) {
        for (const callback of this.syncListeners.values()) {
            try {
                callback(event, data);
            } catch (error) {
                console.error('Error in sync listener:', error);
            }
        }
    }

    resumeSync() {
        if (this.isOnline && this.pendingChanges.size > 0) {
            this.processPendingChanges();
        }
    }

    pauseSync() {
        // Sync is automatically paused when offline
        console.log('⏸️ Sync paused - offline mode');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Status and health methods
    getSyncStatus() {
        return {
            isOnline: this.isOnline,
            isSyncing: this.isSyncing,
            lastSyncTime: this.lastSyncTime,
            pendingChanges: this.pendingChanges.size,
            conflicts: this.conflicts.length,
            collections: Object.keys(this.collections),
            realTimeConnected: this.realTimeConnection?.connected || false
        };
    }

    getConflictHistory() {
        return [...this.conflicts];
    }

    isHealthy() {
        return this.watchedCollections.size > 0 && (this.isOnline || this.pendingChanges.size < 100);
    }
}

export default DataSynchronizer;