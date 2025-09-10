"""
Ainflue Core Infrastructure - Dependency Injection Core
=======================================================

Enterprise-grade dependency injection container with lifecycle management,
auto-wiring, factory patterns, and advanced container features.
Provides IoC (Inversion of Control) for all Ainflue core components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import inspect
import logging
import threading
import time
from typing import (
    Dict, List, Optional, Any, Union, Type, Callable, 
    TypeVar, Generic, Protocol, runtime_checkable
)
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
import weakref
from collections import defaultdict

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Scope(str, Enum):
    """Dependency injection scopes"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"
    PROTOTYPE = "prototype"

class LifecyclePhase(str, Enum):
    """Component lifecycle phases"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    DISPOSED = "disposed"

@runtime_checkable
class Injectable(Protocol):
    """Protocol for injectable components"""
    
    async def initialize(self) -> bool:
        """Initialize the component"""
        ...
    
    async def start(self) -> bool:
        """Start the component"""
        ...
    
    async def stop(self) -> bool:
        """Stop the component"""
        ...

@dataclass
class ComponentRegistration:
    """Component registration information"""
    interface: Type
    implementation: Type
    scope: Scope
    factory: Optional[Callable] = None
    dependencies: List[Type] = field(default_factory=list)
    lifecycle_phase: LifecyclePhase = LifecyclePhase.REGISTERED
    singleton_instance: Optional[Any] = None
    initialization_order: int = 0
    tags: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Callable[[], bool]] = None

@dataclass
class ContainerMetrics:
    """Dependency injection container metrics"""
    total_registrations: int = 0
    singleton_instances: int = 0
    transient_resolutions: int = 0
    scoped_resolutions: int = 0
    failed_resolutions: int = 0
    circular_dependencies: int = 0
    initialization_time_ms: float = 0.0

class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected"""
    pass

class ResolutionError(Exception):
    """Raised when dependency resolution fails"""
    pass

class ScopedContainer:
    """Scoped dependency container"""
    
    def __init__(self, parent_container: 'DependencyInjectionCore'):
        self.parent = parent_container
        self.scoped_instances: Dict[Type, Any] = {}
        self.disposed = False

    def get_scoped_instance(self, interface: Type) -> Optional[Any]:
        """Get scoped instance"""
        return self.scoped_instances.get(interface)

    def set_scoped_instance(self, interface: Type, instance: Any):
        """Set scoped instance"""
        self.scoped_instances[interface] = instance

    async def dispose(self):
        """Dispose scoped instances"""
        if self.disposed:
            return
        
        for instance in self.scoped_instances.values():
            if hasattr(instance, 'dispose'):
                try:
                    await instance.dispose()
                except Exception as e:
                    logger.error(f"Error disposing scoped instance: {str(e)}")
        
        self.scoped_instances.clear()
        self.disposed = True

