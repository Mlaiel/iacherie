/**
 * @fileoverview UI Framework - Custom Desktop UI Framework
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/ui_framework
 * @description Professional UI framework optimized for desktop applications with component system
 */

class UIFramework {
  constructor() {
    this.components = new Map();
    this.templates = new Map();
    this.layouts = new Map();
    this.controllers = new Map();
    this.plugins = new Map();
    
    this.config = {
      enableVirtualDOM: true,
      enableHotReload: true,
      optimizeRendering: true,
      enableA11y: true,
      enableAnimations: true,
      enableTooltips: true,
      gridSystem: 12,
      breakpoints: {
        xs: 0,
        sm: 576,
        md: 768,
        lg: 992,
        xl: 1200,
        xxl: 1400
      }
    };

    this.renderQueue = [];
    this.isRendering = false;
    this.observers = new Map();

    this.initializeFramework();
    console.log('UI Framework initialized');
  }

  /**
   * Initialize the UI framework
   */
  initializeFramework() {
    this.setupVirtualDOM();
    this.setupComponentSystem();
    this.setupLayoutSystem();
    this.setupEventSystem();
    this.setupPluginSystem();
    this.loadCoreComponents();
  }

  /**
   * Setup Virtual DOM system
   */
  setupVirtualDOM() {
    if (!this.config.enableVirtualDOM) return;

    this.virtualDOM = {
      tree: null,
      pendingUpdates: new Set(),
      batchUpdateTimer: null
    };

    // Batch DOM updates for performance
    this.batchDOMUpdates = this.debounce(() => {
      this.processPendingUpdates();
    }, 16); // ~60fps
  }

  /**
   * Setup component system
   */
  setupComponentSystem() {
    // Base component class
    this.Component = class {
      constructor(props = {}, children = []) {
        this.props = props;
        this.children = children;
        this.state = {};
        this.refs = new Map();
        this.mounted = false;
        this.id = this.generateComponentId();
        this.eventListeners = new Map();
      }

      setState(newState) {
        this.state = { ...this.state, ...newState };
        this.forceUpdate();
      }

      render() {
        throw new Error('Component must implement render method');
      }

      componentDidMount() {}
      componentWillUnmount() {}
      componentDidUpdate() {}

      forceUpdate() {
        if (this.mounted) {
          uiFramework.scheduleUpdate(this);
        }
      }

      addEventListener(event, handler) {
        if (!this.eventListeners.has(event)) {
          this.eventListeners.set(event, new Set());
        }
        this.eventListeners.get(event).add(handler);
      }

      removeEventListener(event, handler) {
        const handlers = this.eventListeners.get(event);
        if (handlers) {
          handlers.delete(handler);
        }
      }

      destroy() {
        this.componentWillUnmount();
        this.eventListeners.clear();
        this.refs.clear();
        this.mounted = false;
      }
    };
  }

  /**
   * Setup layout system
   */
  setupLayoutSystem() {
    // Grid system
    this.Grid = class extends this.Component {
      render() {
        const { columns = 12, gap = '1rem', className = '' } = this.props;
        
        return this.createElement('div', {
          className: `ui-grid ${className}`,
          style: {
            display: 'grid',
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap
          }
        }, this.children);
      }
    };

    // Flexbox container
    this.Flex = class extends this.Component {
      render() {
        const { 
          direction = 'row', 
          justify = 'flex-start',
          align = 'stretch',
          wrap = 'nowrap',
          gap = '0',
          className = ''
        } = this.props;
        
        return this.createElement('div', {
          className: `ui-flex ${className}`,
          style: {
            display: 'flex',
            flexDirection: direction,
            justifyContent: justify,
            alignItems: align,
            flexWrap: wrap,
            gap
          }
        }, this.children);
      }
    };

    // Container
    this.Container = class extends this.Component {
      render() {
        const { fluid = false, className = '' } = this.props;
        
        return this.createElement('div', {
          className: `ui-container ${fluid ? 'fluid' : ''} ${className}`
        }, this.children);
      }
    };
  }

  /**
   * Setup event system
   */
  setupEventSystem() {
    this.eventManager = {
      delegates: new Map(),
      globalHandlers: new Map()
    };

    // Event delegation for performance
    document.addEventListener('click', this.handleDelegatedEvent.bind(this));
    document.addEventListener('change', this.handleDelegatedEvent.bind(this));
    document.addEventListener('input', this.handleDelegatedEvent.bind(this));
    document.addEventListener('focus', this.handleDelegatedEvent.bind(this));
    document.addEventListener('blur', this.handleDelegatedEvent.bind(this));
  }

  /**
   * Setup plugin system
   */
  setupPluginSystem() {
    this.pluginAPI = {
      registerComponent: this.registerComponent.bind(this),
      registerTemplate: this.registerTemplate.bind(this),
      registerLayout: this.registerLayout.bind(this),
      addEventListener: this.addEventListener.bind(this),
      createElement: this.createElement.bind(this)
    };
  }

