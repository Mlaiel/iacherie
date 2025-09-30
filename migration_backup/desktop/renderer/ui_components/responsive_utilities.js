/**
 * Ainflue Desktop Renderer - Responsive Utilities
 * Professional responsive design utilities
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
 */

'use strict';

class ResponsiveUtilities {
    constructor() {
        this.version = '1.0.0';
        this.author = 'Fahed Mlaiel';
        this.breakpoints = {
            xs: 0,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400
        };
        this.currentBreakpoint = 'xs';
        this.mediaQueries = new Map();
        this.observers = new Map();
        
        this.init();
    }

    /**
     * Initialize responsive utilities
     */
    init() {
        console.log('📱 Initializing Responsive Utilities v' + this.version);
        
        this.setupStyles();
        this.createMediaQueries();
        this.setupResizeObserver();
        this.setupIntersectionObserver();
        this.detectCurrentBreakpoint();
        this.addUtilityClasses();
    }

    /**
     * Create media queries for breakpoints
     */
    createMediaQueries() {
        Object.entries(this.breakpoints).forEach(([name, width]) => {
            if (width > 0) {
                const mediaQuery = window.matchMedia(`(min-width: ${width}px)`);
                
                mediaQuery.addListener((e) => {
                    this.handleBreakpointChange(name, e.matches);
                });
                
                this.mediaQueries.set(name, mediaQuery);
                
                // Initial check
                this.handleBreakpointChange(name, mediaQuery.matches);
            }
        });
    }

    /**
     * Handle breakpoint changes
     */
    handleBreakpointChange(breakpoint, matches) {
        document.documentElement.classList.toggle(`bp-${breakpoint}`, matches);
        
        if (matches) {
            this.currentBreakpoint = breakpoint;
            document.documentElement.setAttribute('data-breakpoint', breakpoint);
            
            this.emit('breakpoint-changed', {
                breakpoint,
                width: window.innerWidth,
                height: window.innerHeight
            });
        }
    }

    /**
     * Detect current breakpoint
     */
    detectCurrentBreakpoint() {
        const width = window.innerWidth;
        
        for (const [name, minWidth] of Object.entries(this.breakpoints).reverse()) {
            if (width >= minWidth) {
                this.currentBreakpoint = name;
                break;
            }
        }
        
        document.documentElement.setAttribute('data-breakpoint', this.currentBreakpoint);
    }

    /**
     * Check if current breakpoint matches
     */
    isBreakpoint(breakpoint) {
        if (Array.isArray(breakpoint)) {
            return breakpoint.includes(this.currentBreakpoint);
        }
        return this.currentBreakpoint === breakpoint;
    }

    /**
     * Check if screen is at least the specified breakpoint
     */
    isAtLeast(breakpoint) {
        const currentWidth = window.innerWidth;
        const breakpointWidth = this.breakpoints[breakpoint];
        return currentWidth >= breakpointWidth;
    }

    /**
     * Check if screen is at most the specified breakpoint
     */
    isAtMost(breakpoint) {
        const currentWidth = window.innerWidth;
        const breakpointWidth = this.breakpoints[breakpoint];
        return currentWidth <= breakpointWidth;
    }

