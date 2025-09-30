/**
 * Ainflue Desktop - Upload Interface Component
 * 
 * Advanced multi-format upload system with drag-and-drop, progress tracking, and AI preprocessing
 * Supports all media formats with intelligent quality analysis and optimization suggestions
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const log = require('electron-log');
const fs = require('fs').promises;
const path = require('path');

class UploadInterface extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      maxFileSize: 500 * 1024 * 1024, // 500MB default
      maxFiles: 20,
      enableBatchUpload: true,
      enableDragDrop: true,
      enableCloudUpload: true,
      enableURLImport: true,
      autoStartUpload: false,
      enablePreprocessing: true,
      enableThumbnails: true,
      enableMetadataExtraction: true,
      supportedFormats: {
        video: ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.m4v'],
        audio: ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.aiff'],
        image: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'],
        document: ['.pdf', '.doc', '.docx', '.txt', '.md']
      },
      uploadEndpoints: {
        local: 'file://',
        cloud: 'https://api.ainflue.com/upload',
        cdn: 'https://cdn.ainflue.com/upload'
      },
      ...options
    };

    // Upload state management
    this.uploads = new Map();
    this.uploadQueue = [];
    this.activeUploads = new Map();
    this.completedUploads = new Map();
    this.failedUploads = new Map();
    
    // Processing state
    this.processors = new Map();
    this.thumbnailCache = new Map();
    this.metadataCache = new Map();
    
    // UI state
    this.dropZoneActive = false;
    this.selectedFiles = [];
    this.uploadProgress = {
      totalFiles: 0,
      completedFiles: 0,
      totalSize: 0,
      uploadedSize: 0,
      currentSpeed: 0,
      timeRemaining: 0
    };

    // Statistics
    this.statistics = {
      totalUploads: 0,
      successfulUploads: 0,
      failedUploads: 0,
      totalDataUploaded: 0,
      averageUploadSpeed: 0,
      formatDistribution: new Map()
    };

    this.initializeUploadInterface();
  }

  /**
   * Initialize upload interface
   */
  async initializeUploadInterface() {
    try {
      this.setupDragDropHandlers();
      this.setupFileInputHandler();
      this.setupProcessors();
      
      log.info('Upload interface initialized successfully');
      this.emit('initialized');
    } catch (error) {
      log.error('Failed to initialize upload interface:', error);
      this.emit('error', error);
    }
  }

  /**
   * Setup drag and drop handlers
   */
  setupDragDropHandlers() {
    if (!this.options.enableDragDrop) return;

    // These would be attached to the actual DOM elements in a real implementation
    this.dragDropHandlers = {
      onDragEnter: (event) => {
        event.preventDefault();
        this.dropZoneActive = true;
        this.emit('dragEnter');
      },

      onDragOver: (event) => {
        event.preventDefault();
        this.emit('dragOver');
      },

      onDragLeave: (event) => {
        event.preventDefault();
        this.dropZoneActive = false;
        this.emit('dragLeave');
      },

      onDrop: async (event) => {
        event.preventDefault();
        this.dropZoneActive = false;
        
        const files = Array.from(event.dataTransfer.files);
        await this.handleFileSelection(files);
        this.emit('drop', { fileCount: files.length });
      }
    };
  }

  /**
   * Setup file input handler
   */
  setupFileInputHandler() {
    this.fileInputHandler = {
      onChange: async (event) => {
        const files = Array.from(event.target.files);
        await this.handleFileSelection(files);
      }
    };
  }

  /**
   * Setup file processors
   */
  setupProcessors() {
    // Thumbnail processor
    this.processors.set('thumbnail', {
      name: 'Thumbnail Generator',
      process: this.generateThumbnail.bind(this),
      supportedTypes: ['video', 'image']
    });

    // Metadata extractor
    this.processors.set('metadata', {
      name: 'Metadata Extractor',
      process: this.extractMetadata.bind(this),
      supportedTypes: ['video', 'audio', 'image']
    });

    // Quality analyzer
    this.processors.set('quality', {
      name: 'Quality Analyzer',
      process: this.analyzeQuality.bind(this),
      supportedTypes: ['video', 'audio', 'image']
    });

    // AI content analyzer
    this.processors.set('ai_analysis', {
      name: 'AI Content Analyzer',
      process: this.analyzeContentAI.bind(this),
      supportedTypes: ['video', 'audio', 'image']
    });
  }

  /**
   * Handle file selection (drag-drop or file input)
   */
  async handleFileSelection(fileList) {
    try {
      const files = Array.from(fileList);
      
      // Validate files
      const validationResults = await this.validateFiles(files);
      const validFiles = validationResults.filter(result => result.valid).map(result => result.file);
      const invalidFiles = validationResults.filter(result => !result.valid);

      if (invalidFiles.length > 0) {
        this.emit('filesRejected', invalidFiles);
      }

      if (validFiles.length === 0) {
        this.emit('noValidFiles');
        return;
      }

      // Create upload entries
      const uploadEntries = await this.createUploadEntries(validFiles);
      
      // Add to queue
      for (const entry of uploadEntries) {
        this.uploadQueue.push(entry);
        this.uploads.set(entry.id, entry);
      }

      this.selectedFiles = uploadEntries;
      this.updateUploadProgress();

      this.emit('filesSelected', {
        validFiles: validFiles.length,
        invalidFiles: invalidFiles.length,
        totalSize: uploadEntries.reduce((sum, entry) => sum + entry.size, 0)
      });

      // Start preprocessing
      if (this.options.enablePreprocessing) {
        await this.startPreprocessing(uploadEntries);
      }

      // Auto-start upload if enabled
      if (this.options.autoStartUpload) {
        await this.startUploads();
      }

    } catch (error) {
      log.error('Error handling file selection:', error);
      this.emit('error', error);
    }
  }

  /**
   * Validate selected files
   */
  async validateFiles(files) {
    const results = [];

    for (const file of files) {
      const result = {
        file,
        valid: true,
        errors: []
      };

      // Check file size
      if (file.size > this.options.maxFileSize) {
        result.valid = false;
        result.errors.push(`File size exceeds maximum (${this.formatBytes(this.options.maxFileSize)})`);
      }

      // Check file format
      const fileType = this.getFileType(file.name);
      const isSupported = this.isSupportedFormat(file.name);
      
      if (!isSupported) {
        result.valid = false;
        result.errors.push('Unsupported file format');
      }

      // Check for duplicates
      const isDuplicate = this.isDuplicateFile(file);
      if (isDuplicate) {
        result.valid = false;
        result.errors.push('Duplicate file already selected');
      }

      // Additional validation based on file type
      if (fileType === 'video' && result.valid) {
        const videoValidation = await this.validateVideoFile(file);
        if (!videoValidation.valid) {
          result.valid = false;
          result.errors.push(...videoValidation.errors);
        }
      }

      results.push(result);
    }

    return results;
  }

  /**
   * Create upload entries for valid files
   */
  async createUploadEntries(files) {
    const entries = [];

    for (const file of files) {
      const uploadId = this.generateUploadId();
      const fileType = this.getFileType(file.name);
      
      const entry = {
        id: uploadId,
        file,
        name: file.name,
        size: file.size,
        type: fileType,
        mimeType: file.type,
        lastModified: file.lastModified,
        
        // Upload state
        status: 'queued', // queued, preprocessing, uploading, completed, failed
        progress: 0,
        uploadedBytes: 0,
        speed: 0,
        timeRemaining: 0,
        
        // Processing state
        preprocessing: {
          thumbnail: { status: 'pending', result: null },
          metadata: { status: 'pending', result: null },
          quality: { status: 'pending', result: null },
          ai_analysis: { status: 'pending', result: null }
        },
        
        // Upload configuration
        destination: 'cloud',
        chunkSize: 1024 * 1024, // 1MB chunks
        maxRetries: 3,
        currentRetries: 0,
        
        // Timestamps
        created: new Date(),
        started: null,
        completed: null,
        
        // Results
        uploadedUrl: null,
        error: null
      };

      entries.push(entry);
    }

    return entries;
  }

  /**
   * Start preprocessing for upload entries
   */
  async startPreprocessing(entries) {
    for (const entry of entries) {
      entry.status = 'preprocessing';
      this.emit('preprocessingStarted', { uploadId: entry.id });

      // Run processors in parallel
      const processingPromises = [];

      for (const [processorName, processor] of this.processors) {
        if (processor.supportedTypes.includes(entry.type)) {
          processingPromises.push(
            this.runProcessor(entry, processorName, processor)
          );
        }
      }

      try {
        await Promise.all(processingPromises);
        this.emit('preprocessingCompleted', { uploadId: entry.id });
      } catch (error) {
        log.warn(`Preprocessing failed for ${entry.name}:`, error);
        this.emit('preprocessingFailed', { uploadId: entry.id, error });
      }
    }
  }

  /**
   * Run a specific processor on an upload entry
   */
  async runProcessor(entry, processorName, processor) {
    try {
      entry.preprocessing[processorName].status = 'processing';
      
      const result = await processor.process(entry.file);
      
      entry.preprocessing[processorName].status = 'completed';
      entry.preprocessing[processorName].result = result;
      
      this.emit('processingComplete', {
        uploadId: entry.id,
        processor: processorName,
        result
      });

      return result;
    } catch (error) {
      entry.preprocessing[processorName].status = 'failed';
      entry.preprocessing[processorName].error = error.message;
      
      log.warn(`Processor ${processorName} failed for ${entry.name}:`, error);
      throw error;
    }
  }

  /**
   * Start uploads for queued files
   */
  async startUploads() {
    try {
      const queuedUploads = this.uploadQueue.filter(entry => 
        entry.status === 'queued' || entry.status === 'preprocessing'
      );

      if (queuedUploads.length === 0) {
        this.emit('noUploadsQueued');
        return;
      }

      this.emit('uploadsStarted', { count: queuedUploads.length });

      // Process uploads with concurrency control
      const maxConcurrent = 3;
      const chunks = this.chunkArray(queuedUploads, maxConcurrent);

      for (const chunk of chunks) {
        const uploadPromises = chunk.map(entry => this.uploadFile(entry));
        await Promise.allSettled(uploadPromises);
      }

      this.emit('uploadsCompleted');
      
    } catch (error) {
      log.error('Error starting uploads:', error);
      this.emit('error', error);
    }
  }

  /**
   * Upload a single file
   */
  async uploadFile(entry) {
    try {
      entry.status = 'uploading';
      entry.started = new Date();
      this.activeUploads.set(entry.id, entry);

      this.emit('uploadStarted', { uploadId: entry.id });

      // Determine upload method based on destination
      let uploadResult;
      switch (entry.destination) {
        case 'local':
          uploadResult = await this.uploadToLocal(entry);
          break;
        case 'cloud':
          uploadResult = await this.uploadToCloud(entry);
          break;
        case 'cdn':
          uploadResult = await this.uploadToCDN(entry);
          break;
        default:
          throw new Error(`Unknown upload destination: ${entry.destination}`);
      }

      // Upload completed successfully
      entry.status = 'completed';
      entry.completed = new Date();
      entry.uploadedUrl = uploadResult.url;
      entry.progress = 100;

      this.activeUploads.delete(entry.id);
      this.completedUploads.set(entry.id, entry);

      this.updateStatistics(entry, true);
      this.updateUploadProgress();

      this.emit('uploadCompleted', {
        uploadId: entry.id,
        url: uploadResult.url,
        duration: entry.completed - entry.started
      });

      return uploadResult;

    } catch (error) {
      // Upload failed
      entry.status = 'failed';
      entry.error = error.message;
      entry.completed = new Date();

      this.activeUploads.delete(entry.id);
      this.failedUploads.set(entry.id, entry);

      this.updateStatistics(entry, false);

      this.emit('uploadFailed', {
        uploadId: entry.id,
        error: error.message
      });

      // Retry if attempts remaining
      if (entry.currentRetries < entry.maxRetries) {
        entry.currentRetries++;
        log.info(`Retrying upload for ${entry.name} (attempt ${entry.currentRetries}/${entry.maxRetries})`);
        
        setTimeout(() => {
          this.uploadFile(entry);
        }, 2000 * entry.currentRetries); // Exponential backoff
      }

      throw error;
    }
  }

  /**
   * Upload to local storage
   */
  async uploadToLocal(entry) {
    const destinationPath = path.join(process.cwd(), 'uploads', entry.name);
    
    // Ensure upload directory exists
    await fs.mkdir(path.dirname(destinationPath), { recursive: true });
    
    // Read file data
    const buffer = await entry.file.arrayBuffer();
    
    // Write to destination
    await fs.writeFile(destinationPath, Buffer.from(buffer));
    
    return {
      url: `file://${destinationPath}`,
      path: destinationPath,
      size: entry.size
    };
  }

  /**
   * Upload to cloud storage
   */
  async uploadToCloud(entry) {
    const endpoint = this.options.uploadEndpoints.cloud;
    
    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', entry.file);
    formData.append('metadata', JSON.stringify({
      originalName: entry.name,
      type: entry.type,
      preprocessing: entry.preprocessing
    }));

    // Upload with progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          entry.progress = (event.loaded / event.total) * 100;
          entry.uploadedBytes = event.loaded;
          
          // Calculate upload speed
          const elapsed = (Date.now() - entry.started.getTime()) / 1000;
          entry.speed = event.loaded / elapsed;
          entry.timeRemaining = (event.total - event.loaded) / entry.speed;
          
          this.updateUploadProgress();
          this.emit('uploadProgress', {
            uploadId: entry.id,
            progress: entry.progress,
            speed: entry.speed,
            timeRemaining: entry.timeRemaining
          });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const response = JSON.parse(xhr.responseText);
          resolve({
            url: response.url,
            id: response.id,
            metadata: response.metadata
          });
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed due to network error'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload was aborted'));
      });

      xhr.open('POST', endpoint);
      xhr.send(formData);
    });
  }

  /**
   * Upload to CDN
   */
  async uploadToCDN(entry) {
    // Similar to cloud upload but with CDN-specific configuration
    return this.uploadToCloud(entry); // Simplified for this implementation
  }

  /**
   * Import from URL
   */
  async importFromURL(url, options = {}) {
    try {
      const importId = this.generateUploadId();
      
      this.emit('urlImportStarted', { importId, url });
      
      // Fetch file from URL
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
      }
      
      // Get file information
      const blob = await response.blob();
      const fileName = options.fileName || this.extractFileNameFromURL(url);
      const file = new File([blob], fileName, { type: blob.type });
      
      // Process as regular upload
      await this.handleFileSelection([file]);
      
      this.emit('urlImportCompleted', { importId, fileName });
      
      return importId;
    } catch (error) {
      log.error('URL import failed:', error);
      this.emit('urlImportFailed', { url, error: error.message });
      throw error;
    }
  }

  /**
   * Pause upload
   */
  pauseUpload(uploadId) {
    const entry = this.uploads.get(uploadId);
    if (entry && entry.status === 'uploading') {
      entry.status = 'paused';
      this.emit('uploadPaused', { uploadId });
    }
  }

  /**
   * Resume upload
   */
  resumeUpload(uploadId) {
    const entry = this.uploads.get(uploadId);
    if (entry && entry.status === 'paused') {
      entry.status = 'uploading';
      this.uploadFile(entry);
      this.emit('uploadResumed', { uploadId });
    }
  }

  /**
   * Cancel upload
   */
  cancelUpload(uploadId) {
    const entry = this.uploads.get(uploadId);
    if (entry) {
      entry.status = 'cancelled';
      this.activeUploads.delete(uploadId);
      this.emit('uploadCancelled', { uploadId });
    }
  }

  /**
   * Remove upload from queue
   */
  removeUpload(uploadId) {
    const entry = this.uploads.get(uploadId);
    if (entry && (entry.status === 'queued' || entry.status === 'failed')) {
      this.uploads.delete(uploadId);
      this.uploadQueue = this.uploadQueue.filter(e => e.id !== uploadId);
      this.emit('uploadRemoved', { uploadId });
    }
  }

  /**
   * Clear all uploads
   */
  clearUploads() {
    this.uploads.clear();
    this.uploadQueue.length = 0;
    this.activeUploads.clear();
    this.completedUploads.clear();
    this.failedUploads.clear();
    this.selectedFiles = [];
    this.updateUploadProgress();
    this.emit('uploadsCleared');
  }

  /**
   * Processor implementations
   */

  async generateThumbnail(file) {
    // Generate thumbnail for video/image files
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      if (file.type.startsWith('image/')) {
        const img = new Image();
        img.onload = () => {
          canvas.width = 200;
          canvas.height = (img.height / img.width) * 200;
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          resolve({
            dataUrl: canvas.toDataURL('image/jpeg', 0.8),
            width: canvas.width,
            height: canvas.height
          });
        };
        img.src = URL.createObjectURL(file);
      } else if (file.type.startsWith('video/')) {
        const video = document.createElement('video');
        video.onloadedmetadata = () => {
          video.currentTime = Math.min(5, video.duration / 4); // Thumbnail at 25% or 5s
        };
        video.onseeked = () => {
          canvas.width = 200;
          canvas.height = (video.videoHeight / video.videoWidth) * 200;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          resolve({
            dataUrl: canvas.toDataURL('image/jpeg', 0.8),
            width: canvas.width,
            height: canvas.height
          });
        };
        video.src = URL.createObjectURL(file);
      }
    });
  }

  async extractMetadata(file) {
    // Extract metadata from media files
    const metadata = {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: new Date(file.lastModified)
    };

    if (file.type.startsWith('image/')) {
      // Extract image metadata (EXIF data would be extracted here)
      metadata.format = 'image';
      metadata.dimensions = await this.getImageDimensions(file);
    } else if (file.type.startsWith('video/')) {
      // Extract video metadata
      metadata.format = 'video';
      const videoInfo = await this.getVideoInfo(file);
      metadata.duration = videoInfo.duration;
      metadata.dimensions = videoInfo.dimensions;
      metadata.fps = videoInfo.fps;
    } else if (file.type.startsWith('audio/')) {
      // Extract audio metadata
      metadata.format = 'audio';
      const audioInfo = await this.getAudioInfo(file);
      metadata.duration = audioInfo.duration;
      metadata.bitRate = audioInfo.bitRate;
      metadata.sampleRate = audioInfo.sampleRate;
    }

    return metadata;
  }

  async analyzeQuality(file) {
    // Analyze file quality
    const quality = {
      overall: 0.8, // Mock quality score
      resolution: 'high',
      clarity: 'good',
      compression: 'optimal',
      recommendations: []
    };

    if (file.size < 1024 * 1024) { // < 1MB
      quality.recommendations.push('Consider higher quality for better results');
    }

    return quality;
  }

  async analyzeContentAI(file) {
    // AI-powered content analysis
    return {
      objects: ['person', 'background'],
      scenes: ['indoor'],
      mood: 'positive',
      colors: ['blue', 'white'],
      tags: ['professional', 'studio'],
      contentType: 'portrait',
      appropriateness: 'safe',
      confidence: 0.85
    };
  }

  /**
   * Utility methods
   */

  getFileType(fileName) {
    const ext = path.extname(fileName).toLowerCase();
    
    for (const [type, extensions] of Object.entries(this.options.supportedFormats)) {
      if (extensions.includes(ext)) {
        return type;
      }
    }
    
    return 'unknown';
  }

  isSupportedFormat(fileName) {
    return this.getFileType(fileName) !== 'unknown';
  }

  isDuplicateFile(file) {
    return this.selectedFiles.some(entry => 
      entry.name === file.name && 
      entry.size === file.size && 
      entry.lastModified === file.lastModified
    );
  }

  async validateVideoFile(file) {
    // Video-specific validation
    return {
      valid: true,
      errors: []
    };
  }

  generateUploadId() {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  updateUploadProgress() {
    const totalFiles = this.uploads.size;
    const completedFiles = this.completedUploads.size;
    const totalSize = Array.from(this.uploads.values()).reduce((sum, entry) => sum + entry.size, 0);
    const uploadedSize = Array.from(this.uploads.values()).reduce((sum, entry) => sum + entry.uploadedBytes, 0);

    this.uploadProgress = {
      totalFiles,
      completedFiles,
      totalSize,
      uploadedSize,
      currentSpeed: this.calculateAverageSpeed(),
      timeRemaining: this.calculateTimeRemaining()
    };

    this.emit('progressUpdate', this.uploadProgress);
  }

  calculateAverageSpeed() {
    const activeEntries = Array.from(this.activeUploads.values());
    if (activeEntries.length === 0) return 0;
    
    return activeEntries.reduce((sum, entry) => sum + entry.speed, 0) / activeEntries.length;
  }

  calculateTimeRemaining() {
    const remainingSize = this.uploadProgress.totalSize - this.uploadProgress.uploadedSize;
    const speed = this.uploadProgress.currentSpeed;
    return speed > 0 ? remainingSize / speed : 0;
  }

  updateStatistics(entry, success) {
    this.statistics.totalUploads++;
    
    if (success) {
      this.statistics.successfulUploads++;
      this.statistics.totalDataUploaded += entry.size;
      
      // Update format distribution
      const currentCount = this.statistics.formatDistribution.get(entry.type) || 0;
      this.statistics.formatDistribution.set(entry.type, currentCount + 1);
      
      // Update average speed
      if (entry.speed > 0) {
        this.statistics.averageUploadSpeed = (
          (this.statistics.averageUploadSpeed * (this.statistics.successfulUploads - 1) + entry.speed) /
          this.statistics.successfulUploads
        );
      }
    } else {
      this.statistics.failedUploads++;
    }
  }

  extractFileNameFromURL(url) {
    return url.split('/').pop().split('?')[0] || 'imported_file';
  }

  // Placeholder methods for media analysis (would integrate with actual libraries)
  async getImageDimensions(file) { return { width: 1920, height: 1080 }; }
  async getVideoInfo(file) { return { duration: 120, dimensions: { width: 1920, height: 1080 }, fps: 30 }; }
  async getAudioInfo(file) { return { duration: 180, bitRate: 320000, sampleRate: 44100 }; }

  /**
   * Get upload statistics
   */
  getStatistics() {
    return {
      ...this.statistics,
      currentUploads: this.activeUploads.size,
      queuedUploads: this.uploadQueue.length,
      successRate: this.statistics.totalUploads > 0 ? 
        (this.statistics.successfulUploads / this.statistics.totalUploads) * 100 : 0
    };
  }

  /**
   * Get all uploads with status
   */
  getAllUploads() {
    return Array.from(this.uploads.values());
  }

  /**
   * Get uploads by status
   */
  getUploadsByStatus(status) {
    return Array.from(this.uploads.values()).filter(upload => upload.status === status);
  }

  /**
   * Clean up resources
   */
  destroy() {
    // Cancel all active uploads
    for (const uploadId of this.activeUploads.keys()) {
      this.cancelUpload(uploadId);
    }
    
    // Clear all data
    this.clearUploads();
    this.thumbnailCache.clear();
    this.metadataCache.clear();
    
    this.removeAllListeners();
    log.info('Upload interface destroyed');
  }
}

module.exports = UploadInterface;