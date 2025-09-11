/**
 * Ainflue Desktop - Revenue Analytics Component
 * 
 * Advanced revenue tracking and analytics dashboard for content creators
 * Implements real-time monetization insights, forecasting, and optimization
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class RevenueAnalytics {
  constructor(container, analyticsEngine, revenueTracker) {
    this.container = container;
    this.analyticsEngine = analyticsEngine;
    this.revenueTracker = revenueTracker;
    this.currentPeriod = 'month';
    this.revenueStreams = new Map();
    this.forecasting = null;
    
    this.init();
  }

  init() {
    this.createAnalyticsInterface();
    this.setupEventListeners();
    this.initializeAnalytics();
    this.loadRevenueData();
  }

  createAnalyticsInterface() {
    this.container.innerHTML = `
      <div class="revenue-analytics">
        <div class="analytics-header">
          <h3><i class="fas fa-chart-line"></i> Revenue Analytics</h3>
          <div class="period-selector">
            <button class="period-btn active" data-period="day">Day</button>
            <button class="period-btn" data-period="week">Week</button>
            <button class="period-btn active" data-period="month">Month</button>
            <button class="period-btn" data-period="quarter">Quarter</button>
            <button class="period-btn" data-period="year">Year</button>
          </div>
        </div>

        <div class="analytics-content">
          <!-- Revenue Overview -->
          <div class="revenue-overview">
            <div class="overview-cards">
              <div class="revenue-card total">
                <div class="card-icon"><i class="fas fa-dollar-sign"></i></div>
                <div class="card-content">
                  <div class="card-value" id="totalRevenue">$0</div>
                  <div class="card-label">Total Revenue</div>
                  <div class="card-change positive" id="totalChange">+0%</div>
                </div>
              </div>
              
              <div class="revenue-card monthly">
                <div class="card-icon"><i class="fas fa-calendar-alt"></i></div>
                <div class="card-content">
                  <div class="card-value" id="monthlyRevenue">$0</div>
                  <div class="card-label">This Month</div>
                  <div class="card-change" id="monthlyChange">+0%</div>
                </div>
              </div>
              
              <div class="revenue-card daily">
                <div class="card-icon"><i class="fas fa-clock"></i></div>
                <div class="card-content">
                  <div class="card-value" id="dailyRevenue">$0</div>
                  <div class="card-label">Today</div>
                  <div class="card-change" id="dailyChange">+0%</div>
                </div>
              </div>
              
              <div class="revenue-card rpm">
                <div class="card-icon"><i class="fas fa-eye"></i></div>
                <div class="card-content">
                  <div class="card-value" id="revenuePerMille">$0</div>
                  <div class="card-label">RPM</div>
                  <div class="card-change" id="rpmChange">+0%</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Revenue Chart -->
          <div class="revenue-chart-section">
            <div class="chart-header">
              <h4>Revenue Trend</h4>
              <div class="chart-controls">
                <select id="chartMetric">
                  <option value="revenue">Revenue</option>
                  <option value="views">Views</option>
                  <option value="engagement">Engagement</option>
                  <option value="rpm">RPM</option>
                </select>
                <button class="btn-small" id="exportChart">
                  <i class="fas fa-download"></i>
                  Export
                </button>
              </div>
            </div>
            <div class="chart-container">
              <canvas id="revenueChart" width="800" height="300"></canvas>
            </div>
          </div>

          <!-- Revenue Streams -->
          <div class="revenue-streams">
            <div class="streams-header">
              <h4>Revenue Streams</h4>
              <button class="btn-primary" id="addRevenueStream">
                <i class="fas fa-plus"></i>
                Add Stream
              </button>
            </div>
            <div class="streams-grid" id="streamsGrid">
              <!-- Revenue streams will be populated here -->
            </div>
          </div>

          <!-- Platform Breakdown -->
          <div class="platform-breakdown">
            <div class="breakdown-header">
              <h4>Platform Performance</h4>
              <div class="breakdown-controls">
                <button class="btn-small" id="refreshPlatforms">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
              </div>
            </div>
            <div class="platforms-container">
              <div class="platforms-chart">
                <canvas id="platformsChart" width="400" height="400"></canvas>
              </div>
              <div class="platforms-details" id="platformsDetails">
                <!-- Platform details will be populated here -->
              </div>
            </div>
          </div>

          <!-- Revenue Forecasting -->
          <div class="revenue-forecasting">
            <div class="forecasting-header">
              <h4>Revenue Forecasting</h4>
              <div class="forecasting-controls">
                <select id="forecastPeriod">
                  <option value="week">Next Week</option>
                  <option value="month">Next Month</option>
                  <option value="quarter">Next Quarter</option>
                  <option value="year">Next Year</option>
                </select>
                <button class="btn-primary" id="generateForecast">
                  <i class="fas fa-crystal-ball"></i>
                  Generate Forecast
                </button>
              </div>
            </div>
            <div class="forecast-container" id="forecastContainer">
              <div class="no-forecast">
                <i class="fas fa-chart-area"></i>
                <p>Generate AI-powered revenue forecasts</p>
              </div>
            </div>
          </div>

          <!-- Top Performing Content -->
          <div class="top-content">
            <div class="content-header">
              <h4>Top Performing Content</h4>
              <div class="content-filters">
                <select id="contentPeriod">
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                  <option value="quarter">This Quarter</option>
                </select>
                <select id="contentMetric">
                  <option value="revenue">By Revenue</option>
                  <option value="views">By Views</option>
                  <option value="engagement">By Engagement</option>
                </select>
              </div>
            </div>
            <div class="content-list" id="topContentList">
              <!-- Top content will be populated here -->
            </div>
          </div>

          <!-- Revenue Optimization -->
          <div class="revenue-optimization">
            <div class="optimization-header">
              <h4>Revenue Optimization</h4>
              <button class="btn-secondary" id="runOptimization">
                <i class="fas fa-magic"></i>
                Run AI Analysis
              </button>
            </div>
            <div class="optimization-insights" id="optimizationInsights">
              <div class="no-insights">
                <i class="fas fa-lightbulb"></i>
                <p>Run AI analysis to get revenue optimization insights</p>
              </div>
            </div>
          </div>

          <!-- Revenue Goals -->
          <div class="revenue-goals">
            <div class="goals-header">
              <h4>Revenue Goals</h4>
              <button class="btn-primary" id="setGoal">
                <i class="fas fa-target"></i>
                Set Goal
              </button>
            </div>
            <div class="goals-container" id="goalsContainer">
              <!-- Goals will be populated here -->
            </div>
          </div>
        </div>

        <!-- Revenue Stream Modal -->
        <div class="modal-overlay" id="revenueStreamModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4 id="streamModalTitle">Add Revenue Stream</h4>
              <button class="modal-close" id="closeStreamModal">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <form id="revenueStreamForm">
                <div class="form-group">
                  <label>Stream Name</label>
                  <input type="text" name="name" placeholder="e.g., YouTube Ad Revenue" required>
                </div>
                <div class="form-group">
                  <label>Platform</label>
                  <select name="platform" required>
                    <option value="">Select Platform</option>
                    <option value="youtube">YouTube</option>
                    <option value="tiktok">TikTok</option>
                    <option value="instagram">Instagram</option>
                    <option value="spotify">Spotify</option>
                    <option value="patreon">Patreon</option>
                    <option value="twitch">Twitch</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Revenue Type</label>
                  <select name="type" required>
                    <option value="">Select Type</option>
                    <option value="ad_revenue">Ad Revenue</option>
                    <option value="subscriptions">Subscriptions</option>
                    <option value="donations">Donations</option>
                    <option value="merchandise">Merchandise</option>
                    <option value="sponsorships">Sponsorships</option>
                    <option value="affiliate">Affiliate Marketing</option>
                    <option value="courses">Courses/Education</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Current Monthly Revenue</label>
                  <input type="number" name="monthlyRevenue" placeholder="0" step="0.01" min="0">
                </div>
                <div class="form-group">
                  <label>Growth Rate (%)</label>
                  <input type="number" name="growthRate" placeholder="0" step="0.1">
                </div>
                <div class="form-actions">
                  <button type="button" class="btn-secondary" onclick="window.revenueAnalytics?.hideStreamModal()">
                    Cancel
                  </button>
                  <button type="submit" class="btn-primary">
                    Add Stream
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
    // Period selection
    this.container.querySelectorAll('.period-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.changePeriod(e.target.dataset.period);
      });
    });

    // Chart controls
    this.container.querySelector('#chartMetric').addEventListener('change', () => {
      this.updateChart();
    });

    this.container.querySelector('#exportChart').addEventListener('click', () => {
      this.exportChart();
    });

    // Revenue stream management
    this.container.querySelector('#addRevenueStream').addEventListener('click', () => {
      this.showStreamModal();
    });

    this.container.querySelector('#closeStreamModal').addEventListener('click', () => {
      this.hideStreamModal();
    });

    this.container.querySelector('#revenueStreamForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.addRevenueStream(e.target);
    });

    // Platform breakdown
    this.container.querySelector('#refreshPlatforms').addEventListener('click', () => {
      this.refreshPlatformData();
    });

    // Forecasting
    this.container.querySelector('#generateForecast').addEventListener('click', () => {
      this.generateForecast();
    });

    // Optimization
    this.container.querySelector('#runOptimization').addEventListener('click', () => {
      this.runOptimizationAnalysis();
    });

    // Goals
    this.container.querySelector('#setGoal').addEventListener('click', () => {
      this.showGoalModal();
    });

    // Content filters
    this.container.querySelector('#contentPeriod').addEventListener('change', () => {
      this.updateTopContent();
    });

    this.container.querySelector('#contentMetric').addEventListener('change', () => {
      this.updateTopContent();
    });
  }

  initializeAnalytics() {
    this.initializeCharts();
    this.loadRevenueStreams();
    this.updateOverviewCards();
  }

  async loadRevenueData() {
    try {
      const revenueData = await this.revenueTracker.getRevenueData(this.currentPeriod);
      this.updateAnalytics(revenueData);
    } catch (error) {
      console.error('Failed to load revenue data:', error);
      this.showError('Failed to load revenue data');
    }
  }

  changePeriod(period) {
    // Update button states
    this.container.querySelectorAll('.period-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    this.container.querySelector(`[data-period="${period}"]`).classList.add('active');

    this.currentPeriod = period;
    this.loadRevenueData();
  }

  updateAnalytics(data) {
    this.updateOverviewCards(data);
    this.updateChart(data);
    this.updatePlatformBreakdown(data);
    this.updateTopContent(data);
  }

  updateOverviewCards(data = {}) {
    const cards = {
      totalRevenue: data.total || 0,
      monthlyRevenue: data.monthly || 0,
      dailyRevenue: data.daily || 0,
      revenuePerMille: data.rpm || 0
    };

    const changes = {
      totalChange: data.totalChange || 0,
      monthlyChange: data.monthlyChange || 0,
      dailyChange: data.dailyChange || 0,
      rpmChange: data.rpmChange || 0
    };

    // Update values
    Object.entries(cards).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        element.textContent = this.formatCurrency(value);
      }
    });

    // Update changes
    Object.entries(changes).forEach(([key, value]) => {
      const element = this.container.querySelector(`#${key}`);
      if (element) {
        element.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
        element.className = `card-change ${value >= 0 ? 'positive' : 'negative'}`;
      }
    });
  }

  initializeCharts() {
    // Initialize revenue trend chart
    const revenueCtx = this.container.querySelector('#revenueChart');
    if (revenueCtx) {
      this.revenueChart = this.createChart(revenueCtx, 'line');
    }

    // Initialize platform breakdown chart
    const platformsCtx = this.container.querySelector('#platformsChart');
    if (platformsCtx) {
      this.platformsChart = this.createChart(platformsCtx, 'doughnut');
    }
  }

  createChart(canvas, type) {
    const ctx = canvas.getContext('2d');
    
    // Mock chart implementation - replace with actual Chart.js
    const mockChart = {
      canvas,
      type,
      update: (data) => {
        this.drawMockChart(ctx, data, type);
      },
      destroy: () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    };

    return mockChart;
  }

  drawMockChart(ctx, data, type) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    
    if (type === 'line') {
      this.drawLineChart(ctx, data);
    } else if (type === 'doughnut') {
      this.drawDoughnutChart(ctx, data);
    }
  }

  drawLineChart(ctx, data = {}) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 40;
    
    // Mock data points
    const points = data.points || [
      {x: padding, y: height - 80},
      {x: width * 0.2, y: height - 120},
      {x: width * 0.4, y: height - 100},
      {x: width * 0.6, y: height - 150},
      {x: width * 0.8, y: height - 130},
      {x: width - padding, y: height - 180}
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

    // Draw line
    ctx.strokeStyle = '#4caf50';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(point => {
      ctx.lineTo(point.x, point.y);
    });
    ctx.stroke();

    // Draw points
    ctx.fillStyle = '#4caf50';
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      ctx.fill();
    });
  }

  drawDoughnutChart(ctx, data = {}) {
    const centerX = ctx.canvas.width / 2;
    const centerY = ctx.canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;
    const innerRadius = radius * 0.6;

    const segments = data.segments || [
      {label: 'YouTube', value: 40, color: '#ff0000'},
      {label: 'TikTok', value: 25, color: '#000000'},
      {label: 'Instagram', value: 20, color: '#e4405f'},
      {label: 'Spotify', value: 15, color: '#1db954'}
    ];

    let currentAngle = -Math.PI / 2;
    const total = segments.reduce((sum, seg) => sum + seg.value, 0);

    segments.forEach(segment => {
      const segmentAngle = (segment.value / total) * 2 * Math.PI;
      
      // Draw segment
      ctx.fillStyle = segment.color;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + segmentAngle);
      ctx.arc(centerX, centerY, innerRadius, currentAngle + segmentAngle, currentAngle, true);
      ctx.closePath();
      ctx.fill();

      currentAngle += segmentAngle;
    });

    // Draw center text
    ctx.fillStyle = '#fff';
    ctx.font = '16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Revenue', centerX, centerY - 5);
    ctx.fillText('Breakdown', centerX, centerY + 15);
  }

  updateChart(data) {
    const metric = this.container.querySelector('#chartMetric').value;
    const chartData = this.prepareChartData(data, metric);
    
    if (this.revenueChart) {
      this.revenueChart.update(chartData);
    }
  }

  prepareChartData(data, metric) {
    // Mock data preparation
    return {
      points: this.generateMockDataPoints(metric),
      metric
    };
  }

  generateMockDataPoints(metric) {
    const baseValues = {
      revenue: [1000, 1200, 1100, 1500, 1300, 1800],
      views: [50000, 60000, 55000, 75000, 65000, 90000],
      engagement: [2500, 3000, 2750, 3750, 3250, 4500],
      rpm: [20, 24, 22, 30, 26, 36]
    };

    const values = baseValues[metric] || baseValues.revenue;
    const width = this.container.querySelector('#revenueChart').width;
    const height = this.container.querySelector('#revenueChart').height;
    const padding = 40;

    return values.map((value, index) => ({
      x: padding + (index * (width - 2 * padding) / (values.length - 1)),
      y: height - padding - (value / Math.max(...values)) * (height - 2 * padding)
    }));
  }

  async loadRevenueStreams() {
    try {
      const streams = await this.revenueTracker.getRevenueStreams();
      streams.forEach(stream => {
        this.revenueStreams.set(stream.id, stream);
      });
      this.displayRevenueStreams();
    } catch (error) {
      console.error('Failed to load revenue streams:', error);
    }
  }

  displayRevenueStreams() {
    const container = this.container.querySelector('#streamsGrid');
    
    if (this.revenueStreams.size === 0) {
      container.innerHTML = `
        <div class="no-streams">
          <i class="fas fa-stream"></i>
          <p>No revenue streams configured</p>
          <button class="btn-link" onclick="window.revenueAnalytics?.showStreamModal()">
            Add your first revenue stream
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = Array.from(this.revenueStreams.values()).map(stream => `
      <div class="stream-card">
        <div class="stream-header">
          <div class="stream-info">
            <h5 class="stream-name">${stream.name}</h5>
            <span class="stream-platform">${stream.platform}</span>
          </div>
          <div class="stream-actions">
            <button class="btn-tiny" onclick="window.revenueAnalytics?.editStream('${stream.id}')">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-tiny danger" onclick="window.revenueAnalytics?.removeStream('${stream.id}')">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
        <div class="stream-metrics">
          <div class="stream-revenue">
            <span class="metric-value">${this.formatCurrency(stream.monthlyRevenue)}</span>
            <span class="metric-label">Monthly</span>
          </div>
          <div class="stream-growth">
            <span class="metric-value ${stream.growthRate >= 0 ? 'positive' : 'negative'}">
              ${stream.growthRate >= 0 ? '+' : ''}${stream.growthRate}%
            </span>
            <span class="metric-label">Growth</span>
          </div>
        </div>
        <div class="stream-progress">
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${Math.min(100, (stream.monthlyRevenue / 10000) * 100)}%"></div>
          </div>
        </div>
      </div>
    `).join('');
  }

  updatePlatformBreakdown(data) {
    const platformData = data?.platforms || this.getMockPlatformData();
    
    // Update chart
    if (this.platformsChart) {
      this.platformsChart.update({
        segments: platformData.map(platform => ({
          label: platform.name,
          value: platform.revenue,
          color: platform.color
        }))
      });
    }

    // Update details
    this.displayPlatformDetails(platformData);
  }

  displayPlatformDetails(platforms) {
    const container = this.container.querySelector('#platformsDetails');
    
    container.innerHTML = platforms.map(platform => `
      <div class="platform-detail">
        <div class="platform-indicator" style="background-color: ${platform.color}"></div>
        <div class="platform-info">
          <span class="platform-name">${platform.name}</span>
          <span class="platform-revenue">${this.formatCurrency(platform.revenue)}</span>
        </div>
        <div class="platform-change ${platform.change >= 0 ? 'positive' : 'negative'}">
          ${platform.change >= 0 ? '+' : ''}${platform.change}%
        </div>
      </div>
    `).join('');
  }

  getMockPlatformData() {
    return [
      {name: 'YouTube', revenue: 2500, change: 12.5, color: '#ff0000'},
      {name: 'TikTok', revenue: 1800, change: 8.3, color: '#000000'},
      {name: 'Instagram', revenue: 1200, change: -2.1, color: '#e4405f'},
      {name: 'Spotify', revenue: 900, change: 15.7, color: '#1db954'},
      {name: 'Patreon', revenue: 600, change: 5.4, color: '#ff424d'}
    ];
  }

  async generateForecast() {
    try {
      this.showForecastLoading(true);
      
      const period = this.container.querySelector('#forecastPeriod').value;
      const historicalData = await this.revenueTracker.getHistoricalData();
      const forecast = await this.analyticsEngine.generateRevenueForecast(historicalData, period);
      
      this.displayForecast(forecast);
      
    } catch (error) {
      console.error('Forecast generation failed:', error);
      this.showError('Failed to generate forecast');
    } finally {
      this.showForecastLoading(false);
    }
  }

  displayForecast(forecast) {
    const container = this.container.querySelector('#forecastContainer');
    
    container.innerHTML = `
      <div class="forecast-results">
        <div class="forecast-summary">
          <div class="forecast-card">
            <h5>Predicted Revenue</h5>
            <div class="forecast-value">${this.formatCurrency(forecast.predictedRevenue)}</div>
            <div class="forecast-confidence">Confidence: ${forecast.confidence}%</div>
          </div>
          <div class="forecast-card">
            <h5>Growth Rate</h5>
            <div class="forecast-value ${forecast.growthRate >= 0 ? 'positive' : 'negative'}">
              ${forecast.growthRate >= 0 ? '+' : ''}${forecast.growthRate}%
            </div>
            <div class="forecast-range">Range: ${forecast.minGrowth}% - ${forecast.maxGrowth}%</div>
          </div>
        </div>
        
        <div class="forecast-factors">
          <h5>Key Factors</h5>
          <ul class="factors-list">
            ${forecast.factors.map(factor => `
              <li class="factor-item ${factor.impact}">
                <span class="factor-name">${factor.name}</span>
                <span class="factor-impact">${factor.impact}</span>
              </li>
            `).join('')}
          </ul>
        </div>
        
        <div class="forecast-recommendations">
          <h5>Recommendations</h5>
          <ul class="recommendations-list">
            ${forecast.recommendations.map(rec => `
              <li class="recommendation-item">
                <i class="fas fa-lightbulb"></i>
                ${rec}
              </li>
            `).join('')}
          </ul>
        </div>
      </div>
    `;
  }

  async runOptimizationAnalysis() {
    try {
      this.showOptimizationLoading(true);
      
      const currentData = await this.revenueTracker.getCurrentMetrics();
      const insights = await this.analyticsEngine.analyzeOptimization(currentData);
      
      this.displayOptimizationInsights(insights);
      
    } catch (error) {
      console.error('Optimization analysis failed:', error);
      this.showError('Failed to run optimization analysis');
    } finally {
      this.showOptimizationLoading(false);
    }
  }

  displayOptimizationInsights(insights) {
    const container = this.container.querySelector('#optimizationInsights');
    
    container.innerHTML = `
      <div class="optimization-results">
        <div class="optimization-score">
          <div class="score-circle">
            <div class="score-value">${insights.score}</div>
            <div class="score-label">Optimization Score</div>
          </div>
        </div>
        
        <div class="optimization-opportunities">
          <h5>Optimization Opportunities</h5>
          ${insights.opportunities.map(opp => `
            <div class="opportunity-item ${opp.priority}">
              <div class="opportunity-header">
                <span class="opportunity-title">${opp.title}</span>
                <span class="opportunity-impact">+${opp.potentialIncrease}%</span>
              </div>
              <p class="opportunity-description">${opp.description}</p>
              <button class="btn-small primary" onclick="window.revenueAnalytics?.implementOptimization('${opp.id}')">
                Implement
              </button>
            </div>
          `).join('')}
        </div>
        
        <div class="optimization-timeline">
          <h5>Implementation Timeline</h5>
          <div class="timeline-items">
            ${insights.timeline.map(item => `
              <div class="timeline-item">
                <div class="timeline-date">${item.date}</div>
                <div class="timeline-action">${item.action}</div>
                <div class="timeline-impact">${item.expectedImpact}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  updateTopContent(data) {
    const period = this.container.querySelector('#contentPeriod').value;
    const metric = this.container.querySelector('#contentMetric').value;
    
    // Mock top content data
    const topContent = this.getMockTopContent(period, metric);
    
    const container = this.container.querySelector('#topContentList');
    container.innerHTML = topContent.map(content => `
      <div class="content-item">
        <div class="content-thumbnail">
          <img src="${content.thumbnail}" alt="${content.title}" />
          <div class="content-duration">${content.duration}</div>
        </div>
        <div class="content-info">
          <h6 class="content-title">${content.title}</h6>
          <p class="content-platform">${content.platform}</p>
          <div class="content-metrics">
            <span class="metric">
              <i class="fas fa-eye"></i>
              ${this.formatNumber(content.views)}
            </span>
            <span class="metric">
              <i class="fas fa-dollar-sign"></i>
              ${this.formatCurrency(content.revenue)}
            </span>
            <span class="metric">
              <i class="fas fa-heart"></i>
              ${this.formatNumber(content.engagement)}
            </span>
          </div>
        </div>
        <div class="content-performance">
          <div class="performance-score ${this.getPerformanceClass(content.score)}">
            ${content.score}%
          </div>
        </div>
      </div>
    `).join('');
  }

  getMockTopContent(period, metric) {
    return [
      {
        title: 'How to Make Viral Music',
        platform: 'YouTube',
        thumbnail: '/thumbnails/viral-music.jpg',
        duration: '12:34',
        views: 150000,
        revenue: 850,
        engagement: 12500,
        score: 92
      },
      {
        title: 'Behind the Scenes: Studio Setup',
        platform: 'TikTok',
        thumbnail: '/thumbnails/studio-setup.jpg',
        duration: '0:45',
        views: 89000,
        revenue: 320,
        engagement: 8900,
        score: 87
      }
    ];
  }

  // Revenue stream management
  showStreamModal() {
    this.container.querySelector('#revenueStreamModal').style.display = 'flex';
  }

  hideStreamModal() {
    this.container.querySelector('#revenueStreamModal').style.display = 'none';
    this.container.querySelector('#revenueStreamForm').reset();
  }

  addRevenueStream(form) {
    const formData = new FormData(form);
    const stream = {
      id: `stream_${Date.now()}`,
      name: formData.get('name'),
      platform: formData.get('platform'),
      type: formData.get('type'),
      monthlyRevenue: parseFloat(formData.get('monthlyRevenue')) || 0,
      growthRate: parseFloat(formData.get('growthRate')) || 0
    };

    this.revenueStreams.set(stream.id, stream);
    this.displayRevenueStreams();
    this.hideStreamModal();
    this.showSuccess('Revenue stream added successfully');
  }

  // Utility methods
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  getPerformanceClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'average';
    return 'poor';
  }

  showForecastLoading(show) {
    const button = this.container.querySelector('#generateForecast');
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
      button.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-crystal-ball"></i> Generate Forecast';
      button.disabled = false;
    }
  }

  showOptimizationLoading(show) {
    const button = this.container.querySelector('#runOptimization');
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
      button.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-magic"></i> Run AI Analysis';
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

  exportChart() {
    const canvas = this.container.querySelector('#revenueChart');
    const link = document.createElement('a');
    link.download = `revenue_chart_${Date.now()}.png`;
    link.href = canvas.toDataURL();
    link.click();
  }

  addStyles() {
    const styles = `
      <style>
        .revenue-analytics {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .analytics-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
          border-bottom: 1px solid #333;
        }

        .analytics-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .period-selector {
          display: flex;
          gap: 2px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          padding: 2px;
        }

        .period-btn {
          padding: 6px 12px;
          background: none;
          border: none;
          color: #fff;
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .period-btn.active {
          background: rgba(255, 255, 255, 0.2);
        }

        .analytics-content {
          padding: 20px;
        }

        .overview-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .revenue-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 20px;
          background: #252526;
          border-radius: 8px;
          border-left: 4px solid #4caf50;
        }

        .card-icon {
          font-size: 32px;
          color: #4caf50;
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

        .card-change {
          font-size: 12px;
          font-weight: 600;
        }

        .card-change.positive { color: #4caf50; }
        .card-change.negative { color: #f44336; }

        .revenue-chart-section,
        .revenue-streams,
        .platform-breakdown,
        .revenue-forecasting,
        .top-content,
        .revenue-optimization,
        .revenue-goals {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .chart-header,
        .streams-header,
        .breakdown-header,
        .forecasting-header,
        .content-header,
        .optimization-header,
        .goals-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .chart-header h4,
        .streams-header h4,
        .breakdown-header h4,
        .forecasting-header h4,
        .content-header h4,
        .optimization-header h4,
        .goals-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .chart-container {
          position: relative;
          height: 300px;
          margin-top: 16px;
        }

        .streams-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
        }

        .stream-card {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 16px;
          border: 1px solid #333;
        }

        .stream-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .stream-name {
          margin: 0 0 4px 0;
          color: #fff;
          font-size: 14px;
        }

        .stream-platform {
          font-size: 12px;
          color: #999;
          text-transform: capitalize;
        }

        .stream-metrics {
          display: flex;
          justify-content: space-between;
          margin-bottom: 12px;
        }

        .metric-value {
          display: block;
          font-size: 18px;
          font-weight: bold;
          color: #fff;
        }

        .metric-value.positive { color: #4caf50; }
        .metric-value.negative { color: #f44336; }

        .metric-label {
          font-size: 10px;
          color: #999;
          text-transform: uppercase;
        }

        .platforms-container {
          display: flex;
          gap: 20px;
          align-items: center;
        }

        .platforms-chart {
          flex-shrink: 0;
        }

        .platforms-details {
          flex: 1;
        }

        .platform-detail {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 8px 0;
          border-bottom: 1px solid #333;
        }

        .platform-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .platform-info {
          flex: 1;
          display: flex;
          justify-content: space-between;
        }

        .platform-name {
          color: #fff;
          font-size: 14px;
        }

        .platform-revenue {
          color: #4caf50;
          font-weight: 600;
        }

        .platform-change {
          font-size: 12px;
          font-weight: 600;
        }

        .platform-change.positive { color: #4caf50; }
        .platform-change.negative { color: #f44336; }

        .content-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #1a1a1a;
          border-radius: 6px;
          margin-bottom: 12px;
        }

        .content-thumbnail {
          position: relative;
          width: 80px;
          height: 60px;
          border-radius: 4px;
          overflow: hidden;
        }

        .content-thumbnail img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .content-duration {
          position: absolute;
          bottom: 4px;
          right: 4px;
          background: rgba(0, 0, 0, 0.8);
          color: #fff;
          padding: 2px 4px;
          border-radius: 2px;
          font-size: 10px;
        }

        .content-info {
          flex: 1;
        }

        .content-title {
          margin: 0 0 4px 0;
          color: #fff;
          font-size: 14px;
          font-weight: 500;
        }

        .content-platform {
          margin: 0 0 8px 0;
          color: #999;
          font-size: 12px;
        }

        .content-metrics {
          display: flex;
          gap: 16px;
        }

        .content-metrics .metric {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #ccc;
        }

        .performance-score {
          padding: 8px 12px;
          border-radius: 20px;
          font-weight: bold;
          font-size: 14px;
        }

        .performance-score.excellent { background: #4caf50; color: #fff; }
        .performance-score.good { background: #8bc34a; color: #fff; }
        .performance-score.average { background: #ff9800; color: #fff; }
        .performance-score.poor { background: #f44336; color: #fff; }

        .progress-bar {
          width: 100%;
          height: 6px;
          background: #444;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #4caf50;
          transition: width 0.5s ease;
        }

        .btn-primary, .btn-secondary, .btn-small, .btn-tiny {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #4caf50; color: #fff; }
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
          max-width: 500px;
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
        .form-group select {
          width: 100%;
          padding: 8px 12px;
          background: #252526;
          border: 1px solid #444;
          border-radius: 4px;
          color: #fff;
          font-size: 14px;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 20px;
        }

        .no-streams,
        .no-forecast,
        .no-insights {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }

        .no-streams i,
        .no-forecast i,
        .no-insights i {
          font-size: 48px;
          margin-bottom: 16px;
          color: #444;
        }

        .btn-link {
          background: none;
          border: none;
          color: #4caf50;
          cursor: pointer;
          text-decoration: underline;
          font-size: 14px;
        }
      </style>
    `;
    
    if (!document.querySelector('#revenue-analytics-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'revenue-analytics-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  refreshData() {
    this.loadRevenueData();
  }

  exportData() {
    const data = {
      timestamp: new Date().toISOString(),
      period: this.currentPeriod,
      revenueStreams: Array.from(this.revenueStreams.values()),
      overview: this.getOverviewData()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `revenue_analytics_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  getOverviewData() {
    return {
      totalRevenue: this.container.querySelector('#totalRevenue').textContent,
      monthlyRevenue: this.container.querySelector('#monthlyRevenue').textContent,
      dailyRevenue: this.container.querySelector('#dailyRevenue').textContent,
      rpm: this.container.querySelector('#revenuePerMille').textContent
    };
  }

  destroy() {
    if (this.revenueChart) {
      this.revenueChart.destroy();
    }
    if (this.platformsChart) {
      this.platformsChart.destroy();
    }
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RevenueAnalytics;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.RevenueAnalytics = RevenueAnalytics;
  window.revenueAnalytics = null; // Will be set when instantiated
}