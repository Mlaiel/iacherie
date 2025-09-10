/**
 * Ainflue Desktop - Content Library Component
 * 
 * Advanced content management with AI-powered organization and professional workflow support
 * Implements multi-format content library with search, filtering, and metadata management
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class ContentLibraryComponent {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      multiSelect: true,
      dragDrop: true,
      preview: true,
      search: true,
      filters: true,
      metadata: true,
      virtualScrolling: true,
      realTimeUpdates: true,
      aiOrganization: true,
      ...options
    };

    this.contentItems = new Map();
    this.filteredItems = [];
    this.selectedItems = new Set();
    this.currentView = 'grid';
    this.sortBy = 'dateModified';
    this.sortOrder = 'desc';
    this.searchQuery = '';
    this.activeFilters = new Map();
    this.dragData = null;
    this.virtualScrollOffset = 0;
    this.viewportHeight = 0;
    this.itemHeight = 180;

    this.supportedFormats = {
      audio: ['.mp3', '.wav', '.flac', '.aiff', '.aac', '.m4a', '.ogg'],
      video: ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv'],
      image: ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.tiff'],
      document: ['.pdf', '.txt', '.md', '.doc', '.docx']
    };

    this.initialize();
  }

  initialize() {
    this.createStructure();
    this.setupEventHandlers();
    this.initializeFilters();
    this.loadContentLibrary();
    this.setupVirtualScrolling();
    this.initializeAIFeatures();
  }

  createStructure() {
    this.container.innerHTML = `
      <div class="content-library">
        <div class="library-header">
          <div class="library-toolbar">
            <div class="search-section">
              <div class="search-input-wrapper">
                <input type="text" class="library-search" placeholder="Search content..." />
                <div class="search-icon">🔍</div>
              </div>
              <button class="ai-organize-btn" title="AI-Powered Organization">🤖</button>
            </div>
            
            <div class="view-controls">
              <button class="view-btn" data-view="grid" title="Grid View">⊞</button>
              <button class="view-btn" data-view="list" title="List View">☰</button>
              <button class="view-btn" data-view="timeline" title="Timeline View">📊</button>
            </div>
            
            <div class="sort-controls">
              <select class="sort-select">
                <option value="dateModified">Date Modified</option>
                <option value="dateCreated">Date Created</option>
                <option value="name">Name</option>
                <option value="size">File Size</option>
                <option value="duration">Duration</option>
                <option value="rating">Rating</option>
              </select>
              <button class="sort-order-btn" data-order="desc" title="Sort Order">⬇</button>
            </div>
          </div>
          
          <div class="library-filters">
            <div class="filter-group">
              <label>Type:</label>
              <div class="filter-buttons">
                <button class="filter-btn" data-filter="type" data-value="all">All</button>
                <button class="filter-btn" data-filter="type" data-value="audio">Audio</button>
                <button class="filter-btn" data-filter="type" data-value="video">Video</button>
                <button class="filter-btn" data-filter="type" data-value="image">Images</button>
                <button class="filter-btn" data-filter="type" data-value="document">Documents</button>
              </div>
            </div>
            
            <div class="filter-group">
              <label>Status:</label>
              <div class="filter-buttons">
                <button class="filter-btn" data-filter="status" data-value="all">All</button>
                <button class="filter-btn" data-filter="status" data-value="processed">Processed</button>
                <button class="filter-btn" data-filter="status" data-value="pending">Pending</button>
                <button class="filter-btn" data-filter="status" data-value="protected">Protected</button>
              </div>
            </div>
            
            <div class="filter-group">
              <label>Quality:</label>
              <div class="filter-buttons">
                <button class="filter-btn" data-filter="quality" data-value="all">All</button>
                <button class="filter-btn" data-filter="quality" data-value="professional">Professional</button>
                <button class="filter-btn" data-filter="quality" data-value="broadcast">Broadcast</button>
                <button class="filter-btn" data-filter="quality" data-value="web">Web</button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="library-content">
          <div class="content-viewport">
            <div class="content-items-container"></div>
          </div>
          
          <div class="library-sidebar">
            <div class="metadata-panel">
              <h3>Properties</h3>
              <div class="metadata-content">
                <p class="no-selection">Select an item to view properties</p>
              </div>
            </div>
            
            <div class="preview-panel">
              <h3>Preview</h3>
              <div class="preview-content">
                <div class="preview-placeholder">
                  <div class="preview-icon">👁</div>
                  <p>Select an item to preview</p>
                </div>
              </div>
            </div>
            
            <div class="ai-insights-panel">
              <h3>AI Insights</h3>
              <div class="insights-content">
                <div class="insight-placeholder">
                  <div class="ai-icon">🤖</div>
                  <p>AI analysis will appear here</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="library-footer">
          <div class="status-bar">
            <span class="items-count">0 items</span>
            <span class="selection-info"></span>
            <span class="storage-info">0 MB used</span>
          </div>
        </div>
      </div>
    `;

    // Add professional styling
    this.addStyling();
  }

  addStyling() {
    const style = document.createElement('style');
    style.textContent = `
      .content-library {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: #1a1a1a;
        color: #ffffff;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .library-header {
        background: #2a2a2a;
        border-bottom: 1px solid #404040;
        padding: 12px;
      }

      .library-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
      }

      .search-section {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .search-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
      }

      .library-search {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 8px;
        padding: 8px 12px 8px 36px;
        color: #ffffff;
        width: 300px;
        font-size: 14px;
      }

      .library-search:focus {
        outline: none;
        border-color: #007aff;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
      }

      .search-icon {
        position: absolute;
        left: 12px;
        color: #888;
        pointer-events: none;
      }

      .ai-organize-btn, .view-btn, .sort-order-btn {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .ai-organize-btn:hover, .view-btn:hover, .sort-order-btn:hover {
        background: #4a4a4a;
        border-color: #007aff;
      }

      .view-controls, .sort-controls {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .sort-select {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 6px;
        color: #ffffff;
        padding: 8px 12px;
        margin-right: 4px;
      }

      .library-filters {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
      }

      .filter-group {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .filter-group label {
        font-size: 12px;
        color: #888;
        font-weight: 500;
      }

      .filter-buttons {
        display: flex;
        gap: 4px;
      }

      .filter-btn {
        background: #3a3a3a;
        border: 1px solid #555;
        border-radius: 4px;
        color: #ffffff;
        padding: 4px 8px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .filter-btn:hover {
        background: #4a4a4a;
      }

      .filter-btn.active {
        background: #007aff;
        border-color: #007aff;
      }

      .library-content {
        flex: 1;
        display: flex;
        overflow: hidden;
      }

      .content-viewport {
        flex: 1;
        overflow: auto;
        background: #1a1a1a;
      }

      .content-items-container {
        padding: 16px;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
      }

      .content-item {
        background: #2a2a2a;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
      }

      .content-item:hover {
        background: #3a3a3a;
        border-color: #007aff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      }

      .content-item.selected {
        background: #1a4a7a;
        border-color: #007aff;
      }

      .content-item.dragging {
        opacity: 0.6;
        transform: rotate(5deg);
      }

      .item-thumbnail {
        width: 100%;
        height: 100px;
        background: #3a3a3a;
        border-radius: 4px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
      }

      .item-thumbnail img {
        max-width: 100%;
        max-height: 100%;
        object-fit: cover;
      }

      .item-icon {
        font-size: 32px;
        opacity: 0.6;
      }

      .item-info {
        font-size: 12px;
      }

      .item-name {
        font-weight: 500;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .item-details {
        color: #888;
        display: flex;
        justify-content: space-between;
      }

      .item-status {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff00;
      }

      .item-status.pending { background: #ffaa00; }
      .item-status.error { background: #ff4444; }

      .library-sidebar {
        width: 300px;
        background: #2a2a2a;
        border-left: 1px solid #404040;
        display: flex;
        flex-direction: column;
      }

      .metadata-panel, .preview-panel, .ai-insights-panel {
        flex: 1;
        border-bottom: 1px solid #404040;
        padding: 16px;
      }

      .metadata-panel h3, .preview-panel h3, .ai-insights-panel h3 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #ffffff;
      }

      .preview-placeholder, .insight-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 120px;
        color: #888;
        text-align: center;
      }

      .preview-icon, .ai-icon {
        font-size: 24px;
        margin-bottom: 8px;
        opacity: 0.6;
      }

      .library-footer {
        background: #2a2a2a;
        border-top: 1px solid #404040;
        padding: 8px 16px;
      }

      .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #888;
      }

      /* List view styles */
      .content-items-container.list-view {
        display: block;
      }

      .content-item.list-item {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin-bottom: 4px;
      }

      .content-item.list-item .item-thumbnail {
        width: 48px;
        height: 48px;
        margin-right: 12px;
        margin-bottom: 0;
      }

      .content-item.list-item .item-info {
        flex: 1;
      }

      /* Timeline view styles */
      .content-items-container.timeline-view {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }

      .content-item.timeline-item {
        display: flex;
        align-items: center;
        height: 40px;
        padding: 4px 12px;
      }

      /* Drag and drop styles */
      .drop-zone {
        border: 2px dashed #007aff;
        background: rgba(0, 122, 255, 0.1);
      }

      .drop-zone-active {
        border-color: #00ff00;
        background: rgba(0, 255, 0, 0.1);
      }
    `;
    document.head.appendChild(style);
  }

  setupEventHandlers() {
    // Search functionality
    this.container.querySelector('.library-search').addEventListener('input', (e) => {
      this.searchQuery = e.target.value;
      this.filterContent();
    });

    // AI organize button
    this.container.querySelector('.ai-organize-btn').addEventListener('click', () => {
      this.organizeWithAI();
    });

    // View controls
    this.container.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.setView(e.target.dataset.view);
      });
    });

    // Sort controls
    this.container.querySelector('.sort-select').addEventListener('change', (e) => {
      this.sortBy = e.target.value;
      this.sortContent();
    });

    this.container.querySelector('.sort-order-btn').addEventListener('click', (e) => {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      e.target.textContent = this.sortOrder === 'asc' ? '⬆' : '⬇';
      e.target.dataset.order = this.sortOrder;
      this.sortContent();
    });

    // Filter buttons
    this.container.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.handleFilterClick(e.target);
      });
    });

    // Content viewport scrolling
    this.container.querySelector('.content-viewport').addEventListener('scroll', (e) => {
      this.handleScroll(e);
    });

    // Drag and drop
    this.setupDragAndDrop();
  }

  setupDragAndDrop() {
    const viewport = this.container.querySelector('.content-viewport');

    // File drop handling
    viewport.addEventListener('dragover', (e) => {
      e.preventDefault();
      viewport.classList.add('drop-zone');
    });

    viewport.addEventListener('dragleave', (e) => {
      if (!viewport.contains(e.relatedTarget)) {
        viewport.classList.remove('drop-zone');
      }
    });

    viewport.addEventListener('drop', (e) => {
      e.preventDefault();
      viewport.classList.remove('drop-zone');
      this.handleFileDrop(e);
    });

    // Item drag handling
    this.container.addEventListener('dragstart', (e) => {
      if (e.target.closest('.content-item')) {
        this.handleItemDragStart(e);
      }
    });

    this.container.addEventListener('dragend', (e) => {
      if (e.target.closest('.content-item')) {
        this.handleItemDragEnd(e);
      }
    });
  }

  initializeFilters() {
    this.activeFilters.set('type', 'all');
    this.activeFilters.set('status', 'all');
    this.activeFilters.set('quality', 'all');

    // Set default active filter
    this.container.querySelector('.filter-btn[data-filter="type"][data-value="all"]').classList.add('active');
    this.container.querySelector('.filter-btn[data-filter="status"][data-value="all"]').classList.add('active');
    this.container.querySelector('.filter-btn[data-filter="quality"][data-value="all"]').classList.add('active');
  }

  async loadContentLibrary() {
    try {
      // Simulate loading content from the system
      const mockContent = this.generateMockContent();
      
      for (const item of mockContent) {
        this.contentItems.set(item.id, item);
      }

      this.filterContent();
      this.updateStatusBar();
    } catch (error) {
      console.error('Failed to load content library:', error);
    }
  }

  generateMockContent() {
    const mockItems = [];
    const types = ['audio', 'video', 'image'];
    const statuses = ['processed', 'pending', 'protected'];
    const qualities = ['professional', 'broadcast', 'web'];

    for (let i = 0; i < 50; i++) {
      const type = types[Math.floor(Math.random() * types.length)];
      const extension = this.supportedFormats[type][Math.floor(Math.random() * this.supportedFormats[type].length)];
      
      mockItems.push({
        id: `item_${i}`,
        name: `Content Item ${i + 1}${extension}`,
        type: type,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        quality: qualities[Math.floor(Math.random() * qualities.length)],
        size: Math.floor(Math.random() * 100) + 1, // MB
        duration: type === 'image' ? null : Math.floor(Math.random() * 300) + 30, // seconds
        dateCreated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
        dateModified: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
        rating: Math.floor(Math.random() * 5) + 1,
        thumbnail: null,
        metadata: {
          bitrate: type === 'audio' ? '320 kbps' : null,
          resolution: type !== 'audio' ? '1920x1080' : null,
          channels: type === 'audio' ? 'Stereo' : null
        },
        aiAnalysis: {
          genre: type === 'audio' ? 'Electronic' : null,
          mood: 'Energetic',
          tags: ['professional', 'high-quality'],
          suggestions: ['Consider adding reverb', 'Optimize for streaming']
        }
      });
    }

    return mockItems;
  }

  filterContent() {
    this.filteredItems = Array.from(this.contentItems.values()).filter(item => {
      // Search query filter
      if (this.searchQuery) {
        const searchLower = this.searchQuery.toLowerCase();
        if (!item.name.toLowerCase().includes(searchLower) &&
            !item.aiAnalysis.tags.some(tag => tag.toLowerCase().includes(searchLower))) {
          return false;
        }
      }

      // Type filter
      const typeFilter = this.activeFilters.get('type');
      if (typeFilter !== 'all' && item.type !== typeFilter) {
        return false;
      }

      // Status filter
      const statusFilter = this.activeFilters.get('status');
      if (statusFilter !== 'all' && item.status !== statusFilter) {
        return false;
      }

      // Quality filter
      const qualityFilter = this.activeFilters.get('quality');
      if (qualityFilter !== 'all' && item.quality !== qualityFilter) {
        return false;
      }

      return true;
    });

    this.sortContent();
    this.renderContent();
    this.updateStatusBar();
  }

  sortContent() {
    this.filteredItems.sort((a, b) => {
      let aValue, bValue;

      switch (this.sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'duration':
          aValue = a.duration || 0;
          bValue = b.duration || 0;
          break;
        case 'rating':
          aValue = a.rating;
          bValue = b.rating;
          break;
        case 'dateCreated':
          aValue = a.dateCreated.getTime();
          bValue = b.dateCreated.getTime();
          break;
        case 'dateModified':
        default:
          aValue = a.dateModified.getTime();
          bValue = b.dateModified.getTime();
          break;
      }

      if (this.sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }

  renderContent() {
    const container = this.container.querySelector('.content-items-container');
    container.innerHTML = '';

    // Apply view class
    container.className = `content-items-container ${this.currentView}-view`;

    for (const item of this.filteredItems) {
      const itemElement = this.createContentItemElement(item);
      container.appendChild(itemElement);
    }
  }

  createContentItemElement(item) {
    const element = document.createElement('div');
    element.className = `content-item ${this.currentView}-item`;
    element.dataset.itemId = item.id;
    element.draggable = true;

    const typeIcon = this.getTypeIcon(item.type);
    const formattedSize = this.formatFileSize(item.size * 1024 * 1024);
    const formattedDuration = item.duration ? this.formatDuration(item.duration) : '';

    element.innerHTML = `
      <div class="item-thumbnail">
        ${item.thumbnail ? `<img src="${item.thumbnail}" alt="Thumbnail" />` : `<div class="item-icon">${typeIcon}</div>`}
      </div>
      <div class="item-info">
        <div class="item-name" title="${item.name}">${item.name}</div>
        <div class="item-details">
          <span>${formattedSize}</span>
          ${formattedDuration ? `<span>${formattedDuration}</span>` : ''}
        </div>
      </div>
      <div class="item-status ${item.status}"></div>
    `;

    element.addEventListener('click', (e) => {
      this.handleItemSelection(item, e.ctrlKey || e.metaKey);
    });

    element.addEventListener('dblclick', () => {
      this.openItem(item);
    });

    return element;
  }

  setView(viewType) {
    this.currentView = viewType;
    
    // Update active view button
    this.container.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === viewType);
    });

    this.renderContent();
  }

  handleFilterClick(button) {
    const filterType = button.dataset.filter;
    const filterValue = button.dataset.value;

    // Update active filter button
    this.container.querySelectorAll(`.filter-btn[data-filter="${filterType}"]`).forEach(btn => {
      btn.classList.remove('active');
    });
    button.classList.add('active');

    // Update filter
    this.activeFilters.set(filterType, filterValue);
    this.filterContent();
  }

  handleItemSelection(item, multiSelect = false) {
    if (!multiSelect) {
      this.selectedItems.clear();
    }

    if (this.selectedItems.has(item.id)) {
      this.selectedItems.delete(item.id);
    } else {
      this.selectedItems.add(item.id);
    }

    // Update visual selection
    this.updateSelectionVisual();
    
    // Update metadata panel
    this.updateMetadataPanel();
    
    // Update preview panel
    this.updatePreviewPanel();
    
    // Update AI insights
    this.updateAIInsights();
    
    // Update status bar
    this.updateStatusBar();
  }

  updateSelectionVisual() {
    this.container.querySelectorAll('.content-item').forEach(element => {
      const itemId = element.dataset.itemId;
      element.classList.toggle('selected', this.selectedItems.has(itemId));
    });
  }

  updateMetadataPanel() {
    const panel = this.container.querySelector('.metadata-content');
    
    if (this.selectedItems.size === 0) {
      panel.innerHTML = '<p class="no-selection">Select an item to view properties</p>';
      return;
    }

    if (this.selectedItems.size === 1) {
      const itemId = Array.from(this.selectedItems)[0];
      const item = this.contentItems.get(itemId);
      
      panel.innerHTML = `
        <div class="metadata-item">
          <label>Name:</label>
          <span>${item.name}</span>
        </div>
        <div class="metadata-item">
          <label>Type:</label>
          <span>${item.type}</span>
        </div>
        <div class="metadata-item">
          <label>Size:</label>
          <span>${this.formatFileSize(item.size * 1024 * 1024)}</span>
        </div>
        ${item.duration ? `
        <div class="metadata-item">
          <label>Duration:</label>
          <span>${this.formatDuration(item.duration)}</span>
        </div>
        ` : ''}
        <div class="metadata-item">
          <label>Status:</label>
          <span>${item.status}</span>
        </div>
        <div class="metadata-item">
          <label>Quality:</label>
          <span>${item.quality}</span>
        </div>
        <div class="metadata-item">
          <label>Created:</label>
          <span>${item.dateCreated.toLocaleDateString()}</span>
        </div>
        <div class="metadata-item">
          <label>Modified:</label>
          <span>${item.dateModified.toLocaleDateString()}</span>
        </div>
      `;
    } else {
      panel.innerHTML = `<p class="multi-selection">${this.selectedItems.size} items selected</p>`;
    }
  }

  updatePreviewPanel() {
    const panel = this.container.querySelector('.preview-content');
    
    if (this.selectedItems.size !== 1) {
      panel.innerHTML = `
        <div class="preview-placeholder">
          <div class="preview-icon">👁</div>
          <p>Select an item to preview</p>
        </div>
      `;
      return;
    }

    const itemId = Array.from(this.selectedItems)[0];
    const item = this.contentItems.get(itemId);
    
    // Generate preview based on type
    let previewContent = '';
    
    switch (item.type) {
      case 'audio':
        previewContent = `
          <div class="audio-preview">
            <div class="waveform-placeholder">🎵 Audio Waveform</div>
            <div class="audio-controls">
              <button class="play-btn">▶</button>
              <span class="time">0:00 / ${this.formatDuration(item.duration)}</span>
            </div>
          </div>
        `;
        break;
      case 'video':
        previewContent = `
          <div class="video-preview">
            <div class="video-placeholder">🎬 Video Preview</div>
            <div class="video-controls">
              <button class="play-btn">▶</button>
              <span class="time">0:00 / ${this.formatDuration(item.duration)}</span>
            </div>
          </div>
        `;
        break;
      case 'image':
        previewContent = `
          <div class="image-preview">
            <div class="image-placeholder">🖼 Image Preview</div>
          </div>
        `;
        break;
      default:
        previewContent = `
          <div class="document-preview">
            <div class="document-placeholder">📄 Document Preview</div>
          </div>
        `;
    }
    
    panel.innerHTML = previewContent;
  }

  updateAIInsights() {
    const panel = this.container.querySelector('.insights-content');
    
    if (this.selectedItems.size !== 1) {
      panel.innerHTML = `
        <div class="insight-placeholder">
          <div class="ai-icon">🤖</div>
          <p>AI analysis will appear here</p>
        </div>
      `;
      return;
    }

    const itemId = Array.from(this.selectedItems)[0];
    const item = this.contentItems.get(itemId);
    
    panel.innerHTML = `
      <div class="ai-insights">
        ${item.aiAnalysis.genre ? `
        <div class="insight-item">
          <label>Genre:</label>
          <span>${item.aiAnalysis.genre}</span>
        </div>
        ` : ''}
        <div class="insight-item">
          <label>Mood:</label>
          <span>${item.aiAnalysis.mood}</span>
        </div>
        <div class="insight-item">
          <label>Tags:</label>
          <div class="tag-list">
            ${item.aiAnalysis.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
          </div>
        </div>
        <div class="insight-item">
          <label>Suggestions:</label>
          <ul class="suggestion-list">
            ${item.aiAnalysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  }

  updateStatusBar() {
    const statusBar = this.container.querySelector('.status-bar');
    const itemsCount = statusBar.querySelector('.items-count');
    const selectionInfo = statusBar.querySelector('.selection-info');
    const storageInfo = statusBar.querySelector('.storage-info');
    
    itemsCount.textContent = `${this.filteredItems.length} items`;
    
    if (this.selectedItems.size > 0) {
      selectionInfo.textContent = `${this.selectedItems.size} selected`;
    } else {
      selectionInfo.textContent = '';
    }
    
    const totalSize = Array.from(this.contentItems.values())
      .reduce((total, item) => total + item.size, 0);
    storageInfo.textContent = `${this.formatFileSize(totalSize * 1024 * 1024)} used`;
  }

  // AI Organization
  async organizeWithAI() {
    console.log('🤖 AI organization started...');
    
    // Simulate AI analysis and organization
    const organizationSuggestions = {
      collections: [
        { name: 'Music Tracks', items: [], type: 'audio' },
        { name: 'Video Content', items: [], type: 'video' },
        { name: 'Graphics & Images', items: [], type: 'image' }
      ],
      duplicates: [],
      qualityIssues: [],
      optimizationSuggestions: []
    };
    
    // Organize items by type and quality
    for (const item of this.contentItems.values()) {
      const collection = organizationSuggestions.collections.find(c => c.type === item.type);
      if (collection) {
        collection.items.push(item.id);
      }
    }
    
    console.log('🤖 AI organization complete:', organizationSuggestions);
    
    // Show organization results (would implement modal/panel in real app)
    alert(`AI Organization Complete!\n\nFound:\n- ${organizationSuggestions.collections[0].items.length} audio files\n- ${organizationSuggestions.collections[1].items.length} video files\n- ${organizationSuggestions.collections[2].items.length} image files`);
  }

  // Drag and Drop Handlers
  handleFileDrop(event) {
    const files = Array.from(event.dataTransfer.files);
    console.log('📁 Files dropped:', files.map(f => f.name));
    
    for (const file of files) {
      this.importFile(file);
    }
  }

  handleItemDragStart(event) {
    const item = event.target.closest('.content-item');
    item.classList.add('dragging');
    
    this.dragData = {
      itemId: item.dataset.itemId,
      startTime: Date.now()
    };
    
    event.dataTransfer.effectAllowed = 'copy';
    event.dataTransfer.setData('text/plain', item.dataset.itemId);
  }

  handleItemDragEnd(event) {
    const item = event.target.closest('.content-item');
    item.classList.remove('dragging');
    this.dragData = null;
  }

  async importFile(file) {
    const fileType = this.detectFileType(file.name);
    
    if (!fileType) {
      console.warn('Unsupported file type:', file.name);
      return;
    }
    
    const newItem = {
      id: `imported_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      type: fileType,
      status: 'pending',
      quality: 'web',
      size: Math.round(file.size / (1024 * 1024)),
      duration: fileType === 'image' ? null : 120, // Default duration
      dateCreated: new Date(),
      dateModified: new Date(),
      rating: 3,
      thumbnail: null,
      metadata: {},
      aiAnalysis: {
        genre: null,
        mood: 'Unknown',
        tags: ['imported'],
        suggestions: ['Analyze with AI for optimization suggestions']
      }
    };
    
    this.contentItems.set(newItem.id, newItem);
    this.filterContent();
    
    console.log('📥 File imported:', newItem.name);
  }

  detectFileType(filename) {
    const extension = '.' + filename.split('.').pop().toLowerCase();
    
    for (const [type, extensions] of Object.entries(this.supportedFormats)) {
      if (extensions.includes(extension)) {
        return type;
      }
    }
    
    return null;
  }

  openItem(item) {
    console.log('🔓 Opening item:', item.name);
    // In a real application, this would open the item in the appropriate editor
  }

  // Virtual Scrolling (for large libraries)
  setupVirtualScrolling() {
    if (!this.options.virtualScrolling) return;
    
    const viewport = this.container.querySelector('.content-viewport');
    this.viewportHeight = viewport.clientHeight;
    
    // Virtual scrolling would be implemented here for performance with large libraries
  }

  handleScroll(event) {
    // Virtual scrolling logic would be implemented here
  }

  initializeAIFeatures() {
    if (!this.options.aiOrganization) return;
    
    // Initialize AI-powered features like smart tagging, duplicate detection, etc.
    console.log('🤖 AI features initialized');
  }

  // Utility Methods
  getTypeIcon(type) {
    const icons = {
      audio: '🎵',
      video: '🎬',
      image: '🖼',
      document: '📄'
    };
    return icons[type] || '📄';
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  // Public API
  getSelectedItems() {
    return Array.from(this.selectedItems).map(id => this.contentItems.get(id));
  }

  selectAll() {
    this.selectedItems.clear();
    for (const item of this.filteredItems) {
      this.selectedItems.add(item.id);
    }
    this.updateSelectionVisual();
    this.updateStatusBar();
  }

  clearSelection() {
    this.selectedItems.clear();
    this.updateSelectionVisual();
    this.updateMetadataPanel();
    this.updatePreviewPanel();
    this.updateAIInsights();
    this.updateStatusBar();
  }

  refresh() {
    this.loadContentLibrary();
  }

  exportSelected() {
    const selected = this.getSelectedItems();
    console.log('📤 Exporting selected items:', selected.map(item => item.name));
    // Export functionality would be implemented here
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ContentLibraryComponent;
}