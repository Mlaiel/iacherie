/**
 * 📝 INPUT COMPONENT TEMPLATE - ENTERPRISE FORM INPUT
 * ===================================================
 * 
 * Enterprise-grade Input component with:
 * - Multiple input types and variants
 * - Validation and error handling
 * - Accessibility compliance (WCAG)
 * - Animation and transitions
 * - Icon support and labels
 * - Creator Economy theming
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React, { forwardRef, InputHTMLAttributes, ReactNode, useState, useEffect } from 'react';
import styled, { css, keyframes } from 'styled-components';

// Animation keyframes
const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
`;

const shake = keyframes`
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
`;

// Types
export type InputVariant = 'default' | 'filled' | 'outlined' | 'underlined' | 'creator-glow';
export type InputSize = 'sm' | 'md' | 'lg';
export type InputType = 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'textarea';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Input variant */
  variant?: InputVariant;
  
  /** Input size */
  size?: InputSize;
  
  /** Input type */
  inputType?: InputType;
  
  /** Label text */
  label?: string;
  
  /** Helper text */
  helperText?: string;
  
  /** Error message */
  error?: string;
  
  /** Success message */
  success?: string;
  
  /** Loading state */
  loading?: boolean;
  
  /** Icon before input */
  startIcon?: ReactNode;
  
  /** Icon after input */
  endIcon?: ReactNode;
  
  /** Full width input */
  fullWidth?: boolean;
  
  /** Floating label */
  floatingLabel?: boolean;
  
  /** Character counter */
  showCounter?: boolean;
  
  /** Maximum characters */
  maxLength?: number;
  
  /** Debounce delay for onChange */
  debounceMs?: number;
  
  /** Custom validation function */
  validate?: (value: string) => string | null;
  
  /** Rows for textarea */
  rows?: number;
  
  /** Auto-resize textarea */
  autoResize?: boolean;
}

// Styled components
const InputContainer = styled.div<Pick<InputProps, 'fullWidth'>>`
  position: relative;
  display: ${props => props.fullWidth ? 'block' : 'inline-block'};
  width: ${props => props.fullWidth ? '100%' : 'auto'};
  margin-bottom: 1rem;
`;

const InputWrapper = styled.div<Pick<InputProps, 'variant' | 'size' | 'loading' | 'error' | 'success'>>`
  position: relative;
  display: flex;
  align-items: center;
  
  ${props => {
    switch (props.size) {
      case 'sm':
        return css`
          min-height: 2rem;
          font-size: 0.875rem;
        `;
      case 'lg':
        return css`
          min-height: 3rem;
          font-size: 1.125rem;
        `;
      default: // md
        return css`
          min-height: 2.5rem;
          font-size: 1rem;
        `;
    }
  }}
  
  ${props => props.loading && css`
    pointer-events: none;
    opacity: 0.7;
  `}
  
  ${props => props.error && css`
    animation: ${shake} 0.5s ease-in-out;
  `}
`;

