/**
 * @fileoverview Event Dispatcher - Professional Event Management System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module src/renderer/event_dispatcher
 * @description Advanced event system with async support, middleware, and performance optimization
 */

class EventDispatcher {
  constructor() {
    this.listeners = new Map();
    this.onceListeners = new Map();
    this.middleware = [];
    this.eventHistory = [];
    this.maxHistorySize = 100;
    this.metrics = {
      totalEvents: 0,
      successfulEvents: 0,
      failedEvents: 0,
      averageProcessingTime: 0
    };
    
    this.wildcardListeners = new Set();
    this.namespaces = new Map();
    this.eventQueue = [];
    this.processing = false;
    this.batchProcessing = false;
    this.batchDelay = 10; // ms

    this.initializeBuiltInEvents();
    console.log('Event Dispatcher initialized');
  }

  /**
   * Initialize built-in events for Ainflue Desktop
   */
  initializeBuiltInEvents() {
    // Application lifecycle events
    this.defineEventNamespace('app', [
      'ready', 'focus', 'blur', 'minimize', 'maximize', 'close',
      'theme-changed', 'language-changed', 'fullscreen-enter', 'fullscreen-exit'
    ]);

    // Content management events
    this.defineEventNamespace('content', [
      'uploaded', 'processed', 'deleted', 'selected', 'deselected',
      'library-updated', 'metadata-updated', 'export-started', 'export-completed'
    ]);

    // AI processing events
    this.defineEventNamespace('ai', [
      'analysis-started', 'analysis-progress', 'analysis-completed', 'analysis-failed',
      'enhancement-started', 'enhancement-completed', 'recommendations-updated'
    ]);

    // Studio events
    this.defineEventNamespace('studio', [
      'project-created', 'project-opened', 'project-saved', 'project-closed',
      'timeline-updated', 'track-added', 'track-removed', 'playback-started', 'playback-stopped'
    ]);

    // Security events
    this.defineEventNamespace('security', [
      'content-encrypted', 'watermark-applied', 'signature-created',
      'access-granted', 'access-denied', 'security-alert'
    ]);

    // Collaboration events
    this.defineEventNamespace('collaboration', [
      'session-created', 'session-joined', 'session-left', 'user-connected',
      'user-disconnected', 'data-synced', 'conflict-detected'
    ]);

    // Platform integration events
    this.defineEventNamespace('platform', [
      'connected', 'disconnected', 'published', 'scheduled',
      'analytics-updated', 'error-occurred'
    ]);

    // UI events
    this.defineEventNamespace('ui', [
      'modal-opened', 'modal-closed', 'sidebar-toggled', 'panel-resized',
      'notification-shown', 'tooltip-shown', 'tooltip-hidden'
    ]);

    // Performance events
    this.defineEventNamespace('performance', [
      'metrics-updated', 'memory-warning', 'cpu-high', 'gpu-activity',
      'disk-space-low', 'network-status-changed'
    ]);
  }

  /**
   * Define event namespace with predefined events
   */
  defineEventNamespace(namespace, events) {
    if (!this.namespaces.has(namespace)) {
      this.namespaces.set(namespace, new Set());
    }
    
    const namespaceEvents = this.namespaces.get(namespace);
    events.forEach(event => namespaceEvents.add(event));
  }

  /**
   * Add event listener
   */
  on(event, listener, options = {}) {
    const { 
      once = false, 
      priority = 0, 
      namespace = null,
      condition = null,
      throttle = 0,
      debounce = 0
    } = options;

    if (typeof listener !== 'function') {
      throw new Error('Event listener must be a function');
    }

    const wrappedListener = this.wrapListener(listener, {
      condition,
      throttle,
      debounce,
      namespace
    });

    const listenerData = {
      id: this.generateListenerId(),
      listener: wrappedListener,
      originalListener: listener,
      priority,
      namespace,
      options
    };

    // Handle wildcard listeners
    if (event === '*' || event.includes('*')) {
      this.wildcardListeners.add(listenerData);
      return this.createUnsubscriber(event, listenerData.id, true);
    }

    // Regular event listeners
    const targetMap = once ? this.onceListeners : this.listeners;
    
    if (!targetMap.has(event)) {
      targetMap.set(event, []);
    }

    const listeners = targetMap.get(event);
    
    // Insert listener based on priority (higher priority first)
    const insertIndex = listeners.findIndex(l => l.priority < priority);
    if (insertIndex === -1) {
      listeners.push(listenerData);
    } else {
      listeners.splice(insertIndex, 0, listenerData);
    }

    return this.createUnsubscriber(event, listenerData.id, once);
  }

