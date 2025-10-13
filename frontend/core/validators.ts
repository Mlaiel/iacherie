/**
 * 🔍 Validation Schemas - Enterprise Data Validation System
 * 
 * @fileoverview Comprehensive validation schemas for all platform data structures
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  score: number; // 0-100 validation score
}

export interface ValidationError {
  field: string;
  code: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  suggestion?: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  impact: 'performance' | 'security' | 'usability' | 'seo';
}

export interface ValidationSchema {
  name: string;
  version: string;
  fields: FieldValidation[];
  customRules: CustomValidationRule[];
}

export interface FieldValidation {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'date' | 'email' | 'url' | 'file';
  required: boolean;
  constraints: FieldConstraints;
  sanitization?: SanitizationRule[];
  customValidators?: string[];
}

export interface FieldConstraints {
  // String constraints
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  allowedValues?: string[];
  encoding?: 'utf8' | 'ascii' | 'base64';
  
  // Number constraints
  min?: number;
  max?: number;
  decimal?: boolean;
  precision?: number;
  
  // Array constraints
  minItems?: number;
  maxItems?: number;
  uniqueItems?: boolean;
  itemType?: string;
  
  // File constraints
  maxSize?: number; // bytes
  allowedTypes?: string[];
  dimensions?: { width: number; height: number; };
  
  // Date constraints
  minDate?: Date;
  maxDate?: Date;
  format?: string;
}

export interface SanitizationRule {
  type: 'trim' | 'lowercase' | 'uppercase' | 'escape' | 'strip_html' | 'normalize' | 'custom';
  options?: Record<string, any>;
}

export interface CustomValidationRule {
  name: string;
  description: string;
  validator: (value: any, context: any) => ValidationResult | Promise<ValidationResult>;
  async?: boolean;
}

/**
 * Core Validation Schemas
 */

// User Profile Validation
export const UserProfileSchema: ValidationSchema = {
  name: 'UserProfile',
  version: '2.1.0',
  fields: [
    {
      name: 'username',
      type: 'string',
      required: true,
      constraints: {
        minLength: 3,
        maxLength: 30,
        pattern: /^[a-zA-Z0-9_-]+$/
      },
      sanitization: [
        { type: 'trim' },
        { type: 'lowercase' }
      ]
    },
    {
      name: 'email',
      type: 'email',
      required: true,
      constraints: {
        maxLength: 320
      },
      sanitization: [
        { type: 'trim' },
        { type: 'lowercase' }
      ]
    },
    {
      name: 'displayName',
      type: 'string',
      required: true,
      constraints: {
        minLength: 1,
        maxLength: 100
      },
      sanitization: [
        { type: 'trim' },
        { type: 'escape' }
      ]
    },
    {
      name: 'bio',
      type: 'string',
      required: false,
      constraints: {
        maxLength: 500
      },
      sanitization: [
        { type: 'trim' },
        { type: 'strip_html' }
      ]
    },
    {
      name: 'avatar',
      type: 'file',
      required: false,
      constraints: {
        maxSize: 5 * 1024 * 1024, // 5MB
        allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
        dimensions: { width: 1000, height: 1000 }
      }
    }
  ],
  customRules: [
    {
      name: 'unique_username',
      description: 'Username must be unique across platform',
      validator: async (value: string) => {
        // Simulate database check
        const exists = await checkUsernameExists(value);
        return {
          isValid: !exists,
          errors: exists ? [{
            field: 'username',
            code: 'DUPLICATE_USERNAME',
            message: 'Username is already taken',
            severity: 'high' as const,
            suggestion: 'Try adding numbers or underscores'
          }] : [],
          warnings: [],
          score: exists ? 0 : 100
        };
      },
      async: true
    }
  ]
};

