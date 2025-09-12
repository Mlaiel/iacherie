/**
 * Node.js-specific Implementation for Ainflue JavaScript SDK
 * Optimized for server-side environments with file system and OS integration
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Expert Implementation by: Backend Senior + DevOps + Security + Audio Engineer + DBA
 */

import { AinflueClient } from './ainflue-client';
import { AinflueConfig } from './config';
import { AxiosAdapter } from './axios-adapter';
import { ApiResponse } from './interfaces';
import { SecurityError, ConfigurationError, NetworkError } from './errors';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as crypto from 'crypto';
import { performance } from 'perf_hooks';

/**
 * Node.js-optimized Ainflue SDK Client
 */
export class NodeClient extends AinflueClient {
  private fileSystemWatcher?: fs.FSWatcher;
  private processMonitor: ProcessMonitor;
  private storageManager: NodeStorageManager;
  private networkMonitor: NetworkMonitor;

  constructor(config: AinflueConfig) {
    // Use AxiosAdapter for Node.js with better HTTP/2 support
    super({
      ...config,
      adapter: new AxiosAdapter(config.baseUrl, {
        'Authorization': config.apiKey ? `Bearer ${config.apiKey}` : '',
        'Content-Type': 'application/json',
        'User-Agent': `ainflue-node-sdk/${config.version || '1.0.0'} (${os.platform()} ${os.arch()})`,
      }),
    });

    this.processMonitor = new ProcessMonitor();
    this.storageManager = new NodeStorageManager();
    this.networkMonitor = new NetworkMonitor();
    
    this.initializeNodeFeatures();
  }

  /**
   * Initialize Node.js-specific features
   * Implementation: Backend Senior + DevOps + Security
   */
  private initializeNodeFeatures(): void {
    // Process monitoring
    this.setupProcessMonitoring();

    // File system monitoring
    this.setupFileSystemMonitoring();

    // Network monitoring
    this.setupNetworkMonitoring();

    // Graceful shutdown handling
    this.setupGracefulShutdown();

    // Environment validation
    this.validateEnvironment();
  }

  /**
   * Setup process monitoring and resource tracking
   * Implementation: DevOps + Backend Senior
   */
  private setupProcessMonitoring(): void {
    this.processMonitor.start();

    // Monitor for memory leaks
    setInterval(() => {
      const memUsage = process.memoryUsage();
      if (memUsage.heapUsed > 500 * 1024 * 1024) { // 500MB threshold
        console.warn('High memory usage detected:', {
          heapUsed: `${Math.round(memUsage.heapUsed / 1024 / 1024)}MB`,
          heapTotal: `${Math.round(memUsage.heapTotal / 1024 / 1024)}MB`,
          external: `${Math.round(memUsage.external / 1024 / 1024)}MB`,
        });
      }
    }, 60000); // Check every minute
  }

  /**
   * Setup file system monitoring for cache invalidation
   * Implementation: DevOps + DBA
   */
  private setupFileSystemMonitoring(): void {
    const cacheDir = this.storageManager.getCacheDirectory();
    
    try {
      this.fileSystemWatcher = fs.watch(cacheDir, (eventType, filename) => {
        if (filename && eventType === 'change') {
          console.debug(`Cache file changed: ${filename}`);
          // Invalidate specific cache entry
          this.storageManager.invalidateCache(filename);
        }
      });
    } catch (error) {
      console.warn('File system monitoring setup failed:', error);
    }
  }

  /**
   * Setup network monitoring for connection health
   * Implementation: DevOps + Backend Senior
   */
  private setupNetworkMonitoring(): void {
    this.networkMonitor.start();
    
    this.networkMonitor.on('connectionDown', () => {
      console.warn('Network connection lost, entering offline mode');
    });

    this.networkMonitor.on('connectionRestored', () => {
      console.info('Network connection restored, resuming operations');
    });
  }

  /**
   * Setup graceful shutdown handling
   * Implementation: DevOps + Security
   */
  private setupGracefulShutdown(): void {
    const gracefulShutdown = (signal: string) => {
      console.info(`Received ${signal}, initiating graceful shutdown...`);
      
      this.destroy()
        .then(() => {
          console.info('Graceful shutdown completed');
          process.exit(0);
        })
        .catch((error) => {
          console.error('Error during shutdown:', error);
          process.exit(1);
        });
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    process.on('SIGHUP', () => gracefulShutdown('SIGHUP'));
  }

  /**
   * Validate Node.js environment and dependencies
   * Implementation: DevOps + Security
   */
  private validateEnvironment(): void {
    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.substring(1).split('.')[0]);
    
    if (majorVersion < 14) {
      console.warn(`Node.js version ${nodeVersion} is not officially supported. Please upgrade to v14 or later.`);
    }

    // Check required environment variables
    const requiredEnvVars = ['NODE_ENV'];
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
      console.warn('Missing environment variables:', missingVars);
    }

