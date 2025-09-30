/**
 * Ainflue Desktop - Protection Dashboard Component
 * 
 * Advanced rights protection interface for intellectual property management
 * Implements DMCA compliance, copyright detection, and legal protection tools
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class ProtectionDashboard {
  constructor(container, securityManager, copyrightEngine) {
    this.container = container;
    this.securityManager = securityManager;
    this.copyrightEngine = copyrightEngine;
    this.protectedAssets = new Map();
    this.monitoringActive = false;
    this.violations = [];
    
    this.init();
  }

  init() {
    this.createDashboardStructure();
    this.setupEventListeners();
    this.initializeProtectionServices();
    this.startRealTimeMonitoring();
  }

  createDashboardStructure() {
    this.container.innerHTML = `
      <div class="protection-dashboard">
        <div class="dashboard-header">
          <h3><i class="fas fa-shield-alt"></i> IP Protection Dashboard</h3>
          <div class="protection-status">
            <div class="status-indicator ${this.monitoringActive ? 'active' : 'inactive'}">
              <div class="status-light"></div>
              <span>Real-time Protection ${this.monitoringActive ? 'Active' : 'Inactive'}</span>
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <!-- Protection Overview -->
          <div class="protection-overview">
            <div class="metric-cards">
              <div class="metric-card assets">
                <div class="metric-icon"><i class="fas fa-file-shield"></i></div>
                <div class="metric-value" id="protectedAssetsCount">0</div>
                <div class="metric-label">Protected Assets</div>
              </div>
              <div class="metric-card violations">
                <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="metric-value" id="violationsCount">0</div>
                <div class="metric-label">Violations Detected</div>
              </div>
              <div class="metric-card takedowns">
                <div class="metric-icon"><i class="fas fa-gavel"></i></div>
                <div class="metric-value" id="takedownsCount">0</div>
                <div class="metric-label">DMCA Takedowns</div>
              </div>
              <div class="metric-card revenue">
                <div class="metric-icon"><i class="fas fa-dollar-sign"></i></div>
                <div class="metric-value" id="protectedRevenue">$0</div>
                <div class="metric-label">Protected Revenue</div>
              </div>
            </div>
          </div>

          <!-- Protection Controls -->
          <div class="protection-controls">
            <div class="control-section">
              <h4>Protection Settings</h4>
              <div class="control-grid">
                <label class="control-toggle">
                  <input type="checkbox" id="autoWatermark" checked>
                  <span class="toggle-slider"></span>
                  Auto Watermarking
                </label>
                <label class="control-toggle">
                  <input type="checkbox" id="copyrightMonitoring" checked>
                  <span class="toggle-slider"></span>
                  Copyright Monitoring
                </label>
                <label class="control-toggle">
                  <input type="checkbox" id="dmcaProtection" checked>
                  <span class="toggle-slider"></span>
                  DMCA Protection
                </label>
                <label class="control-toggle">
                  <input type="checkbox" id="realTimeAlerts" checked>
                  <span class="toggle-slider"></span>
                  Real-time Alerts
                </label>
                <label class="control-toggle">
                  <input type="checkbox" id="aiDetection" checked>
                  <span class="toggle-slider"></span>
                  AI Detection
                </label>
                <label class="control-toggle">
                  <input type="checkbox" id="blockchainRegistry">
                  <span class="toggle-slider"></span>
                  Blockchain Registry
                </label>
              </div>
            </div>

            <div class="action-buttons">
              <button class="btn-primary" id="scanAllContent">
                <i class="fas fa-search"></i>
                Scan All Content
              </button>
              <button class="btn-secondary" id="generateReport">
                <i class="fas fa-file-alt"></i>
                Generate Report
              </button>
              <button class="btn-danger" id="emergencyProtection">
                <i class="fas fa-ban"></i>
                Emergency Protection
              </button>
            </div>
          </div>

          <!-- Protected Assets Table -->
          <div class="protected-assets">
            <div class="section-header">
              <h4>Protected Assets</h4>
              <div class="filter-controls">
                <select id="assetTypeFilter">
                  <option value="all">All Types</option>
                  <option value="video">Video</option>
                  <option value="audio">Audio</option>
                  <option value="image">Image</option>
                  <option value="text">Text</option>
                </select>
                <select id="protectionLevelFilter">
                  <option value="all">All Levels</option>
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="premium">Premium</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>
            <div class="assets-table-container">
              <table class="assets-table" id="assetsTable">
                <thead>
                  <tr>
                    <th>Asset</th>
                    <th>Type</th>
                    <th>Protection Level</th>
                    <th>Status</th>
                    <th>Violations</th>
                    <th>Last Scan</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody id="assetsTableBody">
                  <tr class="no-data">
                    <td colspan="7">
                      <div class="no-data-message">
                        <i class="fas fa-shield-alt"></i>
                        <p>No protected assets found</p>
                        <button class="btn-link" onclick="this.closest('.protection-dashboard').querySelector('#scanAllContent').click()">
                          Start protecting your content
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Violations Monitor -->
          <div class="violations-monitor">
            <div class="section-header">
              <h4>Recent Violations</h4>
              <div class="monitor-controls">
                <button class="btn-small" id="refreshViolations">
                  <i class="fas fa-sync-alt"></i>
                  Refresh
                </button>
                <button class="btn-small" id="exportViolations">
                  <i class="fas fa-download"></i>
                  Export
                </button>
              </div>
            </div>
            <div class="violations-list" id="violationsList">
              <div class="no-violations">
                <i class="fas fa-check-circle"></i>
                <p>No violations detected</p>
              </div>
            </div>
          </div>

          <!-- Legal Actions -->
          <div class="legal-actions">
            <div class="section-header">
              <h4>Legal Actions</h4>
              <button class="btn-primary" id="newLegalAction">
                <i class="fas fa-plus"></i>
                New Action
              </button>
            </div>
            <div class="actions-grid" id="legalActionsGrid">
              <div class="no-actions">
                <i class="fas fa-balance-scale"></i>
                <p>No legal actions in progress</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Protection Modal -->
        <div class="modal-overlay" id="protectionModal" style="display: none;">
          <div class="modal-content">
            <div class="modal-header">
              <h4 id="modalTitle">Asset Protection</h4>
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
    // Protection controls
    this.container.querySelectorAll('.control-toggle input').forEach(toggle => {
      toggle.addEventListener('change', (e) => {
        this.handleProtectionToggle(e.target.id, e.target.checked);
      });
    });

    // Action buttons
    this.container.querySelector('#scanAllContent').addEventListener('click', () => {
      this.scanAllContent();
    });

    this.container.querySelector('#generateReport').addEventListener('click', () => {
      this.generateProtectionReport();
    });

    this.container.querySelector('#emergencyProtection').addEventListener('click', () => {
      this.activateEmergencyProtection();
    });

    this.container.querySelector('#refreshViolations').addEventListener('click', () => {
      this.refreshViolations();
    });

    this.container.querySelector('#exportViolations').addEventListener('click', () => {
      this.exportViolations();
    });

    this.container.querySelector('#newLegalAction').addEventListener('click', () => {
      this.showNewLegalActionModal();
    });

    // Filters
    this.container.querySelector('#assetTypeFilter').addEventListener('change', () => {
      this.filterAssets();
    });

    this.container.querySelector('#protectionLevelFilter').addEventListener('change', () => {
      this.filterAssets();
    });

    // Modal controls
    this.container.querySelector('#closeModal').addEventListener('click', () => {
      this.hideModal();
    });

    // Listen for content changes
    window.electronAPI?.onContentUpdated?.(this.handleContentUpdate.bind(this));
  }

  initializeProtectionServices() {
    this.protectionSettings = {
      autoWatermark: true,
      copyrightMonitoring: true,
      dmcaProtection: true,
      realTimeAlerts: true,
      aiDetection: true,
      blockchainRegistry: false
    };

    this.loadProtectedAssets();
    this.updateMetrics();
  }

  async startRealTimeMonitoring() {
    if (this.monitoringActive) return;

    try {
      this.monitoringActive = true;
      this.updateProtectionStatus();

      // Start monitoring intervals
      this.violationCheckInterval = setInterval(() => {
        this.checkForViolations();
      }, 30000); // Check every 30 seconds

      this.assetScanInterval = setInterval(() => {
        this.scanProtectedAssets();
      }, 300000); // Scan every 5 minutes

      console.log('Real-time protection monitoring started');
    } catch (error) {
      console.error('Failed to start protection monitoring:', error);
      this.monitoringActive = false;
      this.updateProtectionStatus();
    }
  }

  async loadProtectedAssets() {
    try {
      // Load from secure storage
      const assets = await this.securityManager.getProtectedAssets();
      assets.forEach(asset => {
        this.protectedAssets.set(asset.id, asset);
      });

      this.updateAssetsTable();
      this.updateMetrics();
    } catch (error) {
      console.error('Failed to load protected assets:', error);
    }
  }

  async scanAllContent() {
    try {
      this.showProgress('Scanning content for protection opportunities...');

      // Get all user content
      const content = await window.electronAPI?.getAllUserContent?.() || [];
      
      for (const item of content) {
        if (!this.protectedAssets.has(item.id)) {
          await this.protectAsset(item);
        }
      }

      this.hideProgress();
      this.updateAssetsTable();
      this.updateMetrics();
      
      this.showSuccess('Content scan completed');
    } catch (error) {
      this.hideProgress();
      console.error('Content scan failed:', error);
      this.showError('Failed to scan content: ' + error.message);
    }
  }

  async protectAsset(asset) {
    try {
      const protectionLevel = this.determineProtectionLevel(asset);
      
      const protectedAsset = {
        id: asset.id,
        name: asset.name,
        type: asset.type,
        protectionLevel,
        status: 'protected',
        createdAt: new Date(),
        lastScan: new Date(),
        violations: [],
        fingerprint: await this.generateFingerprint(asset),
        watermark: this.protectionSettings.autoWatermark ? await this.addWatermark(asset) : null,
        registrations: []
      };

      // Register with copyright engine
      if (this.protectionSettings.copyrightMonitoring) {
        const registration = await this.copyrightEngine.registerAsset(protectedAsset);
        protectedAsset.registrations.push(registration);
      }

      // Store in secure storage
      await this.securityManager.storeProtectedAsset(protectedAsset);
      
      this.protectedAssets.set(asset.id, protectedAsset);
      
      return protectedAsset;
    } catch (error) {
      console.error('Failed to protect asset:', error);
      throw error;
    }
  }

  async checkForViolations() {
    if (!this.protectionSettings.copyrightMonitoring) return;

    try {
      for (const [assetId, asset] of this.protectedAssets) {
        if (asset.status === 'protected') {
          const violations = await this.copyrightEngine.scanForViolations(asset);
          
          if (violations.length > 0) {
            this.handleNewViolations(asset, violations);
          }
        }
      }
    } catch (error) {
      console.error('Violation check failed:', error);
    }
  }

  handleNewViolations(asset, violations) {
    violations.forEach(violation => {
      const violationRecord = {
        id: `violation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        assetId: asset.id,
        assetName: asset.name,
        type: violation.type,
        severity: violation.severity,
        platform: violation.platform,
        url: violation.url,
        detectedAt: new Date(),
        status: 'new',
        evidence: violation.evidence
      };

      this.violations.unshift(violationRecord);
      asset.violations.push(violationRecord.id);

      // Real-time alerts
      if (this.protectionSettings.realTimeAlerts) {
        this.showViolationAlert(violationRecord);
      }

      // Auto DMCA if enabled
      if (this.protectionSettings.dmcaProtection && violation.severity === 'high') {
        this.initiateDMCATakedown(violationRecord);
      }
    });

    this.updateViolationsList();
    this.updateMetrics();
  }

  async initiateDMCATakedown(violation) {
    try {
      const takedownRequest = {
        violationId: violation.id,
        platform: violation.platform,
        url: violation.url,
        type: 'dmca',
        status: 'pending',
        initiatedAt: new Date()
      };

      // Submit DMCA request
      const result = await this.copyrightEngine.submitDMCA(takedownRequest);
      
      violation.dmcaRequest = result;
      violation.status = 'dmca_pending';

      this.updateViolationsList();
      this.showInfo(`DMCA takedown initiated for ${violation.platform}`);
    } catch (error) {
      console.error('DMCA initiation failed:', error);
      this.showError('Failed to initiate DMCA takedown');
    }
  }

  updateAssetsTable() {
    const tableBody = this.container.querySelector('#assetsTableBody');
    
    if (this.protectedAssets.size === 0) {
      tableBody.innerHTML = `
        <tr class="no-data">
          <td colspan="7">
            <div class="no-data-message">
              <i class="fas fa-shield-alt"></i>
              <p>No protected assets found</p>
              <button class="btn-link" onclick="this.closest('.protection-dashboard').querySelector('#scanAllContent').click()">
                Start protecting your content
              </button>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    const rows = Array.from(this.protectedAssets.values()).map(asset => `
      <tr class="asset-row" data-asset-id="${asset.id}">
        <td>
          <div class="asset-info">
            <div class="asset-icon">
              <i class="fas ${this.getAssetIcon(asset.type)}"></i>
            </div>
            <div class="asset-details">
              <span class="asset-name">${asset.name}</span>
              <span class="asset-id">${asset.id}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="asset-type ${asset.type}">${asset.type}</span>
        </td>
        <td>
          <span class="protection-level ${asset.protectionLevel}">${asset.protectionLevel}</span>
        </td>
        <td>
          <span class="asset-status ${asset.status}">
            <i class="fas ${this.getStatusIcon(asset.status)}"></i>
            ${asset.status}
          </span>
        </td>
        <td>
          <span class="violations-count ${asset.violations.length > 0 ? 'has-violations' : ''}">
            ${asset.violations.length}
          </span>
        </td>
        <td>
          <span class="last-scan">${this.formatDate(asset.lastScan)}</span>
        </td>
        <td>
          <div class="asset-actions">
            <button class="btn-small" onclick="window.protectionDashboard.viewAsset('${asset.id}')" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn-small" onclick="window.protectionDashboard.scanAsset('${asset.id}')" title="Rescan">
              <i class="fas fa-sync-alt"></i>
            </button>
            <button class="btn-small danger" onclick="window.protectionDashboard.removeProtection('${asset.id}')" title="Remove Protection">
              <i class="fas fa-shield-alt"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    tableBody.innerHTML = rows;
  }

  updateViolationsList() {
    const violationsList = this.container.querySelector('#violationsList');
    
    if (this.violations.length === 0) {
      violationsList.innerHTML = `
        <div class="no-violations">
          <i class="fas fa-check-circle"></i>
          <p>No violations detected</p>
        </div>
      `;
      return;
    }

    const recentViolations = this.violations.slice(0, 10);
    
    violationsList.innerHTML = recentViolations.map(violation => `
      <div class="violation-item ${violation.status}">
        <div class="violation-header">
          <div class="violation-info">
            <span class="violation-type ${violation.severity}">${violation.type}</span>
            <span class="violation-platform">${violation.platform}</span>
          </div>
          <div class="violation-time">${this.formatTimeAgo(violation.detectedAt)}</div>
        </div>
        <div class="violation-details">
          <p class="violation-asset">${violation.assetName}</p>
          <p class="violation-url">
            <a href="${violation.url}" target="_blank" title="View violation">
              ${this.truncateUrl(violation.url)}
            </a>
          </p>
        </div>
        <div class="violation-actions">
          <button class="btn-small" onclick="window.protectionDashboard.viewViolation('${violation.id}')">
            <i class="fas fa-eye"></i>
            View
          </button>
          <button class="btn-small primary" onclick="window.protectionDashboard.initiateDMCA('${violation.id}')">
            <i class="fas fa-gavel"></i>
            DMCA
          </button>
          <button class="btn-small secondary" onclick="window.protectionDashboard.markResolved('${violation.id}')">
            <i class="fas fa-check"></i>
            Resolve
          </button>
        </div>
      </div>
    `).join('');
  }

  updateMetrics() {
    this.container.querySelector('#protectedAssetsCount').textContent = this.protectedAssets.size;
    this.container.querySelector('#violationsCount').textContent = this.violations.length;
    
    const takedowns = this.violations.filter(v => v.dmcaRequest).length;
    this.container.querySelector('#takedownsCount').textContent = takedowns;
    
    // Calculate protected revenue (mock calculation)
    const protectedRevenue = this.protectedAssets.size * 1000;
    this.container.querySelector('#protectedRevenue').textContent = `$${protectedRevenue.toLocaleString()}`;
  }

  updateProtectionStatus() {
    const statusIndicator = this.container.querySelector('.status-indicator');
    const statusText = statusIndicator.querySelector('span');
    
    statusIndicator.className = `status-indicator ${this.monitoringActive ? 'active' : 'inactive'}`;
    statusText.textContent = `Real-time Protection ${this.monitoringActive ? 'Active' : 'Inactive'}`;
  }

  // Helper methods
  determineProtectionLevel(asset) {
    // Simple logic - can be enhanced
    if (asset.type === 'video') return 'premium';
    if (asset.type === 'audio') return 'standard';
    return 'basic';
  }

  async generateFingerprint(asset) {
    // Generate unique fingerprint for asset
    const data = `${asset.id}${asset.name}${asset.type}${Date.now()}`;
    return btoa(data).substring(0, 16);
  }

  async addWatermark(asset) {
    // Mock watermark addition
    return {
      type: 'digital',
      strength: 'medium',
      addedAt: new Date()
    };
  }

  getAssetIcon(type) {
    const icons = {
      video: 'fa-video',
      audio: 'fa-music',
      image: 'fa-image',
      text: 'fa-file-alt'
    };
    return icons[type] || 'fa-file';
  }

  getStatusIcon(status) {
    const icons = {
      protected: 'fa-shield-alt',
      scanning: 'fa-sync-alt fa-spin',
      violation: 'fa-exclamation-triangle',
      error: 'fa-times-circle'
    };
    return icons[status] || 'fa-question';
  }

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

  truncateUrl(url) {
    return url.length > 50 ? url.substring(0, 47) + '...' : url;
  }

  // Modal methods
  showModal(title, content) {
    const modal = this.container.querySelector('#protectionModal');
    const titleElement = modal.querySelector('#modalTitle');
    const bodyElement = modal.querySelector('#modalBody');
    
    titleElement.textContent = title;
    bodyElement.innerHTML = content;
    modal.style.display = 'flex';
  }

  hideModal() {
    this.container.querySelector('#protectionModal').style.display = 'none';
  }

  // Notification methods
  showSuccess(message) {
    this.showNotification('success', message);
  }

  showError(message) {
    this.showNotification('error', message);
  }

  showInfo(message) {
    this.showNotification('info', message);
  }

  showNotification(type, message) {
    if (window.electronAPI?.showNotification) {
      window.electronAPI.showNotification(type, message);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  addStyles() {
    const styles = `
      <style>
        .protection-dashboard {
          background: #1a1a1a;
          color: #fff;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          border-radius: 8px;
          overflow: hidden;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
          border-bottom: 1px solid #333;
        }

        .dashboard-header h3 {
          margin: 0;
          color: #fff;
          font-size: 16px;
          font-weight: 600;
        }

        .protection-status {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
        }

        .status-light {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #666;
          animation: pulse 2s infinite;
        }

        .status-indicator.active .status-light {
          background: #4caf50;
        }

        .dashboard-content {
          padding: 20px;
        }

        .metric-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .metric-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          background: #252526;
          border-radius: 8px;
          border-left: 4px solid #666;
        }

        .metric-card.assets { border-left-color: #2196f3; }
        .metric-card.violations { border-left-color: #ff9800; }
        .metric-card.takedowns { border-left-color: #f44336; }
        .metric-card.revenue { border-left-color: #4caf50; }

        .metric-icon {
          font-size: 24px;
          color: #ccc;
        }

        .metric-value {
          font-size: 24px;
          font-weight: bold;
          color: #fff;
        }

        .metric-label {
          font-size: 12px;
          color: #999;
        }

        .control-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }

        .control-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          font-size: 14px;
        }

        .toggle-slider {
          width: 40px;
          height: 20px;
          background: #444;
          border-radius: 20px;
          position: relative;
          transition: all 0.3s ease;
        }

        .toggle-slider::before {
          content: '';
          position: absolute;
          width: 16px;
          height: 16px;
          background: #fff;
          border-radius: 50%;
          top: 2px;
          left: 2px;
          transition: all 0.3s ease;
        }

        .control-toggle input:checked + .toggle-slider {
          background: #d32f2f;
        }

        .control-toggle input:checked + .toggle-slider::before {
          transform: translateX(20px);
        }

        .assets-table {
          width: 100%;
          border-collapse: collapse;
          background: #252526;
          border-radius: 8px;
          overflow: hidden;
        }

        .assets-table th,
        .assets-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #333;
        }

        .assets-table th {
          background: #333;
          font-weight: 600;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .violation-item {
          background: #252526;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 8px;
          border-left: 4px solid #ff9800;
        }

        .violation-item.resolved {
          border-left-color: #4caf50;
          opacity: 0.7;
        }

        .btn-primary, .btn-secondary, .btn-danger, .btn-small {
          padding: 6px 12px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.3s ease;
        }

        .btn-primary { background: #d32f2f; color: #fff; }
        .btn-secondary { background: #666; color: #fff; }
        .btn-danger { background: #f44336; color: #fff; }
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

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;
    
    if (!document.querySelector('#protection-dashboard-styles')) {
      const styleElement = document.createElement('div');
      styleElement.id = 'protection-dashboard-styles';
      styleElement.innerHTML = styles;
      document.head.appendChild(styleElement);
    }
  }

  // Public API methods
  async activateEmergencyProtection() {
    try {
      // Implement emergency protection measures
      this.showInfo('Emergency protection activated');
    } catch (error) {
      this.showError('Failed to activate emergency protection');
    }
  }

  async generateProtectionReport() {
    try {
      const report = {
        timestamp: new Date().toISOString(),
        protectedAssets: this.protectedAssets.size,
        violations: this.violations.length,
        assets: Array.from(this.protectedAssets.values()),
        recentViolations: this.violations.slice(0, 50)
      };

      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `protection_report_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);

      this.showSuccess('Protection report generated');
    } catch (error) {
      this.showError('Failed to generate report');
    }
  }

  destroy() {
    if (this.violationCheckInterval) {
      clearInterval(this.violationCheckInterval);
    }
    if (this.assetScanInterval) {
      clearInterval(this.assetScanInterval);
    }
    this.container.innerHTML = '';
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProtectionDashboard;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.ProtectionDashboard = ProtectionDashboard;
  window.protectionDashboard = null; // Will be set when instantiated
}