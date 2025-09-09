"""Backend Core Orchestration Module
Central orchestration for backend services and components.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceInfo:
    """Service information structure."""
    name: str
    status: ServiceStatus
    version: str = "1.0.0"
    health_check_url: Optional[str] = None
    dependencies: List[str] = None
    started_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class BackendOrchestrator:
    """Central orchestrator for backend services."""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.startup_hooks: List[Callable] = []
        self.shutdown_hooks: List[Callable] = []
        self.initialized = False
        
    async def initialize(self):
        """Initialize the orchestrator."""
        logger.info("Initializing Backend Orchestrator...")
        
        # Register core services
        await self._register_core_services()
        
        # Run startup hooks
        await self._run_startup_hooks()
        
        self.initialized = True
        logger.info("✅ Backend Orchestrator initialized successfully")
    
    async def _register_core_services(self):
        """Register core backend services."""
        core_services = [
            ServiceInfo("api_gateway", ServiceStatus.STOPPED, "2.0.0"),
            ServiceInfo("user_service", ServiceStatus.STOPPED, "2.0.0"),
            ServiceInfo("content_service", ServiceStatus.STOPPED, "2.0.0"),
            ServiceInfo("protection_service", ServiceStatus.STOPPED, "2.0.0"),
            ServiceInfo("analytics_service", ServiceStatus.STOPPED, "2.0.0"),
            ServiceInfo("notification_service", ServiceStatus.STOPPED, "2.0.0"),
        ]
        
        for service in core_services:
            self.services[service.name] = service
            
        logger.info(f"Registered {len(core_services)} core services")
    
    async def _run_startup_hooks(self):
        """Run startup hooks."""
        for hook in self.startup_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Startup hook failed: {e}")
    
    async def register_service(self, service_info: ServiceInfo):
        """Register a new service."""
        self.services[service_info.name] = service_info
        logger.info(f"Registered service: {service_info.name}")
    
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service."""
        if service_name not in self.services:
            logger.error(f"Service not found: {service_name}")
            return False
        
        service = self.services[service_name]
        
        try:
            logger.info(f"Starting service: {service_name}")
            service.status = ServiceStatus.STARTING
            
            # Check dependencies
            for dep in service.dependencies:
                if dep not in self.services or self.services[dep].status != ServiceStatus.RUNNING:
                    logger.error(f"Dependency not running: {dep}")
                    service.status = ServiceStatus.ERROR
                    return False
            
            # Mock service startup
            await asyncio.sleep(0.1)  # Simulate startup time
            
            service.status = ServiceStatus.RUNNING
            service.started_at = datetime.utcnow()
            
            logger.info(f"✅ Service started: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            return False
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific service."""
        if service_name not in self.services:
            logger.error(f"Service not found: {service_name}")
            return False
        
        service = self.services[service_name]
        
        try:
            logger.info(f"Stopping service: {service_name}")
            service.status = ServiceStatus.STOPPING
            
            # Mock service shutdown
            await asyncio.sleep(0.1)  # Simulate shutdown time
            
            service.status = ServiceStatus.STOPPED
            service.started_at = None
            
            logger.info(f"✅ Service stopped: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {service_name}: {e}")
            service.status = ServiceStatus.ERROR
            return False
    
    async def start_all_services(self) -> Dict[str, bool]:
        """Start all registered services."""
        results = {}
        
        # Sort services by dependencies (simplified)
        service_names = list(self.services.keys())
        
        for service_name in service_names:
            results[service_name] = await self.start_service(service_name)
        
        return results
    
    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all running services."""
        results = {}
        
        # Stop in reverse order
        service_names = list(reversed(list(self.services.keys())))
        
        for service_name in service_names:
            if self.services[service_name].status == ServiceStatus.RUNNING:
                results[service_name] = await self.stop_service(service_name)
        
        return results
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get status of a specific service."""
        return self.services.get(service_name)
    
    def get_all_services_status(self) -> Dict[str, ServiceInfo]:
        """Get status of all services."""
        return self.services.copy()
    
    async def health_check(self, service_name: str = None) -> Dict[str, Any]:
        """Perform health check on services."""
        if service_name:
            service = self.services.get(service_name)
            if not service:
                return {"error": f"Service not found: {service_name}"}
            
            return {
                "service": service_name,
                "status": service.status.value,
                "healthy": service.status == ServiceStatus.RUNNING,
                "started_at": service.started_at.isoformat() if service.started_at else None
            }
        
        # Health check all services
        results = {}
        for name, service in self.services.items():
            results[name] = {
                "status": service.status.value,
                "healthy": service.status == ServiceStatus.RUNNING,
                "started_at": service.started_at.isoformat() if service.started_at else None
            }
        
        return {
            "orchestrator": "healthy" if self.initialized else "initializing",
            "services": results,
            "total_services": len(self.services),
            "running_services": len([s for s in self.services.values() if s.status == ServiceStatus.RUNNING])
        }
    
    def add_startup_hook(self, hook: Callable):
        """Add a startup hook."""
        self.startup_hooks.append(hook)
    
    def add_shutdown_hook(self, hook: Callable):
        """Add a shutdown hook."""
        self.shutdown_hooks.append(hook)
    
    async def shutdown(self):
        """Shutdown the orchestrator."""
        logger.info("Shutting down Backend Orchestrator...")
        
        # Stop all services
        await self.stop_all_services()
        
        # Run shutdown hooks
        for hook in self.shutdown_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Shutdown hook failed: {e}")
        
        self.initialized = False
        logger.info("✅ Backend Orchestrator shutdown complete")


# Global orchestrator instance
_orchestrator = None


async def get_orchestrator() -> BackendOrchestrator:
    """Get global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BackendOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator


# Convenience functions
async def start_service(service_name: str) -> bool:
    """Start a service."""
    orchestrator = await get_orchestrator()
    return await orchestrator.start_service(service_name)


async def stop_service(service_name: str) -> bool:
    """Stop a service."""
    orchestrator = await get_orchestrator()
    return await orchestrator.stop_service(service_name)


async def get_service_status(service_name: str) -> Optional[ServiceInfo]:
    """Get service status."""
    orchestrator = await get_orchestrator()
    return orchestrator.get_service_status(service_name)


async def health_check(service_name: str = None) -> Dict[str, Any]:
    """Perform health check."""
    orchestrator = await get_orchestrator()
    return await orchestrator.health_check(service_name)


# Export main classes and functions
__all__ = [
    "BackendOrchestrator",
    "PlatformOrchestrator",  # Alias for BackendOrchestrator
    "ServiceStatus",
    "ServiceInfo",
    "get_orchestrator",
    "start_service",
    "stop_service",
    "get_service_status",
    "health_check"
]

# Alias for compatibility
PlatformOrchestrator = BackendOrchestrator