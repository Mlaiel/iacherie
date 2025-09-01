"""Advanced Environment Configuration Management
===========================================

Production-ready configuration system with secrets management,
environment validation, and security features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import base64
from pathlib import Path
import hashlib
import secrets
import yaml
try:
    import boto3
    HAS_AWS = True
except ImportError:
    HAS_AWS = False

logger = logging.getLogger(__name__)


class Environment(Enum):
    """
Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class SecretSource(Enum):
    """Secret source types"""

    ENVIRONMENT = "environment"
    FILE = "file"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GOOGLE_SECRET_MANAGER = "google_secret_manager"
    HASHICORP_VAULT = "hashicorp_vault"


@dataclass
class SecretConfig:
    """Configuration for a secret"""
    key: str
    source: SecretSource
    required: bool = True
    default: Optional[str] = None
    source_config: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass 
class EnvironmentConfig:
    """
Environment configuration"""
    name: str
    environment: Environment
    debug: bool = False
    secrets: List[SecretConfig] = field(default_factory=list)
    config_overrides: Dict[str, Any] = field(default_factory=dict)


class SecretManager:
    """
Secure secret management with multiple backends"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)  # 5 minutes
        self.logger = logging.getLogger(__name__)
        
    async def get_secret(self, secret_config: SecretConfig) -> Optional[str]:
        """
Get secret from configured source"""
        try:
            cache_key = f"{secret_config.source.value}:{secret_config.key}"
            
            # Check cache first
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            secret_value = None
            
            if secret_config.source == SecretSource.ENVIRONMENT:
                secret_value = self._get_from_environment(secret_config)
            elif secret_config.source == SecretSource.FILE:
                secret_value = await self._get_from_file(secret_config)
            elif secret_config.source == SecretSource.AWS_SECRETS_MANAGER:
                secret_value = await self._get_from_aws_secrets(secret_config)
            elif secret_config.source == SecretSource.AZURE_KEY_VAULT:
                secret_value = await self._get_from_azure_vault(secret_config)
            elif secret_config.source == SecretSource.GOOGLE_SECRET_MANAGER:
                secret_value = await self._get_from_google_secrets(secret_config)
            elif secret_config.source == SecretSource.HASHICORP_VAULT:
                secret_value = await self._get_from_vault(secret_config)
            
            # Use default if no value found
            if secret_value is None and secret_config.default:
                secret_value = secret_config.default
                
            # Check if required secret is missing
            if secret_value is None and secret_config.required:
                raise ValueError(f"Required secret '{secret_config.key}' not found")
            
            # Cache the result
            if secret_value:
                self.cache[cache_key] = secret_value
                
            return secret_value
            
        except Exception as e:
            self.logger.error(f"Failed to get secret '{secret_config.key}': {str(e)}")
            if secret_config.required:
                raise
            return secret_config.default
    
    def _get_from_environment(self, secret_config: SecretConfig) -> Optional[str]:
        """Get secret from environment variables"""
        env_key = secret_config.source_config.get('env_key', secret_config.key.upper())
        return os.getenv(env_key)
    
    async def _get_from_file(self, secret_config: SecretConfig) -> Optional[str]:
        """
