/**
 * Ainflue Desktop Renderer - Modal Manager
 * Professional modal and dialog management system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class ModalManager {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.modals = new Map();
        this.modalStack = [];
        this.zIndexBase = 10000;
        this.config = {
            closeOnOverlay: true,
            closeOnEscape: true,
            animationDuration: 300,
            maxWidth: '90vw',
            maxHeight: '90vh'
        };
        
        this.init();
    }

    /**
     * Initialize modal manager
     */
    init() {
        console.log('🪟 Initializing Modal Manager v' + this.version);
        
        this.setupStyles();
        this.setupEventHandlers();
        this.createOverlay();
    }

    /**
     * Create modal overlay
     */
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.id = 'modal-overlay';
        this.overlay.className = 'modal-overlay hidden';
        document.body.appendChild(this.overlay);

        // Overlay click handler
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay && this.config.closeOnOverlay) {
                this.closeTop();
            }
        });
    }

    /**
     * Show modal
     */
    show(options = {}) {
        const {
            title = '',
            content = '',
            size = 'md',
            type = 'default',
            buttons = [],
            closeButton = true,
            draggable = false,
            resizable = false,
            centered = true,
            className = '',
            onOpen = null,
            onClose = null
        } = options;

        const id = this.generateId();
        
        const modal = {
            id,
            title,
            content,
            size,
            type,
            buttons,
            closeButton,
            draggable,
            resizable,
            centered,
            className,
            onOpen,
            onClose,
            element: null,
            zIndex: this.zIndexBase + this.modalStack.length
        };

        // Create modal element
        modal.element = this.createModalElement(modal);
        
        // Add to DOM
        document.body.appendChild(modal.element);
        
        // Show overlay
        this.showOverlay();
        
        // Add to stack
        this.modalStack.push(id);
        this.modals.set(id, modal);
        
        // Show modal with animation
        requestAnimationFrame(() => {
            modal.element.classList.add('modal--visible');
            
            if (onOpen) {
                onOpen(modal);
            }
        });

        // Focus management
        this.focusModal(modal.element);
        
        this.emit('modal-opened', modal);
        
        return id;
    }

    /**
     * Create modal element
     */
    createModalElement(modal) {
        const element = document.createElement('div');
        element.className = `modal modal--${modal.size} modal--${modal.type} ${modal.className}`;
        element.setAttribute('data-id', modal.id);
        element.style.zIndex = modal.zIndex;

        // Modal structure
        let modalHTML = '<div class="modal__dialog">';
        
        // Header
        if (modal.title || modal.closeButton) {
            modalHTML += '<div class="modal__header">';
            
            if (modal.title) {
                modalHTML += `<h3 class="modal__title">${modal.title}</h3>`;
            }
            
            if (modal.closeButton) {
                modalHTML += '<button class="modal__close" title="Close">×</button>';
            }
            
            modalHTML += '</div>';
        }
        
        // Content
        modalHTML += `<div class="modal__content">${modal.content}</div>`;
        
        // Footer with buttons
        if (modal.buttons.length > 0) {
            modalHTML += '<div class="modal__footer">';
            
            modal.buttons.forEach(button => {
                const btnClass = `modal__button modal__button--${button.type || 'default'}`;
                modalHTML += `<button class="${btnClass}" data-action="${button.action || ''}">${button.text}</button>`;
            });
            
            modalHTML += '</div>';
        }
        
        modalHTML += '</div>';
        element.innerHTML = modalHTML;

        // Setup event handlers
        this.setupModalEvents(element, modal);
        
        // Make draggable if requested
        if (modal.draggable) {
            this.makeDraggable(element);
        }
        
        // Make resizable if requested
        if (modal.resizable) {
            this.makeResizable(element);
        }

        return element;
    }

    /**
     * Setup modal event handlers
     */
    setupModalEvents(element, modal) {
        // Close button
        const closeBtn = element.querySelector('.modal__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.close(modal.id);
            });
        }

        // Button actions
        const actionBtns = element.querySelectorAll('.modal__button[data-action]');
        actionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.getAttribute('data-action');
                const button = modal.buttons.find(b => b.action === action);
                
                if (button && button.callback) {
                    const result = button.callback(modal);
                    
                    // Close modal unless callback returns false
                    if (result !== false) {
                        this.close(modal.id);
                    }
                } else if (action === 'close' || action === 'cancel') {
                    this.close(modal.id);
                }
            });
        });

        // Prevent dialog clicks from closing modal
        const dialog = element.querySelector('.modal__dialog');
        if (dialog) {
            dialog.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    /**
     * Close modal
     */
    close(id) {
        const modal = this.modals.get(id);
        if (!modal) return;

        // Call onClose callback
        if (modal.onClose) {
            const result = modal.onClose(modal);
            if (result === false) return; // Prevent closing
        }

        // Remove from stack
        const stackIndex = this.modalStack.indexOf(id);
        if (stackIndex > -1) {
            this.modalStack.splice(stackIndex, 1);
        }

        // Animate out
        modal.element.classList.remove('modal--visible');
        
        setTimeout(() => {
            // Remove from DOM
            if (modal.element.parentNode) {
                modal.element.parentNode.removeChild(modal.element);
            }
            
            // Remove from map
            this.modals.delete(id);
            
            // Hide overlay if no more modals
            if (this.modalStack.length === 0) {
                this.hideOverlay();
            } else {
                // Focus previous modal
                const topModalId = this.modalStack[this.modalStack.length - 1];
                const topModal = this.modals.get(topModalId);
                if (topModal) {
                    this.focusModal(topModal.element);
                }
            }
            
            this.emit('modal-closed', modal);
        }, this.config.animationDuration);
    }

    /**
     * Close top modal
     */
    closeTop() {
        if (this.modalStack.length > 0) {
            const topId = this.modalStack[this.modalStack.length - 1];
            this.close(topId);
        }
    }

    /**
     * Close all modals
     */
    closeAll() {
        [...this.modalStack].forEach(id => {
            this.close(id);
        });
    }

    /**
     * Show confirmation dialog
     */
    confirm(message, options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Confirm',
                confirmText = 'OK',
                cancelText = 'Cancel',
                type = 'warning'
            } = options;

            this.show({
                title,
                content: `<p>${message}</p>`,
                type,
                size: 'sm',
                buttons: [
                    {
                        text: cancelText,
                        type: 'secondary',
                        action: 'cancel',
                        callback: () => {
                            resolve(false);
                        }
                    },
                    {
                        text: confirmText,
                        type: 'primary',
                        action: 'confirm',
                        callback: () => {
                            resolve(true);
                        }
                    }
                ]
            });
        });
    }

    /**
     * Show alert dialog
     */
    alert(message, options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Alert',
                buttonText = 'OK',
                type = 'info'
            } = options;

            this.show({
                title,
                content: `<p>${message}</p>`,
                type,
                size: 'sm',
                buttons: [
                    {
                        text: buttonText,
                        type: 'primary',
                        action: 'ok',
                        callback: () => {
                            resolve(true);
                        }
                    }
                ]
            });
        });
    }

    /**
     * Show prompt dialog
     */
    prompt(message, options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Input',
                defaultValue = '',
                placeholder = '',
                confirmText = 'OK',
                cancelText = 'Cancel',
                type = 'text',
                required = false
            } = options;

            const inputId = 'prompt-input-' + Date.now();
            const content = `
                <p>${message}</p>
                <div class="modal__input-group">
                    <input 
                        id="${inputId}"
                        type="${type}" 
                        class="modal__input" 
                        placeholder="${placeholder}"
                        value="${defaultValue}"
                        ${required ? 'required' : ''}
                    />
                </div>
            `;

            const modalId = this.show({
                title,
                content,
                size: 'sm',
                buttons: [
                    {
                        text: cancelText,
                        type: 'secondary',
                        action: 'cancel',
                        callback: () => {
                            resolve(null);
                        }
                    },
                    {
                        text: confirmText,
                        type: 'primary',
                        action: 'confirm',
                        callback: () => {
                            const input = document.getElementById(inputId);
                            const value = input ? input.value.trim() : '';
                            
                            if (required && !value) {
                                input.focus();
                                return false; // Don't close modal
                            }
                            
                            resolve(value);
                        }
                    }
                ],
                onOpen: () => {
                    // Focus input
                    const input = document.getElementById(inputId);
                    if (input) {
                        input.focus();
                        input.select();
                    }
                }
            });
        });
    }

    /**
     * Show overlay
     */
    showOverlay() {
        this.overlay.classList.remove('hidden');
        requestAnimationFrame(() => {
            this.overlay.classList.add('modal-overlay--visible');
        });
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide overlay
     */
    hideOverlay() {
        this.overlay.classList.remove('modal-overlay--visible');
        
        setTimeout(() => {
            this.overlay.classList.add('hidden');
            
            // Restore body scroll
            document.body.style.overflow = '';
        }, this.config.animationDuration);
    }

    /**
     * Focus modal
     */
    focusModal(element) {
        // Find first focusable element
        const focusableElements = element.querySelectorAll(
            'button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        } else {
            element.focus();
        }
    }

    /**
     * Make modal draggable
     */
    makeDraggable(element) {
        const header = element.querySelector('.modal__header');
        const dialog = element.querySelector('.modal__dialog');
        
        if (!header || !dialog) return;

        let isDragging = false;
        let startX, startY, startLeft, startTop;

        header.style.cursor = 'move';
        header.setAttribute('title', 'Drag to move');

        header.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('modal__close')) return;
            
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = dialog.getBoundingClientRect();
            startLeft = rect.left;
            startTop = rect.top;

            dialog.style.position = 'fixed';
            dialog.style.margin = '0';
            dialog.style.left = startLeft + 'px';
            dialog.style.top = startTop + 'px';
            
            element.classList.add('modal--dragging');
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            dialog.style.left = (startLeft + deltaX) + 'px';
            dialog.style.top = (startTop + deltaY) + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.classList.remove('modal--dragging');
            }
        });
    }

    /**
     * Make modal resizable
     */
    makeResizable(element) {
        const dialog = element.querySelector('.modal__dialog');
        if (!dialog) return;

        // Add resize handles
        const handles = ['n', 'e', 's', 'w', 'ne', 'se', 'sw', 'nw'];
        
        handles.forEach(handle => {
            const resizeHandle = document.createElement('div');
            resizeHandle.className = `modal__resize-handle modal__resize-handle--${handle}`;
            dialog.appendChild(resizeHandle);
            
            this.setupResizeHandle(resizeHandle, handle, dialog);
        });
    }

    /**
     * Setup resize handle
     */
    setupResizeHandle(handle, direction, dialog) {
        let isResizing = false;
        let startX, startY, startWidth, startHeight, startLeft, startTop;

        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = dialog.getBoundingClientRect();
            startWidth = rect.width;
            startHeight = rect.height;
            startLeft = rect.left;
            startTop = rect.top;
            
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            let newWidth = startWidth;
            let newHeight = startHeight;
            let newLeft = startLeft;
            let newTop = startTop;

            // Handle different resize directions
            if (direction.includes('e')) {
                newWidth = Math.max(300, startWidth + deltaX);
            }
            if (direction.includes('w')) {
                newWidth = Math.max(300, startWidth - deltaX);
                newLeft = startLeft + (startWidth - newWidth);
            }
            if (direction.includes('s')) {
                newHeight = Math.max(200, startHeight + deltaY);
            }
            if (direction.includes('n')) {
                newHeight = Math.max(200, startHeight - deltaY);
                newTop = startTop + (startHeight - newHeight);
            }

            dialog.style.width = newWidth + 'px';
            dialog.style.height = newHeight + 'px';
            dialog.style.left = newLeft + 'px';
            dialog.style.top = newTop + 'px';
        });

        document.addEventListener('mouseup', () => {
            isResizing = false;
        });
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Escape key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.config.closeOnEscape) {
                this.closeTop();
            }
        });

        // Tab navigation within modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab' && this.modalStack.length > 0) {
                const topModalId = this.modalStack[this.modalStack.length - 1];
                const topModal = this.modals.get(topModalId);
                
                if (topModal) {
                    this.handleTabNavigation(e, topModal.element);
                }
            }
        });
    }

    /**
     * Handle tab navigation within modal
     */
    handleTabNavigation(e, modal) {
        const focusableElements = modal.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('modal-manager-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'modal-manager-styles';
        styles.textContent = `
            /* Modal Manager Styles */
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                z-index: 9999;
                opacity: 0;
                transition: opacity ${this.config.animationDuration}ms ease;
            }
            
            .modal-overlay.hidden {
                display: none;
            }
            
            .modal-overlay--visible {
                opacity: 1;
            }
            
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                opacity: 0;
                transform: scale(0.9);
                transition: all ${this.config.animationDuration}ms ease;
            }
            
            .modal--visible {
                opacity: 1;
                transform: scale(1);
            }
            
            .modal__dialog {
                background: white;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                max-width: ${this.config.maxWidth};
                max-height: ${this.config.maxHeight};
                width: 100%;
                display: flex;
                flex-direction: column;
                position: relative;
                overflow: hidden;
            }
            
            .modal--sm .modal__dialog {
                max-width: 400px;
            }
            
            .modal--md .modal__dialog {
                max-width: 600px;
            }
            
            .modal--lg .modal__dialog {
                max-width: 800px;
            }
            
            .modal--xl .modal__dialog {
                max-width: 1200px;
            }
            
            .modal--fullscreen .modal__dialog {
                max-width: 100vw;
                max-height: 100vh;
                height: 100vh;
                border-radius: 0;
            }
            
            .modal__header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
                background: #f9fafb;
            }
            
            .modal__title {
                margin: 0;
                font-size: 1.25rem;
                font-weight: 600;
                color: #111827;
            }
            
            .modal__close {
                width: 32px;
                height: 32px;
                border: none;
                background: transparent;
                color: #6b7280;
                cursor: pointer;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                line-height: 1;
                transition: all 0.2s;
            }
            
            .modal__close:hover {
                background: #e5e7eb;
                color: #374151;
            }
            
            .modal__content {
                padding: 24px;
                flex: 1;
                overflow-y: auto;
            }
            
            .modal__footer {
                display: flex;
                justify-content: flex-end;
                gap: 12px;
                padding: 16px 24px;
                border-top: 1px solid #e5e7eb;
                background: #f9fafb;
            }
            
            .modal__button {
                padding: 8px 16px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
            }
            
            .modal__button:hover {
                background: #f9fafb;
                border-color: #9ca3af;
            }
            
            .modal__button--primary {
                background: #3b82f6;
                border-color: #3b82f6;
                color: white;
            }
            
            .modal__button--primary:hover {
                background: #2563eb;
                border-color: #2563eb;
            }
            
            .modal__button--danger {
                background: #ef4444;
                border-color: #ef4444;
                color: white;
            }
            
            .modal__button--danger:hover {
                background: #dc2626;
                border-color: #dc2626;
            }
            
            .modal__button--success {
                background: #10b981;
                border-color: #10b981;
                color: white;
            }
            
            .modal__button--success:hover {
                background: #059669;
                border-color: #059669;
            }
            
            .modal__input-group {
                margin: 16px 0;
            }
            
            .modal__input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.2s;
            }
            
            .modal__input:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .modal--dragging {
                user-select: none;
            }
            
            .modal__resize-handle {
                position: absolute;
                background: transparent;
            }
            
            .modal__resize-handle--n {
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                cursor: n-resize;
            }
            
            .modal__resize-handle--e {
                top: 0;
                right: 0;
                bottom: 0;
                width: 4px;
                cursor: e-resize;
            }
            
            .modal__resize-handle--s {
                bottom: 0;
                left: 0;
                right: 0;
                height: 4px;
                cursor: s-resize;
            }
            
            .modal__resize-handle--w {
                top: 0;
                left: 0;
                bottom: 0;
                width: 4px;
                cursor: w-resize;
            }
            
            .modal__resize-handle--ne {
                top: 0;
                right: 0;
                width: 8px;
                height: 8px;
                cursor: ne-resize;
            }
            
            .modal__resize-handle--se {
                bottom: 0;
                right: 0;
                width: 8px;
                height: 8px;
                cursor: se-resize;
            }
            
            .modal__resize-handle--sw {
                bottom: 0;
                left: 0;
                width: 8px;
                height: 8px;
                cursor: sw-resize;
            }
            
            .modal__resize-handle--nw {
                top: 0;
                left: 0;
                width: 8px;
                height: 8px;
                cursor: nw-resize;
            }
            
            /* Modal types */
            .modal--success .modal__header {
                background: #f0fdf4;
                border-color: #bbf7d0;
            }
            
            .modal--warning .modal__header {
                background: #fffbeb;
                border-color: #fed7aa;
            }
            
            .modal--error .modal__header {
                background: #fef2f2;
                border-color: #fecaca;
            }
            
            @media (max-width: 640px) {
                .modal {
                    padding: 10px;
                }
                
                .modal__dialog {
                    max-width: 100%;
                    max-height: 100%;
                }
                
                .modal__header,
                .modal__content,
                .modal__footer {
                    padding: 16px;
                }
                
                .modal__footer {
                    flex-direction: column;
                }
                
                .modal__button {
                    width: 100%;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'modal-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Get modal count
     */
    getCount() {
        return this.modalStack.length;
    }

    /**
     * Is modal open
     */
    isOpen(id = null) {
        if (id) {
            return this.modals.has(id);
        }
        return this.modalStack.length > 0;
    }

    /**
     * Get top modal
     */
    getTop() {
        if (this.modalStack.length === 0) return null;
        const topId = this.modalStack[this.modalStack.length - 1];
        return this.modals.get(topId);
    }

    /**
     * Configure modal manager
     */
    configure(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }

    /**
     * Destroy modal manager
     */
    destroy() {
        this.closeAll();
        
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
        
        // Remove styles
        const styles = document.getElementById('modal-manager-styles');
        if (styles) styles.remove();
        
        console.log('🪟 Modal Manager destroyed');
    }
}

// Export for ES6 modules
export default ModalManager;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.ModalManager = ModalManager;
}