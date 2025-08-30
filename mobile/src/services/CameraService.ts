/**
 * Camera Service - Advanced camera and media capture service
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * WARNING: This software is proprietary and confidential. 
 * Unauthorized copying, distribution, or use is strictly prohibited.
 * All rights reserved by Fahed Mlaiel.
 */

import { offlineStorageService } from './OfflineStorageService';
import { mobileAPIService } from './MobileAPIService';

export interface CameraCapabilities {
  isSupported: boolean;
  cameras: CameraDevice[];
  supportedFormats: MediaFormat[];
  maxResolution: { width: number; height: number };
  supportedFeatures: CameraFeature[];
}

export interface CameraDevice {
  id: string;
  label: string;
  type: 'front' | 'back' | 'external';
  capabilities: {
    video: VideoCapabilities;
    photo: PhotoCapabilities;
    audio: AudioCapabilities;
  };
}

export interface VideoCapabilities {
  resolutions: Resolution[];
  frameRates: number[];
  codecs: string[];
  maxBitrate: number;
  stabilization: boolean;
  autofocus: boolean;
  zoom: { min: number; max: number };
}

export interface PhotoCapabilities {
  resolutions: Resolution[];
  formats: ('jpeg' | 'png' | 'webp' | 'raw')[];
  flash: boolean;
  hdr: boolean;
  portraitMode: boolean;
  nightMode: boolean;
}

export interface AudioCapabilities {
  sampleRates: number[];
  channels: number[];
  codecs: string[];
  noiseCancellation: boolean;
  echoCancellation: boolean;
}

export interface Resolution {
  width: number;
  height: number;
  aspectRatio: string;
  megapixels?: number;
}

export interface MediaFormat {
  container: string;
  videoCodec?: string;
  audioCodec?: string;
  extension: string;
  mimeType: string;
}

export type CameraFeature = 'stabilization' | 'autofocus' | 'flash' | 'hdr' | 'portraitMode' | 'nightMode' | 'slowMotion' | 'timelapsse' | 'panorama';

export interface CaptureOptions {
  camera?: string; // camera device ID
  quality: 'low' | 'medium' | 'high' | 'ultra';
  format?: string;
  resolution?: Resolution;
  orientation?: 'portrait' | 'landscape' | 'auto';
  flash?: boolean;
  timer?: number; // seconds
  burst?: number; // number of photos
  location?: boolean;
  watermark?: {
    text?: string;
    image?: string;
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center';
    opacity: number;
  };
}

export interface VideoRecordingOptions extends CaptureOptions {
  duration?: number; // max duration in seconds
  frameRate?: number;
  bitrate?: number;
  stabilization?: boolean;
  audioEnabled?: boolean;
  microphoneGain?: number;
  slowMotion?: boolean;
  timelapsse?: { interval: number };
}

export interface PhotoCaptureOptions extends CaptureOptions {
  hdr?: boolean;
  portraitMode?: boolean;
  nightMode?: boolean;
  rawCapture?: boolean;
}

export interface CaptureResult {
  success: boolean;
  file?: CapturedFile;
  error?: string;
  metadata?: CaptureMetadata;
}

export interface CapturedFile {
  id: string;
  type: 'photo' | 'video';
  blob: Blob;
  url: string;
  filename: string;
  size: number;
  mimeType: string;
  createdAt: number;
}

export interface CaptureMetadata {
  camera: string;
  resolution: Resolution;
  fileSize: number;
  duration?: number; // for videos
  frameRate?: number; // for videos
  iso?: number;
  exposureTime?: number;
  fNumber?: number;
  focalLength?: number;
  location?: { latitude: number; longitude: number };
  orientation: number;
  timestamp: number;
  deviceInfo: {
    make: string;
    model: string;
    software: string;
  };
}

