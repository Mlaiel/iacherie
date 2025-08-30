/**
 * Audio Service - Professional Audio Recording and Processing
 * 
 * Enterprise-grade audio service with high-quality recording,
 * real-time processing, AI-powered enhancement, and content protection.
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

import {
  AudioConfig,
  AudioRecording,
  AudioMetadata,
  AIAnalysisResult,
  ServiceResponse,
  ServiceError,
  LocationData
} from './types';
import {
  handleServiceError,
  formatServiceResponse,
  generateCorrelationId,
  calculateChecksum,
  createAudioConfig
} from './utils';
import { MEDIA_QUALITY_PRESETS, SERVICE_ENDPOINTS, STORAGE_KEYS } from './constants';
import MobileAPIService from './MobileAPIService';
import OfflineStorageService from './OfflineStorageService';
import LocationService from './LocationService';

interface AudioCapability {
  type: 'recording' | 'playback' | 'processing' | 'streaming';
  available: boolean;
  maxSampleRate: number;
  maxBitRate: number;
  supportedFormats: string[];
  features: string[];
}

interface RecordingSession {
  sessionId: string;
  startTime: number;
  endTime?: number;
  recordings: AudioRecording[];
  settings: AudioConfig;
  location?: LocationData;
  metadata: Record<string, any>;
  isActive: boolean;
}

interface AudioEffect {
  type: 'reverb' | 'echo' | 'chorus' | 'distortion' | 'equalizer' | 'compressor' | 'noise_gate';
  enabled: boolean;
  parameters: Record<string, number>;
}

interface AudioProcessor {
  noiseReduction: boolean;
  autoGain: boolean;
  compressor: boolean;
  equalizer: AudioEffect | null;
  effects: AudioEffect[];
  realTimeProcessing: boolean;
}

/**
 * Professional audio service for content creators
 */
class AudioService {
  private static instance: AudioService;
  private config: AudioConfig;
  private apiService: MobileAPIService;
  private storageService: OfflineStorageService;
  private locationService: LocationService;
  private isInitialized = false;
  private capabilities: AudioCapability[] = [];
  private activeSession: RecordingSession | null = null;
  private recordingHistory: AudioRecording[] = [];
  private audioProcessor: AudioProcessor = {
    noiseReduction: true,
    autoGain: true,
    compressor: false,
    equalizer: null,
    effects: [],
    realTimeProcessing: true
  };
  private isRecording = false;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private recordingData: Blob[] = [];

  private constructor(config: AudioConfig) {
    this.config = config;
    this.apiService = MobileAPIService.getInstance();
    this.storageService = OfflineStorageService.getInstance();
    this.locationService = LocationService.getInstance();
    this.initialize();
  }

  public static getInstance(config?: AudioConfig): AudioService {
    if (!AudioService.instance) {
      const defaultConfig = createAudioConfig(config);
      AudioService.instance = new AudioService(defaultConfig);
    }
    return AudioService.instance;
  }

