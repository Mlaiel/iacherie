/**
 * @fileoverview Responsive Layout - Advanced Responsive Design System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/responsive_layout
 * @description Professional responsive layout system with breakpoints, grids, and adaptive components
 */

class ResponsiveLayout {
  constructor() {
    this.breakpoints = new Map([
      ['xs', { min: 0, max: 575, name: 'Extra Small', type: 'mobile' }],
      ['sm', { min: 576, max: 767, name: 'Small', type: 'mobile' }],
      ['md', { min: 768, max: 991, name: 'Medium', type: 'tablet' }],
      ['lg', { min: 992, max: 1199, name: 'Large', type: 'desktop' }],
      ['xl', { min: 1200, max: 1399, name: 'Extra Large', type: 'desktop' }],
      ['xxl', { min: 1400, max: Infinity, name: 'Extra Extra Large', type: 'desktop' }]
    ]);

    this.currentBreakpoint = null;
    this.currentViewport = null;
    this.layoutElements = new Map();
    this.responsiveComponents = new Set();
    this.mediaQueries = new Map();
    this.observers = new Map();

    this.config = {
      enableFluidGrid: true,
      enableResponsiveImages: true,
      enableResponsiveText: true,
      enableContainerQueries: true,
      enableOrientationSupport: true,
      debounceDelay: 100,
      gridColumns: 12,
      gridGutter: '1rem',
      containerMaxWidths: {
        sm: '540px',
        md: '720px',
        lg: '960px',
        xl: '1140px',
        xxl: '1320px'
      }
    };

    this.initializeResponsiveLayout();
    console.log('Responsive Layout initialized');
  }

  /**
   * Initialize responsive layout system
   */
  initializeResponsiveLayout() {
    this.setupMediaQueries();
    this.setupResizeObserver();
    this.setupOrientationHandling();
    this.setupContainerQueries();
    this.detectInitialBreakpoint();
    this.injectResponsiveCSS();
    this.setupLayoutUtilities();
  }

  /**
   * Setup media queries for all breakpoints
   */
  setupMediaQueries() {
    this.breakpoints.forEach((breakpoint, name) => {
      if (breakpoint.max === Infinity) {
        // For largest breakpoint, only min-width
        const query = `(min-width: ${breakpoint.min}px)`;
        this.createMediaQuery(name, query);
      } else {
        // For other breakpoints, use range
        const query = `(min-width: ${breakpoint.min}px) and (max-width: ${breakpoint.max}px)`;
        this.createMediaQuery(name, query);
      }
    });

    // Additional useful media queries
    this.createMediaQuery('mobile', '(max-width: 767px)');
    this.createMediaQuery('tablet', '(min-width: 768px) and (max-width: 1023px)');
    this.createMediaQuery('desktop', '(min-width: 1024px)');
    this.createMediaQuery('landscape', '(orientation: landscape)');
    this.createMediaQuery('portrait', '(orientation: portrait)');
    this.createMediaQuery('retina', '(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)');
  }

  /**
   * Create and setup media query
   */
  createMediaQuery(name, query) {
    const mediaQuery = window.matchMedia(query);
    const handler = this.createBreakpointHandler(name);
    
    mediaQuery.addListener(handler);
    this.mediaQueries.set(name, { mediaQuery, handler });
    
    // Call handler initially
    handler(mediaQuery);
  }

  /**
   * Create breakpoint change handler
   */
  createBreakpointHandler(breakpointName) {
    return this.debounce((mediaQuery) => {
      if (mediaQuery.matches) {
        this.handleBreakpointChange(breakpointName, mediaQuery);
      }
    }, this.config.debounceDelay);
  }

  /**
   * Handle breakpoint changes
   */
  handleBreakpointChange(breakpointName, mediaQuery) {
    const oldBreakpoint = this.currentBreakpoint;
    
    // Update current breakpoint if it's a main breakpoint
    if (this.breakpoints.has(breakpointName)) {
      this.currentBreakpoint = breakpointName;
    }

    // Update viewport information
    this.updateViewportInfo();

    // Apply responsive changes
    this.applyResponsiveChanges(breakpointName, oldBreakpoint);

    // Emit breakpoint change event
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('layout.breakpoint-changed', {
        current: breakpointName,
        previous: oldBreakpoint,
        viewport: this.currentViewport,
        mediaQuery: mediaQuery.media
      });
    }

