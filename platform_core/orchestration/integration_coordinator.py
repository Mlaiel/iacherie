"""
Integration Coordinator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Integration Coordinator - Enterprise Core Component
External system integration management system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive integration coordination capabilities including:
- External system integration management
- API gateway coordination
- Third-party service integration
- Data synchronization coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from contextlib import asynccontextmanager

# Optional import for aiohttp
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    # Create dummy class for type hints
    class aiohttp:
    """aiohttp: class implementation"""
        class ClientSession:
    """ClientSession: class implementation"""
            pass
        class ClientTimeout:
    """ClientTimeout: class implementation"""
            pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Integration type enumeration"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_TRANSFER = "file_transfer"
    STREAM = "stream"


class IntegrationStatus(Enum):
    """Integration status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


class AuthMethod(Enum):
    """Authentication method enumeration"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"
    NONE = "none"


@dataclass
class IntegrationConfig:
    """Integration configuration"""
    integration_id: str
    name: str
    type: IntegrationType
    endpoint: str
    auth_method: AuthMethod
    credentials: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    health_check_url: Optional[str] = None
    health_check_interval: int = 60
    rate_limit: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationMetrics:
    """Integration performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime_percentage: float = 100.0
    error_rate: float = 0.0
    throughput: float = 0.0


@dataclass
class IntegrationInstance:
    """Integration instance"""
    config: IntegrationConfig
    status: IntegrationStatus
    created_at: datetime
    last_health_check: Optional[datetime] = None
    metrics: IntegrationMetrics = field(default_factory=IntegrationMetrics)
    session: Optional[aiohttp.ClientSession] = None
    connection_pool: Optional[Any] = None


