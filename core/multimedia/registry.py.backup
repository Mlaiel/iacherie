"""Multimedia Registry - Enterprise Component Registration System

Advanced registry system for managing multimedia processing components.
Provides dynamic component discovery, registration, and lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import inspect
import importlib
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Multimedia component types"""
    PROCESSOR = "processor"
    CONVERTER = "converter"
    ANALYZER = "analyzer"
    ENHANCER = "enhancer"
    ENCODER = "encoder"
    DECODER = "decoder"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    GENERATOR = "generator"
    FILTER = "filter"
    TRANSCODER = "transcoder"
    COMPRESSOR = "compressor"
    STREAMER = "streamer"
    WATERMARK = "watermark"


class ComponentStatus(Enum):
    """Component status"""
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    DEPRECATED = "deprecated"


@dataclass
class ComponentMetadata:
    """Component metadata information"""
    component_id: str
    name: str
    description: str
    version: str
    author: str
    component_type: ComponentType
    supported_formats: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    configuration_schema: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ComponentStatus = ComponentStatus.REGISTERED
    enabled: bool = True


@dataclass
class ComponentRegistration:
    """Component registration details"""
    metadata: ComponentMetadata
    component_class: Type
    instance: Optional[Any] = None
    initialization_config: Dict[str, Any] = field(default_factory=dict)
    runtime_stats: Dict[str, Any] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0
    average_processing_time: float = 0.0


class MultimediaComponent(ABC):
    """Base class for multimedia components"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any] = None):
        """Initialize component"""
        pass
        
    @abstractmethod
    async def process(self, data: Any, options: Dict[str, Any] = None) -> Any:
        """Process multimedia data"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Component health check"""
        pass
        
    @abstractmethod
    def get_metadata(self) -> ComponentMetadata:
        """Get component metadata"""
        pass
        
    async def cleanup(self):
        """Cleanup component resources"""
        pass


