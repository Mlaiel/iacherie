/**
 * @fileoverview API Client - Backend Communication Layer
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/api_client
 * @description Professional API client for secure backend communication with retry logic and caching
 */

class APIClient {
  constructor() {
    this.baseURL = process.env.NODE_ENV === 'development' 
      ? 'http://localhost:8000/api' 
      : 'https://api.ainflue.com';
    
    this.config = {
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      cacheTimeout: 5 * 60 * 1000, // 5 minutes
      enableCache: true,
      enableMetrics: true
    };

    this.cache = new Map();
    this.metrics = {
      requests: 0,
      successful: 0,
      failed: 0,
      cached: 0,
      averageResponseTime: 0
    };

    this.interceptors = {
      request: [],
      response: []
    };

    this.authToken = null;
    this.refreshToken = null;
    this.sessionId = null;

    this.initializeClient();
    console.log('API Client initialized');
  }

  /**
   * Initialize API client with default configurations
   */
  initializeClient() {
    // Setup default request interceptor
    this.addRequestInterceptor(async (config) => {
      // Add authentication headers
      if (this.authToken) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${this.authToken}`;
      }

      // Add session ID
      if (this.sessionId) {
        config.headers = config.headers || {};
        config.headers['X-Session-ID'] = this.sessionId;
      }

      // Add client information
      config.headers = config.headers || {};
      config.headers['X-Client'] = 'Ainflue-Desktop';
      config.headers['X-Client-Version'] = '1.0.0';
      config.headers['Content-Type'] = 'application/json';

      return config;
    });

    // Setup default response interceptor
    this.addResponseInterceptor(
      (response) => {
        this.metrics.successful++;
        return response;
      },
      (error) => {
        this.metrics.failed++;
        return this.handleResponseError(error);
      }
    );
  }

  /**
   * Add request interceptor
   */
  addRequestInterceptor(interceptor) {
    this.interceptors.request.push(interceptor);
  }

  /**
   * Add response interceptor
   */
  addResponseInterceptor(successHandler, errorHandler) {
    this.interceptors.response.push({ successHandler, errorHandler });
  }

  /**
   * Apply request interceptors
   */
  async applyRequestInterceptors(config) {
    let processedConfig = config;
    
    for (const interceptor of this.interceptors.request) {
      try {
        processedConfig = await interceptor(processedConfig) || processedConfig;
      } catch (error) {
        console.error('Request interceptor error:', error);
      }
    }
    
    return processedConfig;
  }

  /**
   * Apply response interceptors
   */
  async applyResponseInterceptors(response, isError = false) {
    let processedResponse = response;
    
    for (const { successHandler, errorHandler } of this.interceptors.response) {
      try {
        if (isError && errorHandler) {
          processedResponse = await errorHandler(processedResponse) || processedResponse;
        } else if (!isError && successHandler) {
          processedResponse = await successHandler(processedResponse) || processedResponse;
        }
      } catch (error) {
        console.error('Response interceptor error:', error);
      }
    }
    
    return processedResponse;
  }

  /**
   * Make HTTP request with retry logic and caching
   */
  async request(config) {
    const startTime = Date.now();
    this.metrics.requests++;

    try {
      // Apply request interceptors
      const processedConfig = await this.applyRequestInterceptors(config);
      
      // Generate cache key
      const cacheKey = this.generateCacheKey(processedConfig);
      
      // Check cache for GET requests
      if (processedConfig.method === 'GET' && this.config.enableCache) {
        const cached = this.getFromCache(cacheKey);
        if (cached) {
          this.metrics.cached++;
          return cached;
        }
      }

      // Make request with retry logic
      const response = await this.requestWithRetry(processedConfig);
      
      // Apply response interceptors
      const processedResponse = await this.applyResponseInterceptors(response);
      
      // Cache GET responses
      if (processedConfig.method === 'GET' && this.config.enableCache) {
        this.setCache(cacheKey, processedResponse);
      }

      // Update metrics
      const responseTime = Date.now() - startTime;
      this.updateMetrics(responseTime);

      return processedResponse;

    } catch (error) {
      const processedError = await this.applyResponseInterceptors(error, true);
      throw processedError;
    }
  }

  /**
   * Make request with retry logic
   */
  async requestWithRetry(config, attempt = 1) {
    try {
      return await this.makeHTTPRequest(config);
    } catch (error) {
      if (attempt < this.config.retryAttempts && this.shouldRetry(error)) {
        console.warn(`Request failed, retrying (${attempt}/${this.config.retryAttempts})...`);
        await this.delay(this.config.retryDelay * attempt);
        return this.requestWithRetry(config, attempt + 1);
      }
      throw error;
    }
  }

  /**
   * Make actual HTTP request
   */
  async makeHTTPRequest(config) {
    const { url, method = 'GET', data, headers = {}, timeout = this.config.timeout } = config;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      };

    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      
      throw error;
    }
  }

  /**
   * GET request
   */
  async get(endpoint, params = {}, config = {}) {
    const url = this.buildURL(endpoint, params);
    return this.request({ 
      ...config, 
      url, 
      method: 'GET' 
    });
  }

  /**
   * POST request
   */
  async post(endpoint, data = {}, config = {}) {
    const url = this.buildURL(endpoint);
    return this.request({ 
      ...config, 
      url, 
      method: 'POST', 
      data 
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data = {}, config = {}) {
    const url = this.buildURL(endpoint);
    return this.request({ 
      ...config, 
      url, 
      method: 'PUT', 
      data 
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint, config = {}) {
    const url = this.buildURL(endpoint);
    return this.request({ 
      ...config, 
      url, 
      method: 'DELETE' 
    });
  }

  /**
   * PATCH request
   */
  async patch(endpoint, data = {}, config = {}) {
    const url = this.buildURL(endpoint);
    return this.request({ 
      ...config, 
      url, 
      method: 'PATCH', 
      data 
    });
  }

  // API Endpoints for Ainflue Business Logic

  /**
   * Authentication endpoints
   */
  async authenticate(credentials) {
    const response = await this.post('/auth/login', credentials);
    
    if (response.data.token) {
      this.setAuthToken(response.data.token);
      this.setSessionId(response.data.sessionId);
    }
    
    return response;
  }

  async refreshAuthToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await this.post('/auth/refresh', {
      refreshToken: this.refreshToken
    });
    
    if (response.data.token) {
      this.setAuthToken(response.data.token);
    }
    
    return response;
  }

  async logout() {
    try {
      await this.post('/auth/logout');
    } finally {
      this.clearAuth();
    }
  }

  /**
   * Content management endpoints
   */
  async uploadContent(contentData, progressCallback) {
    return this.post('/content/upload', contentData, {
      onProgress: progressCallback
    });
  }

  async getContentLibrary(filters = {}) {
    return this.get('/content/library', filters);
  }

  async getContentMetadata(contentId) {
    return this.get(`/content/${contentId}/metadata`);
  }

  async updateContentMetadata(contentId, metadata) {
    return this.put(`/content/${contentId}/metadata`, metadata);
  }

  async deleteContent(contentId) {
    return this.delete(`/content/${contentId}`);
  }

  /**
   * AI processing endpoints
   */
  async requestAIAnalysis(contentId, analysisType) {
    return this.post('/ai/analyze', {
      contentId,
      analysisType
    });
  }

  async getAIAnalysisResult(analysisId) {
    return this.get(`/ai/analysis/${analysisId}`);
  }

  async enhanceContent(contentId, enhancementOptions) {
    return this.post(`/ai/enhance/${contentId}`, enhancementOptions);
  }

  async generateMetadata(contentId, options) {
    return this.post(`/ai/metadata/${contentId}`, options);
  }

  /**
   * Security and protection endpoints
   */
  async encryptContent(contentId, protectionLevel) {
    return this.post(`/security/encrypt/${contentId}`, {
      protectionLevel
    });
  }

  async addWatermark(contentId, watermarkOptions) {
    return this.post(`/security/watermark/${contentId}`, watermarkOptions);
  }

  async createDigitalSignature(contentId) {
    return this.post(`/security/signature/${contentId}`);
  }

  /**
   * SEO optimization endpoints
   */
  async optimizeSEO(contentId, seoOptions) {
    return this.post(`/seo/optimize/${contentId}`, seoOptions);
  }

  async getSEORecommendations(contentId) {
    return this.get(`/seo/recommendations/${contentId}`);
  }

  async analyzeKeywords(content) {
    return this.post('/seo/keywords', { content });
  }

  /**
   * Collaboration endpoints
   */
  async createCollaborationSession(projectId, participants) {
    return this.post('/collaboration/sessions', {
      projectId,
      participants
    });
  }

  async joinCollaborationSession(sessionId) {
    return this.post(`/collaboration/sessions/${sessionId}/join`);
  }

  async syncCollaborationData(sessionId, data) {
    return this.post(`/collaboration/sessions/${sessionId}/sync`, data);
  }

  /**
   * Distribution endpoints
   */
  async publishToPlatform(contentId, platform, publishOptions) {
    return this.post('/distribution/publish', {
      contentId,
      platform,
      options: publishOptions
    });
  }

  async schedulePublication(contentId, platforms, schedule) {
    return this.post('/distribution/schedule', {
      contentId,
      platforms,
      schedule
    });
  }

  async getPublicationStatus(publicationId) {
    return this.get(`/distribution/status/${publicationId}`);
  }

  /**
   * Analytics endpoints
   */
  async getContentAnalytics(contentId, timeRange) {
    return this.get(`/analytics/content/${contentId}`, { timeRange });
  }

  async getPerformanceMetrics(timeRange) {
    return this.get('/analytics/performance', { timeRange });
  }

  async getRevenueAnalytics(timeRange) {
    return this.get('/analytics/revenue', { timeRange });
  }

  /**
   * Project management endpoints
   */
  async createProject(projectData) {
    return this.post('/projects', projectData);
  }

  async getProjects(filters = {}) {
    return this.get('/projects', filters);
  }

  async getProject(projectId) {
    return this.get(`/projects/${projectId}`);
  }

  async updateProject(projectId, projectData) {
    return this.put(`/projects/${projectId}`, projectData);
  }

  async deleteProject(projectId) {
    return this.delete(`/projects/${projectId}`);
  }

  /**
   * Platform integration endpoints
   */
  async connectPlatform(platform, credentials) {
    return this.post(`/platforms/${platform}/connect`, credentials);
  }

  async disconnectPlatform(platform) {
    return this.delete(`/platforms/${platform}/disconnect`);
  }

  async getPlatformStatus(platform) {
    return this.get(`/platforms/${platform}/status`);
  }

  // Utility methods

  /**
   * Build full URL with parameters
   */
  buildURL(endpoint, params = {}) {
    const url = new URL(endpoint, this.baseURL);
    
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null) {
        url.searchParams.append(key, params[key]);
      }
    });
    
    return url.toString();
  }

  /**
   * Generate cache key
   */
  generateCacheKey(config) {
    const { url, method = 'GET', data } = config;
    const key = `${method}:${url}`;
    
    if (data) {
      const dataHash = this.hashObject(data);
      return `${key}:${dataHash}`;
    }
    
    return key;
  }

  /**
   * Hash object for cache key
   */
  hashObject(obj) {
    const str = JSON.stringify(obj, Object.keys(obj).sort());
    let hash = 0;
    
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return hash.toString(36);
  }

  /**
   * Cache management
   */
  getFromCache(key) {
    const cached = this.cache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.config.cacheTimeout) {
      return cached.data;
    }
    
    if (cached) {
      this.cache.delete(key);
    }
    
    return null;
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  clearCache() {
    this.cache.clear();
    console.log('API cache cleared');
  }

  /**
   * Authentication management
   */
  setAuthToken(token) {
    this.authToken = token;
    // Store in secure storage if available
    if (window.electronAPI) {
      window.electronAPI.secureStore.set('authToken', token);
    }
  }

  setRefreshToken(token) {
    this.refreshToken = token;
    if (window.electronAPI) {
      window.electronAPI.secureStore.set('refreshToken', token);
    }
  }

  setSessionId(sessionId) {
    this.sessionId = sessionId;
  }

  clearAuth() {
    this.authToken = null;
    this.refreshToken = null;
    this.sessionId = null;
    
    if (window.electronAPI) {
      window.electronAPI.secureStore.delete('authToken');
      window.electronAPI.secureStore.delete('refreshToken');
    }
  }

  /**
   * Error handling
   */
  shouldRetry(error) {
    // Retry on network errors or 5xx status codes
    return error.message.includes('fetch') ||
           error.message.includes('timeout') ||
           (error.status >= 500 && error.status < 600);
  }

  async handleResponseError(error) {
    // Handle authentication errors
    if (error.status === 401) {
      try {
        await this.refreshAuthToken();
        return error; // Let the interceptor retry
      } catch (refreshError) {
        this.clearAuth();
        // Redirect to login
        if (window.stateManager) {
          window.stateManager.setState('user.authenticated', false);
        }
      }
    }

    // Handle rate limiting
    if (error.status === 429) {
      const retryAfter = error.headers?.['retry-after'] || 60;
      console.warn(`Rate limited. Retrying after ${retryAfter} seconds`);
      await this.delay(retryAfter * 1000);
    }

    return error;
  }

  /**
   * Metrics and monitoring
   */
  updateMetrics(responseTime) {
    const currentAvg = this.metrics.averageResponseTime;
    const totalRequests = this.metrics.successful + this.metrics.failed;
    
    this.metrics.averageResponseTime = 
      (currentAvg * (totalRequests - 1) + responseTime) / totalRequests;
  }

  getMetrics() {
    return {
      ...this.metrics,
      cacheHitRate: this.metrics.requests > 0 
        ? (this.metrics.cached / this.metrics.requests * 100).toFixed(2) + '%'
        : '0%',
      successRate: this.metrics.requests > 0
        ? (this.metrics.successful / this.metrics.requests * 100).toFixed(2) + '%'
        : '0%'
    };
  }

  /**
   * Utility delay function
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Configuration management
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    console.log('API Client configuration updated');
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.cache.clear();
    this.interceptors.request = [];
    this.interceptors.response = [];
    this.clearAuth();
    console.log('API Client cleaned up');
  }
}

// Create and export singleton instance
const apiClient = new APIClient();

// Export both class and instance
window.APIClient = APIClient;
window.apiClient = apiClient;

export { APIClient, apiClient };
export default apiClient;