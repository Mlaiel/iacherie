"""Handlers Index Module
====================

Main entry point for all crawler handlers with factory functions and configuration.
Provides simplified access to enterprise-grade handler systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""
import asyncio
import logging
from typing import Dict, Optional, Any
import aioredis

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.utils.redis_client import get_redis_client
from backend.utils.encryption_utils import EncryptionManager
from backend.utils.compression_utils import CompressionManager
from backend.utils.notification_utils import NotificationManager
from backend.utils.metrics_utils import MetricsCollector
from backend.utils.alert_utils import AlertManager

# Import all handlers
from .content_handler import create_content_handler, ContentHandler
from .event_handler import create_event_dispatcher, EventDispatcher
from .response_handler import create_response_handler, ResponseHandler
from .error_handler import create_error_handler, ErrorHandler
from .retry_handler import create_retry_handler, RetryHandler
from .data_handler import create_data_handler, DataHandler

logger = get_logger(__name__)


class HandlersManager:
    """    Centralized manager for all crawler handlers.
    Provides unified access and lifecycle management.
    """    
    def __init__(self):
        self.content_handler: Optional[ContentHandler] = None
        self.event_dispatcher: Optional[EventDispatcher] = None
        self.response_handler: Optional[ResponseHandler] = None
        self.error_handler: Optional[ErrorHandler] = None
        self.retry_handler: Optional[RetryHandler] = None
        self.data_handler: Optional[DataHandler] = None
        
        self._redis_client: Optional[aioredis.Redis] = None
        self._initialized = False
    
    async def initialize(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        notification_manager: Optional[NotificationManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        alert_manager: Optional[AlertManager] = None,
        encryption_manager: Optional[EncryptionManager] = None,
        compression_manager: Optional[CompressionManager] = None
    ) -> bool:
        """        Initialize all handlers with dependencies.
        
        Args:
            redis_client: Redis client for caching and queuing
            notification_manager: Notification system
            metrics_collector: Metrics collection system
            alert_manager: Alert management system
            encryption_manager: Data encryption system
            compression_manager: Data compression system
            
        Returns:
            True if initialization successful
        """        try:
            logger.info("Initializing Handlers Manager...")
            
            # Get or create Redis client
            if redis_client is None:
                self._redis_client = await get_redis_client()
            else:
                self._redis_client = redis_client
            
            # Initialize utility managers if not provided
            if encryption_manager is None:
                encryption_manager = EncryptionManager()
            
            if compression_manager is None:
                compression_manager = CompressionManager()
            
            # Initialize handlers
            self.content_handler = create_content_handler()
            
            self.event_dispatcher = await create_event_dispatcher(
                redis_client=self._redis_client
            )
            
            self.response_handler = create_response_handler()
            
            self.error_handler = create_error_handler(
                notification_manager=notification_manager,
                metrics_collector=metrics_collector,
                alert_manager=alert_manager
            )
            
            self.retry_handler = await create_retry_handler(
                redis_client=self._redis_client,
                metrics_collector=metrics_collector
            )
            
            self.data_handler = create_data_handler(
                encryption_manager=encryption_manager,
                compression_manager=compression_manager
            )
            
            # Start event workers
            await self.event_dispatcher.start_workers()
            
            self._initialized = True
            logger.info("Handlers Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Handlers Manager initialization failed: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown all handlers."""        try:
            logger.info("Shutting down Handlers Manager...")
            
            if self.event_dispatcher and self._initialized:
                await self.event_dispatcher.stop_workers()
            
            if self._redis_client:
                await self._redis_client.close()
            
            self._initialized = False
            logger.info("Handlers Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Handlers Manager shutdown failed: {e}")
    
    def is_ready(self) -> bool:
        """Check if all handlers are ready."""        return (
            self._initialized and
            self.content_handler is not None and
            self.event_dispatcher is not None and
            self.response_handler is not None and
            self.error_handler is not None and
            self.retry_handler is not None and
            self.data_handler is not None
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all handlers."""        try:
            health_status = {
                'overall_status': 'healthy',
                'initialized': self._initialized,
                'handlers': {},
                'dependencies': {},
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Check individual handlers
            health_status['handlers'] = {
                'content_handler': self.content_handler is not None,
                'event_dispatcher': self.event_dispatcher is not None,
                'response_handler': self.response_handler is not None,
                'error_handler': self.error_handler is not None,
                'retry_handler': self.retry_handler is not None,
                'data_handler': self.data_handler is not None
            }
            
            # Check dependencies
            health_status['dependencies'] = {
                'redis_connected': self._redis_client is not None and not self._redis_client.closed,
                'event_workers_running': (
                    self.event_dispatcher is not None and 
                    self.event_dispatcher.is_running
                ) if self.event_dispatcher else False
            }
            
            # Check if any component is unhealthy
            all_handlers_ready = all(health_status['handlers'].values())
            all_deps_ready = all(health_status['dependencies'].values())
            
            if not (all_handlers_ready and all_deps_ready):
                health_status['overall_status'] = 'unhealthy'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'timestamp': asyncio.get_event_loop().time()
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all handlers."""        try:
            stats = {
                'manager_status': {
                    'initialized': self._initialized,
                    'ready': self.is_ready()
                },
                'handlers': {}
            }
            
            # Event dispatcher stats
            if self.event_dispatcher:
                stats['handlers']['event_dispatcher'] = await self.event_dispatcher.get_system_stats()
            
            # Retry handler stats
            if self.retry_handler:
                stats['handlers']['retry_handler'] = await self.retry_handler.get_retry_statistics()
            
            # Error handler stats
            if self.error_handler:
                stats['handlers']['error_handler'] = await self.error_handler.get_error_statistics()
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics collection failed: {e}")
            return {'error': str(e)}


# Global handlers manager instance
_handlers_manager: Optional[HandlersManager] = None


async def get_handlers_manager() -> HandlersManager:
    """Get or create the global handlers manager instance."""    global _handlers_manager
    
    if _handlers_manager is None:
        _handlers_manager = HandlersManager()
        await _handlers_manager.initialize()
    
    return _handlers_manager


async def initialize_handlers(
    redis_client: Optional[aioredis.Redis] = None,
    **kwargs
) -> HandlersManager:
    """    Initialize handlers with custom configuration.
    
    Args:
        redis_client: Custom Redis client
        **kwargs: Additional initialization parameters
        
    Returns:
        Initialized HandlersManager
    """    manager = HandlersManager()
    await manager.initialize(redis_client=redis_client, **kwargs)
    return manager


async def shutdown_handlers():
    """Shutdown the global handlers manager."""    global _handlers_manager
    
    if _handlers_manager:
        await _handlers_manager.shutdown()
        _handlers_manager = None


# Convenience functions for direct handler access
async def get_content_handler() -> ContentHandler:
    """Get the content handler instance."""    manager = await get_handlers_manager()
    return manager.content_handler


async def get_event_dispatcher() -> EventDispatcher:
    """Get the event dispatcher instance."""    manager = await get_handlers_manager()
    return manager.event_dispatcher


async def get_response_handler() -> ResponseHandler:
    """Get the response handler instance."""    manager = await get_handlers_manager()
    return manager.response_handler


async def get_error_handler() -> ErrorHandler:
    """Get the error handler instance."""    manager = await get_handlers_manager()
    return manager.error_handler


async def get_retry_handler() -> RetryHandler:
    """Get the retry handler instance."""    manager = await get_handlers_manager()
    return manager.retry_handler


async def get_data_handler() -> DataHandler:
    """Get the data handler instance."""    manager = await get_handlers_manager()
    return manager.data_handler


# Export public interface
__all__ = [
    'HandlersManager',
    'get_handlers_manager',
    'initialize_handlers',
    'shutdown_handlers',
    'get_content_handler',
    'get_event_dispatcher',
    'get_response_handler',
    'get_error_handler',
    'get_retry_handler',
    'get_data_handler'
]
