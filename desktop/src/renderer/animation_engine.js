/**
 * @fileoverview Animation Engine - Professional Animation System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/animation_engine
 * @description Advanced animation system with performance optimization and easing functions
 */

class AnimationEngine {
  constructor() {
    this.animations = new Map();
    this.sequences = new Map();
    this.easingFunctions = new Map();
    this.runningAnimations = new Set();
    this.animationId = 0;
    
    this.config = {
      enableAnimations: true,
      respectReducedMotion: true,
      defaultDuration: 300,
      defaultEasing: 'easeOutCubic',
      enableGPUAcceleration: true,
      useRAF: true,
      enableDebug: false
    };

    this.performance = {
      totalAnimations: 0,
      activeAnimations: 0,
      droppedFrames: 0,
      averageFPS: 60
    };

    this.initializeAnimationEngine();
    console.log('Animation Engine initialized');
  }

  /**
   * Initialize animation engine
   */
  initializeAnimationEngine() {
    this.setupEasingFunctions();
    this.setupPerformanceMonitoring();
    this.setupReducedMotionHandling();
    this.setupAnimationObserver();
    this.injectAnimationCSS();
  }

  /**
   * Setup easing functions
   */
  setupEasingFunctions() {
    // Linear easing
    this.registerEasing('linear', t => t);

    // Quadratic easing
    this.registerEasing('easeInQuad', t => t * t);
    this.registerEasing('easeOutQuad', t => t * (2 - t));
    this.registerEasing('easeInOutQuad', t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);

    // Cubic easing
    this.registerEasing('easeInCubic', t => t * t * t);
    this.registerEasing('easeOutCubic', t => (--t) * t * t + 1);
    this.registerEasing('easeInOutCubic', t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1);

    // Quartic easing
    this.registerEasing('easeInQuart', t => t * t * t * t);
    this.registerEasing('easeOutQuart', t => 1 - (--t) * t * t * t);
    this.registerEasing('easeInOutQuart', t => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t);

    // Quintic easing
    this.registerEasing('easeInQuint', t => t * t * t * t * t);
    this.registerEasing('easeOutQuint', t => 1 + (--t) * t * t * t * t);
    this.registerEasing('easeInOutQuint', t => t < 0.5 ? 16 * t * t * t * t * t : 1 + 16 * (--t) * t * t * t * t);

    // Sine easing
    this.registerEasing('easeInSine', t => 1 - Math.cos(t * Math.PI / 2));
    this.registerEasing('easeOutSine', t => Math.sin(t * Math.PI / 2));
    this.registerEasing('easeInOutSine', t => -(Math.cos(Math.PI * t) - 1) / 2);

    // Exponential easing
    this.registerEasing('easeInExpo', t => t === 0 ? 0 : Math.pow(2, 10 * (t - 1)));
    this.registerEasing('easeOutExpo', t => t === 1 ? 1 : 1 - Math.pow(2, -10 * t));
    this.registerEasing('easeInOutExpo', t => {
      if (t === 0) return 0;
      if (t === 1) return 1;
      if (t < 0.5) return Math.pow(2, 20 * t - 10) / 2;
      return (2 - Math.pow(2, -20 * t + 10)) / 2;
    });

    // Circular easing
    this.registerEasing('easeInCirc', t => 1 - Math.sqrt(1 - t * t));
    this.registerEasing('easeOutCirc', t => Math.sqrt(1 - (--t) * t));
    this.registerEasing('easeInOutCirc', t => t < 0.5 ? (1 - Math.sqrt(1 - 4 * t * t)) / 2 : (Math.sqrt(1 - (-2 * t + 2) * (-2 * t + 2)) + 1) / 2);

    // Back easing
    this.registerEasing('easeInBack', t => {
      const c1 = 1.70158;
      const c3 = c1 + 1;
      return c3 * t * t * t - c1 * t * t;
    });
    this.registerEasing('easeOutBack', t => {
      const c1 = 1.70158;
      const c3 = c1 + 1;
      return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
    });

    // Elastic easing
    this.registerEasing('easeInElastic', t => {
      const c4 = (2 * Math.PI) / 3;
      return t === 0 ? 0 : t === 1 ? 1 : -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
    });
    this.registerEasing('easeOutElastic', t => {
      const c4 = (2 * Math.PI) / 3;
      return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
    });

    // Bounce easing
    this.registerEasing('easeOutBounce', t => {
      const n1 = 7.5625;
      const d1 = 2.75;
      if (t < 1 / d1) {
        return n1 * t * t;
      } else if (t < 2 / d1) {
        return n1 * (t -= 1.5 / d1) * t + 0.75;
      } else if (t < 2.5 / d1) {
        return n1 * (t -= 2.25 / d1) * t + 0.9375;
      } else {
        return n1 * (t -= 2.625 / d1) * t + 0.984375;
      }
    });
  }

