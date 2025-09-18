/**
 * 🎨 REACT PORTAL TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ==========================================================
 * 
 * Enterprise-grade React portal template with:
 * - TypeScript support with strict typing
 * - Modal and overlay management
 * - Portal escape mechanisms
 * - Focus management and accessibility
 * - Z-index and stacking context management
 * - Event delegation and cleanup
 * - SSR compatibility
 * 
 * ⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
 * ==========================================
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 * 
 * Author: Frontend Expert - Fahed Mlaiel
 * Version: 1.0.0
 */

import React, { 
  useEffect, 
  useRef, 
  useState, 
  useCallback,
  ReactNode,
  ReactPortal,
  ComponentType
} from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface PortalProps {
  children: ReactNode;
  container?: Element | string;
  className?: string;
  style?: React.CSSProperties;
  onMount?: () => void;
  onUnmount?: () => void;
}

interface ModalPortalProps extends PortalProps {
  isOpen: boolean;
  onClose?: () => void;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  lockScroll?: boolean;
  backdrop?: boolean;
  backdropClassName?: string;
  focusFirstElement?: boolean;
  returnFocus?: boolean;
  animation?: ModalAnimation;
  zIndex?: number;
}

interface TooltipPortalProps extends PortalProps {
  isVisible: boolean;
  targetRef: React.RefObject<HTMLElement>;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  offset?: number;
  arrow?: boolean;
  delay?: number;
}

interface NotificationPortalProps extends PortalProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
  autoClose?: boolean;
  duration?: number;
  onAutoClose?: () => void;
}

interface DropdownPortalProps extends PortalProps {
  isOpen: boolean;
  triggerRef: React.RefObject<HTMLElement>;
  onClose?: () => void;
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
  offset?: { x: number; y: number };
  closeOnClickOutside?: boolean;
  closeOnScroll?: boolean;
}

type ModalAnimation = 'fade' | 'scale' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right';

// ============================================================================
// PORTAL MANAGER
// ============================================================================

class PortalManager {
  private static instance: PortalManager;
  private containers: Map<string, HTMLElement> = new Map();
  private zIndexCounter = 1000;

  static getInstance(): PortalManager {
    if (!PortalManager.instance) {
      PortalManager.instance = new PortalManager();
    }
    return PortalManager.instance;
  }

  getContainer(name: string): HTMLElement {
    if (!this.containers.has(name)) {
      const container = document.createElement('div');
      container.setAttribute('data-portal-name', name);
      container.className = `portal-container portal-${name}`;
      document.body.appendChild(container);
      this.containers.set(name, container);
    }
    return this.containers.get(name)!;
  }

  removeContainer(name: string): void {
    const container = this.containers.get(name);
    if (container && container.children.length === 0) {
      document.body.removeChild(container);
      this.containers.delete(name);
    }
  }

  getNextZIndex(): number {
    return ++this.zIndexCounter;
  }

  cleanup(): void {
    this.containers.forEach((container, name) => {
      if (container.children.length === 0) {
        this.removeContainer(name);
      }
    });
  }
}

// ============================================================================
// BASE PORTAL COMPONENT
// ============================================================================

export const Portal: React.FC<PortalProps> = ({
  children,
  container,
  className,
  style,
  onMount,
  onUnmount
}) => {
  const [mounted, setMounted] = useState(false);
  const portalRef = useRef<HTMLDivElement>(null);

  // Get or create container
  const getPortalContainer = useCallback(() => {
    if (typeof container === 'string') {
      const existing = document.getElementById(container);
      if (existing) return existing;
      
      // Create container if it doesn't exist
      const newContainer = document.createElement('div');
      newContainer.id = container;
      document.body.appendChild(newContainer);
      return newContainer;
    }
    
    if (container instanceof Element) {
      return container;
    }
    
    // Default: use body
    return document.body;
  }, [container]);

  useEffect(() => {
    setMounted(true);
    
    // Create portal element
    const portalElement = document.createElement('div');
    portalElement.className = className || 'portal';
    if (style) {
      Object.assign(portalElement.style, style);
    }
    
    portalRef.current = portalElement;
    onMount?.();

    return () => {
      onUnmount?.();
      if (portalRef.current?.parentNode) {
        portalRef.current.parentNode.removeChild(portalRef.current);
      }
    };
  }, [className, style, onMount, onUnmount]);

  if (!mounted || typeof window === 'undefined') {
    return null;
  }

  const portalContainer = getPortalContainer();
  
  if (!portalRef.current) {
    return null;
  }

  if (!portalRef.current.parentNode) {
    portalContainer.appendChild(portalRef.current);
  }

  return createPortal(children, portalRef.current);
};

// ============================================================================
// MODAL PORTAL COMPONENT
// ============================================================================

