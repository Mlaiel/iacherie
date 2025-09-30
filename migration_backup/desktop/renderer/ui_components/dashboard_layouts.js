/**
 * Ainflue Desktop Renderer - Dashboard Layouts
 * Responsive dashboard layout system
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class DashboardLayouts {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.layouts = new Map();
        this.currentLayout = null;
        this.breakpoints = {
            xs: 480,
            sm: 768,
            md: 1024,
            lg: 1280,
            xl: 1536
        };
        this.gridConfig = {
            columns: 12,
            gap: '20px',
            padding: '20px'
        };
        
        this.init();
    }

    /**
     * Initialize dashboard layout system
     */
    init() {
        console.log('📊 Initializing Dashboard Layouts v' + this.version);
        
        this.createLayoutTemplates();
        this.setupResponsiveSystem();
        this.setupLayoutStyles();
        this.detectScreenSize();
        
        // Listen for window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
    }

    /**
     * Create dashboard layout templates
     */
    createLayoutTemplates() {
        // Single Column Layout (Mobile)
        this.layouts.set('single-column', {
            name: 'Single Column',
            description: 'Single column layout for mobile devices',
            breakpoints: ['xs', 'sm'],
            grid: {
                areas: '"header" "main" "footer"',
                rows: 'auto 1fr auto',
                columns: '1fr'
            },
            panels: {
                header: { area: 'header', span: 12 },
                main: { area: 'main', span: 12 },
                footer: { area: 'footer', span: 12 }
            }
        });

        // Two Column Layout (Tablet)
        this.layouts.set('two-column', {
            name: 'Two Column',
            description: 'Two column layout for tablets',
            breakpoints: ['md'],
            grid: {
                areas: '"header header" "sidebar main" "footer footer"',
                rows: 'auto 1fr auto',
                columns: '250px 1fr'
            },
            panels: {
                header: { area: 'header', span: 12 },
                sidebar: { area: 'sidebar', span: 3 },
                main: { area: 'main', span: 9 },
                footer: { area: 'footer', span: 12 }
            }
        });

        // Three Column Layout (Desktop)
        this.layouts.set('three-column', {
            name: 'Three Column',
            description: 'Three column layout for desktop',
            breakpoints: ['lg', 'xl'],
            grid: {
                areas: '"header header header" "sidebar main aside" "footer footer footer"',
                rows: 'auto 1fr auto',
                columns: '250px 1fr 300px'
            },
            panels: {
                header: { area: 'header', span: 12 },
                sidebar: { area: 'sidebar', span: 2 },
                main: { area: 'main', span: 8 },
                aside: { area: 'aside', span: 2 },
                footer: { area: 'footer', span: 12 }
            }
        });

        // Professional Studio Layout
        this.layouts.set('studio-layout', {
            name: 'Studio Layout',
            description: 'Professional studio interface layout',
            breakpoints: ['lg', 'xl'],
            grid: {
                areas: '"header header header header" "sidebar timeline timeline properties" "sidebar timeline timeline properties" "footer footer footer footer"',
                rows: 'auto 1fr 1fr auto',
                columns: '200px 1fr 1fr 250px'
            },
            panels: {
                header: { area: 'header', span: 12 },
                sidebar: { area: 'sidebar', span: 2 },
                timeline: { area: 'timeline', span: 8 },
                properties: { area: 'properties', span: 2 },
                footer: { area: 'footer', span: 12 }
            }
        });

        // Analytics Dashboard Layout
        this.layouts.set('analytics-dashboard', {
            name: 'Analytics Dashboard',
            description: 'Analytics-focused dashboard layout',
            breakpoints: ['md', 'lg', 'xl'],
            grid: {
                areas: '"header header header" "metrics metrics metrics" "charts charts sidebar" "footer footer footer"',
                rows: 'auto auto 1fr auto',
                columns: '1fr 1fr 300px'
            },
            panels: {
                header: { area: 'header', span: 12 },
                metrics: { area: 'metrics', span: 12 },
                charts: { area: 'charts', span: 8 },
                sidebar: { area: 'sidebar', span: 4 },
                footer: { area: 'footer', span: 12 }
            }
        });
    }

    /**
     * Apply layout to dashboard
     */
    applyLayout(layoutName, container = document.body) {
        const layout = this.layouts.get(layoutName);
        if (!layout) {
            console.error('Layout not found:', layoutName);
            return false;
        }

        console.log('📊 Applying layout:', layout.name);

        // Remove existing layout classes
        container.classList.remove(...Array.from(container.classList).filter(c => c.startsWith('layout-')));
        
        // Add new layout class
        container.classList.add(`layout-${layoutName}`);

        // Create grid container if not exists
        let gridContainer = container.querySelector('.dashboard-grid');
        if (!gridContainer) {
            gridContainer = document.createElement('div');
            gridContainer.className = 'dashboard-grid';
            
            // Move existing content to grid
            while (container.firstChild) {
                gridContainer.appendChild(container.firstChild);
            }
            
            container.appendChild(gridContainer);
        }

        // Apply grid styles
        this.applyGridStyles(gridContainer, layout);

        // Create layout panels
        this.createLayoutPanels(gridContainer, layout);

        this.currentLayout = layoutName;
        this.emit('layout-applied', { layout: layoutName, config: layout });

        return true;
    }

    /**
     * Apply grid styles to container
     */
    applyGridStyles(container, layout) {
        const { grid } = layout;
        
        container.style.display = 'grid';
        container.style.gridTemplateAreas = grid.areas;
        container.style.gridTemplateRows = grid.rows;
        container.style.gridTemplateColumns = grid.columns;
        container.style.gap = this.gridConfig.gap;
        container.style.padding = this.gridConfig.padding;
        container.style.height = '100vh';
    }

    /**
     * Create layout panels
     */
    createLayoutPanels(container, layout) {
        const { panels } = layout;

        Object.entries(panels).forEach(([panelName, config]) => {
            let panel = container.querySelector(`[data-panel="${panelName}"]`);
            
            if (!panel) {
                panel = document.createElement('div');
                panel.setAttribute('data-panel', panelName);
                panel.className = `dashboard-panel panel-${panelName}`;
                container.appendChild(panel);
            }

            // Apply panel styles
            panel.style.gridArea = config.area;
            panel.classList.add(`span-${config.span}`);

            // Add panel content placeholder if empty
            if (!panel.hasChildNodes()) {
                this.addPanelPlaceholder(panel, panelName);
            }
        });
    }

    /**
     * Add placeholder content to panels
     */
    addPanelPlaceholder(panel, panelName) {
        const placeholder = document.createElement('div');
        placeholder.className = 'panel-placeholder';
        
        const icon = this.getPanelIcon(panelName);
        const title = panelName.charAt(0).toUpperCase() + panelName.slice(1);
        
        placeholder.innerHTML = `
            <div class="placeholder-content">
                <span class="placeholder-icon">${icon}</span>
                <h3 class="placeholder-title">${title}</h3>
                <p class="placeholder-description">This ${panelName} panel is ready for content</p>
            </div>
        `;
        
        panel.appendChild(placeholder);
    }

    /**
     * Get icon for panel type
     */
    getPanelIcon(panelName) {
        const icons = {
            header: '🎯',
            sidebar: '🗂️',
            main: '📊',
            aside: '⚙️',
            footer: 'ℹ️',
            timeline: '🎬',
            properties: '🔧',
            metrics: '📈',
            charts: '📊'
        };
        
        return icons[panelName] || '📦';
    }

    /**
     * Create responsive widget
     */
    createWidget(options = {}) {
        const {
            title = 'Widget',
            content = '',
            span = 4,
            height = 'auto',
            resizable = true,
            collapsible = true,
            removable = false
        } = options;

        const widget = document.createElement('div');
        widget.className = `dashboard-widget span-${span}`;
        widget.style.height = height;

        widget.innerHTML = `
            <div class="widget-header">
                <h3 class="widget-title">${title}</h3>
                <div class="widget-controls">
                    ${collapsible ? '<button class="widget-btn collapse-btn" title="Collapse">−</button>' : ''}
                    ${resizable ? '<button class="widget-btn resize-btn" title="Resize">⤡</button>' : ''}
                    ${removable ? '<button class="widget-btn remove-btn" title="Remove">×</button>' : ''}
                </div>
            </div>
            <div class="widget-content">
                ${content}
            </div>
        `;

        // Add widget controls
        this.setupWidgetControls(widget);

        return widget;
    }

    /**
     * Setup widget controls
     */
    setupWidgetControls(widget) {
        const collapseBtn = widget.querySelector('.collapse-btn');
        const resizeBtn = widget.querySelector('.resize-btn');
        const removeBtn = widget.querySelector('.remove-btn');
        const content = widget.querySelector('.widget-content');

        // Collapse functionality
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                const isCollapsed = widget.classList.toggle('widget-collapsed');
                collapseBtn.textContent = isCollapsed ? '+' : '−';
                collapseBtn.title = isCollapsed ? 'Expand' : 'Collapse';
            });
        }

        // Resize functionality
        if (resizeBtn) {
            resizeBtn.addEventListener('click', () => {
                this.showResizeDialog(widget);
            });
        }

        // Remove functionality
        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                if (confirm('Remove this widget?')) {
                    widget.remove();
                    this.emit('widget-removed', { widget });
                }
            });
        }

        // Make widget draggable
        this.makeWidgetDraggable(widget);
    }

    /**
     * Make widget draggable
     */
    makeWidgetDraggable(widget) {
        const header = widget.querySelector('.widget-header');
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        header.style.cursor = 'move';

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            
            const rect = widget.getBoundingClientRect();
            startLeft = rect.left;
            startTop = rect.top;

            widget.style.position = 'absolute';
            widget.style.zIndex = '1000';
            widget.classList.add('dragging');

            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;

            widget.style.left = (startLeft + deltaX) + 'px';
            widget.style.top = (startTop + deltaY) + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                widget.classList.remove('dragging');
                
                // Snap to grid or reset position
                setTimeout(() => {
                    widget.style.position = '';
                    widget.style.left = '';
                    widget.style.top = '';
                    widget.style.zIndex = '';
                }, 100);
            }
        });
    }

    /**
     * Setup responsive system
     */
    setupResponsiveSystem() {
        // Create media query listeners
        Object.entries(this.breakpoints).forEach(([name, width]) => {
            const mediaQuery = window.matchMedia(`(min-width: ${width}px)`);
            
            mediaQuery.addListener((e) => {
                this.handleBreakpointChange(name, e.matches);
            });
            
            // Initial check
            this.handleBreakpointChange(name, mediaQuery.matches);
        });
    }

    /**
     * Handle breakpoint changes
     */
    handleBreakpointChange(breakpoint, matches) {
        document.body.classList.toggle(`bp-${breakpoint}`, matches);
        
        if (matches) {
            this.currentBreakpoint = breakpoint;
            this.autoSelectLayout();
        }
    }

    /**
     * Auto-select appropriate layout based on screen size
     */
    autoSelectLayout() {
        const width = window.innerWidth;
        let selectedLayout = 'single-column';

        if (width >= this.breakpoints.xl) {
            selectedLayout = 'three-column';
        } else if (width >= this.breakpoints.lg) {
            selectedLayout = 'two-column';
        } else if (width >= this.breakpoints.md) {
            selectedLayout = 'two-column';
        }

        if (this.currentLayout !== selectedLayout) {
            this.applyLayout(selectedLayout);
        }
    }

    /**
     * Detect current screen size
     */
    detectScreenSize() {
        const width = window.innerWidth;
        
        if (width >= this.breakpoints.xl) return 'xl';
        if (width >= this.breakpoints.lg) return 'lg';
        if (width >= this.breakpoints.md) return 'md';
        if (width >= this.breakpoints.sm) return 'sm';
        return 'xs';
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const newSize = this.detectScreenSize();
        this.autoSelectLayout();
        this.emit('screen-size-changed', { size: newSize });
    }

    /**
     * Setup layout styles
     */
    setupLayoutStyles() {
        if (document.getElementById('dashboard-layouts-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'dashboard-layouts-styles';
        styles.textContent = `
            /* Dashboard Layout Styles */
            .dashboard-grid {
                width: 100%;
                min-height: 100vh;
                background: #f8fafc;
            }
            
            .dashboard-panel {
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            
            .panel-placeholder {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                text-align: center;
                color: #6b7280;
            }
            
            .placeholder-content {
                max-width: 200px;
            }
            
            .placeholder-icon {
                font-size: 2rem;
                display: block;
                margin-bottom: 1rem;
            }
            
            .placeholder-title {
                margin: 0 0 0.5rem 0;
                font-size: 1.25rem;
                font-weight: 600;
                color: #374151;
            }
            
            .placeholder-description {
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.4;
            }
            
            .dashboard-widget {
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-bottom: 1rem;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .dashboard-widget:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            .widget-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 1rem 1.25rem;
                border-bottom: 1px solid #e5e7eb;
                background: #f9fafb;
            }
            
            .widget-title {
                margin: 0;
                font-size: 1rem;
                font-weight: 600;
                color: #111827;
            }
            
            .widget-controls {
                display: flex;
                gap: 0.5rem;
            }
            
            .widget-btn {
                width: 24px;
                height: 24px;
                border: none;
                background: transparent;
                color: #6b7280;
                cursor: pointer;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .widget-btn:hover {
                background: #e5e7eb;
                color: #374151;
            }
            
            .widget-content {
                padding: 1.25rem;
                flex: 1;
            }
            
            .widget-collapsed .widget-content {
                display: none;
            }
            
            .dragging {
                opacity: 0.8;
                transform: rotate(2deg);
            }
            
            /* Responsive spans */
            @media (max-width: 768px) {
                .dashboard-widget {
                    grid-column: 1 / -1;
                }
            }
            
            /* Grid spans */
            .span-1 { grid-column: span 1; }
            .span-2 { grid-column: span 2; }
            .span-3 { grid-column: span 3; }
            .span-4 { grid-column: span 4; }
            .span-6 { grid-column: span 6; }
            .span-8 { grid-column: span 8; }
            .span-12 { grid-column: span 12; }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Debounce utility
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Get available layouts
     */
    getAvailableLayouts() {
        return Array.from(this.layouts.entries()).map(([key, layout]) => ({
            key,
            name: layout.name,
            description: layout.description,
            breakpoints: layout.breakpoints
        }));
    }

    /**
     * Get current layout
     */
    getCurrentLayout() {
        return this.currentLayout;
    }

    /**
     * Destroy layout system
     */
    destroy() {
        this.layouts.clear();
        this.currentLayout = null;
        
        // Remove styles
        const styles = document.getElementById('dashboard-layouts-styles');
        if (styles) styles.remove();
        
        console.log('📊 Dashboard Layouts destroyed');
    }
}

// Export for ES6 modules
export default DashboardLayouts;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.DashboardLayouts = DashboardLayouts;
}