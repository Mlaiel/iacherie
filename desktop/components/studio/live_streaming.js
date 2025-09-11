/**
 * Ainflue Desktop - Live Streaming Interface
 * 
 * Professional live streaming management for content creators
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');

class LiveStreaming extends EventEmitter {
  constructor() {
    super();
    this.isStreaming = false;
    this.streamConfig = null;
    this.platforms = new Map();
    this.analytics = {
      viewers: 0,
      duration: 0,
      bitrate: 0,
      fps: 0,
      dropped: 0
    };
    this.streamKey = null;
    this.rtmpUrl = null;
    
    this.initializePlatforms();
    this.setupStreamConfig();
  }

  /**
   * Initialize streaming platforms
   */
  initializePlatforms() {
    this.platforms.set('youtube', {
      name: 'YouTube Live',
      rtmpUrl: 'rtmp://a.rtmp.youtube.com/live2',
      maxBitrate: 51000,
      maxResolution: '4K',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['chat', 'analytics', 'scheduling', 'thumbnails']
    });

    this.platforms.set('twitch', {
      name: 'Twitch',
      rtmpUrl: 'rtmp://live.twitch.tv/app',
      maxBitrate: 8500,
      maxResolution: '1080p',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['chat', 'clips', 'raids', 'hosts']
    });

    this.platforms.set('facebook', {
      name: 'Facebook Live',
      rtmpUrl: 'rtmps://live-api-s.facebook.com:443/rtmp',
      maxBitrate: 4000,
      maxResolution: '1080p',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['reactions', 'comments', 'sharing']
    });

    this.platforms.set('instagram', {
      name: 'Instagram Live',
      rtmpUrl: 'rtmps://live-upload.instagram.com:443/rtmp',
      maxBitrate: 3500,
      maxResolution: '1080p',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['stories', 'igtv', 'shopping']
    });

    this.platforms.set('linkedin', {
      name: 'LinkedIn Live',
      rtmpUrl: 'rtmps://1-766-c63.stage.us-east-1.live.linkedin.com:443/live',
      maxBitrate: 5000,
      maxResolution: '1080p',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['professional', 'networking', 'events']
    });

    this.platforms.set('custom', {
      name: 'Custom RTMP',
      rtmpUrl: '',
      maxBitrate: 50000,
      maxResolution: '4K',
      audioCodec: 'AAC',
      videoCodec: 'H.264',
      features: ['flexible', 'custom']
    });
  }

  /**
   * Setup default stream configuration
   */
  setupStreamConfig() {
    this.streamConfig = {
      video: {
        width: 1920,
        height: 1080,
        fps: 30,
        bitrate: 5000,
        codec: 'H.264',
        preset: 'medium',
        profile: 'main',
        level: '4.1',
        keyframe: 2,
        bframes: 2
      },
      audio: {
        sampleRate: 48000,
        bitrate: 128,
        channels: 2,
        codec: 'AAC',
        profile: 'LC'
      },
      sources: {
        camera: null,
        microphone: null,
        desktop: false,
        window: null,
        scenes: []
      },
      output: {
        platform: 'youtube',
        streamKey: '',
        customRtmp: '',
        multistream: false,
        record: false,
        recordPath: '',
        recordFormat: 'mp4'
      },
      advanced: {
        lowLatency: false,
        hardwareAcceleration: true,
        adaptiveBitrate: true,
        bufferSize: 2048,
        maxRetries: 3,
        reconnectDelay: 5
      }
    };
  }

  /**
   * Configure streaming settings
   */
  configureStream(config) {
    try {
      // Validate configuration
      this.validateConfig(config);
      
      // Merge with existing config
      this.streamConfig = {
        ...this.streamConfig,
        ...config
      };

      // Update platform-specific settings
      if (config.output?.platform && this.platforms.has(config.output.platform)) {
        const platform = this.platforms.get(config.output.platform);
        
        // Ensure bitrate doesn't exceed platform limits
        if (this.streamConfig.video.bitrate > platform.maxBitrate) {
          this.streamConfig.video.bitrate = platform.maxBitrate;
        }
        
        this.rtmpUrl = platform.rtmpUrl;
      }

      this.emit('configUpdated', this.streamConfig);
      return true;
    } catch (error) {
      this.emit('error', new Error(`Configuration error: ${error.message}`));
      return false;
    }
  }

  /**
   * Validate stream configuration
   */
  validateConfig(config) {
    if (config.video) {
      if (config.video.width && (config.video.width < 320 || config.video.width > 7680)) {
        throw new Error('Video width must be between 320 and 7680 pixels');
      }
      if (config.video.height && (config.video.height < 240 || config.video.height > 4320)) {
        throw new Error('Video height must be between 240 and 4320 pixels');
      }
      if (config.video.fps && (config.video.fps < 1 || config.video.fps > 120)) {
        throw new Error('FPS must be between 1 and 120');
      }
      if (config.video.bitrate && (config.video.bitrate < 100 || config.video.bitrate > 100000)) {
        throw new Error('Video bitrate must be between 100 and 100000 kbps');
      }
    }

    if (config.audio) {
      if (config.audio.sampleRate && ![22050, 44100, 48000].includes(config.audio.sampleRate)) {
        throw new Error('Audio sample rate must be 22050, 44100, or 48000 Hz');
      }
      if (config.audio.bitrate && (config.audio.bitrate < 32 || config.audio.bitrate > 320)) {
        throw new Error('Audio bitrate must be between 32 and 320 kbps');
      }
      if (config.audio.channels && ![1, 2].includes(config.audio.channels)) {
        throw new Error('Audio channels must be 1 (mono) or 2 (stereo)');
      }
    }
  }

  /**
   * Get available video devices
   */
  async getVideoDevices() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices
        .filter(device => device.kind === 'videoinput')
        .map(device => ({
          id: device.deviceId,
          label: device.label || `Camera ${device.deviceId.slice(0, 8)}`,
          groupId: device.groupId
        }));

      this.emit('devicesEnumerated', { type: 'video', devices: videoDevices });
      return videoDevices;
    } catch (error) {
      this.emit('error', new Error(`Failed to enumerate video devices: ${error.message}`));
      return [];
    }
  }

  /**
   * Get available audio devices
   */
  async getAudioDevices() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioDevices = devices
        .filter(device => device.kind === 'audioinput')
        .map(device => ({
          id: device.deviceId,
          label: device.label || `Microphone ${device.deviceId.slice(0, 8)}`,
          groupId: device.groupId
        }));

      this.emit('devicesEnumerated', { type: 'audio', devices: audioDevices });
      return audioDevices;
    } catch (error) {
      this.emit('error', new Error(`Failed to enumerate audio devices: ${error.message}`));
      return [];
    }
  }

  /**
   * Setup video source
   */
  async setupVideoSource(deviceId = null) {
    try {
      const constraints = {
        video: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          width: { ideal: this.streamConfig.video.width },
          height: { ideal: this.streamConfig.video.height },
          frameRate: { ideal: this.streamConfig.video.fps }
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.streamConfig.sources.camera = stream;
      
      this.emit('videoSourceReady', {
        deviceId,
        resolution: `${this.streamConfig.video.width}x${this.streamConfig.video.height}`,
        fps: this.streamConfig.video.fps
      });

      return stream;
    } catch (error) {
      this.emit('error', new Error(`Failed to setup video source: ${error.message}`));
      return null;
    }
  }

  /**
   * Setup audio source
   */
  async setupAudioSource(deviceId = null) {
    try {
      const constraints = {
        audio: {
          deviceId: deviceId ? { exact: deviceId } : undefined,
          sampleRate: this.streamConfig.audio.sampleRate,
          channelCount: this.streamConfig.audio.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.streamConfig.sources.microphone = stream;
      
      this.emit('audioSourceReady', {
        deviceId,
        sampleRate: this.streamConfig.audio.sampleRate,
        channels: this.streamConfig.audio.channels
      });

      return stream;
    } catch (error) {
      this.emit('error', new Error(`Failed to setup audio source: ${error.message}`));
      return null;
    }
  }

  /**
   * Setup screen capture
   */
  async setupScreenCapture(displayId = null) {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          displaySurface: 'monitor',
          logicalSurface: true,
          cursor: 'always',
          width: { ideal: this.streamConfig.video.width },
          height: { ideal: this.streamConfig.video.height },
          frameRate: { ideal: this.streamConfig.video.fps }
        },
        audio: {
          sampleRate: 48000,
          channelCount: 2,
          echoCancellation: false,
          noiseSuppression: false
        }
      });

      this.streamConfig.sources.desktop = stream;
      
      this.emit('screenCaptureReady', {
        displayId,
        hasAudio: stream.getAudioTracks().length > 0
      });

      return stream;
    } catch (error) {
      this.emit('error', new Error(`Failed to setup screen capture: ${error.message}`));
      return null;
    }
  }

  /**
   * Start streaming
   */
  async startStream(streamKey = null, platform = null) {
    if (this.isStreaming) {
      throw new Error('Stream is already active');
    }

    try {
      // Validate inputs
      if (!streamKey && !this.streamConfig.output.streamKey) {
        throw new Error('Stream key is required');
      }

      const key = streamKey || this.streamConfig.output.streamKey;
      const targetPlatform = platform || this.streamConfig.output.platform;

      if (!this.platforms.has(targetPlatform)) {
        throw new Error(`Unsupported platform: ${targetPlatform}`);
      }

      // Setup media recorder or RTMP encoder
      await this.setupEncoder();
      
      // Start the stream
      this.streamKey = key;
      this.isStreaming = true;
      this.analytics.duration = 0;
      
      // Start analytics monitoring
      this.startAnalyticsMonitoring();
      
      this.emit('streamStarted', {
        platform: targetPlatform,
        timestamp: new Date(),
        config: this.streamConfig
      });

      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to start stream: ${error.message}`));
      return false;
    }
  }

  /**
   * Stop streaming
   */
  async stopStream() {
    if (!this.isStreaming) return false;

    try {
      // Stop encoder
      await this.stopEncoder();
      
      // Stop analytics monitoring
      this.stopAnalyticsMonitoring();
      
      // Clean up sources
      this.cleanupSources();
      
      this.isStreaming = false;
      this.streamKey = null;
      
      this.emit('streamStopped', {
        timestamp: new Date(),
        duration: this.analytics.duration,
        finalStats: { ...this.analytics }
      });

      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to stop stream: ${error.message}`));
      return false;
    }
  }

  /**
   * Setup encoder for streaming
   */
  async setupEncoder() {
    // This would integrate with actual encoding libraries
    // For now, we'll simulate the setup
    
    this.encoder = {
      video: {
        codec: this.streamConfig.video.codec,
        bitrate: this.streamConfig.video.bitrate,
        fps: this.streamConfig.video.fps,
        resolution: `${this.streamConfig.video.width}x${this.streamConfig.video.height}`
      },
      audio: {
        codec: this.streamConfig.audio.codec,
        bitrate: this.streamConfig.audio.bitrate,
        sampleRate: this.streamConfig.audio.sampleRate
      },
      output: {
        format: 'FLV',
        url: `${this.rtmpUrl}/${this.streamKey}`
      }
    };

    this.emit('encoderReady', this.encoder);
  }

  /**
   * Stop encoder
   */
  async stopEncoder() {
    if (this.encoder) {
      this.encoder = null;
      this.emit('encoderStopped');
    }
  }

  /**
   * Start analytics monitoring
   */
  startAnalyticsMonitoring() {
    this.analyticsInterval = setInterval(() => {
      this.updateAnalytics();
    }, 1000);
  }

  /**
   * Stop analytics monitoring
   */
  stopAnalyticsMonitoring() {
    if (this.analyticsInterval) {
      clearInterval(this.analyticsInterval);
      this.analyticsInterval = null;
    }
  }

  /**
   * Update streaming analytics
   */
  updateAnalytics() {
    if (!this.isStreaming) return;

    this.analytics.duration++;
    
    // Simulate analytics data
    this.analytics.viewers = Math.floor(Math.random() * 1000) + 1;
    this.analytics.bitrate = this.streamConfig.video.bitrate + Math.floor(Math.random() * 200) - 100;
    this.analytics.fps = this.streamConfig.video.fps;
    this.analytics.dropped = Math.floor(Math.random() * 10);

    this.emit('analyticsUpdate', { ...this.analytics });
  }

  /**
   * Add scene to stream
   */
  addScene(scene) {
    const sceneId = Date.now().toString();
    const newScene = {
      id: sceneId,
      name: scene.name || `Scene ${this.streamConfig.sources.scenes.length + 1}`,
      sources: scene.sources || [],
      layout: scene.layout || 'single',
      active: this.streamConfig.sources.scenes.length === 0,
      ...scene
    };

    this.streamConfig.sources.scenes.push(newScene);
    
    this.emit('sceneAdded', newScene);
    return sceneId;
  }

  /**
   * Switch to scene
   */
  switchToScene(sceneId) {
    const scene = this.streamConfig.sources.scenes.find(s => s.id === sceneId);
    if (!scene) return false;

    // Deactivate all scenes
    this.streamConfig.sources.scenes.forEach(s => s.active = false);
    
    // Activate target scene
    scene.active = true;
    
    this.emit('sceneChanged', scene);
    return true;
  }

  /**
   * Add overlay to stream
   */
  addOverlay(overlay) {
    const overlayId = Date.now().toString();
    const newOverlay = {
      id: overlayId,
      type: overlay.type || 'text',
      content: overlay.content || '',
      position: overlay.position || { x: 0, y: 0 },
      size: overlay.size || { width: 200, height: 50 },
      style: overlay.style || {},
      visible: true,
      ...overlay
    };

    if (!this.overlays) this.overlays = [];
    this.overlays.push(newOverlay);
    
    this.emit('overlayAdded', newOverlay);
    return overlayId;
  }

  /**
   * Update overlay
   */
  updateOverlay(overlayId, updates) {
    if (!this.overlays) return false;

    const overlay = this.overlays.find(o => o.id === overlayId);
    if (!overlay) return false;

    Object.assign(overlay, updates);
    
    this.emit('overlayUpdated', overlay);
    return true;
  }

  /**
   * Remove overlay
   */
  removeOverlay(overlayId) {
    if (!this.overlays) return false;

    const index = this.overlays.findIndex(o => o.id === overlayId);
    if (index === -1) return false;

    const removed = this.overlays.splice(index, 1)[0];
    
    this.emit('overlayRemoved', removed);
    return true;
  }

  /**
   * Get stream health status
   */
  getStreamHealth() {
    if (!this.isStreaming) {
      return { status: 'offline', health: 0 };
    }

    let health = 100;
    const issues = [];

    // Check bitrate stability
    if (this.analytics.bitrate < this.streamConfig.video.bitrate * 0.8) {
      health -= 20;
      issues.push('Low bitrate');
    }

    // Check dropped frames
    if (this.analytics.dropped > 5) {
      health -= 15;
      issues.push('Dropped frames');
    }

    // Check FPS
    if (this.analytics.fps < this.streamConfig.video.fps * 0.9) {
      health -= 10;
      issues.push('Low FPS');
    }

    let status;
    if (health >= 80) status = 'excellent';
    else if (health >= 60) status = 'good';
    else if (health >= 40) status = 'fair';
    else status = 'poor';

    return {
      status,
      health: Math.max(0, health),
      issues,
      uptime: this.analytics.duration
    };
  }

  /**
   * Get available platforms
   */
  getAvailablePlatforms() {
    return Array.from(this.platforms.entries()).map(([key, platform]) => ({
      id: key,
      name: platform.name,
      maxBitrate: platform.maxBitrate,
      maxResolution: platform.maxResolution,
      features: platform.features
    }));
  }

  /**
   * Clean up media sources
   */
  cleanupSources() {
    if (this.streamConfig.sources.camera) {
      this.streamConfig.sources.camera.getTracks().forEach(track => track.stop());
      this.streamConfig.sources.camera = null;
    }

    if (this.streamConfig.sources.microphone) {
      this.streamConfig.sources.microphone.getTracks().forEach(track => track.stop());
      this.streamConfig.sources.microphone = null;
    }

    if (this.streamConfig.sources.desktop) {
      this.streamConfig.sources.desktop.getTracks().forEach(track => track.stop());
      this.streamConfig.sources.desktop = false;
    }
  }

  /**
   * Get current stream status
   */
  getStreamStatus() {
    return {
      isStreaming: this.isStreaming,
      platform: this.streamConfig.output.platform,
      duration: this.analytics.duration,
      viewers: this.analytics.viewers,
      health: this.getStreamHealth(),
      config: this.streamConfig
    };
  }

  /**
   * Test stream configuration
   */
  async testConfiguration() {
    try {
      // Test video source
      if (this.streamConfig.sources.camera) {
        const videoTrack = this.streamConfig.sources.camera.getVideoTracks()[0];
        if (!videoTrack || videoTrack.readyState !== 'live') {
          throw new Error('Video source not available');
        }
      }

      // Test audio source
      if (this.streamConfig.sources.microphone) {
        const audioTrack = this.streamConfig.sources.microphone.getAudioTracks()[0];
        if (!audioTrack || audioTrack.readyState !== 'live') {
          throw new Error('Audio source not available');
        }
      }

      // Test platform configuration
      const platform = this.platforms.get(this.streamConfig.output.platform);
      if (!platform) {
        throw new Error('Invalid platform configuration');
      }

      // Test RTMP connection (would be actual test in real implementation)
      await this.testRTMPConnection();

      this.emit('configurationTested', { success: true });
      return { success: true, message: 'Configuration test passed' };
    } catch (error) {
      this.emit('configurationTested', { success: false, error: error.message });
      return { success: false, error: error.message };
    }
  }

  /**
   * Test RTMP connection
   */
  async testRTMPConnection() {
    // Simulate RTMP connection test
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.1) { // 90% success rate
          resolve();
        } else {
          reject(new Error('RTMP connection failed'));
        }
      }, 1000);
    });
  }
}

module.exports = LiveStreaming;