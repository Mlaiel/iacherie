/**
 * @fileoverview Theme Engine - Professional Theming System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/theme_engine
 * @description Advanced theming system with dynamic themes, animations, and accessibility
 */

class ThemeEngine {
  constructor() {
    this.themes = new Map();
    this.currentTheme = null;
    this.customProperties = new Map();
    this.animations = new Map();
    this.breakpoints = new Map();
    
    this.config = {
      enableTransitions: true,
      transitionDuration: '0.3s',
      enableAnimations: true,
      enableHighContrast: false,
      enableReducedMotion: false,
      autoDetectPreferences: true,
      persistTheme: true,
      enableDynamicColors: true
    };

    this.observers = {
      media: new Map(),
      mutation: null
    };

    this.initializeThemeEngine();
    console.log('Theme Engine initialized');
  }

  /**
   * Initialize the theme engine
   */
  initializeThemeEngine() {
    this.setupDefaultThemes();
    this.setupMediaQueries();
    this.setupAccessibilityFeatures();
    this.loadPersistedTheme();
    this.applySystemPreferences();
    this.setupStyleManagement();
  }

  /**
   * Setup default themes
   */
  setupDefaultThemes() {
    // Dark theme (default professional theme)
    this.registerTheme('dark', {
      name: 'Dark Professional',
      type: 'dark',
      colors: {
        // Primary colors
        primary: '#6366f1',
        primaryLight: '#818cf8',
        primaryDark: '#4f46e5',
        primaryContrast: '#ffffff',

        // Secondary colors
        secondary: '#06b6d4',
        secondaryLight: '#22d3ee',
        secondaryDark: '#0891b2',
        secondaryContrast: '#ffffff',

        // Success colors
        success: '#10b981',
        successLight: '#34d399',
        successDark: '#059669',
        successContrast: '#ffffff',

        // Warning colors
        warning: '#f59e0b',
        warningLight: '#fbbf24',
        warningDark: '#d97706',
        warningContrast: '#000000',

        // Error colors
        error: '#ef4444',
        errorLight: '#f87171',
        errorDark: '#dc2626',
        errorContrast: '#ffffff',

        // Neutral colors
        neutral50: '#fafafa',
        neutral100: '#f5f5f5',
        neutral200: '#e5e5e5',
        neutral300: '#d4d4d4',
        neutral400: '#a3a3a3',
        neutral500: '#737373',
        neutral600: '#525252',
        neutral700: '#404040',
        neutral800: '#262626',
        neutral900: '#171717',

        // Background colors
        background: '#0a0a0a',
        backgroundLight: '#1a1a1a',
        backgroundMedium: '#2a2a2a',
        backgroundContrast: '#ffffff',

        // Surface colors
        surface: '#1e1e1e',
        surfaceLight: '#2e2e2e',
        surfaceDark: '#0e0e0e',
        surfaceContrast: '#ffffff',

        // Text colors
        textPrimary: '#ffffff',
        textSecondary: '#a3a3a3',
        textTertiary: '#737373',
        textDisabled: '#525252',

        // Border colors
        border: '#404040',
        borderLight: '#525252',
        borderDark: '#262626',

        // Shadow colors
        shadow: 'rgba(0, 0, 0, 0.5)',
        shadowLight: 'rgba(0, 0, 0, 0.25)',
        shadowDark: 'rgba(0, 0, 0, 0.75)'
      },
      fonts: {
        primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        secondary: 'JetBrains Mono, "Fira Code", Monaco, "Courier New", monospace',
        sizes: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem',
          '4xl': '2.25rem',
          '5xl': '3rem'
        },
        weights: {
          light: 300,
          normal: 400,
          medium: 500,
          semibold: 600,
          bold: 700,
          extrabold: 800
        }
      },
      spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
        '3xl': '4rem',
        '4xl': '6rem',
        '5xl': '8rem'
      },
      borderRadius: {
        sm: '0.125rem',
        base: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        full: '9999px'
      },
      shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.5)',
        base: '0 1px 3px 0 rgba(0, 0, 0, 0.5), 0 1px 2px 0 rgba(0, 0, 0, 0.25)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.25)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.25)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.25)',
        inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.25)'
      },
      animations: {
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        transitionFast: 'all 0.15s cubic-bezier(0.4, 0, 0.2, 1)',
        transitionSlow: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        bounce: 'bounce 1s infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        spin: 'spin 1s linear infinite'
      }
    });

    // Light theme
    this.registerTheme('light', {
      name: 'Light Professional',
      type: 'light',
      colors: {
        // Primary colors
        primary: '#6366f1',
        primaryLight: '#818cf8',
        primaryDark: '#4f46e5',
        primaryContrast: '#ffffff',

        // Secondary colors
        secondary: '#06b6d4',
        secondaryLight: '#22d3ee',
        secondaryDark: '#0891b2',
        secondaryContrast: '#ffffff',

        // Success colors
        success: '#10b981',
        successLight: '#34d399',
        successDark: '#059669',
        successContrast: '#ffffff',

        // Warning colors
        warning: '#f59e0b',
        warningLight: '#fbbf24',
        warningDark: '#d97706',
        warningContrast: '#000000',

        // Error colors
        error: '#ef4444',
        errorLight: '#f87171',
        errorDark: '#dc2626',
        errorContrast: '#ffffff',

        // Neutral colors
        neutral50: '#fafafa',
        neutral100: '#f5f5f5',
        neutral200: '#e5e5e5',
        neutral300: '#d4d4d4',
        neutral400: '#a3a3a3',
        neutral500: '#737373',
        neutral600: '#525252',
        neutral700: '#404040',
        neutral800: '#262626',
        neutral900: '#171717',

        // Background colors
        background: '#ffffff',
        backgroundLight: '#fafafa',
        backgroundMedium: '#f5f5f5',
        backgroundContrast: '#000000',

        // Surface colors
        surface: '#ffffff',
        surfaceLight: '#fafafa',
        surfaceDark: '#f5f5f5',
        surfaceContrast: '#000000',

        // Text colors
        textPrimary: '#171717',
        textSecondary: '#525252',
        textTertiary: '#737373',
        textDisabled: '#a3a3a3',

        // Border colors
        border: '#e5e5e5',
        borderLight: '#f5f5f5',
        borderDark: '#d4d4d4',

        // Shadow colors
        shadow: 'rgba(0, 0, 0, 0.1)',
        shadowLight: 'rgba(0, 0, 0, 0.05)',
        shadowDark: 'rgba(0, 0, 0, 0.15)'
      },
      fonts: {
        primary: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        secondary: 'JetBrains Mono, "Fira Code", Monaco, "Courier New", monospace',
        sizes: {
          xs: '0.75rem',
          sm: '0.875rem',
          base: '1rem',
          lg: '1.125rem',
          xl: '1.25rem',
          '2xl': '1.5rem',
          '3xl': '1.875rem',
          '4xl': '2.25rem',
          '5xl': '3rem'
        },
        weights: {
          light: 300,
          normal: 400,
          medium: 500,
          semibold: 600,
          bold: 700,
          extrabold: 800
        }
      },
      spacing: {
        xs: '0.25rem',
        sm: '0.5rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
        '3xl': '4rem',
        '4xl': '6rem',
        '5xl': '8rem'
      },
      borderRadius: {
        sm: '0.125rem',
        base: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        full: '9999px'
      },
      shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
      },
      animations: {
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        transitionFast: 'all 0.15s cubic-bezier(0.4, 0, 0.2, 1)',
        transitionSlow: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        bounce: 'bounce 1s infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        spin: 'spin 1s linear infinite'
      }
    });

    // High contrast theme
    this.registerTheme('high-contrast', {
      name: 'High Contrast',
      type: 'high-contrast',
      colors: {
        primary: '#ffffff',
        primaryContrast: '#000000',
        secondary: '#ffff00',
        secondaryContrast: '#000000',
        success: '#00ff00',
        successContrast: '#000000',
        warning: '#ffff00',
        warningContrast: '#000000',
        error: '#ff0000',
        errorContrast: '#ffffff',
        background: '#000000',
        backgroundContrast: '#ffffff',
        surface: '#000000',
        surfaceContrast: '#ffffff',
        textPrimary: '#ffffff',
        textSecondary: '#ffffff',
        textTertiary: '#ffffff',
        border: '#ffffff',
        shadow: 'transparent'
      },
      fonts: {
        primary: 'Arial, sans-serif',
        secondary: 'Courier New, monospace',
        sizes: {
          xs: '0.875rem',
          sm: '1rem',
          base: '1.125rem',
          lg: '1.25rem',
          xl: '1.5rem',
          '2xl': '1.75rem',
          '3xl': '2rem',
          '4xl': '2.5rem',
          '5xl': '3.5rem'
        },
        weights: {
          light: 400,
          normal: 700,
          medium: 700,
          semibold: 700,
          bold: 900,
          extrabold: 900
        }
      },
      spacing: {
        xs: '0.5rem',
        sm: '0.75rem',
        md: '1.25rem',
        lg: '2rem',
        xl: '2.5rem',
        '2xl': '3.5rem',
        '3xl': '4.5rem',
        '4xl': '6.5rem',
        '5xl': '8.5rem'
      },
      borderRadius: {
        sm: '0rem',
        base: '0rem',
        md: '0rem',
        lg: '0rem',
        xl: '0rem',
        '2xl': '0rem',
        full: '0rem'
      },
      shadows: {
        sm: 'none',
        base: 'none',
        md: 'none',
        lg: 'none',
        xl: 'none',
        inner: 'none'
      },
      animations: {
        transition: 'none',
        transitionFast: 'none',
        transitionSlow: 'none',
        bounce: 'none',
        pulse: 'none',
        spin: 'none'
      }
    });
  }

  /**
   * Setup media queries for responsive design
   */
  setupMediaQueries() {
    const queries = [
      // Color scheme preference
      {
        name: 'prefers-color-scheme-dark',
        query: '(prefers-color-scheme: dark)',
        handler: this.handleColorSchemeChange.bind(this)
      },
      // Reduced motion preference
      {
        name: 'prefers-reduced-motion',
        query: '(prefers-reduced-motion: reduce)',
        handler: this.handleReducedMotionChange.bind(this)
      },
      // High contrast preference
      {
        name: 'prefers-contrast-high',
        query: '(prefers-contrast: high)',
        handler: this.handleHighContrastChange.bind(this)
      },
      // Screen size breakpoints
      {
        name: 'mobile',
        query: '(max-width: 767px)',
        handler: this.handleBreakpointChange.bind(this)
      },
      {
        name: 'tablet',
        query: '(min-width: 768px) and (max-width: 1023px)',
        handler: this.handleBreakpointChange.bind(this)
      },
      {
        name: 'desktop',
        query: '(min-width: 1024px)',
        handler: this.handleBreakpointChange.bind(this)
      }
    ];

    queries.forEach(({ name, query, handler }) => {
      const mediaQuery = window.matchMedia(query);
      mediaQuery.addListener(handler);
      this.observers.media.set(name, { mediaQuery, handler });
      
      // Call handler initially
      handler(mediaQuery);
    });
  }

  /**
   * Setup accessibility features
   */
  setupAccessibilityFeatures() {
    // Focus management
    this.setupFocusManagement();
    
    // Keyboard navigation
    this.setupKeyboardNavigation();
    
    // Screen reader support
    this.setupScreenReaderSupport();
  }

  /**
   * Setup focus management
   */
  setupFocusManagement() {
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.remove('keyboard-navigation');
    });
  }

  /**
   * Setup keyboard navigation
   */
  setupKeyboardNavigation() {
    document.addEventListener('keydown', (event) => {
      // Escape key handling
      if (event.key === 'Escape') {
        this.handleEscapeKey(event);
      }
      
      // Arrow key navigation
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
        this.handleArrowNavigation(event);
      }
    });
  }

  /**
   * Setup screen reader support
   */
  setupScreenReaderSupport() {
    // Add live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    document.body.appendChild(liveRegion);
    
    this.liveRegion = liveRegion;
  }

  /**
   * Setup style management
   */
  setupStyleManagement() {
    // Create style element for theme variables
    this.styleElement = document.createElement('style');
    this.styleElement.id = 'ainflue-theme-variables';
    document.head.appendChild(this.styleElement);

    // Create style element for animations
    this.animationStyleElement = document.createElement('style');
    this.animationStyleElement.id = 'ainflue-theme-animations';
    document.head.appendChild(this.animationStyleElement);

    // Add default animations
    this.setupDefaultAnimations();
  }

  /**
   * Setup default animations
   */
  setupDefaultAnimations() {
    const animations = `
      @keyframes bounce {
        0%, 20%, 53%, 80%, 100% {
          animation-timing-function: cubic-bezier(0.215, 0.610, 0.355, 1.000);
          transform: translate3d(0,0,0);
        }
        40%, 43% {
          animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
          transform: translate3d(0, -30px, 0);
        }
        70% {
          animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
          transform: translate3d(0, -15px, 0);
        }
        90% {
          transform: translate3d(0,-4px,0);
        }
      }

      @keyframes pulse {
        0%, 100% {
          opacity: 1;
        }
        50% {
          opacity: .5;
        }
      }

      @keyframes spin {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
        }
        to {
          opacity: 1;
        }
      }

      @keyframes fadeOut {
        from {
          opacity: 1;
        }
        to {
          opacity: 0;
        }
      }

      @keyframes slideInLeft {
        from {
          transform: translateX(-100%);
        }
        to {
          transform: translateX(0);
        }
      }

      @keyframes slideInRight {
        from {
          transform: translateX(100%);
        }
        to {
          transform: translateX(0);
        }
      }

      @keyframes slideInUp {
        from {
          transform: translateY(100%);
        }
        to {
          transform: translateY(0);
        }
      }

      @keyframes slideInDown {
        from {
          transform: translateY(-100%);
        }
        to {
          transform: translateY(0);
        }
      }
    `;

    this.animationStyleElement.textContent = animations;
  }

  /**
   * Register a theme
   */
  registerTheme(name, theme) {
    if (this.themes.has(name)) {
      console.warn(`Theme '${name}' is being overridden`);
    }
    
    this.themes.set(name, {
      ...theme,
      name: theme.name || name,
      type: theme.type || 'custom'
    });
  }

  /**
   * Apply theme
   */
  applyTheme(themeName) {
    const theme = this.themes.get(themeName);
    
    if (!theme) {
      console.error(`Theme '${themeName}' not found`);
      return false;
    }

    this.currentTheme = themeName;
    
    // Apply CSS custom properties
    this.applyCSSVariables(theme);
    
    // Apply theme class
    this.applyThemeClass(themeName);
    
    // Persist theme preference
    if (this.config.persistTheme) {
      localStorage.setItem('ainflue-theme', themeName);
    }

    // Emit theme change event
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('app.theme-changed', {
        theme: themeName,
        themeData: theme
      });
    }

    // Announce to screen readers
    this.announceToScreenReader(`Theme changed to ${theme.name}`);

    console.log(`Theme applied: ${theme.name}`);
    return true;
  }

  /**
   * Apply CSS custom properties
   */
  applyCSSVariables(theme) {
    const variables = [];

    // Colors
    if (theme.colors) {
      Object.entries(theme.colors).forEach(([key, value]) => {
        variables.push(`--color-${this.kebabCase(key)}: ${value}`);
      });
    }

    // Fonts
    if (theme.fonts) {
      if (theme.fonts.primary) {
        variables.push(`--font-primary: ${theme.fonts.primary}`);
      }
      if (theme.fonts.secondary) {
        variables.push(`--font-secondary: ${theme.fonts.secondary}`);
      }
      
      if (theme.fonts.sizes) {
        Object.entries(theme.fonts.sizes).forEach(([key, value]) => {
          variables.push(`--font-size-${key}: ${value}`);
        });
      }
      
      if (theme.fonts.weights) {
        Object.entries(theme.fonts.weights).forEach(([key, value]) => {
          variables.push(`--font-weight-${key}: ${value}`);
        });
      }
    }

    // Spacing
    if (theme.spacing) {
      Object.entries(theme.spacing).forEach(([key, value]) => {
        variables.push(`--spacing-${key}: ${value}`);
      });
    }

    // Border radius
    if (theme.borderRadius) {
      Object.entries(theme.borderRadius).forEach(([key, value]) => {
        variables.push(`--border-radius-${key}: ${value}`);
      });
    }

    // Shadows
    if (theme.shadows) {
      Object.entries(theme.shadows).forEach(([key, value]) => {
        variables.push(`--shadow-${key}: ${value}`);
      });
    }

    // Animations
    if (theme.animations) {
      Object.entries(theme.animations).forEach(([key, value]) => {
        variables.push(`--animation-${this.kebabCase(key)}: ${value}`);
      });
    }

    // Apply variables to :root
    const css = `:root { ${variables.join('; ')}; }`;
    this.styleElement.textContent = css;
  }

  /**
   * Apply theme class to body
   */
  applyThemeClass(themeName) {
    // Remove existing theme classes
    document.body.classList.forEach(className => {
      if (className.startsWith('theme-')) {
        document.body.classList.remove(className);
      }
    });

    // Add new theme class
    document.body.classList.add(`theme-${themeName}`);
  }

  /**
   * Handle color scheme change
   */
  handleColorSchemeChange(mediaQuery) {
    if (!this.config.autoDetectPreferences) return;

    if (mediaQuery.matches && !this.currentTheme) {
      // User prefers dark mode and no theme is set
      this.applyTheme('dark');
    } else if (!mediaQuery.matches && !this.currentTheme) {
      // User prefers light mode and no theme is set
      this.applyTheme('light');
    }
  }

  /**
   * Handle reduced motion change
   */
  handleReducedMotionChange(mediaQuery) {
    this.config.enableReducedMotion = mediaQuery.matches;
    
    if (mediaQuery.matches) {
      document.body.classList.add('reduce-motion');
      // Disable animations
      document.body.style.setProperty('--animation-transition', 'none');
      document.body.style.setProperty('--animation-transition-fast', 'none');
      document.body.style.setProperty('--animation-transition-slow', 'none');
    } else {
      document.body.classList.remove('reduce-motion');
      // Re-enable animations
      document.body.style.removeProperty('--animation-transition');
      document.body.style.removeProperty('--animation-transition-fast');
      document.body.style.removeProperty('--animation-transition-slow');
    }
  }

  /**
   * Handle high contrast change
   */
  handleHighContrastChange(mediaQuery) {
    this.config.enableHighContrast = mediaQuery.matches;
    
    if (mediaQuery.matches) {
      this.applyTheme('high-contrast');
    }
  }

  /**
   * Handle breakpoint change
   */
  handleBreakpointChange(mediaQuery) {
    // This could be used to apply responsive theme adjustments
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('ui.breakpoint-changed', {
        breakpoint: mediaQuery.media,
        matches: mediaQuery.matches
      });
    }
  }

  /**
   * Handle escape key
   */
  handleEscapeKey(event) {
    // Close modals, dropdowns, etc.
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('ui.escape-key-pressed', { event });
    }
  }

  /**
   * Handle arrow navigation
   */
  handleArrowNavigation(event) {
    // Implement arrow key navigation logic
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('ui.arrow-navigation', { 
        key: event.key,
        event 
      });
    }
  }

  /**
   * Load persisted theme
   */
  loadPersistedTheme() {
    if (!this.config.persistTheme) return;

    const persistedTheme = localStorage.getItem('ainflue-theme');
    if (persistedTheme && this.themes.has(persistedTheme)) {
      this.applyTheme(persistedTheme);
    }
  }

  /**
   * Apply system preferences
   */
  applySystemPreferences() {
    if (!this.config.autoDetectPreferences) return;

    // Apply based on current media query states
    this.observers.media.forEach(({ mediaQuery, handler }) => {
      handler(mediaQuery);
    });
  }

  /**
   * Create custom theme variation
   */
  createThemeVariation(baseName, variationName, overrides) {
    const baseTheme = this.themes.get(baseName);
    
    if (!baseTheme) {
      throw new Error(`Base theme '${baseName}' not found`);
    }

    const variation = this.deepMerge(baseTheme, overrides);
    variation.name = overrides.name || `${baseTheme.name} (${variationName})`;
    
    this.registerTheme(variationName, variation);
    return variation;
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return this.currentTheme;
  }

  /**
   * Get theme data
   */
  getTheme(name) {
    return this.themes.get(name || this.currentTheme);
  }

  /**
   * Get all themes
   */
  getAllThemes() {
    return Array.from(this.themes.entries()).map(([name, theme]) => ({
      name,
      displayName: theme.name,
      type: theme.type
    }));
  }

  /**
   * Set custom property
   */
  setCustomProperty(property, value) {
    this.customProperties.set(property, value);
    document.documentElement.style.setProperty(`--${property}`, value);
  }

  /**
   * Get custom property
   */
  getCustomProperty(property) {
    return this.customProperties.get(property) ||
           getComputedStyle(document.documentElement).getPropertyValue(`--${property}`);
  }

  /**
   * Remove custom property
   */
  removeCustomProperty(property) {
    this.customProperties.delete(property);
    document.documentElement.style.removeProperty(`--${property}`);
  }

  /**
   * Announce to screen reader
   */
  announceToScreenReader(message) {
    if (this.liveRegion) {
      this.liveRegion.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        this.liveRegion.textContent = '';
      }, 1000);
    }
  }

  /**
   * Convert camelCase to kebab-case
   */
  kebabCase(str) {
    return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
  }

  /**
   * Deep merge objects
   */
  deepMerge(target, source) {
    const result = { ...target };
    
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(result[key] || {}, source[key]);
      } else {
        result[key] = source[key];
      }
    }
    
    return result;
  }

  /**
   * Toggle between themes
   */
  toggleTheme(theme1 = 'light', theme2 = 'dark') {
    const newTheme = this.currentTheme === theme1 ? theme2 : theme1;
    this.applyTheme(newTheme);
  }

  /**
   * Get theme statistics
   */
  getStatistics() {
    return {
      totalThemes: this.themes.size,
      currentTheme: this.currentTheme,
      customProperties: this.customProperties.size,
      mediaQueries: this.observers.media.size,
      enabledFeatures: {
        transitions: this.config.enableTransitions,
        animations: this.config.enableAnimations,
        highContrast: this.config.enableHighContrast,
        reducedMotion: this.config.enableReducedMotion
      }
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Re-apply theme if necessary
    if (this.currentTheme) {
      this.applyTheme(this.currentTheme);
    }
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    // Remove media query listeners
    this.observers.media.forEach(({ mediaQuery, handler }) => {
      mediaQuery.removeListener(handler);
    });
    
    // Remove style elements
    if (this.styleElement) {
      this.styleElement.remove();
    }
    
    if (this.animationStyleElement) {
      this.animationStyleElement.remove();
    }
    
    // Remove live region
    if (this.liveRegion) {
      this.liveRegion.remove();
    }
    
    this.themes.clear();
    this.customProperties.clear();
    this.observers.media.clear();
    
    console.log('Theme Engine cleaned up');
  }
}

// Create and export singleton instance
const themeEngine = new ThemeEngine();

// Export both class and instance
window.ThemeEngine = ThemeEngine;
window.themeEngine = themeEngine;

export { ThemeEngine, themeEngine };
export default themeEngine;