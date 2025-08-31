"""
Social Media Agent Module Index & Service Registry
Enterprise-Grade AI-Powered Multi-Platform Social Media Management & Content Protection System

Industrial architecture with service registry, dependency injection, and factory patterns for 
scalable social media automation, content protection, and monetization tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL NOTICE:
This code, architecture, and business concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization without 
explicit written permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries only.

Expert Development Team Specialties:
- Lead AI Developer & ML Engineer - Advanced machine learning and neural network optimization
- Backend Senior Architect - Enterprise-level scalable system design and microservices
- Database Administrator (DBA) - Data modeling, performance optimization, and management
- Security & Microservices Expert - Enterprise security and distributed systems architecture
- Audio Processing Specialist - Digital signal processing and audio content analysis
- DevOps & Infrastructure Engineer - CI/CD, containerization, and cloud deployment strategies
- AI Prompt Engineering Expert - NLP, conversational AI, and content generation systems
- Content Protection Specialist - AI fingerprinting, copyright protection, and anti-piracy
"""

from typing import Dict, Any, List, Optional, Type, Union, Callable, Tuple, Set
import asyncio
import logging
import json
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import importlib
from pathlib import Path

# Core component imports
from .social_media_agent import SocialMediaAgent, SocialMediaAgentManager
from .platform_manager import PlatformManager, PlatformCredentials, PlatformType, PlatformStatus
from .content_scheduler import ContentScheduler, ScheduleOptimizer, SchedulingStrategy
from .engagement_optimizer import EngagementOptimizer, ContentFeatureExtractor, OptimizationStrategy
from .cross_platform_sync import CrossPlatformSync, SyncOperation, ContentTransformer
from .analytics_processor import AnalyticsProcessor, TrendAnalyzer, AnalyticsReport
from .automation_workflows import AutomationWorkflows, WorkflowTrigger, WorkflowEngine
from .platform_adapters import PlatformAdapters, BasePlatformAdapter, AdapterRegistry
from .integration_config import (
    SocialMediaAgentIntegrator,
    AgentIntegrationConfig,
    IntegrationType,
    COMPLETE_INTEGRATION_CONFIG,
    PlatformConfigManager
)

