/**
 * Ainflue Desktop Renderer - Notification System
 * Advanced notification and alert system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class NotificationSystem {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.notifications = new Map();
        this.container = null;
        this.config = {
            position: 'top-right',
            maxNotifications: 5,
            defaultDuration: 5000,
            animationDuration: 300,
            stackSpacing: 10
        };
        
        this.init();
    }

    /**
     * Initialize notification system
     */
    init() {
        console.log('🔔 Initializing Notification System v' + this.version);
        
        this.createContainer();
        this.setupStyles();
        this.setupEventHandlers();
    }

    /**
     * Create notification container
     */
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = `notifications notifications--${this.config.position}`;
        
        document.body.appendChild(this.container);
    }

    /**
     * Show notification
     */
    show(message, options = {}) {
        const {
            type = 'info',
            title = null,
            duration = this.config.defaultDuration,
            persistent = false,
            actions = [],
            icon = null,
            image = null,
            progress = false,
            sound = false
        } = options;

        const id = this.generateId();
        
        const notification = {
            id,
            message,
            type,
            title,
            duration,
            persistent,
            actions,
            icon,
            image,
            progress,
            sound,
            timestamp: Date.now(),
            element: null
        };

        // Create notification element
        notification.element = this.createNotificationElement(notification);
        
        // Add to container
        this.addToContainer(notification);
        
        // Store notification
        this.notifications.set(id, notification);
        
        // Auto-remove if not persistent
        if (!persistent && duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }

        // Play sound if requested
        if (sound) {
            this.playNotificationSound(type);
        }

        this.emit('notification-shown', notification);
        
        return id;
    }

    /**
     * Create notification element
     */
    createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `notification notification--${notification.type}`;
        element.setAttribute('data-id', notification.id);

        // Build notification content
        let content = '';
        
        // Icon
        if (notification.icon || this.getDefaultIcon(notification.type)) {
            const icon = notification.icon || this.getDefaultIcon(notification.type);
            content += `<div class="notification__icon">${icon}</div>`;
        }

        // Main content area
        content += '<div class="notification__content">';
        
        // Title
        if (notification.title) {
            content += `<div class="notification__title">${notification.title}</div>`;
        }
        
        // Message
        content += `<div class="notification__message">${notification.message}</div>`;
        
        // Progress bar
        if (notification.progress) {
            content += '<div class="notification__progress"><div class="progress-bar"></div></div>';
        }
        
        // Actions
        if (notification.actions.length > 0) {
            content += '<div class="notification__actions">';
            notification.actions.forEach(action => {
                content += `<button class="notification__action" data-action="${action.id}">${action.label}</button>`;
            });
            content += '</div>';
        }
        
        content += '</div>';
        
        // Image
        if (notification.image) {
            content += `<div class="notification__image"><img src="${notification.image}" alt="Notification" /></div>`;
        }
        
        // Close button
        if (!notification.persistent || notification.actions.length === 0) {
            content += '<button class="notification__close" title="Close">×</button>';
        }

        element.innerHTML = content;
        
        // Setup event listeners
        this.setupNotificationEvents(element, notification);
        
        return element;
    }

    /**
     * Setup notification event listeners
     */
    setupNotificationEvents(element, notification) {
        // Close button
        const closeBtn = element.querySelector('.notification__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.remove(notification.id);
            });
        }

        // Action buttons
        const actionBtns = element.querySelectorAll('.notification__action');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const actionId = e.target.getAttribute('data-action');
                const action = notification.actions.find(a => a.id === actionId);
                
                if (action && action.callback) {
                    action.callback(notification);
                }
                
                // Remove notification unless action specifies otherwise
                if (!action.keepOpen) {
                    this.remove(notification.id);
                }
            });
        });

        // Click to dismiss (if not persistent)
        if (!notification.persistent && notification.actions.length === 0) {
            element.addEventListener('click', () => {
                this.remove(notification.id);
            });
        }

        // Hover to pause auto-remove
        if (!notification.persistent && notification.duration > 0) {
            let timeoutId = null;
            
            element.addEventListener('mouseenter', () => {
                element.classList.add('notification--paused');
            });
            
            element.addEventListener('mouseleave', () => {
                element.classList.remove('notification--paused');
            });
        }
    }

    /**
     * Add notification to container
     */
    addToContainer(notification) {
        // Check if we need to remove old notifications
        if (this.notifications.size >= this.config.maxNotifications) {
            const oldestId = Array.from(this.notifications.keys())[0];
            this.remove(oldestId);
        }

        // Add with animation
        notification.element.style.transform = this.getInitialTransform();
        notification.element.style.opacity = '0';
        
        this.container.appendChild(notification.element);
        
        // Trigger animation
        requestAnimationFrame(() => {
            notification.element.style.transform = 'translateX(0)';
            notification.element.style.opacity = '1';
        });
    }

    /**
     * Remove notification
     */
    remove(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;

        // Animate out
        notification.element.style.transform = this.getExitTransform();
        notification.element.style.opacity = '0';

        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
            this.notifications.delete(id);
            
            this.emit('notification-removed', notification);
        }, this.config.animationDuration);
    }

    /**
     * Update notification progress
     */
    updateProgress(id, progress) {
        const notification = this.notifications.get(id);
        if (!notification || !notification.progress) return;

        const progressBar = notification.element.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = Math.max(0, Math.min(100, progress)) + '%';
        }
    }

    /**
     * Show success notification
     */
    success(message, options = {}) {
        return this.show(message, { ...options, type: 'success' });
    }

    /**
     * Show error notification
     */
    error(message, options = {}) {
        return this.show(message, { ...options, type: 'error', persistent: options.persistent !== false });
    }

    /**
     * Show warning notification
     */
    warning(message, options = {}) {
        return this.show(message, { ...options, type: 'warning' });
    }

    /**
     * Show info notification
     */
    info(message, options = {}) {
        return this.show(message, { ...options, type: 'info' });
    }

    /**
     * Show loading notification
     */
    loading(message, options = {}) {
        return this.show(message, { 
            ...options, 
            type: 'loading', 
            persistent: true,
            progress: true,
            icon: '<div class="spinner"></div>'
        });
    }

    /**
     * Clear all notifications
     */
    clear() {
        Array.from(this.notifications.keys()).forEach(id => {
            this.remove(id);
        });
    }

    /**
     * Get default icon for notification type
     */
    getDefaultIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            loading: '<div class="spinner"></div>'
        };
        
        return icons[type] || icons.info;
    }

    /**
     * Get initial transform for animation
     */
    getInitialTransform() {
        const position = this.config.position;
        
        if (position.includes('right')) {
            return 'translateX(100%)';
        } else if (position.includes('left')) {
            return 'translateX(-100%)';
        } else if (position.includes('top')) {
            return 'translateY(-100%)';
        } else {
            return 'translateY(100%)';
        }
    }

    /**
     * Get exit transform for animation
     */
    getExitTransform() {
        return this.getInitialTransform();
    }

    /**
     * Play notification sound
     */
    playNotificationSound(type) {
        if (!('AudioContext' in window)) return;

        const audioContext = new AudioContext();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        // Different frequencies for different types
        const frequencies = {
            success: 800,
            error: 400,
            warning: 600,
            info: 500
        };

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(frequencies[type] || frequencies.info, audioContext.currentTime);
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('notification-system-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-system-styles';
        styles.textContent = `
            /* Notification System Styles */
            .notifications {
                position: fixed;
                z-index: 10000;
                pointer-events: none;
                display: flex;
                flex-direction: column;
                gap: ${this.config.stackSpacing}px;
                max-width: 400px;
                width: 100%;
            }
            
            .notifications--top-right {
                top: 20px;
                right: 20px;
            }
            
            .notifications--top-left {
                top: 20px;
                left: 20px;
            }
            
            .notifications--bottom-right {
                bottom: 20px;
                right: 20px;
            }
            
            .notifications--bottom-left {
                bottom: 20px;
                left: 20px;
            }
            
            .notifications--top-center {
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
            }
            
            .notifications--bottom-center {
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
            }
            
            .notification {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 16px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                border-left: 4px solid #e5e7eb;
                pointer-events: auto;
                cursor: pointer;
                transition: all ${this.config.animationDuration}ms ease;
                position: relative;
                overflow: hidden;
            }
            
            .notification:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            }
            
            .notification--success {
                border-left-color: #10b981;
                background: #f0fdf4;
            }
            
            .notification--error {
                border-left-color: #ef4444;
                background: #fef2f2;
            }
            
            .notification--warning {
                border-left-color: #f59e0b;
                background: #fffbeb;
            }
            
            .notification--info {
                border-left-color: #3b82f6;
                background: #eff6ff;
            }
            
            .notification--loading {
                border-left-color: #8b5cf6;
                background: #faf5ff;
            }
            
            .notification__icon {
                flex-shrink: 0;
                font-size: 20px;
                line-height: 1;
            }
            
            .notification__content {
                flex: 1;
                min-width: 0;
            }
            
            .notification__title {
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 4px;
                color: #111827;
            }
            
            .notification__message {
                font-size: 13px;
                line-height: 1.4;
                color: #374151;
            }
            
            .notification__progress {
                margin-top: 8px;
                height: 3px;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 2px;
                overflow: hidden;
            }
            
            .progress-bar {
                height: 100%;
                background: currentColor;
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .notification--success .progress-bar {
                background: #10b981;
            }
            
            .notification--error .progress-bar {
                background: #ef4444;
            }
            
            .notification--warning .progress-bar {
                background: #f59e0b;
            }
            
            .notification--info .progress-bar {
                background: #3b82f6;
            }
            
            .notification__actions {
                display: flex;
                gap: 8px;
                margin-top: 8px;
            }
            
            .notification__action {
                padding: 4px 12px;
                border: 1px solid currentColor;
                background: transparent;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .notification__action:hover {
                background: currentColor;
                color: white;
            }
            
            .notification__close {
                position: absolute;
                top: 8px;
                right: 8px;
                width: 20px;
                height: 20px;
                border: none;
                background: transparent;
                color: #6b7280;
                cursor: pointer;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                line-height: 1;
                transition: all 0.2s;
            }
            
            .notification__close:hover {
                background: rgba(0, 0, 0, 0.1);
                color: #374151;
            }
            
            .notification__image {
                flex-shrink: 0;
                width: 40px;
                height: 40px;
                border-radius: 6px;
                overflow: hidden;
            }
            
            .notification__image img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .spinner {
                width: 16px;
                height: 16px;
                border: 2px solid transparent;
                border-top: 2px solid currentColor;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .notification--paused {
                animation-play-state: paused;
            }
            
            @media (max-width: 480px) {
                .notifications {
                    left: 10px !important;
                    right: 10px !important;
                    max-width: none;
                    transform: none !important;
                }
                
                .notification {
                    margin: 0;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close all notifications
            if (e.key === 'Escape') {
                this.clear();
            }
        });

        // Handle visibility change (pause notifications when tab is hidden)
        document.addEventListener('visibilitychange', () => {
            const isHidden = document.hidden;
            this.container.classList.toggle('notifications--hidden', isHidden);
        });
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'notification-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Get notification count
     */
    getCount() {
        return this.notifications.size;
    }

    /**
     * Get all notifications
     */
    getAll() {
        return Array.from(this.notifications.values());
    }

    /**
     * Update configuration
     */
    configure(newConfig) {
        this.config = { ...this.config, ...newConfig };
        
        // Update container position if changed
        if (newConfig.position) {
            this.container.className = `notifications notifications--${this.config.position}`;
        }
    }

    /**
     * Destroy notification system
     */
    destroy() {
        this.clear();
        
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        // Remove styles
        const styles = document.getElementById('notification-system-styles');
        if (styles) styles.remove();
        
        console.log('🔔 Notification System destroyed');
    }
}

// Export for ES6 modules
export default NotificationSystem;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.NotificationSystem = NotificationSystem;
}