// Content Upload Validation
export const ContentUploadSchema: ValidationSchema = {
  name: 'ContentUpload',
  version: '3.0.0',
  fields: [
    {
      name: 'title',
      type: 'string',
      required: true,
      constraints: {
        minLength: 3,
        maxLength: 200
      },
      sanitization: [
        { type: 'trim' },
        { type: 'escape' }
      ]
    },
    {
      name: 'description',
      type: 'string',
      required: false,
      constraints: {
        maxLength: 5000
      },
      sanitization: [
        { type: 'trim' },
        { type: 'strip_html' }
      ]
    },
    {
      name: 'tags',
      type: 'array',
      required: false,
      constraints: {
        maxItems: 20,
        uniqueItems: true,
        itemType: 'string'
      }
    },
    {
      name: 'category',
      type: 'string',
      required: true,
      constraints: {
        allowedValues: ['music', 'podcast', 'video', 'blog', 'photo', 'document']
      }
    },
    {
      name: 'file',
      type: 'file',
      required: true,
      constraints: {
        maxSize: 500 * 1024 * 1024, // 500MB
        allowedTypes: [
          'audio/mpeg', 'audio/wav', 'audio/flac',
          'video/mp4', 'video/webm',
          'image/jpeg', 'image/png', 'image/webp',
          'application/pdf', 'text/plain'
        ]
      }
    },
    {
      name: 'privacy',
      type: 'string',
      required: true,
      constraints: {
        allowedValues: ['public', 'private', 'unlisted', 'members_only']
      }
    },
    {
      name: 'monetization',
      type: 'object',
      required: false,
      constraints: {}
    }
  ],
  customRules: [
    {
      name: 'content_safety',
      description: 'Content must pass safety and appropriateness checks',
      validator: (content: any) => {
        const issues = performContentSafetyCheck(content);
        return {
          isValid: issues.length === 0,
          errors: issues.map(issue => ({
            field: 'content',
            code: issue.code,
            message: issue.message,
            severity: issue.severity,
            suggestion: issue.suggestion
          })),
          warnings: [],
          score: Math.max(0, 100 - (issues.length * 20))
        };
      }
    }
  ]
};

// API Request Validation
export const APIRequestSchema: ValidationSchema = {
  name: 'APIRequest',
  version: '1.5.0',
  fields: [
    {
      name: 'endpoint',
      type: 'string',
      required: true,
      constraints: {
        pattern: /^\/api\/v\d+\/[a-zA-Z0-9\/_-]+$/
      }
    },
    {
      name: 'method',
      type: 'string',
      required: true,
      constraints: {
        allowedValues: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
      }
    },
    {
      name: 'headers',
      type: 'object',
      required: false,
      constraints: {}
    },
    {
      name: 'body',
      type: 'object',
      required: false,
      constraints: {}
    },
    {
      name: 'params',
      type: 'object',
      required: false,
      constraints: {}
    }
  ],
  customRules: [
    {
      name: 'rate_limit_check',
      description: 'Request must not exceed rate limits',
      validator: (request: any) => {
        const withinLimits = checkRateLimit(request);
        return {
          isValid: withinLimits,
          errors: withinLimits ? [] : [{
            field: 'request',
            code: 'RATE_LIMIT_EXCEEDED',
            message: 'Too many requests',
            severity: 'medium' as const,
            suggestion: 'Wait before retrying'
          }],
          warnings: [],
          score: withinLimits ? 100 : 0
        };
      }
    }
  ]
};

// AI Processing Request Validation
export const AIProcessingSchema: ValidationSchema = {
  name: 'AIProcessing',
  version: '2.0.0',
  fields: [
    {
      name: 'contentId',
      type: 'string',
      required: true,
      constraints: {
        pattern: /^[a-zA-Z0-9_-]+$/,
        minLength: 10,
        maxLength: 50
      }
    },
    {
      name: 'processingType',
      type: 'string',
      required: true,
      constraints: {
        allowedValues: ['enhancement', 'analysis', 'transformation', 'generation']
      }
    },
    {
      name: 'priority',
      type: 'string',
      required: false,
      constraints: {
        allowedValues: ['low', 'normal', 'high', 'urgent']
      }
    },
    {
      name: 'parameters',
      type: 'object',
      required: true,
      constraints: {}
    }
  ],
  customRules: [
    {
      name: 'processing_quota_check',
      description: 'User must have sufficient processing quota',
      validator: (request: any) => {
        const hasQuota = checkProcessingQuota(request.userId, request.processingType);
        return {
          isValid: hasQuota,
          errors: hasQuota ? [] : [{
            field: 'quota',
            code: 'INSUFFICIENT_QUOTA',
            message: 'Processing quota exceeded',
            severity: 'high' as const,
            suggestion: 'Upgrade plan or wait for quota renewal'
          }],
          warnings: [],
          score: hasQuota ? 100 : 0
        };
      }
    }
  ]
};

