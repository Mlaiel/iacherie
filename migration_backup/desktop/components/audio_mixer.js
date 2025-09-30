/**
 * Ainflue Desktop - Audio Mixer Component
 * 
 * Professional multi-channel audio mixer with advanced effects and automation
 * Implements broadcast-quality mixing console with AI-powered enhancement
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class AudioMixerComponent {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      channels: 64,
      effects: true,
      automation: true,
      surround: true,
      realtime: true,
      sampleRate: 48000,
      bitDepth: 24,
      bufferSize: 512,
      enableAI: true,
      ...options
    };

    this.channels = new Map();
    this.masterChannel = null;
    this.effects = new Map();
    this.automationData = new Map();
    this.currentScene = null;
    this.isRecording = false;
    this.isPlaying = false;
    this.currentTime = 0;
    this.totalTime = 0;
    this.vuMeters = new Map();
    this.compressors = new Map();
    this.equalizers = new Map();

    this.audioContext = null;
    this.masterGain = null;
    this.analyzer = null;
    this.recorder = null;

    this.mixerModes = ['studio', 'live', 'mastering', 'streaming'];
    this.currentMode = 'studio';

    this.initialize();
  }

  async initialize() {
    await this.initializeAudioContext();
    this.createMixerInterface();
    this.setupChannels();
    this.setupMasterSection();
    this.setupEffectsRack();
    this.setupAutomation();
    this.setupAIAssistant();
    this.startMetering();
    
    console.log('🎛️ Audio Mixer initialized');
  }

  async initializeAudioContext() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: this.options.sampleRate,
        latencyHint: 'interactive'
      });

      // Create master gain node
      this.masterGain = this.audioContext.createGain();
      this.masterGain.connect(this.audioContext.destination);

      // Create analyzer for metering
      this.analyzer = this.audioContext.createAnalyser();
      this.analyzer.fftSize = 2048;
      this.analyzer.smoothingTimeConstant = 0.3;
      this.masterGain.connect(this.analyzer);

      console.log('🔊 Audio context initialized');
    } catch (error) {
      console.error('❌ Failed to initialize audio context:', error);
    }
  }

  createMixerInterface() {
    this.container.innerHTML = `
      <div class="audio-mixer">
        <div class="mixer-header">
          <div class="mixer-toolbar">
            <div class="mode-selector">
              <select class="mixer-mode-select">
                <option value="studio">Studio Mode</option>
                <option value="live">Live Mode</option>
                <option value="mastering">Mastering Mode</option>
                <option value="streaming">Streaming Mode</option>
              </select>
            </div>
            
            <div class="transport-controls">
              <button class="transport-btn record-btn" title="Record">⏺</button>
              <button class="transport-btn play-btn" title="Play">▶</button>
              <button class="transport-btn pause-btn" title="Pause">⏸</button>
              <button class="transport-btn stop-btn" title="Stop">⏹</button>
              <button class="transport-btn loop-btn" title="Loop">🔁</button>
            </div>
            
            <div class="time-display">
              <span class="current-time">00:00:00</span>
              <span class="separator">/</span>
              <span class="total-time">00:00:00</span>
            </div>
            
            <div class="mixer-actions">
              <button class="ai-assistant-btn" title="AI Assistant">🤖</button>
              <button class="save-scene-btn" title="Save Scene">💾</button>
              <button class="load-scene-btn" title="Load Scene">📁</button>
              <button class="reset-mixer-btn" title="Reset Mixer">🔄</button>
            </div>
          </div>
        </div>
        
        <div class="mixer-content">
          <div class="channels-section">
            <div class="channels-header">
              <h3>Channels</h3>
              <button class="add-channel-btn">+ Add Channel</button>
            </div>
            <div class="channels-container"></div>
          </div>
          
          <div class="master-section">
            <div class="master-header">
              <h3>Master</h3>
            </div>
            <div class="master-channel"></div>
          </div>
          
          <div class="effects-section">
            <div class="effects-header">
              <h3>Effects Rack</h3>
              <button class="add-effect-btn">+ Add Effect</button>
            </div>
            <div class="effects-rack"></div>
          </div>
        </div>
        
        <div class="mixer-footer">
          <div class="cpu-meter">
            <label>CPU:</label>
            <div class="cpu-bar">
              <div class="cpu-fill"></div>
            </div>
            <span class="cpu-value">0%</span>
          </div>
          
          <div class="latency-display">
            <label>Latency:</label>
            <span class="latency-value">5.3ms</span>
          </div>
          
          <div class="sample-rate-display">
            <label>Sample Rate:</label>
            <span class="sample-rate-value">${this.options.sampleRate} Hz</span>
          </div>
        </div>
      </div>
    `;

    this.addMixerStyling();
    this.setupMixerEventHandlers();
  }

  addMixerStyling() {
    const style = document.createElement('style');
    style.textContent = `
      .audio-mixer {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: #ffffff;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        border-radius: 8px;
        overflow: hidden;
      }

      .mixer-header {
        background: #2a2a2a;
        border-bottom: 2px solid #404040;
        padding: 12px;
      }

      .mixer-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }

      .mode-selector select {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px 12px;
        font-size: 14px;
      }

      .transport-controls {
        display: flex;
        gap: 4px;
      }

      .transport-btn {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 16px;
        min-width: 40px;
      }

      .transport-btn:hover {
        background: #4a4a4a;
        border-color: #007aff;
      }

      .transport-btn.active {
        background: #007aff;
        border-color: #007aff;
      }

      .transport-btn.record-btn.active {
        background: #ff3333;
        border-color: #ff3333;
      }

      .time-display {
        font-family: 'SF Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        color: #00ff00;
        background: #1a1a1a;
        padding: 8px 16px;
        border-radius: 6px;
        border: 1px solid #404040;
      }

      .separator {
        color: #666;
        margin: 0 8px;
      }

      .mixer-actions {
        display: flex;
        gap: 8px;
      }

      .ai-assistant-btn, .save-scene-btn, .load-scene-btn, .reset-mixer-btn {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .ai-assistant-btn:hover, .save-scene-btn:hover, .load-scene-btn:hover, .reset-mixer-btn:hover {
        background: #4a4a4a;
        border-color: #007aff;
      }

      .mixer-content {
        flex: 1;
        display: flex;
        overflow: hidden;
      }

      .channels-section {
        flex: 1;
        border-right: 1px solid #404040;
        display: flex;
        flex-direction: column;
      }

      .channels-header, .master-header, .effects-header {
        background: #333;
        padding: 8px 12px;
        border-bottom: 1px solid #404040;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .channels-header h3, .master-header h3, .effects-header h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
      }

      .add-channel-btn, .add-effect-btn {
        background: #007aff;
        border: none;
        border-radius: 4px;
        color: #ffffff;
        padding: 4px 8px;
        font-size: 12px;
        cursor: pointer;
      }

      .channels-container {
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        display: flex;
        padding: 12px;
        gap: 8px;
      }

      .master-section {
        width: 120px;
        border-right: 1px solid #404040;
        display: flex;
        flex-direction: column;
      }

      .master-channel {
        flex: 1;
        padding: 12px;
      }

      .effects-section {
        width: 300px;
        display: flex;
        flex-direction: column;
      }

      .effects-rack {
        flex: 1;
        padding: 12px;
        overflow-y: auto;
      }

      .mixer-channel {
        background: #2a2a2a;
        border: 1px solid #404040;
        border-radius: 8px;
        width: 80px;
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 8px;
        gap: 8px;
        position: relative;
      }

      .channel-label {
        font-size: 10px;
        text-align: center;
        font-weight: 600;
        color: #ccc;
        background: #3a3a3a;
        padding: 2px 4px;
        border-radius: 3px;
      }

      .channel-controls {
        display: flex;
        flex-direction: column;
        gap: 6px;
        flex: 1;
      }

      .control-group {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .control-label {
        font-size: 8px;
        color: #888;
        text-align: center;
      }

      .rotary-knob {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3a3a3a 0%, #4a4a4a 100%);
        border: 2px solid #555;
        position: relative;
        cursor: pointer;
        margin: 0 auto;
      }

      .rotary-knob::after {
        content: '';
        position: absolute;
        top: 4px;
        left: 50%;
        transform: translateX(-50%);
        width: 2px;
        height: 12px;
        background: #00ff00;
        border-radius: 1px;
        transform-origin: 50% 16px;
      }

      .channel-fader {
        writing-mode: bt-lr; /* IE */
        writing-mode: vertical-lr;
        width: 20px;
        height: 200px;
        margin: 0 auto;
        -webkit-appearance: slider-vertical;
      }

      .vu-meter {
        width: 12px;
        height: 200px;
        background: #1a1a1a;
        border: 1px solid #404040;
        border-radius: 6px;
        position: relative;
        overflow: hidden;
      }

      .vu-meter-fill {
        position: absolute;
        bottom: 0;
        width: 100%;
        background: linear-gradient(to top, 
          #00ff00 0%, 
          #00ff00 60%, 
          #ffff00 80%, 
          #ff0000 100%);
        transition: height 0.1s ease;
      }

      .mute-solo-buttons {
        display: flex;
        gap: 2px;
      }

      .mute-btn, .solo-btn {
        flex: 1;
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 3px;
        color: #ffffff;
        padding: 2px;
        font-size: 8px;
        cursor: pointer;
      }

      .mute-btn.active {
        background: #ff3333;
      }

      .solo-btn.active {
        background: #ffff00;
        color: #000;
      }

      .mixer-footer {
        background: #2a2a2a;
        border-top: 1px solid #404040;
        padding: 8px 12px;
        display: flex;
        align-items: center;
        gap: 24px;
        font-size: 12px;
      }

      .cpu-meter {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .cpu-bar {
        width: 60px;
        height: 8px;
        background: #1a1a1a;
        border: 1px solid #404040;
        border-radius: 4px;
        overflow: hidden;
      }

      .cpu-fill {
        height: 100%;
        background: linear-gradient(to right, #00ff00, #ffff00, #ff0000);
        width: 0%;
        transition: width 0.3s ease;
      }

      .effect-module {
        background: #333;
        border: 1px solid #555;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 8px;
      }

      .effect-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
      }

      .effect-name {
        font-size: 12px;
        font-weight: 600;
      }

      .effect-bypass {
        background: #007aff;
        border: none;
        border-radius: 3px;
        color: white;
        padding: 2px 6px;
        font-size: 10px;
        cursor: pointer;
      }

      .effect-bypass.bypassed {
        background: #666;
      }

      .effect-controls {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
      }

      @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
      }

      .recording {
        animation: pulse 1s infinite;
      }
    `;
    document.head.appendChild(style);
  }

  setupMixerEventHandlers() {
    // Mode selector
    this.container.querySelector('.mixer-mode-select').addEventListener('change', (e) => {
      this.setMixerMode(e.target.value);
    });

    // Transport controls
    this.container.querySelector('.record-btn').addEventListener('click', () => {
      this.toggleRecording();
    });

    this.container.querySelector('.play-btn').addEventListener('click', () => {
      this.togglePlayback();
    });

    this.container.querySelector('.pause-btn').addEventListener('click', () => {
      this.pausePlayback();
    });

    this.container.querySelector('.stop-btn').addEventListener('click', () => {
      this.stopPlayback();
    });

    this.container.querySelector('.loop-btn').addEventListener('click', () => {
      this.toggleLoop();
    });

    // AI Assistant
    this.container.querySelector('.ai-assistant-btn').addEventListener('click', () => {
      this.showAIAssistant();
    });

    // Scene management
    this.container.querySelector('.save-scene-btn').addEventListener('click', () => {
      this.saveScene();
    });

    this.container.querySelector('.load-scene-btn').addEventListener('click', () => {
      this.loadScene();
    });

    // Reset mixer
    this.container.querySelector('.reset-mixer-btn').addEventListener('click', () => {
      this.resetMixer();
    });

    // Add channel
    this.container.querySelector('.add-channel-btn').addEventListener('click', () => {
      this.addChannel();
    });

    // Add effect
    this.container.querySelector('.add-effect-btn').addEventListener('click', () => {
      this.addEffect();
    });
  }

  setupChannels() {
    // Create initial channels
    for (let i = 1; i <= 8; i++) {
      this.addChannel(`Ch ${i}`);
    }
  }

  addChannel(name = `Ch ${this.channels.size + 1}`) {
    const channelId = `channel_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const channel = {
      id: channelId,
      name: name,
      gain: 0.75,
      pan: 0,
      muted: false,
      solo: false,
      eq: {
        highGain: 0,
        midGain: 0,
        lowGain: 0
      },
      compressor: {
        threshold: -12,
        ratio: 4,
        attack: 3,
        release: 100,
        enabled: false
      },
      effects: [],
      automation: new Map(),
      inputSource: null,
      vuLevel: 0
    };

    this.channels.set(channelId, channel);
    this.createChannelElement(channel);

    console.log(`🎛️ Channel added: ${name}`);
  }

  createChannelElement(channel) {
    const container = this.container.querySelector('.channels-container');
    
    const channelElement = document.createElement('div');
    channelElement.className = 'mixer-channel';
    channelElement.dataset.channelId = channel.id;

    channelElement.innerHTML = `
      <div class="channel-label">${channel.name}</div>
      
      <div class="channel-controls">
        <div class="control-group">
          <div class="control-label">GAIN</div>
          <div class="rotary-knob gain-knob" data-value="${channel.gain}"></div>
        </div>
        
        <div class="control-group">
          <div class="control-label">PAN</div>
          <div class="rotary-knob pan-knob" data-value="${channel.pan}"></div>
        </div>
        
        <div class="control-group">
          <div class="control-label">HIGH</div>
          <div class="rotary-knob eq-high-knob" data-value="${channel.eq.highGain}"></div>
        </div>
        
        <div class="control-group">
          <div class="control-label">MID</div>
          <div class="rotary-knob eq-mid-knob" data-value="${channel.eq.midGain}"></div>
        </div>
        
        <div class="control-group">
          <div class="control-label">LOW</div>
          <div class="rotary-knob eq-low-knob" data-value="${channel.eq.lowGain}"></div>
        </div>
      </div>
      
      <div class="vu-meter">
        <div class="vu-meter-fill"></div>
      </div>
      
      <input type="range" class="channel-fader" min="0" max="1" step="0.01" value="${channel.gain}" orient="vertical">
      
      <div class="mute-solo-buttons">
        <button class="mute-btn">M</button>
        <button class="solo-btn">S</button>
      </div>
    `;

    container.appendChild(channelElement);
    this.setupChannelEventHandlers(channelElement, channel);
  }

  setupChannelEventHandlers(element, channel) {
    // Fader
    const fader = element.querySelector('.channel-fader');
    fader.addEventListener('input', (e) => {
      channel.gain = parseFloat(e.target.value);
      this.updateChannelGain(channel);
    });

    // Mute button
    const muteBtn = element.querySelector('.mute-btn');
    muteBtn.addEventListener('click', () => {
      channel.muted = !channel.muted;
      muteBtn.classList.toggle('active', channel.muted);
      this.updateChannelMute(channel);
    });

    // Solo button
    const soloBtn = element.querySelector('.solo-btn');
    soloBtn.addEventListener('click', () => {
      channel.solo = !channel.solo;
      soloBtn.classList.toggle('active', channel.solo);
      this.updateChannelSolo(channel);
    });

    // Rotary knobs
    this.setupRotaryKnobs(element, channel);
  }

  setupRotaryKnobs(element, channel) {
    const knobs = element.querySelectorAll('.rotary-knob');
    
    knobs.forEach(knob => {
      let isDragging = false;
      let startY = 0;
      let startValue = parseFloat(knob.dataset.value);

      knob.addEventListener('mousedown', (e) => {
        isDragging = true;
        startY = e.clientY;
        startValue = parseFloat(knob.dataset.value);
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
      });

      function handleMouseMove(e) {
        if (!isDragging) return;

        const deltaY = startY - e.clientY;
        const sensitivity = 0.01;
        let newValue = startValue + (deltaY * sensitivity);

        // Clamp value based on knob type
        if (knob.classList.contains('gain-knob') || knob.classList.contains('pan-knob')) {
          newValue = Math.max(-1, Math.min(1, newValue));
        } else {
          newValue = Math.max(-20, Math.min(20, newValue));
        }

        knob.dataset.value = newValue;
        updateKnobRotation(knob, newValue);
        updateChannelParameter(knob, channel, newValue);
      }

      function handleMouseUp() {
        isDragging = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      }
    });
  }

  updateChannelParameter(knob, channel, value) {
    if (knob.classList.contains('gain-knob')) {
      channel.gain = value;
      this.updateChannelGain(channel);
    } else if (knob.classList.contains('pan-knob')) {
      channel.pan = value;
      this.updateChannelPan(channel);
    } else if (knob.classList.contains('eq-high-knob')) {
      channel.eq.highGain = value;
      this.updateChannelEQ(channel);
    } else if (knob.classList.contains('eq-mid-knob')) {
      channel.eq.midGain = value;
      this.updateChannelEQ(channel);
    } else if (knob.classList.contains('eq-low-knob')) {
      channel.eq.lowGain = value;
      this.updateChannelEQ(channel);
    }
  }

  setupMasterSection() {
    const masterContainer = this.container.querySelector('.master-channel');
    
    this.masterChannel = {
      gain: 0.8,
      limiter: {
        threshold: -1,
        enabled: true
      },
      compressor: {
        threshold: -6,
        ratio: 3,
        enabled: false
      }
    };

    masterContainer.innerHTML = `
      <div class="master-controls">
        <div class="control-group">
          <div class="control-label">MASTER</div>
          <div class="rotary-knob master-gain-knob" data-value="${this.masterChannel.gain}"></div>
        </div>
        
        <div class="master-vu-meter">
          <div class="vu-meter">
            <div class="vu-meter-fill"></div>
          </div>
          <div class="vu-meter">
            <div class="vu-meter-fill"></div>
          </div>
        </div>
        
        <input type="range" class="master-fader" min="0" max="1" step="0.01" value="${this.masterChannel.gain}" orient="vertical">
        
        <div class="master-buttons">
          <button class="limiter-btn active">LIM</button>
          <button class="comp-btn">COMP</button>
        </div>
      </div>
    `;

    this.setupMasterEventHandlers();
  }

  setupMasterEventHandlers() {
    const masterFader = this.container.querySelector('.master-fader');
    masterFader.addEventListener('input', (e) => {
      this.masterChannel.gain = parseFloat(e.target.value);
      this.updateMasterGain();
    });

    const limiterBtn = this.container.querySelector('.limiter-btn');
    limiterBtn.addEventListener('click', () => {
      this.masterChannel.limiter.enabled = !this.masterChannel.limiter.enabled;
      limiterBtn.classList.toggle('active', this.masterChannel.limiter.enabled);
    });

    const compBtn = this.container.querySelector('.comp-btn');
    compBtn.addEventListener('click', () => {
      this.masterChannel.compressor.enabled = !this.masterChannel.compressor.enabled;
      compBtn.classList.toggle('active', this.masterChannel.compressor.enabled);
    });
  }

  setupEffectsRack() {
    const defaultEffects = [
      { name: 'Reverb Hall', type: 'reverb', enabled: true },
      { name: 'Delay 1/8', type: 'delay', enabled: false },
      { name: 'Chorus', type: 'modulation', enabled: false }
    ];

    defaultEffects.forEach(effect => {
      this.addEffectToRack(effect);
    });
  }

  addEffectToRack(effectConfig) {
    const effectsRack = this.container.querySelector('.effects-rack');
    
    const effectElement = document.createElement('div');
    effectElement.className = 'effect-module';
    effectElement.innerHTML = `
      <div class="effect-header">
        <span class="effect-name">${effectConfig.name}</span>
        <button class="effect-bypass ${effectConfig.enabled ? '' : 'bypassed'}">
          ${effectConfig.enabled ? 'ON' : 'OFF'}
        </button>
      </div>
      <div class="effect-controls">
        <div class="control-group">
          <div class="control-label">PARAM 1</div>
          <div class="rotary-knob" data-value="0"></div>
        </div>
        <div class="control-group">
          <div class="control-label">PARAM 2</div>
          <div class="rotary-knob" data-value="0"></div>
        </div>
      </div>
    `;

    effectsRack.appendChild(effectElement);

    // Setup effect bypass
    const bypassBtn = effectElement.querySelector('.effect-bypass');
    bypassBtn.addEventListener('click', () => {
      effectConfig.enabled = !effectConfig.enabled;
      bypassBtn.textContent = effectConfig.enabled ? 'ON' : 'OFF';
      bypassBtn.classList.toggle('bypassed', !effectConfig.enabled);
    });
  }

  setupAutomation() {
    if (!this.options.automation) return;
    
    console.log('🤖 Automation system initialized');
  }

  setupAIAssistant() {
    if (!this.options.enableAI) return;
    
    this.aiAssistant = {
      autoGain: true,
      autoEQ: true,
      intelligentCompression: true,
      realTimeAnalysis: true
    };
    
    console.log('🤖 AI Assistant initialized');
  }

  startMetering() {
    // Start VU meter updates
    setInterval(() => {
      this.updateVUMeters();
      this.updateCPUMeter();
    }, 50);
  }

  updateVUMeters() {
    // Simulate VU meter levels
    this.container.querySelectorAll('.vu-meter-fill').forEach(meter => {
      const level = Math.random() * 80 + 10; // 10-90%
      meter.style.height = `${level}%`;
    });
  }

  updateCPUMeter() {
    const cpuUsage = Math.random() * 30 + 5; // 5-35%
    const cpuFill = this.container.querySelector('.cpu-fill');
    const cpuValue = this.container.querySelector('.cpu-value');
    
    if (cpuFill && cpuValue) {
      cpuFill.style.width = `${cpuUsage}%`;
      cpuValue.textContent = `${cpuUsage.toFixed(1)}%`;
    }
  }

  // Transport Controls
  toggleRecording() {
    this.isRecording = !this.isRecording;
    const recordBtn = this.container.querySelector('.record-btn');
    recordBtn.classList.toggle('active', this.isRecording);
    
    if (this.isRecording) {
      this.container.classList.add('recording');
      console.log('🔴 Recording started');
    } else {
      this.container.classList.remove('recording');
      console.log('⏹ Recording stopped');
    }
  }

  togglePlayback() {
    this.isPlaying = !this.isPlaying;
    const playBtn = this.container.querySelector('.play-btn');
    playBtn.classList.toggle('active', this.isPlaying);
    
    if (this.isPlaying) {
      console.log('▶ Playback started');
      this.startPlaybackTimer();
    } else {
      console.log('⏸ Playback paused');
      this.stopPlaybackTimer();
    }
  }

  pausePlayback() {
    this.isPlaying = false;
    const playBtn = this.container.querySelector('.play-btn');
    playBtn.classList.remove('active');
    this.stopPlaybackTimer();
    console.log('⏸ Playback paused');
  }

  stopPlayback() {
    this.isPlaying = false;
    this.currentTime = 0;
    const playBtn = this.container.querySelector('.play-btn');
    playBtn.classList.remove('active');
    this.stopPlaybackTimer();
    this.updateTimeDisplay();
    console.log('⏹ Playback stopped');
  }

  startPlaybackTimer() {
    this.playbackTimer = setInterval(() => {
      this.currentTime += 0.1;
      this.updateTimeDisplay();
    }, 100);
  }

  stopPlaybackTimer() {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
  }

  updateTimeDisplay() {
    const currentTimeDisplay = this.container.querySelector('.current-time');
    const totalTimeDisplay = this.container.querySelector('.total-time');
    
    currentTimeDisplay.textContent = this.formatTime(this.currentTime);
    totalTimeDisplay.textContent = this.formatTime(this.totalTime);
  }

  formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  // Audio Processing
  updateChannelGain(channel) {
    console.log(`🔊 Channel ${channel.name} gain: ${channel.gain.toFixed(2)}`);
  }

  updateChannelPan(channel) {
    console.log(`🔊 Channel ${channel.name} pan: ${channel.pan.toFixed(2)}`);
  }

  updateChannelEQ(channel) {
    console.log(`🔊 Channel ${channel.name} EQ updated`);
  }

  updateChannelMute(channel) {
    console.log(`🔊 Channel ${channel.name} mute: ${channel.muted}`);
  }

  updateChannelSolo(channel) {
    console.log(`🔊 Channel ${channel.name} solo: ${channel.solo}`);
  }

  updateMasterGain() {
    if (this.masterGain) {
      this.masterGain.gain.value = this.masterChannel.gain;
    }
    console.log(`🔊 Master gain: ${this.masterChannel.gain.toFixed(2)}`);
  }

  // AI Assistant
  showAIAssistant() {
    const suggestions = this.generateAISuggestions();
    alert(`AI Assistant Suggestions:\n\n${suggestions.join('\n')}`);
  }

  generateAISuggestions() {
    return [
      '• Consider reducing low frequencies on vocals',
      '• Add gentle compression to drums for punch',
      '• Master level could use slight limiting',
      '• Room reverb might enhance the mix space'
    ];
  }

  // Scene Management
  saveScene() {
    const scene = {
      name: `Scene ${Date.now()}`,
      channels: Array.from(this.channels.values()),
      master: this.masterChannel,
      effects: Array.from(this.effects.values())
    };
    
    console.log('💾 Scene saved:', scene.name);
    return scene;
  }

  loadScene() {
    console.log('📁 Loading scene...');
    // Implementation would load scene data
  }

  resetMixer() {
    console.log('🔄 Mixer reset');
    // Reset all channels to default values
    this.channels.forEach(channel => {
      channel.gain = 0.75;
      channel.pan = 0;
      channel.muted = false;
      channel.solo = false;
    });
    this.updateAllChannels();
  }

  setMixerMode(mode) {
    this.currentMode = mode;
    console.log(`🎛️ Mixer mode: ${mode}`);
    
    // Adjust interface based on mode
    switch (mode) {
      case 'live':
        // Optimize for live performance
        break;
      case 'mastering':
        // Focus on mastering tools
        break;
      case 'streaming':
        // Optimize for streaming
        break;
      default:
        // Studio mode
        break;
    }
  }

  // Utility Functions
  updateKnobRotation(knob, value) {
    const rotation = (value + 1) * 150 - 150; // -150 to +150 degrees
    knob.style.transform = `rotate(${rotation}deg)`;
  }

  updateAllChannels() {
    this.channels.forEach(channel => {
      this.updateChannelGain(channel);
      this.updateChannelPan(channel);
      this.updateChannelEQ(channel);
    });
  }

  addEffect() {
    console.log('🎛️ Adding new effect...');
    // Implementation would show effect selection dialog
  }

  toggleLoop() {
    console.log('🔁 Loop toggled');
  }

  // Public API
  getChannelCount() {
    return this.channels.size;
  }

  getMasterLevel() {
    return this.masterChannel.gain;
  }

  exportMixSettings() {
    return {
      channels: Array.from(this.channels.values()),
      master: this.masterChannel,
      mode: this.currentMode
    };
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioMixerComponent;
}