  /**
   * Add one-time event listener
   */
  once(event, listener, options = {}) {
    return this.on(event, listener, { ...options, once: true });
  }

  /**
   * Remove event listener
   */
  off(event, listener) {
    // Remove from regular listeners
    if (this.listeners.has(event)) {
      const listeners = this.listeners.get(event);
      const index = listeners.findIndex(l => 
        l.listener === listener || l.originalListener === listener
      );
      if (index !== -1) {
        listeners.splice(index, 1);
        if (listeners.length === 0) {
          this.listeners.delete(event);
        }
        return true;
      }
    }

    // Remove from once listeners
    if (this.onceListeners.has(event)) {
      const listeners = this.onceListeners.get(event);
      const index = listeners.findIndex(l => 
        l.listener === listener || l.originalListener === listener
      );
      if (index !== -1) {
        listeners.splice(index, 1);
        if (listeners.length === 0) {
          this.onceListeners.delete(event);
        }
        return true;
      }
    }

    // Remove from wildcard listeners
    for (const listenerData of this.wildcardListeners) {
      if (listenerData.listener === listener || listenerData.originalListener === listener) {
        this.wildcardListeners.delete(listenerData);
        return true;
      }
    }

    return false;
  }

  /**
   * Emit event synchronously
   */
  emit(event, data = null, options = {}) {
    const { 
      namespace = null,
      bubbles = true,
      cancelable = true,
      async = false
    } = options;

    if (async) {
      return this.emitAsync(event, data, options);
    }

    const startTime = performance.now();
    const eventData = this.createEventData(event, data, options);

    try {
      // Apply middleware
      const processedEvent = this.applyMiddleware('BEFORE_EMIT', eventData);
      
      if (processedEvent.cancelled) {
        return { cancelled: true, result: null };
      }

      // Process the event
      const result = this.processEvent(processedEvent);
      
      // Apply post-middleware
      this.applyMiddleware('AFTER_EMIT', { ...processedEvent, result });
      
      // Update metrics
      this.updateMetrics(true, performance.now() - startTime);
      
      // Add to history
      this.addToHistory(eventData, result, performance.now() - startTime);

      return { cancelled: false, result };

    } catch (error) {
      this.updateMetrics(false, performance.now() - startTime);
      this.handleEventError(eventData, error);
      throw error;
    }
  }

  /**
   * Emit event asynchronously
   */
  async emitAsync(event, data = null, options = {}) {
    const startTime = performance.now();
    const eventData = this.createEventData(event, data, options);

    try {
      // Apply middleware
      const processedEvent = await this.applyMiddlewareAsync('BEFORE_EMIT', eventData);
      
      if (processedEvent.cancelled) {
        return { cancelled: true, result: null };
      }

      // Process the event
      const result = await this.processEventAsync(processedEvent);
      
      // Apply post-middleware
      await this.applyMiddlewareAsync('AFTER_EMIT', { ...processedEvent, result });
      
      // Update metrics
      this.updateMetrics(true, performance.now() - startTime);
      
      // Add to history
      this.addToHistory(eventData, result, performance.now() - startTime);

      return { cancelled: false, result };

    } catch (error) {
      this.updateMetrics(false, performance.now() - startTime);
      this.handleEventError(eventData, error);
      throw error;
    }
  }

  /**
   * Batch emit multiple events
   */
  async emitBatch(events) {
    this.batchProcessing = true;
    const results = [];

    try {
      for (const { event, data, options } of events) {
        const result = await this.emitAsync(event, data, options);
        results.push({ event, result });
      }
    } finally {
      this.batchProcessing = false;
    }

    return results;
  }

  /**
   * Process event synchronously
   */
  processEvent(eventData) {
    const { event, data } = eventData;
    const results = [];

    // Process regular listeners
    const listeners = this.listeners.get(event) || [];
    for (const listenerData of listeners) {
      try {
        const result = listenerData.listener(data, eventData);
        results.push(result);
        
        if (eventData.cancelled) break;
      } catch (error) {
        console.error(`Listener error for event '${event}':`, error);
      }
    }

    // Process once listeners
    const onceListeners = this.onceListeners.get(event) || [];
    for (const listenerData of onceListeners) {
      try {
        const result = listenerData.listener(data, eventData);
        results.push(result);
        
        if (eventData.cancelled) break;
      } catch (error) {
        console.error(`Once listener error for event '${event}':`, error);
      }
    }

    // Remove once listeners
    if (onceListeners.length > 0) {
      this.onceListeners.delete(event);
    }

    // Process wildcard listeners
    for (const listenerData of this.wildcardListeners) {
      if (this.matchesWildcard(event, listenerData.namespace)) {
        try {
          const result = listenerData.listener(data, eventData);
          results.push(result);
          
          if (eventData.cancelled) break;
        } catch (error) {
          console.error(`Wildcard listener error for event '${event}':`, error);
        }
      }
    }

    return results;
  }

