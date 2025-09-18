/**
 * 🎨 MODAL COMPONENT TEMPLATE - ENTERPRISE DIALOG SYSTEM
 * =======================================================
 * 
 * Enterprise-grade Modal component with:
 * - Multiple sizes and variants
 * - Animation and transitions
 * - Accessibility compliance (WCAG)
 * - Portal rendering
 * - Backdrop and escape handling
 * - Creator Economy theming
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { useEffect, useRef, ReactNode, useCallback } from 'react';
import { createPortal } from 'react-dom';
import styled, { css, keyframes } from 'styled-components';

// Animation keyframes
const backdropFadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const backdropFadeOut = keyframes`
  from { opacity: 1; }
  to { opacity: 0; }
`;

const modalSlideIn = keyframes`
  from { 
    opacity: 0; 
    transform: translate(-50%, -50%) scale(0.9); 
  }
  to { 
    opacity: 1; 
    transform: translate(-50%, -50%) scale(1); 
  }
`;

const modalSlideOut = keyframes`
  from { 
    opacity: 1; 
    transform: translate(-50%, -50%) scale(1); 
  }
  to { 
    opacity: 0; 
    transform: translate(-50%, -50%) scale(0.9); 
  }
`;

const modalSlideUp = keyframes`
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
`;

const modalSlideDown = keyframes`
  from { transform: translateY(0); }
  to { transform: translateY(100%); }
`;

// Types
export type ModalSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
export type ModalVariant = 'default' | 'creator-gradient' | 'creator-dark' | 'glass' | 'minimal';
export type ModalAnimation = 'fade' | 'slide' | 'zoom' | 'slide-up';

export interface ModalProps {
  /** Whether modal is open */
  open: boolean;
  
  /** Callback when modal should close */
  onClose: () => void;
  
  /** Modal content */
  children: ReactNode;
  
  /** Modal title */
  title?: string;
  
  /** Modal size */
  size?: ModalSize;
  
  /** Modal variant */
  variant?: ModalVariant;
  
  /** Animation type */
  animation?: ModalAnimation;
  
  /** Close on backdrop click */
  closeOnBackdrop?: boolean;
  
  /** Close on escape key */
  closeOnEscape?: boolean;
  
  /** Show close button */
  showCloseButton?: boolean;
  
  /** Custom backdrop */
  backdrop?: 'default' | 'blur' | 'dark' | 'none';
  
  /** Disable body scroll when open */
  disableBodyScroll?: boolean;
  
  /** Custom z-index */
  zIndex?: number;
  
  /** Portal container */
  container?: HTMLElement;
  
  /** Modal header content */
  header?: ReactNode;
  
  /** Modal footer content */
  footer?: ReactNode;
  
  /** Custom close icon */
  closeIcon?: ReactNode;
  
  /** Callback when modal opens */
  onOpen?: () => void;
  
  /** Callback when animation completes */
  onAnimationComplete?: () => void;
  
  /** Loading state */
  loading?: boolean;
  
  /** Prevent modal from closing */
  preventClose?: boolean;
}

// Styled components
const Backdrop = styled.div<Pick<ModalProps, 'backdrop' | 'zIndex' | 'open'>>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: ${props => props.zIndex || 1000};
  display: flex;
  align-items: center;
  justify-content: center;
  
  ${props => {
    switch (props.backdrop) {
      case 'blur':
        return css`
          background-color: rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(8px);
        `;
      case 'dark':
        return css`
          background-color: rgba(0, 0, 0, 0.8);
        `;
      case 'none':
        return css`
          background-color: transparent;
        `;
      default:
        return css`
          background-color: rgba(0, 0, 0, 0.5);
        `;
    }
  }}
  
  animation: ${props => props.open ? backdropFadeIn : backdropFadeOut} 0.2s ease-in-out;
`;

const ModalContainer = styled.div<Pick<ModalProps, 'size' | 'animation' | 'open'>>`
  position: relative;
  outline: none;
  max-height: 90vh;
  overflow-y: auto;
  
  ${props => {
    switch (props.size) {
      case 'xs':
        return css`
          width: 90%;
          max-width: 400px;
        `;
      case 'sm':
        return css`
          width: 90%;
          max-width: 500px;
        `;
      case 'lg':
        return css`
          width: 90%;
          max-width: 800px;
        `;
      case 'xl':
        return css`
          width: 90%;
          max-width: 1200px;
        `;
      case 'full':
        return css`
          width: 95%;
          height: 95%;
          max-width: none;
          max-height: none;
        `;
      default: // md
        return css`
          width: 90%;
          max-width: 600px;
        `;
    }
  }}
  
  ${props => {
    const isOpen = props.open;
    switch (props.animation) {
      case 'slide':
        return css`
          animation: ${isOpen ? modalSlideIn : modalSlideOut} 0.3s ease-in-out;
        `;
      case 'zoom':
        return css`
          animation: ${isOpen ? modalSlideIn : modalSlideOut} 0.2s ease-in-out;
        `;
      case 'slide-up':
        return css`
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          width: 100%;
          max-width: none;
          border-radius: 1rem 1rem 0 0;
          animation: ${isOpen ? modalSlideUp : modalSlideDown} 0.3s ease-in-out;
        `;
      default: // fade
        return css`
          animation: ${isOpen ? modalSlideIn : modalSlideOut} 0.2s ease-in-out;
        `;
    }
  }}
