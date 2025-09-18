/**
 * 🌀 React Portal Template - Advanced Portal Management
 * =====================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade React Portal implementation with advanced features:
 * modal management, z-index stacking, focus management, and accessibility.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { 
  ReactNode, 
  useEffect, 
  useRef, 
  useState, 
  useCallback, 
  useMemo,
  createContext,
  useContext,
  useLayoutEffect,
  ComponentType
} from 'react';
import { createPortal } from 'react-dom';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface PortalProps {
  children: ReactNode;
  container?: Element | string;
  onMount?: (container: Element) => void;
  onUnmount?: (container: Element) => void;
  className?: string;
  testId?: string;
}

interface ModalPortalProps extends PortalProps {
  isOpen: boolean;
  onClose?: () => void;
  closeOnEscape?: boolean;
  closeOnOverlayClick?: boolean;
  preventScroll?: boolean;
  trapFocus?: boolean;
  restoreFocus?: boolean;
  zIndex?: number;
  overlay?: boolean;
  overlayClassName?: string;
  animation?: 'fade' | 'slide' | 'scale' | 'none';
  animationDuration?: number;
}

interface TooltipPortalProps extends PortalProps {
  trigger: ReactNode;
  content: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  offset?: number;
  delay?: number;
  hideDelay?: number;
  interactive?: boolean;
  arrow?: boolean;
  maxWidth?: string;
}

interface NotificationPortalProps {
  notifications: NotificationItem[];
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
  maxNotifications?: number;
  autoRemove?: boolean;
  autoRemoveDelay?: number;
  className?: string;
}

interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  actions?: NotificationAction[];
  timestamp?: number;
}

interface NotificationAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary';
}

interface PortalManagerContextType {
  registerPortal: (id: string, zIndex: number) => void;
  unregisterPortal: (id: string) => void;
  getTopZIndex: () => number;
  isTopLevel: (id: string) => boolean;
}

interface Position {
  top?: number;
  left?: number;
  bottom?: number;
  right?: number;
}

// ========================================
// 🌐 PORTAL MANAGER CONTEXT
// ========================================

const PortalManagerContext = createContext<PortalManagerContextType | null>(null);

export const usePortalManager = (): PortalManagerContextType => {
  const context = useContext(PortalManagerContext);
  if (!context) {
    throw new Error('usePortalManager must be used within a PortalManagerProvider');
  }
  return context;
};

export const PortalManagerProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [portals, setPortals] = useState<Map<string, number>>(new Map());
  const baseZIndex = useRef(1000);

  const registerPortal = useCallback((id: string, zIndex?: number) => {
    setPortals(prev => {
      const newPortals = new Map(prev);
      const finalZIndex = zIndex || (baseZIndex.current + newPortals.size);
      newPortals.set(id, finalZIndex);
      return newPortals;
    });
  }, []);

  const unregisterPortal = useCallback((id: string) => {
    setPortals(prev => {
      const newPortals = new Map(prev);
      newPortals.delete(id);
      return newPortals;
    });
  }, []);

  const getTopZIndex = useCallback((): number => {
    if (portals.size === 0) return baseZIndex.current;
    return Math.max(...Array.from(portals.values()));
  }, [portals]);

  const isTopLevel = useCallback((id: string): boolean => {
    const portalZIndex = portals.get(id);
    if (!portalZIndex) return false;
    return portalZIndex === getTopZIndex();
  }, [portals, getTopZIndex]);

  const value = useMemo(() => ({
    registerPortal,
    unregisterPortal,
    getTopZIndex,
    isTopLevel
  }), [registerPortal, unregisterPortal, getTopZIndex, isTopLevel]);

  return (
    <PortalManagerContext.Provider value={value}>
      {children}
    </PortalManagerContext.Provider>
  );
};

// ========================================
// 🌀 BASE PORTAL COMPONENT
// ========================================

export const Portal: React.FC<PortalProps> = ({
  children,
  container,
  onMount,
  onUnmount,
  className,
  testId = 'portal'
}) => {
  const [mountNode, setMountNode] = useState<Element | null>(null);

  useEffect(() => {
    let containerElement: Element;

    if (typeof container === 'string') {
      containerElement = document.querySelector(container) || document.body;
    } else if (container instanceof Element) {
      containerElement = container;
    } else {
      containerElement = document.body;
    }

    // Create wrapper div if needed
    if (!containerElement.querySelector(`[data-portal-testid="${testId}"]`)) {
      const wrapper = document.createElement('div');
      wrapper.setAttribute('data-portal-testid', testId);
      if (className) {
        wrapper.className = className;
      }
      containerElement.appendChild(wrapper);
      setMountNode(wrapper);
      onMount?.(wrapper);

      return () => {
        if (containerElement.contains(wrapper)) {
          containerElement.removeChild(wrapper);
          onUnmount?.(wrapper);
        }
      };
    } else {
      const existingWrapper = containerElement.querySelector(`[data-portal-testid="${testId}"]`) as Element;
      setMountNode(existingWrapper);
      onMount?.(existingWrapper);

      return () => {
        onUnmount?.(existingWrapper);
      };
    }
  }, [container, className, testId, onMount, onUnmount]);

  if (!mountNode) return null;

  return createPortal(children, mountNode);
};

// ========================================
// 🎭 MODAL PORTAL COMPONENT
// ========================================

export const ModalPortal: React.FC<ModalPortalProps> = ({
  children,
  isOpen,
  onClose,
  closeOnEscape = true,
  closeOnOverlayClick = true,
  preventScroll = true,
  trapFocus = true,
  restoreFocus = true,
  zIndex = 1000,
  overlay = true,
  overlayClassName = '',
  animation = 'fade',
  animationDuration = 300,
  className,
  testId = 'modal-portal',
  ...portalProps
}) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const portalManager = usePortalManager();
  const portalId = useRef(`modal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);

  // Handle animations
  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), animationDuration);
      return () => clearTimeout(timer);
    } else if (isVisible) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setIsVisible(false);
        setIsAnimating(false);
      }, animationDuration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, isVisible, animationDuration]);

  // Portal registration
  useEffect(() => {
    if (isVisible) {
      portalManager.registerPortal(portalId.current, zIndex);
      return () => portalManager.unregisterPortal(portalId.current);
    }
  }, [isVisible, zIndex, portalManager]);

  // Scroll prevention
  useEffect(() => {
    if (isVisible && preventScroll) {
      const originalOverflow = document.body.style.overflow;
      const originalPaddingRight = document.body.style.paddingRight;
      
      // Calculate scrollbar width
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
      
      document.body.style.overflow = 'hidden';
      if (scrollbarWidth > 0) {
        document.body.style.paddingRight = `${scrollbarWidth}px`;
      }

      return () => {
        document.body.style.overflow = originalOverflow;
        document.body.style.paddingRight = originalPaddingRight;
      };
    }
  }, [isVisible, preventScroll]);

  // Focus management
  useEffect(() => {
    if (isVisible && trapFocus) {
      if (restoreFocus) {
        previousFocusRef.current = document.activeElement as HTMLElement;
      }

      // Focus the modal
      if (modalRef.current) {
        const firstFocusable = modalRef.current.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as HTMLElement;
        
        if (firstFocusable) {
          firstFocusable.focus();
        } else {
          modalRef.current.focus();
        }
      }

      return () => {
        if (restoreFocus && previousFocusRef.current) {
          previousFocusRef.current.focus();
        }
      };
    }
  }, [isVisible, trapFocus, restoreFocus]);

  // Keyboard event handling
  useEffect(() => {
    if (!isVisible) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (closeOnEscape && event.key === 'Escape') {
        onClose?.();
        return;
      }

      if (trapFocus && event.key === 'Tab') {
        const modal = modalRef.current;
        if (!modal) return;

        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement?.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement?.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, closeOnEscape, trapFocus, onClose]);

  const handleOverlayClick = useCallback((event: React.MouseEvent) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose?.();
    }
  }, [closeOnOverlayClick, onClose]);

  const getAnimationStyles = useCallback((): React.CSSProperties => {
    const baseStyles: React.CSSProperties = {
      transition: `all ${animationDuration}ms ease-in-out`
    };

    if (!isVisible) return { ...baseStyles, opacity: 0, pointerEvents: 'none' };

    switch (animation) {
      case 'fade':
        return {
          ...baseStyles,
          opacity: isAnimating && isOpen ? 0 : 1
        };
      case 'slide':
        return {
          ...baseStyles,
          opacity: isAnimating && isOpen ? 0 : 1,
          transform: isAnimating && isOpen ? 'translateY(-20px)' : 'translateY(0)'
        };
      case 'scale':
        return {
          ...baseStyles,
          opacity: isAnimating && isOpen ? 0 : 1,
          transform: isAnimating && isOpen ? 'scale(0.95)' : 'scale(1)'
        };
      case 'none':
      default:
        return baseStyles;
    }
  }, [animation, animationDuration, isAnimating, isOpen, isVisible]);

  if (!isVisible) return null;

  return (
    <Portal {...portalProps} testId={testId}>
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex,
          ...getAnimationStyles()
        }}
      >
        {overlay && (
          <div
            className={`modal-overlay ${overlayClassName}`}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              cursor: closeOnOverlayClick ? 'pointer' : 'default'
            }}
            onClick={handleOverlayClick}
          />
        )}
        
        <div
          ref={modalRef}
          className={className}
          style={{
            position: 'relative',
            zIndex: 1,
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem'
          }}
          tabIndex={-1}
          role="dialog"
          aria-modal="true"
        >
          {children}
        </div>
      </div>
    </Portal>
  );
};

// ========================================
// 💬 TOOLTIP PORTAL COMPONENT
// ========================================

export const TooltipPortal: React.FC<TooltipPortalProps> = ({
  trigger,
  content,
  position = 'auto',
  offset = 8,
  delay = 300,
  hideDelay = 100,
  interactive = false,
  arrow = true,
  maxWidth = '200px',
  className,
  testId = 'tooltip-portal',
  ...portalProps
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [computedPosition, setComputedPosition] = useState<Position>({});
  const [actualPosition, setActualPosition] = useState<string>(position);
  
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const showTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current || !tooltipRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let finalPosition = position;
    const positions: Record<string, Position> = {
      top: {
        left: triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2,
        bottom: viewportHeight - triggerRect.top + offset
      },
      bottom: {
        left: triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2,
        top: triggerRect.bottom + offset
      },
      left: {
        right: viewportWidth - triggerRect.left + offset,
        top: triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
      },
      right: {
        left: triggerRect.right + offset,
        top: triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
      }
    };

    // Auto positioning
    if (position === 'auto') {
      const spaceTop = triggerRect.top;
      const spaceBottom = viewportHeight - triggerRect.bottom;
      const spaceLeft = triggerRect.left;
      const spaceRight = viewportWidth - triggerRect.right;

      const maxSpace = Math.max(spaceTop, spaceBottom, spaceLeft, spaceRight);
      
      if (maxSpace === spaceTop) finalPosition = 'top';
      else if (maxSpace === spaceBottom) finalPosition = 'bottom';
      else if (maxSpace === spaceLeft) finalPosition = 'left';
      else finalPosition = 'right';
    }

    setActualPosition(finalPosition);
    setComputedPosition(positions[finalPosition] || positions.top);
  }, [position, offset]);

  const showTooltip = useCallback(() => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }

    showTimeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  }, [delay]);

  const hideTooltip = useCallback(() => {
    if (showTimeoutRef.current) {
      clearTimeout(showTimeoutRef.current);
      showTimeoutRef.current = null;
    }

    hideTimeoutRef.current = setTimeout(() => {
      setIsVisible(false);
    }, hideDelay);
  }, [hideDelay]);

  useLayoutEffect(() => {
    if (isVisible) {
      calculatePosition();
    }
  }, [isVisible, calculatePosition]);

  useEffect(() => {
    return () => {
      if (showTimeoutRef.current) clearTimeout(showTimeoutRef.current);
      if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
    };
  }, []);

  const getArrowStyles = (): React.CSSProperties => {
    const arrowSize = 6;
    const arrowStyles: Record<string, React.CSSProperties> = {
      top: {
        bottom: -arrowSize,
        left: '50%',
        transform: 'translateX(-50%)',
        borderLeft: `${arrowSize}px solid transparent`,
        borderRight: `${arrowSize}px solid transparent`,
        borderTop: `${arrowSize}px solid #333`
      },
      bottom: {
        top: -arrowSize,
        left: '50%',
        transform: 'translateX(-50%)',
        borderLeft: `${arrowSize}px solid transparent`,
        borderRight: `${arrowSize}px solid transparent`,
        borderBottom: `${arrowSize}px solid #333`
      },
      left: {
        right: -arrowSize,
        top: '50%',
        transform: 'translateY(-50%)',
        borderTop: `${arrowSize}px solid transparent`,
        borderBottom: `${arrowSize}px solid transparent`,
        borderLeft: `${arrowSize}px solid #333`
      },
      right: {
        left: -arrowSize,
        top: '50%',
        transform: 'translateY(-50%)',
        borderTop: `${arrowSize}px solid transparent`,
        borderBottom: `${arrowSize}px solid transparent`,
        borderRight: `${arrowSize}px solid #333`
      }
    };

    return {
      position: 'absolute',
      width: 0,
      height: 0,
      ...arrowStyles[actualPosition]
    };
  };

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={interactive ? undefined : hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        style={{ display: 'inline-block' }}
      >
        {trigger}
      </div>

      {isVisible && (
        <Portal {...portalProps} testId={testId}>
          <div
            ref={tooltipRef}
            className={className}
            style={{
              position: 'fixed',
              zIndex: 9999,
              maxWidth,
              padding: '0.5rem',
              backgroundColor: '#333',
              color: 'white',
              borderRadius: '4px',
              fontSize: '0.875rem',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
              pointerEvents: interactive ? 'auto' : 'none',
              ...computedPosition
            }}
            onMouseEnter={interactive ? showTooltip : undefined}
            onMouseLeave={interactive ? hideTooltip : undefined}
            role="tooltip"
          >
            {content}
            {arrow && <div style={getArrowStyles()} />}
          </div>
        </Portal>
      )}
    </>
  );
};

// ========================================
// 🔔 NOTIFICATION PORTAL COMPONENT
// ========================================

export const NotificationPortal: React.FC<NotificationPortalProps> = ({
  notifications,
  position = 'top-right',
  maxNotifications = 5,
  autoRemove = true,
  autoRemoveDelay = 5000,
  className,
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<NotificationItem[]>([]);

  useEffect(() => {
    setVisibleNotifications(notifications.slice(0, maxNotifications));
  }, [notifications, maxNotifications]);

  useEffect(() => {
    if (!autoRemove) return;

    const timers = visibleNotifications.map(notification => {
      const delay = notification.duration || autoRemoveDelay;
      return setTimeout(() => {
        setVisibleNotifications(prev => 
          prev.filter(n => n.id !== notification.id)
        );
      }, delay);
    });

    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [visibleNotifications, autoRemove, autoRemoveDelay]);

  const getPositionStyles = (): React.CSSProperties => {
    const positions: Record<string, React.CSSProperties> = {
      'top-left': { top: '1rem', left: '1rem' },
      'top-right': { top: '1rem', right: '1rem' },
      'top-center': { top: '1rem', left: '50%', transform: 'translateX(-50%)' },
      'bottom-left': { bottom: '1rem', left: '1rem' },
      'bottom-right': { bottom: '1rem', right: '1rem' },
      'bottom-center': { bottom: '1rem', left: '50%', transform: 'translateX(-50%)' }
    };

    return positions[position] || positions['top-right'];
  };

  const getNotificationIcon = (type: NotificationItem['type']): string => {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[type];
  };

  const getNotificationColor = (type: NotificationItem['type']): string => {
    const colors = {
      success: '#10b981',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6'
    };
    return colors[type];
  };

  if (visibleNotifications.length === 0) return null;

  return (
    <Portal testId="notification-portal">
      <div
        className={className}
        style={{
          position: 'fixed',
          zIndex: 10000,
          pointerEvents: 'none',
          ...getPositionStyles()
        }}
      >
        {visibleNotifications.map((notification, index) => (
          <div
            key={notification.id}
            style={{
              marginBottom: '0.5rem',
              padding: '1rem',
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
              border: `1px solid ${getNotificationColor(notification.type)}`,
              maxWidth: '400px',
              pointerEvents: 'auto',
              transform: `translateY(${index * 10}px)`,
              transition: 'all 0.3s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.25rem', flexShrink: 0 }}>
                {getNotificationIcon(notification.type)}
              </span>
              
              <div style={{ flex: 1, minWidth: 0 }}>
                {notification.title && (
                  <h4 style={{ 
                    margin: '0 0 0.25rem 0', 
                    fontSize: '1rem', 
                    fontWeight: '600',
                    color: getNotificationColor(notification.type)
                  }}>
                    {notification.title}
                  </h4>
                )}
                
                <p style={{ 
                  margin: '0', 
                  fontSize: '0.875rem', 
                  color: '#374151',
                  lineHeight: '1.4'
                }}>
                  {notification.message}
                </p>

                {notification.actions && notification.actions.length > 0 && (
                  <div style={{ 
                    marginTop: '0.75rem', 
                    display: 'flex', 
                    gap: '0.5rem' 
                  }}>
                    {notification.actions.map((action, actionIndex) => (
                      <button
                        key={actionIndex}
                        onClick={action.action}
                        style={{
                          padding: '0.25rem 0.75rem',
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          border: '1px solid',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          backgroundColor: action.variant === 'primary' ? 
                            getNotificationColor(notification.type) : 'transparent',
                          color: action.variant === 'primary' ? 
                            'white' : getNotificationColor(notification.type),
                          borderColor: getNotificationColor(notification.type)
                        }}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Portal>
  );
};

// ========================================
// 🔧 UTILITY FUNCTIONS & HOOKS
// ========================================

export const usePortal = (container?: Element | string) => {
  const [mountNode, setMountNode] = useState<Element | null>(null);

  useEffect(() => {
    let containerElement: Element;

    if (typeof container === 'string') {
      containerElement = document.querySelector(container) || document.body;
    } else if (container instanceof Element) {
      containerElement = container;
    } else {
      containerElement = document.body;
    }

    setMountNode(containerElement);
  }, [container]);

  const renderPortal = useCallback((children: ReactNode) => {
    if (!mountNode) return null;
    return createPortal(children, mountNode);
  }, [mountNode]);

  return renderPortal;
};

export const withPortal = <P extends object>(
  Component: ComponentType<P>,
  container?: Element | string
) => {
  const WrappedComponent = (props: P) => {
    const renderPortal = usePortal(container);
    return renderPortal(<Component {...props} />);
  };

  WrappedComponent.displayName = `withPortal(${Component.displayName || Component.name})`;
  return WrappedComponent;
};

// ========================================
// 📦 EXPORTS
// ========================================

export {
  Portal,
  ModalPortal,
  TooltipPortal,
  NotificationPortal,
  PortalManagerProvider,
  usePortalManager,
  usePortal,
  withPortal
};

export type {
  PortalProps,
  ModalPortalProps,
  TooltipPortalProps,
  NotificationPortalProps,
  NotificationItem,
  NotificationAction,
  PortalManagerContextType,
  Position
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Portal
<Portal container="#portal-root">
  <div>This content will be rendered in #portal-root</div>
</Portal>

// Modal Portal
<ModalPortal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  closeOnEscape={true}
  closeOnOverlayClick={true}
  animation="fade"
  zIndex={1000}
>
  <div style={{ background: 'white', padding: '2rem', borderRadius: '8px' }}>
    <h2>Modal Content</h2>
    <p>This is a modal rendered in a portal.</p>
    <button onClick={() => setIsModalOpen(false)}>Close</button>
  </div>
</ModalPortal>

// Tooltip Portal
<TooltipPortal
  trigger={<button>Hover me</button>}
  content="This is a tooltip"
  position="top"
  delay={200}
  arrow={true}
  interactive={true}
/>

// Notification Portal
<NotificationPortal
  notifications={[
    {
      id: '1',
      type: 'success',
      title: 'Success!',
      message: 'Operation completed successfully',
      actions: [
        { label: 'Undo', action: () => console.log('Undo') },
        { label: 'View', action: () => console.log('View'), variant: 'primary' }
      ]
    }
  ]}
  position="top-right"
  autoRemove={true}
  autoRemoveDelay={5000}
/>

// Using Portal Manager
function App() {
  return (
    <PortalManagerProvider>
      <Router>
        <Routes>
          <Route path="/modal" element={<ModalPage />} />
        </Routes>
      </Router>
    </PortalManagerProvider>
  );
}

// Using Portal Hook
function MyComponent() {
  const renderPortal = usePortal('#custom-portal');
  
  return (
    <div>
      <h1>Main Content</h1>
      {renderPortal(
        <div>This will be rendered in #custom-portal</div>
      )}
    </div>
  );
}

// HOC Usage
const PortalizedComponent = withPortal(MyComponent, '#portal-container');
*/