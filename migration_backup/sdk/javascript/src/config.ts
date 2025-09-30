/**
 * SDK Configuration Management
 * 
 * Enterprise configuration with multi-expert design:
 * - DevOps: Environment-specific configuration management
 * - Sécurité: Secure configuration validation
 * - Backend Senior: Robust configuration patterns
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 */

import { AinflueClientOptions } from './types';

/**
 * SDK Configuration interface
 */
export interface AinflueConfig extends AinflueClientOptions {
  // Additional config properties
  debug?: boolean;
  retryConfig?: {
    maxRetries: number;
    retryDelay: number;
    exponentialBackoff: boolean;
  };
  cacheConfig?: {
    enabled: boolean;
    ttl: number;
    maxSize: number;
    storageType: 'memory' | 'localStorage' | 'sessionStorage';
  };
  rateLimitConfig?: {
    enabled: boolean;
    requestsPerSecond: number;
    burstLimit: number;
  };
}

/**
 * Environment-specific configurations
 */
const ENVIRONMENT_CONFIGS: Record<string, Partial<AinflueConfig>> = {
  production: {
    baseUrl: 'https://api.ainflue.com',
    timeout: 30000,
    enableLogging: false,
    debug: false,
    retryConfig: {
      maxRetries: 3,
      retryDelay: 1000,
      exponentialBackoff: true
    },
    cacheConfig: {
      enabled: true,
      ttl: 300000, // 5 minutes
      maxSize: 100,
      storageType: 'memory'
    },
    rateLimitConfig: {
      enabled: true,
      requestsPerSecond: 10,
      burstLimit: 50
    }
  },
  
  staging: {
    baseUrl: 'https://staging-api.ainflue.com',
    timeout: 30000,
    enableLogging: true,
    debug: true,
    retryConfig: {
      maxRetries: 2,
      retryDelay: 500,
      exponentialBackoff: true
    },
    cacheConfig: {
      enabled: true,
      ttl: 60000, // 1 minute
      maxSize: 50,
      storageType: 'memory'
    },
    rateLimitConfig: {
      enabled: false,
      requestsPerSecond: 20,
      burstLimit: 100
    }
  },
  
  development: {
    baseUrl: 'http://localhost:3000',
    timeout: 60000,
    enableLogging: true,
    debug: true,
    retryConfig: {
      maxRetries: 1,
      retryDelay: 100,
      exponentialBackoff: false
    },
    cacheConfig: {
      enabled: false,
      ttl: 30000, // 30 seconds
      maxSize: 10,
      storageType: 'memory'
    },
    rateLimitConfig: {
      enabled: false,
      requestsPerSecond: 100,
      burstLimit: 1000
    }
  }
};

/**
 * Default configuration
 */
const DEFAULT_CONFIG: AinflueConfig = {
  baseUrl: 'https://api.ainflue.com',
  apiVersion: 'v1',
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
  enableLogging: true,
  enableCaching: true,
  enableMetrics: true,
  customHeaders: {},
  authProvider: 'api_key',
  environment: 'production',
  debug: false,
  
  retryConfig: {
    maxRetries: 3,
    retryDelay: 1000,
    exponentialBackoff: true
  },
  
  cacheConfig: {
    enabled: true,
    ttl: 300000,
    maxSize: 100,
    storageType: 'memory'
  },
  
  rateLimitConfig: {
    enabled: true,
    requestsPerSecond: 10,
    burstLimit: 50
  }
};

/**
 * Configuration validator
 */
class ConfigValidator {
  /**
   * Validate API key format
   */
  static validateApiKey(apiKey: string): boolean {
    if (!apiKey || typeof apiKey !== 'string') {
      return false;
    }
    
    // Basic validation - should be at least 20 characters
    if (apiKey.length < 20) {
      return false;
    }
    
    // Should not contain spaces
    if (apiKey.includes(' ')) {
      return false;
    }
    
    return true;
  }
  
