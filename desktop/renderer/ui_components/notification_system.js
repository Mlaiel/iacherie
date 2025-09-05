/**
 * Ainflue Desktop - Notification System
 * Système notifications avancé
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class NotificationSystem {
    constructor() {
        this.notifications = new Map();
        this.queue = [];
        this.maxVisible = 5;
        this.defaultDuration = 5000;
        
        this.createContainer();
        this.setupEventListeners();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }

    setupEventListeners() {
        // Listen for system notifications
        document.addEventListener('professionalControl', (event) => {
            const { type, data } = event.detail;
            this.handleControlNotification(type, data);
        });
    }

    show(message, type = 'info', options = {}) {
        const notification = {
            id: Date.now() + Math.random(),
            message,
            type,
            duration: options.duration || this.defaultDuration,
            persistent: options.persistent || false,
            actions: options.actions || []
        };

        this.queue.push(notification);
        this.processQueue();
        
        return notification.id;
    }

    processQueue() {
        const visibleCount = this.container.children.length;
        
        if (visibleCount < this.maxVisible && this.queue.length > 0) {
            const notification = this.queue.shift();
            this.renderNotification(notification);
        }
    }

    renderNotification(notification) {
        const element = document.createElement('div');
        element.className = `notification notification-${notification.type}`;
        element.style.cssText = `
            background: ${this.getTypeColor(notification.type)};
            color: white;
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            max-width: 400px;
            pointer-events: auto;
            animation: slideIn 0.3s ease-out;
            display: flex;
            align-items: center;
            gap: 10px;
        `;

        element.innerHTML = `
            <span class="notification-icon">${this.getTypeIcon(notification.type)}</span>
            <span class="notification-message">${notification.message}</span>
            <button class="notification-close" style="
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                margin-left: auto;
                font-size: 16px;
            ">×</button>
        `;

        // Setup close button
        element.querySelector('.notification-close').addEventListener('click', () => {
            this.remove(notification.id);
        });

        this.container.appendChild(element);
        this.notifications.set(notification.id, { ...notification, element });

        // Auto-remove if not persistent
        if (!notification.persistent) {
            setTimeout(() => {
                this.remove(notification.id);
            }, notification.duration);
        }

        // Process next in queue
        setTimeout(() => this.processQueue(), 100);
    }

    getTypeColor(type) {
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6',
            processing: '#8B5CF6'
        };
        return colors[type] || colors.info;
    }

    getTypeIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            processing: '⏳'
        };
        return icons[type] || icons.info;
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (notification && notification.element) {
            notification.element.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.element.parentNode) {
                    notification.element.parentNode.removeChild(notification.element);
                }
                this.notifications.delete(id);
                this.processQueue();
            }, 300);
        }
    }

    handleControlNotification(type, data) {
        switch (type) {
            case 'projectSaved':
                this.show('Project saved successfully', 'success');
                break;
            case 'play':
                this.show('Playback started', 'info', { duration: 2000 });
                break;
            case 'startRecording':
                this.show('Recording started', 'processing', { persistent: true });
                break;
            case 'stopRecording':
                this.show('Recording stopped', 'success');
                break;
            default:
                break;
        }
    }

    // Professional notification methods
    showProcessing(message, id = null) {
        return this.show(message, 'processing', { persistent: true, id });
    }

    showSuccess(message) {
        return this.show(message, 'success');
    }

    showError(message) {
        return this.show(message, 'error', { duration: 8000 });
    }

    showWarning(message) {
        return this.show(message, 'warning', { duration: 6000 });
    }

    clear() {
        this.notifications.forEach((notification, id) => {
            this.remove(id);
        });
        this.queue = [];
    }
}

// Add required CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

export default NotificationSystem;