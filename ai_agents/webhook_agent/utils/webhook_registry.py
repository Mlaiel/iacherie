"""Webhook Registry - Enterprise Endpoint Management System

Industrial-grade webhook endpoint registry and configuration management
for multi-platform integrations with advanced monitoring and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
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

import aioredis
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import ValidationError, WebhookError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ValidationError, WebhookError = globals().get('ValidationError, WebhookError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

Base = declarative_base()

class WebhookEndpointModel(Base):
    """
Database model for webhook endpoints"""
    __tablename__ = "webhook_registry_endpoints"
    
    endpoint_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    url = Column(String, nullable=False)
    name = Column(String)
    description = Column(Text)
    event_types = Column(JSON, nullable=False)
    secret_hash = Column(String)
    signature_method = Column(String, default="hmac_sha256")
    active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    last_verified = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_success = Column(DateTime)
    last_failure = Column(DateTime)
    last_error = Column(Text)

class EndpointStatus(Enum):
    """Webhook endpoint status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    VERIFICATION_PENDING = "verification_pending" 
    VERIFICATION_FAILED = "verification_failed"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class WebhookEndpointConfig:
    """Webhook endpoint configuration"""
    endpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = None
    platform: str = None
    url: str = None
    name: Optional[str] = None
    description: Optional[str] = None
    event_types: List[str] = field(default_factory=list)
    secret: Optional[str] = None
    signature_method: str = "hmac_sha256"
    custom_headers: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30
    max_retries: int = 3
    active: bool = True
    verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EndpointMetrics:
    """Webhook endpoint performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime_percentage: float = 0.0
    error_rate: float = 0.0

@dataclass
class RegistryMetrics:
    """