# Configuration and monitoring imports
from ..base import BaseAgent, AgentStatus, AgentPriority
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import AgentError, ConfigurationError, ServiceNotAvailableError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AgentError, ConfigurationError, ServiceNotAvailableError = globals().get('AgentError, ConfigurationError, ServiceNotAvailableError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.health_checker import HealthChecker
from ...security.access_control import RoleBasedAccessControl

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    STOPPED = "stopped"

class ComponentType(Enum):
    """Component type classification"""
    CORE_AGENT = "core_agent"
    PLATFORM_MANAGER = "platform_manager"
    SCHEDULER = "scheduler"
    OPTIMIZER = "optimizer"
    SYNCHRONIZER = "synchronizer"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    ADAPTER = "adapter"
    INTEGRATION = "integration"

@dataclass
class ServiceRegistration:
    """Service registration metadata"""
    name: str
    component_type: ComponentType
    instance: Any
    dependencies: List[str] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.INITIALIZING
    health_check_url: Optional[str] = None
    metrics_enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_health_check: Optional[datetime] = None

class SocialMediaAgentRegistry:
    """
    Enterprise Service Registry and Factory for Social Media Agent Components
    
    Manages initialization, configuration, dependency injection, health monitoring,
    and lifecycle of all social media management components with enterprise-grade
    features including circuit breakers, health checks, and performance monitoring.
    """
    
    _instance: Optional['SocialMediaAgentRegistry'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'SocialMediaAgentRegistry':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the service registry"""
        if self._initialized:
            return
            
        self.services: Dict[str, ServiceRegistration] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.health_checker = HealthChecker()
        self.performance_monitor = PerformanceMonitor()
        self.access_control = RoleBasedAccessControl()
        self.config_manager = PlatformConfigManager()
        self._startup_order: List[str] = []
        
        # Initialize metrics
        self.service_requests = Counter('social_media_agent_requests_total', 'Total requests', ['service', 'method'])
        self.service_latency = Histogram('social_media_agent_latency_seconds', 'Request latency', ['service'])
        self.active_services = Gauge('social_media_agent_active_services', 'Active services count')
        
        self._initialized = True
        logger.info("Social Media Agent Registry initialized")

    def register_service(
        self, 
        name: str, 
        component_type: ComponentType,
        instance: Any,
        dependencies: Optional[List[str]] = None,
        health_check_url: Optional[str] = None
    ) -> bool:
        """Register a service component with the registry"""



        try:
            if name in self.services:
                logger.warning(f"Service {name} already registered, updating...")
            
            registration = ServiceRegistration(
                name=name,
                component_type=component_type,
                instance=instance,
                dependencies=dependencies or [],
                health_check_url=health_check_url,
                status=ServiceStatus.INITIALIZING
            )
            
            self.services[name] = registration
            self.dependency_graph[name] = set(dependencies or [])
            
            logger.info(f"Registered service: {name} ({component_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {name}: {e}")
            return False

    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance by name"""
        registration = self.services.get(name)
        if registration and registration.status == ServiceStatus.READY:
            return registration.instance
        return None

    def unregister_service(self, name: str) -> bool:
        """Unregister a service from the registry"""



        try:
            if name not in self.services:
                logger.warning(f"Service {name} not found for unregistration")
                return False
                
            # Check for dependent services
            dependents = [
                svc_name for svc_name, deps in self.dependency_graph.items() 
                if name in deps
            ]
            
            if dependents:
                logger.error(f"Cannot unregister {name}: services {dependents} depend on it")
                return False
            
            del self.services[name]
            del self.dependency_graph[name]
            
            logger.info(f"Unregistered service: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {name}: {e}")
            return False

    async def initialize_all_services(self) -> Dict[str, bool]:
        """Initialize all registered services in dependency order"""
        initialization_results = {}
        
        try:
            # Calculate startup order based on dependencies
            startup_order = self._calculate_startup_order()
            self._startup_order = startup_order
            
            for service_name in startup_order:
                registration = self.services.get(service_name)
                if not registration:
                    continue
                
                logger.info(f"Initializing service: {service_name}")
                registration.status = ServiceStatus.INITIALIZING
                
                try:
                    # Initialize the service
                    if hasattr(registration.instance, 'initialize'):
                        success = await registration.instance.initialize()
                    else:
                        success = True
                    
                    if success:
                        registration.status = ServiceStatus.READY
                        registration.last_health_check = datetime.now(timezone.utc)
                        initialization_results[service_name] = True
                        logger.info(f"Successfully initialized: {service_name}")
                    else:
                        registration.status = ServiceStatus.FAILED
                        initialization_results[service_name] = False
                        logger.error(f"Failed to initialize: {service_name}")
                        
                except Exception as e:
                    registration.status = ServiceStatus.FAILED
                    initialization_results[service_name] = False
                    logger.error(f"Error initializing {service_name}: {e}")
            
            # Update metrics
            active_count = sum(1 for reg in self.services.values() if reg.status == ServiceStatus.READY)
            self.active_services.set(active_count)
            
            return initialization_results
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return {name: False for name in self.services.keys()}

    def _calculate_startup_order(self) -> List[str]:
        """Calculate service startup order based on dependencies using topological sort"""
        in_degree = {name: 0 for name in self.services.keys()}
        
        # Calculate in-degrees
        for name, deps in self.dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[name] += 1
        
        # Topological sort
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees of dependent services
            for name, deps in self.dependency_graph.items():
                if current in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)
        
        return result

    async def health_check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all services"""
        results = {}
        
        for name, registration in self.services.items():
            try:
                if hasattr(registration.instance, 'health_check'):
                    health_status = await registration.instance.health_check()
                else:
                    health_status = {"status": "healthy", "message": "No health check implemented"}
                
                results[name] = {
                    "service_status": registration.status.value,
                    "health_check": health_status,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
                
                registration.last_health_check = datetime.now(timezone.utc)
                
            except Exception as e:
                results[name] = {
                    "service_status": registration.status.value,
                    "health_check": {"status": "unhealthy", "error": str(e)},
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
                logger.error(f"Health check failed for {name}: {e}")
        
        return results

    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive status of all services"""
        status = {}
        
        for name, registration in self.services.items():
            status[name] = {
                "component_type": registration.component_type.value,
                "status": registration.status.value,
                "dependencies": list(registration.dependencies),
                "created_at": registration.created_at.isoformat(),
                "last_health_check": registration.last_health_check.isoformat() if registration.last_health_check else None,
                "metrics_enabled": registration.metrics_enabled
            }
        
        return status

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the service dependency graph"""



        return {name: list(deps) for name, deps in self.dependency_graph.items()}

    async def shutdown_all_services(self) -> Dict[str, bool]:
        """Shutdown all services in reverse dependency order"""
        shutdown_results = {}
        
        # Reverse the startup order for shutdown
        shutdown_order = list(reversed(self._startup_order))
        
        for service_name in shutdown_order:
            registration = self.services.get(service_name)
            if not registration:
                continue
                
            logger.info(f"Shutting down service: {service_name}")
            
            try:
                if hasattr(registration.instance, 'shutdown'):
                    success = await registration.instance.shutdown()
                else:
                    success = True
                
                if success:
                    registration.status = ServiceStatus.STOPPED
                    shutdown_results[service_name] = True
                    logger.info(f"Successfully shut down: {service_name}")
                else:
                    shutdown_results[service_name] = False
                    logger.error(f"Failed to shut down: {service_name}")
                    
            except Exception as e:
                shutdown_results[service_name] = False
                logger.error(f"Error shutting down {service_name}: {e}")
        
        return shutdown_results

    @asynccontextmanager
    async def service_context(self, service_name: str):
        """Context manager for safe service operations"""
        service = self.get_service(service_name)
        if not service:
            raise ServiceNotAvailableError(f"Service {service_name} not available")
        
        start_time = time.time()
        
        try:
            yield service
        finally:
            # Record metrics
            duration = time.time() - start_time
            self.service_latency.labels(service=service_name).observe(duration)

# Factory functions for creating pre-configured registries
def create_social_media_registry(auto_initialize: bool = True) -> SocialMediaAgentRegistry:
    """Create and configure Social Media Agent Registry with default components"""
    registry = SocialMediaAgentRegistry()
    
    # Register core components
    try:
        # Core agent
        registry.register_service(
            "social_media_agent",
            ComponentType.CORE_AGENT,
            SocialMediaAgent(),
            dependencies=["platform_manager", "content_scheduler"]
        )
        
        # Platform manager
        registry.register_service(
            "platform_manager", 
            ComponentType.PLATFORM_MANAGER,
            PlatformManager(),
            dependencies=[]
        )
        
        # Content scheduler
        registry.register_service(
            "content_scheduler",
            ComponentType.SCHEDULER, 
            ContentScheduler(),
            dependencies=["platform_manager"]
        )
        
        # Engagement optimizer
        registry.register_service(
            "engagement_optimizer",
            ComponentType.OPTIMIZER,
            EngagementOptimizer(),
            dependencies=["analytics_processor"]
        )
        
        # Analytics processor
        registry.register_service(
            "analytics_processor",
            ComponentType.ANALYTICS,
            AnalyticsProcessor(),
            dependencies=[]
        )
        
        # Cross-platform sync
        registry.register_service(
            "cross_platform_sync",
            ComponentType.SYNCHRONIZER,
            CrossPlatformSync(),
            dependencies=["platform_manager"]
        )
        
        # Automation workflows
        registry.register_service(
            "automation_workflows",
            ComponentType.AUTOMATION,
            AutomationWorkflows(),
            dependencies=["social_media_agent"]
        )
        
        logger.info("Social Media Agent Registry created with default components")
        
        if auto_initialize:
            asyncio.create_task(registry.initialize_all_services())
        
    except Exception as e:
        logger.error(f"Failed to create social media registry: {e}")
        raise
    
    return registry

def create_minimal_registry() -> SocialMediaAgentRegistry:
    """Create minimal registry with only core components"""
    registry = SocialMediaAgentRegistry()
    
    # Register only essential components
    registry.register_service(
        "social_media_agent",
        ComponentType.CORE_AGENT,
        SocialMediaAgent()
    )
    
    return registry

# Global registry instance
_global_registry: Optional[SocialMediaAgentRegistry] = None

def get_global_registry() -> SocialMediaAgentRegistry:
    """Get the global registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = create_social_media_registry()
    return _global_registry

def set_global_registry(registry: SocialMediaAgentRegistry) -> None:
    """Set the global registry instance"""
    global _global_registry
    _global_registry = registry
    def __init__(self):
        self.components: Dict[str, Any] = {}
        self.initialized: bool = False
        self.created_at = datetime.utcnow()
        self.version = "1.0.0"
        
    def register_component(self, name: str, component_class: Type, config: Optional[Dict] = None):
        """Register a component class with configuration"""



        try:
            if config is None:
                config = {}
                
            instance = component_class(**config)
            self.components[name] = {
                'instance': instance,
                'class': component_class,
                'config': config,
                'registered_at': datetime.utcnow()
            }
            logger.info(f"Registered component: {name}")
            return instance
        except Exception as e:
            logger.error(f"Failed to register component {name}: {str(e)}")
            raise
    
    def get_component(self, name: str) -> Any:
        """Get a registered component instance"""
        if name not in self.components:
            raise ValueError(f"Component '{name}' not found in registry")
        return self.components[name]['instance']
    
    def initialize_all(self, global_config: Optional[Dict] = None):
        """Initialize all core social media components"""



        try:
            if global_config is None:
                global_config = {}
            
            # Initialize core components
            self.register_component('agent', SocialMediaAgent, global_config.get('agent', {}))
            self.register_component('platform_manager', PlatformManager, global_config.get('platforms', {}))
            self.register_component('scheduler', ContentScheduler, global_config.get('scheduler', {}))
            self.register_component('optimizer', EngagementOptimizer, global_config.get('optimizer', {}))
            self.register_component('sync', CrossPlatformSync, global_config.get('sync', {}))
            self.register_component('analytics', AnalyticsProcessor, global_config.get('analytics', {}))
            self.register_component('automation', AutomationWorkflows, global_config.get('automation', {}))
            self.register_component('adapters', PlatformAdapters, global_config.get('adapters', {}))
            self.register_component('integrator', SocialMediaAgentIntegrator, global_config.get('integrator', {}))
            
            self.initialized = True
            logger.info("Social Media Agent Registry initialized with full integrations")
            
        except Exception as e:
            logger.error(f"Failed to initialize Social Media Agent Registry: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get registry status and component health"""



        return {
            'initialized': self.initialized,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'components_count': len(self.components),
            'components': {
                name: {
                    'class_name': comp['class'].__name__,
                    'registered_at': comp['registered_at'].isoformat()
                }
                for name, comp in self.components.items()
            }
        }

# Global registry instance
registry = SocialMediaAgentRegistry()

# Convenience functions for quick access
def get_social_media_agent(config: Optional[Dict] = None) -> SocialMediaAgent:
    """Get or create the main social media agent"""
    if not registry.initialized:
        registry.initialize_all({'agent': config or {}})
    return registry.get_component('agent')

def get_platform_manager(config: Optional[Dict] = None) -> PlatformManager:
    """Get or create the platform manager"""
    if not registry.initialized:
        registry.initialize_all({'platforms': config or {}})
    return registry.get_component('platform_manager')

def get_content_scheduler(config: Optional[Dict] = None) -> ContentScheduler:
    """Get or create the content scheduler"""
    if not registry.initialized:
        registry.initialize_all({'scheduler': config or {}})
    return registry.get_component('scheduler')

def get_engagement_optimizer(config: Optional[Dict] = None) -> EngagementOptimizer:
    """Get or create the engagement optimizer"""
    if not registry.initialized:
        registry.initialize_all({'optimizer': config or {}})
    return registry.get_component('optimizer')

# Module metadata
__all__ = [
    'SocialMediaAgent',
    'PlatformManager', 
    'ContentScheduler',
    'EngagementOptimizer',
    'CrossPlatformSync',
    'AnalyticsProcessor',
    'AutomationWorkflows',
    'PlatformAdapters',
    'SocialMediaAgentRegistry',
    'registry',
    'get_social_media_agent',
    'get_platform_manager',
    'get_content_scheduler',
    'get_engagement_optimizer'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright 2025, Fahed Mlaiel. All rights reserved."
