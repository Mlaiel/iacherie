#!/usr/bin/env python3
"""
Resource Coordinator - Enterprise Core Component
Platform resource allocation and management with auto-scaling coordination

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive resource coordination capabilities including:
- Platform resource allocation and management
- Auto-scaling coordination across services
- Resource optimization and performance tuning
- Capacity planning and forecasting
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource type enumeration"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    CUSTOM = "custom"


class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class ResourceStatus(Enum):
    """Resource status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERLOADED = "overloaded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


@dataclass
class ResourceMetrics:
    """Resource utilization metrics"""
    resource_type: ResourceType
    total_capacity: float
    allocated_capacity: float
    used_capacity: float
    available_capacity: float
    utilization_percentage: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourcePool:
    """Resource pool definition"""
    pool_id: str
    name: str
    resource_type: ResourceType
    total_capacity: float
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    min_available: float = 0.1  # 10% minimum
    max_utilization: float = 0.8  # 80% maximum
    scaling_enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Resource allocation request"""
    allocation_id: str
    service_id: str
    resource_type: ResourceType
    requested_amount: float
    allocated_amount: float = 0.0
    status: ResourceStatus = ResourceStatus.AVAILABLE
    priority: int = 1  # 1-10, 10 being highest
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration"""
    policy_id: str
    resource_type: ResourceType
    target_utilization: float = 0.7  # 70%
    scale_up_threshold: float = 0.8  # 80%
    scale_down_threshold: float = 0.4  # 40%
    min_capacity: float = 1.0
    max_capacity: float = 100.0
    scale_up_factor: float = 1.5
    scale_down_factor: float = 0.7
    cooldown_period_seconds: int = 300
    evaluation_period_seconds: int = 60
    enabled: bool = True