    /**
     * Get viewport dimensions
     */
    getViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            breakpoint: this.currentBreakpoint,
            isMobile: this.isMobile(),
            isTablet: this.isTablet(),
            isDesktop: this.isDesktop(),
            orientation: this.getOrientation(),
            aspectRatio: this.getAspectRatio()
        };
    }

    /**
     * Check if mobile device
     */
    isMobile() {
        return this.isAtMost('md') || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * Check if tablet device
     */
    isTablet() {
        return this.isAtLeast('md') && this.isAtMost('lg') && /iPad|Android/i.test(navigator.userAgent);
    }

    /**
     * Check if desktop device
     */
    isDesktop() {
        return this.isAtLeast('lg') && !/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * Get screen orientation
     */
    getOrientation() {
        return window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
    }

    /**
     * Get aspect ratio
     */
    getAspectRatio() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        const ratio = width / height;
        
        if (ratio > 1.7) return 'wide';
        if (ratio > 1.3) return 'standard';
        if (ratio > 0.8) return 'square';
        return 'tall';
    }

    /**
     * Setup resize observer
     */
    setupResizeObserver() {
        if ('ResizeObserver' in window) {
            this.resizeObserver = new ResizeObserver((entries) => {
                entries.forEach(entry => {
                    const element = entry.target;
                    const { width, height } = entry.contentRect;
                    
                    this.emit('element-resized', {
                        element,
                        width,
                        height,
                        entry
                    });
                });
            });
        }
    }

    /**
     * Setup intersection observer
     */
    setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            this.intersectionObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const element = entry.target;
                    const isVisible = entry.isIntersecting;
                    
                    element.classList.toggle('in-viewport', isVisible);
                    
                    this.emit('element-visibility-changed', {
                        element,
                        isVisible,
                        entry
                    });
                });
            }, {
                threshold: [0, 0.25, 0.5, 0.75, 1],
                rootMargin: '50px'
            });
        }
    }

    /**
     * Observe element resize
     */
    observeResize(element, callback) {
        if (!this.resizeObserver) return;
        
        const id = this.generateId();
        this.observers.set(id, { element, callback, type: 'resize' });
        
        if (callback) {
            document.addEventListener('element-resized', (e) => {
                if (e.detail.element === element) {
                    callback(e.detail);
                }
            });
        }
        
        this.resizeObserver.observe(element);
        return id;
    }

    /**
     * Observe element visibility
     */
    observeVisibility(element, callback) {
        if (!this.intersectionObserver) return;
        
        const id = this.generateId();
        this.observers.set(id, { element, callback, type: 'intersection' });
        
        if (callback) {
            document.addEventListener('element-visibility-changed', (e) => {
                if (e.detail.element === element) {
                    callback(e.detail);
                }
            });
        }
        
        this.intersectionObserver.observe(element);
        return id;
    }

    /**
     * Stop observing element
     */
    unobserve(id) {
        const observer = this.observers.get(id);
        if (!observer) return;
        
        if (observer.type === 'resize' && this.resizeObserver) {
            this.resizeObserver.unobserve(observer.element);
        } else if (observer.type === 'intersection' && this.intersectionObserver) {
            this.intersectionObserver.unobserve(observer.element);
        }
        
        this.observers.delete(id);
    }

    /**
     * Make element responsive
     */
    makeResponsive(element, options = {}) {
        const {
            breakpoints = {},
            lazyLoad = false,
            autoHeight = false,
            aspectRatio = null
        } = options;

        // Apply breakpoint-specific styles
        Object.entries(breakpoints).forEach(([bp, styles]) => {
            if (this.isAtLeast(bp)) {
                Object.assign(element.style, styles);
            }
        });

        // Lazy loading
        if (lazyLoad && 'IntersectionObserver' in window) {
            this.observeVisibility(element, ({ isVisible }) => {
                if (isVisible) {
                    element.classList.add('loaded');
                    this.loadLazyContent(element);
                }
            });
        }

        // Auto height adjustment
        if (autoHeight) {
            this.observeResize(element, ({ width }) => {
                this.adjustElementHeight(element, width);
            });
        }

        // Aspect ratio maintenance
        if (aspectRatio) {
            this.maintainAspectRatio(element, aspectRatio);
        }

        // Add responsive class
        element.classList.add('responsive-element');
    }

    /**
     * Load lazy content
     */
    loadLazyContent(element) {
        // Load lazy images
        const lazyImages = element.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });

        // Load lazy videos
        const lazyVideos = element.querySelectorAll('video[data-src]');
        lazyVideos.forEach(video => {
            video.src = video.dataset.src;
            video.removeAttribute('data-src');
        });
    }

    /**
     * Adjust element height
     */
    adjustElementHeight(element, width) {
        // Calculate height based on content and viewport
        const content = element.scrollHeight;
        const viewport = window.innerHeight;
        const maxHeight = viewport * 0.8; // 80% of viewport
        
        element.style.height = Math.min(content, maxHeight) + 'px';
    }

    /**
     * Maintain aspect ratio
     */
    maintainAspectRatio(element, ratio) {
        const [width, height] = ratio.split(':').map(Number);
        const aspectRatio = height / width;
        
        this.observeResize(element, ({ width: elementWidth }) => {
            const calculatedHeight = elementWidth * aspectRatio;
            element.style.height = calculatedHeight + 'px';
        });
    }

    /**
     * Create responsive grid
     */
    createResponsiveGrid(container, options = {}) {
        const {
            columns = { xs: 1, sm: 2, md: 3, lg: 4, xl: 5 },
            gap = '1rem',
            autoFit = false,
            minWidth = '200px'
        } = options;

        container.classList.add('responsive-grid');
        
        // Apply grid styles
        if (autoFit) {
            container.style.display = 'grid';
            container.style.gridTemplateColumns = `repeat(auto-fit, minmax(${minWidth}, 1fr))`;
            container.style.gap = gap;
        } else {
            this.updateGridColumns(container, columns, gap);
        }

        // Update on breakpoint changes
        document.addEventListener('breakpoint-changed', () => {
            if (!autoFit) {
                this.updateGridColumns(container, columns, gap);
            }
        });
    }

    /**
     * Update grid columns based on breakpoint
     */
    updateGridColumns(container, columns, gap) {
        const currentColumns = columns[this.currentBreakpoint] || columns.xs || 1;
        
        container.style.display = 'grid';
        container.style.gridTemplateColumns = `repeat(${currentColumns}, 1fr)`;
        container.style.gap = gap;
    }

    /**
     * Add utility classes to document
     */
    addUtilityClasses() {
        // Device type classes
        document.documentElement.classList.toggle('is-mobile', this.isMobile());
        document.documentElement.classList.toggle('is-tablet', this.isTablet());
        document.documentElement.classList.toggle('is-desktop', this.isDesktop());
        
        // Orientation class
        document.documentElement.classList.add(`orientation-${this.getOrientation()}`);
        
        // Aspect ratio class
        document.documentElement.classList.add(`aspect-${this.getAspectRatio()}`);
        
        // Update on resize
        window.addEventListener('resize', this.debounce(() => {
            this.detectCurrentBreakpoint();
            document.documentElement.className = document.documentElement.className
                .replace(/\b(is-mobile|is-tablet|is-desktop|orientation-\w+|aspect-\w+)\b/g, '');
            
            document.documentElement.classList.toggle('is-mobile', this.isMobile());
            document.documentElement.classList.toggle('is-tablet', this.isTablet());
            document.documentElement.classList.toggle('is-desktop', this.isDesktop());
            document.documentElement.classList.add(`orientation-${this.getOrientation()}`);
            document.documentElement.classList.add(`aspect-${this.getAspectRatio()}`);
        }, 250));
    }

    /**
     * Setup styles
     */
    setupStyles() {
        if (document.getElementById('responsive-utilities-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'responsive-utilities-styles';
        styles.textContent = `
            /* Responsive Utilities Styles */
            
            /* Responsive Grid */
            .responsive-grid {
                display: grid;
                gap: 1rem;
            }
            
            /* Responsive Element */
            .responsive-element {
                max-width: 100%;
                height: auto;
            }
            
            /* Lazy Loading */
            .responsive-element:not(.loaded) {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .responsive-element.loaded {
                opacity: 1;
            }
            
            /* Viewport Utilities */
            .in-viewport {
                animation: fadeInUp 0.6s ease-out;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Display Utilities */
            .d-none { display: none !important; }
            .d-block { display: block !important; }
            .d-inline { display: inline !important; }
            .d-inline-block { display: inline-block !important; }
            .d-flex { display: flex !important; }
            .d-grid { display: grid !important; }
            
            /* Responsive Display Utilities */
            @media (max-width: 575.98px) {
                .d-xs-none { display: none !important; }
                .d-xs-block { display: block !important; }
                .d-xs-inline { display: inline !important; }
                .d-xs-inline-block { display: inline-block !important; }
                .d-xs-flex { display: flex !important; }
                .d-xs-grid { display: grid !important; }
            }
            
            @media (min-width: 576px) {
                .d-sm-none { display: none !important; }
                .d-sm-block { display: block !important; }
                .d-sm-inline { display: inline !important; }
                .d-sm-inline-block { display: inline-block !important; }
                .d-sm-flex { display: flex !important; }
                .d-sm-grid { display: grid !important; }
            }
            
            @media (min-width: 768px) {
                .d-md-none { display: none !important; }
                .d-md-block { display: block !important; }
                .d-md-inline { display: inline !important; }
                .d-md-inline-block { display: inline-block !important; }
                .d-md-flex { display: flex !important; }
                .d-md-grid { display: grid !important; }
            }
            
            @media (min-width: 992px) {
                .d-lg-none { display: none !important; }
                .d-lg-block { display: block !important; }
                .d-lg-inline { display: inline !important; }
                .d-lg-inline-block { display: inline-block !important; }
                .d-lg-flex { display: flex !important; }
                .d-lg-grid { display: grid !important; }
            }
            
            @media (min-width: 1200px) {
                .d-xl-none { display: none !important; }
                .d-xl-block { display: block !important; }
                .d-xl-inline { display: inline !important; }
                .d-xl-inline-block { display: inline-block !important; }
                .d-xl-flex { display: flex !important; }
                .d-xl-grid { display: grid !important; }
            }
            
            /* Flex Utilities */
            .flex-row { flex-direction: row !important; }
            .flex-column { flex-direction: column !important; }
            .flex-wrap { flex-wrap: wrap !important; }
            .flex-nowrap { flex-wrap: nowrap !important; }
            .justify-content-start { justify-content: flex-start !important; }
            .justify-content-end { justify-content: flex-end !important; }
            .justify-content-center { justify-content: center !important; }
            .justify-content-between { justify-content: space-between !important; }
            .justify-content-around { justify-content: space-around !important; }
            .align-items-start { align-items: flex-start !important; }
            .align-items-end { align-items: flex-end !important; }
            .align-items-center { align-items: center !important; }
            .align-items-stretch { align-items: stretch !important; }
            
            /* Spacing Utilities */
            .m-0 { margin: 0 !important; }
            .m-1 { margin: 0.25rem !important; }
            .m-2 { margin: 0.5rem !important; }
            .m-3 { margin: 1rem !important; }
            .m-4 { margin: 1.5rem !important; }
            .m-5 { margin: 3rem !important; }
            
            .p-0 { padding: 0 !important; }
            .p-1 { padding: 0.25rem !important; }
            .p-2 { padding: 0.5rem !important; }
            .p-3 { padding: 1rem !important; }
            .p-4 { padding: 1.5rem !important; }
            .p-5 { padding: 3rem !important; }
            
            /* Text Utilities */
            .text-left { text-align: left !important; }
            .text-center { text-align: center !important; }
            .text-right { text-align: right !important; }
            .text-justify { text-align: justify !important; }
            
            /* Responsive Text Alignment */
            @media (max-width: 767.98px) {
                .text-sm-left { text-align: left !important; }
                .text-sm-center { text-align: center !important; }
                .text-sm-right { text-align: right !important; }
            }
            
            @media (min-width: 768px) {
                .text-md-left { text-align: left !important; }
                .text-md-center { text-align: center !important; }
                .text-md-right { text-align: right !important; }
            }
            
            /* Overflow Utilities */
            .overflow-hidden { overflow: hidden !important; }
            .overflow-scroll { overflow: scroll !important; }
            .overflow-auto { overflow: auto !important; }
            
            /* Position Utilities */
            .position-static { position: static !important; }
            .position-relative { position: relative !important; }
            .position-absolute { position: absolute !important; }
            .position-fixed { position: fixed !important; }
            .position-sticky { position: sticky !important; }
            
            /* Width and Height Utilities */
            .w-25 { width: 25% !important; }
            .w-50 { width: 50% !important; }
            .w-75 { width: 75% !important; }
            .w-100 { width: 100% !important; }
            .w-auto { width: auto !important; }
            
            .h-25 { height: 25% !important; }
            .h-50 { height: 50% !important; }
            .h-75 { height: 75% !important; }
            .h-100 { height: 100% !important; }
            .h-auto { height: auto !important; }
            
            /* Visibility Utilities */
            .visible { visibility: visible !important; }
            .invisible { visibility: hidden !important; }
            
            /* Border Utilities */
            .border { border: 1px solid #dee2e6 !important; }
            .border-0 { border: 0 !important; }
            .border-top { border-top: 1px solid #dee2e6 !important; }
            .border-right { border-right: 1px solid #dee2e6 !important; }
            .border-bottom { border-bottom: 1px solid #dee2e6 !important; }
            .border-left { border-left: 1px solid #dee2e6 !important; }
            
            .rounded { border-radius: 0.25rem !important; }
            .rounded-0 { border-radius: 0 !important; }
            .rounded-circle { border-radius: 50% !important; }
            
            /* Shadow Utilities */
            .shadow-none { box-shadow: none !important; }
            .shadow-sm { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important; }
            .shadow { box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important; }
            .shadow-lg { box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.175) !important; }
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
     * Generate unique ID
     */
    generateId() {
        return 'responsive-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Event emitter
     */
    emit(event, data = null) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * Get current breakpoint
     */
    getCurrentBreakpoint() {
        return this.currentBreakpoint;
    }

    /**
     * Get all breakpoints
     */
    getBreakpoints() {
        return { ...this.breakpoints };
    }

    /**
     * Add custom breakpoint
     */
    addBreakpoint(name, width) {
        this.breakpoints[name] = width;
        
        // Create media query for new breakpoint
        const mediaQuery = window.matchMedia(`(min-width: ${width}px)`);
        mediaQuery.addListener((e) => {
            this.handleBreakpointChange(name, e.matches);
        });
        this.mediaQueries.set(name, mediaQuery);
        
        // Initial check
        this.handleBreakpointChange(name, mediaQuery.matches);
    }

    /**
     * Destroy responsive utilities
     */
    destroy() {
        // Disconnect observers
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        
        // Clear observers map
        this.observers.clear();
        
        // Remove media query listeners
        this.mediaQueries.forEach(mq => {
            mq.removeListener(this.handleBreakpointChange);
        });
        this.mediaQueries.clear();
        
        // Remove styles
        const styles = document.getElementById('responsive-utilities-styles');
        if (styles) styles.remove();
        
        console.log('📱 Responsive Utilities destroyed');
    }
}

// Export for ES6 modules
export default ResponsiveUtilities;

// Global instance for legacy support
if (typeof window !== 'undefined') {
    window.ResponsiveUtilities = ResponsiveUtilities;
}