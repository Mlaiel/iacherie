/**
 * Ainflue Desktop - Modal Manager
 * Gestionnaire modales professionnelles
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class ModalManager {
    constructor() {
        this.modals = new Map();
        this.stack = [];
        this.overlay = null;
        
        this.createOverlay();
        this.setupEventListeners();
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            display: none;
            backdrop-filter: blur(4px);
        `;
        document.body.appendChild(this.overlay);
    }

    setupEventListeners() {
        // Close modal on overlay click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.closeTop();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.stack.length > 0) {
                this.closeTop();
            }
        });
    }

    show(content, options = {}) {
        const modal = {
            id: Date.now() + Math.random(),
            content,
            title: options.title || '',
            size: options.size || 'medium',
            closable: options.closable !== false,
            actions: options.actions || [],
            onClose: options.onClose || null
        };

        const element = this.createModalElement(modal);
        this.modals.set(modal.id, { ...modal, element });
        this.stack.push(modal.id);
        
        this.overlay.appendChild(element);
        this.overlay.style.display = 'block';
        
        // Animate in
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 10);

        return modal.id;
    }

    createModalElement(modal) {
        const element = document.createElement('div');
        element.className = `modal modal-${modal.size}`;
        element.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.9);
            background: #1F2937;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            color: white;
            opacity: 0;
            transition: all 0.3s ease;
            max-height: 90vh;
            overflow-y: auto;
            ${this.getSizeStyles(modal.size)}
        `;

        element.innerHTML = `
            ${modal.title ? `
                <div class="modal-header" style="
                    padding: 20px 30px;
                    border-bottom: 1px solid #374151;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <h3 style="margin: 0; font-size: 1.25rem;">${modal.title}</h3>
                    ${modal.closable ? `
                        <button class="modal-close" style="
                            background: none;
                            border: none;
                            color: #9CA3AF;
                            font-size: 24px;
                            cursor: pointer;
                            padding: 0;
                            width: 30px;
                            height: 30px;
                        ">×</button>
                    ` : ''}
                </div>
            ` : ''}
            <div class="modal-content" style="padding: 30px;">
                ${modal.content}
            </div>
            ${modal.actions.length > 0 ? `
                <div class="modal-actions" style="
                    padding: 20px 30px;
                    border-top: 1px solid #374151;
                    display: flex;
                    gap: 10px;
                    justify-content: flex-end;
                ">
                    ${modal.actions.map(action => `
                        <button class="modal-action-btn" data-action="${action.action}" style="
                            padding: 8px 16px;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 14px;
                            ${action.primary ? 
                                'background: #3B82F6; color: white;' : 
                                'background: #374151; color: #D1D5DB;'
                            }
                        ">${action.label}</button>
                    `).join('')}
                </div>
            ` : ''}
        `;

        // Setup event listeners
        if (modal.closable) {
            const closeBtn = element.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.close(modal.id));
            }
        }

        // Setup action buttons
        element.querySelectorAll('.modal-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleAction(modal.id, action);
            });
        });

        return element;
    }

    getSizeStyles(size) {
        const sizes = {
            small: 'width: 400px; min-height: 200px;',
            medium: 'width: 600px; min-height: 400px;',
            large: 'width: 800px; min-height: 600px;',
            fullscreen: 'width: 90vw; height: 90vh;'
        };
        return sizes[size] || sizes.medium;
    }

    close(id) {
        const modal = this.modals.get(id);
        if (!modal) return;

        // Animate out
        modal.element.style.opacity = '0';
        modal.element.style.transform = 'translate(-50%, -50%) scale(0.9)';

        setTimeout(() => {
            if (modal.element.parentNode) {
                modal.element.parentNode.removeChild(modal.element);
            }
            
            this.modals.delete(id);
            this.stack = this.stack.filter(stackId => stackId !== id);
            
            if (this.stack.length === 0) {
                this.overlay.style.display = 'none';
            }

            if (modal.onClose) {
                modal.onClose();
            }
        }, 300);
    }

    closeTop() {
        if (this.stack.length > 0) {
            this.close(this.stack[this.stack.length - 1]);
        }
    }

    closeAll() {
        [...this.stack].forEach(id => this.close(id));
    }

    handleAction(modalId, action) {
        const modal = this.modals.get(modalId);
        if (modal) {
            const actionConfig = modal.actions.find(a => a.action === action);
            if (actionConfig && actionConfig.handler) {
                actionConfig.handler();
            }
            
            if (actionConfig && actionConfig.closeAfter !== false) {
                this.close(modalId);
            }
        }
    }

    // Professional modal methods
    showConfirm(message, title = 'Confirm') {
        return new Promise((resolve) => {
            this.show(message, {
                title,
                size: 'small',
                actions: [
                    {
                        label: 'Cancel',
                        action: 'cancel',
                        handler: () => resolve(false)
                    },
                    {
                        label: 'Confirm',
                        action: 'confirm',
                        primary: true,
                        handler: () => resolve(true)
                    }
                ]
            });
        });
    }

    showAlert(message, title = 'Alert') {
        return new Promise((resolve) => {
            this.show(message, {
                title,
                size: 'small',
                actions: [
                    {
                        label: 'OK',
                        action: 'ok',
                        primary: true,
                        handler: () => resolve()
                    }
                ]
            });
        });
    }

    showPrompt(message, defaultValue = '', title = 'Input') {
        return new Promise((resolve) => {
            const content = `
                <p>${message}</p>
                <input type="text" id="modal-prompt-input" value="${defaultValue}" style="
                    width: 100%;
                    padding: 8px 12px;
                    border: 1px solid #374151;
                    border-radius: 4px;
                    background: #111827;
                    color: white;
                    margin-top: 10px;
                ">
            `;
            
            const modalId = this.show(content, {
                title,
                size: 'small',
                actions: [
                    {
                        label: 'Cancel',
                        action: 'cancel',
                        handler: () => resolve(null)
                    },
                    {
                        label: 'OK',
                        action: 'ok',
                        primary: true,
                        handler: () => {
                            const input = document.getElementById('modal-prompt-input');
                            resolve(input ? input.value : null);
                        }
                    }
                ]
            });

            // Focus input after modal is shown
            setTimeout(() => {
                const input = document.getElementById('modal-prompt-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }, 100);
        });
    }

    showSettings() {
        const content = `
            <div class="settings-panel">
                <h4>Application Settings</h4>
                <div class="setting-group">
                    <label>Theme</label>
                    <select id="theme-select" style="background: #111827; color: white; border: 1px solid #374151; padding: 8px;">
                        <option value="dark">Dark</option>
                        <option value="light">Light</option>
                    </select>
                </div>
                <div class="setting-group" style="margin-top: 20px;">
                    <label>Auto-save interval (minutes)</label>
                    <input type="number" id="autosave-interval" value="5" min="1" max="60" style="background: #111827; color: white; border: 1px solid #374151; padding: 8px;">
                </div>
            </div>
        `;

        return this.show(content, {
            title: 'Settings',
            size: 'medium',
            actions: [
                {
                    label: 'Cancel',
                    action: 'cancel'
                },
                {
                    label: 'Apply',
                    action: 'apply',
                    primary: true,
                    handler: () => {
                        // Apply settings logic here
                        console.log('Settings applied');
                    }
                }
            ]
        });
    }
}

export default ModalManager;