/**
 * 📝 Form Component Template - UI Component Templates
 * =================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { useState, useCallback, useRef, createContext, useContext } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ================================
// TYPES & INTERFACES
// ================================

export interface FormField {
  name: string;
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'file' | 'date' | 'time' | 'datetime-local';
  label?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  value?: any;
  defaultValue?: any;
  options?: Array<{ label: string; value: any; disabled?: boolean }>;
  validation?: ValidationRule[];
  description?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  min?: number | string;
  max?: number | string;
  step?: number;
  pattern?: string;
  multiple?: boolean;
  accept?: string;
  rows?: number;
  cols?: number;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'filled' | 'outlined' | 'minimal';
  width?: string | number;
  grid?: { xs?: number; sm?: number; md?: number; lg?: number; xl?: number };
  dependsOn?: string[];
  conditional?: (values: Record<string, any>) => boolean;
  transform?: (value: any) => any;
  formatDisplay?: (value: any) => string;
  onChange?: (value: any, field: FormField) => void;
  onBlur?: (value: any, field: FormField) => void;
  onFocus?: (field: FormField) => void;
}

export interface ValidationRule {
  type: 'required' | 'minLength' | 'maxLength' | 'min' | 'max' | 'pattern' | 'email' | 'url' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any, formValues: Record<string, any>) => boolean;
}

export interface FormProps {
  fields: FormField[];
  initialValues?: Record<string, any>;
  onSubmit?: (values: Record<string, any>, isValid: boolean) => void;
  onChange?: (values: Record<string, any>, changedField: string) => void;
  onValidationChange?: (errors: Record<string, string[]>) => void;
  layout?: 'vertical' | 'horizontal' | 'inline';
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'filled' | 'outlined' | 'minimal';
  disabled?: boolean;
  loading?: boolean;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  showErrorSummary?: boolean;
  requiredMark?: boolean;
  labelPosition?: 'top' | 'left' | 'right';
  labelWidth?: string | number;
  spacing?: 'compact' | 'normal' | 'comfortable';
  submitText?: string;
  resetText?: string;
  showSubmit?: boolean;
  showReset?: boolean;
  submitButtonProps?: any;
  resetButtonProps?: any;
  grid?: { columns?: number; gap?: string };
  className?: string;
  'data-testid'?: string;
}

export interface FormContextValue {
  values: Record<string, any>;
  errors: Record<string, string[]>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
  setValue: (name: string, value: any) => void;
  setError: (name: string, errors: string[]) => void;
  setTouched: (name: string, touched: boolean) => void;
  validateField: (name: string) => string[];
  validateForm: () => boolean;
  resetForm: () => void;
  submitForm: () => void;
}

// ================================
// ANIMATIONS
// ================================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const shake = keyframes`
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
`;

const pulse = keyframes`
  0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
  100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
`;

// ================================
// CONTEXT
// ================================

const FormContext = createContext<FormContextValue | null>(null);

export const useFormContext = () => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useFormContext must be used within a Form component');
  }
  return context;
};

// ================================
// STYLED COMPONENTS
// ================================

const FormContainer = styled.form<{
  layout: string;
  spacing: string;
  disabled?: boolean;
  grid?: { columns?: number; gap?: string };
}>`
  width: 100%;
  
  ${({ layout, spacing }) => {
    const spacingValue = {
      compact: '12px',
      normal: '16px',
      comfortable: '24px',
    }[spacing];
    
    switch (layout) {
      case 'horizontal':
        return css`
          .form-field {
            display: flex;
            align-items: flex-start;
            margin-bottom: ${spacingValue};
            
            .form-label {
              min-width: 120px;
              margin-right: 16px;
              margin-bottom: 0;
              padding-top: 8px;
            }
            
            .form-control-wrapper {
              flex: 1;
            }
          }
        `;
      case 'inline':
        return css`
          display: flex;
          flex-wrap: wrap;
          gap: ${spacingValue};
          align-items: flex-end;
          
          .form-field {
            margin-bottom: 0;
          }
        `;
      default:
        return css`
          .form-field {
            margin-bottom: ${spacingValue};
          }
        `;
    }
  }}
  
  ${({ grid }) => grid && css`
    display: grid;
    grid-template-columns: repeat(${grid.columns || 1}, 1fr);
    gap: ${grid.gap || '16px'};
    
    .form-field {
      margin-bottom: 0;
    }
  `}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    pointer-events: none;
  `}
`;

const FormField = styled.div<{
  size: string;
  hasError?: boolean;
  grid?: FormField['grid'];
}>`
  position: relative;
  
  ${({ grid }) => grid && css`
    grid-column: span ${grid.xs || 1};
    
    @media (min-width: 576px) {
      grid-column: span ${grid.sm || grid.xs || 1};
    }
    
    @media (min-width: 768px) {
      grid-column: span ${grid.md || grid.sm || grid.xs || 1};
    }
    
    @media (min-width: 992px) {
      grid-column: span ${grid.lg || grid.md || grid.sm || grid.xs || 1};
    }
    
    @media (min-width: 1200px) {
      grid-column: span ${grid.xl || grid.lg || grid.md || grid.sm || grid.xs || 1};
    }
  `}
  
  ${({ hasError }) => hasError && css`
    animation: ${shake} 0.5s ease-in-out;
  `}
`;

const FormLabel = styled.label<{
  required?: boolean;
  position: string;
  width?: string | number;
}>`
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.5;
  
  ${({ width }) => width && css`
    width: ${typeof width === 'number' ? `${width}px` : width};
  `}
  
  ${({ required }) => required && css`
    &::after {
      content: ' *';
      color: #ef4444;
    }
  `}
`;

const FormControlWrapper = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
`;

const FormControl = styled.div<{
  variant: string;
  size: string;
  hasError?: boolean;
  focused?: boolean;
  disabled?: boolean;
}>`
  position: relative;
  
  input,
  textarea,
  select {
    width: 100%;
    border: 2px solid ${({ hasError }) => hasError ? '#ef4444' : 'rgba(0, 0, 0, 0.1)'};
    border-radius: 8px;
    background: ${({ variant, disabled }) => {
      if (disabled) return '#f9fafb';
      switch (variant) {
        case 'filled': return '#f9fafb';
        case 'minimal': return 'transparent';
        default: return '#ffffff';
      }
    }};
    color: #374151;
    font-family: inherit;
    transition: all 0.2s ease;
    
    ${({ size }) => {
      switch (size) {
        case 'small':
          return css`
            padding: 8px 12px;
            font-size: 0.875rem;
          `;
        case 'large':
          return css`
            padding: 16px 20px;
            font-size: 1.125rem;
          `;
        default:
          return css`
            padding: 12px 16px;
            font-size: 1rem;
          `;
      }
    }}
    
    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    &::placeholder {
      color: rgba(107, 114, 128, 0.7);
    }
    
    ${({ variant }) => variant === 'minimal' && css`
      border: none;
      border-bottom: 2px solid rgba(0, 0, 0, 0.1);
      border-radius: 0;
      padding-left: 0;
      padding-right: 0;
      
      &:focus {
        border-bottom-color: #3b82f6;
        box-shadow: none;
      }
    `}
    
    ${({ variant }) => variant === 'outlined' && css`
      border-width: 1px;
      
      &:focus {
        border-width: 2px;
      }
    `}
  }
  
  textarea {
    resize: vertical;
    min-height: 80px;
  }
  
  ${({ focused }) => focused && css`
    animation: ${pulse} 1s infinite;
  `}
`;

const InputGroup = styled.div`
  display: flex;
  position: relative;
  
  .input-prefix,
  .input-suffix {
    display: flex;
    align-items: center;
    padding: 0 12px;
    background: #f9fafb;
    border: 2px solid rgba(0, 0, 0, 0.1);
    color: #6b7280;
    font-size: 0.875rem;
    white-space: nowrap;
  }
  
  .input-prefix {
    border-right: none;
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
  }
  
  .input-suffix {
    border-left: none;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
  }
  
  input {
    flex: 1;
    
    &:first-child:not(:last-child) {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
    
    &:last-child:not(:first-child) {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
    
    &:not(:first-child):not(:last-child) {
      border-radius: 0;
    }
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  input[type="checkbox"],
  input[type="radio"] {
    width: auto;
    margin: 0;
    cursor: pointer;
  }
  
  span {
    color: #374151;
    line-height: 1.5;
  }
  
  &:hover span {
    color: #111827;
  }
`;

const FormDescription = styled.div`
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 4px;
  line-height: 1.4;
`;

const FormError = styled.div`
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 4px;
  line-height: 1.4;
  
  ul {
    margin: 0;
    padding-left: 16px;
  }
  
  li {
    margin-bottom: 2px;
  }
`;

const FormActions = styled.div<{ layout: string }>`
  display: flex;
  gap: 12px;
  margin-top: 24px;
  
  ${({ layout }) => layout === 'horizontal' && css`
    margin-left: 136px;
  `}
`;

const FormButton = styled.button<{
  variant: 'primary' | 'secondary';
  size: string;
  loading?: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          padding: 8px 16px;
          font-size: 0.875rem;
        `;
      case 'large':
        return css`
          padding: 16px 32px;
          font-size: 1.125rem;
        `;
      default:
        return css`
          padding: 12px 24px;
          font-size: 1rem;
        `;
    }
  }}
  
  ${({ variant }) => {
    switch (variant) {
      case 'primary':
        return css`
          background: #3b82f6;
          color: white;
          
          &:hover:not(:disabled) {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          }
        `;
      case 'secondary':
        return css`
          background: #f9fafb;
          color: #374151;
          border: 1px solid #d1d5db;
          
          &:hover:not(:disabled) {
            background: #f3f4f6;
            border-color: #9ca3af;
          }
        `;
    }
  }}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  ${({ loading }) => loading && css`
    pointer-events: none;
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 16px;
      height: 16px;
      margin-top: -8px;
      margin-left: -8px;
      border: 2px solid transparent;
      border-top-color: currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `}
`;

const ErrorSummary = styled.div`
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  
  .error-title {
    color: #dc2626;
    font-weight: 600;
    margin-bottom: 8px;
  }
  
  .error-list {
    color: #dc2626;
    margin: 0;
    padding-left: 16px;
  }
  
  .error-list li {
    margin-bottom: 4px;
  }
`;

// ================================
// VALIDATION
// ================================

const validateField = (field: FormField, value: any, formValues: Record<string, any>): string[] => {
  const errors: string[] = [];
  
  if (!field.validation) return errors;
  
  for (const rule of field.validation) {
    switch (rule.type) {
      case 'required':
        if (!value || (typeof value === 'string' && !value.trim())) {
          errors.push(rule.message);
        }
        break;
        
      case 'minLength':
        if (value && value.length < rule.value) {
          errors.push(rule.message);
        }
        break;
        
      case 'maxLength':
        if (value && value.length > rule.value) {
          errors.push(rule.message);
        }
        break;
        
      case 'min':
        if (value && Number(value) < rule.value) {
          errors.push(rule.message);
        }
        break;
        
      case 'max':
        if (value && Number(value) > rule.value) {
          errors.push(rule.message);
        }
        break;
        
      case 'pattern':
        if (value && !new RegExp(rule.value).test(value)) {
          errors.push(rule.message);
        }
        break;
        
      case 'email':
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.push(rule.message);
        }
        break;
        
      case 'url':
        if (value && !/^https?:\/\/.+/.test(value)) {
          errors.push(rule.message);
        }
        break;
        
      case 'custom':
        if (rule.validator && !rule.validator(value, formValues)) {
          errors.push(rule.message);
        }
        break;
    }
  }
  
  return errors;
};

// ================================
// FIELD RENDERERS
// ================================

const renderField = (field: FormField, context: FormContextValue) => {
  const {
    values,
    errors,
    touched,
    setValue,
    setTouched,
    validateField: validateFieldContext,
  } = context;
  
  const value = values[field.name];
  const fieldErrors = errors[field.name] || [];
  const isTouched = touched[field.name];
  const hasError = fieldErrors.length > 0 && isTouched;
  
  const handleChange = (newValue: any) => {
    const transformedValue = field.transform ? field.transform(newValue) : newValue;
    setValue(field.name, transformedValue);
    field.onChange?.(transformedValue, field);
  };
  
  const handleBlur = () => {
    setTouched(field.name, true);
    validateFieldContext(field.name);
    field.onBlur?.(value, field);
  };
  
  const handleFocus = () => {
    field.onFocus?.(field);
  };
  
  const baseProps = {
    id: field.name,
    name: field.name,
    disabled: field.disabled,
    readOnly: field.readOnly,
    required: field.required,
    placeholder: field.placeholder,
    onBlur: handleBlur,
    onFocus: handleFocus,
  };
  
  const renderInput = () => {
    const inputProps = {
      ...baseProps,
      value: value || '',
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => handleChange(e.target.value),
      type: field.type,
      min: field.min,
      max: field.max,
      step: field.step,
      pattern: field.pattern,
      multiple: field.multiple,
      accept: field.accept,
    };
    
    if (field.prefix || field.suffix) {
      return (
        <InputGroup>
          {field.prefix && <div className="input-prefix">{field.prefix}</div>}
          <input {...inputProps} />
          {field.suffix && <div className="input-suffix">{field.suffix}</div>}
        </InputGroup>
      );
    }
    
    return <input {...inputProps} />;
  };
  
  const renderTextarea = () => (
    <textarea
      {...baseProps}
      value={value || ''}
      onChange={(e) => handleChange(e.target.value)}
      rows={field.rows || 4}
      cols={field.cols}
    />
  );
  
  const renderSelect = () => (
    <select
      {...baseProps}
      value={value || ''}
      onChange={(e) => handleChange(e.target.value)}
      multiple={field.multiple}
    >
      {!field.required && <option value="">Select an option...</option>}
      {field.options?.map((option) => (
        <option
          key={option.value}
          value={option.value}
          disabled={option.disabled}
        >
          {option.label}
        </option>
      ))}
    </select>
  );
  
  const renderCheckboxGroup = () => (
    <CheckboxGroup>
      {field.options?.map((option) => (
        <CheckboxItem key={option.value}>
          <input
            type={field.type}
            name={field.name}
            value={option.value}
            checked={
              field.type === 'checkbox'
                ? Array.isArray(value) && value.includes(option.value)
                : value === option.value
            }
            onChange={(e) => {
              if (field.type === 'checkbox') {
                const currentValues = Array.isArray(value) ? value : [];
                const newValues = e.target.checked
                  ? [...currentValues, option.value]
                  : currentValues.filter(v => v !== option.value);
                handleChange(newValues);
              } else {
                handleChange(option.value);
              }
            }}
            disabled={field.disabled || option.disabled}
          />
          <span>{option.label}</span>
        </CheckboxItem>
      ))}
    </CheckboxGroup>
  );
  
  const renderSingleCheckbox = () => (
    <CheckboxItem>
      <input
        type="checkbox"
        {...baseProps}
        checked={!!value}
        onChange={(e) => handleChange(e.target.checked)}
      />
      <span>{field.label}</span>
    </CheckboxItem>
  );
  
  const renderControl = () => {
    switch (field.type) {
      case 'textarea':
        return renderTextarea();
      case 'select':
        return renderSelect();
      case 'checkbox':
        return field.options ? renderCheckboxGroup() : renderSingleCheckbox();
      case 'radio':
        return renderCheckboxGroup();
      default:
        return renderInput();
    }
  };
  
  return renderControl();
};

// ================================
// MAIN COMPONENT
// ================================

export const Form: React.FC<FormProps> = ({
  fields,
  initialValues = {},
  onSubmit,
  onChange,
  onValidationChange,
  layout = 'vertical',
  size = 'medium',
  variant = 'default',
  disabled = false,
  loading = false,
  validateOnChange = true,
  validateOnBlur = true,
  showErrorSummary = false,
  requiredMark = true,
  labelPosition = 'top',
  labelWidth,
  spacing = 'normal',
  submitText = 'Submit',
  resetText = 'Reset',
  showSubmit = true,
  showReset = false,
  submitButtonProps = {},
  resetButtonProps = {},
  grid,
  className,
  'data-testid': testId,
}) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const setValue = useCallback((name: string, value: any) => {
    setValues(prev => {
      const newValues = { ...prev, [name]: value };
      onChange?.(newValues, name);
      return newValues;
    });
    
    if (validateOnChange) {
      const field = fields.find(f => f.name === name);
      if (field) {
        const fieldErrors = validateField(field, value, values);
        setErrors(prev => ({ ...prev, [name]: fieldErrors }));
      }
    }
  }, [fields, values, onChange, validateOnChange]);
  
  const setError = useCallback((name: string, fieldErrors: string[]) => {
    setErrors(prev => ({ ...prev, [name]: fieldErrors }));
  }, []);
  
  const setTouchedField = useCallback((name: string, isTouched: boolean) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }));
  }, []);
  
  const validateFieldFn = useCallback((name: string): string[] => {
    const field = fields.find(f => f.name === name);
    if (!field) return [];
    
    const fieldErrors = validateField(field, values[name], values);
    setError(name, fieldErrors);
    return fieldErrors;
  }, [fields, values, setError]);
  
  const validateForm = useCallback((): boolean => {
    const allErrors: Record<string, string[]> = {};
    let isValid = true;
    
    for (const field of fields) {
      if (field.conditional && !field.conditional(values)) continue;
      
      const fieldErrors = validateField(field, values[field.name], values);
      allErrors[field.name] = fieldErrors;
      
      if (fieldErrors.length > 0) {
        isValid = false;
      }
    }
    
    setErrors(allErrors);
    onValidationChange?.(allErrors);
    return isValid;
  }, [fields, values, onValidationChange]);
  
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);
  
  const submitForm = useCallback(async () => {
    setIsSubmitting(true);
    
    // Mark all fields as touched
    const allTouched: Record<string, boolean> = {};
    fields.forEach(field => {
      allTouched[field.name] = true;
    });
    setTouched(allTouched);
    
    const isValid = validateForm();
    
    try {
      await onSubmit?.(values, isValid);
    } finally {
      setIsSubmitting(false);
    }
  }, [fields, values, validateForm, onSubmit]);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitForm();
  };
  
  const contextValue: FormContextValue = {
    values,
    errors,
    touched,
    isSubmitting: isSubmitting || loading,
    isValid: Object.values(errors).every(errs => errs.length === 0),
    setValue,
    setError,
    setTouched: setTouchedField,
    validateField: validateFieldFn,
    validateForm,
    resetForm,
    submitForm,
  };
  
  // Filter visible fields based on conditions
  const visibleFields = fields.filter(field => 
    !field.conditional || field.conditional(values)
  );
  
  // Get all error messages for summary
  const allErrors = Object.entries(errors)
    .filter(([name, errs]) => errs.length > 0 && touched[name])
    .reduce((acc, [name, errs]) => {
      const field = fields.find(f => f.name === name);
      const fieldLabel = field?.label || name;
      return [
        ...acc,
        ...errs.map(err => `${fieldLabel}: ${err}`)
      ];
    }, [] as string[]);
  
  return (
    <FormContext.Provider value={contextValue}>
      <FormContainer
        onSubmit={handleSubmit}
        layout={layout}
        spacing={spacing}
        disabled={disabled || loading}
        grid={grid}
        className={className}
        data-testid={testId}
        noValidate
      >
        {showErrorSummary && allErrors.length > 0 && (
          <ErrorSummary>
            <div className="error-title">Please fix the following errors:</div>
            <ul className="error-list">
              {allErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </ErrorSummary>
        )}
        
        {visibleFields.map((field) => {
          const fieldErrors = errors[field.name] || [];
          const isTouched = touched[field.name];
          const hasError = fieldErrors.length > 0 && isTouched;
          
          return (
            <FormField
              key={field.name}
              className="form-field"
              size={field.size || size}
              hasError={hasError}
              grid={field.grid}
            >
              {field.label && field.type !== 'checkbox' && (
                <FormLabel
                  htmlFor={field.name}
                  className="form-label"
                  required={field.required && requiredMark}
                  position={labelPosition}
                  width={labelWidth}
                >
                  {field.label}
                </FormLabel>
              )}
              
              <FormControlWrapper className="form-control-wrapper">
                <FormControl
                  variant={field.variant || variant}
                  size={field.size || size}
                  hasError={hasError}
                  disabled={field.disabled || disabled}
                >
                  {renderField(field, contextValue)}
                </FormControl>
                
                {field.description && (
                  <FormDescription>{field.description}</FormDescription>
                )}
                
                {hasError && (
                  <FormError>
                    {fieldErrors.length === 1 ? (
                      fieldErrors[0]
                    ) : (
                      <ul>
                        {fieldErrors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    )}
                  </FormError>
                )}
              </FormControlWrapper>
            </FormField>
          );
        })}
        
        {(showSubmit || showReset) && (
          <FormActions layout={layout}>
            {showSubmit && (
              <FormButton
                type="submit"
                variant="primary"
                size={size}
                loading={isSubmitting || loading}
                disabled={disabled}
                {...submitButtonProps}
              >
                {(isSubmitting || loading) ? 'Processing...' : submitText}
              </FormButton>
            )}
            
            {showReset && (
              <FormButton
                type="button"
                variant="secondary"
                size={size}
                onClick={resetForm}
                disabled={disabled || isSubmitting || loading}
                {...resetButtonProps}
              >
                {resetText}
              </FormButton>
            )}
          </FormActions>
        )}
      </FormContainer>
    </FormContext.Provider>
  );
};

// ================================
// UTILITY COMPONENTS
// ================================

export const SimpleForm: React.FC<Partial<FormProps>> = (props) => (
  <Form layout="vertical" size="medium" spacing="normal" {...props} />
);

export const InlineForm: React.FC<Partial<FormProps>> = (props) => (
  <Form layout="inline" size="small" spacing="compact" {...props} />
);

export const CompactForm: React.FC<Partial<FormProps>> = (props) => (
  <Form layout="vertical" size="small" spacing="compact" {...props} />
);

// ================================
// EXPORTS
// ================================

export default Form;

export type {
  FormProps,
  FormField,
  ValidationRule,
  FormContextValue,
};

export {
  useFormContext,
};

/**
 * 📝 Example Usage:
 * 
 * ```tsx
 * const fields: FormField[] = [
 *   {
 *     name: 'name',
 *     type: 'text',
 *     label: 'Full Name',
 *     required: true,
 *     validation: [
 *       { type: 'required', message: 'Name is required' },
 *       { type: 'minLength', value: 2, message: 'Name must be at least 2 characters' }
 *     ]
 *   },
 *   {
 *     name: 'email',
 *     type: 'email',
 *     label: 'Email Address',
 *     required: true,
 *     validation: [
 *       { type: 'required', message: 'Email is required' },
 *       { type: 'email', message: 'Please enter a valid email' }
 *     ]
 *   },
 *   {
 *     name: 'age',
 *     type: 'number',
 *     label: 'Age',
 *     min: 18,
 *     max: 120,
 *     validation: [
 *       { type: 'min', value: 18, message: 'Must be at least 18 years old' }
 *     ]
 *   }
 * ];
 * 
 * <Form
 *   fields={fields}
 *   onSubmit={(values, isValid) => {
 *     if (isValid) {
 *       console.log('Form submitted:', values);
 *     }
 *   }}
 *   showErrorSummary
 *   submitText="Create Account"
 *   resetText="Clear Form"
 *   showReset
 * />
 * ```
 */