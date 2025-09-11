/**
 * Ainflue Desktop - Dynamic Form Builder
 * 
 * Advanced form building system for dynamic user interfaces
 * Supports validation, real-time updates, and accessibility
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

class FormBuilder {
  constructor(options = {}) {
    this.container = options.container || document.body;
    this.themes = {
      default: 'ainflue-form-default',
      dark: 'ainflue-form-dark',
      professional: 'ainflue-form-professional'
    };
    this.currentTheme = options.theme || 'professional';
    this.validators = new Map();
    this.fields = new Map();
    this.formData = {};
    this.onDataChange = options.onDataChange || (() => {});
    this.onSubmit = options.onSubmit || (() => {});
    
    this.initializeBuilder();
  }

  /**
   * Initialize the form builder with base styles and structure
   */
  initializeBuilder() {
    this.createBaseStyles();
    this.setupEventListeners();
  }

  /**
   * Create professional styling for forms
   */
  createBaseStyles() {
    if (document.getElementById('form-builder-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'form-builder-styles';
    styles.textContent = `
      .ainflue-form-container {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        padding: 24px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }
      
      .ainflue-form-professional {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
      }
      
      .ainflue-form-dark {
        background: #2d3748;
        color: #e2e8f0;
      }
      
      .form-field-group {
        margin-bottom: 20px;
        position: relative;
      }
      
      .form-field-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
        font-size: 14px;
        color: inherit;
      }
      
      .form-field-input {
        width: 100%;
        padding: 12px 16px;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
        color: #2d3748;
      }
      
      .form-field-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
      
      .form-field-error {
        color: #e53e3e;
        font-size: 12px;
        margin-top: 4px;
        display: none;
      }
      
      .form-field-input.error {
        border-color: #e53e3e;
      }
      
      .form-submit-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 16px;
      }
      
      .form-submit-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
      }
      
      .form-submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
      
      .form-field-description {
        font-size: 12px;
        color: #718096;
        margin-top: 4px;
      }
      
      .form-field-select {
        appearance: none;
        background-image: url("data:image/svg+xml;charset=US-ASCII,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 4 5'><path fill='%23666' d='M2 0L0 2h4zm0 5L0 3h4z'/></svg>");
        background-repeat: no-repeat;
        background-position: right 12px center;
        background-size: 12px;
        padding-right: 40px;
      }
      
      .form-field-checkbox, .form-field-radio {
        margin-right: 8px;
        transform: scale(1.2);
      }
      
      .form-field-textarea {
        resize: vertical;
        min-height: 100px;
      }
    `;
    
    document.head.appendChild(styles);
  }

  /**
   * Add a field to the form
   */
  addField(config) {
    const fieldId = config.id || `field_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const field = {
      id: fieldId,
      type: config.type || 'text',
      label: config.label || '',
      placeholder: config.placeholder || '',
      required: config.required || false,
      validation: config.validation || null,
      options: config.options || [],
      defaultValue: config.defaultValue || '',
      description: config.description || '',
      attributes: config.attributes || {}
    };
    
    this.fields.set(fieldId, field);
    this.formData[fieldId] = field.defaultValue;
    
    if (field.validation) {
      this.validators.set(fieldId, field.validation);
    }
    
    return fieldId;
  }

  /**
   * Remove a field from the form
   */
  removeField(fieldId) {
    this.fields.delete(fieldId);
    this.validators.delete(fieldId);
    delete this.formData[fieldId];
    
    const fieldElement = document.getElementById(`field-group-${fieldId}`);
    if (fieldElement) {
      fieldElement.remove();
    }
  }

  /**
   * Create form field HTML element
   */
  createFieldElement(field) {
    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'form-field-group';
    fieldGroup.id = `field-group-${field.id}`;
    
    // Label
    if (field.label) {
      const label = document.createElement('label');
      label.className = 'form-field-label';
      label.textContent = field.label + (field.required ? ' *' : '');
      label.setAttribute('for', field.id);
      fieldGroup.appendChild(label);
    }
    
    // Input element
    let inputElement;
    
    switch (field.type) {
      case 'select':
        inputElement = this.createSelectElement(field);
        break;
      case 'textarea':
        inputElement = this.createTextareaElement(field);
        break;
      case 'checkbox':
        inputElement = this.createCheckboxElement(field);
        break;
      case 'radio':
        inputElement = this.createRadioElement(field);
        break;
      default:
        inputElement = this.createInputElement(field);
    }
    
    fieldGroup.appendChild(inputElement);
    
    // Description
    if (field.description) {
      const description = document.createElement('div');
      description.className = 'form-field-description';
      description.textContent = field.description;
      fieldGroup.appendChild(description);
    }
    
    // Error message
    const errorElement = document.createElement('div');
    errorElement.className = 'form-field-error';
    errorElement.id = `error-${field.id}`;
    fieldGroup.appendChild(errorElement);
    
    return fieldGroup;
  }

  /**
   * Create input element
   */
  createInputElement(field) {
    const input = document.createElement('input');
    input.type = field.type;
    input.id = field.id;
    input.name = field.id;
    input.className = 'form-field-input';
    input.placeholder = field.placeholder;
    input.value = field.defaultValue;
    
    if (field.required) {
      input.required = true;
    }
    
    // Apply custom attributes
    Object.keys(field.attributes).forEach(attr => {
      input.setAttribute(attr, field.attributes[attr]);
    });
    
    // Event listeners
    input.addEventListener('input', (e) => this.handleFieldChange(field.id, e.target.value));
    input.addEventListener('blur', (e) => this.validateField(field.id));
    
    return input;
  }

  /**
   * Create select element
   */
  createSelectElement(field) {
    const select = document.createElement('select');
    select.id = field.id;
    select.name = field.id;
    select.className = 'form-field-input form-field-select';
    
    if (field.placeholder) {
      const placeholderOption = document.createElement('option');
      placeholderOption.value = '';
      placeholderOption.textContent = field.placeholder;
      placeholderOption.disabled = true;
      placeholderOption.selected = !field.defaultValue;
      select.appendChild(placeholderOption);
    }
    
    field.options.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.value = option.value || option;
      optionElement.textContent = option.label || option;
      if (option.value === field.defaultValue || option === field.defaultValue) {
        optionElement.selected = true;
      }
      select.appendChild(optionElement);
    });
    
    select.addEventListener('change', (e) => this.handleFieldChange(field.id, e.target.value));
    select.addEventListener('blur', (e) => this.validateField(field.id));
    
    return select;
  }

  /**
   * Create textarea element
   */
  createTextareaElement(field) {
    const textarea = document.createElement('textarea');
    textarea.id = field.id;
    textarea.name = field.id;
    textarea.className = 'form-field-input form-field-textarea';
    textarea.placeholder = field.placeholder;
    textarea.value = field.defaultValue;
    
    if (field.required) {
      textarea.required = true;
    }
    
    textarea.addEventListener('input', (e) => this.handleFieldChange(field.id, e.target.value));
    textarea.addEventListener('blur', (e) => this.validateField(field.id));
    
    return textarea;
  }

  /**
   * Create checkbox element
   */
  createCheckboxElement(field) {
    const container = document.createElement('div');
    
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = field.id;
    checkbox.name = field.id;
    checkbox.className = 'form-field-checkbox';
    checkbox.checked = field.defaultValue;
    
    const label = document.createElement('label');
    label.setAttribute('for', field.id);
    label.textContent = field.label || '';
    
    container.appendChild(checkbox);
    container.appendChild(label);
    
    checkbox.addEventListener('change', (e) => this.handleFieldChange(field.id, e.target.checked));
    
    return container;
  }

  /**
   * Create radio button group
   */
  createRadioElement(field) {
    const container = document.createElement('div');
    
    field.options.forEach(option => {
      const radioContainer = document.createElement('div');
      
      const radio = document.createElement('input');
      radio.type = 'radio';
      radio.id = `${field.id}_${option.value || option}`;
      radio.name = field.id;
      radio.value = option.value || option;
      radio.className = 'form-field-radio';
      radio.checked = (option.value || option) === field.defaultValue;
      
      const label = document.createElement('label');
      label.setAttribute('for', radio.id);
      label.textContent = option.label || option;
      
      radioContainer.appendChild(radio);
      radioContainer.appendChild(label);
      container.appendChild(radioContainer);
      
      radio.addEventListener('change', (e) => {
        if (e.target.checked) {
          this.handleFieldChange(field.id, e.target.value);
        }
      });
    });
    
    return container;
  }

  /**
   * Handle field value changes
   */
  handleFieldChange(fieldId, value) {
    this.formData[fieldId] = value;
    this.clearFieldError(fieldId);
    this.onDataChange(this.formData, fieldId, value);
  }

  /**
   * Validate a specific field
   */
  validateField(fieldId) {
    const field = this.fields.get(fieldId);
    const validator = this.validators.get(fieldId);
    const value = this.formData[fieldId];
    
    // Required validation
    if (field.required && (!value || value.toString().trim() === '')) {
      this.showFieldError(fieldId, `${field.label} is required`);
      return false;
    }
    
    // Custom validation
    if (validator && value) {
      try {
        const result = validator(value, this.formData);
        if (result !== true) {
          this.showFieldError(fieldId, result);
          return false;
        }
      } catch (error) {
        this.showFieldError(fieldId, 'Validation error');
        return false;
      }
    }
    
    this.clearFieldError(fieldId);
    return true;
  }

  /**
   * Validate entire form
   */
  validateForm() {
    let isValid = true;
    
    for (const fieldId of this.fields.keys()) {
      if (!this.validateField(fieldId)) {
        isValid = false;
      }
    }
    
    return isValid;
  }

  /**
   * Show field error
   */
  showFieldError(fieldId, message) {
    const errorElement = document.getElementById(`error-${fieldId}`);
    const inputElement = document.getElementById(fieldId);
    
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
    }
    
    if (inputElement) {
      inputElement.classList.add('error');
    }
  }

  /**
   * Clear field error
   */
  clearFieldError(fieldId) {
    const errorElement = document.getElementById(`error-${fieldId}`);
    const inputElement = document.getElementById(fieldId);
    
    if (errorElement) {
      errorElement.style.display = 'none';
    }
    
    if (inputElement) {
      inputElement.classList.remove('error');
    }
  }

  /**
   * Render the complete form
   */
  render() {
    const formContainer = document.createElement('div');
    formContainer.className = `ainflue-form-container ${this.themes[this.currentTheme]}`;
    
    // Add all fields
    for (const field of this.fields.values()) {
      const fieldElement = this.createFieldElement(field);
      formContainer.appendChild(fieldElement);
    }
    
    // Add submit button
    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.className = 'form-submit-button';
    submitButton.textContent = 'Submit';
    
    submitButton.addEventListener('click', (e) => {
      e.preventDefault();
      if (this.validateForm()) {
        this.onSubmit(this.formData);
      }
    });
    
    formContainer.appendChild(submitButton);
    
    // Clear container and append form
    this.container.innerHTML = '';
    this.container.appendChild(formContainer);
    
    return formContainer;
  }

  /**
   * Get current form data
   */
  getData() {
    return { ...this.formData };
  }

  /**
   * Set form data
   */
  setData(data) {
    Object.keys(data).forEach(fieldId => {
      if (this.fields.has(fieldId)) {
        this.formData[fieldId] = data[fieldId];
        const element = document.getElementById(fieldId);
        if (element) {
          if (element.type === 'checkbox') {
            element.checked = data[fieldId];
          } else {
            element.value = data[fieldId];
          }
        }
      }
    });
  }

  /**
   * Reset form to default values
   */
  reset() {
    for (const [fieldId, field] of this.fields) {
      this.formData[fieldId] = field.defaultValue;
      this.clearFieldError(fieldId);
      
      const element = document.getElementById(fieldId);
      if (element) {
        if (element.type === 'checkbox') {
          element.checked = field.defaultValue;
        } else {
          element.value = field.defaultValue;
        }
      }
    }
  }

  /**
   * Setup global event listeners
   */
  setupEventListeners() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'Enter') {
        if (this.validateForm()) {
          this.onSubmit(this.formData);
        }
      }
    });
  }

  /**
   * Destroy the form builder
   */
  destroy() {
    this.container.innerHTML = '';
    this.fields.clear();
    this.validators.clear();
    this.formData = {};
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FormBuilder;
} else if (typeof window !== 'undefined') {
  window.FormBuilder = FormBuilder;
}

/**
 * Usage Example:
 * 
 * const formBuilder = new FormBuilder({
 *   container: document.getElementById('form-container'),
 *   theme: 'professional',
 *   onDataChange: (data, fieldId, value) => {
 *     console.log('Form data changed:', data);
 *   },
 *   onSubmit: (data) => {
 *     console.log('Form submitted:', data);
 *   }
 * });
 * 
 * formBuilder.addField({
 *   id: 'email',
 *   type: 'email',
 *   label: 'Email Address',
 *   placeholder: 'Enter your email',
 *   required: true,
 *   validation: (value) => {
 *     return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Invalid email format';
 *   }
 * });
 * 
 * formBuilder.render();
 */