  /**
   * Load core components
   */
  loadCoreComponents() {
    // Button component
    this.registerComponent('Button', class extends this.Component {
      render() {
        const { 
          variant = 'primary',
          size = 'medium',
          disabled = false,
          loading = false,
          onClick,
          className = '',
          type = 'button'
        } = this.props;

        return this.createElement('button', {
          type,
          className: `ui-button ui-button--${variant} ui-button--${size} ${disabled ? 'disabled' : ''} ${loading ? 'loading' : ''} ${className}`,
          disabled: disabled || loading,
          'data-component': 'button',
          'data-click': onClick ? 'handleClick' : null
        }, [
          loading && this.createElement('span', { className: 'ui-button__spinner' }),
          this.createElement('span', { className: 'ui-button__content' }, this.children)
        ].filter(Boolean));
      }
    });

    // Input component
    this.registerComponent('Input', class extends this.Component {
      render() {
        const {
          type = 'text',
          placeholder = '',
          value = '',
          disabled = false,
          required = false,
          onChange,
          onFocus,
          onBlur,
          className = '',
          label,
          error
        } = this.props;

        const inputElement = this.createElement('input', {
          type,
          placeholder,
          value,
          disabled,
          required,
          className: `ui-input ${error ? 'ui-input--error' : ''} ${className}`,
          'data-component': 'input',
          'data-change': onChange ? 'handleChange' : null,
          'data-focus': onFocus ? 'handleFocus' : null,
          'data-blur': onBlur ? 'handleBlur' : null
        });

        if (label || error) {
          return this.createElement('div', { className: 'ui-input-group' }, [
            label && this.createElement('label', { className: 'ui-input__label' }, label),
            inputElement,
            error && this.createElement('span', { className: 'ui-input__error' }, error)
          ].filter(Boolean));
        }

        return inputElement;
      }
    });

    // Modal component
    this.registerComponent('Modal', class extends this.Component {
      componentDidMount() {
        if (this.props.open) {
          this.showModal();
        }
      }

      componentDidUpdate() {
        if (this.props.open) {
          this.showModal();
        } else {
          this.hideModal();
        }
      }

      showModal() {
        document.body.classList.add('modal-open');
        if (window.eventDispatcher) {
          window.eventDispatcher.emit('ui.modal-opened', { id: this.id });
        }
      }

      hideModal() {
        document.body.classList.remove('modal-open');
        if (window.eventDispatcher) {
          window.eventDispatcher.emit('ui.modal-closed', { id: this.id });
        }
      }

      render() {
        const { 
          open = false,
          title,
          onClose,
          size = 'medium',
          className = ''
        } = this.props;

        if (!open) return null;

        return this.createElement('div', {
          className: `ui-modal ui-modal--${size} ${className}`,
          'data-component': 'modal'
        }, [
          this.createElement('div', { 
            className: 'ui-modal__backdrop',
            'data-click': onClose ? 'handleBackdropClick' : null
          }),
          this.createElement('div', { className: 'ui-modal__content' }, [
            this.createElement('div', { className: 'ui-modal__header' }, [
              title && this.createElement('h2', { className: 'ui-modal__title' }, title),
              onClose && this.createElement('button', {
                className: 'ui-modal__close',
                'data-click': 'handleClose'
              }, '×')
            ].filter(Boolean)),
            this.createElement('div', { className: 'ui-modal__body' }, this.children)
          ])
        ]);
      }
    });

    // Card component
    this.registerComponent('Card', class extends this.Component {
      render() {
        const {
          variant = 'default',
          padding = 'medium',
          shadow = true,
          className = '',
          header,
          footer
        } = this.props;

        return this.createElement('div', {
          className: `ui-card ui-card--${variant} ui-card--${padding} ${shadow ? 'ui-card--shadow' : ''} ${className}`,
          'data-component': 'card'
        }, [
          header && this.createElement('div', { className: 'ui-card__header' }, header),
          this.createElement('div', { className: 'ui-card__body' }, this.children),
          footer && this.createElement('div', { className: 'ui-card__footer' }, footer)
        ].filter(Boolean));
      }
    });

    // Tabs component
    this.registerComponent('Tabs', class extends this.Component {
      constructor(props, children) {
        super(props, children);
        this.state = {
          activeTab: props.defaultTab || 0
        };
      }

      handleTabClick(index) {
        this.setState({ activeTab: index });
        if (this.props.onChange) {
          this.props.onChange(index);
        }
      }

      render() {
        const { className = '', tabs = [] } = this.props;
        const { activeTab } = this.state;

        return this.createElement('div', {
          className: `ui-tabs ${className}`,
          'data-component': 'tabs'
        }, [
          this.createElement('div', { className: 'ui-tabs__nav' }, 
            tabs.map((tab, index) => 
              this.createElement('button', {
                className: `ui-tabs__tab ${index === activeTab ? 'active' : ''}`,
                'data-click': `handleTabClick:${index}`
              }, tab.label)
            )
          ),
          this.createElement('div', { className: 'ui-tabs__content' },
            this.children[activeTab]
          )
        ]);
      }
    });

    // Progress component
    this.registerComponent('Progress', class extends this.Component {
      render() {
        const {
          value = 0,
          max = 100,
          variant = 'primary',
          size = 'medium',
          showLabel = true,
          className = ''
        } = this.props;

        const percentage = Math.min((value / max) * 100, 100);

        return this.createElement('div', {
          className: `ui-progress ui-progress--${variant} ui-progress--${size} ${className}`,
          'data-component': 'progress'
        }, [
          showLabel && this.createElement('div', { className: 'ui-progress__label' }, `${Math.round(percentage)}%`),
          this.createElement('div', { className: 'ui-progress__track' }, [
            this.createElement('div', {
              className: 'ui-progress__fill',
              style: { width: `${percentage}%` }
            })
          ])
        ]);
      }
    });

    // Tooltip component
    this.registerComponent('Tooltip', class extends this.Component {
      componentDidMount() {
        if (this.config.enableTooltips) {
          this.setupTooltip();
        }
      }

      setupTooltip() {
        // Tooltip implementation would go here
      }

      render() {
        const { content, position = 'top', className = '' } = this.props;
        
        return this.createElement('div', {
          className: `ui-tooltip-trigger ${className}`,
          'data-tooltip': content,
          'data-tooltip-position': position,
          'data-component': 'tooltip'
        }, this.children);
      }
    });
  }