  /**
   * Validate base URL format
   */
  static validateBaseUrl(baseUrl: string): boolean {
    try {
      const url = new URL(baseUrl);
      return ['http:', 'https:'].includes(url.protocol);
    } catch {
      return false;
    }
  }
  
  /**
   * Validate timeout value
   */
  static validateTimeout(timeout: number): boolean {
    return typeof timeout === 'number' && timeout > 0 && timeout <= 300000; // Max 5 minutes
  }
  
  /**
   * Validate retry configuration
   */
  static validateRetryConfig(retryConfig: any): boolean {
    if (!retryConfig || typeof retryConfig !== 'object') {
      return false;
    }
    
    const { maxRetries, retryDelay } = retryConfig;
    
    return (
      typeof maxRetries === 'number' &&
      maxRetries >= 0 &&
      maxRetries <= 10 &&
      typeof retryDelay === 'number' &&
      retryDelay >= 0 &&
      retryDelay <= 60000
    );
  }
  
  /**
   * Validate cache configuration
   */
  static validateCacheConfig(cacheConfig: any): boolean {
    if (!cacheConfig || typeof cacheConfig !== 'object') {
      return false;
    }
    
    const { ttl, maxSize, storageType } = cacheConfig;
    
    return (
      typeof ttl === 'number' &&
      ttl >= 0 &&
      typeof maxSize === 'number' &&
      maxSize >= 0 &&
      ['memory', 'localStorage', 'sessionStorage'].includes(storageType)
    );
  }
  