Get secret from file"""
        file_path = secret_config.source_config.get('file_path')
        if not file_path:
            raise ValueError("file_path required for FILE secret source")
        
        try:
            path = Path(file_path)
            if path.exists():
                content = path.read_text().strip()
                # Support JSON files with key extraction
                if file_path.endswith('.json'):
                    data = json.loads(content)
                    return data.get(secret_config.key)
                return content
            return None
        except Exception as e:
            self.logger.error(f"Failed to read secret file '{file_path}': {str(e)}")
            return None
    
    async def _get_from_aws_secrets(self, secret_config: SecretConfig) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        if not HAS_AWS:
            raise ImportError("boto3 required for AWS Secrets Manager")
        
        try:
            secret_name = secret_config.source_config.get('secret_name', secret_config.key)
            region = secret_config.source_config.get('region', 'us-east-1')
            
            client = boto3.client('secretsmanager', region_name=region)
            response = client.get_secret_value(SecretId=secret_name)
            
            secret_value = response['SecretString']
            
            # If it's JSON, extract the specific key
            try:
                secret_data = json.loads(secret_value)
                return secret_data.get(secret_config.key, secret_value)
            except json.JSONDecodeError:
                return secret_value
                
        except Exception as e:
            self.logger.error(f"Failed to get AWS secret '{secret_config.key}': {str(e)}")
            return None
    
    async def _get_from_azure_vault(self, secret_config: SecretConfig) -> Optional[str]:
        """Get secret from Azure Key Vault"""
        # Placeholder for Azure Key Vault integration
        # Would use azure-keyvault-secrets in production
        self.logger.warning("Azure Key Vault integration not implemented")
        return None
    
    async def _get_from_google_secrets(self, secret_config: SecretConfig) -> Optional[str]:
        """Get secret from Google Secret Manager"""
        # Placeholder for Google Secret Manager integration
        # Would use google-cloud-secret-manager in production
        self.logger.warning("Google Secret Manager integration not implemented")
        return None
    
    async def _get_from_vault(self, secret_config: SecretConfig) -> Optional[str]:
        """Get secret from HashiCorp Vault"""
        # Placeholder for HashiCorp Vault integration
        # Would use hvac in production
        self.logger.warning("HashiCorp Vault integration not implemented")
        return None


class EnvironmentManager:
    """Advanced environment configuration manager"""
    
    def __init__(self):
        self.secret_manager = SecretManager()
        self.config = {}
        self.environment = self._detect_environment()
        self.logger = logging.getLogger(__name__)
        
    def _detect_environment(self) -> Environment:
        """
Auto-detect current environment"""
        env_name = os.getenv('ENVIRONMENT', os.getenv('ENV', 'development')).lower()
        
        # Map common environment names
        env_mapping = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'test': Environment.TESTING,
            'testing': Environment.TESTING,
            'stage': Environment.STAGING,
            'staging': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION
        }
        
        return env_mapping.get(env_name, Environment.DEVELOPMENT)
    
    async def load_configuration(self) -> Dict[str, Any]:
        """
