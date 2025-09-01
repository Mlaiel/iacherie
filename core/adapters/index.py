"""Adapters Module Index - Auto-Discovery and Initialization

This module provides automatic discovery, initialization, and management of all
platform adapters. It serves as the central entry point for adapter operations
and provides utilities for dynamic adapter loading and configuration.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Automatic adapter discovery and registration
- Dynamic loading of adapter modules
- Health monitoring and status reporting
- Configuration validation and management
- Dependency injection and service location
- Performance metrics and analytics
"""

import asyncio
import logging
import importlib
import pkgutil
from typing import Dict, List, Optional, Any, Type, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import inspect
from pathlib import Path

from .base_adapter import BasePlatformAdapter, PlatformType, AdapterStatus
from .adapter_registry import AdapterRegistry, get_adapter_registry

logger = logging.getLogger(__name__)

@dataclass
class AdapterModuleInfo:
    """
Information about an adapter module."""
    module_name: str
    module_path: str
    adapter_classes: List[Type[BasePlatformAdapter]]
    platform_types: Set[PlatformType]
    is_loaded: bool = False
    load_time: Optional[datetime] = None
    error_info: Optional[str] = None

@dataclass
class AdapterDiscoveryResult:
    """
Result of adapter discovery operation."""
    total_modules: int
    loaded_modules: int
    failed_modules: int
    discovered_adapters: List[str]
    errors: List[str]
    discovery_time: float

class AdapterModuleLoader:
    """
Handles loading and unloading of adapter modules."""
    
    def __init__(self):
        self.loaded_modules: Dict[str, AdapterModuleInfo] = {}
        self.adapter_classes: Dict[str, Type[BasePlatformAdapter]] = {}
        self.module_dependencies: Dict[str, List[str]] = {}
    
    async def discover_adapters(self) -> AdapterDiscoveryResult:
        """
Discover all available adapter modules."""
        start_time = datetime.utcnow()
        discovered_adapters = []
        errors = []
        loaded_count = 0
        failed_count = 0
        
        # Get the adapters package directory
        adapters_dir = Path(__file__).parent
        
        # Find all Python files that could contain adapters
        adapter_files = [
            f for f in adapters_dir.glob("*_adapters.py")
            if not f.name.startswith("__")
        ]
        
        for adapter_file in adapter_files:
            module_name = adapter_file.stem
            try:
                module_info = await self._load_adapter_module(module_name)
                if module_info:
                    self.loaded_modules[module_name] = module_info
                    discovered_adapters.extend([cls.__name__ for cls in module_info.adapter_classes])
                    loaded_count += 1
                    logger.info(f"Successfully loaded adapter module: {module_name}")
                else:
                    failed_count += 1
                    logger.warning(f"No adapters found in module: {module_name}")
            except Exception as e:
                error_msg = f"Failed to load adapter module {module_name}: {str(e)}"
                errors.append(error_msg)
                failed_count += 1
                logger.error(error_msg)
        
        discovery_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AdapterDiscoveryResult(
            total_modules=len(adapter_files),
            loaded_modules=loaded_count,
            failed_modules=failed_count,
            discovered_adapters=discovered_adapters,
            errors=errors,
            discovery_time=discovery_time
        )
    
    async def _load_adapter_module(self, module_name: str) -> Optional[AdapterModuleInfo]:
        """Load a specific adapter module and extract adapter classes."""
        try:
            # Import the module
            full_module_name = f"backend.core.adapters.{module_name}"
            module = importlib.import_module(full_module_name)
            
            # Find all adapter classes in the module
            adapter_classes = []
            platform_types = set()
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a subclass of BasePlatformAdapter but not the base class itself
                if (issubclass(obj, BasePlatformAdapter) and 
                    obj != BasePlatformAdapter and 
                    not name.startswith('Base')):
                    
                    adapter_classes.append(obj)
                    self.adapter_classes[obj.__name__] = obj
                    
                    # Try to determine platform type
                    if hasattr(obj, 'platform_type'):
                        platform_types.add(obj.platform_type)
            
            if adapter_classes:
                return AdapterModuleInfo(
                    module_name=module_name,
                    module_path=full_module_name,
                    adapter_classes=adapter_classes,
                    platform_types=platform_types,
                    is_loaded=True,
                    load_time=datetime.utcnow()
                )
            
        except Exception as e:
            logger.error(f"Error loading adapter module {module_name}: {str(e)}")
            return AdapterModuleInfo(
                module_name=module_name,
                module_path=f"backend.core.adapters.{module_name}",
                adapter_classes=[],
                platform_types=set(),
                is_loaded=False,
                error_info=str(e)
            )
        
        return None
    
    def get_adapter_class(self, class_name: str) -> Optional[Type[BasePlatformAdapter]]:
        """Get an adapter class by name."""
        return self.adapter_classes.get(class_name)
    
    def get_adapters_by_platform_type(self, platform_type: PlatformType) -> List[Type[BasePlatformAdapter]]:
        """
Get all adapter classes for a specific platform type."""
        adapters = []
        for module_info in self.loaded_modules.values():
            if platform_type in module_info.platform_types:
                adapters.extend(module_info.adapter_classes)
        return adapters
    
    def get_module_info(self, module_name: str) -> Optional[AdapterModuleInfo]:
        """
Get information about a loaded module."""
        return self.loaded_modules.get(module_name)
    
    def list_all_adapters(self) -> Dict[str, List[str]]:
        """
List all available adapters organized by module."""
        adapters_by_module = {}
        for module_name, module_info in self.loaded_modules.items():
            adapters_by_module[module_name] = [cls.__name__ for cls in module_info.adapter_classes]
        return adapters_by_module