    console.log(`Breakpoint changed: ${oldBreakpoint} → ${breakpointName}`);
  }

  /**
   * Setup resize observer for element-specific responsiveness
   */
  setupResizeObserver() {
    if (!window.ResizeObserver) {
      console.warn('ResizeObserver not supported');
      return;
    }

    this.resizeObserver = new ResizeObserver(
      this.debounce((entries) => {
        entries.forEach(entry => {
          this.handleElementResize(entry);
        });
      }, this.config.debounceDelay)
    );
  }

  /**
   * Setup orientation change handling
   */
  setupOrientationHandling() {
    if (!this.config.enableOrientationSupport) return;

    const handleOrientationChange = this.debounce(() => {
      this.updateViewportInfo();
      this.applyOrientationChanges();
    }, this.config.debounceDelay);

    window.addEventListener('orientationchange', handleOrientationChange);
    screen.orientation?.addEventListener('change', handleOrientationChange);
  }

  /**
   * Setup container queries (modern CSS feature)
   */
  setupContainerQueries() {
    if (!this.config.enableContainerQueries) return;

    // Check for container query support
    if (CSS.supports && CSS.supports('container-type: inline-size')) {
      document.documentElement.classList.add('supports-container-queries');
    } else {
      // Fallback using ResizeObserver
      this.setupContainerQueryFallback();
    }
  }

  /**
   * Setup container query fallback
   */
  setupContainerQueryFallback() {
    // This would implement a JavaScript-based container query system
    // for browsers that don't support native container queries
    console.log('Using container query fallback');
  }

  /**
   * Detect initial breakpoint
   */
  detectInitialBreakpoint() {
    const width = window.innerWidth;
    
    for (const [name, breakpoint] of this.breakpoints) {
      if (width >= breakpoint.min && width <= breakpoint.max) {
        this.currentBreakpoint = name;
        break;
      }
    }
    
    this.updateViewportInfo();
  }

  /**
   * Update viewport information
   */
  updateViewportInfo() {
    this.currentViewport = {
      width: window.innerWidth,
      height: window.innerHeight,
      aspectRatio: window.innerWidth / window.innerHeight,
      orientation: window.innerWidth > window.innerHeight ? 'landscape' : 'portrait',
      devicePixelRatio: window.devicePixelRatio || 1,
      type: this.getViewportType()
    };
  }

  /**
   * Get viewport type based on current breakpoint
   */
  getViewportType() {
    if (!this.currentBreakpoint) return 'unknown';
    
    const breakpoint = this.breakpoints.get(this.currentBreakpoint);
    return breakpoint ? breakpoint.type : 'unknown';
  }

  /**
   * Apply responsive changes
   */
  applyResponsiveChanges(newBreakpoint, oldBreakpoint) {
    // Update body classes
    this.updateBodyClasses(newBreakpoint, oldBreakpoint);
    
    // Update responsive components
    this.updateResponsiveComponents();
    
    // Update layout elements
    this.updateLayoutElements();
    
    // Update responsive images
    if (this.config.enableResponsiveImages) {
      this.updateResponsiveImages();
    }
    
    // Update responsive text
    if (this.config.enableResponsiveText) {
      this.updateResponsiveText();
    }
  }

  /**
   * Update body classes for styling
   */
  updateBodyClasses(newBreakpoint, oldBreakpoint) {
    const body = document.body;
    
    // Remove old breakpoint classes
    if (oldBreakpoint) {
      body.classList.remove(`breakpoint-${oldBreakpoint}`);
      const oldType = this.breakpoints.get(oldBreakpoint)?.type;
      if (oldType) {
        body.classList.remove(`viewport-${oldType}`);
      }
    }
    
    // Add new breakpoint classes
    if (newBreakpoint) {
      body.classList.add(`breakpoint-${newBreakpoint}`);
      const newType = this.breakpoints.get(newBreakpoint)?.type;
      if (newType) {
        body.classList.add(`viewport-${newType}`);
      }
    }
    
    // Add orientation class
    body.classList.remove('orientation-landscape', 'orientation-portrait');
    body.classList.add(`orientation-${this.currentViewport.orientation}`);
  }

  /**
   * Update responsive components
   */
  updateResponsiveComponents() {
    this.responsiveComponents.forEach(component => {
      if (component.onBreakpointChange) {
        component.onBreakpointChange(this.currentBreakpoint, this.currentViewport);
      }
    });
  }

  /**
   * Update layout elements
   */
  updateLayoutElements() {
    this.layoutElements.forEach((config, element) => {
      this.applyResponsiveConfig(element, config);
    });
  }

  /**
   * Update responsive images
   */
  updateResponsiveImages() {
    const images = document.querySelectorAll('img[data-responsive]');
    
    images.forEach(img => {
      const config = this.parseResponsiveConfig(img.dataset.responsive);
      const srcSet = this.generateImageSrcSet(config);
      
      if (srcSet) {
        img.srcset = srcSet;
      }
    });
  }

  /**
   * Update responsive text
   */
  updateResponsiveText() {
    const elements = document.querySelectorAll('[data-responsive-text]');
    
    elements.forEach(element => {
      const config = this.parseResponsiveConfig(element.dataset.responsiveText);
      const fontSize = this.calculateResponsiveFontSize(config);
      
      if (fontSize) {
        element.style.fontSize = fontSize;
      }
    });
  }

  /**
   * Apply orientation changes
   */
  applyOrientationChanges() {
    // Emit orientation change event
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('layout.orientation-changed', {
        orientation: this.currentViewport.orientation,
        viewport: this.currentViewport
      });
    }
  }

  /**
   * Handle element resize
   */
  handleElementResize(entry) {
    const element = entry.target;
    const { width, height } = entry.contentRect;
    
    // Apply element-specific responsive behavior
    if (element.dataset.responsiveElement) {
      this.applyElementResponsiveBehavior(element, { width, height });
    }
    
    // Emit element resize event
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('layout.element-resized', {
        element,
        width,
        height,
        entry
      });
    }
  }

  /**
   * Apply element-specific responsive behavior
   */
  applyElementResponsiveBehavior(element, dimensions) {
    const config = this.parseResponsiveConfig(element.dataset.responsiveElement);
    
    // Apply width-based classes
    if (config.widthClasses) {
      Object.entries(config.widthClasses).forEach(([className, minWidth]) => {
        if (dimensions.width >= minWidth) {
          element.classList.add(className);
        } else {
          element.classList.remove(className);
        }
      });
    }
    
    // Apply aspect ratio classes
    if (config.aspectRatioClasses) {
      const aspectRatio = dimensions.width / dimensions.height;
      Object.entries(config.aspectRatioClasses).forEach(([className, targetRatio]) => {
        if (Math.abs(aspectRatio - targetRatio) < 0.1) {
          element.classList.add(className);
        } else {
          element.classList.remove(className);
        }
      });
    }
  }

  /**
   * Inject responsive CSS utilities
   */
  injectResponsiveCSS() {
    const style = document.createElement('style');
    style.id = 'ainflue-responsive-utilities';
    
    style.textContent = this.generateResponsiveCSS();
    document.head.appendChild(style);
  }

  /**
   * Generate responsive CSS utilities
   */
  generateResponsiveCSS() {
    let css = '';
    
    // Container classes
    css += this.generateContainerCSS();
    
    // Grid utilities
    css += this.generateGridCSS();
    
    // Display utilities
    css += this.generateDisplayUtilities();
    
    // Flexbox utilities
    css += this.generateFlexboxUtilities();
    
    // Spacing utilities
    css += this.generateSpacingUtilities();
    
    // Text utilities
    css += this.generateTextUtilities();
    
    return css;
  }

  /**
   * Generate container CSS
   */
  generateContainerCSS() {
    let css = `
      .container {
        width: 100%;
        margin-left: auto;
        margin-right: auto;
        padding-left: ${this.config.gridGutter};
        padding-right: ${this.config.gridGutter};
      }
      
      .container-fluid {
        width: 100%;
        padding-left: ${this.config.gridGutter};
        padding-right: ${this.config.gridGutter};
      }
    `;
    
    // Container max-widths for each breakpoint
    Object.entries(this.config.containerMaxWidths).forEach(([breakpoint, maxWidth]) => {
      const bp = this.breakpoints.get(breakpoint);
      if (bp) {
        css += `
          @media (min-width: ${bp.min}px) {
            .container {
              max-width: ${maxWidth};
            }
          }
        `;
      }
    });
    
    return css;
  }

  /**
   * Generate grid CSS
   */
  generateGridCSS() {
    let css = `
      .row {
        display: flex;
        flex-wrap: wrap;
        margin-left: calc(${this.config.gridGutter} / -2);
        margin-right: calc(${this.config.gridGutter} / -2);
      }
      
      .col {
        flex: 1 0 0%;
        padding-left: calc(${this.config.gridGutter} / 2);
        padding-right: calc(${this.config.gridGutter} / 2);
      }
    `;
    
    // Generate column classes for each breakpoint
    this.breakpoints.forEach((breakpoint, name) => {
      const prefix = name === 'xs' ? '' : `${name}-`;
      
      if (name === 'xs') {
        css += this.generateColumnClasses('');
      } else {
        css += `
          @media (min-width: ${breakpoint.min}px) {
            ${this.generateColumnClasses(prefix)}
          }
        `;
      }
    });
    
    return css;
  }

  /**
   * Generate column classes
   */
  generateColumnClasses(prefix) {
    let css = '';
    
    for (let i = 1; i <= this.config.gridColumns; i++) {
      const percentage = (i / this.config.gridColumns) * 100;
      css += `
        .col-${prefix}${i} {
          flex: 0 0 ${percentage}%;
          max-width: ${percentage}%;
        }
      `;
    }
    
    // Auto-sizing columns
    css += `
      .col-${prefix}auto {
        flex: 0 0 auto;
        width: auto;
      }
    `;
    
    return css;
  }

  /**
   * Generate display utilities
   */
  generateDisplayUtilities() {
    const displays = ['none', 'block', 'inline', 'inline-block', 'flex', 'inline-flex', 'grid', 'table'];
    let css = '';
    
    this.breakpoints.forEach((breakpoint, name) => {
      const prefix = name === 'xs' ? '' : `${name}-`;
      
      displays.forEach(display => {
        const className = `.d-${prefix}${display}`;
        const rule = `${className} { display: ${display} !important; }`;
        
        if (name === 'xs') {
          css += rule;
        } else {
          css += `
            @media (min-width: ${breakpoint.min}px) {
              ${rule}
            }
          `;
        }
      });
    });
    
    return css;
  }

  /**
   * Generate flexbox utilities
   */
  generateFlexboxUtilities() {
    let css = '';
    
    const flexUtilities = {
      'flex-row': 'flex-direction: row',
      'flex-column': 'flex-direction: column',
      'flex-wrap': 'flex-wrap: wrap',
      'flex-nowrap': 'flex-wrap: nowrap',
      'justify-start': 'justify-content: flex-start',
      'justify-center': 'justify-content: center',
      'justify-end': 'justify-content: flex-end',
      'justify-between': 'justify-content: space-between',
      'justify-around': 'justify-content: space-around',
      'items-start': 'align-items: flex-start',
      'items-center': 'align-items: center',
      'items-end': 'align-items: flex-end',
      'items-stretch': 'align-items: stretch'
    };
    
    this.breakpoints.forEach((breakpoint, name) => {
      const prefix = name === 'xs' ? '' : `${name}-`;
      
      Object.entries(flexUtilities).forEach(([className, rule]) => {
        const fullClassName = `.${prefix}${className}`;
        const fullRule = `${fullClassName} { ${rule} !important; }`;
        
        if (name === 'xs') {
          css += fullRule;
        } else {
          css += `
            @media (min-width: ${breakpoint.min}px) {
              ${fullRule}
            }
          `;
        }
      });
    });
    
    return css;
  }

  /**
   * Generate spacing utilities
   */
  generateSpacingUtilities() {
    let css = '';
    
    const spacingValues = {
      0: '0',
      1: '0.25rem',
      2: '0.5rem',
      3: '1rem',
      4: '1.5rem',
      5: '3rem'
    };
    
    const spacingProperties = {
      m: 'margin',
      mt: 'margin-top',
      mr: 'margin-right',
      mb: 'margin-bottom',
      ml: 'margin-left',
      mx: ['margin-left', 'margin-right'],
      my: ['margin-top', 'margin-bottom'],
      p: 'padding',
      pt: 'padding-top',
      pr: 'padding-right',
      pb: 'padding-bottom',
      pl: 'padding-left',
      px: ['padding-left', 'padding-right'],
      py: ['padding-top', 'padding-bottom']
    };
    
    this.breakpoints.forEach((breakpoint, name) => {
      const prefix = name === 'xs' ? '' : `${name}-`;
      
      Object.entries(spacingProperties).forEach(([prop, cssProps]) => {
        Object.entries(spacingValues).forEach(([size, value]) => {
          const className = `.${prefix}${prop}-${size}`;
          
          let rule;
          if (Array.isArray(cssProps)) {
            rule = cssProps.map(cssProp => `${cssProp}: ${value}`).join('; ');
          } else {
            rule = `${cssProps}: ${value}`;
          }
          
          const fullRule = `${className} { ${rule} !important; }`;
          
          if (name === 'xs') {
            css += fullRule;
          } else {
            css += `
              @media (min-width: ${breakpoint.min}px) {
                ${fullRule}
              }
            `;
          }
        });
      });
    });
    
    return css;
  }

  /**
   * Generate text utilities
   */
  generateTextUtilities() {
    let css = '';
    
    const textUtilities = {
      'text-left': 'text-align: left',
      'text-center': 'text-align: center',
      'text-right': 'text-align: right',
      'text-justify': 'text-align: justify'
    };
    
    this.breakpoints.forEach((breakpoint, name) => {
      const prefix = name === 'xs' ? '' : `${name}-`;
      
      Object.entries(textUtilities).forEach(([className, rule]) => {
        const fullClassName = `.${prefix}${className}`;
        const fullRule = `${fullClassName} { ${rule} !important; }`;
        
        if (name === 'xs') {
          css += fullRule;
        } else {
          css += `
            @media (min-width: ${breakpoint.min}px) {
              ${fullRule}
            }
          `;
        }
      });
    });
    
    return css;
  }

  /**
   * Setup layout utilities
   */
  setupLayoutUtilities() {
    this.utils = {
      getCurrentBreakpoint: () => this.currentBreakpoint,
      getViewport: () => this.currentViewport,
      isBreakpoint: (name) => this.currentBreakpoint === name,
      isAboveBreakpoint: (name) => {
        const current = this.breakpoints.get(this.currentBreakpoint);
        const target = this.breakpoints.get(name);
        return current && target && current.min >= target.min;
      },
      isBelowBreakpoint: (name) => {
        const current = this.breakpoints.get(this.currentBreakpoint);
        const target = this.breakpoints.get(name);
        return current && target && current.max <= target.max;
      },
      isMobile: () => this.getViewportType() === 'mobile',
      isTablet: () => this.getViewportType() === 'tablet',
      isDesktop: () => this.getViewportType() === 'desktop',
      isLandscape: () => this.currentViewport?.orientation === 'landscape',
      isPortrait: () => this.currentViewport?.orientation === 'portrait'
    };
  }

  /**
   * Register responsive component
   */
  registerResponsiveComponent(component) {
    this.responsiveComponents.add(component);
    
    // Call initial breakpoint handler
    if (component.onBreakpointChange) {
      component.onBreakpointChange(this.currentBreakpoint, this.currentViewport);
    }
  }

  /**
   * Unregister responsive component
   */
  unregisterResponsiveComponent(component) {
    this.responsiveComponents.delete(component);
  }

  /**
   * Register layout element
   */
  registerLayoutElement(element, config) {
    this.layoutElements.set(element, config);
    
    // Observe element for resize
    if (this.resizeObserver) {
      this.resizeObserver.observe(element);
    }
    
    // Apply initial configuration
    this.applyResponsiveConfig(element, config);
  }

  /**
   * Unregister layout element
   */
  unregisterLayoutElement(element) {
    this.layoutElements.delete(element);
    
    if (this.resizeObserver) {
      this.resizeObserver.unobserve(element);
    }
  }

  /**
   * Apply responsive configuration to element
   */
  applyResponsiveConfig(element, config) {
    const currentBreakpoint = this.currentBreakpoint;
    
    if (config[currentBreakpoint]) {
      const breakpointConfig = config[currentBreakpoint];
      
      // Apply classes
      if (breakpointConfig.classes) {
        element.className = breakpointConfig.classes;
      }
      
      // Apply styles
      if (breakpointConfig.styles) {
        Object.assign(element.style, breakpointConfig.styles);
      }
      
      // Apply attributes
      if (breakpointConfig.attributes) {
        Object.entries(breakpointConfig.attributes).forEach(([attr, value]) => {
          element.setAttribute(attr, value);
        });
      }
    }
  }

  /**
   * Parse responsive configuration from data attribute
   */
  parseResponsiveConfig(configString) {
    try {
      return JSON.parse(configString);
    } catch (error) {
      console.warn('Invalid responsive config:', configString);
      return {};
    }
  }

  /**
   * Generate image srcset
   */
  generateImageSrcSet(config) {
    if (!config.sources) return null;
    
    return Object.entries(config.sources)
      .map(([breakpoint, src]) => `${src} ${breakpoint}w`)
      .join(', ');
  }

  /**
   * Calculate responsive font size
   */
  calculateResponsiveFontSize(config) {
    const currentBreakpoint = this.currentBreakpoint;
    
    if (config[currentBreakpoint]) {
      return config[currentBreakpoint];
    }
    
    // Fallback to closest breakpoint
    const breakpointOrder = ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'];
    const currentIndex = breakpointOrder.indexOf(currentBreakpoint);
    
    for (let i = currentIndex - 1; i >= 0; i--) {
      if (config[breakpointOrder[i]]) {
        return config[breakpointOrder[i]];
      }
    }
    
    return null;
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
   * Get layout statistics
   */
  getStatistics() {
    return {
      currentBreakpoint: this.currentBreakpoint,
      viewport: this.currentViewport,
      responsiveComponents: this.responsiveComponents.size,
      layoutElements: this.layoutElements.size,
      mediaQueries: this.mediaQueries.size,
      breakpoints: Array.from(this.breakpoints.keys())
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Re-inject CSS if grid configuration changed
    if (newConfig.gridColumns || newConfig.gridGutter) {
      const styleElement = document.getElementById('ainflue-responsive-utilities');
      if (styleElement) {
        styleElement.textContent = this.generateResponsiveCSS();
      }
    }
  }

  /**
   * Force layout update
   */
  forceUpdate() {
    this.detectInitialBreakpoint();
    this.applyResponsiveChanges(this.currentBreakpoint, null);
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    // Remove media query listeners
    this.mediaQueries.forEach(({ mediaQuery, handler }) => {
      mediaQuery.removeListener(handler);
    });
    
    // Disconnect resize observer
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    
    // Remove style element
    const styleElement = document.getElementById('ainflue-responsive-utilities');
    if (styleElement) {
      styleElement.remove();
    }
    
    this.mediaQueries.clear();
    this.layoutElements.clear();
    this.responsiveComponents.clear();
    this.observers.clear();
    
    console.log('Responsive Layout cleaned up');
  }
}

// Create and export singleton instance
const responsiveLayout = new ResponsiveLayout();

// Export both class and instance
window.ResponsiveLayout = ResponsiveLayout;
window.responsiveLayout = responsiveLayout;

export { ResponsiveLayout, responsiveLayout };
export default responsiveLayout;