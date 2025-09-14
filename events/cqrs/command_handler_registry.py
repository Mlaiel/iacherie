"""🚀 Enterprise Command Handler Registry - CQRS Architecture
===========================================================
Module: events/cqrs/command_handler_registry.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE COMMAND HANDLER REGISTRY
Advanced handler management with dependency injection and middleware
- Dynamic handler registration and discovery
- Middleware pipeline with dependency injection
- Handler versioning and backward compatibility
- Performance monitoring and health checks
- Decorator-based handler configuration
- Hot reloading and graceful degradation
"""

import asyncio
import logging
import inspect
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Type, TypeVar, get_type_hints
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import importlib
import sys

from .command_bus import Command, CommandResult, CommandStatus, CommandHandler
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class HandlerLifecycle(Enum):
    """Handler lifecycle states"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    DISABLED = "disabled"
    UNREGISTERED = "unregistered"


class MiddlewarePhase(Enum):
    """Middleware execution phases"""
    PRE_VALIDATION = "pre_validation"
    POST_VALIDATION = "post_validation"
    PRE_EXECUTION = "pre_execution"
    POST_EXECUTION = "post_execution"
    ERROR_HANDLING = "error_handling"


@dataclass
class HandlerMetadata:
    """Metadata for command handlers"""
    handler_id: str
    command_type: str
    handler_class: Type[CommandHandler]
    version: str = "1.0.0"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_enabled: bool = True
    health_check_interval: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandlerInstance:
    """Handler instance with runtime state"""
    metadata: HandlerMetadata
    instance: CommandHandler
    lifecycle_state: HandlerLifecycle = HandlerLifecycle.REGISTERED
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    total_invocations: int = 0
    successful_invocations: int = 0
    failed_invocations: int = 0
    average_execution_time: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    performance_history: deque = field(default_factory=lambda: deque(maxlen=100))


class MiddlewareManager:
    """Manage middleware pipeline for command handlers"""
    
    def __init__(self) -> None:
        self._middleware_registry: Dict[str, Callable] = {}
        self._pipeline_cache: Dict[str, List[Callable]] = {}
    
    def register_middleware(self, name: str, middleware: Callable, phase: MiddlewarePhase) -> None:
        """Register middleware with specific execution phase"""
        middleware_key = f"{phase.value}:{name}"
        self._middleware_registry[middleware_key] = middleware
        logger.info(f"Registered middleware: {name} for phase {phase.value}")
    
    def get_middleware_pipeline(self, handler_metadata: HandlerMetadata, phase: MiddlewarePhase) -> List[Callable]:
        """Get middleware pipeline for handler and phase"""
        cache_key = f"{handler_metadata.handler_id}:{phase.value}"
        
        if cache_key not in self._pipeline_cache:
            pipeline = []
            for middleware_name in handler_metadata.middleware:
                middleware_key = f"{phase.value}:{middleware_name}"
                if middleware_key in self._middleware_registry:
                    pipeline.append(self._middleware_registry[middleware_key])
            
            self._pipeline_cache[cache_key] = pipeline
        
        return self._pipeline_cache[cache_key]
    
    async def execute_middleware_pipeline(self, pipeline: List[Callable], command: Command, 
                                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute middleware pipeline"""
        context = context or {}
        
        for middleware in pipeline:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    result = await middleware(command, context)
                else:
                    result = middleware(command, context)
                
                if isinstance(result, dict):
                    context.update(result)
                    
            except Exception as e:
                logger.error(f"Middleware execution failed: {middleware.__name__} - {e}")
                context["middleware_errors"] = context.get("middleware_errors", []) + [str(e)]
        
        return context


class DependencyInjector:
    """Dependency injection container for handlers"""
    
    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_service(self, name: str, service: Any) -> None:
        """Register service instance"""
        self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """Register service factory"""
        self._factories[name] = factory
    
    def register_singleton(self, name: str, factory: Callable) -> None:
        """Register singleton service"""
        if name not in self._singletons:
            self._singletons[name] = factory()
    
    def resolve_dependencies(self, handler_class: Type[CommandHandler]) -> Dict[str, Any]:
        """Resolve dependencies for handler class"""
        dependencies = {}
        
        # Get constructor signature
        signature = inspect.signature(handler_class.__init__)
        
        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue
            
            # Check if dependency is registered
            if param_name in self._services:
                dependencies[param_name] = self._services[param_name]
            elif param_name in self._factories:
                dependencies[param_name] = self._factories[param_name]()
            elif param_name in self._singletons:
                dependencies[param_name] = self._singletons[param_name]
            elif param.default is not param.empty:
                # Has default value, skip injection
                continue
            else:
                logger.warning(f"Unresolved dependency: {param_name} for handler {handler_class.__name__}")
        
        return dependencies


