/**
 * Ainflue Desktop - AI Processing Panel Component
 * 
 * Advanced AI processing controls for real-time content analysis and optimization
 * Integrates with Ainflue's AI pipeline for intelligent content enhancement
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class AIProcessingPanel {
  constructor(container, aiAnalysisClient, contentProcessor) {
    this.container = container;
    this.aiClient = aiAnalysisClient;
    this.contentProcessor = contentProcessor;
    this.currentTask = null;
    this.processingQueue = [];
    this.supportedFormats = ['video', 'audio', 'image', 'text'];
    
    this.init();
  }

  init() {
    this.createPanelStructure();
    this.setupEventListeners();
    this.initializeAIModules();
  }

  createPanelStructure() {
    this.container.innerHTML = `
      <div class="ai-processing-panel">
        <div class="panel-header">
          <h3><i class="fas fa-brain"></i> AI Processing Studio</h3>
          <div class="panel-controls">
            <button class="btn-toggle-panel" title="Toggle Panel">
              <i class="fas fa-chevron-up"></i>
            </button>
          </div>
        </div>

        <div class="panel-content">
          <!-- Real-time Processing Status -->
          <div class="processing-status">
            <div class="status-indicator">
              <div class="status-light inactive" id="statusLight"></div>
              <span class="status-text">Ready for Processing</span>
            </div>
            <div class="performance-metrics">
              <span class="metric">CPU: <span id="cpuUsage">0%</span></span>
              <span class="metric">GPU: <span id="gpuUsage">0%</span></span>
              <span class="metric">Queue: <span id="queueCount">0</span></span>
            </div>
          </div>

          <!-- AI Processing Modules -->
          <div class="processing-modules">
            <div class="module-group">
              <h4>Content Analysis</h4>
              <div class="module-controls">
                <label class="module-toggle">
                  <input type="checkbox" id="contentRecognition" checked>
                  <span class="toggle-slider"></span>
                  Content Recognition
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="sentimentAnalysis" checked>
                  <span class="toggle-slider"></span>
                  Sentiment Analysis
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="qualityAssessment" checked>
                  <span class="toggle-slider"></span>
                  Quality Assessment
                </label>
              </div>
            </div>

            <div class="module-group">
              <h4>Enhancement & Optimization</h4>
              <div class="module-controls">
                <label class="module-toggle">
                  <input type="checkbox" id="autoEnhancement">
                  <span class="toggle-slider"></span>
                  Auto Enhancement
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="seoOptimization" checked>
                  <span class="toggle-slider"></span>
                  SEO Optimization
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="viralPrediction" checked>
                  <span class="toggle-slider"></span>
                  Viral Prediction
                </label>
              </div>
            </div>

            <div class="module-group">
              <h4>Protection & Security</h4>
              <div class="module-controls">
                <label class="module-toggle">
                  <input type="checkbox" id="copyrightDetection" checked>
                  <span class="toggle-slider"></span>
                  Copyright Detection
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="watermarkInsertion" checked>
                  <span class="toggle-slider"></span>
                  Watermark Insertion
                </label>
                <label class="module-toggle">
                  <input type="checkbox" id="contentValidation" checked>
                  <span class="toggle-slider"></span>
                  Content Validation
                </label>
              </div>
            </div>
          </div>

          <!-- Processing Queue -->
          <div class="processing-queue">
            <h4>Processing Queue</h4>
            <div class="queue-container" id="queueContainer">
              <div class="queue-empty">
                <i class="fas fa-layer-group"></i>
                <p>No items in queue</p>
              </div>
            </div>
          </div>

          <!-- AI Results Display -->
          <div class="ai-results">
            <h4>AI Analysis Results</h4>
            <div class="results-container" id="resultsContainer">
              <div class="results-tabs">
                <button class="tab-btn active" data-tab="overview">Overview</button>
                <button class="tab-btn" data-tab="technical">Technical</button>
                <button class="tab-btn" data-tab="suggestions">Suggestions</button>
                <button class="tab-btn" data-tab="predictions">Predictions</button>
              </div>
              <div class="tab-content" id="overviewTab">
                <div class="no-results">
                  <i class="fas fa-chart-bar"></i>
                  <p>Process content to view AI analysis</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Processing Controls -->
          <div class="processing-controls">
            <button class="btn-primary" id="startProcessing" disabled>
              <i class="fas fa-play"></i>
              Start Processing
            </button>
            <button class="btn-secondary" id="pauseProcessing" disabled>
              <i class="fas fa-pause"></i>
              Pause
            </button>
            <button class="btn-danger" id="stopProcessing" disabled>
              <i class="fas fa-stop"></i>
              Stop
            </button>
            <button class="btn-info" id="exportResults" disabled>
              <i class="fas fa-download"></i>
              Export Results
            </button>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Panel toggle
    this.container.querySelector('.btn-toggle-panel').addEventListener('click', () => {
      this.togglePanel();
    });

    // Module toggles
    this.container.querySelectorAll('.module-toggle input').forEach(toggle => {
      toggle.addEventListener('change', (e) => {
        this.handleModuleToggle(e.target.id, e.target.checked);
      });
    });

    // Processing controls
    this.container.querySelector('#startProcessing').addEventListener('click', () => {
      this.startProcessing();
    });

    this.container.querySelector('#pauseProcessing').addEventListener('click', () => {
      this.pauseProcessing();
    });

    this.container.querySelector('#stopProcessing').addEventListener('click', () => {
      this.stopProcessing();
    });

    this.container.querySelector('#exportResults').addEventListener('click', () => {
      this.exportResults();
    });

    // Results tabs
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchResultsTab(e.target.dataset.tab);
      });
    });

    // Listen for content uploads
    window.electronAPI?.onContentUploaded?.(this.handleContentUpload.bind(this));
  }

  initializeAIModules() {
    this.aiModules = {
      contentRecognition: true,
      sentimentAnalysis: true,
      qualityAssessment: true,
      autoEnhancement: false,
      seoOptimization: true,
      viralPrediction: true,
      copyrightDetection: true,
      watermarkInsertion: true,
      contentValidation: true
    };

    this.updatePerformanceMetrics();
    setInterval(() => this.updatePerformanceMetrics(), 2000);
  }

  async handleContentUpload(contentData) {
    try {
      // Add to processing queue
      const queueItem = {
        id: `task_${Date.now()}`,
        content: contentData,
        timestamp: new Date(),
        status: 'queued',
        progress: 0
      };

      this.processingQueue.push(queueItem);
      this.updateQueueDisplay();
      this.enableProcessingControls();

      // Auto-start if enabled
      if (this.shouldAutoProcess()) {
        await this.startProcessing();
      }

    } catch (error) {
      console.error('Error handling content upload:', error);
      this.showError('Failed to queue content for processing');
    }
  }

  async startProcessing() {
    if (this.processingQueue.length === 0) {
      this.showWarning('No content in queue to process');
      return;
    }

    try {
      this.updateStatus('processing', 'Processing content...');
      this.updateProcessingControls('processing');

      for (const item of this.processingQueue) {
        if (item.status === 'queued') {
          await this.processQueueItem(item);
        }
      }

      this.updateStatus('completed', 'Processing completed');
      this.updateProcessingControls('completed');

    } catch (error) {
      console.error('Processing error:', error);
      this.updateStatus('error', 'Processing failed');
      this.showError('AI processing failed: ' + error.message);
    }
  }

  async processQueueItem(item) {
    try {
      item.status = 'processing';
      this.updateQueueDisplay();

      const results = {};

      // Content Recognition
      if (this.aiModules.contentRecognition) {
        item.progress = 10;
        this.updateQueueDisplay();
        results.recognition = await this.aiClient.analyzeContent(item.content);
      }

      // Sentiment Analysis
      if (this.aiModules.sentimentAnalysis) {
        item.progress = 25;
        this.updateQueueDisplay();
        results.sentiment = await this.aiClient.analyzeSentiment(item.content);
      }

      // Quality Assessment
      if (this.aiModules.qualityAssessment) {
        item.progress = 40;
        this.updateQueueDisplay();
        results.quality = await this.aiClient.assessQuality(item.content);
      }

      // SEO Optimization
      if (this.aiModules.seoOptimization) {
        item.progress = 55;
        this.updateQueueDisplay();
        results.seo = await this.aiClient.optimizeSEO(item.content);
      }

      // Viral Prediction
      if (this.aiModules.viralPrediction) {
        item.progress = 70;
        this.updateQueueDisplay();
        results.viralPrediction = await this.aiClient.predictViralPotential(item.content);
      }

      // Copyright Detection
      if (this.aiModules.copyrightDetection) {
        item.progress = 85;
        this.updateQueueDisplay();
        results.copyright = await this.aiClient.detectCopyright(item.content);
      }

      // Watermark Insertion
      if (this.aiModules.watermarkInsertion) {
        item.progress = 95;
        this.updateQueueDisplay();
        results.watermark = await this.contentProcessor.addWatermark(item.content);
      }

      item.progress = 100;
      item.status = 'completed';
      item.results = results;

      this.updateQueueDisplay();
      this.displayResults(results);

      // Enable export
      this.container.querySelector('#exportResults').disabled = false;

    } catch (error) {
      item.status = 'error';
      item.error = error.message;
      this.updateQueueDisplay();
      throw error;
    }
  }

  pauseProcessing() {
    this.updateStatus('paused', 'Processing paused');
    this.updateProcessingControls('paused');
  }

  stopProcessing() {
    this.processingQueue.forEach(item => {
      if (item.status === 'processing') {
        item.status = 'stopped';
      }
    });

    this.updateStatus('stopped', 'Processing stopped');
    this.updateProcessingControls('stopped');
    this.updateQueueDisplay();
  }

  exportResults() {
    const completedItems = this.processingQueue.filter(item => item.status === 'completed');
    
    if (completedItems.length === 0) {
      this.showWarning('No completed processing results to export');
      return;
    }

    const exportData = {
      timestamp: new Date().toISOString(),
      totalItems: completedItems.length,
      results: completedItems.map(item => ({
        id: item.id,
        contentType: item.content.type,
        timestamp: item.timestamp,
        results: item.results
      }))
    };

    // Trigger download
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai_processing_results_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  displayResults(results) {
    const container = this.container.querySelector('#resultsContainer');
    
    // Update overview tab
    const overviewTab = container.querySelector('#overviewTab');
    overviewTab.innerHTML = this.generateOverviewHTML(results);

    // Show other tabs content
    this.generateTechnicalTab(results);
    this.generateSuggestionsTab(results);
    this.generatePredictionsTab(results);
  }

  generateOverviewHTML(results) {
    const qualityScore = results.quality?.overall || 0;
    const viralScore = results.viralPrediction?.score || 0;
    const sentimentScore = results.sentiment?.score || 0;

    return `
      <div class="results-overview">
        <div class="score-cards">
          <div class="score-card quality">
            <div class="score-icon"><i class="fas fa-star"></i></div>
            <div class="score-value">${qualityScore}%</div>
            <div class="score-label">Quality Score</div>
          </div>
          <div class="score-card viral">
            <div class="score-icon"><i class="fas fa-fire"></i></div>
            <div class="score-value">${viralScore}%</div>
            <div class="score-label">Viral Potential</div>
          </div>
          <div class="score-card sentiment">
            <div class="score-icon"><i class="fas fa-heart"></i></div>
            <div class="score-value">${sentimentScore}%</div>
            <div class="score-label">Sentiment</div>
          </div>
        </div>
        
        <div class="analysis-summary">
          <h5>Key Insights</h5>
          <ul class="insights-list">
            ${this.generateInsightsList(results)}
          </ul>
        </div>
      </div>
    `;
  }

  generateInsightsList(results) {
    const insights = [];
    
    if (results.quality?.overall > 80) {
      insights.push('<li class="insight positive">High quality content detected</li>');
    }
    
    if (results.viralPrediction?.score > 70) {
      insights.push('<li class="insight positive">Strong viral potential identified</li>');
    }
    
    if (results.copyright?.violations?.length > 0) {
      insights.push('<li class="insight warning">Copyright concerns detected</li>');
    }
    
    if (results.seo?.score < 60) {
      insights.push('<li class="insight suggestion">SEO optimization recommended</li>');
    }

    return insights.join('');
  }

  updateQueueDisplay() {
    const container = this.container.querySelector('#queueContainer');
    
    if (this.processingQueue.length === 0) {
      container.innerHTML = `
        <div class="queue-empty">
          <i class="fas fa-layer-group"></i>
          <p>No items in queue</p>
        </div>
      `;
    } else {
      container.innerHTML = this.processingQueue.map(item => `
        <div class="queue-item ${item.status}">
          <div class="item-info">
            <span class="item-name">${item.content.name || 'Unknown Content'}</span>
            <span class="item-type">${item.content.type}</span>
          </div>
          <div class="item-progress">
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${item.progress}%"></div>
            </div>
            <span class="progress-text">${item.progress}%</span>
          </div>
          <div class="item-status">
            <i class="fas ${this.getStatusIcon(item.status)}"></i>
            ${item.status}
          </div>
        </div>
      `).join('');
    }

    // Update queue count
    this.container.querySelector('#queueCount').textContent = this.processingQueue.length;
  }

  getStatusIcon(status) {
    const icons = {
      queued: 'fa-clock',
      processing: 'fa-spinner fa-spin',
      completed: 'fa-check',
      error: 'fa-exclamation-triangle',
      stopped: 'fa-stop',
      paused: 'fa-pause'
    };
    return icons[status] || 'fa-question';
  }

  updateStatus(status, message) {
    const statusLight = this.container.querySelector('#statusLight');
    const statusText = this.container.querySelector('.status-text');
    
    statusLight.className = `status-light ${status}`;
    statusText.textContent = message;
  }

  updateProcessingControls(state) {
    const startBtn = this.container.querySelector('#startProcessing');
    const pauseBtn = this.container.querySelector('#pauseProcessing');
    const stopBtn = this.container.querySelector('#stopProcessing');

    switch (state) {
      case 'processing':
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
        break;
      case 'paused':
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        stopBtn.disabled = false;
        break;
      case 'stopped':
      case 'completed':
        startBtn.disabled = false;
        pauseBtn.disabled = true;
        stopBtn.disabled = true;
        break;
    }
  }

  enableProcessingControls() {
    this.container.querySelector('#startProcessing').disabled = false;
  }

  updatePerformanceMetrics() {
    // Simulate performance metrics
    const cpuUsage = Math.floor(Math.random() * 30) + 10;
    const gpuUsage = Math.floor(Math.random() * 50) + 20;
    
    this.container.querySelector('#cpuUsage').textContent = `${cpuUsage}%`;
    this.container.querySelector('#gpuUsage').textContent = `${gpuUsage}%`;
  }

  shouldAutoProcess() {
    return localStorage.getItem('autoProcessing') === 'true';
  }

  showError(message) {
    // Integration with notification system
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification('error', message);
    } else {
      console.error(message);
    }
  }

  showWarning(message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification('warning', message);
    } else {
      console.warn(message);
    }
  }

  togglePanel() {
    const content = this.container.querySelector('.panel-content');
    const toggleIcon = this.container.querySelector('.btn-toggle-panel i');
    
    content.classList.toggle('collapsed');
    toggleIcon.classList.toggle('fa-chevron-up');
    toggleIcon.classList.toggle('fa-chevron-down');
  }

  handleModuleToggle(moduleId, enabled) {
    this.aiModules[moduleId] = enabled;
    console.log(`AI Module ${moduleId} ${enabled ? 'enabled' : 'disabled'}`);
  }

  switchResultsTab(tabName) {
    // Switch tab logic
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    this.container.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
  }

  addStyles() {
    const styles = `
      <style>
        .ai-processing-panel {
          background: #1a1a1a;
          border: 1px solid #333;
          border-radius: 8px;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: linear-gradient(135deg, #2d2d30 0%, #1e1e1e 100%);
          border-bottom: 1px solid #333;
          border-radius: 8px 8px 0 0;
        }

        .panel-header h3 {
          margin: 0;
          color: #00d4ff;
          font-size: 14px;
          font-weight: 600;
        }

        .panel-content {
          padding: 16px;
          max-height: 600px;
          overflow-y: auto;
        }

        .processing-status {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: #252526;
          border-radius: 6px;
          margin-bottom: 16px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-light {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        .status-light.inactive { background: #666; }
        .status-light.processing { background: #00d4ff; }
        .status-light.completed { background: #4caf50; }
        .status-light.error { background: #f44336; }

        .module-group {
          margin-bottom: 16px;
          padding: 12px;
          background: #2d2d30;
          border-radius: 6px;
        }

        .module-group h4 {
          margin: 0 0 12px 0;
          color: #00d4ff;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .module-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          cursor: pointer;
          font-size: 12px;
        }

        .toggle-slider {
          width: 32px;
          height: 16px;
          background: #444;
          border-radius: 16px;
          position: relative;
          transition: all 0.3s ease;
        }

        .toggle-slider::before {
          content: '';
          position: absolute;
          width: 12px;
          height: 12px;
          background: #fff;
          border-radius: 50%;
          top: 2px;
          left: 2px;
          transition: all 0.3s ease;
        }

        .module-toggle input:checked + .toggle-slider {
          background: #00d4ff;
        }

        .module-toggle input:checked + .toggle-slider::before {
          transform: translateX(16px);
        }

        .processing-controls {
          display: flex;
          gap: 8px;
          margin-top: 16px;
        }

        .btn-primary, .btn-secondary, .btn-danger, .btn-info {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #00d4ff; color: #000; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-danger { background: #f44336; color: #fff; }
        .btn-info { background: #4caf50; color: #fff; }

        .queue-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 12px;
          background: #2d2d30;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .progress-bar {
          width: 80px;
          height: 4px;
          background: #444;
          border-radius: 2px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #00d4ff;
          transition: width 0.3s ease;
        }

        .score-cards {
          display: flex;
          gap: 16px;
          margin-bottom: 16px;
        }

        .score-card {
          flex: 1;
          text-align: center;
          padding: 16px;
          background: #2d2d30;
          border-radius: 6px;
        }

        .score-value {
          font-size: 24px;
          font-weight: bold;
          color: #00d4ff;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;
    
    if (!document.querySelector('#ai-processing-panel-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'ai-processing-panel-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API
  addContentToQueue(content) {
    return this.handleContentUpload(content);
  }

  clearQueue() {
    this.processingQueue = [];
    this.updateQueueDisplay();
    this.updateProcessingControls('stopped');
  }

  getResults() {
    return this.processingQueue
      .filter(item => item.status === 'completed')
      .map(item => item.results);
  }

  destroy() {
    this.stopProcessing();
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AIProcessingPanel;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.AIProcessingPanel = AIProcessingPanel;
}