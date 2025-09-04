/**
 * Advanced Form Management Library
 */

interface FormField {
  name: string;
  value: any;
  error?: string;
  touched: boolean;
  validator?: (value: any) => string | null;
}

interface FormConfig {
  fields: Record<string, Omit<FormField, 'name'>>;
  onSubmit?: (values: Record<string, any>) => void | Promise<void>;
  validationMode?: 'onChange' | 'onBlur' | 'onSubmit';
}

class FormManager {
  private fields: Map<string, FormField> = new Map();
  private listeners: Set<(fields: Map<string, FormField>) => void> = new Set();
  private validationMode: 'onChange' | 'onBlur' | 'onSubmit';
  private onSubmit?: (values: Record<string, any>) => void | Promise<void>;

  constructor(config: FormConfig) {
    this.validationMode = config.validationMode || 'onBlur';
    this.onSubmit = config.onSubmit;

    Object.entries(config.fields).forEach(([name, field]) => {
      this.fields.set(name, { ...field, name });
    });
  }

  setValue(name: string, value: any): void {
    const field = this.fields.get(name);
    if (!field) return;

    const updatedField = { ...field, value };

    if (this.validationMode === 'onChange') {
      updatedField.error = this.validateField(updatedField);
    }

    this.fields.set(name, updatedField);
    this.notifyListeners();
  }

  setTouched(name: string, touched = true): void {
    const field = this.fields.get(name);
    if (!field) return;

    const updatedField = { ...field, touched };

    if (this.validationMode === 'onBlur' && touched) {
      updatedField.error = this.validateField(updatedField);
    }

    this.fields.set(name, updatedField);
    this.notifyListeners();
  }

  setError(name: string, error: string | null): void {
    const field = this.fields.get(name);
    if (!field) return;

    this.fields.set(name, { ...field, error: error || undefined });
    this.notifyListeners();
  }

  getValue(name: string): any {
    return this.fields.get(name)?.value;
  }

  getError(name: string): string | undefined {
    return this.fields.get(name)?.error;
  }

  getField(name: string): FormField | undefined {
    return this.fields.get(name);
  }

  getAllValues(): Record<string, any> {
    const values: Record<string, any> = {};
    this.fields.forEach((field, name) => {
      values[name] = field.value;
    });
    return values;
  }

  getAllErrors(): Record<string, string> {
    const errors: Record<string, string> = {};
    this.fields.forEach((field, name) => {
      if (field.error) {
        errors[name] = field.error;
      }
    });
    return errors;
  }

  isValid(): boolean {
    return Array.from(this.fields.values()).every(field => !field.error);
  }

  isDirty(): boolean {
    return Array.from(this.fields.values()).some(field => field.touched);
  }

  validate(): boolean {
    let isValid = true;

    this.fields.forEach((field, name) => {
      const error = this.validateField(field);
      if (error) {
        isValid = false;
        this.fields.set(name, { ...field, error, touched: true });
      }
    });

    this.notifyListeners();
    return isValid;
  }

  async submit(): Promise<boolean> {
    if (this.validationMode === 'onSubmit') {
      if (!this.validate()) return false;
    } else if (!this.isValid()) {
      return false;
    }

    if (this.onSubmit) {
      try {
        await this.onSubmit(this.getAllValues());
        return true;
      } catch {
        return false;
      }
    }

    return true;
  }

  reset(): void {
    this.fields.forEach((field, name) => {
      this.fields.set(name, {
        ...field,
        value: '',
        error: undefined,
        touched: false,
      });
    });
    this.notifyListeners();
  }

  subscribe(listener: (fields: Map<string, FormField>) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private validateField(field: FormField): string | null {
    if (field.validator) {
      return field.validator(field.value);
    }
    return null;
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(new Map(this.fields)));
  }
}

export { FormManager, type FormField, type FormConfig };
export default FormManager;
