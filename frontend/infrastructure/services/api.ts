/**
 * 🌐 API Service Enterprise - Advanced Backend Communication
 * 
 * @fileoverview Enterprise-grade API client with advanced features
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

// API Configuration
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  retryDelay: number;
  rateLimit: {
    requests: number;
    window: number; // milliseconds
  };
  enableCache: boolean;
  cacheExpiry: number;
  enableMetrics: boolean;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  meta?: {
    timestamp: number;
    requestId: string;
    cached: boolean;
    duration: number;
  };
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
  timestamp: number;
  requestId: string;
}

interface RequestMetrics {
  url: string;
  method: string;
  duration: number;
  status: number;
  success: boolean;
  cached: boolean;
  timestamp: number;
}

interface CacheEntry {
  data: any;
  expires: number;
  timestamp: number;
}

interface RateLimitEntry {
  count: number;
  resetTime: number;
}

const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  rateLimit: {
    requests: 100,
    window: 60000 // 1 minute
  },
  enableCache: true,
  cacheExpiry: 300000, // 5 minutes
  enableMetrics: true
};

class ApiService {
  private config: ApiConfig;
  private cache: Map<string, CacheEntry> = new Map();
  private rateLimits: Map<string, RateLimitEntry> = new Map();
  private metrics: RequestMetrics[] = [];
  private requestQueue: Array<{ 
    resolve: (value: any) => void; 
    reject: (reason: any) => void; 
    request: () => Promise<any> 
  }> = [];
  private activeRequests = 0;
  private maxConcurrentRequests = 10;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.startMetricsCleanup();
  }

  /**
   * Make authenticated API request with advanced features
   */
  async request<T = any>(endpoint: string, options: RequestInit & {
    skipCache?: boolean;
    skipRateLimit?: boolean;
    priority?: 'low' | 'normal' | 'high';
  } = {}): Promise<ApiResponse<T>> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();
    
    try {
      // Check rate limits
      if (!options.skipRateLimit && !this.checkRateLimit(endpoint)) {
        throw this.createApiError('Rate limit exceeded', 429, 'RATE_LIMIT_EXCEEDED', requestId);
      }

      // Check cache first
      if (!options.skipCache && options.method !== 'POST' && options.method !== 'PUT' && options.method !== 'DELETE') {
        const cached = this.getFromCache(endpoint);
        if (cached) {
          return {
            data: cached,
            status: 200,
            statusText: 'OK',
            headers: {},
            meta: {
              timestamp: Date.now(),
              requestId,
              cached: true,
              duration: Date.now() - startTime
            }
          };
        }
      }

      // Queue request if at max concurrent limit
      if (this.activeRequests >= this.maxConcurrentRequests) {
        return new Promise((resolve, reject) => {
          this.requestQueue.push({
            resolve,
            reject,
            request: () => this.executeRequest<T>(endpoint, options, requestId, startTime)
          });
        });
      }

      return await this.executeRequest<T>(endpoint, options, requestId, startTime);
    } catch (error: any) {
      if (error instanceof Error) {
        throw this.createApiError(error.message, 0, 'NETWORK_ERROR', requestId);
      }
      throw error;
    }
  }

  /**
   * Execute the actual HTTP request
   */
  private async executeRequest<T>(
    endpoint: string, 
    options: RequestInit & { skipCache?: boolean }, 
    requestId: string, 
    startTime: number
  ): Promise<ApiResponse<T>> {
    this.activeRequests++;
    
    try {
      const url = `${this.config.baseUrl}${endpoint}`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      const defaultOptions: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          'X-Client-Version': '2.0.0',
          ...this.getAuthHeaders(),
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      };

      let attempt = 0;
      let lastError: any;

      while (attempt < this.config.retries) {
        try {
          const response = await fetch(url, defaultOptions);
          clearTimeout(timeoutId);

          const responseHeaders = this.headersToObject(response.headers);
          
          if (!response.ok) {
            const errorData = await this.parseErrorResponse(response);
            throw this.createApiError(
              errorData.message || response.statusText,
              response.status,
              errorData.code,
              requestId
            );
          }

          const data = await this.parseResponse<T>(response);
          const duration = Date.now() - startTime;

          // Cache successful GET requests
          if (!options.skipCache && options.method !== 'POST' && options.method !== 'PUT' && options.method !== 'DELETE') {
            this.setCache(endpoint, data);
          }

          // Record metrics
          this.recordMetric({
            url: endpoint,
            method: options.method || 'GET',
            duration,
            status: response.status,
            success: true,
            cached: false,
            timestamp: Date.now()
          });

          const result: ApiResponse<T> = {
            data,
            status: response.status,
            statusText: response.statusText,
            headers: responseHeaders,
            meta: {
              timestamp: Date.now(),
              requestId,
              cached: false,
              duration
            }
          };

          return result;
        } catch (error: any) {
          lastError = error;
          attempt++;
          
          if (attempt < this.config.retries && this.isRetryableError(error)) {
            await this.sleep(this.config.retryDelay * attempt);
            continue;
          }
          
          break;
        }
      }

      throw lastError;
    } finally {
      this.activeRequests--;
      this.processQueue();
    }
  }

  /**
   * Parse response based on content type
   */
  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    if (contentType && contentType.includes('text/')) {
      return await response.text() as any;
    }
    
    if (contentType && contentType.includes('application/octet-stream')) {
      return await response.blob() as any;
    }
    
    return await response.json();
  }

  /**
   * Parse error response
   */
  private async parseErrorResponse(response: Response): Promise<any> {
    try {
      return await response.json();
    } catch {
      return { message: response.statusText };
    }
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    const token = this.getAuthToken();
    if (token) {
      return { 'Authorization': `Bearer ${token}` };
    }
    return {};
  }

  /**
   * Get auth token from storage
   */
  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    }
    return null;
  }

  /**
   * Convert Headers to plain object
   */
  private headersToObject(headers: Headers): Record<string, string> {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: any): boolean {
    if (error.name === 'AbortError') return false;
    if (error.status && error.status >= 400 && error.status < 500) return false;
    return true;
  }

  /**
   * Rate limiting
   */
  private checkRateLimit(endpoint: string): boolean {
    const now = Date.now();
    const limit = this.rateLimits.get(endpoint);
    
    if (!limit || now > limit.resetTime) {
      this.rateLimits.set(endpoint, {
        count: 1,
        resetTime: now + this.config.rateLimit.window
      });
      return true;
    }
    
    if (limit.count >= this.config.rateLimit.requests) {
      return false;
    }
    
    limit.count++;
    return true;
  }

  /**
   * Cache management
   */
  private getFromCache(key: string): any | null {
    if (!this.config.enableCache) return null;
    
    const entry = this.cache.get(key);
    if (entry && entry.expires > Date.now()) {
      return entry.data;
    }
    
    if (entry) {
      this.cache.delete(key);
    }
    
    return null;
  }

  private setCache(key: string, data: any): void {
    if (!this.config.enableCache) return;
    
    this.cache.set(key, {
      data,
      expires: Date.now() + this.config.cacheExpiry,
      timestamp: Date.now()
    });
  }

  /**
   * Metrics collection
   */
  private recordMetric(metric: RequestMetrics): void {
    if (!this.config.enableMetrics) return;
    
    this.metrics.push(metric);
    
    // Keep only last 1000 metrics
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
  }

  /**
   * Get API metrics
   */
  getMetrics(): {
    totalRequests: number;
    successRate: number;
    averageResponseTime: number;
    errorRate: number;
    cacheHitRate: number;
    recentErrors: RequestMetrics[];
  } {
    const recent = this.metrics.slice(-100);
    const successful = recent.filter(m => m.success);
    const errors = recent.filter(m => !m.success);
    const cached = recent.filter(m => m.cached);
    
    return {
      totalRequests: this.metrics.length,
      successRate: recent.length > 0 ? (successful.length / recent.length) * 100 : 0,
      averageResponseTime: recent.length > 0 ? recent.reduce((sum, m) => sum + m.duration, 0) / recent.length : 0,
      errorRate: recent.length > 0 ? (errors.length / recent.length) * 100 : 0,
      cacheHitRate: recent.length > 0 ? (cached.length / recent.length) * 100 : 0,
      recentErrors: errors.slice(-10)
    };
  }

  /**
   * Utility methods
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private createApiError(message: string, status: number, code?: string, requestId?: string): ApiError {
    return {
      message,
      status,
      code,
      timestamp: Date.now(),
      requestId: requestId || 'unknown'
    };
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private processQueue(): void {
    if (this.requestQueue.length > 0 && this.activeRequests < this.maxConcurrentRequests) {
      const { resolve, reject, request } = this.requestQueue.shift()!;
      request().then(resolve).catch(reject);
    }
  }

  private startMetricsCleanup(): void {
    setInterval(() => {
      const cutoff = Date.now() - (24 * 60 * 60 * 1000); // 24 hours
      this.metrics = this.metrics.filter(m => m.timestamp > cutoff);
    }, 60 * 60 * 1000); // Run every hour
  }

  /**
   * Clear cache and reset state
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Reset rate limits
   */
  resetRateLimits(): void {
    this.rateLimits.clear();
  }

  // === ENTERPRISE API ENDPOINTS ===

  // Health Check
  async getHealth(): Promise<ApiResponse> {
    return this.request('/health');
  }

  // Content Management
  async getContent(params?: { limit?: number; offset?: number; type?: string }): Promise<ApiResponse> {
    const query = params ? '?' + new URLSearchParams(params as any).toString() : '';
    return this.request(`/api/v1/content${query}`);
  }

  async uploadContent(file: File, metadata?: any): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    return this.request('/api/v1/content/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove Content-Type header to let browser set it with boundary
    });
  }

  async updateContent(contentId: string, data: any): Promise<ApiResponse> {
    return this.request(`/api/v1/content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteContent(contentId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/content/${contentId}`, {
      method: 'DELETE',
    });
  }

  // AI Agents Enterprise
  async getAgents(category?: string): Promise<ApiResponse> {
    const query = category ? `?category=${category}` : '';
    return this.request(`/api/v1/agents${query}`);
  }

  async runAgent(agentId: string, data?: any, options?: { priority?: 'low' | 'normal' | 'high' }): Promise<ApiResponse> {
    return this.request(`/api/v1/agents/${agentId}/run`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
      ...(options?.priority && { priority: options.priority as any })
    });
  }

  async getAgentStatus(agentId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/agents/${agentId}/status`);
  }

  async stopAgent(agentId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/agents/${agentId}/stop`, {
      method: 'POST',
    });
  }

  // Crawlers Enterprise
  async getCrawlers(): Promise<ApiResponse> {
    return this.request('/api/v1/crawlers');
  }

  async runCrawler(crawlerId: string, data?: any): Promise<ApiResponse> {
    return this.request(`/api/v1/crawlers/${crawlerId}/run`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }

  async getCrawlerResults(crawlerId: string, runId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/crawlers/${crawlerId}/runs/${runId}/results`);
  }

  // Violations & Protection
  async getViolations(filters?: { status?: string; severity?: string }): Promise<ApiResponse> {
    const query = filters ? '?' + new URLSearchParams(filters).toString() : '';
    return this.request(`/api/v1/violations${query}`);
  }

  async reportViolation(data: any): Promise<ApiResponse> {
    return this.request('/api/v1/violations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateViolationStatus(violationId: string, status: string): Promise<ApiResponse> {
    return this.request(`/api/v1/violations/${violationId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Analytics Enterprise
  async getRevenue(period?: { start?: string; end?: string }): Promise<ApiResponse> {
    const query = period ? '?' + new URLSearchParams(period).toString() : '';
    return this.request(`/api/v1/analytics/revenue${query}`);
  }

  async getAnalyticsMetrics(type?: string): Promise<ApiResponse> {
    const query = type ? `?type=${type}` : '';
    return this.request(`/api/v1/analytics/metrics${query}`);
  }

  async getEarnings(userId?: string): Promise<ApiResponse> {
    const query = userId ? `?user_id=${userId}` : '';
    return this.request(`/api/v1/analytics/earnings${query}`);
  }

  async getPerformanceMetrics(): Promise<ApiResponse> {
    return this.request('/api/v1/analytics/performance');
  }

  // Authentication Enterprise
  async login(email: string, password: string, rememberMe?: boolean): Promise<ApiResponse> {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    });
  }

  async logout(): Promise<ApiResponse> {
    return this.request('/api/v1/auth/logout', {
      method: 'POST',
    });
  }

  async refreshToken(): Promise<ApiResponse> {
    return this.request('/api/v1/auth/refresh', {
      method: 'POST',
    });
  }

  async resetPassword(email: string): Promise<ApiResponse> {
    return this.request('/api/v1/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse> {
    return this.request('/api/v1/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  // Content Protection Enterprise
  async protectContent(contentId: string, protectionLevel: string, options?: any): Promise<ApiResponse> {
    return this.request(`/api/v1/content/${contentId}/protect`, {
      method: 'POST',
      body: JSON.stringify({ protection_level: protectionLevel, ...options }),
    });
  }

  async generateFingerprint(contentId: string, type?: string): Promise<ApiResponse> {
    return this.request(`/api/v1/content/${contentId}/fingerprint`, {
      method: 'POST',
      body: JSON.stringify({ type }),
    });
  }

  async scanForViolations(contentId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/content/${contentId}/scan`, {
      method: 'POST',
    });
  }

  // Monitoring Enterprise
  async getMonitoringStatus(): Promise<ApiResponse> {
    return this.request('/api/v1/monitoring/status');
  }

  async getSystemHealth(): Promise<ApiResponse> {
    return this.request('/api/v1/monitoring/health');
  }

  async getAlerts(filters?: { severity?: string; status?: string }): Promise<ApiResponse> {
    const query = filters ? '?' + new URLSearchParams(filters).toString() : '';
    return this.request(`/api/v1/alerts${query}`);
  }

  async acknowledgeAlert(alertId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
  }

  // Real-time Features
  async getRealtimeMetrics(): Promise<ApiResponse> {
    return this.request('/api/v1/realtime/metrics');
  }

  async subscribeToUpdates(channels: string[]): Promise<ApiResponse> {
    return this.request('/api/v1/realtime/subscribe', {
      method: 'POST',
      body: JSON.stringify({ channels }),
    });
  }

  // Collaboration Features
  async getCollaborations(): Promise<ApiResponse> {
    return this.request('/api/v1/collaborations');
  }

  async createCollaboration(data: any): Promise<ApiResponse> {
    return this.request('/api/v1/collaborations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCollaboration(collaborationId: string, data: any): Promise<ApiResponse> {
    return this.request(`/api/v1/collaborations/${collaborationId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Platform Integration
  async getPlatforms(): Promise<ApiResponse> {
    return this.request('/api/v1/platforms');
  }

  async connectPlatform(platformId: string, credentials: any): Promise<ApiResponse> {
    return this.request(`/api/v1/platforms/${platformId}/connect`, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async syncPlatform(platformId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/platforms/${platformId}/sync`, {
      method: 'POST',
    });
  }

  // User Management
  async getProfile(): Promise<ApiResponse> {
    return this.request('/api/v1/user/profile');
  }

  async updateProfile(data: any): Promise<ApiResponse> {
    return this.request('/api/v1/user/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getPreferences(): Promise<ApiResponse> {
    return this.request('/api/v1/user/preferences');
  }

  async updatePreferences(preferences: any): Promise<ApiResponse> {
    return this.request('/api/v1/user/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  // Advanced Search
  async search(query: string, filters?: any): Promise<ApiResponse> {
    return this.request('/api/v1/search', {
      method: 'POST',
      body: JSON.stringify({ query, filters }),
    });
  }

  async getSearchSuggestions(query: string): Promise<ApiResponse> {
    return this.request(`/api/v1/search/suggestions?q=${encodeURIComponent(query)}`);
  }

  // Batch Operations
  async batchOperation(operation: string, items: any[]): Promise<ApiResponse> {
    return this.request('/api/v1/batch', {
      method: 'POST',
      body: JSON.stringify({ operation, items }),
    });
  }

  // File Management
  async uploadFile(file: File, path?: string): Promise<ApiResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (path) {
      formData.append('path', path);
    }
    
    return this.request('/api/v1/files/upload', {
      method: 'POST',
      body: formData,
      headers: {},
    });
  }

  async downloadFile(fileId: string): Promise<Blob> {
    const response = await this.request(`/api/v1/files/${fileId}/download`);
    return response.data;
  }

  async deleteFile(fileId: string): Promise<ApiResponse> {
    return this.request(`/api/v1/files/${fileId}`, {
      method: 'DELETE',
    });
  }
}

// Singleton instance with enterprise configuration
export const apiService = new ApiService({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
  rateLimit: {
    requests: 100,
    window: 60000
  },
  enableCache: true,
  cacheExpiry: 300000,
  enableMetrics: true
});

// React hooks for API usage
export function useApiService() {
  const get = (endpoint: string, options?: any) => apiService.request(endpoint, { method: 'GET', ...options });
  const post = (endpoint: string, data?: any, options?: any) => apiService.request(endpoint, { method: 'POST', body: JSON.stringify(data), ...options });
  const put = (endpoint: string, data?: any, options?: any) => apiService.request(endpoint, { method: 'PUT', body: JSON.stringify(data), ...options });
  const del = (endpoint: string, options?: any) => apiService.request(endpoint, { method: 'DELETE', ...options });

  return { get, post, put, del, service: apiService };
}

export default apiService;
