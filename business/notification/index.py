"""
Notification Module Index - Central Entry Point for Business Notifications

Main entry point for the IA Influencer Agent business notification system.
Provides centralized access to all notification components, services, and utilities
with enterprise-grade initialization, configuration management, and monitoring.

Key Features:
- Centralized service initialization and dependency injection
- Configuration management with environment-specific settings
- Health monitoring and system diagnostics
- Service discovery and component registration
- Graceful shutdown and cleanup procedures
- Performance monitoring and metrics collection

Architecture Components:
- NotificationManager: Central orchestration and management
- ServiceRegistry: Component discovery and lifecycle management
- ConfigurationManager: Environment and runtime configuration
- HealthMonitor: System health and performance monitoring
- MetricsCollector: Performance analytics and reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission from the author is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing and usage rights.
"""

from typing import Dict, List, Optional, Any, Union, Type
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import os
import json
from contextlib import asynccontextmanager

# Core notification components
from .notification_service import NotificationService
from .notification_engine import NotificationEngine
from .channel_manager import ChannelManager
from .template_processor import TemplateProcessor
from .priority_classifier import PriorityClassifier
from .personalization_engine import PersonalizationEngine
from .workflow_orchestrator import WorkflowOrchestrator
from .manager import NotificationManager
from .config import NotificationConfig
from .constants import *

# Models and utilities
from .notification_models import *
from .processors import *

logger = logging.getLogger(__name__)


class NotificationModuleError(Exception):
    """Exception for notification module errors."""
    pass


class ServiceRegistry:
    """Service registry for component discovery and lifecycle management."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_configs: Dict[str, Dict[str, Any]] = {}
        self._service_health: Dict[str, Dict[str, Any]] = {}
        self._initialized_services: List[str] = []
    
    def register_service(self, name: str, service: Any, config: Optional[Dict[str, Any]] = None):
        """Register a service component."""
        self._services[name] = service
        self._service_configs[name] = config or {}
        self._service_health[name] = {
            "status": "registered",
            "registered_at": datetime.now(timezone.utc),
            "last_health_check": None,
            "error_count": 0
        }
        logger.info(f"Registered service: {name}")
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service."""
        return self._services.get(name)
    
    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self._services.keys())
    
    def get_service_health(self, name: str) -> Optional[Dict[str, Any]]:
        """Get service health information."""
        return self._service_health.get(name)
    
    def update_service_health(self, name: str, status: str, error: Optional[str] = None):
        """Update service health status."""
        if name in self._service_health:
            self._service_health[name].update({
                "status": status,
                "last_health_check": datetime.now(timezone.utc),
                "error_count": self._service_health[name]["error_count"] + (1 if error else 0),
                "last_error": error
            })


