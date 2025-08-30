/**
 * Mobile API Service - Enterprise Mobile API Integration
 * 
 * Advanced mobile API service providing intelligent request handling,
 * offline capabilities, and seamless backend integration for mobile devices.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import {
  APIRequest,
  APIResponse,
  APIError,
  NetworkStatus,
  BaseService,
  ServiceEvent,
  ServiceEventListener,
  SecurityToken,
} from './types';

interface RequestCache {
  [key: string]: {
    response: APIResponse;
    timestamp: number;
    ttl: number;
  };
}

interface QueuedRequest extends APIRequest {
  id: string;
  timestamp: number;
  resolve: (value: APIResponse) => void;
  reject: (error: APIError) => void;
}

class MobileAPIService implements BaseService {
  private baseURL: string;
  private token: SecurityToken | null = null;
  private isOnline: boolean = true;
  private requestQueue: QueuedRequest[] = [];
  private requestCache: RequestCache = {};
  private listeners: Map<string, ServiceEventListener[]> = new Map();
  private initialized: boolean = false;
  private rateLimiter: Map<string, number> = new Map();

  constructor(baseURL?: string) {
    this.baseURL = baseURL || this.getDefaultBaseURL();
  }

  async initialize(): Promise<void> {
    try {
      // Load cached token
      await this.loadStoredToken();
      
      // Load cached requests
      await this.loadRequestCache();
      
      // Setup network monitoring
      this.setupNetworkMonitoring();
      
      // Process queued requests if online
      if (this.isOnline) {
        await this.processRequestQueue();
      }

      this.initialized = true;
      this.emit('initialized', { success: true });
    } catch (error) {
      this.emit('error', { error: error.message });
      throw error;
    }
  }

  async destroy(): Promise<void> {
    try {
      // Save pending requests
      await this.saveRequestQueue();
      
      // Save cache
      await this.saveRequestCache();
      
      // Clear listeners
      this.listeners.clear();
      
      this.initialized = false;
      this.emit('destroyed', { success: true });
    } catch (error) {
      this.emit('error', { error: error.message });
    }
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  addEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, []);
    }
    this.listeners.get(type)!.push(listener as ServiceEventListener);
  }

  removeEventListener<T>(type: string, listener: ServiceEventListener<T>): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const index = listeners.indexOf(listener as ServiceEventListener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit<T>(type: string, data: T): void {
    const listeners = this.listeners.get(type);
    if (listeners) {
      const event: ServiceEvent<T> = {
        type,
        data,
        timestamp: new Date(),
        source: 'MobileAPIService',
      };
      listeners.forEach(listener => listener(event));
    }
  }

  // Authentication Methods
  async setToken(token: SecurityToken): Promise<void> {
    this.token = token;
    await AsyncStorage.setItem('api_token', JSON.stringify(token));
    this.emit('tokenUpdated', { token });
  }

  async clearToken(): Promise<void> {
    this.token = null;
    await AsyncStorage.removeItem('api_token');
    this.emit('tokenCleared', {});
  }

  getToken(): SecurityToken | null {
    return this.token;
  }

  // Request Methods
  async request<T = any>(request: APIRequest): Promise<APIResponse<T>> {
    try {
      // Check rate limiting
      if (this.isRateLimited(request.endpoint)) {
        throw new Error('Rate limit exceeded');
      }

      // Check cache first
      const cached = this.getCachedResponse(request);
      if (cached) {
        this.emit('cacheHit', { request, response: cached });
        return cached as APIResponse<T>;
      }

      // If offline, queue request
      if (!this.isOnline) {
        return this.queueRequest<T>(request);
      }

      // Make request
      const response = await this.makeRequest<T>(request);
      
      // Cache successful responses
      if (response.status < 400) {
        this.cacheResponse(request, response);
      }

      this.emit('requestCompleted', { request, response });
      return response;

    } catch (error) {
      const apiError: APIError = {
        message: error.message,
        status: error.status,
        code: error.code,
        details: error.response?.data,
        timestamp: new Date(),
      };

      this.emit('requestFailed', { request, error: apiError });
      throw apiError;
    }
  }

  async get<T = any>(endpoint: string, options?: Partial<APIRequest>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'GET',
      endpoint,
      ...options,
    });
  }

  async post<T = any>(endpoint: string, data?: any, options?: Partial<APIRequest>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'POST',
      endpoint,
      data,
      ...options,
    });
  }

  async put<T = any>(endpoint: string, data?: any, options?: Partial<APIRequest>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'PUT',
      endpoint,
      data,
      ...options,
    });
  }

  async delete<T = any>(endpoint: string, options?: Partial<APIRequest>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'DELETE',
      endpoint,
      ...options,
    });
  }

  // Business Logic Methods
  async uploadContent(formData: FormData, onProgress?: (progress: number) => void): Promise<APIResponse> {
    const request: APIRequest = {
      method: 'POST',
      endpoint: '/content/upload',
      data: formData,
      timeout: 300000, // 5 minutes
    };

    // Mock progress for demonstration
    if (onProgress) {
      const progressInterval = setInterval(() => {
        const progress = Math.min(100, Math.random() * 100);
        onProgress(progress);
        if (progress === 100) {
          clearInterval(progressInterval);
        }
      }, 1000);
    }

    return this.request(request);
  }

  async getDashboardData(): Promise<APIResponse> {
    return this.get('/dashboard/metrics');
  }

  async getContentLibrary(page: number = 1, limit: number = 20): Promise<APIResponse> {
    return this.get(`/content/library?page=${page}&limit=${limit}`);
  }

  async getAnalytics(timeframe: string = '30d'): Promise<APIResponse> {
    return this.get(`/analytics/overview?timeframe=${timeframe}`);
  }

  async getProtectionStatus(): Promise<APIResponse> {
    return this.get('/protection/status');
  }

  async reportViolation(violationData: any): Promise<APIResponse> {
    return this.post('/protection/violations', violationData);
  }

  async getCollaborations(): Promise<APIResponse> {
    return this.get('/collaborations');
  }

  async createCollaboration(data: any): Promise<APIResponse> {
    return this.post('/collaborations', data);
  }

  async getNotifications(page: number = 1): Promise<APIResponse> {
    return this.get(`/notifications?page=${page}`);
  }

  async markNotificationRead(notificationId: string): Promise<APIResponse> {
    return this.put(`/notifications/${notificationId}/read`);
  }

  // Private Methods
  private getDefaultBaseURL(): string {
    return __DEV__ 
      ? 'http://10.0.2.2:8000/api/v1'  // Android emulator localhost
      : 'https://api.ainflue.com/v1';
  }

  private async loadStoredToken(): Promise<void> {
    try {
      const tokenStr = await AsyncStorage.getItem('api_token');
      if (tokenStr) {
        this.token = JSON.parse(tokenStr);
        
        // Check if token is expired
        if (this.token?.expiresAt && new Date() > new Date(this.token.expiresAt)) {
          await this.clearToken();
        }
      }
    } catch (error) {
      console.warn('Failed to load stored token:', error);
    }
  }

  private async loadRequestCache(): Promise<void> {
    try {
      const cacheStr = await AsyncStorage.getItem('api_cache');
      if (cacheStr) {
        this.requestCache = JSON.parse(cacheStr);
        
        // Clean expired cache entries
        const now = Date.now();
        Object.keys(this.requestCache).forEach(key => {
          const entry = this.requestCache[key];
          if (now - entry.timestamp > entry.ttl) {
            delete this.requestCache[key];
          }
        });
      }
    } catch (error) {
      console.warn('Failed to load request cache:', error);
    }
  }

  private async saveRequestCache(): Promise<void> {
    try {
      await AsyncStorage.setItem('api_cache', JSON.stringify(this.requestCache));
    } catch (error) {
      console.warn('Failed to save request cache:', error);
    }
  }

  private async saveRequestQueue(): Promise<void> {
    try {
      const queueData = this.requestQueue.map(req => ({
        ...req,
        resolve: undefined,
        reject: undefined,
      }));
      await AsyncStorage.setItem('api_queue', JSON.stringify(queueData));
    } catch (error) {
      console.warn('Failed to save request queue:', error);
    }
  }

  private setupNetworkMonitoring(): void {
    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected || false;
      
      const networkStatus: NetworkStatus = {
        isConnected: this.isOnline,
        connectionType: state.type as any,
        isInternetReachable: state.isInternetReachable || false,
      };

      this.emit('networkStatusChanged', networkStatus);

      // Process queue when coming back online
      if (!wasOnline && this.isOnline) {
        this.processRequestQueue();
      }
    });
  }

  private getCachedResponse(request: APIRequest): APIResponse | null {
    if (request.method !== 'GET') return null;
    
    const cacheKey = this.getCacheKey(request);
    const cached = this.requestCache[cacheKey];
    
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.response;
    }
    
    return null;
  }

  private cacheResponse(request: APIRequest, response: APIResponse): void {
    if (request.method !== 'GET') return;
    
    const cacheKey = this.getCacheKey(request);
    this.requestCache[cacheKey] = {
      response,
      timestamp: Date.now(),
      ttl: 5 * 60 * 1000, // 5 minutes
    };
  }

  private getCacheKey(request: APIRequest): string {
    return `${request.method}:${request.endpoint}:${JSON.stringify(request.data || {})}`;
  }

  private isRateLimited(endpoint: string): boolean {
    const now = Date.now();
    const lastRequest = this.rateLimiter.get(endpoint) || 0;
    
    if (now - lastRequest < 1000) { // 1 second rate limit
      return true;
    }
    
    this.rateLimiter.set(endpoint, now);
    return false;
  }

  private async queueRequest<T>(request: APIRequest): Promise<APIResponse<T>> {
    return new Promise((resolve, reject) => {
      const queuedRequest: QueuedRequest = {
        ...request,
        id: Date.now().toString(),
        timestamp: Date.now(),
        resolve: resolve as any,
        reject,
      };
      
      this.requestQueue.push(queuedRequest);
      this.emit('requestQueued', { request: queuedRequest });
    });
  }

  private async processRequestQueue(): Promise<void> {
    if (!this.isOnline || this.requestQueue.length === 0) return;

    this.emit('queueProcessingStarted', { count: this.requestQueue.length });

    const queue = [...this.requestQueue];
    this.requestQueue = [];

    for (const queuedRequest of queue) {
      try {
        const response = await this.makeRequest(queuedRequest);
        queuedRequest.resolve(response);
        this.emit('queuedRequestCompleted', { request: queuedRequest, response });
      } catch (error) {
        const apiError: APIError = {
          message: error.message,
          status: error.status,
          timestamp: new Date(),
        };
        queuedRequest.reject(apiError);
        this.emit('queuedRequestFailed', { request: queuedRequest, error: apiError });
      }
    }

    this.emit('queueProcessingCompleted', {});
  }

  private async makeRequest<T>(request: APIRequest): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${request.endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...request.headers,
    };

    if (this.token) {
      headers.Authorization = `${this.token.type} ${this.token.value}`;
    }

    const config: RequestInit = {
      method: request.method,
      headers,
    };

    if (request.data) {
      if (request.data instanceof FormData) {
        delete headers['Content-Type']; // Let browser set boundary
        config.body = request.data;
      } else {
        config.body = JSON.stringify(request.data);
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), request.timeout || 30000);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseData = await response.json();
      
      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        timestamp: new Date(),
      };
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }
}

export default new MobileAPIService();