export const ModalPortal: React.FC<ModalPortalProps> = ({
  children,
  isOpen,
  onClose,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  lockScroll = true,
  backdrop = true,
  backdropClassName = '',
  focusFirstElement = true,
  returnFocus = true,
  animation = 'fade',
  zIndex,
  ...portalProps
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const portalManager = PortalManager.getInstance();

  // Lock/unlock scroll
  useEffect(() => {
    if (isOpen && lockScroll) {
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      
      return () => {
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [isOpen, lockScroll]);

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose?.();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Focus management
  useEffect(() => {
    if (isOpen) {
      // Store current focus
      if (returnFocus) {
        previousFocusRef.current = document.activeElement as HTMLElement;
      }

      // Focus first element in modal
      if (focusFirstElement && modalRef.current) {
        const focusableElement = modalRef.current.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as HTMLElement;
        
        focusableElement?.focus();
      }
    } else {
      // Return focus to previous element
      if (returnFocus && previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    }
  }, [isOpen, focusFirstElement, returnFocus]);

  const handleBackdropClick = (event: React.MouseEvent) => {
    if (closeOnBackdropClick && event.target === event.currentTarget) {
      onClose?.();
    }
  };

  const getAnimationVariants = () => {
    switch (animation) {
      case 'scale':
        return {
          initial: { opacity: 0, scale: 0.8 },
          animate: { opacity: 1, scale: 1 },
          exit: { opacity: 0, scale: 0.8 }
        };
      case 'slide-up':
        return {
          initial: { opacity: 0, y: 100 },
          animate: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: 100 }
        };
      case 'slide-down':
        return {
          initial: { opacity: 0, y: -100 },
          animate: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: -100 }
        };
      case 'slide-left':
        return {
          initial: { opacity: 0, x: 100 },
          animate: { opacity: 1, x: 0 },
          exit: { opacity: 0, x: 100 }
        };
      case 'slide-right':
        return {
          initial: { opacity: 0, x: -100 },
          animate: { opacity: 1, x: 0 },
          exit: { opacity: 0, x: -100 }
        };
      default: // fade
        return {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          exit: { opacity: 0 }
        };
    }
  };

  return (
    <Portal
      container={portalManager.getContainer('modals')}
      {...portalProps}
    >
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: zIndex || portalManager.getNextZIndex(),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1rem'
            }}
            onClick={handleBackdropClick}
          >
            {/* Backdrop */}
            {backdrop && (
              <div
                className={`modal-backdrop ${backdropClassName}`}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.5)',
                  backdropFilter: 'blur(4px)'
                }}
              />
            )}

            {/* Modal Content */}
            <motion.div
              ref={modalRef}
              {...getAnimationVariants()}
              transition={{ duration: 0.2 }}
              style={{
                position: 'relative',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                maxWidth: '90vw',
                maxHeight: '90vh',
                overflow: 'auto'
              }}
              onClick={(e) => e.stopPropagation()}
            >
              {children}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </Portal>
  );
};

// ============================================================================
// TOOLTIP PORTAL COMPONENT
// ============================================================================

