/**
 * @fileoverview Accessibility Manager - Comprehensive Accessibility System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/accessibility_manager
 * @description Professional accessibility features including ARIA, keyboard navigation, and screen reader support
 */

class AccessibilityManager {
  constructor() {
    this.focusableElements = new Set();
    this.keyboardTraps = new Set();
    this.announcements = [];
    this.landmarkRegions = new Map();
    this.skipLinks = new Set();
    
    this.config = {
      enableFocusManagement: true,
      enableKeyboardNavigation: true,
      enableScreenReaderSupport: true,
      enableHighContrast: true,
      enableReducedMotion: true,
      enableAutoFocus: false,
      focusOutlineStyle: 'default',
      announcePageChanges: true,
      announceErrors: true,
      skipLinkSelector: '.skip-link'
    };

    this.state = {
      focusedElement: null,
      keyboardNavigationActive: false,
      screenReaderActive: false,
      highContrastMode: false,
      reducedMotionMode: false
    };

    this.keyBindings = new Map();
    this.focusHistory = [];
    this.maxFocusHistory = 10;

    this.initializeAccessibility();
    console.log('Accessibility Manager initialized');
  }

  /**
   * Initialize accessibility features
   */
  initializeAccessibility() {
    this.setupFocusManagement();
    this.setupKeyboardNavigation();
    this.setupScreenReaderSupport();
    this.setupARIASupport();
    this.setupMediaQueryListeners();
    this.setupSkipLinks();
    this.setupLandmarks();
    this.injectAccessibilityCSS();
    this.performInitialAudit();
  }

  /**
   * Setup focus management
   */
  setupFocusManagement() {
    if (!this.config.enableFocusManagement) return;

    // Track focus changes
    document.addEventListener('focusin', this.handleFocusIn.bind(this));
    document.addEventListener('focusout', this.handleFocusOut.bind(this));

    // Keyboard navigation detection
    document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
    document.addEventListener('mousedown', this.handleMouseNavigation.bind(this));

    // Focus visibility management
    this.setupFocusVisibility();
  }

  /**
   * Setup focus visibility
   */
  setupFocusVisibility() {
    const style = document.createElement('style');
    style.id = 'ainflue-focus-styles';
    
    let focusCSS = '';
    
    switch (this.config.focusOutlineStyle) {
      case 'enhanced':
        focusCSS = `
          .js-focus-visible :focus:not(.focus-visible) {
            outline: none;
          }
          
          .focus-visible {
            outline: 2px solid var(--color-primary, #6366f1) !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
          }
        `;
        break;
      case 'high-contrast':
        focusCSS = `
          .js-focus-visible :focus:not(.focus-visible) {
            outline: none;
          }
          
          .focus-visible {
            outline: 3px solid #000000 !important;
            outline-offset: 1px !important;
            background: #ffff00 !important;
            color: #000000 !important;
          }
          
          @media (prefers-color-scheme: dark) {
            .focus-visible {
              outline: 3px solid #ffffff !important;
              background: #000000 !important;
              color: #ffffff !important;
            }
          }
        `;
        break;
      default:
        focusCSS = `
          .js-focus-visible :focus:not(.focus-visible) {
            outline: none;
          }
          
          .focus-visible {
            outline: 2px solid var(--color-primary, #6366f1) !important;
            outline-offset: 2px !important;
          }
        `;
    }
    
    style.textContent = focusCSS;
    document.head.appendChild(style);

    // Apply focus-visible polyfill behavior
    document.body.classList.add('js-focus-visible');
  }

  /**
   * Setup keyboard navigation
   */
  setupKeyboardNavigation() {
    if (!this.config.enableKeyboardNavigation) return;

    // Register default key bindings
    this.registerKeyBinding('Tab', this.handleTabNavigation.bind(this));
    this.registerKeyBinding('Shift+Tab', this.handleShiftTabNavigation.bind(this));
    this.registerKeyBinding('Escape', this.handleEscapeKey.bind(this));
    this.registerKeyBinding('Enter', this.handleEnterKey.bind(this));
    this.registerKeyBinding('Space', this.handleSpaceKey.bind(this));
    this.registerKeyBinding('ArrowDown', this.handleArrowNavigation.bind(this));
    this.registerKeyBinding('ArrowUp', this.handleArrowNavigation.bind(this));
    this.registerKeyBinding('ArrowLeft', this.handleArrowNavigation.bind(this));
    this.registerKeyBinding('ArrowRight', this.handleArrowNavigation.bind(this));
    this.registerKeyBinding('Home', this.handleHomeKey.bind(this));
    this.registerKeyBinding('End', this.handleEndKey.bind(this));

    // Global keyboard event listener
    document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
  }

