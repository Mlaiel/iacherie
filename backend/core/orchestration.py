"""
Platform Orchestration Module for Ainflue
Advanced orchestration system for coordinating all platform components

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Import the existing orchestrator
from .core_orchestrator import PlatformWideOrchestrationEngine as CoreOrchestrator


class OrchestrationStatus(Enum):
    """Status enumeration for orchestration operations"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class OrchestrationMetrics:
    """Metrics for orchestration performance"""
    active_services: int = 0
    processed_requests: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    uptime_seconds: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class PlatformOrchestrator:
    """
    Main platform orchestrator for Ainflue
    Coordinates all services, AI agents, and business logic
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize platform orchestrator"""
        self.config = config or {}
        self.status = OrchestrationStatus.INITIALIZING
        self.metrics = OrchestrationMetrics()
        self.logger = logging.getLogger(__name__)
        self.core_orchestrator = CoreOrchestrator()
        self.services: Dict[str, Any] = {}
        self.start_time = datetime.utcnow()
        
    async def initialize(self) -> bool:
        """Initialize the platform orchestrator"""
        try:
            self.logger.info("Initializing Platform Orchestrator...")
            
            # Initialize core orchestrator
            await self.core_orchestrator.initialize()
            
            # Initialize services registry
            self._initialize_services_registry()
            
            # Set status to running
            self.status = OrchestrationStatus.RUNNING
            
            self.logger.info("Platform Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            self.status = OrchestrationStatus.ERROR
            return False
    
    def _initialize_services_registry(self):
        """Initialize the services registry"""
        self.services = {
            'ai_engine': None,
            'protection_engine': None,
            'content_processor': None,
            'monetization_engine': None,
            'analytics_engine': None,
            'notification_engine': None,
            'security_engine': None,
            'seo_engine': None,
            'collaboration_engine': None,
            'gamification_engine': None
        }
    
    async def start_service(self, service_name: str, service_instance: Any) -> bool:
        """Start a platform service"""
        try:
            if service_name in self.services:
                self.services[service_name] = service_instance
                if hasattr(service_instance, 'start'):
                    await service_instance.start()
                self.metrics.active_services += 1
                self.logger.info(f"Service {service_name} started successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to start service {service_name}: {e}")
            return False
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a platform service"""
        try:
            if service_name in self.services and self.services[service_name]:
                service = self.services[service_name]
                if hasattr(service, 'stop'):
                    await service.stop()
                self.services[service_name] = None
                self.metrics.active_services -= 1
                self.logger.info(f"Service {service_name} stopped successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop service {service_name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_status = {
            'status': self.status.value,
            'uptime': (datetime.utcnow() - self.start_time).total_seconds(),
            'services': {},
            'metrics': self._get_current_metrics()
        }
        
        for service_name, service in self.services.items():
            if service and hasattr(service, 'health_check'):
                try:
                    service_health = await service.health_check()
                    health_status['services'][service_name] = service_health
                except Exception as e:
                    health_status['services'][service_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                health_status['services'][service_name] = {
                    'status': 'not_running'
                }
        
        return health_status
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current orchestration metrics"""
        return {
            'active_services': self.metrics.active_services,
            'processed_requests': self.metrics.processed_requests,
            'error_count': self.metrics.error_count,
            'average_response_time': self.metrics.average_response_time,
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    async def shutdown(self) -> bool:
        """Shutdown the platform orchestrator"""
        try:
            self.logger.info("Shutting down Platform Orchestrator...")
            
            # Stop all services
            for service_name in list(self.services.keys()):
                await self.stop_service(service_name)
            
            # Shutdown core orchestrator
            if hasattr(self.core_orchestrator, 'shutdown'):
                await self.core_orchestrator.shutdown()
            
            self.status = OrchestrationStatus.STOPPED
            self.logger.info("Platform Orchestrator shut down successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.status = OrchestrationStatus.ERROR
            return False


# Singleton instance for global access
_orchestrator_instance: Optional[PlatformOrchestrator] = None


def get_platform_orchestrator() -> PlatformOrchestrator:
    """Get the global platform orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PlatformOrchestrator()
    return _orchestrator_instance


async def initialize_platform() -> bool:
    """Initialize the entire platform"""
    orchestrator = get_platform_orchestrator()
    return await orchestrator.initialize()


async def shutdown_platform() -> bool:
    """Shutdown the entire platform"""
    orchestrator = get_platform_orchestrator()
    return await orchestrator.shutdown()


# Export main classes and functions
__all__ = [
    'PlatformOrchestrator',
    'OrchestrationStatus',
    'OrchestrationMetrics',
    'get_platform_orchestrator',
    'initialize_platform',
    'shutdown_platform'
]