@dataclass
class CapacityForecast:
    """Capacity planning forecast"""
    resource_type: ResourceType
    current_capacity: float
    predicted_demand: float
    forecast_horizon_hours: int
    confidence_level: float
    recommended_capacity: float
    recommended_action: ScalingDirection
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ResourceProvider(ABC):
    """Abstract resource provider interface"""
    
    @abstractmethod
    async def get_current_metrics(self, resource_type: ResourceType) -> ResourceMetrics:
        """Get current resource metrics"""
        pass
    
    @abstractmethod
    async def allocate_resource(self, allocation: ResourceAllocation) -> bool:
        """Allocate resources"""
        pass
    
    @abstractmethod
    async def deallocate_resource(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        pass
    
    @abstractmethod
    async def scale_resource(self, resource_type: ResourceType, new_capacity: float) -> bool:
        """Scale resource capacity"""
        pass


class MockResourceProvider(ResourceProvider):
    """Mock resource provider for testing"""
    
    def __init__(self):
        self.resource_pools: Dict[ResourceType, ResourcePool] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        
        # Initialize mock pools
        self._initialize_mock_pools()
    
    def _initialize_mock_pools(self):
        """Initialize mock resource pools"""
        self.resource_pools[ResourceType.CPU] = ResourcePool(
            pool_id="cpu_pool_1",
            name="Primary CPU Pool",
            resource_type=ResourceType.CPU,
            total_capacity=100.0  # 100 cores
        )
        
        self.resource_pools[ResourceType.MEMORY] = ResourcePool(
            pool_id="memory_pool_1",
            name="Primary Memory Pool",
            resource_type=ResourceType.MEMORY,
            total_capacity=1000.0  # 1000 GB
        )
        
        self.resource_pools[ResourceType.STORAGE] = ResourcePool(
            pool_id="storage_pool_1",
            name="Primary Storage Pool",
            resource_type=ResourceType.STORAGE,
            total_capacity=10000.0  # 10 TB
        )
    
    async def get_current_metrics(self, resource_type: ResourceType) -> ResourceMetrics:
        """Get current resource metrics"""
        pool = self.resource_pools.get(resource_type)
        if not pool:
            raise ValueError(f"Resource pool not found for type: {resource_type}")
        
        # Calculate current usage
        used_capacity = pool.allocated_capacity * 0.8  # Simulate 80% usage of allocated
        available_capacity = pool.total_capacity - pool.allocated_capacity
        utilization_percentage = (pool.allocated_capacity / pool.total_capacity) * 100
        
        return ResourceMetrics(
            resource_type=resource_type,
            total_capacity=pool.total_capacity,
            allocated_capacity=pool.allocated_capacity,
            used_capacity=used_capacity,
            available_capacity=available_capacity,
            utilization_percentage=utilization_percentage
        )
    
    async def allocate_resource(self, allocation: ResourceAllocation) -> bool:
        """Allocate resources"""
        pool = self.resource_pools.get(allocation.resource_type)
        if not pool:
            return False
        
        available = pool.total_capacity - pool.allocated_capacity
        if available >= allocation.requested_amount:
            pool.allocated_capacity += allocation.requested_amount
            allocation.allocated_amount = allocation.requested_amount
            allocation.status = ResourceStatus.ALLOCATED
            self.allocations[allocation.allocation_id] = allocation
            return True
        
        return False
    
    async def deallocate_resource(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        allocation = self.allocations.get(allocation_id)
        if not allocation:
            return False
        
        pool = self.resource_pools.get(allocation.resource_type)
        if pool:
            pool.allocated_capacity -= allocation.allocated_amount
            allocation.status = ResourceStatus.AVAILABLE
            del self.allocations[allocation_id]
            return True
        
        return False
    
    async def scale_resource(self, resource_type: ResourceType, new_capacity: float) -> bool:
        """Scale resource capacity"""
        pool = self.resource_pools.get(resource_type)
        if not pool:
            return False
        
        if new_capacity >= pool.allocated_capacity:
            pool.total_capacity = new_capacity
            return True
        
        return False


class ResourceCoordinator:
    """
    Enterprise Resource Coordinator
    
    Provides comprehensive platform resource allocation, management, and
    auto-scaling coordination with enterprise-grade optimization and
    capacity planning capabilities.
    """
    
    def __init__(self, resource_provider: Optional[ResourceProvider] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.resource_provider = resource_provider or MockResourceProvider()
        self.resource_pools: Dict[str, ResourcePool] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.scaling_policies: Dict[ResourceType, ScalingPolicy] = {}
        self.metrics_history: Dict[ResourceType, List[ResourceMetrics]] = {}
        self.last_scaling_action: Dict[ResourceType, datetime] = {}
        
        # Configuration
        self._monitoring_interval = self.config.get('monitoring_interval', 30)
        self._metrics_retention_hours = self.config.get('metrics_retention_hours', 168)  # 7 days
        self._scaling_evaluation_interval = self.config.get('scaling_evaluation_interval', 60)
        self._capacity_forecast_interval = self.config.get('capacity_forecast_interval', 3600)  # 1 hour
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._scaling_task: Optional[asyncio.Task] = None
        self._forecasting_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("Resource Coordinator initialized")
    
    async def start(self) -> None:
        """Start the resource coordinator"""
        try:
            logger.info("Starting Resource Coordinator...")
            
            # Initialize default scaling policies
            await self._initialize_default_policies()
            
            # Start background tasks
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._scaling_task = asyncio.create_task(self._scaling_loop())
            self._forecasting_task = asyncio.create_task(self._forecasting_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Resource Coordinator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Resource Coordinator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the resource coordinator"""
        try:
            logger.info("Stopping Resource Coordinator...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
            if self._scaling_task:
                self._scaling_task.cancel()
            if self._forecasting_task:
                self._forecasting_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            logger.info("Resource Coordinator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Resource Coordinator: {e}")
    
    # Resource Pool Management
    async def register_resource_pool(self, pool: ResourcePool) -> bool:
        """Register a resource pool"""
        try:
            self.resource_pools[pool.pool_id] = pool
            
            # Initialize metrics history
            if pool.resource_type not in self.metrics_history:
                self.metrics_history[pool.resource_type] = []
            
            logger.info(f"Resource pool {pool.pool_id} ({pool.resource_type.value}) registered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register resource pool {pool.pool_id}: {e}")
            return False
    
    async def unregister_resource_pool(self, pool_id: str) -> bool:
        """Unregister a resource pool"""
        try:
            if pool_id in self.resource_pools:
                pool = self.resource_pools.pop(pool_id)
                logger.info(f"Resource pool {pool_id} ({pool.resource_type.value}) unregistered")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister resource pool {pool_id}: {e}")
            return False
    
    # Resource Allocation
    async def allocate_resources(self, allocation: ResourceAllocation) -> bool:
        """Allocate resources for a service"""
        try:
            # Check if resources are available
            metrics = await self.resource_provider.get_current_metrics(allocation.resource_type)
            
            if metrics.available_capacity >= allocation.requested_amount:
                # Attempt allocation
                success = await self.resource_provider.allocate_resource(allocation)
                
                if success:
                    self.allocations[allocation.allocation_id] = allocation
                    logger.info(f"Resources allocated: {allocation.requested_amount} {allocation.resource_type.value} to {allocation.service_id}")
                    return True
            
            logger.warning(f"Insufficient resources for allocation {allocation.allocation_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to allocate resources for {allocation.allocation_id}: {e}")
            return False
    
    async def deallocate_resources(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        try:
            if allocation_id not in self.allocations:
                logger.warning(f"Allocation {allocation_id} not found")
                return False
            
            allocation = self.allocations[allocation_id]
            success = await self.resource_provider.deallocate_resource(allocation_id)
            
            if success:
                del self.allocations[allocation_id]
                logger.info(f"Resources deallocated: {allocation.allocated_amount} {allocation.resource_type.value} from {allocation.service_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to deallocate resources for {allocation_id}: {e}")
            return False
    
    # Scaling Management
    async def register_scaling_policy(self, policy: ScalingPolicy) -> bool:
        """Register an auto-scaling policy"""
        try:
            self.scaling_policies[policy.resource_type] = policy
            logger.info(f"Scaling policy registered for {policy.resource_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register scaling policy for {policy.resource_type.value}: {e}")
            return False
    
    async def trigger_scaling(self, resource_type: ResourceType, direction: ScalingDirection, factor: Optional[float] = None) -> bool:
        """Manually trigger resource scaling"""
        try:
            policy = self.scaling_policies.get(resource_type)
            if not policy or not policy.enabled:
                logger.warning(f"No scaling policy or disabled for {resource_type.value}")
                return False
            
            # Check cooldown period
            last_scaling = self.last_scaling_action.get(resource_type)
            if last_scaling:
                cooldown_remaining = (datetime.utcnow() - last_scaling).total_seconds()
                if cooldown_remaining < policy.cooldown_period_seconds:
                    logger.info(f"Scaling cooldown active for {resource_type.value}")
                    return False
            
            # Get current metrics
            metrics = await self.resource_provider.get_current_metrics(resource_type)
            current_capacity = metrics.total_capacity
            
            # Calculate new capacity
            if direction == ScalingDirection.UP:
                scale_factor = factor or policy.scale_up_factor
                new_capacity = min(current_capacity * scale_factor, policy.max_capacity)
            elif direction == ScalingDirection.DOWN:
                scale_factor = factor or policy.scale_down_factor
                new_capacity = max(current_capacity * scale_factor, policy.min_capacity)
            else:
                return False
            
            # Ensure new capacity can accommodate allocated resources
            if new_capacity < metrics.allocated_capacity:
                logger.warning(f"Cannot scale down below allocated capacity for {resource_type.value}")
                return False
            
            # Perform scaling
            success = await self.resource_provider.scale_resource(resource_type, new_capacity)
            
            if success:
                self.last_scaling_action[resource_type] = datetime.utcnow()
                logger.info(f"Scaled {resource_type.value} from {current_capacity} to {new_capacity}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to scale {resource_type.value}: {e}")
            return False
    
    # Metrics and Monitoring
    async def get_resource_metrics(self, resource_type: Optional[ResourceType] = None) -> Dict[str, Any]:
        """Get current resource metrics"""
        try:
            if resource_type:
                metrics = await self.resource_provider.get_current_metrics(resource_type)
                return {
                    "resource_type": resource_type.value,
                    "total_capacity": metrics.total_capacity,
                    "allocated_capacity": metrics.allocated_capacity,
                    "used_capacity": metrics.used_capacity,
                    "available_capacity": metrics.available_capacity,
                    "utilization_percentage": metrics.utilization_percentage,
                    "timestamp": metrics.timestamp.isoformat()
                }
            else:
                # Return metrics for all resource types
                all_metrics = {}
                for rt in ResourceType:
                    try:
                        metrics = await self.resource_provider.get_current_metrics(rt)
                        all_metrics[rt.value] = {
                            "total_capacity": metrics.total_capacity,
                            "allocated_capacity": metrics.allocated_capacity,
                            "used_capacity": metrics.used_capacity,
                            "available_capacity": metrics.available_capacity,
                            "utilization_percentage": metrics.utilization_percentage,
                            "timestamp": metrics.timestamp.isoformat()
                        }
                    except:
                        pass  # Skip resource types that don't exist
                
                return all_metrics
            
        except Exception as e:
            logger.error(f"Failed to get resource metrics: {e}")
            return {}
    
    async def get_resource_history(self, resource_type: ResourceType, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical resource metrics"""
        try:
            history = self.metrics_history.get(resource_type, [])
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_metrics = [
                {
                    "total_capacity": m.total_capacity,
                    "allocated_capacity": m.allocated_capacity,
                    "used_capacity": m.used_capacity,
                    "utilization_percentage": m.utilization_percentage,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in history
                if m.timestamp > cutoff_time
            ]
            
            return recent_metrics
            
        except Exception as e:
            logger.error(f"Failed to get resource history for {resource_type.value}: {e}")
            return []
    
    # Capacity Forecasting
    async def generate_capacity_forecast(self, resource_type: ResourceType, horizon_hours: int = 24) -> CapacityForecast:
        """Generate capacity forecast using historical data"""
        try:
            history = self.metrics_history.get(resource_type, [])
            
            if len(history) < 10:  # Need minimum data points
                current_metrics = await self.resource_provider.get_current_metrics(resource_type)
                return CapacityForecast(
                    resource_type=resource_type,
                    current_capacity=current_metrics.total_capacity,
                    predicted_demand=current_metrics.allocated_capacity,
                    forecast_horizon_hours=horizon_hours,
                    confidence_level=0.5,
                    recommended_capacity=current_metrics.total_capacity,
                    recommended_action=ScalingDirection.STABLE
                )
            
            # Simple trend analysis
            recent_metrics = history[-24:]  # Last 24 data points
            utilizations = [m.utilization_percentage for m in recent_metrics]
            
            # Calculate trend
            trend = self._calculate_trend(utilizations)
            current_capacity = recent_metrics[-1].total_capacity
            current_utilization = recent_metrics[-1].utilization_percentage
            
            # Predict future utilization
            predicted_utilization = current_utilization + (trend * horizon_hours)
            predicted_demand = (predicted_utilization / 100) * current_capacity
            
            # Determine recommended action
            policy = self.scaling_policies.get(resource_type)
            if policy:
                if predicted_utilization > policy.scale_up_threshold * 100:
                    recommended_action = ScalingDirection.UP
                    recommended_capacity = current_capacity * policy.scale_up_factor
                elif predicted_utilization < policy.scale_down_threshold * 100:
                    recommended_action = ScalingDirection.DOWN
                    recommended_capacity = current_capacity * policy.scale_down_factor
                else:
                    recommended_action = ScalingDirection.STABLE
                    recommended_capacity = current_capacity
            else:
                recommended_action = ScalingDirection.STABLE
                recommended_capacity = current_capacity
            
            # Calculate confidence based on data variance
            confidence = max(0.1, 1.0 - (statistics.stdev(utilizations) / 100))
            
            return CapacityForecast(
                resource_type=resource_type,
                current_capacity=current_capacity,
                predicted_demand=predicted_demand,
                forecast_horizon_hours=horizon_hours,
                confidence_level=confidence,
                recommended_capacity=recommended_capacity,
                recommended_action=recommended_action
            )
            
        except Exception as e:
            logger.error(f"Failed to generate capacity forecast for {resource_type.value}: {e}")
            current_metrics = await self.resource_provider.get_current_metrics(resource_type)
            return CapacityForecast(
                resource_type=resource_type,
                current_capacity=current_metrics.total_capacity,
                predicted_demand=current_metrics.allocated_capacity,
                forecast_horizon_hours=horizon_hours,
                confidence_level=0.1,
                recommended_capacity=current_metrics.total_capacity,
                recommended_action=ScalingDirection.STABLE
            )
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    # Status and Reports
    async def get_coordination_status(self) -> Dict[str, Any]:
        """Get overall resource coordination status"""
        try:
            status = {
                "resource_pools": len(self.resource_pools),
                "active_allocations": len(self.allocations),
                "scaling_policies": len(self.scaling_policies),
                "total_resources": {},
                "utilization_summary": {},
                "recent_scaling_actions": []
            }
            
            # Aggregate resource information
            for resource_type in ResourceType:
                try:
                    metrics = await self.resource_provider.get_current_metrics(resource_type)
                    status["total_resources"][resource_type.value] = {
                        "total_capacity": metrics.total_capacity,
                        "allocated_capacity": metrics.allocated_capacity,
                        "utilization_percentage": metrics.utilization_percentage
                    }
                    
                    # Utilization summary
                    if metrics.utilization_percentage > 80:
                        util_status = "high"
                    elif metrics.utilization_percentage > 60:
                        util_status = "medium"
                    else:
                        util_status = "low"
                    
                    status["utilization_summary"][resource_type.value] = util_status
                    
                except:
                    pass
            
            # Recent scaling actions
            for resource_type, timestamp in self.last_scaling_action.items():
                if (datetime.utcnow() - timestamp).total_seconds() < 3600:  # Last hour
                    status["recent_scaling_actions"].append({
                        "resource_type": resource_type.value,
                        "timestamp": timestamp.isoformat()
                    })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get coordination status: {e}")
            return {"error": str(e)}
    
    # Internal Methods
    async def _initialize_default_policies(self) -> None:
        """Initialize default scaling policies"""
        try:
            # CPU scaling policy
            cpu_policy = ScalingPolicy(
                policy_id="default_cpu_policy",
                resource_type=ResourceType.CPU,
                target_utilization=0.7,
                scale_up_threshold=0.8,
                scale_down_threshold=0.4,
                min_capacity=10.0,
                max_capacity=1000.0,
                cooldown_period_seconds=300
            )
            
            await self.register_scaling_policy(cpu_policy)
            
            # Memory scaling policy
            memory_policy = ScalingPolicy(
                policy_id="default_memory_policy",
                resource_type=ResourceType.MEMORY,
                target_utilization=0.75,
                scale_up_threshold=0.85,
                scale_down_threshold=0.45,
                min_capacity=100.0,
                max_capacity=10000.0,
                cooldown_period_seconds=300
            )
            
            await self.register_scaling_policy(memory_policy)
            
            logger.info("Default scaling policies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default policies: {e}")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                # Collect metrics for all resource types
                for resource_type in ResourceType:
                    try:
                        metrics = await self.resource_provider.get_current_metrics(resource_type)
                        
                        # Store in history
                        if resource_type not in self.metrics_history:
                            self.metrics_history[resource_type] = []
                        
                        self.metrics_history[resource_type].append(metrics)
                        
                        # Limit history size
                        max_entries = int(self._metrics_retention_hours * 3600 / self._monitoring_interval)
                        if len(self.metrics_history[resource_type]) > max_entries:
                            self.metrics_history[resource_type] = self.metrics_history[resource_type][-max_entries:]
                        
                    except Exception as e:
                        logger.debug(f"Could not collect metrics for {resource_type.value}: {e}")
                
                await asyncio.sleep(self._monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(30)
    
    async def _scaling_loop(self) -> None:
        """Background auto-scaling loop"""
        while not self._shutdown_event.is_set():
            try:
                for resource_type, policy in self.scaling_policies.items():
                    if not policy.enabled:
                        continue
                    
                    try:
                        # Get current metrics
                        metrics = await self.resource_provider.get_current_metrics(resource_type)
                        utilization = metrics.utilization_percentage / 100
                        
                        # Check if scaling is needed
                        if utilization > policy.scale_up_threshold:
                            await self.trigger_scaling(resource_type, ScalingDirection.UP)
                        elif utilization < policy.scale_down_threshold:
                            await self.trigger_scaling(resource_type, ScalingDirection.DOWN)
                        
                    except Exception as e:
                        logger.debug(f"Scaling evaluation error for {resource_type.value}: {e}")
                
                await asyncio.sleep(self._scaling_evaluation_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scaling loop error: {e}")
                await asyncio.sleep(60)
    
    async def _forecasting_loop(self) -> None:
        """Background capacity forecasting loop"""
        while not self._shutdown_event.is_set():
            try:
                for resource_type in ResourceType:
                    try:
                        forecast = await self.generate_capacity_forecast(resource_type, 24)
                        
                        # Log forecast if confidence is high enough
                        if forecast.confidence_level > 0.7:
                            logger.info(f"Capacity forecast for {resource_type.value}: "
                                      f"recommended action = {forecast.recommended_action.value}, "
                                      f"confidence = {forecast.confidence_level:.2f}")
                        
                    except Exception as e:
                        logger.debug(f"Forecasting error for {resource_type.value}: {e}")
                
                await asyncio.sleep(self._capacity_forecast_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Forecasting loop error: {e}")
                await asyncio.sleep(1800)  # 30 minutes
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Clean up expired allocations
                expired_allocations = []
                for allocation_id, allocation in self.allocations.items():
                    if allocation.expires_at and allocation.expires_at < current_time:
                        expired_allocations.append(allocation_id)
                
                for allocation_id in expired_allocations:
                    await self.deallocate_resources(allocation_id)
                    logger.info(f"Cleaned up expired allocation: {allocation_id}")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    # Context Manager Support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function
def create_resource_coordinator(resource_provider: Optional[ResourceProvider] = None, config: Optional[Dict[str, Any]] = None) -> ResourceCoordinator:
    """Factory function to create a Resource Coordinator"""
    return ResourceCoordinator(resource_provider, config)


# Example usage
async def main():
    """Example usage of Resource Coordinator"""
    async with create_resource_coordinator() as coordinator:
        # Register a resource pool
        cpu_pool = ResourcePool(
            pool_id="production_cpu",
            name="Production CPU Pool",
            resource_type=ResourceType.CPU,
            total_capacity=100.0,
            scaling_enabled=True
        )
        
        await coordinator.register_resource_pool(cpu_pool)
        
        # Create a resource allocation
        allocation = ResourceAllocation(
            allocation_id="test_allocation_1",
            service_id="content_service",
            resource_type=ResourceType.CPU,
            requested_amount=10.0,
            priority=5
        )
        
        # Allocate resources
        success = await coordinator.allocate_resources(allocation)
        print(f"Resource allocation successful: {success}")
        
        # Get current metrics
        metrics = await coordinator.get_resource_metrics(ResourceType.CPU)
        print(f"CPU metrics: {json.dumps(metrics, indent=2, default=str)}")
        
        # Wait a bit for monitoring
        await asyncio.sleep(5)
        
        # Get coordination status
        status = await coordinator.get_coordination_status()
        print(f"Coordination status: {json.dumps(status, indent=2, default=str)}")
        
        # Deallocate resources
        await coordinator.deallocate_resources(allocation.allocation_id)


if __name__ == "__main__":
    asyncio.run(main())