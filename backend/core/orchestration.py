"""Platform Orchestration Engine

Central orchestration system for managing all platform services and workflows.
Author: Fahed Mlaiel <mlaiel@live.de>
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


class ServiceStatus:
    """Service status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class PlatformService(ABC):
    """Base class for platform services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.status = ServiceStatus.STOPPED
        self.logger = logging.getLogger(f"service.{service_name}")
        
    @abstractmethod
    async def start(self) -> bool:
        """Start the service"""
        pass
        
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the service"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass


class PlatformOrchestrator:
    """Central platform orchestrator managing all services"""
    
    def __init__(self):
        self.services: Dict[str, PlatformService] = {}
        self.service_dependencies: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(__name__)
        self.startup_time: Optional[datetime] = None
        
    def register_service(self, service: PlatformService, dependencies: Optional[List[str]] = None) -> None:
        """Register a service with the orchestrator"""
        self.services[service.service_name] = service
        self.service_dependencies[service.service_name] = dependencies or []
        self.logger.info(f"Registered service: {service.service_name}")
        
    async def start_all_services(self) -> Dict[str, bool]:
        """Start all services in dependency order"""
        self.logger.info("Starting platform orchestration...")
        self.startup_time = datetime.utcnow()
        
        results = {}
        started_services = set()
        
        # Topological sort for dependency resolution
        sorted_services = self._resolve_dependencies()
        
        for service_name in sorted_services:
            if service_name in self.services:
                try:
                    service = self.services[service_name]
                    service.status = ServiceStatus.STARTING
                    
                    self.logger.info(f"Starting service: {service_name}")
                    success = await service.start()
                    
                    if success:
                        service.status = ServiceStatus.RUNNING
                        started_services.add(service_name)
                        results[service_name] = True
                        self.logger.info(f"Service started successfully: {service_name}")
                    else:
                        service.status = ServiceStatus.ERROR
                        results[service_name] = False
                        self.logger.error(f"Failed to start service: {service_name}")
                        
                except Exception as e:
                    service.status = ServiceStatus.ERROR
                    results[service_name] = False
                    self.logger.error(f"Exception starting service {service_name}: {e}")
                    
        return results
        
    async def stop_all_services(self) -> Dict[str, bool]:
        """Stop all services in reverse dependency order"""
        self.logger.info("Stopping platform services...")
        
        results = {}
        sorted_services = self._resolve_dependencies()
        
        # Stop in reverse order
        for service_name in reversed(sorted_services):
            if service_name in self.services:
                try:
                    service = self.services[service_name]
                    service.status = ServiceStatus.STOPPING
                    
                    self.logger.info(f"Stopping service: {service_name}")
                    success = await service.stop()
                    
                    if success:
                        service.status = ServiceStatus.STOPPED
                        results[service_name] = True
                        self.logger.info(f"Service stopped successfully: {service_name}")
                    else:
                        service.status = ServiceStatus.ERROR
                        results[service_name] = False
                        self.logger.error(f"Failed to stop service: {service_name}")
                        
                except Exception as e:
                    service.status = ServiceStatus.ERROR
                    results[service_name] = False
                    self.logger.error(f"Exception stopping service {service_name}: {e}")
                    
        return results
        
    async def health_check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all services"""
        results = {}
        
        for service_name, service in self.services.items():
            try:
                health_data = await service.health_check()
                results[service_name] = {
                    "status": service.status,
                    "health": health_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                results[service_name] = {
                    "status": ServiceStatus.ERROR,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        return results
        
    def get_service_status(self, service_name: str) -> Optional[str]:
        """Get status of a specific service"""
        if service_name in self.services:
            return self.services[service_name].status
        return None
        
    def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status"""
        running_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.RUNNING)
        total_services = len(self.services)
        
        return {
            "platform_status": "healthy" if running_services == total_services else "degraded",
            "total_services": total_services,
            "running_services": running_services,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "services": {name: service.status for name, service in self.services.items()}
        }
        
    def _resolve_dependencies(self) -> List[str]:
        """Resolve service dependencies using topological sort"""
        # Simple dependency resolution - can be enhanced
        visited = set()
        result = []
        
        def visit(service_name: str):
            if service_name in visited:
                return
            visited.add(service_name)
            
            # Visit dependencies first
            for dep in self.service_dependencies.get(service_name, []):
                if dep in self.services:
                    visit(dep)
                    
            result.append(service_name)
            
        for service_name in self.services:
            visit(service_name)
            
        return result


class AIAgentsOrchestrator(PlatformService):
    """AI Agents orchestration service"""
    
    def __init__(self):
        super().__init__("ai_agents")
        self.agents: Dict[str, Any] = {}
        
    async def start(self) -> bool:
        """Start AI agents orchestrator"""
        try:
            self.logger.info("Starting AI Agents Orchestrator...")
            # Initialize AI agents here
            return True
        except Exception as e:
            self.logger.error(f"Failed to start AI agents: {e}")
            return False
            
    async def stop(self) -> bool:
        """Stop AI agents orchestrator"""
        try:
            self.logger.info("Stopping AI Agents Orchestrator...")
            # Cleanup AI agents here
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop AI agents: {e}")
            return False
            
    async def health_check(self) -> Dict[str, Any]:
        """Check AI agents health"""
        return {
            "agents_count": len(self.agents),
            "status": "healthy",
            "memory_usage": "normal"
        }


class DatabaseOrchestrator(PlatformService):
    """Database services orchestrator"""
    
    def __init__(self):
        super().__init__("database")
        
    async def start(self) -> bool:
        """Start database services"""
        try:
            self.logger.info("Starting Database services...")
            # Initialize database connections here
            return True
        except Exception as e:
            self.logger.error(f"Failed to start database services: {e}")
            return False
            
    async def stop(self) -> bool:
        """Stop database services"""
        try:
            self.logger.info("Stopping Database services...")
            # Close database connections here
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop database services: {e}")
            return False
            
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        return {
            "connections": "active",
            "status": "healthy",
            "response_time": "normal"
        }


class MonetizationOrchestrator(PlatformService):
    """Monetization services orchestrator"""
    
    def __init__(self):
        super().__init__("monetization")
        
    async def start(self) -> bool:
        """Start monetization services"""
        try:
            self.logger.info("Starting Monetization services...")
            # Initialize payment processors, etc.
            return True
        except Exception as e:
            self.logger.error(f"Failed to start monetization services: {e}")
            return False
            
    async def stop(self) -> bool:
        """Stop monetization services"""
        try:
            self.logger.info("Stopping Monetization services...")
            # Cleanup payment processors
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop monetization services: {e}")
            return False
            
    async def health_check(self) -> Dict[str, Any]:
        """Check monetization health"""
        return {
            "payment_gateways": "connected",
            "status": "healthy",
            "transaction_processing": "normal"
        }


# Global orchestrator instance
platform_orchestrator = PlatformOrchestrator()


async def initialize_platform():
    """Initialize the complete platform"""
    # Register core services
    ai_service = AIAgentsOrchestrator()
    db_service = DatabaseOrchestrator()
    monetization_service = MonetizationOrchestrator()
    
    # Register with dependencies
    platform_orchestrator.register_service(db_service)  # Database first
    platform_orchestrator.register_service(ai_service, dependencies=["database"])
    platform_orchestrator.register_service(monetization_service, dependencies=["database"])
    
    # Start all services
    results = await platform_orchestrator.start_all_services()
    
    return results


async def shutdown_platform():
    """Shutdown the complete platform"""
    return await platform_orchestrator.stop_all_services()


def get_platform_health():
    """Get current platform health status"""
    return platform_orchestrator.get_platform_status()