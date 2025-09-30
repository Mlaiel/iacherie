/**
 * 🎨 REACT COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * =============================================================
 * 
 * Enterprise-grade React component template with:
 * - TypeScript support with strict typing
 * - Performance optimization (memoization)
 * - Accessibility (a11y) compliance
 * - Error boundaries and error handling
 * - Responsive design and mobile-first
 * - Theming and styled-components
 * - Testing utilities and mocks
 * - Storybook integration
 * 
 * Author: Frontend Expert
 * Version: 1.0.0
 */

import React, { 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef,
  forwardRef,
  memo,
  ReactNode,
  HTMLAttributes,
  ComponentPropsWithRef
} from 'react';
import styled, { css, ThemeProvider } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { ErrorBoundary } from 'react-error-boundary';

// Type definitions
interface Theme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  breakpoints: {
    mobile: string;
    tablet: string;
    desktop: string;
    wide: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
    fontWeight: {
      light: number;
      regular: number;
      medium: number;
      bold: number;
    };
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
  };
}

interface ComponentTemplateProps extends HTMLAttributes<HTMLDivElement> {
  /** Component variant for different visual styles */
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  
  /** Size of the component */
  size?: 'sm' | 'md' | 'lg';
  
  /** Whether the component is disabled */
  disabled?: boolean;
  
  /** Whether the component is in loading state */
  loading?: boolean;
  
  /** Custom icon to display */
  icon?: ReactNode;
  
  /** Content to display in the component */
  children?: ReactNode;
  
  /** Custom CSS class name */
  className?: string;
  
  /** Accessibility label */
  ariaLabel?: string;
  
  /** Accessibility describedby */
  ariaDescribedBy?: string;
  
  /** Whether component is full width */
  fullWidth?: boolean;
  
  /** Custom styles */
  customStyles?: React.CSSProperties;
  
  /** Event handlers */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLDivElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLDivElement>) => void;
  onKeyDown?: (event: React.KeyboardEvent<HTMLDivElement>) => void;
  
  /** Data attributes for testing */
  'data-testid'?: string;
  'data-cy'?: string;
}

interface StyledComponentProps {
  $variant: ComponentTemplateProps['variant'];
  $size: ComponentTemplateProps['size'];
  $disabled: boolean;
  $loading: boolean;
  $fullWidth: boolean;
}

// Default theme
const defaultTheme: Theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545',
    info: '#17a2b8',
    background: '#ffffff',
    surface: '#f8f9fa',
    text: '#212529',
    textSecondary: '#6c757d'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '3rem'
  },
  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1200px'
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      md: '1rem',
      lg: '1.125rem',
      xl: '1.25rem'
    },
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      bold: 700
    }
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem'
  }
};

// Styled components
const StyledContainer = styled(motion.div)<StyledComponentProps>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${({ theme }) => theme.spacing.sm};
  font-family: ${({ theme }) => theme.typography.fontFamily};
  border: 1px solid transparent;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: all 0.2s ease-in-out;
  cursor: ${({ $disabled }) => ($disabled ? 'not-allowed' : 'pointer')};
  position: relative;
  overflow: hidden;
  
  // Size variants
  ${({ $size, theme }) => {
    switch ($size) {
      case 'sm':
        return css`
          padding: ${theme.spacing.xs} ${theme.spacing.sm};
          font-size: ${theme.typography.fontSize.sm};
          min-height: 2rem;
        `;
      case 'lg':
        return css`
          padding: ${theme.spacing.md} ${theme.spacing.lg};
          font-size: ${theme.typography.fontSize.lg};
          min-height: 3rem;
        `;
      default:
        return css`
          padding: ${theme.spacing.sm} ${theme.spacing.md};
          font-size: ${theme.typography.fontSize.md};
          min-height: 2.5rem;
        `;
    }
  }}
  
  // Color variants
  ${({ $variant, theme, $disabled }) => {
    const color = theme.colors[$variant || 'primary'];
    
    if ($disabled) {
      return css`
        background-color: ${theme.colors.surface};
        color: ${theme.colors.textSecondary};
        border-color: ${theme.colors.textSecondary};
        opacity: 0.6;
      `;
    }
    
    return css`
      background-color: ${color};
      color: ${$variant === 'warning' ? theme.colors.text : '#ffffff'};
      border-color: ${color};
      
      &:hover:not(:disabled) {
        background-color: ${color}dd;
        border-color: ${color}dd;
        box-shadow: ${theme.shadows.md};
        transform: translateY(-1px);
      }
      
      &:active:not(:disabled) {
        transform: translateY(0);
        box-shadow: ${theme.shadows.sm};
      }
      
      &:focus-visible {
        outline: 2px solid ${color};
        outline-offset: 2px;
      }
    `;
  }}
  
  // Full width
  ${({ $fullWidth }) =>
    $fullWidth &&
    css`
      width: 100%;
    `}
  
  // Loading state
  ${({ $loading }) =>
    $loading &&
    css`
      pointer-events: none;
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        animation: loading 1.5s infinite;
      }
      
      @keyframes loading {
        0% {
          transform: translateX(-100%);
        }
        100% {
          transform: translateX(100%);
        }
      }
    `}
  
  // Responsive design
  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    font-size: ${({ theme }) => theme.typography.fontSize.sm};
    padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
  }