  /**
   * Setup screen reader support
   */
  setupScreenReaderSupport() {
    if (!this.config.enableScreenReaderSupport) return;

    // Create live regions for announcements
    this.createLiveRegions();

    // Setup page change announcements
    if (this.config.announcePageChanges) {
      this.setupPageChangeAnnouncements();
    }

    // Setup error announcements
    if (this.config.announceErrors) {
      this.setupErrorAnnouncements();
    }

    // Detect screen reader
    this.detectScreenReader();
  }

  /**
   * Create live regions for screen reader announcements
   */
  createLiveRegions() {
    // Polite live region
    this.politeRegion = this.createLiveRegion('polite');
    
    // Assertive live region
    this.assertiveRegion = this.createLiveRegion('assertive');
    
    // Status region
    this.statusRegion = this.createLiveRegion('polite', 'status');
  }

  /**
   * Create a live region element
   */
  createLiveRegion(politeness, role = null) {
    const region = document.createElement('div');
    region.setAttribute('aria-live', politeness);
    region.setAttribute('aria-atomic', 'true');
    
    if (role) {
      region.setAttribute('role', role);
    }
    
    // Hide visually but keep accessible
    region.style.cssText = `
      position: absolute !important;
      left: -10000px !important;
      width: 1px !important;
      height: 1px !important;
      overflow: hidden !important;
    `;
    
    document.body.appendChild(region);
    return region;
  }

  /**
   * Setup ARIA support
   */
  setupARIASupport() {
    // Auto-add ARIA labels for common elements
    this.autoAddARIALabels();
    
    // Setup ARIA live region observers
    this.setupARIAObservers();
    
    // Setup role-specific behaviors
    this.setupRoleBehaviors();
  }

