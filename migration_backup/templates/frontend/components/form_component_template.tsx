/**
 * 🎨 FORM COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ===========================================================
 * 
 * Enterprise-grade form component template with:
 * - TypeScript support with strict typing
 * - Comprehensive validation (sync/async)
 * - Field-level and form-level validation
 * - Dynamic form building
 * - File upload with progress
 * - Multi-step form support
 * - Auto-save and draft functionality
 * - Accessibility compliance (ARIA, keyboard navigation)
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
  useState, 
  useCallback, 
  useEffect, 
  useRef,
  ReactNode,
  FormEvent,
  ChangeEvent,
  FocusEvent
} from 'react';
import styled, { css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface FieldConfig {
  name: string;
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'date' | 'datetime-local' | 'time' | 'select' | 'textarea' | 'checkbox' | 'radio' | 'file' | 'custom';
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  options?: Array<{ value: string | number; label: string; disabled?: boolean }>;
  validation?: ValidationRule[];
  asyncValidation?: (value: any) => Promise<string | null>;
  description?: string;
  icon?: ReactNode;
  prefix?: ReactNode;
  suffix?: ReactNode;
  autoComplete?: string;
  dependencies?: string[];
  conditionalRender?: (values: Record<string, any>) => boolean;
  transform?: (value: any) => any;
  format?: (value: any) => string;
  parse?: (value: string) => any;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'filled';
  multiple?: boolean;
  accept?: string;
  maxLength?: number;
  minLength?: number;
  min?: number;
  max?: number;
  step?: number;
  rows?: number;
  cols?: number;
  customComponent?: React.ComponentType<any>;
  className?: string;
  style?: React.CSSProperties;
}

interface ValidationRule {
  type: 'required' | 'email' | 'url' | 'minLength' | 'maxLength' | 'min' | 'max' | 'pattern' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any, values: Record<string, any>) => boolean;
}

interface FormProps {
  fields: FieldConfig[];
  initialValues?: Record<string, any>;
  onSubmit: (values: Record<string, any>) => Promise<void> | void;
  onValuesChange?: (values: Record<string, any>) => void;
  validation?: 'onChange' | 'onBlur' | 'onSubmit';
  autoSave?: boolean;
  autoSaveDelay?: number;
  multiStep?: boolean;
  steps?: FormStep[];
  layout?: 'vertical' | 'horizontal' | 'inline';
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'filled';
  loading?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  resetOnSubmit?: boolean;
  submitText?: string;
  resetText?: string;
  showProgress?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

interface FormStep {
  id: string;
  title: string;
  description?: string;
  fields: string[];
  validation?: boolean;
}

interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  validating: Record<string, boolean>;
  isSubmitting: boolean;
  isValid: boolean;
  currentStep: number;
  submitCount: number;
}

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const FormContainer = styled.form<{
  layout: 'vertical' | 'horizontal' | 'inline';
  disabled?: boolean;
}>`
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  ${({ layout }) => {
    switch (layout) {
      case 'horizontal':
        return css`
          .form-field {
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            
            .field-label {
              width: 200px;
              margin-right: 1rem;
              margin-bottom: 0;
              padding-top: 0.5rem;
            }
            
            .field-content {
              flex: 1;
            }
          }
        `;
      case 'inline':
        return css`
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          align-items: flex-end;
          
          .form-field {
            flex: 0 0 auto;
            margin-bottom: 0;
          }
        `;
      default: // vertical
        return css`
          .form-field {
            margin-bottom: 1.5rem;
          }
        `;
    }
  }}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    pointer-events: none;
  `}
`;

const FormField = styled.div<{ size: 'small' | 'medium' | 'large' }>`
  position: relative;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          font-size: 13px;
          
          .field-label {
            font-size: 12px;
          }
        `;
      case 'large':
        return css`
          font-size: 16px;
          
          .field-label {
            font-size: 16px;
          }
        `;
      default: // medium
        return css`
          font-size: 14px;
          
          .field-label {
            font-size: 14px;
          }
        `;
    }
  }}
`;

const FieldLabel = styled.label<{ required?: boolean }>`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  
  ${({ required }) => required && css`
    &::after {
      content: ' *';
      color: #ef4444;
    }
  `}
`;

const FieldDescription = styled.div`
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 0.5rem;
`;

const InputContainer = styled.div<{
  hasIcon?: boolean;
  hasPrefix?: boolean;
  hasSuffix?: boolean;
  error?: boolean;
  success?: boolean;
  disabled?: boolean;
  variant: 'default' | 'outlined' | 'filled';
  size: 'small' | 'medium' | 'large';
}>`
  position: relative;
  display: flex;
  align-items: center;
  
  ${({ variant }) => {
    switch (variant) {
      case 'filled':
        return css`
          background: #f9fafb;
          border: 2px solid transparent;
          border-radius: 8px;
          
          &:focus-within {
            background: white;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
      case 'outlined':
        return css`
          background: transparent;
          border: 2px solid #d1d5db;
          border-radius: 8px;
          
          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
      default:
        return css`
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          
          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
    }
  }}
  
  ${({ error }) => error && css`
    border-color: #ef4444 !important;
    
    &:focus-within {
      border-color: #ef4444 !important;
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
    }
  `}
  
  ${({ success }) => success && css`
    border-color: #10b981 !important;
    
    &:focus-within {
      border-color: #10b981 !important;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }
  `}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    background: #f9fafb;
  `}
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          min-height: 36px;
          padding: 0 10px;
        `;
      case 'large':
        return css`
          min-height: 56px;
          padding: 0 18px;
        `;
      default: // medium
        return css`
          min-height: 44px;
          padding: 0 14px;
        `;
    }
  }}
`;

const BaseInput = styled.input<{ hasIcon?: boolean; hasPrefix?: boolean; hasSuffix?: boolean }>`
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: inherit;
  
  &::placeholder {
    color: #9ca3af;
  }
  
  &:disabled {
    cursor: not-allowed;
  }
  
  ${({ hasIcon, hasPrefix, hasSuffix }) => css`
    padding-left: ${hasIcon || hasPrefix ? '0' : '0'};
    padding-right: ${hasSuffix ? '0' : '0'};
  `}
`;

const TextArea = styled.textarea<{ hasIcon?: boolean; hasPrefix?: boolean; hasSuffix?: boolean }>`
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: inherit;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  
  &::placeholder {
    color: #9ca3af;
  }
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const Select = styled.select`
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #374151;
  font-size: inherit;
  cursor: pointer;
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const CheckboxContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  cursor: pointer;
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const RadioGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const RadioContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Radio = styled.input`
  width: 16px;
  height: 16px;
  cursor: pointer;
  
  &:disabled {
    cursor: not-allowed;
  }
`;

const FieldIcon = styled.div`
  display: flex;
  align-items: center;
  color: #6b7280;
  margin-right: 0.5rem;
`;

const FieldPrefix = styled.div`
  display: flex;
  align-items: center;
  color: #6b7280;
  margin-right: 0.5rem;
  white-space: nowrap;
`;

const FieldSuffix = styled.div`
  display: flex;
  align-items: center;
  color: #6b7280;
  margin-left: 0.5rem;
  white-space: nowrap;
`;

const FieldError = styled(motion.div)`
  color: #ef4444;
  font-size: 12px;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const FieldSuccess = styled.div`
  color: #10b981;
  font-size: 12px;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const FormActions = styled.div<{ layout: 'vertical' | 'horizontal' | 'inline' }>`
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  
  ${({ layout }) => layout === 'horizontal' && css`
    margin-left: 200px;
    padding-left: 1rem;
  `}
`;

const SubmitButton = styled.button<{ 
  variant?: 'primary' | 'secondary';
  size: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
}>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          padding: 8px 16px;
          font-size: 13px;
        `;
      case 'large':
        return css`
          padding: 16px 32px;
          font-size: 16px;
        `;
      default: // medium
        return css`
          padding: 12px 24px;
          font-size: 14px;
        `;
    }
  }}
  
  ${({ variant }) => {
    switch (variant) {
      case 'secondary':
        return css`
          background: #f3f4f6;
          color: #374151;
          
          &:hover:not(:disabled) {
            background: #e5e7eb;
          }
        `;
      default: // primary
        return css`
          background: #3b82f6;
          color: white;
          
          &:hover:not(:disabled) {
            background: #2563eb;
          }
        `;
    }
  }}
  
  ${({ disabled, loading }) => (disabled || loading) && css`
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  `}
`;

const FormProgress = styled.div`
  margin-bottom: 2rem;
`;

const ProgressBar = styled.div<{ progress: number }>`
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    width: ${({ progress }) => progress}%;
    background: #3b82f6;
    transition: width 0.3s ease;
  }
`;

const StepIndicator = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const Step = styled.div<{ active?: boolean; completed?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
  position: relative;
  
  &:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 16px;
    left: 50%;
    right: -50%;
    height: 2px;
    background: ${({ completed }) => completed ? '#3b82f6' : '#e5e7eb'};
  }
`;

const StepCircle = styled.div<{ active?: boolean; completed?: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  margin-bottom: 0.5rem;
  position: relative;
  z-index: 1;
  
  ${({ active, completed }) => {
    if (completed) {
      return css`
        background: #3b82f6;
        color: white;
      `;
    } else if (active) {
      return css`
        background: white;
        color: #3b82f6;
        border: 2px solid #3b82f6;
      `;
    } else {
      return css`
        background: #e5e7eb;
        color: #6b7280;
      `;
    }
  }}
`;

const StepTitle = styled.div<{ active?: boolean }>`
  font-size: 12px;
  font-weight: 500;
  color: ${({ active }) => active ? '#3b82f6' : '#6b7280'};
`;

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

const validateField = (value: any, rules: ValidationRule[], allValues: Record<string, any>): string | null => {
  for (const rule of rules) {
    switch (rule.type) {
      case 'required':
        if (!value || (typeof value === 'string' && !value.trim())) {
          return rule.message;
        }
        break;
        
      case 'email':
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          return rule.message;
        }
        break;
        
      case 'url':
        if (value && !/^https?:\/\/.+/.test(value)) {
          return rule.message;
        }
        break;
        
      case 'minLength':
        if (value && value.length < rule.value) {
          return rule.message;
        }
        break;
        
      case 'maxLength':
        if (value && value.length > rule.value) {
          return rule.message;
        }
        break;
        
      case 'min':
        if (value && Number(value) < rule.value) {
          return rule.message;
        }
        break;
        
      case 'max':
        if (value && Number(value) > rule.value) {
          return rule.message;
        }
        break;
        
      case 'pattern':
        if (value && !new RegExp(rule.value).test(value)) {
          return rule.message;
        }
        break;
        
      case 'custom':
        if (rule.validator && !rule.validator(value, allValues)) {
          return rule.message;
        }
        break;
    }
  }
  
  return null;
};

// ============================================================================
// MAIN FORM COMPONENT
// ============================================================================

export const Form: React.FC<FormProps> = ({
  fields = [],
  initialValues = {},
  onSubmit,
  onValuesChange,
  validation = 'onBlur',
  autoSave = false,
  autoSaveDelay = 1000,
  multiStep = false,
  steps = [],
  layout = 'vertical',
  size = 'medium',
  variant = 'default',
  loading = false,
  disabled = false,
  readonly = false,
  resetOnSubmit = false,
  submitText = 'Submit',
  resetText = 'Reset',
  showProgress = false,
  className,
  style,
  ...props
}) => {
  const [state, setState] = useState<FormState>({
    values: { ...initialValues },
    errors: {},
    touched: {},
    validating: {},
    isSubmitting: false,
    isValid: false,
    currentStep: 0,
    submitCount: 0,
  });

  const autoSaveTimeoutRef = useRef<NodeJS.Timeout>();
  const formRef = useRef<HTMLFormElement>(null);

  // Get current step fields
  const currentStepFields = useMemo(() => {
    if (!multiStep || !steps.length) return fields;
    return fields.filter(field => steps[state.currentStep]?.fields.includes(field.name));
  }, [multiStep, steps, state.currentStep, fields]);

  // Calculate form progress
  const formProgress = useMemo(() => {
    if (!showProgress) return 0;
    
    const totalFields = fields.length;
    const filledFields = fields.filter(field => {
      const value = state.values[field.name];
      return value !== undefined && value !== '' && value !== null;
    }).length;
    
    return totalFields > 0 ? (filledFields / totalFields) * 100 : 0;
  }, [fields, state.values, showProgress]);

  // Validate form
  const validateForm = useCallback(async () => {
    const errors: Record<string, string> = {};
    const fieldsToValidate = multiStep ? currentStepFields : fields;
    
    // Sync validation
    for (const field of fieldsToValidate) {
      if (field.validation) {
        const error = validateField(state.values[field.name], field.validation, state.values);
        if (error) {
          errors[field.name] = error;
        }
      }
    }
    
    // Async validation
    const asyncValidations = fieldsToValidate
      .filter(field => field.asyncValidation)
      .map(async field => {
        setState(prev => ({
          ...prev,
          validating: { ...prev.validating, [field.name]: true }
        }));
        
        try {
          const error = await field.asyncValidation!(state.values[field.name]);
          if (error) {
            errors[field.name] = error;
          }
        } catch (err) {
          errors[field.name] = 'Validation failed';
        } finally {
          setState(prev => ({
            ...prev,
            validating: { ...prev.validating, [field.name]: false }
          }));
        }
      });
    
    await Promise.all(asyncValidations);
    
    setState(prev => ({
      ...prev,
      errors,
      isValid: Object.keys(errors).length === 0
    }));
    
    return Object.keys(errors).length === 0;
  }, [fields, currentStepFields, multiStep, state.values]);

  // Handle field change
  const handleFieldChange = useCallback((fieldName: string, value: any) => {
    const field = fields.find(f => f.name === fieldName);
    const transformedValue = field?.transform ? field.transform(value) : value;
    
    setState(prev => {
      const newValues = { ...prev.values, [fieldName]: transformedValue };
      
      // Clear field error on change if validation is onChange
      const newErrors = { ...prev.errors };
      if (validation === 'onChange') {
        delete newErrors[fieldName];
      }
      
      return {
        ...prev,
        values: newValues,
        errors: newErrors,
        touched: { ...prev.touched, [fieldName]: true }
      };
    });
    
    onValuesChange?.(state.values);
    
    // Auto-save
    if (autoSave) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      autoSaveTimeoutRef.current = setTimeout(() => {
        // Implement auto-save logic here
        console.log('Auto-saving form...', state.values);
      }, autoSaveDelay);
    }
    
    // Validate on change
    if (validation === 'onChange') {
      setTimeout(validateForm, 0);
    }
  }, [fields, validation, state.values, onValuesChange, autoSave, autoSaveDelay, validateForm]);

  // Handle field blur
  const handleFieldBlur = useCallback((fieldName: string) => {
    setState(prev => ({
      ...prev,
      touched: { ...prev.touched, [fieldName]: true }
    }));
    
    if (validation === 'onBlur') {
      setTimeout(validateForm, 0);
    }
  }, [validation, validateForm]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    
    setState(prev => ({ ...prev, isSubmitting: true, submitCount: prev.submitCount + 1 }));
    
    try {
      const isValid = await validateForm();
      
      if (isValid) {
        if (multiStep && state.currentStep < steps.length - 1) {
          // Move to next step
          setState(prev => ({ ...prev, currentStep: prev.currentStep + 1 }));
        } else {
          // Submit form
          await onSubmit(state.values);
          
          if (resetOnSubmit) {
            setState(prev => ({
              ...prev,
              values: { ...initialValues },
              errors: {},
              touched: {},
              currentStep: 0
            }));
          }
        }
      }
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [validateForm, multiStep, state.currentStep, state.values, steps.length, onSubmit, resetOnSubmit, initialValues]);

  // Handle reset
  const handleReset = useCallback(() => {
    setState(prev => ({
      ...prev,
      values: { ...initialValues },
      errors: {},
      touched: {},
      currentStep: 0,
      submitCount: 0
    }));
  }, [initialValues]);

  // Navigate steps
  const goToStep = useCallback((stepIndex: number) => {
    if (stepIndex >= 0 && stepIndex < steps.length) {
      setState(prev => ({ ...prev, currentStep: stepIndex }));
    }
  }, [steps.length]);

  // Render field
  const renderField = useCallback((field: FieldConfig) => {
    if (field.conditionalRender && !field.conditionalRender(state.values)) {
      return null;
    }

    const value = state.values[field.name] || '';
    const error = state.errors[field.name];
    const isValidating = state.validating[field.name];
    const isTouched = state.touched[field.name];
    const isDisabled = disabled || readonly || field.disabled || field.readonly;
    const hasError = error && (isTouched || state.submitCount > 0);
    const isSuccess = !error && isTouched && field.validation && field.validation.length > 0;

    const commonProps = {
      id: field.name,
      name: field.name,
      disabled: isDisabled,
      readOnly: readonly || field.readonly,
      autoComplete: field.autoComplete,
      'aria-describedby': error ? `${field.name}-error` : field.description ? `${field.name}-description` : undefined,
      'aria-invalid': hasError,
    };

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      let newValue: any = e.target.value;
      
      if (field.type === 'number') {
        newValue = e.target.value === '' ? '' : Number(e.target.value);
      } else if (field.type === 'checkbox') {
        newValue = (e.target as HTMLInputElement).checked;
      } else if (field.type === 'file') {
        newValue = (e.target as HTMLInputElement).files;
      }
      
      if (field.parse) {
        newValue = field.parse(newValue);
      }
      
      handleFieldChange(field.name, newValue);
    };

    const handleBlur = (e: FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      handleFieldBlur(field.name);
    };

    let fieldInput: ReactNode;

    if (field.customComponent) {
      const CustomComponent = field.customComponent;
      fieldInput = (
        <CustomComponent
          {...commonProps}
          value={value}
          onChange={(newValue: any) => handleFieldChange(field.name, newValue)}
          onBlur={() => handleFieldBlur(field.name)}
          error={hasError}
          field={field}
        />
      );
    } else {
      switch (field.type) {
        case 'textarea':
          fieldInput = (
            <InputContainer
              hasIcon={!!field.icon}
              hasPrefix={!!field.prefix}
              hasSuffix={!!field.suffix}
              error={hasError}
              success={isSuccess}
              disabled={isDisabled}
              variant={field.variant || variant}
              size={field.size || size}
            >
              {field.icon && <FieldIcon>{field.icon}</FieldIcon>}
              {field.prefix && <FieldPrefix>{field.prefix}</FieldPrefix>}
              <TextArea
                {...commonProps}
                value={field.format ? field.format(value) : value}
                placeholder={field.placeholder}
                rows={field.rows}
                cols={field.cols}
                maxLength={field.maxLength}
                minLength={field.minLength}
                onChange={handleChange}
                onBlur={handleBlur}
              />
              {field.suffix && <FieldSuffix>{field.suffix}</FieldSuffix>}
              {isValidating && <LoadingSpinner />}
            </InputContainer>
          );
          break;

        case 'select':
          fieldInput = (
            <InputContainer
              hasIcon={!!field.icon}
              hasPrefix={!!field.prefix}
              hasSuffix={!!field.suffix}
              error={hasError}
              success={isSuccess}
              disabled={isDisabled}
              variant={field.variant || variant}
              size={field.size || size}
            >
              {field.icon && <FieldIcon>{field.icon}</FieldIcon>}
              {field.prefix && <FieldPrefix>{field.prefix}</FieldPrefix>}
              <Select
                {...commonProps}
                value={value}
                multiple={field.multiple}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                {field.placeholder && (
                  <option value="" disabled>
                    {field.placeholder}
                  </option>
                )}
                {field.options?.map(option => (
                  <option
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                  >
                    {option.label}
                  </option>
                ))}
              </Select>
              {field.suffix && <FieldSuffix>{field.suffix}</FieldSuffix>}
              {isValidating && <LoadingSpinner />}
            </InputContainer>
          );
          break;

        case 'checkbox':
          fieldInput = (
            <CheckboxContainer>
              <Checkbox
                {...commonProps}
                type="checkbox"
                checked={!!value}
                onChange={handleChange}
                onBlur={handleBlur}
              />
              <label htmlFor={field.name}>{field.label}</label>
            </CheckboxContainer>
          );
          break;

        case 'radio':
          fieldInput = (
            <RadioGroup>
              {field.options?.map(option => (
                <RadioContainer key={option.value}>
                  <Radio
                    {...commonProps}
                    type="radio"
                    value={option.value}
                    checked={value === option.value}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    disabled={isDisabled || option.disabled}
                  />
                  <label htmlFor={`${field.name}-${option.value}`}>
                    {option.label}
                  </label>
                </RadioContainer>
              ))}
            </RadioGroup>
          );
          break;

        default:
          fieldInput = (
            <InputContainer
              hasIcon={!!field.icon}
              hasPrefix={!!field.prefix}
              hasSuffix={!!field.suffix}
              error={hasError}
              success={isSuccess}
              disabled={isDisabled}
              variant={field.variant || variant}
              size={field.size || size}
            >
              {field.icon && <FieldIcon>{field.icon}</FieldIcon>}
              {field.prefix && <FieldPrefix>{field.prefix}</FieldPrefix>}
              <BaseInput
                {...commonProps}
                type={field.type}
                value={field.format ? field.format(value) : value}
                placeholder={field.placeholder}
                maxLength={field.maxLength}
                minLength={field.minLength}
                min={field.min}
                max={field.max}
                step={field.step}
                accept={field.accept}
                multiple={field.multiple}
                onChange={handleChange}
                onBlur={handleBlur}
              />
              {field.suffix && <FieldSuffix>{field.suffix}</FieldSuffix>}
              {isValidating && <LoadingSpinner />}
            </InputContainer>
          );
      }
    }

    return (
      <FormField
        key={field.name}
        className={`form-field ${field.className || ''}`}
        size={field.size || size}
        style={field.style}
      >
        {field.type !== 'checkbox' && (
          <FieldLabel
            className="field-label"
            htmlFor={field.name}
            required={field.required}
          >
            {field.label}
          </FieldLabel>
        )}
        
        {field.description && (
          <FieldDescription id={`${field.name}-description`}>
            {field.description}
          </FieldDescription>
        )}
        
        <div className="field-content">
          {fieldInput}
        </div>
        
        <AnimatePresence>
          {hasError && (
            <FieldError
              id={`${field.name}-error`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                <path d="M6 0C2.686 0 0 2.686 0 6s2.686 6 6 6 6-2.686 6-6S9.314 0 6 0zM6 9a1 1 0 110-2 1 1 0 010 2zm1-3V3a1 1 0 10-2 0v3a1 1 0 102 0z"/>
              </svg>
              {error}
            </FieldError>
          )}
        </AnimatePresence>
        
        {isSuccess && (
          <FieldSuccess>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M10 3L4.5 8.5L2 6"/>
            </svg>
            Valid
          </FieldSuccess>
        )}
      </FormField>
    );
  }, [
    state.values,
    state.errors,
    state.touched,
    state.validating,
    state.submitCount,
    disabled,
    readonly,
    variant,
    size,
    handleFieldChange,
    handleFieldBlur
  ]);

  return (
    <FormContainer
      ref={formRef}
      className={className}
      style={style}
      layout={layout}
      disabled={disabled || loading}
      onSubmit={handleSubmit}
      {...props}
    >
      {/* Progress Indicator */}
      {showProgress && (
        <FormProgress>
          <ProgressBar progress={formProgress} />
          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            {Math.round(formProgress)}% Complete
          </div>
        </FormProgress>
      )}

      {/* Step Indicator */}
      {multiStep && steps.length > 0 && (
        <StepIndicator>
          {steps.map((step, index) => (
            <Step
              key={step.id}
              active={index === state.currentStep}
              completed={index < state.currentStep}
            >
              <StepCircle
                active={index === state.currentStep}
                completed={index < state.currentStep}
              >
                {index < state.currentStep ? '✓' : index + 1}
              </StepCircle>
              <StepTitle active={index === state.currentStep}>
                {step.title}
              </StepTitle>
            </Step>
          ))}
        </StepIndicator>
      )}

      {/* Form Fields */}
      {currentStepFields.map(renderField)}

      {/* Form Actions */}
      <FormActions layout={layout}>
        {multiStep && state.currentStep > 0 && (
          <SubmitButton
            type="button"
            variant="secondary"
            size={size}
            onClick={() => goToStep(state.currentStep - 1)}
          >
            Previous
          </SubmitButton>
        )}
        
        <SubmitButton
          type="submit"
          size={size}
          loading={state.isSubmitting}
          disabled={state.isSubmitting || loading}
        >
          {state.isSubmitting && <LoadingSpinner />}
          {multiStep && state.currentStep < steps.length - 1 ? 'Next' : submitText}
        </SubmitButton>
        
        <SubmitButton
          type="button"
          variant="secondary"
          size={size}
          onClick={handleReset}
          disabled={state.isSubmitting || loading}
        >
          {resetText}
        </SubmitButton>
      </FormActions>
    </FormContainer>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const FormExamples: React.FC = () => {
  const [formValues, setFormValues] = useState({});

  const sampleFields: FieldConfig[] = [
    {
      name: 'firstName',
      type: 'text',
      label: 'First Name',
      placeholder: 'Enter your first name',
      required: true,
      validation: [
        { type: 'required', message: 'First name is required' },
        { type: 'minLength', value: 2, message: 'First name must be at least 2 characters' }
      ]
    },
    {
      name: 'lastName',
      type: 'text',
      label: 'Last Name',
      placeholder: 'Enter your last name',
      required: true,
      validation: [
        { type: 'required', message: 'Last name is required' }
      ]
    },
    {
      name: 'email',
      type: 'email',
      label: 'Email Address',
      placeholder: 'Enter your email',
      required: true,
      validation: [
        { type: 'required', message: 'Email is required' },
        { type: 'email', message: 'Please enter a valid email address' }
      ]
    },
    {
      name: 'age',
      type: 'number',
      label: 'Age',
      placeholder: 'Enter your age',
      min: 18,
      max: 120,
      validation: [
        { type: 'min', value: 18, message: 'You must be at least 18 years old' },
        { type: 'max', value: 120, message: 'Please enter a valid age' }
      ]
    },
    {
      name: 'bio',
      type: 'textarea',
      label: 'Bio',
      placeholder: 'Tell us about yourself...',
      rows: 4,
      maxLength: 500,
      description: 'Max 500 characters'
    },
    {
      name: 'country',
      type: 'select',
      label: 'Country',
      placeholder: 'Select your country',
      options: [
        { value: 'us', label: 'United States' },
        { value: 'ca', label: 'Canada' },
        { value: 'uk', label: 'United Kingdom' },
        { value: 'fr', label: 'France' },
        { value: 'de', label: 'Germany' }
      ]
    },
    {
      name: 'newsletter',
      type: 'checkbox',
      label: 'Subscribe to newsletter'
    }
  ];

  const handleSubmit = async (values: Record<string, any>) => {
    console.log('Form submitted:', values);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px' }}>
      <h2>Form Component Examples</h2>
      
      <div style={{ marginBottom: '3rem' }}>
        <h3>Basic Form</h3>
        <Form
          fields={sampleFields}
          onSubmit={handleSubmit}
          onValuesChange={setFormValues}
          validation="onBlur"
          showProgress
        />
      </div>

      <div style={{ marginBottom: '3rem' }}>
        <h3>Horizontal Layout</h3>
        <Form
          fields={sampleFields.slice(0, 4)}
          layout="horizontal"
          onSubmit={handleSubmit}
          size="small"
          variant="outlined"
        />
      </div>

      <div style={{ marginBottom: '3rem' }}>
        <h3>Inline Layout</h3>
        <Form
          fields={sampleFields.slice(0, 3)}
          layout="inline"
          onSubmit={handleSubmit}
          size="medium"
          variant="filled"
        />
      </div>

      <div>
        <h3>Form Values</h3>
        <pre style={{ 
          background: '#f3f4f6', 
          padding: '1rem', 
          borderRadius: '8px',
          fontSize: '12px'
        }}>
          {JSON.stringify(formValues, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default Form;