class ConfigurationManager:
    """Configuration management for notification module."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "config"
        self._config_cache: Dict[str, Any] = {}
        self._environment = os.getenv("ENVIRONMENT", "development")
        self._load_configurations()
    
    def _load_configurations(self):
        """Load configuration files."""
        try:
            # Load base configuration
            base_config_file = self.config_path / "base.json"
            if base_config_file.exists():
                with open(base_config_file, 'r') as f:
                    self._config_cache["base"] = json.load(f)
            
            # Load environment-specific configuration
            env_config_file = self.config_path / f"{self._environment}.json"
            if env_config_file.exists():
                with open(env_config_file, 'r') as f:
                    self._config_cache["environment"] = json.load(f)
            
            # Load notification-specific configuration
            notification_config_file = self.config_path / "notification.json"
            if notification_config_file.exists():
                with open(notification_config_file, 'r') as f:
                    self._config_cache["notification"] = json.load(f)
                    
            logger.info(f"Loaded configurations for environment: {self._environment}")
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback hierarchy."""
        # Check environment config first
        if "environment" in self._config_cache:
            env_value = self._config_cache["environment"].get(key)
            if env_value is not None:
                return env_value
        
        # Check notification config
        if "notification" in self._config_cache:
            notification_value = self._config_cache["notification"].get(key)
            if notification_value is not None:
                return notification_value
        
        # Check base config
        if "base" in self._config_cache:
            base_value = self._config_cache["base"].get(key)
            if base_value is not None:
                return base_value
        
        # Check environment variables
        env_key = key.upper().replace(".", "_")
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        return default
    
    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration object."""
        try:
            config_data = {
                "redis_url": self.get_config("redis.url", "redis://localhost:6379/0"),
                "database_url": self.get_config("database.url", "postgresql://localhost/notification"),
                "smtp_host": self.get_config("smtp.host", "localhost"),
                "smtp_port": self.get_config("smtp.port", 587),
                "smtp_username": self.get_config("smtp.username", ""),
                "smtp_password": self.get_config("smtp.password", ""),
                "sms_provider": self.get_config("sms.provider", "twilio"),
                "sms_api_key": self.get_config("sms.api_key", ""),
                "push_service_key": self.get_config("push.service_key", ""),
                "webhook_secret": self.get_config("webhook.secret", ""),
                "default_sender": self.get_config("notification.default_sender", "noreply@iainfluencer.com"),
                "max_retry_attempts": self.get_config("notification.max_retry_attempts", 3),
                "retry_delay": self.get_config("notification.retry_delay", 60),
                "template_cache_ttl": self.get_config("notification.template_cache_ttl", 3600),
                "priority_model_path": self.get_config("ai.priority_model_path"),
                "personalization_enabled": self.get_config("notification.personalization_enabled", True),
                "analytics_enabled": self.get_config("notification.analytics_enabled", True)
            }
            
            return NotificationConfig(**config_data)
            
        except Exception as e:
            logger.error(f"Failed to create notification config: {e}")
            return NotificationConfig()  # Return default config


class HealthMonitor:
    """Health monitoring for notification system."""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self._health_checks: Dict[str, callable] = {}
        self._monitoring_active = False
        self._health_check_interval = 60  # seconds
        self._background_task: Optional[asyncio.Task] = None
    
    def register_health_check(self, service_name: str, health_check_func: callable):
        """Register health check function for a service."""
        self._health_checks[service_name] = health_check_func
        logger.info(f"Registered health check for service: {service_name}")
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service."""
        try:
            if service_name not in self._health_checks:
                return {
                    "service": service_name,
                    "status": "unknown",
                    "error": "No health check registered"
                }
            
            health_check = self._health_checks[service_name]
            health_result = await health_check() if asyncio.iscoroutinefunction(health_check) else health_check()
            
            # Update service registry
            status = "healthy" if health_result.get("healthy", False) else "unhealthy"
            error = health_result.get("error") if not health_result.get("healthy", False) else None
            self.service_registry.update_service_health(service_name, status, error)
            
            return {
                "service": service_name,
                "status": status,
                "details": health_result,
                "checked_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.service_registry.update_service_health(service_name, "error", str(e))
            
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "checked_at": datetime.now(timezone.utc)
            }
    
    async def check_all_services_health(self) -> Dict[str, Any]:
        """Check health of all registered services."""
        try:
            health_results = {}
            
            for service_name in self.service_registry.list_services():
                health_results[service_name] = await self.check_service_health(service_name)
            
            # Calculate overall system health
            healthy_services = sum(1 for result in health_results.values() if result["status"] == "healthy")
            total_services = len(health_results)
            overall_health = "healthy" if healthy_services == total_services else "degraded" if healthy_services > 0 else "unhealthy"
            
            return {
                "overall_status": overall_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": health_results,
                "checked_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "checked_at": datetime.now(timezone.utc)
            }
    
    async def start_monitoring(self):
        """Start background health monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._background_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started health monitoring")
    
    async def stop_monitoring(self):
        """Stop background health monitoring."""
        self._monitoring_active = False
        
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                health_status = await self.check_all_services_health()
                
                # Log unhealthy services
                for service_name, status in health_status["services"].items():
                    if status["status"] != "healthy":
                        logger.warning(f"Service {service_name} is {status['status']}: {status.get('error', 'Unknown issue')}")
                
                await asyncio.sleep(self._health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(self._health_check_interval)


class MetricsCollector:
    """Performance metrics collection and reporting."""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = self._create_metric_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        key = self._create_metric_key(name, labels)
        self._gauges[key] = value
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value."""
        key = self._create_metric_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
    
    def _create_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create metric key with labels."""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "histograms": {
                key: {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
                for key, values in self._histograms.items()
            },
            "collected_at": datetime.now(timezone.utc)
        }
    
    def reset_metrics(self):
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


class NotificationModule:
    """
    Main notification module class providing centralized access and management.
    
    Handles initialization, configuration, service discovery, health monitoring,
    and graceful shutdown of all notification system components.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize notification module."""
        self.config_path = config_path
        self._initialized = False
        self._shutdown = False
        
        # Core components
        self.service_registry = ServiceRegistry()
        self.config_manager = ConfigurationManager(config_path)
        self.health_monitor = HealthMonitor(self.service_registry)
        self.metrics_collector = MetricsCollector()
        
        # Notification services
        self.notification_manager: Optional[NotificationManager] = None
        self.notification_service: Optional[NotificationService] = None
        self.notification_engine: Optional[NotificationEngine] = None
        
        logger.info("Notification module created")
    
    async def initialize(self) -> bool:
        """Initialize the notification module and all components."""
        if self._initialized:
            return True
        
        try:
            logger.info("Initializing notification module...")
            
            # Load configuration
            config = self.config_manager.get_notification_config()
            
            # Initialize core services
            await self._initialize_core_services(config)
            
            # Initialize business processors
            await self._initialize_processors(config)
            
            # Initialize advanced features
            await self._initialize_advanced_features(config)
            
            # Register health checks
            await self._register_health_checks()
            
            # Start health monitoring
            await self.health_monitor.start_monitoring()
            
            # Initialize metrics
            self._initialize_metrics()
            
            self._initialized = True
            
            logger.info("Notification module initialized successfully")
            self.metrics_collector.increment_counter("module.initialization.success")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize notification module: {e}")
            self.metrics_collector.increment_counter("module.initialization.failure")
            return False
    
    async def _initialize_core_services(self, config: NotificationConfig):
        """Initialize core notification services."""
        try:
            # Initialize channel manager
            channel_manager = ChannelManager(config)
            await channel_manager.initialize()
            self.service_registry.register_service("channel_manager", channel_manager)
            
            # Initialize template processor
            template_processor = TemplateProcessor(config)
            await template_processor.initialize()
            self.service_registry.register_service("template_processor", template_processor)
            
            # Initialize priority classifier
            priority_classifier = PriorityClassifier(config)
            self.service_registry.register_service("priority_classifier", priority_classifier)
            
            # Initialize personalization engine
            personalization_engine = PersonalizationEngine(config)
            self.service_registry.register_service("personalization_engine", personalization_engine)
            
            # Initialize notification engine
            self.notification_engine = NotificationEngine(
                channel_manager=channel_manager,
                template_processor=template_processor,
                priority_classifier=priority_classifier,
                personalization_engine=personalization_engine,
                config=config
            )
            await self.notification_engine.initialize()
            self.service_registry.register_service("notification_engine", self.notification_engine)
            
            logger.info("Core notification services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize core services: {e}")
            raise
    
    async def _initialize_processors(self, config: NotificationConfig):
        """Initialize business notification processors."""
        try:
            # Import and initialize processors
            from .processors import (
                ContentProtectionProcessor,
                CollaborationProcessor,
                MonetizationProcessor,
                SEOProcessor,
                DistributionProcessor
            )
            
            processors = {
                "content_protection": ContentProtectionProcessor(config),
                "collaboration": CollaborationProcessor(config),
                "monetization": MonetizationProcessor(config),
                "seo": SEOProcessor(config),
                "distribution": DistributionProcessor(config)
            }
            
            # Register processors
            for name, processor in processors.items():
                self.service_registry.register_service(f"processor_{name}", processor)
            
            logger.info("Business notification processors initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize processors: {e}")
            raise
    
    async def _initialize_advanced_features(self, config: NotificationConfig):
        """Initialize advanced notification features."""
        try:
            # Initialize notification service
            processors = {
                name.replace("processor_", ""): service 
                for name, service in self.service_registry._services.items() 
                if name.startswith("processor_")
            }
            
            self.notification_service = NotificationService(
                engine=self.notification_engine,
                processors=processors,
                config=config
            )
            await self.notification_service.initialize()
            self.service_registry.register_service("notification_service", self.notification_service)
            
            # Initialize workflow orchestrator
            workflow_orchestrator = WorkflowOrchestrator(
                notification_service=self.notification_service,
                config=config
            )
            self.service_registry.register_service("workflow_orchestrator", workflow_orchestrator)
            
            # Initialize notification manager
            self.notification_manager = NotificationManager(
                notification_service=self.notification_service,
                workflow_orchestrator=workflow_orchestrator,
                config=config
            )
            await self.notification_manager.initialize()
            self.service_registry.register_service("notification_manager", self.notification_manager)
            
            logger.info("Advanced notification features initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize advanced features: {e}")
            raise
    
    async def _register_health_checks(self):
        """Register health checks for all services."""
        try:
            # Register health checks for each service
            for service_name in self.service_registry.list_services():
                service = self.service_registry.get_service(service_name)
                
                # Check if service has health check method
                if hasattr(service, 'health_check'):
                    self.health_monitor.register_health_check(service_name, service.health_check)
                else:
                    # Create basic health check
                    self.health_monitor.register_health_check(
                        service_name,
                        lambda s=service: {"healthy": s is not None, "service_type": type(s).__name__}
                    )
            
            logger.info("Health checks registered for all services")
            
        except Exception as e:
            logger.error(f"Failed to register health checks: {e}")
    
    def _initialize_metrics(self):
        """Initialize metrics collection."""
        try:
            # Set initial metrics
            self.metrics_collector.set_gauge("module.services.total", len(self.service_registry.list_services()))
            self.metrics_collector.set_gauge("module.initialized", 1.0)
            self.metrics_collector.increment_counter("module.start")
            
            logger.info("Metrics collection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize metrics: {e}")
    
    # Public API methods
    
    def get_notification_manager(self) -> Optional[NotificationManager]:
        """Get the notification manager instance."""
        if not self._initialized:
            raise NotificationModuleError("Module not initialized. Call initialize() first.")
        return self.notification_manager
    
    def get_notification_service(self) -> Optional[NotificationService]:
        """Get the notification service instance."""
        if not self._initialized:
            raise NotificationModuleError("Module not initialized. Call initialize() first.")
        return self.notification_service
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a specific service by name."""
        if not self._initialized:
            raise NotificationModuleError("Module not initialized. Call initialize() first.")
        return self.service_registry.get_service(service_name)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        if not self._initialized:
            return {
                "overall_status": "not_initialized",
                "error": "Module not initialized"
            }
        
        return await self.health_monitor.check_all_services_health()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics_collector.get_metrics()
    
    def is_initialized(self) -> bool:
        """Check if module is initialized."""
        return self._initialized
    
    def is_healthy(self) -> bool:
        """Check if module is healthy."""
        if not self._initialized:
            return False
        
        # Basic health check - could be enhanced
        return len(self.service_registry.list_services()) > 0
    
    async def shutdown(self):
        """Gracefully shutdown the notification module."""
        if self._shutdown:
            return
        
        try:
            logger.info("Shutting down notification module...")
            
            # Stop health monitoring
            await self.health_monitor.stop_monitoring()
            
            # Shutdown services in reverse order
            services_to_shutdown = [
                "notification_manager",
                "workflow_orchestrator",
                "notification_service",
                "notification_engine",
                "personalization_engine",
                "priority_classifier",
                "template_processor",
                "channel_manager"
            ]
            
            for service_name in services_to_shutdown:
                service = self.service_registry.get_service(service_name)
                if service and hasattr(service, 'shutdown'):
                    try:
                        if asyncio.iscoroutinefunction(service.shutdown):
                            await service.shutdown()
                        else:
                            service.shutdown()
                        logger.info(f"Shut down service: {service_name}")
                    except Exception as e:
                        logger.error(f"Error shutting down {service_name}: {e}")
            
            # Final metrics update
            self.metrics_collector.set_gauge("module.initialized", 0.0)
            self.metrics_collector.increment_counter("module.shutdown")
            
            self._shutdown = True
            self._initialized = False
            
            logger.info("Notification module shut down successfully")
            
        except Exception as e:
            logger.error(f"Error during notification module shutdown: {e}")