  /**
   * Auto-add ARIA labels
   */
  autoAddARIALabels() {
    // Add labels to form controls without labels
    const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby]), textarea:not([aria-label]):not([aria-labelledby]), select:not([aria-label]):not([aria-labelledby])');
    
    unlabeledInputs.forEach(input => {
      const placeholder = input.getAttribute('placeholder');
      const name = input.getAttribute('name');
      
      if (placeholder) {
        input.setAttribute('aria-label', placeholder);
      } else if (name) {
        input.setAttribute('aria-label', this.humanizeString(name));
      }
    });

    // Add labels to buttons without text or labels
    const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby]):empty, button:not([aria-label]):not([aria-labelledby])[title]');
    
    unlabeledButtons.forEach(button => {
      const title = button.getAttribute('title');
      if (title) {
        button.setAttribute('aria-label', title);
      }
    });
  }

  /**
   * Setup media query listeners for accessibility preferences
   */
  setupMediaQueryListeners() {
    // High contrast preference
    if (window.matchMedia) {
      const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
      highContrastQuery.addListener(this.handleHighContrastChange.bind(this));
      this.handleHighContrastChange(highContrastQuery);

      // Reduced motion preference
      const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      reducedMotionQuery.addListener(this.handleReducedMotionChange.bind(this));
      this.handleReducedMotionChange(reducedMotionQuery);
    }
  }

  /**
   * Setup skip links
   */
  setupSkipLinks() {
    const skipLinks = document.querySelectorAll(this.config.skipLinkSelector);
    
    skipLinks.forEach(link => {
      this.skipLinks.add(link);
      link.addEventListener('click', this.handleSkipLinkClick.bind(this));
    });

    // Auto-create skip link if none exists
    if (skipLinks.length === 0) {
      this.createDefaultSkipLink();
    }
  }

  /**
   * Create default skip link
   */
  createDefaultSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
      position: absolute;
      top: -40px;
      left: 6px;
      background: var(--color-background, #fff);
      color: var(--color-text-primary, #000);
      padding: 8px;
      text-decoration: none;
      border-radius: 0 0 4px 4px;
      border: 2px solid var(--color-primary, #6366f1);
      z-index: 1000;
      transition: top 0.3s;
    `;

    // Show on focus
    skipLink.addEventListener('focus', () => {
      skipLink.style.top = '0';
    });

    skipLink.addEventListener('blur', () => {
      skipLink.style.top = '-40px';
    });

    document.body.insertBefore(skipLink, document.body.firstChild);
    this.skipLinks.add(skipLink);
  }

  /**
   * Setup landmarks
   */
  setupLandmarks() {
    // Identify and register landmarks
    const landmarks = document.querySelectorAll('[role="banner"], [role="navigation"], [role="main"], [role="complementary"], [role="contentinfo"], header, nav, main, aside, footer');
    
    landmarks.forEach(landmark => {
      const role = landmark.getAttribute('role') || this.getImplicitRole(landmark.tagName.toLowerCase());
      this.landmarkRegions.set(landmark, role);
    });

    // Add landmark navigation
    this.setupLandmarkNavigation();
  }

  /**
   * Get implicit ARIA role for HTML elements
   */
  getImplicitRole(tagName) {
    const roles = {
      'header': 'banner',
      'nav': 'navigation',
      'main': 'main',
      'aside': 'complementary',
      'footer': 'contentinfo',
      'article': 'article',
      'section': 'region',
      'button': 'button',
      'a': 'link',
      'img': 'img'
    };
    
    return roles[tagName] || null;
  }

  /**
   * Setup landmark navigation
   */
  setupLandmarkNavigation() {
    // Alt+1-9 for landmark navigation
    for (let i = 1; i <= 9; i++) {
      this.registerKeyBinding(`Alt+${i}`, (event) => {
        event.preventDefault();
        this.navigateToLandmark(i - 1);
      });
    }
  }

  /**
   * Inject accessibility CSS
   */
  injectAccessibilityCSS() {
    const style = document.createElement('style');
    style.id = 'ainflue-accessibility-utilities';
    
    style.textContent = `
      /* Screen reader only content */
      .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
      }
      
      /* Focus management */
      .no-focus-outline:focus {
        outline: none !important;
      }
      
      /* High contrast mode */
      @media (prefers-contrast: high) {
        * {
          background-color: transparent !important;
          color: ButtonText !important;
          border-color: ButtonText !important;
        }
        
        a, button, [role="button"] {
          background-color: ButtonFace !important;
          color: ButtonText !important;
          border: 2px solid ButtonText !important;
        }
        
        a:hover, a:focus,
        button:hover, button:focus,
        [role="button"]:hover, [role="button"]:focus {
          background-color: Highlight !important;
          color: HighlightText !important;
        }
      }
      
      /* Reduced motion */
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
          scroll-behavior: auto !important;
        }
      }
      
      /* Skip links */
      .skip-link:not(:focus) {
        position: absolute !important;
        top: -40px !important;
        left: 6px !important;
      }
      
      .skip-link:focus {
        position: absolute !important;
        top: 0 !important;
        left: 6px !important;
        z-index: 1000 !important;
      }
      
      /* Focus indicators */
      .focus-indicator {
        outline: 2px solid var(--color-primary, #6366f1) !important;
        outline-offset: 2px !important;
      }
      
      /* Keyboard navigation indicators */
      .keyboard-navigation-active *:focus {
        outline: 2px solid var(--color-primary, #6366f1) !important;
        outline-offset: 2px !important;
      }
    `;
    
    document.head.appendChild(style);
  }

  /**
   * Perform initial accessibility audit
   */
  performInitialAudit() {
    const issues = [];

    // Check for missing alt text on images
    const images = document.querySelectorAll('img:not([alt])');
    if (images.length > 0) {
      issues.push(`${images.length} images missing alt text`);
    }

    // Check for missing form labels
    const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby]):not([id]), textarea:not([aria-label]):not([aria-labelledby]):not([id])');
    if (unlabeledInputs.length > 0) {
      issues.push(`${unlabeledInputs.length} form controls missing labels`);
    }

    // Check for missing heading structure
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    if (headings.length === 0) {
      issues.push('No heading structure found');
    }

    // Check for missing main landmark
    const main = document.querySelector('main, [role="main"]');
    if (!main) {
      issues.push('No main landmark found');
    }

    if (issues.length > 0) {
      console.warn('Accessibility issues found:', issues);
    } else {
      console.log('Initial accessibility audit passed');
    }

    return issues;
  }

  /**
   * Handle focus in events
   */
  handleFocusIn(event) {
    this.state.focusedElement = event.target;
    this.addToFocusHistory(event.target);

    // Add focus indicator
    event.target.classList.add('focus-visible');

    // Emit focus event
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('accessibility.focus-changed', {
        element: event.target,
        previousElement: this.focusHistory[this.focusHistory.length - 2]
      });
    }
  }

  /**
   * Handle focus out events
   */
  handleFocusOut(event) {
    // Remove focus indicator
    event.target.classList.remove('focus-visible');
  }

  /**
   * Handle keyboard navigation detection
   */
  handleKeyboardNavigation(event) {
    if (event.key === 'Tab') {
      this.state.keyboardNavigationActive = true;
      document.body.classList.add('keyboard-navigation-active');
    }
  }

  /**
   * Handle mouse navigation detection
   */
  handleMouseNavigation() {
    this.state.keyboardNavigationActive = false;
    document.body.classList.remove('keyboard-navigation-active');
  }

  /**
   * Handle global keydown events
   */
  handleGlobalKeydown(event) {
    const key = this.getKeyString(event);
    const handler = this.keyBindings.get(key);
    
    if (handler) {
      handler(event);
    }
  }

  /**
   * Get key string representation
   */
  getKeyString(event) {
    const parts = [];
    
    if (event.ctrlKey) parts.push('Ctrl');
    if (event.altKey) parts.push('Alt');
    if (event.shiftKey) parts.push('Shift');
    if (event.metaKey) parts.push('Meta');
    
    parts.push(event.key);
    
    return parts.join('+');
  }

  /**
   * Register key binding
   */
  registerKeyBinding(keyString, handler) {
    this.keyBindings.set(keyString, handler);
  }

  /**
   * Unregister key binding
   */
  unregisterKeyBinding(keyString) {
    this.keyBindings.delete(keyString);
  }

  /**
   * Handle Tab navigation
   */
  handleTabNavigation(event) {
    // Let browser handle default tab behavior unless in a focus trap
    if (this.isInFocusTrap(event.target)) {
      this.handleFocusTrapNavigation(event, 'forward');
    }
  }

  /**
   * Handle Shift+Tab navigation
   */
  handleShiftTabNavigation(event) {
    if (this.isInFocusTrap(event.target)) {
      this.handleFocusTrapNavigation(event, 'backward');
    }
  }

  /**
   * Handle escape key
   */
  handleEscapeKey(event) {
    // Close modals, dialogs, etc.
    if (window.eventDispatcher) {
      window.eventDispatcher.emit('accessibility.escape-pressed', { event });
    }
  }

  /**
   * Handle enter key
   */
  handleEnterKey(event) {
    // Activate buttons, links, etc.
    const target = event.target;
    
    if (target.matches('[role="button"], [role="menuitem"], [role="tab"]') && !target.disabled) {
      event.preventDefault();
      target.click();
    }
  }

  /**
   * Handle space key
   */
  handleSpaceKey(event) {
    // Activate buttons, checkboxes, etc.
    const target = event.target;
    
    if (target.matches('[role="button"], [role="checkbox"]') && !target.disabled) {
      event.preventDefault();
      target.click();
    }
  }

  /**
   * Handle arrow navigation
   */
  handleArrowNavigation(event) {
    const target = event.target;
    
    // Handle specific role-based navigation
    if (target.matches('[role="tablist"] [role="tab"]')) {
      this.handleTablistNavigation(event);
    } else if (target.matches('[role="menu"] [role="menuitem"], [role="menubar"] [role="menuitem"]')) {
      this.handleMenuNavigation(event);
    } else if (target.matches('[role="listbox"] [role="option"]')) {
      this.handleListboxNavigation(event);
    }
  }

  /**
   * Handle home key
   */
  handleHomeKey(event) {
    // Navigate to first focusable element in container
    const container = this.findNavigationContainer(event.target);
    if (container) {
      const firstFocusable = this.getFirstFocusableElement(container);
      if (firstFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  /**
   * Handle end key
   */
  handleEndKey(event) {
    // Navigate to last focusable element in container
    const container = this.findNavigationContainer(event.target);
    if (container) {
      const lastFocusable = this.getLastFocusableElement(container);
      if (lastFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    }
  }

  /**
   * Announce message to screen readers
   */
  announce(message, priority = 'polite') {
    if (!this.config.enableScreenReaderSupport) return;

    const region = priority === 'assertive' ? this.assertiveRegion : this.politeRegion;
    
    // Clear and set new message
    region.textContent = '';
    setTimeout(() => {
      region.textContent = message;
    }, 100);

    // Add to announcements history
    this.announcements.push({
      message,
      priority,
      timestamp: Date.now()
    });

    // Keep only recent announcements
    if (this.announcements.length > 50) {
      this.announcements.shift();
    }
  }

  /**
   * Create focus trap
   */
  createFocusTrap(container) {
    const focusableElements = this.getFocusableElements(container);
    
    const trap = {
      container,
      firstFocusable: focusableElements[0],
      lastFocusable: focusableElements[focusableElements.length - 1],
      previousFocus: document.activeElement
    };

    this.keyboardTraps.add(trap);
    
    // Focus first element
    if (trap.firstFocusable) {
      trap.firstFocusable.focus();
    }

    return trap;
  }

  /**
   * Remove focus trap
   */
  removeFocusTrap(trap) {
    this.keyboardTraps.delete(trap);
    
    // Restore previous focus
    if (trap.previousFocus && trap.previousFocus.focus) {
      trap.previousFocus.focus();
    }
  }

  /**
   * Get focusable elements
   */
  getFocusableElements(container = document) {
    const selector = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"]), [role="button"]:not([disabled]), [role="link"]:not([disabled])';
    
    return Array.from(container.querySelectorAll(selector))
      .filter(element => {
        return element.offsetWidth > 0 && 
               element.offsetHeight > 0 && 
               !element.hasAttribute('hidden') &&
               getComputedStyle(element).visibility !== 'hidden';
      });
  }

  /**
   * Navigate to landmark
   */
  navigateToLandmark(index) {
    const landmarks = Array.from(this.landmarkRegions.keys());
    
    if (landmarks[index]) {
      landmarks[index].focus();
      this.announce(`Navigated to ${this.landmarkRegions.get(landmarks[index])} landmark`);
    }
  }

  /**
   * Handle high contrast change
   */
  handleHighContrastChange(mediaQuery) {
    this.state.highContrastMode = mediaQuery.matches;
    
    if (mediaQuery.matches) {
      document.body.classList.add('high-contrast-mode');
    } else {
      document.body.classList.remove('high-contrast-mode');
    }

    if (window.eventDispatcher) {
      window.eventDispatcher.emit('accessibility.high-contrast-changed', {
        enabled: mediaQuery.matches
      });
    }
  }

  /**
   * Handle reduced motion change
   */
  handleReducedMotionChange(mediaQuery) {
    this.state.reducedMotionMode = mediaQuery.matches;
    
    if (mediaQuery.matches) {
      document.body.classList.add('reduced-motion-mode');
    } else {
      document.body.classList.remove('reduced-motion-mode');
    }

    if (window.eventDispatcher) {
      window.eventDispatcher.emit('accessibility.reduced-motion-changed', {
        enabled: mediaQuery.matches
      });
    }
  }

  /**
   * Detect screen reader
   */
  detectScreenReader() {
    // This is a simplified detection method
    // In reality, screen reader detection is not recommended
    const hasScreenReader = window.navigator.userAgent.includes('NVDA') ||
                           window.navigator.userAgent.includes('JAWS') ||
                           window.speechSynthesis;
    
    this.state.screenReaderActive = hasScreenReader;
  }

  /**
   * Add element to focus history
   */
  addToFocusHistory(element) {
    this.focusHistory.push(element);
    
    if (this.focusHistory.length > this.maxFocusHistory) {
      this.focusHistory.shift();
    }
  }

  /**
   * Humanize string (convert camelCase/snake_case to readable text)
   */
  humanizeString(str) {
    return str
      .replace(/([A-Z])/g, ' $1')
      .replace(/[_-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase()
      .replace(/^\w/, c => c.toUpperCase());
  }

  /**
   * Get accessibility statistics
   */
  getStatistics() {
    return {
      focusableElements: this.focusableElements.size,
      keyboardTraps: this.keyboardTraps.size,
      announcements: this.announcements.length,
      landmarks: this.landmarkRegions.size,
      skipLinks: this.skipLinks.size,
      keyBindings: this.keyBindings.size,
      state: { ...this.state }
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    // Reapply configuration-dependent features
    if (newConfig.focusOutlineStyle) {
      this.setupFocusVisibility();
    }
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    // Remove live regions
    if (this.politeRegion) {
      this.politeRegion.remove();
    }
    if (this.assertiveRegion) {
      this.assertiveRegion.remove();
    }
    if (this.statusRegion) {
      this.statusRegion.remove();
    }

    // Remove style elements
    const styleElement = document.getElementById('ainflue-accessibility-utilities');
    if (styleElement) {
      styleElement.remove();
    }

    const focusStyleElement = document.getElementById('ainflue-focus-styles');
    if (focusStyleElement) {
      focusStyleElement.remove();
    }

    // Clear collections
    this.focusableElements.clear();
    this.keyboardTraps.clear();
    this.landmarkRegions.clear();
    this.skipLinks.clear();
    this.keyBindings.clear();
    this.announcements.length = 0;
    this.focusHistory.length = 0;

    console.log('Accessibility Manager cleaned up');
  }
}

// Create and export singleton instance
const accessibilityManager = new AccessibilityManager();

// Export both class and instance
window.AccessibilityManager = AccessibilityManager;
window.accessibilityManager = accessibilityManager;

export { AccessibilityManager, accessibilityManager };
export default accessibilityManager;