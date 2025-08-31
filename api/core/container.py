"""
Enterprise-grade dependency injection container for IA Influencer Agent.
Implements professional IoC patterns with lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, Generic
from abc import ABC, abstractmethod
from enum import Enum
import threading
import inspect
from contextlib import contextmanager
from dataclasses import dataclass


T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime management strategies."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceDescriptor:
    """Service registration descriptor."""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT
    dependencies: Optional[list] = None


class IServiceContainer(ABC):
    """Interface for dependency injection container."""
    
    @abstractmethod
    def register_singleton(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a singleton service."""
        pass
    
    @abstractmethod
    def register_transient(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a transient service."""
        pass
    
    @abstractmethod
    def register_scoped(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a scoped service."""
        pass
    
    @abstractmethod
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a service factory."""
        pass
    
    @abstractmethod
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance."""
        pass


class ServiceContainer(IServiceContainer):
    """Professional dependency injection container implementation."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
        self._scope_stack = []
    
    def register_singleton(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a singleton service with lifetime management."""
        impl_type = implementation or service_type
        
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifetime=ServiceLifetime.SINGLETON,
                dependencies=self._get_dependencies(impl_type)
            )
    
    def register_transient(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a transient service (new instance every time)."""
        impl_type = implementation or service_type
        
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifetime=ServiceLifetime.TRANSIENT,
                dependencies=self._get_dependencies(impl_type)
            )
    
    def register_scoped(self, service_type: Type[T], implementation: Type[T] = None) -> None:
        """Register a scoped service (one instance per scope)."""
        impl_type = implementation or service_type
        
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifetime=ServiceLifetime.SCOPED,
                dependencies=self._get_dependencies(impl_type)
            )
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a service factory function."""
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                factory=factory,
                lifetime=ServiceLifetime.TRANSIENT
            )
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a pre-created instance as singleton."""
        with self._lock:
            self._services[service_type] = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifetime=ServiceLifetime.SINGLETON
            )
            self._singletons[service_type] = instance
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance with dependency injection."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Handle different lifetime strategies
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._resolve_singleton(service_type, descriptor)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._resolve_scoped(service_type, descriptor)
        else:
            return self._resolve_transient(descriptor)
    
    def _resolve_singleton(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """Resolve singleton instance with thread safety."""
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        with self._lock:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = self._create_instance(descriptor)
            self._singletons[service_type] = instance
            return instance
    
    def _resolve_scoped(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """Resolve scoped instance within current scope."""
        if service_type in self._scoped_instances:
            return self._scoped_instances[service_type]
        
        instance = self._create_instance(descriptor)
        self._scoped_instances[service_type] = instance
        return instance
    
    def _resolve_transient(self, descriptor: ServiceDescriptor) -> T:
        """Resolve transient instance (always new)."""



        return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create service instance with dependency injection."""
        # Use pre-created instance
        if descriptor.instance is not None:
            return descriptor.instance
        
        # Use factory function
        if descriptor.factory is not None:
            return descriptor.factory()
        
        # Create from implementation type
        if descriptor.implementation_type is None:
            raise ValueError("No implementation type or factory provided")
        
        # Resolve dependencies
        dependencies = []
        if descriptor.dependencies:
            for dep_type in descriptor.dependencies:
                dependencies.append(self.resolve(dep_type))
        
        # Create instance with dependencies
        return descriptor.implementation_type(*dependencies)
    
    def _get_dependencies(self, impl_type: Type) -> list:
        """Extract constructor dependencies using type hints."""



        try:
            signature = inspect.signature(impl_type.__init__)
            dependencies = []
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
            
            return dependencies
        except Exception:
            return []
    
    @contextmanager
    def create_scope(self):
        """Create a dependency injection scope."""
        self._scope_stack.append({})
        old_scoped = self._scoped_instances
        self._scoped_instances = {}
        
        try:
            yield self
        finally:
            self._scoped_instances = old_scoped
            self._scope_stack.pop()
    
    def clear_scope(self):
        """Clear current scope instances."""
        self._scoped_instances.clear()
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service type is registered."""



        return service_type in self._services
    
    def get_registered_services(self) -> Dict[Type, ServiceDescriptor]:
        """Get all registered services for debugging."""



        return self._services.copy()


class ServiceLocator:
    """Service locator pattern implementation."""
    
    _instance: Optional['ServiceLocator'] = None
    _container: Optional[IServiceContainer] = None
    _lock = threading.RLock()
    
    def __new__(cls) -> 'ServiceLocator':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_container(self, container: IServiceContainer) -> None:
        """Set the service container."""
        with self._lock:
            self._container = container
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve service using configured container."""
        if self._container is None:
            raise RuntimeError("Service container not configured")
        
        return self._container.resolve(service_type)
    
    @property
    def container(self) -> IServiceContainer:
        """Get the configured container."""
        if self._container is None:
            raise RuntimeError("Service container not configured")
        return self._container


# Global service container instance
_global_container = ServiceContainer()
_service_locator = ServiceLocator()
_service_locator.set_container(_global_container)


def register_singleton(service_type: Type[T], implementation: Type[T] = None) -> None:
    """Register singleton service in global container."""
    _global_container.register_singleton(service_type, implementation)


def register_transient(service_type: Type[T], implementation: Type[T] = None) -> None:
    """Register transient service in global container."""
    _global_container.register_transient(service_type, implementation)


def register_scoped(service_type: Type[T], implementation: Type[T] = None) -> None:
    """Register scoped service in global container."""
    _global_container.register_scoped(service_type, implementation)


def register_factory(service_type: Type[T], factory: Callable[[], T]) -> None:
    """Register service factory in global container."""
    _global_container.register_factory(service_type, factory)


def register_instance(service_type: Type[T], instance: T) -> None:
    """Register instance as singleton in global container."""
    _global_container.register_instance(service_type, instance)


def resolve(service_type: Type[T]) -> T:
    """Resolve service from global container."""



    return _global_container.resolve(service_type)


def get_container() -> ServiceContainer:
    """Get global service container."""



    return _global_container


def create_scope():
    """Create dependency injection scope."""



    return _global_container.create_scope()


class Injectable:
    """Base class for injectable services."""
    pass


def injectable(cls: Type[T]) -> Type[T]:
    """Decorator to mark class as injectable service."""
    if not hasattr(cls, '__injectable__'):
        cls.__injectable__ = True
    return cls


def service(lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT):
    """Decorator to register service with specific lifetime."""
    def decorator(cls: Type[T]) -> Type[T]:
        if lifetime == ServiceLifetime.SINGLETON:
            register_singleton(cls)
        elif lifetime == ServiceLifetime.SCOPED:
            register_scoped(cls)
        else:
            register_transient(cls)
        
        return injectable(cls)
    
    return decorator
