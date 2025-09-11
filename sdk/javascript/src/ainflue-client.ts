/**
 * Core Ainflue Client Implementation
 * 
 * Enterprise-grade TypeScript client with multi-expert design:
 * - Lead Dev IA: AI-powered content analysis and processing
 * - Backend Senior: Robust HTTP client with retry logic
 * - Sécurité: Secure authentication and request validation
 * - DevOps: Performance monitoring and error tracking
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 */

import { EventEmitter } from './utils/event-emitter';
import { Logger } from './utils/logger';
import { HttpClient } from './http-client';
import { ApiClient } from './api-client';
import { AuthManager } from './auth/auth-manager';
import { CacheManager } from './utils/cache-manager';
import { RetryHandler } from './utils/retry-handler';

import {
  AinflueClientOptions,
  RequestOptions,
  ContentMetadata,
  AnalysisOptions,
  ProtectionOptions,
  UploadOptions,
  UploadResult,
  ContentAnalysisResult,
  ContentProtectionResult,
  UserProfile,
  AnalyticsData,
  ApiResponse,
  EventType,
  EventData
} from './types';

import {
  AinflueError,
  AuthenticationError,
  ValidationError,
  NetworkError,
  RateLimitError
} from './errors';

/**
 * Main Ainflue SDK Client
 * 
 * Provides comprehensive access to the Ainflue platform:
 * - Content upload and analysis
 * - AI-powered content protection
 * - User management and analytics
 * - Real-time event handling
 */
export class AinflueClient extends EventEmitter {
  private readonly config: Required<AinflueClientOptions>;
  private readonly logger: Logger;
  private readonly httpClient: HttpClient;
  private readonly apiClient: ApiClient;
  private readonly authManager: AuthManager;
  private readonly cacheManager: CacheManager;
  private readonly retryHandler: RetryHandler;
  
  // Client state
  private isInitialized = false;
  private metrics = {
    requestCount: 0,
    errorCount: 0,
    lastRequestTime: 0,
    averageResponseTime: 0
  };

  constructor(options: AinflueClientOptions) {
    super();
    
    // Merge with defaults
    this.config = {
      baseUrl: 'https://api.ainflue.com',
      apiVersion: 'v1',
      timeout: 30000,
      maxRetries: 3,
      retryDelay: 1000,
      enableLogging: true,
      enableCaching: true,
      enableMetrics: true,
      customHeaders: {},
      authProvider: 'api_key',
      environment: 'production',
      ...options
    };

    // Initialize core components
    this.logger = new Logger({
      level: this.config.enableLogging ? 'info' : 'error',
      prefix: 'AinflueClient'
    });

    this.retryHandler = new RetryHandler({
      maxRetries: this.config.maxRetries,
      retryDelay: this.config.retryDelay
    });

    this.cacheManager = new CacheManager({
      enabled: this.config.enableCaching,
      ttl: 300000, // 5 minutes default
      maxSize: 100
    });

    this.httpClient = new HttpClient({
      baseURL: `${this.config.baseUrl}/${this.config.apiVersion}`,
      timeout: this.config.timeout,
      headers: {
        'User-Agent': 'Ainflue-JS-SDK/1.0.0',
        'X-SDK-Version': '1.0.0',
        ...this.config.customHeaders
      }
    });

    this.apiClient = new ApiClient(this.httpClient, {
      retryHandler: this.retryHandler,
      cacheManager: this.cacheManager,
      logger: this.logger
    });

    this.authManager = new AuthManager({
      provider: this.config.authProvider,
      apiKey: this.config.apiKey,
      logger: this.logger
    });

    this.logger.info(`Ainflue Client initialized for ${this.config.environment} environment`);
  }

