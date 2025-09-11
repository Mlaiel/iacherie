/**
 * Ainflue Desktop - SEO Optimizer Component
 * 
 * Advanced SEO optimization tools for content creators
 * Implements real-time SEO analysis, keyword optimization, and viral content strategy
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class SEOOptimizer {
  constructor(container, aiAnalysisClient) {
    this.container = container;
    this.aiClient = aiAnalysisClient;
    this.currentContent = null;
    this.seoScore = 0;
    this.keywords = [];
    this.suggestions = [];
    this.competitorData = {};
    
    this.init();
  }

  init() {
    this.createOptimizerInterface();
    this.setupEventListeners();
    this.initializeSEOModules();
  }

  createOptimizerInterface() {
    this.container.innerHTML = `
      <div class="seo-optimizer">
        <div class="optimizer-header">
          <h3><i class="fas fa-search-plus"></i> SEO Optimization Studio</h3>
          <div class="seo-score-display">
            <div class="score-circle" id="seoScoreCircle">
              <div class="score-value" id="seoScoreValue">0</div>
              <div class="score-label">SEO Score</div>
            </div>
          </div>
        </div>

        <div class="optimizer-content">
          <!-- Content Input Section -->
          <div class="content-input-section">
            <div class="section-header">
              <h4>Content Analysis</h4>
              <div class="input-controls">
                <button class="btn-secondary" id="loadFromProject">
                  <i class="fas fa-folder-open"></i>
                  Load from Project
                </button>
                <button class="btn-primary" id="analyzeContent">
                  <i class="fas fa-search"></i>
                  Analyze SEO
                </button>
              </div>
            </div>

            <div class="content-input">
              <div class="input-tabs">
                <button class="tab-btn active" data-tab="title">Title</button>
                <button class="tab-btn" data-tab="description">Description</button>
                <button class="tab-btn" data-tab="tags">Tags</button>
                <button class="tab-btn" data-tab="transcript">Transcript</button>
              </div>

              <div class="tab-content" id="titleTab">
                <textarea 
                  id="contentTitle" 
                  placeholder="Enter your content title..."
                  maxlength="100"
                  rows="2"
                ></textarea>
                <div class="character-count">
                  <span id="titleCount">0</span>/100 characters
                </div>
              </div>

              <div class="tab-content hidden" id="descriptionTab">
                <textarea 
                  id="contentDescription" 
                  placeholder="Enter your content description..."
                  maxlength="5000"
                  rows="6"
                ></textarea>
                <div class="character-count">
                  <span id="descriptionCount">0</span>/5000 characters
                </div>
              </div>

              <div class="tab-content hidden" id="tagsTab">
                <div class="tags-input-container">
                  <input 
                    type="text" 
                    id="tagsInput" 
                    placeholder="Add tags (press Enter to add)"
                  />
                  <div class="tags-list" id="tagsList"></div>
                </div>
                <div class="suggested-tags">
                  <h5>Suggested Tags</h5>
                  <div class="suggested-tags-list" id="suggestedTagsList">
                    <span class="no-suggestions">Analyze content to get tag suggestions</span>
                  </div>
                </div>
              </div>

              <div class="tab-content hidden" id="transcriptTab">
                <textarea 
                  id="contentTranscript" 
                  placeholder="Paste your content transcript for deeper analysis..."
                  rows="8"
                ></textarea>
                <div class="transcript-tools">
                  <button class="btn-small" id="extractFromAudio">
                    <i class="fas fa-microphone"></i>
                    Extract from Audio
                  </button>
                  <button class="btn-small" id="extractFromVideo">
                    <i class="fas fa-video"></i>
                    Extract from Video
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- SEO Analysis Results -->
          <div class="seo-analysis-results">
            <div class="section-header">
              <h4>SEO Analysis</h4>
              <div class="analysis-controls">
                <select id="platformSelect">
                  <option value="youtube">YouTube</option>
                  <option value="tiktok">TikTok</option>
                  <option value="instagram">Instagram</option>
                  <option value="twitter">Twitter</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="general">General Web</option>
                </select>
                <button class="btn-small" id="refreshAnalysis">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
              </div>
            </div>

            <div class="analysis-grid">
              <!-- SEO Metrics -->
              <div class="metric-card">
                <div class="metric-header">
                  <h5>SEO Metrics</h5>
                  <div class="metric-score" id="seoMetricScore">0%</div>
                </div>
                <div class="metric-details">
                  <div class="metric-item">
                    <span class="metric-label">Title Optimization</span>
                    <div class="progress-bar">
                      <div class="progress-fill" id="titleProgress" style="width: 0%"></div>
                    </div>
                    <span class="metric-value" id="titleScore">0%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Description Quality</span>
                    <div class="progress-bar">
                      <div class="progress-fill" id="descriptionProgress" style="width: 0%"></div>
                    </div>
                    <span class="metric-value" id="descriptionScore">0%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Keyword Density</span>
                    <div class="progress-bar">
                      <div class="progress-fill" id="keywordProgress" style="width: 0%"></div>
                    </div>
                    <span class="metric-value" id="keywordScore">0%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Readability</span>
                    <div class="progress-bar">
                      <div class="progress-fill" id="readabilityProgress" style="width: 0%"></div>
                    </div>
                    <span class="metric-value" id="readabilityScore">0%</span>
                  </div>
                </div>
              </div>

              <!-- Keyword Analysis -->
              <div class="keyword-analysis">
                <div class="metric-header">
                  <h5>Keyword Analysis</h5>
                  <button class="btn-small" id="researchKeywords">
                    <i class="fas fa-search"></i>
                    Research
                  </button>
                </div>
                <div class="keywords-container" id="keywordsContainer">
                  <div class="no-keywords">
                    <i class="fas fa-key"></i>
                    <p>Analyze content to discover keywords</p>
                  </div>
                </div>
              </div>

              <!-- Viral Potential -->
              <div class="viral-analysis">
                <div class="metric-header">
                  <h5>Viral Potential</h5>
                  <div class="viral-score" id="viralScore">0%</div>
                </div>
                <div class="viral-factors" id="viralFactors">
                  <div class="factor-item">
                    <span class="factor-label">Emotional Impact</span>
                    <div class="factor-bar">
                      <div class="factor-fill" id="emotionalImpact" style="width: 0%"></div>
                    </div>
                  </div>
                  <div class="factor-item">
                    <span class="factor-label">Trending Topics</span>
                    <div class="factor-bar">
                      <div class="factor-fill" id="trendingTopics" style="width: 0%"></div>
                    </div>
                  </div>
                  <div class="factor-item">
                    <span class="factor-label">Shareability</span>
                    <div class="factor-bar">
                      <div class="factor-fill" id="shareability" style="width: 0%"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Competitor Analysis -->
              <div class="competitor-analysis">
                <div class="metric-header">
                  <h5>Competitor Analysis</h5>
                  <button class="btn-small" id="analyzeCompetitors">
                    <i class="fas fa-chart-line"></i>
                    Analyze
                  </button>
                </div>
                <div class="competitors-container" id="competitorsContainer">
                  <div class="no-competitors">
                    <i class="fas fa-users"></i>
                    <p>Run analysis to compare with competitors</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Optimization Suggestions -->
          <div class="optimization-suggestions">
            <div class="section-header">
              <h4>Optimization Suggestions</h4>
              <div class="suggestions-controls">
                <button class="btn-primary" id="applyAllSuggestions">
                  <i class="fas fa-magic"></i>
                  Apply All
                </button>
                <button class="btn-secondary" id="exportSuggestions">
                  <i class="fas fa-download"></i>
                  Export
                </button>
              </div>
            </div>

            <div class="suggestions-list" id="suggestionsList">
              <div class="no-suggestions">
                <i class="fas fa-lightbulb"></i>
                <p>Analyze your content to get optimization suggestions</p>
              </div>
            </div>
          </div>

          <!-- Trending Analysis -->
          <div class="trending-analysis">
            <div class="section-header">
              <h4>Trending Analysis</h4>
              <div class="trending-controls">
                <select id="trendingPlatform">
                  <option value="youtube">YouTube</option>
                  <option value="tiktok">TikTok</option>
                  <option value="instagram">Instagram</option>
                  <option value="twitter">Twitter</option>
                </select>
                <select id="trendingCategory">
                  <option value="all">All Categories</option>
                  <option value="music">Music</option>
                  <option value="gaming">Gaming</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="education">Education</option>
                  <option value="technology">Technology</option>
                </select>
              </div>
            </div>

            <div class="trending-grid" id="trendingGrid">
              <div class="trending-keywords">
                <h5>Trending Keywords</h5>
                <div class="trending-items" id="trendingKeywords">
                  <div class="loading">Loading trending data...</div>
                </div>
              </div>

              <div class="trending-hashtags">
                <h5>Trending Hashtags</h5>
                <div class="trending-items" id="trendingHashtags">
                  <div class="loading">Loading trending data...</div>
                </div>
              </div>

              <div class="trending-topics">
                <h5>Hot Topics</h5>
                <div class="trending-items" id="hotTopics">
                  <div class="loading">Loading trending data...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Tab switching
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Content input
    this.container.querySelector('#contentTitle').addEventListener('input', (e) => {
      this.updateCharacterCount('title', e.target.value);
      this.debouncedAnalysis();
    });

    this.container.querySelector('#contentDescription').addEventListener('input', (e) => {
      this.updateCharacterCount('description', e.target.value);
      this.debouncedAnalysis();
    });

    this.container.querySelector('#contentTranscript').addEventListener('input', () => {
      this.debouncedAnalysis();
    });

    // Tags input
    this.container.querySelector('#tagsInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.addTag(e.target.value.trim());
        e.target.value = '';
      }
    });

    // Action buttons
    this.container.querySelector('#analyzeContent').addEventListener('click', () => {
      this.analyzeContent();
    });

    this.container.querySelector('#loadFromProject').addEventListener('click', () => {
      this.loadFromProject();
    });

    this.container.querySelector('#researchKeywords').addEventListener('click', () => {
      this.researchKeywords();
    });

    this.container.querySelector('#analyzeCompetitors').addEventListener('click', () => {
      this.analyzeCompetitors();
    });

    this.container.querySelector('#applyAllSuggestions').addEventListener('click', () => {
      this.applyAllSuggestions();
    });

    this.container.querySelector('#exportSuggestions').addEventListener('click', () => {
      this.exportSuggestions();
    });

    // Platform changes
    this.container.querySelector('#platformSelect').addEventListener('change', () => {
      this.debouncedAnalysis();
    });

    this.container.querySelector('#trendingPlatform').addEventListener('change', () => {
      this.loadTrendingData();
    });

    this.container.querySelector('#trendingCategory').addEventListener('change', () => {
      this.loadTrendingData();
    });

    // Debounced analysis
    this.debouncedAnalysis = this.debounce(this.analyzeContent.bind(this), 1000);
  }

  initializeSEOModules() {
    this.loadTrendingData();
    this.updateSEOScore(0);
  }

  switchTab(tabName) {
    // Hide all tabs
    this.container.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.add('hidden');
    });

    // Remove active class from all buttons
    this.container.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });

    // Show selected tab
    this.container.querySelector(`#${tabName}Tab`).classList.remove('hidden');
    this.container.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
  }

  updateCharacterCount(type, text) {
    const countElement = this.container.querySelector(`#${type}Count`);
    countElement.textContent = text.length;
    
    // Update visual indicator
    const maxLengths = { title: 100, description: 5000 };
    const percentage = (text.length / maxLengths[type]) * 100;
    
    if (percentage > 90) {
      countElement.style.color = '#f44336';
    } else if (percentage > 75) {
      countElement.style.color = '#ff9800';
    } else {
      countElement.style.color = '#4caf50';
    }
  }

  addTag(tag) {
    if (!tag || this.keywords.includes(tag)) return;

    this.keywords.push(tag);
    this.updateTagsList();
    this.debouncedAnalysis();
  }

  removeTag(tag) {
    this.keywords = this.keywords.filter(k => k !== tag);
    this.updateTagsList();
    this.debouncedAnalysis();
  }

  updateTagsList() {
    const tagsList = this.container.querySelector('#tagsList');
    
    if (this.keywords.length === 0) {
      tagsList.innerHTML = '<div class="no-tags">No tags added</div>';
      return;
    }

    tagsList.innerHTML = this.keywords.map(tag => `
      <span class="tag-item">
        ${tag}
        <button class="tag-remove" onclick="window.seoOptimizer?.removeTag('${tag}')">
          <i class="fas fa-times"></i>
        </button>
      </span>
    `).join('');
  }

  async analyzeContent() {
    try {
      this.showAnalysisLoading(true);

      const content = this.getCurrentContent();
      const platform = this.container.querySelector('#platformSelect').value;

      // Perform SEO analysis
      const analysis = await this.aiClient.analyzeSEO({
        title: content.title,
        description: content.description,
        tags: content.tags,
        transcript: content.transcript,
        platform
      });

      this.displayAnalysisResults(analysis);
      this.generateSuggestions(analysis);
      this.updateSEOScore(analysis.overallScore);

    } catch (error) {
      console.error('SEO analysis failed:', error);
      this.showError('Failed to analyze content: ' + error.message);
    } finally {
      this.showAnalysisLoading(false);
    }
  }

  getCurrentContent() {
    return {
      title: this.container.querySelector('#contentTitle').value,
      description: this.container.querySelector('#contentDescription').value,
      tags: this.keywords,
      transcript: this.container.querySelector('#contentTranscript').value
    };
  }

  displayAnalysisResults(analysis) {
    // Update SEO metrics
    this.updateMetricProgress('title', analysis.titleScore);
    this.updateMetricProgress('description', analysis.descriptionScore);
    this.updateMetricProgress('keyword', analysis.keywordScore);
    this.updateMetricProgress('readability', analysis.readabilityScore);

    // Update overall SEO metric score
    this.container.querySelector('#seoMetricScore').textContent = `${analysis.overallScore}%`;

    // Display keywords
    this.displayKeywords(analysis.keywords);

    // Update viral potential
    this.updateViralAnalysis(analysis.viralPotential);
  }

  updateMetricProgress(metric, score) {
    const progressFill = this.container.querySelector(`#${metric}Progress`);
    const scoreValue = this.container.querySelector(`#${metric}Score`);
    
    progressFill.style.width = `${score}%`;
    scoreValue.textContent = `${score}%`;

    // Color coding
    if (score >= 80) {
      progressFill.style.background = '#4caf50';
    } else if (score >= 60) {
      progressFill.style.background = '#ff9800';
    } else {
      progressFill.style.background = '#f44336';
    }
  }

  displayKeywords(keywords) {
    const container = this.container.querySelector('#keywordsContainer');
    
    if (!keywords || keywords.length === 0) {
      container.innerHTML = `
        <div class="no-keywords">
          <i class="fas fa-key"></i>
          <p>No keywords found</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="keywords-list">
        ${keywords.map(keyword => `
          <div class="keyword-item">
            <span class="keyword-text">${keyword.text}</span>
            <div class="keyword-metrics">
              <span class="keyword-volume">Vol: ${keyword.volume || 'N/A'}</span>
              <span class="keyword-difficulty">Diff: ${keyword.difficulty || 'N/A'}</span>
              <span class="keyword-trend ${keyword.trend || 'stable'}">${keyword.trend || 'stable'}</span>
            </div>
            <button class="btn-tiny" onclick="window.seoOptimizer?.addKeywordToTags('${keyword.text}')">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        `).join('')}
      </div>
    `;
  }

  updateViralAnalysis(viralData) {
    if (!viralData) return;

    this.container.querySelector('#viralScore').textContent = `${viralData.overallScore}%`;
    
    // Update factor bars
    this.updateFactorBar('emotionalImpact', viralData.emotionalImpact);
    this.updateFactorBar('trendingTopics', viralData.trendingAlignment);
    this.updateFactorBar('shareability', viralData.shareability);
  }

  updateFactorBar(factorId, score) {
    const factorFill = this.container.querySelector(`#${factorId}`);
    if (factorFill) {
      factorFill.style.width = `${score}%`;
      
      if (score >= 80) {
        factorFill.style.background = '#4caf50';
      } else if (score >= 60) {
        factorFill.style.background = '#ff9800';
      } else {
        factorFill.style.background = '#f44336';
      }
    }
  }

  generateSuggestions(analysis) {
    const suggestions = [];

    // Title suggestions
    if (analysis.titleScore < 80) {
      suggestions.push({
        type: 'title',
        priority: 'high',
        title: 'Optimize Title',
        description: 'Your title could be more engaging. Consider adding power words or emotional triggers.',
        action: 'Suggest better title',
        actionType: 'title_suggestion'
      });
    }

    // Description suggestions
    if (analysis.descriptionScore < 70) {
      suggestions.push({
        type: 'description',
        priority: 'medium',
        title: 'Improve Description',
        description: 'Add more relevant keywords and call-to-action phrases to your description.',
        action: 'Enhance description',
        actionType: 'description_enhancement'
      });
    }

    // Keyword suggestions
    if (analysis.keywordScore < 60) {
      suggestions.push({
        type: 'keywords',
        priority: 'high',
        title: 'Add More Keywords',
        description: 'Include more relevant keywords to improve discoverability.',
        action: 'Research keywords',
        actionType: 'keyword_research'
      });
    }

    // Trending suggestions
    if (analysis.viralPotential?.trendingAlignment < 50) {
      suggestions.push({
        type: 'trending',
        priority: 'medium',
        title: 'Align with Trends',
        description: 'Your content could better align with current trending topics.',
        action: 'View trending topics',
        actionType: 'trending_analysis'
      });
    }

    this.displaySuggestions(suggestions);
  }

  displaySuggestions(suggestions) {
    const container = this.container.querySelector('#suggestionsList');
    
    if (suggestions.length === 0) {
      container.innerHTML = `
        <div class="no-suggestions">
          <i class="fas fa-check-circle"></i>
          <p>Great! Your content is well optimized.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = suggestions.map(suggestion => `
      <div class="suggestion-item ${suggestion.priority}">
        <div class="suggestion-header">
          <div class="suggestion-info">
            <span class="suggestion-type">${suggestion.type}</span>
            <span class="suggestion-priority ${suggestion.priority}">${suggestion.priority}</span>
          </div>
          <button class="suggestion-dismiss" onclick="this.parentElement.parentElement.remove()">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="suggestion-content">
          <h5 class="suggestion-title">${suggestion.title}</h5>
          <p class="suggestion-description">${suggestion.description}</p>
          <button class="suggestion-action btn-small primary" 
                  onclick="window.seoOptimizer?.executeSuggestion('${suggestion.actionType}')">
            <i class="fas fa-magic"></i>
            ${suggestion.action}
          </button>
        </div>
      </div>
    `).join('');

    this.suggestions = suggestions;
  }

  async loadTrendingData() {
    try {
      const platform = this.container.querySelector('#trendingPlatform').value;
      const category = this.container.querySelector('#trendingCategory').value;

      // Mock trending data - in real implementation, this would call actual APIs
      const trendingData = await this.getMockTrendingData(platform, category);
      
      this.displayTrendingKeywords(trendingData.keywords);
      this.displayTrendingHashtags(trendingData.hashtags);
      this.displayHotTopics(trendingData.topics);

    } catch (error) {
      console.error('Failed to load trending data:', error);
    }
  }

  displayTrendingKeywords(keywords) {
    const container = this.container.querySelector('#trendingKeywords');
    
    container.innerHTML = keywords.map(keyword => `
      <div class="trending-item keyword">
        <span class="trending-text">${keyword.text}</span>
        <span class="trending-growth ${keyword.growth > 0 ? 'positive' : 'negative'}">
          ${keyword.growth > 0 ? '+' : ''}${keyword.growth}%
        </span>
        <button class="btn-tiny" onclick="window.seoOptimizer?.addKeywordToTags('${keyword.text}')">
          <i class="fas fa-plus"></i>
        </button>
      </div>
    `).join('');
  }

  displayTrendingHashtags(hashtags) {
    const container = this.container.querySelector('#trendingHashtags');
    
    container.innerHTML = hashtags.map(hashtag => `
      <div class="trending-item hashtag">
        <span class="trending-text">#${hashtag.text}</span>
        <span class="trending-volume">${hashtag.volume}</span>
        <button class="btn-tiny" onclick="window.seoOptimizer?.addKeywordToTags('#${hashtag.text}')">
          <i class="fas fa-plus"></i>
        </button>
      </div>
    `).join('');
  }

  displayHotTopics(topics) {
    const container = this.container.querySelector('#hotTopics');
    
    container.innerHTML = topics.map(topic => `
      <div class="trending-item topic">
        <span class="trending-text">${topic.text}</span>
        <span class="trending-score">${topic.score}%</span>
        <button class="btn-tiny" onclick="window.seoOptimizer?.exploreTopicKeywords('${topic.text}')">
          <i class="fas fa-search"></i>
        </button>
      </div>
    `).join('');
  }

  updateSEOScore(score) {
    this.seoScore = score;
    const scoreElement = this.container.querySelector('#seoScoreValue');
    const circleElement = this.container.querySelector('#seoScoreCircle');
    
    scoreElement.textContent = score;
    
    // Update circle color based on score
    if (score >= 80) {
      circleElement.className = 'score-circle excellent';
    } else if (score >= 60) {
      circleElement.className = 'score-circle good';
    } else if (score >= 40) {
      circleElement.className = 'score-circle average';
    } else {
      circleElement.className = 'score-circle poor';
    }
  }

  // Utility methods
  async getMockTrendingData(platform, category) {
    // Mock data - replace with real API calls
    return {
      keywords: [
        { text: 'viral music', growth: 25 },
        { text: 'trending dance', growth: 18 },
        { text: 'new release', growth: -5 },
        { text: 'behind scenes', growth: 12 }
      ],
      hashtags: [
        { text: 'viral', volume: '1.2M' },
        { text: 'trending', volume: '890K' },
        { text: 'newmusic', volume: '654K' },
        { text: 'artist', volume: '432K' }
      ],
      topics: [
        { text: 'AI Music Generation', score: 95 },
        { text: 'Virtual Concerts', score: 87 },
        { text: 'Music NFTs', score: 72 },
        { text: 'Social Media Music', score: 68 }
      ]
    };
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  showAnalysisLoading(show) {
    const button = this.container.querySelector('#analyzeContent');
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
      button.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-search"></i> Analyze SEO';
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
        .seo-optimizer {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .optimizer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #673ab7 0%, #3f51b5 100%);
          border-bottom: 1px solid #333;
        }

        .optimizer-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .score-circle {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          border: 3px solid #666;
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
          font-size: 18px;
          font-weight: bold;
          color: #fff;
        }

        .score-label {
          font-size: 8px;
          color: #ccc;
          text-transform: uppercase;
        }

        .optimizer-content {
          padding: 20px;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .section-header h4 {
          margin: 0;
          color: #fff;
          font-size: 14px;
          font-weight: 600;
        }

        .input-tabs {
          display: flex;
          gap: 1px;
          margin-bottom: 16px;
          background: #333;
          border-radius: 6px 6px 0 0;
          overflow: hidden;
        }

        .tab-btn {
          padding: 8px 16px;
          background: #2d2d30;
          border: none;
          color: #ccc;
          cursor: pointer;
          transition: all 0.3s ease;
          font-size: 12px;
        }

        .tab-btn.active {
          background: #673ab7;
          color: #fff;
        }

        .tab-content {
          background: #252526;
          border-radius: 0 0 6px 6px;
          padding: 16px;
        }

        .tab-content.hidden {
          display: none;
        }

        .tab-content textarea,
        .tab-content input {
          width: 100%;
          background: #1a1a1a;
          border: 1px solid #444;
          border-radius: 4px;
          padding: 8px 12px;
          color: #fff;
          font-family: inherit;
          font-size: 14px;
          resize: vertical;
        }

        .character-count {
          text-align: right;
          font-size: 12px;
          color: #999;
          margin-top: 4px;
        }

        .tags-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 12px;
        }

        .tag-item {
          display: flex;
          align-items: center;
          gap: 4px;
          background: #673ab7;
          color: #fff;
          padding: 4px 8px;
          border-radius: 16px;
          font-size: 12px;
        }

        .tag-remove {
          background: none;
          border: none;
          color: #fff;
          cursor: pointer;
          padding: 0;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .analysis-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .metric-card,
        .keyword-analysis,
        .viral-analysis,
        .competitor-analysis {
          background: #252526;
          border-radius: 8px;
          padding: 16px;
        }

        .metric-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .metric-header h5 {
          margin: 0;
          color: #fff;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .metric-item {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 8px;
        }

        .metric-label {
          flex: 1;
          font-size: 12px;
          color: #ccc;
        }

        .progress-bar {
          width: 80px;
          height: 6px;
          background: #444;
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: #673ab7;
          transition: width 0.5s ease;
        }

        .metric-value {
          font-size: 12px;
          color: #fff;
          width: 30px;
          text-align: right;
        }

        .keyword-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 12px;
          background: #1a1a1a;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .keyword-metrics {
          display: flex;
          gap: 8px;
          font-size: 10px;
          color: #999;
        }

        .suggestion-item {
          background: #252526;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 12px;
          border-left: 4px solid #666;
        }

        .suggestion-item.high { border-left-color: #f44336; }
        .suggestion-item.medium { border-left-color: #ff9800; }
        .suggestion-item.low { border-left-color: #4caf50; }

        .trending-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
        }

        .trending-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 12px;
          background: #2d2d30;
          border-radius: 4px;
          margin-bottom: 8px;
        }

        .trending-growth.positive { color: #4caf50; }
        .trending-growth.negative { color: #f44336; }

        .btn-primary, .btn-secondary, .btn-small, .btn-tiny {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #673ab7; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }
        .btn-tiny { background: #555; color: #fff; padding: 2px 6px; font-size: 10px; }

        .hidden { display: none !important; }
      </style>
    `;
    
    if (!document.querySelector('#seo-optimizer-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'seo-optimizer-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  addKeywordToTags(keyword) {
    this.addTag(keyword);
  }

  async researchKeywords() {
    const content = this.getCurrentContent();
    const keywords = await this.aiClient.researchKeywords(content);
    this.displayKeywords(keywords);
  }

  async analyzeCompetitors() {
    const content = this.getCurrentContent();
    const competitors = await this.aiClient.analyzeCompetitors(content);
    this.displayCompetitors(competitors);
  }

  applyAllSuggestions() {
    this.suggestions.forEach(suggestion => {
      this.executeSuggestion(suggestion.actionType);
    });
  }

  executeSuggestion(actionType) {
    switch (actionType) {
      case 'title_suggestion':
        this.suggestBetterTitle();
        break;
      case 'description_enhancement':
        this.enhanceDescription();
        break;
      case 'keyword_research':
        this.researchKeywords();
        break;
      case 'trending_analysis':
        this.loadTrendingData();
        break;
    }
  }

  async exportSuggestions() {
    const exportData = {
      timestamp: new Date().toISOString(),
      content: this.getCurrentContent(),
      seoScore: this.seoScore,
      suggestions: this.suggestions,
      keywords: this.keywords
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `seo_analysis_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  destroy() {
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SEOOptimizer;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.SEOOptimizer = SEOOptimizer;
  window.seoOptimizer = null; // Will be set when instantiated
}