const StyledInput = styled.input<InputProps>`
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  transition: all 0.2s ease-in-out;
  
  ${props => {
    const padding = {
      sm: '0.5rem',
      md: '0.75rem',
      lg: '1rem'
    }[props.size || 'md'];
    
    return css`
      padding: ${padding};
    `;
  }}
  
  ${props => props.startIcon && css`
    padding-left: 2.5rem;
  `}
  
  ${props => props.endIcon && css`
    padding-right: 2.5rem;
  `}
  
  &::placeholder {
    color: #9ca3af;
    opacity: 1;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const StyledTextarea = styled.textarea<InputProps>`
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  resize: ${props => props.autoResize ? 'none' : 'vertical'};
  transition: all 0.2s ease-in-out;
  min-height: ${props => props.rows ? `${props.rows * 1.5}em` : '4em'};
  
  ${props => {
    const padding = {
      sm: '0.5rem',
      md: '0.75rem',
      lg: '1rem'
    }[props.size || 'md'];
    
    return css`
      padding: ${padding};
    `;
  }}
  
  &::placeholder {
    color: #9ca3af;
    opacity: 1;
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const InputField = styled.div<Pick<InputProps, 'variant' | 'error' | 'success' | 'disabled'>>`
  position: relative;
  display: flex;
  align-items: center;
  border-radius: 0.375rem;
  transition: all 0.2s ease-in-out;
  
  ${props => {
    const borderColor = props.error ? '#ef4444' : props.success ? '#10b981' : '#d1d5db';
    const focusColor = props.error ? '#ef4444' : props.success ? '#10b981' : '#3b82f6';
    
    switch (props.variant) {
      case 'filled':
        return css`
          background-color: #f3f4f6;
          border: 2px solid transparent;
          
          &:focus-within {
            background-color: #ffffff;
            border-color: ${focusColor};
            box-shadow: 0 0 0 3px ${focusColor}20;
          }
        `;
      
      case 'outlined':
        return css`
          background-color: #ffffff;
          border: 2px solid ${borderColor};
          
          &:focus-within {
            border-color: ${focusColor};
            box-shadow: 0 0 0 3px ${focusColor}20;
          }
        `;
      
      case 'underlined':
        return css`
          background-color: transparent;
          border: none;
          border-bottom: 2px solid ${borderColor};
          border-radius: 0;
          
          &:focus-within {
            border-bottom-color: ${focusColor};
            box-shadow: 0 2px 0 0 ${focusColor};
          }
        `;
      
      case 'creator-glow':
        return css`
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: 2px solid transparent;
          padding: 2px;
          
          &::before {
            content: '';
            position: absolute;
            inset: 0;
            background: #ffffff;
            border-radius: inherit;
            z-index: -1;
          }
          
          &:focus-within {
            box-shadow: 0 0 20px #667eea;
          }
        `;
      
      default: // default
        return css`
          background-color: #ffffff;
          border: 1px solid ${borderColor};
          
          &:focus-within {
            border-color: ${focusColor};
            box-shadow: 0 0 0 3px ${focusColor}20;
          }
        `;
    }
  }}
  
  ${props => props.disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
  `}
`;

const Label = styled.label<{ floating?: boolean; focused?: boolean; hasValue?: boolean }>`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  
  ${props => props.floating && css`
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    background-color: #ffffff;
    padding: 0 0.25rem;
    pointer-events: none;
    transition: all 0.2s ease-in-out;
    z-index: 1;
    
    ${(props.focused || props.hasValue) && css`
      top: 0;
      transform: translateY(-50%);
      font-size: 0.75rem;
      color: #3b82f6;
    `}
  `}
`;

const IconWrapper = styled.div<{ position: 'start' | 'end' }>`
  position: absolute;
  ${props => props.position === 'start' ? 'left: 0.75rem;' : 'right: 0.75rem;'}
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
  z-index: 2;
`;

const HelperText = styled.div<{ type?: 'error' | 'success' | 'helper' }>`
  margin-top: 0.25rem;
  font-size: 0.75rem;
  animation: ${fadeIn} 0.2s ease-in-out;
  
  ${props => {
    switch (props.type) {
      case 'error':
        return css`color: #ef4444;`;
      case 'success':
        return css`color: #10b981;`;
      default:
        return css`color: #6b7280;`;
    }
  }}
`;

const CharacterCounter = styled.div<{ exceeded?: boolean }>`
  margin-top: 0.25rem;
  font-size: 0.75rem;
  text-align: right;
  color: ${props => props.exceeded ? '#ef4444' : '#6b7280'};
