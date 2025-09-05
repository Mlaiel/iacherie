/**
 * Ainflue Desktop - Sidebar Navigation
 * Navigation sidebar dynamique
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class SidebarNavigation {
    constructor() {
        this.items = new Map();
        this.activeItem = null;
        this.collapsed = false;
        
        this.initializeNavigation();
        this.createSidebar();
    }

    initializeNavigation() {
        // Professional navigation items for content creators
        this.items.set('home', {
            icon: '🏠',
            label: 'Home',
            action: 'showHome',
            category: 'main'
        });

        this.items.set('timeline', {
            icon: '🎬',
            label: 'Timeline',
            action: 'showTimeline',
            category: 'editing'
        });

        this.items.set('studio', {
            icon: '🎨',
            label: 'AI Studio',
            action: 'showStudio',
            category: 'ai'
        });

        this.items.set('mixer', {
            icon: '🎛️',
            label: 'Audio Mixer',
            action: 'showMixer',
            category: 'audio'
        });

        this.items.set('protection', {
            icon: '🛡️',
            label: 'Protection',
            action: 'showProtection',
            category: 'security'
        });

        this.items.set('analytics', {
            icon: '📊',
            label: 'Analytics',
            action: 'showAnalytics',
            category: 'business'
        });

        this.items.set('monetization', {
            icon: '💰',
            label: 'Monetization',
            action: 'showMonetization',
            category: 'business'
        });

        this.items.set('collaboration', {
            icon: '🤝',
            label: 'Collaboration',
            action: 'showCollaboration',
            category: 'social'
        });

        this.items.set('distribution', {
            icon: '📡',
            label: 'Distribution',
            action: 'showDistribution',
            category: 'publishing'
        });

        this.items.set('settings', {
            icon: '⚙️',
            label: 'Settings',
            action: 'showSettings',
            category: 'system'
        });
    }

    createSidebar() {
        // Find or create sidebar
        let sidebar = document.querySelector('.sidebar');
        if (!sidebar) {
            sidebar = document.createElement('div');
            sidebar.className = 'sidebar';
            sidebar.style.cssText = `
                width: 250px;
                background: rgba(55, 65, 81, 0.8);
                backdrop-filter: blur(10px);
                border-right: 1px solid rgba(75, 85, 99, 0.3);
                padding: 20px;
                height: 100vh;
                overflow-y: auto;
                transition: all 0.3s ease;
            `;
            
            const container = document.querySelector('.app-container') || document.body;
            container.insertBefore(sidebar, container.firstChild);
        }

        this.sidebar = sidebar;
        this.renderNavigation();
    }

    renderNavigation() {
        this.sidebar.innerHTML = `
            <div class="sidebar-header" style="margin-bottom: 30px;">
                <div class="logo" style="
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #3B82F6;
                    text-align: center;
                ">🎵 Ainflue Studio</div>
            </div>
            <nav class="sidebar-nav">
                ${this.renderNavigationItems()}
            </nav>
            <div class="sidebar-footer" style="
                margin-top: auto;
                padding-top: 20px;
                border-top: 1px solid rgba(75, 85, 99, 0.3);
            ">
                <button class="collapse-btn" style="
                    width: 100%;
                    padding: 8px;
                    background: rgba(59, 130, 246, 0.1);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    color: #3B82F6;
                    border-radius: 6px;
                    cursor: pointer;
                ">
                    ${this.collapsed ? '→' : '←'} ${this.collapsed ? 'Expand' : 'Collapse'}
                </button>
            </div>
        `;

        this.setupEventListeners();
    }

    renderNavigationItems() {
        const categories = this.groupItemsByCategory();
        let html = '';

        Object.entries(categories).forEach(([category, items]) => {
            if (category !== 'main') {
                html += `<div class="nav-category" style="
                    margin: 20px 0 10px 0;
                    font-size: 0.8rem;
                    color: #9CA3AF;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                ">${category}</div>`;
            }

            items.forEach(([id, item]) => {
                html += `
                    <div class="nav-item ${this.activeItem === id ? 'active' : ''}" 
                         data-item="${id}" 
                         style="
                        padding: 12px 16px;
                        margin: 4px 0;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.2s;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        ${this.activeItem === id ? 
                            'background: rgba(59, 130, 246, 0.2); color: #3B82F6;' : 
                            'color: #D1D5DB;'
                        }
                    ">
                        <span class="nav-icon">${item.icon}</span>
                        <span class="nav-label" style="${this.collapsed ? 'display: none;' : ''}">${item.label}</span>
                    </div>
                `;
            });
        });

        return html;
    }

    groupItemsByCategory() {
        const categories = {};
        
        this.items.forEach((item, id) => {
            if (!categories[item.category]) {
                categories[item.category] = [];
            }
            categories[item.category].push([id, item]);
        });

        return categories;
    }

    setupEventListeners() {
        // Navigation item clicks
        this.sidebar.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const itemId = item.getAttribute('data-item');
                this.selectItem(itemId);
            });

            item.addEventListener('mouseenter', () => {
                if (!item.classList.contains('active')) {
                    item.style.background = 'rgba(59, 130, 246, 0.1)';
                }
            });

            item.addEventListener('mouseleave', () => {
                if (!item.classList.contains('active')) {
                    item.style.background = 'transparent';
                }
            });
        });

        // Collapse button
        const collapseBtn = this.sidebar.querySelector('.collapse-btn');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                this.toggleCollapse();
            });
        }
    }

    selectItem(itemId) {
        const item = this.items.get(itemId);
        if (!item) return;

        // Update active state
        this.activeItem = itemId;
        
        // Update visual state
        this.sidebar.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
            navItem.style.background = 'transparent';
            navItem.style.color = '#D1D5DB';
        });

        const activeElement = this.sidebar.querySelector(`[data-item="${itemId}"]`);
        if (activeElement) {
            activeElement.classList.add('active');
            activeElement.style.background = 'rgba(59, 130, 246, 0.2)';
            activeElement.style.color = '#3B82F6';
        }

        // Dispatch navigation event
        this.dispatchNavigationEvent(item.action, itemId);
    }

    toggleCollapse() {
        this.collapsed = !this.collapsed;
        
        if (this.collapsed) {
            this.sidebar.style.width = '80px';
            this.sidebar.querySelectorAll('.nav-label').forEach(label => {
                label.style.display = 'none';
            });
            this.sidebar.querySelector('.logo').style.display = 'none';
            this.sidebar.querySelectorAll('.nav-category').forEach(cat => {
                cat.style.display = 'none';
            });
        } else {
            this.sidebar.style.width = '250px';
            this.sidebar.querySelectorAll('.nav-label').forEach(label => {
                label.style.display = 'block';
            });
            this.sidebar.querySelector('.logo').style.display = 'block';
            this.sidebar.querySelectorAll('.nav-category').forEach(cat => {
                cat.style.display = 'block';
            });
        }

        // Update collapse button
        const collapseBtn = this.sidebar.querySelector('.collapse-btn');
        if (collapseBtn) {
            collapseBtn.innerHTML = `${this.collapsed ? '→' : '←'} ${this.collapsed ? 'Expand' : 'Collapse'}`;
        }

        this.dispatchNavigationEvent('sidebarToggle', this.collapsed);
    }

    dispatchNavigationEvent(action, data) {
        const event = new CustomEvent('sidebarNavigation', {
            detail: { action, data }
        });
        document.dispatchEvent(event);
    }

    addNavigationItem(id, config) {
        this.items.set(id, config);
        this.renderNavigation();
    }

    removeNavigationItem(id) {
        this.items.delete(id);
        this.renderNavigation();
    }

    getActiveItem() {
        return this.activeItem;
    }

    setActiveItem(itemId) {
        this.selectItem(itemId);
    }

    isCollapsed() {
        return this.collapsed;
    }

    show() {
        this.sidebar.style.display = 'block';
    }

    hide() {
        this.sidebar.style.display = 'none';
    }
}

export default SidebarNavigation;