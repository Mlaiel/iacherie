/**
 * Ainflue Desktop Renderer - Header Controls
 * Professional header control components
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class HeaderControls {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.controls = new Map();
        this.header = null;
        
        this.init();
    }

    /**
     * Initialize header controls
     */
    init() {
        console.log('🎯 Initializing Header Controls v' + this.version);
        
        this.setupStyles();
        this.createHeaderStructure();
        this.addDefaultControls();
    }

    /**
     * Create header structure
     */
    createHeaderStructure() {
        this.header = document.createElement('header');
        this.header.className = 'app-header';
        this.header.innerHTML = `
            <div class="header-left">
                <div class="header-brand"></div>
                <div class="header-breadcrumbs"></div>
            </div>
            <div class="header-center">
                <div class="header-search"></div>
            </div>
            <div class="header-right">
                <div class="header-actions"></div>
                <div class="header-user"></div>
            </div>
        `;
        
        // Insert at top of page
        document.body.insertBefore(this.header, document.body.firstChild);
    }

    /**
     * Add default controls
     */
    addDefaultControls() {
        // Search control
        this.addSearch({
            placeholder: 'Search projects, files, or content...',
            onSearch: (query) => console.log('Search:', query)
        });

        // Action buttons
        this.addAction({
            id: 'new-project',
            icon: '📁',
            label: 'New Project',
            onClick: () => console.log('New project')
        });

        this.addAction({
            id: 'import',
            icon: '📤',
            label: 'Import',
            onClick: () => console.log('Import content')
        });

        // User menu
        this.addUserMenu({
            name: 'User',
            avatar: '👤',
            menu: [
                { label: 'Profile', onClick: () => console.log('Profile') },
                { label: 'Settings', onClick: () => console.log('Settings') },
                { type: 'separator' },
                { label: 'Sign Out', onClick: () => console.log('Sign out') }
            ]
        });
    }

    /**
     * Add search functionality
     */
    addSearch(options = {}) {
        const {
            placeholder = 'Search...',
            onSearch = null,
            suggestions = [],
            shortcuts = true
        } = options;

        const searchContainer = this.header.querySelector('.header-search');
        searchContainer.innerHTML = `
            <div class="search-box">
                <input 
                    type="text" 
                    class="search-input" 
                    placeholder="${placeholder}"
                    autocomplete="off"
                />
                <button class="search-button" title="Search">🔍</button>
                ${shortcuts ? '<div class="search-shortcut">⌘K</div>' : ''}
                <div class="search-suggestions hidden"></div>
            </div>
        `;

        const input = searchContainer.querySelector('.search-input');
        const button = searchContainer.querySelector('.search-button');
        const suggestionsContainer = searchContainer.querySelector('.search-suggestions');

        // Search functionality
        const performSearch = () => {
            const query = input.value.trim();
            if (query && onSearch) {
                onSearch(query);
            }
        };

        // Event listeners
        button.addEventListener('click', performSearch);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });

        // Global search shortcut
        if (shortcuts) {
            document.addEventListener('keydown', (e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    input.focus();
                }
            });
        }

        // Suggestions handling
        if (suggestions.length > 0) {
            this.setupSearchSuggestions(input, suggestionsContainer, suggestions, onSearch);
        }
    }

    /**
     * Setup search suggestions
     */
    setupSearchSuggestions(input, container, suggestions, onSearch) {
        let currentIndex = -1;

        input.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();
            
            if (query.length < 2) {
                container.classList.add('hidden');
                return;
            }

            const filtered = suggestions.filter(item => 
                item.label.toLowerCase().includes(query) ||
                (item.keywords && item.keywords.some(k => k.toLowerCase().includes(query)))
            );

            if (filtered.length === 0) {
                container.classList.add('hidden');
                return;
            }

            // Render suggestions
            container.innerHTML = filtered.map((item, index) => `
                <div class="suggestion-item" data-index="${index}">
                    ${item.icon ? `<span class="suggestion-icon">${item.icon}</span>` : ''}
                    <span class="suggestion-label">${this.highlightMatch(item.label, query)}</span>
                    ${item.category ? `<span class="suggestion-category">${item.category}</span>` : ''}
                </div>
            `).join('');

            container.classList.remove('hidden');
            currentIndex = -1;

            // Add click handlers
            container.querySelectorAll('.suggestion-item').forEach((item, index) => {
                item.addEventListener('click', () => {
                    const suggestion = filtered[index];
                    input.value = suggestion.value || suggestion.label;
                    container.classList.add('hidden');
                    if (onSearch) onSearch(suggestion.value || suggestion.label);
                });
            });
        });

        // Keyboard navigation for suggestions
        input.addEventListener('keydown', (e) => {
            const items = container.querySelectorAll('.suggestion-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentIndex = Math.min(currentIndex + 1, items.length - 1);
                this.updateSuggestionSelection(items, currentIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentIndex = Math.max(currentIndex - 1, -1);
                this.updateSuggestionSelection(items, currentIndex);
            } else if (e.key === 'Enter' && currentIndex >= 0) {
                e.preventDefault();
                items[currentIndex].click();
            } else if (e.key === 'Escape') {
                container.classList.add('hidden');
                currentIndex = -1;
            }
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !container.contains(e.target)) {
                container.classList.add('hidden');
            }
        });
    }

    /**
     * Highlight search matches
     */
    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Update suggestion selection
     */
    updateSuggestionSelection(items, index) {
        items.forEach((item, i) => {
            item.classList.toggle('suggestion-item--selected', i === index);
        });
    }

    /**
     * Add action button
     */
    addAction(options = {}) {
        const {
            id = this.generateId(),
            icon = null,
            label = '',
            onClick = null,
            dropdown = null,
            badge = null,
            tooltip = label
        } = options;

        const actionsContainer = this.header.querySelector('.header-actions');
        
        const action = document.createElement('div');
        action.className = 'header-action';
        action.setAttribute('data-id', id);

        const button = document.createElement('button');
        button.className = 'action-button';
        button.title = tooltip;

        button.innerHTML = `
            ${icon ? `<span class="action-icon">${icon}</span>` : ''}
            ${label ? `<span class="action-label">${label}</span>` : ''}
            ${badge ? `<span class="action-badge">${badge}</span>` : ''}
            ${dropdown ? '<span class="action-arrow">▼</span>' : ''}
        `;

        // Event handling
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (dropdown) {
                this.toggleDropdown(action, dropdown);
            } else if (onClick) {
                onClick(e);
            }
        });

        action.appendChild(button);
        
        // Add dropdown if specified
        if (dropdown) {
            const dropdownElement = this.createDropdown(dropdown);
            action.appendChild(dropdownElement);
            action.classList.add('header-action--has-dropdown');
        }

        actionsContainer.appendChild(action);
        
        this.controls.set(id, {
            id,
            element: action,
            button,
            options
        });

        return id;
    }

    /**
     * Create dropdown menu
     */
    createDropdown(items) {
        const dropdown = document.createElement('div');
        dropdown.className = 'action-dropdown hidden';

        dropdown.innerHTML = items.map(item => {
            if (item.type === 'separator') {
                return '<div class="dropdown-separator"></div>';
            }
            
            return `
                <div class="dropdown-item" ${item.disabled ? 'data-disabled="true"' : ''}>
                    ${item.icon ? `<span class="dropdown-icon">${item.icon}</span>` : ''}
                    <span class="dropdown-label">${item.label}</span>
                    ${item.shortcut ? `<span class="dropdown-shortcut">${item.shortcut}</span>` : ''}
                </div>
            `;
        }).join('');

        // Add click handlers
        dropdown.querySelectorAll('.dropdown-item').forEach((item, index) => {
            const menuItem = items.filter(i => i.type !== 'separator')[index];
            if (menuItem && menuItem.onClick && !menuItem.disabled) {
                item.addEventListener('click', () => {
                    menuItem.onClick();
                    this.hideAllDropdowns();
                });
            }
        });

        return dropdown;
    }

    /**
     * Toggle dropdown
     */
    toggleDropdown(action, items) {
        const dropdown = action.querySelector('.action-dropdown');
        const isVisible = !dropdown.classList.contains('hidden');

        // Hide all other dropdowns first
        this.hideAllDropdowns();

        if (!isVisible) {
            dropdown.classList.remove('hidden');
            action.classList.add('header-action--active');
            
            // Position dropdown
            this.positionDropdown(action, dropdown);
        }
    }

    /**
     * Position dropdown
     */
    positionDropdown(action, dropdown) {
        const rect = action.getBoundingClientRect();
        const dropdownRect = dropdown.getBoundingClientRect();
        
        // Check if dropdown fits on screen
        if (rect.right + dropdownRect.width > window.innerWidth) {
            dropdown.style.right = '0';
            dropdown.style.left = 'auto';
        } else {
            dropdown.style.left = '0';
            dropdown.style.right = 'auto';
        }
    }

    /**
     * Hide all dropdowns
     */
    hideAllDropdowns() {
        this.header.querySelectorAll('.action-dropdown').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
        
        this.header.querySelectorAll('.header-action--active').forEach(action => {
            action.classList.remove('header-action--active');
        });
    }

    /**
     * Add user menu
     */
    addUserMenu(options = {}) {
        const {
            name = 'User',
            avatar = null,
            status = null,
            menu = []
        } = options;

        const userContainer = this.header.querySelector('.header-user');
        userContainer.innerHTML = `
            <div class="user-menu">
                <button class="user-button">
                    <div class="user-avatar">${avatar || name.charAt(0)}</div>
                    <div class="user-info">
                        <div class="user-name">${name}</div>
                        ${status ? `<div class="user-status">${status}</div>` : ''}
                    </div>
                    <span class="user-arrow">▼</span>
                </button>
                <div class="user-dropdown hidden">
                    ${menu.map(item => {
                        if (item.type === 'separator') {
                            return '<div class="dropdown-separator"></div>';
                        }
                        
                        return `
                            <div class="dropdown-item">
                                ${item.icon ? `<span class="dropdown-icon">${item.icon}</span>` : ''}
                                <span class="dropdown-label">${item.label}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        // Event handling
        const userButton = userContainer.querySelector('.user-button');
        const userDropdown = userContainer.querySelector('.user-dropdown');

        userButton.addEventListener('click', () => {
            const isVisible = !userDropdown.classList.contains('hidden');
            this.hideAllDropdowns();
            
            if (!isVisible) {
                userDropdown.classList.remove('hidden');
                userContainer.classList.add('user-menu--active');
            }
        });

        // Add menu item handlers
        userContainer.querySelectorAll('.dropdown-item').forEach((item, index) => {
            const menuItem = menu.filter(i => i.type !== 'separator')[index];
            if (menuItem && menuItem.onClick) {
                item.addEventListener('click', () => {
                    menuItem.onClick();
                    this.hideAllDropdowns();
                });
            }
        });
    }

    /**
     * Add breadcrumb navigation
     */
    addBreadcrumbs(items = []) {
        const breadcrumbContainer = this.header.querySelector('.header-breadcrumbs');
        
        if (items.length === 0) {
            breadcrumbContainer.innerHTML = '';
            return;
        }

        breadcrumbContainer.innerHTML = `
            <nav class="breadcrumbs" aria-label="Breadcrumb">
                ${items.map((item, index) => `
                    <span class="breadcrumb-item ${index === items.length - 1 ? 'breadcrumb-item--current' : ''}">
                        ${item.href && index < items.length - 1 ? 
                            `<a href="${item.href}" class="breadcrumb-link">${item.label}</a>` :
                            `<span class="breadcrumb-text">${item.label}</span>`
                        }
                        ${index < items.length - 1 ? '<span class="breadcrumb-separator">›</span>' : ''}
                    </span>
                `).join('')}
            </nav>
        `;
    }

    /**
     * Update action badge
     */
    updateActionBadge(id, badge) {
        const control = this.controls.get(id);
        if (!control) return;

        const badgeElement = control.button.querySelector('.action-badge');
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
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('header-controls-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'header-controls-styles';
        styles.textContent = `
            /* Header Controls Styles */
            .app-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                height: 60px;
                background: white;
                border-bottom: 1px solid #e5e7eb;
                padding: 0 20px;
                position: relative;
                z-index: 100;
            }
            
            .header-left,
            .header-center,
            .header-right {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .header-left {
                flex: 0 0 auto;
            }
            
            .header-center {
                flex: 1;
                justify-content: center;
                max-width: 600px;
            }
            
            .header-right {
                flex: 0 0 auto;
            }
            
            /* Search */
            .search-box {
                position: relative;
                width: 100%;
                max-width: 400px;
            }
            
            .search-input {
                width: 100%;
                padding: 8px 40px 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #f9fafb;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .search-input:focus {
                outline: none;
                border-color: #3b82f6;
                background: white;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .search-button {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                background: transparent;
                border: none;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
            }
            
            .search-button:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .search-shortcut {
                position: absolute;
                right: 36px;
                top: 50%;
                transform: translateY(-50%);
                background: #e5e7eb;
                color: #6b7280;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
                pointer-events: none;
            }
            
            /* Search Suggestions */
            .search-suggestions {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                margin-top: 4px;
            }
            
            .suggestion-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 12px;
                cursor: pointer;
                transition: background 0.2s;
            }
            
            .suggestion-item:hover,
            .suggestion-item--selected {
                background: #f3f4f6;
            }
            
            .suggestion-icon {
                font-size: 16px;
                flex-shrink: 0;
            }
            
            .suggestion-label {
                flex: 1;
                font-size: 14px;
            }
            
            .suggestion-label mark {
                background: #fef3c7;
                color: #92400e;
                padding: 0;
            }
            
            .suggestion-category {
                font-size: 12px;
                color: #6b7280;
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            /* Actions */
            .header-actions {
                display: flex;
                gap: 8px;
            }
            
            .header-action {
                position: relative;
            }
            
            .action-button {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 12px;
                background: transparent;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                color: #374151;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .action-button:hover {
                background: #f9fafb;
                border-color: #9ca3af;
            }
            
            .header-action--active .action-button {
                background: #3b82f6;
                border-color: #3b82f6;
                color: white;
            }
            
            .action-icon {
                font-size: 16px;
            }
            
            .action-badge {
                background: #ef4444;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 16px;
                text-align: center;
                line-height: 1;
            }
            
            .action-arrow {
                font-size: 10px;
                color: #6b7280;
            }
            
            /* Dropdowns */
            .action-dropdown,
            .user-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                min-width: 180px;
                z-index: 1000;
                margin-top: 4px;
                overflow: hidden;
            }
            
            .dropdown-item {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 12px;
                cursor: pointer;
                transition: background 0.2s;
                font-size: 14px;
            }
            
            .dropdown-item:hover {
                background: #f3f4f6;
            }
            
            .dropdown-item[data-disabled="true"] {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .dropdown-icon {
                font-size: 16px;
                width: 20px;
                text-align: center;
            }
            
            .dropdown-label {
                flex: 1;
            }
            
            .dropdown-shortcut {
                font-size: 12px;
                color: #6b7280;
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            .dropdown-separator {
                height: 1px;
                background: #e5e7eb;
                margin: 4px 0;
            }
            
            /* User Menu */
            .user-menu {
                position: relative;
            }
            
            .user-button {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 6px 12px;
                background: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .user-button:hover {
                background: #f9fafb;
                border-color: #e5e7eb;
            }
            
            .user-menu--active .user-button {
                background: #f3f4f6;
                border-color: #d1d5db;
            }
            
            .user-avatar {
                width: 32px;
                height: 32px;
                background: #3b82f6;
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
            }
            
            .user-info {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }
            
            .user-name {
                font-size: 14px;
                font-weight: 500;
                color: #111827;
                line-height: 1.2;
            }
            
            .user-status {
                font-size: 12px;
                color: #6b7280;
                line-height: 1.2;
            }
            
            .user-arrow {
                font-size: 10px;
                color: #6b7280;
            }
            
            .user-dropdown {
                right: 0;
                left: auto;
            }
            
            /* Breadcrumbs */
            .breadcrumbs {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 14px;
            }
            
            .breadcrumb-item {
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .breadcrumb-link {
                color: #6b7280;
                text-decoration: none;
                transition: color 0.2s;
            }
            
            .breadcrumb-link:hover {
                color: #374151;
            }
            
            .breadcrumb-text {
                color: #111827;
                font-weight: 500;
            }
            
            .breadcrumb-separator {
                color: #d1d5db;
                font-size: 12px;
            }
            
            .hidden {
                display: none !important;
            }
            
            @media (max-width: 768px) {
                .app-header {
                    padding: 0 16px;
                }
                
                .header-center {
                    max-width: 200px;
                }
                
                .action-label {
                    display: none;
                }
                
                .user-info {
                    display: none;
                }
                
                .search-shortcut {
                    display: none;
                }
            }
        `;
        
        document.head.appendChild(styles);

        // Hide dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.header.contains(e.target)) {
                this.hideAllDropdowns();
            }
        });
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return 'header-control-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Destroy header controls
     */
    destroy() {
        if (this.header && this.header.parentNode) {
            this.header.parentNode.removeChild(this.header);
        }
        
        this.controls.clear();
        
        // Remove styles
        const styles = document.getElementById('header-controls-styles');
        if (styles) styles.remove();
        
        console.log('🎯 Header Controls destroyed');
    }
}

// Export for ES6 modules
export default HeaderControls;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.HeaderControls = HeaderControls;
}