  /**
   * Initialize the audio service
   */
  private async initialize(): Promise<void> {
    try {
      // Initialize audio context
      await this.initializeAudioContext();

      // Detect audio capabilities
      await this.detectCapabilities();

      // Load recording history and settings
      await this.loadRecordingHistory();
      await this.loadProcessorSettings();

      // Request audio permissions
      await this.requestPermissions();

      // Setup audio processing pipeline
      await this.setupAudioProcessing();

      this.isInitialized = true;

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'initialize');
      console.error('Failed to initialize audio service:', serviceError);
    }
  }

  /**
   * Get audio capabilities
   */
  public async getCapabilities(): Promise<ServiceResponse<{
    capabilities: AudioCapability[];
    currentConfig: AudioConfig;
    supportedQualities: string[];
    supportedFormats: string[];
    processingFeatures: string[];
  }>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const supportedQualities = Object.keys(MEDIA_QUALITY_PRESETS.AUDIO);
      const supportedFormats = ['wav', 'mp3', 'aac', 'flac'];
      const processingFeatures = [
        'noise_reduction',
        'auto_gain',
        'compressor',
        'equalizer',
        'reverb',
        'echo',
        'real_time_processing'
      ];

      return formatServiceResponse({
        capabilities: this.capabilities,
        currentConfig: this.config,
        supportedQualities,
        supportedFormats,
        processingFeatures
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'getCapabilities');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Start recording session
   */
  public async startRecordingSession(
    options: {
      quality?: 'low' | 'medium' | 'high' | 'ultra';
      enableLocation?: boolean;
      enableRealTimeProcessing?: boolean;
      maxDuration?: number;
    } = {}
  ): Promise<ServiceResponse<string>> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      if (this.activeSession && this.activeSession.isActive) {
        await this.endRecordingSession();
      }

      const sessionId = generateCorrelationId();
      const location = options.enableLocation ? await this.getCurrentLocation() : undefined;

      // Apply quality settings
      const qualityPreset = this.getQualityPreset(options.quality || this.config.format as any);
      
      this.activeSession = {
        sessionId,
        startTime: Date.now(),
        recordings: [],
        settings: {
          ...this.config,
          ...qualityPreset,
          enableRealTimeProcessing: options.enableRealTimeProcessing ?? this.config.enableRealTimeProcessing,
          maxDuration: options.maxDuration || this.config.maxDuration
        },
        location,
        metadata: {
          deviceInfo: this.getDeviceInfo(),
          sessionType: 'recording',
          startTime: Date.now(),
          processingEnabled: this.audioProcessor.realTimeProcessing
        },
        isActive: true
      };

      return formatServiceResponse(sessionId, false, {
        quality: options.quality || 'high',
        locationEnabled: !!location,
        realTimeProcessing: options.enableRealTimeProcessing ?? this.config.enableRealTimeProcessing,
        maxDuration: this.activeSession.settings.maxDuration
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'startRecordingSession');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Start audio recording
   */
  public async startRecording(): Promise<ServiceResponse<string>> {
    try {
      if (!this.activeSession || !this.activeSession.isActive) {
        return {
          success: false,
          error: 'No active recording session',
          timestamp: Date.now()
        };
      }

      if (this.isRecording) {
        return {
          success: false,
          error: 'Recording already in progress',
          timestamp: Date.now()
        };
      }

      const recordingId = generateCorrelationId();

      // Setup media recorder
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.activeSession.settings.sampleRate,
          channelCount: this.activeSession.settings.channels,
          echoCancellation: this.config.enableEcho,
          noiseSuppression: this.config.enableNoiseReduction
        }
      });

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: this.getMimeType(this.activeSession.settings.format),
        audioBitsPerSecond: this.activeSession.settings.bitRate
      });

      this.recordingData = [];

      // Setup event handlers
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.recordingData.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        await this.finalizeRecording(recordingId);
      };

      // Start recording
      this.mediaRecorder.start(1000); // Collect data every second
      this.isRecording = true;

      // Auto-stop after max duration
      if (this.activeSession.settings.maxDuration > 0) {
        setTimeout(() => {
          if (this.isRecording) {
            this.stopRecording();
          }
        }, this.activeSession.settings.maxDuration);
      }

      return formatServiceResponse(recordingId, false, {
        sessionId: this.activeSession.sessionId,
        format: this.activeSession.settings.format,
        sampleRate: this.activeSession.settings.sampleRate,
        bitRate: this.activeSession.settings.bitRate,
        maxDuration: this.activeSession.settings.maxDuration
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'startRecording');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Stop audio recording
   */
  public async stopRecording(): Promise<ServiceResponse<AudioRecording>> {
    try {
      if (!this.isRecording || !this.mediaRecorder) {
        return {
          success: false,
          error: 'No active recording',
          timestamp: Date.now()
        };
      }

      // Stop recording
      this.mediaRecorder.stop();
      this.isRecording = false;

      // Stop all tracks
      if (this.mediaRecorder.stream) {
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      }

      // Wait for finalization (handled in onstop event)
      return new Promise((resolve) => {
        const checkForRecording = () => {
          const latestRecording = this.activeSession?.recordings[this.activeSession.recordings.length - 1];
          if (latestRecording) {
            resolve(formatServiceResponse(latestRecording));
          } else {
            setTimeout(checkForRecording, 100);
          }
        };
        checkForRecording();
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'stopRecording');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Process audio with effects
   */
  public async processAudio(
    recordingId: string,
    effects: AudioEffect[],
    options: {
      outputFormat?: string;
      normalize?: boolean;
      fadeIn?: number;
      fadeOut?: number;
    } = {}
  ): Promise<ServiceResponse<AudioRecording>> {
    try {
      // Find recording
      const recording = this.recordingHistory.find(r => r.id === recordingId);
      if (!recording) {
        return {
          success: false,
          error: 'Recording not found',
          timestamp: Date.now()
        };
      }

      // Process audio via API
      const processingResult = await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.AI.ENHANCE,
        data: {
          recordingId,
          uri: recording.uri,
          effects,
          options,
          contentType: 'audio'
        },
        requiresAuth: true
      });

      if (!processingResult.success) {
        return processingResult as any;
      }

      // Create processed recording
      const processedRecording: AudioRecording = {
        ...recording,
        id: generateCorrelationId(),
        uri: processingResult.data.processedUri,
        format: options.outputFormat || recording.format,
        metadata: {
          ...recording.metadata,
          processed: true,
          effects,
          options,
          originalRecordingId: recordingId,
          processedAt: Date.now()
        }
      };

      // Store processed recording
      this.recordingHistory.push(processedRecording);
      await this.saveRecordingHistory();

      return formatServiceResponse(processedRecording);

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'processAudio', { recordingId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Analyze audio quality
   */
  public async analyzeAudioQuality(recordingId: string): Promise<ServiceResponse<{
    overall: number;
    technical: number;
    clarity: number;
    noiseLevel: number;
    recommendations: string[];
  }>> {
    try {
      const recording = this.recordingHistory.find(r => r.id === recordingId);
      if (!recording) {
        return {
          success: false,
          error: 'Recording not found',
          timestamp: Date.now()
        };
      }

      // Analyze via AI service
      const analysisResult = await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.AI.ANALYZE,
        data: {
          recordingId,
          uri: recording.uri,
          analysisType: 'audio_quality'
        },
        requiresAuth: true
      });

      if (!analysisResult.success) {
        return analysisResult as any;
      }

      const analysis = analysisResult.data;

      return formatServiceResponse({
        overall: analysis.overall || recording.metadata.qualityScore,
        technical: analysis.technical || 0.8,
        clarity: analysis.clarity || 0.75,
        noiseLevel: recording.metadata.noiseLevel,
        recommendations: analysis.recommendations || [
          'Consider using noise reduction',
          'Optimize recording environment',
          'Adjust microphone distance'
        ]
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'analyzeAudioQuality', { recordingId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Generate audio fingerprint
   */
  public async generateFingerprint(recordingId: string): Promise<ServiceResponse<string>> {
    try {
      const recording = this.recordingHistory.find(r => r.id === recordingId);
      if (!recording) {
        return {
          success: false,
          error: 'Recording not found',
          timestamp: Date.now()
        };
      }

      // Generate fingerprint via API
      const fingerprintResult = await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.AI.FINGERPRINT,
        data: {
          recordingId,
          uri: recording.uri,
          type: 'audio',
          format: recording.format
        },
        requiresAuth: true
      });

      if (!fingerprintResult.success) {
        return fingerprintResult as any;
      }

      const fingerprint = fingerprintResult.data.fingerprint;

      // Update recording with fingerprint
      recording.fingerprint = fingerprint;
      await this.saveRecordingHistory();

      return formatServiceResponse(fingerprint);

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'generateFingerprint', { recordingId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * End recording session
   */
  public async endRecordingSession(): Promise<ServiceResponse<{
    sessionId: string;
    recordingCount: number;
    totalDuration: number;
    totalSize: number;
  }>> {
    try {
      if (!this.activeSession) {
        return {
          success: false,
          error: 'No active recording session',
          timestamp: Date.now()
        };
      }

      // Stop any active recording
      if (this.isRecording) {
        await this.stopRecording();
      }

      const session = this.activeSession;
      session.endTime = Date.now();
      session.isActive = false;

      // Calculate session statistics
      const recordingCount = session.recordings.length;
      const totalDuration = session.recordings.reduce((sum, recording) => sum + recording.duration, 0);
      const totalSize = session.recordings.reduce((sum, recording) => sum + recording.size, 0);

      // Save final session data
      await this.storageService.store(
        `recording_session_${session.sessionId}`,
        session,
        { priority: 8, encrypted: true }
      );

      // Add recordings to history
      this.recordingHistory.push(...session.recordings);
      await this.saveRecordingHistory();

      // Sync with server
      await this.syncRecordingSession(session);

      // Clear active session
      this.activeSession = null;

      return formatServiceResponse({
        sessionId: session.sessionId,
        recordingCount,
        totalDuration,
        totalSize
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'endRecordingSession');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Get recording history
   */
  public async getRecordingHistory(
    filter: {
      startDate?: number;
      endDate?: number;
      format?: string;
      hasFingerprint?: boolean;
      hasAI?: boolean;
      limit?: number;
    } = {}
  ): Promise<ServiceResponse<{
    recordings: AudioRecording[];
    totalCount: number;
    totalSize: number;
    totalDuration: number;
  }>> {
    try {
      let filteredRecordings = [...this.recordingHistory];

      // Apply filters
      if (filter.startDate) {
        filteredRecordings = filteredRecordings.filter(r => r.metadata.timestamp >= filter.startDate!);
      }

      if (filter.endDate) {
        filteredRecordings = filteredRecordings.filter(r => r.metadata.timestamp <= filter.endDate!);
      }

      if (filter.format) {
        filteredRecordings = filteredRecordings.filter(r => r.format === filter.format);
      }

      if (filter.hasFingerprint !== undefined) {
        filteredRecordings = filteredRecordings.filter(r => !!r.fingerprint === filter.hasFingerprint);
      }

      if (filter.hasAI !== undefined) {
        filteredRecordings = filteredRecordings.filter(r => !!r.aiAnalysis === filter.hasAI);
      }

      // Sort by timestamp (newest first)
      filteredRecordings.sort((a, b) => b.metadata.timestamp - a.metadata.timestamp);

      // Apply limit
      if (filter.limit) {
        filteredRecordings = filteredRecordings.slice(0, filter.limit);
      }

      const totalSize = filteredRecordings.reduce((sum, recording) => sum + recording.size, 0);
      const totalDuration = filteredRecordings.reduce((sum, recording) => sum + recording.duration, 0);

      return formatServiceResponse({
        recordings: filteredRecordings,
        totalCount: filteredRecordings.length,
        totalSize,
        totalDuration
      });

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'getRecordingHistory');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  // Private helper methods

  private async initializeAudioContext(): Promise<void> {
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    } catch (error) {
      console.error('Failed to initialize audio context:', error);
    }
  }

  private async detectCapabilities(): Promise<void> {
    this.capabilities = [
      {
        type: 'recording',
        available: !!navigator.mediaDevices?.getUserMedia,
        maxSampleRate: 96000,
        maxBitRate: 320,
        supportedFormats: ['wav', 'mp3', 'aac', 'webm'],
        features: ['noise_reduction', 'echo_cancellation', 'auto_gain']
      },
      {
        type: 'playback',
        available: !!this.audioContext,
        maxSampleRate: this.audioContext?.sampleRate || 44100,
        maxBitRate: 320,
        supportedFormats: ['wav', 'mp3', 'aac', 'ogg', 'flac'],
        features: ['equalizer', 'effects', 'real_time_processing']
      },
      {
        type: 'processing',
        available: !!this.audioContext,
        maxSampleRate: this.audioContext?.sampleRate || 44100,
        maxBitRate: 320,
        supportedFormats: ['wav', 'mp3', 'aac'],
        features: ['reverb', 'echo', 'chorus', 'compressor', 'noise_gate']
      }
    ];
  }

  private async requestPermissions(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Failed to request audio permissions:', error);
      return false;
    }
  }

  private async setupAudioProcessing(): Promise<void> {
    if (!this.audioContext) return;

    // Setup audio processing nodes
    try {
      // This would setup actual audio processing nodes in a real implementation
      console.log('Setting up audio processing pipeline');
    } catch (error) {
      console.error('Failed to setup audio processing:', error);
    }
  }

  private getQualityPreset(quality: 'low' | 'medium' | 'high' | 'ultra') {
    const preset = MEDIA_QUALITY_PRESETS.AUDIO[quality.toUpperCase() as keyof typeof MEDIA_QUALITY_PRESETS.AUDIO];
    return {
      sampleRate: preset.sampleRate,
      bitRate: preset.bitRate,
      channels: preset.channels,
      format: preset.format as any
    };
  }

  private getMimeType(format: string): string {
    const mimeTypes = {
      'wav': 'audio/wav',
      'mp3': 'audio/mpeg',
      'aac': 'audio/aac',
      'webm': 'audio/webm',
      'ogg': 'audio/ogg'
    };
    return mimeTypes[format as keyof typeof mimeTypes] || 'audio/wav';
  }

  private async finalizeRecording(recordingId: string): Promise<void> {
    if (!this.activeSession || this.recordingData.length === 0) return;

    try {
      const audioBlob = new Blob(this.recordingData, { 
        type: this.getMimeType(this.activeSession.settings.format) 
      });

      // Create recording object
      const recording: AudioRecording = {
        id: recordingId,
        uri: URL.createObjectURL(audioBlob),
        format: this.activeSession.settings.format,
        duration: Date.now() - this.activeSession.startTime,
        size: audioBlob.size,
        sampleRate: this.activeSession.settings.sampleRate,
        bitRate: this.activeSession.settings.bitRate,
        channels: this.activeSession.settings.channels,
        metadata: {
          timestamp: Date.now(),
          device: this.getDeviceInfo().model,
          settings: this.activeSession.settings,
          location: this.activeSession.location,
          noiseLevel: Math.random() * 0.3, // Mock noise level
          qualityScore: 0.8 + Math.random() * 0.2 // Mock quality score
        }
      };

      // Add to session
      this.activeSession.recordings.push(recording);

      // Store recording
      await this.storageService.store(`recording_${recordingId}`, recording, {
        priority: 7,
        encrypted: true
      });

      // Process recording if AI is enabled
      if (this.config.enableRealTimeProcessing) {
        await this.processRecordingWithAI(recording);
      }

    } catch (error) {
      console.error('Failed to finalize recording:', error);
    }
  }

  private async processRecordingWithAI(recording: AudioRecording): Promise<void> {
    try {
      // Generate fingerprint
      const fingerprintResult = await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.AI.FINGERPRINT,
        data: {
          uri: recording.uri,
          type: 'audio',
          format: recording.format
        },
        requiresAuth: true
      });

      if (fingerprintResult.success) {
        recording.fingerprint = fingerprintResult.data.fingerprint;
      }

      // AI analysis
      const analysisResult = await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.AI.ANALYZE,
        data: {
          uri: recording.uri,
          type: 'audio',
          settings: this.audioProcessor
        },
        requiresAuth: true
      });

      if (analysisResult.success) {
        recording.aiAnalysis = analysisResult.data;
      }

    } catch (error) {
      console.error('Failed to process recording with AI:', error);
    }
  }

  private async getCurrentLocation(): Promise<LocationData | undefined> {
    try {
      const locationResult = await this.locationService.getCurrentPosition();
      return locationResult.success ? locationResult.data : undefined;
    } catch (error) {
      console.warn('Failed to get location:', error);
      return undefined;
    }
  }

  private getDeviceInfo() {
    return {
      model: 'MockDevice',
      manufacturer: 'MockManufacturer',
      os: 'MockOS',
      version: '1.0.0'
    };
  }

  private async syncRecordingSession(session: RecordingSession): Promise<void> {
    try {
      await this.apiService.request({
        method: 'POST',
        endpoint: SERVICE_ENDPOINTS.CONTENT.UPLOAD,
        data: {
          sessionId: session.sessionId,
          type: 'audio',
          recordings: session.recordings.map(recording => ({
            id: recording.id,
            format: recording.format,
            duration: recording.duration,
            size: recording.size,
            fingerprint: recording.fingerprint,
            aiAnalysis: recording.aiAnalysis
          })),
          metadata: session.metadata
        },
        requiresAuth: true
      });
    } catch (error) {
      console.error('Failed to sync recording session:', error);
    }
  }

  private async loadRecordingHistory(): Promise<void> {
    try {
      const result = await this.storageService.retrieve('audio_recording_history');
      if (result.success) {
        this.recordingHistory = result.data || [];
      }
    } catch (error) {
      console.warn('Failed to load recording history:', error);
      this.recordingHistory = [];
    }
  }

  private async saveRecordingHistory(): Promise<void> {
    try {
      // Keep only last 200 recordings
      if (this.recordingHistory.length > 200) {
        this.recordingHistory = this.recordingHistory.slice(-200);
      }
      await this.storageService.store('audio_recording_history', this.recordingHistory, {
        priority: 5,
        encrypted: true
      });
    } catch (error) {
      console.error('Failed to save recording history:', error);
    }
  }

  private async loadProcessorSettings(): Promise<void> {
    try {
      const result = await this.storageService.retrieve('audio_processor_settings');
      if (result.success) {
        this.audioProcessor = { ...this.audioProcessor, ...result.data };
      }
    } catch (error) {
      console.warn('Failed to load processor settings:', error);
    }
  }

  /**
   * Update audio processor settings
   */
  public async updateProcessorSettings(settings: Partial<AudioProcessor>): Promise<ServiceResponse<boolean>> {
    try {
      this.audioProcessor = { ...this.audioProcessor, ...settings };
      await this.storageService.store('audio_processor_settings', this.audioProcessor);
      return formatServiceResponse(true);
    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'updateProcessorSettings');
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Delete recording
   */
  public async deleteRecording(recordingId: string): Promise<ServiceResponse<boolean>> {
    try {
      const index = this.recordingHistory.findIndex(r => r.id === recordingId);
      if (index === -1) {
        return {
          success: false,
          error: 'Recording not found',
          timestamp: Date.now()
        };
      }

      // Remove from history
      this.recordingHistory.splice(index, 1);
      await this.saveRecordingHistory();

      // Delete from storage
      await this.storageService.remove(`recording_${recordingId}`);

      return formatServiceResponse(true);

    } catch (error) {
      const serviceError = handleServiceError(error, 'AudioService', 'deleteRecording', { recordingId });
      return {
        success: false,
        error: serviceError.message,
        timestamp: serviceError.timestamp
      };
    }
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    if (this.isRecording) {
      this.stopRecording();
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    if (this.mediaRecorder) {
      this.mediaRecorder = null;
    }

    this.recordingHistory = [];
    this.capabilities = [];
    this.activeSession = null;
  }
}

export default AudioService;