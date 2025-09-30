/**
 * Ainflue Desktop Renderer - Professional Controls
 * Professional interface controls and components
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class ProfessionalControls {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.components = new Map();
        this.initialized = false;
        
        this.init();
    }

    /**
     * Initialize professional controls system
     */
    init() {
        if (this.initialized) return;
        
        console.log('🎛️ Initializing Professional Controls v' + this.version);
        
        this.createControlTemplates();
        this.setupEventHandlers();
        this.loadControlStyles();
        
        this.initialized = true;
        this.emit('controls-ready');
    }

    /**
     * Create professional control templates
     */
    createControlTemplates() {
        // Professional Button Templates
        this.components.set('pro-button', {
            template: `
                <button class="pro-btn" data-variant="primary">
                    <span class="btn-icon"></span>
                    <span class="btn-text"></span>
                    <span class="btn-loading hidden">
                        <div class="spinner"></div>
                    </span>
                </button>
            `,
            variants: ['primary', 'secondary', 'danger', 'success', 'warning', 'ghost'],
            sizes: ['xs', 'sm', 'md', 'lg', 'xl']
        });

        // Professional Input Controls
        this.components.set('pro-input', {
            template: `
                <div class="pro-input-group">
                    <label class="pro-label"></label>
                    <div class="input-wrapper">
                        <input class="pro-input" type="text" />
                        <span class="input-icon"></span>
                        <span class="validation-indicator"></span>
                    </div>
                    <span class="help-text"></span>
                    <span class="error-text hidden"></span>
                </div>
            `,
            types: ['text', 'email', 'password', 'number', 'tel', 'url'],
            validations: ['required', 'email', 'numeric', 'alpha', 'alphanumeric']
        });

        // Professional Slider Controls
        this.components.set('pro-slider', {
            template: `
                <div class="pro-slider-group">
                    <label class="slider-label">
                        <span class="label-text"></span>
                        <span class="value-display"></span>
                    </label>
                    <div class="slider-wrapper">
                        <input type="range" class="pro-slider" />
                        <div class="slider-track">
                            <div class="slider-fill"></div>
                            <div class="slider-thumb"></div>
                        </div>
                        <div class="slider-markers"></div>
                    </div>
                </div>
            `,
            ranges: ['0-100', '0-1', '-1-1', 'custom'],
            precision: [0, 1, 2, 3]
        });

        // Professional Toggle Switch
        this.components.set('pro-toggle', {
            template: `
                <div class="pro-toggle-group">
                    <label class="toggle-label">
                        <input type="checkbox" class="toggle-input" />
                        <span class="toggle-switch">
                            <span class="toggle-thumb"></span>
                        </span>
                        <span class="toggle-text"></span>
                    </label>
                </div>
            `,
            variants: ['default', 'success', 'warning', 'danger'],
            sizes: ['sm', 'md', 'lg']
        });

        // Professional Dropdown
        this.components.set('pro-dropdown', {
            template: `
                <div class="pro-dropdown">
                    <button class="dropdown-trigger">
                        <span class="trigger-text"></span>
                        <span class="trigger-icon">▼</span>
                    </button>
                    <div class="dropdown-menu hidden">
                        <div class="dropdown-search">
                            <input type="text" placeholder="Search..." />
                        </div>
                        <div class="dropdown-items"></div>
                    </div>
                </div>
            `,
            features: ['search', 'multi-select', 'grouping', 'virtual-scroll'],
            positions: ['bottom', 'top', 'left', 'right']
        });
    }

    /**
     * Create professional button with advanced features
     */
    createButton(options = {}) {
        const {
            text = 'Button',
            icon = null,
            variant = 'primary',
            size = 'md',
            loading = false,
            disabled = false,
            onClick = null,
            tooltip = null
        } = options;

        const button = document.createElement('button');
        button.className = `pro-btn pro-btn--${variant} pro-btn--${size}`;
        
        if (disabled) button.disabled = true;
        if (tooltip) button.setAttribute('title', tooltip);

        // Button structure
        button.innerHTML = `
            ${icon ? `<span class="btn-icon">${icon}</span>` : ''}
            <span class="btn-text">${text}</span>
            <span class="btn-loading ${loading ? '' : 'hidden'}">
                <div class="spinner"></div>
            </span>
        `;

        // Event handling
        if (onClick) {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                if (!button.disabled && !loading) {
                    onClick(e, button);
                }
            });
        }

        return button;
    }

    /**
     * Create professional input with validation
     */
    createInput(options = {}) {
        const {
            label = '',
            type = 'text',
            placeholder = '',
            value = '',
            required = false,
            validation = null,
            helpText = '',
            icon = null,
            onChange = null
        } = options;

        const container = document.createElement('div');
        container.className = 'pro-input-group';

        container.innerHTML = `
            <label class="pro-label">${label}${required ? ' *' : ''}</label>
            <div class="input-wrapper">
                <input 
                    class="pro-input" 
                    type="${type}" 
                    placeholder="${placeholder}"
                    value="${value}"
                    ${required ? 'required' : ''}
                />
                ${icon ? `<span class="input-icon">${icon}</span>` : ''}
                <span class="validation-indicator"></span>
            </div>
            ${helpText ? `<span class="help-text">${helpText}</span>` : ''}
            <span class="error-text hidden"></span>
        `;

        const input = container.querySelector('.pro-input');
        
        // Validation setup
        if (validation) {
            this.setupInputValidation(input, validation, container);
        }

        // Event handling
        if (onChange) {
            input.addEventListener('input', (e) => onChange(e.target.value, e));
        }

        return container;
    }

    /**
     * Create professional slider control
     */
    createSlider(options = {}) {
        const {
            label = '',
            min = 0,
            max = 100,
            step = 1,
            value = 50,
            precision = 0,
            unit = '',
            markers = false,
            onChange = null
        } = options;

        const container = document.createElement('div');
        container.className = 'pro-slider-group';

        container.innerHTML = `
            <label class="slider-label">
                <span class="label-text">${label}</span>
                <span class="value-display">${value.toFixed(precision)}${unit}</span>
            </label>
            <div class="slider-wrapper">
                <input 
                    type="range" 
                    class="pro-slider" 
                    min="${min}" 
                    max="${max}" 
                    step="${step}" 
                    value="${value}"
                />
                <div class="slider-track">
                    <div class="slider-fill"></div>
                    <div class="slider-thumb"></div>
                </div>
                ${markers ? '<div class="slider-markers"></div>' : ''}
            </div>
        `;

        const slider = container.querySelector('.pro-slider');
        const valueDisplay = container.querySelector('.value-display');
        const sliderFill = container.querySelector('.slider-fill');

        // Update visual elements
        const updateSlider = (val) => {
            const percentage = ((val - min) / (max - min)) * 100;
            sliderFill.style.width = percentage + '%';
            valueDisplay.textContent = parseFloat(val).toFixed(precision) + unit;
        };

        // Initial setup
        updateSlider(value);

        // Event handling
        slider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            updateSlider(val);
            if (onChange) onChange(val, e);
        });

        // Add markers if requested
        if (markers) {
            this.addSliderMarkers(container, min, max, step);
        }

        return container;
    }

    /**
     * Create professional toggle switch
     */
    createToggle(options = {}) {
        const {
            label = '',
            checked = false,
            variant = 'default',
            size = 'md',
            disabled = false,
            onChange = null
        } = options;

        const container = document.createElement('div');
        container.className = `pro-toggle-group pro-toggle--${variant} pro-toggle--${size}`;

        container.innerHTML = `
            <label class="toggle-label">
                <input 
                    type="checkbox" 
                    class="toggle-input" 
                    ${checked ? 'checked' : ''}
                    ${disabled ? 'disabled' : ''}
                />
                <span class="toggle-switch">
                    <span class="toggle-thumb"></span>
                </span>
                <span class="toggle-text">${label}</span>
            </label>
        `;

        const input = container.querySelector('.toggle-input');

        // Event handling
        if (onChange) {
            input.addEventListener('change', (e) => onChange(e.target.checked, e));
        }

        return container;
    }

    /**
     * Setup input validation
     */
    setupInputValidation(input, validation, container) {
        const errorElement = container.querySelector('.error-text');
        const indicator = container.querySelector('.validation-indicator');

        const validate = () => {
            const value = input.value;
            let isValid = true;
            let message = '';

            // Validation logic
            if (validation.required && !value.trim()) {
                isValid = false;
                message = 'This field is required';
            } else if (validation.email && value && !this.isValidEmail(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            } else if (validation.minLength && value.length < validation.minLength) {
                isValid = false;
                message = `Minimum ${validation.minLength} characters required`;
            } else if (validation.pattern && value && !validation.pattern.test(value)) {
                isValid = false;
                message = validation.message || 'Invalid format';
            }

            // Update UI
            container.classList.toggle('pro-input--error', !isValid);
            container.classList.toggle('pro-input--valid', isValid && value);
            
            if (!isValid && message) {
                errorElement.textContent = message;
                errorElement.classList.remove('hidden');
            } else {
                errorElement.classList.add('hidden');
            }

            indicator.textContent = isValid ? '✓' : '✗';
            
            return isValid;
        };

        input.addEventListener('blur', validate);
        input.addEventListener('input', () => {
            // Clear error on input
            if (container.classList.contains('pro-input--error')) {
                setTimeout(validate, 300);
            }
        });

        // Store validation function
        input.validate = validate;
    }

    /**
     * Add slider markers
     */
    addSliderMarkers(container, min, max, step) {
        const markersContainer = container.querySelector('.slider-markers');
        const steps = Math.floor((max - min) / step) + 1;
        
        for (let i = 0; i < steps; i++) {
            const marker = document.createElement('div');
            marker.className = 'slider-marker';
            marker.style.left = (i / (steps - 1)) * 100 + '%';
            markersContainer.appendChild(marker);
        }
    }

    /**
     * Email validation
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Global keyboard shortcuts for professional controls
        document.addEventListener('keydown', (e) => {
            // Focus management
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
            
            // Professional shortcuts
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.handleQuickAction();
                        break;
                }
            }
        });

        // Touch and mobile support
        if ('ontouchstart' in window) {
            this.setupTouchControls();
        }
    }

    /**
     * Handle tab navigation for accessibility
     */
    handleTabNavigation(e) {
        const focusableElements = document.querySelectorAll(
            'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        
        const focusedIndex = Array.from(focusableElements).indexOf(document.activeElement);
        
        if (e.shiftKey && focusedIndex === 0) {
            e.preventDefault();
            focusableElements[focusableElements.length - 1].focus();
        } else if (!e.shiftKey && focusedIndex === focusableElements.length - 1) {
            e.preventDefault();
            focusableElements[0].focus();
        }
    }

    /**
     * Setup touch controls for mobile devices
     */
    setupTouchControls() {
        let touchStartY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            const touchY = e.touches[0].clientY;
            const deltaY = touchStartY - touchY;
            
            // Custom touch handling for sliders and controls
            if (e.target.classList.contains('pro-slider')) {
                this.handleSliderTouch(e, deltaY);
            }
        }, { passive: false });
    }

    /**
     * Load control styles
     */
    loadControlStyles() {
        if (document.getElementById('professional-controls-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'professional-controls-styles';
        styles.textContent = `
            /* Professional Controls Base Styles */
            .pro-btn {
                position: relative;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                user-select: none;
            }
            
            .pro-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .pro-btn--primary {
                background: #3B82F6;
                color: white;
            }
            
            .pro-btn--primary:hover:not(:disabled) {
                background: #2563EB;
                transform: translateY(-1px);
            }
            
            .pro-input-group {
                margin-bottom: 16px;
            }
            
            .pro-label {
                display: block;
                margin-bottom: 4px;
                font-weight: 500;
                color: #374151;
            }
            
            .input-wrapper {
                position: relative;
            }
            
            .pro-input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                transition: border-color 0.2s;
            }
            
            .pro-input:focus {
                outline: none;
                border-color: #3B82F6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .hidden {
                display: none !important;
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Cleanup and destroy
     */
    destroy() {
        this.components.clear();
        this.initialized = false;
        
        // Remove styles
        const styles = document.getElementById('professional-controls-styles');
        if (styles) styles.remove();
        
        console.log('🎛️ Professional Controls destroyed');
    }
}

// Export for ES6 modules
export default ProfessionalControls;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.ProfessionalControls = ProfessionalControls;
}