    // Validate TLS configuration
    if (process.env.NODE_TLS_REJECT_UNAUTHORIZED === '0') {
      console.error('TLS certificate validation is disabled! This is a security risk.');
    }
  }

  /**
   * Upload file from file system with progress tracking
   * Implementation: Backend Senior + Audio Engineer + Security
   */
  async uploadFileFromPath(
    filePath: string,
    endpoint: string,
    onProgress?: (progress: { loaded: number; total: number; percentage: number }) => void
  ): Promise<ApiResponse<any>> {
    // Validate file exists and is accessible
    await this.validateFileAccess(filePath);

    const stats = await fs.promises.stat(filePath);
    const fileStream = fs.createReadStream(filePath);

    // Create form data with stream
    const FormData = require('form-data');
    const formData = new FormData();
    formData.append('file', fileStream, {
      filename: path.basename(filePath),
      contentType: this.detectMimeType(filePath),
    });

    // Track upload progress
    let uploadedBytes = 0;
    fileStream.on('data', (chunk: Buffer) => {
      uploadedBytes += chunk.length;
      if (onProgress) {
        onProgress({
          loaded: uploadedBytes,
          total: stats.size,
          percentage: Math.round((uploadedBytes / stats.size) * 100),
        });
      }
    });

    return this.httpClient.post(endpoint, formData, {
      headers: formData.getHeaders(),
      timeout: 600000, // 10 minutes for large file uploads
    });
  }

  /**
   * Validate file access and security
   * Implementation: Security + Backend Senior
   */
  private async validateFileAccess(filePath: string): Promise<void> {
    try {
      // Check if file exists
      await fs.promises.access(filePath, fs.constants.F_OK);
      
      // Check if file is readable
      await fs.promises.access(filePath, fs.constants.R_OK);
      
      // Get file stats
      const stats = await fs.promises.stat(filePath);
      
      // Validate file size (max 1GB)
      if (stats.size > 1024 * 1024 * 1024) {
        throw new SecurityError('File size exceeds maximum allowed size (1GB)');
      }
      
      // Validate file is not a directory
      if (stats.isDirectory()) {
        throw new SecurityError('Cannot upload directory');
      }
      
      // Validate file path doesn't contain dangerous patterns
      const normalizedPath = path.normalize(filePath);
      if (normalizedPath.includes('..') || normalizedPath.includes('~')) {
        throw new SecurityError('Invalid file path detected');
      }
      
    } catch (error) {
      if (error instanceof SecurityError) {
        throw error;
      }
      throw new ConfigurationError(`File access validation failed: ${error.message}`);
    }
  }

  /**
   * Detect MIME type from file extension
   * Implementation: Backend Senior + Audio Engineer
   */
  private detectMimeType(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    
    const mimeTypes: Record<string, string> = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.mp4': 'video/mp4',
      '.webm': 'video/webm',
      '.mov': 'video/quicktime',
      '.mp3': 'audio/mpeg',
      '.wav': 'audio/wav',
      '.flac': 'audio/flac',
      '.ogg': 'audio/ogg',
      '.pdf': 'application/pdf',
      '.txt': 'text/plain',
      '.json': 'application/json',
      '.xml': 'application/xml',
    };
    
    return mimeTypes[ext] || 'application/octet-stream';
  }

  /**
   * Process audio file for AI analysis
   * Implementation: Audio Engineer + ML Engineer + Lead Dev IA
   */
  async processAudioFile(filePath: string, options?: {
    format?: string;
    sampleRate?: number;
    channels?: number;
  }): Promise<ApiResponse<any>> {
    // Validate audio file
    await this.validateFileAccess(filePath);
    
    const mimeType = this.detectMimeType(filePath);
    if (!mimeType.startsWith('audio/')) {
      throw new SecurityError('File is not a valid audio format');
    }

    // Read file and create form data
    const fileBuffer = await fs.promises.readFile(filePath);
    const FormData = require('form-data');
    const formData = new FormData();
    
    formData.append('audio', fileBuffer, {
      filename: path.basename(filePath),
      contentType: mimeType,
    });
    
    if (options) {
      formData.append('options', JSON.stringify(options));
    }

    return this.httpClient.post('/api/v1/audio/process', formData, {
      headers: formData.getHeaders(),
      timeout: 300000, // 5 minutes for audio processing
    });
  }

  /**
   * Bulk upload files from directory
   * Implementation: Backend Senior + DevOps + DBA
   */
  async bulkUploadDirectory(
    directoryPath: string,
    endpoint: string,
    options?: {
      recursive?: boolean;
      fileFilter?: (fileName: string) => boolean;
      concurrency?: number;
      onProgress?: (progress: { completed: number; total: number; current: string }) => void;
    }
  ): Promise<ApiResponse<any>[]> {
    const { recursive = false, fileFilter, concurrency = 3 } = options || {};
    
    // Get list of files
    const files = await this.getFilesInDirectory(directoryPath, recursive, fileFilter);
    
    if (files.length === 0) {
      return [];
    }

    // Upload files with controlled concurrency
    const results: ApiResponse<any>[] = [];
    const errors: Error[] = [];
    
    for (let i = 0; i < files.length; i += concurrency) {
      const batch = files.slice(i, i + concurrency);
      
      const batchPromises = batch.map(async (filePath) => {
        try {
          options?.onProgress?.({
            completed: results.length,
            total: files.length,
            current: path.basename(filePath),
          });
          
          return await this.uploadFileFromPath(filePath, endpoint);
        } catch (error) {
          errors.push(new Error(`Failed to upload ${filePath}: ${error.message}`));
          return null;
        }
      });
      
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults.filter(result => result !== null) as ApiResponse<any>[]);
    }
    
    if (errors.length > 0) {
      console.warn(`Bulk upload completed with ${errors.length} errors:`, errors);
    }
    
    return results;
  }

  /**
   * Get files in directory with filtering
   * Implementation: Backend Senior + DevOps
   */
  private async getFilesInDirectory(
    directoryPath: string,
    recursive: boolean,
    fileFilter?: (fileName: string) => boolean
  ): Promise<string[]> {
    const files: string[] = [];
    
    const processDirectory = async (dirPath: string) => {
      const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        
        if (entry.isFile()) {
          if (!fileFilter || fileFilter(entry.name)) {
            files.push(fullPath);
          }
        } else if (entry.isDirectory() && recursive) {
          await processDirectory(fullPath);
        }
      }
    };
    
    await processDirectory(directoryPath);
    return files;
  }

  /**
   * Get system information for analytics
   * Implementation: DevOps + Security
   */
  getSystemInfo(): any {
    return {
      platform: os.platform(),
      arch: os.arch(),
      release: os.release(),
      nodeVersion: process.version,
      memory: {
        total: os.totalmem(),
        free: os.freemem(),
        process: process.memoryUsage(),
      },
      cpu: {
        model: os.cpus()[0]?.model || 'unknown',
        cores: os.cpus().length,
        loadavg: os.loadavg(),
      },
      uptime: {
        system: os.uptime(),
        process: process.uptime(),
      },
      env: process.env.NODE_ENV || 'development',
    };
  }

  /**
   * Get stored data from file system
   * Implementation: DBA + Security + Backend Senior
   */
  async getStoredData(key: string): Promise<any> {
    return this.storageManager.get(key);
  }

  /**
   * Set data in file system storage
   * Implementation: DBA + Security + Backend Senior
   */
  async setStoredData(key: string, value: any, options?: { encrypt?: boolean; expire?: number }): Promise<void> {
    return this.storageManager.set(key, value, options);
  }

  /**
   * Clear stored data
   * Implementation: DBA + Security
   */
  async clearStoredData(key?: string): Promise<void> {
    return this.storageManager.clear(key);
  }

  /**
   * Cleanup Node.js-specific resources
   * Implementation: DevOps + Backend Senior
   */
  async destroy(): Promise<void> {
    console.info('Shutting down Node.js client...');
    
    // Stop file system watcher
    if (this.fileSystemWatcher) {
      this.fileSystemWatcher.close();
    }
    
    // Stop process monitor
    this.processMonitor.stop();
    
    // Stop network monitor
    this.networkMonitor.stop();
    
    // Clear storage
    await this.storageManager.destroy();
    
    // Call parent destroy
    await super.destroy?.();
    
    console.info('Node.js client shutdown completed');
  }
}

