/**
 * Ainflue Desktop - API Aggregator Service
 * 
 * Centralized API management layer that aggregates multiple backend services,
 * handles authentication, rate limiting, caching, and provides a unified interface.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class APIAggregator {
    constructor() {
        this.services = new Map();
        this.cache = new Map();
        this.rateLimits = new Map();
        this.authTokens = new Map();
        this.requestQueue = [];
        this.isProcessingQueue = false;
        this.config = {
            baseURL: 'https://api.ainflue.com',
            timeout: 30000,
            retryAttempts: 3,
            cacheTimeout: 5 * 60 * 1000, // 5 minutes
            rateLimit: {
                requests: 100,
                window: 60 * 1000 // 1 minute
            }
        };

        // Service endpoints configuration
        this.serviceEndpoints = {
            ai: {
                baseURL: '/api/ai',
                endpoints: {
                    analyze: '/analyze',
                    process: '/process',
                    optimize: '/optimize',
                    predict: '/predict',
                    recommendations: '/recommendations'
                },
                rateLimit: { requests: 50, window: 60000 }
            },
            content: {
                baseURL: '/api/content',
                endpoints: {
                    upload: '/upload',
                    metadata: '/metadata',
                    watermark: '/watermark',
                    convert: '/convert',
                    download: '/download'
                },
                rateLimit: { requests: 200, window: 60000 }
            },
            collaboration: {
                baseURL: '/api/collaboration',
                endpoints: {
                    projects: '/projects',
                    teams: '/teams',
                    chat: '/chat',
                    reviews: '/reviews',
                    permissions: '/permissions'
                },
                rateLimit: { requests: 100, window: 60000 }
            },
            analytics: {
                baseURL: '/api/analytics',
                endpoints: {
                    performance: '/performance',
                    revenue: '/revenue',
                    engagement: '/engagement',
                    trends: '/trends',
                    reports: '/reports'
                },
                rateLimit: { requests: 75, window: 60000 }
            },
            platform: {
                baseURL: '/api/platform',
                endpoints: {
                    connect: '/connect',
                    publish: '/publish',
                    schedule: '/schedule',
                    status: '/status',
                    oauth: '/oauth'
                },
                rateLimit: { requests: 150, window: 60000 }
            },
            user: {
                baseURL: '/api/user',
                endpoints: {
                    profile: '/profile',
                    preferences: '/preferences',
                    subscription: '/subscription',
                    billing: '/billing',
                    notifications: '/notifications'
                },
                rateLimit: { requests: 100, window: 60000 }
            }
        };
    }

    async initialize() {
        console.log('🌐 Initializing API Aggregator...');

        // Initialize services
        for (const [serviceName, config] of Object.entries(this.serviceEndpoints)) {
            await this.initializeService(serviceName, config);
        }

        // Start request queue processor
        this.startQueueProcessor();

        // Set up periodic cache cleanup
        this.startCacheCleanup();

        // Load cached authentication tokens
        await this.loadAuthTokens();

        console.log('✅ API Aggregator initialized');
    }

    async initializeService(serviceName, config) {
        const service = {
            name: serviceName,
            baseURL: this.config.baseURL + config.baseURL,
            endpoints: config.endpoints,
            rateLimit: config.rateLimit || this.config.rateLimit,
            requestCount: 0,
            windowStart: Date.now(),
            isConnected: false,
            lastHealth: null
        };

        this.services.set(serviceName, service);
        this.rateLimits.set(serviceName, {
            count: 0,
            windowStart: Date.now()
        });

        // Test service connectivity
        try {
            await this.healthCheck(serviceName);
            service.isConnected = true;
            console.log(`✅ Service ${serviceName} connected`);
        } catch (error) {
            console.warn(`⚠️ Service ${serviceName} not available:`, error.message);
        }
    }

    async healthCheck(serviceName) {
        const service = this.services.get(serviceName);
        if (!service) {
            throw new Error(`Service ${serviceName} not found`);
        }

        try {
            const response = await this.makeRequest(serviceName, 'GET', '/health', null, {
                bypassCache: true,
                bypassRateLimit: true
            });
            
            service.lastHealth = {
                timestamp: Date.now(),
                status: response.status || 'healthy',
                latency: response.latency || 0
            };

            return response;
        } catch (error) {
            service.lastHealth = {
                timestamp: Date.now(),
                status: 'unhealthy',
                error: error.message
            };
            throw error;
        }
    }

    async makeRequest(serviceName, method, endpoint, data = null, options = {}) {
        const {
            bypassCache = false,
            bypassRateLimit = false,
            priority = 'normal',
            timeout = this.config.timeout
        } = options;

        // Check rate limits
        if (!bypassRateLimit && !this.checkRateLimit(serviceName)) {
            throw new Error(`Rate limit exceeded for service ${serviceName}`);
        }

        // Check cache for GET requests
        const cacheKey = this.generateCacheKey(serviceName, method, endpoint, data);
        if (method === 'GET' && !bypassCache && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.config.cacheTimeout) {
                console.debug(`📦 Cache hit for ${serviceName}${endpoint}`);
                return cached.data;
            }
            this.cache.delete(cacheKey);
        }

        // Create request object
        const request = {
            id: this.generateRequestId(),
            serviceName,
            method,
            endpoint,
            data,
            options,
            priority,
            timestamp: Date.now(),
            attempts: 0
        };

        // Add to queue or process immediately
        if (priority === 'high' || this.requestQueue.length === 0) {
            return await this.processRequest(request);
        } else {
            return new Promise((resolve, reject) => {
                request.resolve = resolve;
                request.reject = reject;
                this.requestQueue.push(request);
                this.sortQueueByPriority();
            });
        }
    }

    async processRequest(request) {
        const { serviceName, method, endpoint, data, options } = request;
        const service = this.services.get(serviceName);
        
        if (!service) {
            throw new Error(`Service ${serviceName} not found`);
        }

        const url = service.baseURL + endpoint;
        const headers = await this.buildHeaders(serviceName, options);

        try {
            const startTime = Date.now();
            
            // Make HTTP request
            const response = await this.httpRequest(method, url, data, headers, options.timeout);
            
            const endTime = Date.now();
            const latency = endTime - startTime;

            // Update rate limit counter
            this.updateRateLimit(serviceName);

            // Cache successful GET requests
            if (method === 'GET' && response.status >= 200 && response.status < 300) {
                const cacheKey = this.generateCacheKey(serviceName, method, endpoint, data);
                this.cache.set(cacheKey, {
                    data: response.data,
                    timestamp: Date.now()
                });
            }

            // Log request metrics
            this.logRequestMetrics(serviceName, endpoint, method, latency, response.status);

            return {
                data: response.data,
                status: response.status,
                headers: response.headers,
                latency
            };

        } catch (error) {
            // Handle retries
            if (request.attempts < this.config.retryAttempts && this.shouldRetry(error)) {
                request.attempts++;
                console.warn(`🔄 Retrying request to ${serviceName}${endpoint} (attempt ${request.attempts})`);
                
                // Exponential backoff
                const delay = Math.pow(2, request.attempts) * 1000;
                await this.sleep(delay);
                
                return await this.processRequest(request);
            }

            console.error(`❌ Request failed to ${serviceName}${endpoint}:`, error.message);
            throw error;
        }
    }

    async httpRequest(method, url, data, headers, timeout) {
        // Mock HTTP request implementation
        // In production, this would use fetch or axios
        return new Promise((resolve, reject) => {
            const requestTimeout = setTimeout(() => {
                reject(new Error('Request timeout'));
            }, timeout);

            // Simulate API call
            setTimeout(() => {
                clearTimeout(requestTimeout);
                
                // Mock response based on URL
                if (url.includes('/health')) {
                    resolve({
                        status: 200,
                        data: { status: 'healthy', timestamp: Date.now() },
                        headers: { 'content-type': 'application/json' }
                    });
                } else {
                    resolve({
                        status: 200,
                        data: { success: true, result: 'mock-data', timestamp: Date.now() },
                        headers: { 'content-type': 'application/json' }
                    });
                }
            }, Math.random() * 500 + 100); // 100-600ms response time
        });
    }

    async buildHeaders(serviceName, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Ainflue-Desktop/1.0.0',
            'X-Client-Version': '1.0.0',
            'X-Platform': process.platform
        };

        // Add authentication token if available
        const token = this.authTokens.get(serviceName) || this.authTokens.get('global');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Add custom headers from options
        if (options.headers) {
            Object.assign(headers, options.headers);
        }

        return headers;
    }

    checkRateLimit(serviceName) {
        const service = this.services.get(serviceName);
        const rateLimitInfo = this.rateLimits.get(serviceName);
        
        if (!service || !rateLimitInfo) return true;

        const now = Date.now();
        const windowElapsed = now - rateLimitInfo.windowStart;

        // Reset window if elapsed
        if (windowElapsed >= service.rateLimit.window) {
            rateLimitInfo.count = 0;
            rateLimitInfo.windowStart = now;
            return true;
        }

        return rateLimitInfo.count < service.rateLimit.requests;
    }

    updateRateLimit(serviceName) {
        const rateLimitInfo = this.rateLimits.get(serviceName);
        if (rateLimitInfo) {
            rateLimitInfo.count++;
        }
    }

    generateCacheKey(serviceName, method, endpoint, data) {
        const dataString = data ? JSON.stringify(data) : '';
        return `${serviceName}:${method}:${endpoint}:${this.hashString(dataString)}`;
    }

    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString(36);
    }

    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    startQueueProcessor() {
        if (this.isProcessingQueue) return;

        this.isProcessingQueue = true;
        
        const processQueue = async () => {
            while (this.requestQueue.length > 0) {
                const request = this.requestQueue.shift();
                
                try {
                    const result = await this.processRequest(request);
                    if (request.resolve) request.resolve(result);
                } catch (error) {
                    if (request.reject) request.reject(error);
                }
            }

            // Continue processing
            setTimeout(processQueue, 100);
        };

        processQueue();
    }

    sortQueueByPriority() {
        this.requestQueue.sort((a, b) => {
            const priorityOrder = { high: 3, normal: 2, low: 1 };
            return priorityOrder[b.priority] - priorityOrder[a.priority];
        });
    }

    startCacheCleanup() {
        setInterval(() => {
            const now = Date.now();
            for (const [key, cached] of this.cache) {
                if (now - cached.timestamp > this.config.cacheTimeout) {
                    this.cache.delete(key);
                }
            }
        }, 60000); // Cleanup every minute
    }

    async loadAuthTokens() {
        try {
            if (window.electronAPI) {
                const tokens = await window.electronAPI.invoke('store-get', 'api-tokens');
                if (tokens) {
                    this.authTokens = new Map(Object.entries(tokens));
                    console.log('🔑 Loaded authentication tokens');
                }
            }
        } catch (error) {
            console.warn('Failed to load auth tokens:', error);
        }
    }

    async saveAuthTokens() {
        try {
            if (window.electronAPI) {
                const tokensObject = Object.fromEntries(this.authTokens);
                await window.electronAPI.invoke('store-set', 'api-tokens', tokensObject);
            }
        } catch (error) {
            console.error('Failed to save auth tokens:', error);
        }
    }

    setAuthToken(serviceName, token) {
        this.authTokens.set(serviceName, token);
        this.saveAuthTokens();
    }

    shouldRetry(error) {
        // Retry on network errors, timeouts, and 5xx status codes
        if (error.message.includes('timeout')) return true;
        if (error.message.includes('network')) return true;
        if (error.status >= 500) return true;
        return false;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    logRequestMetrics(serviceName, endpoint, method, latency, status) {
        console.debug(`📊 ${method} ${serviceName}${endpoint} - ${status} (${latency}ms)`);
    }

    // Public API methods for specific services
    async analyzeContent(contentData, analysisType = 'full') {
        return await this.makeRequest('ai', 'POST', '/analyze', {
            content: contentData,
            type: analysisType,
            options: { includeRecommendations: true }
        });
    }

    async processAI(contentPath, processingOptions) {
        return await this.makeRequest('ai', 'POST', '/process', {
            contentPath,
            options: processingOptions
        }, { priority: 'high' });
    }

    async uploadContent(file, metadata) {
        return await this.makeRequest('content', 'POST', '/upload', {
            file,
            metadata
        }, { priority: 'high', timeout: 60000 });
    }

    async getContentMetadata(contentId) {
        return await this.makeRequest('content', 'GET', `/metadata/${contentId}`);
    }

    async getAnalytics(type, timeRange) {
        return await this.makeRequest('analytics', 'GET', `/${type}`, {
            timeRange
        });
    }

    async publishContent(platforms, content, schedule) {
        return await this.makeRequest('platform', 'POST', '/publish', {
            platforms,
            content,
            schedule
        }, { priority: 'high' });
    }

    async getUserProfile() {
        return await this.makeRequest('user', 'GET', '/profile');
    }

    // Service management methods
    getServiceStatus() {
        const status = {};
        for (const [name, service] of this.services) {
            status[name] = {
                connected: service.isConnected,
                lastHealth: service.lastHealth,
                rateLimit: this.rateLimits.get(name)
            };
        }
        return status;
    }

    getCacheStats() {
        return {
            size: this.cache.size,
            hitRate: this.cacheHitRate || 0,
            memoryUsage: this.estimateCacheSize()
        };
    }

    estimateCacheSize() {
        let size = 0;
        for (const [key, cached] of this.cache) {
            size += key.length + JSON.stringify(cached).length;
        }
        return size;
    }

    clearCache(pattern = null) {
        if (!pattern) {
            this.cache.clear();
            console.log('🧹 Cleared all cache');
        } else {
            const regex = new RegExp(pattern);
            for (const key of this.cache.keys()) {
                if (regex.test(key)) {
                    this.cache.delete(key);
                }
            }
            console.log(`🧹 Cleared cache matching pattern: ${pattern}`);
        }
    }

    isHealthy() {
        const connectedServices = Array.from(this.services.values()).filter(s => s.isConnected).length;
        return connectedServices > 0 && this.isProcessingQueue;
    }

    getQueueStatus() {
        return {
            queueSize: this.requestQueue.length,
            isProcessing: this.isProcessingQueue,
            priorityDistribution: this.getQueuePriorityDistribution()
        };
    }

    getQueuePriorityDistribution() {
        const distribution = { high: 0, normal: 0, low: 0 };
        for (const request of this.requestQueue) {
            distribution[request.priority]++;
        }
        return distribution;
    }
}

export default APIAggregator;