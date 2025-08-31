"""Resource Manager Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/resource_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Resource Management System
Responsibility: Intelligent resource allocation and optimization for workers
Technologies: ML Resource Prediction, Dynamic Allocation, Cost Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Resource monitoring → ML prediction → Dynamic allocation → 
Cost optimization → Performance tuning → Capacity planning → Auto-scaling
"""from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, NamedTuple
import logging
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import gc
import resource
import os
import docker
from kubernetes import client, config as k8s_config

from .crawler_worker import CrawlerWorker, WorkerStatus, WorkerConfig
from .worker_pool import WorkerPool, PoolStatus
from ...monitoring.performance_monitor import PerformanceMonitor
from ...ml.prediction.resource_predictor import ResourcePredictor
from ...utils.math_utils import MathUtils
from ...core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ResourceType(Enum):
    """Types of resources managed"""    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""    STATIC = "static"
    DYNAMIC = "dynamic"
    PREDICTIVE = "predictive"
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"


class ResourceStatus(Enum):
    """Resource availability status"""    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERALLOCATED = "overallocated"
    EXHAUSTED = "exhausted"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


@dataclass
class ResourceLimit:
    """Resource limit configuration"""    resource_type: ResourceType
    min_value: float
    max_value: float
    current_value: float
    unit: str
    soft_limit: float
    hard_limit: float
    auto_scale: bool = True
    priority: int = 1


@dataclass
class ResourceUsage:
    """Current resource usage metrics"""    resource_type: ResourceType
    current_usage: float
    peak_usage: float
    average_usage: float
    utilization_percentage: float
    timestamp: datetime
    worker_id: Optional[str] = None
    pool_id: Optional[str] = None


@dataclass
class ResourceAllocation:
    """Resource allocation record"""    allocation_id: str
    worker_id: str
    resource_type: ResourceType
    allocated_amount: float
    allocation_time: datetime
    expiry_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourcePrediction:
    """ML-based resource prediction"""    resource_type: ResourceType
    prediction_horizon: timedelta
    predicted_usage: float
    confidence_level: float
    prediction_time: datetime
    factors: Dict[str, float] = field(default_factory=dict)