export const TooltipPortal: React.FC<TooltipPortalProps> = ({
  children,
  isVisible,
  targetRef,
  placement = 'top',
  offset = 8,
  arrow = true,
  delay = 0,
  ...portalProps
}) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const calculatePosition = useCallback(() => {
    if (!targetRef.current || !tooltipRef.current) return;

    const targetRect = targetRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    
    let x = 0;
    let y = 0;

    switch (placement) {
      case 'top':
        x = targetRect.left + targetRect.width / 2 - tooltipRect.width / 2;
        y = targetRect.top - tooltipRect.height - offset;
        break;
      case 'bottom':
        x = targetRect.left + targetRect.width / 2 - tooltipRect.width / 2;
        y = targetRect.bottom + offset;
        break;
      case 'left':
        x = targetRect.left - tooltipRect.width - offset;
        y = targetRect.top + targetRect.height / 2 - tooltipRect.height / 2;
        break;
      case 'right':
        x = targetRect.right + offset;
        y = targetRect.top + targetRect.height / 2 - tooltipRect.height / 2;
        break;
    }

    // Keep tooltip within viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    x = Math.max(8, Math.min(x, viewportWidth - tooltipRect.width - 8));
    y = Math.max(8, Math.min(y, viewportHeight - tooltipRect.height - 8));

    setPosition({ x, y });
  }, [targetRef, placement, offset]);

  useEffect(() => {
    if (isVisible) {
      if (delay > 0) {
        timeoutRef.current = setTimeout(() => {
          calculatePosition();
        }, delay);
      } else {
        calculatePosition();
      }

      // Recalculate on scroll/resize
      const handleReposition = () => calculatePosition();
      window.addEventListener('scroll', handleReposition);
      window.addEventListener('resize', handleReposition);

      return () => {
        window.removeEventListener('scroll', handleReposition);
        window.removeEventListener('resize', handleReposition);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      };
    }
  }, [isVisible, calculatePosition, delay]);

  return (
    <Portal {...portalProps}>
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.15 }}
            style={{
              position: 'fixed',
              left: position.x,
              top: position.y,
              zIndex: 9999,
              backgroundColor: '#374151',
              color: 'white',
              padding: '0.5rem 0.75rem',
              borderRadius: '6px',
              fontSize: '0.875rem',
              fontWeight: 500,
              pointerEvents: 'none',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}
          >
            {children}
            
            {/* Arrow */}
            {arrow && (
              <div
                style={{
                  position: 'absolute',
                  width: 0,
                  height: 0,
                  borderStyle: 'solid',
                  ...(placement === 'top' && {
                    bottom: '-5px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    borderLeftColor: 'transparent',
                    borderRightColor: 'transparent',
                    borderBottomColor: 'transparent',
                    borderTopColor: '#374151',
                    borderWidth: '5px 5px 0 5px'
                  }),
                  ...(placement === 'bottom' && {
                    top: '-5px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    borderLeftColor: 'transparent',
                    borderRightColor: 'transparent',
                    borderTopColor: 'transparent',
                    borderBottomColor: '#374151',
                    borderWidth: '0 5px 5px 5px'
                  }),
                  ...(placement === 'left' && {
                    right: '-5px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    borderTopColor: 'transparent',
                    borderBottomColor: 'transparent',
                    borderRightColor: 'transparent',
                    borderLeftColor: '#374151',
                    borderWidth: '5px 0 5px 5px'
                  }),
                  ...(placement === 'right' && {
                    left: '-5px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    borderTopColor: 'transparent',
                    borderBottomColor: 'transparent',
                    borderLeftColor: 'transparent',
                    borderRightColor: '#374151',
                    borderWidth: '5px 5px 5px 0'
                  })
                }}
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </Portal>
  );
};

// ============================================================================
// NOTIFICATION PORTAL COMPONENT
// ============================================================================

export const NotificationPortal: React.FC<NotificationPortalProps> = ({
  children,
  position = 'top-right',
  autoClose = true,
  duration = 5000,
  onAutoClose,
  ...portalProps
}) => {
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (autoClose) {
      timeoutRef.current = setTimeout(() => {
        onAutoClose?.();
      }, duration);

      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      };
    }
  }, [autoClose, duration, onAutoClose]);

  const getPositionStyles = () => {
    const base = {
      position: 'fixed' as const,
      zIndex: 9999
    };

    switch (position) {
      case 'top-left':
        return { ...base, top: '1rem', left: '1rem' };
      case 'top-right':
        return { ...base, top: '1rem', right: '1rem' };
      case 'top-center':
        return { ...base, top: '1rem', left: '50%', transform: 'translateX(-50%)' };
      case 'bottom-left':
        return { ...base, bottom: '1rem', left: '1rem' };
      case 'bottom-right':
        return { ...base, bottom: '1rem', right: '1rem' };
      case 'bottom-center':
        return { ...base, bottom: '1rem', left: '50%', transform: 'translateX(-50%)' };
      default:
        return { ...base, top: '1rem', right: '1rem' };
    }
  };

  return (
    <Portal {...portalProps}>
      <motion.div
        initial={{ opacity: 0, y: position.includes('top') ? -20 : 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: position.includes('top') ? -20 : 20 }}
        transition={{ duration: 0.3 }}
        style={getPositionStyles()}
      >
        {children}
      </motion.div>
    </Portal>
  );
};

// ============================================================================
// DROPDOWN PORTAL COMPONENT
// ============================================================================

