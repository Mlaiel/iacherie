/**
 * Mobile API Service - Enhanced mobile API communication service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

export interface NetworkStatus {
  isConnected: boolean;
  connectionType: 'wifi' | 'cellular' | 'unknown' | 'none';
  isInternetReachable: boolean;
  strength?: number;
}

export interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  priority?: 'low' | 'normal' | 'high' | 'critical';
  cache?: boolean;
  offlineSupport?: boolean;
}

export interface ContentUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
  speed?: number;
  estimatedTimeRemaining?: number;
}

export interface MobileApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
  timestamp: number;
  requestId: string;
  fromCache?: boolean;
}

export interface ContentMetadata {
  contentId: string;
  type: 'audio' | 'video' | 'image' | 'document';
  size: number;
  duration?: number;
  resolution?: { width: number; height: number };
  format: string;
  quality: 'low' | 'medium' | 'high' | 'ultra';
  location?: { latitude: number; longitude: number };
  timestamp: number;
  fingerprint?: string;
}

export interface CollaborationRequest {
  requestId: string;
  fromUserId: string;
  toUserId: string;
  projectType: 'music' | 'video' | 'photography' | 'comedy' | 'blog';
  message: string;
  budget?: { min: number; max: number; currency: string };
  deadline?: number;
  skills: string[];
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
}

export interface MonetizationData {
  revenue: {
    total: number;
    monthly: number;
    daily: number;
    currency: string;
  };
  streams: {
    count: number;
    revenue: number;
  };
  licenses: {
    active: number;
    revenue: number;
  };
  collaborations: {
    completed: number;
    revenue: number;
  };
  growth: {
    percentage: number;
    trend: 'up' | 'down' | 'stable';
  };
}

export class MobileAPIService {
  private baseURL: string;
  private requestQueue: Map<string, Promise<any>>;
  private retryQueue: Array<{ request: Function; config: ApiRequestConfig; attempts: number }>;
  private networkStatus: NetworkStatus;
  private requestIdCounter: number;

  constructor() {
    this.baseURL = process.env.NODE_ENV === 'development' 
      ? 'http://10.0.2.2:8000/api'
      : 'https://api.ainflue.com';
    
    this.requestQueue = new Map();
    this.retryQueue = [];
    this.networkStatus = {
      isConnected: true,
      connectionType: 'unknown',
      isInternetReachable: true
    };
    this.requestIdCounter = 0;
    
    this.initializeNetworkMonitoring();
    this.startRetryProcessor();
  }

  private initializeNetworkMonitoring(): void {
    // Monitor network status changes
    if (typeof window !== 'undefined' && 'navigator' in window) {
      window.addEventListener('online', () => {
        this.networkStatus.isConnected = true;
        this.processRetryQueue();
      });
      
      window.addEventListener('offline', () => {
        this.networkStatus.isConnected = false;
      });
    }
  }

  private startRetryProcessor(): void {
    setInterval(() => {
      if (this.networkStatus.isConnected && this.retryQueue.length > 0) {
        this.processRetryQueue();
      }
    }, 5000);
  }

  private async processRetryQueue(): Promise<void> {
    const queue = [...this.retryQueue];
    this.retryQueue = [];

    for (const item of queue) {
      if (item.attempts < (item.config.retries || 3)) {
        try {
          await item.request();
        } catch (error) {
          item.attempts++;
          if (item.attempts < (item.config.retries || 3)) {
            this.retryQueue.push(item);
          }
        }
      }
    }
  }

  private generateRequestId(): string {
    return `mobile_req_${++this.requestIdCounter}_${Date.now()}`;
  }

  async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}, 
    config: ApiRequestConfig = {}
  ): Promise<MobileApiResponse<T>> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    try {
      // Check network connectivity
      if (!this.networkStatus.isConnected && !config.offlineSupport) {
        throw new Error('No internet connection');
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          'X-Client-Type': 'mobile',
          ...options.headers,
        },
        timeout: config.timeout || 30000,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        data,
        status: response.status,
        timestamp: Date.now(),
        requestId,
        fromCache: false,
      };

    } catch (error) {
      // Add to retry queue if retries are configured
      if (config.retries && config.retries > 0) {
        this.retryQueue.push({
          request: () => this.makeRequest(endpoint, options, { ...config, retries: 0 }),
          config,
          attempts: 0
        });
      }

      throw error;
    }
  }

  // Content Management with Mobile Optimizations
  async uploadContent(
    contentData: ContentMetadata,
    file: Blob | File,
    onProgress?: (progress: ContentUploadProgress) => void
  ): Promise<MobileApiResponse<{ contentId: string; fingerprintId: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(contentData));

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress: ContentUploadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: (event.loaded / event.total) * 100,
            speed: event.loaded / ((Date.now() - startTime) / 1000),
          };
          
          if (progress.speed) {
            progress.estimatedTimeRemaining = (event.total - event.loaded) / progress.speed;
          }
          
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });

      const startTime = Date.now();
      xhr.open('POST', `${this.baseURL}/content/upload/mobile`);
      xhr.setRequestHeader('X-Client-Type', 'mobile');
      xhr.send(formData);
    });
  }

  // AI-Powered Content Protection
  async generateContentFingerprint(
    contentId: string,
    type: 'audio' | 'video' | 'image'
  ): Promise<MobileApiResponse<{ fingerprintId: string; protectionLevel: string }>> {
    return this.makeRequest(`/protection/fingerprint/generate`, {
      method: 'POST',
      body: JSON.stringify({ contentId, type, platform: 'mobile' }),
    });
  }

  async checkContentViolations(
    contentId: string
  ): Promise<MobileApiResponse<{ violations: any[]; riskLevel: string }>> {
    return this.makeRequest(`/protection/violations/check/${contentId}`);
  }

  // Collaboration & Monetization
  async getCollaborationRecommendations(
    userProfile: { skills: string[]; interests: string[]; budget: number }
  ): Promise<MobileApiResponse<CollaborationRequest[]>> {
    return this.makeRequest('/collaboration/recommendations', {
      method: 'POST',
      body: JSON.stringify({ profile: userProfile, platform: 'mobile' }),
    });
  }

  async createCollaborationRequest(
    request: Omit<CollaborationRequest, 'requestId' | 'status'>
  ): Promise<MobileApiResponse<{ requestId: string }>> {
    return this.makeRequest('/collaboration/requests', {
      method: 'POST',
      body: JSON.stringify({ ...request, source: 'mobile' }),
    });
  }

  async getMonetizationDashboard(): Promise<MobileApiResponse<MonetizationData>> {
    return this.makeRequest('/monetization/dashboard/mobile');
  }

  async optimizeContentForSEO(
    contentId: string,
    metadata: { title: string; description: string; tags: string[] }
  ): Promise<MobileApiResponse<{ optimizedMetadata: any; seoScore: number }>> {
    return this.makeRequest('/seo/optimize', {
      method: 'POST',
      body: JSON.stringify({ contentId, metadata, platform: 'mobile' }),
    });
  }

  // Real-time Analytics
  async trackUserEngagement(
    action: string,
    data: Record<string, any>
  ): Promise<MobileApiResponse<{ tracked: boolean }>> {
    return this.makeRequest('/analytics/engagement', {
      method: 'POST',
      body: JSON.stringify({ 
        action, 
        data, 
        platform: 'mobile',
        timestamp: Date.now(),
        client: 'mobile_app'
      }),
    }, { priority: 'low', cache: false });
  }

  async getRealtimeMetrics(): Promise<MobileApiResponse<{
    activeUsers: number;
    engagement: number;
    revenue: number;
    collaborations: number;
  }>> {
    return this.makeRequest('/analytics/realtime/mobile');
  }

  // Network & Performance Monitoring
  getNetworkStatus(): NetworkStatus {
    return { ...this.networkStatus };
  }

  async testNetworkSpeed(): Promise<{ downloadSpeed: number; uploadSpeed: number; latency: number }> {
    const startTime = Date.now();
    
    try {
      const response = await fetch(`${this.baseURL}/health/speed-test`);
      const latency = Date.now() - startTime;
      const data = await response.json();
      
      return {
        downloadSpeed: data.downloadSpeed || 0,
        uploadSpeed: data.uploadSpeed || 0,
        latency,
      };
    } catch (error) {
      return { downloadSpeed: 0, uploadSpeed: 0, latency: 999999 };
    }
  }

  async optimizeForConnection(): Promise<void> {
    const speed = await this.testNetworkSpeed();
    
    if (speed.downloadSpeed < 1000000) { // Less than 1 Mbps
      // Enable low-bandwidth mode
      this.baseURL = this.baseURL.replace('/api', '/api/lite');
    }
  }

  // Caching and Offline Support
  async clearCache(): Promise<void> {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => caches.delete(name))
      );
    }
  }

  async getCacheSize(): Promise<number> {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      return estimate.usage || 0;
    }
    return 0;
  }
}

// Export singleton instance
export const mobileAPIService = new MobileAPIService();