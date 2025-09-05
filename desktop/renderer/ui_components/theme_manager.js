/**
 * Ainflue Desktop Renderer - Theme Manager
 * Professional theme management system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class ThemeManager {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.themes = new Map();
        this.currentTheme = 'light';
        this.customProperties = new Map();
        this.systemPreference = 'light';
        
        this.init();
    }

    /**
     * Initialize theme manager
     */
    init() {
        console.log('🎨 Initializing Theme Manager v' + this.version);
        
        this.setupDefaultThemes();
        this.detectSystemPreference();
        this.setupMediaQueryListener();
        this.loadSavedTheme();
        this.setupStyles();
    }

    /**
     * Setup default themes
     */
    setupDefaultThemes() {
        // Light Theme
        this.themes.set('light', {
            name: 'Light',
            type: 'light',
            properties: {
                // Colors
                '--primary-color': '#3b82f6',
                '--primary-hover': '#2563eb',
                '--primary-active': '#1d4ed8',
                '--secondary-color': '#6b7280',
                '--success-color': '#10b981',
                '--warning-color': '#f59e0b',
                '--error-color': '#ef4444',
                '--info-color': '#3b82f6',
                
                // Background colors
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f8fafc',
                '--bg-tertiary': '#f1f5f9',
                '--bg-accent': '#e2e8f0',
                '--bg-overlay': 'rgba(0, 0, 0, 0.5)',
                
                // Text colors
                '--text-primary': '#111827',
                '--text-secondary': '#6b7280',
                '--text-tertiary': '#9ca3af',
                '--text-inverse': '#ffffff',
                '--text-muted': '#d1d5db',
                
                // Border colors
                '--border-primary': '#e5e7eb',
                '--border-secondary': '#d1d5db',
                '--border-focus': '#3b82f6',
                '--border-error': '#ef4444',
                
                // Shadow colors
                '--shadow-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                '--shadow-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                '--shadow-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                '--shadow-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
                
                // Component specific
                '--header-bg': '#ffffff',
                '--sidebar-bg': '#374151',
                '--card-bg': '#ffffff',
                '--modal-bg': '#ffffff',
                '--button-bg': '#3b82f6',
                '--input-bg': '#ffffff',
                
                // Sizes
                '--border-radius': '6px',
                '--border-radius-lg': '8px',
                '--border-radius-xl': '12px',
                '--spacing-xs': '0.25rem',
                '--spacing-sm': '0.5rem',
                '--spacing-md': '1rem',
                '--spacing-lg': '1.5rem',
                '--spacing-xl': '3rem'
            }
        });

        // Dark Theme
        this.themes.set('dark', {
            name: 'Dark',
            type: 'dark',
            properties: {
                // Colors
                '--primary-color': '#60a5fa',
                '--primary-hover': '#3b82f6',
                '--primary-active': '#2563eb',
                '--secondary-color': '#9ca3af',
                '--success-color': '#34d399',
                '--warning-color': '#fbbf24',
                '--error-color': '#f87171',
                '--info-color': '#60a5fa',
                
                // Background colors
                '--bg-primary': '#111827',
                '--bg-secondary': '#1f2937',
                '--bg-tertiary': '#374151',
                '--bg-accent': '#4b5563',
                '--bg-overlay': 'rgba(0, 0, 0, 0.75)',
                
                // Text colors
                '--text-primary': '#f9fafb',
                '--text-secondary': '#d1d5db',
                '--text-tertiary': '#9ca3af',
                '--text-inverse': '#111827',
                '--text-muted': '#6b7280',
                
                // Border colors
                '--border-primary': '#374151',
                '--border-secondary': '#4b5563',
                '--border-focus': '#60a5fa',
                '--border-error': '#f87171',
                
                // Shadow colors
                '--shadow-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.25)',
                '--shadow-md': '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
                '--shadow-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
                '--shadow-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.4)',
                
                // Component specific
                '--header-bg': '#1f2937',
                '--sidebar-bg': '#111827',
                '--card-bg': '#1f2937',
                '--modal-bg': '#1f2937',
                '--button-bg': '#3b82f6',
                '--input-bg': '#374151',
                
                // Sizes (same as light)
                '--border-radius': '6px',
                '--border-radius-lg': '8px',
                '--border-radius-xl': '12px',
                '--spacing-xs': '0.25rem',
                '--spacing-sm': '0.5rem',
                '--spacing-md': '1rem',
                '--spacing-lg': '1.5rem',
                '--spacing-xl': '3rem'
            }
        });

        // High Contrast Theme
        this.themes.set('high-contrast', {
            name: 'High Contrast',
            type: 'dark',
            properties: {
                '--primary-color': '#ffffff',
                '--primary-hover': '#e5e7eb',
                '--primary-active': '#d1d5db',
                '--secondary-color': '#ffffff',
                '--success-color': '#00ff00',
                '--warning-color': '#ffff00',
                '--error-color': '#ff0000',
                '--info-color': '#00ffff',
                
                '--bg-primary': '#000000',
                '--bg-secondary': '#1a1a1a',
                '--bg-tertiary': '#333333',
                '--bg-accent': '#4d4d4d',
                '--bg-overlay': 'rgba(0, 0, 0, 0.9)',
                
                '--text-primary': '#ffffff',
                '--text-secondary': '#ffffff',
                '--text-tertiary': '#cccccc',
                '--text-inverse': '#000000',
                '--text-muted': '#999999',
                
                '--border-primary': '#ffffff',
                '--border-secondary': '#cccccc',
                '--border-focus': '#00ffff',
                '--border-error': '#ff0000',
                
                '--shadow-sm': '0 1px 2px 0 rgba(255, 255, 255, 0.1)',
                '--shadow-md': '0 4px 6px -1px rgba(255, 255, 255, 0.1)',
                '--shadow-lg': '0 10px 15px -3px rgba(255, 255, 255, 0.1)',
                '--shadow-xl': '0 20px 25px -5px rgba(255, 255, 255, 0.1)',
                
                '--header-bg': '#000000',
                '--sidebar-bg': '#000000',
                '--card-bg': '#1a1a1a',
                '--modal-bg': '#000000',
                '--button-bg': '#ffffff',
                '--input-bg': '#1a1a1a',
                
                '--border-radius': '2px',
                '--border-radius-lg': '4px',
                '--border-radius-xl': '6px',
                '--spacing-xs': '0.25rem',
                '--spacing-sm': '0.5rem',
                '--spacing-md': '1rem',
                '--spacing-lg': '1.5rem',
                '--spacing-xl': '3rem'
            }
        });

        // Professional Blue Theme
        this.themes.set('professional', {
            name: 'Professional',
            type: 'light',
            properties: {
                '--primary-color': '#1e40af',
                '--primary-hover': '#1d4ed8',
                '--primary-active': '#1e3a8a',
                '--secondary-color': '#64748b',
                '--success-color': '#059669',
                '--warning-color': '#d97706',
                '--error-color': '#dc2626',
                '--info-color': '#0284c7',
                
                '--bg-primary': '#ffffff',
                '--bg-secondary': '#f8fafc',
                '--bg-tertiary': '#e2e8f0',
                '--bg-accent': '#cbd5e1',
                '--bg-overlay': 'rgba(30, 64, 175, 0.1)',
                
                '--text-primary': '#0f172a',
                '--text-secondary': '#475569',
                '--text-tertiary': '#64748b',
                '--text-inverse': '#ffffff',
                '--text-muted': '#94a3b8',
                
                '--border-primary': '#e2e8f0',
                '--border-secondary': '#cbd5e1',
                '--border-focus': '#1e40af',
                '--border-error': '#dc2626',
                
                '--shadow-sm': '0 1px 2px 0 rgba(30, 64, 175, 0.05)',
                '--shadow-md': '0 4px 6px -1px rgba(30, 64, 175, 0.1)',
                '--shadow-lg': '0 10px 15px -3px rgba(30, 64, 175, 0.1)',
                '--shadow-xl': '0 20px 25px -5px rgba(30, 64, 175, 0.1)',
                
                '--header-bg': '#f8fafc',
                '--sidebar-bg': '#1e40af',
                '--card-bg': '#ffffff',
                '--modal-bg': '#ffffff',
                '--button-bg': '#1e40af',
                '--input-bg': '#ffffff',
                
                '--border-radius': '4px',
                '--border-radius-lg': '6px',
                '--border-radius-xl': '8px',
                '--spacing-xs': '0.25rem',
                '--spacing-sm': '0.5rem',
                '--spacing-md': '1rem',
                '--spacing-lg': '1.5rem',
                '--spacing-xl': '3rem'
            }
        });
    }

    /**
     * Detect system preference
     */
    detectSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.systemPreference = 'dark';
        } else {
            this.systemPreference = 'light';
        }
    }

    /**
     * Setup media query listener for system preference changes
     */
    setupMediaQueryListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addListener((e) => {
                this.systemPreference = e.matches ? 'dark' : 'light';
                
                if (this.currentTheme === 'auto') {
                    this.applySystemTheme();
                }
                
                this.emit('system-preference-changed', {
                    preference: this.systemPreference
                });
            });
        }
    }

    /**
     * Load saved theme from storage
     */
    loadSavedTheme() {
        let savedTheme = 'light';
        
        if (typeof Storage !== 'undefined') {
            savedTheme = localStorage.getItem('theme') || 'light';
        }
        
        this.setTheme(savedTheme);
    }

    /**
     * Set theme
     */
    setTheme(themeName) {
        if (themeName === 'auto') {
            this.currentTheme = 'auto';
            this.applySystemTheme();
        } else if (this.themes.has(themeName)) {
            this.currentTheme = themeName;
            this.applyTheme(themeName);
        } else {
            console.warn(`Theme "${themeName}" not found`);
            return false;
        }
        
        // Save to storage
        if (typeof Storage !== 'undefined') {
            localStorage.setItem('theme', themeName);
        }
        
        this.emit('theme-changed', {
            theme: themeName,
            actualTheme: this.getActualTheme()
        });
        
        return true;
    }

    /**
     * Apply system theme
     */
    applySystemTheme() {
        const systemTheme = this.systemPreference === 'dark' ? 'dark' : 'light';
        this.applyTheme(systemTheme);
    }

    /**
     * Apply theme properties
     */
    applyTheme(themeName) {
        const theme = this.themes.get(themeName);
        if (!theme) return;

        const root = document.documentElement;
        
        // Apply theme properties
        Object.entries(theme.properties).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });
        
        // Add theme class
        root.className = root.className.replace(/theme-\w+/g, '');
        root.classList.add(`theme-${themeName}`);
        
        // Add theme type class
        root.classList.remove('theme-type-light', 'theme-type-dark');
        root.classList.add(`theme-type-${theme.type}`);
        
        // Update meta theme-color
        this.updateMetaThemeColor(theme.properties['--bg-primary']);
    }

    /**
     * Update meta theme color for mobile browsers
     */
    updateMetaThemeColor(color) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.content = color;
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Get actual applied theme (resolves 'auto')
     */
    getActualTheme() {
        if (this.currentTheme === 'auto') {
            return this.systemPreference === 'dark' ? 'dark' : 'light';
        }
        return this.currentTheme;
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const currentActual = this.getActualTheme();
        const newTheme = currentActual === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    /**
     * Create custom theme
     */
    createCustomTheme(name, properties, type = 'light') {
        const theme = {
            name: name.charAt(0).toUpperCase() + name.slice(1),
            type,
            properties: { ...properties }
        };
        
        this.themes.set(name, theme);
        
        this.emit('theme-created', { name, theme });
        
        return name;
    }

    /**
     * Update theme property
     */
    updateThemeProperty(property, value, themeName = this.currentTheme) {
        if (themeName === 'auto') {
            themeName = this.getActualTheme();
        }
        
        const theme = this.themes.get(themeName);
        if (!theme) return;
        
        theme.properties[property] = value;
        
        // Apply immediately if it's the current theme
        if (themeName === this.getActualTheme()) {
            document.documentElement.style.setProperty(property, value);
        }
        
        this.emit('theme-property-updated', {
            property,
            value,
            theme: themeName
        });
    }

    /**
     * Get theme property
     */
    getThemeProperty(property, themeName = this.currentTheme) {
        if (themeName === 'auto') {
            themeName = this.getActualTheme();
        }
        
        const theme = this.themes.get(themeName);
        if (!theme) return null;
        
        return theme.properties[property];
    }

    /**
     * Create theme picker UI
     */
    createThemePicker(container) {
        const picker = document.createElement('div');
        picker.className = 'theme-picker';
        
        picker.innerHTML = `
            <div class="theme-picker__header">
                <h3>Choose Theme</h3>
            </div>
            <div class="theme-picker__options">
                <div class="theme-option ${this.currentTheme === 'auto' ? 'active' : ''}" data-theme="auto">
                    <div class="theme-preview theme-preview--auto">
                        <div class="preview-section preview-light"></div>
                        <div class="preview-section preview-dark"></div>
                    </div>
                    <span class="theme-name">Auto</span>
                </div>
                ${Array.from(this.themes.entries()).map(([key, theme]) => `
                    <div class="theme-option ${this.currentTheme === key ? 'active' : ''}" data-theme="${key}">
                        <div class="theme-preview theme-preview--${theme.type}">
                            <div class="preview-header" style="background: ${theme.properties['--header-bg']}"></div>
                            <div class="preview-content" style="background: ${theme.properties['--bg-primary']}"></div>
                            <div class="preview-accent" style="background: ${theme.properties['--primary-color']}"></div>
                        </div>
                        <span class="theme-name">${theme.name}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add event listeners
        picker.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                const themeName = option.dataset.theme;
                this.setTheme(themeName);
                
                // Update active state
                picker.querySelectorAll('.theme-option').forEach(opt => {
                    opt.classList.remove('active');
                });
                option.classList.add('active');
            });
        });
        
        container.appendChild(picker);
        return picker;
    }

    /**
     * Export theme
     */
    exportTheme(themeName) {
        const theme = this.themes.get(themeName);
        if (!theme) return null;
        
        return {
            name: themeName,
            data: theme,
            version: this.version,
            exported: new Date().toISOString()
        };
    }

    /**
     * Import theme
     */
    importTheme(themeData) {
        const { name, data } = themeData;
        
        if (!name || !data) {
            throw new Error('Invalid theme data');
        }
        
        this.themes.set(name, data);
        
        this.emit('theme-imported', { name, theme: data });
        
        return name;
    }

    /**
     * Get available themes
     */
    getAvailableThemes() {
        return Array.from(this.themes.entries()).map(([key, theme]) => ({
            key,
            name: theme.name,
            type: theme.type
        }));
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('theme-manager-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'theme-manager-styles';
        styles.textContent = `
            /* Theme Manager Styles */
            .theme-picker {
                background: var(--bg-primary);
                border: 1px solid var(--border-primary);
                border-radius: var(--border-radius-lg);
                padding: 20px;
                box-shadow: var(--shadow-lg);
            }
            
            .theme-picker__header {
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid var(--border-primary);
            }
            
            .theme-picker__header h3 {
                margin: 0;
                color: var(--text-primary);
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .theme-picker__options {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 12px;
            }
            
            .theme-option {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                padding: 12px;
                border: 2px solid var(--border-primary);
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: all 0.2s ease;
                background: var(--bg-secondary);
            }
            
            .theme-option:hover {
                border-color: var(--primary-color);
                transform: translateY(-2px);
            }
            
            .theme-option.active {
                border-color: var(--primary-color);
                background: var(--primary-color);
                color: var(--text-inverse);
            }
            
            .theme-preview {
                width: 60px;
                height: 40px;
                border-radius: 4px;
                overflow: hidden;
                border: 1px solid rgba(0, 0, 0, 0.1);
                display: flex;
                flex-direction: column;
                position: relative;
            }
            
            .theme-preview--auto {
                flex-direction: row;
            }
            
            .theme-preview--auto .preview-section {
                flex: 1;
                height: 100%;
            }
            
            .preview-light {
                background: #ffffff;
            }
            
            .preview-dark {
                background: #111827;
            }
            
            .preview-header {
                height: 12px;
                width: 100%;
            }
            
            .preview-content {
                flex: 1;
                width: 100%;
            }
            
            .preview-accent {
                position: absolute;
                bottom: 2px;
                right: 2px;
                width: 8px;
                height: 8px;
                border-radius: 50%;
            }
            
            .theme-name {
                font-size: 0.75rem;
                font-weight: 500;
                text-align: center;
                color: inherit;
            }
            
            /* Theme transitions */
            * {
                transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
            }
            
            /* Theme-specific adjustments */
            .theme-high-contrast {
                --transition-duration: 0.1s;
            }
            
            .theme-high-contrast *:focus {
                outline: 3px solid var(--border-focus) !important;
                outline-offset: 2px !important;
            }
            
            /* Print styles */
            @media print {
                .theme-picker {
                    display: none;
                }
                
                * {
                    background: white !important;
                    color: black !important;
                    box-shadow: none !important;
                }
            }
            
            /* Reduced motion */
            @media (prefers-reduced-motion: reduce) {
                * {
                    transition: none !important;
                    animation: none !important;
                }
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
     * Destroy theme manager
     */
    destroy() {
        // Remove theme classes
        const root = document.documentElement;
        root.className = root.className.replace(/theme-\w+/g, '');
        
        // Clear custom properties
        this.customProperties.forEach((value, property) => {
            root.style.removeProperty(property);
        });
        
        this.themes.clear();
        this.customProperties.clear();
        
        // Remove styles
        const styles = document.getElementById('theme-manager-styles');
        if (styles) styles.remove();
        
        console.log('🎨 Theme Manager destroyed');
    }
}

// Export for ES6 modules
export default ThemeManager;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.ThemeManager = ThemeManager;
}