`;

const ModalContent = styled.div<Pick<ModalProps, 'variant'>>`
  position: relative;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  ${props => {
    switch (props.variant) {
      case 'creator-gradient':
        return css`
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        `;
      case 'creator-dark':
        return css`
          background-color: #1a1a1a;
          color: white;
          border: 1px solid #333;
        `;
      case 'glass':
        return css`
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
        `;
      case 'minimal':
        return css`
          background-color: white;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        `;
      default:
        return css`
          background-color: white;
          color: #374151;
        `;
    }
  }}
`;

const ModalHeader = styled.div<{ hasCloseButton?: boolean }>`
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 4rem;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.25;
`;

const ModalBody = styled.div`
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
`;

const ModalFooter = styled.div`
  padding: 1.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  border: none;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  z-index: 10;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.2);
    transform: scale(1.1);
  }
  
  &:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }
  
  svg {
    width: 1.25rem;
    height: 1.25rem;
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
`;

const LoadingSpinner = styled.div`
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Hook for managing body scroll
const useBodyScroll = (disabled: boolean) => {
  useEffect(() => {
    if (disabled) {
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      
      return () => {
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [disabled]);
};

// Hook for escape key handling
const useEscapeKey = (onEscape: () => void, enabled: boolean) => {
  useEffect(() => {
    if (!enabled) return;
    
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onEscape();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onEscape, enabled]);
};

// Default close icon
const DefaultCloseIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

// Modal component
export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  children,
  title,
  size = 'md',
  variant = 'default',
  animation = 'fade',
  closeOnBackdrop = true,
  closeOnEscape = true,
  showCloseButton = true,
  backdrop = 'default',
  disableBodyScroll = true,
  zIndex = 1000,
  container,
  header,
  footer,
  closeIcon,
  onOpen,
  onAnimationComplete,
  loading = false,
  preventClose = false
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Manage body scroll
  useBodyScroll(open && disableBodyScroll);

  // Handle escape key
  useEscapeKey(() => {
    if (!preventClose) {
      onClose();
    }
  }, open && closeOnEscape);

  // Focus management
  useEffect(() => {
    if (open) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
      onOpen?.();
    } else {
      previousActiveElement.current?.focus();
    }
  }, [open, onOpen]);

  // Handle backdrop click
  const handleBackdropClick = useCallback((event: React.MouseEvent) => {
    if (event.target === event.currentTarget && closeOnBackdrop && !preventClose) {
      onClose();
    }
  }, [closeOnBackdrop, onClose, preventClose]);

  // Handle close button click
  const handleCloseClick = useCallback(() => {
    if (!preventClose) {
      onClose();
    }
  }, [onClose, preventClose]);

  // Animation complete handler
  useEffect(() => {
    if (open) {
      const timer = setTimeout(() => {
        onAnimationComplete?.();
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [open, onAnimationComplete]);

  if (!open) return null;

  const modalContent = (
    <Backdrop
      backdrop={backdrop}
      zIndex={zIndex}
      open={open}
      onClick={handleBackdropClick}
      data-testid="modal-backdrop"
    >
      <ModalContainer
        ref={modalRef}
        size={size}
        animation={animation}
        open={open}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "modal-title" : undefined}
        data-testid="modal-container"
      >
        <ModalContent variant={variant}>
          {/* Loading overlay */}
          {loading && (
            <LoadingOverlay data-testid="modal-loading">
              <LoadingSpinner />
            </LoadingOverlay>
          )}
          
          {/* Close button */}
          {showCloseButton && !preventClose && (
            <CloseButton
              onClick={handleCloseClick}
              aria-label="Close modal"
              data-testid="modal-close"
            >
              {closeIcon || <DefaultCloseIcon />}
            </CloseButton>
          )}
          
          {/* Header */}
          {(title || header) && (
            <ModalHeader hasCloseButton={showCloseButton} data-testid="modal-header">
              {header || (
                <ModalTitle id="modal-title">
                  {title}
                </ModalTitle>
              )}
            </ModalHeader>
          )}
          
          {/* Body */}
          <ModalBody data-testid="modal-body">
            {children}
          </ModalBody>
          
          {/* Footer */}
          {footer && (
            <ModalFooter data-testid="modal-footer">
              {footer}
            </ModalFooter>
          )}
        </ModalContent>
      </ModalContainer>
    </Backdrop>
  );

  return createPortal(
    modalContent,
    container || document.body
  );
};

// Confirm Modal component
export interface ConfirmModalProps {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'default' | 'danger' | 'warning';
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  open,
  onConfirm,
  onCancel,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'default'
}) => {
  return (
    <Modal
      open={open}
      onClose={onCancel}
      title={title}
      size="sm"
      footer={
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={onCancel}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              background: 'white',
              cursor: 'pointer'
            }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '0.375rem',
              background: variant === 'danger' ? '#ef4444' : '#3b82f6',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            {confirmText}
          </button>
        </div>
      }
    >
      <p>{message}</p>
    </Modal>
  );
};

// Export types and components
export type { ModalProps, ModalSize, ModalVariant, ModalAnimation, ConfirmModalProps };
export { Backdrop, ModalContainer, ModalContent, ModalHeader, ModalBody, ModalFooter };

export default Modal;