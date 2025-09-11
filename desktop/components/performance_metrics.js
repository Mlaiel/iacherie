/**
 * Ainflue Desktop - Performance Metrics Component
 * 
 * Advanced performance tracking and analytics for content optimization
 * Implements real-time metrics monitoring, A/B testing, and performance insights
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class PerformanceMetrics {
  constructor(container, metricsEngine, performanceTracker) {
    this.container = container;
    this.metricsEngine = metricsEngine;
    this.performanceTracker = performanceTracker;
    this.currentView = 'overview';
    this.realTimeEnabled = true;
    this.updateInterval = null;
    
    this.init();
  }

  init() {
    this.createMetricsInterface();
    this.setupEventListeners();
    this.initializeMetrics();
    this.startRealTimeUpdates();
  }

  createMetricsInterface() {
    this.container.innerHTML = `
      <div class="performance-metrics">
        <div class="metrics-header">
          <h3><i class="fas fa-tachometer-alt"></i> Performance Metrics</h3>
          <div class="header-controls">
            <div class="real-time-toggle">
              <label class="toggle-switch">
                <input type="checkbox" id="realTimeToggle" checked>
                <span class="toggle-slider"></span>
                Real-time
              </label>
            </div>
            <button class="btn-secondary" id="exportMetrics">
              <i class="fas fa-download"></i>
              Export
            </button>
          </div>
        </div>

        <div class="metrics-content">
          <!-- Performance Overview -->
          <div class="performance-overview">
            <div class="overview-grid">
              <!-- Key Performance Indicators -->
              <div class="kpi-section">
                <h4>Key Performance Indicators</h4>
                <div class="kpi-cards">
                  <div class="kpi-card views">
                    <div class="kpi-icon"><i class="fas fa-eye"></i></div>
                    <div class="kpi-content">
                      <div class="kpi-value" id="totalViews">0</div>
                      <div class="kpi-label">Total Views</div>
                      <div class="kpi-change" id="viewsChange">+0%</div>
                    </div>
                    <div class="kpi-chart" id="viewsChart"></div>
                  </div>

                  <div class="kpi-card engagement">
                    <div class="kpi-icon"><i class="fas fa-heart"></i></div>
                    <div class="kpi-content">
                      <div class="kpi-value" id="engagementRate">0%</div>
                      <div class="kpi-label">Engagement Rate</div>
                      <div class="kpi-change" id="engagementChange">+0%</div>
                    </div>
                    <div class="kpi-chart" id="engagementChart"></div>
                  </div>

                  <div class="kpi-card retention">
                    <div class="kpi-icon"><i class="fas fa-users"></i></div>
                    <div class="kpi-content">
                      <div class="kpi-value" id="retentionRate">0%</div>
                      <div class="kpi-label">Retention Rate</div>
                      <div class="kpi-change" id="retentionChange">+0%</div>
                    </div>
                    <div class="kpi-chart" id="retentionChart"></div>
                  </div>

                  <div class="kpi-card conversion">
                    <div class="kpi-icon"><i class="fas fa-convert"></i></div>
                    <div class="kpi-content">
                      <div class="kpi-value" id="conversionRate">0%</div>
                      <div class="kpi-label">Conversion Rate</div>
                      <div class="kpi-change" id="conversionChange">+0%</div>
                    </div>
                    <div class="kpi-chart" id="conversionChart"></div>
                  </div>
                </div>
              </div>

              <!-- Performance Score -->
              <div class="performance-score-section">
                <h4>Overall Performance Score</h4>
                <div class="score-container">
                  <div class="score-circle" id="performanceScoreCircle">
                    <div class="score-value" id="performanceScore">0</div>
                    <div class="score-label">Performance Score</div>
                  </div>
                  <div class="score-breakdown">
                    <div class="score-item">
                      <span class="score-metric">Content Quality</span>
                      <div class="score-bar">
                        <div class="score-fill" id="qualityScore" style="width: 0%"></div>
                      </div>
                      <span class="score-value" id="qualityValue">0%</span>
                    </div>
                    <div class="score-item">
                      <span class="score-metric">Audience Engagement</span>
                      <div class="score-bar">
                        <div class="score-fill" id="audienceScore" style="width: 0%"></div>
                      </div>
                      <span class="score-value" id="audienceValue">0%</span>
                    </div>
                    <div class="score-item">
                      <span class="score-metric">Platform Optimization</span>
                      <div class="score-bar">
                        <div class="score-fill" id="platformScore" style="width: 0%"></div>
                      </div>
                      <span class="score-value" id="platformValue">0%</span>
                    </div>
                    <div class="score-item">
                      <span class="score-metric">Growth Rate</span>
                      <div class="score-bar">
                        <div class="score-fill" id="growthScore" style="width: 0%"></div>
                      </div>
                      <span class="score-value" id="growthValue">0%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Detailed Analytics -->
          <div class="detailed-analytics">
            <div class="analytics-tabs">
              <button class="tab-btn active" data-tab="audience">
                <i class="fas fa-users"></i>
                Audience Analytics
              </button>
              <button class="tab-btn" data-tab="content">
                <i class="fas fa-play"></i>
                Content Performance
              </button>
              <button class="tab-btn" data-tab="platforms">
                <i class="fas fa-share-alt"></i>
                Platform Analytics
              </button>
              <button class="tab-btn" data-tab="realtime">
                <i class="fas fa-broadcast-tower"></i>
                Real-time
              </button>
            </div>

            <!-- Audience Analytics Tab -->
            <div class="tab-content active" id="audienceTab">
              <div class="audience-analytics">
                <div class="audience-grid">
                  <div class="demographics-chart">
                    <h5>Audience Demographics</h5>
                    <div class="demographics-container">
                      <canvas id="demographicsChart" width="400" height="300"></canvas>
                    </div>
                  </div>
                  
                  <div class="audience-behavior">
                    <h5>Audience Behavior</h5>
                    <div class="behavior-metrics">
                      <div class="behavior-item">
                        <span class="behavior-label">Average Watch Time</span>
                        <span class="behavior-value" id="avgWatchTime">0:00</span>
                        <div class="behavior-trend positive" id="watchTimeTrend">+5.2%</div>
                      </div>
                      <div class="behavior-item">
                        <span class="behavior-label">Click-through Rate</span>
                        <span class="behavior-value" id="clickThroughRate">0%</span>
                        <div class="behavior-trend" id="ctrTrend">+2.1%</div>
                      </div>
                      <div class="behavior-item">
                        <span class="behavior-label">Bounce Rate</span>
                        <span class="behavior-value" id="bounceRate">0%</span>
                        <div class="behavior-trend negative" id="bounceTrend">-1.3%</div>
                      </div>
                      <div class="behavior-item">
                        <span class="behavior-label">Return Visitors</span>
                        <span class="behavior-value" id="returnVisitors">0%</span>
                        <div class="behavior-trend positive" id="returnTrend">+8.7%</div>
                      </div>
                    </div>
                  </div>

                  <div class="geographic-distribution">
                    <h5>Geographic Distribution</h5>
                    <div class="geo-list" id="geoList">
                      <!-- Geographic data will be populated here -->
                    </div>
                  </div>

                  <div class="audience-growth">
                    <h5>Audience Growth</h5>
                    <div class="growth-chart-container">
                      <canvas id="audienceGrowthChart" width="600" height="200"></canvas>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Content Performance Tab -->
            <div class="tab-content" id="contentTab">
              <div class="content-performance">
                <div class="content-filters">
                  <select id="contentTimeframe">
                    <option value="7d">Last 7 days</option>
                    <option value="30d">Last 30 days</option>
                    <option value="90d">Last 90 days</option>
                    <option value="1y">Last year</option>
                  </select>
                  <select id="contentType">
                    <option value="all">All Content</option>
                    <option value="video">Videos</option>
                    <option value="audio">Audio</option>
                    <option value="image">Images</option>
                    <option value="text">Text</option>
                  </select>
                  <select id="contentSort">
                    <option value="views">Sort by Views</option>
                    <option value="engagement">Sort by Engagement</option>
                    <option value="revenue">Sort by Revenue</option>
                    <option value="date">Sort by Date</option>
                  </select>
                </div>

                <div class="content-table-container">
                  <table class="content-table">
                    <thead>
                      <tr>
                        <th>Content</th>
                        <th>Type</th>
                        <th>Views</th>
                        <th>Engagement</th>
                        <th>Revenue</th>
                        <th>Performance</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody id="contentTableBody">
                      <!-- Content data will be populated here -->
                    </tbody>
                  </table>
                </div>

                <div class="content-insights">
                  <h5>Content Insights</h5>
                  <div class="insights-grid" id="contentInsights">
                    <!-- Insights will be populated here -->
                  </div>
                </div>
              </div>
            </div>

            <!-- Platform Analytics Tab -->
            <div class="tab-content" id="platformsTab">
              <div class="platform-analytics">
                <div class="platform-comparison">
                  <h5>Platform Performance Comparison</h5>
                  <div class="comparison-chart-container">
                    <canvas id="platformComparisonChart" width="800" height="400"></canvas>
                  </div>
                </div>

                <div class="platform-breakdown">
                  <h5>Platform Breakdown</h5>
                  <div class="platform-cards" id="platformCards">
                    <!-- Platform cards will be populated here -->
                  </div>
                </div>

                <div class="cross-platform-insights">
                  <h5>Cross-Platform Insights</h5>
                  <div class="insights-container" id="crossPlatformInsights">
                    <!-- Cross-platform insights will be populated here -->
                  </div>
                </div>
              </div>
            </div>

            <!-- Real-time Tab -->
            <div class="tab-content" id="realtimeTab">
              <div class="realtime-analytics">
                <div class="realtime-overview">
                  <h5>Live Activity</h5>
                  <div class="live-metrics">
                    <div class="live-metric">
                      <span class="live-label">Active Viewers</span>
                      <span class="live-value" id="activeViewers">0</span>
                      <div class="live-indicator active"></div>
                    </div>
                    <div class="live-metric">
                      <span class="live-label">Live Engagement</span>
                      <span class="live-value" id="liveEngagement">0</span>
                      <div class="live-indicator"></div>
                    </div>
                    <div class="live-metric">
                      <span class="live-label">Peak Concurrent</span>
                      <span class="live-value" id="peakConcurrent">0</span>
                      <div class="live-indicator"></div>
                    </div>
                  </div>
                </div>

                <div class="realtime-chart">
                  <h5>Real-time Activity Stream</h5>
                  <div class="activity-chart-container">
                    <canvas id="realtimeChart" width="800" height="300"></canvas>
                  </div>
                </div>

                <div class="activity-feed">
                  <h5>Activity Feed</h5>
                  <div class="feed-container" id="activityFeed">
                    <!-- Real-time activity feed will be populated here -->
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Performance Alerts -->
          <div class="performance-alerts">
            <div class="alerts-header">
              <h4>Performance Alerts</h4>
              <button class="btn-small" id="configureAlerts">
                <i class="fas fa-cog"></i>
                Configure
              </button>
            </div>
            <div class="alerts-container" id="alertsContainer">
              <div class="no-alerts">
                <i class="fas fa-bell"></i>
                <p>No performance alerts</p>
              </div>
            </div>
          </div>

          <!-- Performance Recommendations -->
          <div class="performance-recommendations">
            <div class="recommendations-header">
              <h4>AI Performance Recommendations</h4>
              <button class="btn-primary" id="generateRecommendations">
                <i class="fas fa-brain"></i>
                Generate Insights
              </button>
            </div>
            <div class="recommendations-container" id="recommendationsContainer">
              <div class="no-recommendations">
                <i class="fas fa-lightbulb"></i>
                <p>Generate AI insights to optimize performance</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Real-time toggle
    this.container.querySelector('#realTimeToggle').addEventListener('change', (e) => {
      this.toggleRealTime(e.target.checked);
    });

    // Export functionality
    this.container.querySelector('#exportMetrics').addEventListener('click', () => {
      this.exportMetrics();
    });

    // Tab switching
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Content filters
    this.container.querySelector('#contentTimeframe').addEventListener('change', () => {
      this.updateContentPerformance();
    });

    this.container.querySelector('#contentType').addEventListener('change', () => {
      this.updateContentPerformance();
    });

    this.container.querySelector('#contentSort').addEventListener('change', () => {
      this.updateContentPerformance();
    });

    // Recommendations
    this.container.querySelector('#generateRecommendations').addEventListener('click', () => {
      this.generateRecommendations();
    });

    // Alerts configuration
    this.container.querySelector('#configureAlerts').addEventListener('click', () => {
      this.showAlertsConfiguration();
    });
  }

  initializeMetrics() {
    this.loadPerformanceData();
    this.initializeCharts();
    this.loadContentPerformance();
    this.loadPlatformAnalytics();
  }

  startRealTimeUpdates() {
    if (this.realTimeEnabled) {
      this.updateInterval = setInterval(() => {
        this.updateRealTimeMetrics();
      }, 5000); // Update every 5 seconds
    }
  }

  stopRealTimeUpdates() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  toggleRealTime(enabled) {
    this.realTimeEnabled = enabled;
    
    if (enabled) {
      this.startRealTimeUpdates();
      this.showSuccess('Real-time updates enabled');
    } else {
      this.stopRealTimeUpdates();
      this.showInfo('Real-time updates disabled');
    }
  }

  async loadPerformanceData() {
    try {
      const data = await this.performanceTracker.getOverviewData();
      this.updateKPIs(data);
      this.updatePerformanceScore(data);
    } catch (error) {
      console.error('Failed to load performance data:', error);
      this.showError('Failed to load performance data');
    }
  }

  updateKPIs(data) {
    const kpis = {
      totalViews: data.views || 0,
      engagementRate: data.engagementRate || 0,
      retentionRate: data.retentionRate || 0,
      conversionRate: data.conversionRate || 0
    };

    const changes = {
      viewsChange: data.viewsChange || 0,
      engagementChange: data.engagementChange || 0,
      retentionChange: data.retentionChange || 0,
      conversionChange: data.conversionChange || 0
    };

    // Update KPI values
    Object.entries(kpis).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        if (key.includes('Rate')) {
          element.textContent = `${value.toFixed(1)}%`;
        } else {
          element.textContent = this.formatNumber(value);
        }
      }
    });

    // Update KPI changes
    Object.entries(changes).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        element.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
        element.className = `kpi-change ${value >= 0 ? 'positive' : 'negative'}`;
      }
    });

    // Update mini charts
    this.updateMiniCharts(data);
  }

  updatePerformanceScore(data) {
    const overallScore = data.overallScore || 0;
    const scores = {
      quality: data.qualityScore || 0,
      audience: data.audienceScore || 0,
      platform: data.platformScore || 0,
      growth: data.growthScore || 0
    };

    // Update overall score
    const scoreElement = this.container.querySelector('#performanceScore');
    const circleElement = this.container.querySelector('#performanceScoreCircle');
    
    scoreElement.textContent = overallScore;
    circleElement.className = `score-circle ${this.getScoreClass(overallScore)}`;

    // Update breakdown scores
    Object.entries(scores).forEach(([key, value]) => {
      const fillElement = this.container.querySelector(`#${key}Score`);
      const valueElement = this.container.querySelector(`#${key}Value`);
      
      if (fillElement && valueElement) {
        fillElement.style.width = `${value}%`;
        fillElement.className = `score-fill ${this.getScoreClass(value)}`;
        valueElement.textContent = `${value}%`;
      }
    });
  }

  updateMiniCharts(data) {
    // Update mini sparkline charts for each KPI
    const chartData = {
      views: data.viewsHistory || [],
      engagement: data.engagementHistory || [],
      retention: data.retentionHistory || [],
      conversion: data.conversionHistory || []
    };

    Object.entries(chartData).forEach(([key, history]) => {
      this.drawMiniChart(`${key}Chart`, history);
    });
  }

  drawMiniChart(elementId, data) {
    const container = this.container.querySelector(`#${elementId}`);
    if (!container || !data.length) return;

    // Create SVG sparkline
    const svg = this.createSVGSparkline(data);
    container.innerHTML = '';
    container.appendChild(svg);
  }

  createSVGSparkline(data, width = 60, height = 30) {
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

  initializeCharts() {
    // Initialize demographic chart
    const demographicsCtx = this.container.querySelector('#demographicsChart');
    if (demographicsCtx) {
      this.demographicsChart = this.createChart(demographicsCtx, 'pie');
    }

    // Initialize audience growth chart
    const growthCtx = this.container.querySelector('#audienceGrowthChart');
    if (growthCtx) {
      this.audienceGrowthChart = this.createChart(growthCtx, 'line');
    }

    // Initialize platform comparison chart
    const platformCtx = this.container.querySelector('#platformComparisonChart');
    if (platformCtx) {
      this.platformChart = this.createChart(platformCtx, 'bar');
    }

    // Initialize real-time chart
    const realtimeCtx = this.container.querySelector('#realtimeChart');
    if (realtimeCtx) {
      this.realtimeChart = this.createChart(realtimeCtx, 'line');
    }
  }

  createChart(canvas, type) {
    // Mock chart implementation
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
    
    switch (type) {
      case 'pie':
        this.drawPieChart(ctx, data);
        break;
      case 'line':
        this.drawLineChart(ctx, data);
        break;
      case 'bar':
        this.drawBarChart(ctx, data);
        break;
    }
  }

  drawPieChart(ctx, data = {}) {
    const centerX = ctx.canvas.width / 2;
    const centerY = ctx.canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;

    const segments = data.segments || [
      {label: '18-24', value: 30, color: '#4caf50'},
      {label: '25-34', value: 40, color: '#2196f3'},
      {label: '35-44', value: 20, color: '#ff9800'},
      {label: '45+', value: 10, color: '#f44336'}
    ];

    let currentAngle = -Math.PI / 2;
    const total = segments.reduce((sum, seg) => sum + seg.value, 0);

    segments.forEach(segment => {
      const segmentAngle = (segment.value / total) * 2 * Math.PI;
      
      ctx.fillStyle = segment.color;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + segmentAngle);
      ctx.lineTo(centerX, centerY);
      ctx.closePath();
      ctx.fill();

      currentAngle += segmentAngle;
    });
  }

  drawLineChart(ctx, data = {}) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 20;

    const points = data.points || this.generateMockPoints(width, height, padding);

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

    // Draw line
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(point => ctx.lineTo(point.x, point.y));
    ctx.stroke();

    // Draw points
    ctx.fillStyle = '#4caf50';
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 3, 0, 2 * Math.PI);
      ctx.fill();
    });
  }

  drawBarChart(ctx, data = {}) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 40;

    const bars = data.bars || [
      {label: 'YouTube', value: 75, color: '#ff0000'},
      {label: 'TikTok', value: 60, color: '#000000'},
      {label: 'Instagram', value: 45, color: '#e4405f'},
      {label: 'Twitter', value: 30, color: '#1da1f2'}
    ];

    const barWidth = (width - 2 * padding) / bars.length - 10;
    const maxValue = Math.max(...bars.map(b => b.value));

    bars.forEach((bar, index) => {
      const barHeight = (bar.value / maxValue) * (height - 2 * padding);
      const x = padding + index * (barWidth + 10);
      const y = height - padding - barHeight;

      ctx.fillStyle = bar.color;
      ctx.fillRect(x, y, barWidth, barHeight);

      // Draw label
      ctx.fillStyle = '#fff';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(bar.label, x + barWidth / 2, height - padding + 15);
    });
  }

  generateMockPoints(width, height, padding) {
    const points = [];
    const numPoints = 10;
    
    for (let i = 0; i < numPoints; i++) {
      points.push({
        x: padding + (i * (width - 2 * padding) / (numPoints - 1)),
        y: padding + Math.random() * (height - 2 * padding)
      });
    }
    
    return points;
  }

  switchTab(tabName) {
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

    this.currentView = tabName;

    // Load tab-specific data
    switch (tabName) {
      case 'audience':
        this.loadAudienceAnalytics();
        break;
      case 'content':
        this.loadContentPerformance();
        break;
      case 'platforms':
        this.loadPlatformAnalytics();
        break;
      case 'realtime':
        this.loadRealTimeData();
        break;
    }
  }

  async loadAudienceAnalytics() {
    try {
      const data = await this.performanceTracker.getAudienceData();
      this.updateAudienceMetrics(data);
      this.updateDemographicsChart(data);
      this.updateGeographicData(data);
    } catch (error) {
      console.error('Failed to load audience analytics:', error);
    }
  }

  updateAudienceMetrics(data) {
    const metrics = {
      avgWatchTime: data.avgWatchTime || '0:00',
      clickThroughRate: data.ctr || 0,
      bounceRate: data.bounceRate || 0,
      returnVisitors: data.returnVisitors || 0
    };

    Object.entries(metrics).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        if (key === 'avgWatchTime') {
          element.textContent = value;
        } else {
          element.textContent = `${value.toFixed(1)}%`;
        }
      }
    });
  }

  updateDemographicsChart(data) {
    if (this.demographicsChart) {
      this.demographicsChart.update({
        segments: data.demographics || []
      });
    }
  }

  updateGeographicData(data) {
    const container = this.container.querySelector('#geoList');
    const geoData = data.geographic || this.getMockGeographicData();
    
    container.innerHTML = geoData.map(geo => `
      <div class="geo-item">
        <span class="geo-country">${geo.country}</span>
        <div class="geo-bar">
          <div class="geo-fill" style="width: ${geo.percentage}%"></div>
        </div>
        <span class="geo-percentage">${geo.percentage}%</span>
      </div>
    `).join('');
  }

  getMockGeographicData() {
    return [
      {country: 'United States', percentage: 35},
      {country: 'United Kingdom', percentage: 15},
      {country: 'Canada', percentage: 12},
      {country: 'Germany', percentage: 10},
      {country: 'Australia', percentage: 8},
      {country: 'Others', percentage: 20}
    ];
  }

  async loadContentPerformance() {
    try {
      const filters = this.getContentFilters();
      const data = await this.performanceTracker.getContentData(filters);
      this.updateContentTable(data);
      this.updateContentInsights(data);
    } catch (error) {
      console.error('Failed to load content performance:', error);
    }
  }

  getContentFilters() {
    return {
      timeframe: this.container.querySelector('#contentTimeframe').value,
      type: this.container.querySelector('#contentType').value,
      sort: this.container.querySelector('#contentSort').value
    };
  }

  updateContentTable(data) {
    const tableBody = this.container.querySelector('#contentTableBody');
    const content = data.content || this.getMockContentData();
    
    tableBody.innerHTML = content.map(item => `
      <tr class="content-row">
        <td>
          <div class="content-info">
            <img src="${item.thumbnail}" alt="${item.title}" class="content-thumb" />
            <div class="content-details">
              <span class="content-title">${item.title}</span>
              <span class="content-date">${this.formatDate(item.publishDate)}</span>
            </div>
          </div>
        </td>
        <td><span class="content-type ${item.type}">${item.type}</span></td>
        <td>${this.formatNumber(item.views)}</td>
        <td>${item.engagement.toFixed(1)}%</td>
        <td>${this.formatCurrency(item.revenue)}</td>
        <td>
          <div class="performance-indicator ${this.getPerformanceClass(item.performance)}">
            ${item.performance}%
          </div>
        </td>
        <td>
          <button class="btn-tiny" onclick="window.performanceMetrics?.viewContentDetails('${item.id}')">
            <i class="fas fa-eye"></i>
          </button>
        </td>
      </tr>
    `).join('');
  }

  getMockContentData() {
    return [
      {
        id: '1',
        title: 'How to Create Viral Content',
        type: 'video',
        thumbnail: '/thumbs/viral-content.jpg',
        publishDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        views: 125000,
        engagement: 8.5,
        revenue: 450,
        performance: 92
      },
      {
        id: '2',
        title: 'Music Production Tips',
        type: 'audio',
        thumbnail: '/thumbs/music-tips.jpg',
        publishDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
        views: 89000,
        engagement: 6.2,
        revenue: 280,
        performance: 87
      }
    ];
  }

  async updateRealTimeMetrics() {
    if (!this.realTimeEnabled || this.currentView !== 'realtime') return;

    try {
      const data = await this.performanceTracker.getRealTimeData();
      this.updateLiveMetrics(data);
      this.updateActivityFeed(data);
      this.updateRealTimeChart(data);
    } catch (error) {
      console.error('Failed to update real-time metrics:', error);
    }
  }

  updateLiveMetrics(data) {
    const metrics = {
      activeViewers: data.activeViewers || 0,
      liveEngagement: data.liveEngagement || 0,
      peakConcurrent: data.peakConcurrent || 0
    };

    Object.entries(metrics).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        element.textContent = this.formatNumber(value);
      }
    });
  }

  updateActivityFeed(data) {
    const feed = this.container.querySelector('#activityFeed');
    const activities = data.activities || this.getMockActivities();
    
    feed.innerHTML = activities.map(activity => `
      <div class="activity-item">
        <div class="activity-icon">
          <i class="fas ${activity.icon}"></i>
        </div>
        <div class="activity-content">
          <span class="activity-text">${activity.text}</span>
          <span class="activity-time">${this.formatTimeAgo(activity.timestamp)}</span>
        </div>
      </div>
    `).join('');
  }

  getMockActivities() {
    const now = Date.now();
    return [
      {
        icon: 'fa-eye',
        text: 'New viewer from United States',
        timestamp: new Date(now - 30000)
      },
      {
        icon: 'fa-heart',
        text: 'Content liked by @user123',
        timestamp: new Date(now - 60000)
      },
      {
        icon: 'fa-share',
        text: 'Content shared on Twitter',
        timestamp: new Date(now - 90000)
      }
    ];
  }

  async generateRecommendations() {
    try {
      this.showRecommendationsLoading(true);
      
      const currentMetrics = await this.performanceTracker.getCurrentMetrics();
      const recommendations = await this.metricsEngine.generateRecommendations(currentMetrics);
      
      this.displayRecommendations(recommendations);
      
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
      this.showError('Failed to generate recommendations');
    } finally {
      this.showRecommendationsLoading(false);
    }
  }

  displayRecommendations(recommendations) {
    const container = this.container.querySelector('#recommendationsContainer');
    
    container.innerHTML = `
      <div class="recommendations-list">
        ${recommendations.map(rec => `
          <div class="recommendation-item ${rec.priority}">
            <div class="rec-header">
              <span class="rec-title">${rec.title}</span>
              <span class="rec-impact">+${rec.expectedImprovement}%</span>
            </div>
            <p class="rec-description">${rec.description}</p>
            <div class="rec-actions">
              <button class="btn-small primary" onclick="window.performanceMetrics?.implementRecommendation('${rec.id}')">
                Implement
              </button>
              <button class="btn-small secondary" onclick="window.performanceMetrics?.dismissRecommendation('${rec.id}')">
                Dismiss
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
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

  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  }

  formatDate(date) {
    return new Date(date).toLocaleDateString();
  }

  formatTimeAgo(date) {
    const diff = Date.now() - new Date(date).getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return `${seconds}s ago`;
  }

  getScoreClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
  }

  getPerformanceClass(performance) {
    if (performance >= 80) return 'excellent';
    if (performance >= 60) return 'good';
    if (performance >= 40) return 'average';
    return 'poor';
  }

  showRecommendationsLoading(show) {
    const button = this.container.querySelector('#generateRecommendations');
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
      button.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-brain"></i> Generate Insights';
      button.disabled = false;
    }
  }

  showError(message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification('error', message);
    } else {
      console.error(message);
    }
  }

  showSuccess(message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification('success', message);
    } else {
      console.log(message);
    }
  }

  showInfo(message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification('info', message);
    } else {
      console.log(message);
    }
  }

  exportMetrics() {
    const data = {
      timestamp: new Date().toISOString(),
      overview: this.getOverviewData(),
      audience: this.getAudienceData(),
      content: this.getContentData(),
      platforms: this.getPlatformData()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance_metrics_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  addStyles() {
    const styles = `
      <style>
        .performance-metrics {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .metrics-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
          border-bottom: 1px solid #333;
        }

        .metrics-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .header-controls {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .toggle-switch {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #fff;
        }

        .toggle-slider {
          width: 32px;
          height: 16px;
          background: rgba(255, 255, 255, 0.3);
          border-radius: 16px;
          position: relative;
          cursor: pointer;
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

        .toggle-switch input:checked + .toggle-slider {
          background: rgba(76, 175, 80, 0.8);
        }

        .toggle-switch input:checked + .toggle-slider::before {
          transform: translateX(16px);
        }

        .metrics-content {
          padding: 20px;
        }

        .overview-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 20px;
          margin-bottom: 24px;
        }

        .kpi-cards {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .kpi-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 20px;
          background: #252526;
          border-radius: 8px;
          position: relative;
        }

        .kpi-icon {
          font-size: 32px;
          color: #2196f3;
        }

        .kpi-content {
          flex: 1;
        }

        .kpi-value {
          font-size: 24px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 4px;
        }

        .kpi-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .kpi-change {
          font-size: 12px;
          font-weight: 600;
        }

        .kpi-change.positive { color: #4caf50; }
        .kpi-change.negative { color: #f44336; }

        .kpi-chart {
          position: absolute;
          bottom: 8px;
          right: 8px;
          width: 60px;
          height: 30px;
        }

        .score-container {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .score-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          border: 8px solid #666;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .score-circle.excellent { border-color: #4caf50; }
        .score-circle.good { border-color: #8bc34a; }
        .score-circle.average { border-color: #ff9800; }
        .score-circle.poor { border-color: #f44336; }

        .score-value {
          font-size: 32px;
          font-weight: bold;
          color: #fff;
        }

        .score-label {
          font-size: 10px;
          color: #999;
          text-transform: uppercase;
        }

        .score-breakdown {
          flex: 1;
        }

        .score-item {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .score-metric {
          width: 120px;
          font-size: 12px;
          color: #ccc;
        }

        .score-bar {
          flex: 1;
          height: 8px;
          background: #444;
          border-radius: 4px;
          overflow: hidden;
        }

        .score-fill {
          height: 100%;
          background: #2196f3;
          transition: width 0.5s ease;
        }

        .score-fill.excellent { background: #4caf50; }
        .score-fill.good { background: #8bc34a; }
        .score-fill.average { background: #ff9800; }
        .score-fill.poor { background: #f44336; }

        .analytics-tabs {
          display: flex;
          background: #252526;
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
          background: #2196f3;
          color: #fff;
        }

        .tab-content {
          display: none;
          background: #252526;
          border-radius: 0 0 6px 6px;
          padding: 20px;
        }

        .tab-content.active {
          display: block;
        }

        .audience-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
        }

        .behavior-metrics {
          display: grid;
          gap: 12px;
        }

        .behavior-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          background: #1a1a1a;
          border-radius: 4px;
        }

        .behavior-label {
          color: #ccc;
          font-size: 12px;
        }

        .behavior-value {
          color: #fff;
          font-weight: 600;
        }

        .behavior-trend {
          font-size: 11px;
          font-weight: 600;
        }

        .behavior-trend.positive { color: #4caf50; }
        .behavior-trend.negative { color: #f44336; }

        .geo-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 8px 0;
          border-bottom: 1px solid #333;
        }

        .geo-country {
          width: 100px;
          font-size: 12px;
          color: #ccc;
        }

        .geo-bar {
          flex: 1;
          height: 6px;
          background: #444;
          border-radius: 3px;
          overflow: hidden;
        }

        .geo-fill {
          height: 100%;
          background: #2196f3;
          transition: width 0.5s ease;
        }

        .geo-percentage {
          width: 30px;
          text-align: right;
          font-size: 12px;
          color: #fff;
        }

        .content-filters {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .content-filters select {
          padding: 6px 12px;
          background: #1a1a1a;
          border: 1px solid #444;
          border-radius: 4px;
          color: #fff;
          font-size: 12px;
        }

        .content-table {
          width: 100%;
          border-collapse: collapse;
          background: #1a1a1a;
          border-radius: 6px;
          overflow: hidden;
        }

        .content-table th,
        .content-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #333;
        }

        .content-table th {
          background: #333;
          font-weight: 600;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .content-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .content-thumb {
          width: 40px;
          height: 30px;
          object-fit: cover;
          border-radius: 2px;
        }

        .content-details {
          display: flex;
          flex-direction: column;
        }

        .content-title {
          font-size: 12px;
          color: #fff;
          font-weight: 500;
        }

        .content-date {
          font-size: 10px;
          color: #999;
        }

        .content-type {
          padding: 2px 6px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
        }

        .content-type.video { background: #f44336; color: #fff; }
        .content-type.audio { background: #9c27b0; color: #fff; }
        .content-type.image { background: #ff9800; color: #fff; }
        .content-type.text { background: #4caf50; color: #fff; }

        .performance-indicator {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          text-align: center;
        }

        .performance-indicator.excellent { background: #4caf50; color: #fff; }
        .performance-indicator.good { background: #8bc34a; color: #fff; }
        .performance-indicator.average { background: #ff9800; color: #fff; }
        .performance-indicator.poor { background: #f44336; color: #fff; }

        .live-metrics {
          display: flex;
          gap: 20px;
          margin-bottom: 20px;
        }

        .live-metric {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 16px;
          background: #1a1a1a;
          border-radius: 6px;
          position: relative;
        }

        .live-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .live-value {
          font-size: 20px;
          font-weight: bold;
          color: #fff;
        }

        .live-indicator {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #666;
        }

        .live-indicator.active {
          background: #4caf50;
          animation: pulse 2s infinite;
        }

        .activity-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 8px 12px;
          background: #1a1a1a;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .activity-icon {
          width: 32px;
          height: 32px;
          background: #2196f3;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          color: #fff;
        }

        .activity-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .activity-text {
          font-size: 12px;
          color: #fff;
        }

        .activity-time {
          font-size: 10px;
          color: #999;
        }

        .btn-primary, .btn-secondary, .btn-small, .btn-tiny {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #2196f3; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }
        .btn-tiny { background: #555; color: #fff; padding: 2px 6px; font-size: 10px; }

        .performance-alerts,
        .performance-recommendations {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .alerts-header,
        .recommendations-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .alerts-header h4,
        .recommendations-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .no-alerts,
        .no-recommendations {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }

        .no-alerts i,
        .no-recommendations i {
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
    
    if (!document.querySelector('#performance-metrics-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'performance-metrics-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  refreshMetrics() {
    this.loadPerformanceData();
  }

  getOverviewData() {
    return {
      totalViews: this.container.querySelector('#totalViews').textContent,
      engagementRate: this.container.querySelector('#engagementRate').textContent,
      retentionRate: this.container.querySelector('#retentionRate').textContent,
      conversionRate: this.container.querySelector('#conversionRate').textContent
    };
  }

  destroy() {
    this.stopRealTimeUpdates();
    
    // Destroy charts
    if (this.demographicsChart) this.demographicsChart.destroy();
    if (this.audienceGrowthChart) this.audienceGrowthChart.destroy();
    if (this.platformChart) this.platformChart.destroy();
    if (this.realtimeChart) this.realtimeChart.destroy();
    
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PerformanceMetrics;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.PerformanceMetrics = PerformanceMetrics;
  window.performanceMetrics = null; // Will be set when instantiated
}