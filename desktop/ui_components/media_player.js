/**
 * Ainflue Desktop - Advanced Media Player
 * 
 * Professional media player supporting multiple formats
 * Audio, video, live streams, playlists, and advanced controls
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

class MediaPlayer {
  constructor(options = {}) {
    this.container = options.container || document.body;
    this.autoplay = options.autoplay || false;
    this.controls = options.controls !== false;
    this.volume = options.volume || 0.8;
    this.playbackRate = options.playbackRate || 1.0;
    this.loop = options.loop || false;
    this.muted = options.muted || false;
    this.theme = options.theme || 'professional';
    
    // Event callbacks
    this.onPlay = options.onPlay || (() => {});
    this.onPause = options.onPause || (() => {});
    this.onEnded = options.onEnded || (() => {});
    this.onTimeUpdate = options.onTimeUpdate || (() => {});
    this.onVolumeChange = options.onVolumeChange || (() => {});
    this.onError = options.onError || (() => {});
    
    // State management
    this.currentMedia = null;
    this.playlist = [];
    this.currentIndex = 0;
    this.isPlaying = false;
    this.isFullscreen = false;
    this.currentTime = 0;
    this.duration = 0;
    
    // Supported formats
    this.supportedFormats = {
      video: ['mp4', 'webm', 'ogg', 'avi', 'mov', 'mkv'],
      audio: ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a'],
      streaming: ['m3u8', 'mpd', 'rtmp', 'rtsp']
    };
    
    this.initializePlayer();
  }

  /**
   * Initialize the media player
   */
  initializePlayer() {
    this.createPlayerStructure();
    this.createPlayerStyles();
    this.setupEventListeners();
    this.setupKeyboardShortcuts();
  }

  /**
   * Create player HTML structure
   */
  createPlayerStructure() {
    this.playerContainer = document.createElement('div');
    this.playerContainer.className = `ainflue-media-player ${this.theme}`;
    this.playerContainer.innerHTML = `
      <div class="media-viewport">
        <video class="media-element" preload="metadata"></video>
        <audio class="media-element" preload="metadata" style="display: none;"></audio>
        
        <div class="media-overlay">
          <div class="loading-spinner">
            <div class="spinner"></div>
          </div>
          
          <div class="play-button-overlay">
            <button class="play-btn-large" aria-label="Play">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </button>
          </div>
          
          <div class="error-message" style="display: none;">
            <div class="error-content">
              <h3>Media Error</h3>
              <p class="error-text">Unable to load media file</p>
              <button class="retry-btn">Retry</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="media-controls" ${!this.controls ? 'style="display: none;"' : ''}>
        <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-buffer"></div>
            <div class="progress-current"></div>
            <div class="progress-handle"></div>
          </div>
          <div class="time-display">
            <span class="current-time">0:00</span>
            <span class="duration">0:00</span>
          </div>
        </div>
        
        <div class="control-buttons">
          <div class="left-controls">
            <button class="control-btn play-pause" aria-label="Play/Pause">
              <svg class="play-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <svg class="pause-icon" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
            </button>
            
            <button class="control-btn prev" aria-label="Previous">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
              </svg>
            </button>
            
            <button class="control-btn next" aria-label="Next">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </button>
            
            <div class="volume-container">
              <button class="control-btn volume-btn" aria-label="Volume">
                <svg class="volume-high" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
                <svg class="volume-muted" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                  <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                </svg>
              </button>
              <div class="volume-slider">
                <input type="range" class="volume-range" min="0" max="100" value="80">
              </div>
            </div>
          </div>
          
          <div class="right-controls">
            <div class="playback-rate">
              <select class="rate-selector">
                <option value="0.5">0.5x</option>
                <option value="0.75">0.75x</option>
                <option value="1" selected>1x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="2">2x</option>
              </select>
            </div>
            
            <button class="control-btn playlist-btn" aria-label="Playlist">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
              </svg>
            </button>
            
            <button class="control-btn fullscreen-btn" aria-label="Fullscreen">
              <svg class="fullscreen-enter" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
              </svg>
              <svg class="fullscreen-exit" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div class="playlist-panel" style="display: none;">
        <div class="playlist-header">
          <h3>Playlist</h3>
          <button class="close-playlist">×</button>
        </div>
        <div class="playlist-items"></div>
      </div>
    `;
    
    this.container.appendChild(this.playerContainer);
    this.cacheElements();
  }

  /**
   * Cache DOM elements for performance
   */
  cacheElements() {
    this.videoElement = this.playerContainer.querySelector('video.media-element');
    this.audioElement = this.playerContainer.querySelector('audio.media-element');
    this.playPauseBtn = this.playerContainer.querySelector('.play-pause');
    this.playBtnLarge = this.playerContainer.querySelector('.play-btn-large');
    this.prevBtn = this.playerContainer.querySelector('.prev');
    this.nextBtn = this.playerContainer.querySelector('.next');
    this.volumeBtn = this.playerContainer.querySelector('.volume-btn');
    this.volumeSlider = this.playerContainer.querySelector('.volume-range');
    this.progressBar = this.playerContainer.querySelector('.progress-bar');
    this.progressCurrent = this.playerContainer.querySelector('.progress-current');
    this.progressBuffer = this.playerContainer.querySelector('.progress-buffer');
    this.progressHandle = this.playerContainer.querySelector('.progress-handle');
    this.currentTimeEl = this.playerContainer.querySelector('.current-time');
    this.durationEl = this.playerContainer.querySelector('.duration');
    this.fullscreenBtn = this.playerContainer.querySelector('.fullscreen-btn');
    this.playlistBtn = this.playerContainer.querySelector('.playlist-btn');
    this.playlistPanel = this.playerContainer.querySelector('.playlist-panel');
    this.playlistItems = this.playerContainer.querySelector('.playlist-items');
    this.rateSelector = this.playerContainer.querySelector('.rate-selector');
    this.loadingSpinner = this.playerContainer.querySelector('.loading-spinner');
    this.errorMessage = this.playerContainer.querySelector('.error-message');
    this.retryBtn = this.playerContainer.querySelector('.retry-btn');
  }

  /**
   * Create player styles
   */
  createPlayerStyles() {
    if (document.getElementById('media-player-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'media-player-styles';
    styles.textContent = `
      .ainflue-media-player {
        background: #000;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        position: relative;
        max-width: 100%;
      }
      
      .ainflue-media-player.professional {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
      }
      
      .media-viewport {
        position: relative;
        background: #000;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .media-element {
        width: 100%;
        height: auto;
        max-height: 70vh;
        outline: none;
      }
      
      .media-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
      }
      
      .loading-spinner {
        position: absolute;
        z-index: 3;
      }
      
      .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .play-button-overlay {
        position: absolute;
        z-index: 2;
        pointer-events: auto;
      }
      
      .play-btn-large {
        width: 80px;
        height: 80px;
        border: none;
        background: rgba(102, 126, 234, 0.9);
        color: white;
        border-radius: 50%;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .play-btn-large:hover {
        background: rgba(102, 126, 234, 1);
        transform: scale(1.1);
      }
      
      .play-btn-large svg {
        width: 32px;
        height: 32px;
        margin-left: 4px;
      }
      
      .error-message {
        position: absolute;
        z-index: 4;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        pointer-events: auto;
      }
      
      .error-content h3 {
        margin: 0 0 10px 0;
        color: #e53e3e;
      }
      
      .retry-btn {
        background: #667eea;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 10px;
      }
      
      .media-controls {
        background: linear-gradient(180deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.9) 100%);
        color: white;
        padding: 16px;
      }
      
      .progress-container {
        margin-bottom: 16px;
      }
      
      .progress-bar {
        position: relative;
        height: 6px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
        cursor: pointer;
        margin-bottom: 8px;
      }
      
      .progress-buffer {
        position: absolute;
        height: 100%;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
        width: 0%;
      }
      
      .progress-current {
        position: absolute;
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 3px;
        width: 0%;
      }
      
      .progress-handle {
        position: absolute;
        width: 16px;
        height: 16px;
        background: #667eea;
        border-radius: 50%;
        top: -5px;
        left: 0;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s ease;
        transform: translateX(-50%);
      }
      
      .progress-bar:hover .progress-handle {
        opacity: 1;
      }
      
      .time-display {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.8);
      }
      
      .control-buttons {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .left-controls, .right-controls {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      .control-btn {
        background: none;
        border: none;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
      }
      
      .control-btn:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      .control-btn svg {
        width: 20px;
        height: 20px;
      }
      
      .volume-container {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .volume-slider {
        width: 80px;
        opacity: 0;
        transition: opacity 0.2s ease;
      }
      
      .volume-container:hover .volume-slider {
        opacity: 1;
      }
      
      .volume-range {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
        outline: none;
        -webkit-appearance: none;
      }
      
      .volume-range::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 14px;
        height: 14px;
        background: #667eea;
        border-radius: 50%;
        cursor: pointer;
      }
      
      .rate-selector {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        outline: none;
      }
      
      .playlist-panel {
        position: absolute;
        right: 0;
        top: 0;
        width: 300px;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        z-index: 5;
        overflow-y: auto;
      }
      
      .playlist-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      .close-playlist {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
      }
      
      .playlist-item {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        cursor: pointer;
        transition: background 0.2s ease;
      }
      
      .playlist-item:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      .playlist-item.active {
        background: rgba(102, 126, 234, 0.3);
      }
      
      .playlist-item-title {
        font-weight: 600;
        margin-bottom: 4px;
      }
      
      .playlist-item-duration {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
      }
      
      .ainflue-media-player.fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 9999;
        border-radius: 0;
      }
      
      .ainflue-media-player.fullscreen .media-element {
        max-height: calc(100vh - 100px);
      }
    `;
    
    document.head.appendChild(styles);
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Play/Pause button
    this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
    this.playBtnLarge.addEventListener('click', () => this.togglePlayPause());
    
    // Previous/Next buttons
    this.prevBtn.addEventListener('click', () => this.previousMedia());
    this.nextBtn.addEventListener('click', () => this.nextMedia());
    
    // Volume controls
    this.volumeBtn.addEventListener('click', () => this.toggleMute());
    this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value / 100));
    
    // Progress bar
    this.progressBar.addEventListener('click', (e) => this.seek(e));
    this.progressHandle.addEventListener('mousedown', (e) => this.startSeeking(e));
    
    // Fullscreen
    this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    
    // Playlist
    this.playlistBtn.addEventListener('click', () => this.togglePlaylist());
    this.playerContainer.querySelector('.close-playlist').addEventListener('click', () => this.closePlaylist());
    
    // Playback rate
    this.rateSelector.addEventListener('change', (e) => this.setPlaybackRate(parseFloat(e.target.value)));
    
    // Retry button
    this.retryBtn.addEventListener('click', () => this.retryLoad());
    
    // Media element events
    this.setupMediaEvents();
    
    // Viewport click
    this.playerContainer.querySelector('.media-viewport').addEventListener('click', (e) => {
      if (e.target.classList.contains('media-element')) {
        this.togglePlayPause();
      }
    });
  }

  /**
   * Setup media element events
   */
  setupMediaEvents() {
    const setupEvents = (element) => {
      element.addEventListener('loadstart', () => this.showLoading());
      element.addEventListener('loadedmetadata', () => this.updateDuration());
      element.addEventListener('canplay', () => this.hideLoading());
      element.addEventListener('play', () => this.handlePlay());
      element.addEventListener('pause', () => this.handlePause());
      element.addEventListener('ended', () => this.handleEnded());
      element.addEventListener('timeupdate', () => this.updateProgress());
      element.addEventListener('progress', () => this.updateBuffer());
      element.addEventListener('volumechange', () => this.updateVolumeDisplay());
      element.addEventListener('error', (e) => this.handleError(e));
      element.addEventListener('waiting', () => this.showLoading());
      element.addEventListener('playing', () => this.hideLoading());
    };
    
    setupEvents(this.videoElement);
    setupEvents(this.audioElement);
  }

  /**
   * Setup keyboard shortcuts
   */
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (!this.playerContainer.contains(document.activeElement) && !this.isFullscreen) return;
      
      switch (e.code) {
        case 'Space':
          e.preventDefault();
          this.togglePlayPause();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          this.seek(null, this.currentTime - 10);
          break;
        case 'ArrowRight':
          e.preventDefault();
          this.seek(null, this.currentTime + 10);
          break;
        case 'ArrowUp':
          e.preventDefault();
          this.setVolume(Math.min(1, this.currentMedia.volume + 0.1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          this.setVolume(Math.max(0, this.currentMedia.volume - 0.1));
          break;
        case 'KeyM':
          e.preventDefault();
          this.toggleMute();
          break;
        case 'KeyF':
          e.preventDefault();
          this.toggleFullscreen();
          break;
        case 'Escape':
          if (this.isFullscreen) {
            this.exitFullscreen();
          }
          break;
      }
    });
  }

  /**
   * Load media file or URL
   */
  loadMedia(source, type = 'auto') {
    this.showLoading();
    this.hideError();
    
    // Determine media type
    const mediaType = this.detectMediaType(source, type);
    
    // Switch between video and audio elements
    if (mediaType === 'video') {
      this.currentMedia = this.videoElement;
      this.videoElement.style.display = 'block';
      this.audioElement.style.display = 'none';
    } else {
      this.currentMedia = this.audioElement;
      this.videoElement.style.display = 'none';
      this.audioElement.style.display = 'block';
    }
    
    // Set source
    this.currentMedia.src = source;
    this.currentMedia.volume = this.volume;
    this.currentMedia.muted = this.muted;
    this.currentMedia.playbackRate = this.playbackRate;
    this.currentMedia.loop = this.loop;
    
    // Load the media
    this.currentMedia.load();
    
    if (this.autoplay) {
      this.currentMedia.play().catch(() => {
        // Autoplay was prevented
        this.hideLoading();
      });
    } else {
      this.hideLoading();
    }
  }

  /**
   * Detect media type from source
   */
  detectMediaType(source, type) {
    if (type !== 'auto') return type;
    
    const extension = source.split('.').pop().toLowerCase();
    
    if (this.supportedFormats.video.includes(extension)) {
      return 'video';
    } else if (this.supportedFormats.audio.includes(extension)) {
      return 'audio';
    } else {
      return 'video'; // Default to video for unknown types
    }
  }

  /**
   * Toggle play/pause
   */
  togglePlayPause() {
    if (!this.currentMedia) return;
    
    if (this.isPlaying) {
      this.currentMedia.pause();
    } else {
      this.currentMedia.play().catch(e => this.handleError(e));
    }
  }

  /**
   * Play media
   */
  play() {
    if (this.currentMedia) {
      this.currentMedia.play().catch(e => this.handleError(e));
    }
  }

  /**
   * Pause media
   */
  pause() {
    if (this.currentMedia) {
      this.currentMedia.pause();
    }
  }

  /**
   * Seek to specific time
   */
  seek(event, time) {
    if (!this.currentMedia) return;
    
    if (event) {
      const rect = this.progressBar.getBoundingClientRect();
      const percent = (event.clientX - rect.left) / rect.width;
      time = percent * this.duration;
    }
    
    this.currentMedia.currentTime = Math.max(0, Math.min(time, this.duration));
  }

  /**
   * Set volume (0-1)
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    
    if (this.currentMedia) {
      this.currentMedia.volume = this.volume;
    }
    
    this.volumeSlider.value = this.volume * 100;
    this.updateVolumeDisplay();
    this.onVolumeChange(this.volume);
  }

  /**
   * Toggle mute
   */
  toggleMute() {
    this.muted = !this.muted;
    
    if (this.currentMedia) {
      this.currentMedia.muted = this.muted;
    }
    
    this.updateVolumeDisplay();
  }

  /**
   * Set playback rate
   */
  setPlaybackRate(rate) {
    this.playbackRate = rate;
    
    if (this.currentMedia) {
      this.currentMedia.playbackRate = rate;
    }
  }

  /**
   * Toggle fullscreen
   */
  toggleFullscreen() {
    if (this.isFullscreen) {
      this.exitFullscreen();
    } else {
      this.enterFullscreen();
    }
  }

  /**
   * Enter fullscreen mode
   */
  enterFullscreen() {
    this.isFullscreen = true;
    this.playerContainer.classList.add('fullscreen');
    
    if (this.playerContainer.requestFullscreen) {
      this.playerContainer.requestFullscreen();
    } else if (this.playerContainer.webkitRequestFullscreen) {
      this.playerContainer.webkitRequestFullscreen();
    } else if (this.playerContainer.mozRequestFullScreen) {
      this.playerContainer.mozRequestFullScreen();
    }
    
    this.updateFullscreenButton();
  }

  /**
   * Exit fullscreen mode
   */
  exitFullscreen() {
    this.isFullscreen = false;
    this.playerContainer.classList.remove('fullscreen');
    
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    }
    
    this.updateFullscreenButton();
  }

  /**
   * Update fullscreen button icon
   */
  updateFullscreenButton() {
    const enterIcon = this.fullscreenBtn.querySelector('.fullscreen-enter');
    const exitIcon = this.fullscreenBtn.querySelector('.fullscreen-exit');
    
    if (this.isFullscreen) {
      enterIcon.style.display = 'none';
      exitIcon.style.display = 'block';
    } else {
      enterIcon.style.display = 'block';
      exitIcon.style.display = 'none';
    }
  }

  /**
   * Add media to playlist
   */
  addToPlaylist(media) {
    this.playlist.push({
      id: Date.now() + Math.random(),
      url: media.url,
      title: media.title || 'Untitled',
      duration: media.duration || '0:00',
      type: media.type || 'auto'
    });
    
    this.updatePlaylistDisplay();
  }

  /**
   * Load playlist
   */
  loadPlaylist(playlist) {
    this.playlist = playlist.map(item => ({
      id: Date.now() + Math.random(),
      ...item
    }));
    
    this.currentIndex = 0;
    this.updatePlaylistDisplay();
    
    if (this.playlist.length > 0) {
      this.loadMedia(this.playlist[0].url, this.playlist[0].type);
    }
  }

  /**
   * Play next media in playlist
   */
  nextMedia() {
    if (this.playlist.length === 0) return;
    
    this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
    const media = this.playlist[this.currentIndex];
    this.loadMedia(media.url, media.type);
    this.updatePlaylistDisplay();
  }

  /**
   * Play previous media in playlist
   */
  previousMedia() {
    if (this.playlist.length === 0) return;
    
    this.currentIndex = this.currentIndex === 0 ? this.playlist.length - 1 : this.currentIndex - 1;
    const media = this.playlist[this.currentIndex];
    this.loadMedia(media.url, media.type);
    this.updatePlaylistDisplay();
  }

  /**
   * Toggle playlist visibility
   */
  togglePlaylist() {
    const isVisible = this.playlistPanel.style.display !== 'none';
    this.playlistPanel.style.display = isVisible ? 'none' : 'block';
  }

  /**
   * Close playlist
   */
  closePlaylist() {
    this.playlistPanel.style.display = 'none';
  }

  /**
   * Update playlist display
   */
  updatePlaylistDisplay() {
    this.playlistItems.innerHTML = '';
    
    this.playlist.forEach((item, index) => {
      const itemEl = document.createElement('div');
      itemEl.className = `playlist-item ${index === this.currentIndex ? 'active' : ''}`;
      itemEl.innerHTML = `
        <div class="playlist-item-title">${item.title}</div>
        <div class="playlist-item-duration">${item.duration}</div>
      `;
      
      itemEl.addEventListener('click', () => {
        this.currentIndex = index;
        this.loadMedia(item.url, item.type);
        this.updatePlaylistDisplay();
      });
      
      this.playlistItems.appendChild(itemEl);
    });
  }

  /**
   * Event handlers
   */
  handlePlay() {
    this.isPlaying = true;
    this.playBtnLarge.style.display = 'none';
    this.playPauseBtn.querySelector('.play-icon').style.display = 'none';
    this.playPauseBtn.querySelector('.pause-icon').style.display = 'block';
    this.onPlay();
  }

  handlePause() {
    this.isPlaying = false;
    this.playBtnLarge.style.display = 'flex';
    this.playPauseBtn.querySelector('.play-icon').style.display = 'block';
    this.playPauseBtn.querySelector('.pause-icon').style.display = 'none';
    this.onPause();
  }

  handleEnded() {
    this.isPlaying = false;
    this.playBtnLarge.style.display = 'flex';
    this.onEnded();
    
    // Auto play next in playlist
    if (this.playlist.length > 0 && !this.loop) {
      setTimeout(() => this.nextMedia(), 1000);
    }
  }

  handleError(error) {
    this.hideLoading();
    this.showError('Unable to load media file');
    this.onError(error);
  }

  /**
   * Update progress display
   */
  updateProgress() {
    if (!this.currentMedia) return;
    
    this.currentTime = this.currentMedia.currentTime;
    this.duration = this.currentMedia.duration || 0;
    
    const percent = this.duration ? (this.currentTime / this.duration) * 100 : 0;
    this.progressCurrent.style.width = `${percent}%`;
    this.progressHandle.style.left = `${percent}%`;
    
    this.currentTimeEl.textContent = this.formatTime(this.currentTime);
    this.onTimeUpdate(this.currentTime, this.duration);
  }

  /**
   * Update buffer display
   */
  updateBuffer() {
    if (!this.currentMedia || !this.currentMedia.buffered.length) return;
    
    const buffered = this.currentMedia.buffered.end(this.currentMedia.buffered.length - 1);
    const percent = this.duration ? (buffered / this.duration) * 100 : 0;
    this.progressBuffer.style.width = `${percent}%`;
  }

  /**
   * Update duration display
   */
  updateDuration() {
    if (!this.currentMedia) return;
    
    this.duration = this.currentMedia.duration || 0;
    this.durationEl.textContent = this.formatTime(this.duration);
  }

  /**
   * Update volume display
   */
  updateVolumeDisplay() {
    const volumeHigh = this.volumeBtn.querySelector('.volume-high');
    const volumeMuted = this.volumeBtn.querySelector('.volume-muted');
    
    if (this.muted || this.volume === 0) {
      volumeHigh.style.display = 'none';
      volumeMuted.style.display = 'block';
    } else {
      volumeHigh.style.display = 'block';
      volumeMuted.style.display = 'none';
    }
  }

  /**
   * Show loading spinner
   */
  showLoading() {
    this.loadingSpinner.style.display = 'block';
  }

  /**
   * Hide loading spinner
   */
  hideLoading() {
    this.loadingSpinner.style.display = 'none';
  }

  /**
   * Show error message
   */
  showError(message) {
    this.errorMessage.querySelector('.error-text').textContent = message;
    this.errorMessage.style.display = 'block';
  }

  /**
   * Hide error message
   */
  hideError() {
    this.errorMessage.style.display = 'none';
  }

  /**
   * Retry loading current media
   */
  retryLoad() {
    if (this.currentMedia) {
      this.hideError();
      this.currentMedia.load();
    }
  }

  /**
   * Format time in MM:SS format
   */
  formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  /**
   * Start seeking (drag)
   */
  startSeeking(e) {
    e.preventDefault();
    
    const handleMouseMove = (e) => {
      const rect = this.progressBar.getBoundingClientRect();
      const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const time = percent * this.duration;
      
      if (this.currentMedia) {
        this.currentMedia.currentTime = time;
      }
    };
    
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }

  /**
   * Destroy the player
   */
  destroy() {
    if (this.currentMedia) {
      this.currentMedia.pause();
      this.currentMedia.src = '';
    }
    
    this.container.removeChild(this.playerContainer);
    
    // Remove styles if no other players exist
    if (!document.querySelector('.ainflue-media-player')) {
      const styles = document.getElementById('media-player-styles');
      if (styles) {
        styles.remove();
      }
    }
  }

  /**
   * Get current state
   */
  getState() {
    return {
      isPlaying: this.isPlaying,
      currentTime: this.currentTime,
      duration: this.duration,
      volume: this.volume,
      muted: this.muted,
      playbackRate: this.playbackRate,
      currentIndex: this.currentIndex,
      playlist: this.playlist
    };
  }

  /**
   * Set player state
   */
  setState(state) {
    if (state.volume !== undefined) this.setVolume(state.volume);
    if (state.muted !== undefined) this.muted = state.muted;
    if (state.playbackRate !== undefined) this.setPlaybackRate(state.playbackRate);
    if (state.playlist) this.loadPlaylist(state.playlist);
    if (state.currentIndex !== undefined) this.currentIndex = state.currentIndex;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MediaPlayer;
} else if (typeof window !== 'undefined') {
  window.MediaPlayer = MediaPlayer;
}

/**
 * Usage Example:
 * 
 * const player = new MediaPlayer({
 *   container: document.getElementById('player-container'),
 *   autoplay: false,
 *   controls: true,
 *   theme: 'professional',
 *   onPlay: () => console.log('Playing'),
 *   onPause: () => console.log('Paused'),
 *   onTimeUpdate: (currentTime, duration) => console.log(`${currentTime}/${duration}`)
 * });
 * 
 * // Load single media
 * player.loadMedia('path/to/video.mp4', 'video');
 * 
 * // Load playlist
 * player.loadPlaylist([
 *   { url: 'video1.mp4', title: 'Video 1', type: 'video' },
 *   { url: 'audio1.mp3', title: 'Audio 1', type: 'audio' }
 * ]);
 */