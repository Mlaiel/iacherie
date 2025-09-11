/**
 * Ainflue Desktop - Collaboration Hub Component
 * 
 * Advanced collaboration management for content creators
 * Implements AI-powered creator matching, project collaboration, and revenue sharing
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class CollaborationHub {
  constructor(container, aiMatchingEngine, collaborationManager) {
    this.container = container;
    this.aiMatcher = aiMatchingEngine;
    this.collaborationManager = collaborationManager;
    this.activeCollaborations = new Map();
    this.potentialMatches = [];
    this.projects = [];
    
    this.init();
  }

  init() {
    this.createHubInterface();
    this.setupEventListeners();
    this.initializeCollaborationServices();
    this.loadUserData();
  }

  createHubInterface() {
    this.container.innerHTML = `
      <div class="collaboration-hub">
        <div class="hub-header">
          <h3><i class="fas fa-users"></i> Collaboration Hub</h3>
          <div class="hub-status">
            <div class="status-badge active">
              <i class="fas fa-circle"></i>
              Online
            </div>
            <div class="collaboration-count">
              <span id="activeCollabCount">0</span> Active
            </div>
          </div>
        </div>

        <div class="hub-content">
          <!-- Navigation Tabs -->
          <div class="hub-navigation">
            <button class="nav-tab active" data-tab="dashboard">
              <i class="fas fa-tachometer-alt"></i>
              Dashboard
            </button>
            <button class="nav-tab" data-tab="matches">
              <i class="fas fa-search"></i>
              Find Collaborators
            </button>
            <button class="nav-tab" data-tab="projects">
              <i class="fas fa-project-diagram"></i>
              Projects
            </button>
            <button class="nav-tab" data-tab="messages">
              <i class="fas fa-comments"></i>
              Messages
              <span class="notification-badge" id="messagesBadge" style="display: none;">0</span>
            </button>
            <button class="nav-tab" data-tab="earnings">
              <i class="fas fa-chart-line"></i>
              Earnings
            </button>
          </div>

          <!-- Dashboard Tab -->
          <div class="tab-content active" id="dashboardTab">
            <div class="dashboard-grid">
              <!-- Quick Stats -->
              <div class="stats-overview">
                <h4>Collaboration Overview</h4>
                <div class="stats-cards">
                  <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-handshake"></i></div>
                    <div class="stat-value" id="totalCollabs">0</div>
                    <div class="stat-label">Total Collaborations</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-star"></i></div>
                    <div class="stat-value" id="avgRating">0.0</div>
                    <div class="stat-label">Average Rating</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                    <div class="stat-value" id="totalEarnings">$0</div>
                    <div class="stat-label">Total Earnings</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-trophy"></i></div>
                    <div class="stat-value" id="successRate">0%</div>
                    <div class="stat-label">Success Rate</div>
                  </div>
                </div>
              </div>

              <!-- Recent Activity -->
              <div class="recent-activity">
                <h4>Recent Activity</h4>
                <div class="activity-list" id="activityList">
                  <div class="no-activity">
                    <i class="fas fa-clock"></i>
                    <p>No recent activity</p>
                  </div>
                </div>
              </div>

              <!-- AI Recommendations -->
              <div class="ai-recommendations">
                <h4>AI Recommendations</h4>
                <div class="recommendations-list" id="recommendationsList">
                  <div class="loading-recommendations">
                    <i class="fas fa-brain"></i>
                    <p>AI is analyzing collaboration opportunities...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Find Collaborators Tab -->
          <div class="tab-content" id="matchesTab">
            <div class="matches-container">
              <div class="search-filters">
                <h4>Find Your Perfect Collaborator</h4>
                <div class="filter-grid">
                  <div class="filter-group">
                    <label>Content Type</label>
                    <select id="contentTypeFilter">
                      <option value="all">All Types</option>
                      <option value="music">Music</option>
                      <option value="video">Video</option>
                      <option value="podcast">Podcast</option>
                      <option value="blog">Blog</option>
                      <option value="photography">Photography</option>
                    </select>
                  </div>
                  <div class="filter-group">
                    <label>Skill Level</label>
                    <select id="skillLevelFilter">
                      <option value="all">All Levels</option>
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="expert">Expert</option>
                      <option value="professional">Professional</option>
                    </select>
                  </div>
                  <div class="filter-group">
                    <label>Location</label>
                    <select id="locationFilter">
                      <option value="all">All Locations</option>
                      <option value="local">Local (50km)</option>
                      <option value="national">National</option>
                      <option value="international">International</option>
                    </select>
                  </div>
                  <div class="filter-group">
                    <label>Budget Range</label>
                    <select id="budgetFilter">
                      <option value="all">All Budgets</option>
                      <option value="free">Free Collaboration</option>
                      <option value="low">$1 - $100</option>
                      <option value="medium">$100 - $1000</option>
                      <option value="high">$1000+</option>
                    </select>
                  </div>
                </div>
                <div class="search-actions">
                  <button class="btn-primary" id="searchCollaborators">
                    <i class="fas fa-search"></i>
                    Find Matches
                  </button>
                  <button class="btn-secondary" id="aiSmartMatch">
                    <i class="fas fa-brain"></i>
                    AI Smart Match
                  </button>
                </div>
              </div>

              <div class="matches-results" id="matchesResults">
                <div class="no-matches">
                  <i class="fas fa-users"></i>
                  <p>Click "Find Matches" to discover collaborators</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Projects Tab -->
          <div class="tab-content" id="projectsTab">
            <div class="projects-container">
              <div class="projects-header">
                <h4>Collaboration Projects</h4>
                <button class="btn-primary" id="createProject">
                  <i class="fas fa-plus"></i>
                  New Project
                </button>
              </div>

              <div class="projects-filter">
                <select id="projectStatusFilter">
                  <option value="all">All Projects</option>
                  <option value="planning">Planning</option>
                  <option value="active">Active</option>
                  <option value="review">Under Review</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              <div class="projects-grid" id="projectsGrid">
                <div class="no-projects">
                  <i class="fas fa-project-diagram"></i>
                  <p>No projects yet. Create your first collaboration project!</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Messages Tab -->
          <div class="tab-content" id="messagesTab">
            <div class="messages-container">
              <div class="conversations-sidebar">
                <div class="conversations-header">
                  <h4>Conversations</h4>
                  <button class="btn-small" id="newConversation">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
                <div class="conversations-list" id="conversationsList">
                  <div class="no-conversations">
                    <i class="fas fa-comments"></i>
                    <p>No conversations yet</p>
                  </div>
                </div>
              </div>

              <div class="chat-area">
                <div class="chat-header" id="chatHeader">
                  <div class="chat-placeholder">
                    <i class="fas fa-comment"></i>
                    <p>Select a conversation to start chatting</p>
                  </div>
                </div>
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input" id="chatInput" style="display: none;">
                  <input type="text" placeholder="Type your message..." id="messageInput">
                  <button class="btn-primary" id="sendMessage">
                    <i class="fas fa-paper-plane"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Earnings Tab -->
          <div class="tab-content" id="earningsTab">
            <div class="earnings-container">
              <div class="earnings-overview">
                <h4>Collaboration Earnings</h4>
                <div class="earnings-summary">
                  <div class="earnings-card">
                    <div class="earnings-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="earnings-info">
                      <div class="earnings-value" id="monthlyEarnings">$0</div>
                      <div class="earnings-label">This Month</div>
                    </div>
                  </div>
                  <div class="earnings-card">
                    <div class="earnings-icon"><i class="fas fa-coins"></i></div>
                    <div class="earnings-info">
                      <div class="earnings-value" id="pendingEarnings">$0</div>
                      <div class="earnings-label">Pending</div>
                    </div>
                  </div>
                  <div class="earnings-card">
                    <div class="earnings-icon"><i class="fas fa-wallet"></i></div>
                    <div class="earnings-info">
                      <div class="earnings-value" id="availableBalance">$0</div>
                      <div class="earnings-label">Available</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="earnings-chart">
                <h5>Earnings Trend</h5>
                <canvas id="earningsChart" width="400" height="200"></canvas>
              </div>

              <div class="transactions-history">
                <h5>Transaction History</h5>
                <div class="transactions-list" id="transactionsList">
                  <div class="no-transactions">
                    <i class="fas fa-receipt"></i>
                    <p>No transactions yet</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Collaboration Modal -->
        <div class="modal-overlay" id="collaborationModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4 id="modalTitle">Collaboration Details</h4>
              <button class="modal-close" id="closeModal">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body" id="modalBody">
              <!-- Dynamic content -->
            </div>
          </div>
        </div>
      </div>
    `;

    this.addStyles();
  }

  setupEventListeners() {
    // Navigation tabs
    this.container.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.switchTab(e.target.dataset.tab);
      });
    });

    // Search and matching
    this.container.querySelector('#searchCollaborators').addEventListener('click', () => {
      this.searchCollaborators();
    });

    this.container.querySelector('#aiSmartMatch').addEventListener('click', () => {
      this.performAISmartMatch();
    });

    // Project management
    this.container.querySelector('#createProject').addEventListener('click', () => {
      this.showCreateProjectModal();
    });

    this.container.querySelector('#projectStatusFilter').addEventListener('change', () => {
      this.filterProjects();
    });

    // Messaging
    this.container.querySelector('#newConversation').addEventListener('click', () => {
      this.startNewConversation();
    });

    this.container.querySelector('#sendMessage').addEventListener('click', () => {
      this.sendMessage();
    });

    this.container.querySelector('#messageInput').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });

    // Modal controls
    this.container.querySelector('#closeModal').addEventListener('click', () => {
      this.hideModal();
    });

    // Filter changes
    this.container.querySelectorAll('select[id$="Filter"]').forEach(select => {
      select.addEventListener('change', () => {
        this.updateFilters();
      });
    });
  }

  initializeCollaborationServices() {
    this.loadAIRecommendations();
    this.loadRecentActivity();
    this.updateStats();
  }

  async loadUserData() {
    try {
      // Load user's collaboration data
      const userData = await this.collaborationManager.getUserProfile();
      this.userProfile = userData;
      
      // Load active collaborations
      const collaborations = await this.collaborationManager.getActiveCollaborations();
      collaborations.forEach(collab => {
        this.activeCollaborations.set(collab.id, collab);
      });

      this.updateActiveCollaborationCount();
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  }

  switchTab(tabName) {
    // Update navigation
    this.container.querySelectorAll('.nav-tab').forEach(tab => {
      tab.classList.remove('active');
    });
    this.container.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    this.container.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });
    this.container.querySelector(`#${tabName}Tab`).classList.add('active');

    // Load tab-specific data
    switch (tabName) {
      case 'matches':
        this.loadPotentialMatches();
        break;
      case 'projects':
        this.loadProjects();
        break;
      case 'messages':
        this.loadConversations();
        break;
      case 'earnings':
        this.loadEarningsData();
        break;
    }
  }

  async searchCollaborators() {
    try {
      this.showSearchLoading(true);

      const filters = this.getSearchFilters();
      const matches = await this.aiMatcher.findCollaborators(filters);
      
      this.displayMatches(matches);
      this.potentialMatches = matches;

    } catch (error) {
      console.error('Search failed:', error);
      this.showError('Failed to search for collaborators');
    } finally {
      this.showSearchLoading(false);
    }
  }

  async performAISmartMatch() {
    try {
      this.showSearchLoading(true);

      const userProfile = await this.collaborationManager.getUserProfile();
      const smartMatches = await this.aiMatcher.generateSmartMatches(userProfile);
      
      this.displayMatches(smartMatches);
      this.potentialMatches = smartMatches;

      this.showSuccess('AI has found perfect matches for you!');

    } catch (error) {
      console.error('AI matching failed:', error);
      this.showError('AI matching failed');
    } finally {
      this.showSearchLoading(false);
    }
  }

  displayMatches(matches) {
    const container = this.container.querySelector('#matchesResults');
    
    if (!matches || matches.length === 0) {
      container.innerHTML = `
        <div class="no-matches">
          <i class="fas fa-search"></i>
          <p>No matches found. Try adjusting your search criteria.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="matches-grid">
        ${matches.map(match => this.createMatchCard(match)).join('')}
      </div>
    `;
  }

  createMatchCard(match) {
    return `
      <div class="match-card" data-match-id="${match.id}">
        <div class="match-header">
          <div class="match-avatar">
            <img src="${match.avatar || '/default-avatar.png'}" alt="${match.name}" />
            <div class="match-status ${match.online ? 'online' : 'offline'}"></div>
          </div>
          <div class="match-info">
            <h5 class="match-name">${match.name}</h5>
            <p class="match-speciality">${match.speciality}</p>
            <div class="match-rating">
              ${this.createStarRating(match.rating)}
              <span class="rating-value">(${match.rating})</span>
            </div>
          </div>
          <div class="match-compatibility">
            <div class="compatibility-score">${match.compatibilityScore}%</div>
            <div class="compatibility-label">Match</div>
          </div>
        </div>

        <div class="match-details">
          <div class="match-skills">
            ${match.skills.slice(0, 3).map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
          </div>
          <div class="match-stats">
            <span class="stat">
              <i class="fas fa-handshake"></i>
              ${match.collaborations} collabs
            </span>
            <span class="stat">
              <i class="fas fa-clock"></i>
              ${match.responseTime}
            </span>
            <span class="stat">
              <i class="fas fa-dollar-sign"></i>
              ${match.priceRange}
            </span>
          </div>
        </div>

        <div class="match-actions">
          <button class="btn-secondary" onclick="window.collaborationHub?.viewProfile('${match.id}')">
            <i class="fas fa-user"></i>
            View Profile
          </button>
          <button class="btn-primary" onclick="window.collaborationHub?.startCollaboration('${match.id}')">
            <i class="fas fa-handshake"></i>
            Collaborate
          </button>
        </div>
      </div>
    `;
  }

  createStarRating(rating) {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push('<i class="fas fa-star"></i>');
    }
    
    if (hasHalfStar) {
      stars.push('<i class="fas fa-star-half-alt"></i>');
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push('<i class="far fa-star"></i>');
    }

    return stars.join('');
  }

  async loadProjects() {
    try {
      const projects = await this.collaborationManager.getProjects();
      this.projects = projects;
      this.displayProjects(projects);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  }

  displayProjects(projects) {
    const container = this.container.querySelector('#projectsGrid');
    
    if (!projects || projects.length === 0) {
      container.innerHTML = `
        <div class="no-projects">
          <i class="fas fa-project-diagram"></i>
          <p>No projects yet. Create your first collaboration project!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = projects.map(project => `
      <div class="project-card ${project.status}">
        <div class="project-header">
          <h5 class="project-title">${project.title}</h5>
          <span class="project-status ${project.status}">${project.status}</span>
        </div>
        <div class="project-details">
          <p class="project-description">${project.description}</p>
          <div class="project-meta">
            <span class="project-collaborators">
              <i class="fas fa-users"></i>
              ${project.collaborators.length} collaborators
            </span>
            <span class="project-deadline">
              <i class="fas fa-calendar"></i>
              ${this.formatDate(project.deadline)}
            </span>
            <span class="project-budget">
              <i class="fas fa-dollar-sign"></i>
              ${project.budget}
            </span>
          </div>
        </div>
        <div class="project-progress">
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${project.progress}%"></div>
          </div>
          <span class="progress-text">${project.progress}% complete</span>
        </div>
        <div class="project-actions">
          <button class="btn-secondary" onclick="window.collaborationHub?.viewProject('${project.id}')">
            <i class="fas fa-eye"></i>
            View
          </button>
          <button class="btn-primary" onclick="window.collaborationHub?.openProject('${project.id}')">
            <i class="fas fa-folder-open"></i>
            Open
          </button>
        </div>
      </div>
    `).join('');
  }

  async loadConversations() {
    try {
      const conversations = await this.collaborationManager.getConversations();
      this.displayConversations(conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  }

  displayConversations(conversations) {
    const container = this.container.querySelector('#conversationsList');
    
    if (!conversations || conversations.length === 0) {
      container.innerHTML = `
        <div class="no-conversations">
          <i class="fas fa-comments"></i>
          <p>No conversations yet</p>
        </div>
      `;
      return;
    }

    container.innerHTML = conversations.map(conv => `
      <div class="conversation-item" onclick="window.collaborationHub?.openConversation('${conv.id}')">
        <div class="conversation-avatar">
          <img src="${conv.participant.avatar}" alt="${conv.participant.name}" />
          <div class="online-indicator ${conv.participant.online ? 'online' : 'offline'}"></div>
        </div>
        <div class="conversation-info">
          <h6 class="participant-name">${conv.participant.name}</h6>
          <p class="last-message">${conv.lastMessage.text}</p>
          <span class="message-time">${this.formatTimeAgo(conv.lastMessage.timestamp)}</span>
        </div>
        ${conv.unreadCount > 0 ? `<div class="unread-badge">${conv.unreadCount}</div>` : ''}
      </div>
    `).join('');
  }

  async loadEarningsData() {
    try {
      const earnings = await this.collaborationManager.getEarningsData();
      this.displayEarnings(earnings);
    } catch (error) {
      console.error('Failed to load earnings:', error);
    }
  }

  displayEarnings(earnings) {
    this.container.querySelector('#monthlyEarnings').textContent = `$${earnings.monthly.toLocaleString()}`;
    this.container.querySelector('#pendingEarnings').textContent = `$${earnings.pending.toLocaleString()}`;
    this.container.querySelector('#availableBalance').textContent = `$${earnings.available.toLocaleString()}`;
    
    // Display transactions
    this.displayTransactions(earnings.transactions);
    
    // Draw earnings chart
    this.drawEarningsChart(earnings.chartData);
  }

  displayTransactions(transactions) {
    const container = this.container.querySelector('#transactionsList');
    
    if (!transactions || transactions.length === 0) {
      container.innerHTML = `
        <div class="no-transactions">
          <i class="fas fa-receipt"></i>
          <p>No transactions yet</p>
        </div>
      `;
      return;
    }

    container.innerHTML = transactions.map(transaction => `
      <div class="transaction-item ${transaction.type}">
        <div class="transaction-info">
          <span class="transaction-description">${transaction.description}</span>
          <span class="transaction-date">${this.formatDate(transaction.date)}</span>
        </div>
        <div class="transaction-amount ${transaction.type}">
          ${transaction.type === 'credit' ? '+' : '-'}$${transaction.amount}
        </div>
      </div>
    `).join('');
  }

  async loadAIRecommendations() {
    try {
      const recommendations = await this.aiMatcher.getRecommendations();
      this.displayRecommendations(recommendations);
    } catch (error) {
      console.error('Failed to load AI recommendations:', error);
    }
  }

  displayRecommendations(recommendations) {
    const container = this.container.querySelector('#recommendationsList');
    
    if (!recommendations || recommendations.length === 0) {
      container.innerHTML = `
        <div class="no-recommendations">
          <i class="fas fa-lightbulb"></i>
          <p>No recommendations available</p>
        </div>
      `;
      return;
    }

    container.innerHTML = recommendations.map(rec => `
      <div class="recommendation-item">
        <div class="recommendation-icon">
          <i class="fas ${rec.icon}"></i>
        </div>
        <div class="recommendation-content">
          <h6 class="recommendation-title">${rec.title}</h6>
          <p class="recommendation-description">${rec.description}</p>
          <button class="btn-small primary" onclick="window.collaborationHub?.executeRecommendation('${rec.id}')">
            ${rec.action}
          </button>
        </div>
      </div>
    `).join('');
  }

  loadRecentActivity() {
    // Mock recent activity
    const activities = [
      {
        type: 'collaboration_started',
        user: 'Alex Johnson',
        project: 'Summer Vibes Track',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
      },
      {
        type: 'project_completed',
        project: 'Podcast Series',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000)
      }
    ];

    this.displayRecentActivity(activities);
  }

  displayRecentActivity(activities) {
    const container = this.container.querySelector('#activityList');
    
    if (!activities || activities.length === 0) {
      container.innerHTML = `
        <div class="no-activity">
          <i class="fas fa-clock"></i>
          <p>No recent activity</p>
        </div>
      `;
      return;
    }

    container.innerHTML = activities.map(activity => `
      <div class="activity-item">
        <div class="activity-icon">
          <i class="fas ${this.getActivityIcon(activity.type)}"></i>
        </div>
        <div class="activity-content">
          <p class="activity-description">${this.formatActivityDescription(activity)}</p>
          <span class="activity-time">${this.formatTimeAgo(activity.timestamp)}</span>
        </div>
      </div>
    `).join('');
  }

  updateStats() {
    // Mock stats - replace with real data
    this.container.querySelector('#totalCollabs').textContent = '12';
    this.container.querySelector('#avgRating').textContent = '4.8';
    this.container.querySelector('#totalEarnings').textContent = '$5,240';
    this.container.querySelector('#successRate').textContent = '94%';
  }

  updateActiveCollaborationCount() {
    this.container.querySelector('#activeCollabCount').textContent = this.activeCollaborations.size;
  }

  getSearchFilters() {
    return {
      contentType: this.container.querySelector('#contentTypeFilter').value,
      skillLevel: this.container.querySelector('#skillLevelFilter').value,
      location: this.container.querySelector('#locationFilter').value,
      budget: this.container.querySelector('#budgetFilter').value
    };
  }

  // Utility methods
  formatDate(date) {
    return new Date(date).toLocaleDateString();
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

  getActivityIcon(type) {
    const icons = {
      collaboration_started: 'fa-handshake',
      project_completed: 'fa-check-circle',
      message_received: 'fa-envelope',
      payment_received: 'fa-dollar-sign'
    };
    return icons[type] || 'fa-info-circle';
  }

  formatActivityDescription(activity) {
    switch (activity.type) {
      case 'collaboration_started':
        return `Started collaboration with ${activity.user} on "${activity.project}"`;
      case 'project_completed':
        return `Completed project "${activity.project}"`;
      default:
        return 'Activity update';
    }
  }

  showSearchLoading(show) {
    const button = this.container.querySelector('#searchCollaborators');
    const aiButton = this.container.querySelector('#aiSmartMatch');
    
    if (show) {
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
      button.disabled = true;
      aiButton.disabled = true;
    } else {
      button.innerHTML = '<i class="fas fa-search"></i> Find Matches';
      button.disabled = false;
      aiButton.disabled = false;
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

  // Modal methods
  showModal(title, content) {
    const modal = this.container.querySelector('#collaborationModal');
    const titleElement = modal.querySelector('#modalTitle');
    const bodyElement = modal.querySelector('#modalBody');
    
    titleElement.textContent = title;
    bodyElement.innerHTML = content;
    modal.style.display = 'flex';
  }

  hideModal() {
    this.container.querySelector('#collaborationModal').style.display = 'none';
  }

  addStyles() {
    const styles = `
      <style>
        .collaboration-hub {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .hub-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%);
          border-bottom: 1px solid #333;
        }

        .hub-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .hub-status {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
        }

        .status-badge.active {
          color: #4caf50;
        }

        .hub-navigation {
          display: flex;
          background: #252526;
          border-bottom: 1px solid #333;
        }

        .nav-tab {
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
          position: relative;
        }

        .nav-tab.active {
          background: #9c27b0;
          color: #fff;
        }

        .notification-badge {
          background: #f44336;
          color: #fff;
          border-radius: 50%;
          width: 16px;
          height: 16px;
          font-size: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          position: absolute;
          top: 6px;
          right: 6px;
        }

        .tab-content {
          display: none;
          padding: 20px;
        }

        .tab-content.active {
          display: block;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 20px;
        }

        .stats-cards {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          margin-top: 12px;
        }

        .stat-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          background: #252526;
          border-radius: 8px;
        }

        .stat-icon {
          font-size: 24px;
          color: #9c27b0;
        }

        .stat-value {
          font-size: 20px;
          font-weight: bold;
          color: #fff;
        }

        .stat-label {
          font-size: 12px;
          color: #999;
        }

        .filter-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 16px;
        }

        .filter-group label {
          display: block;
          margin-bottom: 4px;
          font-size: 12px;
          color: #ccc;
        }

        .filter-group select {
          width: 100%;
          padding: 8px 12px;
          background: #252526;
          border: 1px solid #444;
          border-radius: 4px;
          color: #fff;
        }

        .matches-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 20px;
        }

        .match-card {
          background: #252526;
          border-radius: 8px;
          padding: 16px;
          border: 1px solid #333;
          transition: all 0.3s ease;
        }

        .match-card:hover {
          border-color: #9c27b0;
          transform: translateY(-2px);
        }

        .match-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .match-avatar {
          position: relative;
        }

        .match-avatar img {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          object-fit: cover;
        }

        .match-status {
          position: absolute;
          bottom: 2px;
          right: 2px;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          border: 2px solid #252526;
        }

        .match-status.online { background: #4caf50; }
        .match-status.offline { background: #666; }

        .match-info {
          flex: 1;
        }

        .match-name {
          margin: 0 0 4px 0;
          font-size: 14px;
          color: #fff;
        }

        .match-speciality {
          margin: 0 0 4px 0;
          font-size: 12px;
          color: #999;
        }

        .match-rating {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
        }

        .match-rating .fas,
        .match-rating .far {
          color: #ff9800;
        }

        .compatibility-score {
          font-size: 18px;
          font-weight: bold;
          color: #4caf50;
        }

        .compatibility-label {
          font-size: 10px;
          color: #999;
        }

        .skill-tag {
          background: #9c27b0;
          color: #fff;
          padding: 2px 6px;
          border-radius: 12px;
          font-size: 10px;
          margin-right: 4px;
        }

        .match-stats {
          display: flex;
          gap: 12px;
          margin-top: 8px;
          font-size: 11px;
          color: #999;
        }

        .match-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
        }

        .project-card {
          background: #252526;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .project-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .project-title {
          margin: 0;
          color: #fff;
          font-size: 14px;
        }

        .project-status {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 10px;
          text-transform: uppercase;
        }

        .project-status.active { background: #4caf50; color: #fff; }
        .project-status.planning { background: #ff9800; color: #fff; }
        .project-status.review { background: #2196f3; color: #fff; }
        .project-status.completed { background: #9e9e9e; color: #fff; }

        .progress-bar {
          width: 100%;
          height: 6px;
          background: #444;
          border-radius: 3px;
          overflow: hidden;
          margin: 8px 0;
        }

        .progress-fill {
          height: 100%;
          background: #9c27b0;
          transition: width 0.5s ease;
        }

        .btn-primary, .btn-secondary, .btn-small {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #9c27b0; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-small { background: #444; color: #fff; padding: 4px 8px; }

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

        .modal-close {
          background: none;
          border: none;
          color: #ccc;
          cursor: pointer;
          font-size: 16px;
        }

        .messages-container {
          display: flex;
          height: 500px;
        }

        .conversations-sidebar {
          width: 300px;
          border-right: 1px solid #333;
        }

        .chat-area {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .chat-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #666;
        }

        .earnings-summary {
          display: flex;
          gap: 16px;
          margin-bottom: 20px;
        }

        .earnings-card {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          background: #252526;
          border-radius: 8px;
        }

        .earnings-icon {
          font-size: 24px;
          color: #4caf50;
        }

        .earnings-value {
          font-size: 20px;
          font-weight: bold;
          color: #4caf50;
        }

        .earnings-label {
          font-size: 12px;
          color: #999;
        }
      </style>
    `;
    
    if (!document.querySelector('#collaboration-hub-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'collaboration-hub-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  viewProfile(matchId) {
    const match = this.potentialMatches.find(m => m.id === matchId);
    if (match) {
      this.showModal('Collaborator Profile', this.createProfileModal(match));
    }
  }

  startCollaboration(matchId) {
    const match = this.potentialMatches.find(m => m.id === matchId);
    if (match) {
      this.showModal('Start Collaboration', this.createCollaborationModal(match));
    }
  }

  createProfileModal(match) {
    return `
      <div class="profile-modal">
        <div class="profile-header">
          <img src="${match.avatar}" alt="${match.name}" class="profile-avatar" />
          <div class="profile-info">
            <h4>${match.name}</h4>
            <p>${match.speciality}</p>
            <div class="profile-rating">${this.createStarRating(match.rating)}</div>
          </div>
        </div>
        <div class="profile-details">
          <h5>Skills</h5>
          <div class="skills-list">
            ${match.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
          </div>
          <h5>Portfolio</h5>
          <div class="portfolio-samples">
            <!-- Portfolio items would go here -->
          </div>
        </div>
      </div>
    `;
  }

  createCollaborationModal(match) {
    return `
      <div class="collaboration-form">
        <h5>Start a new collaboration with ${match.name}</h5>
        <form id="collaborationForm">
          <div class="form-group">
            <label>Project Type</label>
            <select name="projectType">
              <option value="music">Music Production</option>
              <option value="video">Video Creation</option>
              <option value="podcast">Podcast</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="form-group">
            <label>Project Description</label>
            <textarea name="description" rows="4" placeholder="Describe your collaboration idea..."></textarea>
          </div>
          <div class="form-group">
            <label>Budget</label>
            <input type="text" name="budget" placeholder="e.g., $500 or Revenue Share" />
          </div>
          <div class="form-group">
            <label>Timeline</label>
            <input type="date" name="deadline" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" onclick="window.collaborationHub?.hideModal()">
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              Send Collaboration Request
            </button>
          </div>
        </form>
      </div>
    `;
  }

  destroy() {
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CollaborationHub;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.CollaborationHub = CollaborationHub;
  window.collaborationHub = null; // Will be set when instantiated
}