  /**
   * Process event asynchronously
   */
  async processEventAsync(eventData) {
    const { event, data } = eventData;
    const results = [];

    // Process regular listeners
    const listeners = this.listeners.get(event) || [];
    for (const listenerData of listeners) {
      try {
        const result = await listenerData.listener(data, eventData);
        results.push(result);
        
        if (eventData.cancelled) break;
      } catch (error) {
        console.error(`Async listener error for event '${event}':`, error);
      }
    }

    // Process once listeners
    const onceListeners = this.onceListeners.get(event) || [];
    for (const listenerData of onceListeners) {
      try {
        const result = await listenerData.listener(data, eventData);
        results.push(result);
        
        if (eventData.cancelled) break;
      } catch (error) {
        console.error(`Async once listener error for event '${event}':`, error);
      }
    }

    // Remove once listeners
    if (onceListeners.length > 0) {
      this.onceListeners.delete(event);
    }

    // Process wildcard listeners
    for (const listenerData of this.wildcardListeners) {
      if (this.matchesWildcard(event, listenerData.namespace)) {
        try {
          const result = await listenerData.listener(data, eventData);
          results.push(result);
          
          if (eventData.cancelled) break;
        } catch (error) {
          console.error(`Async wildcard listener error for event '${event}':`, error);
        }
      }
    }

    return results;
  }

  /**
   * Add middleware
   */
  addMiddleware(middleware) {
    if (typeof middleware !== 'function') {
      throw new Error('Middleware must be a function');
    }

    this.middleware.push(middleware);
    
    return () => {
      const index = this.middleware.indexOf(middleware);
      if (index > -1) {
        this.middleware.splice(index, 1);
      }
    };
  }

  /**
   * Apply middleware
   */
  applyMiddleware(phase, eventData) {
    let processedData = eventData;

    for (const middleware of this.middleware) {
      try {
        const result = middleware(phase, processedData);
        if (result !== undefined) {
          processedData = result;
        }
      } catch (error) {
        console.error('Middleware error:', error);
      }
    }

    return processedData;
  }

  /**
   * Apply middleware asynchronously
   */
  async applyMiddlewareAsync(phase, eventData) {
    let processedData = eventData;

    for (const middleware of this.middleware) {
      try {
        const result = await middleware(phase, processedData);
        if (result !== undefined) {
          processedData = result;
        }
      } catch (error) {
        console.error('Async middleware error:', error);
      }
    }

    return processedData;
  }

  /**
   * Create event data object
   */
  createEventData(event, data, options) {
    return {
      event,
      data,
      timestamp: Date.now(),
      id: this.generateEventId(),
      cancelled: false,
      bubbles: options.bubbles !== false,
      cancelable: options.cancelable !== false,
      namespace: options.namespace || this.extractNamespace(event),
      preventDefault: function() {
        if (this.cancelable) {
          this.cancelled = true;
        }
      }
    };
  }

  /**
   * Wrap listener with additional functionality
   */
  wrapListener(listener, options) {
    const { condition, throttle, debounce } = options;
    let wrappedListener = listener;

    // Add condition checking
    if (condition) {
      const conditionalListener = wrappedListener;
      wrappedListener = (data, eventData) => {
        if (condition(data, eventData)) {
          return conditionalListener(data, eventData);
        }
      };
    }

    // Add throttling
    if (throttle > 0) {
      wrappedListener = this.throttle(wrappedListener, throttle);
    }

    // Add debouncing
    if (debounce > 0) {
      wrappedListener = this.debounce(wrappedListener, debounce);
    }

    return wrappedListener;
  }

