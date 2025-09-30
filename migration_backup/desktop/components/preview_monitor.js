/**
 * Ainflue Desktop - Preview Monitor Component
 * 
 * Professional content preview system with real-time rendering and multi-format support
 * Provides high-quality preview capabilities for video, audio, and image content
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const log = require('electron-log');

class PreviewMonitor extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      previewQuality: 'high',
      maxPreviewSize: { width: 1920, height: 1080 },
      enableRealTime: true,
      enableFilters: true,
      enableColorCorrection: true,
      enableAudioMeter: true,
      bufferSize: 4096,
      frameRate: 30,
      ...options
    };

    this.currentMedia = null;
    this.isPlaying = false;
    this.currentTime = 0;
    this.duration = 0;
    this.volume = 1.0;
    this.playbackRate = 1.0;
    this.filters = new Map();
    this.canvas = null;
    this.context = null;
    this.audioContext = null;
    this.audioAnalyzer = null;
    this.previewHistory = [];
    
    // Preview states
    this.states = {
      IDLE: 'idle',
      LOADING: 'loading',
      PLAYING: 'playing',
      PAUSED: 'paused',
      SEEKING: 'seeking',
      ERROR: 'error'
    };
    
    this.currentState = this.states.IDLE;
    this.initializePreviewEngine();
  }

  /**
   * Initialize the preview engine with canvas and audio contexts
   */
  async initializePreviewEngine() {
    try {
      // Initialize audio context for audio analysis
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.audioAnalyzer = this.audioContext.createAnalyser();
      this.audioAnalyzer.fftSize = 2048;
      
      // Setup canvas for video preview
      this.setupCanvas();
      
      // Initialize filter engine
      this.initializeFilters();
      
      log.info('Preview monitor engine initialized successfully');
      this.emit('initialized');
    } catch (error) {
      log.error('Failed to initialize preview engine:', error);
      this.emit('error', error);
    }
  }

  /**
   * Setup canvas for video rendering
   */
  setupCanvas() {
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.options.maxPreviewSize.width;
    this.canvas.height = this.options.maxPreviewSize.height;
    this.context = this.canvas.getContext('2d');
    
    // Setup WebGL context for hardware acceleration if available
    try {
      this.glContext = this.canvas.getContext('webgl2') || this.canvas.getContext('webgl');
      if (this.glContext) {
        log.info('WebGL acceleration enabled for preview');
      }
    } catch (error) {
      log.warn('WebGL not available, using 2D context');
    }
  }

  /**
   * Initialize filter engine with professional filters
   */
  initializeFilters() {
    const filterDefinitions = {
      brightness: { min: -100, max: 100, default: 0 },
      contrast: { min: -100, max: 100, default: 0 },
      saturation: { min: -100, max: 100, default: 0 },
      hue: { min: -180, max: 180, default: 0 },
      gamma: { min: 0.1, max: 3.0, default: 1.0 },
      exposure: { min: -3, max: 3, default: 0 },
      highlights: { min: -100, max: 100, default: 0 },
      shadows: { min: -100, max: 100, default: 0 },
      vibrance: { min: -100, max: 100, default: 0 },
      temperature: { min: -100, max: 100, default: 0 },
      tint: { min: -100, max: 100, default: 0 }
    };

    for (const [name, config] of Object.entries(filterDefinitions)) {
      this.filters.set(name, {
        ...config,
        value: config.default,
        enabled: false
      });
    }
  }

  /**
   * Load media file for preview
   */
  async loadMedia(mediaPath, metadata = {}) {
    try {
      this.setState(this.states.LOADING);
      
      const mediaInfo = await this.analyzeMedia(mediaPath);
      
      this.currentMedia = {
        path: mediaPath,
        metadata: { ...metadata, ...mediaInfo },
        type: this.detectMediaType(mediaPath),
        duration: mediaInfo.duration || 0,
        size: mediaInfo.size || { width: 0, height: 0 },
        frameRate: mediaInfo.frameRate || 30,
        audioChannels: mediaInfo.audioChannels || 2,
        bitRate: mediaInfo.bitRate || 0
      };

      this.duration = this.currentMedia.duration;
      this.currentTime = 0;
      
      // Load media based on type
      await this.loadMediaContent();
      
      this.setState(this.states.IDLE);
      this.emit('mediaLoaded', this.currentMedia);
      
      log.info(`Media loaded successfully: ${mediaPath}`);
    } catch (error) {
      this.setState(this.states.ERROR);
      log.error('Failed to load media:', error);
      this.emit('error', error);
    }
  }

  /**
   * Load media content based on type
   */
  async loadMediaContent() {
    if (!this.currentMedia) return;

    switch (this.currentMedia.type) {
      case 'video':
        await this.loadVideoContent();
        break;
      case 'audio':
        await this.loadAudioContent();
        break;
      case 'image':
        await this.loadImageContent();
        break;
      default:
        throw new Error(`Unsupported media type: ${this.currentMedia.type}`);
    }
  }

  /**
   * Load video content for preview
   */
  async loadVideoContent() {
    return new Promise((resolve, reject) => {
      this.videoElement = document.createElement('video');
      this.videoElement.src = this.currentMedia.path;
      this.videoElement.preload = 'metadata';
      
      this.videoElement.addEventListener('loadedmetadata', () => {
        this.duration = this.videoElement.duration;
        this.setupVideoAudio();
        resolve();
      });
      
      this.videoElement.addEventListener('error', reject);
    });
  }

  /**
   * Load audio content for preview
   */
  async loadAudioContent() {
    return new Promise((resolve, reject) => {
      this.audioElement = document.createElement('audio');
      this.audioElement.src = this.currentMedia.path;
      this.audioElement.preload = 'metadata';
      
      this.audioElement.addEventListener('loadedmetadata', () => {
        this.duration = this.audioElement.duration;
        this.setupAudioAnalysis();
        resolve();
      });
      
      this.audioElement.addEventListener('error', reject);
    });
  }

  /**
   * Load image content for preview
   */
  async loadImageContent() {
    return new Promise((resolve, reject) => {
      this.imageElement = new Image();
      this.imageElement.onload = () => {
        this.renderImageToCanvas();
        resolve();
      };
      this.imageElement.onerror = reject;
      this.imageElement.src = this.currentMedia.path;
    });
  }

  /**
   * Setup audio analysis for video content
   */
  setupVideoAudio() {
    if (this.audioContext && this.videoElement) {
      const source = this.audioContext.createMediaElementSource(this.videoElement);
      source.connect(this.audioAnalyzer);
      this.audioAnalyzer.connect(this.audioContext.destination);
    }
  }

  /**
   * Setup audio analysis for audio content
   */
  setupAudioAnalysis() {
    if (this.audioContext && this.audioElement) {
      const source = this.audioContext.createMediaElementSource(this.audioElement);
      source.connect(this.audioAnalyzer);
      this.audioAnalyzer.connect(this.audioContext.destination);
    }
  }

  /**
   * Render image to canvas with filters
   */
  renderImageToCanvas() {
    if (!this.context || !this.imageElement) return;

    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Apply filters
    this.applyFilters();
    
    // Draw image
    this.context.drawImage(
      this.imageElement,
      0, 0,
      this.canvas.width,
      this.canvas.height
    );
  }

  /**
   * Play media content
   */
  async play() {
    try {
      if (!this.currentMedia) {
        throw new Error('No media loaded');
      }

      this.setState(this.states.PLAYING);
      this.isPlaying = true;

      if (this.videoElement) {
        await this.videoElement.play();
        this.startVideoRender();
      } else if (this.audioElement) {
        await this.audioElement.play();
        this.startAudioVisualization();
      }

      this.startTimeUpdate();
      this.emit('play');
      
      log.info('Preview playback started');
    } catch (error) {
      this.setState(this.states.ERROR);
      log.error('Failed to start playback:', error);
      this.emit('error', error);
    }
  }

  /**
   * Pause media playback
   */
  pause() {
    this.setState(this.states.PAUSED);
    this.isPlaying = false;

    if (this.videoElement) {
      this.videoElement.pause();
    }
    if (this.audioElement) {
      this.audioElement.pause();
    }

    this.stopTimeUpdate();
    this.emit('pause');
    
    log.info('Preview playback paused');
  }

  /**
   * Stop media playback
   */
  stop() {
    this.setState(this.states.IDLE);
    this.isPlaying = false;
    this.currentTime = 0;

    if (this.videoElement) {
      this.videoElement.pause();
      this.videoElement.currentTime = 0;
    }
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement.currentTime = 0;
    }

    this.stopTimeUpdate();
    this.emit('stop');
    
    log.info('Preview playback stopped');
  }

  /**
   * Seek to specific time
   */
  async seek(time) {
    try {
      this.setState(this.states.SEEKING);
      
      const clampedTime = Math.max(0, Math.min(time, this.duration));
      this.currentTime = clampedTime;

      if (this.videoElement) {
        this.videoElement.currentTime = clampedTime;
      }
      if (this.audioElement) {
        this.audioElement.currentTime = clampedTime;
      }

      this.setState(this.isPlaying ? this.states.PLAYING : this.states.PAUSED);
      this.emit('seek', clampedTime);
      
      log.info(`Seeked to time: ${clampedTime}`);
    } catch (error) {
      log.error('Failed to seek:', error);
      this.emit('error', error);
    }
  }

  /**
   * Set playback volume
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    
    if (this.videoElement) {
      this.videoElement.volume = this.volume;
    }
    if (this.audioElement) {
      this.audioElement.volume = this.volume;
    }

    this.emit('volumeChanged', this.volume);
  }

  /**
   * Set playback rate
   */
  setPlaybackRate(rate) {
    this.playbackRate = Math.max(0.25, Math.min(4, rate));
    
    if (this.videoElement) {
      this.videoElement.playbackRate = this.playbackRate;
    }
    if (this.audioElement) {
      this.audioElement.playbackRate = this.playbackRate;
    }

    this.emit('playbackRateChanged', this.playbackRate);
  }

  /**
   * Apply filter to preview
   */
  setFilter(filterName, value, enabled = true) {
    if (this.filters.has(filterName)) {
      const filter = this.filters.get(filterName);
      filter.value = Math.max(filter.min, Math.min(filter.max, value));
      filter.enabled = enabled;
      
      this.applyFilters();
      this.emit('filterChanged', filterName, filter);
    }
  }

  /**
   * Apply all active filters
   */
  applyFilters() {
    if (!this.context) return;

    let filterString = '';
    
    for (const [name, filter] of this.filters) {
      if (filter.enabled) {
        switch (name) {
          case 'brightness':
            filterString += `brightness(${100 + filter.value}%) `;
            break;
          case 'contrast':
            filterString += `contrast(${100 + filter.value}%) `;
            break;
          case 'saturation':
            filterString += `saturate(${100 + filter.value}%) `;
            break;
          case 'hue':
            filterString += `hue-rotate(${filter.value}deg) `;
            break;
        }
      }
    }

    this.context.filter = filterString;
  }

  /**
   * Start video rendering loop
   */
  startVideoRender() {
    if (!this.videoElement || !this.context) return;

    const renderFrame = () => {
      if (this.isPlaying && !this.videoElement.paused) {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.applyFilters();
        this.context.drawImage(
          this.videoElement,
          0, 0,
          this.canvas.width,
          this.canvas.height
        );
        
        this.renderOverlays();
        requestAnimationFrame(renderFrame);
      }
    };

    requestAnimationFrame(renderFrame);
  }

  /**
   * Start audio visualization
   */
  startAudioVisualization() {
    if (!this.audioAnalyzer || !this.context) return;

    const bufferLength = this.audioAnalyzer.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const visualize = () => {
      if (this.isPlaying) {
        this.audioAnalyzer.getByteFrequencyData(dataArray);
        this.renderAudioVisualization(dataArray);
        requestAnimationFrame(visualize);
      }
    };

    requestAnimationFrame(visualize);
  }

  /**
   * Render audio visualization
   */
  renderAudioVisualization(dataArray) {
    if (!this.context) return;

    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    const barWidth = this.canvas.width / dataArray.length * 2;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * this.canvas.height;
      
      this.context.fillStyle = `hsl(${i / dataArray.length * 360}, 100%, 50%)`;
      this.context.fillRect(x, this.canvas.height - barHeight, barWidth, barHeight);
      
      x += barWidth + 1;
    }
  }

  /**
   * Render overlays (timecode, waveform, etc.)
   */
  renderOverlays() {
    if (!this.context) return;

    // Render timecode
    this.renderTimecode();
    
    // Render audio levels if available
    if (this.audioAnalyzer) {
      this.renderAudioLevels();
    }
  }

  /**
   * Render timecode overlay
   */
  renderTimecode() {
    const timecode = this.formatTimecode(this.currentTime);
    
    this.context.save();
    this.context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    this.context.fillRect(10, 10, 120, 30);
    
    this.context.fillStyle = 'white';
    this.context.font = '16px monospace';
    this.context.fillText(timecode, 20, 30);
    this.context.restore();
  }

  /**
   * Render audio levels
   */
  renderAudioLevels() {
    if (!this.audioAnalyzer) return;

    const bufferLength = this.audioAnalyzer.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.audioAnalyzer.getByteFrequencyData(dataArray);

    // Calculate RMS level
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i] * dataArray[i];
    }
    const rms = Math.sqrt(sum / bufferLength);
    const level = (rms / 255) * 100;

    // Render level meter
    this.context.save();
    this.context.fillStyle = 'rgba(0, 0, 0, 0.7)';
    this.context.fillRect(this.canvas.width - 60, 10, 50, 200);
    
    // Level bar
    const barHeight = (level / 100) * 180;
    this.context.fillStyle = level > 80 ? 'red' : level > 60 ? 'yellow' : 'green';
    this.context.fillRect(this.canvas.width - 50, 190 - barHeight, 30, barHeight);
    this.context.restore();
  }

  /**
   * Start time update loop
   */
  startTimeUpdate() {
    this.timeUpdateInterval = setInterval(() => {
      if (this.isPlaying) {
        if (this.videoElement) {
          this.currentTime = this.videoElement.currentTime;
        } else if (this.audioElement) {
          this.currentTime = this.audioElement.currentTime;
        }
        
        this.emit('timeUpdate', this.currentTime);
        
        // Check for end of media
        if (this.currentTime >= this.duration) {
          this.stop();
          this.emit('ended');
        }
      }
    }, 1000 / this.options.frameRate);
  }

  /**
   * Stop time update loop
   */
  stopTimeUpdate() {
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval);
      this.timeUpdateInterval = null;
    }
  }

  /**
   * Format time as timecode
   */
  formatTimecode(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const frames = Math.floor((seconds % 1) * this.options.frameRate);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${frames.toString().padStart(2, '0')}`;
  }

  /**
   * Analyze media file to extract metadata
   */
  async analyzeMedia(mediaPath) {
    // This would integrate with FFmpeg or similar for real analysis
    // For now, returning mock data
    return {
      duration: 120,
      size: { width: 1920, height: 1080 },
      frameRate: 30,
      audioChannels: 2,
      bitRate: 5000000
    };
  }

  /**
   * Detect media type from file path
   */
  detectMediaType(mediaPath) {
    const ext = path.extname(mediaPath).toLowerCase();
    
    if (['.mp4', '.mov', '.avi', '.mkv', '.webm'].includes(ext)) {
      return 'video';
    } else if (['.mp3', '.wav', '.flac', '.aac', '.m4a'].includes(ext)) {
      return 'audio';
    } else if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(ext)) {
      return 'image';
    }
    
    return 'unknown';
  }

  /**
   * Set preview state
   */
  setState(state) {
    if (this.currentState !== state) {
      const previousState = this.currentState;
      this.currentState = state;
      this.emit('stateChanged', state, previousState);
    }
  }

  /**
   * Get current preview canvas
   */
  getCanvas() {
    return this.canvas;
  }

  /**
   * Get current media information
   */
  getCurrentMedia() {
    return this.currentMedia;
  }

  /**
   * Get current playback state
   */
  getState() {
    return {
      state: this.currentState,
      isPlaying: this.isPlaying,
      currentTime: this.currentTime,
      duration: this.duration,
      volume: this.volume,
      playbackRate: this.playbackRate
    };
  }

  /**
   * Export current frame as image
   */
  exportFrame(format = 'png') {
    if (!this.canvas) return null;
    
    return this.canvas.toDataURL(`image/${format}`);
  }

  /**
   * Clean up resources
   */
  destroy() {
    this.stop();
    this.stopTimeUpdate();
    
    if (this.audioContext) {
      this.audioContext.close();
    }
    
    if (this.videoElement) {
      this.videoElement.remove();
    }
    
    if (this.audioElement) {
      this.audioElement.remove();
    }
    
    this.removeAllListeners();
    log.info('Preview monitor destroyed');
  }
}

module.exports = PreviewMonitor;