  /**
   * Setup performance monitoring
   */
  setupPerformanceMonitoring() {
    if (!this.config.enableDebug) return;

    let lastTime = performance.now();
    let frameCount = 0;
    let fpsBuffer = [];

    const monitor = (currentTime) => {
      frameCount++;
      const deltaTime = currentTime - lastTime;

      if (deltaTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / deltaTime);
        fpsBuffer.push(fps);

        if (fpsBuffer.length > 10) {
          fpsBuffer.shift();
        }

        this.performance.averageFPS = fpsBuffer.reduce((a, b) => a + b, 0) / fpsBuffer.length;
        this.performance.activeAnimations = this.runningAnimations.size;

        frameCount = 0;
        lastTime = currentTime;
      }

      if (this.runningAnimations.size > 0) {
        requestAnimationFrame(monitor);
      }
    };

    this.performanceMonitor = monitor;
  }

  /**
   * Setup reduced motion handling
   */
  setupReducedMotionHandling() {
    if (!this.config.respectReducedMotion) return;

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleReducedMotion = (e) => {
      if (e.matches) {
        this.config.enableAnimations = false;
        this.stopAllAnimations();
      } else {
        this.config.enableAnimations = true;
      }
    };

    mediaQuery.addListener(handleReducedMotion);
    handleReducedMotion(mediaQuery);
  }

  /**
   * Setup animation observer
   */
  setupAnimationObserver() {
    // Observe CSS animations and transitions
    document.addEventListener('animationstart', this.handleCSSAnimationStart.bind(this));
    document.addEventListener('animationend', this.handleCSSAnimationEnd.bind(this));
    document.addEventListener('transitionstart', this.handleCSSTransitionStart.bind(this));
    document.addEventListener('transitionend', this.handleCSSTransitionEnd.bind(this));
  }

  /**
   * Inject animation CSS utilities
   */
  injectAnimationCSS() {
    const style = document.createElement('style');
    style.id = 'ainflue-animation-utilities';
    
    style.textContent = `
      /* Animation utilities */
      .animate-none { animation: none !important; }
      .animate-spin { animation: spin 1s linear infinite; }
      .animate-ping { animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite; }
      .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
      .animate-bounce { animation: bounce 1s infinite; }
      .animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
      .animate-fade-out { animation: fadeOut 0.3s ease-out forwards; }
      .animate-slide-in-left { animation: slideInLeft 0.3s ease-out forwards; }
      .animate-slide-in-right { animation: slideInRight 0.3s ease-out forwards; }
      .animate-slide-in-up { animation: slideInUp 0.3s ease-out forwards; }
      .animate-slide-in-down { animation: slideInDown 0.3s ease-out forwards; }
      
      /* Transition utilities */
      .transition-none { transition: none !important; }
      .transition-all { transition: all 0.15s ease-in-out; }
      .transition-colors { transition: color, background-color, border-color 0.15s ease-in-out; }
      .transition-opacity { transition: opacity 0.15s ease-in-out; }
      .transition-transform { transition: transform 0.15s ease-in-out; }
      
      /* Duration utilities */
      .duration-75 { transition-duration: 75ms; }
      .duration-100 { transition-duration: 100ms; }
      .duration-150 { transition-duration: 150ms; }
      .duration-200 { transition-duration: 200ms; }
      .duration-300 { transition-duration: 300ms; }
      .duration-500 { transition-duration: 500ms; }
      .duration-700 { transition-duration: 700ms; }
      .duration-1000 { transition-duration: 1000ms; }
      
      /* Easing utilities */
      .ease-linear { transition-timing-function: linear; }
      .ease-in { transition-timing-function: cubic-bezier(0.4, 0, 1, 1); }
      .ease-out { transition-timing-function: cubic-bezier(0, 0, 0.2, 1); }
      .ease-in-out { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }
      
      /* Transform utilities */
      .transform { transform: translateZ(0); }
      .transform-gpu { transform: translate3d(0, 0, 0); }
      
      /* Animation delays */
      .delay-75 { animation-delay: 75ms; }
      .delay-100 { animation-delay: 100ms; }
      .delay-150 { animation-delay: 150ms; }
      .delay-200 { animation-delay: 200ms; }
      .delay-300 { animation-delay: 300ms; }
      .delay-500 { animation-delay: 500ms; }
      .delay-700 { animation-delay: 700ms; }
      .delay-1000 { animation-delay: 1000ms; }
      
      /* Reduced motion */
      @media (prefers-reduced-motion: reduce) {
        .animate-spin,
        .animate-ping,
        .animate-pulse,
        .animate-bounce {
          animation: none;
        }
        
        .transition-all,
        .transition-colors,
        .transition-opacity,
        .transition-transform {
          transition: none;
        }
      }
    `;
    
    document.head.appendChild(style);
  }

  /**
   * Register easing function
   */
  registerEasing(name, easingFunction) {
    if (typeof easingFunction !== 'function') {
      throw new Error('Easing function must be a function');
    }
    
    this.easingFunctions.set(name, easingFunction);
  }

  /**
   * Create animation
   */
  animate(element, properties, options = {}) {
    if (!this.config.enableAnimations) {
      // Apply final state immediately
      this.applyStyles(element, properties);
      return Promise.resolve();
    }

    const animationId = this.generateAnimationId();
    const config = this.normalizeAnimationConfig(options);
    
    const animation = {
      id: animationId,
      element,
      properties,
      config,
      startTime: null,
      currentTime: 0,
      isRunning: false,
      isPaused: false,
      isCompleted: false,
      initialValues: {},
      resolve: null,
      reject: null
    };

    // Store initial values
    animation.initialValues = this.getInitialValues(element, properties);

    // Create promise
    const promise = new Promise((resolve, reject) => {
      animation.resolve = resolve;
      animation.reject = reject;
    });

    this.animations.set(animationId, animation);
    this.startAnimation(animation);

    return promise;
  }

  /**
   * Create animation sequence
   */
  sequence(animations) {
    const sequenceId = this.generateAnimationId();
    let currentIndex = 0;

    const runNext = () => {
      if (currentIndex >= animations.length) {
        this.sequences.delete(sequenceId);
        return Promise.resolve();
      }

      const { element, properties, options } = animations[currentIndex];
      currentIndex++;

      return this.animate(element, properties, options).then(runNext);
    };

    const promise = runNext();
    this.sequences.set(sequenceId, { animations, promise });

    return promise;
  }

  /**
   * Create parallel animations
   */
  parallel(animations) {
    const promises = animations.map(({ element, properties, options }) => 
      this.animate(element, properties, options)
    );

    return Promise.all(promises);
  }

  /**
   * Start animation
   */
  startAnimation(animation) {
    if (animation.isRunning) return;

    animation.isRunning = true;
    animation.startTime = performance.now();
    this.runningAnimations.add(animation);

    // Start performance monitoring if first animation
    if (this.runningAnimations.size === 1 && this.performanceMonitor) {
      requestAnimationFrame(this.performanceMonitor);
    }

    this.runAnimationFrame(animation);
  }

  /**
   * Run animation frame
   */
  runAnimationFrame(animation) {
    if (!animation.isRunning || animation.isPaused) return;

    const currentTime = performance.now();
    const elapsed = currentTime - animation.startTime;
    const progress = Math.min(elapsed / animation.config.duration, 1);

    // Apply easing
    const easedProgress = this.applyEasing(progress, animation.config.easing);

    // Update element properties
    this.updateElementProperties(animation, easedProgress);

    // Call progress callback
    if (animation.config.onProgress) {
      animation.config.onProgress(easedProgress, animation);
    }

    // Check if animation is complete
    if (progress >= 1) {
      this.completeAnimation(animation);
    } else {
      // Schedule next frame
      if (this.config.useRAF) {
        requestAnimationFrame(() => this.runAnimationFrame(animation));
      } else {
        setTimeout(() => this.runAnimationFrame(animation), 16); // ~60fps
      }
    }
  }

  /**
   * Update element properties
   */
  updateElementProperties(animation, progress) {
    const { element, properties, initialValues } = animation;

    Object.entries(properties).forEach(([property, targetValue]) => {
      const initialValue = initialValues[property];
      const currentValue = this.interpolateValue(initialValue, targetValue, progress);
      
      this.setElementProperty(element, property, currentValue);
    });
  }

  /**
   * Interpolate between values
   */
  interpolateValue(from, to, progress) {
    // Handle different value types
    if (typeof from === 'number' && typeof to === 'number') {
      return from + (to - from) * progress;
    }

    if (typeof from === 'string' && typeof to === 'string') {
      // Handle color interpolation
      if (this.isColor(from) && this.isColor(to)) {
        return this.interpolateColor(from, to, progress);
      }

      // Handle unit values (px, %, em, etc.)
      const fromMatch = from.match(/^(-?\d*\.?\d+)(.*)$/);
      const toMatch = to.match(/^(-?\d*\.?\d+)(.*)$/);

      if (fromMatch && toMatch && fromMatch[2] === toMatch[2]) {
        const fromNum = parseFloat(fromMatch[1]);
        const toNum = parseFloat(toMatch[1]);
        const unit = fromMatch[2];
        return (fromNum + (toNum - fromNum) * progress) + unit;
      }
    }

    // Fallback to discrete transition at 50%
    return progress < 0.5 ? from : to;
  }

  /**
   * Interpolate colors
   */
  interpolateColor(from, to, progress) {
    const fromRgb = this.parseColor(from);
    const toRgb = this.parseColor(to);

    if (!fromRgb || !toRgb) return progress < 0.5 ? from : to;

    const r = Math.round(fromRgb.r + (toRgb.r - fromRgb.r) * progress);
    const g = Math.round(fromRgb.g + (toRgb.g - fromRgb.g) * progress);
    const b = Math.round(fromRgb.b + (toRgb.b - fromRgb.b) * progress);
    const a = fromRgb.a + (toRgb.a - fromRgb.a) * progress;

    return `rgba(${r}, ${g}, ${b}, ${a})`;
  }

  /**
   * Parse color string to RGB object
   */
  parseColor(color) {
    // Create temporary element to get computed color
    const div = document.createElement('div');
    div.style.color = color;
    document.body.appendChild(div);
    
    const computedColor = getComputedStyle(div).color;
    document.body.removeChild(div);

    const match = computedColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    
    if (match) {
      return {
        r: parseInt(match[1]),
        g: parseInt(match[2]),
        b: parseInt(match[3]),
        a: match[4] ? parseFloat(match[4]) : 1
      };
    }

    return null;
  }

  /**
   * Check if string is a color
   */
  isColor(value) {
    return /^(#|rgb|hsl|hwb|lab|lch|color\()/i.test(value) || 
           CSS.supports('color', value);
  }

  /**
   * Set element property
   */
  setElementProperty(element, property, value) {
    if (property.startsWith('--')) {
      // CSS custom property
      element.style.setProperty(property, value);
    } else if (property in element.style) {
      // CSS style property
      element.style[property] = value;
    } else if (property === 'scrollTop' || property === 'scrollLeft') {
      // Scroll properties
      element[property] = value;
    } else {
      // Attribute
      element.setAttribute(property, value);
    }
  }

  /**
   * Get initial values
   */
  getInitialValues(element, properties) {
    const initialValues = {};

    Object.keys(properties).forEach(property => {
      if (property.startsWith('--')) {
        // CSS custom property
        initialValues[property] = getComputedStyle(element).getPropertyValue(property) || '0';
      } else if (property in element.style) {
        // CSS style property
        const computedStyle = getComputedStyle(element);
        initialValues[property] = computedStyle[property] || element.style[property] || this.getDefaultValue(property);
      } else if (property === 'scrollTop' || property === 'scrollLeft') {
        // Scroll properties
        initialValues[property] = element[property];
      } else {
        // Attribute
        initialValues[property] = element.getAttribute(property) || '0';
      }
    });

    return initialValues;
  }

  /**
   * Get default value for CSS property
   */
  getDefaultValue(property) {
    const defaults = {
      opacity: '1',
      translateX: '0px',
      translateY: '0px',
      translateZ: '0px',
      scaleX: '1',
      scaleY: '1',
      scaleZ: '1',
      rotateX: '0deg',
      rotateY: '0deg',
      rotateZ: '0deg',
      skewX: '0deg',
      skewY: '0deg'
    };

    return defaults[property] || '0';
  }

  /**
   * Apply easing function
   */
  applyEasing(progress, easingName) {
    const easingFunction = this.easingFunctions.get(easingName);
    
    if (!easingFunction) {
      console.warn(`Easing function '${easingName}' not found, using linear`);
      return progress;
    }

    return easingFunction(progress);
  }

  /**
   * Complete animation
   */
  completeAnimation(animation) {
    animation.isRunning = false;
    animation.isCompleted = true;
    this.runningAnimations.delete(animation);

    // Ensure final values are applied
    this.updateElementProperties(animation, 1);

    // Call completion callback
    if (animation.config.onComplete) {
      animation.config.onComplete(animation);
    }

    // Resolve promise
    if (animation.resolve) {
      animation.resolve(animation);
    }

    // Clean up
    this.animations.delete(animation.id);
    this.performance.totalAnimations++;
  }

  /**
   * Pause animation
   */
  pauseAnimation(animationId) {
    const animation = this.animations.get(animationId);
    if (animation && animation.isRunning) {
      animation.isPaused = true;
    }
  }

  /**
   * Resume animation
   */
  resumeAnimation(animationId) {
    const animation = this.animations.get(animationId);
    if (animation && animation.isPaused) {
      animation.isPaused = false;
      animation.startTime = performance.now() - animation.currentTime;
      this.runAnimationFrame(animation);
    }
  }

  /**
   * Stop animation
   */
  stopAnimation(animationId) {
    const animation = this.animations.get(animationId);
    if (animation) {
      animation.isRunning = false;
      this.runningAnimations.delete(animation);
      
      if (animation.reject) {
        animation.reject(new Error('Animation stopped'));
      }
      
      this.animations.delete(animationId);
    }
  }

  /**
   * Stop all animations
   */
  stopAllAnimations() {
    this.runningAnimations.forEach(animation => {
      this.stopAnimation(animation.id);
    });
  }

  /**
   * Normalize animation configuration
   */
  normalizeAnimationConfig(options) {
    return {
      duration: options.duration || this.config.defaultDuration,
      easing: options.easing || this.config.defaultEasing,
      delay: options.delay || 0,
      onProgress: options.onProgress,
      onComplete: options.onComplete
    };
  }

  /**
   * Generate unique animation ID
   */
  generateAnimationId() {
    return `animation_${++this.animationId}_${Date.now()}`;
  }

  /**
   * Apply styles immediately
   */
  applyStyles(element, styles) {
    Object.entries(styles).forEach(([property, value]) => {
      this.setElementProperty(element, property, value);
    });
  }

  /**
   * Handle CSS animation events
   */
  handleCSSAnimationStart(event) {
    if (this.config.enableDebug) {
      console.log('CSS Animation started:', event.animationName);
    }
  }

  handleCSSAnimationEnd(event) {
    if (this.config.enableDebug) {
      console.log('CSS Animation ended:', event.animationName);
    }
  }

  handleCSSTransitionStart(event) {
    if (this.config.enableDebug) {
      console.log('CSS Transition started:', event.propertyName);
    }
  }

  handleCSSTransitionEnd(event) {
    if (this.config.enableDebug) {
      console.log('CSS Transition ended:', event.propertyName);
    }
  }

  /**
   * Create stagger animation
   */
  stagger(elements, properties, options = {}) {
    const staggerDelay = options.staggerDelay || 100;
    const baseDelay = options.delay || 0;

    const promises = Array.from(elements).map((element, index) => {
      const delay = baseDelay + (index * staggerDelay);
      return this.animate(element, properties, { ...options, delay });
    });

    return Promise.all(promises);
  }

  /**
   * Create spring animation
   */
  spring(element, properties, options = {}) {
    const config = {
      tension: options.tension || 170,
      friction: options.friction || 26,
      mass: options.mass || 1,
      ...options
    };

    // Spring physics simulation would be implemented here
    // For now, use elastic easing as approximation
    return this.animate(element, properties, {
      ...config,
      easing: 'easeOutElastic',
      duration: config.duration || 800
    });
  }

  /**
   * Get animation performance metrics
   */
  getPerformanceMetrics() {
    return {
      ...this.performance,
      runningAnimations: this.runningAnimations.size,
      totalRegisteredEasings: this.easingFunctions.size
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    if (!newConfig.enableAnimations) {
      this.stopAllAnimations();
    }
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.stopAllAnimations();
    this.animations.clear();
    this.sequences.clear();
    this.runningAnimations.clear();
    
    // Remove style element
    const styleElement = document.getElementById('ainflue-animation-utilities');
    if (styleElement) {
      styleElement.remove();
    }
    
    console.log('Animation Engine cleaned up');
  }
}

// Create and export singleton instance
const animationEngine = new AnimationEngine();

// Export both class and instance
window.AnimationEngine = AnimationEngine;
window.animationEngine = animationEngine;

export { AnimationEngine, animationEngine };
export default animationEngine;