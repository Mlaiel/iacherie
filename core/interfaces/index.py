"""Interface discovery and registration module for IA Influencer Agent.

This module provides utilities for interface discovery, validation,
and registration within the IA Influencer Agent system.

Author: Fahed Mlaiel <mlaiel@live.de>
© 2025 - All rights reserved. Unauthorized use prohibited.
"""import inspect
from typing import Dict, List, Type, Any, Optional
from abc import ABC
import importlib
import pkgutil

from . import (
    content_interfaces,
    ai_interfaces,
    platform_interfaces,
    user_interfaces,
    monetization_interfaces,
    collaboration_interfaces,
    security_interfaces,
    monitoring_interfaces,
    storage_interfaces,
    integration_interfaces
)


class InterfaceRegistry:
    """Registry for managing and discovering system interfaces."""    
    def __init__(self):
        self._interfaces: Dict[str, Type[ABC]] = {}
        self._interface_categories: Dict[str, List[str]] = {}
        self._implementation_registry: Dict[str, List[Type]] = {}
        self._register_all_interfaces()
    
    def _register_all_interfaces(self) -> None:
        """Register all available interfaces from the module."""        interface_modules = [
            ("content", content_interfaces),
            ("ai", ai_interfaces),
            ("platform", platform_interfaces),
            ("user", user_interfaces),
            ("monetization", monetization_interfaces),
            ("collaboration", collaboration_interfaces),
            ("security", security_interfaces),
            ("monitoring", monitoring_interfaces),
            ("storage", storage_interfaces),
            ("integration", integration_interfaces)
        ]
        
        for category, module in interface_modules:
            self._register_module_interfaces(category, module)
    
    def _register_module_interfaces(self, category: str, module: Any) -> None:
        """Register interfaces from a specific module."""        self._interface_categories[category] = []
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, ABC) and 
                name.endswith('Interface') and
                obj != ABC):
                
                self._interfaces[name] = obj
                self._interface_categories[category].append(name)
                self._implementation_registry[name] = []
    
    def get_interface(self, interface_name: str) -> Optional[Type[ABC]]:
        """Get interface class by name."""        return self._interfaces.get(interface_name)
    
    def get_interfaces_by_category(self, category: str) -> List[Type[ABC]]:
        """Get all interfaces in a specific category."""        interface_names = self._interface_categories.get(category, [])
        return [self._interfaces[name] for name in interface_names]
    
    def get_all_interfaces(self) -> Dict[str, Type[ABC]]:
        """Get all registered interfaces."""        return self._interfaces.copy()
    
    def get_categories(self) -> List[str]:
        """Get all available interface categories."""        return list(self._interface_categories.keys())
    
    def register_implementation(
        self, 
        interface_name: str, 
        implementation_class: Type
    ) -> bool:
        """Register an implementation for a specific interface."""        if interface_name not in self._interfaces:
            return False
        
        interface_class = self._interfaces[interface_name]
        if not issubclass(implementation_class, interface_class):
            return False
        
        if implementation_class not in self._implementation_registry[interface_name]:
            self._implementation_registry[interface_name].append(implementation_class)
        
        return True
    
    def get_implementations(self, interface_name: str) -> List[Type]:
        """Get all registered implementations for an interface."""        return self._implementation_registry.get(interface_name, []).copy()
    
    def validate_implementation(
        self, 
        interface_name: str, 
        implementation_class: Type
    ) -> Dict[str, Any]:
        """Validate that a class properly implements an interface."""        if interface_name not in self._interfaces:
            return {
                "valid": False,
                "errors": [f"Interface '{interface_name}' not found"]
            }
        
        interface_class = self._interfaces[interface_name]
        errors = []
        
        # Check if class inherits from interface
        if not issubclass(implementation_class, interface_class):
            errors.append(f"Class does not inherit from {interface_name}")
        
        # Check if all abstract methods are implemented
        abstract_methods = getattr(interface_class, '__abstractmethods__', set())
        missing_methods = []
        
        for method_name in abstract_methods:
            if not hasattr(implementation_class, method_name):
                missing_methods.append(method_name)
            else:
                method = getattr(implementation_class, method_name)
                if getattr(method, '__isabstractmethod__', False):
                    missing_methods.append(method_name)
        
        if missing_methods:
            errors.append(f"Missing implementation for methods: {missing_methods}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "missing_methods": missing_methods,
            "abstract_methods": list(abstract_methods)
        }
    
    def get_interface_methods(self, interface_name: str) -> List[Dict[str, Any]]:
        """Get detailed information about interface methods."""        if interface_name not in self._interfaces:
            return []
        
        interface_class = self._interfaces[interface_name]
        methods = []
        
        for name, method in inspect.getmembers(interface_class, predicate=inspect.isfunction):
            if not name.startswith('_'):
                signature = inspect.signature(method)
                methods.append({
                    "name": name,
                    "signature": str(signature),
                    "parameters": list(signature.parameters.keys()),
                    "return_annotation": signature.return_annotation,
                    "docstring": inspect.getdoc(method),
                    "is_abstract": getattr(method, '__isabstractmethod__', False)
                })
        
        return methods
    
    def generate_interface_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary of all interfaces."""        summary = {
            "total_interfaces": len(self._interfaces),
            "categories": {},
            "interfaces": {}
        }
        
        for category, interface_names in self._interface_categories.items():
            summary["categories"][category] = {
                "count": len(interface_names),
                "interfaces": interface_names
            }
        
        for interface_name, interface_class in self._interfaces.items():
            abstract_methods = getattr(interface_class, '__abstractmethods__', set())
            implementations = len(self._implementation_registry.get(interface_name, []))
            
            summary["interfaces"][interface_name] = {
                "module": interface_class.__module__,
                "abstract_methods_count": len(abstract_methods),
                "abstract_methods": list(abstract_methods),
                "implementations_count": implementations,
                "docstring": inspect.getdoc(interface_class)
            }
        
        return summary


# Global interface registry instance
interface_registry = InterfaceRegistry()


def get_interface(interface_name: str) -> Optional[Type[ABC]]:
    """Get interface class by name."""    return interface_registry.get_interface(interface_name)


def get_interfaces_by_category(category: str) -> List[Type[ABC]]:
    """Get all interfaces in a specific category."""    return interface_registry.get_interfaces_by_category(category)


def validate_implementation(interface_name: str, implementation_class: Type) -> Dict[str, Any]:
    """Validate that a class properly implements an interface."""    return interface_registry.validate_implementation(interface_name, implementation_class)


def register_implementation(interface_name: str, implementation_class: Type) -> bool:
    """Register an implementation for a specific interface."""    return interface_registry.register_implementation(interface_name, implementation_class)


def list_all_interfaces() -> Dict[str, Type[ABC]]:
    """List all available interfaces."""    return interface_registry.get_all_interfaces()


def get_interface_summary() -> Dict[str, Any]:
    """Get comprehensive summary of all interfaces."""    return interface_registry.generate_interface_summary()


# Interface discovery utilities
def discover_interface_implementations(package_name: str) -> Dict[str, List[Type]]:
    """    Discover interface implementations in a package.
    
    Args:
        package_name: Name of package to scan for implementations
        
    Returns:
        Dictionary mapping interface names to implementation classes
    """    implementations = {}
    
    try:
        package = importlib.import_module(package_name)
        
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            try:
                module = importlib.import_module(modname)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if class implements any of our interfaces
                    for interface_name, interface_class in interface_registry.get_all_interfaces().items():
                        if (issubclass(obj, interface_class) and 
                            obj != interface_class and
                            not inspect.isabstract(obj)):
                            
                            if interface_name not in implementations:
                                implementations[interface_name] = []
                            implementations[interface_name].append(obj)
                            
            except ImportError:
                continue
                
    except ImportError:
        pass
    
    return implementations


# Validation utilities
def check_interface_coverage(implementation_classes: List[Type]) -> Dict[str, Any]:
    """    Check which interfaces are covered by provided implementation classes.
    
    Args:
        implementation_classes: List of implementation classes to check
        
    Returns:
        Coverage report with implemented and missing interfaces
    """    all_interfaces = interface_registry.get_all_interfaces()
    implemented = set()
    missing = set(all_interfaces.keys())
    
    coverage_details = {}
    
    for impl_class in implementation_classes:
        for interface_name, interface_class in all_interfaces.items():
            if issubclass(impl_class, interface_class):
                implemented.add(interface_name)
                missing.discard(interface_name)
                
                validation = interface_registry.validate_implementation(interface_name, impl_class)
                coverage_details[interface_name] = {
                    "implementation_class": impl_class.__name__,
                    "validation": validation
                }
    
    return {
        "total_interfaces": len(all_interfaces),
        "implemented_count": len(implemented),
        "missing_count": len(missing),
        "coverage_percentage": (len(implemented) / len(all_interfaces)) * 100,
        "implemented_interfaces": list(implemented),
        "missing_interfaces": list(missing),
        "details": coverage_details
    }


__all__ = [
    "InterfaceRegistry",
    "interface_registry",
    "get_interface",
    "get_interfaces_by_category", 
    "validate_implementation",
    "register_implementation",
    "list_all_interfaces",
    "get_interface_summary",
    "discover_interface_implementations",
    "check_interface_coverage"
]
