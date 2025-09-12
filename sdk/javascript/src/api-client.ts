/**
 * API Client Implementation for Ainflue JavaScript SDK
 * High-level API client with intelligent routing and business logic integration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Lead Dev IA + Backend Senior + Business Logic + Security
 */

import { HttpClient } from './http-client';
import { AinflueConfig } from './config';
import { ApiResponse, CreatorProfile, ContentItem, AnalyticsData, AIProcessingRequest, AIProcessingResponse } from './interfaces';
import { AuthenticationError, ValidationError, ErrorHandler } from './errors';

/**
 * Main API Client for Ainflue Platform
 * Provides business logic integration across the complete Creator workflow
 */
export class ApiClient {
  private httpClient: HttpClient;
  private config: AinflueConfig;

  constructor(config: AinflueConfig) {
    this.config = config;
    this.httpClient = new HttpClient(config);
  }

  // ==========================================
  // CREATOR ONBOARDING & PROFILE MANAGEMENT
  // Implementation: Backend Senior + Lead Dev IA
  // ==========================================

  /**
   * Register new creator account with AI-powered profile optimization
   */
  async registerCreator(profileData: Partial<CreatorProfile>): Promise<ApiResponse<CreatorProfile>> {
    this.validateCreatorProfile(profileData);
    
    return this.httpClient.post<CreatorProfile>('/api/v1/creators/register', {
      ...profileData,
      registrationSource: 'sdk',
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Get creator profile with AI insights
   */
  async getCreatorProfile(creatorId: string): Promise<ApiResponse<CreatorProfile>> {
    return this.httpClient.get<CreatorProfile>(`/api/v1/creators/${creatorId}`);
  }

  /**
   * Update creator profile with intelligent validation
   */
  async updateCreatorProfile(creatorId: string, updates: Partial<CreatorProfile>): Promise<ApiResponse<CreatorProfile>> {
    this.validateCreatorProfile(updates);
    
    return this.httpClient.put<CreatorProfile>(`/api/v1/creators/${creatorId}`, updates);
  }

  // ==========================================
  // CONTENT UPLOAD & MANAGEMENT
  // Implementation: Audio Engineer + ML Engineer + Backend Senior
  // ==========================================

  /**
   * Upload content with multi-format support and AI analysis
   */
  async uploadContent(contentData: FormData, metadata: Partial<ContentItem>): Promise<ApiResponse<ContentItem>> {
    // Validate content metadata
    this.validateContentMetadata(metadata);

    // Enhanced upload with progress tracking
    const response = await this.httpClient.request<ContentItem>('POST', '/api/v1/content/upload', {
      body: contentData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: this.config.uploadTimeout || 120, // Extended timeout for uploads
    });

    return response;
  }

  /**
   * Get content details with AI analysis results
   */
  async getContent(contentId: string): Promise<ApiResponse<ContentItem>> {
    return this.httpClient.get<ContentItem>(`/api/v1/content/${contentId}`);
  }

  /**
   * Update content metadata and trigger reprocessing
   */
  async updateContent(contentId: string, updates: Partial<ContentItem>): Promise<ApiResponse<ContentItem>> {
    this.validateContentMetadata(updates);
    
    return this.httpClient.put<ContentItem>(`/api/v1/content/${contentId}`, updates);
  }

  /**
   * Delete content with proper cleanup
   */
  async deleteContent(contentId: string): Promise<ApiResponse<void>> {
    return this.httpClient.delete<void>(`/api/v1/content/${contentId}`);
  }

  /**
   * List creator's content with filtering and pagination
   */
  async listContent(creatorId: string, filters?: {
    type?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ items: ContentItem[]; total: number; hasMore: boolean }>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.httpClient.get(`/api/v1/creators/${creatorId}/content${query}`);
  }

  // ==========================================
  // AI PROCESSING & ANALYSIS
  // Implementation: Lead Dev IA + ML Engineer + IA Prompt Engineer
  // ==========================================

  /**
   * Submit content for AI processing with intelligent routing
   */
  async submitForAIProcessing(request: AIProcessingRequest): Promise<ApiResponse<AIProcessingResponse>> {
    this.validateAIProcessingRequest(request);

    return this.httpClient.post<AIProcessingResponse>('/api/v1/ai/process', {
      ...request,
      processingMode: request.processingMode || 'standard',
      priority: request.priority || 'normal',
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Get AI processing status and results
   */
  async getAIProcessingStatus(processingId: string): Promise<ApiResponse<AIProcessingResponse>> {
    return this.httpClient.get<AIProcessingResponse>(`/api/v1/ai/process/${processingId}`);
  }

  /**
   * Get AI insights for content optimization
   */
  async getAIInsights(contentId: string, insightTypes?: string[]): Promise<ApiResponse<any>> {
    const params = insightTypes ? `?types=${insightTypes.join(',')}` : '';
    return this.httpClient.get(`/api/v1/ai/insights/${contentId}${params}`);
  }

  // ==========================================
  // CONTENT PROTECTION & COPYRIGHT
  // Implementation: Security + Legal + Blockchain
  // ==========================================

  /**
   * Enable copyright protection for content
   */
  async enableCopyrightProtection(contentId: string, protectionOptions?: {
    watermarkLevel?: 'light' | 'medium' | 'heavy';
    fingerprintEnabled?: boolean;
    blockchainRegistration?: boolean;
  }): Promise<ApiResponse<{ protectionId: string; status: string }>> {
    return this.httpClient.post(`/api/v1/protection/copyright/${contentId}`, protectionOptions || {});
  }

  /**
   * Check for copyright violations
   */
  async checkCopyrightViolations(contentId: string): Promise<ApiResponse<any>> {
    return this.httpClient.get(`/api/v1/protection/violations/${contentId}`);
  }

  // ==========================================
  // SEO OPTIMIZATION
  // Implementation: SEO + Lead Dev IA + ML Engineer
  // ==========================================

  /**
   * Generate SEO optimizations for content
   */
  async generateSEOOptimizations(contentId: string, targetKeywords?: string[]): Promise<ApiResponse<any>> {
    const body = targetKeywords ? { keywords: targetKeywords } : {};
    return this.httpClient.post(`/api/v1/seo/optimize/${contentId}`, body);
  }

  /**
   * Get SEO performance analytics
   */
  async getSEOAnalytics(contentId: string, dateRange?: { from: string; to: string }): Promise<ApiResponse<any>> {
    const params = dateRange ? `?from=${dateRange.from}&to=${dateRange.to}` : '';
    return this.httpClient.get(`/api/v1/seo/analytics/${contentId}${params}`);
  }

  // ==========================================
  // COLLABORATION & PARTNERSHIPS
  // Implementation: Business + Microservices + Backend Senior
  // ==========================================

  /**
   * Create collaboration request
   */
  async createCollaboration(collaborationData: {
    partnerId: string;
    projectType: string;
    description: string;
    terms?: any;
  }): Promise<ApiResponse<any>> {
    return this.httpClient.post('/api/v1/collaborations', collaborationData);
  }

  /**
   * List collaboration opportunities
   */
  async listCollaborations(filters?: {
    status?: string;
    type?: string;
    limit?: number;
  }): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.httpClient.get(`/api/v1/collaborations${query}`);
  }

  // ==========================================
  // DISTRIBUTION & PUBLISHING
  // Implementation: Microservices + DevOps + Backend Senior
  // ==========================================

  /**
   * Publish content to multiple platforms
   */
  async publishToplatforms(contentId: string, platforms: string[], scheduledDate?: string): Promise<ApiResponse<any>> {
    return this.httpClient.post(`/api/v1/distribution/publish/${contentId}`, {
      platforms,
      scheduledDate,
      publishMode: 'multi-platform',
    });
  }

  /**
   * Get publishing status across platforms
   */
  async getPublishingStatus(contentId: string): Promise<ApiResponse<any>> {
    return this.httpClient.get(`/api/v1/distribution/status/${contentId}`);
  }

  // ==========================================
  // MONETIZATION & REVENUE
  // Implementation: Business + DBA + Security
  // ==========================================

  /**
   * Get revenue analytics
   */
  async getRevenueAnalytics(creatorId: string, dateRange?: { from: string; to: string }): Promise<ApiResponse<any>> {
    const params = dateRange ? `?from=${dateRange.from}&to=${dateRange.to}` : '';
    return this.httpClient.get(`/api/v1/revenue/analytics/${creatorId}${params}`);
  }

  /**
   * Setup monetization for content
   */
  async setupMonetization(contentId: string, monetizationConfig: {
    type: 'subscription' | 'pay-per-view' | 'ads' | 'sponsorship';
    pricing?: any;
    restrictions?: any;
  }): Promise<ApiResponse<any>> {
    return this.httpClient.post(`/api/v1/monetization/setup/${contentId}`, monetizationConfig);
  }

  // ==========================================
  // ANALYTICS & INSIGHTS
  // Implementation: ML Engineer + DBA + Lead Dev IA
  // ==========================================

  /**
   * Get comprehensive analytics data
   */
  async getAnalytics(creatorId: string, metrics: string[], dateRange?: { from: string; to: string }): Promise<ApiResponse<AnalyticsData>> {
    const body = {
      metrics,
      dateRange,
      includeAIInsights: true,
    };

    return this.httpClient.post<AnalyticsData>(`/api/v1/analytics/${creatorId}`, body);
  }

  /**
   * Get real-time performance metrics
   */
  async getRealTimeMetrics(contentId: string): Promise<ApiResponse<any>> {
    return this.httpClient.get(`/api/v1/analytics/realtime/${contentId}`);
  }

  // ==========================================
  // VALIDATION METHODS
  // Implementation: Security + Backend Senior
  // ==========================================

  private validateCreatorProfile(profile: Partial<CreatorProfile>): void {
    if (profile.email && !this.isValidEmail(profile.email)) {
      throw new ValidationError('Invalid email format', 'email', profile.email);
    }

    if (profile.username && (!profile.username || profile.username.length < 3)) {
      throw new ValidationError('Username must be at least 3 characters', 'username', profile.username);
    }
  }

  private validateContentMetadata(metadata: Partial<ContentItem>): void {
    if (metadata.title && metadata.title.length < 1) {
      throw new ValidationError('Content title is required', 'title', metadata.title);
    }

    if (metadata.type && !['image', 'video', 'audio', 'document'].includes(metadata.type)) {
      throw new ValidationError('Invalid content type', 'type', metadata.type);
    }
  }

  private validateAIProcessingRequest(request: AIProcessingRequest): void {
    if (!request.contentId) {
      throw new ValidationError('Content ID is required', 'contentId', request.contentId);
    }

    if (!request.processingType) {
      throw new ValidationError('Processing type is required', 'processingType', request.processingType);
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}