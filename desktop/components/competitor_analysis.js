/**
 * Ainflue Desktop - Competitor Analysis Component
 * 
 * Advanced competitor tracking and competitive intelligence
 * Implements comprehensive competitor monitoring, analysis, and strategic insights
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class CompetitorAnalysis {
  constructor(container, competitorEngine, marketIntelligence) {
    this.container = container;
    this.competitorEngine = competitorEngine;
    this.marketIntelligence = marketIntelligence;
    this.competitors = new Map();
    this.watchedCompetitors = new Set();
    this.analysisResults = {};
    
    this.init();
  }

  init() {
    this.createAnalysisInterface();
    this.setupEventListeners();
    this.initializeCompetitorTracking();
    this.loadCompetitorData();
  }

  createAnalysisInterface() {
    this.container.innerHTML = `
      <div class="competitor-analysis">
        <div class="analysis-header">
          <h3><i class="fas fa-crosshairs"></i> Competitor Analysis</h3>
          <div class="analysis-controls">
            <div class="tracking-status">
              <div class="status-indicator active" id="trackingStatus">
                <div class="status-light"></div>
                <span>Tracking Active</span>
              </div>
            </div>
            <button class="btn-primary" id="addCompetitor">
              <i class="fas fa-plus"></i>
              Add Competitor
            </button>
          </div>
        </div>

        <div class="analysis-content">
          <!-- Competitive Overview -->
          <div class="competitive-overview">
            <div class="overview-metrics">
              <div class="overview-card market-position">
                <div class="card-icon"><i class="fas fa-chart-line"></i></div>
                <div class="card-content">
                  <div class="card-value" id="marketPosition">#0</div>
                  <div class="card-label">Market Position</div>
                  <div class="card-change" id="positionChange">-</div>
                </div>
                <div class="position-chart" id="positionChart"></div>
              </div>

              <div class="overview-card competitive-score">
                <div class="card-icon"><i class="fas fa-trophy"></i></div>
                <div class="card-content">
                  <div class="card-value" id="competitiveScore">0</div>
                  <div class="card-label">Competitive Score</div>
                  <div class="card-change" id="scoreChange">+0</div>
                </div>
                <div class="score-gauge" id="scoreGauge"></div>
              </div>

              <div class="overview-card market-share">
                <div class="card-icon"><i class="fas fa-pie-chart"></i></div>
                <div class="card-content">
                  <div class="card-value" id="marketShare">0%</div>
                  <div class="card-label">Market Share</div>
                  <div class="card-change" id="shareChange">+0%</div>
                </div>
                <div class="share-visualization" id="shareVisualization"></div>
              </div>

              <div class="overview-card growth-rate">
                <div class="card-icon"><i class="fas fa-trending-up"></i></div>
                <div class="card-content">
                  <div class="card-value" id="growthRate">0%</div>
                  <div class="card-label">Growth Rate</div>
                  <div class="card-change" id="growthChange">+0%</div>
                </div>
                <div class="growth-trend" id="growthTrend"></div>
              </div>
            </div>
          </div>

          <!-- Competitor Tracking -->
          <div class="competitor-tracking">
            <div class="tracking-header">
              <h4>Competitor Tracking</h4>
              <div class="tracking-controls">
                <select id="trackingTimeframe">
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                </select>
                <button class="btn-small" id="refreshTracking">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
              </div>
            </div>
            <div class="competitors-grid" id="competitorsGrid">
              <!-- Competitor cards will be populated here -->
            </div>
          </div>

          <!-- Competitive Intelligence -->
          <div class="competitive-intelligence">
            <div class="intelligence-header">
              <h4>AI Competitive Intelligence</h4>
              <button class="btn-primary" id="generateIntelligence">
                <i class="fas fa-brain"></i>
                Generate Insights
              </button>
            </div>
            <div class="intelligence-container" id="intelligenceContainer">
              <div class="no-intelligence">
                <i class="fas fa-lightbulb"></i>
                <p>Generate AI insights to discover competitive opportunities</p>
              </div>
            </div>
          </div>

          <!-- SWOT Analysis -->
          <div class="swot-analysis">
            <div class="swot-header">
              <h4>SWOT Analysis</h4>
              <button class="btn-secondary" id="updateSWOT">
                <i class="fas fa-sync-alt"></i>
                Update Analysis
              </button>
            </div>
            <div class="swot-grid" id="swotGrid">
              <div class="swot-quadrant strengths">
                <h5><i class="fas fa-plus-circle"></i> Strengths</h5>
                <ul id="strengthsList">
                  <li>Strong brand recognition in target market</li>
                  <li>High-quality content production capabilities</li>
                  <li>Engaged and loyal audience base</li>
                </ul>
              </div>
              <div class="swot-quadrant weaknesses">
                <h5><i class="fas fa-minus-circle"></i> Weaknesses</h5>
                <ul id="weaknessesList">
                  <li>Limited presence on emerging platforms</li>
                  <li>Lower posting frequency than competitors</li>
                  <li>Opportunities for SEO optimization</li>
                </ul>
              </div>
              <div class="swot-quadrant opportunities">
                <h5><i class="fas fa-lightbulb"></i> Opportunities</h5>
                <ul id="opportunitiesList">
                  <li>Expansion to TikTok and YouTube Shorts</li>
                  <li>Collaboration with trending influencers</li>
                  <li>Integration of AI-powered content tools</li>
                </ul>
              </div>
              <div class="swot-quadrant threats">
                <h5><i class="fas fa-exclamation-triangle"></i> Threats</h5>
                <ul id="threatsList">
                  <li>Increasing competition in content space</li>
                  <li>Platform algorithm changes affecting reach</li>
                  <li>Rising content production costs</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Alerts & Notifications -->
          <div class="competitive-alerts">
            <div class="alerts-header">
              <h4>Competitive Alerts</h4>
              <div class="alerts-controls">
                <button class="btn-small" id="configureAlerts">
                  <i class="fas fa-cog"></i>
                  Configure
                </button>
                <button class="btn-small" id="clearAlerts">
                  <i class="fas fa-trash"></i>
                  Clear
                </button>
              </div>
            </div>
            <div class="alerts-container" id="alertsContainer">
              <div class="no-alerts">
                <i class="fas fa-bell"></i>
                <p>No competitive alerts</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Add Competitor Modal -->
        <div class="modal-overlay" id="addCompetitorModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4>Add Competitor</h4>
              <button class="modal-close" id="closeCompetitorModal">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <form id="addCompetitorForm">
                <div class="form-group">
                  <label>Competitor Name</label>
                  <input type="text" name="name" placeholder="e.g., Competitor Channel" required>
                </div>
                <div class="form-group">
                  <label>Primary Platform</label>
                  <select name="platform" required>
                    <option value="">Select Platform</option>
                    <option value="youtube">YouTube</option>
                    <option value="tiktok">TikTok</option>
                    <option value="instagram">Instagram</option>
                    <option value="twitter">Twitter</option>
                    <option value="twitch">Twitch</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Handle/Username</label>
                  <input type="text" name="handle" placeholder="@username" required>
                </div>
                <div class="form-group">
                  <label>Category</label>
                  <select name="category">
                    <option value="direct">Direct Competitor</option>
                    <option value="indirect">Indirect Competitor</option>
                    <option value="aspirational">Aspirational</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Tracking Level</label>
                  <select name="trackingLevel">
                    <option value="basic">Basic Monitoring</option>
                    <option value="detailed">Detailed Analysis</option>
                    <option value="comprehensive">Comprehensive Tracking</option>
                  </select>
                </div>
                <div class="form-actions">
                  <button type="button" class="btn-secondary" onclick="window.competitorAnalysis?.hideCompetitorModal()">
                    Cancel
                  </button>
                  <button type="submit" class="btn-primary">
                    Add Competitor
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
    // Add competitor functionality
    this.container.querySelector('#addCompetitor').addEventListener('click', () => {
      this.showCompetitorModal();
    });

    this.container.querySelector('#closeCompetitorModal').addEventListener('click', () => {
      this.hideCompetitorModal();
    });

    this.container.querySelector('#addCompetitorForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.addCompetitor(e.target);
    });

    // Tracking controls
    this.container.querySelector('#trackingTimeframe').addEventListener('change', () => {
      this.updateCompetitorTracking();
    });

    this.container.querySelector('#refreshTracking').addEventListener('click', () => {
      this.refreshTrackingData();
    });

    // Intelligence and analysis
    this.container.querySelector('#generateIntelligence').addEventListener('click', () => {
      this.generateCompetitiveIntelligence();
    });

    this.container.querySelector('#updateSWOT').addEventListener('click', () => {
      this.updateSWOTAnalysis();
    });

    // Alerts
    this.container.querySelector('#configureAlerts').addEventListener('click', () => {
      this.showAlertsConfiguration();
    });

    this.container.querySelector('#clearAlerts').addEventListener('click', () => {
      this.clearAllAlerts();
    });
  }

  initializeCompetitorTracking() {
    this.loadTrackedCompetitors();
    this.startCompetitiveMonitoring();
    this.updateCompetitiveOverview();
  }

  async loadCompetitorData() {
    try {
      // Mock data for initial load
      const data = {
        marketPosition: 5,
        competitiveScore: 78,
        marketShare: 12.5,
        growthRate: 15.3,
        positionChange: 2,
        scoreChange: 5,
        shareChange: 2.1,
        growthChange: 3.2
      };
      
      this.updateOverviewMetrics(data);
      this.updateCompetitorTracking();
    } catch (error) {
      console.error('Failed to load competitor data:', error);
      this.showError('Failed to load competitor data');
    }
  }

  updateOverviewMetrics(data) {
    // Update metric values
    this.container.querySelector('#marketPosition').textContent = `#${data.marketPosition}`;
    this.container.querySelector('#competitiveScore').textContent = data.competitiveScore;
    this.container.querySelector('#marketShare').textContent = `${data.marketShare}%`;
    this.container.querySelector('#growthRate').textContent = `${data.growthRate}%`;

    // Update changes
    this.container.querySelector('#positionChange').textContent = `+${data.positionChange}`;
    this.container.querySelector('#scoreChange').textContent = `+${data.scoreChange}`;
    this.container.querySelector('#shareChange').textContent = `+${data.shareChange}%`;
    this.container.querySelector('#growthChange').textContent = `+${data.growthChange}%`;

    // Update gauge
    this.updateScoreGauge(data.competitiveScore);
  }

  updateScoreGauge(score) {
    const container = this.container.querySelector('#scoreGauge');
    if (!container) return;

    const percentage = Math.min(score / 100, 1) * 100;
    const color = score >= 80 ? '#4caf50' : score >= 60 ? '#ff9800' : '#f44336';

    container.innerHTML = `
      <div class="gauge-bar">
        <div class="gauge-fill" style="width: ${percentage}%; background: ${color}"></div>
      </div>
    `;
  }

  async updateCompetitorTracking() {
    // Mock competitor data
    const competitors = [
      {
        id: '1',
        name: 'TechReviewer Pro',
        platform: 'youtube',
        handle: 'techreviewerpro',
        category: 'direct',
        avatar: '/avatars/competitor1.jpg',
        followers: 250000,
        engagement: 4.2,
        postFrequency: 3.5,
        followersChange: 12.5,
        engagementChange: -2.1,
        frequencyChange: 8.3,
        contentAlert: true,
        growthAlert: false,
        engagementAlert: false,
        performanceHistory: [45, 48, 52, 49, 55, 58, 54, 60]
      },
      {
        id: '2',
        name: 'Creative Studio',
        platform: 'instagram',
        handle: 'creativestudio',
        category: 'indirect',
        avatar: '/avatars/competitor2.jpg',
        followers: 180000,
        engagement: 6.8,
        postFrequency: 5.2,
        followersChange: 8.7,
        engagementChange: 5.4,
        frequencyChange: -1.2,
        contentAlert: false,
        growthAlert: true,
        engagementAlert: false,
        performanceHistory: [38, 42, 45, 47, 49, 52, 48, 51]
      }
    ];

    this.displayCompetitorCards(competitors);
  }

  displayCompetitorCards(competitors) {
    const container = this.container.querySelector('#competitorsGrid');
    
    if (!competitors || competitors.length === 0) {
      container.innerHTML = `
        <div class="no-competitors">
          <i class="fas fa-users"></i>
          <p>No competitors being tracked</p>
          <button class="btn-link" onclick="window.competitorAnalysis?.showCompetitorModal()">
            Add your first competitor
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = competitors.map(competitor => `
      <div class="competitor-card ${competitor.category}">
        <div class="competitor-header">
          <div class="competitor-info">
            <div class="competitor-avatar">
              <div class="avatar-placeholder">
                <i class="fas fa-user"></i>
              </div>
              <div class="platform-badge">
                <i class="fab fa-${competitor.platform}"></i>
              </div>
            </div>
            <div class="competitor-details">
              <h5 class="competitor-name">${competitor.name}</h5>
              <span class="competitor-handle">@${competitor.handle}</span>
              <span class="competitor-category">${competitor.category}</span>
            </div>
          </div>
          <div class="competitor-actions">
            <button class="btn-tiny" onclick="window.competitorAnalysis?.viewCompetitor('${competitor.id}')">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn-tiny" onclick="window.competitorAnalysis?.editCompetitor('${competitor.id}')">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-tiny danger" onclick="window.competitorAnalysis?.removeCompetitor('${competitor.id}')">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <div class="competitor-metrics">
          <div class="metric-row">
            <span class="metric-label">Followers</span>
            <span class="metric-value">${this.formatNumber(competitor.followers)}</span>
            <span class="metric-change ${competitor.followersChange >= 0 ? 'positive' : 'negative'}">
              ${competitor.followersChange >= 0 ? '+' : ''}${competitor.followersChange.toFixed(1)}%
            </span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Engagement</span>
            <span class="metric-value">${competitor.engagement.toFixed(1)}%</span>
            <span class="metric-change ${competitor.engagementChange >= 0 ? 'positive' : 'negative'}">
              ${competitor.engagementChange >= 0 ? '+' : ''}${competitor.engagementChange.toFixed(1)}%
            </span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Post Frequency</span>
            <span class="metric-value">${competitor.postFrequency}/day</span>
            <span class="metric-change ${competitor.frequencyChange >= 0 ? 'positive' : 'negative'}">
              ${competitor.frequencyChange >= 0 ? '+' : ''}${competitor.frequencyChange.toFixed(1)}%
            </span>
          </div>
        </div>

        <div class="competitor-chart">
          <canvas class="mini-chart" data-competitor="${competitor.id}" width="200" height="60"></canvas>
        </div>

        <div class="competitor-status">
          <div class="status-indicators">
            <div class="status-item ${competitor.contentAlert ? 'alert' : ''}">
              <i class="fas fa-file-alt"></i>
              <span>Content</span>
            </div>
            <div class="status-item ${competitor.growthAlert ? 'alert' : ''}">
              <i class="fas fa-chart-line"></i>
              <span>Growth</span>
            </div>
            <div class="status-item ${competitor.engagementAlert ? 'alert' : ''}">
              <i class="fas fa-heart"></i>
              <span>Engagement</span>
            </div>
          </div>
        </div>
      </div>
    `).join('');

    // Draw mini charts
    competitors.forEach(competitor => {
      this.drawCompetitorChart(competitor.id, competitor.performanceHistory);
    });
  }

  drawCompetitorChart(competitorId, data) {
    const canvas = this.container.querySelector(`canvas[data-competitor="${competitorId}"]`);
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
    ctx.strokeStyle = '#f44336';
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

  async generateCompetitiveIntelligence() {
    try {
      this.showIntelligenceLoading(true);
      
      // Mock intelligence data
      const intelligence = {
        insights: [
          {
            id: '1',
            type: 'Content Gap',
            priority: 'high',
            title: 'Underutilized Short-Form Content',
            description: 'Competitors are gaining 40% more engagement with short-form content. Consider increasing your TikTok and YouTube Shorts presence.'
          },
          {
            id: '2',
            type: 'Posting Schedule',
            priority: 'medium',
            title: 'Optimal Posting Times Identified',
            description: 'Analysis shows your competitors post 35% more during peak engagement hours (6-8 PM). Adjusting your schedule could increase reach by 25%.'
          },
          {
            id: '3',
            type: 'Collaboration Opportunity',
            priority: 'low',
            title: 'Cross-Promotion Potential',
            description: 'TechReviewer Pro has 15% audience overlap with your channel. A collaboration could benefit both parties with minimal audience cannibalization.'
          }
        ]
      };
      
      this.displayCompetitiveIntelligence(intelligence);
      
    } catch (error) {
      console.error('Failed to generate intelligence:', error);
      this.showError('Failed to generate competitive intelligence');
    } finally {
      this.showIntelligenceLoading(false);
    }
  }

  displayCompetitiveIntelligence(intelligence) {
    const container = this.container.querySelector('#intelligenceContainer');
    
    container.innerHTML = `
      <div class="intelligence-results">
        ${intelligence.insights?.map(insight => `
          <div class="intelligence-item ${insight.priority}">
            <div class="intelligence-header">
              <div class="intelligence-type">${insight.type}</div>
              <div class="intelligence-priority ${insight.priority}">${insight.priority}</div>
            </div>
            <h6 class="intelligence-title">${insight.title}</h6>
            <p class="intelligence-description">${insight.description}</p>
            <div class="intelligence-actions">
              <button class="btn-small primary" onclick="window.competitorAnalysis?.implementInsight('${insight.id}')">
                Implement
              </button>
              <button class="btn-small secondary" onclick="window.competitorAnalysis?.saveInsight('${insight.id}')">
                Save for Later
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // Modal functionality
  showCompetitorModal() {
    this.container.querySelector('#addCompetitorModal').style.display = 'flex';
  }

  hideCompetitorModal() {
    this.container.querySelector('#addCompetitorModal').style.display = 'none';
    this.container.querySelector('#addCompetitorForm').reset();
  }

  addCompetitor(form) {
    const formData = new FormData(form);
    const competitor = {
      name: formData.get('name'),
      platform: formData.get('platform'),
      handle: formData.get('handle'),
      category: formData.get('category'),
      trackingLevel: formData.get('trackingLevel')
    };

    this.createCompetitorTracking(competitor);
  }

  async createCompetitorTracking(competitor) {
    try {
      // Mock adding competitor
      this.hideCompetitorModal();
      this.showSuccess('Competitor added successfully');
      this.updateCompetitorTracking();
    } catch (error) {
      console.error('Failed to add competitor:', error);
      this.showError('Failed to add competitor');
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

  showIntelligenceLoading(show) {
    const button = this.container.querySelector('#generateIntelligence');
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

  addStyles() {
    const styles = `
      <style>
        .competitor-analysis {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .analysis-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
          border-bottom: 1px solid #333;
        }

        .analysis-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .analysis-controls {
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
          background: #4caf50;
          animation: pulse 2s infinite;
        }

        .analysis-content {
          padding: 20px;
        }

        .overview-metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .overview-card {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          border-left: 4px solid #f44336;
          position: relative;
        }

        .overview-card.competitive-score { border-left-color: #ff9800; }
        .overview-card.market-share { border-left-color: #2196f3; }
        .overview-card.growth-rate { border-left-color: #4caf50; }

        .card-icon {
          font-size: 28px;
          color: #f44336;
          margin-bottom: 8px;
        }

        .card-value {
          font-size: 28px;
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
          color: #4caf50;
        }

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

        .competitor-tracking,
        .competitive-intelligence,
        .swot-analysis,
        .competitive-alerts {
          background: #252526;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .tracking-header,
        .intelligence-header,
        .swot-header,
        .alerts-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .tracking-header h4,
        .intelligence-header h4,
        .swot-header h4,
        .alerts-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .competitors-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px;
        }

        .competitor-card {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 16px;
          border: 1px solid #333;
        }

        .competitor-card.direct { border-left: 4px solid #f44336; }
        .competitor-card.indirect { border-left: 4px solid #ff9800; }
        .competitor-card.aspirational { border-left: 4px solid #4caf50; }

        .competitor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .competitor-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .competitor-avatar {
          position: relative;
        }

        .avatar-placeholder {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #333;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #999;
        }

        .platform-badge {
          position: absolute;
          bottom: -2px;
          right: -2px;
          width: 16px;
          height: 16px;
          background: #333;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 8px;
          color: #fff;
        }

        .competitor-name {
          margin: 0 0 2px 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .competitor-handle {
          color: #999;
          font-size: 12px;
          display: block;
        }

        .competitor-category {
          color: #666;
          font-size: 10px;
          text-transform: uppercase;
          display: block;
        }

        .competitor-actions {
          display: flex;
          gap: 4px;
        }

        .competitor-metrics {
          margin-bottom: 12px;
        }

        .metric-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
          font-size: 12px;
        }

        .metric-label {
          color: #999;
          flex: 1;
        }

        .metric-value {
          color: #fff;
          font-weight: 500;
          margin-right: 8px;
        }

        .metric-change {
          font-size: 10px;
          font-weight: 600;
          width: 40px;
          text-align: right;
        }

        .metric-change.positive { color: #4caf50; }
        .metric-change.negative { color: #f44336; }

        .competitor-chart {
          margin-bottom: 12px;
        }

        .status-indicators {
          display: flex;
          gap: 8px;
        }

        .status-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          padding: 4px;
          border-radius: 4px;
          background: #333;
          font-size: 8px;
          color: #999;
        }

        .status-item.alert {
          background: #f44336;
          color: #fff;
          animation: blink 1s infinite;
        }

        .swot-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 16px;
        }

        .swot-quadrant {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 16px;
        }

        .swot-quadrant.strengths { border-left: 4px solid #4caf50; }
        .swot-quadrant.weaknesses { border-left: 4px solid #f44336; }
        .swot-quadrant.opportunities { border-left: 4px solid #2196f3; }
        .swot-quadrant.threats { border-left: 4px solid #ff9800; }

        .swot-quadrant h5 {
          margin: 0 0 12px 0;
          color: #fff;
          font-size: 14px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .swot-quadrant ul {
          margin: 0;
          padding-left: 16px;
          color: #ccc;
        }

        .swot-quadrant li {
          margin-bottom: 8px;
          font-size: 12px;
          line-height: 1.4;
        }

        .intelligence-item {
          background: #1a1a1a;
          border-radius: 6px;
          padding: 16px;
          margin-bottom: 12px;
          border-left: 4px solid #666;
        }

        .intelligence-item.high { border-left-color: #f44336; }
        .intelligence-item.medium { border-left-color: #ff9800; }
        .intelligence-item.low { border-left-color: #4caf50; }

        .intelligence-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .intelligence-priority {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .intelligence-priority.high { background: #f44336; color: #fff; }
        .intelligence-priority.medium { background: #ff9800; color: #fff; }
        .intelligence-priority.low { background: #4caf50; color: #fff; }

        .intelligence-title {
          margin: 0 0 8px 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .intelligence-description {
          margin: 0 0 12px 0;
          color: #ccc;
          font-size: 12px;
          line-height: 1.4;
        }

        .intelligence-actions {
          display: flex;
          gap: 8px;
        }

        .btn-primary, .btn-secondary, .btn-small, .btn-tiny {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #f44336; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }
        .btn-tiny { background: #555; color: #fff; padding: 2px 6px; font-size: 10px; }

        .btn-small.primary { background: #f44336; }
        .btn-small.secondary { background: #666; }

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

        .no-competitors,
        .no-intelligence,
        .no-alerts {
          text-align: center;
          padding: 40px 20px;
          color: #666;
        }

        .no-competitors i,
        .no-intelligence i,
        .no-alerts i {
          font-size: 48px;
          margin-bottom: 16px;
          color: #444;
        }

        .btn-link {
          background: none;
          border: none;
          color: #f44336;
          cursor: pointer;
          text-decoration: underline;
          font-size: 14px;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0.3; }
        }
      </style>
    `;
    
    if (!document.querySelector('#competitor-analysis-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'competitor-analysis-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  startCompetitiveMonitoring() {
    this.monitoringInterval = setInterval(() => {
      this.updateCompetitorTracking();
    }, 300000); // Update every 5 minutes
  }

  refreshTrackingData() {
    this.updateCompetitorTracking();
    this.showSuccess('Competitor data refreshed');
  }

  clearAllAlerts() {
    this.showSuccess('All alerts cleared');
  }

  updateSWOTAnalysis() {
    this.showSuccess('SWOT analysis updated');
  }

  showAlertsConfiguration() {
    this.showSuccess('Alerts configuration opened');
  }

  viewCompetitor(id) {
    this.showSuccess(`Viewing competitor ${id}`);
  }

  editCompetitor(id) {
    this.showSuccess(`Editing competitor ${id}`);
  }

  removeCompetitor(id) {
    this.showSuccess(`Removed competitor ${id}`);
  }

  implementInsight(id) {
    this.showSuccess(`Implementing insight ${id}`);
  }

  saveInsight(id) {
    this.showSuccess(`Saved insight ${id} for later`);
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
  module.exports = CompetitorAnalysis;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.CompetitorAnalysis = CompetitorAnalysis;
  window.competitorAnalysis = null; // Will be set when instantiated
}