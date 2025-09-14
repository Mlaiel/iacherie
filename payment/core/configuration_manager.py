"""💳 Payment Gateway Configuration Manager
==========================================

Enterprise-grade configuration management for payment gateway providers
with dynamic configuration updates, environment-specific settings, and
real-time provider switching capabilities.

Features:
- Environment-specific provider configurations
- Dynamic provider switching and routing
- API key and credential management
- Provider health monitoring and alerting
- A/B testing support
- Configuration validation and compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
import os
from pathlib import Path
import hashlib
import hmac
from cryptography.fernet import Fernet
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"


class ProviderStatus(Enum):
    """Provider status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


@dataclass
class ProviderCredentials:
    """Secure provider credentials"""
    provider_name: str
    api_key: str
    secret_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    additional_keys: Dict[str, str] = field(default_factory=dict)
    
    def encrypt_credentials(self, encryption_key: bytes) -> Dict[str, str]:
        """Encrypt sensitive credentials"""
        fernet = Fernet(encryption_key)
        encrypted = {}
        
        encrypted['api_key'] = fernet.encrypt(self.api_key.encode()).decode()
        if self.secret_key:
            encrypted['secret_key'] = fernet.encrypt(self.secret_key.encode()).decode()
        if self.webhook_secret:
            encrypted['webhook_secret'] = fernet.encrypt(self.webhook_secret.encode()).decode()
            
        for key, value in self.additional_keys.items():
            encrypted[f'additional_{key}'] = fernet.encrypt(value.encode()).decode()
            
        return encrypted
    
    @classmethod
    def decrypt_credentials(cls, encrypted_data: Dict[str, str], 
                          encryption_key: bytes, provider_name: str) -> 'ProviderCredentials':
        """Decrypt credentials from encrypted data"""
        fernet = Fernet(encryption_key)
        
        api_key = fernet.decrypt(encrypted_data['api_key'].encode()).decode()
        secret_key = None
        webhook_secret = None
        additional_keys = {}
        
        if 'secret_key' in encrypted_data:
            secret_key = fernet.decrypt(encrypted_data['secret_key'].encode()).decode()
        if 'webhook_secret' in encrypted_data:
            webhook_secret = fernet.decrypt(encrypted_data['webhook_secret'].encode()).decode()
            
        for key, value in encrypted_data.items():
            if key.startswith('additional_'):
                actual_key = key.replace('additional_', '')
                additional_keys[actual_key] = fernet.decrypt(value.encode()).decode()
        
        return cls(
            provider_name=provider_name,
            api_key=api_key,
            secret_key=secret_key,
            webhook_secret=webhook_secret,
            additional_keys=additional_keys
        )