`;

const LoadingSpinner = styled.div`
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Input component
export const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputProps>(({
  variant = 'default',
  size = 'md',
  inputType = 'text',
  label,
  helperText,
  error,
  success,
  loading = false,
  startIcon,
  endIcon,
  fullWidth = false,
  floatingLabel = false,
  showCounter = false,
  maxLength,
  debounceMs = 0,
  validate,
  rows,
  autoResize = false,
  value,
  onChange,
  onBlur,
  ...props
}, ref) => {
  const [internalValue, setInternalValue] = useState(value || '');
  const [focused, setFocused] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Debounced change handler
  useEffect(() => {
    if (debounceMs > 0) {
      const timer = setTimeout(() => {
        if (validate && internalValue) {
          const errorMsg = validate(String(internalValue));
          setValidationError(errorMsg);
        }
      }, debounceMs);

      return () => clearTimeout(timer);
    }
  }, [internalValue, debounceMs, validate]);

  // Auto-resize for textarea
  useEffect(() => {
    if (autoResize && inputType === 'textarea' && ref && 'current' in ref && ref.current) {
      const textarea = ref.current as HTMLTextAreaElement;
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [internalValue, autoResize, inputType, ref]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    
    if (debounceMs === 0) {
      onChange?.(e);
      
      if (validate) {
        const errorMsg = validate(newValue);
        setValidationError(errorMsg);
      }
    }
  };

  const handleFocus = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFocused(true);
    props.onFocus?.(e);
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFocused(false);
    onBlur?.(e);
  };

  const hasValue = Boolean(internalValue || value);
  const displayError = error || validationError;
  const charCount = String(internalValue || value || '').length;
  const charExceeded = maxLength ? charCount > maxLength : false;

  const InputComponent = inputType === 'textarea' ? StyledTextarea : StyledInput;

  return (
    <InputContainer fullWidth={fullWidth} data-testid="input-container">
      {/* Non-floating label */}
      {label && !floatingLabel && (
        <Label htmlFor={props.id} data-testid="input-label">
          {label}
        </Label>
      )}
      
      <InputWrapper
        variant={variant}
        size={size}
        loading={loading}
        error={!!displayError}
        success={!!success}
      >
        <InputField
          variant={variant}
          error={!!displayError}
          success={!!success}
          disabled={props.disabled}
        >
          {/* Floating label */}
          {label && floatingLabel && (
            <Label
              floating
              focused={focused}
              hasValue={hasValue}
              htmlFor={props.id}
              data-testid="floating-label"
            >
              {label}
            </Label>
          )}
          
          {/* Start icon */}
          {startIcon && (
            <IconWrapper position="start" data-testid="start-icon">
              {startIcon}
            </IconWrapper>
          )}
          
          {/* Input/Textarea */}
          <InputComponent
            {...props}
            ref={ref as any}
            type={inputType === 'textarea' ? undefined : inputType}
            variant={variant}
            size={size}
            startIcon={startIcon}
            endIcon={endIcon || loading}
            value={internalValue || value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            rows={rows}
            autoResize={autoResize}
            maxLength={maxLength}
            aria-invalid={!!displayError}
            aria-describedby={
              [
                displayError && `${props.id}-error`,
                success && `${props.id}-success`,
                helperText && `${props.id}-helper`
              ].filter(Boolean).join(' ') || undefined
            }
            data-testid="input-field"
          />
          
          {/* End icon or loading spinner */}
          {(endIcon || loading) && (
            <IconWrapper position="end" data-testid="end-icon">
              {loading ? <LoadingSpinner /> : endIcon}
            </IconWrapper>
          )}
        </InputField>
      </InputWrapper>
      
      {/* Error message */}
      {displayError && (
        <HelperText type="error" id={`${props.id}-error`} data-testid="error-message">
          {displayError}
        </HelperText>
      )}
      
      {/* Success message */}
      {success && !displayError && (
        <HelperText type="success" id={`${props.id}-success`} data-testid="success-message">
          {success}
        </HelperText>
      )}
      
      {/* Helper text */}
      {helperText && !displayError && !success && (
        <HelperText type="helper" id={`${props.id}-helper`} data-testid="helper-text">
          {helperText}
        </HelperText>
      )}
      
      {/* Character counter */}
      {showCounter && maxLength && (
        <CharacterCounter exceeded={charExceeded} data-testid="character-counter">
          {charCount}/{maxLength}
        </CharacterCounter>
      )}
    </InputContainer>
  );
});

Input.displayName = 'Input';

// Export types and components
export type { InputProps, InputVariant, InputSize, InputType };
export { InputContainer, InputField, StyledInput, StyledTextarea };

export default Input;