class IntegrationCoordinator:
    """
    Enterprise Integration Coordinator
    
    Manages comprehensive external system integrations with support for multiple
    protocols, authentication methods, and enterprise-grade reliability.
    """
    
    def __init__(self) -> None:
        self.integrations: Dict[str, IntegrationInstance] = {}
        self.integration_registry: Dict[str, IntegrationConfig] = {}
        self.active_connections: Dict[str, Any] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        self.integration_lock = asyncio.Lock()
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "integration_created": [],
            "integration_connected": [],
            "integration_disconnected": [],
            "integration_error": [],
            "health_check_failed": [],
            "rate_limit_exceeded": []
        }
        
        # Configuration
        self.max_concurrent_connections = 100
        self.connection_timeout = timedelta(minutes=5)
        self.health_check_enabled = True
        self.auto_retry_enabled = True
        
        logger.info("Integration Coordinator initialized")
    
    async def register_integration(self, config: IntegrationConfig) -> bool:
        """Register a new integration"""
        try:
            async with self.integration_lock:
                if config.integration_id in self.integration_registry:
                    logger.warning(f"Integration already registered: {config.integration_id}")
                    return False
                
                self.integration_registry[config.integration_id] = config
                
                # Create integration instance
                instance = IntegrationInstance(
                    config=config,
                    status=IntegrationStatus.INACTIVE,
                    created_at=datetime.utcnow()
                )
                
                self.integrations[config.integration_id] = instance
                
                # Trigger event
                await self._trigger_event("integration_created", config.integration_id)
                
                logger.info(f"Integration registered: {config.integration_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register integration {config.integration_id}: {e}")
            return False
    
    async def connect_integration(self, integration_id: str) -> bool:
        """Connect to an integration"""
        instance = self.integrations.get(integration_id)
        if not instance:
            logger.error(f"Integration not found: {integration_id}")
            return False
        
        try:
            instance.status = IntegrationStatus.CONNECTING
            
            # Create connection based on type
            if instance.config.type == IntegrationType.REST_API:
                success = await self._connect_rest_api(instance)
            elif instance.config.type == IntegrationType.WEBSOCKET:
                success = await self._connect_websocket(instance)
            elif instance.config.type == IntegrationType.DATABASE:
                success = await self._connect_database(instance)
            elif instance.config.type == IntegrationType.MESSAGE_QUEUE:
                success = await self._connect_message_queue(instance)
            else:
                success = await self._connect_generic(instance)
            
            if success:
                instance.status = IntegrationStatus.ACTIVE
                
                # Start health checking if enabled
                if self.health_check_enabled and instance.config.health_check_url:
                    await self._start_health_check(integration_id)
                
                await self._trigger_event("integration_connected", integration_id)
                logger.info(f"Integration connected: {integration_id}")
            else:
                instance.status = IntegrationStatus.ERROR
                await self._trigger_event("integration_error", integration_id)
                logger.error(f"Failed to connect integration: {integration_id}")
            
            return success
            
        except Exception as e:
            instance.status = IntegrationStatus.ERROR
            logger.error(f"Integration connection error {integration_id}: {e}")
            return False
    
    async def disconnect_integration(self, integration_id: str) -> bool:
        """Disconnect an integration"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return False
        
        try:
            # Stop health check
            if integration_id in self.health_check_tasks:
                self.health_check_tasks[integration_id].cancel()
                del self.health_check_tasks[integration_id]
            
            # Close connections
            if instance.session:
                await instance.session.close()
                instance.session = None
            
            if integration_id in self.active_connections:
                connection = self.active_connections[integration_id]
                if hasattr(connection, 'close'):
                    await connection.close()
                del self.active_connections[integration_id]
            
            instance.status = IntegrationStatus.DISCONNECTED
            await self._trigger_event("integration_disconnected", integration_id)
            
            logger.info(f"Integration disconnected: {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect integration {integration_id}: {e}")
            return False
    
    async def send_request(
        self,
        integration_id: str,
        method: str = "GET",
        path: str = "",
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Send request through integration"""
        instance = self.integrations.get(integration_id)
        if not instance or instance.status != IntegrationStatus.ACTIVE:
            logger.error(f"Integration not available: {integration_id}")
            return None
        
        start_time = datetime.utcnow()
        
        try:
            # Check rate limiting
            if not await self._check_rate_limit(integration_id):
                await self._trigger_event("rate_limit_exceeded", integration_id)
                return None
            
            # Prepare request
            url = f"{instance.config.endpoint.rstrip('/')}/{path.lstrip('/')}"
            request_headers = {**instance.config.headers}
            if headers:
                request_headers.update(headers)
            
            # Add authentication
            await self._add_authentication(instance, request_headers)
            
            # Send request
            if instance.config.type == IntegrationType.REST_API:
                response = await self._send_rest_request(
                    instance, method, url, data, request_headers, params
                )
            elif instance.config.type == IntegrationType.GRAPHQL:
                response = await self._send_graphql_request(
                    instance, data, request_headers
                )
            else:
                response = await self._send_generic_request(
                    instance, method, url, data, request_headers, params
                )
            
            # Update metrics
            await self._update_metrics(instance, start_time, True)
            
            return response
            
        except Exception as e:
            await self._update_metrics(instance, start_time, False)
            logger.error(f"Request failed for integration {integration_id}: {e}")
            
            # Retry if configured
            if self.auto_retry_enabled and instance.config.retry_count > 0:
                return await self._retry_request(
                    integration_id, method, path, data, headers, params
                )
            
            return None
    
    async def send_webhook(
        self,
        integration_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send webhook to integration"""
        instance = self.integrations.get(integration_id)
        if not instance or instance.config.type != IntegrationType.WEBHOOK:
            return False
        
        try:
            webhook_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload
            }
            
            response = await self.send_request(
                integration_id,
                method="POST",
                data=webhook_data
            )
            
            return response is not None
            
        except Exception as e:
            logger.error(f"Webhook send failed for {integration_id}: {e}")
            return False
    
    async def get_integration_status(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration status"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return None
        
        return {
            "integration_id": integration_id,
            "name": instance.config.name,
            "type": instance.config.type.value,
            "status": instance.status.value,
            "created_at": instance.created_at.isoformat(),
            "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None,
            "metrics": {
                "total_requests": instance.metrics.total_requests,
                "successful_requests": instance.metrics.successful_requests,
                "failed_requests": instance.metrics.failed_requests,
                "average_response_time": instance.metrics.average_response_time,
                "uptime_percentage": instance.metrics.uptime_percentage,
                "error_rate": instance.metrics.error_rate,
                "throughput": instance.metrics.throughput
            }
        }
    
    async def list_integrations(self, status_filter: Optional[IntegrationStatus] = None) -> List[Dict[str, Any]]:
        """List all integrations"""
        integrations = []
        
        for integration_id, instance in self.integrations.items():
            if status_filter and instance.status != status_filter:
                continue
            
            status_info = await self.get_integration_status(integration_id)
            if status_info:
                integrations.append(status_info)
        
        return integrations
    
    async def get_integration_metrics(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed integration metrics"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return None
        
        metrics = instance.metrics
        return {
            "integration_id": integration_id,
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "success_rate": (metrics.successful_requests / max(metrics.total_requests, 1)) * 100,
            "error_rate": metrics.error_rate,
            "average_response_time": metrics.average_response_time,
            "uptime_percentage": metrics.uptime_percentage,
            "throughput": metrics.throughput,
            "last_request_time": metrics.last_request_time.isoformat() if metrics.last_request_time else None
        }
    
    async def update_integration_config(
        self,
        integration_id: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """Update integration configuration"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return False
        
        try:
            # Update configuration
            for key, value in config_updates.items():
                if hasattr(instance.config, key):
                    setattr(instance.config, key, value)
            
            # Update registry
            self.integration_registry[integration_id] = instance.config
            
            logger.info(f"Integration config updated: {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update config for {integration_id}: {e}")
            return False
    
    async def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test integration connectivity"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return {"status": "error", "message": "Integration not found"}
        
        start_time = datetime.utcnow()
        
        try:
            # Test basic connectivity
            if instance.config.health_check_url:
                response = await self.send_request(
                    integration_id,
                    method="GET",
                    path=instance.config.health_check_url
                )
                success = response is not None
            else:
                # Basic endpoint test
                response = await self.send_request(integration_id, method="GET")
                success = response is not None
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "success" if success else "error",
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat(),
                "integration_status": instance.status.value
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def add_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Add event handler"""
        if event_type not in self.event_handlers:
            return False
        
        self.event_handlers[event_type].append(handler)
        return True
    
    async def remove_event_handler(self, event_type: str, handler: Callable) -> bool:
        """Remove event handler"""
        if event_type not in self.event_handlers:
            return False
        
        try:
            self.event_handlers[event_type].remove(handler)
            return True
        except ValueError:
            return False
    
    # Private methods
    
    async def _connect_rest_api(self, instance: IntegrationInstance) -> bool:
        """Connect to REST API"""
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available - using simulation mode")
            await asyncio.sleep(0.1)
            return True
            
        try:
            timeout = aiohttp.ClientTimeout(total=instance.config.timeout)
            instance.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            async with instance.session.get(instance.config.endpoint) as response:
                return response.status < 400
                
        except Exception as e:
            logger.error(f"REST API connection failed: {e}")
            return False
    
    async def _connect_websocket(self, instance: IntegrationInstance) -> bool:
        """Connect to WebSocket"""
        try:
            # WebSocket connection logic would go here
            # For now, simulate connection
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def _connect_database(self, instance: IntegrationInstance) -> bool:
        """Connect to database"""
        try:
            # Database connection logic would go here
            # For now, simulate connection
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def _connect_message_queue(self, instance: IntegrationInstance) -> bool:
        """Connect to message queue"""
        try:
            # Message queue connection logic would go here
            # For now, simulate connection
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Message queue connection failed: {e}")
            return False
    
    async def _connect_generic(self, instance: IntegrationInstance) -> bool:
        """Generic connection handler"""
        try:
            # Generic connection logic
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Generic connection failed: {e}")
            return False
    
    async def _send_rest_request(
        self,
        instance: IntegrationInstance,
        method: str,
        url: str,
        data: Optional[Any],
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Send REST request"""
        if not AIOHTTP_AVAILABLE or not instance.session:
            logger.warning("aiohttp not available - simulating request")
            await asyncio.sleep(0.1)
            return {"simulated": True, "status": "ok"}
        
        try:
            kwargs = {
                "headers": headers,
                "params": params
            }
            
            if data:
                if method.upper() in ["POST", "PUT", "PATCH"]:
                    kwargs["json"] = data
            
            async with instance.session.request(method, url, **kwargs) as response:
                if response.status < 400:
                    return await response.json()
                else:
                    logger.error(f"HTTP {response.status}: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"REST request failed: {e}")
            return None
    
    async def _send_graphql_request(
        self,
        instance: IntegrationInstance,
        query_data: Any,
        headers: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Send GraphQL request"""
        if not AIOHTTP_AVAILABLE or not instance.session:
            logger.warning("aiohttp not available - simulating GraphQL request")
            await asyncio.sleep(0.1)
            return {"simulated": True, "data": {}}
        
        try:
            async with instance.session.post(
                instance.config.endpoint,
                json=query_data,
                headers=headers
            ) as response:
                if response.status < 400:
                    return await response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"GraphQL request failed: {e}")
            return None
    
    async def _send_generic_request(
        self,
        instance: IntegrationInstance,
        method: str,
        url: str,
        data: Optional[Any],
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Send generic request"""
        # Default to REST-like behavior
        return await self._send_rest_request(instance, method, url, data, headers, params)
    
    async def _add_authentication(self, instance -> None: IntegrationInstance, headers -> None: Dict[str, str]) -> None:
        """Add authentication to headers"""
        auth_method = instance.config.auth_method
        credentials = instance.config.credentials
        
        if auth_method == AuthMethod.API_KEY:
            key_name = credentials.get("key_name", "X-API-Key")
            api_key = credentials.get("api_key")
            if api_key:
                headers[key_name] = api_key
        
        elif auth_method == AuthMethod.BEARER_TOKEN:
            token = credentials.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        elif auth_method == AuthMethod.BASIC_AUTH:
            username = credentials.get("username")
            password = credentials.get("password")
            if username and password:
                import base64
                auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers["Authorization"] = f"Basic {auth_string}"
        
        # OAuth2 and certificate auth would need more complex handling
    
    async def _check_rate_limit(self, integration_id: str) -> bool:
        """Check rate limiting"""
        instance = self.integrations.get(integration_id)
        if not instance or not instance.config.rate_limit:
            return True
        
        # Simple rate limiting implementation
        # In production, this would use Redis or similar
        return True
    
    async def _update_metrics(self, instance -> None: IntegrationInstance, start_time -> None: datetime, success -> None: bool) -> None:
        """Update integration metrics"""
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        instance.metrics.total_requests += 1
        instance.metrics.last_request_time = datetime.utcnow()
        
        if success:
            instance.metrics.successful_requests += 1
        else:
            instance.metrics.failed_requests += 1
        
        # Update averages
        instance.metrics.average_response_time = (
            (instance.metrics.average_response_time * (instance.metrics.total_requests - 1) + response_time) /
            instance.metrics.total_requests
        )
        
        instance.metrics.error_rate = (
            instance.metrics.failed_requests / instance.metrics.total_requests
        ) * 100
    
    async def _retry_request(
        self,
        integration_id: str,
        method: str,
        path: str,
        data: Optional[Any],
        headers: Optional[Dict[str, str]],
        params: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Retry failed request"""
        instance = self.integrations.get(integration_id)
        if not instance:
            return None
        
        for attempt in range(instance.config.retry_count):
            await asyncio.sleep(instance.config.retry_delay * (2 ** attempt))
            
            result = await self.send_request(integration_id, method, path, data, headers, params)
            if result is not None:
                return result
        
        return None
    
    async def _start_health_check(self, integration_id -> None: str) -> None:
        """Start health check task"""
        async def health_check_loop() -> None:
            while True:
                try:
                    instance = self.integrations.get(integration_id)
                    if not instance or instance.status != IntegrationStatus.ACTIVE:
                        break
                    
                    # Perform health check
                    test_result = await self.test_integration(integration_id)
                    instance.last_health_check = datetime.utcnow()
                    
                    if test_result["status"] != "success":
                        await self._trigger_event("health_check_failed", integration_id)
                        instance.status = IntegrationStatus.ERROR
                        break
                    
                    await asyncio.sleep(instance.config.health_check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health check error for {integration_id}: {e}")
                    break
        
        task = asyncio.create_task(health_check_loop())
        self.health_check_tasks[integration_id] = task
    
    async def _trigger_event(self, event_type -> None: str, integration_id -> None: str) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(integration_id)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
integration_coordinator = IntegrationCoordinator()


# Convenience functions
async def register_rest_api(
    integration_id: str,
    name: str,
    endpoint: str,
    auth_method: AuthMethod = AuthMethod.NONE,
    credentials: Optional[Dict[str, Any]] = None
) -> bool:
    """Register REST API integration"""
    config = IntegrationConfig(
        integration_id=integration_id,
        name=name,
        type=IntegrationType.REST_API,
        endpoint=endpoint,
        auth_method=auth_method,
        credentials=credentials or {}
    )
    return await integration_coordinator.register_integration(config)


async def connect(integration_id: str) -> bool:
    """Connect integration"""
    return await integration_coordinator.connect_integration(integration_id)


async def disconnect(integration_id: str) -> bool:
    """Disconnect integration"""
    return await integration_coordinator.disconnect_integration(integration_id)


async def send_request(
    integration_id: str,
    method: str = "GET",
    path: str = "",
    data: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """Send request through integration"""
    return await integration_coordinator.send_request(integration_id, method, path, data)


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Register a REST API integration
        await register_rest_api(
            "external_api",
            "External API Service",
            "https://api.example.com",
            AuthMethod.API_KEY,
            {"api_key": "test-key"}
        )
        
        # Connect to the integration
        connected = await connect("external_api")
        print(f"Connected: {connected}")
        
        # Send a request
        response = await send_request("external_api", "GET", "/users")
        print(f"Response: {response}")
        
        # Get status
        status = await integration_coordinator.get_integration_status("external_api")
        print(f"Status: {status}")
    
    asyncio.run(main())