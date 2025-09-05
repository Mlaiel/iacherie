"""Environment Validator
=======================

Validation system for environment configurations to ensure compliance,
security, and operational requirements for the IA-Influencer Agent Platform.

Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, Any, List, Tuple, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class EnvironmentValidator:
    """Environment configuration validator"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, environment: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate environment configuration"""
        self.errors.clear()
        self.warnings.clear()
        
        try:
            if not config:
                config = self._get_environment_config(environment)
            
            # Run validation checks
            self._validate_basic_structure(config)
            self._validate_security_settings(config, environment)
            self._validate_database_config(config)
            self._validate_redis_config(config)
            self._validate_api_config(config)
            self._validate_ai_ml_config(config)
            self._validate_storage_config(config)
            self._validate_monitoring_config(config)
            self._validate_external_services(config)
            self._validate_environment_specific(config, environment)
            
            # Log results
            if self.errors:
                logger.error(f"Environment validation failed for {environment}: {len(self.errors)} errors")
                for error in self.errors:
                    logger.error(f"  - {error}")
                return False
            
            if self.warnings:
                logger.warning(f"Environment validation completed for {environment} with {len(self.warnings)} warnings")
                for warning in self.warnings:
                    logger.warning(f"  - {warning}")
            else:
                logger.info(f"Environment validation passed for {environment}")
            
            return True
            
        except Exception as e:
            self.errors.append(f"Validation failed with exception: {str(e)}")
            logger.error(f"Environment validation exception for {environment}: {str(e)}")
            return False
    
    def _get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for environment"""
        try:
            if environment == 'development':
                from . import development
                return development.get_config()
            elif environment == 'staging':
                from . import staging
                return staging.get_config()
            elif environment == 'production':
                from . import production
                return production.get_config()
            elif environment == 'testing':
                from . import testing
                return testing.get_config()
            else:
                raise ValidationError(f"Unknown environment: {environment}")
        except ImportError as e:
            raise ValidationError(f"Failed to import {environment} configuration: {str(e)}")
    
    def _validate_basic_structure(self, config: Dict[str, Any]) -> None:
        """Validate basic configuration structure"""
        required_keys = ['environment', 'database', 'redis', 'api', 'security']
        
        for key in required_keys:
            if key not in config:
                self.errors.append(f"Missing required configuration key: {key}")
        
        if 'environment' in config and not isinstance(config['environment'], str):
            self.errors.append("Environment must be a string")
    
    def _validate_security_settings(self, config: Dict[str, Any], environment: str) -> None:
        """Validate security configuration"""
        if 'security' not in config:
            return
        
        security_config = config['security']
        
        # Secret key validation
        if 'secret_key' not in security_config:
            self.errors.append("Missing security.secret_key")
        elif not security_config['secret_key']:
            self.errors.append("security.secret_key cannot be empty")
        elif environment == 'production' and 'test' in security_config['secret_key'].lower():
            self.errors.append("Production environment cannot use test secret key")
        
        # Password validation
        if 'password_min_length' in security_config:
            min_length = security_config['password_min_length']
            if environment == 'production' and min_length < 8:
                self.warnings.append("Production password minimum length should be at least 8 characters")
        
        # Token expiration
        if 'access_token_expire_minutes' in security_config:
            expire_minutes = security_config['access_token_expire_minutes']
            if environment == 'production' and expire_minutes > 120:
                self.warnings.append("Production token expiration seems too long for security")
    
    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Validate database configuration"""
        if 'database' not in config:
            return
        
        db_config = config['database']
        
        required_db_keys = ['host', 'port', 'username', 'password', 'database']
        for key in required_db_keys:
            if key not in db_config:
                self.errors.append(f"Missing database.{key}")
            elif not db_config[key] and key != 'password':  # Password can be empty for local dev
                self.errors.append(f"database.{key} cannot be empty")
        
        # Port validation
        if 'port' in db_config:
            try:
                port = int(db_config['port'])
                if not (1 <= port <= 65535):
                    self.errors.append("Database port must be between 1 and 65535")
            except (ValueError, TypeError):
                self.errors.append("Database port must be a valid integer")
        
        # Pool size validation
        if 'pool_size' in db_config:
            try:
                pool_size = int(db_config['pool_size'])
                if pool_size < 1:
                    self.errors.append("Database pool_size must be at least 1")
                elif pool_size > 100:
                    self.warnings.append("Database pool_size seems very high")
            except (ValueError, TypeError):
                self.errors.append("Database pool_size must be a valid integer")
    
    def _validate_redis_config(self, config: Dict[str, Any]) -> None:
        """Validate Redis configuration"""
        if 'redis' not in config:
            return
        
        redis_config = config['redis']
        
        required_redis_keys = ['host', 'port', 'db']
        for key in required_redis_keys:
            if key not in redis_config:
                self.errors.append(f"Missing redis.{key}")
        
        # Port validation
        if 'port' in redis_config:
            try:
                port = int(redis_config['port'])
                if not (1 <= port <= 65535):
                    self.errors.append("Redis port must be between 1 and 65535")
            except (ValueError, TypeError):
                self.errors.append("Redis port must be a valid integer")
        
        # Database validation
        if 'db' in redis_config:
            try:
                db = int(redis_config['db'])
                if not (0 <= db <= 15):
                    self.errors.append("Redis db must be between 0 and 15")
            except (ValueError, TypeError):
                self.errors.append("Redis db must be a valid integer")
    
    def _validate_api_config(self, config: Dict[str, Any]) -> None:
        """Validate API configuration"""
        if 'api' not in config:
            return
        
        api_config = config['api']
        
        # Port validation
        if 'port' in api_config:
            try:
                port = int(api_config['port'])
                if not (1 <= port <= 65535):
                    self.errors.append("API port must be between 1 and 65535")
            except (ValueError, TypeError):
                self.errors.append("API port must be a valid integer")
        
        # Workers validation
        if 'workers' in api_config:
            try:
                workers = int(api_config['workers'])
                if workers < 1:
                    self.errors.append("API workers must be at least 1")
                elif workers > 32:
                    self.warnings.append("API workers count seems very high")
            except (ValueError, TypeError):
                self.errors.append("API workers must be a valid integer")
    
    def _validate_ai_ml_config(self, config: Dict[str, Any]) -> None:
        """Validate AI/ML configuration"""
        if 'ai_ml' not in config:
            return
        
        ai_config = config['ai_ml']
        
        # Model cache directory
        if 'model_cache_dir' in ai_config:
            cache_dir = ai_config['model_cache_dir']
            if not cache_dir:
                self.errors.append("ai_ml.model_cache_dir cannot be empty")
            elif not os.path.isabs(cache_dir):
                self.warnings.append("ai_ml.model_cache_dir should be an absolute path")
        
        # Batch size validation
        if 'batch_size' in ai_config:
            try:
                batch_size = int(ai_config['batch_size'])
                if batch_size < 1:
                    self.errors.append("ai_ml.batch_size must be at least 1")
                elif batch_size > 1000:
                    self.warnings.append("ai_ml.batch_size seems very large")
            except (ValueError, TypeError):
                self.errors.append("ai_ml.batch_size must be a valid integer")
    
    def _validate_storage_config(self, config: Dict[str, Any]) -> None:
        """Validate storage configuration"""
        if 'storage' not in config:
            return
        
        storage_config = config['storage']
        
        # Storage type validation
        if 'type' in storage_config:
            storage_type = storage_config['type']
            if storage_type not in ['local', 's3', 'azure', 'gcp']:
                self.errors.append(f"Invalid storage type: {storage_type}")
        
        # Max file size validation
        if 'max_file_size' in storage_config:
            try:
                max_size = int(storage_config['max_file_size'])
                if max_size < 1:
                    self.errors.append("storage.max_file_size must be positive")
                elif max_size > 10 * 1024 * 1024 * 1024:  # 10GB
                    self.warnings.append("storage.max_file_size seems very large")
            except (ValueError, TypeError):
                self.errors.append("storage.max_file_size must be a valid integer")
    
    def _validate_monitoring_config(self, config: Dict[str, Any]) -> None:
        """Validate monitoring configuration"""
        if 'monitoring' not in config:
            return
        
        monitoring_config = config['monitoring']
        
        # Metrics port validation
        if 'metrics_port' in monitoring_config:
            try:
                port = int(monitoring_config['metrics_port'])
                if not (1 <= port <= 65535):
                    self.errors.append("monitoring.metrics_port must be between 1 and 65535")
            except (ValueError, TypeError):
                self.errors.append("monitoring.metrics_port must be a valid integer")
    
    def _validate_external_services(self, config: Dict[str, Any]) -> None:
        """Validate external services configuration"""
        if 'external_services' not in config:
            return
        
        # OpenAI validation
        if 'openai' in config['external_services']:
            openai_config = config['external_services']['openai']
            if 'api_key' in openai_config and not openai_config['api_key']:
                self.warnings.append("OpenAI API key is empty")
        
        # Stripe validation
        if 'stripe' in config['external_services']:
            stripe_config = config['external_services']['stripe']
            required_stripe_keys = ['publishable_key', 'secret_key']
            for key in required_stripe_keys:
                if key in stripe_config and not stripe_config[key]:
                    self.warnings.append(f"Stripe {key} is empty")
    
    def _validate_environment_specific(self, config: Dict[str, Any], environment: str) -> None:
        """Validate environment-specific requirements"""
        if environment == 'production':
            self._validate_production_requirements(config)
        elif environment == 'testing':
            self._validate_testing_requirements(config)
    
    def _validate_production_requirements(self, config: Dict[str, Any]) -> None:
        """Validate production-specific requirements"""
        # Debug mode should be disabled
        if config.get('debug', False):
            self.errors.append("Debug mode must be disabled in production")
        
        # SSL/TLS requirements
        if 'database' in config and config['database'].get('ssl_mode') != 'require':
            self.warnings.append("SSL should be required for production database")
        
        # Secret key strength
        if 'security' in config:
            secret_key = config['security'].get('secret_key', '')
            if len(secret_key) < 32:
                self.warnings.append("Production secret key should be at least 32 characters")
    
    def _validate_testing_requirements(self, config: Dict[str, Any]) -> None:
        """Validate testing-specific requirements"""
        # Testing flag should be enabled
        if not config.get('testing', False):
            self.warnings.append("Testing flag should be enabled in testing environment")
        
        # Mock services should be used
        if 'external_services' in config:
            for service, service_config in config['external_services'].items():
                if not service_config.get('use_mock', False):
                    self.warnings.append(f"Service {service} should use mocks in testing environment")
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report"""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'passed': len(self.errors) == 0
        }

# Global validator instance
def validate(environment: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Validate environment configuration"""
    validator = EnvironmentValidator()
    return validator.validate(environment, config)

def get_validation_report(environment: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get detailed validation report"""
    validator = EnvironmentValidator()
    validator.validate(environment, config)
    return validator.get_validation_report()