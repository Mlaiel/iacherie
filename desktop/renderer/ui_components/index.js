/**
 * Ainflue Desktop - UI Components Index
 * Index et export composants UI professionnels
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Professional UI components for desktop renderer
 * Supports multi-creator workflows and responsive design
 */

// Import all UI components
import { ProfessionalControls } from './professional_controls.js';
import { DashboardLayouts } from './dashboard_layouts.js';
import { NotificationSystem } from './notification_system.js';
import { ModalManager } from './modal_manager.js';
import { SidebarNavigation } from './sidebar_navigation.js';
import { HeaderControls } from './header_controls.js';
import { StatusIndicators } from './status_indicators.js';
import { ResponsiveUtilities } from './responsive_utilities.js';
import { ThemeManager } from './theme_manager.js';

/**
 * UI Components Registry
 * Central registry for all professional UI components
 */
class UIComponentsRegistry {
    constructor() {
        this.components = new Map();
        this.initialized = false;
        this.theme = 'dark';
        this.locale = 'en';
        
        this.initializeComponents();
    }

    /**
     * Initialize all UI components
     */
    initializeComponents() {
        try {
            // Register core components
            this.components.set('controls', new ProfessionalControls());
            this.components.set('layouts', new DashboardLayouts());
            this.components.set('notifications', new NotificationSystem());
            this.components.set('modals', new ModalManager());
            this.components.set('sidebar', new SidebarNavigation());
            this.components.set('header', new HeaderControls());
            this.components.set('status', new StatusIndicators());
            this.components.set('responsive', new ResponsiveUtilities());
            this.components.set('themes', new ThemeManager());

            this.initialized = true;
            console.log('✅ UI Components Registry initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize UI Components:', error);
            throw error;
        }
    }

    /**
     * Get component by name
     * @param {string} name - Component name
     * @returns {Object} Component instance
     */
    getComponent(name) {
        if (!this.initialized) {
            throw new Error('UI Components Registry not initialized');
        }
        return this.components.get(name);
    }

    /**
     * Register custom component
     * @param {string} name - Component name
     * @param {Object} component - Component instance
     */
    registerComponent(name, component) {
        this.components.set(name, component);
    }

    /**
     * Set application theme
     * @param {string} theme - Theme name (dark/light)
     */
    setTheme(theme) {
        this.theme = theme;
        const themeManager = this.getComponent('themes');
        if (themeManager) {
            themeManager.applyTheme(theme);
        }
    }

    /**
     * Set application locale
     * @param {string} locale - Locale code
     */
    setLocale(locale) {
        this.locale = locale;
        this.components.forEach(component => {
            if (component.setLocale) {
                component.setLocale(locale);
            }
        });
    }
}

// Global registry instance
const uiRegistry = new UIComponentsRegistry();

// Export components and utilities
export {
    uiRegistry,
    ProfessionalControls,
    DashboardLayouts,
    NotificationSystem,
    ModalManager,
    SidebarNavigation,
    HeaderControls,
    StatusIndicators,
    ResponsiveUtilities,
    ThemeManager
};

// Default export
export default uiRegistry;