class DependencyInjectionCore:
    """Enterprise dependency injection container"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize dependency injection container"""
        self.level = level
        self.registrations: Dict[Type, ComponentRegistration] = {}
        self.instances: Dict[Type, Any] = {}
        self.scoped_containers: weakref.WeakSet = weakref.WeakSet()
        self.resolution_stack: List[Type] = []
        self.metrics = ContainerMetrics()
        self.lifecycle_callbacks: Dict[LifecyclePhase, List[Callable]] = defaultdict(list)
        self.auto_wire_enabled = True
        self.strict_mode = level == "enterprise"
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialization order tracking
        self._initialization_order = 0
        
        # Component graph for dependency analysis
        self._dependency_graph: Dict[Type, List[Type]] = defaultdict(list)
        
        logger.info(f"💉 Dependency Injection Core initialized - Level: {level}")

    def register(
        self,
        interface: Type[T],
        implementation: Optional[Type[T]] = None,
        scope: Scope = Scope.SINGLETON,
        factory: Optional[Callable[[], T]] = None,
        condition: Optional[Callable[[], bool]] = None,
        **tags
    ) -> 'DependencyInjectionCore':
        """Register a component with the container"""
        
        if implementation is None and factory is None:
            implementation = interface
        
        if implementation and factory:
            raise ValueError("Cannot specify both implementation and factory")
        
        with self._lock:
            # Auto-discover dependencies
            dependencies = []
            if implementation:
                dependencies = self._discover_dependencies(implementation)
            
            registration = ComponentRegistration(
                interface=interface,
                implementation=implementation,
                scope=scope,
                factory=factory,
                dependencies=dependencies,
                initialization_order=self._initialization_order,
                tags=tags,
                condition=condition
            )
            
            self.registrations[interface] = registration
            self._initialization_order += 1
            self.metrics.total_registrations += 1
            
            # Update dependency graph
            self._dependency_graph[interface] = dependencies
            
            logger.debug(f"📝 Registered {interface.__name__} with scope {scope.value}")
            
        return self

    def register_singleton(self, interface: Type[T], implementation: Type[T] = None) -> 'DependencyInjectionCore':
        """Register a singleton component"""
        return self.register(interface, implementation, Scope.SINGLETON)

    def register_transient(self, interface: Type[T], implementation: Type[T] = None) -> 'DependencyInjectionCore':
        """Register a transient component"""
        return self.register(interface, implementation, Scope.TRANSIENT)

    def register_scoped(self, interface: Type[T], implementation: Type[T] = None) -> 'DependencyInjectionCore':
        """Register a scoped component"""
        return self.register(interface, implementation, Scope.SCOPED)

    def register_factory(self, interface: Type[T], factory: Callable[[], T], scope: Scope = Scope.SINGLETON) -> 'DependencyInjectionCore':
        """Register a factory function"""
        return self.register(interface, factory=factory, scope=scope)

    def register_instance(self, interface: Type[T], instance: T) -> 'DependencyInjectionCore':
        """Register an existing instance as singleton"""
        with self._lock:
            registration = ComponentRegistration(
                interface=interface,
                implementation=type(instance),
                scope=Scope.SINGLETON,
                singleton_instance=instance,
                lifecycle_phase=LifecyclePhase.INITIALIZED
            )
            
            self.registrations[interface] = registration
            self.instances[interface] = instance
            self.metrics.total_registrations += 1
            self.metrics.singleton_instances += 1
            
        return self

    def _discover_dependencies(self, implementation: Type) -> List[Type]:
        """Auto-discover constructor dependencies"""
        if not self.auto_wire_enabled:
            return []
        
        try:
            signature = inspect.signature(implementation.__init__)
            dependencies = []
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
            
            return dependencies
            
        except Exception as e:
            logger.warning(f"Failed to auto-discover dependencies for {implementation.__name__}: {str(e)}")
            return []

    def resolve(self, interface: Type[T], scoped_container: Optional[ScopedContainer] = None) -> T:
        """Resolve a component from the container"""
        
        start_time = time.time()
        
        try:
            with self._lock:
                # Check for circular dependencies
                if interface in self.resolution_stack:
                    cycle = " -> ".join([t.__name__ for t in self.resolution_stack[self.resolution_stack.index(interface):]] + [interface.__name__])
                    self.metrics.circular_dependencies += 1
                    raise CircularDependencyError(f"Circular dependency detected: {cycle}")
                
                self.resolution_stack.append(interface)
                
                try:
                    instance = self._resolve_internal(interface, scoped_container)
                    
                    # Update metrics
                    resolution_time = (time.time() - start_time) * 1000
                    self.metrics.initialization_time_ms += resolution_time
                    
                    return instance
                    
                finally:
                    self.resolution_stack.pop()
                    
        except Exception as e:
            self.metrics.failed_resolutions += 1
            logger.error(f"Failed to resolve {interface.__name__}: {str(e)}")
            raise ResolutionError(f"Cannot resolve {interface.__name__}: {str(e)}")

    def _resolve_internal(self, interface: Type[T], scoped_container: Optional[ScopedContainer]) -> T:
        """Internal resolution logic"""
        
        # Check if registered
        if interface not in self.registrations:
            if self.strict_mode:
                raise ResolutionError(f"Interface {interface.__name__} is not registered")
            
            # Try to create instance directly in non-strict mode
            return self._create_instance(interface, [], scoped_container)
        
        registration = self.registrations[interface]
        
        # Check condition
        if registration.condition and not registration.condition():
            raise ResolutionError(f"Condition not met for {interface.__name__}")
        
        # Handle different scopes
        if registration.scope == Scope.SINGLETON:
            return self._resolve_singleton(registration, scoped_container)
        elif registration.scope == Scope.TRANSIENT:
            self.metrics.transient_resolutions += 1
            return self._create_instance(registration.implementation, registration.dependencies, scoped_container)
        elif registration.scope == Scope.SCOPED:
            return self._resolve_scoped(registration, scoped_container)
        elif registration.scope == Scope.PROTOTYPE:
            return self._create_instance(registration.implementation, registration.dependencies, scoped_container)
        else:
            raise ResolutionError(f"Unknown scope: {registration.scope}")

    def _resolve_singleton(self, registration: ComponentRegistration, scoped_container: Optional[ScopedContainer]) -> Any:
        """Resolve singleton instance"""
        
        if registration.singleton_instance is not None:
            return registration.singleton_instance
        
        # Create singleton instance
        instance = self._create_instance(registration.implementation, registration.dependencies, scoped_container)
        registration.singleton_instance = instance
        self.instances[registration.interface] = instance
        self.metrics.singleton_instances += 1
        
        return instance

    def _resolve_scoped(self, registration: ComponentRegistration, scoped_container: Optional[ScopedContainer]) -> Any:
        """Resolve scoped instance"""
        
        if scoped_container is None:
            # Create new scoped container
            scoped_container = self.create_scope()
        
        # Check if instance already exists in scope
        existing = scoped_container.get_scoped_instance(registration.interface)
        if existing is not None:
            return existing
        
        # Create new scoped instance
        instance = self._create_instance(registration.implementation, registration.dependencies, scoped_container)
        scoped_container.set_scoped_instance(registration.interface, instance)
        self.metrics.scoped_resolutions += 1
        
        return instance

    def _create_instance(self, implementation: Type, dependencies: List[Type], scoped_container: Optional[ScopedContainer]) -> Any:
        """Create instance with dependency injection"""
        
        if implementation is None:
            raise ResolutionError("Implementation is None")
        
        # Check if it's a factory
        registration = self.registrations.get(implementation)
        if registration and registration.factory:
            return registration.factory()
        
        try:
            # Resolve dependencies
            resolved_dependencies = []
            for dep_type in dependencies:
                resolved_dep = self._resolve_internal(dep_type, scoped_container)
                resolved_dependencies.append(resolved_dep)
            
            # Create instance
            instance = implementation(*resolved_dependencies)
            
            return instance
            
        except Exception as e:
            raise ResolutionError(f"Failed to create instance of {implementation.__name__}: {str(e)}")

    def create_scope(self) -> ScopedContainer:
        """Create a new scope"""
        scope = ScopedContainer(self)
        self.scoped_containers.add(scope)
        return scope

    @asynccontextmanager
    async def scope(self):
        """Context manager for scoped resolution"""
        scoped_container = self.create_scope()
        try:
            yield scoped_container
        finally:
            await scoped_container.dispose()

    def try_resolve(self, interface: Type[T]) -> Optional[T]:
        """Try to resolve a component, return None if not possible"""
        try:
            return self.resolve(interface)
        except Exception:
            return None

    def is_registered(self, interface: Type) -> bool:
        """Check if interface is registered"""
        return interface in self.registrations

    def get_registration(self, interface: Type) -> Optional[ComponentRegistration]:
        """Get registration information"""
        return self.registrations.get(interface)

    def unregister(self, interface: Type):
        """Unregister a component"""
        with self._lock:
            if interface in self.registrations:
                registration = self.registrations.pop(interface)
                
                # Clean up singleton instance
                if registration.singleton_instance is not None:
                    self.instances.pop(interface, None)
                    self.metrics.singleton_instances -= 1
                
                # Remove from dependency graph
                self._dependency_graph.pop(interface, None)
                
                self.metrics.total_registrations -= 1
                
                logger.debug(f"🗑️ Unregistered {interface.__name__}")

    def add_lifecycle_callback(self, phase: LifecyclePhase, callback: Callable[[Any], None]):
        """Add lifecycle callback"""
        self.lifecycle_callbacks[phase].append(callback)

    async def initialize_all(self):
        """Initialize all registered components"""
        logger.info("🚀 Initializing all registered components")
        
        # Sort by initialization order
        sorted_registrations = sorted(
            self.registrations.values(),
            key=lambda r: r.initialization_order
        )
        
        for registration in sorted_registrations:
            await self._initialize_component(registration)

    async def _initialize_component(self, registration: ComponentRegistration):
        """Initialize a single component"""
        try:
            registration.lifecycle_phase = LifecyclePhase.INITIALIZING
            
            # Resolve instance
            instance = self.resolve(registration.interface)
            
            # Initialize if implements Injectable protocol
            if isinstance(instance, Injectable):
                await instance.initialize()
            
            registration.lifecycle_phase = LifecyclePhase.INITIALIZED
            
            # Call lifecycle callbacks
            for callback in self.lifecycle_callbacks[LifecyclePhase.INITIALIZED]:
                callback(instance)
            
            logger.debug(f"✅ Initialized {registration.interface.__name__}")
            
        except Exception as e:
            registration.lifecycle_phase = LifecyclePhase.STOPPED
            logger.error(f"❌ Failed to initialize {registration.interface.__name__}: {str(e)}")
            raise

    async def start_all(self):
        """Start all initialized components"""
        logger.info("▶️ Starting all components")
        
        for registration in self.registrations.values():
            if registration.lifecycle_phase == LifecyclePhase.INITIALIZED:
                await self._start_component(registration)

    async def _start_component(self, registration: ComponentRegistration):
        """Start a single component"""
        try:
            registration.lifecycle_phase = LifecyclePhase.STARTING
            
            instance = self.instances.get(registration.interface)
            if instance and isinstance(instance, Injectable):
                await instance.start()
            
            registration.lifecycle_phase = LifecyclePhase.RUNNING
            
            # Call lifecycle callbacks
            for callback in self.lifecycle_callbacks[LifecyclePhase.RUNNING]:
                callback(instance)
            
            logger.debug(f"▶️ Started {registration.interface.__name__}")
            
        except Exception as e:
            registration.lifecycle_phase = LifecyclePhase.STOPPED
            logger.error(f"❌ Failed to start {registration.interface.__name__}: {str(e)}")
            raise

    async def stop_all(self):
        """Stop all running components"""
        logger.info("⏹️ Stopping all components")
        
        # Stop in reverse order
        sorted_registrations = sorted(
            self.registrations.values(),
            key=lambda r: r.initialization_order,
            reverse=True
        )
        
        for registration in sorted_registrations:
            if registration.lifecycle_phase == LifecyclePhase.RUNNING:
                await self._stop_component(registration)

    async def _stop_component(self, registration: ComponentRegistration):
        """Stop a single component"""
        try:
            registration.lifecycle_phase = LifecyclePhase.STOPPING
            
            instance = self.instances.get(registration.interface)
            if instance and isinstance(instance, Injectable):
                await instance.stop()
            
            registration.lifecycle_phase = LifecyclePhase.STOPPED
            
            # Call lifecycle callbacks
            for callback in self.lifecycle_callbacks[LifecyclePhase.STOPPED]:
                callback(instance)
            
            logger.debug(f"⏹️ Stopped {registration.interface.__name__}")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {registration.interface.__name__}: {str(e)}")

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get dependency graph for visualization"""
        graph = {}
        for interface, dependencies in self._dependency_graph.items():
            graph[interface.__name__] = [dep.__name__ for dep in dependencies]
        return graph

    def validate_dependencies(self) -> List[str]:
        """Validate all dependencies can be resolved"""
        errors = []
        
        for interface, registration in self.registrations.items():
            try:
                # Try to resolve without creating instance
                self._validate_resolution_path(interface, set())
            except Exception as e:
                errors.append(f"{interface.__name__}: {str(e)}")
        
        return errors

    def _validate_resolution_path(self, interface: Type, visited: set):
        """Validate resolution path without creating instances"""
        if interface in visited:
            raise CircularDependencyError(f"Circular dependency involving {interface.__name__}")
        
        if interface not in self.registrations:
            if self.strict_mode:
                raise ResolutionError(f"Interface {interface.__name__} is not registered")
            return
        
        visited.add(interface)
        registration = self.registrations[interface]
        
        for dependency in registration.dependencies:
            self._validate_resolution_path(dependency, visited.copy())

    def get_metrics(self) -> ContainerMetrics:
        """Get container metrics"""
        return self.metrics

    def clear(self):
        """Clear all registrations and instances"""
        with self._lock:
            self.registrations.clear()
            self.instances.clear()
            self._dependency_graph.clear()
            self.metrics = ContainerMetrics()
            self._initialization_order = 0

    async def health_check(self) -> bool:
        """Health check for dependency injection system"""
        try:
            # Validate all dependencies
            errors = self.validate_dependencies()
            
            if errors:
                logger.warning(f"Dependency validation errors: {errors}")
                return len(errors) == 0
            
            return True
            
        except Exception as e:
            logger.error(f"DI health check failed: {str(e)}")
            return False

# Global container instance
container = DependencyInjectionCore()

# Decorator for easy registration
def injectable(scope: Scope = Scope.SINGLETON, interface: Optional[Type] = None):
    """Decorator to mark class as injectable"""
    def decorator(cls):
        registration_interface = interface or cls
        container.register(registration_interface, cls, scope)
        return cls
    return decorator

# Module exports
__all__ = [
    "DependencyInjectionCore", "Injectable", "Scope", "LifecyclePhase",
    "ComponentRegistration", "ContainerMetrics", "ScopedContainer",
    "CircularDependencyError", "ResolutionError", "container", "injectable"
]

logger.info("💉 Dependency Injection Core module loaded")