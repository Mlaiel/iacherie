"""
Webhook Manager - Enterprise Webhook Configuration Management

Advanced webhook configuration and endpoint management system for multi-platform
integration with comprehensive monitoring and analytics capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import aioredis
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import WebhookError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    WebhookError, ValidationError = globals().get('WebhookError, ValidationError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

Base = declarative_base()

class WebhookEndpointModel(Base):
    """Database model for webhook endpoints"""
    __tablename__ = "webhook_endpoints"
    
    endpoint_id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    event_types = Column(JSON, nullable=False)
    secret_encrypted = Column(Text)
    signature_method = Column(String, default="hmac_sha256")
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    active = Column(Boolean, default=True)
    headers = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_error = Column(Text)

class WebhookConfigurationModel(Base):
    """Database model for webhook configurations"""
    __tablename__ = "webhook_configurations"
    
    config_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

class WebhookStatus(Enum):
    """Webhook endpoint status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

@dataclass
class WebhookConfiguration:
    """Webhook configuration data structure"""
    config_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = None
    platform: str = None
    endpoint_url: str = None
    secret: str = None
    event_types: List[str] = field(default_factory=list)
    signature_method: str = "hmac_sha256"
    max_retries: int = 3
    timeout_seconds: int = 30
    custom_headers: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Dict[str, int] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class WebhookHealthStatus:
    """Webhook endpoint health status"""
    endpoint_id: str
    status: WebhookStatus
    last_check: datetime
    response_time_ms: float
    success_rate: float
    total_requests: int
    failed_requests: int
    last_error: Optional[str] = None