/**
 * Validation Engine
 */
export class ValidationEngine {
  private schemas: Map<string, ValidationSchema> = new Map();
  private customValidators: Map<string, Function> = new Map();

  constructor() {
    this.registerDefaultSchemas();
    this.registerDefaultValidators();
  }

  /**
   * Register validation schema
   */
  registerSchema(schema: ValidationSchema): void {
    this.schemas.set(schema.name, schema);
  }

  /**
   * Validate data against schema
   */
  async validate(data: any, schemaName: string): Promise<ValidationResult> {
    const schema = this.schemas.get(schemaName);
    if (!schema) {
      return {
        isValid: false,
        errors: [{
          field: 'schema',
          code: 'SCHEMA_NOT_FOUND',
          message: `Schema '${schemaName}' not found`,
          severity: 'critical'
        }],
        warnings: [],
        score: 0
      };
    }

    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    let totalScore = 0;
    let fieldCount = 0;

    // Validate each field
    for (const field of schema.fields) {
      const fieldResult = await this.validateField(data[field.name], field, data);
      errors.push(...fieldResult.errors);
      warnings.push(...fieldResult.warnings);
      totalScore += fieldResult.score;
      fieldCount++;
    }

    // Run custom rules
    for (const rule of schema.customRules) {
      try {
        const ruleResult = rule.async 
          ? await rule.validator(data, { schema })
          : rule.validator(data, { schema });
        
        // Handle both sync and async results
        const resolvedResult = await Promise.resolve(ruleResult);
        errors.push(...resolvedResult.errors);
        warnings.push(...resolvedResult.warnings);
        totalScore += resolvedResult.score;
        fieldCount++;
      } catch (error) {
        errors.push({
          field: 'custom_rule',
          code: 'VALIDATION_ERROR',
          message: `Custom rule '${rule.name}' failed: ${error}`,
          severity: 'medium'
        });
      }
    }

    const avgScore = fieldCount > 0 ? totalScore / fieldCount : 0;
    
    return {
      isValid: errors.filter(e => e.severity === 'critical' || e.severity === 'high').length === 0,
      errors,
      warnings,
      score: Math.round(avgScore)
    };
  }

  /**
   * Sanitize data according to schema
   */
  sanitize(data: any, schemaName: string): any {
    const schema = this.schemas.get(schemaName);
    if (!schema) return data;

    const sanitized = { ...data };

    for (const field of schema.fields) {
      if (sanitized[field.name] && field.sanitization) {
        sanitized[field.name] = this.applySanitization(sanitized[field.name], field.sanitization);
      }
    }

    return sanitized;
  }

  /**
   * Validate individual field
   */
  private async validateField(value: any, field: FieldValidation, context: any): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    let score = 100;

    // Check required
    if (field.required && (value === undefined || value === null || value === '')) {
      errors.push({
        field: field.name,
        code: 'REQUIRED_FIELD',
        message: `Field '${field.name}' is required`,
        severity: 'high',
        suggestion: 'Provide a value for this field'
      });
      score = 0;
    }

    if (value === undefined || value === null) {
      return { isValid: errors.length === 0, errors, warnings, score };
    }

    // Type validation
    if (!this.validateType(value, field.type)) {
      errors.push({
        field: field.name,
        code: 'INVALID_TYPE',
        message: `Field '${field.name}' must be of type ${field.type}`,
        severity: 'high',
        suggestion: `Convert value to ${field.type}`
      });
      score -= 30;
    }

    // Constraint validation
    const constraintResult = this.validateConstraints(value, field.constraints, field.name);
    errors.push(...constraintResult.errors);
    warnings.push(...constraintResult.warnings);
    score -= constraintResult.penalty;

    // Custom validators
    if (field.customValidators) {
      for (const validatorName of field.customValidators) {
        const validator = this.customValidators.get(validatorName);
        if (validator) {
          try {
            const result = await validator(value, context);
            if (!result.isValid) {
              errors.push(...result.errors);
              score -= 20;
            }
          } catch (error) {
            errors.push({
              field: field.name,
              code: 'VALIDATOR_ERROR',
              message: `Custom validator '${validatorName}' failed`,
              severity: 'medium'
            });
          }
        }
      }
    }