  /**
   * Register a component
   */
  registerComponent(name, ComponentClass) {
    if (this.components.has(name)) {
      console.warn(`Component '${name}' is being overridden`);
    }
    
    this.components.set(name, ComponentClass);
  }

  /**
   * Register a template
   */
  registerTemplate(name, template) {
    this.templates.set(name, template);
  }

  /**
   * Register a layout
   */
  registerLayout(name, layout) {
    this.layouts.set(name, layout);
  }

  /**
   * Create element (Virtual DOM)
   */
  createElement(tag, props = {}, children = []) {
    const element = {
      tag,
      props: { ...props },
      children: Array.isArray(children) ? children : [children],
      key: props.key || null,
      ref: props.ref || null
    };

    return element;
  }

  /**
   * Render virtual element to DOM
   */
  render(virtualElement, container) {
    if (typeof virtualElement === 'string' || typeof virtualElement === 'number') {
      return document.createTextNode(virtualElement);
    }

    if (!virtualElement || !virtualElement.tag) {
      return document.createTextNode('');
    }

    const element = document.createElement(virtualElement.tag);

    // Set attributes and properties
    Object.entries(virtualElement.props).forEach(([key, value]) => {
      if (key === 'className') {
        element.className = value;
      } else if (key === 'style' && typeof value === 'object') {
        Object.assign(element.style, value);
      } else if (key.startsWith('data-')) {
        element.setAttribute(key, value);
      } else if (key in element) {
        element[key] = value;
      } else {
        element.setAttribute(key, value);
      }
    });

    // Render children
    virtualElement.children.forEach(child => {
      if (child) {
        const childElement = this.render(child, element);
        if (childElement) {
          element.appendChild(childElement);
        }
      }
    });

    if (container) {
      container.appendChild(element);
    }

    return element;
  }

  /**
   * Create component instance
   */
  createComponent(name, props = {}, children = []) {
    const ComponentClass = this.components.get(name);
    
    if (!ComponentClass) {
      throw new Error(`Component '${name}' not found`);
    }

    const instance = new ComponentClass(props, children);
    instance.mounted = true;
    instance.componentDidMount();

    return instance;
  }

  /**
   * Mount component to DOM
   */
  mount(component, container) {
    if (typeof component === 'string') {
      // Component name
      const instance = this.createComponent(component);
      const virtualElement = instance.render();
      const domElement = this.render(virtualElement);
      container.appendChild(domElement);
      return instance;
    } else if (component instanceof this.Component) {
      // Component instance
      const virtualElement = component.render();
      const domElement = this.render(virtualElement);
      container.appendChild(domElement);
      return component;
    } else {
      // Virtual element
      const domElement = this.render(component);
      container.appendChild(domElement);
      return domElement;
    }
  }

  /**
   * Handle delegated events
   */
  handleDelegatedEvent(event) {
    let target = event.target;
    
    while (target && target !== document) {
      const component = target.getAttribute('data-component');
      const handler = target.getAttribute(`data-${event.type}`);
      
      if (component && handler) {
        this.executeEventHandler(handler, event, target);
        break;
      }
      
      target = target.parentElement;
    }
  }

