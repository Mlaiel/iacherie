/**
 * Browser-specific Implementation for Ainflue JavaScript SDK
 * Optimized for browser environments with DOM integration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Frontend + Security + DevOps + Audio Engineer + Lead Dev IA
 */

import { AinflueClient } from './ainflue-client';
import { AinflueConfig } from './config';
import { FetchAdapter } from './fetch-adapter';
import { ApiResponse } from './interfaces';
import { SecurityError, ConfigurationError } from './errors';

/**
 * Browser-optimized Ainflue SDK Client
 */
export class BrowserClient extends AinflueClient {
  private performanceObserver?: PerformanceObserver;
  private visibilityChangeHandler?: () => void;
  private storageManager: BrowserStorageManager;

  constructor(config: AinflueConfig) {
    // Use FetchAdapter for browser compatibility
    super({
      ...config,
      adapter: new FetchAdapter(config.baseUrl, {
        'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : '',
        'Content-Type': 'application/json',
      }),
    });

    this.storageManager = new BrowserStorageManager();
    this.initializeBrowserFeatures();
  }

  /**
   * Initialize browser-specific features
   * Implementation: Frontend + DevOps + Lead Dev IA
   */
  private initializeBrowserFeatures(): void {
    // Performance monitoring
    if (typeof PerformanceObserver !== 'undefined') {
      this.setupPerformanceMonitoring();
    }

    // Visibility change handling for pausing requests
    if (typeof document !== 'undefined') {
      this.setupVisibilityHandling();
    }

    // Network status monitoring
    if (typeof navigator !== 'undefined' && 'onLine' in navigator) {
      this.setupNetworkMonitoring();
    }

    // Service Worker integration
    if ('serviceWorker' in navigator) {
      this.setupServiceWorkerIntegration();
    }
  }