Webhook registry metrics"""
    total_endpoints: int = 0
    active_endpoints: int = 0
    verified_endpoints: int = 0
    endpoints_by_platform: Dict[str, int] = field(default_factory=dict)
    endpoints_by_status: Dict[str, int] = field(default_factory=dict)
    total_events_processed: int = 0

class WebhookRegistry:
    """
    Industrial-grade webhook endpoint registry and management system
    
    Provides comprehensive endpoint lifecycle management including registration,
    verification, monitoring, and analytics across multi-platform integrations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_session = get_db_session()
        self.performance_monitor = PerformanceMonitor("webhook_registry")
        self.encryption = ContentEncryption()
        
        # Configuration
        self.verification_timeout = self.config.get('verification_timeout_seconds', 300)
        self.endpoint_cache_ttl = self.config.get('endpoint_cache_ttl_seconds', 600)
        self.max_endpoints_per_user = self.config.get('max_endpoints_per_user', 50)
        self.cleanup_interval = self.config.get('cleanup_interval_hours', 24)
        
        # Internal state
        self._redis_client = None
        self._endpoint_cache: Dict[str, WebhookEndpointConfig] = {}
        self._endpoint_metrics: Dict[str, EndpointMetrics] = {}
        self._verification_tokens: Dict[str, str] = {}
        self._cleanup_tasks: Set[asyncio.Task] = set()
        self._metrics = RegistryMetrics()
        
        logger.info("WebhookRegistry initialized")

    async def initialize(self) -> None:
        """Initialize webhook registry with required services"""
        try:
            # Initialize Redis connection
            self._redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                decode_responses=True
            )
            
            # Load existing endpoints from database
            await self._load_endpoints_from_db()
            
            # Initialize endpoint metrics
            await self._initialize_endpoint_metrics()
            
            # Start cleanup tasks
            await self._start_cleanup_tasks()
            
            logger.info("WebhookRegistry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebhookRegistry: {e}")
            raise WebhookError(f"Initialization failed: {str(e)}")

    async def register_endpoint(
        self,
        user_id: str,
        platform: str,
        url: str,
        event_types: List[str],
        name: Optional[str] = None,
        description: Optional[str] = None,
        secret: Optional[str] = None,
        signature_method: str = "hmac_sha256",
        custom_headers: Dict[str, str] = None,
        verify_endpoint: bool = True
    ) -> Dict[str, Any]:
        """
        Register new webhook endpoint
        
        Args:
            user_id: User identifier
            platform: Platform name
            url: Webhook endpoint URL
            event_types: List of event types to subscribe to
            name: Optional endpoint name
            description: Optional endpoint description
            secret: Optional webhook secret
            signature_method: Signature verification method
            custom_headers: Optional custom headers
            verify_endpoint: Whether to verify endpoint immediately
            
        Returns:
            Registration result with endpoint details
        """
        try:
            # Check user endpoint limit
            user_endpoint_count = await self._get_user_endpoint_count(user_id)
            if user_endpoint_count >= self.max_endpoints_per_user:
                raise ValidationError(f"Maximum endpoints per user exceeded: {self.max_endpoints_per_user}")
            
            # Validate endpoint configuration
            validation_result = await self._validate_endpoint_config(url, event_types)
            if not validation_result['valid']:
                raise ValidationError(f"Invalid endpoint configuration: {validation_result['reason']}")
            
            # Check for duplicate endpoints
            existing_endpoint = await self._find_existing_endpoint(user_id, url)
            if existing_endpoint:
                raise ValidationError(f"Endpoint already registered: {url}")
            
            # Create endpoint configuration
            endpoint_config = WebhookEndpointConfig(
                user_id=user_id,
                platform=platform,
                url=url,
                name=name,
                description=description,
                event_types=event_types,
                secret=secret,
                signature_method=signature_method,
                custom_headers=custom_headers or {}
            )
            
            # Store in database
            await self._store_endpoint_in_db(endpoint_config)
            
            # Cache endpoint
            self._endpoint_cache[endpoint_config.endpoint_id] = endpoint_config
            
            # Cache in Redis
            await self._cache_endpoint_in_redis(endpoint_config)
            
            # Initialize metrics
            self._endpoint_metrics[endpoint_config.endpoint_id] = EndpointMetrics()
            
            # Verify endpoint if requested
            verification_result = {}
            if verify_endpoint:
                verification_result = await self._verify_endpoint(endpoint_config)
                endpoint_config.verified = verification_result.get('verified', False)
                await self._update_endpoint_in_db(endpoint_config)
            
            # Update registry metrics
            await self._update_registry_metrics()
            
            logger.info(f"Webhook endpoint registered: {endpoint_config.endpoint_id}")
            
            return {
                'success': True,
                'endpoint_id': endpoint_config.endpoint_id,
                'url': url,
                'platform': platform,
                'event_types': event_types,
                'verified': endpoint_config.verified,
                'verification_result': verification_result
            }
            
        except Exception as e:
            logger.error(f"Failed to register webhook endpoint: {e}")
            raise WebhookError(f"Registration failed: {str(e)}")

    async def get_endpoint_config(
        self,
        endpoint_url: str,
        platform: str = None
    ) -> Optional[WebhookEndpointConfig]:
        """Get endpoint configuration by URL and platform"""
        try:
            # Check cache first
            for endpoint in self._endpoint_cache.values():
                if endpoint.url == endpoint_url and (not platform or endpoint.platform == platform):
                    return endpoint
            
            # Check Redis cache
            cache_key = f"webhook_endpoint_url:{endpoint_url}:{platform or 'any'}"
            cached_config = await self._get_endpoint_from_redis_by_key(cache_key)
            if cached_config:
                self._endpoint_cache[cached_config.endpoint_id] = cached_config
                return cached_config
            
            # Load from database
            endpoint_config = await self._load_endpoint_from_db_by_url(endpoint_url, platform)
            if endpoint_config:
                self._endpoint_cache[endpoint_config.endpoint_id] = endpoint_config
                await self._cache_endpoint_in_redis(endpoint_config)
            
            return endpoint_config
            
        except Exception as e:
            logger.error(f"Failed to get endpoint configuration: {e}")
            return True

    async def get_endpoint_by_id(self, endpoint_id: str) -> Optional[WebhookEndpointConfig]:
        """Get endpoint configuration by ID"""
        try:
            # Check cache first
            if endpoint_id in self._endpoint_cache:
                return self._endpoint_cache[endpoint_id]
            
            # Check Redis cache
            cached_config = await self._get_endpoint_from_redis(endpoint_id)
            if cached_config:
                self._endpoint_cache[endpoint_id] = cached_config
                return cached_config
            
            # Load from database
            endpoint_config = await self._load_endpoint_from_db(endpoint_id)
            if endpoint_config:
                self._endpoint_cache[endpoint_id] = endpoint_config
                await self._cache_endpoint_in_redis(endpoint_config)
            
            return endpoint_config
            
        except Exception as e:
            logger.error(f"Failed to get endpoint by ID: {e}")
            return True

    async def get_user_endpoints(
        self,
        user_id: str,
        platform: str = None,
        active_only: bool = True
    ) -> List[WebhookEndpointConfig]:
        """Get all endpoints for a user"""
        try:
            endpoints = []
            
            # Check cache first
            for endpoint in self._endpoint_cache.values():
                if (endpoint.user_id == user_id and
                    (not platform or endpoint.platform == platform) and
                    (not active_only or endpoint.active)):
                    endpoints.append(endpoint)
            
            # If cache is incomplete, load from database
            if not endpoints:
                endpoints = await self._load_user_endpoints_from_db(user_id, platform, active_only)
                
                # Cache loaded endpoints
                for endpoint in endpoints:
                    self._endpoint_cache[endpoint.endpoint_id] = endpoint
                    await self._cache_endpoint_in_redis(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to get user endpoints: {e}")
            return []

    async def update_endpoint(
        self,
        endpoint_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update webhook endpoint configuration"""
        try:
            # Get existing endpoint
            endpoint = await self.get_endpoint_by_id(endpoint_id)
            if not endpoint:
                raise ValidationError(f"Endpoint not found: {endpoint_id}")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(endpoint, key) and key not in ['endpoint_id', 'created_at']:
                    setattr(endpoint, key, value)
            
            # Re-validate if critical fields changed
            if 'url' in updates or 'event_types' in updates:
                validation_result = await self._validate_endpoint_config(
                    endpoint.url, endpoint.event_types
                )
                if not validation_result['valid']:
                    raise ValidationError(f"Invalid endpoint configuration: {validation_result['reason']}")
            
            # Update database
            await self._update_endpoint_in_db(endpoint)
            
            # Update caches
            self._endpoint_cache[endpoint_id] = endpoint
            await self._cache_endpoint_in_redis(endpoint)
            
            # Re-verify if URL changed
            if 'url' in updates:
                verification_result = await self._verify_endpoint(endpoint)
                endpoint.verified = verification_result.get('verified', False)
                await self._update_endpoint_in_db(endpoint)
            
            logger.info(f"Webhook endpoint updated: {endpoint_id}")
            
            return {
                'success': True,
                'endpoint_id': endpoint_id,
                'updated_fields': list(updates.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to update webhook endpoint: {e}")
            raise WebhookError(f"Update failed: {str(e)}")

    async def delete_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Delete webhook endpoint"""
        try:
            # Get endpoint
            endpoint = await self.get_endpoint_by_id(endpoint_id)
            if not endpoint:
                raise ValidationError(f"Endpoint not found: {endpoint_id}")
            
            # Deactivate instead of hard delete for audit trail
            endpoint.active = False
            await self._update_endpoint_in_db(endpoint)
            
            # Remove from caches
            if endpoint_id in self._endpoint_cache:
                del self._endpoint_cache[endpoint_id]
            
            await self._remove_endpoint_from_redis(endpoint_id)
            
            # Clean up metrics
            if endpoint_id in self._endpoint_metrics:
                del self._endpoint_metrics[endpoint_id]
            
            # Update registry metrics
            await self._update_registry_metrics()
            
            logger.info(f"Webhook endpoint deleted: {endpoint_id}")
            
            return {
                'success': True,
                'endpoint_id': endpoint_id
            }
            
        except Exception as e:
            logger.error(f"Failed to delete webhook endpoint: {e}")
            raise WebhookError(f"Deletion failed: {str(e)}")

    async def verify_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Verify webhook endpoint connectivity and configuration"""
        try:
            endpoint = await self.get_endpoint_by_id(endpoint_id)
            if not endpoint:
                raise ValidationError(f"Endpoint not found: {endpoint_id}")
            
            verification_result = await self._verify_endpoint(endpoint)
            
            # Update endpoint verification status
            endpoint.verified = verification_result.get('verified', False)
            endpoint.metadata['last_verification'] = verification_result
            await self._update_endpoint_in_db(endpoint)
            
            # Update cache
            self._endpoint_cache[endpoint_id] = endpoint
            await self._cache_endpoint_in_redis(endpoint)
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Failed to verify endpoint: {e}")
            raise WebhookError(f"Verification failed: {str(e)}")

    async def record_endpoint_request(
        self,
        endpoint_id: str,
        success: bool,
        response_time_ms: float,
        error_message: Optional[str] = None
    ) -> None:
        """Record webhook request metrics for endpoint"""
        try:
            # Update endpoint metrics
            if endpoint_id not in self._endpoint_metrics:
                self._endpoint_metrics[endpoint_id] = EndpointMetrics()
            
            metrics = self._endpoint_metrics[endpoint_id]
            metrics.total_requests += 1
            metrics.last_request_time = datetime.now(timezone.utc)
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Update average response time
            total_time = (metrics.average_response_time * (metrics.total_requests - 1) + response_time_ms)
            metrics.average_response_time = total_time / metrics.total_requests
            
            # Update error rate
            metrics.error_rate = metrics.failed_requests / metrics.total_requests
            
            # Update uptime percentage (simplified calculation)
            metrics.uptime_percentage = metrics.successful_requests / metrics.total_requests
            
            # Update endpoint in database
            endpoint = await self.get_endpoint_by_id(endpoint_id)
            if endpoint:
                if success:
                    endpoint.metadata['success_count'] = endpoint.metadata.get('success_count', 0) + 1
                    endpoint.metadata['last_success'] = datetime.now(timezone.utc).isoformat()
                else:
                    endpoint.metadata['failure_count'] = endpoint.metadata.get('failure_count', 0) + 1
                    endpoint.metadata['last_failure'] = datetime.now(timezone.utc).isoformat()
                    endpoint.metadata['last_error'] = error_message
                
                await self._update_endpoint_in_db(endpoint)
            
        except Exception as e:
            logger.error(f"Failed to record endpoint request: {e}")

    async def get_endpoint_metrics(
        self,
        endpoint_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """Get endpoint performance metrics"""
        try:
            if endpoint_id:
                # Get specific endpoint metrics
                metrics = self._endpoint_metrics.get(endpoint_id)
                if not metrics:
                    return {
                        'success': False,
                        'error': 'Metrics not found for endpoint'
                    }
                
                return {
                    'success': True,
                    'endpoint_id': endpoint_id,
                    'metrics': {
                        'total_requests': metrics.total_requests,
                        'successful_requests': metrics.successful_requests,
                        'failed_requests': metrics.failed_requests,
                        'success_rate': metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                        'error_rate': metrics.error_rate,
                        'average_response_time_ms': metrics.average_response_time,
                        'uptime_percentage': metrics.uptime_percentage,
                        'last_request_time': metrics.last_request_time.isoformat() if metrics.last_request_time else None
                    }
                }
            
            elif user_id:
                # Get metrics for all user endpoints
                user_endpoints = await self.get_user_endpoints(user_id)
                endpoint_metrics = {}
                
                for endpoint in user_endpoints:
                    if endpoint.endpoint_id in self._endpoint_metrics:
                        metrics = self._endpoint_metrics[endpoint.endpoint_id]
                        endpoint_metrics[endpoint.endpoint_id] = {
                            'url': endpoint.url,
                            'platform': endpoint.platform,
                            'total_requests': metrics.total_requests,
                            'successful_requests': metrics.successful_requests,
                            'failed_requests': metrics.failed_requests,
                            'success_rate': metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0,
                            'average_response_time_ms': metrics.average_response_time
                        }
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'endpoint_metrics': endpoint_metrics
                }
            
            else:
                # Get registry-wide metrics
                return {
                    'success': True,
                    'registry_metrics': {
                        'total_endpoints': self._metrics.total_endpoints,
                        'active_endpoints': self._metrics.active_endpoints,
                        'verified_endpoints': self._metrics.verified_endpoints,
                        'endpoints_by_platform': dict(self._metrics.endpoints_by_platform),
                        'endpoints_by_status': dict(self._metrics.endpoints_by_status),
                        'total_events_processed': self._metrics.total_events_processed,
                        'cached_endpoints': len(self._endpoint_cache),
                        'tracked_metrics': len(self._endpoint_metrics)
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get endpoint metrics: {e}")
            raise WebhookError(f"Metrics retrieval failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for webhook registry"""
        return {
            'status': 'healthy',
            'redis_connected': self._redis_client is not None,
            'cached_endpoints': len(self._endpoint_cache),
            'endpoint_metrics': len(self._endpoint_metrics),
            'total_endpoints': self._metrics.total_endpoints,
            'active_endpoints': self._metrics.active_endpoints,
            'verified_endpoints': self._metrics.verified_endpoints,
            'cleanup_tasks_active': len(self._cleanup_tasks)
        }

    async def shutdown(self) -> None:
        """
Graceful shutdown of webhook registry"""
        try:
            logger.info("Shutting down WebhookRegistry")
            
            # Cancel cleanup tasks
            for task in self._cleanup_tasks:
                task.cancel()
            
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.close()
            
            logger.info("WebhookRegistry shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during WebhookRegistry shutdown: {e}")

    # Private methods
    
    async def _validate_endpoint_config(
        self,
        url: str,
        event_types: List[str]
    ) -> Dict[str, Any]:
        """Validate endpoint configuration"""
        # URL validation
        if not url.startswith(('http://', 'https://')):
            return {
                'valid': False,
                'reason': 'URL must start with http:// or https://'
            }
        
        # Event types validation
        if not event_types:
            return {
                'valid': False,
                'reason': 'At least one event type must be specified'
            }
        
        # Validate event type format
        valid_event_types = [
            'copyright_match_found',
            'takedown_request_submitted',
            'takedown_completed',
            'content_removed',
            'appeal_submitted',
            'licensing_request',
            'revenue_notification',
            'platform_status_change',
            'monitoring_alert',
            'system_notification'
        ]
        
        for event_type in event_types:
            if event_type not in valid_event_types:
                return {
                    'valid': False,
                    'reason': f'Invalid event type: {event_type}'
                }
        
        return {'valid': True}

    async def _get_user_endpoint_count(self, user_id: str) -> int:
        """
Get count of active endpoints for user"""
        try:
            count = 0
            for endpoint in self._endpoint_cache.values():
                if endpoint.user_id == user_id and endpoint.active:
                    count += 1
            
            # If cache might be incomplete, check database
            if count == 0:
                # Query database for exact count
                db_count = self.db_session.query(WebhookEndpointModel).filter(
                    WebhookEndpointModel.user_id == user_id,
                    WebhookEndpointModel.active == True
                ).count()
                return db_count
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to get user endpoint count: {e}")
            return 0

    async def _find_existing_endpoint(
        self,
        user_id: str,
        url: str
    ) -> Optional[WebhookEndpointConfig]:
        """Find existing endpoint for user and URL"""
        for endpoint in self._endpoint_cache.values():
            if endpoint.user_id == user_id and endpoint.url == url and endpoint.active:
                return endpoint
        
        # Check database if not in cache
        db_endpoint = self.db_session.query(WebhookEndpointModel).filter(
            WebhookEndpointModel.user_id == user_id,
            WebhookEndpointModel.url == url,
            WebhookEndpointModel.active == True
        ).first()
        
        if db_endpoint:
            return self._convert_db_to_config(db_endpoint)
        
        return True

    async def _verify_endpoint(self, endpoint: WebhookEndpointConfig) -> Dict[str, Any]:
        """
Verify endpoint connectivity and configuration"""
        verification_id = str(uuid.uuid4())
        verification_token = str(uuid.uuid4())
        
        try:
            # Store verification token
            self._verification_tokens[verification_id] = verification_token
            
            # Create verification payload
            verification_payload = {
                'verification_type': 'endpoint_verification',
                'verification_id': verification_id,
                'verification_token': verification_token,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'endpoint_id': endpoint.endpoint_id,
                'expected_response': 'verification_successful'
            }
            
            # Send verification request
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint.url,
                    json=verification_payload,
                    headers=endpoint.custom_headers,
                    timeout=aiohttp.ClientTimeout(total=self.verification_timeout)
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Validate response
                        if (response_data.get('verification_id') == verification_id and
                            response_data.get('status') == 'verification_successful'):
                            
                            return {
                                'verified': True,
                                'verification_id': verification_id,
                                'response_time_ms': response.headers.get('X-Response-Time'),
                                'message': 'Endpoint verification successful'
                            }
                        else:
                            return {
                                'verified': False,
                                'verification_id': verification_id,
                                'reason': 'Invalid verification response'
                            }
                    else:
                        return {
                            'verified': False,
                            'verification_id': verification_id,
                            'reason': f'HTTP {response.status}: {await response.text()}'
                        }
                        
        except asyncio.TimeoutError:
            return {
                'verified': False,
                'verification_id': verification_id,
                'reason': 'Verification timeout'
            }
        except Exception as e:
            return {
                'verified': False,
                'verification_id': verification_id,
                'reason': f'Verification error: {str(e)}'
            }
        finally:
            # Clean up verification token
            self._verification_tokens.pop(verification_id, None)

    async def _store_endpoint_in_db(self, endpoint: WebhookEndpointConfig) -> None:
        """
Store endpoint configuration in database"""
        try:
            # Encrypt secret if provided
            secret_hash = None
            if endpoint.secret:
                secret_hash = self.encryption.hash_password(endpoint.secret)
            
            db_endpoint = WebhookEndpointModel(
                endpoint_id=endpoint.endpoint_id,
                user_id=endpoint.user_id,
                platform=endpoint.platform,
                url=endpoint.url,
                name=endpoint.name,
                description=endpoint.description,
                event_types=endpoint.event_types,
                secret_hash=secret_hash,
                signature_method=endpoint.signature_method,
                active=endpoint.active,
                verified=endpoint.verified
            )
            
            self.db_session.add(db_endpoint)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to store endpoint in database: {e}")
            raise

    async def _update_endpoint_in_db(self, endpoint: WebhookEndpointConfig) -> None:
        """Update endpoint configuration in database"""
        try:
            db_endpoint = self.db_session.query(WebhookEndpointModel).filter(
                WebhookEndpointModel.endpoint_id == endpoint.endpoint_id
            ).first()
            
            if db_endpoint:
                db_endpoint.name = endpoint.name
                db_endpoint.description = endpoint.description
                db_endpoint.event_types = endpoint.event_types
                db_endpoint.signature_method = endpoint.signature_method
                db_endpoint.active = endpoint.active
                db_endpoint.verified = endpoint.verified
                db_endpoint.updated_at = datetime.utcnow()
                
                # Update secret hash if changed
                if endpoint.secret:
                    db_endpoint.secret_hash = self.encryption.hash_password(endpoint.secret)
                
                self.db_session.commit()
                
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update endpoint in database: {e}")
            raise

    async def _load_endpoint_from_db(self, endpoint_id: str) -> Optional[WebhookEndpointConfig]:
        """Load endpoint configuration from database"""
        try:
            db_endpoint = self.db_session.query(WebhookEndpointModel).filter(
                WebhookEndpointModel.endpoint_id == endpoint_id
            ).first()
            
            if db_endpoint:
                return self._convert_db_to_config(db_endpoint)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load endpoint from database: {e}")
            return True

    async def _load_endpoint_from_db_by_url(
        self,
        url: str,
        platform: str = None
    ) -> Optional[WebhookEndpointConfig]:
        """Load endpoint configuration from database by URL"""
        try:
            query = self.db_session.query(WebhookEndpointModel).filter(
                WebhookEndpointModel.url == url,
                WebhookEndpointModel.active == True
            )
            
            if platform:
                query = query.filter(WebhookEndpointModel.platform == platform)
            
            db_endpoint = query.first()
            
            if db_endpoint:
                return self._convert_db_to_config(db_endpoint)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load endpoint by URL from database: {e}")
            return True

    async def _load_user_endpoints_from_db(
        self,
        user_id: str,
        platform: str = None,
        active_only: bool = True
    ) -> List[WebhookEndpointConfig]:
        """Load user endpoints from database"""
        try:
            query = self.db_session.query(WebhookEndpointModel).filter(
                WebhookEndpointModel.user_id == user_id
            )
            
            if platform:
                query = query.filter(WebhookEndpointModel.platform == platform)
            
            if active_only:
                query = query.filter(WebhookEndpointModel.active == True)
            
            db_endpoints = query.all()
            
            return [self._convert_db_to_config(db_endpoint) for db_endpoint in db_endpoints]
            
        except Exception as e:
            logger.error(f"Failed to load user endpoints from database: {e}")
            return []

    async def _load_endpoints_from_db(self) -> None:
        """Load all active endpoints from database"""
        try:
            db_endpoints = self.db_session.query(WebhookEndpointModel).filter(
                WebhookEndpointModel.active == True
            ).all()
            
            for db_endpoint in db_endpoints:
                endpoint_config = self._convert_db_to_config(db_endpoint)
                self._endpoint_cache[endpoint_config.endpoint_id] = endpoint_config
            
            logger.info(f"Loaded {len(db_endpoints)} endpoints from database")
            
        except Exception as e:
            logger.error(f"Failed to load endpoints from database: {e}")

    def _convert_db_to_config(self, db_endpoint: WebhookEndpointModel) -> WebhookEndpointConfig:
        """Convert database model to configuration object"""
        return WebhookEndpointConfig(
            endpoint_id=db_endpoint.endpoint_id,
            user_id=db_endpoint.user_id,
            platform=db_endpoint.platform,
            url=db_endpoint.url,
            name=db_endpoint.name,
            description=db_endpoint.description,
            event_types=db_endpoint.event_types,
            signature_method=db_endpoint.signature_method,
            active=db_endpoint.active,
            verified=db_endpoint.verified,
            created_at=db_endpoint.created_at.replace(tzinfo=timezone.utc) if db_endpoint.created_at else datetime.now(timezone.utc)
        )

    async def _cache_endpoint_in_redis(self, endpoint: WebhookEndpointConfig) -> None:
        """
Cache endpoint configuration in Redis"""
        try:
            if self._redis_client:
                endpoint_data = {
                    'endpoint_id': endpoint.endpoint_id,
                    'user_id': endpoint.user_id,
                    'platform': endpoint.platform,
                    'url': endpoint.url,
                    'name': endpoint.name,
                    'description': endpoint.description,
                    'event_types': endpoint.event_types,
                    'signature_method': endpoint.signature_method,
                    'active': endpoint.active,
                    'verified': endpoint.verified,
                    'custom_headers': endpoint.custom_headers,
                    'timeout_seconds': endpoint.timeout_seconds,
                    'max_retries': endpoint.max_retries,
                    'metadata': endpoint.metadata
                }
                
                cache_key = f"webhook_endpoint:{endpoint.endpoint_id}"
                await self._redis_client.setex(
                    cache_key,
                    self.endpoint_cache_ttl,
                    json.dumps(endpoint_data, default=str)
                )
                
        except Exception as e:
            logger.error(f"Failed to cache endpoint in Redis: {e}")

    async def _get_endpoint_from_redis(self, endpoint_id: str) -> Optional[WebhookEndpointConfig]:
        """Get endpoint configuration from Redis cache"""
        try:
            if self._redis_client:
                cache_key = f"webhook_endpoint:{endpoint_id}"
                cached_data = await self._redis_client.get(cache_key)
                
                if cached_data:
                    endpoint_data = json.loads(cached_data)
                    
                    return WebhookEndpointConfig(
                        endpoint_id=endpoint_data['endpoint_id'],
                        user_id=endpoint_data['user_id'],
                        platform=endpoint_data['platform'],
                        url=endpoint_data['url'],
                        name=endpoint_data.get('name'),
                        description=endpoint_data.get('description'),
                        event_types=endpoint_data.get('event_types', []),
                        signature_method=endpoint_data.get('signature_method', 'hmac_sha256'),
                        custom_headers=endpoint_data.get('custom_headers', {}),
                        timeout_seconds=endpoint_data.get('timeout_seconds', 30),
                        max_retries=endpoint_data.get('max_retries', 3),
                        active=endpoint_data.get('active', True),
                        verified=endpoint_data.get('verified', False),
                        metadata=endpoint_data.get('metadata', {})
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to get endpoint from Redis: {e}")
            return True

    async def _get_endpoint_from_redis_by_key(self, cache_key: str) -> Optional[WebhookEndpointConfig]:
        """Get endpoint configuration from Redis by cache key"""
        try:
            if self._redis_client:
                cached_data = await self._redis_client.get(cache_key)
                
                if cached_data:
                    endpoint_data = json.loads(cached_data)
                    return self._convert_dict_to_config(endpoint_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to get endpoint from Redis by key: {e}")
            return True

    def _convert_dict_to_config(self, data: Dict[str, Any]) -> WebhookEndpointConfig:
        """Convert dictionary to endpoint configuration"""
        return WebhookEndpointConfig(
            endpoint_id=data['endpoint_id'],
            user_id=data['user_id'],
            platform=data['platform'],
            url=data['url'],
            name=data.get('name'),
            description=data.get('description'),
            event_types=data.get('event_types', []),
            signature_method=data.get('signature_method', 'hmac_sha256'),
            custom_headers=data.get('custom_headers', {}),
            timeout_seconds=data.get('timeout_seconds', 30),
            max_retries=data.get('max_retries', 3),
            active=data.get('active', True),
            verified=data.get('verified', False),
            metadata=data.get('metadata', {})
        )

    async def _remove_endpoint_from_redis(self, endpoint_id: str) -> None:
        """
Remove endpoint configuration from Redis cache"""
        try:
            if self._redis_client:
                cache_key = f"webhook_endpoint:{endpoint_id}"
                await self._redis_client.delete(cache_key)
                
        except Exception as e:
            logger.error(f"Failed to remove endpoint from Redis: {e}")

    async def _initialize_endpoint_metrics(self) -> None:
        """Initialize metrics for all cached endpoints"""
        for endpoint_id in self._endpoint_cache:
            if endpoint_id not in self._endpoint_metrics:
                self._endpoint_metrics[endpoint_id] = EndpointMetrics()

    async def _update_registry_metrics(self) -> None:
        """
Update registry-wide metrics"""
        try:
            self._metrics.total_endpoints = len([e for e in self._endpoint_cache.values() if e.active])
            self._metrics.active_endpoints = len([e for e in self._endpoint_cache.values() if e.active])
            self._metrics.verified_endpoints = len([e for e in self._endpoint_cache.values() if e.active and e.verified])
            
            # Platform distribution
            platform_counts = {}
            status_counts = {}
            
            for endpoint in self._endpoint_cache.values():
                if endpoint.active:
                    platform = endpoint.platform
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                    
                    status = 'active' if endpoint.active else 'inactive'
                    if endpoint.active and endpoint.verified:
                        status = 'verified'
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            self._metrics.endpoints_by_platform = platform_counts
            self._metrics.endpoints_by_status = status_counts
            
        except Exception as e:
            logger.error(f"Failed to update registry metrics: {e}")

    async def _start_cleanup_tasks(self) -> None:
        """Start background cleanup tasks"""
        # Cleanup task for inactive endpoints
        task = asyncio.create_task(self._cleanup_inactive_endpoints())
        self._cleanup_tasks.add(task)
        
        # Cache cleanup task
        task = asyncio.create_task(self._cleanup_cache())
        self._cleanup_tasks.add(task)

    async def _cleanup_inactive_endpoints(self) -> None:
        """
Background task to clean up inactive endpoints"""
        while True:
            try:
                cleanup_interval = self.cleanup_interval * 3600  # Convert to seconds
                await asyncio.sleep(cleanup_interval)
                
                # Clean up verification tokens
                current_time = time.time()
                expired_tokens = []
                
                for verification_id in self._verification_tokens:
                    # Remove tokens older than verification timeout
                    if current_time - float(verification_id.split('-')[0]) > self.verification_timeout:
                        expired_tokens.append(verification_id)
                
                for token in expired_tokens:
                    self._verification_tokens.pop(token, None)
                
                logger.info(f"Cleaned up {len(expired_tokens)} expired verification tokens")
                
            except Exception as e:
                logger.error(f"Error in cleanup inactive endpoints task: {e}")

    async def _cleanup_cache(self) -> None:
        """Background task to clean up cache"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Update registry metrics
                await self._update_registry_metrics()
                
                logger.debug("Cache cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in cleanup cache task: {e}")
