/**
 * 📋 Form Component Template - Enterprise Form Builder
 * ====================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade form components with advanced features:
 * validation, dynamic fields, multi-step forms, file uploads, auto-save.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { 
  useState, 
  useEffect, 
  useCallback, 
  useMemo, 
  useRef,
  forwardRef,
  useImperativeHandle,
  createContext,
  useContext
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea' | 'select' | 'multiselect' | 'checkbox' | 'radio' | 'file' | 'date' | 'datetime-local' | 'time' | 'range' | 'color';
  value?: any;
  defaultValue?: any;
  placeholder?: string;
  description?: string;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  hidden?: boolean;
  autoFocus?: boolean;
  autoComplete?: string;
  validation?: ValidationConfig;
  options?: FieldOption[];
  multiple?: boolean;
  accept?: string; // for file inputs
  min?: number | string;
  max?: number | string;
  step?: number | string;
  pattern?: string;
  maxLength?: number;
  minLength?: number;
  rows?: number; // for textarea
  cols?: number; // for textarea
  size?: 'small' | 'medium' | 'large';
  layout?: 'horizontal' | 'vertical';
  width?: string | number;
  className?: string;
  style?: React.CSSProperties;
  onChange?: (value: any, field: FormField) => void;
  onBlur?: (value: any, field: FormField) => void;
  onFocus?: (value: any, field: FormField) => void;
  render?: (field: FormField, value: any, error?: string) => React.ReactNode;
  dependsOn?: string[]; // Fields this field depends on
  showWhen?: (values: Record<string, any>) => boolean; // Conditional visibility
}

interface FieldOption {
  label: string;
  value: any;
  disabled?: boolean;
  description?: string;
  icon?: React.ReactNode;
}

interface ValidationConfig {
  rules?: ValidationRule[];
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  debounceMs?: number;
}

interface ValidationRule {
  type: 'required' | 'email' | 'url' | 'number' | 'integer' | 'positive' | 'min' | 'max' | 'minLength' | 'maxLength' | 'pattern' | 'custom';
  value?: any;
  message?: string;
  validator?: (value: any, values: Record<string, any>) => boolean | string | Promise<boolean | string>;
}

interface FormProps {
  fields: FormField[];
  initialValues?: Record<string, any>;
  layout?: 'horizontal' | 'vertical' | 'inline';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  readOnly?: boolean;
  autoSave?: boolean;
  autoSaveDelay?: number;
  validateOnSubmit?: boolean;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  resetOnSubmit?: boolean;
  multiStep?: boolean;
  steps?: FormStep[];
  currentStep?: number;
  showProgress?: boolean;
  submitText?: string;
  resetText?: string;
  nextText?: string;
  previousText?: string;
  loading?: boolean;
  submitting?: boolean;
  className?: string;
  formClassName?: string;
  fieldClassName?: string;
  errorClassName?: string;
  onSubmit?: (values: Record<string, any>, form: FormRef) => void | Promise<void>;
  onReset?: (form: FormRef) => void;
  onChange?: (values: Record<string, any>, changedField: string, form: FormRef) => void;
  onValidationChange?: (errors: Record<string, string>, isValid: boolean, form: FormRef) => void;
  onStepChange?: (step: number, direction: 'next' | 'previous') => void;
  onAutoSave?: (values: Record<string, any>) => void;
  beforeSubmit?: (values: Record<string, any>) => Record<string, any> | Promise<Record<string, any>>;
  afterSubmit?: (result: any, values: Record<string, any>) => void;
  testId?: string;
}

interface FormStep {
  title: string;
  description?: string;
  fields: string[]; // Field names included in this step
  validation?: boolean; // Whether to validate this step before proceeding
  optional?: boolean;
  icon?: React.ReactNode;
}

interface FormRef {
  submit: () => Promise<void>;
  reset: () => void;
  validate: () => Promise<boolean>;
  getValues: () => Record<string, any>;
  setValues: (values: Record<string, any>) => void;
  getValue: (fieldName: string) => any;
  setValue: (fieldName: string, value: any) => void;
  getErrors: () => Record<string, string>;
  setErrors: (errors: Record<string, string>) => void;
  getError: (fieldName: string) => string | undefined;
  setError: (fieldName: string, error: string) => void;
  clearErrors: () => void;
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (step: number) => void;
  isValid: () => boolean;
  isDirty: () => boolean;
  isSubmitting: () => boolean;
}

interface FormContextType {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  layout: string;
  size: string;
  setValue: (name: string, value: any) => void;
  setError: (name: string, error: string) => void;
  clearError: (name: string) => void;
  setTouched: (name: string, touched: boolean) => void;
}

// ========================================
// 🌐 FORM CONTEXT
// ========================================

const FormContext = createContext<FormContextType | null>(null);

export const useFormContext = () => {
  const context = useContext(FormContext);
  if (!context) {
    throw new Error('useFormContext must be used within a Form component');
  }
  return context;
};

// ========================================
// 🎨 FORM STYLES
// ========================================

const getFormStyles = (layout: string, size: string) => ({
  form: {
    width: '100%',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
  },

  fieldGroup: {
    marginBottom: size === 'small' ? '1rem' : 
                 size === 'large' ? '1.5rem' : '1.25rem',
    display: layout === 'inline' ? 'inline-block' : 'block',
    marginRight: layout === 'inline' ? '1rem' : 0
  },

  label: {
    display: 'block',
    marginBottom: '0.25rem',
    fontSize: size === 'small' ? '0.875rem' : 
              size === 'large' ? '1rem' : '0.9375rem',
    fontWeight: '500',
    color: '#374151'
  },

  input: {
    width: '100%',
    padding: size === 'small' ? '0.375rem 0.75rem' : 
             size === 'large' ? '0.75rem 1rem' : '0.5rem 0.75rem',
    fontSize: size === 'small' ? '0.875rem' : 
              size === 'large' ? '1.125rem' : '1rem',
    lineHeight: '1.5',
    color: '#374151',
    backgroundColor: '#ffffff',
    border: '1px solid #d1d5db',
    borderRadius: '0.375rem',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    transition: 'border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out',
    outline: 'none'
  },

  inputFocus: {
    borderColor: '#3b82f6',
    boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.1)'
  },

  inputError: {
    borderColor: '#ef4444',
    boxShadow: '0 0 0 3px rgba(239, 68, 68, 0.1)'
  },

  inputDisabled: {
    backgroundColor: '#f9fafb',
    color: '#9ca3af',
    cursor: 'not-allowed'
  },

  textarea: {
    minHeight: '80px',
    resize: 'vertical' as const
  },

  select: {
    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e")`,
    backgroundPosition: 'right 0.5rem center',
    backgroundRepeat: 'no-repeat',
    backgroundSize: '1.5em 1.5em',
    paddingRight: '2.5rem'
  },

  checkbox: {
    width: 'auto',
    marginRight: '0.5rem'
  },

  radio: {
    width: 'auto',
    marginRight: '0.5rem'
  },

  file: {
    padding: '0.5rem',
    border: '2px dashed #d1d5db',
    borderRadius: '0.375rem',
    backgroundColor: '#f9fafb',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'border-color 0.15s ease-in-out'
  },

  fileHover: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff'
  },

  description: {
    marginTop: '0.25rem',
    fontSize: '0.875rem',
    color: '#6b7280'
  },

  error: {
    marginTop: '0.25rem',
    fontSize: '0.875rem',
    color: '#ef4444'
  },

  buttons: {
    display: 'flex',
    gap: '1rem',
    marginTop: '2rem',
    paddingTop: '1rem',
    borderTop: '1px solid #e5e7eb'
  },

  button: {
    padding: size === 'small' ? '0.375rem 0.75rem' : 
             size === 'large' ? '0.75rem 1.5rem' : '0.5rem 1rem',
    fontSize: size === 'small' ? '0.875rem' : 
              size === 'large' ? '1.125rem' : '1rem',
    fontWeight: '500',
    borderRadius: '0.375rem',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.15s ease-in-out',
    outline: 'none'
  },

  primaryButton: {
    backgroundColor: '#3b82f6',
    color: '#ffffff'
  },

  secondaryButton: {
    backgroundColor: '#6b7280',
    color: '#ffffff'
  },

  disabledButton: {
    backgroundColor: '#d1d5db',
    color: '#9ca3af',
    cursor: 'not-allowed'
  },

  progress: {
    width: '100%',
    height: '0.5rem',
    backgroundColor: '#e5e7eb',
    borderRadius: '0.25rem',
    overflow: 'hidden' as const,
    marginBottom: '2rem'
  },

  progressBar: {
    height: '100%',
    backgroundColor: '#3b82f6',
    transition: 'width 0.3s ease-in-out'
  },

  stepIndicator: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '2rem'
  },

  step: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    flex: 1
  },

  stepNumber: {
    width: '2rem',
    height: '2rem',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '0.875rem',
    fontWeight: '500',
    marginBottom: '0.5rem'
  },

  stepTitle: {
    fontSize: '0.875rem',
    fontWeight: '500',
    textAlign: 'center' as const
  }
});

// ========================================
// 🔍 VALIDATION UTILITIES
// ========================================

const validateField = async (field: FormField, value: any, allValues: Record<string, any>): Promise<string | null> => {
  if (!field.validation?.rules) return null;

  for (const rule of field.validation.rules) {
    let isValid = true;
    let errorMessage = rule.message || `Validation failed for ${field.label}`;

    switch (rule.type) {
      case 'required':
        isValid = value !== null && value !== undefined && value !== '';
        errorMessage = rule.message || `${field.label} is required`;
        break;

      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = !value || emailRegex.test(value);
        errorMessage = rule.message || `${field.label} must be a valid email`;
        break;

      case 'url':
        try {
          if (value) new URL(value);
          isValid = true;
        } catch {
          isValid = false;
        }
        errorMessage = rule.message || `${field.label} must be a valid URL`;
        break;

      case 'number':
        isValid = !value || !isNaN(Number(value));
        errorMessage = rule.message || `${field.label} must be a number`;
        break;

      case 'integer':
        isValid = !value || (Number.isInteger(Number(value)));
        errorMessage = rule.message || `${field.label} must be an integer`;
        break;

      case 'positive':
        isValid = !value || Number(value) > 0;
        errorMessage = rule.message || `${field.label} must be positive`;
        break;

      case 'min':
        isValid = !value || Number(value) >= Number(rule.value);
        errorMessage = rule.message || `${field.label} must be at least ${rule.value}`;
        break;

      case 'max':
        isValid = !value || Number(value) <= Number(rule.value);
        errorMessage = rule.message || `${field.label} must be at most ${rule.value}`;
        break;

      case 'minLength':
        isValid = !value || String(value).length >= Number(rule.value);
        errorMessage = rule.message || `${field.label} must be at least ${rule.value} characters`;
        break;

      case 'maxLength':
        isValid = !value || String(value).length <= Number(rule.value);
        errorMessage = rule.message || `${field.label} must be at most ${rule.value} characters`;
        break;

      case 'pattern':
        const regex = new RegExp(rule.value);
        isValid = !value || regex.test(String(value));
        errorMessage = rule.message || `${field.label} format is invalid`;
        break;

      case 'custom':
        if (rule.validator) {
          const result = await rule.validator(value, allValues);
          if (typeof result === 'boolean') {
            isValid = result;
          } else {
            isValid = false;
            errorMessage = result;
          }
        }
        break;
    }

    if (!isValid) {
      return errorMessage;
    }
  }

  return null;
};

// ========================================
// 🏗️ FIELD RENDERER
// ========================================

const FormField: React.FC<{
  field: FormField;
  value: any;
  error?: string;
  onChange: (value: any) => void;
  onBlur: () => void;
  onFocus: () => void;
}> = ({ field, value, error, onChange, onBlur, onFocus }) => {
  const [focused, setFocused] = useState(false);
  const [fileHover, setFileHover] = useState(false);
  const { layout, size } = useFormContext();
  const styles = getFormStyles(layout, size);

  const handleFocus = useCallback(() => {
    setFocused(true);
    onFocus();
  }, [onFocus]);

  const handleBlur = useCallback(() => {
    setFocused(false);
    onBlur();
  }, [onBlur]);

  if (field.render) {
    return <>{field.render(field, value, error)}</>;
  }

  const inputStyle = {
    ...styles.input,
    ...(focused && styles.inputFocus),
    ...(error && styles.inputError),
    ...(field.disabled && styles.inputDisabled),
    ...field.style
  };

  const renderInput = () => {
    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            required={field.required}
            disabled={field.disabled}
            readOnly={field.readOnly}
            rows={field.rows}
            cols={field.cols}
            maxLength={field.maxLength}
            minLength={field.minLength}
            style={{ ...inputStyle, ...styles.textarea }}
            autoFocus={field.autoFocus}
            autoComplete={field.autoComplete}
          />
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
            required={field.required}
            disabled={field.disabled}
            style={{ ...inputStyle, ...styles.select }}
            autoFocus={field.autoFocus}
          >
            {!field.required && <option value="">Select...</option>}
            {field.options?.map((option, index) => (
              <option key={index} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'multiselect':
        return (
          <select
            multiple
            value={Array.isArray(value) ? value : []}
            onChange={(e) => {
              const selectedValues = Array.from(e.target.selectedOptions, option => option.value);
              onChange(selectedValues);
            }}
            onFocus={handleFocus}
            onBlur={handleBlur}
            required={field.required}
            disabled={field.disabled}
            style={{ ...inputStyle, height: 'auto', minHeight: '80px' }}
            autoFocus={field.autoFocus}
          >
            {field.options?.map((option, index) => (
              <option key={index} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <label style={{ display: 'flex', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={Boolean(value)}
              onChange={(e) => onChange(e.target.checked)}
              onFocus={handleFocus}
              onBlur={handleBlur}
              required={field.required}
              disabled={field.disabled}
              style={styles.checkbox}
              autoFocus={field.autoFocus}
            />
            <span>{field.label}</span>
          </label>
        );

      case 'radio':
        return (
          <div>
            {field.options?.map((option, index) => (
              <label key={index} style={{ display: 'block', marginBottom: '0.5rem' }}>
                <input
                  type="radio"
                  name={field.name}
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => onChange(e.target.value)}
                  onFocus={handleFocus}
                  onBlur={handleBlur}
                  required={field.required}
                  disabled={field.disabled || option.disabled}
                  style={styles.radio}
                  autoFocus={field.autoFocus && index === 0}
                />
                <span>{option.label}</span>
                {option.description && (
                  <div style={styles.description}>{option.description}</div>
                )}
              </label>
            ))}
          </div>
        );

      case 'file':
        return (
          <div
            style={{
              ...styles.file,
              ...(fileHover && styles.fileHover)
            }}
            onDragOver={(e) => {
              e.preventDefault();
              setFileHover(true);
            }}
            onDragLeave={() => setFileHover(false)}
            onDrop={(e) => {
              e.preventDefault();
              setFileHover(false);
              const files = Array.from(e.dataTransfer.files);
              onChange(field.multiple ? files : files[0]);
            }}
          >
            <input
              type="file"
              onChange={(e) => {
                const files = Array.from(e.target.files || []);
                onChange(field.multiple ? files : files[0]);
              }}
              onFocus={handleFocus}
              onBlur={handleBlur}
              accept={field.accept}
              multiple={field.multiple}
              required={field.required}
              disabled={field.disabled}
              style={{ display: 'none' }}
              id={`file-${field.name}`}
              autoFocus={field.autoFocus}
            />
            <label htmlFor={`file-${field.name}`} style={{ cursor: 'pointer' }}>
              📁 {value ? (Array.isArray(value) ? `${value.length} files selected` : value.name) : 'Choose files or drag and drop'}
            </label>
          </div>
        );

      case 'range':
        return (
          <div>
            <input
              type="range"
              value={value || field.min || 0}
              onChange={(e) => onChange(Number(e.target.value))}
              onFocus={handleFocus}
              onBlur={handleBlur}
              min={field.min}
              max={field.max}
              step={field.step}
              required={field.required}
              disabled={field.disabled}
              style={{ ...inputStyle, appearance: 'auto' }}
              autoFocus={field.autoFocus}
            />
            <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '0.875rem' }}>
              {value || field.min || 0}
            </div>
          </div>
        );

      default:
        return (
          <input
            type={field.type}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={field.placeholder}
            required={field.required}
            disabled={field.disabled}
            readOnly={field.readOnly}
            min={field.min}
            max={field.max}
            step={field.step}
            pattern={field.pattern}
            maxLength={field.maxLength}
            minLength={field.minLength}
            style={inputStyle}
            autoFocus={field.autoFocus}
            autoComplete={field.autoComplete}
          />
        );
    }
  };

  return (
    <div className={field.className} style={field.style}>
      {field.type !== 'checkbox' && (
        <label style={styles.label}>
          {field.label}
          {field.required && <span style={{ color: '#ef4444' }}> *</span>}
        </label>
      )}
      
      {renderInput()}
      
      {field.description && (
        <div style={styles.description}>{field.description}</div>
      )}
      
      {error && (
        <div style={styles.error}>{error}</div>
      )}
    </div>
  );
};

// ========================================
// 📝 MAIN FORM COMPONENT
// ========================================

export const Form = forwardRef<FormRef, FormProps>(({
  fields = [],
  initialValues = {},
  layout = 'vertical',
  size = 'medium',
  disabled = false,
  readOnly = false,
  autoSave = false,
  autoSaveDelay = 2000,
  validateOnSubmit = true,
  validateOnChange = false,
  validateOnBlur = true,
  resetOnSubmit = false,
  multiStep = false,
  steps = [],
  currentStep: controlledCurrentStep,
  showProgress = true,
  submitText = 'Submit',
  resetText = 'Reset',
  nextText = 'Next',
  previousText = 'Previous',
  loading = false,
  submitting = false,
  className = '',
  formClassName = '',
  fieldClassName = '',
  errorClassName = '',
  onSubmit,
  onReset,
  onChange,
  onValidationChange,
  onStepChange,
  onAutoSave,
  beforeSubmit,
  afterSubmit,
  testId = 'form'
}, ref) => {
  // State management
  const [values, setValues] = useState<Record<string, any>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [currentStepInternal, setCurrentStepInternal] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(submitting);
  const [isDirty, setIsDirty] = useState(false);

  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const initialValuesRef = useRef(initialValues);

  const currentStep = controlledCurrentStep !== undefined ? controlledCurrentStep : currentStepInternal;

  // Memoized computed values
  const visibleFields = useMemo(() => {
    return fields.filter(field => {
      if (field.hidden) return false;
      if (field.showWhen && !field.showWhen(values)) return false;
      
      if (multiStep && steps.length > 0) {
        const currentStepFields = steps[currentStep]?.fields || [];
        return currentStepFields.includes(field.name);
      }
      
      return true;
    });
  }, [fields, values, multiStep, steps, currentStep]);

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0;
  }, [errors]);

  const totalSteps = multiStep ? steps.length : 1;
  const progress = multiStep ? ((currentStep + 1) / totalSteps) * 100 : 100;

  // Validation
  const validateAllFields = useCallback(async (): Promise<boolean> => {
    const newErrors: Record<string, string> = {};
    
    for (const field of visibleFields) {
      const error = await validateField(field, values[field.name], values);
      if (error) {
        newErrors[field.name] = error;
      }
    }
    
    setErrors(newErrors);
    onValidationChange?.(newErrors, Object.keys(newErrors).length === 0, {
      getValues: () => values,
      getErrors: () => newErrors
    } as FormRef);
    
    return Object.keys(newErrors).length === 0;
  }, [visibleFields, values, onValidationChange]);

  const validateField = useCallback(async (fieldName: string): Promise<void> => {
    const field = fields.find(f => f.name === fieldName);
    if (!field) return;

    const error = await validateField(field, values[fieldName], values);
    
    setErrors(prev => {
      const newErrors = { ...prev };
      if (error) {
        newErrors[fieldName] = error;
      } else {
        delete newErrors[fieldName];
      }
      return newErrors;
    });
  }, [fields, values]);

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !isDirty) return;

    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }

    autoSaveTimeoutRef.current = setTimeout(() => {
      onAutoSave?.(values);
    }, autoSaveDelay);

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [values, autoSave, autoSaveDelay, isDirty, onAutoSave]);

  // Value change handler
  const handleValueChange = useCallback(async (fieldName: string, value: any) => {
    const newValues = { ...values, [fieldName]: value };
    setValues(newValues);
    setIsDirty(JSON.stringify(newValues) !== JSON.stringify(initialValuesRef.current));
    
    const field = fields.find(f => f.name === fieldName);
    
    onChange?.(newValues, fieldName, {
      getValues: () => newValues,
      setValue: (name, val) => setValues(prev => ({ ...prev, [name]: val }))
    } as FormRef);

    if (field?.onChange) {
      field.onChange(value, field);
    }

    if (validateOnChange || field?.validation?.validateOnChange) {
      const debounceMs = field?.validation?.debounceMs || 300;
      
      setTimeout(() => {
        validateField(fieldName);
      }, debounceMs);
    }
  }, [values, fields, onChange, validateOnChange]);

  // Blur handler
  const handleBlur = useCallback((fieldName: string) => {
    setTouched(prev => ({ ...prev, [fieldName]: true }));
    
    const field = fields.find(f => f.name === fieldName);
    if (field?.onBlur) {
      field.onBlur(values[fieldName], field);
    }

    if (validateOnBlur || field?.validation?.validateOnBlur) {
      validateField(fieldName);
    }
  }, [fields, values, validateOnBlur]);

  // Focus handler
  const handleFocus = useCallback((fieldName: string) => {
    const field = fields.find(f => f.name === fieldName);
    if (field?.onFocus) {
      field.onFocus(values[fieldName], field);
    }
  }, [fields, values]);

  // Form submission
  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      if (validateOnSubmit) {
        const isFormValid = await validateAllFields();
        if (!isFormValid) {
          setIsSubmitting(false);
          return;
        }
      }

      let finalValues = values;
      
      if (beforeSubmit) {
        finalValues = await beforeSubmit(values);
      }

      const result = await onSubmit?.(finalValues, {
        getValues: () => finalValues,
        isValid: () => isValid
      } as FormRef);

      if (afterSubmit) {
        afterSubmit(result, finalValues);
      }

      if (resetOnSubmit) {
        handleReset();
      }

    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [values, isSubmitting, validateOnSubmit, validateAllFields, beforeSubmit, onSubmit, afterSubmit, resetOnSubmit, isValid]);

  // Form reset
  const handleReset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsDirty(false);
    setCurrentStepInternal(0);
    onReset?.({
      getValues: () => initialValues
    } as FormRef);
  }, [initialValues, onReset]);

  // Step navigation
  const nextStep = useCallback(() => {
    if (currentStep < totalSteps - 1) {
      const newStep = currentStep + 1;
      setCurrentStepInternal(newStep);
      onStepChange?.(newStep, 'next');
    }
  }, [currentStep, totalSteps, onStepChange]);

  const previousStep = useCallback(() => {
    if (currentStep > 0) {
      const newStep = currentStep - 1;
      setCurrentStepInternal(newStep);
      onStepChange?.(newStep, 'previous');
    }
  }, [currentStep, onStepChange]);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStepInternal(step);
      onStepChange?.(step, step > currentStep ? 'next' : 'previous');
    }
  }, [totalSteps, currentStep, onStepChange]);

  // Imperative handle
  useImperativeHandle(ref, () => ({
    submit: handleSubmit,
    reset: handleReset,
    validate: validateAllFields,
    getValues: () => values,
    setValues: (newValues) => {
      setValues(newValues);
      setIsDirty(true);
    },
    getValue: (fieldName) => values[fieldName],
    setValue: (fieldName, value) => handleValueChange(fieldName, value),
    getErrors: () => errors,
    setErrors: (newErrors) => setErrors(newErrors),
    getError: (fieldName) => errors[fieldName],
    setError: (fieldName, error) => setErrors(prev => ({ ...prev, [fieldName]: error })),
    clearErrors: () => setErrors({}),
    nextStep,
    previousStep,
    goToStep,
    isValid: () => isValid,
    isDirty: () => isDirty,
    isSubmitting: () => isSubmitting
  }), [
    handleSubmit, 
    handleReset, 
    validateAllFields, 
    values, 
    handleValueChange, 
    errors, 
    nextStep, 
    previousStep, 
    goToStep, 
    isValid, 
    isDirty, 
    isSubmitting
  ]);

  const styles = getFormStyles(layout, size);

  const contextValue: FormContextType = {
    values,
    errors,
    touched,
    isSubmitting,
    layout,
    size,
    setValue: (name, value) => handleValueChange(name, value),
    setError: (name, error) => setErrors(prev => ({ ...prev, [name]: error })),
    clearError: (name) => setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[name];
      return newErrors;
    }),
    setTouched: (name, isTouched) => setTouched(prev => ({ ...prev, [name]: isTouched }))
  };

  return (
    <FormContext.Provider value={contextValue}>
      <div className={className} data-testid={testId}>
        {multiStep && showProgress && (
          <div>
            {/* Progress Bar */}
            <div style={styles.progress}>
              <div 
                style={{ 
                  ...styles.progressBar, 
                  width: `${progress}%` 
                }} 
              />
            </div>

            {/* Step Indicator */}
            <div style={styles.stepIndicator}>
              {steps.map((step, index) => (
                <div key={index} style={styles.step}>
                  <div
                    style={{
                      ...styles.stepNumber,
                      backgroundColor: index <= currentStep ? '#3b82f6' : '#e5e7eb',
                      color: index <= currentStep ? '#ffffff' : '#6b7280'
                    }}
                  >
                    {step.icon || (index + 1)}
                  </div>
                  <div style={styles.stepTitle}>{step.title}</div>
                  {step.description && (
                    <div style={styles.description}>{step.description}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <form 
          className={formClassName}
          style={styles.form}
          onSubmit={handleSubmit}
          noValidate
        >
          {visibleFields.map((field) => (
            <div
              key={field.name}
              className={fieldClassName}
              style={styles.fieldGroup}
            >
              <FormField
                field={{
                  ...field,
                  disabled: disabled || field.disabled,
                  readOnly: readOnly || field.readOnly
                }}
                value={values[field.name]}
                error={touched[field.name] ? errors[field.name] : undefined}
                onChange={(value) => handleValueChange(field.name, value)}
                onBlur={() => handleBlur(field.name)}
                onFocus={() => handleFocus(field.name)}
              />
            </div>
          ))}

          <div style={styles.buttons}>
            {multiStep && currentStep > 0 && (
              <button
                type="button"
                onClick={previousStep}
                style={{
                  ...styles.button,
                  ...styles.secondaryButton
                }}
                disabled={isSubmitting}
              >
                {previousText}
              </button>
            )}

            {multiStep && currentStep < totalSteps - 1 ? (
              <button
                type="button"
                onClick={nextStep}
                style={{
                  ...styles.button,
                  ...styles.primaryButton,
                  ...(isSubmitting && styles.disabledButton)
                }}
                disabled={isSubmitting}
              >
                {nextText}
              </button>
            ) : (
              <button
                type="submit"
                style={{
                  ...styles.button,
                  ...styles.primaryButton,
                  ...(isSubmitting && styles.disabledButton)
                }}
                disabled={isSubmitting || (!isValid && validateOnSubmit)}
              >
                {isSubmitting ? '⏳ Submitting...' : submitText}
              </button>
            )}

            <button
              type="button"
              onClick={handleReset}
              style={{
                ...styles.button,
                ...styles.secondaryButton
              }}
              disabled={isSubmitting}
            >
              {resetText}
            </button>
          </div>
        </form>

        {loading && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              border: '3px solid #f3f4f6',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
          </div>
        )}
      </div>
    </FormContext.Provider>
  );
});

Form.displayName = 'Form';

// ========================================
// 📦 EXPORTS
// ========================================

export { Form as default, FormField, useFormContext };

export type {
  FormProps,
  FormField as FormFieldType,
  FormRef,
  FormStep,
  ValidationRule,
  ValidationConfig,
  FieldOption
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Form
<Form
  fields={[
    {
      name: 'firstName',
      label: 'First Name',
      type: 'text',
      required: true,
      validation: {
        rules: [
          { type: 'required', message: 'First name is required' },
          { type: 'minLength', value: 2, message: 'Must be at least 2 characters' }
        ]
      }
    },
    {
      name: 'email',
      label: 'Email',
      type: 'email',
      required: true,
      validation: {
        rules: [
          { type: 'required' },
          { type: 'email' }
        ]
      }
    },
    {
      name: 'age',
      label: 'Age',
      type: 'number',
      validation: {
        rules: [
          { type: 'min', value: 18, message: 'Must be at least 18' },
          { type: 'max', value: 100, message: 'Must be less than 100' }
        ]
      }
    }
  ]}
  onSubmit={(values) => {
    console.log('Form submitted:', values);
  }}
  validateOnSubmit={true}
  validateOnBlur={true}
/>

// Multi-step Form
<Form
  fields={[
    { name: 'firstName', label: 'First Name', type: 'text', required: true },
    { name: 'lastName', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'phone', label: 'Phone', type: 'tel' },
    { name: 'address', label: 'Address', type: 'textarea' },
    { name: 'terms', label: 'I agree to the terms', type: 'checkbox', required: true }
  ]}
  multiStep={true}
  steps={[
    {
      title: 'Personal Info',
      fields: ['firstName', 'lastName'],
      validation: true
    },
    {
      title: 'Contact',
      fields: ['email', 'phone'],
      validation: true
    },
    {
      title: 'Address & Terms',
      fields: ['address', 'terms']
    }
  ]}
  onSubmit={(values) => console.log('Multi-step form:', values)}
  onStepChange={(step, direction) => console.log('Step changed:', step, direction)}
/>

// Form with Dynamic Fields
<Form
  fields={[
    {
      name: 'userType',
      label: 'User Type',
      type: 'select',
      options: [
        { label: 'Individual', value: 'individual' },
        { label: 'Business', value: 'business' }
      ],
      required: true
    },
    {
      name: 'companyName',
      label: 'Company Name',
      type: 'text',
      showWhen: (values) => values.userType === 'business',
      required: true
    },
    {
      name: 'taxId',
      label: 'Tax ID',
      type: 'text',
      showWhen: (values) => values.userType === 'business'
    }
  ]}
  onSubmit={(values) => console.log('Dynamic form:', values)}
/>

// Form with Custom Validation
<Form
  fields={[
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      required: true,
      validation: {
        rules: [
          { type: 'minLength', value: 8 },
          {
            type: 'custom',
            validator: (value) => {
              const hasNumber = /\d/.test(value);
              const hasUpper = /[A-Z]/.test(value);
              const hasLower = /[a-z]/.test(value);
              
              if (!hasNumber || !hasUpper || !hasLower) {
                return 'Password must contain uppercase, lowercase, and numbers';
              }
              return true;
            }
          }
        ]
      }
    },
    {
      name: 'confirmPassword',
      label: 'Confirm Password',
      type: 'password',
      required: true,
      validation: {
        rules: [
          {
            type: 'custom',
            validator: (value, values) => {
              return value === values.password || 'Passwords do not match';
            }
          }
        ]
      }
    }
  ]}
  onSubmit={(values) => console.log('Form with validation:', values)}
/>

// Form with Auto-save
<Form
  fields={formFields}
  autoSave={true}
  autoSaveDelay={3000}
  onAutoSave={(values) => {
    localStorage.setItem('form-draft', JSON.stringify(values));
    console.log('Auto-saved:', values);
  }}
  initialValues={JSON.parse(localStorage.getItem('form-draft') || '{}')}
  onSubmit={(values) => console.log('Form submitted:', values)}
/>
*/