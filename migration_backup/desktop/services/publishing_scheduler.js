/**
 * Ainflue Desktop - Publishing Scheduler Service
 * 
 * Automated publishing scheduler for multi-platform content distribution
 * with advanced timing, queue management, and platform-specific optimization.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class PublishingScheduler {
    constructor() {
        this.scheduledTasks = new Map();
        this.publishingQueue = [];
        this.platforms = new Map();
        this.isRunning = false;
        this.pollingInterval = 60000; // 1 minute
        this.maxRetries = 3;
        this.batchSize = 5;
        
        this.platformConfigs = {
            youtube: {
                maxFileSize: 128 * 1024 * 1024 * 1024, // 128GB
                supportedFormats: ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                maxDuration: 12 * 60 * 60, // 12 hours
                requiresThumbnail: true,
                optimalTimes: ['10:00', '14:00', '18:00', '20:00']
            },
            instagram: {
                maxFileSize: 4 * 1024 * 1024 * 1024, // 4GB
                supportedFormats: ['mp4', 'mov'],
                maxDuration: 60 * 60, // 1 hour
                aspectRatios: ['1:1', '4:5', '9:16'],
                optimalTimes: ['11:00', '13:00', '17:00', '19:00']
            },
            tiktok: {
                maxFileSize: 287 * 1024 * 1024, // 287MB
                supportedFormats: ['mp4', 'mov'],
                maxDuration: 10 * 60, // 10 minutes
                aspectRatio: '9:16',
                optimalTimes: ['06:00', '10:00', '19:00', '21:00']
            },
            twitter: {
                maxFileSize: 512 * 1024 * 1024, // 512MB
                supportedFormats: ['mp4', 'mov'],
                maxDuration: 2 * 60 + 20, // 2:20
                optimalTimes: ['09:00', '12:00', '15:00', '18:00']
            },
            facebook: {
                maxFileSize: 10 * 1024 * 1024 * 1024, // 10GB
                supportedFormats: ['mp4', 'mov', 'avi'],
                maxDuration: 4 * 60 * 60, // 4 hours
                optimalTimes: ['13:00', '15:00', '20:00', '21:00']
            },
            linkedin: {
                maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
                supportedFormats: ['mp4', 'mov', 'avi'],
                maxDuration: 10 * 60, // 10 minutes
                optimalTimes: ['09:00', '12:00', '17:00']
            }
        };
    }

    async initialize() {
        console.log('📅 Initializing Publishing Scheduler...');
        
        // Load saved schedules
        await this.loadScheduledTasks();
        
        // Initialize platform connections
        await this.initializePlatforms();
        
        // Start the scheduler
        this.startScheduler();
        
        console.log('✅ Publishing Scheduler initialized');
    }

    async loadScheduledTasks() {
        try {
            if (window.electronAPI) {
                const savedTasks = await window.electronAPI.invoke('store-get', 'scheduled-publishing');
                if (savedTasks) {
                    this.scheduledTasks = new Map(Object.entries(savedTasks));
                    console.log(`📋 Loaded ${this.scheduledTasks.size} scheduled tasks`);
                }
            }
        } catch (error) {
            console.warn('Failed to load scheduled tasks:', error);
        }
    }

    async saveScheduledTasks() {
        try {
            if (window.electronAPI) {
                const tasksObject = Object.fromEntries(this.scheduledTasks);
                await window.electronAPI.invoke('store-set', 'scheduled-publishing', tasksObject);
            }
        } catch (error) {
            console.error('Failed to save scheduled tasks:', error);
        }
    }

    async initializePlatforms() {
        // Initialize platform API clients
        for (const [platform, config] of Object.entries(this.platformConfigs)) {
            try {
                const apiClient = await this.createPlatformClient(platform, config);
                this.platforms.set(platform, {
                    client: apiClient,
                    config: config,
                    isConnected: false,
                    lastSync: null
                });
            } catch (error) {
                console.warn(`Failed to initialize ${platform} client:`, error);
            }
        }
    }

    async createPlatformClient(platform, config) {
        // Mock platform client - in production this would be real API clients
        return {
            platform,
            config,
            async authenticate() {
                // Authentication logic here
                return { success: true, token: 'mock-token' };
            },
            async publish(content, metadata) {
                // Publishing logic here
                console.log(`📤 Publishing to ${platform}:`, metadata.title);
                return {
                    success: true,
                    publishedUrl: `https://${platform}.com/content/${Date.now()}`,
                    id: `${platform}_${Date.now()}`
                };
            },
            async getAnalytics(contentId) {
                // Analytics fetching logic
                return {
                    views: Math.floor(Math.random() * 10000),
                    likes: Math.floor(Math.random() * 1000),
                    shares: Math.floor(Math.random() * 100),
                    comments: Math.floor(Math.random() * 50)
                };
            }
        };
    }

    startScheduler() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.schedulerInterval = setInterval(() => {
            this.processScheduledTasks();
        }, this.pollingInterval);
        
        console.log('⏰ Publishing scheduler started');
    }

    stopScheduler() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        clearInterval(this.schedulerInterval);
        console.log('⏸️ Publishing scheduler stopped');
    }

    async schedulePublish(content, platforms, publishTime, options = {}) {
        const taskId = this.generateTaskId();
        const scheduledTask = {
            id: taskId,
            content: {
                filePath: content.filePath,
                title: content.title,
                description: content.description,
                tags: content.tags || [],
                thumbnail: content.thumbnail,
                category: content.category
            },
            platforms: platforms,
            publishTime: new Date(publishTime),
            options: {
                optimizeForPlatform: options.optimizeForPlatform !== false,
                crossPost: options.crossPost || false,
                notifyOnComplete: options.notifyOnComplete !== false,
                retryOnFailure: options.retryOnFailure !== false,
                ...options
            },
            status: 'scheduled',
            created: new Date(),
            retryCount: 0
        };

        // Validate platforms and content
        const validation = await this.validateScheduledTask(scheduledTask);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
        }

        // Store the task
        this.scheduledTasks.set(taskId, scheduledTask);
        await this.saveScheduledTasks();

        console.log(`📅 Scheduled publish task ${taskId} for ${publishTime}`);
        
        // Add to immediate queue if time is near
        if (scheduledTask.publishTime.getTime() - Date.now() < this.pollingInterval) {
            this.publishingQueue.push(scheduledTask);
        }

        return taskId;
    }

    async validateScheduledTask(task) {
        const errors = [];
        
        // Validate content
        if (!task.content.filePath) {
            errors.push('Content file path is required');
        }
        
        if (!task.content.title) {
            errors.push('Content title is required');
        }

        // Validate platforms
        for (const platform of task.platforms) {
            if (!this.platformConfigs[platform]) {
                errors.push(`Unsupported platform: ${platform}`);
                continue;
            }

            const config = this.platformConfigs[platform];
            
            // Check file format
            if (task.content.filePath) {
                const extension = task.content.filePath.split('.').pop().toLowerCase();
                if (!config.supportedFormats.includes(extension)) {
                    errors.push(`${platform} does not support ${extension} format`);
                }
            }
        }

        // Validate publish time
        if (task.publishTime < new Date()) {
            errors.push('Publish time must be in the future');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    async processScheduledTasks() {
        const now = new Date();
        const tasksToProcess = [];

        // Find tasks ready for publishing
        for (const [taskId, task] of this.scheduledTasks) {
            if (task.status === 'scheduled' && task.publishTime <= now) {
                tasksToProcess.push(task);
            }
        }

        if (tasksToProcess.length === 0) return;

        console.log(`🔄 Processing ${tasksToProcess.length} scheduled tasks`);

        // Process tasks in batches
        for (let i = 0; i < tasksToProcess.length; i += this.batchSize) {
            const batch = tasksToProcess.slice(i, i + this.batchSize);
            await this.processBatch(batch);
        }
    }

    async processBatch(tasks) {
        const promises = tasks.map(task => this.publishTask(task));
        await Promise.allSettled(promises);
    }

    async publishTask(task) {
        try {
            task.status = 'publishing';
            this.scheduledTasks.set(task.id, task);

            console.log(`📤 Publishing task ${task.id} to ${task.platforms.join(', ')}`);

            const results = {};
            
            // Publish to each platform
            for (const platform of task.platforms) {
                try {
                    const result = await this.publishToPlatform(task, platform);
                    results[platform] = result;
                } catch (error) {
                    console.error(`Failed to publish to ${platform}:`, error);
                    results[platform] = { success: false, error: error.message };
                }
            }

            // Update task status
            const hasFailures = Object.values(results).some(r => !r.success);
            if (hasFailures && task.options.retryOnFailure && task.retryCount < this.maxRetries) {
                task.retryCount++;
                task.status = 'scheduled';
                task.publishTime = new Date(Date.now() + (task.retryCount * 30 * 60 * 1000)); // Retry in 30, 60, 90 minutes
                console.log(`🔄 Retrying task ${task.id} (attempt ${task.retryCount})`);
            } else {
                task.status = hasFailures ? 'failed' : 'completed';
                task.completed = new Date();
                task.results = results;
            }

            this.scheduledTasks.set(task.id, task);
            await this.saveScheduledTasks();

            // Send notification if requested
            if (task.options.notifyOnComplete) {
                await this.sendCompletionNotification(task);
            }

        } catch (error) {
            console.error(`Error processing task ${task.id}:`, error);
            task.status = 'failed';
            task.error = error.message;
            this.scheduledTasks.set(task.id, task);
        }
    }

    async publishToPlatform(task, platform) {
        const platformClient = this.platforms.get(platform);
        if (!platformClient) {
            throw new Error(`Platform ${platform} not initialized`);
        }

        // Optimize content for platform if requested
        let optimizedContent = task.content;
        if (task.options.optimizeForPlatform) {
            optimizedContent = await this.optimizeContentForPlatform(task.content, platform);
        }

        // Prepare metadata
        const metadata = {
            title: optimizedContent.title,
            description: optimizedContent.description,
            tags: optimizedContent.tags,
            category: optimizedContent.category,
            thumbnail: optimizedContent.thumbnail,
            platform: platform
        };

        // Publish content
        const result = await platformClient.client.publish(optimizedContent, metadata);
        
        console.log(`✅ Published to ${platform}: ${result.publishedUrl}`);
        return result;
    }

    async optimizeContentForPlatform(content, platform) {
        const config = this.platformConfigs[platform];
        const optimized = { ...content };

        // Platform-specific optimizations
        switch (platform) {
            case 'instagram':
                // Optimize hashtags for Instagram
                if (optimized.tags) {
                    optimized.tags = optimized.tags.map(tag => tag.startsWith('#') ? tag : `#${tag}`);
                }
                break;
            
            case 'youtube':
                // Optimize description for YouTube
                if (optimized.description && optimized.description.length > 1000) {
                    optimized.description = optimized.description.substring(0, 997) + '...';
                }
                break;
            
            case 'tiktok':
                // Optimize for TikTok's algorithm
                if (optimized.tags) {
                    optimized.tags = [...optimized.tags, '#fyp', '#trending'];
                }
                break;
        }

        return optimized;
    }

    async sendCompletionNotification(task) {
        const notification = {
            title: 'Publishing Complete',
            message: `Content "${task.content.title}" has been published to ${task.platforms.join(', ')}`,
            type: task.status === 'completed' ? 'success' : 'error',
            timestamp: new Date()
        };

        // Send to notification system
        window.dispatchEvent(new CustomEvent('show-notification', { detail: notification }));
    }

    // Public API methods
    async getScheduledTasks() {
        return Array.from(this.scheduledTasks.values());
    }

    async getTask(taskId) {
        return this.scheduledTasks.get(taskId);
    }

    async cancelTask(taskId) {
        const task = this.scheduledTasks.get(taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        if (task.status === 'publishing') {
            throw new Error('Cannot cancel task that is currently publishing');
        }

        task.status = 'cancelled';
        task.cancelled = new Date();
        this.scheduledTasks.set(taskId, task);
        await this.saveScheduledTasks();

        console.log(`❌ Cancelled task ${taskId}`);
        return true;
    }

    async updateTask(taskId, updates) {
        const task = this.scheduledTasks.get(taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        if (task.status !== 'scheduled') {
            throw new Error('Can only update scheduled tasks');
        }

        // Apply updates
        Object.assign(task, updates);
        
        // Re-validate
        const validation = await this.validateScheduledTask(task);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
        }

        this.scheduledTasks.set(taskId, task);
        await this.saveScheduledTasks();

        console.log(`📝 Updated task ${taskId}`);
        return task;
    }

    getOptimalPublishTimes(platform, timezone = 'UTC') {
        const config = this.platformConfigs[platform];
        if (!config || !config.optimalTimes) {
            return [];
        }

        return config.optimalTimes.map(time => {
            const [hours, minutes] = time.split(':').map(Number);
            const date = new Date();
            date.setHours(hours, minutes, 0, 0);
            return date;
        });
    }

    getPlatformLimitations(platform) {
        return this.platformConfigs[platform] || null;
    }

    generateTaskId() {
        return `pub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async getAnalytics(taskId) {
        const task = this.scheduledTasks.get(taskId);
        if (!task || task.status !== 'completed') {
            return null;
        }

        const analytics = {};
        
        for (const platform of task.platforms) {
            if (task.results && task.results[platform] && task.results[platform].success) {
                const platformClient = this.platforms.get(platform);
                if (platformClient) {
                    try {
                        analytics[platform] = await platformClient.client.getAnalytics(task.results[platform].id);
                    } catch (error) {
                        console.warn(`Failed to get analytics for ${platform}:`, error);
                    }
                }
            }
        }

        return analytics;
    }

    isHealthy() {
        return this.isRunning && this.platforms.size > 0;
    }

    getStatus() {
        return {
            isRunning: this.isRunning,
            scheduledTasks: this.scheduledTasks.size,
            queueSize: this.publishingQueue.length,
            platforms: Array.from(this.platforms.keys()),
            lastProcessed: this.lastProcessedTime
        };
    }
}

export default PublishingScheduler;