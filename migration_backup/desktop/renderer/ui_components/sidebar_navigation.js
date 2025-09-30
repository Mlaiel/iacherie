/**
 * Ainflue Desktop Renderer - Sidebar Navigation
 * Professional sidebar navigation component
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class SidebarNavigation {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.navigation = null;
        this.menuItems = new Map();
        this.activeItem = null;
        this.collapsed = false;
        this.config = {
            collapsible: true,
            width: 250,
            collapsedWidth: 60,
            animationDuration: 300,
            autoCollapse: false,
            breakpoint: 768
        };
        
        this.init();
    }

    /**
     * Initialize sidebar navigation
     */
    init() {
        console.log('🗂️ Initializing Sidebar Navigation v' + this.version);
        
        this.setupStyles();
        this.createNavigation();
        this.setupEventHandlers();
        this.setupResponsiveHandling();
    }

    /**
     * Create navigation structure
     */
    createNavigation() {
        this.navigation = document.createElement('nav');
        this.navigation.className = 'sidebar-nav';
        this.navigation.setAttribute('role', 'navigation');
        this.navigation.setAttribute('aria-label', 'Main navigation');

        // Navigation header
        const header = document.createElement('div');
        header.className = 'sidebar-nav__header';
        header.innerHTML = `
            <div class="sidebar-nav__logo">
                <span class="logo-icon">🎵</span>
                <span class="logo-text">Ainflue</span>
            </div>
            ${this.config.collapsible ? '<button class="sidebar-nav__toggle" title="Toggle sidebar">☰</button>' : ''}
        `;
        
        // Navigation menu
        const menu = document.createElement('div');
        menu.className = 'sidebar-nav__menu';
        
        // Navigation footer
        const footer = document.createElement('div');
        footer.className = 'sidebar-nav__footer';

        this.navigation.appendChild(header);
        this.navigation.appendChild(menu);
        this.navigation.appendChild(footer);

        // Add to page
        const existingSidebar = document.querySelector('.sidebar');
        if (existingSidebar) {
            existingSidebar.appendChild(this.navigation);
        } else {
            document.body.insertBefore(this.navigation, document.body.firstChild);
        }

        // Setup toggle functionality
        this.setupToggle();
    }

    /**
     * Add menu item
     */
    addMenuItem(options = {}) {
        const {
            id = this.generateId(),
            label = '',
            icon = null,
            href = null,
            onClick = null,
            badge = null,
            submenu = [],
            active = false,
            disabled = false,
            group = null,
            position = 'end'
        } = options;

        const menuItem = {
            id,
            label,
            icon,
            href,
            onClick,
            badge,
            submenu,
            active,
            disabled,
            group,
            element: null
        };

        // Create menu item element
        menuItem.element = this.createMenuItemElement(menuItem);
        
        // Add to menu
        const menu = this.navigation.querySelector('.sidebar-nav__menu');
        if (position === 'start') {
            menu.insertBefore(menuItem.element, menu.firstChild);
        } else {
            menu.appendChild(menuItem.element);
        }

        // Store menu item
        this.menuItems.set(id, menuItem);

        // Set as active if specified
        if (active) {
            this.setActive(id);
        }

        return id;
    }

    /**
     * Create menu item element
     */
    createMenuItemElement(menuItem) {
        const item = document.createElement('div');
        item.className = `sidebar-nav__item ${menuItem.disabled ? 'sidebar-nav__item--disabled' : ''}`;
        item.setAttribute('data-id', menuItem.id);

        // Main item content
        const link = document.createElement(menuItem.href ? 'a' : 'button');
        link.className = 'sidebar-nav__link';
        
        if (menuItem.href) {
            link.href = menuItem.href;
        }
        
        if (menuItem.disabled) {
            link.setAttribute('disabled', 'true');
            link.setAttribute('aria-disabled', 'true');
        }

        // Build link content
        let linkContent = '';
        
        if (menuItem.icon) {
            linkContent += `<span class="sidebar-nav__icon">${menuItem.icon}</span>`;
        }
        
        linkContent += `<span class="sidebar-nav__text">${menuItem.label}</span>`;
        
        if (menuItem.badge) {
            linkContent += `<span class="sidebar-nav__badge">${menuItem.badge}</span>`;
        }
        
        if (menuItem.submenu.length > 0) {
            linkContent += '<span class="sidebar-nav__arrow">▶</span>';
        }

        link.innerHTML = linkContent;
        item.appendChild(link);

        // Add submenu if present
        if (menuItem.submenu.length > 0) {
            const submenu = this.createSubmenu(menuItem.submenu);
            item.appendChild(submenu);
            item.classList.add('sidebar-nav__item--has-submenu');
        }

        // Setup event handlers
        this.setupMenuItemEvents(item, menuItem);

        return item;
    }

    /**
     * Create submenu
     */
    createSubmenu(items) {
        const submenu = document.createElement('div');
        submenu.className = 'sidebar-nav__submenu';

        items.forEach(subItem => {
            const subElement = document.createElement('div');
            subElement.className = 'sidebar-nav__subitem';

            const subLink = document.createElement(subItem.href ? 'a' : 'button');
            subLink.className = 'sidebar-nav__sublink';
            
            if (subItem.href) {
                subLink.href = subItem.href;
            }

            subLink.innerHTML = `
                ${subItem.icon ? `<span class="sidebar-nav__icon">${subItem.icon}</span>` : ''}
                <span class="sidebar-nav__text">${subItem.label}</span>
                ${subItem.badge ? `<span class="sidebar-nav__badge">${subItem.badge}</span>` : ''}
            `;

            // Event handling for submenu items
            subLink.addEventListener('click', (e) => {
                if (subItem.onClick) {
                    e.preventDefault();
                    subItem.onClick(subItem, e);
                }
                
                this.emit('submenu-item-click', { item: subItem, event: e });
            });

            subElement.appendChild(subLink);
            submenu.appendChild(subElement);
        });

        return submenu;
    }

    /**
     * Setup menu item event handlers
     */
    setupMenuItemEvents(element, menuItem) {
        const link = element.querySelector('.sidebar-nav__link');
        
        link.addEventListener('click', (e) => {
            if (menuItem.disabled) return;

            // Handle submenu toggle
            if (menuItem.submenu.length > 0) {
                e.preventDefault();
                this.toggleSubmenu(element);
                return;
            }

            // Handle custom click handler
            if (menuItem.onClick) {
                e.preventDefault();
                menuItem.onClick(menuItem, e);
            }

            // Set as active
            this.setActive(menuItem.id);
            
            this.emit('menu-item-click', { item: menuItem, event: e });
        });

        // Hover effects
        element.addEventListener('mouseenter', () => {
            if (this.collapsed) {
                this.showTooltip(element, menuItem.label);
            }
        });

        element.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });
    }

    /**
     * Toggle submenu
     */
    toggleSubmenu(element) {
        const isExpanded = element.classList.contains('sidebar-nav__item--expanded');
        
        // Close other submenus first
        this.navigation.querySelectorAll('.sidebar-nav__item--expanded').forEach(item => {
            if (item !== element) {
                item.classList.remove('sidebar-nav__item--expanded');
            }
        });

        // Toggle current submenu
        element.classList.toggle('sidebar-nav__item--expanded', !isExpanded);
        
        const arrow = element.querySelector('.sidebar-nav__arrow');
        if (arrow) {
            arrow.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(90deg)';
        }
    }

    /**
     * Set active menu item
     */
    setActive(id) {
        // Remove active from all items
        this.navigation.querySelectorAll('.sidebar-nav__item--active').forEach(item => {
            item.classList.remove('sidebar-nav__item--active');
        });

        // Set new active item
        const menuItem = this.menuItems.get(id);
        if (menuItem && menuItem.element) {
            menuItem.element.classList.add('sidebar-nav__item--active');
            this.activeItem = id;
            
            this.emit('active-changed', { activeId: id, item: menuItem });
        }
    }

    /**
     * Update badge for menu item
     */
    updateBadge(id, badge) {
        const menuItem = this.menuItems.get(id);
        if (!menuItem) return;

        menuItem.badge = badge;
        
        const badgeElement = menuItem.element.querySelector('.sidebar-nav__badge');
        if (badgeElement) {
            if (badge) {
                badgeElement.textContent = badge;
                badgeElement.style.display = '';
            } else {
                badgeElement.style.display = 'none';
            }
        }
    }

    /**
     * Remove menu item
     */
    removeMenuItem(id) {
        const menuItem = this.menuItems.get(id);
        if (!menuItem) return;

        if (menuItem.element && menuItem.element.parentNode) {
            menuItem.element.parentNode.removeChild(menuItem.element);
        }

        this.menuItems.delete(id);

        if (this.activeItem === id) {
            this.activeItem = null;
        }
    }

    /**
     * Toggle sidebar collapsed state
     */
    toggle() {
        this.collapsed = !this.collapsed;
        this.navigation.classList.toggle('sidebar-nav--collapsed', this.collapsed);
        
        // Update toggle button
        const toggleBtn = this.navigation.querySelector('.sidebar-nav__toggle');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', this.collapsed ? 'Expand sidebar' : 'Collapse sidebar');
        }

        // Store state
        if (typeof Storage !== 'undefined') {
            localStorage.setItem('sidebar-collapsed', this.collapsed);
        }

        this.emit('collapsed-changed', { collapsed: this.collapsed });
    }

    /**
     * Setup toggle functionality
     */
    setupToggle() {
        const toggleBtn = this.navigation.querySelector('.sidebar-nav__toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggle();
            });
        }

        // Restore state from localStorage
        if (typeof Storage !== 'undefined') {
            const savedState = localStorage.getItem('sidebar-collapsed');
            if (savedState === 'true') {
                this.collapsed = true;
                this.navigation.classList.add('sidebar-nav--collapsed');
            }
        }
    }

    /**
     * Show tooltip for collapsed items
     */
    showTooltip(element, text) {
        this.hideTooltip(); // Remove any existing tooltip

        const tooltip = document.createElement('div');
        tooltip.className = 'sidebar-nav__tooltip';
        tooltip.textContent = text;
        
        const rect = element.getBoundingClientRect();
        tooltip.style.top = rect.top + 'px';
        tooltip.style.left = (rect.right + 10) + 'px';
        
        document.body.appendChild(tooltip);
        this.currentTooltip = tooltip;

        // Show with animation
        requestAnimationFrame(() => {
            tooltip.classList.add('sidebar-nav__tooltip--visible');
        });
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }

    /**
     * Add group separator
     */
    addGroupSeparator(label = '') {
        const separator = document.createElement('div');
        separator.className = 'sidebar-nav__separator';
        
        if (label) {
            separator.innerHTML = `<span class="separator-label">${label}</span>`;
        }

        const menu = this.navigation.querySelector('.sidebar-nav__menu');
        menu.appendChild(separator);

        return separator;
    }

    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Keyboard navigation
        this.navigation.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // Outside click to close submenus
        document.addEventListener('click', (e) => {
            if (!this.navigation.contains(e.target)) {
                this.navigation.querySelectorAll('.sidebar-nav__item--expanded').forEach(item => {
                    item.classList.remove('sidebar-nav__item--expanded');
                });
            }
        });
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboardNavigation(e) {
        const focusedElement = document.activeElement;
        const menuItems = Array.from(this.navigation.querySelectorAll('.sidebar-nav__link'));
        const currentIndex = menuItems.indexOf(focusedElement);

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = (currentIndex + 1) % menuItems.length;
                menuItems[nextIndex].focus();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex === 0 ? menuItems.length - 1 : currentIndex - 1;
                menuItems[prevIndex].focus();
                break;
                
            case 'Enter':
            case ' ':
                e.preventDefault();
                focusedElement.click();
                break;
                
            case 'Escape':
                // Close expanded submenus
                this.navigation.querySelectorAll('.sidebar-nav__item--expanded').forEach(item => {
                    item.classList.remove('sidebar-nav__item--expanded');
                });
                break;
        }
    }

    /**
     * Setup responsive handling
     */
    setupResponsiveHandling() {
        const mediaQuery = window.matchMedia(`(max-width: ${this.config.breakpoint}px)`);
        
        const handleResize = (e) => {
            if (e.matches && this.config.autoCollapse) {
                // Mobile view - auto collapse
                this.collapsed = true;
                this.navigation.classList.add('sidebar-nav--collapsed');
            }
        };

        mediaQuery.addListener(handleResize);
        handleResize(mediaQuery); // Initial check
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('sidebar-navigation-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'sidebar-navigation-styles';
        styles.textContent = `
            /* Sidebar Navigation Styles */
            .sidebar-nav {
                width: ${this.config.width}px;
                height: 100vh;
                background: #374151;
                border-right: 1px solid #4b5563;
                display: flex;
                flex-direction: column;
                transition: width ${this.config.animationDuration}ms ease;
                position: relative;
                z-index: 100;
            }
            
            .sidebar-nav--collapsed {
                width: ${this.config.collapsedWidth}px;
            }
            
            .sidebar-nav__header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 20px;
                border-bottom: 1px solid #4b5563;
                background: #1f2937;
            }
            
            .sidebar-nav__logo {
                display: flex;
                align-items: center;
                gap: 12px;
                color: white;
                font-weight: 600;
                font-size: 1.2rem;
            }
            
            .logo-icon {
                font-size: 1.5rem;
                flex-shrink: 0;
            }
            
            .sidebar-nav--collapsed .logo-text {
                display: none;
            }
            
            .sidebar-nav__toggle {
                background: transparent;
                border: none;
                color: #9ca3af;
                cursor: pointer;
                padding: 8px;
                border-radius: 4px;
                font-size: 16px;
                transition: all 0.2s;
            }
            
            .sidebar-nav__toggle:hover {
                background: #4b5563;
                color: white;
            }
            
            .sidebar-nav__menu {
                flex: 1;
                overflow-y: auto;
                padding: 8px 0;
            }
            
            .sidebar-nav__item {
                margin: 2px 8px;
                border-radius: 6px;
                overflow: hidden;
            }
            
            .sidebar-nav__link {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                color: #d1d5db;
                text-decoration: none;
                border: none;
                background: transparent;
                width: 100%;
                text-align: left;
                cursor: pointer;
                border-radius: 6px;
                transition: all 0.2s;
                font-size: 14px;
            }
            
            .sidebar-nav__link:hover {
                background: #4b5563;
                color: white;
            }
            
            .sidebar-nav__item--active .sidebar-nav__link {
                background: #3b82f6;
                color: white;
            }
            
            .sidebar-nav__item--disabled .sidebar-nav__link {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .sidebar-nav__icon {
                font-size: 18px;
                flex-shrink: 0;
                width: 20px;
                text-align: center;
            }
            
            .sidebar-nav__text {
                flex: 1;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            .sidebar-nav--collapsed .sidebar-nav__text {
                display: none;
            }
            
            .sidebar-nav__badge {
                background: #ef4444;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 18px;
                text-align: center;
                line-height: 1.2;
            }
            
            .sidebar-nav--collapsed .sidebar-nav__badge {
                position: absolute;
                top: 8px;
                right: 8px;
                transform: scale(0.8);
            }
            
            .sidebar-nav__arrow {
                font-size: 12px;
                transition: transform 0.2s;
                color: #9ca3af;
            }
            
            .sidebar-nav--collapsed .sidebar-nav__arrow {
                display: none;
            }
            
            .sidebar-nav__submenu {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
                background: #1f2937;
                margin: 0 -8px;
            }
            
            .sidebar-nav__item--expanded .sidebar-nav__submenu {
                max-height: 300px;
                padding: 4px 0;
            }
            
            .sidebar-nav__subitem {
                margin: 0;
            }
            
            .sidebar-nav__sublink {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 16px 8px 48px;
                color: #9ca3af;
                text-decoration: none;
                border: none;
                background: transparent;
                width: 100%;
                text-align: left;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 13px;
            }
            
            .sidebar-nav__sublink:hover {
                background: #374151;
                color: #d1d5db;
            }
            
            .sidebar-nav__separator {
                margin: 16px 16px 8px 16px;
                padding-top: 16px;
                border-top: 1px solid #4b5563;
            }
            
            .separator-label {
                color: #9ca3af;
                font-size: 11px;
                text-transform: uppercase;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            .sidebar-nav--collapsed .separator-label {
                display: none;
            }
            
            .sidebar-nav__footer {
                padding: 16px;
                border-top: 1px solid #4b5563;
                background: #1f2937;
            }
            
            .sidebar-nav__tooltip {
                position: fixed;
                background: #1f2937;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                z-index: 1000;
                opacity: 0;
                transform: translateX(-10px);
                transition: all 0.2s ease;
                pointer-events: none;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                white-space: nowrap;
            }
            
            .sidebar-nav__tooltip--visible {
                opacity: 1;
                transform: translateX(0);
            }
            
            .sidebar-nav__tooltip::before {
                content: '';
                position: absolute;
                left: -6px;
                top: 50%;
                transform: translateY(-50%);
                border: 6px solid transparent;
                border-right-color: #1f2937;
            }
            
            @media (max-width: ${this.config.breakpoint}px) {
                .sidebar-nav {
                    position: fixed;
                    top: 0;
                    left: 0;
                    z-index: 1000;
                    transform: translateX(-100%);
                    transition: transform 0.3s ease;
                }
                
                .sidebar-nav--mobile-open {
                    transform: translateX(0);
                }
                
                .sidebar-nav--collapsed {
                    width: ${this.config.width}px;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'nav-item-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Get active item
     */
    getActiveItem() {
        return this.activeItem;
    }

    /**
     * Get all menu items
     */
    getMenuItems() {
        return Array.from(this.menuItems.values());
    }

    /**
     * Configure navigation
     */
    configure(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }

    /**
     * Destroy navigation
     */
    destroy() {
        if (this.navigation && this.navigation.parentNode) {
            this.navigation.parentNode.removeChild(this.navigation);
        }
        
        this.hideTooltip();
        this.menuItems.clear();
        
        // Remove styles
        const styles = document.getElementById('sidebar-navigation-styles');
        if (styles) styles.remove();
        
        console.log('🗂️ Sidebar Navigation destroyed');
    }
}

// Export for ES6 modules
export default SidebarNavigation;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.SidebarNavigation = SidebarNavigation;
}