    return {
      isValid: errors.filter(e => e.severity === 'critical' || e.severity === 'high').length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }

  /**
   * Validate data type
   */
  private validateType(value: any, type: string): boolean {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'array':
        return Array.isArray(value);
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      case 'date':
        return value instanceof Date || !isNaN(Date.parse(value));
      case 'email':
        return typeof value === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
      case 'url':
        return typeof value === 'string' && /^https?:\/\/.+/.test(value);
      case 'file':
        return value instanceof File || (typeof value === 'object' && value.type && value.size);
      default:
        return true;
    }
  }

  /**
   * Validate field constraints
   */
  private validateConstraints(value: any, constraints: FieldConstraints, fieldName: string): {
    errors: ValidationError[];
    warnings: ValidationWarning[];
    penalty: number;
  } {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    let penalty = 0;

    // String constraints
    if (typeof value === 'string') {
      if (constraints.minLength && value.length < constraints.minLength) {
        errors.push({
          field: fieldName,
          code: 'MIN_LENGTH',
          message: `Minimum length is ${constraints.minLength}`,
          severity: 'medium',
          suggestion: `Add ${constraints.minLength - value.length} more characters`
        });
        penalty += 20;
      }

      if (constraints.maxLength && value.length > constraints.maxLength) {
        errors.push({
          field: fieldName,
          code: 'MAX_LENGTH',
          message: `Maximum length is ${constraints.maxLength}`,
          severity: 'medium',
          suggestion: `Remove ${value.length - constraints.maxLength} characters`
        });
        penalty += 20;
      }

      if (constraints.pattern && !constraints.pattern.test(value)) {
        errors.push({
          field: fieldName,
          code: 'INVALID_PATTERN',
          message: 'Value does not match required pattern',
          severity: 'medium',
          suggestion: 'Check the format requirements'
        });
        penalty += 25;
      }

      if (constraints.allowedValues && !constraints.allowedValues.includes(value)) {
        errors.push({
          field: fieldName,
          code: 'INVALID_VALUE',
          message: `Value must be one of: ${constraints.allowedValues.join(', ')}`,
          severity: 'medium',
          suggestion: `Choose from allowed values`
        });
        penalty += 30;
      }
    }

    // Number constraints
    if (typeof value === 'number') {
      if (constraints.min !== undefined && value < constraints.min) {
        errors.push({
          field: fieldName,
          code: 'MIN_VALUE',
          message: `Minimum value is ${constraints.min}`,
          severity: 'medium'
        });
        penalty += 20;
      }

      if (constraints.max !== undefined && value > constraints.max) {
        errors.push({
          field: fieldName,
          code: 'MAX_VALUE',
          message: `Maximum value is ${constraints.max}`,
          severity: 'medium'
        });
        penalty += 20;
      }
    }

    // Array constraints
    if (Array.isArray(value)) {
      if (constraints.minItems && value.length < constraints.minItems) {
        errors.push({
          field: fieldName,
          code: 'MIN_ITEMS',
          message: `Minimum ${constraints.minItems} items required`,
          severity: 'medium'
        });
        penalty += 15;
      }

      if (constraints.maxItems && value.length > constraints.maxItems) {
        errors.push({
          field: fieldName,
          code: 'MAX_ITEMS',
          message: `Maximum ${constraints.maxItems} items allowed`,
          severity: 'medium'
        });
        penalty += 15;
      }

      if (constraints.uniqueItems) {
        const unique = new Set(value);
        if (unique.size !== value.length) {
          warnings.push({
            field: fieldName,
            message: 'Duplicate items detected',
            impact: 'usability'
          });
          penalty += 10;
        }
      }
    }

    // File constraints
    if (value instanceof File || (typeof value === 'object' && value.size)) {
      if (constraints.maxSize && value.size > constraints.maxSize) {
        errors.push({
          field: fieldName,
          code: 'FILE_TOO_LARGE',
          message: `File size exceeds ${this.formatFileSize(constraints.maxSize)}`,
          severity: 'high',
          suggestion: 'Compress the file or choose a smaller one'
        });
        penalty += 30;
      }

      if (constraints.allowedTypes && !constraints.allowedTypes.includes(value.type)) {
        errors.push({
          field: fieldName,
          code: 'INVALID_FILE_TYPE',
          message: `File type '${value.type}' not allowed`,
          severity: 'high',
          suggestion: `Use one of: ${constraints.allowedTypes.join(', ')}`
        });
        penalty += 25;
      }
    }

    return { errors, warnings, penalty };
  }

  /**
   * Apply sanitization rules
   */
  private applySanitization(value: any, rules: SanitizationRule[]): any {
    let sanitized = value;

    for (const rule of rules) {
      switch (rule.type) {
        case 'trim':
          if (typeof sanitized === 'string') {
            sanitized = sanitized.trim();
          }
          break;
        case 'lowercase':
          if (typeof sanitized === 'string') {
            sanitized = sanitized.toLowerCase();
          }
          break;
        case 'uppercase':
          if (typeof sanitized === 'string') {
            sanitized = sanitized.toUpperCase();
          }
          break;
        case 'escape':
          if (typeof sanitized === 'string') {
            sanitized = sanitized
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#x27;');
          }
          break;
        case 'strip_html':
          if (typeof sanitized === 'string') {
            sanitized = sanitized.replace(/<[^>]*>/g, '');
          }
          break;
      }
    }

    return sanitized;
  }

  /**
   * Format file size for human reading
   */
  private formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Register default schemas
   */
  private registerDefaultSchemas(): void {
    this.registerSchema(UserProfileSchema);
    this.registerSchema(ContentUploadSchema);
    this.registerSchema(APIRequestSchema);
    this.registerSchema(AIProcessingSchema);
  }

  /**
   * Register default validators
   */
  private registerDefaultValidators(): void {
    this.customValidators.set('profanity_check', (value: string) => {
      const hasProfanity = checkProfanity(value);
      return {
        isValid: !hasProfanity,
        errors: hasProfanity ? [{
          field: 'content',
          code: 'PROFANITY_DETECTED',
          message: 'Inappropriate language detected',
          severity: 'high' as const,
          suggestion: 'Remove inappropriate content'
        }] : [],
        warnings: [],
        score: hasProfanity ? 0 : 100
      };
    });

    this.customValidators.set('spam_check', (value: string) => {
      const isSpam = checkSpam(value);
      return {
        isValid: !isSpam,
        errors: isSpam ? [{
          field: 'content',
          code: 'SPAM_DETECTED',
          message: 'Content appears to be spam',
          severity: 'medium' as const,
          suggestion: 'Make content more meaningful and unique'
        }] : [],
        warnings: [],
        score: isSpam ? 20 : 100
      };
    });
  }
}