/**
 * Process Monitor for resource tracking
 * Implementation: DevOps + Backend Senior
 */
class ProcessMonitor {
  private monitoring = false;
  private interval?: NodeJS.Timeout;

  start(): void {
    if (this.monitoring) return;
    
    this.monitoring = true;
    this.interval = setInterval(() => {
      this.collectMetrics();
    }, 30000); // Collect every 30 seconds
  }

  stop(): void {
    this.monitoring = false;
    if (this.interval) {
      clearInterval(this.interval);
    }
  }

  private collectMetrics(): void {
    const metrics = {
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(),
      uptime: process.uptime(),
      pid: process.pid,
      timestamp: new Date().toISOString(),
    };

    // Log metrics for monitoring
    console.debug('Process metrics:', metrics);
  }
}

/**
 * Node.js Storage Manager with file system backend
 * Implementation: DBA + Security + Backend Senior
 */
class NodeStorageManager {
  private cacheDir: string;
  private encryptionKey: string;

  constructor() {
    this.cacheDir = path.join(os.tmpdir(), 'ainflue-cache');
    this.encryptionKey = this.generateEncryptionKey();
    this.ensureCacheDirectory();
  }

  private generateEncryptionKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  private ensureCacheDirectory(): void {
    if (!fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true, mode: 0o700 });
    }
  }

  getCacheDirectory(): string {
    return this.cacheDir;
  }

  async get(key: string): Promise<any> {
    const filePath = path.join(this.cacheDir, `${key}.json`);
    
    try {
      if (!fs.existsSync(filePath)) {
        return null;
      }

      const data = JSON.parse(await fs.promises.readFile(filePath, 'utf8'));
      
      // Check expiration
      if (data.expires && Date.now() > data.expires) {
        await this.remove(key);
        return null;
      }

      // Decrypt if necessary
      if (data.encrypted) {
        return this.decrypt(data.value);
      }

      return data.value;
    } catch (error) {
      console.warn(`Failed to get stored data for key ${key}:`, error);
      return null;
    }
  }

  async set(key: string, value: any, options: { encrypt?: boolean; expire?: number } = {}): Promise<void> {
    const filePath = path.join(this.cacheDir, `${key}.json`);
    
    try {
      const data: any = { value };
      
      // Set expiration
      if (options.expire) {
        data.expires = Date.now() + options.expire;
      }
      
      // Encrypt if requested
      if (options.encrypt) {
        data.value = this.encrypt(value);
        data.encrypted = true;
      }

      await fs.promises.writeFile(filePath, JSON.stringify(data), { mode: 0o600 });
    } catch (error) {
      console.warn(`Failed to set stored data for key ${key}:`, error);
    }
  }

  async remove(key: string): Promise<void> {
    const filePath = path.join(this.cacheDir, `${key}.json`);
    
    try {
      if (fs.existsSync(filePath)) {
        await fs.promises.unlink(filePath);
      }
    } catch (error) {
      console.warn(`Failed to remove stored data for key ${key}:`, error);
    }
  }

  async clear(key?: string): Promise<void> {
    if (key) {
      await this.remove(key);
      return;
    }

    try {
      const files = await fs.promises.readdir(this.cacheDir);
      await Promise.all(
        files
          .filter(file => file.endsWith('.json'))
          .map(file => fs.promises.unlink(path.join(this.cacheDir, file)))
      );
    } catch (error) {
      console.warn('Failed to clear stored data:', error);
    }
  }

  invalidateCache(filename: string): void {
    const key = path.basename(filename, '.json');
    this.remove(key).catch(console.warn);
  }

  private encrypt(data: any): string {
    const cipher = crypto.createCipher('aes-256-cbc', this.encryptionKey);
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return encrypted;
  }

  private decrypt(encryptedData: string): any {
    try {
      const decipher = crypto.createDecipher('aes-256-cbc', this.encryptionKey);
      let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      return JSON.parse(decrypted);
    } catch {
      return null;
    }
  }

  async destroy(): Promise<void> {
    await this.clear();
  }
}

/**
 * Network Monitor for connection health
 * Implementation: DevOps + Backend Senior
 */
class NetworkMonitor {
  private monitoring = false;
  private interval?: NodeJS.Timeout;
  private listeners: Map<string, Function[]> = new Map();

  start(): void {
    if (this.monitoring) return;
    
    this.monitoring = true;
    this.interval = setInterval(() => {
      this.checkConnection();
    }, 30000); // Check every 30 seconds
  }

  stop(): void {
    this.monitoring = false;
    if (this.interval) {
      clearInterval(this.interval);
    }
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  private emit(event: string, ...args: any[]): void {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(...args));
  }

  private async checkConnection(): Promise<void> {
    // Simple connection check - in production, use more sophisticated monitoring
    try {
      const { default: fetch } = await import('node-fetch');
      const response = await fetch('https://www.google.com', { 
        timeout: 5000,
        method: 'HEAD',
      });
      
      if (response.ok) {
        this.emit('connectionRestored');
      }
    } catch (error) {
      this.emit('connectionDown', error);
    }
  }
}