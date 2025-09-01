"""Microservices Configuration Index for IA-Influencer Agent Platform
==================================================================

Central index and orchestration module for all microservices configurations.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import all configuration modules
from . import (
    service_discovery_config,
    load_balancer_config,
    message_broker_config,
    circuit_breaker_config,
    service_mesh_config,
    api_gateway_config,
    health_check_config,
    distributed_tracing_config,
    
    # New configuration modules
    content_protection_config,
    fingerprinting_engine_config,
    web_crawler_config,
    monetization_engine_config,
    licensing_engine_config,
    platform_integration_config,
    analytics_engine_config,
    event_driven_config,
    
    # Implementation classes
    ServiceRegistry,
    LoadBalancer,
    CircuitBreakerRegistry,
    HealthChecker,
    
    # New orchestrator classes
    ContentProtectionOrchestrator,
    PlatformIntegrationOrchestrator,
    RealTimeAnalyticsOrchestrator,
    EventDrivenOrchestrator,
    
    # Pre-configured instances
    MICROSERVICE_REGISTRATIONS,
    MICROSERVICE_UPSTREAMS,
    MICROSERVICE_CIRCUIT_BREAKER_RULES,
    MICROSERVICE_HEALTH_CHECKS,
    MICROSERVICE_TRACING_CONFIGS,
    
    # New orchestrator instances
    content_protection_orchestrator,
    platform_integration_orchestrator,
    analytics_orchestrator,
    event_orchestrator
)


logger = logging.getLogger(__name__)


class InitializationStatus(str, Enum):
    """
Initialization status for microservices components."""

    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    READY = "ready"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class ComponentStatus:
    """Status information for a microservice component."""
    name: str
    status: InitializationStatus
    error_message: Optional[str] = None
    last_updated: Optional[float] = None
    health_status: Optional[str] = None
    dependencies_ready: bool = False


class MicroservicesOrchestrator:
    """
    Central orchestrator for all microservices components.
    Manages initialization, health checking, and lifecycle management.
    """
    
    def __init__(self):
        self.components: Dict[str, ComponentStatus] = {}
        self.service_registry: Optional[ServiceRegistry] = None
        self.load_balancer: Optional[LoadBalancer] = None
        self.circuit_breaker_registry: Optional[CircuitBreakerRegistry] = None
        self.health_checker: Optional[HealthChecker] = None
        self.initialized = False
        
        # Initialize component status tracking
        self._initialize_component_status()
    
    def _initialize_component_status(self):
        """
