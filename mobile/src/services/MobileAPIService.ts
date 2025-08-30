/**
 * Mobile API Service - Professional Mobile API Management
 * 
 * Enterprise-grade mobile API service with offline support, intelligent caching,
 * automatic retry mechanisms, and comprehensive error handling.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import NetInfo from '@react-native-async-storage/async-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'crypto-js';

interface MobileAPIConfig {
  baseUrl: string;
  apiKey: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableCaching: boolean;
  enableOfflineQueue: boolean;
  encryptionKey: string;
}

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  status: number;
  cached?: boolean;
  timestamp: number;
}

interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  endpoint: string;
  data?: any;
  headers?: Record<string, string>;
  cacheKey?: string;
  cacheTTL?: number;
  priority?: 'low' | 'normal' | 'high';
  requiresAuth?: boolean;
  requiresNetwork?: boolean;
}

class MobileAPIService {
  private static instance: MobileAPIService;
  private config: MobileAPIConfig;
  private cache: Map<string, any> = new Map();
  private offlineQueue: Array<RequestConfig> = [];
  private isOnline: boolean = true;
  private authToken: string | null = null;

  private constructor(config: MobileAPIConfig) {
    this.config = config;
    this.initializeNetworkMonitoring();
    this.loadOfflineQueue();
  }

  public static getInstance(config?: MobileAPIConfig): MobileAPIService {
    if (!MobileAPIService.instance) {
      if (!config) {
        throw new Error('MobileAPIService requires configuration on first initialization');
      }
      MobileAPIService.instance = new MobileAPIService(config);
    }
    return MobileAPIService.instance;
  }

  private async initializeNetworkMonitoring(): Promise<void> {
    // Monitor network connectivity
    const netInfo = await NetInfo.fetch();
    this.isOnline = netInfo.isConnected ?? false;

    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected ?? false;

      if (!wasOnline && this.isOnline) {
        this.processOfflineQueue();
      }
    });
  }

  private async loadOfflineQueue(): Promise<void> {
    try {
      const queueData = await AsyncStorage.getItem('ainflue_api_offline_queue');
      if (queueData) {
        const decryptedData = this.decrypt(queueData);
        this.offlineQueue = JSON.parse(decryptedData);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
    }
  }

  private async saveOfflineQueue(): Promise<void> {
    try {
      const encryptedData = this.encrypt(JSON.stringify(this.offlineQueue));
      await AsyncStorage.setItem('ainflue_api_offline_queue', encryptedData);
    } catch (error) {
      console.error('Failed to save offline queue:', error);
    }
  }

  private encrypt(data: string): string {
    return CryptoJS.AES.encrypt(data, this.config.encryptionKey).toString();
  }

  private decrypt(encryptedData: string): string {
    const bytes = CryptoJS.AES.decrypt(encryptedData, this.config.encryptionKey);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  public async request<T = any>(requestConfig: RequestConfig): Promise<APIResponse<T>> {
    const {
      method,
      endpoint,
      data,
      headers = {},
      cacheKey,
      cacheTTL = 300000, // 5 minutes default
      requiresAuth = true,
      requiresNetwork = true
    } = requestConfig;

    // Check cache first for GET requests
    if (method === 'GET' && cacheKey && this.config.enableCaching) {
      const cachedResponse = await this.getCachedResponse<T>(cacheKey);
      if (cachedResponse) {
        return cachedResponse;
      }
    }

    // Handle offline scenarios
    if (!this.isOnline) {
      if (requiresNetwork) {
        if (this.config.enableOfflineQueue) {
          this.addToOfflineQueue(requestConfig);
          return {
            success: false,
            error: 'Request queued for when network is available',
            status: 0,
            timestamp: Date.now()
          };
        } else {
          return {
            success: false,
            error: 'Network unavailable and offline queue disabled',
            status: 0,
            timestamp: Date.now()
          };
        }
      }
    }

    // Prepare request headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': 'Ainflue-Mobile/1.0',
      'X-API-Key': this.config.apiKey,
      ...headers
    };

    if (requiresAuth && this.authToken) {
      requestHeaders['Authorization'] = `Bearer ${this.authToken}`;
    }

    // Prepare request URL
    const url = `${this.config.baseUrl}${endpoint}`;

    // Execute request with retry logic
    return this.executeWithRetry<T>(
      url,
      method,
      data,
      requestHeaders,
      cacheKey,
      cacheTTL
    );
  }

  private async executeWithRetry<T>(
    url: string,
    method: string,
    data: any,
    headers: Record<string, string>,
    cacheKey?: string,
    cacheTTL?: number
  ): Promise<APIResponse<T>> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        const requestOptions: RequestInit = {
          method,
          headers,
          signal: controller.signal,
        };

        if (data && method !== 'GET') {
          requestOptions.body = JSON.stringify(data);
        }

        const response = await fetch(url, requestOptions);
        clearTimeout(timeoutId);

        const responseData = await response.json();

        const apiResponse: APIResponse<T> = {
          success: response.ok,
          data: responseData,
          status: response.status,
          timestamp: Date.now()
        };

        if (!response.ok) {
          apiResponse.error = responseData.message || `HTTP ${response.status}`;
        }

        // Cache successful GET responses
        if (response.ok && method === 'GET' && cacheKey && this.config.enableCaching) {
          await this.cacheResponse(cacheKey, apiResponse, cacheTTL);
        }

        return apiResponse;

      } catch (error) {
        lastError = error as Error;

        if (attempt < this.config.retryAttempts) {
          await this.delay(this.config.retryDelay * Math.pow(2, attempt));
        }
      }
    }

    return {
      success: false,
      error: lastError?.message || 'Request failed after all retries',
      status: 0,
      timestamp: Date.now()
    };
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async getCachedResponse<T>(cacheKey: string): Promise<APIResponse<T> | null> {
    try {
      const cachedData = await AsyncStorage.getItem(`ainflue_cache_${cacheKey}`);
      if (cachedData) {
        const decryptedData = this.decrypt(cachedData);
        const parsed = JSON.parse(decryptedData);

        if (parsed.expiresAt > Date.now()) {
          return {
            ...parsed.response,
            cached: true
          };
        } else {
          await AsyncStorage.removeItem(`ainflue_cache_${cacheKey}`);
        }
      }
    } catch (error) {
      console.error('Failed to get cached response:', error);
    }

    return null;
  }

  private async cacheResponse<T>(
    cacheKey: string,
    response: APIResponse<T>,
    ttl?: number
  ): Promise<void> {
    try {
      const cacheData = {
        response,
        expiresAt: Date.now() + (ttl || 300000)
      };

      const encryptedData = this.encrypt(JSON.stringify(cacheData));
      await AsyncStorage.setItem(`ainflue_cache_${cacheKey}`, encryptedData);
    } catch (error) {
      console.error('Failed to cache response:', error);
    }
  }

  private addToOfflineQueue(requestConfig: RequestConfig): void {
    this.offlineQueue.push({
      ...requestConfig,
      timestamp: Date.now()
    } as any);

    this.saveOfflineQueue();
  }

  private async processOfflineQueue(): Promise<void> {
    const queue = [...this.offlineQueue];
    this.offlineQueue = [];

    for (const requestConfig of queue) {
      try {
        await this.request(requestConfig);
      } catch (error) {
        console.error('Failed to process offline queue item:', error);
        // Re-add to queue if it fails
        this.offlineQueue.push(requestConfig);
      }
    }

    if (this.offlineQueue.length > 0) {
      this.saveOfflineQueue();
    }
  }

  // Authentication methods
  public setAuthToken(token: string): void {
    this.authToken = token;
  }

  public clearAuthToken(): void {
    this.authToken = null;
  }

  public async login(credentials: { email: string; password: string }): Promise<APIResponse<{ token: string; user: any }>> {
    return this.request({
      method: 'POST',
      endpoint: '/auth/login',
      data: credentials,
      requiresAuth: false
    });
  }

  public async refreshToken(): Promise<APIResponse<{ token: string }>> {
    return this.request({
      method: 'POST',
      endpoint: '/auth/refresh',
      requiresAuth: true
    });
  }

  // Content management methods
  public async uploadContent(contentData: FormData): Promise<APIResponse<{ contentId: string }>> {
    return this.request({
      method: 'POST',
      endpoint: '/content/upload',
      data: contentData,
      priority: 'high'
    });
  }

  public async getContent(contentId: string): Promise<APIResponse<any>> {
    return this.request({
      method: 'GET',
      endpoint: `/content/${contentId}`,
      cacheKey: `content_${contentId}`,
      cacheTTL: 600000 // 10 minutes
    });
  }

  public async getUserProfile(userId: string): Promise<APIResponse<any>> {
    return this.request({
      method: 'GET',
      endpoint: `/users/${userId}`,
      cacheKey: `user_profile_${userId}`,
      cacheTTL: 900000 // 15 minutes
    });
  }

  public async updateUserProfile(userId: string, profileData: any): Promise<APIResponse<any>> {
    return this.request({
      method: 'PUT',
      endpoint: `/users/${userId}`,
      data: profileData
    });
  }

  // Analytics methods
  public async trackEvent(eventData: any): Promise<APIResponse<any>> {
    return this.request({
      method: 'POST',
      endpoint: '/analytics/events',
      data: eventData,
      priority: 'low',
      requiresNetwork: false
    });
  }

  // Utility methods
  public clearCache(): Promise<void> {
    return AsyncStorage.clear();
  }

  public getCacheSize(): Promise<number> {
    // Implementation would calculate cache size
    return Promise.resolve(0);
  }

  public getOfflineQueueSize(): number {
    return this.offlineQueue.length;
  }

  public isNetworkAvailable(): boolean {
    return this.isOnline;
  }
}

export default MobileAPIService;