  /**
   * Validate complete configuration
   */
  static validate(config: AinflueConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Required fields
    if (config.apiKey && !this.validateApiKey(config.apiKey)) {
      errors.push('Invalid API key format');
    }
    
    if (config.baseUrl && !this.validateBaseUrl(config.baseUrl)) {
      errors.push('Invalid base URL format');
    }
    
    if (config.timeout && !this.validateTimeout(config.timeout)) {
      errors.push('Invalid timeout value (must be between 1ms and 5 minutes)');
    }
    
    // Optional configurations
    if (config.retryConfig && !this.validateRetryConfig(config.retryConfig)) {
      errors.push('Invalid retry configuration');
    }
    
    if (config.cacheConfig && !this.validateCacheConfig(config.cacheConfig)) {
      errors.push('Invalid cache configuration');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

/**
 * Configuration manager
 */
export class ConfigManager {
  private config: AinflueConfig;
  
  constructor(userConfig: Partial<AinflueConfig> = {}) {
    this.config = this.createConfig(userConfig);
  }
  
  /**
   * Create configuration from user input
   */
  private createConfig(userConfig: Partial<AinflueConfig>): AinflueConfig {
    // Start with default config
    let config = { ...DEFAULT_CONFIG };
    
    // Apply environment-specific config if specified
    if (userConfig.environment && ENVIRONMENT_CONFIGS[userConfig.environment]) {
      config = {
        ...config,
        ...ENVIRONMENT_CONFIGS[userConfig.environment]
      };
    }
    
    // Apply user config
    config = {
      ...config,
      ...userConfig
    };
    
    // Merge nested configurations
    if (userConfig.retryConfig) {
      config.retryConfig = {
        ...config.retryConfig,
        ...userConfig.retryConfig
      };
    }
    
    if (userConfig.cacheConfig) {
      config.cacheConfig = {
        ...config.cacheConfig,
        ...userConfig.cacheConfig
      };
    }
    
    if (userConfig.rateLimitConfig) {
      config.rateLimitConfig = {
        ...config.rateLimitConfig,
        ...userConfig.rateLimitConfig
      };
    }
    
    // Validate configuration
    const validation = ConfigValidator.validate(config);
    if (!validation.valid) {
      throw new Error(`Invalid configuration: ${validation.errors.join(', ')}`);
    }
    
    return config;
  }
  
  /**
   * Get configuration value
   */
  get<K extends keyof AinflueConfig>(key: K): AinflueConfig[K] {
    return this.config[key];
  }
  
  /**
   * Set configuration value
   */
  set<K extends keyof AinflueConfig>(key: K, value: AinflueConfig[K]): void {
    this.config[key] = value;
    
    // Re-validate after change
    const validation = ConfigValidator.validate(this.config);
    if (!validation.valid) {
      throw new Error(`Invalid configuration after update: ${validation.errors.join(', ')}`);
    }
  }
  
  /**
   * Get all configuration
   */
  getAll(): AinflueConfig {
    return { ...this.config };
  }
  
  /**
   * Update multiple configuration values
   */
  update(updates: Partial<AinflueConfig>): void {
    const newConfig = {
      ...this.config,
      ...updates
    };
    
    // Validate new configuration
    const validation = ConfigValidator.validate(newConfig);
    if (!validation.valid) {
      throw new Error(`Invalid configuration update: ${validation.errors.join(', ')}`);
    }
    
    this.config = newConfig;
  }
  
  /**
   * Reset to default configuration
   */
  reset(): void {
    this.config = { ...DEFAULT_CONFIG };
  }
  
  /**
   * Clone configuration manager
   */
  clone(): ConfigManager {
    return new ConfigManager(this.config);
  }
  
  /**
   * Export configuration for debugging
   */
  toJSON(): object {
    const config = { ...this.config };
    
    // Mask sensitive information
    if (config.apiKey) {
      config.apiKey = config.apiKey.substring(0, 8) + '...';
    }
    
    return config;
  }
}

/**
 * Create default configuration
 */
export function createDefaultConfig(environment?: string): AinflueConfig {
  const envConfig = environment ? ENVIRONMENT_CONFIGS[environment] : {};
  
  return {
    ...DEFAULT_CONFIG,
    ...envConfig,
    environment: environment || 'production'
  };
}

/**
 * Create configuration from environment variables
 */
export function createConfigFromEnv(): Partial<AinflueConfig> {
  const config: Partial<AinflueConfig> = {};
  
  // Check for environment variables (Node.js)
  if (typeof process !== 'undefined' && process.env) {
    if (process.env.AINFLUE_API_KEY) {
      config.apiKey = process.env.AINFLUE_API_KEY;
    }
    
    if (process.env.AINFLUE_BASE_URL) {
      config.baseUrl = process.env.AINFLUE_BASE_URL;
    }
    
    if (process.env.AINFLUE_ENVIRONMENT) {
      config.environment = process.env.AINFLUE_ENVIRONMENT as any;
    }
    
    if (process.env.AINFLUE_TIMEOUT) {
      config.timeout = parseInt(process.env.AINFLUE_TIMEOUT, 10);
    }
    
    if (process.env.AINFLUE_DEBUG) {
      config.debug = process.env.AINFLUE_DEBUG === 'true';
    }
  }
  
  return config;
}

/**
 * Merge configurations with precedence
 */
export function mergeConfigs(...configs: Partial<AinflueConfig>[]): AinflueConfig {
  let mergedConfig = { ...DEFAULT_CONFIG };
  
  for (const config of configs) {
    mergedConfig = {
      ...mergedConfig,
      ...config
    };
    
    // Deep merge nested objects
    if (config.retryConfig) {
      mergedConfig.retryConfig = {
        ...mergedConfig.retryConfig,
        ...config.retryConfig
      };
    }
    
    if (config.cacheConfig) {
      mergedConfig.cacheConfig = {
        ...mergedConfig.cacheConfig,
        ...config.cacheConfig
      };
    }
    
    if (config.rateLimitConfig) {
      mergedConfig.rateLimitConfig = {
        ...mergedConfig.rateLimitConfig,
        ...config.rateLimitConfig
      };
    }
  }
  
  return mergedConfig;
}

// Export configuration utilities
export {
  DEFAULT_CONFIG,
  ENVIRONMENT_CONFIGS,
  ConfigValidator
};