export const DropdownPortal: React.FC<DropdownPortalProps> = ({
  children,
  isOpen,
  triggerRef,
  onClose,
  placement = 'bottom-start',
  offset = { x: 0, y: 8 },
  closeOnClickOutside = true,
  closeOnScroll = true,
  ...portalProps
}) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const dropdownRef = useRef<HTMLDivElement>(null);

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current || !dropdownRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const dropdownRect = dropdownRef.current.getBoundingClientRect();
    
    let x = 0;
    let y = 0;

    switch (placement) {
      case 'bottom-start':
        x = triggerRect.left;
        y = triggerRect.bottom + offset.y;
        break;
      case 'bottom-end':
        x = triggerRect.right - dropdownRect.width;
        y = triggerRect.bottom + offset.y;
        break;
      case 'top-start':
        x = triggerRect.left;
        y = triggerRect.top - dropdownRect.height - offset.y;
        break;
      case 'top-end':
        x = triggerRect.right - dropdownRect.width;
        y = triggerRect.top - dropdownRect.height - offset.y;
        break;
    }

    x += offset.x;

    // Keep dropdown within viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    x = Math.max(8, Math.min(x, viewportWidth - dropdownRect.width - 8));
    y = Math.max(8, Math.min(y, viewportHeight - dropdownRect.height - 8));

    setPosition({ x, y });
  }, [triggerRef, placement, offset]);

  // Handle click outside
  useEffect(() => {
    if (!isOpen || !closeOnClickOutside) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        onClose?.();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, closeOnClickOutside, onClose, triggerRef]);

  // Handle scroll
  useEffect(() => {
    if (!isOpen) return;

    if (closeOnScroll) {
      const handleScroll = () => onClose?.();
      window.addEventListener('scroll', handleScroll, true);
      return () => window.removeEventListener('scroll', handleScroll, true);
    } else {
      const handleScroll = () => calculatePosition();
      window.addEventListener('scroll', handleScroll);
      window.addEventListener('resize', handleScroll);
      return () => {
        window.removeEventListener('scroll', handleScroll);
        window.removeEventListener('resize', handleScroll);
      };
    }
  }, [isOpen, closeOnScroll, onClose, calculatePosition]);

  useEffect(() => {
    if (isOpen) {
      calculatePosition();
    }
  }, [isOpen, calculatePosition]);

  return (
    <Portal {...portalProps}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={dropdownRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.1 }}
            style={{
              position: 'fixed',
              left: position.x,
              top: position.y,
              zIndex: 9999,
              backgroundColor: 'white',
              borderRadius: '6px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              border: '1px solid #e5e7eb',
              minWidth: '8rem'
            }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </Portal>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const PortalExamples: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  const tooltipTriggerRef = useRef<HTMLButtonElement>(null);
  const dropdownTriggerRef = useRef<HTMLButtonElement>(null);

  return (
    <div className="portal-examples" style={{ padding: '2rem' }}>
      <h2>Portal Examples</h2>

      {/* Modal Example */}
      <section style={{ marginBottom: '2rem' }}>
        <h3>Modal Portal</h3>
        <button onClick={() => setIsModalOpen(true)}>
          Open Modal
        </button>
        
        <ModalPortal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          animation="scale"
        >
          <div style={{ padding: '2rem', minWidth: '400px' }}>
            <h3>Modal Title</h3>
            <p>This is a modal rendered in a portal.</p>
            <div style={{ marginTop: '1rem' }}>
              <button onClick={() => setIsModalOpen(false)}>
                Close
              </button>
            </div>
          </div>
        </ModalPortal>
      </section>

      {/* Tooltip Example */}
      <section style={{ marginBottom: '2rem' }}>
        <h3>Tooltip Portal</h3>
        <button
          ref={tooltipTriggerRef}
          onMouseEnter={() => setIsTooltipVisible(true)}
          onMouseLeave={() => setIsTooltipVisible(false)}
        >
          Hover for Tooltip
        </button>
        
        <TooltipPortal
          isVisible={isTooltipVisible}
          targetRef={tooltipTriggerRef}
          placement="top"
        >
          This is a tooltip rendered in a portal!
        </TooltipPortal>
      </section>

      {/* Notification Example */}
      <section style={{ marginBottom: '2rem' }}>
        <h3>Notification Portal</h3>
        <button onClick={() => setNotification('Success! This is a notification.')}>
          Show Notification
        </button>
        
        {notification && (
          <NotificationPortal
            position="top-right"
            autoClose={true}
            duration={3000}
            onAutoClose={() => setNotification(null)}
          >
            <div style={{
              backgroundColor: '#10b981',
              color: 'white',
              padding: '1rem',
              borderRadius: '6px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
            }}>
              {notification}
            </div>
          </NotificationPortal>
        )}
      </section>

      {/* Dropdown Example */}
      <section style={{ marginBottom: '2rem' }}>
        <h3>Dropdown Portal</h3>
        <button
          ref={dropdownTriggerRef}
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        >
          Toggle Dropdown
        </button>
        
        <DropdownPortal
          isOpen={isDropdownOpen}
          triggerRef={dropdownTriggerRef}
          onClose={() => setIsDropdownOpen(false)}
          placement="bottom-start"
        >
          <div style={{ padding: '0.5rem' }}>
            <div style={{ padding: '0.5rem', cursor: 'pointer' }}>Option 1</div>
            <div style={{ padding: '0.5rem', cursor: 'pointer' }}>Option 2</div>
            <div style={{ padding: '0.5rem', cursor: 'pointer' }}>Option 3</div>
          </div>
        </DropdownPortal>
      </section>
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  Portal,
  ModalPortal,
  TooltipPortal,
  NotificationPortal,
  DropdownPortal,
  PortalExamples,
  PortalManager
};