Load complete environment configuration"""
        try:
            self.logger.info(f"Loading configuration for environment: {self.environment.value}")
            
            # Load base configuration
            base_config = self._load_base_config()
            
            # Load environment-specific configuration
            env_config = self._load_environment_config()
            
            # Load secrets
            secrets_config = await self._load_secrets()
            
            # Merge configurations (secrets override env, env overrides base)
            final_config = {
                **base_config,
                **env_config,
                **secrets_config,
                'environment': self.environment.value,
                'loaded_at': self._get_timestamp()
            }
            
            # Validate configuration
            await self._validate_configuration(final_config)
            
            self.config = final_config
            self.logger.info("Configuration loaded successfully")
            
            return final_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def _load_base_config(self) -> Dict[str, Any]:
        """Load base configuration common to all environments"""
        base_config = {
            # Application settings
            'app': {
                'name': 'Ainflue',
                'version': '1.0.0',
                'debug': self.environment == Environment.DEVELOPMENT,
                'host': '0.0.0.0',
                'port': int(os.getenv('PORT', 8000)),
                'workers': int(os.getenv('WORKERS', 4)),
                'log_level': os.getenv('LOG_LEVEL', 'INFO').upper()
            },
            
            # Database settings
            'database': {
                'driver': os.getenv('DB_DRIVER', 'postgresql+asyncpg'),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'name': os.getenv('DB_NAME', 'ainflue'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 30)),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600))
            },
            
            # Redis/Cache settings
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASSWORD'),
                'ssl': os.getenv('REDIS_SSL', 'false').lower() == 'true',
                'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 50))
            },
            
            # Security settings
            'security': {
                'secret_key': os.getenv('SECRET_KEY'),
                'jwt_algorithm': os.getenv('JWT_ALGORITHM', 'HS256'),
                'jwt_expiry_hours': int(os.getenv('JWT_EXPIRY_HOURS', 24)),
                'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
                'rate_limit_requests': int(os.getenv('RATE_LIMIT_REQUESTS', 100)),
                'rate_limit_window': int(os.getenv('RATE_LIMIT_WINDOW', 60))
            },
            
            # AI/ML settings
            'ai': {
                'model_path': os.getenv('AI_MODEL_PATH', '/app/models'),
                'max_batch_size': int(os.getenv('AI_MAX_BATCH_SIZE', 32)),
                'inference_timeout': int(os.getenv('AI_INFERENCE_TIMEOUT', 30)),
                'gpu_enabled': os.getenv('AI_GPU_ENABLED', 'false').lower() == 'true'
            },
            
            # Storage settings
            'storage': {
                'type': os.getenv('STORAGE_TYPE', 'local'),
                'local_path': os.getenv('STORAGE_LOCAL_PATH', '/app/storage'),
                'aws_bucket': os.getenv('AWS_S3_BUCKET'),
                'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
                'azure_container': os.getenv('AZURE_CONTAINER'),
                'gcp_bucket': os.getenv('GCP_BUCKET')
            },
            
            # Monitoring settings
            'monitoring': {
                'metrics_enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
                'metrics_port': int(os.getenv('METRICS_PORT', 9090)),
                'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 30)),
                'log_structured': os.getenv('LOG_STRUCTURED', 'true').lower() == 'true'
            }
        }
        
        return base_config
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """
Load environment-specific configuration overrides"""
        env_config = {}
        
        # Load from environment-specific config file if exists
        config_file = f"config/{self.environment.value}.yaml"
        if Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                self.logger.info(f"Loaded environment config from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load {config_file}: {str(e)}")
        
        # Environment-specific defaults
        if self.environment == Environment.PRODUCTION:
            env_config.update({
                'app': {'debug': False, 'log_level': 'WARNING'},
                'security': {'cors_origins': os.getenv('CORS_ORIGINS', '').split(',')},
                'monitoring': {'metrics_enabled': True}
            })
        elif self.environment == Environment.STAGING:
            env_config.update({
                'app': {'debug': False, 'log_level': 'INFO'},
                'monitoring': {'metrics_enabled': True}
            })
        elif self.environment == Environment.DEVELOPMENT:
            env_config.update({
                'app': {'debug': True, 'log_level': 'DEBUG'},
                'security': {'cors_origins': ['*']},
                'monitoring': {'metrics_enabled': True}
            })
        
        return env_config
    
    async def _load_secrets(self) -> Dict[str, Any]:
        """Load secrets from configured sources"""
        secrets_config = {}
        
        # Define secrets configuration
        secrets = [
            SecretConfig(
                key='database_url',
                source=SecretSource.ENVIRONMENT,
                source_config={'env_key': 'DATABASE_URL'},
                required=True
            ),
            SecretConfig(
                key='secret_key', 
                source=SecretSource.ENVIRONMENT,
                source_config={'env_key': 'SECRET_KEY'},
                required=True,
                default=self._generate_secret_key()
            ),
            SecretConfig(
                key='jwt_secret',
                source=SecretSource.ENVIRONMENT, 
                source_config={'env_key': 'JWT_SECRET'},
                required=True,
                default=self._generate_secret_key()
            ),
            SecretConfig(
                key='encryption_key',
                source=SecretSource.ENVIRONMENT,
                source_config={'env_key': 'ENCRYPTION_KEY'},
                required=True,
                default=self._generate_encryption_key()
            )
        ]
        
        # Add cloud secrets for production
        if self.environment == Environment.PRODUCTION:
            if HAS_AWS:
                secrets.extend([
                    SecretConfig(
                        key='aws_access_key',
                        source=SecretSource.AWS_SECRETS_MANAGER,
                        source_config={'secret_name': 'ainflue/aws/credentials'},
                        required=False
                    ),
                    SecretConfig(
                        key='database_password',
                        source=SecretSource.AWS_SECRETS_MANAGER,
                        source_config={'secret_name': 'ainflue/database/password'},
                        required=True
                    )
                ])
        
        # Load all secrets
        for secret_config in secrets:
            try:
                secret_value = await self.secret_manager.get_secret(secret_config)
                if secret_value:
                    secrets_config[secret_config.key] = secret_value
            except Exception as e:
                self.logger.error(f"Failed to load secret '{secret_config.key}': {str(e)}")
                if secret_config.required:
                    raise
        
        return secrets_config
    
    def _generate_secret_key(self) -> str:
        """Generate a secure random secret key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _generate_encryption_key(self) -> str:
        """
Generate a secure encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    async def _validate_configuration(self, config: Dict[str, Any]):
        """