# Global notification module instance
_notification_module: Optional[NotificationModule] = None


# Module-level convenience functions
async def initialize_notification_module(config_path: Optional[Path] = None) -> NotificationModule:
    """Initialize global notification module instance."""
    global _notification_module
    
    if _notification_module is None:
        _notification_module = NotificationModule(config_path)
    
    if not _notification_module.is_initialized():
        success = await _notification_module.initialize()
        if not success:
            raise NotificationModuleError("Failed to initialize notification module")
    
    return _notification_module


def get_notification_module() -> Optional[NotificationModule]:
    """Get global notification module instance."""
    return _notification_module


async def get_notification_manager() -> Optional[NotificationManager]:
    """Get notification manager from global module."""
    if _notification_module and _notification_module.is_initialized():
        return _notification_module.get_notification_manager()
    return None


async def get_notification_service() -> Optional[NotificationService]:
    """Get notification service from global module."""
    if _notification_module and _notification_module.is_initialized():
        return _notification_module.get_notification_service()
    return None


async def shutdown_notification_module():
    """Shutdown global notification module."""
    global _notification_module
    
    if _notification_module:
        await _notification_module.shutdown()
        _notification_module = None


# Context manager for notification module lifecycle
@asynccontextmanager
async def notification_module_context(config_path: Optional[Path] = None):
    """Context manager for notification module lifecycle."""
    module = None
    try:
        module = await initialize_notification_module(config_path)
        yield module
    finally:
        if module:
            await module.shutdown()


# Module exports for convenient access
__all__ = [
    # Main module classes
    "NotificationModule",
    "ServiceRegistry", 
    "ConfigurationManager",
    "HealthMonitor",
    "MetricsCollector",
    
    # Module functions
    "initialize_notification_module",
    "get_notification_module",
    "get_notification_manager", 
    "get_notification_service",
    "shutdown_notification_module",
    "notification_module_context",
    
    # Core services
    "NotificationManager",
    "NotificationService",
    "NotificationEngine",
    "ChannelManager",
    "TemplateProcessor",
    "PriorityClassifier",
    "PersonalizationEngine",
    "WorkflowOrchestrator",
    
    # Models and processors
    "NotificationRequest",
    "NotificationResponse",
    "NotificationContent",
    "NotificationTemplate",
    "NotificationMetrics",
    "ContentProtectionProcessor",
    "CollaborationProcessor", 
    "MonetizationProcessor",
    "SEOProcessor",
    "DistributionProcessor",
    
    # Configuration and constants
    "NotificationConfig",
    "NOTIFICATION_TYPES",
    "PRIORITY_LEVELS",
    "CHANNEL_TYPES",
    "BUSINESS_RULES",
    
    # Exceptions
    "NotificationModuleError"
]
