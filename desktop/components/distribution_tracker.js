/**
 * Ainflue Desktop - Distribution Tracker Component
 * 
 * Multi-platform content distribution tracking and optimization
 * Implements comprehensive distribution analytics, reach monitoring, and channel performance
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class DistributionTracker {
  constructor(container, distributionEngine, analyticsService) {
    this.container = container;
    this.distributionEngine = distributionEngine;
    this.analyticsService = analyticsService;
    this.platforms = new Map();
    this.distributionJobs = new Map();
    this.reachData = {};
    
    this.init();
  }

  init() {
    this.createTrackerInterface();
    this.setupEventListeners();
    this.initializeDistributionTracking();
    this.loadDistributionData();
  }

  createTrackerInterface() {
    this.container.innerHTML = `
      <div class="distribution-tracker">
        <div class="tracker-header">
          <h3><i class="fas fa-share-alt-square"></i> Distribution Tracker</h3>
          <div class="tracker-controls">
            <div class="sync-status">
              <div class="sync-indicator active" id="syncStatus">
                <div class="sync-light"></div>
                <span>Live Sync</span>
              </div>
            </div>
            <button class="btn-primary" id="syncAllPlatforms">
              <i class="fas fa-sync-alt"></i>
              Sync All
            </button>
          </div>
        </div>

        <div class="tracker-content">
          <!-- Distribution Overview -->
          <div class="distribution-overview">
            <div class="overview-metrics">
              <div class="metric-card reach">
                <div class="metric-icon"><i class="fas fa-eye"></i></div>
                <div class="metric-content">
                  <div class="metric-value" id="totalReach">0</div>
                  <div class="metric-label">Total Reach</div>
                  <div class="metric-change" id="reachChange">+0%</div>
                </div>
                <div class="metric-chart" id="reachChart"></div>
              </div>

              <div class="metric-card platforms">
                <div class="metric-icon"><i class="fas fa-broadcast-tower"></i></div>
                <div class="metric-content">
                  <div class="metric-value" id="activePlatforms">0</div>
                  <div class="metric-label">Active Platforms</div>
                  <div class="metric-change" id="platformsChange">+0</div>
                </div>
                <div class="platforms-list" id="platformsList">
                  <!-- Platforms will be listed here -->
                </div>
              </div>

              <div class="metric-card success-rate">
                <div class="metric-icon"><i class="fas fa-check-circle"></i></div>
                <div class="metric-content">
                  <div class="metric-value" id="successRate">0%</div>
                  <div class="metric-label">Success Rate</div>
                  <div class="metric-change" id="successChange">+0%</div>
                </div>
                <div class="success-breakdown" id="successBreakdown">
                  <!-- Success breakdown will be shown here -->
                </div>
              </div>

              <div class="metric-card distribution-speed">
                <div class="metric-icon"><i class="fas fa-tachometer-alt"></i></div>
                <div class="metric-content">
                  <div class="metric-value" id="avgDistributionTime">0s</div>
                  <div class="metric-label">Avg Distribution Time</div>
                  <div class="metric-change" id="speedChange">-0%</div>
                </div>
                <div class="speed-gauge" id="speedGauge"></div>
              </div>
            </div>
          </div>

          <!-- Platform Performance Grid -->
          <div class="platform-performance">
            <div class="performance-header">
              <h4>Platform Performance</h4>
              <div class="performance-controls">
                <select id="performanceTimeframe">
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                </select>
                <button class="btn-small" id="refreshPerformance">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
              </div>
            </div>
            <div class="platforms-grid" id="platformsGrid">
              <!-- Platform cards will be populated here -->
            </div>
          </div>

          <!-- Distribution Timeline -->
          <div class="distribution-timeline">
            <div class="timeline-header">
              <h4>Distribution Timeline</h4>
              <div class="timeline-controls">
                <select id="timelineView">
                  <option value="schedule">Scheduled Posts</option>
                  <option value="published">Published Content</option>
                  <option value="failed">Failed Distributions</option>
                </select>
                <button class="btn-secondary" id="schedulePost">
                  <i class="fas fa-calendar-plus"></i>
                  Schedule Post
                </button>
              </div>
            </div>
            <div class="timeline-container" id="timelineContainer">
              <!-- Timeline items will be populated here -->
            </div>
          </div>

          <!-- Geographic Distribution -->
          <div class="geographic-distribution">
            <div class="geographic-header">
              <h4>Geographic Reach</h4>
              <div class="geographic-controls">
                <select id="geographicMetric">
                  <option value="reach">Reach</option>
                  <option value="engagement">Engagement</option>
                  <option value="conversion">Conversion</option>
                </select>
                <button class="btn-small" id="exportGeoData">
                  <i class="fas fa-download"></i>
                  Export
                </button>
              </div>
            </div>
            <div class="geographic-container">
              <div class="world-map" id="worldMap">
                <!-- World map visualization -->
                <div class="map-placeholder">
                  <i class="fas fa-globe"></i>
                  <p>Geographic distribution map</p>
                </div>
              </div>
              <div class="geographic-details" id="geographicDetails">
                <!-- Geographic breakdown will be shown here -->
              </div>
            </div>
          </div>

          <!-- Content Distribution Analysis -->
          <div class="content-distribution">
            <div class="content-header">
              <h4>Content Distribution Analysis</h4>
              <div class="content-filters">
                <select id="contentTypeFilter">
                  <option value="all">All Content</option>
                  <option value="video">Videos</option>
                  <option value="image">Images</option>
                  <option value="audio">Audio</option>
                  <option value="text">Text</option>
                </select>
                <select id="distributionStatus">
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="publishing">Publishing</option>
                  <option value="published">Published</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>
            <div class="content-table-container">
              <table class="distribution-table">
                <thead>
                  <tr>
                    <th>Content</th>
                    <th>Type</th>
                    <th>Platforms</th>
                    <th>Status</th>
                    <th>Reach</th>
                    <th>Performance</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody id="distributionTableBody">
                  <!-- Distribution data will be populated here -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Distribution Insights -->
          <div class="distribution-insights">
            <div class="insights-header">
              <h4>AI Distribution Insights</h4>
              <button class="btn-primary" id="generateInsights">
                <i class="fas fa-brain"></i>
                Generate Insights
              </button>
            </div>
            <div class="insights-container" id="insightsContainer">
              <div class="no-insights">
                <i class="fas fa-lightbulb"></i>
                <p>Generate AI insights to optimize your distribution strategy</p>
              </div>
            </div>
          </div>

          <!-- Distribution Optimization -->
          <div class="distribution-optimization">
            <div class="optimization-header">
              <h4>Distribution Optimization</h4>
              <div class="optimization-controls">
                <button class="btn-secondary" id="optimizeSchedule">
                  <i class="fas fa-clock"></i>
                  Optimize Schedule
                </button>
                <button class="btn-secondary" id="suggestPlatforms">
                  <i class="fas fa-share-alt"></i>
                  Suggest Platforms
                </button>
              </div>
            </div>
            <div class="optimization-results" id="optimizationResults">
              <div class="no-optimization">
                <i class="fas fa-chart-line"></i>
                <p>Run optimization to improve distribution performance</p>
              </div>
            </div>
          </div>

          <!-- Real-time Distribution Monitor -->
          <div class="realtime-monitor">
            <div class="monitor-header">
              <h4>Real-time Distribution Monitor</h4>
              <div class="monitor-status">
                <span class="status-indicator active">
                  <i class="fas fa-circle"></i>
                  Live
                </span>
              </div>
            </div>
            <div class="monitor-feed" id="realtimeFeed">
              <!-- Real-time distribution events will be shown here -->
            </div>
          </div>
        </div>

        <!-- Schedule Post Modal -->
        <div class="modal-overlay" id="scheduleModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4>Schedule Distribution</h4>
              <button class="modal-close" id="closeScheduleModal">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <form id="scheduleForm">
                <div class="form-group">
                  <label>Content</label>
                  <select name="content" required>
                    <option value="">Select content to distribute</option>
                    <!-- Content options will be populated here -->
                  </select>
                </div>
                <div class="form-group">
                  <label>Platforms</label>
                  <div class="platforms-checklist" id="platformsChecklist">
                    <!-- Platform checkboxes will be populated here -->
                  </div>
                </div>
                <div class="form-group">
                  <label>Schedule Type</label>
                  <select name="scheduleType" required>
                    <option value="immediate">Immediate</option>
                    <option value="scheduled">Scheduled Time</option>
                    <option value="optimal">Optimal Time (AI)</option>
                  </select>
                </div>
                <div class="form-group" id="scheduleDateGroup" style="display: none;">
                  <label>Schedule Date & Time</label>
                  <input type="datetime-local" name="scheduleDate">
                </div>
                <div class="form-group">
                  <label>Custom Message (Optional)</label>
                  <textarea name="customMessage" rows="3" placeholder="Add a custom message for this distribution..."></textarea>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn-secondary" onclick="window.distributionTracker?.hideScheduleModal()">
                    Cancel
                  </button>
                  <button type="submit" class="btn-primary">
                    Schedule Distribution
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Sync controls
    this.container.querySelector('#syncAllPlatforms').addEventListener('click', () => {
      this.syncAllPlatforms();
    });

    // Performance controls
    this.container.querySelector('#performanceTimeframe').addEventListener('change', () => {
      this.updatePlatformPerformance();
    });

    this.container.querySelector('#refreshPerformance').addEventListener('click', () => {
      this.refreshPerformanceData();
    });

    // Timeline controls
    this.container.querySelector('#timelineView').addEventListener('change', () => {
      this.updateTimelineView();
    });

    this.container.querySelector('#schedulePost').addEventListener('click', () => {
      this.showScheduleModal();
    });

    // Geographic controls
    this.container.querySelector('#geographicMetric').addEventListener('change', () => {
      this.updateGeographicData();
    });

    this.container.querySelector('#exportGeoData').addEventListener('click', () => {
      this.exportGeographicData();
    });

    // Content filters
    this.container.querySelector('#contentTypeFilter').addEventListener('change', () => {
      this.filterDistributionContent();
    });

    this.container.querySelector('#distributionStatus').addEventListener('change', () => {
      this.filterDistributionContent();
    });

    // Insights and optimization
    this.container.querySelector('#generateInsights').addEventListener('click', () => {
      this.generateDistributionInsights();
    });

    this.container.querySelector('#optimizeSchedule').addEventListener('click', () => {
      this.optimizeSchedule();
    });

    this.container.querySelector('#suggestPlatforms').addEventListener('click', () => {
      this.suggestPlatforms();
    });

    // Modal controls
    this.container.querySelector('#closeScheduleModal').addEventListener('click', () => {
      this.hideScheduleModal();
    });

    this.container.querySelector('#scheduleForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.scheduleDistribution(e.target);
    });

    // Schedule type change
    this.container.querySelector('select[name="scheduleType"]').addEventListener('change', (e) => {
      this.toggleScheduleDateField(e.target.value);
    });
  }

  initializeDistributionTracking() {
    this.loadConnectedPlatforms();
    this.startRealTimeMonitoring();
    this.updateDistributionMetrics();
  }

  async loadDistributionData() {
    try {
      const data = await this.distributionEngine.getDistributionOverview();
      this.updateOverviewMetrics(data);
      this.updatePlatformPerformance();
      this.updateTimelineView();
      this.updateGeographicData();
      this.updateDistributionTable();
    } catch (error) {
      console.error('Failed to load distribution data:', error);
      this.showError('Failed to load distribution data');
    }
  }

  updateOverviewMetrics(data) {
    const metrics = {
      totalReach: data.totalReach || 0,
      activePlatforms: data.activePlatforms || 0,
      successRate: data.successRate || 0,
      avgDistributionTime: data.avgDistributionTime || 0
    };

    const changes = {
      reachChange: data.reachChange || 0,
      platformsChange: data.platformsChange || 0,
      successChange: data.successChange || 0,
      speedChange: data.speedChange || 0
    };

    // Update metric values
    this.container.querySelector('#totalReach').textContent = this.formatNumber(metrics.totalReach);
    this.container.querySelector('#activePlatforms').textContent = metrics.activePlatforms;
    this.container.querySelector('#successRate').textContent = `${metrics.successRate.toFixed(1)}%`;
    this.container.querySelector('#avgDistributionTime').textContent = `${metrics.avgDistributionTime}s`;

    // Update changes
    Object.entries(changes).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        const prefix = key === 'platformsChange' ? '' : (value >= 0 ? '+' : '');
        const suffix = key === 'platformsChange' ? '' : '%';
        element.textContent = `${prefix}${value.toFixed(1)}${suffix}`;
        element.className = `metric-change ${value >= 0 ? 'positive' : 'negative'}`;
      }
    });

    // Update charts and visualizations
    this.updateReachChart(data.reachHistory);
    this.updatePlatformsList(data.platforms);
    this.updateSuccessBreakdown(data.successBreakdown);
    this.updateSpeedGauge(metrics.avgDistributionTime);
  }

  updateReachChart(data) {
    const chartContainer = this.container.querySelector('#reachChart');
    if (!chartContainer || !data) return;

    const svg = this.createSVGSparkline(data, 100, 40);
    chartContainer.innerHTML = '';
    chartContainer.appendChild(svg);
  }

  createSVGSparkline(data, width = 100, height = 40) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    if (!data || data.length < 2) return svg;

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

  updatePlatformsList(platforms) {
    const container = this.container.querySelector('#platformsList');
    if (!platforms || platforms.length === 0) {
      container.innerHTML = '<span class="no-platforms">No platforms connected</span>';
      return;
    }

    container.innerHTML = platforms.slice(0, 4).map(platform => `
      <div class="platform-indicator ${platform.status}" title="${platform.name}">
        <i class="fab fa-${platform.icon}"></i>
      </div>
    `).join('');
  }

  updateSuccessBreakdown(breakdown) {
    const container = this.container.querySelector('#successBreakdown');
    if (!breakdown) return;

    const total = breakdown.success + breakdown.failed + breakdown.pending;
    const successPercent = total > 0 ? (breakdown.success / total) * 100 : 0;
    const failedPercent = total > 0 ? (breakdown.failed / total) * 100 : 0;
    const pendingPercent = total > 0 ? (breakdown.pending / total) * 100 : 0;

    container.innerHTML = `
      <div class="breakdown-bar">
        <div class="breakdown-segment success" style="width: ${successPercent}%"></div>
        <div class="breakdown-segment failed" style="width: ${failedPercent}%"></div>
        <div class="breakdown-segment pending" style="width: ${pendingPercent}%"></div>
      </div>
    `;
  }

  updateSpeedGauge(speed) {
    const container = this.container.querySelector('#speedGauge');
    if (!container) return;

    // Create simple gauge (0-60 seconds scale)
    const maxSpeed = 60;
    const percentage = Math.min(speed / maxSpeed, 1) * 100;
    const color = speed <= 10 ? '#4caf50' : speed <= 30 ? '#ff9800' : '#f44336';

    container.innerHTML = `
      <div class="gauge-bar">
        <div class="gauge-fill" style="width: ${percentage}%; background: ${color}"></div>
      </div>
    `;
  }

  async updatePlatformPerformance() {
    try {
      const timeframe = this.container.querySelector('#performanceTimeframe').value;
      const platforms = await this.distributionEngine.getPlatformPerformance(timeframe);
      this.displayPlatformCards(platforms);
    } catch (error) {
      console.error('Failed to update platform performance:', error);
    }
  }

  displayPlatformCards(platforms) {
    const container = this.container.querySelector('#platformsGrid');
    
    if (!platforms || platforms.length === 0) {
      container.innerHTML = `
        <div class="no-platforms-grid">
          <i class="fas fa-share-alt"></i>
          <p>No platforms connected</p>
          <button class="btn-link" onclick="window.distributionTracker?.connectPlatform()">
            Connect your first platform
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = platforms.map(platform => `
      <div class="platform-card ${platform.status}">
        <div class="platform-header">
          <div class="platform-info">
            <div class="platform-icon">
              <i class="fab fa-${platform.icon}"></i>
            </div>
            <div class="platform-details">
              <h5 class="platform-name">${platform.name}</h5>
              <span class="platform-handle">@${platform.handle}</span>
            </div>
          </div>
          <div class="platform-status">
            <span class="status-badge ${platform.status}">${platform.status}</span>
          </div>
        </div>

        <div class="platform-metrics">
          <div class="metric-row">
            <span class="metric-label">Posts</span>
            <span class="metric-value">${platform.postsCount}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Reach</span>
            <span class="metric-value">${this.formatNumber(platform.reach)}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Engagement</span>
            <span class="metric-value">${platform.engagement.toFixed(1)}%</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Success Rate</span>
            <span class="metric-value">${platform.successRate.toFixed(1)}%</span>
          </div>
        </div>

        <div class="platform-chart">
          <canvas class="mini-chart" data-platform="${platform.id}" width="200" height="60"></canvas>
        </div>

        <div class="platform-actions">
          <button class="btn-small" onclick="window.distributionTracker?.viewPlatformDetails('${platform.id}')">
            <i class="fas fa-eye"></i>
            Details
          </button>
          <button class="btn-small" onclick="window.distributionTracker?.syncPlatform('${platform.id}')">
            <i class="fas fa-sync-alt"></i>
            Sync
          </button>
          <button class="btn-small ${platform.status === 'active' ? 'danger' : 'success'}" onclick="window.distributionTracker?.togglePlatform('${platform.id}')">
            <i class="fas fa-power-off"></i>
            ${platform.status === 'active' ? 'Disable' : 'Enable'}
          </button>
        </div>
      </div>
    `).join('');

    // Draw mini charts for each platform
    platforms.forEach(platform => {
      this.drawPlatformChart(platform.id, platform.performanceHistory);
    });
  }

  drawPlatformChart(platformId, data) {
    const canvas = this.container.querySelector(`canvas[data-platform="${platformId}"]`);
    if (!canvas || !data) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    if (data.length < 2) return;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    // Draw line
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });

    ctx.stroke();
  }

  updateTimelineView() {
    const view = this.container.querySelector('#timelineView').value;
    this.loadTimelineData(view);
  }

  async loadTimelineData(view) {
    try {
      const data = await this.distributionEngine.getTimelineData(view);
      this.displayTimeline(data, view);
    } catch (error) {
      console.error('Failed to load timeline data:', error);
    }
  }

  displayTimeline(data, view) {
    const container = this.container.querySelector('#timelineContainer');
    
    if (!data || data.length === 0) {
      container.innerHTML = `
        <div class="no-timeline-data">
          <i class="fas fa-calendar"></i>
          <p>No ${view} content found</p>
        </div>
      `;
      return;
    }

    container.innerHTML = data.map(item => `
      <div class="timeline-item ${item.status}">
        <div class="timeline-marker">
          <div class="timeline-dot ${item.status}"></div>
          <div class="timeline-line"></div>
        </div>
        <div class="timeline-content">
          <div class="timeline-header">
            <h6 class="timeline-title">${item.title}</h6>
            <span class="timeline-time">${this.formatDateTime(item.scheduledTime || item.publishedTime)}</span>
          </div>
          <div class="timeline-details">
            <div class="timeline-platforms">
              ${item.platforms.map(platform => `
                <span class="platform-tag ${platform.status}">
                  <i class="fab fa-${platform.icon}"></i>
                  ${platform.name}
                </span>
              `).join('')}
            </div>
            <div class="timeline-metrics">
              ${item.reach ? `<span class="metric">Reach: ${this.formatNumber(item.reach)}</span>` : ''}
              ${item.engagement ? `<span class="metric">Engagement: ${item.engagement.toFixed(1)}%</span>` : ''}
            </div>
          </div>
          ${item.status === 'failed' ? `
            <div class="timeline-error">
              <i class="fas fa-exclamation-triangle"></i>
              ${item.errorMessage}
            </div>
          ` : ''}
          <div class="timeline-actions">
            <button class="btn-tiny" onclick="window.distributionTracker?.viewContent('${item.id}')">
              <i class="fas fa-eye"></i>
              View
            </button>
            ${item.status === 'scheduled' ? `
              <button class="btn-tiny" onclick="window.distributionTracker?.editSchedule('${item.id}')">
                <i class="fas fa-edit"></i>
                Edit
              </button>
              <button class="btn-tiny danger" onclick="window.distributionTracker?.cancelSchedule('${item.id}')">
                <i class="fas fa-times"></i>
                Cancel
              </button>
            ` : ''}
            ${item.status === 'failed' ? `
              <button class="btn-tiny" onclick="window.distributionTracker?.retryDistribution('${item.id}')">
                <i class="fas fa-redo"></i>
                Retry
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `).join('');
  }

  async updateGeographicData() {
    try {
      const metric = this.container.querySelector('#geographicMetric').value;
      const data = await this.distributionEngine.getGeographicData(metric);
      this.displayGeographicData(data);
    } catch (error) {
      console.error('Failed to update geographic data:', error);
    }
  }

  displayGeographicData(data) {
    const detailsContainer = this.container.querySelector('#geographicDetails');
    
    if (!data || data.countries.length === 0) {
      detailsContainer.innerHTML = `
        <div class="no-geographic-data">
          <i class="fas fa-globe"></i>
          <p>No geographic data available</p>
        </div>
      `;
      return;
    }

    detailsContainer.innerHTML = `
      <div class="geographic-list">
        <h5>Top Performing Regions</h5>
        ${data.countries.map((country, index) => `
          <div class="geographic-item">
            <div class="country-rank">${index + 1}</div>
            <div class="country-flag">
              <img src="/flags/${country.code.toLowerCase()}.png" alt="${country.name}" />
            </div>
            <div class="country-info">
              <span class="country-name">${country.name}</span>
              <span class="country-metric">${this.formatNumber(country.value)} ${data.unit}</span>
            </div>
            <div class="country-bar">
              <div class="country-fill" style="width: ${country.percentage}%"></div>
            </div>
            <div class="country-percentage">${country.percentage.toFixed(1)}%</div>
          </div>
        `).join('')}
      </div>
    `;
  }

  updateDistributionTable() {
    // Mock distribution table data
    const tableData = this.getMockDistributionData();
    this.displayDistributionTable(tableData);
  }

  getMockDistributionData() {
    return [
      {
        id: '1',
        title: 'Summer Music Video',
        type: 'video',
        platforms: ['youtube', 'tiktok', 'instagram'],
        status: 'published',
        reach: 125000,
        performance: 87,
        publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000)
      },
      {
        id: '2',
        title: 'Behind the Scenes',
        type: 'image',
        platforms: ['instagram', 'twitter'],
        status: 'publishing',
        reach: 0,
        performance: 0,
        publishedAt: new Date()
      }
    ];
  }

  displayDistributionTable(data) {
    const tableBody = this.container.querySelector('#distributionTableBody');
    
    tableBody.innerHTML = data.map(item => `
      <tr class="distribution-row">
        <td>
          <div class="content-info">
            <div class="content-type-icon ${item.type}">
              <i class="fas ${this.getContentTypeIcon(item.type)}"></i>
            </div>
            <div class="content-details">
              <span class="content-title">${item.title}</span>
              <span class="content-time">${this.formatTimeAgo(item.publishedAt)}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="content-type-badge ${item.type}">${item.type}</span>
        </td>
        <td>
          <div class="platforms-list">
            ${item.platforms.map(platform => `
              <span class="platform-badge">
                <i class="fab fa-${platform}"></i>
              </span>
            `).join('')}
          </div>
        </td>
        <td>
          <span class="status-badge ${item.status}">${item.status}</span>
        </td>
        <td>${this.formatNumber(item.reach)}</td>
        <td>
          <div class="performance-score ${this.getPerformanceClass(item.performance)}">
            ${item.performance}%
          </div>
        </td>
        <td>
          <div class="table-actions">
            <button class="btn-tiny" onclick="window.distributionTracker?.viewDistributionDetails('${item.id}')">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn-tiny" onclick="window.distributionTracker?.redistributeContent('${item.id}')">
              <i class="fas fa-share-alt"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  getContentTypeIcon(type) {
    const icons = {
      video: 'fa-video',
      image: 'fa-image',
      audio: 'fa-music',
      text: 'fa-file-alt'
    };
    return icons[type] || 'fa-file';
  }

  getPerformanceClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
  }

  startRealTimeMonitoring() {
    this.monitoringInterval = setInterval(() => {
      this.updateRealTimeFeed();
    }, 5000);
  }

  updateRealTimeFeed() {
    const feed = this.container.querySelector('#realtimeFeed');
    const mockEvents = this.generateMockEvents();
    
    feed.innerHTML = mockEvents.map(event => `
      <div class="feed-item ${event.type}">
        <div class="feed-icon">
          <i class="fas ${event.icon}"></i>
        </div>
        <div class="feed-content">
          <span class="feed-text">${event.text}</span>
          <span class="feed-time">${this.formatTimeAgo(event.timestamp)}</span>
        </div>
      </div>
    `).join('');
  }

  generateMockEvents() {
    const now = Date.now();
    return [
      {
        type: 'success',
        icon: 'fa-check-circle',
        text: 'Successfully published to YouTube',
        timestamp: new Date(now - 30000)
      },
      {
        type: 'info',
        icon: 'fa-upload',
        text: 'Uploading to Instagram...',
        timestamp: new Date(now - 60000)
      },
      {
        type: 'warning',
        icon: 'fa-exclamation-triangle',
        text: 'Twitter upload delayed - API rate limit',
        timestamp: new Date(now - 120000)
      }
    ];
  }

  // Modal and form handling
  showScheduleModal() {
    this.loadScheduleModalData();
    this.container.querySelector('#scheduleModal').style.display = 'flex';
  }

  hideScheduleModal() {
    this.container.querySelector('#scheduleModal').style.display = 'none';
    this.container.querySelector('#scheduleForm').reset();
  }

  loadScheduleModalData() {
    // Load available content and platforms for scheduling
    this.loadContentOptions();
    this.loadPlatformCheckboxes();
  }

  loadContentOptions() {
    const select = this.container.querySelector('select[name="content"]');
    // Mock content options
    select.innerHTML = `
      <option value="">Select content to distribute</option>
      <option value="1">Summer Music Video</option>
      <option value="2">Behind the Scenes Photos</option>
      <option value="3">New Track Preview</option>
    `;
  }

  loadPlatformCheckboxes() {
    const container = this.container.querySelector('#platformsChecklist');
    const platforms = [
      { id: 'youtube', name: 'YouTube', icon: 'youtube' },
      { id: 'tiktok', name: 'TikTok', icon: 'tiktok' },
      { id: 'instagram', name: 'Instagram', icon: 'instagram' },
      { id: 'twitter', name: 'Twitter', icon: 'twitter' },
      { id: 'facebook', name: 'Facebook', icon: 'facebook' }
    ];

    container.innerHTML = platforms.map(platform => `
      <label class="platform-checkbox">
        <input type="checkbox" name="platforms" value="${platform.id}">
        <span class="checkbox-custom"></span>
        <i class="fab fa-${platform.icon}"></i>
        ${platform.name}
      </label>
    `).join('');
  }

  toggleScheduleDateField(scheduleType) {
    const dateGroup = this.container.querySelector('#scheduleDateGroup');
    dateGroup.style.display = scheduleType === 'scheduled' ? 'block' : 'none';
  }

  scheduleDistribution(form) {
    const formData = new FormData(form);
    const platforms = formData.getAll('platforms');
    
    if (platforms.length === 0) {
      this.showError('Please select at least one platform');
      return;
    }

    const distribution = {
      contentId: formData.get('content'),
      platforms: platforms,
      scheduleType: formData.get('scheduleType'),
      scheduleDate: formData.get('scheduleDate'),
      customMessage: formData.get('customMessage')
    };

    this.createDistributionJob(distribution);
  }

  async createDistributionJob(distribution) {
    try {
      const job = await this.distributionEngine.scheduleDistribution(distribution);
      this.hideScheduleModal();
      this.showSuccess('Distribution scheduled successfully');
      this.updateTimelineView();
    } catch (error) {
      console.error('Failed to schedule distribution:', error);
      this.showError('Failed to schedule distribution');
    }
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

  formatDateTime(date) {
    return new Date(date).toLocaleString();
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

  addStyles() {
    const styles = `
      <style>
        .distribution-tracker {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .tracker-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
          border-bottom: 1px solid #333;
        }

        .tracker-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .tracker-controls {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .sync-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #fff;
        }

        .sync-light {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #4caf50;
          animation: pulse 2s infinite;
        }

        .tracker-content {
          padding: 20px;
        }

        .overview-metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .metric-card {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          border-left: 4px solid #ff9800;
          position: relative;
        }

        .metric-card.platforms { border-left-color: #2196f3; }
        .metric-card.success-rate { border-left-color: #4caf50; }
        .metric-card.distribution-speed { border-left-color: #9c27b0; }

        .metric-icon {
          font-size: 28px;
          color: #ff9800;
          margin-bottom: 8px;
        }

        .metric-value {
          font-size: 28px;
          font-weight: bold;
          color: #fff;
          margin-bottom: 4px;
        }

        .metric-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .metric-change {
          font-size: 12px;
          font-weight: 600;
        }

        .metric-change.positive { color: #4caf50; }
        .metric-change.negative { color: #f44336; }

        .metric-chart {
          position: absolute;
          bottom: 12px;
          right: 12px;
          width: 100px;
          height: 40px;
        }

        .platforms-list {
          display: flex;
          gap: 4px;
          margin-top: 8px;
        }

        .platform-indicator {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          background: #444;
          color: #999;
        }

        .platform-indicator.active {
          background: #4caf50;
          color: #fff;
        }

        .platform-indicator.error {
          background: #f44336;
          color: #fff;
        }

        .breakdown-bar {
          display: flex;
          height: 6px;
          border-radius: 3px;
          overflow: hidden;
          margin-top: 8px;
        }

        .breakdown-segment.success { background: #4caf50; }
        .breakdown-segment.failed { background: #f44336; }
        .breakdown-segment.pending { background: #ff9800; }

        .gauge-bar {
          width: 100%;
          height: 6px;
          background: #444;
          border-radius: 3px;
          overflow: hidden;
          margin-top: 8px;
        }

        .gauge-fill {
          height: 100%;
          transition: width 0.5s ease;
        }

        .platform-performance,
        .distribution-timeline,
        .geographic-distribution,
        .content-distribution,
        .distribution-insights,
        .distribution-optimization,
        .realtime-monitor {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .performance-header,
        .timeline-header,
        .geographic-header,
        .content-header,
        .insights-header,
        .optimization-header,
        .monitor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .performance-header h4,
        .timeline-header h4,
        .geographic-header h4,
        .content-header h4,
        .insights-header h4,
        .optimization-header h4,
        .monitor-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .platforms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px;
        }

        .platform-card {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 16px;
          border: 1px solid #333;
        }

        .platform-card.active { border-color: #4caf50; }
        .platform-card.error { border-color: #f44336; }
        .platform-card.warning { border-color: #ff9800; }

        .platform-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .platform-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .platform-icon {
          font-size: 24px;
          color: #ff9800;
        }

        .platform-name {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .platform-handle {
          color: #999;
          font-size: 12px;
        }

        .status-badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .status-badge.active { background: #4caf50; color: #fff; }
        .status-badge.error { background: #f44336; color: #fff; }
        .status-badge.warning { background: #ff9800; color: #fff; }
        .status-badge.pending { background: #2196f3; color: #fff; }

        .platform-metrics {
          margin-bottom: 12px;
        }

        .metric-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 4px;
          font-size: 12px;
        }

        .metric-label {
          color: #999;
        }

        .metric-value {
          color: #fff;
          font-weight: 500;
        }

        .platform-chart {
          margin-bottom: 12px;
        }

        .platform-actions {
          display: flex;
          gap: 6px;
        }

        .timeline-item {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .timeline-marker {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex-shrink: 0;
        }

        .timeline-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #666;
        }

        .timeline-dot.scheduled { background: #2196f3; }
        .timeline-dot.published { background: #4caf50; }
        .timeline-dot.failed { background: #f44336; }
        .timeline-dot.publishing { background: #ff9800; }

        .timeline-line {
          width: 2px;
          height: 40px;
          background: #333;
          margin-top: 4px;
        }

        .timeline-content {
          flex: 1;
          background: #1a1a1a;
          border-radius: 6px;
          padding: 12px;
        }

        .timeline-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .timeline-title {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 500;
        }

        .timeline-time {
          color: #999;
          font-size: 12px;
        }

        .timeline-platforms {
          display: flex;
          gap: 6px;
          margin-bottom: 8px;
        }

        .platform-tag {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 2px 6px;
          border-radius: 12px;
          font-size: 10px;
          background: #333;
          color: #ccc;
        }

        .platform-tag.success { background: #4caf50; color: #fff; }
        .platform-tag.error { background: #f44336; color: #fff; }

        .geographic-container {
          display: flex;
          gap: 20px;
        }

        .world-map {
          flex: 1;
          min-height: 300px;
          background: #1a1a1a;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #666;
        }

        .geographic-details {
          width: 300px;
        }

        .geographic-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          border-bottom: 1px solid #333;
        }

        .country-rank {
          width: 20px;
          text-align: center;
          font-weight: bold;
          color: #ff9800;
        }

        .country-flag img {
          width: 20px;
          height: 15px;
          object-fit: cover;
        }

        .country-info {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .country-name {
          font-size: 12px;
          color: #fff;
        }

        .country-metric {
          font-size: 10px;
          color: #999;
        }

        .country-bar {
          width: 60px;
          height: 4px;
          background: #444;
          border-radius: 2px;
          overflow: hidden;
        }

        .country-fill {
          height: 100%;
          background: #ff9800;
        }

        .country-percentage {
          width: 40px;
          text-align: right;
          font-size: 12px;
          color: #fff;
        }

        .distribution-table {
          width: 100%;
          border-collapse: collapse;
          background: #1a1a1a;
          border-radius: 6px;
          overflow: hidden;
        }

        .distribution-table th,
        .distribution-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #333;
        }

        .distribution-table th {
          background: #333;
          font-weight: 600;
          font-size: 12px;
          text-transform: uppercase;
        }

        .content-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .content-type-icon {
          width: 32px;
          height: 32px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
        }

        .content-type-icon.video { background: #f44336; color: #fff; }
        .content-type-icon.image { background: #4caf50; color: #fff; }
        .content-type-icon.audio { background: #9c27b0; color: #fff; }
        .content-type-icon.text { background: #2196f3; color: #fff; }

        .content-title {
          font-size: 14px;
          color: #fff;
          font-weight: 500;
        }

        .content-time {
          font-size: 12px;
          color: #999;
        }

        .content-type-badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
        }

        .platforms-list {
          display: flex;
          gap: 4px;
        }

        .platform-badge {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #444;
          color: #ccc;
          font-size: 10px;
        }

        .performance-score {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          text-align: center;
        }

        .performance-score.excellent { background: #4caf50; color: #fff; }
        .performance-score.good { background: #8bc34a; color: #fff; }
        .performance-score.average { background: #ff9800; color: #fff; }
        .performance-score.poor { background: #f44336; color: #fff; }

        .feed-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          margin-bottom: 6px;
          border-radius: 4px;
          background: #1a1a1a;
        }

        .feed-icon {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
        }

        .feed-item.success .feed-icon { background: #4caf50; color: #fff; }
        .feed-item.info .feed-icon { background: #2196f3; color: #fff; }
        .feed-item.warning .feed-icon { background: #ff9800; color: #fff; }

        .feed-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .feed-text {
          font-size: 12px;
          color: #fff;
        }

        .feed-time {
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

        .btn-primary { background: #ff9800; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }
        .btn-tiny { background: #555; color: #fff; padding: 2px 6px; font-size: 10px; }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
        }

        .modal-content {
          background: #1a1a1a;
          border-radius: 8px;
          max-width: 600px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid #333;
        }

        .modal-body {
          padding: 20px;
        }

        .form-group {
          margin-bottom: 16px;
        }

        .form-group label {
          display: block;
          margin-bottom: 4px;
          color: #ccc;
          font-size: 12px;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
          width: 100%;
          padding: 8px 12px;
          background: #252526;
          border: 1px solid #444;
          border-radius: 4px;
          color: #fff;
          font-size: 14px;
        }

        .platforms-checklist {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 8px;
        }

        .platform-checkbox {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px;
          background: #252526;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .platform-checkbox:hover {
          background: #333;
        }

        .checkbox-custom {
          width: 16px;
          height: 16px;
          border: 2px solid #666;
          border-radius: 3px;
          position: relative;
        }

        .platform-checkbox input:checked + .checkbox-custom {
          background: #ff9800;
          border-color: #ff9800;
        }

        .platform-checkbox input:checked + .checkbox-custom::after {
          content: '✓';
          position: absolute;
          top: -2px;
          left: 2px;
          color: #fff;
          font-size: 12px;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 20px;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;
    
    if (!document.querySelector('#distribution-tracker-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'distribution-tracker-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  syncAllPlatforms() {
    this.showSuccess('Syncing all platforms...');
    // Implementation would sync with all connected platforms
  }

  connectPlatform() {
    this.showInfo('Platform connection wizard would open here');
  }

  destroy() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DistributionTracker;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.DistributionTracker = DistributionTracker;
  window.distributionTracker = null; // Will be set when instantiated
}