class HandlerValidator:
    """Validate command handlers for registration"""
    
    @staticmethod
    def validate_handler_class(handler_class: Type[CommandHandler]) -> List[str]:
        """Validate handler class implementation"""
        errors = []
        
        # Check if inherits from CommandHandler
        if not issubclass(handler_class, CommandHandler):
            errors.append(f"Handler must inherit from CommandHandler: {handler_class}")
        
        # Check if handle method is implemented
        if not hasattr(handler_class, "handle"):
            errors.append(f"Handler must implement handle method: {handler_class}")
        
        # Check handle method signature
        try:
            signature = inspect.signature(handler_class.handle)
            params = list(signature.parameters.keys())
            
            if len(params) < 2 or params[1] != "command":
                errors.append(f"Handle method must accept command parameter: {handler_class}")
        except Exception as e:
            errors.append(f"Cannot inspect handle method signature: {e}")
        
        return errors
    
    @staticmethod
    def validate_dependencies(handler_class: Type[CommandHandler], available_services: List[str]) -> List[str]:
        """Validate handler dependencies"""
        errors = []
        
        try:
            signature = inspect.signature(handler_class.__init__)
            
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue
                
                if param.default is param.empty and param_name not in available_services:
                    errors.append(f"Unresolved dependency: {param_name}")
        
        except Exception as e:
            errors.append(f"Cannot validate dependencies: {e}")
        
        return errors


class HandlerDiscovery:
    """Discover and auto-register command handlers"""
    
    def __init__(self) -> None:
        self._discovered_handlers: Dict[str, Type[CommandHandler]] = {}
    
    def discover_handlers_in_module(self, module_name: str) -> List[Type[CommandHandler]]:
        """Discover handlers in Python module"""
        handlers = []
        
        try:
            module = importlib.import_module(module_name)
            
            for name in dir(module):
                obj = getattr(module, name)
                
                if (inspect.isclass(obj) and 
                    issubclass(obj, CommandHandler) and 
                    obj != CommandHandler):
                    handlers.append(obj)
                    
        except Exception as e:
            logger.error(f"Failed to discover handlers in module {module_name}: {e}")
        
        return handlers
    
    def discover_handlers_with_decorator(self) -> Dict[str, Type[CommandHandler]]:
        """Discover handlers marked with decorators"""
        return dict(self._discovered_handlers)
    
    def register_decorated_handler(self, command_type: str, handler_class: Type[CommandHandler]) -> None:
        """Register handler discovered via decorator"""
        self._discovered_handlers[command_type] = handler_class


# Decorator for automatic handler registration
def command_handler(command_type -> None: str, version -> None: str = "1.0.0", description -> None: str = "",
                   tags -> None: List[str] = None, middleware -> None: List[str] = None,
                   timeout_seconds -> None: int = 30, max_retries -> None: int = 3) -> None:
    """Decorator for automatic command handler registration"""
    
    def decorator(handler_class -> None: Type[CommandHandler]) -> None:
        # Store metadata in class
        handler_class._command_metadata = HandlerMetadata(
            handler_id=f"{command_type}_handler_{version}",
            command_type=command_type,
            handler_class=handler_class,
            version=version,
            description=description,
            tags=tags or [],
            middleware=middleware or [],
            timeout_seconds=timeout_seconds,
            max_retries=max_retries
        )
        
        # Register with discovery system
        discovery = HandlerDiscovery()
        discovery.register_decorated_handler(command_type, handler_class)
        
        return handler_class
    
    return decorator


