"""
Centralized Index for Internationalization Core Module - Ainflue Platform
================================================================================
Module: core/i18n/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Core Index - Multilingual System Registry
Responsibility: Central registry and coordination of all i18n components
Technologies: Python, Registry Pattern, Component Discovery
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Component registry → Module discovery → Service coordination → 
Health monitoring → Performance tracking → Centralized management
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Type, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import inspect

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Component operational status"""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ComponentType(Enum):
    """Component types in the i18n system"""
    MANAGER = "manager"
    ENGINE = "engine"
    PROCESSOR = "processor"
    LOCALIZATION = "localization"
    COMPLIANCE = "compliance"
    AI_SERVICE = "ai_service"
    SUPPORT_SERVICE = "support_service"


@dataclass
class ComponentInfo:
    """Information about registered components"""
    name: str
    component_type: ComponentType
    class_ref: Type
    instance: Optional[Any] = None
    status: ComponentStatus = ComponentStatus.INITIALIZED
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    health_status: bool = True
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class InternationalizationIndex:
    """Central registry and coordinator for all i18n components"""
    
    def __init__(self):
        self.components: Dict[str, ComponentInfo] = {}
        self.component_instances: Dict[str, Any] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.initialization_order: List[str] = []
        self.health_monitor_active = False
        
        logger.info("Internationalization Index initialized")
    
    def register_component(
        self,
        name: str,
        component_class: Type,
        component_type: ComponentType,
        dependencies: List[str] = None,
        capabilities: List[str] = None,
        version: str = "1.0.0"
    ) -> bool:
        """Register a component in the index"""
        try:
            if name in self.components:
                logger.warning(f"Component {name} already registered, updating...")
            
            component_info = ComponentInfo(
                name=name,
                component_type=component_type,
                class_ref=component_class,
                dependencies=dependencies or [],
                capabilities=capabilities or [],
                version=version
            )
            
            self.components[name] = component_info
            self.dependency_graph[name] = dependencies or []
            
            logger.info(f"Registered component: {name} ({component_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register component {name}: {e}")
            return False
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get component instance by name"""
        return self.component_instances.get(name)
    
    def get_component_info(self, name: str) -> Optional[ComponentInfo]:
        """Get component information"""
        return self.components.get(name)
    
    def list_components(
        self,
        component_type: Optional[ComponentType] = None,
        status: Optional[ComponentStatus] = None
    ) -> List[ComponentInfo]:
        """List components by type and/or status"""
        components = list(self.components.values())
        
        if component_type:
            components = [c for c in components if c.component_type == component_type]
        
        if status:
            components = [c for c in components if c.status == status]
        
        return components
    
    def resolve_dependencies(self) -> List[str]:
        """Resolve component dependencies and return initialization order"""
        try:
            # Topological sort for dependency resolution
            visited = set()
            temp_visited = set()
            order = []
            
            def visit(component_name: str):
                if component_name in temp_visited:
                    raise ValueError(f"Circular dependency detected involving {component_name}")
                
                if component_name not in visited:
                    temp_visited.add(component_name)
                    
                    # Visit dependencies first
                    for dep in self.dependency_graph.get(component_name, []):
                        if dep in self.components:
                            visit(dep)
                    
                    temp_visited.remove(component_name)
                    visited.add(component_name)
                    order.append(component_name)
            
            # Visit all components
            for component_name in self.components:
                if component_name not in visited:
                    visit(component_name)
            
            self.initialization_order = order
            logger.info(f"Dependency resolution complete. Order: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to resolve dependencies: {e}")
            return list(self.components.keys())
    
    async def initialize_component(self, name: str, **kwargs) -> bool:
        """Initialize a specific component"""
        try:
            if name not in self.components:
                logger.error(f"Component {name} not registered")
                return False
            
            component_info = self.components[name]
            
            # Check if dependencies are satisfied
            for dep in component_info.dependencies:
                if dep not in self.component_instances:
                    logger.error(f"Dependency {dep} not available for {name}")
                    return False
            
            # Initialize component
            component_class = component_info.class_ref
            
            # Check if component requires specific initialization parameters
            if hasattr(component_class, '__init__'):
                sig = inspect.signature(component_class.__init__)
                init_kwargs = {}
                
                # Inject dependencies if needed
                for param_name, param in sig.parameters.items():
                    if param_name in ['self']:
                        continue
                    if param_name in self.component_instances:
                        init_kwargs[param_name] = self.component_instances[param_name]
                    elif param_name in kwargs:
                        init_kwargs[param_name] = kwargs[param_name]
            
            # Create instance
            try:
                instance = component_class(**init_kwargs)
            except TypeError:
                # Fallback to no-args initialization
                instance = component_class()
            
            # Call async initialization if available
            if hasattr(instance, 'initialize') and callable(instance.initialize):
                if inspect.iscoroutinefunction(instance.initialize):
                    await instance.initialize()
                else:
                    instance.initialize()
            
            self.component_instances[name] = instance
            component_info.instance = instance
            component_info.status = ComponentStatus.ACTIVE
            
            logger.info(f"Component {name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize component {name}: {e}")
            if name in self.components:
                self.components[name].status = ComponentStatus.ERROR
            return False
    
    async def initialize_all_components(self, **kwargs) -> bool:
        """Initialize all components in dependency order"""
        try:
            order = self.resolve_dependencies()
            
            success_count = 0
            for component_name in order:
                if await self.initialize_component(component_name, **kwargs):
                    success_count += 1
                else:
                    logger.error(f"Failed to initialize {component_name}")
            
            logger.info(f"Initialized {success_count}/{len(order)} components")
            return success_count == len(order)
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    async def health_check(self, component_name: Optional[str] = None) -> Dict[str, bool]:
        """Perform health check on components"""
        results = {}
        
        components_to_check = [component_name] if component_name else list(self.component_instances.keys())
        
        for name in components_to_check:
            try:
                instance = self.component_instances.get(name)
                if not instance:
                    results[name] = False
                    continue
                
                # Check if component has health check method
                if hasattr(instance, 'health_check') and callable(instance.health_check):
                    if inspect.iscoroutinefunction(instance.health_check):
                        health = await instance.health_check()
                    else:
                        health = instance.health_check()
                    results[name] = bool(health)
                else:
                    # Basic health check - component exists and is active
                    results[name] = self.components[name].status == ComponentStatus.ACTIVE
                
                # Update component health status
                if name in self.components:
                    self.components[name].health_status = results[name]
                    self.components[name].last_health_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        
        return results
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_results = await self.health_check()
        
        status = {
            "total_components": len(self.components),
            "active_components": len([c for c in self.components.values() if c.status == ComponentStatus.ACTIVE]),
            "healthy_components": sum(health_results.values()),
            "component_health": health_results,
            "initialization_order": self.initialization_order,
            "dependency_graph": self.dependency_graph,
            "components": {
                name: {
                    "type": info.component_type.value,
                    "status": info.status.value,
                    "version": info.version,
                    "dependencies": info.dependencies,
                    "capabilities": info.capabilities,
                    "healthy": health_results.get(name, False)
                }
                for name, info in self.components.items()
            }
        }
        
        return status
    
    def shutdown_component(self, name: str) -> bool:
        """Shutdown a specific component"""
        try:
            if name in self.component_instances:
                instance = self.component_instances[name]
                
                # Call shutdown method if available
                if hasattr(instance, 'shutdown') and callable(instance.shutdown):
                    instance.shutdown()
                
                del self.component_instances[name]
                
                if name in self.components:
                    self.components[name].status = ComponentStatus.INACTIVE
                    self.components[name].instance = None
                
                logger.info(f"Component {name} shutdown successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to shutdown component {name}: {e}")
            return False
    
    def shutdown_all_components(self) -> bool:
        """Shutdown all components in reverse dependency order"""
        try:
            # Shutdown in reverse order
            shutdown_order = list(reversed(self.initialization_order))
            
            for component_name in shutdown_order:
                self.shutdown_component(component_name)
            
            logger.info("All components shutdown successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown components: {e}")
            return False


# Global index instance
_global_index: Optional[InternationalizationIndex] = None


def get_i18n_index() -> InternationalizationIndex:
    """Get the global internationalization index"""
    global _global_index
    if _global_index is None:
        _global_index = InternationalizationIndex()
    return _global_index


def register_i18n_component(
    name: str,
    component_class: Type,
    component_type: ComponentType,
    dependencies: List[str] = None,
    capabilities: List[str] = None,
    version: str = "1.0.0"
) -> bool:
    """Convenience function to register a component"""
    return get_i18n_index().register_component(
        name, component_class, component_type, dependencies, capabilities, version
    )


# Auto-register core components when module is imported
def _auto_register_components():
    """Auto-register core i18n components"""
    try:
        index = get_i18n_index()
        
        # Import and register components
        from .language_manager import InternationalizationManager
        from .cultural_localization import CulturalLocalization
        from .dialect_processor import DialectProcessor
        from .ui_translation_engine import UITranslationEngine
        from .rtl_language_support import RTLLanguageSupport
        from .voice_localization import VoiceLocalization
        from .currency_localization import CurrencyLocalization
        from .regional_compliance import RegionalCompliance
        from .translation_quality_ai import TranslationQualityAI
        from .locale_detection_ai import LocaleDetectionAI
        
        # Register components with dependencies
        components = [
            ("language_manager", InternationalizationManager, ComponentType.MANAGER, [], ["language_support", "translation", "detection"]),
            ("cultural_localization", CulturalLocalization, ComponentType.LOCALIZATION, ["language_manager"], ["cultural_adaptation", "context_analysis"]),
            ("dialect_processor", DialectProcessor, ComponentType.PROCESSOR, ["language_manager"], ["dialect_detection", "variant_processing"]),
            ("ui_translation_engine", UITranslationEngine, ComponentType.ENGINE, ["language_manager", "translation_quality_ai"], ["ui_translation", "batch_processing"]),
            ("rtl_language_support", RTLLanguageSupport, ComponentType.SUPPORT_SERVICE, ["language_manager"], ["rtl_processing", "text_direction"]),
            ("voice_localization", VoiceLocalization, ComponentType.LOCALIZATION, ["language_manager"], ["voice_synthesis", "audio_localization"]),
            ("currency_localization", CurrencyLocalization, ComponentType.LOCALIZATION, ["language_manager"], ["currency_formatting", "regional_currencies"]),
            ("regional_compliance", RegionalCompliance, ComponentType.COMPLIANCE, ["language_manager"], ["legal_compliance", "regional_regulations"]),
            ("translation_quality_ai", TranslationQualityAI, ComponentType.AI_SERVICE, ["language_manager"], ["quality_assessment", "ai_scoring"]),
            ("locale_detection_ai", LocaleDetectionAI, ComponentType.AI_SERVICE, ["language_manager"], ["locale_detection", "ai_analysis"]),
        ]
        
        for name, cls, comp_type, deps, caps in components:
            index.register_component(name, cls, comp_type, deps, caps)
        
        logger.info("Auto-registration of core i18n components completed")
        
    except ImportError as e:
        logger.warning(f"Some components not available for auto-registration: {e}")
    except Exception as e:
        logger.error(f"Failed to auto-register components: {e}")


# Perform auto-registration when module is imported
_auto_register_components()