export interface EditingOptions {
  crop?: { x: number; y: number; width: number; height: number };
  resize?: Resolution;
  rotate?: number; // degrees
  filters?: {
    brightness?: number; // -100 to 100
    contrast?: number; // -100 to 100
    saturation?: number; // -100 to 100
    blur?: number; // 0 to 10
    sharpen?: number; // 0 to 10
    vintage?: boolean;
    blackAndWhite?: boolean;
    sepia?: boolean;
  };
  overlays?: {
    text?: { content: string; position: { x: number; y: number }; style: any };
    stickers?: { url: string; position: { x: number; y: number }; size: { width: number; height: number } }[];
    logo?: { url: string; position: string; opacity: number };
  };
}

export class CameraService {
  private isInitialized: boolean = false;
  private capabilities: CameraCapabilities;
  private currentStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private isRecording: boolean = false;
  private capturedFiles: Map<string, CapturedFile> = new Map();
  private defaultSettings: CaptureOptions;

  constructor() {
    this.capabilities = {
      isSupported: false,
      cameras: [],
      supportedFormats: [],
      maxResolution: { width: 0, height: 0 },
      supportedFeatures: [],
    };

    this.defaultSettings = {
      quality: 'high',
      orientation: 'auto',
      flash: false,
      location: false,
    };

    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    try {
      // Check for camera support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('Camera API not supported');
        return;
      }

      // Detect camera capabilities
      await this.detectCapabilities();
      
      // Load settings
      await this.loadSettings();
      
      // Initialize capture handlers
      this.setupCaptureHandlers();
      
      this.isInitialized = true;
      console.log('Camera Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Camera Service:', error);
    }
  }

  // Public API Methods
  async requestPermissions(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      
      // Stop the stream immediately, we just needed permission
      stream.getTracks().forEach(track => track.stop());
      
      return true;
    } catch (error) {
      console.error('Camera permission denied:', error);
      return false;
    }
  }

  getCapabilities(): CameraCapabilities {
    return { ...this.capabilities };
  }

  async getAvailableCameras(): Promise<CameraDevice[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const cameras = devices.filter(device => device.kind === 'videoinput');
      
      return cameras.map(device => ({
        id: device.deviceId,
        label: device.label || `Camera ${device.deviceId.substring(0, 8)}`,
        type: this.detectCameraType(device.label),
        capabilities: this.getCameraCapabilities(device.deviceId),
      }));
    } catch (error) {
      console.error('Failed to get available cameras:', error);
      return [];
    }
  }

  // Photo Capture
  async capturePhoto(options?: PhotoCaptureOptions): Promise<CaptureResult> {
    try {
      if (!this.capabilities.isSupported) {
        return { success: false, error: 'Camera not supported' };
      }

      const captureOptions = { ...this.defaultSettings, ...options };
      
      // Start camera stream
      const stream = await this.startCameraStream(captureOptions);
      
      // Create video element for capture
      const video = await this.createVideoElement(stream);
      
      // Apply camera settings
      await this.applyCameraSettings(stream, captureOptions);
      
      // Add timer delay if specified
      if (captureOptions.timer) {
        await this.delay(captureOptions.timer * 1000);
      }

      // Capture photo(s)
      const results: CapturedFile[] = [];
      const burstCount = captureOptions.burst || 1;
      
      for (let i = 0; i < burstCount; i++) {
        const capturedFile = await this.captureFrame(video, captureOptions);
        results.push(capturedFile);
        
        if (burstCount > 1 && i < burstCount - 1) {
          await this.delay(200); // 200ms between burst shots
        }
      }

      // Stop camera stream
      this.stopCameraStream(stream);

      // Process and save files
      const processedFiles = await Promise.all(
        results.map(file => this.processPhotoCapture(file, captureOptions))
      );

      // Return first file (or combined burst result)
      const mainFile = processedFiles[0];
      const metadata = await this.generateCaptureMetadata(mainFile, captureOptions);

      return {
        success: true,
        file: mainFile,
        metadata,
      };

    } catch (error) {
      console.error('Photo capture failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Video Recording
  async startVideoRecording(options?: VideoRecordingOptions): Promise<CaptureResult> {
    try {
      if (!this.capabilities.isSupported) {
        return { success: false, error: 'Camera not supported' };
      }

      if (this.isRecording) {
        return { success: false, error: 'Already recording' };
      }

      const recordOptions = { ...this.defaultSettings, ...options };
      
      // Start camera stream
      const stream = await this.startCameraStream(recordOptions);
      this.currentStream = stream;
      
      // Apply video settings
      await this.applyCameraSettings(stream, recordOptions);
      
      // Setup media recorder
      const mimeType = this.getBestVideoMimeType();
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        videoBitsPerSecond: recordOptions.bitrate || this.getOptimalBitrate(recordOptions.quality),
        audioBitsPerSecond: 128000, // 128 kbps audio
      });

      this.mediaRecorder = mediaRecorder;
      
      // Setup recording handlers
      const chunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: mimeType });
        const capturedFile = await this.createCapturedFile('video', blob);
        
        // Process video
        const processedFile = await this.processVideoCapture(capturedFile, recordOptions);
        
        // Generate metadata
        const metadata = await this.generateCaptureMetadata(processedFile, recordOptions);
        
        // Save file
        this.capturedFiles.set(processedFile.id, processedFile);
        
        // Emit recording complete event
        this.emitRecordingEvent('completed', { file: processedFile, metadata });
      };

      // Start recording
      mediaRecorder.start(1000); // 1 second chunks
      this.isRecording = true;
      
      // Set duration limit if specified
      if (recordOptions.duration) {
        setTimeout(() => {
          this.stopVideoRecording();
        }, recordOptions.duration * 1000);
      }

      this.emitRecordingEvent('started', { options: recordOptions });

      return { success: true };

    } catch (error) {
      console.error('Video recording start failed:', error);
      return { success: false, error: error.message };
    }
  }

  async stopVideoRecording(): Promise<CaptureResult> {
    try {
      if (!this.isRecording || !this.mediaRecorder) {
        return { success: false, error: 'Not recording' };
      }

      this.mediaRecorder.stop();
      this.isRecording = false;
      
      if (this.currentStream) {
        this.stopCameraStream(this.currentStream);
        this.currentStream = null;
      }

      this.emitRecordingEvent('stopped');

      return { success: true };
    } catch (error) {
      console.error('Video recording stop failed:', error);
      return { success: false, error: error.message };
    }
  }

  async pauseVideoRecording(): Promise<boolean> {
    if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.pause();
      this.emitRecordingEvent('paused');
      return true;
    }
    return false;
  }

  async resumeVideoRecording(): Promise<boolean> {
    if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state === 'paused') {
      this.mediaRecorder.resume();
      this.emitRecordingEvent('resumed');
      return true;
    }
    return false;
  }

  getRecordingStatus(): { isRecording: boolean; duration: number; state?: string } {
    return {
      isRecording: this.isRecording,
      duration: this.mediaRecorder ? Date.now() - this.mediaRecorder.stream.getTracks()[0].getSettings().timestamp || 0 : 0,
      state: this.mediaRecorder?.state,
    };
  }

  // Media Processing
  async editMedia(fileId: string, options: EditingOptions): Promise<CaptureResult> {
    try {
      const file = this.capturedFiles.get(fileId);
      if (!file) {
        return { success: false, error: 'File not found' };
      }

      const editedFile = await this.processMediaEditing(file, options);
      
      // Save edited version
      const newFileId = `${fileId}_edited_${Date.now()}`;
      const newFile = { ...editedFile, id: newFileId };
      this.capturedFiles.set(newFileId, newFile);

      return { success: true, file: newFile };
    } catch (error) {
      console.error('Media editing failed:', error);
      return { success: false, error: error.message };
    }
  }

  async compressMedia(fileId: string, quality: 'low' | 'medium' | 'high'): Promise<CaptureResult> {
    try {
      const file = this.capturedFiles.get(fileId);
      if (!file) {
        return { success: false, error: 'File not found' };
      }

      const compressedFile = await this.compressFile(file, quality);
      
      // Update file in storage
      this.capturedFiles.set(fileId, compressedFile);

      return { success: true, file: compressedFile };
    } catch (error) {
      console.error('Media compression failed:', error);
      return { success: false, error: error.message };
    }
  }

  // File Management
  getCapturedFiles(): CapturedFile[] {
    return Array.from(this.capturedFiles.values());
  }

  async saveToGallery(fileId: string): Promise<boolean> {
    try {
      const file = this.capturedFiles.get(fileId);
      if (!file) return false;

      // Save to device gallery/storage
      if ('showSaveFilePicker' in window) {
        const fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: file.filename,
          types: [{
            description: file.type === 'photo' ? 'Images' : 'Videos',
            accept: { [file.mimeType]: [`.${file.filename.split('.').pop()}`] },
          }],
        });

        const writable = await fileHandle.createWritable();
        await writable.write(file.blob);
        await writable.close();
      } else {
        // Fallback: trigger download
        const url = URL.createObjectURL(file.blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.filename;
        a.click();
        URL.revokeObjectURL(url);
      }

      return true;
    } catch (error) {
      console.error('Save to gallery failed:', error);
      return false;
    }
  }

  async deleteFile(fileId: string): Promise<boolean> {
    try {
      const file = this.capturedFiles.get(fileId);
      if (file) {
        // Revoke blob URL
        if (file.url) {
          URL.revokeObjectURL(file.url);
        }
        
        // Remove from storage
        this.capturedFiles.delete(fileId);
        
        // Remove from offline storage
        await offlineStorageService.remove(`camera_file_${fileId}`);
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Delete file failed:', error);
      return false;
    }
  }

  // Content Protection Integration
  async uploadForProtection(fileId: string): Promise<{ success: boolean; fingerprintId?: string; error?: string }> {
    try {
      const file = this.capturedFiles.get(fileId);
      if (!file) {
        return { success: false, error: 'File not found' };
      }

      // Generate content metadata
      const metadata = await this.generateCaptureMetadata(file, {});
      
      // Upload to content protection system
      const response = await mobileAPIService.uploadContent(
        {
          contentId: file.id,
          type: file.type === 'photo' ? 'image' : 'video',
          size: file.size,
          format: file.mimeType,
          quality: 'high',
          timestamp: file.createdAt,
          fingerprint: await this.generateContentFingerprint(file),
        },
        file.blob
      );

      if (response.status === 200) {
        return {
          success: true,
          fingerprintId: response.data.fingerprintId,
        };
      }

      return { success: false, error: 'Upload failed' };
    } catch (error) {
      console.error('Upload for protection failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Private Methods
  private async detectCapabilities(): Promise<void> {
    try {
      if (!navigator.mediaDevices) {
        return;
      }

      this.capabilities.isSupported = true;
      
      // Get available cameras
      this.capabilities.cameras = await this.getAvailableCameras();
      
      // Detect supported formats
      this.capabilities.supportedFormats = this.getSupportedFormats();
      
      // Detect max resolution
      this.capabilities.maxResolution = await this.getMaxResolution();
      
      // Detect supported features
      this.capabilities.supportedFeatures = this.getSupportedFeatures();
      
    } catch (error) {
      console.error('Capability detection failed:', error);
    }
  }

  private detectCameraType(label: string): 'front' | 'back' | 'external' {
    const lowerLabel = label.toLowerCase();
    
    if (lowerLabel.includes('front') || lowerLabel.includes('user') || lowerLabel.includes('selfie')) {
      return 'front';
    } else if (lowerLabel.includes('back') || lowerLabel.includes('rear') || lowerLabel.includes('environment')) {
      return 'back';
    } else {
      return 'external';
    }
  }

  private getCameraCapabilities(deviceId: string): CameraDevice['capabilities'] {
    // This would query actual device capabilities in a real implementation
    return {
      video: {
        resolutions: [
          { width: 1920, height: 1080, aspectRatio: '16:9' },
          { width: 1280, height: 720, aspectRatio: '16:9' },
          { width: 640, height: 480, aspectRatio: '4:3' },
        ],
        frameRates: [15, 24, 30, 60],
        codecs: ['h264', 'vp8', 'vp9'],
        maxBitrate: 8000000, // 8 Mbps
        stabilization: true,
        autofocus: true,
        zoom: { min: 1, max: 8 },
      },
      photo: {
        resolutions: [
          { width: 4032, height: 3024, aspectRatio: '4:3', megapixels: 12.2 },
          { width: 3264, height: 2448, aspectRatio: '4:3', megapixels: 8.0 },
          { width: 2048, height: 1536, aspectRatio: '4:3', megapixels: 3.1 },
        ],
        formats: ['jpeg', 'png', 'webp'],
        flash: true,
        hdr: true,
        portraitMode: true,
        nightMode: true,
      },
      audio: {
        sampleRates: [44100, 48000],
        channels: [1, 2],
        codecs: ['aac', 'opus'],
        noiseCancellation: true,
        echoCancellation: true,
      },
    };
  }

  private getSupportedFormats(): MediaFormat[] {
    const formats: MediaFormat[] = [];
    
    // Check video formats
    if (MediaRecorder.isTypeSupported('video/mp4; codecs="avc1.42E01E,mp4a.40.2"')) {
      formats.push({
        container: 'mp4',
        videoCodec: 'h264',
        audioCodec: 'aac',
        extension: 'mp4',
        mimeType: 'video/mp4',
      });
    }
    
    if (MediaRecorder.isTypeSupported('video/webm; codecs="vp8,opus"')) {
      formats.push({
        container: 'webm',
        videoCodec: 'vp8',
        audioCodec: 'opus',
        extension: 'webm',
        mimeType: 'video/webm',
      });
    }
    
    // Photo formats (always supported)
    formats.push(
      {
        container: 'jpeg',
        extension: 'jpg',
        mimeType: 'image/jpeg',
      },
      {
        container: 'png',
        extension: 'png',
        mimeType: 'image/png',
      },
      {
        container: 'webp',
        extension: 'webp',
        mimeType: 'image/webp',
      }
    );
    
    return formats;
  }

  private async getMaxResolution(): Promise<Resolution> {
    try {
      // Try to get highest resolution supported
      const constraints = {
        video: {
          width: { ideal: 4096 },
          height: { ideal: 2160 },
        },
      };
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      const track = stream.getVideoTracks()[0];
      const settings = track.getSettings();
      
      stream.getTracks().forEach(track => track.stop());
      
      return {
        width: settings.width || 1920,
        height: settings.height || 1080,
        aspectRatio: this.calculateAspectRatio(settings.width || 1920, settings.height || 1080),
      };
    } catch (error) {
      return { width: 1920, height: 1080, aspectRatio: '16:9' };
    }
  }

  private getSupportedFeatures(): CameraFeature[] {
    const features: CameraFeature[] = ['autofocus'];
    
    // Check for advanced features (would be platform-specific in real implementation)
    if ('ImageCapture' in window) {
      features.push('flash', 'hdr');
    }
    
    return features;
  }

  private async startCameraStream(options: CaptureOptions): Promise<MediaStream> {
    const constraints: MediaStreamConstraints = {
      video: {
        deviceId: options.camera ? { exact: options.camera } : undefined,
        width: options.resolution?.width || this.getResolutionForQuality(options.quality).width,
        height: options.resolution?.height || this.getResolutionForQuality(options.quality).height,
        facingMode: options.camera ? undefined : 'environment',
      },
      audio: true,
    };

    return navigator.mediaDevices.getUserMedia(constraints);
  }

  private async createVideoElement(stream: MediaStream): Promise<HTMLVideoElement> {
    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();
    
    return new Promise((resolve) => {
      video.onloadedmetadata = () => resolve(video);
    });
  }

  private async applyCameraSettings(stream: MediaStream, options: CaptureOptions): Promise<void> {
    const track = stream.getVideoTracks()[0];
    
    if ('ImageCapture' in window) {
      const imageCapture = new (window as any).ImageCapture(track);
      
      try {
        // Apply photo settings if available
        const photoCapabilities = await imageCapture.getPhotoCapabilities();
        const settings: any = {};
        
        if (options.flash && photoCapabilities.fillLightMode.includes('flash')) {
          settings.fillLightMode = 'flash';
        }
        
        if (Object.keys(settings).length > 0) {
          await imageCapture.setOptions(settings);
        }
      } catch (error) {
        console.warn('Failed to apply camera settings:', error);
      }
    }
  }

  private async captureFrame(video: HTMLVideoElement, options: CaptureOptions): Promise<CapturedFile> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);
    
    // Apply watermark if specified
    if (options.watermark) {
      await this.applyWatermark(ctx, canvas, options.watermark);
    }
    
    // Convert to blob
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(this.createCapturedFile('photo', blob!));
      }, 'image/jpeg', this.getJpegQuality(options.quality));
    });
  }

  private async createCapturedFile(type: 'photo' | 'video', blob: Blob): Promise<CapturedFile> {
    const id = `${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const extension = type === 'photo' ? 'jpg' : 'mp4';
    const filename = `${id}.${extension}`;
    const url = URL.createObjectURL(blob);
    
    return {
      id,
      type,
      blob,
      url,
      filename,
      size: blob.size,
      mimeType: blob.type,
      createdAt: Date.now(),
    };
  }

  private async processPhotoCapture(file: CapturedFile, options: CaptureOptions): Promise<CapturedFile> {
    // Apply photo processing based on options
    let processedBlob = file.blob;
    
    // Auto-enhance based on quality setting
    if (options.quality === 'ultra') {
      processedBlob = await this.enhancePhoto(processedBlob);
    }
    
    // Save file for offline access
    await offlineStorageService.store(`camera_file_${file.id}`, {
      ...file,
      blob: undefined, // Don't store blob directly
    });
    
    return { ...file, blob: processedBlob };
  }

  private async processVideoCapture(file: CapturedFile, options: VideoRecordingOptions): Promise<CapturedFile> {
    // Apply video processing based on options
    let processedBlob = file.blob;
    
    // Apply stabilization if enabled
    if (options.stabilization) {
      processedBlob = await this.stabilizeVideo(processedBlob);
    }
    
    // Save file for offline access
    await offlineStorageService.store(`camera_file_${file.id}`, {
      ...file,
      blob: undefined, // Don't store blob directly
    });
    
    return { ...file, blob: processedBlob };
  }

  private async generateCaptureMetadata(file: CapturedFile, options: CaptureOptions): Promise<CaptureMetadata> {
    const metadata: CaptureMetadata = {
      camera: options.camera || 'default',
      resolution: await this.getFileResolution(file),
      fileSize: file.size,
      orientation: 1, // Normal orientation
      timestamp: file.createdAt,
      deviceInfo: {
        make: 'Unknown',
        model: navigator.platform,
        software: navigator.userAgent,
      },
    };
    
    // Add location if enabled
    if (options.location) {
      metadata.location = await this.getCurrentLocation();
    }
    
    // Add video-specific metadata
    if (file.type === 'video') {
      metadata.duration = await this.getVideoDuration(file.blob);
      metadata.frameRate = 30; // Default, would be detected in real implementation
    }
    
    return metadata;
  }

  private stopCameraStream(stream: MediaStream): void {
    stream.getTracks().forEach(track => track.stop());
  }

  private getResolutionForQuality(quality: string): Resolution {
    const resolutions = {
      low: { width: 640, height: 480, aspectRatio: '4:3' },
      medium: { width: 1280, height: 720, aspectRatio: '16:9' },
      high: { width: 1920, height: 1080, aspectRatio: '16:9' },
      ultra: { width: 3840, height: 2160, aspectRatio: '16:9' },
    };
    
    return resolutions[quality as keyof typeof resolutions] || resolutions.high;
  }

  private getJpegQuality(quality: string): number {
    const qualities = { low: 0.6, medium: 0.8, high: 0.9, ultra: 0.95 };
    return qualities[quality as keyof typeof qualities] || 0.9;
  }

  private getOptimalBitrate(quality: string): number {
    const bitrates = {
      low: 1000000,    // 1 Mbps
      medium: 3000000, // 3 Mbps
      high: 6000000,   // 6 Mbps
      ultra: 12000000, // 12 Mbps
    };
    
    return bitrates[quality as keyof typeof bitrates] || 6000000;
  }

  private getBestVideoMimeType(): string {
    const types = [
      'video/mp4; codecs="avc1.42E01E,mp4a.40.2"',
      'video/webm; codecs="vp8,opus"',
      'video/webm; codecs="vp9,opus"',
    ];
    
    return types.find(type => MediaRecorder.isTypeSupported(type)) || 'video/webm';
  }

  private calculateAspectRatio(width: number, height: number): string {
    const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
    const divisor = gcd(width, height);
    return `${width / divisor}:${height / divisor}`;
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Processing Methods (simplified implementations)
  private async enhancePhoto(blob: Blob): Promise<Blob> {
    // In a real implementation, this would apply AI-based photo enhancement
    return blob;
  }

  private async stabilizeVideo(blob: Blob): Promise<Blob> {
    // In a real implementation, this would apply video stabilization
    return blob;
  }

  private async processMediaEditing(file: CapturedFile, options: EditingOptions): Promise<CapturedFile> {
    // In a real implementation, this would apply the editing options
    return file;
  }

  private async compressFile(file: CapturedFile, quality: string): Promise<CapturedFile> {
    // In a real implementation, this would compress the file
    return file;
  }

  private async applyWatermark(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement, watermark: any): Promise<void> {
    // Apply watermark to canvas context
    if (watermark.text) {
      ctx.font = '20px Arial';
      ctx.fillStyle = `rgba(255, 255, 255, ${watermark.opacity})`;
      ctx.fillText(watermark.text, 20, canvas.height - 20);
    }
  }

  private async getFileResolution(file: CapturedFile): Promise<Resolution> {
    if (file.type === 'photo') {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
          resolve({
            width: img.width,
            height: img.height,
            aspectRatio: this.calculateAspectRatio(img.width, img.height),
          });
        };
        img.src = file.url;
      });
    } else {
      return new Promise((resolve) => {
        const video = document.createElement('video');
        video.onloadedmetadata = () => {
          resolve({
            width: video.videoWidth,
            height: video.videoHeight,
            aspectRatio: this.calculateAspectRatio(video.videoWidth, video.videoHeight),
          });
        };
        video.src = file.url;
      });
    }
  }

  private async getVideoDuration(blob: Blob): Promise<number> {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.onloadedmetadata = () => {
        resolve(video.duration);
      };
      video.src = URL.createObjectURL(blob);
    });
  }

  private async getCurrentLocation(): Promise<{ latitude: number; longitude: number } | undefined> {
    if (!navigator.geolocation) return undefined;
    
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        () => resolve(undefined),
        { timeout: 10000 }
      );
    });
  }

  private async generateContentFingerprint(file: CapturedFile): Promise<string> {
    // Generate a basic fingerprint for content protection
    const arrayBuffer = await file.blob.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private emitRecordingEvent(type: string, data?: any): void {
    // Emit custom events for recording state changes
    const event = new CustomEvent(`camera-recording-${type}`, { detail: data });
    window.dispatchEvent(event);
  }

  private setupCaptureHandlers(): void {
    // Setup event handlers for capture operations
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.isRecording) {
        // Pause recording when app goes to background
        this.pauseVideoRecording();
      }
    });
  }

  private async loadSettings(): Promise<void> {
    const stored = await offlineStorageService.retrieve('camera_settings');
    if (stored) {
      this.defaultSettings = { ...this.defaultSettings, ...stored };
    }
  }
}

// Export singleton instance
export const cameraService = new CameraService();