class EnterpriseCommandHandlerRegistry:
    """Enterprise command handler registry with advanced features"""
    
    def __init__(self) -> None:
        self._handlers: Dict[str, HandlerInstance] = {}
        self._command_type_mapping: Dict[str, List[str]] = defaultdict(list)
        self._middleware_manager = MiddlewareManager()
        self._dependency_injector = DependencyInjector()
        self._handler_validator = HandlerValidator()
        self._handler_discovery = HandlerDiscovery()
        
        # Configuration
        self._auto_discovery_enabled = True
        self._health_check_enabled = True
        self._performance_monitoring_enabled = True
        
        # Metrics
        self._metrics = {
            "handlers_registered": 0,
            "handlers_active": 0,
            "total_invocations": 0,
            "failed_invocations": 0,
            "average_execution_time": 0.0
        }
        
        # Health check task
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def register_handler(self, metadata: HandlerMetadata, 
                        dependencies: Dict[str, Any] = None) -> str:
        """Register command handler with metadata"""
        # Validate handler class
        validation_errors = self._handler_validator.validate_handler_class(metadata.handler_class)
        if validation_errors:
            raise EventValidationError(f"Handler validation failed: {validation_errors}")
        
        # Resolve dependencies
        handler_dependencies = self._dependency_injector.resolve_dependencies(metadata.handler_class)
        if dependencies:
            handler_dependencies.update(dependencies)
        
        # Create handler instance
        try:
            handler_instance_obj = metadata.handler_class(**handler_dependencies)
        except Exception as e:
            raise EventProcessingError(f"Failed to create handler instance: {e}")
        
        # Create handler registry entry
        handler_instance = HandlerInstance(
            metadata=metadata,
            instance=handler_instance_obj,
            lifecycle_state=HandlerLifecycle.INITIALIZING
        )
        
        # Initialize handler
        try:
            if hasattr(handler_instance_obj, "initialize"):
                if asyncio.iscoroutinefunction(handler_instance_obj.initialize):
                    asyncio.create_task(handler_instance_obj.initialize())
                else:
                    handler_instance_obj.initialize()
            
            handler_instance.lifecycle_state = HandlerLifecycle.ACTIVE
            
        except Exception as e:
            logger.error(f"Handler initialization failed: {e}")
            handler_instance.lifecycle_state = HandlerLifecycle.DEGRADED
        
        # Register handler
        self._handlers[metadata.handler_id] = handler_instance
        self._command_type_mapping[metadata.command_type].append(metadata.handler_id)
        
        self._metrics["handlers_registered"] += 1
        if handler_instance.lifecycle_state == HandlerLifecycle.ACTIVE:
            self._metrics["handlers_active"] += 1
        
        logger.info(f"Registered command handler: {metadata.handler_id} for type {metadata.command_type}")
        return metadata.handler_id
    
    def register_service(self, name: str, service: Any) -> None:
        """Register service for dependency injection"""
        self._dependency_injector.register_service(name, service)
    
    def register_middleware(self, name: str, middleware: Callable, phase: MiddlewarePhase) -> None:
        """Register middleware"""
        self._middleware_manager.register_middleware(name, middleware, phase)
    
    def auto_discover_handlers(self, module_patterns: List[str]) -> int:
        """Auto-discover and register handlers from modules"""
        if not self._auto_discovery_enabled:
            return 0
        
        discovered_count = 0
        
        for pattern in module_patterns:
            try:
                handlers = self._handler_discovery.discover_handlers_in_module(pattern)
                
                for handler_class in handlers:
                    if hasattr(handler_class, "_command_metadata"):
                        metadata = handler_class._command_metadata
                        try:
                            self.register_handler(metadata)
                            discovered_count += 1
                        except Exception as e:
                            logger.error(f"Failed to register discovered handler {handler_class}: {e}")
                            
            except Exception as e:
                logger.error(f"Failed to discover handlers in pattern {pattern}: {e}")
        
        logger.info(f"Auto-discovered and registered {discovered_count} handlers")
        return discovered_count
    
    def get_handler(self, command_type: str, version: str = None) -> Optional[HandlerInstance]:
        """Get handler for command type"""
        handler_ids = self._command_type_mapping.get(command_type, [])
        
        if not handler_ids:
            return None
        
        # Filter by version if specified
        if version:
            for handler_id in handler_ids:
                handler = self._handlers[handler_id]
                if handler.metadata.version == version and handler.lifecycle_state == HandlerLifecycle.ACTIVE:
                    return handler
        
        # Return first active handler
        for handler_id in handler_ids:
            handler = self._handlers[handler_id]
            if handler.lifecycle_state == HandlerLifecycle.ACTIVE:
                return handler
        
        return None
    
    def get_all_handlers_for_command(self, command_type: str) -> List[HandlerInstance]:
        """Get all handlers for command type"""
        handler_ids = self._command_type_mapping.get(command_type, [])
        return [self._handlers[handler_id] for handler_id in handler_ids]
    
    async def execute_command(self, command: Command) -> CommandResult:
        """Execute command with full middleware pipeline"""
        handler_instance = self.get_handler(command.command_type)
        if not handler_instance:
            raise EventProcessingError(f"No handler registered for command type: {command.command_type}")
        
        start_time = time.time()
        context = {"handler_id": handler_instance.metadata.handler_id}
        
        try:
            # Pre-validation middleware
            pre_validation_pipeline = self._middleware_manager.get_middleware_pipeline(
                handler_instance.metadata, MiddlewarePhase.PRE_VALIDATION
            )
            context = await self._middleware_manager.execute_middleware_pipeline(
                pre_validation_pipeline, command, context
            )
            
            # Validation
            if hasattr(handler_instance.instance, "validate"):
                validation_result = await self._call_handler_method(
                    handler_instance.instance.validate, command
                )
                if not validation_result:
                    raise EventValidationError("Command validation failed")
            
            # Post-validation middleware
            post_validation_pipeline = self._middleware_manager.get_middleware_pipeline(
                handler_instance.metadata, MiddlewarePhase.POST_VALIDATION
            )
            context = await self._middleware_manager.execute_middleware_pipeline(
                post_validation_pipeline, command, context
            )
            
            # Pre-execution middleware
            pre_execution_pipeline = self._middleware_manager.get_middleware_pipeline(
                handler_instance.metadata, MiddlewarePhase.PRE_EXECUTION
            )
            context = await self._middleware_manager.execute_middleware_pipeline(
                pre_execution_pipeline, command, context
            )
            
            # Execute command
            result = await self._call_handler_method(handler_instance.instance.handle, command)
            
            # Post-execution middleware
            post_execution_pipeline = self._middleware_manager.get_middleware_pipeline(
                handler_instance.metadata, MiddlewarePhase.POST_EXECUTION
            )
            context["result"] = result
            context = await self._middleware_manager.execute_middleware_pipeline(
                post_execution_pipeline, command, context
            )
            
            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            await self._update_handler_metrics(handler_instance, execution_time, True)
            
            return result
            
        except Exception as e:
            # Error handling middleware
            error_pipeline = self._middleware_manager.get_middleware_pipeline(
                handler_instance.metadata, MiddlewarePhase.ERROR_HANDLING
            )
            context["error"] = e
            await self._middleware_manager.execute_middleware_pipeline(
                error_pipeline, command, context
            )
            
            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            await self._update_handler_metrics(handler_instance, execution_time, False)
            
            # Update handler state
            handler_instance.last_error = str(e)
            handler_instance.last_error_time = datetime.utcnow()
            
            raise
    
    async def _call_handler_method(self, method: Callable, *args) -> Any:
        """Call handler method with proper async handling"""
        if asyncio.iscoroutinefunction(method):
            return await method(*args)
        else:
            return method(*args)
    
    async def _update_handler_metrics(self, handler_instance: HandlerInstance, 
                                    execution_time: float, success: bool) -> None:
        """Update handler performance metrics"""
        handler_instance.total_invocations += 1
        
        if success:
            handler_instance.successful_invocations += 1
        else:
            handler_instance.failed_invocations += 1
        
        # Update average execution time
        handler_instance.average_execution_time = (
            (handler_instance.average_execution_time * (handler_instance.total_invocations - 1) + execution_time) /
            handler_instance.total_invocations
        )
        
        # Add to performance history
        handler_instance.performance_history.append({
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.utcnow()
        })
        
        # Update global metrics
        self._metrics["total_invocations"] += 1
        if not success:
            self._metrics["failed_invocations"] += 1
        
        # Update global average execution time
        current_avg = self._metrics["average_execution_time"]
        total_invocations = self._metrics["total_invocations"]
        new_avg = ((current_avg * (total_invocations - 1)) + execution_time) / total_invocations
        self._metrics["average_execution_time"] = new_avg
    
    def _start_background_tasks(self) -> None:
        """Start background tasks"""
        if self._health_check_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all handlers"""
        for handler_instance in self._handlers.values():
            try:
                if hasattr(handler_instance.instance, "health_check"):
                    is_healthy = await self._call_handler_method(
                        handler_instance.instance.health_check
                    )
                    
                    if not is_healthy and handler_instance.lifecycle_state == HandlerLifecycle.ACTIVE:
                        handler_instance.lifecycle_state = HandlerLifecycle.DEGRADED
                        self._metrics["handlers_active"] -= 1
                        logger.warning(f"Handler {handler_instance.metadata.handler_id} degraded")
                    
                    elif is_healthy and handler_instance.lifecycle_state == HandlerLifecycle.DEGRADED:
                        handler_instance.lifecycle_state = HandlerLifecycle.ACTIVE
                        self._metrics["handlers_active"] += 1
                        logger.info(f"Handler {handler_instance.metadata.handler_id} recovered")
                
                handler_instance.last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Health check failed for handler {handler_instance.metadata.handler_id}: {e}")
                if handler_instance.lifecycle_state == HandlerLifecycle.ACTIVE:
                    handler_instance.lifecycle_state = HandlerLifecycle.DEGRADED
                    self._metrics["handlers_active"] -= 1
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister command handler"""
        if handler_id not in self._handlers:
            return False
        
        handler_instance = self._handlers[handler_id]
        
        # Call cleanup if available
        try:
            if hasattr(handler_instance.instance, "cleanup"):
                if asyncio.iscoroutinefunction(handler_instance.instance.cleanup):
                    asyncio.create_task(handler_instance.instance.cleanup())
                else:
                    handler_instance.instance.cleanup()
        except Exception as e:
            logger.error(f"Handler cleanup failed: {e}")
        
        # Remove from registries
        command_type = handler_instance.metadata.command_type
        self._command_type_mapping[command_type].remove(handler_id)
        if not self._command_type_mapping[command_type]:
            del self._command_type_mapping[command_type]
        
        del self._handlers[handler_id]
        
        if handler_instance.lifecycle_state == HandlerLifecycle.ACTIVE:
            self._metrics["handlers_active"] -= 1
        
        logger.info(f"Unregistered handler: {handler_id}")
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics"""
        return dict(self._metrics)
    
    def get_handler_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all handlers"""
        status = {}
        
        for handler_id, handler_instance in self._handlers.items():
            status[handler_id] = {
                "command_type": handler_instance.metadata.command_type,
                "version": handler_instance.metadata.version,
                "lifecycle_state": handler_instance.lifecycle_state.value,
                "total_invocations": handler_instance.total_invocations,
                "successful_invocations": handler_instance.successful_invocations,
                "failed_invocations": handler_instance.failed_invocations,
                "success_rate": (
                    handler_instance.successful_invocations / handler_instance.total_invocations * 100
                ) if handler_instance.total_invocations > 0 else 0,
                "average_execution_time": handler_instance.average_execution_time,
                "last_health_check": handler_instance.last_health_check.isoformat(),
                "last_error": handler_instance.last_error,
                "last_error_time": handler_instance.last_error_time.isoformat() if handler_instance.last_error_time else None
            }
        
        return status
    
    def get_command_type_mapping(self) -> Dict[str, List[str]]:
        """Get command type to handler mapping"""
        return dict(self._command_type_mapping)
    
    async def shutdown(self) -> None:
        """Graceful shutdown of registry"""
        logger.info("Shutting down command handler registry...")
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Unregister all handlers
        handler_ids = list(self._handlers.keys())
        for handler_id in handler_ids:
            self.unregister_handler(handler_id)
        
        logger.info("Command handler registry shutdown complete")


# Singleton instance for global access
_command_handler_registry_instance: Optional[EnterpriseCommandHandlerRegistry] = None


def get_command_handler_registry() -> EnterpriseCommandHandlerRegistry:
    """Get singleton command handler registry instance"""
    global _command_handler_registry_instance
    if _command_handler_registry_instance is None:
        _command_handler_registry_instance = EnterpriseCommandHandlerRegistry()
    return _command_handler_registry_instance


def reset_command_handler_registry() -> None:
    """Reset command handler registry instance (for testing)"""
    global _command_handler_registry_instance
    if _command_handler_registry_instance:
        asyncio.create_task(_command_handler_registry_instance.shutdown())
    _command_handler_registry_instance = None