// Utility functions (simplified implementations)
async function checkUsernameExists(username: string): Promise<boolean> {
  // Simulate database check
  return Math.random() > 0.8;
}

function performContentSafetyCheck(content: any): Array<{code: string; message: string; severity: 'low' | 'medium' | 'high' | 'critical'; suggestion?: string}> {
  // Simulate safety check
  return Math.random() > 0.9 ? [{
    code: 'INAPPROPRIATE_CONTENT',
    message: 'Content may contain inappropriate material',
    severity: 'high',
    suggestion: 'Review and modify content'
  }] : [];
}

function checkRateLimit(request: any): boolean {
  // Simulate rate limit check
  return Math.random() > 0.1;
}

function checkProcessingQuota(userId: string, processingType: string): boolean {
  // Simulate quota check
  return Math.random() > 0.2;
}

function checkProfanity(text: string): boolean {
  // Simplified profanity check
  const profanityWords = ['badword1', 'badword2'];
  return profanityWords.some(word => text.toLowerCase().includes(word));
}

function checkSpam(text: string): boolean {
  // Simplified spam check
  return text.length > 1000 && /(.)\1{10,}/.test(text);
}

// Singleton instance
export const validationEngine = new ValidationEngine();

// React hooks for validation
export function useValidation() {
  const validate = async (data: any, schemaName: string) => {
    return validationEngine.validate(data, schemaName);
  };

  const sanitize = (data: any, schemaName: string) => {
    return validationEngine.sanitize(data, schemaName);
  };

  return { validate, sanitize };
}

export default ValidationEngine;