  /**
   * Throttle function
   */
  throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        return func.apply(this, args);
      }
    };
  }

  /**
   * Debounce function
   */
  debounce(func, delay) {
    let timeoutId;
    return function(...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Check if event matches wildcard pattern
   */
  matchesWildcard(event, namespace) {
    if (namespace) {
      return event.startsWith(namespace + '.');
    }
    return true;
  }

  /**
   * Extract namespace from event name
   */
  extractNamespace(event) {
    const parts = event.split('.');
    return parts.length > 1 ? parts[0] : null;
  }

  /**
   * Generate unique listener ID
   */
  generateListenerId() {
    return `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique event ID
   */
  generateEventId() {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Create unsubscriber function
   */
  createUnsubscriber(event, listenerId, isOnce = false) {
    return () => {
      const targetMap = isOnce ? this.onceListeners : this.listeners;
      
      if (targetMap.has(event)) {
        const listeners = targetMap.get(event);
        const index = listeners.findIndex(l => l.id === listenerId);
        
        if (index !== -1) {
          listeners.splice(index, 1);
          if (listeners.length === 0) {
            targetMap.delete(event);
          }
          return true;
        }
      }
      
      // Check wildcard listeners
      for (const listenerData of this.wildcardListeners) {
        if (listenerData.id === listenerId) {
          this.wildcardListeners.delete(listenerData);
          return true;
        }
      }
      
      return false;
    };
  }

  /**
   * Handle event processing errors
   */
  handleEventError(eventData, error) {
    console.error(`Event processing error for '${eventData.event}':`, error);
    
    // Emit error event
    try {
      this.emit('error', {
        originalEvent: eventData,
        error: error.message,
        stack: error.stack
      });
    } catch (e) {
      console.error('Failed to emit error event:', e);
    }
  }

  /**
   * Update performance metrics
   */
  updateMetrics(success, processingTime) {
    this.metrics.totalEvents++;
    
    if (success) {
      this.metrics.successfulEvents++;
    } else {
      this.metrics.failedEvents++;
    }

    // Update average processing time
    const totalProcessed = this.metrics.successfulEvents + this.metrics.failedEvents;
    this.metrics.averageProcessingTime = 
      (this.metrics.averageProcessingTime * (totalProcessed - 1) + processingTime) / totalProcessed;
  }

  /**
   * Add event to history
   */
  addToHistory(eventData, result, processingTime) {
    this.eventHistory.push({
      ...eventData,
      result,
      processingTime
    });

    // Keep history size manageable
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }
  }

  /**
   * Get event metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      successRate: this.metrics.totalEvents > 0 
        ? (this.metrics.successfulEvents / this.metrics.totalEvents * 100).toFixed(2) + '%'
        : '0%',
      activeListeners: this.getListenerCount(),
      namespaces: Array.from(this.namespaces.keys())
    };
  }

  /**
   * Get total listener count
   */
  getListenerCount() {
    let count = 0;
    
    for (const listeners of this.listeners.values()) {
      count += listeners.length;
    }
    
    for (const listeners of this.onceListeners.values()) {
      count += listeners.length;
    }
    
    count += this.wildcardListeners.size;
    
    return count;
  }

  /**
   * Get event history
   */
  getHistory(limit = 10) {
    return this.eventHistory.slice(-limit);
  }

  /**
   * Clear event history
   */
  clearHistory() {
    this.eventHistory.length = 0;
  }

  /**
   * Remove all listeners
   */
  removeAllListeners(event = null) {
    if (event) {
      this.listeners.delete(event);
      this.onceListeners.delete(event);
    } else {
      this.listeners.clear();
      this.onceListeners.clear();
      this.wildcardListeners.clear();
    }
  }

  /**
   * Check if event has listeners
   */
  hasListeners(event) {
    return this.listeners.has(event) || 
           this.onceListeners.has(event) ||
           this.wildcardListeners.size > 0;
  }

  /**
   * Get listeners for event
   */
  getListeners(event) {
    const regular = this.listeners.get(event) || [];
    const once = this.onceListeners.get(event) || [];
    const wildcards = Array.from(this.wildcardListeners)
      .filter(l => this.matchesWildcard(event, l.namespace));
    
    return [...regular, ...once, ...wildcards];
  }

  /**
   * Debug information
   */
  debug() {
    console.group('Event Dispatcher Debug');
    console.log('Metrics:', this.getMetrics());
    console.log('Active Events:', Array.from(this.listeners.keys()));
    console.log('Once Events:', Array.from(this.onceListeners.keys()));
    console.log('Wildcard Listeners:', this.wildcardListeners.size);
    console.log('Namespaces:', Object.fromEntries(this.namespaces));
    console.log('Recent History:', this.getHistory(5));
    console.groupEnd();
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.removeAllListeners();
    this.middleware.length = 0;
    this.eventHistory.length = 0;
    this.namespaces.clear();
    console.log('Event Dispatcher cleaned up');
  }
}

// Create and export singleton instance
const eventDispatcher = new EventDispatcher();

// Export both class and instance
window.EventDispatcher = EventDispatcher;
window.eventDispatcher = eventDispatcher;

export { EventDispatcher, eventDispatcher };
export default eventDispatcher;