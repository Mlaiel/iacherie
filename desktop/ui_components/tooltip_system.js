/**
 * Ainflue Desktop - Advanced Tooltip System
 * 
 * Professional tooltip management with animations, positioning, and themes
 * Supports rich content, interactive tooltips, and accessibility
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

class TooltipSystem {
  constructor(options = {}) {
    this.options = {
      defaultPosition: 'top',
      defaultTheme: 'professional',
      showDelay: 500,
      hideDelay: 100,
      animationDuration: 200,
      maxWidth: 300,
      offset: 10,
      arrow: true,
      interactive: false,
      allowHTML: false,
      followCursor: false,
      ...options
    };
    
    this.tooltips = new Map();
    this.activeTooltip = null;
    this.showTimer = null;
    this.hideTimer = null;
    this.isInitialized = false;
    
    this.initialize();
  }

  /**
   * Initialize the tooltip system
   */
  initialize() {
    if (this.isInitialized) return;
    
    this.createStyles();
    this.setupGlobalEventListeners();
    this.isInitialized = true;
  }

  /**
   * Create tooltip styles
   */
  createStyles() {
    if (document.getElementById('tooltip-system-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'tooltip-system-styles';
    styles.textContent = `
      .ainflue-tooltip {
        position: absolute;
        z-index: 10000;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        line-height: 1.4;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        pointer-events: none;
        opacity: 0;
        transform: scale(0.8);
        transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
        max-width: 300px;
        word-wrap: break-word;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      }
      
      .ainflue-tooltip.visible {
        opacity: 1;
        transform: scale(1);
      }
      
      .ainflue-tooltip.interactive {
        pointer-events: auto;
      }
      
      /* Themes */
      .ainflue-tooltip.professional {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }
      
      .ainflue-tooltip.dark {
        background: #2d3748;
        color: #e2e8f0;
        border: 1px solid #4a5568;
      }
      
      .ainflue-tooltip.light {
        background: #ffffff;
        color: #2d3748;
        border: 1px solid #e2e8f0;
      }
      
      .ainflue-tooltip.error {
        background: #fed7d7;
        color: #c53030;
        border: 1px solid #feb2b2;
      }
      
      .ainflue-tooltip.success {
        background: #c6f6d5;
        color: #22543d;
        border: 1px solid #9ae6b4;
      }
      
      .ainflue-tooltip.warning {
        background: #fefcbf;
        color: #744210;
        border: 1px solid #f6e05e;
      }
      
      .ainflue-tooltip.info {
        background: #bee3f8;
        color: #2a4365;
        border: 1px solid #90cdf4;
      }
      
      /* Arrow */
      .ainflue-tooltip::before {
        content: '';
        position: absolute;
        width: 0;
        height: 0;
        border-style: solid;
      }
      
      /* Top arrow */
      .ainflue-tooltip.position-top::before {
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border-width: 6px 6px 0 6px;
        border-color: currentColor transparent transparent transparent;
      }
      
      /* Bottom arrow */
      .ainflue-tooltip.position-bottom::before {
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        border-width: 0 6px 6px 6px;
        border-color: transparent transparent currentColor transparent;
      }
      
      /* Left arrow */
      .ainflue-tooltip.position-left::before {
        top: 50%;
        left: 100%;
        transform: translateY(-50%);
        border-width: 6px 0 6px 6px;
        border-color: transparent transparent transparent currentColor;
      }
      
      /* Right arrow */
      .ainflue-tooltip.position-right::before {
        top: 50%;
        right: 100%;
        transform: translateY(-50%);
        border-width: 6px 6px 6px 0;
        border-color: transparent currentColor transparent transparent;
      }
      
      .ainflue-tooltip.no-arrow::before {
        display: none;
      }
      
      /* Rich content */
      .tooltip-title {
        font-weight: 600;
        margin-bottom: 4px;
        font-size: 16px;
      }
      
      .tooltip-content {
        margin-bottom: 8px;
      }
      
      .tooltip-actions {
        display: flex;
        gap: 8px;
        margin-top: 8px;
      }
      
      .tooltip-button {
        padding: 4px 8px;
        border: none;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }
      
      .tooltip-button.primary {
        background: rgba(255, 255, 255, 0.2);
        color: inherit;
      }
      
      .tooltip-button.primary:hover {
        background: rgba(255, 255, 255, 0.3);
      }
      
      .tooltip-button.secondary {
        background: transparent;
        color: inherit;
        border: 1px solid rgba(255, 255, 255, 0.3);
      }
      
      .tooltip-button.secondary:hover {
        background: rgba(255, 255, 255, 0.1);
      }
      
      /* Loading state */
      .tooltip-loading {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .tooltip-spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top: 2px solid currentColor;
        border-radius: 50%;
        animation: tooltip-spin 1s linear infinite;
      }
      
      @keyframes tooltip-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      /* Responsive */
      @media (max-width: 768px) {
        .ainflue-tooltip {
          max-width: 250px;
          font-size: 13px;
          padding: 6px 10px;
        }
      }
    `;
    
    document.head.appendChild(styles);
  }

  /**
   * Setup global event listeners
   */
  setupGlobalEventListeners() {
    // Handle mouse events for automatic tooltips
    document.addEventListener('mouseenter', (e) => this.handleMouseEnter(e), true);
    document.addEventListener('mouseleave', (e) => this.handleMouseLeave(e), true);
    document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    
    // Handle focus events for accessibility
    document.addEventListener('focusin', (e) => this.handleFocusIn(e), true);
    document.addEventListener('focusout', (e) => this.handleFocusOut(e), true);
    
    // Handle scroll to update positions
    document.addEventListener('scroll', () => this.updateActiveTooltipPosition(), true);
    window.addEventListener('resize', () => this.updateActiveTooltipPosition());
    
    // Handle click outside interactive tooltips
    document.addEventListener('click', (e) => this.handleClickOutside(e));
  }

  /**
   * Add tooltip to an element
   */
  add(element, content, options = {}) {
    if (typeof element === 'string') {
      element = document.querySelector(element);
    }
    
    if (!element) {
      console.warn('Tooltip target element not found');
      return null;
    }
    
    const tooltipId = this.generateId();
    const config = {
      id: tooltipId,
      element,
      content,
      position: options.position || this.options.defaultPosition,
      theme: options.theme || this.options.defaultTheme,
      showDelay: options.showDelay !== undefined ? options.showDelay : this.options.showDelay,
      hideDelay: options.hideDelay !== undefined ? options.hideDelay : this.options.hideDelay,
      maxWidth: options.maxWidth || this.options.maxWidth,
      offset: options.offset !== undefined ? options.offset : this.options.offset,
      arrow: options.arrow !== undefined ? options.arrow : this.options.arrow,
      interactive: options.interactive || this.options.interactive,
      allowHTML: options.allowHTML || this.options.allowHTML,
      followCursor: options.followCursor || this.options.followCursor,
      trigger: options.trigger || 'hover',
      onShow: options.onShow || (() => {}),
      onHide: options.onHide || (() => {}),
      onUpdate: options.onUpdate || (() => {}),
      ...options
    };
    
    this.tooltips.set(tooltipId, config);
    element.setAttribute('data-tooltip-id', tooltipId);
    
    return tooltipId;
  }

  /**
   * Remove tooltip from an element
   */
  remove(elementOrId) {
    let tooltipId;
    
    if (typeof elementOrId === 'string') {
      if (this.tooltips.has(elementOrId)) {
        tooltipId = elementOrId;
      } else {
        const element = document.querySelector(elementOrId);
        tooltipId = element?.getAttribute('data-tooltip-id');
      }
    } else {
      tooltipId = elementOrId?.getAttribute('data-tooltip-id');
    }
    
    if (!tooltipId || !this.tooltips.has(tooltipId)) return false;
    
    this.hide(tooltipId);
    this.tooltips.delete(tooltipId);
    
    const config = this.tooltips.get(tooltipId);
    if (config?.element) {
      config.element.removeAttribute('data-tooltip-id');
    }
    
    return true;
  }

  /**
   * Show tooltip
   */
  show(elementOrId, options = {}) {
    let config;
    
    if (typeof elementOrId === 'string') {
      if (this.tooltips.has(elementOrId)) {
        config = this.tooltips.get(elementOrId);
      } else {
        const element = document.querySelector(elementOrId);
        const tooltipId = element?.getAttribute('data-tooltip-id');
        config = this.tooltips.get(tooltipId);
      }
    } else {
      const tooltipId = elementOrId?.getAttribute('data-tooltip-id');
      config = this.tooltips.get(tooltipId);
    }
    
    if (!config) return false;
    
    // Clear any existing timers
    this.clearTimers();
    
    // Hide active tooltip if different
    if (this.activeTooltip && this.activeTooltip.id !== config.id) {
      this.hide(this.activeTooltip.id);
    }
    
    // Create or update tooltip element
    const tooltipEl = this.createTooltipElement(config, options);
    
    // Position tooltip
    this.positionTooltip(tooltipEl, config);
    
    // Show with animation
    requestAnimationFrame(() => {
      tooltipEl.classList.add('visible');
    });
    
    this.activeTooltip = {
      id: config.id,
      element: tooltipEl,
      config
    };
    
    // Call onShow callback
    config.onShow(config.id, tooltipEl);
    
    return true;
  }

  /**
   * Hide tooltip
   */
  hide(tooltipId) {
    if (!tooltipId && this.activeTooltip) {
      tooltipId = this.activeTooltip.id;
    }
    
    if (!this.activeTooltip || this.activeTooltip.id !== tooltipId) return false;
    
    const { element: tooltipEl, config } = this.activeTooltip;
    
    // Hide with animation
    tooltipEl.classList.remove('visible');
    
    // Remove from DOM after animation
    setTimeout(() => {
      if (tooltipEl.parentNode) {
        tooltipEl.parentNode.removeChild(tooltipEl);
      }
    }, this.options.animationDuration);
    
    // Call onHide callback
    config.onHide(config.id, tooltipEl);
    
    this.activeTooltip = null;
    
    return true;
  }

  /**
   * Update tooltip content
   */
  update(elementOrId, content, options = {}) {
    let config;
    
    if (typeof elementOrId === 'string') {
      config = this.tooltips.get(elementOrId);
    } else {
      const tooltipId = elementOrId?.getAttribute('data-tooltip-id');
      config = this.tooltips.get(tooltipId);
    }
    
    if (!config) return false;
    
    // Update configuration
    config.content = content;
    Object.assign(config, options);
    
    // Update active tooltip if it's currently shown
    if (this.activeTooltip && this.activeTooltip.id === config.id) {
      const tooltipEl = this.activeTooltip.element;
      this.updateTooltipContent(tooltipEl, config);
      this.positionTooltip(tooltipEl, config);
      
      // Call onUpdate callback
      config.onUpdate(config.id, tooltipEl);
    }
    
    return true;
  }

  /**
   * Create tooltip element
   */
  createTooltipElement(config, options = {}) {
    const existing = document.getElementById(`tooltip-${config.id}`);
    if (existing) {
      this.updateTooltipContent(existing, config);
      return existing;
    }
    
    const tooltipEl = document.createElement('div');
    tooltipEl.id = `tooltip-${config.id}`;
    tooltipEl.className = this.buildTooltipClasses(config);
    tooltipEl.style.maxWidth = `${config.maxWidth}px`;
    
    this.updateTooltipContent(tooltipEl, config);
    
    // Add to DOM
    document.body.appendChild(tooltipEl);
    
    // Setup interactive events if needed
    if (config.interactive) {
      this.setupInteractiveEvents(tooltipEl, config);
    }
    
    return tooltipEl;
  }

  /**
   * Update tooltip content
   */
  updateTooltipContent(tooltipEl, config) {
    if (typeof config.content === 'string') {
      if (config.allowHTML) {
        tooltipEl.innerHTML = config.content;
      } else {
        tooltipEl.textContent = config.content;
      }
    } else if (typeof config.content === 'object') {
      // Rich content object
      tooltipEl.innerHTML = this.buildRichContent(config.content);
    } else if (typeof config.content === 'function') {
      // Dynamic content
      const result = config.content();
      if (typeof result === 'string') {
        tooltipEl.innerHTML = config.allowHTML ? result : result.replace(/</g, '&lt;');
      } else {
        tooltipEl.innerHTML = this.buildRichContent(result);
      }
    }
  }

  /**
   * Build rich content HTML
   */
  buildRichContent(content) {
    let html = '';
    
    if (content.title) {
      html += `<div class="tooltip-title">${this.escapeHTML(content.title)}</div>`;
    }
    
    if (content.text) {
      html += `<div class="tooltip-content">${this.escapeHTML(content.text)}</div>`;
    }
    
    if (content.loading) {
      html += `
        <div class="tooltip-loading">
          <div class="tooltip-spinner"></div>
          <span>${this.escapeHTML(content.loading)}</span>
        </div>
      `;
    }
    
    if (content.actions && content.actions.length > 0) {
      html += '<div class="tooltip-actions">';
      content.actions.forEach(action => {
        const type = action.type || 'primary';
        html += `
          <button class="tooltip-button ${type}" data-action="${action.id || ''}">
            ${this.escapeHTML(action.text)}
          </button>
        `;
      });
      html += '</div>';
    }
    
    return html;
  }

  /**
   * Build tooltip CSS classes
   */
  buildTooltipClasses(config) {
    const classes = ['ainflue-tooltip'];
    
    classes.push(config.theme);
    classes.push(`position-${config.position}`);
    
    if (!config.arrow) {
      classes.push('no-arrow');
    }
    
    if (config.interactive) {
      classes.push('interactive');
    }
    
    return classes.join(' ');
  }

  /**
   * Position tooltip relative to target element
   */
  positionTooltip(tooltipEl, config) {
    const targetRect = config.element.getBoundingClientRect();
    const tooltipRect = tooltipEl.getBoundingClientRect();
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight
    };
    
    let position = config.position;
    let top, left;
    
    // Calculate initial position
    switch (position) {
      case 'top':
        top = targetRect.top - tooltipRect.height - config.offset;
        left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = targetRect.bottom + config.offset;
        left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
        left = targetRect.left - tooltipRect.width - config.offset;
        break;
      case 'right':
        top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
        left = targetRect.right + config.offset;
        break;
    }
    
    // Auto-flip if tooltip goes outside viewport
    if (top < 0 && (position === 'top' || position === 'left' || position === 'right')) {
      if (position === 'top') {
        position = 'bottom';
        top = targetRect.bottom + config.offset;
      } else {
        top = Math.max(config.offset, top);
      }
    }
    
    if (top + tooltipRect.height > viewport.height && position === 'bottom') {
      position = 'top';
      top = targetRect.top - tooltipRect.height - config.offset;
    }
    
    if (left < 0 && (position === 'left' || position === 'top' || position === 'bottom')) {
      if (position === 'left') {
        position = 'right';
        left = targetRect.right + config.offset;
      } else {
        left = Math.max(config.offset, left);
      }
    }
    
    if (left + tooltipRect.width > viewport.width && position === 'right') {
      position = 'left';
      left = targetRect.left - tooltipRect.width - config.offset;
    }
    
    // Final position adjustments
    left = Math.max(config.offset, Math.min(left, viewport.width - tooltipRect.width - config.offset));
    top = Math.max(config.offset, Math.min(top, viewport.height - tooltipRect.height - config.offset));
    
    // Apply position
    tooltipEl.style.left = `${left + window.scrollX}px`;
    tooltipEl.style.top = `${top + window.scrollY}px`;
    
    // Update position class if changed
    tooltipEl.className = this.buildTooltipClasses({ ...config, position });
  }

  /**
   * Setup interactive tooltip events
   */
  setupInteractiveEvents(tooltipEl, config) {
    // Handle action buttons
    tooltipEl.addEventListener('click', (e) => {
      if (e.target.classList.contains('tooltip-button')) {
        const actionId = e.target.getAttribute('data-action');
        if (config.onAction) {
          config.onAction(actionId, e.target, config.id);
        }
      }
    });
    
    // Prevent hiding when mouse is over tooltip
    tooltipEl.addEventListener('mouseenter', () => {
      this.clearTimers();
    });
    
    tooltipEl.addEventListener('mouseleave', () => {
      this.scheduleHide(config);
    });
  }

  /**
   * Handle mouse enter events
   */
  handleMouseEnter(e) {
    const tooltipId = e.target.getAttribute('data-tooltip-id');
    if (!tooltipId) return;
    
    const config = this.tooltips.get(tooltipId);
    if (!config || config.trigger !== 'hover') return;
    
    this.clearTimers();
    
    if (config.showDelay > 0) {
      this.showTimer = setTimeout(() => {
        this.show(tooltipId);
      }, config.showDelay);
    } else {
      this.show(tooltipId);
    }
  }

  /**
   * Handle mouse leave events
   */
  handleMouseLeave(e) {
    const tooltipId = e.target.getAttribute('data-tooltip-id');
    if (!tooltipId) return;
    
    const config = this.tooltips.get(tooltipId);
    if (!config || config.trigger !== 'hover') return;
    
    this.clearTimers();
    this.scheduleHide(config);
  }

  /**
   * Handle mouse move for cursor following
   */
  handleMouseMove(e) {
    if (!this.activeTooltip || !this.activeTooltip.config.followCursor) return;
    
    const tooltipEl = this.activeTooltip.element;
    const offset = this.activeTooltip.config.offset;
    
    tooltipEl.style.left = `${e.pageX + offset}px`;
    tooltipEl.style.top = `${e.pageY + offset}px`;
  }

  /**
   * Handle focus events for accessibility
   */
  handleFocusIn(e) {
    const tooltipId = e.target.getAttribute('data-tooltip-id');
    if (!tooltipId) return;
    
    const config = this.tooltips.get(tooltipId);
    if (!config || (config.trigger !== 'focus' && config.trigger !== 'hover')) return;
    
    this.show(tooltipId);
  }

  /**
   * Handle focus out events
   */
  handleFocusOut(e) {
    const tooltipId = e.target.getAttribute('data-tooltip-id');
    if (!tooltipId) return;
    
    const config = this.tooltips.get(tooltipId);
    if (!config || (config.trigger !== 'focus' && config.trigger !== 'hover')) return;
    
    this.scheduleHide(config);
  }

  /**
   * Handle click outside interactive tooltips
   */
  handleClickOutside(e) {
    if (!this.activeTooltip || !this.activeTooltip.config.interactive) return;
    
    const tooltipEl = this.activeTooltip.element;
    const targetEl = this.activeTooltip.config.element;
    
    if (!tooltipEl.contains(e.target) && !targetEl.contains(e.target)) {
      this.hide();
    }
  }

  /**
   * Update active tooltip position
   */
  updateActiveTooltipPosition() {
    if (!this.activeTooltip) return;
    
    const { element: tooltipEl, config } = this.activeTooltip;
    this.positionTooltip(tooltipEl, config);
  }

  /**
   * Schedule tooltip hide with delay
   */
  scheduleHide(config) {
    if (config.hideDelay > 0) {
      this.hideTimer = setTimeout(() => {
        this.hide();
      }, config.hideDelay);
    } else {
      this.hide();
    }
  }

  /**
   * Clear show/hide timers
   */
  clearTimers() {
    if (this.showTimer) {
      clearTimeout(this.showTimer);
      this.showTimer = null;
    }
    
    if (this.hideTimer) {
      clearTimeout(this.hideTimer);
      this.hideTimer = null;
    }
  }

  /**
   * Generate unique ID
   */
  generateId() {
    return `tooltip_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Escape HTML to prevent XSS
   */
  escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Hide all tooltips
   */
  hideAll() {
    if (this.activeTooltip) {
      this.hide();
    }
    this.clearTimers();
  }

  /**
   * Get all active tooltips
   */
  getAll() {
    return Array.from(this.tooltips.values());
  }

  /**
   * Destroy tooltip system
   */
  destroy() {
    this.hideAll();
    this.tooltips.clear();
    
    // Remove event listeners
    document.removeEventListener('mouseenter', this.handleMouseEnter, true);
    document.removeEventListener('mouseleave', this.handleMouseLeave, true);
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('focusin', this.handleFocusIn, true);
    document.removeEventListener('focusout', this.handleFocusOut, true);
    document.removeEventListener('scroll', this.updateActiveTooltipPosition, true);
    window.removeEventListener('resize', this.updateActiveTooltipPosition);
    document.removeEventListener('click', this.handleClickOutside);
    
    // Remove styles if no other instances exist
    if (!document.querySelector('[data-tooltip-id]')) {
      const styles = document.getElementById('tooltip-system-styles');
      if (styles) {
        styles.remove();
      }
    }
    
    this.isInitialized = false;
  }

  /**
   * Create a simple tooltip (static method)
   */
  static create(element, content, options = {}) {
    const system = new TooltipSystem();
    return system.add(element, content, options);
  }

  /**
   * Show a temporary tooltip at specific coordinates
   */
  static showAt(x, y, content, options = {}) {
    const system = new TooltipSystem();
    const tempEl = document.createElement('div');
    tempEl.style.position = 'absolute';
    tempEl.style.left = `${x}px`;
    tempEl.style.top = `${y}px`;
    tempEl.style.width = '1px';
    tempEl.style.height = '1px';
    tempEl.style.pointerEvents = 'none';
    tempEl.style.opacity = '0';
    
    document.body.appendChild(tempEl);
    
    const tooltipId = system.add(tempEl, content, {
      position: 'bottom',
      showDelay: 0,
      ...options
    });
    
    system.show(tooltipId);
    
    // Auto cleanup
    setTimeout(() => {
      system.remove(tooltipId);
      if (tempEl.parentNode) {
        tempEl.parentNode.removeChild(tempEl);
      }
    }, options.autoHide || 3000);
    
    return tooltipId;
  }
}

// Global tooltip system instance
let globalTooltipSystem = null;

/**
 * Get or create global tooltip system
 */
function getGlobalTooltipSystem() {
  if (!globalTooltipSystem) {
    globalTooltipSystem = new TooltipSystem();
  }
  return globalTooltipSystem;
}

// Convenience functions for common use cases
const Tooltip = {
  add: (element, content, options) => getGlobalTooltipSystem().add(element, content, options),
  remove: (elementOrId) => getGlobalTooltipSystem().remove(elementOrId),
  show: (elementOrId, options) => getGlobalTooltipSystem().show(elementOrId, options),
  hide: (tooltipId) => getGlobalTooltipSystem().hide(tooltipId),
  update: (elementOrId, content, options) => getGlobalTooltipSystem().update(elementOrId, content, options),
  hideAll: () => getGlobalTooltipSystem().hideAll(),
  create: TooltipSystem.create,
  showAt: TooltipSystem.showAt
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { TooltipSystem, Tooltip };
} else if (typeof window !== 'undefined') {
  window.TooltipSystem = TooltipSystem;
  window.Tooltip = Tooltip;
}

/**
 * Usage Examples:
 * 
 * // Simple tooltip
 * Tooltip.add('#my-button', 'This is a helpful tooltip');
 * 
 * // Rich tooltip with actions
 * Tooltip.add('#my-element', {
 *   title: 'Confirmation',
 *   text: 'Are you sure you want to delete this item?',
 *   actions: [
 *     { id: 'confirm', text: 'Delete', type: 'primary' },
 *     { id: 'cancel', text: 'Cancel', type: 'secondary' }
 *   ]
 * }, {
 *   theme: 'error',
 *   interactive: true,
 *   onAction: (actionId) => {
 *     if (actionId === 'confirm') {
 *       // Delete item
 *     }
 *     Tooltip.hide();
 *   }
 * });
 * 
 * // Dynamic content tooltip
 * Tooltip.add('#status', () => {
 *   return `Current time: ${new Date().toLocaleTimeString()}`;
 * }, {
 *   position: 'bottom',
 *   theme: 'info'
 * });
 * 
 * // Temporary tooltip at coordinates
 * Tooltip.showAt(100, 200, 'Success!', {
 *   theme: 'success',
 *   autoHide: 2000
 * });
 */