/**
 * Audio Service - Advanced audio recording and processing service
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

export interface AudioCapabilities {
  isSupported: boolean;
  inputDevices: AudioDevice[];
  outputDevices: AudioDevice[];
  supportedFormats: AudioFormat[];
  maxChannels: number;
  sampleRates: number[];
  features: AudioFeature[];
}

export interface AudioDevice {
  id: string;
  label: string;
  type: 'microphone' | 'speaker' | 'headphones' | 'bluetooth' | 'usb';
  channels: number;
  sampleRate: number;
  isDefault: boolean;
}

export interface AudioFormat {
  codec: string;
  mimeType: string;
  extension: string;
  quality: 'low' | 'medium' | 'high' | 'lossless';
  bitrate: number;
  sampleRate: number;
  channels: number;
}

export type AudioFeature = 'echoCancellation' | 'noiseSuppression' | 'autoGainControl' | 'spatialAudio' | 'beamforming' | 'processing';

export interface RecordingOptions {
  deviceId?: string;
  quality: 'low' | 'medium' | 'high' | 'studio';
  format?: string;
  sampleRate?: number;
  channels?: number;
  bitrate?: number;
  duration?: number; // max duration in seconds
  echoCancellation?: boolean;
  noiseSuppression?: boolean;
  autoGainControl?: boolean;
  volume?: number; // 0.0 to 1.0
  monitoring?: boolean; // real-time monitoring
  effects?: AudioEffect[];
  metadata?: {
    title?: string;
    artist?: string;
    genre?: string;
    tags?: string[];
  };
}

export interface AudioEffect {
  type: 'reverb' | 'echo' | 'compressor' | 'equalizer' | 'distortion' | 'filter' | 'pitch' | 'tempo';
  enabled: boolean;
  parameters: Record<string, number>;
}

export interface RecordingResult {
  success: boolean;
  file?: AudioFile;
  error?: string;
  metadata?: AudioMetadata;
}

export interface AudioFile {
  id: string;
  blob: Blob;
  url: string;
  filename: string;
  size: number;
  mimeType: string;
  duration: number;
  createdAt: number;
  waveform?: number[]; // Waveform data for visualization
  peaks?: number[]; // Peak data for waveform
}

export interface AudioMetadata {
  duration: number;
  sampleRate: number;
  channels: number;
  bitrate: number;
  format: string;
  fileSize: number;
  recordingDevice: string;
  timestamp: number;
  fingerprint?: string;
  musicFeatures?: {
    tempo?: number;
    key?: string;
    loudness?: number;
    energy?: number;
    danceability?: number;
    valence?: number;
  };
}

export interface AudioAnalysis {
  waveform: number[];
  spectrum: number[];
  peaks: number[];
  volume: number;
  frequency: number;
  tempo?: number;
  pitch?: number;
  silence: { start: number; end: number }[];
  clips: { start: number; end: number }[];
}

export interface PlaybackOptions {
  startTime?: number;
  endTime?: number;
  loop?: boolean;
  volume?: number;
  playbackRate?: number;
  effects?: AudioEffect[];
  crossfade?: number; // seconds
}

export interface AudioProcessingOptions {
  normalize?: boolean;
  trim?: { start: number; end: number };
  fade?: { in: number; out: number };
  gain?: number; // dB
  effects?: AudioEffect[];
  quality?: 'low' | 'medium' | 'high' | 'studio';
  format?: string;
}

export class AudioService {
  private isInitialized: boolean = false;
  private capabilities: AudioCapabilities;
  private mediaRecorder: MediaRecorder | null = null;
  private currentStream: MediaStream | null = null;
  private isRecording: boolean = false;
  private recordingStartTime: number = 0;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private audioFiles: Map<string, AudioFile> = new Map();
  private currentPlayback: HTMLAudioElement | null = null;
  private defaultSettings: RecordingOptions;
  private visualizationData: { waveform: number[]; spectrum: number[] } = { waveform: [], spectrum: [] };

  constructor() {
    this.capabilities = {
      isSupported: false,
      inputDevices: [],
      outputDevices: [],
      supportedFormats: [],
      maxChannels: 2,
      sampleRates: [],
      features: [],
    };

    this.defaultSettings = {
      quality: 'high',
      sampleRate: 44100,
      channels: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
      volume: 1.0,
      monitoring: false,
      effects: [],
    };

    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    try {
      // Check for audio API support
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('Audio API not supported');
        return;
      }

      // Initialize Web Audio API
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Detect audio capabilities
      await this.detectCapabilities();
      
      // Load settings
      await this.loadSettings();
      
      // Setup audio event handlers
      this.setupAudioHandlers();
      
      this.isInitialized = true;
      console.log('Audio Service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Audio Service:', error);
    }
  }

  // Public API Methods
  async requestPermissions(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Stop the stream immediately, we just needed permission
      stream.getTracks().forEach(track => track.stop());
      
      return true;
    } catch (error) {
      console.error('Audio permission denied:', error);
      return false;
    }
  }

  getCapabilities(): AudioCapabilities {
    return { ...this.capabilities };
  }

  async getAudioDevices(): Promise<{ input: AudioDevice[]; output: AudioDevice[] }> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      
      const input = devices
        .filter(device => device.kind === 'audioinput')
        .map(device => this.createAudioDevice(device, 'microphone'));
      
      const output = devices
        .filter(device => device.kind === 'audiooutput')
        .map(device => this.createAudioDevice(device, 'speaker'));
      
      return { input, output };
    } catch (error) {
      console.error('Failed to get audio devices:', error);
      return { input: [], output: [] };
    }
  }

  // Recording Operations
  async startRecording(options?: RecordingOptions): Promise<RecordingResult> {
    try {
      if (!this.capabilities.isSupported) {
        return { success: false, error: 'Audio recording not supported' };
      }

      if (this.isRecording) {
        return { success: false, error: 'Already recording' };
      }

      const recordOptions = { ...this.defaultSettings, ...options };
      
      // Start audio stream
      const stream = await this.startAudioStream(recordOptions);
      this.currentStream = stream;
      
      // Setup audio context and analyser for real-time processing
      await this.setupAudioProcessing(stream, recordOptions);
      
      // Setup media recorder
      const mimeType = this.getBestAudioMimeType();
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: recordOptions.bitrate || this.getBitrateForQuality(recordOptions.quality),
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
        const audioFile = await this.createAudioFile(blob, recordOptions);
        
        // Process audio file
        const processedFile = await this.processRecordedAudio(audioFile, recordOptions);
        
        // Generate metadata
        const metadata = await this.generateAudioMetadata(processedFile, recordOptions);
        
        // Save file
        this.audioFiles.set(processedFile.id, processedFile);
        
        // Emit recording complete event
        this.emitRecordingEvent('completed', { file: processedFile, metadata });
      };

      // Start recording
      mediaRecorder.start(100); // 100ms chunks for better real-time processing
      this.isRecording = true;
      this.recordingStartTime = Date.now();
      
      // Set duration limit if specified
      if (recordOptions.duration) {
        setTimeout(() => {
          this.stopRecording();
        }, recordOptions.duration * 1000);
      }

      // Start real-time analysis
      this.startRealtimeAnalysis();

      this.emitRecordingEvent('started', { options: recordOptions });

      return { success: true };

    } catch (error) {
      console.error('Recording start failed:', error);
      return { success: false, error: error.message };
    }
  }

  async stopRecording(): Promise<RecordingResult> {
    try {
      if (!this.isRecording || !this.mediaRecorder) {
        return { success: false, error: 'Not recording' };
      }

      this.mediaRecorder.stop();
      this.isRecording = false;
      this.recordingStartTime = 0;
      
      if (this.currentStream) {
        this.stopAudioStream(this.currentStream);
        this.currentStream = null;
      }

      this.stopRealtimeAnalysis();
      this.emitRecordingEvent('stopped');

      return { success: true };
    } catch (error) {
      console.error('Recording stop failed:', error);
      return { success: false, error: error.message };
    }
  }

  async pauseRecording(): Promise<boolean> {
    if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.pause();
      this.emitRecordingEvent('paused');
      return true;
    }
    return false;
  }

  async resumeRecording(): Promise<boolean> {
    if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state === 'paused') {
      this.mediaRecorder.resume();
      this.emitRecordingEvent('resumed');
      return true;
    }
    return false;
  }

  getRecordingStatus(): { isRecording: boolean; duration: number; state?: string; volume?: number } {
    return {
      isRecording: this.isRecording,
      duration: this.isRecording ? (Date.now() - this.recordingStartTime) / 1000 : 0,
      state: this.mediaRecorder?.state,
      volume: this.getCurrentVolume(),
    };
  }

  // Playback Operations
  async playAudio(fileId: string, options?: PlaybackOptions): Promise<boolean> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) {
        console.error('Audio file not found:', fileId);
        return false;
      }

      // Stop current playback
      if (this.currentPlayback) {
        this.currentPlayback.pause();
      }

      // Create audio element
      const audio = new Audio(audioFile.url);
      this.currentPlayback = audio;

      // Apply playback options
      if (options) {
        audio.currentTime = options.startTime || 0;
        audio.volume = options.volume !== undefined ? options.volume : 1.0;
        audio.playbackRate = options.playbackRate || 1.0;
        audio.loop = options.loop || false;
      }

      // Setup audio context for effects if needed
      if (options?.effects && options.effects.length > 0) {
        await this.setupPlaybackEffects(audio, options.effects);
      }

      // Play audio
      await audio.play();
      
      // Handle end time
      if (options?.endTime) {
        setTimeout(() => {
          audio.pause();
        }, (options.endTime - (options.startTime || 0)) * 1000);
      }

      return true;
    } catch (error) {
      console.error('Audio playback failed:', error);
      return false;
    }
  }

  async stopPlayback(): Promise<void> {
    if (this.currentPlayback) {
      this.currentPlayback.pause();
      this.currentPlayback.currentTime = 0;
      this.currentPlayback = null;
    }
  }

  async pausePlayback(): Promise<void> {
    if (this.currentPlayback) {
      this.currentPlayback.pause();
    }
  }

  async resumePlayback(): Promise<void> {
    if (this.currentPlayback) {
      await this.currentPlayback.play();
    }
  }

  getPlaybackStatus(): { isPlaying: boolean; currentTime: number; duration: number; volume: number } {
    if (!this.currentPlayback) {
      return { isPlaying: false, currentTime: 0, duration: 0, volume: 0 };
    }

    return {
      isPlaying: !this.currentPlayback.paused,
      currentTime: this.currentPlayback.currentTime,
      duration: this.currentPlayback.duration || 0,
      volume: this.currentPlayback.volume,
    };
  }

  // Audio Processing
  async processAudio(fileId: string, options: AudioProcessingOptions): Promise<RecordingResult> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) {
        return { success: false, error: 'Audio file not found' };
      }

      const processedFile = await this.applyAudioProcessing(audioFile, options);
      
      // Save processed version
      const newFileId = `${fileId}_processed_${Date.now()}`;
      const newFile = { ...processedFile, id: newFileId };
      this.audioFiles.set(newFileId, newFile);

      return { success: true, file: newFile };
    } catch (error) {
      console.error('Audio processing failed:', error);
      return { success: false, error: error.message };
    }
  }

  async analyzeAudio(fileId: string): Promise<AudioAnalysis | null> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) return null;

      return await this.performAudioAnalysis(audioFile);
    } catch (error) {
      console.error('Audio analysis failed:', error);
      return null;
    }
  }

  async generateWaveform(fileId: string, samples: number = 1000): Promise<number[]> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) return [];

      return await this.extractWaveform(audioFile, samples);
    } catch (error) {
      console.error('Waveform generation failed:', error);
      return [];
    }
  }

  // Real-time Analysis
  getVisualizationData(): { waveform: number[]; spectrum: number[] } {
    return { ...this.visualizationData };
  }

  getCurrentVolume(): number {
    if (!this.analyser) return 0;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    // Calculate RMS volume
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    return Math.sqrt(sum / bufferLength) / 255;
  }

  // File Management
  getAudioFiles(): AudioFile[] {
    return Array.from(this.audioFiles.values());
  }

  async saveToLibrary(fileId: string): Promise<boolean> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) return false;

      // Save to device storage
      if ('showSaveFilePicker' in window) {
        const fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: audioFile.filename,
          types: [{
            description: 'Audio Files',
            accept: { [audioFile.mimeType]: [`.${audioFile.filename.split('.').pop()}`] },
          }],
        });

        const writable = await fileHandle.createWritable();
        await writable.write(audioFile.blob);
        await writable.close();
      } else {
        // Fallback: trigger download
        const url = URL.createObjectURL(audioFile.blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = audioFile.filename;
        a.click();
        URL.revokeObjectURL(url);
      }

      return true;
    } catch (error) {
      console.error('Save to library failed:', error);
      return false;
    }
  }

  async deleteAudioFile(fileId: string): Promise<boolean> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (audioFile) {
        // Revoke blob URL
        if (audioFile.url) {
          URL.revokeObjectURL(audioFile.url);
        }
        
        // Remove from storage
        this.audioFiles.delete(fileId);
        
        // Remove from offline storage
        await offlineStorageService.remove(`audio_file_${fileId}`);
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Delete audio file failed:', error);
      return false;
    }
  }

  // Music Business Integration
  async uploadForProtection(fileId: string): Promise<{ success: boolean; fingerprintId?: string; error?: string }> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) {
        return { success: false, error: 'Audio file not found' };
      }

      // Generate audio fingerprint
      const fingerprint = await this.generateAudioFingerprint(audioFile);
      
      // Generate metadata
      const metadata = await this.generateAudioMetadata(audioFile, {});
      
      // Upload to content protection system
      const response = await mobileAPIService.uploadContent(
        {
          contentId: audioFile.id,
          type: 'audio',
          size: audioFile.size,
          duration: audioFile.duration,
          format: audioFile.mimeType,
          quality: 'high',
          timestamp: audioFile.createdAt,
          fingerprint,
        },
        audioFile.blob
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

  async generateMusicAnalysis(fileId: string): Promise<AudioMetadata['musicFeatures'] | null> {
    try {
      const audioFile = this.audioFiles.get(fileId);
      if (!audioFile) return null;

      // Analyze musical features using Web Audio API
      const musicFeatures = await this.analyzeMusicFeatures(audioFile);
      
      return musicFeatures;
    } catch (error) {
      console.error('Music analysis failed:', error);
      return null;
    }
  }

  // Private Methods
  private async detectCapabilities(): Promise<void> {
    try {
      if (!navigator.mediaDevices) return;

      this.capabilities.isSupported = true;
      
      // Get available devices
      const devices = await this.getAudioDevices();
      this.capabilities.inputDevices = devices.input;
      this.capabilities.outputDevices = devices.output;
      
      // Detect supported formats
      this.capabilities.supportedFormats = this.getSupportedFormats();
      
      // Detect features
      this.capabilities.features = this.getSupportedFeatures();
      
      // Detect sample rates and channels
      this.capabilities.sampleRates = [8000, 16000, 22050, 44100, 48000, 96000];
      this.capabilities.maxChannels = 2;
      
    } catch (error) {
      console.error('Capability detection failed:', error);
    }
  }

  private createAudioDevice(device: MediaDeviceInfo, type: AudioDevice['type']): AudioDevice {
    return {
      id: device.deviceId,
      label: device.label || `${type} ${device.deviceId.substring(0, 8)}`,
      type,
      channels: type === 'microphone' ? 1 : 2,
      sampleRate: 44100,
      isDefault: device.deviceId === 'default',
    };
  }

  private getSupportedFormats(): AudioFormat[] {
    const formats: AudioFormat[] = [];
    
    // Check audio formats
    if (MediaRecorder.isTypeSupported('audio/mp4; codecs="mp4a.40.2"')) {
      formats.push({
        codec: 'aac',
        mimeType: 'audio/mp4',
        extension: 'mp4',
        quality: 'high',
        bitrate: 128000,
        sampleRate: 44100,
        channels: 2,
      });
    }
    
    if (MediaRecorder.isTypeSupported('audio/webm; codecs="opus"')) {
      formats.push({
        codec: 'opus',
        mimeType: 'audio/webm',
        extension: 'webm',
        quality: 'high',
        bitrate: 128000,
        sampleRate: 48000,
        channels: 2,
      });
    }
    
    if (MediaRecorder.isTypeSupported('audio/wav')) {
      formats.push({
        codec: 'pcm',
        mimeType: 'audio/wav',
        extension: 'wav',
        quality: 'lossless',
        bitrate: 1411200, // 16-bit 44.1kHz stereo
        sampleRate: 44100,
        channels: 2,
      });
    }
    
    return formats;
  }

  private getSupportedFeatures(): AudioFeature[] {
    const features: AudioFeature[] = ['processing'];
    
    // Check for advanced audio features
    if (this.audioContext) {
      features.push('echoCancellation', 'noiseSuppression', 'autoGainControl');
    }
    
    return features;
  }

  private async startAudioStream(options: RecordingOptions): Promise<MediaStream> {
    const constraints: MediaStreamConstraints = {
      audio: {
        deviceId: options.deviceId ? { exact: options.deviceId } : undefined,
        sampleRate: options.sampleRate || 44100,
        channelCount: options.channels || 1,
        echoCancellation: options.echoCancellation !== false,
        noiseSuppression: options.noiseSuppression !== false,
        autoGainControl: options.autoGainControl !== false,
        sampleSize: 16,
      },
    };

    return navigator.mediaDevices.getUserMedia(constraints);
  }

  private async setupAudioProcessing(stream: MediaStream, options: RecordingOptions): Promise<void> {
    if (!this.audioContext) return;

    const source = this.audioContext.createMediaStreamSource(stream);
    
    // Create analyser for real-time analysis
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 2048;
    this.analyser.smoothingTimeConstant = 0.8;
    
    // Apply effects if specified
    let currentNode: AudioNode = source;
    
    if (options.effects && options.effects.length > 0) {
      for (const effect of options.effects) {
        if (effect.enabled) {
          const effectNode = await this.createEffectNode(effect);
          if (effectNode) {
            currentNode.connect(effectNode);
            currentNode = effectNode;
          }
        }
      }
    }
    
    // Connect to analyser
    currentNode.connect(this.analyser);
    
    // Connect to destination for monitoring if enabled
    if (options.monitoring) {
      const gainNode = this.audioContext.createGain();
      gainNode.gain.value = options.volume || 0.5;
      this.analyser.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
    }
  }

  private async createEffectNode(effect: AudioEffect): Promise<AudioNode | null> {
    if (!this.audioContext) return null;

    switch (effect.type) {
      case 'reverb':
        return this.createReverbNode(effect.parameters);
      case 'echo':
        return this.createEchoNode(effect.parameters);
      case 'compressor':
        return this.createCompressorNode(effect.parameters);
      case 'equalizer':
        return this.createEqualizerNode(effect.parameters);
      case 'filter':
        return this.createFilterNode(effect.parameters);
      default:
        return null;
    }
  }

  private createReverbNode(params: Record<string, number>): AudioNode {
    const convolver = this.audioContext!.createConvolver();
    // Create impulse response for reverb (simplified)
    const length = this.audioContext!.sampleRate * (params.roomSize || 2);
    const impulse = this.audioContext!.createBuffer(2, length, this.audioContext!.sampleRate);
    
    for (let channel = 0; channel < 2; channel++) {
      const channelData = impulse.getChannelData(channel);
      for (let i = 0; i < length; i++) {
        channelData[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, params.decay || 2);
      }
    }
    
    convolver.buffer = impulse;
    return convolver;
  }

  private createEchoNode(params: Record<string, number>): AudioNode {
    const delay = this.audioContext!.createDelay(1);
    delay.delayTime.value = params.delay || 0.3;
    
    const feedback = this.audioContext!.createGain();
    feedback.gain.value = params.feedback || 0.3;
    
    const wet = this.audioContext!.createGain();
    wet.gain.value = params.wet || 0.5;
    
    delay.connect(feedback);
    feedback.connect(delay);
    delay.connect(wet);
    
    return delay;
  }

  private createCompressorNode(params: Record<string, number>): AudioNode {
    const compressor = this.audioContext!.createDynamicsCompressor();
    compressor.threshold.value = params.threshold || -24;
    compressor.knee.value = params.knee || 30;
    compressor.ratio.value = params.ratio || 12;
    compressor.attack.value = params.attack || 0.003;
    compressor.release.value = params.release || 0.25;
    return compressor;
  }

  private createEqualizerNode(params: Record<string, number>): AudioNode {
    // Create a basic 3-band EQ
    const lowFilter = this.audioContext!.createBiquadFilter();
    lowFilter.type = 'lowshelf';
    lowFilter.frequency.value = 320;
    lowFilter.gain.value = params.low || 0;
    
    const midFilter = this.audioContext!.createBiquadFilter();
    midFilter.type = 'peaking';
    midFilter.frequency.value = 1000;
    midFilter.Q.value = 0.5;
    midFilter.gain.value = params.mid || 0;
    
    const highFilter = this.audioContext!.createBiquadFilter();
    highFilter.type = 'highshelf';
    highFilter.frequency.value = 3200;
    highFilter.gain.value = params.high || 0;
    
    lowFilter.connect(midFilter);
    midFilter.connect(highFilter);
    
    return lowFilter;
  }

  private createFilterNode(params: Record<string, number>): AudioNode {
    const filter = this.audioContext!.createBiquadFilter();
    filter.type = (params.type as BiquadFilterType) || 'lowpass';
    filter.frequency.value = params.frequency || 1000;
    filter.Q.value = params.q || 1;
    filter.gain.value = params.gain || 0;
    return filter;
  }

  private getBestAudioMimeType(): string {
    const types = [
      'audio/mp4; codecs="mp4a.40.2"',
      'audio/webm; codecs="opus"',
      'audio/wav',
      'audio/ogg; codecs="opus"',
    ];
    
    return types.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';
  }

  private getBitrateForQuality(quality: string): number {
    const bitrates = {
      low: 64000,    // 64 kbps
      medium: 128000, // 128 kbps
      high: 192000,   // 192 kbps
      studio: 320000, // 320 kbps
    };
    
    return bitrates[quality as keyof typeof bitrates] || 128000;
  }

  private async createAudioFile(blob: Blob, options: RecordingOptions): Promise<AudioFile> {
    const id = `audio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const extension = this.getExtensionFromMimeType(blob.type);
    const filename = options.metadata?.title 
      ? `${options.metadata.title}.${extension}`
      : `${id}.${extension}`;
    
    const url = URL.createObjectURL(blob);
    const duration = await this.getAudioDuration(blob);
    
    return {
      id,
      blob,
      url,
      filename,
      size: blob.size,
      mimeType: blob.type,
      duration,
      createdAt: Date.now(),
    };
  }

  private async processRecordedAudio(audioFile: AudioFile, options: RecordingOptions): Promise<AudioFile> {
    // Apply post-recording processing
    let processedBlob = audioFile.blob;
    
    // Apply effects if specified
    if (options.effects && options.effects.length > 0) {
      processedBlob = await this.applyEffectsToBlob(processedBlob, options.effects);
    }
    
    // Generate waveform data
    const waveform = await this.extractWaveform(audioFile, 1000);
    
    // Save file for offline access
    await offlineStorageService.store(`audio_file_${audioFile.id}`, {
      ...audioFile,
      blob: undefined, // Don't store blob directly
      waveform,
    });
    
    return { ...audioFile, blob: processedBlob, waveform };
  }

  private async generateAudioMetadata(audioFile: AudioFile, options: RecordingOptions): Promise<AudioMetadata> {
    const metadata: AudioMetadata = {
      duration: audioFile.duration,
      sampleRate: 44100, // Would be detected in real implementation
      channels: 1, // Would be detected in real implementation
      bitrate: this.getBitrateForQuality(options.quality || 'high'),
      format: audioFile.mimeType,
      fileSize: audioFile.size,
      recordingDevice: options.deviceId || 'default',
      timestamp: audioFile.createdAt,
    };
    
    // Generate audio fingerprint
    metadata.fingerprint = await this.generateAudioFingerprint(audioFile);
    
    // Analyze music features if applicable
    if (audioFile.duration > 10) { // Only for longer recordings
      metadata.musicFeatures = await this.analyzeMusicFeatures(audioFile);
    }
    
    return metadata;
  }

  private stopAudioStream(stream: MediaStream): void {
    stream.getTracks().forEach(track => track.stop());
  }

  private startRealtimeAnalysis(): void {
    if (!this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const waveformData = new Uint8Array(bufferLength);
    const spectrumData = new Uint8Array(bufferLength);

    const updateVisualization = () => {
      if (!this.isRecording || !this.analyser) return;

      this.analyser.getByteTimeDomainData(waveformData);
      this.analyser.getByteFrequencyData(spectrumData);

      // Normalize data for visualization
      this.visualizationData.waveform = Array.from(waveformData).map(value => (value - 128) / 128);
      this.visualizationData.spectrum = Array.from(spectrumData).map(value => value / 255);

      requestAnimationFrame(updateVisualization);
    };

    updateVisualization();
  }

  private stopRealtimeAnalysis(): void {
    this.visualizationData = { waveform: [], spectrum: [] };
  }

  private async setupPlaybackEffects(audio: HTMLAudioElement, effects: AudioEffect[]): Promise<void> {
    if (!this.audioContext) return;

    const source = this.audioContext.createMediaElementSource(audio);
    let currentNode: AudioNode = source;

    for (const effect of effects) {
      if (effect.enabled) {
        const effectNode = await this.createEffectNode(effect);
        if (effectNode) {
          currentNode.connect(effectNode);
          currentNode = effectNode;
        }
      }
    }

    currentNode.connect(this.audioContext.destination);
  }

  private async applyAudioProcessing(audioFile: AudioFile, options: AudioProcessingOptions): Promise<AudioFile> {
    // In a real implementation, this would apply audio processing using Web Audio API
    // For now, return the original file
    return audioFile;
  }

  private async performAudioAnalysis(audioFile: AudioFile): Promise<AudioAnalysis> {
    // In a real implementation, this would perform comprehensive audio analysis
    const analysis: AudioAnalysis = {
      waveform: audioFile.waveform || [],
      spectrum: [],
      peaks: [],
      volume: 0.5,
      frequency: 440,
      silence: [],
      clips: [],
    };

    return analysis;
  }

  private async extractWaveform(audioFile: AudioFile, samples: number): Promise<number[]> {
    if (!this.audioContext) return [];

    try {
      const arrayBuffer = await audioFile.blob.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      
      const channelData = audioBuffer.getChannelData(0);
      const blockSize = Math.floor(channelData.length / samples);
      const waveform: number[] = [];
      
      for (let i = 0; i < samples; i++) {
        const start = i * blockSize;
        const end = start + blockSize;
        let sum = 0;
        
        for (let j = start; j < end; j++) {
          sum += Math.abs(channelData[j]);
        }
        
        waveform.push(sum / blockSize);
      }
      
      return waveform;
    } catch (error) {
      console.error('Waveform extraction failed:', error);
      return [];
    }
  }

  private async generateAudioFingerprint(audioFile: AudioFile): Promise<string> {
    // Generate a basic audio fingerprint for content protection
    const arrayBuffer = await audioFile.blob.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private async analyzeMusicFeatures(audioFile: AudioFile): Promise<AudioMetadata['musicFeatures']> {
    // In a real implementation, this would use advanced audio analysis
    // For now, return mock data
    return {
      tempo: 120 + Math.random() * 60,
      key: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][Math.floor(Math.random() * 12)],
      loudness: -10 + Math.random() * 20,
      energy: Math.random(),
      danceability: Math.random(),
      valence: Math.random(),
    };
  }

  private async getAudioDuration(blob: Blob): Promise<number> {
    return new Promise((resolve) => {
      const audio = new Audio();
      audio.onloadedmetadata = () => {
        resolve(audio.duration);
      };
      audio.onerror = () => resolve(0);
      audio.src = URL.createObjectURL(blob);
    });
  }

  private getExtensionFromMimeType(mimeType: string): string {
    const extensions: Record<string, string> = {
      'audio/mp4': 'mp4',
      'audio/webm': 'webm',
      'audio/wav': 'wav',
      'audio/ogg': 'ogg',
      'audio/mpeg': 'mp3',
    };
    
    return extensions[mimeType] || 'audio';
  }

  private async applyEffectsToBlob(blob: Blob, effects: AudioEffect[]): Promise<Blob> {
    // In a real implementation, this would apply effects to the audio blob
    return blob;
  }

  private emitRecordingEvent(type: string, data?: any): void {
    const event = new CustomEvent(`audio-recording-${type}`, { detail: data });
    window.dispatchEvent(event);
  }

  private setupAudioHandlers(): void {
    // Handle audio context state changes
    if (this.audioContext) {
      this.audioContext.addEventListener('statechange', () => {
        if (this.audioContext!.state === 'suspended') {
          // Resume audio context on user interaction
          document.addEventListener('click', () => {
            this.audioContext!.resume();
          }, { once: true });
        }
      });
    }

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.isRecording) {
        // Continue recording in background (mobile-specific behavior)
        console.log('Recording continues in background');
      }
    });
  }

  private async loadSettings(): Promise<void> {
    const stored = await offlineStorageService.retrieve('audio_settings');
    if (stored) {
      this.defaultSettings = { ...this.defaultSettings, ...stored };
    }
  }
}

// Export singleton instance
export const audioService = new AudioService();