Initialize status tracking for all components."""
        components = [
            "service_discovery",
            "load_balancer",
            "message_broker",
            "circuit_breaker",
            "service_mesh",
            "api_gateway",
            "health_checker",
            "distributed_tracing"
        ]
        
        for component in components:
            self.components[component] = ComponentStatus(
                name=component,
                status=InitializationStatus.NOT_STARTED
            )
    
    async def initialize_all(self) -> bool:
        """
        Initialize all microservices components in the correct order.
        Returns True if all components initialized successfully.
        """
        logger.info("Starting microservices orchestrator initialization...")
        
        try:
            # Step 1: Initialize service discovery
            await self._initialize_service_discovery()
            
            # Step 2: Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            # Step 3: Initialize load balancer
            await self._initialize_load_balancer()
            
            # Step 4: Initialize health checker
            await self._initialize_health_checker()
            
            # Step 5: Register all microservices
            await self._register_microservices()
            
            # Step 6: Start health monitoring
            await self._start_health_monitoring()
            
            # Step 7: Initialize new specialized systems
            await self._initialize_specialized_systems()
            
            self.initialized = True
            logger.info("Microservices orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize microservices orchestrator: {e}")
            await self.shutdown_all()
            return False
    
    async def _initialize_service_discovery(self):
        """Initialize service discovery component."""
        logger.info("Initializing service discovery...")
        self.components["service_discovery"].status = InitializationStatus.INITIALIZING
        
        try:
            self.service_registry = ServiceRegistry(service_discovery_config)
            
            # Register pre-configured services
            for service_name, registration in MICROSERVICE_REGISTRATIONS.items():
                self.service_registry.register_service(registration)
                logger.debug(f"Registered service: {service_name}")
            
            self.components["service_discovery"].status = InitializationStatus.READY
            logger.info("Service discovery initialized successfully")
            
        except Exception as e:
            self.components["service_discovery"].status = InitializationStatus.FAILED
            self.components["service_discovery"].error_message = str(e)
            raise
    
    async def _initialize_circuit_breakers(self):
        """Initialize circuit breaker registry."""
        logger.info("Initializing circuit breakers...")
        self.components["circuit_breaker"].status = InitializationStatus.INITIALIZING
        
        try:
            self.circuit_breaker_registry = CircuitBreakerRegistry(circuit_breaker_config)
            
            # Create circuit breakers for all services
            for service_name, rule in MICROSERVICE_CIRCUIT_BREAKER_RULES.items():
                cb = self.circuit_breaker_registry.get_or_create(service_name, rule)
                logger.debug(f"Created circuit breaker for: {service_name}")
            
            self.components["circuit_breaker"].status = InitializationStatus.READY
            logger.info("Circuit breakers initialized successfully")
            
        except Exception as e:
            self.components["circuit_breaker"].status = InitializationStatus.FAILED
            self.components["circuit_breaker"].error_message = str(e)
            raise
    
    async def _initialize_load_balancer(self):
        """Initialize load balancer."""
        logger.info("Initializing load balancer...")
        self.components["load_balancer"].status = InitializationStatus.INITIALIZING
        
        try:
            self.load_balancer = LoadBalancer(load_balancer_config)
            
            # Add upstream configurations
            for upstream_name, upstream in MICROSERVICE_UPSTREAMS.items():
                self.load_balancer.add_upstream(upstream)
                logger.debug(f"Added upstream: {upstream_name}")
            
            self.components["load_balancer"].status = InitializationStatus.READY
            logger.info("Load balancer initialized successfully")
            
        except Exception as e:
            self.components["load_balancer"].status = InitializationStatus.FAILED
            self.components["load_balancer"].error_message = str(e)
            raise
    
    async def _initialize_health_checker(self):
        """Initialize health checker."""
        logger.info("Initializing health checker...")
        self.components["health_checker"].status = InitializationStatus.INITIALIZING
        
        try:
            self.health_checker = HealthChecker(health_check_config)
            
            # Add health check definitions
            for check_name, check_def in MICROSERVICE_HEALTH_CHECKS.items():
                self.health_checker.add_check(check_def)
                logger.debug(f"Added health check: {check_name}")
            
            self.components["health_checker"].status = InitializationStatus.READY
            logger.info("Health checker initialized successfully")
            
        except Exception as e:
            self.components["health_checker"].status = InitializationStatus.FAILED
            self.components["health_checker"].error_message = str(e)
            raise
    
    async def _register_microservices(self):
        """Register all microservices with service discovery."""
        if not self.service_registry:
            raise RuntimeError("Service registry not initialized")
        
        logger.info("Registering microservices...")
        
        # All microservices are already registered during service discovery init
        logger.info("Microservices registration completed")
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all services."""
        if not self.health_checker:
            raise RuntimeError("Health checker not initialized")
        
        logger.info("Starting health monitoring...")
        
        # Run initial health check
        results = await self.health_checker.run_all_checks()
        
        for service_name, result in results.items():
            logger.info(f"Health check result for {service_name}: {result.status}")
        
        logger.info("Health monitoring started successfully")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "orchestrator_initialized": self.initialized,
            "components": {},
            "services": {},
            "overall_health": "unknown"
        }
        
        # Component status
        for name, component in self.components.items():
            status["components"][name] = {
                "status": component.status.value,
                "error": component.error_message,
                "last_updated": component.last_updated,
                "health_status": component.health_status
            }
        
        # Service health status
        if self.health_checker:
            try:
                results = await self.health_checker.run_all_checks()
                for service_name, result in results.items():
                    status["services"][service_name] = {
                        "status": result.status.value,
                        "response_time": result.response_time,
                        "timestamp": result.timestamp.isoformat(),
                        "error": result.error
                    }
                
                # Calculate overall health
                overall_status = self.health_checker.get_overall_status()
                status["overall_health"] = overall_status.value
                
            except Exception as e:
                logger.error(f"Failed to get health status: {e}")
                status["overall_health"] = "error"
        
        return status
    
    async def shutdown_all(self):
        """Shutdown all microservices components."""
        logger.info("Shutting down microservices orchestrator...")
        
        # Update all component status to stopped
        for component in self.components.values():
            component.status = InitializationStatus.STOPPED
        
        # Cleanup resources
        self.service_registry = None
        self.load_balancer = None
        self.circuit_breaker_registry = None
        self.health_checker = None
        self.initialized = False
        
        logger.info("Microservices orchestrator shutdown completed")
    
    def is_ready(self) -> bool:
        """Check if all critical components are ready."""
        critical_components = [
            "service_discovery",
            "circuit_breaker", 
            "load_balancer",
            "health_checker"
        ]
        
        return all(
            self.components[comp].status == InitializationStatus.READY
            for comp in critical_components
        )
    
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
        """Get status of a specific component."""
        return self.components.get(component_name)
    
    async def _initialize_specialized_systems(self):
        """
Initialize specialized microservice systems"""
        logger.info("Initializing specialized microservice systems...")
        
        # Initialize content protection system
        logger.info("Initializing content protection system...")
        try:
            content_protection_success = await content_protection_orchestrator.initialize_services()
            if not all(content_protection_success.values()):
                logger.warning("Some content protection services failed to initialize")
        except Exception as e:
            logger.error(f"Content protection system initialization failed: {e}")
        
        # Initialize platform integrations
        logger.info("Initializing platform integrations...")
        try:
            platform_success = await platform_integration_orchestrator.initialize_platforms()
            if not all(platform_success.values()):
                logger.warning("Some platform integrations failed to initialize")
        except Exception as e:
            logger.error(f"Platform integration system initialization failed: {e}")
        
        # Initialize analytics system
        logger.info("Initializing real-time analytics system...")
        try:
            analytics_success = await analytics_orchestrator.initialize_analytics()
            if not analytics_success:
                logger.warning("Analytics system failed to initialize")
        except Exception as e:
            logger.error(f"Analytics system initialization failed: {e}")
        
        # Initialize event-driven system
        logger.info("Initializing event-driven architecture...")
        try:
            event_success = await event_orchestrator.initialize_event_system()
            if not event_success:
                logger.warning("Event-driven system failed to initialize")
        except Exception as e:
            logger.error(f"Event-driven system initialization failed: {e}")
        
        logger.info("Specialized systems initialization completed")