class MultimediaRegistry:
    """Enterprise multimedia component registry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.components: Dict[str, ComponentRegistration] = {}
        self.component_types: Dict[ComponentType, List[str]] = {}
        self.format_mappings: Dict[str, List[str]] = {}
        self.capability_index: Dict[str, List[str]] = {}
        
        # Registry configuration
        self.auto_discovery_enabled = config.get("auto_discovery", True)
        self.discovery_paths = config.get("discovery_paths", [])
        self.lazy_loading = config.get("lazy_loading", True)
        self.component_validation = config.get("validation", True)
        
        # Performance tracking
        self.registry_stats = {
            "total_components": 0,
            "active_components": 0,
            "failed_components": 0,
            "total_registrations": 0,
            "total_lookups": 0
        }
        
        self._initialize_component_types()
        
    async def initialize(self):
        """Initialize registry and discover components"""
        try:
            if self.auto_discovery_enabled:
                await self._discover_components()
                
            await self._initialize_core_components()
            
            logger.info(f"Multimedia registry initialized with {len(self.components)} components")
            
        except Exception as e:
            logger.error(f"Failed to initialize registry: {e}")
            raise
            
    def register_component(
        self,
        component_class: Type[MultimediaComponent],
        config: Dict[str, Any] = None
    ) -> str:
        """Register multimedia component"""
        try:
            # Create temporary instance to get metadata
            temp_instance = component_class()
            metadata = temp_instance.get_metadata()
            
            # Validate component if enabled
            if self.component_validation:
                if not self._validate_component(component_class, metadata):
                    raise ValueError(f"Component validation failed: {metadata.component_id}")
                    
            # Create registration
            registration = ComponentRegistration(
                metadata=metadata,
                component_class=component_class,
                initialization_config=config or {}
            )
            
            # Store component
            self.components[metadata.component_id] = registration
            
            # Update indexes
            self._update_indexes(metadata)
            
            # Update stats
            self.registry_stats["total_components"] += 1
            self.registry_stats["total_registrations"] += 1
            
            logger.info(f"Component registered: {metadata.component_id}")
            return metadata.component_id
            
        except Exception as e:
            logger.error(f"Failed to register component: {e}")
            raise
            
    async def get_component(self, component_id: str) -> Optional[MultimediaComponent]:
        """Get component instance by ID"""
        try:
            registration = self.components.get(component_id)
            if not registration:
                return None
                
            # Lazy loading - create instance if not exists
            if not registration.instance and self.lazy_loading:
                await self._initialize_component(registration)
                
            # Update usage stats
            registration.last_used = datetime.now(timezone.utc)
            registration.usage_count += 1
            self.registry_stats["total_lookups"] += 1
            
            return registration.instance
            
        except Exception as e:
            logger.error(f"Failed to get component {component_id}: {e}")
            return None
            
    def find_components_by_type(self, component_type: ComponentType) -> List[str]:
        """Find components by type"""
        return self.component_types.get(component_type, [])
        
    def find_components_by_format(self, format_name: str) -> List[str]:
        """Find components that support specific format"""
        return self.format_mappings.get(format_name.lower(), [])
        
    def find_components_by_capability(self, capability: str) -> List[str]:
        """Find components by capability"""
        return self.capability_index.get(capability, [])
        
    async def search_components(self, criteria: Dict[str, Any]) -> List[ComponentRegistration]:
        """Search components by multiple criteria"""
        results = []
        
        for component_id, registration in self.components.items():
            if self._matches_criteria(registration, criteria):
                results.append(registration)
                
        # Sort by relevance or performance metrics
        sort_key = criteria.get("sort_by", "usage_count")
        reverse = criteria.get("sort_desc", True)
        
        if sort_key in ["usage_count", "average_processing_time"]:
            results.sort(
                key=lambda r: r.runtime_stats.get(sort_key, 0),
                reverse=reverse
            )
            
        return results
        
    def get_component_metadata(self, component_id: str) -> Optional[ComponentMetadata]:
        """Get component metadata"""
        registration = self.components.get(component_id)
        return registration.metadata if registration else None
        
    def list_components(self, component_type: Optional[ComponentType] = None) -> List[ComponentMetadata]:
        """List all registered components"""
        if component_type:
            component_ids = self.component_types.get(component_type, [])
            return [
                self.components[comp_id].metadata 
                for comp_id in component_ids
                if comp_id in self.components
            ]
        else:
            return [reg.metadata for reg in self.components.values()]
            
    async def unregister_component(self, component_id: str) -> bool:
        """Unregister component"""
        try:
            registration = self.components.get(component_id)
            if not registration:
                return False
                
            # Cleanup component instance
            if registration.instance:
                await registration.instance.cleanup()
                
            # Remove from indexes
            self._remove_from_indexes(registration.metadata)
            
            # Remove from registry
            del self.components[component_id]
            
            # Update stats
            self.registry_stats["total_components"] -= 1
            
            logger.info(f"Component unregistered: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister component {component_id}: {e}")
            return False
            
    async def reload_component(self, component_id: str) -> bool:
        """Reload component"""
        try:
            registration = self.components.get(component_id)
            if not registration:
                return False
                
            # Cleanup existing instance
            if registration.instance:
                await registration.instance.cleanup()
                registration.instance = None
                
            # Reinitialize
            await self._initialize_component(registration)
            
            logger.info(f"Component reloaded: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload component {component_id}: {e}")
            return False
            
    async def enable_component(self, component_id: str) -> bool:
        """Enable component"""
        registration = self.components.get(component_id)
        if registration:
            registration.metadata.enabled = True
            registration.metadata.status = ComponentStatus.ACTIVE
            return True
        return False
        
    async def disable_component(self, component_id: str) -> bool:
        """Disable component"""
        registration = self.components.get(component_id)
        if registration:
            registration.metadata.enabled = False
            registration.metadata.status = ComponentStatus.DISABLED
            if registration.instance:
                await registration.instance.cleanup()
                registration.instance = None
            return True
        return False
        
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        active_count = len([
            r for r in self.components.values()
            if r.metadata.status == ComponentStatus.ACTIVE
        ])
        
        error_count = len([
            r for r in self.components.values()
            if r.metadata.status == ComponentStatus.ERROR
        ])
        
        return {
            **self.registry_stats,
            "active_components": active_count,
            "failed_components": error_count,
            "component_types": {
                comp_type.value: len(comp_ids)
                for comp_type, comp_ids in self.component_types.items()
            },
            "supported_formats": list(self.format_mappings.keys()),
            "available_capabilities": list(self.capability_index.keys())
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Registry health check"""
        try:
            # Check all active components
            healthy_components = 0
            unhealthy_components = []
            
            for component_id, registration in self.components.items():
                if registration.instance and registration.metadata.enabled:
                    try:
                        health = await registration.instance.health_check()
                        if health.get("status") == "healthy":
                            healthy_components += 1
                        else:
                            unhealthy_components.append({
                                "component_id": component_id,
                                "status": health.get("status", "unknown"),
                                "error": health.get("error")
                            })
                    except Exception as e:
                        unhealthy_components.append({
                            "component_id": component_id,
                            "status": "error",
                            "error": str(e)
                        })
                        
            status = "healthy" if not unhealthy_components else "degraded"
            
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_components": len(self.components),
                "healthy_components": healthy_components,
                "unhealthy_components": unhealthy_components,
                "registry_stats": self.get_registry_stats()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    def _initialize_component_types(self):
        """Initialize component type indexes"""
        for comp_type in ComponentType:
            self.component_types[comp_type] = []
            
    async def _discover_components(self):
        """Discover components from configured paths"""
        for path in self.discovery_paths:
            try:
                await self._discover_components_in_path(path)
            except Exception as e:
                logger.error(f"Failed to discover components in {path}: {e}")
                
    async def _discover_components_in_path(self, path: str):
        """Discover components in specific path"""
        try:
            # Import modules and scan for component classes
            module = importlib.import_module(path)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (inspect.isclass(attr) and 
                    issubclass(attr, MultimediaComponent) and 
                    attr != MultimediaComponent):
                    
                    try:
                        self.register_component(attr)
                    except Exception as e:
                        logger.error(f"Failed to register discovered component {attr_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to discover components in path {path}: {e}")
            
    async def _initialize_core_components(self):
        """Initialize core multimedia components"""
        # Register built-in components
        core_components = [
            # These would be actual component implementations
            # For now, we'll create placeholder registrations
        ]
        
        for component_class in core_components:
            try:
                self.register_component(component_class)
            except Exception as e:
                logger.error(f"Failed to register core component: {e}")
                
    async def _initialize_component(self, registration: ComponentRegistration):
        """Initialize component instance"""
        try:
            # Create instance
            instance = registration.component_class()
            
            # Initialize with config
            await instance.initialize(registration.initialization_config)
            
            # Store instance
            registration.instance = instance
            registration.metadata.status = ComponentStatus.ACTIVE
            
            # Update stats
            self.registry_stats["active_components"] += 1
            
        except Exception as e:
            registration.metadata.status = ComponentStatus.ERROR
            registration.error_count += 1
            self.registry_stats["failed_components"] += 1
            raise e
            
    def _validate_component(self, component_class: Type, metadata: ComponentMetadata) -> bool:
        """Validate component implementation"""
        try:
            # Check if class implements required methods
            required_methods = ['initialize', 'process', 'health_check', 'get_metadata']
            
            for method_name in required_methods:
                if not hasattr(component_class, method_name):
                    logger.error(f"Component {metadata.component_id} missing method: {method_name}")
                    return False
                    
            # Check metadata completeness
            if not metadata.component_id or not metadata.name:
                logger.error(f"Component metadata incomplete: {metadata.component_id}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Component validation error: {e}")
            return False
            
    def _update_indexes(self, metadata: ComponentMetadata):
        """Update component indexes"""
        # Type index
        if metadata.component_type not in self.component_types:
            self.component_types[metadata.component_type] = []
        self.component_types[metadata.component_type].append(metadata.component_id)
        
        # Format index
        for format_name in metadata.supported_formats:
            format_key = format_name.lower()
            if format_key not in self.format_mappings:
                self.format_mappings[format_key] = []
            self.format_mappings[format_key].append(metadata.component_id)
            
        # Capability index
        for capability in metadata.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(metadata.component_id)
            
    def _remove_from_indexes(self, metadata: ComponentMetadata):
        """Remove component from indexes"""
        # Type index
        if metadata.component_type in self.component_types:
            if metadata.component_id in self.component_types[metadata.component_type]:
                self.component_types[metadata.component_type].remove(metadata.component_id)
                
        # Format index
        for format_name in metadata.supported_formats:
            format_key = format_name.lower()
            if format_key in self.format_mappings:
                if metadata.component_id in self.format_mappings[format_key]:
                    self.format_mappings[format_key].remove(metadata.component_id)
                    
        # Capability index
        for capability in metadata.capabilities:
            if capability in self.capability_index:
                if metadata.component_id in self.capability_index[capability]:
                    self.capability_index[capability].remove(metadata.component_id)
                    
    def _matches_criteria(self, registration: ComponentRegistration, criteria: Dict[str, Any]) -> bool:
        """Check if component matches search criteria"""
        metadata = registration.metadata
        
        # Component type filter
        if "component_type" in criteria:
            if metadata.component_type != criteria["component_type"]:
                return False
                
        # Format filter
        if "supported_format" in criteria:
            if criteria["supported_format"] not in metadata.supported_formats:
                return False
                
        # Capability filter
        if "capability" in criteria:
            if criteria["capability"] not in metadata.capabilities:
                return False
                
        # Status filter
        if "status" in criteria:
            if metadata.status != criteria["status"]:
                return False
                
        # Enabled filter
        if "enabled" in criteria:
            if metadata.enabled != criteria["enabled"]:
                return False
                
        # Performance filter
        if "min_performance" in criteria:
            avg_time = registration.runtime_stats.get("average_processing_time", float('inf'))
            if avg_time > criteria["min_performance"]:
                return False
                
        return True