  /**
   * Initialize the client
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      this.logger.info('Initializing Ainflue Client...');

      // Initialize authentication
      await this.authManager.initialize();

      // Set auth headers
      const authHeaders = await this.authManager.getAuthHeaders();
      this.httpClient.setDefaultHeaders(authHeaders);

      // Verify connection
      await this.healthCheck();

      this.isInitialized = true;
      this.emit('initialized', { timestamp: new Date() });
      
      this.logger.info('Ainflue Client initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize client:', error);
      throw new AinflueError('Client initialization failed', { originalError: error });
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; timestamp: Date; version: string }> {
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.get<{
        status: string;
        version: string;
        timestamp: string;
      }>('/health');

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      return {
        status: response.data.status,
        timestamp: new Date(response.data.timestamp),
        version: response.data.version
      };
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Upload content for analysis and protection
   */
  async uploadContent(
    file: File | Blob | ArrayBuffer,
    options: UploadOptions = {}
  ): Promise<UploadResult> {
    this.ensureInitialized();
    
    const startTime = performance.now();
    
    try {
      this.logger.info('Starting content upload...');

      // Validate file
      this.validateUploadFile(file);

      // Prepare form data
      const formData = new FormData();
      
      if (file instanceof File) {
        formData.append('file', file, options.filename || file.name);
      } else if (file instanceof Blob) {
        formData.append('file', file, options.filename || 'blob');
      } else {
        // ArrayBuffer
        const blob = new Blob([file]);
        formData.append('file', blob, options.filename || 'file');
      }

      // Add metadata
      if (options.contentType) {
        formData.append('contentType', options.contentType);
      }
      
      if (options.tags) {
        formData.append('tags', JSON.stringify(options.tags));
      }

      if (options.metadata) {
        formData.append('metadata', JSON.stringify(options.metadata));
      }

      if (options.analysisOptions) {
        formData.append('analysisOptions', JSON.stringify(options.analysisOptions));
      }

      if (options.protectionOptions) {
        formData.append('protectionOptions', JSON.stringify(options.protectionOptions));
      }

      // Upload with progress tracking
      const response = await this.apiClient.post<UploadResult>('/content/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: options.onProgress ? (progressEvent) => {
          if (options.onProgress) {
            const progress = {
              loaded: progressEvent.loaded || 0,
              total: progressEvent.total || 0,
              percentage: progressEvent.total ? (progressEvent.loaded / progressEvent.total) * 100 : 0,
              stage: 'uploading' as const
            };
            options.onProgress(progress);
          }
        } : undefined
      });

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      this.emit('upload_complete', {
        uploadId: response.data.uploadId,
        contentId: response.data.contentId,
        duration: responseTime
      });