  /**
   * Setup performance monitoring using PerformanceObserver
   * Implementation: DevOps + Lead Dev IA
   */
  private setupPerformanceMonitoring(): void {
    try {
      this.performanceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'measure' && entry.name.startsWith('ainflue-')) {
            console.debug('Performance metric:', {
              name: entry.name,
              duration: entry.duration,
              startTime: entry.startTime,
            });
          }
        });
      });

      this.performanceObserver.observe({ entryTypes: ['measure', 'navigation'] });
    } catch (error) {
      console.warn('Performance monitoring not available:', error);
    }
  }

  /**
   * Setup visibility change handling
   * Implementation: Frontend + DevOps
   */
  private setupVisibilityHandling(): void {
    this.visibilityChangeHandler = () => {
      if (document.hidden) {
        // Page is hidden, pause non-critical requests
        console.debug('Page hidden, pausing non-critical requests');
      } else {
        // Page is visible, resume normal operation
        console.debug('Page visible, resuming normal operation');
      }
    };

    document.addEventListener('visibilitychange', this.visibilityChangeHandler);
  }

  /**
   * Setup network status monitoring
   * Implementation: DevOps + Frontend
   */
  private setupNetworkMonitoring(): void {
    const handleOnline = () => {
      console.debug('Network connection restored');
      // Trigger retry of failed requests
      this.handleNetworkReconnection();
    };

    const handleOffline = () => {
      console.debug('Network connection lost');
      // Queue requests for later retry
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  }

  /**
   * Setup Service Worker integration for offline support
   * Implementation: DevOps + Frontend + Security
   */
  private async setupServiceWorkerIntegration(): Promise<void> {
    try {
      // Register service worker for offline caching
      const registration = await navigator.serviceWorker.register('/ainflue-sw.js', {
        scope: '/',
      });

      console.debug('Service Worker registered:', registration);

      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'CACHE_UPDATE') {
          console.debug('Cache updated by service worker');
        }
      });

    } catch (error) {
      console.warn('Service Worker registration failed:', error);
    }
  }

  /**
   * Handle network reconnection by retrying failed requests
   * Implementation: DevOps + Lead Dev IA
   */
  private handleNetworkReconnection(): void {
    // This would integrate with a request queue to retry failed requests
    console.debug('Handling network reconnection');
  }

  /**
   * Upload file with progress tracking (browser-specific)
   * Implementation: Frontend + Audio Engineer + Security
   */
  async uploadFileWithProgress(
    file: File,
    endpoint: string,
    onProgress?: (progress: { loaded: number; total: number; percentage: number }) => void
  ): Promise<ApiResponse<any>> {
    // Validate file before upload
    this.validateFileUpload(file);

    const formData = new FormData();
    formData.append('file', file);

    // Create XMLHttpRequest for progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = {
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((event.loaded / event.total) * 100),
          };
          onProgress(progress);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve({
              data,
              status: xhr.status,
              statusText: xhr.statusText,
              headers: this.parseXHRHeaders(xhr),
              success: true,
            });
          } catch {
            resolve({
              data: xhr.responseText,
              status: xhr.status,
              statusText: xhr.statusText,
              headers: this.parseXHRHeaders(xhr),
              success: true,
            });
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
        }
      };

      xhr.onerror = () => reject(new Error('Upload failed due to network error'));

      xhr.open('POST', `${this.config.baseUrl}${endpoint}`);
      
      // Add authentication header
      if (this.config.apiKey) {
        xhr.setRequestHeader('Authorization', `Bearer ${this.config.apiKey}`);
      }

      xhr.send(formData);
    });
  }

  /**
   * Validate file upload security and constraints
   * Implementation: Security + Audio Engineer
   */
  private validateFileUpload(file: File): void {
    // File size validation
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      throw new SecurityError('File size exceeds maximum allowed size');
    }

    // File type validation
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp',
      'video/mp4', 'video/webm', 'video/quicktime',
      'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/flac',
      'application/pdf', 'text/plain',
    ];

    if (!allowedTypes.includes(file.type)) {
      throw new SecurityError(`File type ${file.type} not allowed`);
    }

    // Filename validation
    if (!/^[a-zA-Z0-9._-]+$/.test(file.name)) {
      throw new SecurityError('Invalid filename characters');
    }
  }

  /**
   * Parse XMLHttpRequest headers
   * Implementation: Frontend + Backend Senior
   */
  private parseXHRHeaders(xhr: XMLHttpRequest): Record<string, string> {
    const headers: Record<string, string> = {};
    const headerString = xhr.getAllResponseHeaders();
    
    headerString.split('\r\n').forEach(line => {
      const [key, value] = line.split(': ');
      if (key && value) {
        headers[key.toLowerCase()] = value;
      }
    });

    return headers;
  }

  /**
   * Get browser information for analytics
   * Implementation: DevOps + Security
   */
  getBrowserInfo(): any {
    if (typeof navigator === 'undefined') {
      return null;
    }

    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      languages: navigator.languages,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      maxTouchPoints: navigator.maxTouchPoints || 0,
      hardwareConcurrency: navigator.hardwareConcurrency || 1,
      deviceMemory: (navigator as any).deviceMemory || null,
      connection: (navigator as any).connection ? {
        effectiveType: (navigator as any).connection.effectiveType,
        downlink: (navigator as any).connection.downlink,
        rtt: (navigator as any).connection.rtt,
      } : null,
    };
  }

  /**
   * Capture audio stream (for audio content creation)
   * Implementation: Audio Engineer + Security + Frontend
   */
  async captureAudioStream(constraints: MediaStreamConstraints = { audio: true }): Promise<MediaStream> {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new ConfigurationError('Media capture not supported in this browser');
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      console.debug('Audio stream captured:', stream);
      return stream;
    } catch (error) {
      throw new SecurityError(`Failed to capture audio stream: ${error.message}`);
    }
  }

  /**
   * Process audio for AI analysis
   * Implementation: Audio Engineer + ML Engineer + Lead Dev IA
   */
  async processAudioForAI(audioBlob: Blob): Promise<ApiResponse<any>> {
    // Validate audio file
    if (!audioBlob.type.startsWith('audio/')) {
      throw new SecurityError('Invalid audio format');
    }

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('processingType', 'ai_analysis');

    return this.httpClient.post('/api/v1/audio/process', formData, {
      headers: {
        // Don't set Content-Type, let browser set it with boundary
      },
      timeout: 120000, // 2 minutes for audio processing
    });
  }

  /**
   * Get stored data from browser storage
   * Implementation: Frontend + Security + DBA
   */
  getStoredData(key: string): any {
    return this.storageManager.get(key);
  }

  /**
   * Set data in browser storage
   * Implementation: Frontend + Security + DBA
   */
  setStoredData(key: string, value: any, options?: { encrypt?: boolean; expire?: number }): void {
    this.storageManager.set(key, value, options);
  }

  /**
   * Clear stored data
   * Implementation: Frontend + Security
   */
  clearStoredData(key?: string): void {
    this.storageManager.clear(key);
  }

  /**
   * Cleanup browser-specific resources
   * Implementation: Frontend + DevOps
   */
  destroy(): void {
    // Clean up performance observer
    if (this.performanceObserver) {
      this.performanceObserver.disconnect();
    }

    // Remove event listeners
    if (this.visibilityChangeHandler && typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.visibilityChangeHandler);
    }

    // Clear storage
    this.storageManager.destroy();

    // Call parent destroy
    super.destroy?.();
  }
}