class WebhookManager:
    """
    Enterprise webhook configuration and endpoint management system
    
    Provides comprehensive webhook lifecycle management including registration,
    monitoring, health checking, and performance analytics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_session = get_db_session()
        self.performance_monitor = PerformanceMonitor("webhook_manager")
        self.encryption = ContentEncryption()
        
        # Internal state
        self._redis_client = None
        self._endpoint_cache: Dict[str, WebhookConfiguration] = {}
        self._health_status: Dict[str, WebhookHealthStatus] = {}
        self._monitoring_tasks: Set[asyncio.Task] = set()
        
        # Configuration
        self.cache_ttl = self.config.get('cache_ttl_seconds', 300)
        self.health_check_interval = self.config.get('health_check_interval', 60)
        self.max_concurrent_checks = self.config.get('max_concurrent_checks', 10)
        
        logger.info("WebhookManager initialized")

    async def initialize(self) -> None:
        """Initialize webhook manager with required services"""



        try:
            # Initialize Redis connection
            self._redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                decode_responses=True
            )
            
            # Load existing configurations from database
            await self._load_configurations_from_db()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            logger.info("WebhookManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebhookManager: {e}")
            raise WebhookError(f"Initialization failed: {str(e)}")

    async def register_webhook_endpoint(
        self,
        user_id: str,
        platform: str,
        endpoint_url: str,
        event_types: List[str],
        secret: str = None,
        signature_method: str = "hmac_sha256",
        custom_headers: Dict[str, str] = None,
        rate_limit: Dict[str, int] = None,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Register new webhook endpoint
        
        Args:
            user_id: User identifier
            platform: Platform name (youtube, instagram, tiktok, etc.)
            endpoint_url: Webhook endpoint URL
            event_types: List of event types to subscribe to
            secret: Secret for signature generation
            signature_method: Signature generation method
            custom_headers: Additional HTTP headers
            rate_limit: Rate limiting configuration
            filters: Event filtering rules
            
        Returns:
            Registration result with configuration details
        """



        try:
            # Validate endpoint URL
            validation_result = await self._validate_endpoint_url(endpoint_url)
            if not validation_result['valid']:
                raise ValidationError(f"Invalid endpoint URL: {validation_result['reason']}")
            
            # Create configuration
            config = WebhookConfiguration(
                user_id=user_id,
                platform=platform,
                endpoint_url=endpoint_url,
                secret=secret,
                event_types=event_types,
                signature_method=signature_method,
                custom_headers=custom_headers or {},
                rate_limit=rate_limit or {},
                filters=filters or {}
            )
            
            # Test endpoint connectivity
            test_result = await self._test_endpoint_connectivity(config)
            if not test_result['reachable']:
                logger.warning(f"Endpoint not immediately reachable: {endpoint_url}")
            
            # Store in database
            await self._store_configuration_in_db(config)
            
            # Update cache
            self._endpoint_cache[config.config_id] = config
            
            # Cache in Redis
            await self._cache_configuration_in_redis(config)
            
            # Initialize health monitoring for this endpoint
            await self._initialize_endpoint_monitoring(config)
            
            logger.info(f"Webhook endpoint registered: {config.config_id} for {platform}")
            
            return {
                'success': True,
                'config_id': config.config_id,
                'platform': platform,
                'endpoint_url': endpoint_url,
                'event_types': event_types,
                'connectivity_test': test_result
            }
            
        except Exception as e:
            logger.error(f"Failed to register webhook endpoint: {e}")
            raise WebhookError(f"Registration failed: {str(e)}")

    async def update_webhook_endpoint(
        self,
        config_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing webhook endpoint configuration"""



        try:
            # Get existing configuration
            config = await self.get_webhook_configuration(config_id)
            if not config:
                raise ValidationError(f"Configuration not found: {config_id}")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            # Re-validate if URL changed
            if 'endpoint_url' in updates:
                validation_result = await self._validate_endpoint_url(config.endpoint_url)
                if not validation_result['valid']:
                    raise ValidationError(f"Invalid endpoint URL: {validation_result['reason']}")
            
            # Update database
            await self._update_configuration_in_db(config)
            
            # Update cache
            self._endpoint_cache[config_id] = config
            await self._cache_configuration_in_redis(config)
            
            logger.info(f"Webhook endpoint updated: {config_id}")
            
            return {
                'success': True,
                'config_id': config_id,
                'updated_fields': list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update webhook endpoint: {e}")
            raise WebhookError(f"Update failed: {str(e)}")

    async def get_webhook_configuration(self, config_id: str) -> Optional[WebhookConfiguration]:
        """Get webhook configuration by ID"""



        try:
            # Check cache first
            if config_id in self._endpoint_cache:
                return self._endpoint_cache[config_id]
            
            # Check Redis cache
            cached_config = await self._get_configuration_from_redis(config_id)
            if cached_config:
                self._endpoint_cache[config_id] = cached_config
                return cached_config
            
            # Load from database
            config = await self._load_configuration_from_db(config_id)
            if config:
                self._endpoint_cache[config_id] = config
                await self._cache_configuration_in_redis(config)
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to get webhook configuration: {e}")
            return None

    async def get_user_webhook_configurations(
        self,
        user_id: str,
        platform: str = None,
        active_only: bool = True
    ) -> List[WebhookConfiguration]:
        """Get all webhook configurations for a user"""



        try:
            configurations = []
            
            # Query database
            query = self.db_session.query(WebhookConfigurationModel).filter(
                WebhookConfigurationModel.user_id == user_id
            )
            
            if platform:
                query = query.filter(WebhookConfigurationModel.platform == platform)
            
            if active_only:
                query = query.filter(WebhookConfigurationModel.active == True)
            
            db_configs = query.all()
            
            for db_config in db_configs:
                config = self._convert_db_to_config(db_config)
                configurations.append(config)
                
                # Update cache
                self._endpoint_cache[config.config_id] = config
            
            return configurations
            
        except Exception as e:
            logger.error(f"Failed to get user webhook configurations: {e}")
            return []

    async def delete_webhook_endpoint(self, config_id: str) -> Dict[str, Any]:
        """Delete webhook endpoint configuration"""



        try:
            # Get configuration
            config = await self.get_webhook_configuration(config_id)
            if not config:
                raise ValidationError(f"Configuration not found: {config_id}")
            
            # Mark as inactive in database
            await self._deactivate_configuration_in_db(config_id)
            
            # Remove from caches
            if config_id in self._endpoint_cache:
                del self._endpoint_cache[config_id]
            
            await self._remove_configuration_from_redis(config_id)
            
            # Stop monitoring for this endpoint
            await self._stop_endpoint_monitoring(config_id)
            
            logger.info(f"Webhook endpoint deleted: {config_id}")
            
            return {
                'success': True,
                'config_id': config_id,
                'platform': config.platform
            }
            
        except Exception as e:
            logger.error(f"Failed to delete webhook endpoint: {e}")
            raise WebhookError(f"Deletion failed: {str(e)}")

    async def test_webhook_endpoint(self, config_id: str) -> Dict[str, Any]:
        """Test webhook endpoint connectivity and response"""



        try:
            config = await self.get_webhook_configuration(config_id)
            if not config:
                raise ValidationError(f"Configuration not found: {config_id}")
            
            # Test connectivity
            connectivity_result = await self._test_endpoint_connectivity(config)
            
            # Test with sample payload if reachable
            payload_test_result = {}
            if connectivity_result['reachable']:
                payload_test_result = await self._test_endpoint_with_payload(config)
            
            # Update health status
            health_status = WebhookHealthStatus(
                endpoint_id=config_id,
                status=WebhookStatus.ACTIVE if connectivity_result['reachable'] else WebhookStatus.ERROR,
                last_check=datetime.now(timezone.utc),
                response_time_ms=connectivity_result.get('response_time_ms', 0),
                success_rate=1.0 if connectivity_result['reachable'] else 0.0,
                total_requests=1,
                failed_requests=0 if connectivity_result['reachable'] else 1,
                last_error=connectivity_result.get('error')
            )
            
            self._health_status[config_id] = health_status
            
            return {
                'success': True,
                'config_id': config_id,
                'connectivity_test': connectivity_result,
                'payload_test': payload_test_result,
                'health_status': health_status.__dict__
            }
            
        except Exception as e:
            logger.error(f"Failed to test webhook endpoint: {e}")
            raise WebhookError(f"Test failed: {str(e)}")

    async def get_webhook_health_status(
        self,
        config_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get health status for webhook endpoints"""



        try:
            if config_id:
                # Get specific endpoint health
                if config_id in self._health_status:
                    return {
                        'success': True,
                        'health_status': self._health_status[config_id].__dict__
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Health status not available'
                    }
            
            elif user_id:
                # Get all endpoints health for user
                user_configs = await self.get_user_webhook_configurations(user_id)
                health_statuses = {}
                
                for config in user_configs:
                    if config.config_id in self._health_status:
                        health_statuses[config.config_id] = self._health_status[config.config_id].__dict__
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'health_statuses': health_statuses
                }
            
            else:
                # Get all health statuses
                all_statuses = {
                    config_id: status.__dict__
                    for config_id, status in self._health_status.items()
                }
                
                return {
                    'success': True,
                    'health_statuses': all_statuses
                }
                
        except Exception as e:
            logger.error(f"Failed to get webhook health status: {e}")
            raise WebhookError(f"Health status retrieval failed: {str(e)}")

    async def get_webhook_metrics(
        self,
        config_id: str = None,
        platform: str = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get webhook performance metrics"""



        try:
            metrics = {
                'time_range': time_range,
                'total_endpoints': len(self._endpoint_cache),
                'active_endpoints': sum(1 for c in self._endpoint_cache.values() if c.active),
                'health_statuses': {},
                'platform_breakdown': {},
                'performance_metrics': {}
            }
            
            # Calculate health status distribution
            status_counts = {}
            for health_status in self._health_status.values():
                status = health_status.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            metrics['health_statuses'] = status_counts
            
            # Platform breakdown
            platform_counts = {}
            for config in self._endpoint_cache.values():
                platform = config.platform
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            metrics['platform_breakdown'] = platform_counts
            
            # Performance metrics
            if self._health_status:
                response_times = [s.response_time_ms for s in self._health_status.values()]
                success_rates = [s.success_rate for s in self._health_status.values()]
                
                metrics['performance_metrics'] = {
                    'average_response_time_ms': sum(response_times) / len(response_times),
                    'max_response_time_ms': max(response_times),
                    'min_response_time_ms': min(response_times),
                    'average_success_rate': sum(success_rates) / len(success_rates)
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get webhook metrics: {e}")
            raise WebhookError(f"Metrics retrieval failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for webhook manager"""



        return {
            'status': 'healthy',
            'redis_connected': self._redis_client is not None,
            'cached_configurations': len(self._endpoint_cache),
            'monitoring_tasks': len(self._monitoring_tasks),
            'health_statuses_tracked': len(self._health_status)
        }

    async def shutdown(self) -> None:
        """Graceful shutdown of webhook manager"""



        try:
            logger.info("Shutting down WebhookManager")
            
            # Cancel monitoring tasks
            for task in self._monitoring_tasks:
                task.cancel()
            
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.close()
            
            logger.info("WebhookManager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during WebhookManager shutdown: {e}")

    # Private methods
    
    async def _validate_endpoint_url(self, url: str) -> Dict[str, Any]:
        """Validate webhook endpoint URL"""



        try:
            if not url.startswith(('http://', 'https://')):
                return {
                    'valid': False,
                    'reason': 'URL must start with http:// or https://'
                }
            
            # Additional URL validation logic
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'URL validation error: {str(e)}'
            }

    async def _test_endpoint_connectivity(self, config: WebhookConfiguration) -> Dict[str, Any]:
        """Test basic connectivity to webhook endpoint"""
        start_time = time.time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Simple HEAD request to test connectivity
                async with session.head(config.endpoint_url) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    return {
                        'reachable': True,
                        'status_code': response.status,
                        'response_time_ms': response_time
                    }
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'reachable': False,
                'error': str(e),
                'response_time_ms': response_time
            }

    async def _test_endpoint_with_payload(self, config: WebhookConfiguration) -> Dict[str, Any]:
        """Test endpoint with sample payload"""



        try:
            test_payload = {
                'event_type': 'test',
                'test_mode': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'config_id': config.config_id
            }
            
            timeout = aiohttp.ClientTimeout(total=config.timeout_seconds)
            headers = config.custom_headers.copy()
            headers['Content-Type'] = 'application/json'
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    config.endpoint_url,
                    json=test_payload,
                    headers=headers
                ) as response:
                    response_text = await response.text()
                    
                    return {
                        'success': response.status in [200, 201, 202],
                        'status_code': response.status,
                        'response_text': response_text[:500]  # Truncate long responses
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _store_configuration_in_db(self, config: WebhookConfiguration) -> None:
        """Store configuration in database"""



        try:
            # Encrypt secret if provided
            secret_encrypted = None
            if config.secret:
                secret_encrypted = self.encryption.encrypt(config.secret)
            
            db_config = WebhookConfigurationModel(
                config_id=config.config_id,
                user_id=config.user_id,
                platform=config.platform,
                configuration={
                    'endpoint_url': config.endpoint_url,
                    'event_types': config.event_types,
                    'signature_method': config.signature_method,
                    'max_retries': config.max_retries,
                    'timeout_seconds': config.timeout_seconds,
                    'custom_headers': config.custom_headers,
                    'rate_limit': config.rate_limit,
                    'filters': config.filters,
                    'secret_encrypted': secret_encrypted
                }
            )
            
            self.db_session.add(db_config)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to store configuration in database: {e}")
            raise

    async def _update_configuration_in_db(self, config: WebhookConfiguration) -> None:
        """Update configuration in database"""



        try:
            db_config = self.db_session.query(WebhookConfigurationModel).filter(
                WebhookConfigurationModel.config_id == config.config_id
            ).first()
            
            if db_config:
                # Encrypt secret if provided
                secret_encrypted = None
                if config.secret:
                    secret_encrypted = self.encryption.encrypt(config.secret)
                
                db_config.configuration = {
                    'endpoint_url': config.endpoint_url,
                    'event_types': config.event_types,
                    'signature_method': config.signature_method,
                    'max_retries': config.max_retries,
                    'timeout_seconds': config.timeout_seconds,
                    'custom_headers': config.custom_headers,
                    'rate_limit': config.rate_limit,
                    'filters': config.filters,
                    'secret_encrypted': secret_encrypted
                }
                db_config.updated_at = datetime.utcnow()
                
                self.db_session.commit()
                
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update configuration in database: {e}")
            raise

    async def _load_configuration_from_db(self, config_id: str) -> Optional[WebhookConfiguration]:
        """Load configuration from database"""



        try:
            db_config = self.db_session.query(WebhookConfigurationModel).filter(
                WebhookConfigurationModel.config_id == config_id
            ).first()
            
            if db_config:
                return self._convert_db_to_config(db_config)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load configuration from database: {e}")
            return None

    async def _load_configurations_from_db(self) -> None:
        """Load all active configurations from database"""



        try:
            db_configs = self.db_session.query(WebhookConfigurationModel).filter(
                WebhookConfigurationModel.active == True
            ).all()
            
            for db_config in db_configs:
                config = self._convert_db_to_config(db_config)
                self._endpoint_cache[config.config_id] = config
                
            logger.info(f"Loaded {len(db_configs)} configurations from database")
            
        except Exception as e:
            logger.error(f"Failed to load configurations from database: {e}")

    def _convert_db_to_config(self, db_config: WebhookConfigurationModel) -> WebhookConfiguration:
        """Convert database model to configuration object"""
        config_data = db_config.configuration
        
        # Decrypt secret if present
        secret = None
        if config_data.get('secret_encrypted'):
            secret = self.encryption.decrypt(config_data['secret_encrypted'])
        
        return WebhookConfiguration(
            config_id=db_config.config_id,
            user_id=db_config.user_id,
            platform=db_config.platform,
            endpoint_url=config_data['endpoint_url'],
            secret=secret,
            event_types=config_data.get('event_types', []),
            signature_method=config_data.get('signature_method', 'hmac_sha256'),
            max_retries=config_data.get('max_retries', 3),
            timeout_seconds=config_data.get('timeout_seconds', 30),
            custom_headers=config_data.get('custom_headers', {}),
            rate_limit=config_data.get('rate_limit', {}),
            filters=config_data.get('filters', {}),
            active=db_config.active,
            created_at=db_config.created_at.replace(tzinfo=timezone.utc)
        )

    async def _deactivate_configuration_in_db(self, config_id: str) -> None:
        """Deactivate configuration in database"""



        try:
            db_config = self.db_session.query(WebhookConfigurationModel).filter(
                WebhookConfigurationModel.config_id == config_id
            ).first()
            
            if db_config:
                db_config.active = False
                db_config.updated_at = datetime.utcnow()
                self.db_session.commit()
                
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to deactivate configuration: {e}")
            raise

    async def _cache_configuration_in_redis(self, config: WebhookConfiguration) -> None:
        """Cache configuration in Redis"""



        try:
            if self._redis_client:
                config_data = {
                    'config_id': config.config_id,
                    'user_id': config.user_id,
                    'platform': config.platform,
                    'endpoint_url': config.endpoint_url,
                    'event_types': config.event_types,
                    'signature_method': config.signature_method,
                    'max_retries': config.max_retries,
                    'timeout_seconds': config.timeout_seconds,
                    'custom_headers': config.custom_headers,
                    'rate_limit': config.rate_limit,
                    'filters': config.filters,
                    'active': config.active
                    # Note: Don't cache the secret for security
                }
                
                cache_key = f"webhook_config:{config.config_id}"
                await self._redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(config_data, default=str)
                )
                
        except Exception as e:
            logger.error(f"Failed to cache configuration in Redis: {e}")

    async def _get_configuration_from_redis(self, config_id: str) -> Optional[WebhookConfiguration]:
        """Get configuration from Redis cache"""



        try:
            if self._redis_client:
                cache_key = f"webhook_config:{config_id}"
                cached_data = await self._redis_client.get(cache_key)
                
                if cached_data:
                    config_data = json.loads(cached_data)
                    
                    # Load secret from database since it's not cached
                    db_config = await self._load_configuration_from_db(config_id)
                    secret = db_config.secret if db_config else None
                    
                    return WebhookConfiguration(
                        config_id=config_data['config_id'],
                        user_id=config_data['user_id'],
                        platform=config_data['platform'],
                        endpoint_url=config_data['endpoint_url'],
                        secret=secret,
                        event_types=config_data.get('event_types', []),
                        signature_method=config_data.get('signature_method', 'hmac_sha256'),
                        max_retries=config_data.get('max_retries', 3),
                        timeout_seconds=config_data.get('timeout_seconds', 30),
                        custom_headers=config_data.get('custom_headers', {}),
                        rate_limit=config_data.get('rate_limit', {}),
                        filters=config_data.get('filters', {}),
                        active=config_data.get('active', True)
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get configuration from Redis: {e}")
            return None

    async def _remove_configuration_from_redis(self, config_id: str) -> None:
        """Remove configuration from Redis cache"""



        try:
            if self._redis_client:
                cache_key = f"webhook_config:{config_id}"
                await self._redis_client.delete(cache_key)
                
        except Exception as e:
            logger.error(f"Failed to remove configuration from Redis: {e}")

    async def _start_health_monitoring(self) -> None:
        """Start health monitoring tasks"""
        task = asyncio.create_task(self._health_monitoring_loop())
        self._monitoring_tasks.add(task)

    async def _health_monitoring_loop(self) -> None:
        """Health monitoring background task"""
        while True:
            try:
                await self._check_all_endpoints_health()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying

    async def _check_all_endpoints_health(self) -> None:
        """Check health of all registered endpoints"""



        try:
            # Create tasks for concurrent health checks
            check_tasks = []
            for config in list(self._endpoint_cache.values()):
                if config.active:
                    task = asyncio.create_task(self._check_endpoint_health(config))
                    check_tasks.append(task)
                    
                    # Limit concurrent checks
                    if len(check_tasks) >= self.max_concurrent_checks:
                        await asyncio.gather(*check_tasks, return_exceptions=True)
                        check_tasks = []
            
            # Check remaining tasks
            if check_tasks:
                await asyncio.gather(*check_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error checking endpoints health: {e}")

    async def _check_endpoint_health(self, config: WebhookConfiguration) -> None:
        """Check health of specific endpoint"""



        try:
            connectivity_result = await self._test_endpoint_connectivity(config)
            
            # Update or create health status
            if config.config_id in self._health_status:
                health_status = self._health_status[config.config_id]
                health_status.last_check = datetime.now(timezone.utc)
                health_status.response_time_ms = connectivity_result.get('response_time_ms', 0)
                health_status.total_requests += 1
                
                if connectivity_result['reachable']:
                    health_status.status = WebhookStatus.ACTIVE
                    health_status.last_error = None
                else:
                    health_status.status = WebhookStatus.ERROR
                    health_status.failed_requests += 1
                    health_status.last_error = connectivity_result.get('error')
                
                # Recalculate success rate
                health_status.success_rate = (
                    (health_status.total_requests - health_status.failed_requests) /
                    health_status.total_requests
                )
            else:
                # Create new health status
                health_status = WebhookHealthStatus(
                    endpoint_id=config.config_id,
                    status=WebhookStatus.ACTIVE if connectivity_result['reachable'] else WebhookStatus.ERROR,
                    last_check=datetime.now(timezone.utc),
                    response_time_ms=connectivity_result.get('response_time_ms', 0),
                    success_rate=1.0 if connectivity_result['reachable'] else 0.0,
                    total_requests=1,
                    failed_requests=0 if connectivity_result['reachable'] else 1,
                    last_error=connectivity_result.get('error')
                )
                
                self._health_status[config.config_id] = health_status
                
        except Exception as e:
            logger.error(f"Error checking endpoint health for {config.config_id}: {e}")

    async def _initialize_endpoint_monitoring(self, config: WebhookConfiguration) -> None:
        """Initialize monitoring for new endpoint"""
        await self._check_endpoint_health(config)

    async def _stop_endpoint_monitoring(self, config_id: str) -> None:
        """Stop monitoring for specific endpoint"""
        if config_id in self._health_status:
            del self._health_status[config_id]