Validate configuration completeness and security"""
        
        # Required fields validation
        required_fields = [
            ('app', 'name'),
            ('app', 'host'),
            ('app', 'port'),
            ('database', 'host'),
            ('database', 'name'),
            ('secret_key',),
            ('jwt_secret',)
        ]
        
        for field_path in required_fields:
            current = config
            try:
                for key in field_path:
                    current = current[key]
                if not current:
                    raise ValueError(f"Required field missing or empty: {'.'.join(field_path)}")
            except (KeyError, TypeError):
                raise ValueError(f"Required field missing: {'.'.join(field_path)}")
        
        # Security validation for production
        if self.environment == Environment.PRODUCTION:
            await self._validate_production_security(config)
    
    async def _validate_production_security(self, config: Dict[str, Any]):
        """Validate production security requirements"""
        
        # Check secret key strength
        secret_key = config.get('secret_key', '')
        if len(secret_key) < 32:
            raise ValueError("Production secret key must be at least 32 characters")
        
        # Check CORS configuration
        cors_origins = config.get('security', {}).get('cors_origins', [])
        if '*' in cors_origins:
            self.logger.warning("CORS wildcard (*) detected in production - security risk")
        
        # Check debug mode
        if config.get('app', {}).get('debug', False):
            raise ValueError("Debug mode must be disabled in production")
        
        # Check database security
        database_url = config.get('database_url', '')
        if database_url and 'localhost' in database_url:
            self.logger.warning("Using localhost database in production - check configuration")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
Get configuration value"""
        keys = key.split('.')
        current = self.config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_database_url(self) -> str:
        """
Get complete database URL"""
        database_url = self.get('database_url')
        if database_url:
            return database_url
        
        # Build from components
        db_config = self.get('database', {})
        driver = db_config.get('driver', 'postgresql+asyncpg')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        name = db_config.get('name', 'ainflue')
        user = db_config.get('user', os.getenv('DB_USER', 'postgres'))
        password = db_config.get('password', os.getenv('DB_PASSWORD', ''))
        
        if password:
            return f"{driver}://{user}:{password}@{host}:{port}/{name}"
        else:
            return f"{driver}://{user}@{host}:{port}/{name}"
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """
Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT


# Global instance
env_manager = EnvironmentManager()


async def load_configuration() -> Dict[str, Any]:
    """
Load application configuration"""
    return await env_manager.load_configuration()


def get_config(key: str, default: Any = None) -> Any:
    """
Get configuration value"""
    return env_manager.get(key, default)


def get_environment() -> Environment:
    """
Get current environment"""
    return env_manager.environment


def is_production() -> bool:
    """
Check if running in production"""
    return env_manager.is_production()


def is_development() -> bool:
    """
Check if running in development"""
    return env_manager.is_development()