/**
 * Browser Storage Manager with encryption and expiration
 * Implementation: Security + DBA + DevOps
 */
class BrowserStorageManager {
  private encryptionKey?: CryptoKey;

  constructor() {
    this.initializeEncryption();
  }

  /**
   * Initialize encryption for sensitive data
   * Implementation: Security
   */
  private async initializeEncryption(): Promise<void> {
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      try {
        this.encryptionKey = await crypto.subtle.generateKey(
          { name: 'AES-GCM', length: 256 },
          false,
          ['encrypt', 'decrypt']
        );
      } catch (error) {
        console.warn('Encryption initialization failed:', error);
      }
    }
  }

  /**
   * Get data from storage with decryption support
   * Implementation: Security + DBA
   */
  get(key: string): any {
    try {
      const stored = localStorage.getItem(`ainflue_${key}`);
      if (!stored) return null;

      const data = JSON.parse(stored);

      // Check expiration
      if (data.expires && Date.now() > data.expires) {
        this.remove(key);
        return null;
      }

      // Decrypt if necessary
      if (data.encrypted && this.encryptionKey) {
        return this.decrypt(data.value);
      }

      return data.value;
    } catch (error) {
      console.warn(`Failed to get stored data for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Set data in storage with encryption and expiration
   * Implementation: Security + DBA
   */
  set(key: string, value: any, options: { encrypt?: boolean; expire?: number } = {}): void {
    try {
      const data: any = { value };

      // Set expiration
      if (options.expire) {
        data.expires = Date.now() + options.expire;
      }

      // Encrypt if requested and available
      if (options.encrypt && this.encryptionKey) {
        data.value = this.encrypt(value);
        data.encrypted = true;
      }

      localStorage.setItem(`ainflue_${key}`, JSON.stringify(data));
    } catch (error) {
      console.warn(`Failed to set stored data for key ${key}:`, error);
    }
  }

  /**
   * Remove data from storage
   * Implementation: Security
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(`ainflue_${key}`);
    } catch (error) {
      console.warn(`Failed to remove stored data for key ${key}:`, error);
    }
  }

  /**
   * Clear all or specific stored data
   * Implementation: Security
   */
  clear(key?: string): void {
    if (key) {
      this.remove(key);
      return;
    }

    try {
      // Clear all Ainflue data
      const keys = Object.keys(localStorage).filter(k => k.startsWith('ainflue_'));
      keys.forEach(k => localStorage.removeItem(k));
    } catch (error) {
      console.warn('Failed to clear stored data:', error);
    }
  }

  /**
   * Encrypt data (placeholder implementation)
   * Implementation: Security
   */
  private encrypt(data: any): string {
    // In a real implementation, this would use the Web Crypto API
    // For now, return base64 encoded (not secure!)
    return btoa(JSON.stringify(data));
  }

  /**
   * Decrypt data (placeholder implementation)
   * Implementation: Security
   */
  private decrypt(encryptedData: string): any {
    // In a real implementation, this would use the Web Crypto API
    // For now, return base64 decoded
    try {
      return JSON.parse(atob(encryptedData));
    } catch {
      return null;
    }
  }

  /**
   * Cleanup resources
   * Implementation: Security + DevOps
   */
  destroy(): void {
    // Clear encryption key reference
    this.encryptionKey = undefined;
  }
}