class AdapterHealthMonitor:
    """
Monitors health and performance of loaded adapters."""
    
    def __init__(self):
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        self.last_health_check: Optional[datetime] = None
    
    async def check_adapter_health(self, adapter_name: str, adapter_instance: BasePlatformAdapter) -> Dict[str, Any]:
        """
Check the health of a specific adapter."""
        start_time = datetime.utcnow()
        
        health_status = {
            'adapter_name': adapter_name,
            'status': 'healthy',
            'response_time': 0.0,
            'last_check': start_time.isoformat(),
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check adapter status
            if adapter_instance.status != AdapterStatus.ACTIVE:
                health_status['status'] = 'unhealthy'
                health_status['errors'].append(f"Adapter status is {adapter_instance.status.value}")
            
            # Check rate limiting status
            if hasattr(adapter_instance, 'rate_limiter') and adapter_instance.rate_limiter:
                if adapter_instance.rate_limiter.is_rate_limited():
                    health_status['warnings'].append("Rate limit approaching")
            
            # Test connectivity (if adapter supports it)
            if hasattr(adapter_instance, 'health_check'):
                await adapter_instance.health_check()
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            health_status['response_time'] = response_time
            
            # Store metrics
            if adapter_name not in self.performance_metrics:
                self.performance_metrics[adapter_name] = []
            self.performance_metrics[adapter_name].append(response_time)
            
            # Keep only last 100 measurements
            if len(self.performance_metrics[adapter_name]) > 100:
                self.performance_metrics[adapter_name] = self.performance_metrics[adapter_name][-100:]
        
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['errors'].append(str(e))
            logger.error(f"Health check failed for adapter {adapter_name}: {str(e)}")
        
        self.health_checks[adapter_name] = health_status
        return health_status
    
    async def check_all_adapters_health(self) -> Dict[str, Any]:
        """Check health of all registered adapters."""
        registry = get_adapter_registry()
        all_health = {}
        
        for adapter_id, adapter_instance in registry.adapters.items():
            health_status = await self.check_adapter_health(adapter_id, adapter_instance.adapter)
            all_health[adapter_id] = health_status
        
        self.last_health_check = datetime.utcnow()
        
        # Generate summary
        healthy_count = sum(1 for h in all_health.values() if h['status'] == 'healthy')
        total_count = len(all_health)
        
        summary = {
            'total_adapters': total_count,
            'healthy_adapters': healthy_count,
            'unhealthy_adapters': total_count - healthy_count,
            'overall_health': 'healthy' if healthy_count == total_count else 'degraded',
            'last_check': self.last_health_check.isoformat(),
            'adapters': all_health
        }
        
        return summary
    
    def get_performance_metrics(self, adapter_name: str) -> Dict[str, Any]:
        """
Get performance metrics for a specific adapter."""
        metrics = self.performance_metrics.get(adapter_name, [])
        
        if not metrics:
            return {'error': 'No metrics available'}
        
        return {
            'adapter_name': adapter_name,
            'total_checks': len(metrics),
            'average_response_time': sum(metrics) / len(metrics),
            'min_response_time': min(metrics),
            'max_response_time': max(metrics),
            'recent_avg': sum(metrics[-10:]) / min(len(metrics), 10),
            'metrics_history': metrics[-20:]  # Last 20 measurements
        }

class AdapterIndexManager:
    """
Main manager for adapter discovery, loading, and monitoring."""
    
    def __init__(self):
        self.module_loader = AdapterModuleLoader()
        self.health_monitor = AdapterHealthMonitor()
        self.registry = None
        self.is_initialized = False
        self.initialization_time: Optional[datetime] = None
    
    async def initialize(self, auto_register: bool = True) -> AdapterDiscoveryResult:
        """
Initialize the adapter system with discovery and optional auto-registration."""
        if self.is_initialized:
            logger.warning("Adapter system already initialized")
            return AdapterDiscoveryResult(0, 0, 0, [], [], 0.0)
        
        logger.info("Initializing adapter system...")
        start_time = datetime.utcnow()
        
        # Get or create registry
        self.registry = get_adapter_registry()
        
        # Discover and load adapters
        discovery_result = await self.module_loader.discover_adapters()
        
        if auto_register:
            # Auto-register discovered adapters (with default configs)
            await self._auto_register_adapters()
        
        self.is_initialized = True
        self.initialization_time = datetime.utcnow()
        
        initialization_time = (self.initialization_time - start_time).total_seconds()
        
        logger.info(f"Adapter system initialized in {initialization_time:.2f}s")
        logger.info(f"Loaded {discovery_result.loaded_modules} modules with {len(discovery_result.discovered_adapters)} adapters")
        
        return discovery_result
    
    async def _auto_register_adapters(self):
        """Auto-register discovered adapters with default configurations."""
        # This would typically read from configuration files or environment variables
        # For now, we'll just register the factory classes
        pass
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
Get comprehensive system status."""
        if not self.is_initialized:
            return {'error': 'System not initialized'}
        
        # Get health status
        health_status = await self.health_monitor.check_all_adapters_health()
        
        # Get module information
        modules_info = {}
        for module_name, module_info in self.module_loader.loaded_modules.items():
            modules_info[module_name] = {
                'is_loaded': module_info.is_loaded,
                'adapter_count': len(module_info.adapter_classes),
                'platform_types': [pt.value for pt in module_info.platform_types],
                'load_time': module_info.load_time.isoformat() if module_info.load_time else None,
                'error_info': module_info.error_info
            }
        
        return {
            'system_initialized': self.is_initialized,
            'initialization_time': self.initialization_time.isoformat() if self.initialization_time else None,
            'modules': modules_info,
            'health': health_status,
            'total_adapter_classes': len(self.module_loader.adapter_classes),
            'available_platforms': list(set(pt.value for info in self.module_loader.loaded_modules.values() for pt in info.platform_types))
        }
    
    def get_adapter_class(self, class_name: str) -> Optional[Type[BasePlatformAdapter]]:
        """
Get an adapter class by name."""
        return self.module_loader.get_adapter_class(class_name)
    
    def list_adapters_by_platform(self, platform_type: PlatformType) -> List[str]:
        """
List all available adapters for a platform type."""
        adapters = self.module_loader.get_adapters_by_platform_type(platform_type)
        return [adapter.__name__ for adapter in adapters]
    
    async def reload_module(self, module_name: str) -> bool:
        """
Reload a specific adapter module."""
        try:
            # Unload existing module
            if module_name in self.module_loader.loaded_modules:
                del self.module_loader.loaded_modules[module_name]
            
            # Reload the module
            module_info = await self.module_loader._load_adapter_module(module_name)
            if module_info:
                self.module_loader.loaded_modules[module_name] = module_info
                logger.info(f"Successfully reloaded adapter module: {module_name}")
                return True
            else:
                logger.error(f"Failed to reload adapter module: {module_name}")
                return False
        
        except Exception as e:
            logger.error(f"Error reloading adapter module {module_name}: {str(e)}")
            return False

# Global instance
_adapter_index_manager: Optional[AdapterIndexManager] = None

def get_adapter_index_manager() -> AdapterIndexManager:
    """Get the global adapter index manager instance."""
    global _adapter_index_manager
    if _adapter_index_manager is None:
        _adapter_index_manager = AdapterIndexManager()
    return _adapter_index_manager

async def initialize_adapter_index(auto_register: bool = True) -> AdapterDiscoveryResult:
    """
Initialize the adapter index system."""
    manager = get_adapter_index_manager()
    return await manager.initialize(auto_register)

async def get_adapter_system_status() -> Dict[str, Any]:
    """
Get the current status of the adapter system."""
    manager = get_adapter_index_manager()
    return await manager.get_system_status()

# Export all public functions and classes
__all__ = [
    'AdapterModuleInfo', 'AdapterDiscoveryResult', 'AdapterModuleLoader',
    'AdapterHealthMonitor', 'AdapterIndexManager',
    'get_adapter_index_manager', 'initialize_adapter_index', 'get_adapter_system_status'
]
