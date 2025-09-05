/**
 * Ainflue Desktop - Status Indicators
 * Indicateurs statut temps réel
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class StatusIndicators {
    constructor() {
        this.indicators = new Map();
        this.statusBar = null;
        this.systemInfo = null;
        this.projectStatus = null;
        
        this.createStatusBar();
        this.initializeIndicators();
        this.startSystemMonitoring();
    }

    createStatusBar() {
        let statusBar = document.querySelector('.status-bar');
        if (!statusBar) {
            statusBar = document.createElement('div');
            statusBar.className = 'status-bar';
            statusBar.style.cssText = `
                height: 30px;
                background: rgba(17, 24, 39, 0.9);
                border-top: 1px solid rgba(75, 85, 99, 0.3);
                display: flex;
                align-items: center;
                padding: 0 20px;
                font-size: 0.8rem;
                color: #9CA3AF;
                justify-content: space-between;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                z-index: 1000;
            `;
            
            document.body.appendChild(statusBar);
        }

        this.statusBar = statusBar;
        this.renderStatusBar();
    }

    renderStatusBar() {
        this.statusBar.innerHTML = `
            <div class="status-left" style="display: flex; align-items: center; gap: 15px;">
                <span id="app-status">Ready</span>
                <span id="project-status">No project</span>
                <span id="processing-status" style="display: none;">
                    <span class="status-spinner" style="
                        display: inline-block;
                        width: 10px;
                        height: 10px;
                        border: 1px solid transparent;
                        border-top: 1px solid #3B82F6;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin-right: 6px;
                    "></span>
                    <span id="processing-text">Processing...</span>
                </span>
            </div>

            <div class="status-center" style="display: flex; align-items: center; gap: 15px;">
                <span id="timeline-position">00:00:00</span>
                <span id="selection-info" style="display: none;"></span>
                <span id="zoom-level">100%</span>
            </div>

            <div class="status-right" style="display: flex; align-items: center; gap: 15px;">
                <span id="display-info">1 Display</span>
                <span id="workspace-info">Single Monitor</span>
                <span id="memory-usage"></span>
                <span id="cpu-usage"></span>
                <span class="copyright">© 2025 Fahed Mlaiel</span>
            </div>
        `;

        this.bindStatusElements();
    }

    bindStatusElements() {
        this.indicators.set('app', document.getElementById('app-status'));
        this.indicators.set('project', document.getElementById('project-status'));
        this.indicators.set('processing', document.getElementById('processing-status'));
        this.indicators.set('processingText', document.getElementById('processing-text'));
        this.indicators.set('timeline', document.getElementById('timeline-position'));
        this.indicators.set('selection', document.getElementById('selection-info'));
        this.indicators.set('zoom', document.getElementById('zoom-level'));
        this.indicators.set('display', document.getElementById('display-info'));
        this.indicators.set('workspace', document.getElementById('workspace-info'));
        this.indicators.set('memory', document.getElementById('memory-usage'));
        this.indicators.set('cpu', document.getElementById('cpu-usage'));
    }

    initializeIndicators() {
        this.updateAppStatus('Ready', 'success');
        this.updateProjectStatus('No project loaded');
        this.updateTimelinePosition('00:00:00');
        this.updateZoomLevel(100);
    }

    startSystemMonitoring() {
        // Update system info every 5 seconds
        setInterval(() => {
            this.updateSystemInfo();
        }, 5000);

        // Initial update
        this.updateSystemInfo();
    }

    async updateSystemInfo() {
        try {
            if (window.electronAPI) {
                const systemInfo = await window.electronAPI.invoke('get-system-info');
                this.updateMemoryUsage(systemInfo);
                this.updateCPUUsage(systemInfo);
            }
        } catch (error) {
            console.warn('Could not fetch system info:', error);
        }
    }

    updateAppStatus(status, type = 'info') {
        const indicator = this.indicators.get('app');
        if (indicator) {
            indicator.textContent = status;
            indicator.className = `status-${type}`;
            
            // Apply color based on type
            const colors = {
                success: '#10B981',
                error: '#EF4444',
                warning: '#F59E0B',
                info: '#9CA3AF',
                processing: '#8B5CF6'
            };
            indicator.style.color = colors[type] || colors.info;
        }
    }

    updateProjectStatus(projectName, details = '') {
        const indicator = this.indicators.get('project');
        if (indicator) {
            indicator.textContent = projectName ? `Project: ${projectName}` : 'No project';
            if (details) {
                indicator.title = details;
            }
        }
    }

    showProcessing(message = 'Processing...') {
        const processingIndicator = this.indicators.get('processing');
        const processingText = this.indicators.get('processingText');
        
        if (processingIndicator && processingText) {
            processingText.textContent = message;
            processingIndicator.style.display = 'flex';
            processingIndicator.style.alignItems = 'center';
        }
    }

    hideProcessing() {
        const processingIndicator = this.indicators.get('processing');
        if (processingIndicator) {
            processingIndicator.style.display = 'none';
        }
    }

    updateTimelinePosition(time) {
        const indicator = this.indicators.get('timeline');
        if (indicator) {
            indicator.textContent = time;
        }
    }

    updateSelectionInfo(info) {
        const indicator = this.indicators.get('selection');
        if (indicator) {
            if (info) {
                indicator.textContent = info;
                indicator.style.display = 'inline';
            } else {
                indicator.style.display = 'none';
            }
        }
    }

    updateZoomLevel(level) {
        const indicator = this.indicators.get('zoom');
        if (indicator) {
            indicator.textContent = `${level}%`;
        }
    }

    updateDisplayInfo(displayCount, workspaceType) {
        const displayIndicator = this.indicators.get('display');
        const workspaceIndicator = this.indicators.get('workspace');
        
        if (displayIndicator) {
            displayIndicator.textContent = `${displayCount} Display${displayCount > 1 ? 's' : ''}`;
        }
        
        if (workspaceIndicator && workspaceType) {
            workspaceIndicator.textContent = workspaceType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
    }

    updateMemoryUsage(systemInfo) {
        const indicator = this.indicators.get('memory');
        if (indicator && systemInfo) {
            const usedMemory = systemInfo.totalMemory - systemInfo.freeMemory;
            const usagePercent = Math.round((usedMemory / systemInfo.totalMemory) * 100);
            const usedGB = (usedMemory / (1024 * 1024 * 1024)).toFixed(1);
            const totalGB = (systemInfo.totalMemory / (1024 * 1024 * 1024)).toFixed(1);
            
            indicator.textContent = `RAM: ${usedGB}/${totalGB}GB (${usagePercent}%)`;
            
            // Color based on usage
            if (usagePercent > 80) {
                indicator.style.color = '#EF4444'; // Red
            } else if (usagePercent > 60) {
                indicator.style.color = '#F59E0B'; // Yellow
            } else {
                indicator.style.color = '#10B981'; // Green
            }
        }
    }

    updateCPUUsage(systemInfo) {
        const indicator = this.indicators.get('cpu');
        if (indicator && systemInfo && systemInfo.loadAverage) {
            const cpuUsage = Math.round(systemInfo.loadAverage[0] * 100 / systemInfo.cpuCount);
            indicator.textContent = `CPU: ${Math.min(100, cpuUsage)}%`;
            
            // Color based on usage
            if (cpuUsage > 80) {
                indicator.style.color = '#EF4444'; // Red
            } else if (cpuUsage > 60) {
                indicator.style.color = '#F59E0B'; // Yellow
            } else {
                indicator.style.color = '#10B981'; // Green
            }
        }
    }

    // Professional status methods for different creator workflows
    
    // For Musicians
    updateAudioStatus(sampleRate, bitDepth, channels) {
        this.updateAppStatus(`Audio: ${sampleRate}Hz/${bitDepth}bit/${channels}ch`, 'info');
    }

    // For Video Creators
    updateVideoStatus(resolution, fps, codec) {
        this.updateAppStatus(`Video: ${resolution} @ ${fps}fps (${codec})`, 'info');
    }

    // For Photographers
    updateImageStatus(dimensions, format, colorSpace) {
        this.updateAppStatus(`Image: ${dimensions} ${format} ${colorSpace}`, 'info');
    }

    // For Content Protection
    updateProtectionStatus(active, level) {
        const status = active ? `Protection: ${level}` : 'Protection: Off';
        const type = active ? 'success' : 'warning';
        this.updateAppStatus(status, type);
    }

    // For AI Processing
    updateAIStatus(processing, operation) {
        if (processing) {
            this.showProcessing(`AI ${operation}...`);
            this.updateAppStatus('AI Processing', 'processing');
        } else {
            this.hideProcessing();
            this.updateAppStatus('AI Complete', 'success');
        }
    }

    // For Rendering
    updateRenderStatus(progress, eta) {
        if (progress < 100) {
            this.showProcessing(`Rendering ${progress}% (ETA: ${eta})`);
            this.updateAppStatus('Rendering', 'processing');
        } else {
            this.hideProcessing();
            this.updateAppStatus('Render Complete', 'success');
        }
    }

    // For Collaboration
    updateCollaborationStatus(connected, users) {
        const status = connected ? `Collaboration: ${users} user${users > 1 ? 's' : ''}` : 'Offline';
        const type = connected ? 'success' : 'info';
        this.updateAppStatus(status, type);
    }

    // For Monetization
    updateRevenueStatus(earnings, period) {
        this.updateAppStatus(`Revenue: $${earnings} (${period})`, 'success');
    }

    // Error and warning indicators
    showError(message) {
        this.updateAppStatus(`Error: ${message}`, 'error');
        setTimeout(() => {
            this.updateAppStatus('Ready', 'info');
        }, 5000);
    }

    showWarning(message) {
        this.updateAppStatus(`Warning: ${message}`, 'warning');
        setTimeout(() => {
            this.updateAppStatus('Ready', 'info');
        }, 3000);
    }

    showSuccess(message) {
        this.updateAppStatus(message, 'success');
        setTimeout(() => {
            this.updateAppStatus('Ready', 'info');
        }, 2000);
    }

    // Utility methods
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        return [hours, minutes, secs]
            .map(val => val.toString().padStart(2, '0'))
            .join(':');
    }

    formatBytes(bytes) {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let unitIndex = 0;
        let size = bytes;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }

    // Listen to system events
    setupEventListeners() {
        document.addEventListener('professionalControl', (event) => {
            const { type, data } = event.detail;
            this.handleControlEvent(type, data);
        });

        document.addEventListener('dashboardLayout', (event) => {
            const { type, layout } = event.detail;
            if (type === 'layoutChanged') {
                this.updateDisplayInfo(1, layout);
            }
        });
    }

    handleControlEvent(type, data) {
        switch (type) {
            case 'play':
                this.updateAppStatus('Playing', 'processing');
                break;
            case 'pause':
                this.updateAppStatus('Paused', 'warning');
                break;
            case 'stop':
                this.updateAppStatus('Stopped', 'info');
                break;
            case 'startRecording':
                this.updateAppStatus('Recording', 'error');
                break;
            case 'stopRecording':
                this.updateAppStatus('Recording Stopped', 'success');
                break;
            case 'projectSaved':
                this.showSuccess('Project Saved');
                break;
        }
    }
}

export default StatusIndicators;