  /**
   * Execute event handler
   */
  executeEventHandler(handler, event, element) {
    // Parse handler string (format: "methodName" or "methodName:param")
    const [methodName, param] = handler.split(':');
    
    // Find component instance
    const componentElement = element.closest('[data-component]');
    if (!componentElement) return;
    
    // Execute handler based on component type
    const componentType = componentElement.getAttribute('data-component');
    
    // This is a simplified implementation
    // In a full framework, you'd track component instances
    switch (methodName) {
      case 'handleClick':
        if (componentType === 'button') {
          event.preventDefault();
          // Emit button click event
          if (window.eventDispatcher) {
            window.eventDispatcher.emit('ui.button-clicked', { element, event });
          }
        }
        break;
      case 'handleChange':
        if (componentType === 'input') {
          // Emit input change event
          if (window.eventDispatcher) {
            window.eventDispatcher.emit('ui.input-changed', { 
              element, 
              value: element.value,
              event 
            });
          }
        }
        break;
      case 'handleTabClick':
        if (componentType === 'tabs' && param !== undefined) {
          const tabIndex = parseInt(param);
          // Emit tab change event
          if (window.eventDispatcher) {
            window.eventDispatcher.emit('ui.tab-changed', { 
              element, 
              tabIndex,
              event 
            });
          }
        }
        break;
    }
  }

  /**
   * Schedule component update
   */
  scheduleUpdate(component) {
    if (this.config.optimizeRendering) {
      this.virtualDOM.pendingUpdates.add(component);
      this.batchDOMUpdates();
    } else {
      this.updateComponent(component);
    }
  }

  /**
   * Process pending updates
   */
  processPendingUpdates() {
    if (this.virtualDOM.pendingUpdates.size === 0) return;

    this.isRendering = true;
    
    try {
      for (const component of this.virtualDOM.pendingUpdates) {
        this.updateComponent(component);
      }
    } finally {
      this.virtualDOM.pendingUpdates.clear();
      this.isRendering = false;
    }
  }

  /**
   * Update component
   */
  updateComponent(component) {
    try {
      const virtualElement = component.render();
      // In a full implementation, you'd diff and patch the DOM
      component.componentDidUpdate();
    } catch (error) {
      console.error('Component update failed:', error);
      if (window.errorHandler) {
        window.errorHandler.handleError({
          type: 'component_render_error',
          message: error.message,
          component: component.constructor.name,
          source: 'ui_framework'
        });
      }
    }
  }

  /**
   * Create responsive utilities
   */
  createResponsiveUtils() {
    return {
      getBreakpoint: () => {
        const width = window.innerWidth;
        for (const [name, minWidth] of Object.entries(this.config.breakpoints).reverse()) {
          if (width >= minWidth) return name;
        }
        return 'xs';
      },
      
      isBreakpoint: (breakpoint) => {
        return this.getBreakpoint() === breakpoint;
      },
      
      isAboveBreakpoint: (breakpoint) => {
        const current = this.getBreakpoint();
        const breakpoints = Object.keys(this.config.breakpoints);
        return breakpoints.indexOf(current) >= breakpoints.indexOf(breakpoint);
      }
    };
  }

  /**
   * Generate component ID
   */
  generateComponentId() {
    return `ui_component_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
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
   * Load plugin
   */
  loadPlugin(name, plugin) {
    if (typeof plugin.install === 'function') {
      plugin.install(this.pluginAPI);
      this.plugins.set(name, plugin);
      console.log(`Plugin '${name}' loaded`);
    } else {
      throw new Error(`Plugin '${name}' must have an install method`);
    }
  }

  /**
   * Get component
   */
  getComponent(name) {
    return this.components.get(name);
  }

  /**
   * Get template
   */
  getTemplate(name) {
    return this.templates.get(name);
  }

  /**
   * Get layout
   */
  getLayout(name) {
    return this.layouts.get(name);
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get framework statistics
   */
  getStatistics() {
    return {
      components: this.components.size,
      templates: this.templates.size,
      layouts: this.layouts.size,
      plugins: this.plugins.size,
      pendingUpdates: this.virtualDOM.pendingUpdates.size,
      isRendering: this.isRendering
    };
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.components.clear();
    this.templates.clear();
    this.layouts.clear();
    this.controllers.clear();
    this.plugins.clear();
    this.observers.clear();
    
    if (this.virtualDOM.batchUpdateTimer) {
      clearTimeout(this.virtualDOM.batchUpdateTimer);
    }
    
    console.log('UI Framework cleaned up');
  }
}

// Create and export singleton instance
const uiFramework = new UIFramework();

// Export both class and instance
window.UIFramework = UIFramework;
window.uiFramework = uiFramework;

export { UIFramework, uiFramework };
export default uiFramework;