      this.logger.info(`Content uploaded successfully: ${response.data.contentId}`);
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      this.emit('upload_error', { error: error.message });
      throw this.handleError(error);
    }
  }

  /**
   * Analyze content
   */
  async analyzeContent(
    contentId: string,
    options: AnalysisOptions = { analysisTypes: ['fingerprint'] }
  ): Promise<ContentAnalysisResult> {
    this.ensureInitialized();
    
    const cacheKey = `analysis:${contentId}:${JSON.stringify(options)}`;
    
    // Check cache first
    const cached = this.cacheManager.get<ContentAnalysisResult>(cacheKey);
    if (cached) {
      this.logger.debug(`Returning cached analysis for ${contentId}`);
      return cached;
    }

    const startTime = performance.now();
    
    try {
      this.logger.info(`Analyzing content: ${contentId}`);

      const response = await this.apiClient.post<ContentAnalysisResult>('/content/analyze', {
        contentId,
        options
      });

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      // Cache the result
      this.cacheManager.set(cacheKey, response.data, { ttl: 600000 }); // 10 minutes

      this.emit('analysis_complete', {
        contentId,
        analysisId: response.data.analysisId,
        duration: responseTime
      });

      this.logger.info(`Content analysis completed: ${response.data.analysisId}`);
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Enable content protection
   */
  async protectContent(
    contentId: string,
    options: ProtectionOptions
  ): Promise<ContentProtectionResult> {
    this.ensureInitialized();
    
    const startTime = performance.now();
    
    try {
      this.logger.info(`Enabling protection for content: ${contentId}`);

      const response = await this.apiClient.post<ContentProtectionResult>('/content/protect', {
        contentId,
        options
      });

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      this.emit('protection_enabled', {
        contentId,
        protectionId: response.data.protectionId,
        platforms: response.data.platforms.map(p => p.name),
        duration: responseTime
      });

      this.logger.info(`Content protection enabled: ${response.data.protectionId}`);
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Get user profile
   */
  async getUserProfile(): Promise<UserProfile> {
    this.ensureInitialized();
    
    const cacheKey = 'user:profile';
    
    // Check cache first
    const cached = this.cacheManager.get<UserProfile>(cacheKey);
    if (cached) {
      return cached;
    }

    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.get<UserProfile>('/user/profile');

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      // Cache for 5 minutes
      this.cacheManager.set(cacheKey, response.data, { ttl: 300000 });
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Update user profile
   */
  async updateUserProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    this.ensureInitialized();
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.put<UserProfile>('/user/profile', updates);

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      // Invalidate cache
      this.cacheManager.delete('user:profile');

      this.emit('profile_updated', { updates, duration: responseTime });
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Get analytics data
   */
  async getAnalytics(
    startDate?: Date,
    endDate?: Date,
    filters?: Record<string, any>
  ): Promise<AnalyticsData> {
    this.ensureInitialized();
    
    const params: Record<string, string> = {};
    
    if (startDate) {
      params.startDate = startDate.toISOString();
    }
    
    if (endDate) {
      params.endDate = endDate.toISOString();
    }
    
    if (filters) {
      params.filters = JSON.stringify(filters);
    }

    const cacheKey = `analytics:${JSON.stringify(params)}`;
    
    // Check cache first
    const cached = this.cacheManager.get<AnalyticsData>(cacheKey);
    if (cached) {
      return cached;
    }

    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.get<AnalyticsData>('/analytics/data', { params });

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);

      // Cache for 1 hour
      this.cacheManager.set(cacheKey, response.data, { ttl: 3600000 });
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Search content
   */
  async searchContent(
    query: string,
    filters?: Record<string, any>,
    pagination?: { page: number; limit: number }
  ): Promise<{
    results: ContentMetadata[];
    total: number;
    page: number;
    totalPages: number;
  }> {
    this.ensureInitialized();
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.get('/content/search', {
        params: {
          q: query,
          filters: filters ? JSON.stringify(filters) : undefined,
          page: pagination?.page || 1,
          limit: pagination?.limit || 20
        }
      });

      const responseTime = performance.now() - startTime;
      this.updateMetrics(responseTime, true);
      
      return response.data;
    } catch (error) {
      this.updateMetrics(performance.now() - startTime, false);
      throw this.handleError(error);
    }
  }

  /**
   * Get client metrics
   */
  getMetrics(): {
    requestCount: number;
    errorCount: number;
    successRate: number;
    averageResponseTime: number;
    lastRequestTime: number;
  } {
    const successRate = this.metrics.requestCount > 0 
      ? ((this.metrics.requestCount - this.metrics.errorCount) / this.metrics.requestCount) * 100 
      : 0;

    return {
      requestCount: this.metrics.requestCount,
      errorCount: this.metrics.errorCount,
      successRate,
      averageResponseTime: this.metrics.averageResponseTime,
      lastRequestTime: this.metrics.lastRequestTime
    };
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cacheManager.clear();
    this.logger.info('Cache cleared');
  }

  /**
   * Dispose client resources
   */
  async dispose(): Promise<void> {
    this.logger.info('Disposing Ainflue Client...');
    
    // Clear cache
    this.clearCache();
    
    // Dispose auth manager
    await this.authManager.dispose();
    
    // Remove all listeners
    this.removeAllListeners();
    
    this.isInitialized = false;
    this.logger.info('Ainflue Client disposed');
  }

  // Private helper methods

  private ensureInitialized(): void {
    if (!this.isInitialized) {
      throw new AinflueError('Client not initialized. Call initialize() first.');
    }
  }

  private validateUploadFile(file: File | Blob | ArrayBuffer): void {
    const maxSize = 100 * 1024 * 1024; // 100MB
    
    let size: number;
    
    if (file instanceof File) {
      size = file.size;
    } else if (file instanceof Blob) {
      size = file.size;
    } else {
      size = file.byteLength;
    }
    
    if (size > maxSize) {
      throw new ValidationError(`File size (${size} bytes) exceeds maximum allowed size (${maxSize} bytes)`);
    }
    
    if (size === 0) {
      throw new ValidationError('File is empty');
    }
  }

  private updateMetrics(responseTime: number, success: boolean): void {
    if (!this.config.enableMetrics) {
      return;
    }
    
    this.metrics.requestCount++;
    this.metrics.lastRequestTime = Date.now();
    
    if (!success) {
      this.metrics.errorCount++;
    }
    
    // Update average response time (exponential moving average)
    const alpha = 0.1;
    this.metrics.averageResponseTime = 
      this.metrics.averageResponseTime * (1 - alpha) + responseTime * alpha;
  }

  private handleError(error: any): AinflueError {
    this.logger.error('API Error:', error);
    
    if (error instanceof AinflueError) {
      return error;
    }
    
    // Handle different error types
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          return new AuthenticationError('Authentication failed', { status, data });
        case 422:
          return new ValidationError('Validation failed', { status, data });
        case 429:
          return new RateLimitError('Rate limit exceeded', { status, data });
        case 500:
        case 502:
        case 503:
        case 504:
          return new NetworkError('Server error', { status, data });
        default:
          return new AinflueError(`HTTP error ${status}`, { status, data });
      }
    } else if (error.code === 'NETWORK_ERROR') {
      return new NetworkError('Network connection failed', { originalError: error });
    } else {
      return new AinflueError(error.message || 'Unknown error', { originalError: error });
    }
  }
}