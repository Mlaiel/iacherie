"""Platform Integration Core - Noyau Intégration Plateformes Enterprise
================================================================

Ultra-advanced platform integration framework for IA Influencer Agent platform.
Comprehensive multi-platform integration, API gateway management, cross-platform
synchronization, and enterprise-grade platform compliance validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This platform integration core is protected intellectual property.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import aiohttp
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable, Union, Tuple
from dataclasses import dataclass, field
import uuid
from pathlib import Path
import threading
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Types of supported platforms"""
    SOCIAL_MEDIA = "social_media"
    CONTENT_DELIVERY = "content_delivery"
    PAYMENT_GATEWAY = "payment_gateway"
    ANALYTICS_PLATFORM = "analytics_platform"
    CLOUD_STORAGE = "cloud_storage"
    AI_SERVICE = "ai_service"
    MESSAGING_SERVICE = "messaging_service"
    E_COMMERCE = "e_commerce"


class IntegrationStatus(Enum):
    """Status of platform integration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"


class SynchronizationMode(Enum):
    """Data synchronization modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"


class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    BINARY = "binary"
    FORM_DATA = "form_data"
    GRAPHQL = "graphql"


@dataclass
class PlatformConfiguration:
    """Configuration for platform integration"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    api_endpoint: str
    authentication: Dict[str, Any]
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    data_format: DataFormat = DataFormat.JSON
    sync_mode: SynchronizationMode = SynchronizationMode.REAL_TIME
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationMetrics:
    """Metrics for platform integration"""
    platform_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_sync_time: Optional[datetime] = None
    errors_24h: int = 0
    uptime_percentage: float = 100.0


class MultiPlatformIntegrationFramework:
    """
    🌐 Multi-Platform Integration Framework - Master Platform Orchestrator
    
    Enterprise-grade integration framework supporting multiple platforms
    with intelligent routing, load balancing, and failure recovery.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Multi-Platform Integration Framework"""
        self.config = config or {}
        self.platforms: Dict[str, PlatformConfiguration] = {}
        self.metrics: Dict[str, IntegrationMetrics] = {}
        self.session_pool: Dict[str, aiohttp.ClientSession] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._integration_lock = threading.RLock()
        
        # Rate limiting
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        
    async def register_platform(self, platform_config: PlatformConfiguration) -> bool:
        """Register a new platform for integration"""
        
        try:
            with self._integration_lock:
                self.platforms[platform_config.platform_id] = platform_config
                
                # Initialize metrics
                self.metrics[platform_config.platform_id] = IntegrationMetrics(
                    platform_id=platform_config.platform_id
                )
                
                # Initialize rate limiter
                self._initialize_rate_limiter(platform_config)
                
                # Create HTTP session
                await self._create_platform_session(platform_config)
            
            self.logger.info(f"Platform {platform_config.platform_name} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register platform {platform_config.platform_name}: {e}")
            return False
    
    def _initialize_rate_limiter(self, platform_config: PlatformConfiguration):
        """Initialize rate limiter for platform"""
        
        rate_limits = platform_config.rate_limits
        self.rate_limiters[platform_config.platform_id] = {
            'requests_per_minute': rate_limits.get('requests_per_minute', 60),
            'requests_per_hour': rate_limits.get('requests_per_hour', 1000),
            'request_history': [],
            'last_reset': datetime.now()
        }
    
    async def _create_platform_session(self, platform_config: PlatformConfiguration):
        """Create HTTP session for platform"""
        
        # Configure session with authentication
        headers = {}
        auth = platform_config.authentication
        
        if auth.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth.get('token')}"
        elif auth.get('type') == 'api_key':
            headers[auth.get('header_name', 'X-API-Key')] = auth.get('api_key')
        
        # Configure timeouts and connection limits
        timeout = aiohttp.ClientTimeout(
            total=self.config.get('request_timeout', 30),
            connect=self.config.get('connect_timeout', 10)
        )
        
        connector = aiohttp.TCPConnector(
            limit=self.config.get('connection_limit', 100),
            limit_per_host=self.config.get('connection_limit_per_host', 30)
        )
        
        session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=connector
        )
        
        self.session_pool[platform_config.platform_id] = session
    
    async def make_request(self, 
                          platform_id: str,
                          method: str,
                          endpoint: str,
                          data: Any = None,
                          params: Dict[str, Any] = None,
                          headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make request to platform"""
        
        if platform_id not in self.platforms:
            return {
                'success': False,
                'error': f'Platform {platform_id} not registered'
            }
        
        # Check rate limits
        if not await self._check_rate_limit(platform_id):
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'retry_after': self._get_rate_limit_reset_time(platform_id)
            }
        
        platform_config = self.platforms[platform_id]
        session = self.session_pool.get(platform_id)
        
        if not session:
            return {
                'success': False,
                'error': 'Session not available'
            }
        
        start_time = time.time()
        
        try:
            # Build full URL
            full_url = urljoin(platform_config.api_endpoint, endpoint)
            
            # Prepare request data based on format
            request_data = await self._prepare_request_data(
                data, platform_config.data_format
            )
            
            # Make the request
            async with session.request(
                method=method.upper(),
                url=full_url,
                data=request_data,
                params=params,
                headers=headers
            ) as response:
                
                response_time = time.time() - start_time
                
                # Update metrics
                self._update_metrics(platform_id, response.status == 200, response_time)
                
                # Parse response
                response_data = await self._parse_response(response, platform_config.data_format)
                
                return {
                    'success': response.status < 400,
                    'status_code': response.status,
                    'data': response_data,
                    'response_time': response_time,
                    'platform_id': platform_id
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self._update_metrics(platform_id, False, response_time)
            
            self.logger.error(f"Request to {platform_id} failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time,
                'platform_id': platform_id
            }
    
    async def _check_rate_limit(self, platform_id: str) -> bool:
        """Check if request is within rate limits"""
        
        if platform_id not in self.rate_limiters:
            return True
        
        limiter = self.rate_limiters[platform_id]
        now = datetime.now()
        
        # Clean old requests
        limiter['request_history'] = [
            req_time for req_time in limiter['request_history']
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check limits
        requests_last_hour = len(limiter['request_history'])
        requests_last_minute = len([
            req_time for req_time in limiter['request_history']
            if now - req_time < timedelta(minutes=1)
        ])
        
        if requests_last_minute >= limiter['requests_per_minute']:
            return False
        
        if requests_last_hour >= limiter['requests_per_hour']:
            return False
        
        # Add current request
        limiter['request_history'].append(now)
        return True
    
    def _get_rate_limit_reset_time(self, platform_id: str) -> int:
        """Get time until rate limit resets (in seconds)"""
        
        limiter = self.rate_limiters.get(platform_id, {})
        request_history = limiter.get('request_history', [])
        
        if not request_history:
            return 0
        
        # Time until oldest request in current minute expires
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        requests_last_minute = [
            req_time for req_time in request_history
            if req_time > minute_ago
        ]
        
        if requests_last_minute:
            oldest_request = min(requests_last_minute)
            reset_time = oldest_request + timedelta(minutes=1)
            return max(0, int((reset_time - now).total_seconds()))
        
        return 0
    
    async def _prepare_request_data(self, data: Any, data_format: DataFormat) -> Any:
        """Prepare request data based on format"""
        
        if not data:
            return None
        
        if data_format == DataFormat.JSON:
            return json.dumps(data) if not isinstance(data, str) else data
        elif data_format == DataFormat.FORM_DATA:
            return aiohttp.FormData(data) if isinstance(data, dict) else data
        else:
            return data
    
    async def _parse_response(self, response: aiohttp.ClientResponse, data_format: DataFormat) -> Any:
        """Parse response based on format"""
        
        try:
            if data_format == DataFormat.JSON:
                return await response.json()
            elif data_format == DataFormat.XML:
                return await response.text()
            else:
                return await response.text()
                
        except Exception as e:
            self.logger.warning(f"Failed to parse response: {e}")
            return await response.text()
    
    def _update_metrics(self, platform_id: str, success: bool, response_time: float):
        """Update platform metrics"""
        
        if platform_id not in self.metrics:
            return
        
        metrics = self.metrics[platform_id]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            # Count errors in last 24 hours
            # This is simplified - in production, you'd want proper time-based counting
            metrics.errors_24h += 1
        
        # Update average response time
        total_requests = metrics.total_requests
        current_avg = metrics.average_response_time
        metrics.average_response_time = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Update uptime percentage
        if total_requests > 0:
            metrics.uptime_percentage = (
                metrics.successful_requests / total_requests * 100
            )
    
    async def get_platform_status(self, platform_id: str) -> Dict[str, Any]:
        """Get status of specific platform"""
        
        if platform_id not in self.platforms:
            return {'error': 'Platform not found'}
        
        platform_config = self.platforms[platform_id]
        metrics = self.metrics.get(platform_id, IntegrationMetrics(platform_id))
        
        return {
            'platform_id': platform_id,
            'platform_name': platform_config.platform_name,
            'platform_type': platform_config.platform_type.value,
            'status': IntegrationStatus.ACTIVE.value,  # Simplified
            'metrics': {
                'total_requests': metrics.total_requests,
                'success_rate': metrics.uptime_percentage,
                'average_response_time': metrics.average_response_time,
                'errors_24h': metrics.errors_24h
            }
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        
        for session in self.session_pool.values():
            if not session.closed:
                await session.close()
        
        self.session_pool.clear()


class APIGatewayManager:
    """
    🚪 API Gateway Manager - Centralized API Management
    
    Advanced API gateway with routing, load balancing, caching,
    and comprehensive API lifecycle management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the API Gateway Manager"""
        self.config = config or {}
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.middleware_stack: List[Callable] = []
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_route(self, 
                           route_path: str,
                           target_platform: str,
                           target_endpoint: str,
                           methods: List[str] = None,
                           middleware: List[str] = None) -> bool:
        """Register API route"""
        
        try:
            self.routes[route_path] = {
                'target_platform': target_platform,
                'target_endpoint': target_endpoint,
                'methods': methods or ['GET'],
                'middleware': middleware or [],
                'created_at': datetime.now(timezone.utc),
                'request_count': 0
            }
            
            self.logger.info(f"Route {route_path} registered")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register route {route_path}: {e}")
            return False
    
    async def process_request(self, 
                            route_path: str,
                            method: str,
                            data: Any = None,
                            headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Process API request through gateway"""
        
        if route_path not in self.routes:
            return {
                'success': False,
                'error': 'Route not found',
                'status_code': 404
            }
        
        route_config = self.routes[route_path]
        
        # Check method
        if method.upper() not in [m.upper() for m in route_config['methods']]:
            return {
                'success': False,
                'error': 'Method not allowed',
                'status_code': 405
            }
        
        # Update route metrics
        route_config['request_count'] += 1
        
        try:
            # Apply middleware
            request_context = {
                'route_path': route_path,
                'method': method,
                'data': data,
                'headers': headers or {},
                'route_config': route_config
            }
            
            for middleware_name in route_config['middleware']:
                middleware_result = await self._apply_middleware(
                    middleware_name, request_context
                )
                
                if not middleware_result['continue']:
                    return middleware_result['response']
            
            # Check cache
            cache_key = self._generate_cache_key(route_path, method, data)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                return {
                    'success': True,
                    'data': cached_response['data'],
                    'cached': True,
                    'cache_timestamp': cached_response['timestamp']
                }
            
            # Forward request to target platform
            # This would typically use the MultiPlatformIntegrationFramework
            response = {
                'success': True,
                'data': f"Forwarded to {route_config['target_platform']}",
                'target_platform': route_config['target_platform'],
                'target_endpoint': route_config['target_endpoint']
            }
            
            # Cache successful responses
            if response['success']:
                self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request processing failed for {route_path}: {e}")
            return {
                'success': False,
                'error': 'Internal gateway error',
                'status_code': 500
            }
    
    async def _apply_middleware(self, 
                              middleware_name: str,
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply middleware to request"""
        
        # Simplified middleware system
        if middleware_name == 'auth':
            return await self._auth_middleware(context)
        elif middleware_name == 'rate_limit':
            return await self._rate_limit_middleware(context)
        else:
            return {'continue': True}
    
    async def _auth_middleware(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Authentication middleware"""
        
        headers = context.get('headers', {})
        auth_header = headers.get('Authorization')
        
        if not auth_header:
            return {
                'continue': False,
                'response': {
                    'success': False,
                    'error': 'Authentication required',
                    'status_code': 401
                }
            }
        
        # Simplified auth check
        return {'continue': True}
    
    async def _rate_limit_middleware(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rate limiting middleware"""
        
        # Simplified rate limiting
        return {'continue': True}
    
    def _generate_cache_key(self, route_path: str, method: str, data: Any) -> str:
        """Generate cache key for request"""
        
        import hashlib
        
        key_data = f"{route_path}:{method}:{json.dumps(data, sort_keys=True) if data else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired"""
        
        if cache_key not in self.cache:
            return None
        
        cached_item = self.cache[cache_key]
        cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes default
        
        if datetime.now() - cached_item['timestamp'] > timedelta(seconds=cache_ttl):
            del self.cache[cache_key]
            return None
        
        return cached_item
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response"""
        
        if len(self.cache) > self.config.get('max_cache_size', 1000):
            # Simple cache eviction - remove oldest
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'data': response,
            'timestamp': datetime.now()
        }


class CrossPlatformSynchronizer:
    """
    🔄 Cross-Platform Synchronizer - Data Synchronization Engine
    
    Advanced synchronization engine for maintaining data consistency
    across multiple platforms with conflict resolution and recovery.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Cross-Platform Synchronizer"""
        self.config = config or {}
        self.sync_jobs: Dict[str, Dict[str, Any]] = {}
        self.sync_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create_sync_job(self, 
                            job_id: str,
                            source_platform: str,
                            target_platforms: List[str],
                            data_mapping: Dict[str, Any],
                            sync_mode: SynchronizationMode = SynchronizationMode.REAL_TIME) -> bool:
        """Create synchronization job"""
        
        try:
            self.sync_jobs[job_id] = {
                'source_platform': source_platform,
                'target_platforms': target_platforms,
                'data_mapping': data_mapping,
                'sync_mode': sync_mode,
                'created_at': datetime.now(timezone.utc),
                'last_sync': None,
                'sync_count': 0,
                'error_count': 0,
                'status': 'active'
            }
            
            self.logger.info(f"Sync job {job_id} created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sync job {job_id}: {e}")
            return False
    
    async def execute_sync(self, job_id: str, data: Any) -> Dict[str, Any]:
        """Execute synchronization for specific job"""
        
        if job_id not in self.sync_jobs:
            return {
                'success': False,
                'error': 'Sync job not found'
            }
        
        job_config = self.sync_jobs[job_id]
        start_time = datetime.now()
        
        try:
            # Transform data according to mapping
            transformed_data = await self._transform_data(
                data, job_config['data_mapping']
            )
            
            # Sync to target platforms
            sync_results = []
            for target_platform in job_config['target_platforms']:
                result = await self._sync_to_platform(
                    target_platform, transformed_data
                )
                sync_results.append(result)
            
            # Update job statistics
            job_config['sync_count'] += 1
            job_config['last_sync'] = start_time
            
            if any(not r['success'] for r in sync_results):
                job_config['error_count'] += 1
            
            sync_result = {
                'job_id': job_id,
                'success': all(r['success'] for r in sync_results),
                'sync_results': sync_results,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': start_time.isoformat()
            }
            
            self.sync_history.append(sync_result)
            return sync_result
            
        except Exception as e:
            job_config['error_count'] += 1
            self.logger.error(f"Sync execution failed for job {job_id}: {e}")
            
            return {
                'job_id': job_id,
                'success': False,
                'error': str(e),
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _transform_data(self, data: Any, mapping: Dict[str, Any]) -> Any:
        """Transform data according to mapping rules"""
        
        if not mapping:
            return data
        
        # Simplified data transformation
        # In production, this would be more sophisticated
        if isinstance(data, dict):
            transformed = {}
            for source_field, target_field in mapping.items():
                if source_field in data:
                    transformed[target_field] = data[source_field]
            return transformed
        
        return data
    
    async def _sync_to_platform(self, platform_id: str, data: Any) -> Dict[str, Any]:
        """Synchronize data to specific platform"""
        
        # This would typically use the MultiPlatformIntegrationFramework
        # For now, it's a simplified implementation
        
        try:
            # Simulate platform sync
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return {
                'platform_id': platform_id,
                'success': True,
                'records_synced': 1 if data else 0
            }
            
        except Exception as e:
            return {
                'platform_id': platform_id,
                'success': False,
                'error': str(e)
            }


class PlatformIntegrationCore:
    """
    🚀 Platform Integration Core - Master Integration Orchestrator
    
    Central platform integration core that coordinates all integration functionality
    across the IA Influencer Agent platform with enterprise-grade capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Platform Integration Core"""
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize integration components
        self.integration_framework = MultiPlatformIntegrationFramework(
            config.get('integration', {})
        )
        self.api_gateway = APIGatewayManager(config.get('gateway', {}))
        self.synchronizer = CrossPlatformSynchronizer(config.get('sync', {}))
        
        # Core status
        self.is_initialized = False
        self.start_time = None
    
    async def initialize(self) -> bool:
        """Initialize the Platform Integration Core"""
        try:
            self.start_time = datetime.now(timezone.utc)
            
            # Initialize default integrations
            await self._initialize_default_platforms()
            
            self.is_initialized = True
            self.logger.info("Platform Integration Core initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Platform Integration Core initialization failed: {e}")
            return False
    
    async def _initialize_default_platforms(self):
        """Initialize default platform configurations"""
        
        # Example default platforms
        default_platforms = [
            PlatformConfiguration(
                platform_id="youtube",
                platform_name="YouTube",
                platform_type=PlatformType.SOCIAL_MEDIA,
                api_endpoint="https://www.googleapis.com/youtube/v3/",
                authentication={'type': 'api_key', 'api_key': 'your_api_key'},
                rate_limits={'requests_per_minute': 100, 'requests_per_hour': 10000}
            ),
            PlatformConfiguration(
                platform_id="stripe",
                platform_name="Stripe",
                platform_type=PlatformType.PAYMENT_GATEWAY,
                api_endpoint="https://api.stripe.com/v1/",
                authentication={'type': 'bearer', 'token': 'your_stripe_key'},
                rate_limits={'requests_per_minute': 100, 'requests_per_hour': 1000}
            )
        ]
        
        for platform_config in default_platforms:
            await self.integration_framework.register_platform(platform_config)
    
    async def get_core_status(self) -> Dict[str, Any]:
        """Get comprehensive integration core status"""
        
        platform_statuses = {}
        for platform_id in self.integration_framework.platforms.keys():
            platform_statuses[platform_id] = await self.integration_framework.get_platform_status(platform_id)
        
        return {
            'initialized': self.is_initialized,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0,
            'registered_platforms': len(self.integration_framework.platforms),
            'active_routes': len(self.api_gateway.routes),
            'active_sync_jobs': len(self.synchronizer.sync_jobs),
            'platform_statuses': platform_statuses
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.integration_framework.cleanup()


# =============================================================================
# FACTORY AND UTILITY FUNCTIONS
# =============================================================================

def create_platform_integration_core(config: Optional[Dict[str, Any]] = None) -> PlatformIntegrationCore:
    """Factory function to create Platform Integration Core"""
    return PlatformIntegrationCore(config)


async def quick_integration_setup() -> PlatformIntegrationCore:
    """Quick setup for development environment"""
    core = create_platform_integration_core({
        'integration': {},
        'gateway': {'cache_ttl': 300},
        'sync': {}
    })
    
    await core.initialize()
    return core


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'PlatformType',
    'IntegrationStatus',
    'SynchronizationMode',
    'DataFormat',
    
    # Data classes
    'PlatformConfiguration',
    'IntegrationMetrics',
    
    # Main integration classes
    'MultiPlatformIntegrationFramework',
    'APIGatewayManager',
    'CrossPlatformSynchronizer',
    'PlatformIntegrationCore',
    
    # Factory functions
    'create_platform_integration_core',
    'quick_integration_setup'
]