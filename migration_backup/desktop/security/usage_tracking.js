/**
 * Ainflue Desktop - Usage Tracking System
 * 
 * Comprehensive usage tracking for copyright compliance, licensing enforcement,
 * and detailed analytics with privacy-compliant data collection.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class UsageTrackingSystem {
    constructor() {
        this.trackingData = new Map();
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        this.trackingEnabled = true;
        this.privacyMode = false;
        this.dataRetentionDays = 365;
        this.batchSize = 50;
        this.flushInterval = 60000; // 1 minute

        this.config = {
            trackUserActions: true,
            trackContentUsage: true,
            trackSystemMetrics: true,
            trackPerformance: true,
            enableAnalytics: true,
            anonymizeData: false,
            localStorageOnly: false
        };

        // Define tracking categories
        this.categories = {
            content: {
                enabled: true,
                events: ['create', 'edit', 'delete', 'export', 'share', 'process'],
                retention: 730 // 2 years for content tracking
            },
            user: {
                enabled: true,
                events: ['login', 'logout', 'action', 'preference_change'],
                retention: 365 // 1 year for user actions
            },
            system: {
                enabled: true,
                events: ['startup', 'shutdown', 'error', 'performance'],
                retention: 90 // 3 months for system events
            },
            license: {
                enabled: true,
                events: ['check', 'validate', 'violation', 'renewal'],
                retention: 2555 // 7 years for legal compliance
            },
            usage: {
                enabled: true,
                events: ['feature_use', 'time_spent', 'frequency'],
                retention: 365 // 1 year for usage analytics
            }
        };

        this.pendingEvents = [];
        this.eventQueue = [];
    }

    async initialize() {
        console.log('📊 Initializing Usage Tracking System...');

        // Load configuration
        await this.loadConfiguration();

        // Initialize tracking storage
        await this.initializeStorage();

        // Set up automatic flushing
        this.setupAutoFlush();

        // Load existing tracking data
        await this.loadTrackingData();

        // Start session tracking
        await this.startSession();

        // Set up cleanup scheduler
        this.setupCleanupScheduler();

        console.log('✅ Usage Tracking System initialized');
    }

    async loadConfiguration() {
        try {
            if (window.electronAPI) {
                const config = await window.electronAPI.invoke('store-get', 'usage-tracking-config');
                if (config) {
                    Object.assign(this.config, config);
                }

                // Check privacy preferences
                const privacy = await window.electronAPI.invoke('store-get', 'privacy-preferences');
                if (privacy) {
                    this.privacyMode = privacy.strictMode || false;
                    this.config.anonymizeData = privacy.anonymizeData || false;
                }
            }
        } catch (error) {
            console.warn('Failed to load tracking configuration:', error);
        }
    }

    async initializeStorage() {
        // Initialize secure storage for tracking data
        try {
            this.storage = {
                local: new Map(),
                persistent: null
            };

            // Initialize IndexedDB for persistent storage
            if (!this.config.localStorageOnly) {
                await this.initializeIndexedDB();
            }
        } catch (error) {
            console.error('Failed to initialize tracking storage:', error);
        }
    }

    async initializeIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('AinfluueUsageTracking', 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.storage.persistent = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores for different tracking categories
                for (const category of Object.keys(this.categories)) {
                    if (!db.objectStoreNames.contains(category)) {
                        const store = db.createObjectStore(category, { keyPath: 'id', autoIncrement: true });
                        store.createIndex('timestamp', 'timestamp');
                        store.createIndex('sessionId', 'sessionId');
                        store.createIndex('userId', 'userId');
                        store.createIndex('event', 'event');
                    }
                }

                // Create sessions store
                if (!db.objectStoreNames.contains('sessions')) {
                    const sessionsStore = db.createObjectStore('sessions', { keyPath: 'sessionId' });
                    sessionsStore.createIndex('startTime', 'startTime');
                    sessionsStore.createIndex('endTime', 'endTime');
                }
            };
        });
    }

    setupAutoFlush() {
        this.flushTimer = setInterval(() => {
            this.flushPendingEvents();
        }, this.flushInterval);
    }

    setupCleanupScheduler() {
        // Clean up old data daily
        this.cleanupTimer = setInterval(() => {
            this.cleanupExpiredData();
        }, 24 * 60 * 60 * 1000); // Daily
    }

    async loadTrackingData() {
        try {
            // Load recent tracking data for analysis
            const recentData = await this.getRecentTrackingData(7); // Last 7 days
            console.log(`📊 Loaded ${recentData.length} recent tracking events`);
        } catch (error) {
            console.warn('Failed to load tracking data:', error);
        }
    }

    async startSession() {
        const session = {
            sessionId: this.sessionId,
            startTime: this.startTime,
            platform: this.getPlatformInfo(),
            version: await this.getAppVersion(),
            userId: await this.getUserId(),
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };

        await this.saveSession(session);
        
        // Track session start event
        await this.trackEvent('system', 'startup', {
            sessionId: this.sessionId,
            platform: session.platform
        });

        console.log(`📊 Started tracking session: ${this.sessionId}`);
    }

    async trackEvent(category, event, data = {}, options = {}) {
        if (!this.trackingEnabled || !this.categories[category]?.enabled) {
            return null;
        }

        const trackingEvent = {
            id: this.generateEventId(),
            category,
            event,
            data: this.sanitizeData(data),
            timestamp: Date.now(),
            sessionId: this.sessionId,
            userId: await this.getUserId(),
            userAgent: this.config.anonymizeData ? null : navigator.userAgent,
            url: this.config.anonymizeData ? null : window.location.href,
            ...options
        };

        // Add to pending events
        this.pendingEvents.push(trackingEvent);

        // Immediate flush for critical events
        if (options.immediate || this.isCriticalEvent(category, event)) {
            await this.flushPendingEvents();
        }

        console.debug(`📊 Tracked: ${category}.${event}`, data);
        return trackingEvent.id;
    }

    async trackContentUsage(contentId, action, metadata = {}) {
        if (!this.config.trackContentUsage) return;

        const usageData = {
            contentId,
            action,
            contentType: metadata.type,
            fileSize: metadata.size,
            duration: metadata.duration,
            format: metadata.format,
            processingTime: metadata.processingTime,
            aiUsed: metadata.aiProcessing || false
        };

        return await this.trackEvent('content', action, usageData);
    }

    async trackUserAction(action, details = {}) {
        if (!this.config.trackUserActions) return;

        const actionData = {
            action,
            context: details.context || 'unknown',
            feature: details.feature,
            duration: details.duration,
            success: details.success !== false,
            errorCode: details.errorCode
        };

        return await this.trackEvent('user', 'action', actionData);
    }

    async trackSystemMetrics(metrics) {
        if (!this.config.trackSystemMetrics) return;

        const systemData = {
            cpuUsage: metrics.cpu,
            memoryUsage: metrics.memory,
            diskSpace: metrics.disk,
            networkStatus: metrics.network,
            performanceScore: metrics.performance
        };

        return await this.trackEvent('system', 'performance', systemData);
    }

    async trackLicenseEvent(event, licenseInfo = {}) {
        const licenseData = {
            event,
            licenseType: licenseInfo.type,
            expiryDate: licenseInfo.expiry,
            features: licenseInfo.features,
            userId: licenseInfo.userId,
            validationResult: licenseInfo.valid
        };

        return await this.trackEvent('license', event, licenseData, { immediate: true });
    }

    async trackFeatureUsage(feature, usage = {}) {
        if (!this.config.enableAnalytics) return;

        const featureData = {
            feature,
            timeSpent: usage.timeSpent || 0,
            actionsPerformed: usage.actions || 1,
            frequency: usage.frequency || 'first-time',
            satisfaction: usage.satisfaction,
            errors: usage.errors || 0
        };

        return await this.trackEvent('usage', 'feature_use', featureData);
    }

    async flushPendingEvents() {
        if (this.pendingEvents.length === 0) return;

        const eventsToFlush = this.pendingEvents.splice(0, this.batchSize);
        
        try {
            // Save to persistent storage
            await this.saveEvents(eventsToFlush);

            // Send to analytics service if enabled and online
            if (this.config.enableAnalytics && navigator.onLine && !this.config.localStorageOnly) {
                await this.sendToAnalytics(eventsToFlush);
            }

            console.debug(`📊 Flushed ${eventsToFlush.length} tracking events`);
        } catch (error) {
            console.error('Failed to flush tracking events:', error);
            // Put events back in queue for retry
            this.pendingEvents.unshift(...eventsToFlush);
        }
    }

    async saveEvents(events) {
        // Save to local storage
        for (const event of events) {
            this.trackingData.set(event.id, event);
        }

        // Save to IndexedDB
        if (this.storage.persistent) {
            await this.saveEventsToIndexedDB(events);
        }

        // Save to localStorage as backup
        await this.saveEventsToLocalStorage(events);
    }

    async saveEventsToIndexedDB(events) {
        if (!this.storage.persistent) return;

        const promises = [];

        for (const event of events) {
            const promise = new Promise((resolve, reject) => {
                const transaction = this.storage.persistent.transaction([event.category], 'readwrite');
                const store = transaction.objectStore(event.category);
                const request = store.add(event);

                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            });

            promises.push(promise);
        }

        await Promise.all(promises);
    }

    async saveEventsToLocalStorage(events) {
        try {
            const existingEvents = JSON.parse(localStorage.getItem('ainflue-tracking-events') || '[]');
            const allEvents = [...existingEvents, ...events];
            
            // Keep only recent events in localStorage (last 1000)
            const recentEvents = allEvents.slice(-1000);
            localStorage.setItem('ainflue-tracking-events', JSON.stringify(recentEvents));
        } catch (error) {
            console.warn('Failed to save events to localStorage:', error);
        }
    }

    async sendToAnalytics(events) {
        try {
            // Mock analytics service call
            const payload = {
                sessionId: this.sessionId,
                events: events.map(event => this.anonymizeEvent(event)),
                timestamp: Date.now()
            };

            // In production, this would send to actual analytics service
            console.debug('📊 Would send to analytics:', payload);
        } catch (error) {
            console.error('Failed to send to analytics:', error);
        }
    }

    anonymizeEvent(event) {
        if (!this.config.anonymizeData) return event;

        const anonymized = { ...event };
        
        // Remove or hash personally identifiable information
        delete anonymized.userId;
        delete anonymized.userAgent;
        delete anonymized.url;
        
        // Hash sensitive data
        if (anonymized.data.contentId) {
            anonymized.data.contentId = this.hashValue(anonymized.data.contentId);
        }

        return anonymized;
    }

    sanitizeData(data) {
        // Remove sensitive information from tracking data
        const sanitized = { ...data };
        
        // Remove passwords, tokens, keys
        const sensitiveKeys = ['password', 'token', 'key', 'secret', 'auth'];
        for (const key of Object.keys(sanitized)) {
            if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
                delete sanitized[key];
            }
        }

        return sanitized;
    }

    async getUsageAnalytics(timeRange = 7, category = null) {
        try {
            const events = await this.getTrackingData(timeRange, category);
            return this.analyzeUsageData(events);
        } catch (error) {
            console.error('Failed to get usage analytics:', error);
            return null;
        }
    }

    async getTrackingData(days = 7, category = null) {
        const startTime = Date.now() - (days * 24 * 60 * 60 * 1000);
        const events = [];

        // Get from local storage
        for (const [id, event] of this.trackingData) {
            if (event.timestamp >= startTime) {
                if (!category || event.category === category) {
                    events.push(event);
                }
            }
        }

        // Get from IndexedDB
        if (this.storage.persistent) {
            const dbEvents = await this.getEventsFromIndexedDB(startTime, category);
            events.push(...dbEvents);
        }

        return events.sort((a, b) => a.timestamp - b.timestamp);
    }

    async getEventsFromIndexedDB(startTime, category = null) {
        if (!this.storage.persistent) return [];

        const events = [];
        const categories = category ? [category] : Object.keys(this.categories);

        for (const cat of categories) {
            const categoryEvents = await new Promise((resolve, reject) => {
                const transaction = this.storage.persistent.transaction([cat], 'readonly');
                const store = transaction.objectStore(cat);
                const index = store.index('timestamp');
                const range = IDBKeyRange.lowerBound(startTime);
                const request = index.getAll(range);

                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
            });

            events.push(...categoryEvents);
        }

        return events;
    }

    analyzeUsageData(events) {
        const analysis = {
            totalEvents: events.length,
            timeRange: {
                start: Math.min(...events.map(e => e.timestamp)),
                end: Math.max(...events.map(e => e.timestamp))
            },
            categories: {},
            topFeatures: {},
            userSessions: new Set(events.map(e => e.sessionId)).size,
            averageSessionLength: 0,
            errorRate: 0
        };

        // Analyze by category
        for (const category of Object.keys(this.categories)) {
            const categoryEvents = events.filter(e => e.category === category);
            analysis.categories[category] = {
                count: categoryEvents.length,
                events: this.groupEventsByType(categoryEvents)
            };
        }

        // Analyze feature usage
        const featureEvents = events.filter(e => e.category === 'usage' && e.event === 'feature_use');
        for (const event of featureEvents) {
            const feature = event.data.feature;
            if (!analysis.topFeatures[feature]) {
                analysis.topFeatures[feature] = {
                    count: 0,
                    totalTime: 0,
                    errors: 0
                };
            }
            analysis.topFeatures[feature].count++;
            analysis.topFeatures[feature].totalTime += event.data.timeSpent || 0;
            analysis.topFeatures[feature].errors += event.data.errors || 0;
        }

        // Calculate error rate
        const errorEvents = events.filter(e => e.category === 'system' && e.event === 'error');
        analysis.errorRate = events.length > 0 ? (errorEvents.length / events.length) * 100 : 0;

        return analysis;
    }

    groupEventsByType(events) {
        const grouped = {};
        for (const event of events) {
            if (!grouped[event.event]) {
                grouped[event.event] = 0;
            }
            grouped[event.event]++;
        }
        return grouped;
    }

    async cleanupExpiredData() {
        console.log('🧹 Cleaning up expired tracking data...');

        let cleaned = 0;

        // Clean local storage
        const now = Date.now();
        for (const [id, event] of this.trackingData) {
            const retention = this.categories[event.category]?.retention || this.dataRetentionDays;
            const expiry = event.timestamp + (retention * 24 * 60 * 60 * 1000);
            
            if (now > expiry) {
                this.trackingData.delete(id);
                cleaned++;
            }
        }

        // Clean IndexedDB
        if (this.storage.persistent) {
            const dbCleaned = await this.cleanupExpiredIndexedDBData();
            cleaned += dbCleaned;
        }

        console.log(`🧹 Cleaned up ${cleaned} expired tracking events`);
    }

    async cleanupExpiredIndexedDBData() {
        if (!this.storage.persistent) return 0;

        let cleaned = 0;
        const now = Date.now();

        for (const [category, config] of Object.entries(this.categories)) {
            const retention = config.retention || this.dataRetentionDays;
            const cutoffTime = now - (retention * 24 * 60 * 60 * 1000);

            try {
                const deletedCount = await new Promise((resolve, reject) => {
                    const transaction = this.storage.persistent.transaction([category], 'readwrite');
                    const store = transaction.objectStore(category);
                    const index = store.index('timestamp');
                    const range = IDBKeyRange.upperBound(cutoffTime);
                    
                    let count = 0;
                    const request = index.openCursor(range);
                    
                    request.onsuccess = (event) => {
                        const cursor = event.target.result;
                        if (cursor) {
                            cursor.delete();
                            count++;
                            cursor.continue();
                        } else {
                            resolve(count);
                        }
                    };
                    
                    request.onerror = () => reject(request.error);
                });

                cleaned += deletedCount;
            } catch (error) {
                console.warn(`Failed to clean category ${category}:`, error);
            }
        }

        return cleaned;
    }

    // Helper methods
    generateSessionId() {
        return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateEventId() {
        return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    hashValue(value) {
        // Simple hash function for anonymization
        let hash = 0;
        for (let i = 0; i < value.length; i++) {
            const char = value.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString(36);
    }

    async getUserId() {
        try {
            if (window.electronAPI) {
                const userId = await window.electronAPI.invoke('store-get', 'user-id');
                return this.config.anonymizeData ? this.hashValue(userId || 'anonymous') : userId;
            }
        } catch (error) {
            // Fallback to session-based ID
        }
        return this.config.anonymizeData ? 'anonymous' : this.sessionId;
    }

    async getAppVersion() {
        try {
            if (window.electronAPI) {
                const platformInfo = await window.electronAPI.invoke('get-platform-info');
                return platformInfo?.version || '1.0.0';
            }
        } catch (error) {
            return '1.0.0';
        }
    }

    getPlatformInfo() {
        return {
            platform: navigator.platform,
            language: navigator.language,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            screen: {
                width: screen.width,
                height: screen.height,
                colorDepth: screen.colorDepth
            }
        };
    }

    isCriticalEvent(category, event) {
        const criticalEvents = {
            license: ['violation', 'check'],
            system: ['error', 'startup', 'shutdown'],
            user: ['login', 'logout']
        };

        return criticalEvents[category]?.includes(event) || false;
    }

    async saveSession(session) {
        if (this.storage.persistent) {
            try {
                await new Promise((resolve, reject) => {
                    const transaction = this.storage.persistent.transaction(['sessions'], 'readwrite');
                    const store = transaction.objectStore('sessions');
                    const request = store.put(session);

                    request.onsuccess = () => resolve();
                    request.onerror = () => reject(request.error);
                });
            } catch (error) {
                console.warn('Failed to save session:', error);
            }
        }
    }

    // Public API methods
    setTrackingEnabled(enabled) {
        this.trackingEnabled = enabled;
        console.log(`📊 Tracking ${enabled ? 'enabled' : 'disabled'}`);
    }

    setPrivacyMode(enabled) {
        this.privacyMode = enabled;
        this.config.anonymizeData = enabled;
        console.log(`🔒 Privacy mode ${enabled ? 'enabled' : 'disabled'}`);
    }

    async endSession() {
        const endTime = Date.now();
        const sessionDuration = endTime - this.startTime;

        // Track session end
        await this.trackEvent('system', 'shutdown', {
            sessionDuration,
            eventsTracked: this.trackingData.size
        }, { immediate: true });

        // Flush any remaining events
        await this.flushPendingEvents();

        // Update session record
        try {
            if (this.storage.persistent) {
                await new Promise((resolve, reject) => {
                    const transaction = this.storage.persistent.transaction(['sessions'], 'readwrite');
                    const store = transaction.objectStore('sessions');
                    const request = store.get(this.sessionId);

                    request.onsuccess = () => {
                        const session = request.result;
                        if (session) {
                            session.endTime = endTime;
                            session.duration = sessionDuration;
                            session.eventCount = this.trackingData.size;
                            store.put(session);
                        }
                        resolve();
                    };

                    request.onerror = () => reject(request.error);
                });
            }
        } catch (error) {
            console.warn('Failed to update session end:', error);
        }

        // Clean up timers
        if (this.flushTimer) clearInterval(this.flushTimer);
        if (this.cleanupTimer) clearInterval(this.cleanupTimer);

        console.log(`📊 Session ended: ${this.sessionId} (${sessionDuration}ms)`);
    }

    getTrackingStatus() {
        return {
            enabled: this.trackingEnabled,
            privacyMode: this.privacyMode,
            sessionId: this.sessionId,
            eventsTracked: this.trackingData.size,
            pendingEvents: this.pendingEvents.length,
            sessionDuration: Date.now() - this.startTime,
            categories: Object.keys(this.categories).filter(cat => this.categories[cat].enabled)
        };
    }

    isHealthy() {
        return this.trackingEnabled && this.sessionId && this.pendingEvents.length < 1000;
    }
}

export default UsageTrackingSystem;