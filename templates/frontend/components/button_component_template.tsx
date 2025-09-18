/**
 * 🔘 BUTTON COMPONENT TEMPLATE - ENTERPRISE UI COMPONENT
 * ======================================================
 * 
 * Enterprise-grade Button component with:
 * - Multiple variants and sizes
 * - Loading and disabled states
 * - Accessibility compliance (WCAG)
 * - Animation and transitions
 * - Icon support
 * - Creator Economy theming
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { forwardRef, ButtonHTMLAttributes, ReactNode, useState } from 'react';
import styled, { css, keyframes } from 'styled-components';

// Animation keyframes
const rippleEffect = keyframes`
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
`;

const loadingSpinner = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

// Types
export type ButtonVariant = 
  | 'primary' 
  | 'secondary' 
  | 'success' 
  | 'danger' 
  | 'warning' 
  | 'info' 
  | 'light' 
  | 'dark' 
  | 'outline' 
  | 'ghost' 
  | 'link'
  | 'creator-gradient'
  | 'creator-neon';

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'size'> {
  /** Button variant */
  variant?: ButtonVariant;
  
  /** Button size */
  size?: ButtonSize;
  
  /** Loading state */
  loading?: boolean;
  
  /** Disabled state */
  disabled?: boolean;
  
  /** Full width button */
  fullWidth?: boolean;
  
  /** Icon before text */
  startIcon?: ReactNode;
  
  /** Icon after text */
  endIcon?: ReactNode;
  
  /** Button content */
  children?: ReactNode;
  
  /** Enable ripple effect on click */
  enableRipple?: boolean;
  
  /** Enable pulse animation */
  enablePulse?: boolean;
  
  /** Custom loading text */
  loadingText?: string;
  
  /** Button shape */
  shape?: 'rounded' | 'square' | 'circle';
  
  /** Elevation/shadow level */
  elevation?: 0 | 1 | 2 | 3 | 4;
}

// Styled components
const StyledButton = styled.button<ButtonProps>`
  /* Base styles */
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: ${props => {
    switch (props.shape) {
      case 'square': return '0';
      case 'circle': return '50%';
      default: return '0.375rem';
    }
  }};
  font-family: inherit;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  overflow: hidden;
  outline: none;
  
  /* Size variants */
  ${props => {
    switch (props.size) {
      case 'xs':
        return css`
          padding: 0.25rem 0.5rem;
          font-size: 0.75rem;
          line-height: 1.25;
        `;
      case 'sm':
        return css`
          padding: 0.375rem 0.75rem;
          font-size: 0.875rem;
          line-height: 1.25;
        `;
      case 'lg':
        return css`
          padding: 0.75rem 1.5rem;
          font-size: 1.125rem;
          line-height: 1.25;
        `;
      case 'xl':
        return css`
          padding: 1rem 2rem;
          font-size: 1.25rem;
          line-height: 1.25;
        `;
      default: // md
        return css`
          padding: 0.5rem 1rem;
          font-size: 1rem;
          line-height: 1.25;
        `;
    }
  }}
  
  /* Full width */
  ${props => props.fullWidth && css`
    width: 100%;
  `}
  
  /* Elevation/shadow */
  ${props => {
    const shadows = {
      0: 'none',
      1: '0 1px 2px rgba(0, 0, 0, 0.05)',
      2: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
      3: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
      4: '0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)'
    };
    return css`box-shadow: ${shadows[props.elevation || 1]};`;
  }}
  
  /* Variant styles */
  ${props => {
    switch (props.variant) {
      case 'primary':
        return css`
          background-color: #007bff;
          color: white;
          &:hover:not(:disabled) {
            background-color: #0056b3;
            transform: translateY(-1px);
          }
          &:active {
            transform: translateY(0);
            background-color: #004085;
          }
        `;
      case 'secondary':
        return css`
          background-color: #6c757d;
          color: white;
          &:hover:not(:disabled) {
            background-color: #545b62;
            transform: translateY(-1px);
          }
        `;
      case 'success':
        return css`
          background-color: #28a745;
          color: white;
          &:hover:not(:disabled) {
            background-color: #1e7e34;
            transform: translateY(-1px);
          }
        `;
      case 'danger':
        return css`
          background-color: #dc3545;
          color: white;
          &:hover:not(:disabled) {
            background-color: #c82333;
            transform: translateY(-1px);
          }
        `;
      case 'warning':
        return css`
          background-color: #ffc107;
          color: #212529;
          &:hover:not(:disabled) {
            background-color: #e0a800;
            transform: translateY(-1px);
          }
        `;
      case 'info':
        return css`
          background-color: #17a2b8;
          color: white;
          &:hover:not(:disabled) {
            background-color: #138496;
            transform: translateY(-1px);
          }
        `;
      case 'light':
        return css`
          background-color: #f8f9fa;
          color: #212529;
          border: 1px solid #dee2e6;
          &:hover:not(:disabled) {
            background-color: #e2e6ea;
            transform: translateY(-1px);
          }
        `;
      case 'dark':
        return css`
          background-color: #343a40;
          color: white;
          &:hover:not(:disabled) {
            background-color: #23272b;
            transform: translateY(-1px);
          }
        `;
      case 'outline':
        return css`
          background-color: transparent;
          color: #007bff;
          border: 2px solid #007bff;
          &:hover:not(:disabled) {
            background-color: #007bff;
            color: white;
            transform: translateY(-1px);
          }
        `;
      case 'ghost':
        return css`
          background-color: transparent;
          color: #007bff;
          &:hover:not(:disabled) {
            background-color: rgba(0, 123, 255, 0.1);
            transform: translateY(-1px);
          }
        `;
      case 'link':
        return css`
          background-color: transparent;
          color: #007bff;
          text-decoration: underline;
          padding: 0;
          &:hover:not(:disabled) {
            color: #0056b3;
            text-decoration: none;
          }
        `;
      case 'creator-gradient':
        return css`
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          &:hover:not(:disabled) {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            transform: translateY(-2px) scale(1.02);
          }
        `;
      case 'creator-neon':
        return css`
          background-color: #000;
          color: #00ff88;
          border: 2px solid #00ff88;
          box-shadow: 0 0 10px #00ff88;
          &:hover:not(:disabled) {
            background-color: #00ff88;
            color: #000;
            box-shadow: 0 0 20px #00ff88, 0 0 40px #00ff88;
            transform: translateY(-2px);
          }
        `;
      default:
        return css`
          background-color: #007bff;
          color: white;
          &:hover:not(:disabled) {
            background-color: #0056b3;
            transform: translateY(-1px);
          }
        `;
    }
  }}
  
  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }
  
  /* Loading state */
  ${props => props.loading && css`
    cursor: wait;
    pointer-events: none;
  `}
  
  /* Pulse animation */
  ${props => props.enablePulse && css`
    animation: ${pulse} 2s infinite;
  `}
  
  /* Focus styles */
  &:focus-visible {
    outline: 2px solid #007bff;
    outline-offset: 2px;
  }
  
  /* Ripple container */
  .ripple {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.6);
    animation: ${rippleEffect} 600ms linear;
    pointer-events: none;
  }
`;