class ResourceManager:
    """    Intelligent resource manager for worker system
    
    Features:
    - ML-based resource prediction
    - Dynamic allocation and deallocation
    - Cost optimization algorithms
    - Performance monitoring
    - Auto-scaling integration
    - Multi-tenant resource isolation
    """    def __init__(self, allocation_strategy: AllocationStrategy = AllocationStrategy.BALANCED):
        self.allocation_strategy = allocation_strategy
        self.resource_limits: Dict[ResourceType, ResourceLimit] = {}
        self.current_allocations: Dict[str, ResourceAllocation] = {}
        self.usage_history: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.predictions: Dict[ResourceType, ResourcePrediction] = {}
        
        # Components
        self.performance_monitor = PerformanceMonitor()
        self.resource_predictor = ResourcePredictor()
        self.math_utils = MathUtils()
        
        # System monitoring
        self.system_resources = {}
        self.container_stats = {}
        self.kubernetes_stats = {}
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        self.is_running = False
        
        # Thread pool for resource operations
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ResourceManager")
        
        # Initialize Docker client if available
        try:
            self.docker_client = docker.from_env()
        except Exception:
            self.docker_client = None
            
        # Initialize Kubernetes client if available
        try:
            k8s_config.load_incluster_config()
            self.k8s_client = client.CoreV1Api()
        except Exception:
            try:
                k8s_config.load_kube_config()
                self.k8s_client = client.CoreV1Api()
            except Exception:
                self.k8s_client = None

    async def start(self) -> bool:
        """Start resource manager"""        try:
            logger.info("🚀 Starting resource manager")
            
            # Initialize resource limits
            await self._initialize_resource_limits()
            
            # Start monitoring
            await self._start_monitoring()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            
            logger.info("✅ Resource manager started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start resource manager: {e}")
            return False

    async def stop(self) -> None:
        """Stop resource manager"""        try:
            logger.info("🛑 Stopping resource manager")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Shutdown executor
            self.executor.shutdown(wait=True, timeout=30)
            
            # Close Docker client
            if self.docker_client:
                self.docker_client.close()
            
            logger.info("✅ Resource manager stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping resource manager: {e}")

    async def allocate_resources(self, worker_id: str, required_resources: Dict[ResourceType, float],
                               priority: int = 1, timeout: int = 300) -> Dict[ResourceType, ResourceAllocation]:
        """Allocate resources to a worker"""        try:
            allocations = {}
            
            # Check resource availability
            availability = await self._check_resource_availability(required_resources)
            
            if not all(availability.values()):
                # Try to free up resources or scale
                await self._handle_resource_shortage(required_resources, priority)
                
                # Re-check availability
                availability = await self._check_resource_availability(required_resources)
                
                if not all(availability.values()):
                    raise Exception("Insufficient resources available")
            
            # Allocate each resource
            for resource_type, amount in required_resources.items():
                allocation = await self._allocate_single_resource(
                    worker_id, resource_type, amount, priority
                )
                allocations[resource_type] = allocation
            
            logger.info(f"✅ Resources allocated to worker {worker_id}: {list(required_resources.keys())}")
            return allocations
            
        except Exception as e:
            logger.error(f"❌ Failed to allocate resources to worker {worker_id}: {e}")
            
            # Rollback partial allocations
            for allocation in allocations.values():
                await self.deallocate_resources(allocation.allocation_id)
            
            raise

    async def deallocate_resources(self, allocation_id: str) -> bool:
        """Deallocate resources"""        try:
            allocation = self.current_allocations.get(allocation_id)
            if not allocation:
                logger.warning(f"⚠️ Allocation not found: {allocation_id}")
                return False
            
            # Free the resource
            await self._free_single_resource(allocation)
            
            # Remove from tracking
            del self.current_allocations[allocation_id]
            
            logger.info(f"✅ Resources deallocated: {allocation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deallocate resources {allocation_id}: {e}")
            return False

    async def get_resource_status(self) -> Dict[str, Any]:
        """Get comprehensive resource status"""        try:
            # Update current resource usage
            await self._update_resource_usage()
            
            # Get system resources
            system_info = await self._get_system_resource_info()
            
            # Calculate utilization
            utilization = await self._calculate_resource_utilization()
            
            # Get predictions
            predictions = await self._get_resource_predictions()
            
            # Get allocations summary
            allocations_summary = self._get_allocations_summary()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_resources": system_info,
                "resource_limits": {
                    rt.value: {
                        "min_value": limit.min_value,
                        "max_value": limit.max_value,
                        "current_value": limit.current_value,
                        "soft_limit": limit.soft_limit,
                        "hard_limit": limit.hard_limit,
                        "unit": limit.unit,
                        "auto_scale": limit.auto_scale
                    } for rt, limit in self.resource_limits.items()
                },
                "utilization": utilization,
                "predictions": predictions,
                "allocations": allocations_summary,
                "allocation_strategy": self.allocation_strategy.value,
                "is_running": self.is_running
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource status: {e}")
            return {"error": str(e)}

    async def optimize_allocation(self, target_metric: str = "cost") -> Dict[str, Any]:
        """Optimize resource allocation based on target metric"""        try:
            logger.info(f"🔄 Optimizing resource allocation for: {target_metric}")
            
            # Analyze current allocations
            analysis = await self._analyze_current_allocations()
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(analysis, target_metric)
            
            # Apply optimizations if safe
            applied_optimizations = await self._apply_optimizations(recommendations)
            
            result = {
                "optimization_target": target_metric,
                "analysis": analysis,
                "recommendations": recommendations,
                "applied_optimizations": applied_optimizations,
                "estimated_savings": self._calculate_estimated_savings(applied_optimizations),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Resource allocation optimization completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize allocation: {e}")
            return {"error": str(e)}

    async def predict_resource_needs(self, horizon_hours: int = 24) -> Dict[ResourceType, ResourcePrediction]:
        """Predict future resource needs using ML"""        try:
            predictions = {}
            
            for resource_type in ResourceType:
                if resource_type in self.usage_history and self.usage_history[resource_type]:
                    # Prepare historical data
                    historical_data = list(self.usage_history[resource_type])
                    
                    # Generate prediction
                    prediction = await self.resource_predictor.predict_resource_usage(
                        resource_type=resource_type,
                        historical_data=historical_data,
                        prediction_horizon=timedelta(hours=horizon_hours)
                    )
                    
                    predictions[resource_type] = prediction
            
            # Store predictions
            self.predictions = predictions
            
            logger.info(f"🔮 Generated resource predictions for {horizon_hours} hours")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Failed to predict resource needs: {e}")
            return {}

    async def handle_resource_alert(self, resource_type: ResourceType, 
                                  alert_type: str, current_value: float) -> bool:
        """Handle resource alert and take corrective action"""        try:
            logger.warning(f"⚠️ Resource alert: {resource_type.value} - {alert_type} - {current_value}")
            
            if alert_type == "high_usage":
                return await self._handle_high_usage_alert(resource_type, current_value)
            elif alert_type == "low_availability":
                return await self._handle_low_availability_alert(resource_type, current_value)
            elif alert_type == "allocation_failure":
                return await self._handle_allocation_failure_alert(resource_type, current_value)
            elif alert_type == "prediction_threshold":
                return await self._handle_prediction_threshold_alert(resource_type, current_value)
            else:
                logger.warning(f"⚠️ Unknown alert type: {alert_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to handle resource alert: {e}")
            return False

    async def _initialize_resource_limits(self) -> None:
        """Initialize resource limits based on system capabilities"""        try:
            # Get system information
            cpu_count = psutil.cpu_count()
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # CPU limits
            self.resource_limits[ResourceType.CPU] = ResourceLimit(
                resource_type=ResourceType.CPU,
                min_value=0.1,
                max_value=cpu_count,
                current_value=0.0,
                unit="cores",
                soft_limit=cpu_count * 0.8,
                hard_limit=cpu_count * 0.95
            )
            
            # Memory limits (in GB)
            memory_gb = memory_info.total / (1024**3)
            self.resource_limits[ResourceType.MEMORY] = ResourceLimit(
                resource_type=ResourceType.MEMORY,
                min_value=0.1,
                max_value=memory_gb,
                current_value=0.0,
                unit="GB",
                soft_limit=memory_gb * 0.8,
                hard_limit=memory_gb * 0.95
            )
            
            # Disk limits (in GB)
            disk_gb = disk_info.total / (1024**3)
            self.resource_limits[ResourceType.DISK] = ResourceLimit(
                resource_type=ResourceType.DISK,
                min_value=1.0,
                max_value=disk_gb,
                current_value=0.0,
                unit="GB",
                soft_limit=disk_gb * 0.8,
                hard_limit=disk_gb * 0.9
            )
            
            # Network limits (in Mbps)
            self.resource_limits[ResourceType.NETWORK] = ResourceLimit(
                resource_type=ResourceType.NETWORK,
                min_value=1.0,
                max_value=1000.0,  # Assume 1Gbps
                current_value=0.0,
                unit="Mbps",
                soft_limit=800.0,
                hard_limit=950.0
            )
            
            logger.info("✅ Resource limits initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize resource limits: {e}")
            raise

    async def _start_monitoring(self) -> None:
        """Start resource monitoring"""        try:
            # Initial resource usage update
            await self._update_resource_usage()
            
            logger.info("✅ Resource monitoring started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
            raise

    async def _start_background_tasks(self) -> None:
        """Start background resource management tasks"""        try:
            # Resource monitor
            monitor_task = asyncio.create_task(self._resource_monitor())
            self.background_tasks.add(monitor_task)
            
            # Resource predictor
            predictor_task = asyncio.create_task(self._resource_predictor_task())
            self.background_tasks.add(predictor_task)
            
            # Resource optimizer
            optimizer_task = asyncio.create_task(self._resource_optimizer_task())
            self.background_tasks.add(optimizer_task)
            
            # Cleanup task
            cleanup_task = asyncio.create_task(self._resource_cleanup_task())
            self.background_tasks.add(cleanup_task)
            
            logger.info("✅ Background resource tasks started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _check_resource_availability(self, required_resources: Dict[ResourceType, float]) -> Dict[ResourceType, bool]:
        """Check if required resources are available"""        try:
            availability = {}
            
            for resource_type, amount in required_resources.items():
                limit = self.resource_limits.get(resource_type)
                if not limit:
                    availability[resource_type] = False
                    continue
                
                # Calculate current allocated amount
                allocated_amount = sum(
                    alloc.allocated_amount for alloc in self.current_allocations.values()
                    if alloc.resource_type == resource_type
                )
                
                # Check if we can allocate more
                available_amount = limit.soft_limit - allocated_amount
                availability[resource_type] = amount <= available_amount
            
            return availability
            
        except Exception as e:
            logger.error(f"❌ Failed to check resource availability: {e}")
            return {rt: False for rt in required_resources.keys()}

    async def _allocate_single_resource(self, worker_id: str, resource_type: ResourceType, 
                                      amount: float, priority: int) -> ResourceAllocation:
        """Allocate a single resource"""        try:
            allocation_id = f"{worker_id}_{resource_type.value}_{int(time.time())}"
            
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                worker_id=worker_id,
                resource_type=resource_type,
                allocated_amount=amount,
                allocation_time=datetime.utcnow(),
                metadata={"priority": priority}
            )
            
            # Track allocation
            self.current_allocations[allocation_id] = allocation
            
            # Update resource limits
            limit = self.resource_limits[resource_type]
            limit.current_value += amount
            
            # Apply system-level allocation if needed
            await self._apply_system_allocation(allocation)
            
            return allocation
            
        except Exception as e:
            logger.error(f"❌ Failed to allocate single resource: {e}")
            raise

    async def _free_single_resource(self, allocation: ResourceAllocation) -> None:
        """Free a single resource allocation"""        try:
            # Update resource limits
            limit = self.resource_limits[allocation.resource_type]
            limit.current_value -= allocation.allocated_amount
            
            # Apply system-level deallocation if needed
            await self._apply_system_deallocation(allocation)
            
        except Exception as e:
            logger.error(f"❌ Failed to free single resource: {e}")
            raise

    async def _apply_system_allocation(self, allocation: ResourceAllocation) -> None:
        """Apply allocation at system level (Docker, Kubernetes, etc.)"""        try:
            if allocation.resource_type == ResourceType.CPU:
                await self._apply_cpu_allocation(allocation)
            elif allocation.resource_type == ResourceType.MEMORY:
                await self._apply_memory_allocation(allocation)
            # Add other resource types as needed
            
        except Exception as e:
            logger.error(f"❌ Failed to apply system allocation: {e}")

    async def _apply_system_deallocation(self, allocation: ResourceAllocation) -> None:
        """Apply deallocation at system level"""        try:
            if allocation.resource_type == ResourceType.CPU:
                await self._apply_cpu_deallocation(allocation)
            elif allocation.resource_type == ResourceType.MEMORY:
                await self._apply_memory_deallocation(allocation)
            # Add other resource types as needed
            
        except Exception as e:
            logger.error(f"❌ Failed to apply system deallocation: {e}")

    async def _apply_cpu_allocation(self, allocation: ResourceAllocation) -> None:
        """Apply CPU allocation using cgroups or container limits"""        try:
            # Docker container CPU limit
            if self.docker_client:
                # Implementation for Docker CPU limits
                pass
            
            # Kubernetes CPU limit
            if self.k8s_client:
                # Implementation for Kubernetes CPU limits
                pass
            
            # Process-level CPU affinity
            worker_pid = self._get_worker_pid(allocation.worker_id)
            if worker_pid:
                # Set CPU affinity
                process = psutil.Process(worker_pid)
                # Calculate CPU cores to assign
                cpu_cores = min(int(allocation.allocated_amount), psutil.cpu_count())
                if cpu_cores > 0:
                    process.cpu_affinity(list(range(cpu_cores)))
            
        except Exception as e:
            logger.error(f"❌ Failed to apply CPU allocation: {e}")

    async def _apply_memory_allocation(self, allocation: ResourceAllocation) -> None:
        """Apply memory allocation using cgroups or container limits"""        try:
            # Docker container memory limit
            if self.docker_client:
                # Implementation for Docker memory limits
                pass
            
            # Kubernetes memory limit
            if self.k8s_client:
                # Implementation for Kubernetes memory limits
                pass
            
            # Process-level memory monitoring
            worker_pid = self._get_worker_pid(allocation.worker_id)
            if worker_pid:
                # Set up memory monitoring for the process
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to apply memory allocation: {e}")

    async def _apply_cpu_deallocation(self, allocation: ResourceAllocation) -> None:
        """Remove CPU allocation constraints"""        try:
            worker_pid = self._get_worker_pid(allocation.worker_id)
            if worker_pid:
                process = psutil.Process(worker_pid)
                # Reset CPU affinity to all cores
                process.cpu_affinity(list(range(psutil.cpu_count())))
            
        except Exception as e:
            logger.error(f"❌ Failed to apply CPU deallocation: {e}")

    async def _apply_memory_deallocation(self, allocation: ResourceAllocation) -> None:
        """Remove memory allocation constraints"""        try:
            # Remove memory constraints
            # Implementation depends on the system
            pass
            
        except Exception as e:
            logger.error(f"❌ Failed to apply memory deallocation: {e}")

    def _get_worker_pid(self, worker_id: str) -> Optional[int]:
        """Get process ID for a worker"""        try:
            # This would need to be implemented based on how workers are tracked
            # For now, return None
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get worker PID: {e}")
            return None

    async def _update_resource_usage(self) -> None:
        """Update current resource usage metrics"""        try:
            current_time = datetime.utcnow()
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_usage_record = ResourceUsage(
                resource_type=ResourceType.CPU,
                current_usage=cpu_usage,
                peak_usage=cpu_usage,  # Would track over time
                average_usage=cpu_usage,  # Would calculate from history
                utilization_percentage=cpu_usage,
                timestamp=current_time
            )
            self.usage_history[ResourceType.CPU].append(cpu_usage_record)
            
            # Memory usage
            memory_info = psutil.virtual_memory()
            memory_usage_gb = (memory_info.total - memory_info.available) / (1024**3)
            memory_usage_record = ResourceUsage(
                resource_type=ResourceType.MEMORY,
                current_usage=memory_usage_gb,
                peak_usage=memory_usage_gb,
                average_usage=memory_usage_gb,
                utilization_percentage=memory_info.percent,
                timestamp=current_time
            )
            self.usage_history[ResourceType.MEMORY].append(memory_usage_record)
            
            # Disk usage
            disk_info = psutil.disk_usage('/')
            disk_usage_gb = disk_info.used / (1024**3)
            disk_usage_record = ResourceUsage(
                resource_type=ResourceType.DISK,
                current_usage=disk_usage_gb,
                peak_usage=disk_usage_gb,
                average_usage=disk_usage_gb,
                utilization_percentage=(disk_info.used / disk_info.total) * 100,
                timestamp=current_time
            )
            self.usage_history[ResourceType.DISK].append(disk_usage_record)
            
            # Network usage
            network_info = psutil.net_io_counters()
            # This is a simplified calculation
            network_usage_mbps = 0.0  # Would need proper calculation
            network_usage_record = ResourceUsage(
                resource_type=ResourceType.NETWORK,
                current_usage=network_usage_mbps,
                peak_usage=network_usage_mbps,
                average_usage=network_usage_mbps,
                utilization_percentage=0.0,  # Would calculate based on bandwidth
                timestamp=current_time
            )
            self.usage_history[ResourceType.NETWORK].append(network_usage_record)
            
        except Exception as e:
            logger.error(f"❌ Failed to update resource usage: {e}")

    async def _get_system_resource_info(self) -> Dict[str, Any]:
        """Get comprehensive system resource information"""        try:
            # Basic system info
            cpu_count = psutil.cpu_count()
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            network_info = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "cores": cpu_count,
                    "usage_percent": cpu_usage,
                    "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
                },
                "memory": {
                    "total_gb": memory_info.total / (1024**3),
                    "available_gb": memory_info.available / (1024**3),
                    "used_gb": (memory_info.total - memory_info.available) / (1024**3),
                    "usage_percent": memory_info.percent
                },
                "disk": {
                    "total_gb": disk_info.total / (1024**3),
                    "used_gb": disk_info.used / (1024**3),
                    "free_gb": disk_info.free / (1024**3),
                    "usage_percent": (disk_info.used / disk_info.total) * 100
                },
                "network": {
                    "bytes_sent": network_info.bytes_sent,
                    "bytes_recv": network_info.bytes_recv,
                    "packets_sent": network_info.packets_sent,
                    "packets_recv": network_info.packets_recv
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get system resource info: {e}")
            return {}

    async def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization percentages"""        try:
            utilization = {}
            
            for resource_type, limit in self.resource_limits.items():
                if limit.max_value > 0:
                    utilization[resource_type.value] = (limit.current_value / limit.max_value) * 100
                else:
                    utilization[resource_type.value] = 0.0
            
            return utilization
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate resource utilization: {e}")
            return {}

    async def _get_resource_predictions(self) -> Dict[str, Any]:
        """Get current resource predictions"""        try:
            predictions_dict = {}
            
            for resource_type, prediction in self.predictions.items():
                predictions_dict[resource_type.value] = {
                    "predicted_usage": prediction.predicted_usage,
                    "confidence_level": prediction.confidence_level,
                    "prediction_horizon_hours": prediction.prediction_horizon.total_seconds() / 3600,
                    "prediction_time": prediction.prediction_time.isoformat(),
                    "factors": prediction.factors
                }
            
            return predictions_dict
            
        except Exception as e:
            logger.error(f"❌ Failed to get resource predictions: {e}")
            return {}

    def _get_allocations_summary(self) -> Dict[str, Any]:
        """Get summary of current allocations"""        try:
            summary = {
                "total_allocations": len(self.current_allocations),
                "by_resource_type": defaultdict(int),
                "by_worker": defaultdict(int),
                "total_allocated": defaultdict(float)
            }
            
            for allocation in self.current_allocations.values():
                summary["by_resource_type"][allocation.resource_type.value] += 1
                summary["by_worker"][allocation.worker_id] += 1
                summary["total_allocated"][allocation.resource_type.value] += allocation.allocated_amount
            
            return dict(summary)
            
        except Exception as e:
            logger.error(f"❌ Failed to get allocations summary: {e}")
            return {}

    async def _resource_monitor(self) -> None:
        """Background resource monitoring task"""        while not self.shutdown_event.is_set():
            try:
                await self._update_resource_usage()
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Resource monitor error: {e}")
                await asyncio.sleep(60)

    async def _resource_predictor_task(self) -> None:
        """Background resource prediction task"""        while not self.shutdown_event.is_set():
            try:
                await self.predict_resource_needs(horizon_hours=24)
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"❌ Resource predictor error: {e}")
                await asyncio.sleep(1800)

    async def _resource_optimizer_task(self) -> None:
        """Background resource optimization task"""        while not self.shutdown_event.is_set():
            try:
                await self.optimize_allocation(target_metric="balanced")
                await asyncio.sleep(1800)  # Optimize every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Resource optimizer error: {e}")
                await asyncio.sleep(3600)

    async def _resource_cleanup_task(self) -> None:
        """Background resource cleanup task"""        while not self.shutdown_event.is_set():
            try:
                await self._cleanup_expired_allocations()
                await self._cleanup_old_usage_data()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Resource cleanup error: {e}")
                await asyncio.sleep(600)

    async def _cleanup_expired_allocations(self) -> None:
        """Clean up expired resource allocations"""        try:
            current_time = datetime.utcnow()
            expired_allocations = []
            
            for allocation_id, allocation in self.current_allocations.items():
                if allocation.expiry_time and allocation.expiry_time < current_time:
                    expired_allocations.append(allocation_id)
            
            for allocation_id in expired_allocations:
                await self.deallocate_resources(allocation_id)
                logger.info(f"🧹 Cleaned up expired allocation: {allocation_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired allocations: {e}")

    async def _cleanup_old_usage_data(self) -> None:
        """Clean up old usage data to prevent memory growth"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            for resource_type in self.usage_history:
                # Remove old entries
                while (self.usage_history[resource_type] and 
                       self.usage_history[resource_type][0].timestamp < cutoff_time):
                    self.usage_history[resource_type].popleft()
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old usage data: {e}")

    async def _handle_resource_shortage(self, required_resources: Dict[ResourceType, float], priority: int) -> None:
        """Handle resource shortage by freeing or scaling resources"""        try:
            logger.warning(f"⚠️ Handling resource shortage for priority {priority}")
            
            # Try to free up resources from lower priority allocations
            freed_resources = await self._free_lower_priority_resources(required_resources, priority)
            
            if not freed_resources:
                # Try to scale up resources if possible
                await self._scale_up_resources(required_resources)
            
        except Exception as e:
            logger.error(f"❌ Failed to handle resource shortage: {e}")

    async def _free_lower_priority_resources(self, required_resources: Dict[ResourceType, float], 
                                           min_priority: int) -> bool:
        """Free resources from lower priority allocations"""        try:
            freed_any = False
            
            for resource_type, required_amount in required_resources.items():
                # Find lower priority allocations
                lower_priority_allocations = [
                    (alloc_id, alloc) for alloc_id, alloc in self.current_allocations.items()
                    if (alloc.resource_type == resource_type and 
                        alloc.metadata.get('priority', 0) < min_priority)
                ]
                
                # Sort by priority (lowest first)
                lower_priority_allocations.sort(key=lambda x: x[1].metadata.get('priority', 0))
                
                freed_amount = 0.0
                for alloc_id, allocation in lower_priority_allocations:
                    if freed_amount >= required_amount:
                        break
                    
                    await self.deallocate_resources(alloc_id)
                    freed_amount += allocation.allocated_amount
                    freed_any = True
                    
                    logger.info(f"🔄 Freed {allocation.allocated_amount} {resource_type.value} from worker {allocation.worker_id}")
            
            return freed_any
            
        except Exception as e:
            logger.error(f"❌ Failed to free lower priority resources: {e}")
            return False

    async def _scale_up_resources(self, required_resources: Dict[ResourceType, float]) -> None:
        """Scale up resources if possible"""        try:
            # Implementation would depend on the infrastructure
            # For example, scaling Kubernetes pods, adding Docker containers, etc.
            logger.info(f"📈 Attempting to scale up resources: {list(required_resources.keys())}")
            
            # Placeholder for actual scaling logic
            
        except Exception as e:
            logger.error(f"❌ Failed to scale up resources: {e}")

    async def _analyze_current_allocations(self) -> Dict[str, Any]:
        """Analyze current resource allocations for optimization"""        try:
            # Placeholder for allocation analysis
            return {
                "total_allocations": len(self.current_allocations),
                "utilization_efficiency": 0.0,
                "cost_efficiency": 0.0,
                "recommendations_count": 0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze allocations: {e}")
            return {}

    async def _generate_optimization_recommendations(self, analysis: Dict[str, Any], 
                                                   target_metric: str) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""        try:
            # Placeholder for optimization recommendations
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
            return []

    async def _apply_optimizations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply safe optimization recommendations"""        try:
            applied = []
            
            for recommendation in recommendations:
                if recommendation.get('safety_score', 0) > 0.8:
                    # Apply safe optimizations only
                    # Implementation would depend on recommendation type
                    applied.append(recommendation)
            
            return applied
            
        except Exception as e:
            logger.error(f"❌ Failed to apply optimizations: {e}")
            return []

    def _calculate_estimated_savings(self, applied_optimizations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate estimated savings from optimizations"""        try:
            return {
                "cost_savings_percent": 0.0,
                "performance_improvement_percent": 0.0,
                "resource_efficiency_improvement_percent": 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate estimated savings: {e}")
            return {}

    async def _handle_high_usage_alert(self, resource_type: ResourceType, current_value: float) -> bool:
        """Handle high resource usage alert"""        try:
            # Scale up if possible
            await self._scale_up_resources({resource_type: current_value * 0.2})
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle high usage alert: {e}")
            return False

    async def _handle_low_availability_alert(self, resource_type: ResourceType, current_value: float) -> bool:
        """Handle low resource availability alert"""        try:
            # Free up resources from low priority tasks
            await self._free_lower_priority_resources({resource_type: current_value}, priority=1)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle low availability alert: {e}")
            return False

    async def _handle_allocation_failure_alert(self, resource_type: ResourceType, current_value: float) -> bool:
        """Handle allocation failure alert"""        try:
            # Try emergency resource freeing
            await self._emergency_resource_cleanup(resource_type)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle allocation failure alert: {e}")
            return False

    async def _handle_prediction_threshold_alert(self, resource_type: ResourceType, current_value: float) -> bool:
        """Handle prediction threshold alert"""        try:
            # Proactively scale based on prediction
            await self._proactive_scaling(resource_type, current_value)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to handle prediction threshold alert: {e}")
            return False

    async def _emergency_resource_cleanup(self, resource_type: ResourceType) -> None:
        """Emergency resource cleanup"""        try:
            # Force garbage collection
            gc.collect()
            
            # Clear caches
            # Implementation specific to resource type
            
            logger.warning(f"🚨 Emergency cleanup performed for {resource_type.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed emergency resource cleanup: {e}")

    async def _proactive_scaling(self, resource_type: ResourceType, predicted_value: float) -> None:
        """Proactive scaling based on predictions"""        try:
            # Scale up before hitting limits
            scale_amount = predicted_value * 0.1  # Scale by 10% of predicted need
            await self._scale_up_resources({resource_type: scale_amount})
            
            logger.info(f"📈 Proactive scaling triggered for {resource_type.value}: {scale_amount}")
            
        except Exception as e:
            logger.error(f"❌ Failed proactive scaling: {e}")


# Resource manager factory and singleton
_resource_manager_instance: Optional[ResourceManager] = None


def get_resource_manager(allocation_strategy: AllocationStrategy = AllocationStrategy.BALANCED) -> ResourceManager:
    """Get or create resource manager singleton"""    global _resource_manager_instance
    
    if _resource_manager_instance is None:
        _resource_manager_instance = ResourceManager(allocation_strategy)
    
    return _resource_manager_instance


async def initialize_resource_manager(allocation_strategy: AllocationStrategy = AllocationStrategy.BALANCED) -> bool:
    """Initialize global resource manager"""    try:
        manager = get_resource_manager(allocation_strategy)
        return await manager.start()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize resource manager: {e}")
        return False


async def shutdown_resource_manager() -> None:
    """Shutdown global resource manager"""    global _resource_manager_instance
    
    if _resource_manager_instance:
        await _resource_manager_instance.stop()
        _resource_manager_instance = None
