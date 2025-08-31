"""Multimedia Factory - Enterprise Component Factory

Advanced factory system for creating multimedia processing components.
Provides dynamic component instantiation and configuration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import importlib
import inspect

from .registry import MultimediaRegistry, MultimediaComponent, ComponentType, ComponentMetadata
from .converter import MultimediaConverter
from .analyzer import MultimediaAnalyzer
from .optimizer import MultimediaOptimizer
from .enhancer import MultimediaEnhancer
from .transcoder import MultimediaTranscoder
from .encoder import MultimediaEncoder
from .decoder import MultimediaDecoder
from .validator import MultimediaValidator
from .normalizer import MultimediaNormalizer
from .generator import MultimediaGenerator
from .watermark import MultimediaWatermark
from .compressor import MultimediaCompressor

logger = logging.getLogger(__name__)


class FactoryMode(Enum):
    """Factory creation modes"""
    SINGLETON = "singleton"
    PROTOTYPE = "prototype"
    POOLED = "pooled"
    LAZY = "lazy"


@dataclass
class ComponentBlueprint:
    """Component creation blueprint"""
    component_id: str
    component_class: Type[MultimediaComponent]
    creation_mode: FactoryMode = FactoryMode.SINGLETON
    initialization_config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    lifecycle_hooks: Dict[str, Callable] = field(default_factory=dict)
    pool_size: int = 5
    enabled: bool = True


@dataclass
class ComponentInstance:
    """Component instance wrapper"""
    instance_id: str
    component: MultimediaComponent
    blueprint: ComponentBlueprint
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 0
    status: str = "active"  # active, idle, error, destroyed


class MultimediaFactory:
    """Enterprise multimedia component factory"""
    
    def __init__(self, config: Dict[str, Any], registry: Optional[MultimediaRegistry] = None):
        self.config = config
        self.registry = registry or MultimediaRegistry(config.get("registry", {}))
        
        # Component management
        self.blueprints: Dict[str, ComponentBlueprint] = {}
        self.singletons: Dict[str, ComponentInstance] = {}
        self.pools: Dict[str, List[ComponentInstance]] = {}
        self.instances: Dict[str, ComponentInstance] = {}
        
        # Configuration
        self.max_pool_size = config.get("max_pool_size", 10)
        self.instance_timeout = config.get("instance_timeout", 3600)
        self.cleanup_interval = config.get("cleanup_interval", 300)
        self.lazy_initialization = config.get("lazy_initialization", True)
        
        # Factory statistics
        self.factory_stats = {
            "total_created": 0,
            "total_destroyed": 0,
            "active_instances": 0,
            "creation_time": 0.0,
            "component_usage": {}
        }
        
        self._setup_default_blueprints()
        
    async def initialize(self):
        """Initialize factory"""
        try:
            await self.registry.initialize()
            
            # Pre-create singleton instances if not lazy
            if not self.lazy_initialization:
                await self._precreate_singletons()
                
            # Start cleanup task
            asyncio.create_task(self._cleanup_worker())
            
            logger.info("Multimedia factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize factory: {e}")
            raise
            
    async def create_component(
        self, 
        component_id: str, 
        config: Dict[str, Any] = None,
        force_new: bool = False
    ) -> MultimediaComponent:
        """Create multimedia component"""
        try:
            blueprint = self.blueprints.get(component_id)
            if not blueprint or not blueprint.enabled:
                raise ValueError(f"Component blueprint not found or disabled: {component_id}")
                
            config = config or {}
            
            # Handle different creation modes
            if blueprint.creation_mode == FactoryMode.SINGLETON and not force_new:
                return await self._get_singleton(blueprint, config)
            elif blueprint.creation_mode == FactoryMode.POOLED and not force_new:
                return await self._get_pooled_instance(blueprint, config)
            else:
                return await self._create_new_instance(blueprint, config)
                
        except Exception as e:
            logger.error(f"Failed to create component {component_id}: {e}")
            raise
            
    async def get_component(self, component_id: str) -> Optional[MultimediaComponent]:
        """Get existing component instance"""
        try:
            blueprint = self.blueprints.get(component_id)
            if not blueprint:
                return None
                
            if blueprint.creation_mode == FactoryMode.SINGLETON:
                if component_id in self.singletons:
                    return self.singletons[component_id].component
                    
            # For other modes, create new instance
            return await self.create_component(component_id)
            
        except Exception as e:
            logger.error(f"Failed to get component {component_id}: {e}")
            return None
            
    async def destroy_component(self, instance_id: str) -> bool:
        """Destroy component instance"""
        try:
            instance = self.instances.get(instance_id)
            if not instance:
                return False
                
            # Execute lifecycle hooks
            if "before_destroy" in instance.blueprint.lifecycle_hooks:
                await instance.blueprint.lifecycle_hooks["before_destroy"](instance.component)
                
            # Cleanup component
            await instance.component.cleanup()
            
            # Remove from tracking
            instance.status = "destroyed"
            if instance_id in self.instances:
                del self.instances[instance_id]
                
            # Remove from pools
            for pool in self.pools.values():
                pool[:] = [inst for inst in pool if inst.instance_id != instance_id]
                
            # Remove from singletons
            for component_id, singleton in list(self.singletons.items()):
                if singleton.instance_id == instance_id:
                    del self.singletons[component_id]
                    
            # Update statistics
            self.factory_stats["total_destroyed"] += 1
            self.factory_stats["active_instances"] -= 1
            
            logger.info(f"Component instance destroyed: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy component {instance_id}: {e}")
            return False
            
    def register_blueprint(self, blueprint: ComponentBlueprint) -> bool:
        """Register component blueprint"""
        try:
            # Validate blueprint
            if not self._validate_blueprint(blueprint):
                return False
                
            self.blueprints[blueprint.component_id] = blueprint
            
            # Initialize pool if needed
            if blueprint.creation_mode == FactoryMode.POOLED:
                self.pools[blueprint.component_id] = []
                
            logger.info(f"Component blueprint registered: {blueprint.component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register blueprint: {e}")
            return False
            
    def unregister_blueprint(self, component_id: str) -> bool:
        """Unregister component blueprint"""
        try:
            if component_id not in self.blueprints:
                return False
                
            # Destroy all instances
            instances_to_destroy = [
                inst.instance_id for inst in self.instances.values()
                if inst.blueprint.component_id == component_id
            ]
            
            for instance_id in instances_to_destroy:
                asyncio.create_task(self.destroy_component(instance_id))
                
            # Remove blueprint
            del self.blueprints[component_id]
            
            # Clean up pools
            if component_id in self.pools:
                del self.pools[component_id]
                
            logger.info(f"Component blueprint unregistered: {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister blueprint {component_id}: {e}")
            return False
            
    def list_blueprints(self) -> List[Dict[str, Any]]:
        """List registered blueprints"""
        return [
            {
                "component_id": blueprint.component_id,
                "component_class": blueprint.component_class.__name__,
                "creation_mode": blueprint.creation_mode.value,
                "dependencies": blueprint.dependencies,
                "enabled": blueprint.enabled,
                "pool_size": blueprint.pool_size if blueprint.creation_mode == FactoryMode.POOLED else None
            }
            for blueprint in self.blueprints.values()
        ]
        
    def get_component_instances(self, component_id: str) -> List[Dict[str, Any]]:
        """Get instances of specific component"""
        instances = [
            {
                "instance_id": inst.instance_id,
                "created_at": inst.created_at.isoformat(),
                "last_used": inst.last_used.isoformat(),
                "usage_count": inst.usage_count,
                "status": inst.status
            }
            for inst in self.instances.values()
            if inst.blueprint.component_id == component_id
        ]
        
        return instances
        
    async def get_factory_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        pool_stats = {}
        for component_id, pool in self.pools.items():
            pool_stats[component_id] = {
                "size": len(pool),
                "active": len([inst for inst in pool if inst.status == "active"]),
                "idle": len([inst for inst in pool if inst.status == "idle"])
            }
            
        return {
            **self.factory_stats,
            "active_instances": len([inst for inst in self.instances.values() if inst.status == "active"]),
            "singletons_count": len(self.singletons),
            "pools_stats": pool_stats,
            "blueprints_count": len(self.blueprints),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Factory health check"""
        try:
            # Check registry health
            registry_health = await self.registry.health_check()
            
            # Check component instances
            healthy_instances = 0
            unhealthy_instances = 0
            
            for instance in self.instances.values():
                try:
                    health = await instance.component.health_check()
                    if health.get("status") == "healthy":
                        healthy_instances += 1
                    else:
                        unhealthy_instances += 1
                except Exception:
                    unhealthy_instances += 1
                    
            status = "healthy"
            if registry_health.get("status") != "healthy" or unhealthy_instances > 0:
                status = "degraded"
                
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "registry_health": registry_health,
                "instances": {
                    "healthy": healthy_instances,
                    "unhealthy": unhealthy_instances,
                    "total": len(self.instances)
                },
                "factory_stats": await self.get_factory_stats()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _get_singleton(self, blueprint: ComponentBlueprint, config: Dict[str, Any]) -> MultimediaComponent:
        """Get or create singleton instance"""
        if blueprint.component_id in self.singletons:
            instance = self.singletons[blueprint.component_id]
            instance.last_used = datetime.now(timezone.utc)
            instance.usage_count += 1
            return instance.component
            
        # Create new singleton
        component = await self._create_new_instance(blueprint, config)
        return component
        
    async def _get_pooled_instance(self, blueprint: ComponentBlueprint, config: Dict[str, Any]) -> MultimediaComponent:
        """Get instance from pool"""
        pool = self.pools.get(blueprint.component_id, [])
        
        # Find idle instance
        for instance in pool:
            if instance.status == "idle":
                instance.status = "active"
                instance.last_used = datetime.now(timezone.utc)
                instance.usage_count += 1
                return instance.component
                
        # Create new instance if pool not full
        if len(pool) < blueprint.pool_size:
            component = await self._create_new_instance(blueprint, config)
            return component
            
        # Wait for instance to become available
        # This is a simplified implementation
        # In production, you might implement a proper queue
        await asyncio.sleep(0.1)
        return await self._get_pooled_instance(blueprint, config)
        
    async def _create_new_instance(self, blueprint: ComponentBlueprint, config: Dict[str, Any]) -> MultimediaComponent:
        """Create new component instance"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Resolve dependencies
            dependencies = await self._resolve_dependencies(blueprint.dependencies)
            
            # Merge configuration
            final_config = {**blueprint.initialization_config, **config}
            if dependencies:
                final_config["dependencies"] = dependencies
                
            # Create component instance
            component = blueprint.component_class()
            
            # Initialize component
            await component.initialize(final_config)
            
            # Execute lifecycle hooks
            if "after_create" in blueprint.lifecycle_hooks:
                await blueprint.lifecycle_hooks["after_create"](component)
                
            # Create instance wrapper
            instance_id = f"{blueprint.component_id}_{datetime.now().timestamp()}_{id(component)}"
            instance = ComponentInstance(
                instance_id=instance_id,
                component=component,
                blueprint=blueprint
            )
            
            # Track instance
            self.instances[instance_id] = instance
            
            # Handle specific creation modes
            if blueprint.creation_mode == FactoryMode.SINGLETON:
                self.singletons[blueprint.component_id] = instance
            elif blueprint.creation_mode == FactoryMode.POOLED:
                self.pools[blueprint.component_id].append(instance)
                instance.status = "idle"
                
            # Update statistics
            creation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.factory_stats["total_created"] += 1
            self.factory_stats["active_instances"] += 1
            self.factory_stats["creation_time"] += creation_time
            
            # Update component usage stats
            component_id = blueprint.component_id
            if component_id not in self.factory_stats["component_usage"]:
                self.factory_stats["component_usage"][component_id] = {
                    "created": 0,
                    "avg_creation_time": 0.0
                }
                
            usage_stats = self.factory_stats["component_usage"][component_id]
            usage_stats["created"] += 1
            usage_stats["avg_creation_time"] = (
                (usage_stats["avg_creation_time"] * (usage_stats["created"] - 1) + creation_time) /
                usage_stats["created"]
            )
            
            logger.info(f"Component created: {blueprint.component_id} ({instance_id})")
            return component
            
        except Exception as e:
            logger.error(f"Failed to create component {blueprint.component_id}: {e}")
            raise
            
    async def _resolve_dependencies(self, dependencies: List[str]) -> Dict[str, MultimediaComponent]:
        """Resolve component dependencies"""
        resolved = {}
        
        for dep_id in dependencies:
            dep_component = await self.get_component(dep_id)
            if dep_component:
                resolved[dep_id] = dep_component
            else:
                logger.warning(f"Dependency not found: {dep_id}")
                
        return resolved
        
    def _setup_default_blueprints(self):
        """Setup default component blueprints"""
        default_blueprints = [
            ComponentBlueprint(
                component_id="multimedia_converter",
                component_class=MultimediaConverter,
                creation_mode=FactoryMode.SINGLETON
            ),
            ComponentBlueprint(
                component_id="multimedia_analyzer",
                component_class=MultimediaAnalyzer,
                creation_mode=FactoryMode.SINGLETON
            ),
            ComponentBlueprint(
                component_id="multimedia_optimizer",
                component_class=MultimediaOptimizer,
                creation_mode=FactoryMode.POOLED,
                pool_size=3
            ),
            ComponentBlueprint(
                component_id="multimedia_enhancer",
                component_class=MultimediaEnhancer,
                creation_mode=FactoryMode.POOLED,
                pool_size=3
            ),
            ComponentBlueprint(
                component_id="multimedia_transcoder",
                component_class=MultimediaTranscoder,
                creation_mode=FactoryMode.POOLED,
                pool_size=5
            ),
            ComponentBlueprint(
                component_id="multimedia_encoder",
                component_class=MultimediaEncoder,
                creation_mode=FactoryMode.POOLED,
                pool_size=5
            ),
            ComponentBlueprint(
                component_id="multimedia_decoder",
                component_class=MultimediaDecoder,
                creation_mode=FactoryMode.POOLED,
                pool_size=5
            ),
            ComponentBlueprint(
                component_id="multimedia_validator",
                component_class=MultimediaValidator,
                creation_mode=FactoryMode.SINGLETON
            ),
            ComponentBlueprint(
                component_id="multimedia_normalizer",
                component_class=MultimediaNormalizer,
                creation_mode=FactoryMode.POOLED,
                pool_size=3
            ),
            ComponentBlueprint(
                component_id="multimedia_generator",
                component_class=MultimediaGenerator,
                creation_mode=FactoryMode.POOLED,
                pool_size=2
            ),
            ComponentBlueprint(
                component_id="multimedia_watermark",
                component_class=MultimediaWatermark,
                creation_mode=FactoryMode.POOLED,
                pool_size=3
            ),
            ComponentBlueprint(
                component_id="multimedia_compressor",
                component_class=MultimediaCompressor,
                creation_mode=FactoryMode.POOLED,
                pool_size=5
            )
        ]
        
        for blueprint in default_blueprints:
            self.blueprints[blueprint.component_id] = blueprint
            
            # Initialize pools
            if blueprint.creation_mode == FactoryMode.POOLED:
                self.pools[blueprint.component_id] = []
                
    def _validate_blueprint(self, blueprint: ComponentBlueprint) -> bool:
        """Validate component blueprint"""
        try:
            # Basic validation
            if not blueprint.component_id:
                logger.error("Blueprint component_id is required")
                return False
                
            if not blueprint.component_class:
                logger.error("Blueprint component_class is required")
                return False
                
            # Check if class is valid
            if not issubclass(blueprint.component_class, MultimediaComponent):
                logger.error(f"Component class must inherit from MultimediaComponent: {blueprint.component_class}")
                return False
                
            # Check pool size for pooled components
            if blueprint.creation_mode == FactoryMode.POOLED and blueprint.pool_size <= 0:
                logger.error("Pool size must be greater than 0 for pooled components")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Blueprint validation error: {e}")
            return False
            
    async def _precreate_singletons(self):
        """Pre-create singleton instances"""
        for blueprint in self.blueprints.values():
            if blueprint.creation_mode == FactoryMode.SINGLETON and blueprint.enabled:
                try:
                    await self._create_new_instance(blueprint, {})
                except Exception as e:
                    logger.error(f"Failed to precreate singleton {blueprint.component_id}: {e}")
                    
    async def _cleanup_worker(self):
        """Background cleanup worker"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_instances()
                await self._optimize_pools()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                
    async def _cleanup_expired_instances(self):
        """Cleanup expired instances"""
        current_time = datetime.now(timezone.utc)
        expired_instances = []
        
        for instance_id, instance in self.instances.items():
            # Check if instance is expired
            elapsed = (current_time - instance.last_used).total_seconds()
            if elapsed > self.instance_timeout and instance.status == "idle":
                expired_instances.append(instance_id)
                
        # Cleanup expired instances
        for instance_id in expired_instances:
            await self.destroy_component(instance_id)
            
        if expired_instances:
            logger.info(f"Cleaned up {len(expired_instances)} expired instances")
            
    async def _optimize_pools(self):
        """Optimize pool sizes"""
        for component_id, pool in self.pools.items():
            blueprint = self.blueprints.get(component_id)
            if not blueprint:
                continue
                
            # Remove destroyed instances from pool
            pool[:] = [inst for inst in pool if inst.status != "destroyed"]
            
            # Adjust pool size based on usage
            active_count = len([inst for inst in pool if inst.status == "active"])
            idle_count = len([inst for inst in pool if inst.status == "idle"])
            
            # If too many idle instances, remove some
            if idle_count > blueprint.pool_size // 2:
                instances_to_remove = idle_count - (blueprint.pool_size // 2)
                for _ in range(instances_to_remove):
                    if pool:
                        instance = pool.pop(0)
                        await self.destroy_component(instance.instance_id)