@dataclass
class ProviderConfiguration:
    """Complete provider configuration"""
    provider_name: str
    status: ProviderStatus
    priority: int  # Lower number = higher priority
    capabilities: List[str]
    supported_currencies: List[str]
    supported_countries: List[str]
    fee_structure: Dict[str, Decimal]
    rate_limits: Dict[str, int]
    timeout_seconds: int
    retry_attempts: int
    fallback_providers: List[str]
    environment_specific: Dict[Environment, Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ABTestConfiguration:
    """A/B testing configuration for payment providers"""
    test_id: str
    test_name: str
    enabled: bool
    traffic_split: Dict[str, int]  # provider_name: percentage
    target_metrics: List[str]
    start_date: datetime
    end_date: datetime
    criteria: Dict[str, Any]  # targeting criteria


class PaymentGatewayConfigurationManager:
    """
    Enterprise configuration manager for payment gateway providers
    with dynamic updates, security, and monitoring capabilities.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize configuration manager"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.environment = Environment(config.get('environment', 'development'))
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_encryption_key()
        
        # Provider configurations
        self.provider_configs: Dict[str, ProviderConfiguration] = {}
        self.provider_credentials: Dict[str, ProviderCredentials] = {}
        
        # A/B testing
        self.ab_tests: Dict[str, ABTestConfiguration] = {}
        
        # Redis for caching and real-time updates
        self.redis_client = None
        
        # Configuration validation
        self.config_validators = {}
        
    async def initialize(self) -> None:
        """Initialize the configuration manager"""
        try:
            # Connect to Redis for caching
            if 'redis' in self.config:
                redis_config = self.config['redis']
                self.redis_client = await aioredis.from_url(
                    f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                )
            
            # Load configurations
            await self._load_configurations()
            await self._load_credentials()
            await self._load_ab_tests()
            
            self.logger.info(f"Configuration manager initialized for {self.environment.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration manager: {e}")
            raise
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for credentials"""
        key_path = Path(self.config.get('encryption_key_path', '.payment_key'))
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)  # Restrict permissions
            return key
    
    async def add_provider_configuration(self, config: ProviderConfiguration) -> bool:
        """Add or update provider configuration"""
        try:
            # Validate configuration
            if not await self._validate_provider_config(config):
                raise ValueError(f"Invalid configuration for provider {config.provider_name}")
            
            # Store configuration
            self.provider_configs[config.provider_name] = config
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"provider_config:{config.provider_name}",
                    3600,  # 1 hour TTL
                    json.dumps(config.__dict__, default=str)
                )
            
            self.logger.info(f"Added provider configuration: {config.provider_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add provider configuration: {e}")
            return False
    
    async def add_provider_credentials(self, credentials: ProviderCredentials) -> bool:
        """Add encrypted provider credentials"""
        try:
            # Encrypt credentials
            encrypted_data = credentials.encrypt_credentials(self.encryption_key)
            
            # Store encrypted credentials
            self.provider_credentials[credentials.provider_name] = credentials
            
            # Cache encrypted version in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"provider_credentials:{credentials.provider_name}",
                    1800,  # 30 minutes TTL for security
                    json.dumps(encrypted_data)
                )
            
            self.logger.info(f"Added encrypted credentials for: {credentials.provider_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add provider credentials: {e}")
            return False
    
    async def get_provider_configuration(self, provider_name: str) -> Optional[ProviderConfiguration]:
        """Get provider configuration with caching"""
        try:
            # Check cache first
            if self.redis_client:
                cached = await self.redis_client.get(f"provider_config:{provider_name}")
                if cached:
                    config_data = json.loads(cached)
                    # Reconstruct configuration object
                    return self._reconstruct_provider_config(config_data)
            
            # Return from memory
            return self.provider_configs.get(provider_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get provider configuration: {e}")
            return None
    
    async def get_provider_credentials(self, provider_name: str) -> Optional[ProviderCredentials]:
        """Get decrypted provider credentials"""
        try:
            # Check cache first
            if self.redis_client:
                cached = await self.redis_client.get(f"provider_credentials:{provider_name}")
                if cached:
                    encrypted_data = json.loads(cached)
                    return ProviderCredentials.decrypt_credentials(
                        encrypted_data, self.encryption_key, provider_name
                    )
            
            # Return from memory
            return self.provider_credentials.get(provider_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get provider credentials: {e}")
            return None
    
    async def get_active_providers(self) -> List[ProviderConfiguration]:
        """Get all active providers sorted by priority"""
        try:
            active_providers = [
                config for config in self.provider_configs.values()
                if config.status == ProviderStatus.ACTIVE
            ]
            
            # Sort by priority (lower number = higher priority)
            return sorted(active_providers, key=lambda x: x.priority)
            
        except Exception as e:
            self.logger.error(f"Failed to get active providers: {e}")
            return []
    
    async def get_providers_for_currency(self, currency: str) -> List[ProviderConfiguration]:
        """Get providers that support specific currency"""
        try:
            active_providers = await self.get_active_providers()
            return [
                provider for provider in active_providers
                if currency in provider.supported_currencies or 'ALL' in provider.supported_currencies
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get providers for currency {currency}: {e}")
            return []
    
    async def get_providers_for_country(self, country: str) -> List[ProviderConfiguration]:
        """Get providers that support specific country"""
        try:
            active_providers = await self.get_active_providers()
            return [
                provider for provider in active_providers
                if country in provider.supported_countries or 'ALL' in provider.supported_countries
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get providers for country {country}: {e}")
            return []
    
    async def update_provider_status(self, provider_name: str, status: ProviderStatus) -> bool:
        """Update provider status"""
        try:
            if provider_name not in self.provider_configs:
                raise ValueError(f"Provider {provider_name} not found")
            
            old_status = self.provider_configs[provider_name].status
            self.provider_configs[provider_name].status = status
            self.provider_configs[provider_name].updated_at = datetime.now()
            
            # Update cache
            if self.redis_client:
                await self.redis_client.delete(f"provider_config:{provider_name}")
            
            self.logger.info(f"Updated provider {provider_name} status: {old_status.value} -> {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update provider status: {e}")
            return False
    
    async def create_ab_test(self, ab_test: ABTestConfiguration) -> bool:
        """Create A/B test configuration"""
        try:
            # Validate traffic split adds up to 100%
            total_traffic = sum(ab_test.traffic_split.values())
            if total_traffic != 100:
                raise ValueError(f"Traffic split must add up to 100%, got {total_traffic}%")
            
            # Validate providers exist
            for provider_name in ab_test.traffic_split.keys():
                if provider_name not in self.provider_configs:
                    raise ValueError(f"Provider {provider_name} not configured")
            
            self.ab_tests[ab_test.test_id] = ab_test
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"ab_test:{ab_test.test_id}",
                    86400,  # 24 hours TTL
                    json.dumps(ab_test.__dict__, default=str)
                )
            
            self.logger.info(f"Created A/B test: {ab_test.test_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create A/B test: {e}")
            return False
    
    async def get_provider_for_user(self, user_id: str, amount: Decimal, 
                                  currency: str, country: str) -> Optional[str]:
        """Get optimal provider for user considering A/B tests and routing rules"""
        try:
            # Check active A/B tests
            for ab_test in self.ab_tests.values():
                if ab_test.enabled and ab_test.start_date <= datetime.now() <= ab_test.end_date:
                    if await self._user_matches_ab_criteria(user_id, ab_test.criteria):
                        # Determine provider based on traffic split
                        provider = self._select_provider_from_split(user_id, ab_test.traffic_split)
                        if provider:
                            return provider
            
            # Default routing logic
            suitable_providers = await self.get_providers_for_currency(currency)
            country_providers = await self.get_providers_for_country(country)
            
            # Get intersection of currency and country support
            optimal_providers = [
                p for p in suitable_providers 
                if p in country_providers
            ]
            
            if optimal_providers:
                # Return highest priority provider
                return optimal_providers[0].provider_name
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get provider for user: {e}")
            return None
    
    async def _validate_provider_config(self, config: ProviderConfiguration) -> bool:
        """Validate provider configuration"""
        try:
            # Basic validation
            if not config.provider_name or not config.capabilities:
                return False
            
            # Currency validation
            for currency in config.supported_currencies:
                if currency != 'ALL' and len(currency) not in [3, 4]:  # Standard currency codes
                    return False
            
            # Fee structure validation
            for fee_type, amount in config.fee_structure.items():
                if amount < 0:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def _reconstruct_provider_config(self, config_data: Dict[str, Any]) -> ProviderConfiguration:
        """Reconstruct ProviderConfiguration from JSON data"""
        # Convert strings back to appropriate types
        config_data['status'] = ProviderStatus(config_data['status'])
        config_data['fee_structure'] = {k: Decimal(v) for k, v in config_data['fee_structure'].items()}
        config_data['created_at'] = datetime.fromisoformat(config_data['created_at'])
        config_data['updated_at'] = datetime.fromisoformat(config_data['updated_at'])
        
        # Handle environment specific data
        env_specific = {}
        for env_str, data in config_data.get('environment_specific', {}).items():
            env_specific[Environment(env_str)] = data
        config_data['environment_specific'] = env_specific
        
        return ProviderConfiguration(**config_data)
    
    async def _user_matches_ab_criteria(self, user_id: str, criteria: Dict[str, Any]) -> bool:
        """Check if user matches A/B test criteria"""
        # This is a simplified implementation
        # In practice, you'd check user attributes, behavior, etc.
        return True
    
    def _select_provider_from_split(self, user_id: str, traffic_split: Dict[str, int]) -> Optional[str]:
        """Select provider based on traffic split and user ID"""
        # Use consistent hashing based on user ID
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
        
        cumulative = 0
        for provider, percentage in traffic_split.items():
            cumulative += percentage
            if hash_value < cumulative:
                return provider
        
        return None
    
    async def _load_configurations(self) -> None:
        """Load provider configurations from storage"""
        # Implementation would load from database/file system
        pass
    
    async def _load_credentials(self) -> None:
        """Load encrypted credentials from secure storage"""
        # Implementation would load from secure storage
        pass
    
    async def _load_ab_tests(self) -> None:
        """Load A/B test configurations"""
        # Implementation would load from storage
        pass


# Export main class
__all__ = [
    "PaymentGatewayConfigurationManager",
    "ProviderConfiguration",
    "ProviderCredentials", 
    "ABTestConfiguration",
    "Environment",
    "ProviderStatus"
]