/**
 * Validation Library
 */

interface ValidationRule {
  test: (value: any) => boolean;
  message: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

class Validator {
  private rules: ValidationRule[] = [];

  required(message = 'This field is required'): Validator {
    this.rules.push({
      test: (value) => value !== null && value !== undefined && value !== '',
      message,
    });
    return this;
  }

  minLength(length: number, message?: string): Validator {
    this.rules.push({
      test: (value) => typeof value === 'string' && value.length >= length,
      message: message || `Must be at least ${length} characters`,
    });
    return this;
  }

  maxLength(length: number, message?: string): Validator {
    this.rules.push({
      test: (value) => typeof value === 'string' && value.length <= length,
      message: message || `Must be no more than ${length} characters`,
    });
    return this;
  }

  email(message = 'Must be a valid email address'): Validator {
    this.rules.push({
      test: (value) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return typeof value === 'string' && emailRegex.test(value);
      },
      message,
    });
    return this;
  }

  numeric(message = 'Must be a number'): Validator {
    this.rules.push({
      test: (value) => !isNaN(Number(value)),
      message,
    });
    return this;
  }

  min(minimum: number, message?: string): Validator {
    this.rules.push({
      test: (value) => Number(value) >= minimum,
      message: message || `Must be at least ${minimum}`,
    });
    return this;
  }

  max(maximum: number, message?: string): Validator {
    this.rules.push({
      test: (value) => Number(value) <= maximum,
      message: message || `Must be no more than ${maximum}`,
    });
    return this;
  }

  pattern(regex: RegExp, message = 'Invalid format'): Validator {
    this.rules.push({
      test: (value) => typeof value === 'string' && regex.test(value),
      message,
    });
    return this;
  }

  custom(test: (value: any) => boolean, message: string): Validator {
    this.rules.push({ test, message });
    return this;
  }

  validate(value: any): ValidationResult {
    const errors: string[] = [];

    for (const rule of this.rules) {
      if (!rule.test(value)) {
        errors.push(rule.message);
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  static create(): Validator {
    return new Validator();
  }
}

export { Validator, type ValidationResult };
export default Validator;
