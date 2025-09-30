/**
 * Ainflue Desktop Renderer - Status Indicators
 * Real-time status indicator components
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class StatusIndicators {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.indicators = new Map();
        this.updateInterval = null;
        
        this.init();
    }

    /**
     * Initialize status indicators
     */
    init() {
        console.log('📊 Initializing Status Indicators v' + this.version);
        
        this.setupStyles();
        this.createStatusBar();
        this.startSystemMonitoring();
    }

    /**
     * Create main status bar
     */
    createStatusBar() {
        const statusBar = document.createElement('div');
        statusBar.id = 'main-status-bar';
        statusBar.className = 'status-bar';
        
        statusBar.innerHTML = `
            <div class="status-section status-left">
                <div class="status-indicator" id="app-status">
                    <span class="status-dot status-success"></span>
                    <span class="status-text">Ready</span>
                </div>
            </div>
            <div class="status-section status-center">
                <div class="status-indicator" id="processing-status" style="display: none;">
                    <span class="status-spinner"></span>
                    <span class="status-text">Processing...</span>
                </div>
            </div>
            <div class="status-section status-right">
                <div class="status-indicator" id="system-status"></div>
                <div class="status-indicator" id="network-status"></div>
                <div class="status-indicator" id="time-status"></div>
            </div>
        `;
        
        document.body.appendChild(statusBar);
        
        // Setup default indicators
        this.setupSystemIndicators();
    }

    /**
     * Setup system indicators
     */
    setupSystemIndicators() {
        // System performance indicator
        this.addIndicator('system-performance', {
            container: 'system-status',
            type: 'performance',
            updateInterval: 2000
        });

        // Network status indicator
        this.addIndicator('network-connection', {
            container: 'network-status',
            type: 'network',
            updateInterval: 5000
        });

        // Time indicator
        this.addIndicator('current-time', {
            container: 'time-status',
            type: 'time',
            updateInterval: 1000
        });
    }

    /**
     * Add status indicator
     */
    addIndicator(id, options = {}) {
        const {
            container = null,
            type = 'generic',
            status = 'unknown',
            text = '',
            icon = null,
            tooltip = '',
            updateInterval = 0,
            onClick = null,
            animated = false
        } = options;

        const indicator = {
            id,
            type,
            status,
            text,
            icon,
            tooltip,
            updateInterval,
            onClick,
            animated,
            element: null,
            timer: null
        };

        // Create indicator element
        indicator.element = this.createIndicatorElement(indicator);
        
        // Add to container
        if (container) {
            const containerElement = document.getElementById(container);
            if (containerElement) {
                containerElement.appendChild(indicator.element);
            }
        } else {
            // Add to main status bar
            const statusBar = document.getElementById('main-status-bar');
            if (statusBar) {
                statusBar.querySelector('.status-right').appendChild(indicator.element);
            }
        }

        // Setup auto-update if specified
        if (updateInterval > 0) {
            indicator.timer = setInterval(() => {
                this.updateIndicator(id);
            }, updateInterval);
        }

        this.indicators.set(id, indicator);
        
        // Initial update
        this.updateIndicator(id);

        return id;
    }

    /**
     * Create indicator element
     */
    createIndicatorElement(indicator) {
        const element = document.createElement('div');
        element.className = 'status-indicator';
        element.setAttribute('data-id', indicator.id);
        element.setAttribute('data-type', indicator.type);
        
        if (indicator.tooltip) {
            element.title = indicator.tooltip;
        }

        // Add click handler
        if (indicator.onClick) {
            element.style.cursor = 'pointer';
            element.addEventListener('click', () => {
                indicator.onClick(indicator);
            });
        }

        return element;
    }

    /**
     * Update indicator content
     */
    updateIndicator(id) {
        const indicator = this.indicators.get(id);
        if (!indicator) return;

        let content = '';
        
        switch (indicator.type) {
            case 'performance':
                content = this.getPerformanceContent();
                break;
            case 'network':
                content = this.getNetworkContent();
                break;
            case 'time':
                content = this.getTimeContent();
                break;
            case 'progress':
                content = this.getProgressContent(indicator);
                break;
            case 'generic':
            default:
                content = this.getGenericContent(indicator);
                break;
        }

        indicator.element.innerHTML = content;
        
        // Update tooltip
        if (indicator.tooltip) {
            indicator.element.title = indicator.tooltip;
        }
    }

    /**
     * Get performance indicator content
     */
    getPerformanceContent() {
        // Simulate system performance data
        const cpuUsage = Math.floor(Math.random() * 30) + 10; // 10-40%
        const memoryUsage = Math.floor(Math.random() * 40) + 30; // 30-70%
        
        let statusClass = 'status-success';
        if (cpuUsage > 70 || memoryUsage > 80) {
            statusClass = 'status-error';
        } else if (cpuUsage > 50 || memoryUsage > 60) {
            statusClass = 'status-warning';
        }

        return `
            <span class="status-dot ${statusClass}"></span>
            <span class="status-text">CPU: ${cpuUsage}% | RAM: ${memoryUsage}%</span>
        `;
    }

    /**
     * Get network indicator content
     */
    getNetworkContent() {
        const isOnline = navigator.onLine;
        const statusClass = isOnline ? 'status-success' : 'status-error';
        const statusText = isOnline ? 'Online' : 'Offline';
        
        return `
            <span class="status-dot ${statusClass}"></span>
            <span class="status-text">${statusText}</span>
        `;
    }

    /**
     * Get time indicator content
     */
    getTimeContent() {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        return `
            <span class="status-icon">🕐</span>
            <span class="status-text">${timeString}</span>
        `;
    }

    /**
     * Get progress indicator content
     */
    getProgressContent(indicator) {
        const { progress = 0, total = 100 } = indicator;
        const percentage = Math.round((progress / total) * 100);
        
        return `
            <div class="progress-indicator">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="progress-text">${percentage}%</span>
            </div>
        `;
    }

    /**
     * Get generic indicator content
     */
    getGenericContent(indicator) {
        let content = '';
        
        // Status dot
        if (indicator.status !== 'none') {
            content += `<span class="status-dot status-${indicator.status}"></span>`;
        }
        
        // Icon
        if (indicator.icon) {
            content += `<span class="status-icon">${indicator.icon}</span>`;
        }
        
        // Text
        if (indicator.text) {
            content += `<span class="status-text">${indicator.text}</span>`;
        }
        
        return content;
    }

    /**
     * Update indicator status
     */
    setStatus(id, status, text = null) {
        const indicator = this.indicators.get(id);
        if (!indicator) return;

        indicator.status = status;
        if (text !== null) {
            indicator.text = text;
        }

        this.updateIndicator(id);
    }

    /**
     * Update indicator text
     */
    setText(id, text) {
        const indicator = this.indicators.get(id);
        if (!indicator) return;

        indicator.text = text;
        this.updateIndicator(id);
    }

    /**
     * Update progress indicator
     */
    setProgress(id, progress, total = 100) {
        const indicator = this.indicators.get(id);
        if (!indicator) return;

        indicator.progress = progress;
        indicator.total = total;
        this.updateIndicator(id);
    }

    /**
     * Show processing indicator
     */
    showProcessing(text = 'Processing...') {
        const processingIndicator = document.getElementById('processing-status');
        if (processingIndicator) {
            processingIndicator.querySelector('.status-text').textContent = text;
            processingIndicator.style.display = 'flex';
        }
    }

    /**
     * Hide processing indicator
     */
    hideProcessing() {
        const processingIndicator = document.getElementById('processing-status');
        if (processingIndicator) {
            processingIndicator.style.display = 'none';
        }
    }

    /**
     * Add toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `status-toast status-toast--${type}`;
        
        toast.innerHTML = `
            <span class="toast-icon">${this.getToastIcon(type)}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">×</button>
        `;

        // Position toast
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '10000';

        document.body.appendChild(toast);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                this.removeToast(toast);
            }, duration);
        }

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('status-toast--visible');
        });

        return toast;
    }

    /**
     * Remove toast
     */
    removeToast(toast) {
        toast.classList.remove('status-toast--visible');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    /**
     * Get toast icon
     */
    getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    /**
     * Start system monitoring
     */
    startSystemMonitoring() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            this.updateIndicator('network-connection');
        });

        window.addEventListener('offline', () => {
            this.updateIndicator('network-connection');
        });

        // Monitor page visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    /**
     * Pause updates when page is hidden
     */
    pauseUpdates() {
        this.indicators.forEach(indicator => {
            if (indicator.timer) {
                clearInterval(indicator.timer);
                indicator.timer = null;
            }
        });
    }

    /**
     * Resume updates when page is visible
     */
    resumeUpdates() {
        this.indicators.forEach(indicator => {
            if (indicator.updateInterval > 0 && !indicator.timer) {
                indicator.timer = setInterval(() => {
                    this.updateIndicator(indicator.id);
                }, indicator.updateInterval);
            }
        });
    }

    /**
     * Remove indicator
     */
    removeIndicator(id) {
        const indicator = this.indicators.get(id);
        if (!indicator) return;

        // Clear timer
        if (indicator.timer) {
            clearInterval(indicator.timer);
        }

        // Remove element
        if (indicator.element && indicator.element.parentNode) {
            indicator.element.parentNode.removeChild(indicator.element);
        }

        this.indicators.delete(id);
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('status-indicators-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'status-indicators-styles';
        styles.textContent = `
            /* Status Indicators Styles */
            .status-bar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                height: 32px;
                background: #f8fafc;
                border-top: 1px solid #e5e7eb;
                padding: 0 16px;
                font-size: 12px;
                color: #6b7280;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                z-index: 50;
            }

            .status-section {
                display: flex;
                align-items: center;
                gap: 16px;
            }

            .status-left {
                flex: 0 0 auto;
            }

            .status-center {
                flex: 1;
                justify-content: center;
            }

            .status-right {
                flex: 0 0 auto;
            }

            .status-indicator {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.2s;
            }

            .status-indicator:hover {
                background: #f3f4f6;
            }

            .status-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                flex-shrink: 0;
            }

            .status-dot.status-success {
                background: #10b981;
            }

            .status-dot.status-warning {
                background: #f59e0b;
            }

            .status-dot.status-error {
                background: #ef4444;
            }

            .status-dot.status-info {
                background: #3b82f6;
            }

            .status-dot.status-unknown {
                background: #6b7280;
            }

            .status-icon {
                font-size: 14px;
                flex-shrink: 0;
            }

            .status-text {
                white-space: nowrap;
                font-weight: 500;
            }

            .status-spinner {
                width: 12px;
                height: 12px;
                border: 2px solid #e5e7eb;
                border-top: 2px solid #3b82f6;
                border-radius: 50%;
                animation: status-spin 1s linear infinite;
                flex-shrink: 0;
            }

            @keyframes status-spin {
                to { transform: rotate(360deg); }
            }

            /* Progress Indicator */
            .progress-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .progress-bar {
                width: 80px;
                height: 4px;
                background: #e5e7eb;
                border-radius: 2px;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                background: #3b82f6;
                transition: width 0.3s ease;
                border-radius: 2px;
            }

            .progress-text {
                font-size: 11px;
                font-weight: 500;
                min-width: 30px;
                text-align: right;
            }

            /* Toast Notifications */
            .status-toast {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                background: white;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                border-left: 4px solid #e5e7eb;
                min-width: 300px;
                max-width: 400px;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }

            .status-toast--visible {
                opacity: 1;
                transform: translateX(0);
            }

            .status-toast--success {
                border-left-color: #10b981;
                background: #f0fdf4;
            }

            .status-toast--error {
                border-left-color: #ef4444;
                background: #fef2f2;
            }

            .status-toast--warning {
                border-left-color: #f59e0b;
                background: #fffbeb;
            }

            .status-toast--info {
                border-left-color: #3b82f6;
                background: #eff6ff;
            }

            .toast-icon {
                font-size: 16px;
                flex-shrink: 0;
            }

            .toast-message {
                flex: 1;
                font-size: 14px;
                color: #374151;
                line-height: 1.4;
            }

            .toast-close {
                background: transparent;
                border: none;
                color: #6b7280;
                cursor: pointer;
                padding: 2px;
                border-radius: 2px;
                font-size: 16px;
                line-height: 1;
                transition: color 0.2s;
            }

            .toast-close:hover {
                color: #374151;
            }

            /* Animated indicators */
            .status-indicator[data-type="processing"] .status-text {
                animation: status-pulse 1.5s ease-in-out infinite;
            }

            @keyframes status-pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.6; }
            }

            /* Responsive */
            @media (max-width: 768px) {
                .status-bar {
                    padding: 0 12px;
                }

                .status-section {
                    gap: 12px;
                }

                .status-text {
                    display: none;
                }

                .status-indicator {
                    padding: 4px;
                }

                .status-toast {
                    min-width: 250px;
                    margin: 0 10px;
                }
            }

            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .status-bar {
                    background: #1f2937;
                    border-color: #374151;
                    color: #d1d5db;
                }

                .status-indicator:hover {
                    background: #374151;
                }

                .status-toast {
                    background: #1f2937;
                    color: #d1d5db;
                }

                .status-toast--success { background: #064e3b; }
                .status-toast--error { background: #7f1d1d; }
                .status-toast--warning { background: #78350f; }
                .status-toast--info { background: #1e3a8a; }

                .toast-message {
                    color: #d1d5db;
                }

                .progress-bar {
                    background: #374151;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Get all indicators
     */
    getIndicators() {
        return Array.from(this.indicators.values());
    }

    /**
     * Clear all indicators
     */
    clearAll() {
        this.indicators.forEach((indicator, id) => {
            this.removeIndicator(id);
        });
    }

    /**
     * Destroy status indicators
     */
    destroy() {
        this.clearAll();
        
        // Remove status bar
        const statusBar = document.getElementById('main-status-bar');
        if (statusBar && statusBar.parentNode) {
            statusBar.parentNode.removeChild(statusBar);
        }
        
        // Remove styles
        const styles = document.getElementById('status-indicators-styles');
        if (styles) styles.remove();
        
        console.log('📊 Status Indicators destroyed');
    }
}

// Export for ES6 modules
export default StatusIndicators;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.StatusIndicators = StatusIndicators;
}