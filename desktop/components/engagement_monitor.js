/**
 * Ainflue Desktop - Engagement Monitor Component
 * 
 * Real-time engagement tracking and social listening for content creators
 * Implements comprehensive engagement analytics, sentiment analysis, and community insights
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class EngagementMonitor {
  constructor(container, engagementEngine, socialListeningService) {
    this.container = container;
    this.engagementEngine = engagementEngine;
    this.socialListening = socialListeningService;
    this.isMonitoring = false;
    this.engagementData = new Map();
    this.alerts = [];
    
    this.init();
  }

  init() {
    this.createMonitorInterface();
    this.setupEventListeners();
    this.initializeMonitoring();
    this.startRealTimeTracking();
  }

  createMonitorInterface() {
    this.container.innerHTML = `
      <div class="engagement-monitor">
        <div class="monitor-header">
          <h3><i class="fas fa-heart-pulse"></i> Engagement Monitor</h3>
          <div class="monitor-controls">
            <div class="monitoring-status">
              <div class="status-indicator ${this.isMonitoring ? 'active' : 'inactive'}" id="monitoringStatus">
                <div class="status-light"></div>
                <span>${this.isMonitoring ? 'Monitoring' : 'Stopped'}</span>
              </div>
            </div>
            <button class="btn-primary" id="toggleMonitoring">
              <i class="fas ${this.isMonitoring ? 'fa-pause' : 'fa-play'}"></i>
              ${this.isMonitoring ? 'Pause' : 'Start'} Monitoring
            </button>
          </div>
        </div>

        <div class="monitor-content">
          <!-- Real-time Engagement Overview -->
          <div class="engagement-overview">
            <div class="overview-cards">
              <div class="engagement-card total">
                <div class="card-icon"><i class="fas fa-chart-line"></i></div>
                <div class="card-content">
                  <div class="card-value" id="totalEngagement">0</div>
                  <div class="card-label">Total Engagement</div>
                  <div class="card-trend" id="engagementTrend">+0%</div>
                </div>
                <div class="card-sparkline" id="engagementSparkline"></div>
              </div>

              <div class="engagement-card likes">
                <div class="card-icon"><i class="fas fa-thumbs-up"></i></div>
                <div class="card-content">
                  <div class="card-value" id="totalLikes">0</div>
                  <div class="card-label">Likes</div>
                  <div class="card-trend" id="likesTrend">+0%</div>
                </div>
                <div class="card-sparkline" id="likesSparkline"></div>
              </div>

              <div class="engagement-card comments">
                <div class="card-icon"><i class="fas fa-comments"></i></div>
                <div class="card-content">
                  <div class="card-value" id="totalComments">0</div>
                  <div class="card-label">Comments</div>
                  <div class="card-trend" id="commentsTrend">+0%</div>
                </div>
                <div class="card-sparkline" id="commentsSparkline"></div>
              </div>

              <div class="engagement-card shares">
                <div class="card-icon"><i class="fas fa-share"></i></div>
                <div class="card-content">
                  <div class="card-value" id="totalShares">0</div>
                  <div class="card-label">Shares</div>
                  <div class="card-trend" id="sharesTrend">+0%</div>
                </div>
                <div class="card-sparkline" id="sharesSparkline"></div>
              </div>

              <div class="engagement-card sentiment">
                <div class="card-icon"><i class="fas fa-smile"></i></div>
                <div class="card-content">
                  <div class="card-value" id="sentimentScore">0%</div>
                  <div class="card-label">Sentiment Score</div>
                  <div class="card-trend" id="sentimentTrend">+0%</div>
                </div>
                <div class="sentiment-breakdown" id="sentimentBreakdown">
                  <div class="sentiment-bar">
                    <div class="sentiment-positive" style="width: 0%"></div>
                    <div class="sentiment-neutral" style="width: 0%"></div>
                    <div class="sentiment-negative" style="width: 0%"></div>
                  </div>
                </div>
              </div>

              <div class="engagement-card engagement-rate">
                <div class="card-icon"><i class="fas fa-percentage"></i></div>
                <div class="card-content">
                  <div class="card-value" id="engagementRate">0%</div>
                  <div class="card-label">Engagement Rate</div>
                  <div class="card-trend" id="rateTrend">+0%</div>
                </div>
                <div class="rate-gauge" id="rateGauge"></div>
              </div>
            </div>
          </div>

          <!-- Engagement Timeline -->
          <div class="engagement-timeline">
            <div class="timeline-header">
              <h4>Engagement Timeline</h4>
              <div class="timeline-controls">
                <select id="timelineRange">
                  <option value="1h">Last Hour</option>
                  <option value="6h">Last 6 Hours</option>
                  <option value="24h" selected>Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                </select>
                <button class="btn-small" id="refreshTimeline">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
              </div>
            </div>
            <div class="timeline-chart-container">
              <canvas id="engagementTimelineChart" width="800" height="300"></canvas>
            </div>
          </div>

          <!-- Social Listening -->
          <div class="social-listening">
            <div class="listening-tabs">
              <button class="tab-btn active" data-tab="mentions">
                <i class="fas fa-at"></i>
                Mentions
              </button>
              <button class="tab-btn" data-tab="hashtags">
                <i class="fas fa-hashtag"></i>
                Hashtags
              </button>
              <button class="tab-btn" data-tab="keywords">
                <i class="fas fa-key"></i>
                Keywords
              </button>
              <button class="tab-btn" data-tab="competitors">
                <i class="fas fa-users"></i>
                Competitors
              </button>
            </div>

            <!-- Mentions Tab -->
            <div class="tab-content active" id="mentionsTab">
              <div class="mentions-container">
                <div class="mentions-header">
                  <h5>Recent Mentions</h5>
                  <div class="mentions-controls">
                    <select id="mentionsFilter">
                      <option value="all">All Mentions</option>
                      <option value="positive">Positive</option>
                      <option value="neutral">Neutral</option>
                      <option value="negative">Negative</option>
                    </select>
                    <button class="btn-small" id="exportMentions">
                      <i class="fas fa-download"></i>
                      Export
                    </button>
                  </div>
                </div>
                <div class="mentions-list" id="mentionsList">
                  <!-- Mentions will be populated here -->
                </div>
              </div>
            </div>

            <!-- Hashtags Tab -->
            <div class="tab-content" id="hashtagsTab">
              <div class="hashtags-container">
                <div class="hashtags-header">
                  <h5>Trending Hashtags</h5>
                  <div class="hashtags-controls">
                    <select id="hashtagsPeriod">
                      <option value="1h">Last Hour</option>
                      <option value="24h">Last 24 Hours</option>
                      <option value="7d">Last 7 Days</option>
                    </select>
                  </div>
                </div>
                <div class="hashtags-cloud" id="hashtagsCloud">
                  <!-- Hashtags cloud will be populated here -->
                </div>
                <div class="hashtags-performance" id="hashtagsPerformance">
                  <!-- Hashtag performance will be populated here -->
                </div>
              </div>
            </div>

            <!-- Keywords Tab -->
            <div class="tab-content" id="keywordsTab">
              <div class="keywords-container">
                <div class="keywords-header">
                  <h5>Keyword Performance</h5>
                  <button class="btn-primary" id="addKeyword">
                    <i class="fas fa-plus"></i>
                    Add Keyword
                  </button>
                </div>
                <div class="keywords-list" id="keywordsList">
                  <!-- Keywords will be populated here -->
                </div>
              </div>
            </div>

            <!-- Competitors Tab -->
            <div class="tab-content" id="competitorsTab">
              <div class="competitors-container">
                <div class="competitors-header">
                  <h5>Competitor Analysis</h5>
                  <button class="btn-primary" id="addCompetitor">
                    <i class="fas fa-plus"></i>
                    Add Competitor
                  </button>
                </div>
                <div class="competitors-comparison" id="competitorsComparison">
                  <!-- Competitor comparison will be populated here -->
                </div>
              </div>
            </div>
          </div>

          <!-- Engagement Insights -->
          <div class="engagement-insights">
            <div class="insights-header">
              <h4>AI Engagement Insights</h4>
              <button class="btn-secondary" id="generateInsights">
                <i class="fas fa-brain"></i>
                Generate Insights
              </button>
            </div>
            <div class="insights-container" id="insightsContainer">
              <div class="no-insights">
                <i class="fas fa-lightbulb"></i>
                <p>Generate AI insights to understand engagement patterns</p>
              </div>
            </div>
          </div>

          <!-- Engagement Alerts -->
          <div class="engagement-alerts">
            <div class="alerts-header">
              <h4>Engagement Alerts</h4>
              <div class="alerts-controls">
                <button class="btn-small" id="configureAlerts">
                  <i class="fas fa-cog"></i>
                  Configure
                </button>
                <button class="btn-small" id="clearAlerts">
                  <i class="fas fa-trash"></i>
                  Clear All
                </button>
              </div>
            </div>
            <div class="alerts-container" id="alertsContainer">
              <div class="no-alerts">
                <i class="fas fa-bell"></i>
                <p>No engagement alerts</p>
              </div>
            </div>
          </div>

          <!-- Top Engaging Content -->
          <div class="top-engaging-content">
            <div class="content-header">
              <h4>Top Engaging Content</h4>
              <div class="content-filters">
                <select id="contentPeriod">
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                </select>
                <select id="engagementMetric">
                  <option value="total">Total Engagement</option>
                  <option value="rate">Engagement Rate</option>
                  <option value="comments">Comments</option>
                  <option value="shares">Shares</option>
                </select>
              </div>
            </div>
            <div class="content-grid" id="topEngagingContent">
              <!-- Top engaging content will be populated here -->
            </div>
          </div>
        </div>

        <!-- Modals -->
        <div class="modal-overlay" id="alertsModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4>Configure Engagement Alerts</h4>
              <button class="modal-close" id="closeAlertsModal">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <!-- Alert configuration will be populated here -->
            </div>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Monitoring control
    this.container.querySelector('#toggleMonitoring').addEventListener('click', () => {
      this.toggleMonitoring();
    });

    // Timeline controls
    this.container.querySelector('#timelineRange').addEventListener('change', () => {
      this.updateTimelineChart();
    });

    this.container.querySelector('#refreshTimeline').addEventListener('click', () => {
      this.refreshTimeline();
    });

    // Tab switching
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchListeningTab(e.target.dataset.tab);
      });
    });

    // Filters and controls
    this.container.querySelector('#mentionsFilter').addEventListener('change', () => {
      this.filterMentions();
    });

    this.container.querySelector('#hashtagsPeriod').addEventListener('change', () => {
      this.updateHashtagsData();
    });

    // Content filters
    this.container.querySelector('#contentPeriod').addEventListener('change', () => {
      this.updateTopEngagingContent();
    });

    this.container.querySelector('#engagementMetric').addEventListener('change', () => {
      this.updateTopEngagingContent();
    });

    // Action buttons
    this.container.querySelector('#generateInsights').addEventListener('click', () => {
      this.generateEngagementInsights();
    });

    this.container.querySelector('#configureAlerts').addEventListener('click', () => {
      this.showAlertsConfiguration();
    });

    this.container.querySelector('#clearAlerts').addEventListener('click', () => {
      this.clearAllAlerts();
    });

    this.container.querySelector('#addKeyword').addEventListener('click', () => {
      this.showAddKeywordModal();
    });

    this.container.querySelector('#addCompetitor').addEventListener('click', () => {
      this.showAddCompetitorModal();
    });

    // Export functionality
    this.container.querySelector('#exportMentions').addEventListener('click', () => {
      this.exportMentions();
    });

    // Modal controls
    this.container.querySelector('#closeAlertsModal').addEventListener('click', () => {
      this.hideAlertsModal();
    });
  }

  initializeMonitoring() {
    this.loadEngagementData();
    this.initializeCharts();
    this.loadSocialListeningData();
    this.loadTopEngagingContent();
  }

  async startRealTimeTracking() {
    if (this.trackingInterval) return;

    this.isMonitoring = true;
    this.updateMonitoringStatus();

    this.trackingInterval = setInterval(() => {
      this.updateRealTimeData();
    }, 10000); // Update every 10 seconds
  }

  stopRealTimeTracking() {
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }

    this.isMonitoring = false;
    this.updateMonitoringStatus();
  }

  toggleMonitoring() {
    if (this.isMonitoring) {
      this.stopRealTimeTracking();
      this.showInfo('Engagement monitoring stopped');
    } else {
      this.startRealTimeTracking();
      this.showSuccess('Engagement monitoring started');
    }
  }

  updateMonitoringStatus() {
    const statusElement = this.container.querySelector('#monitoringStatus');
    const buttonElement = this.container.querySelector('#toggleMonitoring');
    
    statusElement.className = `status-indicator ${this.isMonitoring ? 'active' : 'inactive'}`;
    statusElement.querySelector('span').textContent = this.isMonitoring ? 'Monitoring' : 'Stopped';
    
    buttonElement.innerHTML = `
      <i class="fas ${this.isMonitoring ? 'fa-pause' : 'fa-play'}"></i>
      ${this.isMonitoring ? 'Pause' : 'Start'} Monitoring
    `;
  }

  async loadEngagementData() {
    try {
      const data = await this.engagementEngine.getEngagementOverview();
      this.updateEngagementCards(data);
    } catch (error) {
      console.error('Failed to load engagement data:', error);
      this.showError('Failed to load engagement data');
    }
  }

  updateEngagementCards(data) {
    const metrics = {
      totalEngagement: data.totalEngagement || 0,
      totalLikes: data.totalLikes || 0,
      totalComments: data.totalComments || 0,
      totalShares: data.totalShares || 0,
      sentimentScore: data.sentimentScore || 0,
      engagementRate: data.engagementRate || 0
    };

    const trends = {
      engagementTrend: data.engagementTrend || 0,
      likesTrend: data.likesTrend || 0,
      commentsTrend: data.commentsTrend || 0,
      sharesTrend: data.sharesTrend || 0,
      sentimentTrend: data.sentimentTrend || 0,
      rateTrend: data.rateTrend || 0
    };

    // Update metric values
    Object.entries(metrics).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        if (key.includes('Rate') || key.includes('Score')) {
          element.textContent = `${value.toFixed(1)}%`;
        } else {
          element.textContent = this.formatNumber(value);
        }
      }
    });

    // Update trends
    Object.entries(trends).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        element.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
        element.className = `card-trend ${value >= 0 ? 'positive' : 'negative'}`;
      }
    });

    // Update sparklines
    this.updateSparklines(data);
    
    // Update sentiment breakdown
    this.updateSentimentBreakdown(data);
    
    // Update engagement rate gauge
    this.updateEngagementGauge(data.engagementRate || 0);
  }

  updateSparklines(data) {
    const sparklineData = {
      engagement: data.engagementHistory || [],
      likes: data.likesHistory || [],
      comments: data.commentsHistory || [],
      shares: data.sharesHistory || []
    };

    Object.entries(sparklineData).forEach(([key, history]) => {
      this.drawSparkline(`${key}Sparkline`, history);
    });
  }

  drawSparkline(elementId, data) {
    const container = this.container.querySelector(`#${elementId}`);
    if (!container || !data.length) return;

    const svg = this.createSVGSparkline(data, 80, 30);
    container.innerHTML = '';
    container.appendChild(svg);
  }

  createSVGSparkline(data, width = 80, height = 30) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    if (data.length < 2) return svg;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');

    const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    polyline.setAttribute('points', points);
    polyline.setAttribute('fill', 'none');
    polyline.setAttribute('stroke', '#4caf50');
    polyline.setAttribute('stroke-width', '2');

    svg.appendChild(polyline);
    return svg;
  }

  updateSentimentBreakdown(data) {
    const sentiment = data.sentiment || { positive: 0, neutral: 0, negative: 0 };
    const total = sentiment.positive + sentiment.neutral + sentiment.negative || 1;

    const positivePercent = (sentiment.positive / total) * 100;
    const neutralPercent = (sentiment.neutral / total) * 100;
    const negativePercent = (sentiment.negative / total) * 100;

    const breakdownElement = this.container.querySelector('#sentimentBreakdown .sentiment-bar');
    if (breakdownElement) {
      breakdownElement.querySelector('.sentiment-positive').style.width = `${positivePercent}%`;
      breakdownElement.querySelector('.sentiment-neutral').style.width = `${neutralPercent}%`;
      breakdownElement.querySelector('.sentiment-negative').style.width = `${negativePercent}%`;
    }
  }

  updateEngagementGauge(rate) {
    const gaugeElement = this.container.querySelector('#rateGauge');
    if (!gaugeElement) return;

    // Create simple gauge visualization
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '60');
    svg.setAttribute('height', '30');
    svg.setAttribute('viewBox', '0 0 60 30');

    const arc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const angle = (rate / 100) * 180;
    const radians = (angle * Math.PI) / 180;
    const x = 30 + 20 * Math.cos(radians);
    const y = 25 - 20 * Math.sin(radians);

    arc.setAttribute('d', `M 10 25 A 20 20 0 0 1 ${x} ${y}`);
    arc.setAttribute('stroke', rate >= 70 ? '#4caf50' : rate >= 40 ? '#ff9800' : '#f44336');
    arc.setAttribute('stroke-width', '3');
    arc.setAttribute('fill', 'none');

    svg.appendChild(arc);
    gaugeElement.innerHTML = '';
    gaugeElement.appendChild(svg);
  }

  initializeCharts() {
    const timelineCtx = this.container.querySelector('#engagementTimelineChart');
    if (timelineCtx) {
      this.timelineChart = this.createChart(timelineCtx, 'line');
      this.updateTimelineChart();
    }
  }

  createChart(canvas, type) {
    const ctx = canvas.getContext('2d');
    return {
      canvas,
      type,
      update: (data) => this.drawChart(ctx, data, type),
      destroy: () => ctx.clearRect(0, 0, canvas.width, canvas.height)
    };
  }

  drawChart(ctx, data, type) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    
    if (type === 'line') {
      this.drawTimelineChart(ctx, data);
    }
  }

  drawTimelineChart(ctx, data = {}) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 40;

    // Mock timeline data
    const datasets = data.datasets || [
      {
        label: 'Likes',
        data: this.generateMockTimeSeries(24),
        color: '#4caf50'
      },
      {
        label: 'Comments',
        data: this.generateMockTimeSeries(24),
        color: '#2196f3'
      },
      {
        label: 'Shares',
        data: this.generateMockTimeSeries(24),
        color: '#ff9800'
      }
    ];

    // Draw grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for (let i = 1; i < 5; i++) {
      const y = height * (i / 5);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw datasets
    datasets.forEach(dataset => {
      const points = dataset.data.map((value, index) => ({
        x: padding + (index * (width - 2 * padding) / (dataset.data.length - 1)),
        y: height - padding - (value / 100) * (height - 2 * padding)
      }));

      ctx.strokeStyle = dataset.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      points.forEach(point => ctx.lineTo(point.x, point.y));
      ctx.stroke();
    });

    // Draw legend
    datasets.forEach((dataset, index) => {
      const legendY = 20 + index * 20;
      ctx.fillStyle = dataset.color;
      ctx.fillRect(width - 120, legendY, 12, 12);
      ctx.fillStyle = '#fff';
      ctx.font = '12px Arial';
      ctx.fillText(dataset.label, width - 100, legendY + 9);
    });
  }

  generateMockTimeSeries(points) {
    return Array.from({ length: points }, () => Math.floor(Math.random() * 100));
  }

  async updateRealTimeData() {
    if (!this.isMonitoring) return;

    try {
      const realtimeData = await this.engagementEngine.getRealTimeData();
      this.updateEngagementCards(realtimeData);
      this.checkForAlerts(realtimeData);
    } catch (error) {
      console.error('Failed to update real-time data:', error);
    }
  }

  switchListeningTab(tabName) {
    // Update tab buttons
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    this.container.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    this.container.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    this.container.querySelector(`#${tabName}Tab`).classList.add('active');

    // Load tab-specific data
    switch (tabName) {
      case 'mentions':
        this.loadMentions();
        break;
      case 'hashtags':
        this.loadHashtags();
        break;
      case 'keywords':
        this.loadKeywords();
        break;
      case 'competitors':
        this.loadCompetitors();
        break;
    }
  }

  async loadMentions() {
    try {
      const mentions = await this.socialListening.getMentions();
      this.displayMentions(mentions);
    } catch (error) {
      console.error('Failed to load mentions:', error);
    }
  }

  displayMentions(mentions) {
    const container = this.container.querySelector('#mentionsList');
    
    if (!mentions || mentions.length === 0) {
      container.innerHTML = `
        <div class="no-mentions">
          <i class="fas fa-search"></i>
          <p>No mentions found</p>
        </div>
      `;
      return;
    }

    container.innerHTML = mentions.map(mention => `
      <div class="mention-item ${mention.sentiment}">
        <div class="mention-header">
          <div class="mention-author">
            <img src="${mention.author.avatar}" alt="${mention.author.name}" class="author-avatar" />
            <div class="author-info">
              <span class="author-name">${mention.author.name}</span>
              <span class="author-handle">@${mention.author.handle}</span>
            </div>
          </div>
          <div class="mention-meta">
            <span class="mention-platform">${mention.platform}</span>
            <span class="mention-time">${this.formatTimeAgo(mention.timestamp)}</span>
          </div>
        </div>
        <div class="mention-content">
          <p class="mention-text">${mention.text}</p>
          <div class="mention-engagement">
            <span class="engagement-metric">
              <i class="fas fa-heart"></i>
              ${this.formatNumber(mention.likes)}
            </span>
            <span class="engagement-metric">
              <i class="fas fa-comment"></i>
              ${this.formatNumber(mention.replies)}
            </span>
            <span class="engagement-metric">
              <i class="fas fa-retweet"></i>
              ${this.formatNumber(mention.retweets)}
            </span>
          </div>
        </div>
        <div class="mention-sentiment">
          <span class="sentiment-label ${mention.sentiment}">${mention.sentiment}</span>
          <span class="sentiment-score">${mention.sentimentScore}%</span>
        </div>
      </div>
    `).join('');
  }

  async loadHashtags() {
    try {
      const hashtags = await this.socialListening.getHashtags();
      this.displayHashtags(hashtags);
    } catch (error) {
      console.error('Failed to load hashtags:', error);
    }
  }

  displayHashtags(hashtags) {
    const cloudContainer = this.container.querySelector('#hashtagsCloud');
    const performanceContainer = this.container.querySelector('#hashtagsPerformance');
    
    // Display hashtag cloud
    if (hashtags && hashtags.length > 0) {
      cloudContainer.innerHTML = hashtags.map(hashtag => `
        <span class="hashtag-item" style="font-size: ${12 + (hashtag.weight * 8)}px;">
          #${hashtag.tag}
        </span>
      `).join('');

      // Display performance table
      performanceContainer.innerHTML = `
        <table class="hashtags-table">
          <thead>
            <tr>
              <th>Hashtag</th>
              <th>Mentions</th>
              <th>Reach</th>
              <th>Engagement</th>
              <th>Trend</th>
            </tr>
          </thead>
          <tbody>
            ${hashtags.slice(0, 10).map(hashtag => `
              <tr>
                <td>#${hashtag.tag}</td>
                <td>${this.formatNumber(hashtag.mentions)}</td>
                <td>${this.formatNumber(hashtag.reach)}</td>
                <td>${hashtag.engagement.toFixed(1)}%</td>
                <td class="trend ${hashtag.trend >= 0 ? 'positive' : 'negative'}">
                  ${hashtag.trend >= 0 ? '+' : ''}${hashtag.trend.toFixed(1)}%
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } else {
      cloudContainer.innerHTML = '<p class="no-data">No hashtag data available</p>';
      performanceContainer.innerHTML = '';
    }
  }

  async generateEngagementInsights() {
    try {
      this.showInsightsLoading(true);
      
      const engagementData = await this.engagementEngine.getAnalyticsData();
      const insights = await this.engagementEngine.generateInsights(engagementData);
      
      this.displayInsights(insights);
      
    } catch (error) {
      console.error('Failed to generate insights:', error);
      this.showError('Failed to generate engagement insights');
    } finally {
      this.showInsightsLoading(false);
    }
  }

  displayInsights(insights) {
    const container = this.container.querySelector('#insightsContainer');
    
    container.innerHTML = `
      <div class="insights-list">
        ${insights.map(insight => `
          <div class="insight-item ${insight.type}">
            <div class="insight-header">
              <div class="insight-icon">
                <i class="fas ${insight.icon}"></i>
              </div>
              <div class="insight-title">${insight.title}</div>
              <div class="insight-impact ${insight.impact}">${insight.impact}</div>
            </div>
            <p class="insight-description">${insight.description}</p>
            <div class="insight-actions">
              <button class="btn-small primary" onclick="window.engagementMonitor?.applyInsight('${insight.id}')">
                Apply Recommendation
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  checkForAlerts(data) {
    const alerts = [];

    // Check for engagement drops
    if (data.engagementTrend < -10) {
      alerts.push({
        id: `alert_${Date.now()}`,
        type: 'warning',
        title: 'Engagement Drop Detected',
        message: `Engagement has dropped by ${Math.abs(data.engagementTrend).toFixed(1)}%`,
        timestamp: new Date()
      });
    }

    // Check for negative sentiment spike
    if (data.sentiment.negative > 30) {
      alerts.push({
        id: `alert_${Date.now()}_1`,
        type: 'danger',
        title: 'Negative Sentiment Alert',
        message: `Negative sentiment is unusually high (${data.sentiment.negative}%)`,
        timestamp: new Date()
      });
    }

    // Check for viral content
    if (data.engagementTrend > 50) {
      alerts.push({
        id: `alert_${Date.now()}_2`,
        type: 'success',
        title: 'Viral Content Detected',
        message: `Content is going viral! Engagement up ${data.engagementTrend.toFixed(1)}%`,
        timestamp: new Date()
      });
    }

    if (alerts.length > 0) {
      this.addAlerts(alerts);
    }
  }

  addAlerts(alerts) {
    this.alerts.unshift(...alerts);
    this.displayAlerts();
    
    // Show notification for new alerts
    alerts.forEach(alert => {
      this.showNotification(alert.type, alert.message);
    });
  }

  displayAlerts() {
    const container = this.container.querySelector('#alertsContainer');
    
    if (this.alerts.length === 0) {
      container.innerHTML = `
        <div class="no-alerts">
          <i class="fas fa-bell"></i>
          <p>No engagement alerts</p>
        </div>
      `;
      return;
    }

    container.innerHTML = this.alerts.slice(0, 10).map(alert => `
      <div class="alert-item ${alert.type}">
        <div class="alert-icon">
          <i class="fas ${this.getAlertIcon(alert.type)}"></i>
        </div>
        <div class="alert-content">
          <h6 class="alert-title">${alert.title}</h6>
          <p class="alert-message">${alert.message}</p>
          <span class="alert-time">${this.formatTimeAgo(alert.timestamp)}</span>
        </div>
        <button class="alert-dismiss" onclick="window.engagementMonitor?.dismissAlert('${alert.id}')">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `).join('');
  }

  getAlertIcon(type) {
    const icons = {
      success: 'fa-check-circle',
      warning: 'fa-exclamation-triangle',
      danger: 'fa-exclamation-circle',
      info: 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
  }

  // Utility methods
  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  formatTimeAgo(date) {
    const diff = Date.now() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  }

  showInsightsLoading(show) {
    const button = this.container.querySelector('#generateInsights');
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
      button.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-brain"></i> Generate Insights';
      button.disabled = false;
    }
  }

  showNotification(type, message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  showError(message) {
    this.showNotification('error', message);
  }

  showSuccess(message) {
    this.showNotification('success', message);
  }

  showInfo(message) {
    this.showNotification('info', message);
  }

  addStyles() {
    const styles = `
      <style>
        .engagement-monitor {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .monitor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);
          border-bottom: 1px solid #333;
        }

        .monitor-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .monitor-controls {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #fff;
        }

        .status-light {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #666;
        }

        .status-indicator.active .status-light {
          background: #4caf50;
          animation: pulse 2s infinite;
        }

        .monitor-content {
          padding: 20px;
        }

        .overview-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .engagement-card {
          background: #252526;
          border-radius: 8px;
          padding: 16px;
          border-left: 4px solid #e91e63;
          position: relative;
        }

        .engagement-card.likes { border-left-color: #4caf50; }
        .engagement-card.comments { border-left-color: #2196f3; }
        .engagement-card.shares { border-left-color: #ff9800; }
        .engagement-card.sentiment { border-left-color: #9c27b0; }
        .engagement-card.engagement-rate { border-left-color: #00bcd4; }

        .card-icon {
          font-size: 24px;
          color: #e91e63;
          margin-bottom: 8px;
        }

        .card-value {
          font-size: 24px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 4px;
        }

        .card-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .card-trend {
          font-size: 12px;
          font-weight: 600;
        }

        .card-trend.positive { color: #4caf50; }
        .card-trend.negative { color: #f44336; }

        .card-sparkline {
          position: absolute;
          bottom: 8px;
          right: 8px;
          width: 80px;
          height: 30px;
        }

        .sentiment-bar {
          display: flex;
          height: 4px;
          border-radius: 2px;
          overflow: hidden;
          margin-top: 4px;
        }

        .sentiment-positive { background: #4caf50; }
        .sentiment-neutral { background: #ff9800; }
        .sentiment-negative { background: #f44336; }

        .rate-gauge {
          position: absolute;
          bottom: 8px;
          right: 8px;
          width: 60px;
          height: 30px;
        }

        .engagement-timeline,
        .social-listening,
        .engagement-insights,
        .engagement-alerts,
        .top-engaging-content {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .timeline-header,
        .insights-header,
        .alerts-header,
        .content-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .timeline-header h4,
        .insights-header h4,
        .alerts-header h4,
        .content-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .timeline-controls,
        .alerts-controls,
        .content-filters {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .timeline-controls select,
        .content-filters select {
          padding: 4px 8px;
          background: #1a1a1a;
          border: 1px solid #444;
          border-radius: 4px;
          color: #fff;
          font-size: 12px;
        }

        .listening-tabs {
          display: flex;
          background: #1a1a1a;
          border-radius: 6px 6px 0 0;
          overflow: hidden;
          margin-bottom: 0;
        }

        .tab-btn {
          flex: 1;
          padding: 12px 16px;
          background: none;
          border: none;
          color: #ccc;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 6px;
          justify-content: center;
        }

        .tab-btn.active {
          background: #e91e63;
          color: #fff;
        }

        .tab-content {
          display: none;
          background: #1a1a1a;
          border-radius: 0 0 6px 6px;
          padding: 20px;
        }

        .tab-content.active {
          display: block;
        }

        .mention-item {
          background: #252526;
          border-radius: 6px;
          padding: 16px;
          margin-bottom: 12px;
          border-left: 4px solid #666;
        }

        .mention-item.positive { border-left-color: #4caf50; }
        .mention-item.neutral { border-left-color: #ff9800; }
        .mention-item.negative { border-left-color: #f44336; }

        .mention-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .mention-author {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .author-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          object-fit: cover;
        }

        .author-name {
          font-weight: 600;
          color: #fff;
          font-size: 14px;
        }

        .author-handle {
          color: #999;
          font-size: 12px;
        }

        .mention-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 2px;
        }

        .mention-platform {
          background: #444;
          color: #fff;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          text-transform: uppercase;
        }

        .mention-time {
          color: #999;
          font-size: 10px;
        }

        .mention-text {
          color: #ccc;
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 8px;
        }

        .mention-engagement {
          display: flex;
          gap: 16px;
        }

        .engagement-metric {
          display: flex;
          align-items: center;
          gap: 4px;
          color: #999;
          font-size: 12px;
        }

        .mention-sentiment {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 8px;
        }

        .sentiment-label {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .sentiment-label.positive { background: #4caf50; color: #fff; }
        .sentiment-label.neutral { background: #ff9800; color: #fff; }
        .sentiment-label.negative { background: #f44336; color: #fff; }

        .hashtags-cloud {
          margin-bottom: 20px;
          padding: 16px;
          background: #1a1a1a;
          border-radius: 6px;
        }

        .hashtag-item {
          display: inline-block;
          margin: 4px 8px;
          color: #e91e63;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .hashtag-item:hover {
          color: #fff;
        }

        .hashtags-table {
          width: 100%;
          border-collapse: collapse;
          background: #252526;
          border-radius: 6px;
          overflow: hidden;
        }

        .hashtags-table th,
        .hashtags-table td {
          padding: 8px 12px;
          text-align: left;
          border-bottom: 1px solid #333;
        }

        .hashtags-table th {
          background: #333;
          font-weight: 600;
          font-size: 12px;
          text-transform: uppercase;
        }

        .hashtags-table .trend.positive { color: #4caf50; }
        .hashtags-table .trend.negative { color: #f44336; }

        .alert-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #252526;
          border-radius: 6px;
          margin-bottom: 8px;
          border-left: 4px solid #666;
        }

        .alert-item.success { border-left-color: #4caf50; }
        .alert-item.warning { border-left-color: #ff9800; }
        .alert-item.danger { border-left-color: #f44336; }
        .alert-item.info { border-left-color: #2196f3; }

        .alert-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
        }

        .alert-item.success .alert-icon { background: #4caf50; color: #fff; }
        .alert-item.warning .alert-icon { background: #ff9800; color: #fff; }
        .alert-item.danger .alert-icon { background: #f44336; color: #fff; }
        .alert-item.info .alert-icon { background: #2196f3; color: #fff; }

        .alert-content {
          flex: 1;
        }

        .alert-title {
          margin: 0 0 4px 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .alert-message {
          margin: 0 0 4px 0;
          color: #ccc;
          font-size: 12px;
        }

        .alert-time {
          color: #999;
          font-size: 10px;
        }

        .alert-dismiss {
          background: none;
          border: none;
          color: #666;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.3s ease;
        }

        .alert-dismiss:hover {
          background: #444;
          color: #fff;
        }

        .btn-primary, .btn-secondary, .btn-small {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #e91e63; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }

        .no-mentions,
        .no-insights,
        .no-alerts {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }

        .no-mentions i,
        .no-insights i,
        .no-alerts i {
          font-size: 48px;
          margin-bottom: 16px;
          color: #444;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;
    
    if (!document.querySelector('#engagement-monitor-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'engagement-monitor-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  refreshData() {
    this.loadEngagementData();
    this.loadSocialListeningData();
  }

  exportEngagementData() {
    const data = {
      timestamp: new Date().toISOString(),
      engagement: this.getEngagementMetrics(),
      mentions: this.getMentionsData(),
      alerts: this.alerts
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `engagement_data_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  dismissAlert(alertId) {
    this.alerts = this.alerts.filter(alert => alert.id !== alertId);
    this.displayAlerts();
  }

  clearAllAlerts() {
    this.alerts = [];
    this.displayAlerts();
    this.showSuccess('All alerts cleared');
  }

  destroy() {
    this.stopRealTimeTracking();
    
    if (this.timelineChart) {
      this.timelineChart.destroy();
    }
    
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = EngagementMonitor;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.EngagementMonitor = EngagementMonitor;
  window.engagementMonitor = null; // Will be set when instantiated
}