const LoadingSpinner = styled.div`
  width: 1em;
  height: 1em;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: ${loadingSpinner} 1s linear infinite;
`;

// Button component
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  startIcon,
  endIcon,
  children,
  enableRipple = true,
  enablePulse = false,
  loadingText,
  shape = 'rounded',
  elevation = 1,
  onClick,
  ...props
}, ref) => {
  const [ripples, setRipples] = useState<Array<{ id: number; x: number; y: number; size: number }>>([]);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (loading || disabled) return;

    // Create ripple effect
    if (enableRipple) {
      const button = event.currentTarget;
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = event.clientX - rect.left - size / 2;
      const y = event.clientY - rect.top - size / 2;
      
      const newRipple = {
        id: Date.now(),
        x,
        y,
        size
      };
      
      setRipples(prev => [...prev, newRipple]);
      
      // Remove ripple after animation
      setTimeout(() => {
        setRipples(prev => prev.filter(r => r.id !== newRipple.id));
      }, 600);
    }

    onClick?.(event);
  };

  return (
    <StyledButton
      ref={ref}
      variant={variant}
      size={size}
      loading={loading}
      disabled={disabled || loading}
      fullWidth={fullWidth}
      enablePulse={enablePulse}
      shape={shape}
      elevation={elevation}
      onClick={handleClick}
      aria-disabled={disabled || loading}
      aria-busy={loading}
      data-testid="button"
      {...props}
    >
      {/* Loading spinner */}
      {loading && <LoadingSpinner data-testid="loading-spinner" />}
      
      {/* Start icon */}
      {!loading && startIcon && (
        <span className="button-start-icon" data-testid="start-icon">
          {startIcon}
        </span>
      )}
      
      {/* Button content */}
      {loading && loadingText ? loadingText : children}
      
      {/* End icon */}
      {!loading && endIcon && (
        <span className="button-end-icon" data-testid="end-icon">
          {endIcon}
        </span>
      )}
      
      {/* Ripple effects */}
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          className="ripple"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size
          }}
        />
      ))}
    </StyledButton>
  );
});

Button.displayName = 'Button';

// Button Group component
export interface ButtonGroupProps {
  children: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  spacing?: number;
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const StyledButtonGroup = styled.div<ButtonGroupProps>`
  display: flex;
  flex-direction: ${props => props.orientation === 'vertical' ? 'column' : 'row'};
  gap: ${props => props.spacing || 0}px;
  
  ${props => props.spacing === 0 && css`
    ${StyledButton} {
      border-radius: 0;
      
      &:first-child {
        border-top-left-radius: 0.375rem;
        ${props.orientation === 'vertical' 
          ? 'border-top-right-radius: 0.375rem;' 
          : 'border-bottom-left-radius: 0.375rem;'
        }
      }
      
      &:last-child {
        border-bottom-right-radius: 0.375rem;
        ${props.orientation === 'vertical' 
          ? 'border-bottom-left-radius: 0.375rem;' 
          : 'border-top-right-radius: 0.375rem;'
        }
      }
      
      &:not(:last-child) {
        ${props.orientation === 'vertical' ? 'border-bottom' : 'border-right'}: 1px solid rgba(255,255,255,0.2);
      }
    }
  `}
`;

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  orientation = 'horizontal',
  spacing = 0,
  variant,
  size,
  ...props
}) => {
  // Clone children and apply group props
  const clonedChildren = React.Children.map(children, child => {
    if (React.isValidElement(child) && child.type === Button) {
      return React.cloneElement(child, {
        variant: child.props.variant || variant,
        size: child.props.size || size,
        ...child.props
      });
    }
    return child;
  });

  return (
    <StyledButtonGroup
      orientation={orientation}
      spacing={spacing}
      role="group"
      data-testid="button-group"
      {...props}
    >
      {clonedChildren}
    </StyledButtonGroup>
  );
};

// Export types and components
export type { ButtonProps, ButtonGroupProps, ButtonVariant, ButtonSize };
export { StyledButton, LoadingSpinner };

export default Button;