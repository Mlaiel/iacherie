/**
 * Ainflue Desktop - Dashboard Layouts
 * Layouts dashboard adaptatifs
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class DashboardLayouts {
    constructor() {
        this.layouts = new Map();
        this.currentLayout = 'default';
        this.breakpoints = {
            mobile: 768,
            tablet: 1024,
            desktop: 1440,
            ultrawide: 1920
        };
        
        this.initializeLayouts();
        this.setupResponsiveListeners();
    }

    initializeLayouts() {
        // Default professional layout
        this.layouts.set('default', {
            name: 'Professional Studio',
            sidebar: { width: 250, position: 'left', collapsible: true },
            header: { height: 60, fixed: true },
            main: { padding: 30, overflow: 'auto' },
            panels: ['timeline', 'mixer', 'properties'],
            grid: 'sidebar-main',
            responsive: true
        });

        // Musician-focused layout
        this.layouts.set('musician', {
            name: 'Audio Production',
            sidebar: { width: 200, position: 'left' },
            panels: ['waveform', 'mixer', 'effects', 'timeline'],
            grid: 'audio-centric',
            responsive: true
        });

        // Photographer layout
        this.layouts.set('photographer', {
            name: 'Photo Studio',
            sidebar: { width: 220, position: 'left' },
            panels: ['gallery', 'editor', 'properties', 'histogram'],
            grid: 'photo-centric',
            responsive: true
        });
    }

    setupResponsiveListeners() {
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    applyLayout(layoutName, options = {}) {
        const layout = this.layouts.get(layoutName);
        if (!layout) {
            console.error(`Layout '${layoutName}' not found`);
            return;
        }

        this.currentLayout = layoutName;
        this.applyCSSGrid(layout);
        this.setupPanels(layout);
        
        if (layout.responsive) {
            this.applyResponsiveBehavior(layout);
        }

        this.dispatchLayoutEvent('layoutChanged', { layout: layoutName, config: layout });
        console.log(`✅ Applied layout: ${layout.name}`);
    }

    applyCSSGrid(layout) {
        const container = document.querySelector('.app-container') || document.body;
        container.classList.remove(...Array.from(container.classList).filter(c => c.startsWith('layout-')));
        container.classList.add(`layout-${this.currentLayout}`);
        container.style.display = 'grid';
    }

    setupPanels(layout) {
        layout.panels.forEach(panelName => {
            this.createPanel(panelName, layout);
        });
    }

    createPanel(panelName, layout) {
        let panel = document.querySelector(`[data-panel="${panelName}"]`);
        
        if (!panel) {
            panel = document.createElement('div');
            panel.className = `dashboard-panel panel-${panelName}`;
            panel.setAttribute('data-panel', panelName);
            panel.innerHTML = `
                <div class="panel-header">
                    <span class="panel-title">${this.formatPanelName(panelName)}</span>
                </div>
                <div class="panel-content">
                    <div class="placeholder">${this.formatPanelName(panelName)} Content</div>
                </div>
            `;
            
            const container = document.querySelector('.app-container') || document.body;
            container.appendChild(panel);
        }

        panel.style.gridArea = panelName;
    }

    formatPanelName(name) {
        return name.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    handleResize() {
        const layout = this.layouts.get(this.currentLayout);
        if (layout && layout.responsive) {
            this.applyResponsiveBehavior(layout);
        }
    }

    applyResponsiveBehavior(layout) {
        const width = window.innerWidth;
        const container = document.querySelector('.app-container');
        
        if (width < this.breakpoints.mobile) {
            container.classList.add('mobile-layout');
        } else {
            container.classList.remove('mobile-layout');
        }
    }

    dispatchLayoutEvent(eventType, data) {
        const event = new CustomEvent('dashboardLayout', {
            detail: { type: eventType, ...data }
        });
        document.dispatchEvent(event);
    }

    getCurrentLayout() {
        return this.currentLayout;
    }

    getAvailableLayouts() {
        return Array.from(this.layouts.keys());
    }
}

export default DashboardLayouts;