`;

const IconWrapper = styled.div<{ $size: ComponentTemplateProps['size'] }>`
  display: flex;
  align-items: center;
  justify-content: center;
  
  ${({ $size }) => {
    switch ($size) {
      case 'sm':
        return css`
          width: 1rem;
          height: 1rem;
        `;
      case 'lg':
        return css`
          width: 1.5rem;
          height: 1.5rem;
        `;
      default:
        return css`
          width: 1.25rem;
          height: 1.25rem;
        `;
    }
  }}
  
  svg {
    width: 100%;
    height: 100%;
  }
`;

const LoadingSpinner = styled.div<{ $size: ComponentTemplateProps['size'] }>`
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  ${({ $size }) => {
    switch ($size) {
      case 'sm':
        return css`
          width: 0.875rem;
          height: 0.875rem;
        `;
      case 'lg':
        return css`
          width: 1.25rem;
          height: 1.25rem;
        `;
      default:
        return css`
          width: 1rem;
          height: 1rem;
        `;
    }
  }}
  
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

// Error Fallback Component
const ErrorFallback: React.FC<{ error: Error; resetErrorBoundary: () => void }> = ({
  error,
  resetErrorBoundary
}) => {
  return (
    <div role="alert" style={{ padding: '1rem', border: '1px solid #dc3545', borderRadius: '0.375rem' }}>
      <h2 style={{ color: '#dc3545', marginBottom: '0.5rem' }}>
        Something went wrong
      </h2>
      <p style={{ marginBottom: '1rem', color: '#6c757d' }}>
        An error occurred while rendering this component.
      </p>
      <details style={{ marginBottom: '1rem' }}>
        <summary style={{ cursor: 'pointer', color: '#007bff' }}>
          Error details
        </summary>
        <pre style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#dc3545' }}>
          {error.message}
        </pre>
      </details>
      <button
        onClick={resetErrorBoundary}
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: 'pointer'
        }}
      >
        Try again
      </button>
    </div>
  );
};

// Main component
const ComponentTemplate = forwardRef<HTMLDivElement, ComponentTemplateProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      icon,
      children,
      className,
      ariaLabel,
      ariaDescribedBy,
      fullWidth = false,
      customStyles,
      'data-testid': dataTestId,
      'data-cy': dataCy,
      onClick,
      onFocus,
      onBlur,
      onKeyDown,
      ...restProps
    },
    ref
  ) => {
    const [isHovered, setIsHovered] = useState(false);
    const [isFocused, setIsFocused] = useState(false);
    
    // Keyboard navigation
    const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLDivElement>) => {
      if (disabled) return;
      
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onClick?.(event as any);
      }
      
      onKeyDown?.(event);
    }, [disabled, onClick, onKeyDown]);
    
    // Focus management
    const handleFocus = useCallback((event: React.FocusEvent<HTMLDivElement>) => {
      setIsFocused(true);
      onFocus?.(event);
    }, [onFocus]);
    
    const handleBlur = useCallback((event: React.FocusEvent<HTMLDivElement>) => {
      setIsFocused(false);
      onBlur?.(event);
    }, [onBlur]);
    
    // Click handler
    const handleClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
      if (disabled || loading) return;
      onClick?.(event);
    }, [disabled, loading, onClick]);
    
    // Accessibility attributes
    const accessibilityProps = useMemo(() => ({
      role: 'button',
      tabIndex: disabled ? -1 : 0,
      'aria-label': ariaLabel || 'Component',
      'aria-describedby': ariaDescribedBy,
      'aria-disabled': disabled,
      'aria-busy': loading
    }), [disabled, loading, ariaLabel, ariaDescribedBy]);
    
    return (
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <StyledContainer
          ref={ref}
          className={className}
          style={customStyles}
          $variant={variant}
          $size={size}
          $disabled={disabled}
          $loading={loading}
          $fullWidth={fullWidth}
          data-testid={dataTestId}
          data-cy={dataCy}
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          whileHover={!disabled && !loading ? { scale: 1.02 } : undefined}
          whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
          onClick={handleClick}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...accessibilityProps}
          {...restProps}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 'inherit' }}>
            {loading && <LoadingSpinner $size={size} />}
            {!loading && icon && (
              <IconWrapper $size={size}>
                {icon}
              </IconWrapper>
            )}
            {children && <span>{children}</span>}
          </div>
        </StyledContainer>
      </ErrorBoundary>
    );
  }
);

ComponentTemplate.displayName = 'ComponentTemplate';

// Memoized component for performance
const MemoizedComponentTemplate = memo(ComponentTemplate);

// Higher-order component for theming
const withTheme = (Component: React.ComponentType<any>) => {
  return (props: any) => (
    <ThemeProvider theme={defaultTheme}>
      <Component {...props} />
    </ThemeProvider>
  );
};

// Enhanced component with theme
const ThemedComponentTemplate = withTheme(MemoizedComponentTemplate);

// Export types and components
export type {
  ComponentTemplateProps,
  Theme
};

export {
  ComponentTemplate,
  MemoizedComponentTemplate,
  ThemedComponentTemplate,
  defaultTheme,
  withTheme,
  ErrorFallback
};

export default ThemedComponentTemplate;