# Global orchestrator instance
orchestrator = MicroservicesOrchestrator()


# Configuration summary for debugging and monitoring
CONFIGURATION_SUMMARY = {
    # Core microservices
    "total_microservices": len(MICROSERVICE_REGISTRATIONS),
    "configured_upstreams": len(MICROSERVICE_UPSTREAMS),
    "circuit_breaker_rules": len(MICROSERVICE_CIRCUIT_BREAKER_RULES),
    "health_checks": len(MICROSERVICE_HEALTH_CHECKS),
    "tracing_configs": len(MICROSERVICE_TRACING_CONFIGS),
    "service_discovery_type": service_discovery_config.discovery_type,
    "load_balancing_strategy": load_balancer_config.default_strategy,
    "message_broker_type": message_broker_config.broker_type,
    "service_mesh_type": service_mesh_config.mesh_type,
    "tracing_backend": distributed_tracing_config.backend,
    
    # Specialized systems
    "content_protection": {
        "services": len(content_protection_orchestrator.configs),
        "protection_modes": ["passive", "active", "aggressive", "forensic"],
        "fingerprint_algorithms": 8
    },
    "platform_integration": {
        "platforms": len(platform_integration_orchestrator.config.platforms),
        "supported_types": 6,
        "features": ["upload", "analytics", "monetization", "streaming"]
    },
    "analytics": {
        "metrics": len(analytics_orchestrator.event_processor.metrics_definitions),
        "real_time": analytics_orchestrator.config.enable_real_time_streaming,
        "storage_backends": 3
    },
    "event_system": {
        "event_types": len(event_orchestrator.publisher.EVENT_SCHEMAS if hasattr(event_orchestrator, 'publisher') else {}),
        "streams": len(event_orchestrator.config.EVENT_STREAMS if hasattr(event_orchestrator, 'config') else {}),
        "broker_type": event_orchestrator.config.broker_type if hasattr(event_orchestrator, 'config') else "unknown"
    }
}


# Convenience functions for easy access
async def initialize_microservices() -> bool:
    """Initialize all microservices components."""
    return await orchestrator.initialize_all()


async def get_system_status() -> Dict[str, Any]:
    """
Get comprehensive system status."""
    return await orchestrator.get_system_status()


async def shutdown_microservices():
    """
Shutdown all microservices components."""
    await orchestrator.shutdown_all()


def is_system_ready() -> bool:
    """
Check if the microservices system is ready."""
    return orchestrator.is_ready()


def get_configuration_summary() -> Dict[str, Any]:
    """
Get configuration summary."""
    return CONFIGURATION_SUMMARY.copy()


# Export main components
__all__ = [
    'MicroservicesOrchestrator',
    'orchestrator',
    'initialize_microservices',
    'get_system_status', 
    'shutdown_microservices',
    'is_system_ready',
    'get_configuration_summary',
    'CONFIGURATION_SUMMARY'
]
