"""
GPU Resource Manager - AI/ML Pipeline Infrastructure
Enterprise GPU hardware optimization and resource allocation with intelligent workload distribution.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: EXCLUSIVE INTELLECTUAL PROPERTY - Fahed Mlaiel
WARNING: Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import numpy as np
import psutil
import GPUtil
import pynvml
import redis
import boto3
from kubernetes import client, config as k8s_config
import docker
import subprocess
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import nvidia_ml_py3 as nvml


class GPUType(Enum):
    """GPU hardware types"""
    V100 = "V100"
    A100 = "A100"
    H100 = "H100"
    RTX_3090 = "RTX_3090"
    RTX_4090 = "RTX_4090"
    T4 = "T4"
    K80 = "K80"
    P100 = "P100"
    UNKNOWN = "UNKNOWN"


class WorkloadType(Enum):
    """ML workload types for GPU optimization"""
    TRAINING = "training"
    INFERENCE = "inference"
    BATCH_INFERENCE = "batch_inference"
    FINE_TUNING = "fine_tuning"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    DATA_PREPROCESSING = "data_preprocessing"
    MODEL_EVALUATION = "model_evaluation"
    DISTRIBUTED_TRAINING = "distributed_training"


class ResourceStatus(Enum):
    """GPU resource status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class GPUDevice:
    """GPU device information"""
    device_id: str
    gpu_index: int
    gpu_type: GPUType
    total_memory_mb: int
    available_memory_mb: int
    utilization_percent: float
    temperature_celsius: float
    power_usage_watts: float
    compute_capability: tuple[int, int]
    node_id: str
    status: ResourceStatus
    current_workload: Optional[str] = None
    allocated_to: Optional[str] = None
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


@dataclass
class GPUNode:
    """GPU node cluster information"""
    node_id: str
    hostname: str
    ip_address: str
    total_gpus: int
    available_gpus: int
    gpu_devices: List[GPUDevice]
    
    # Node resources
    total_cpu_cores: int
    available_cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    
    # Network and storage
    network_bandwidth_gbps: float
    storage_type: str
    storage_capacity_gb: float
    
    # Status and health
    status: ResourceStatus
    health_score: float
    last_heartbeat: datetime
    node_metrics: Dict[str, Any]
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()


@dataclass
class ResourceRequest:
    """GPU resource allocation request"""
    request_id: str
    workload_id: str
    workload_type: WorkloadType
    
    # GPU requirements
    gpu_count: int
    min_gpu_memory_mb: int
    preferred_gpu_types: List[GPUType]
    
    # Compute requirements
    cpu_cores: float
    memory_gb: float
    
    # Performance requirements
    max_latency_ms: Optional[float] = None
    min_throughput_ops_sec: Optional[float] = None
    
    # Scheduling preferences
    priority: int = 1  # 1=low, 5=high
    max_wait_time: timedelta = timedelta(hours=1)
    preemptible: bool = False
    multi_node: bool = False
    
    # Resource affinity
    node_affinity: Optional[List[str]] = None
    anti_affinity: Optional[List[str]] = None
    
    requested_at: datetime = None
    requested_by: str = None
    
    def __post_init__(self):
        if self.requested_at is None:
            self.requested_at = datetime.utcnow()


@dataclass
class ResourceAllocation:
    """GPU resource allocation result"""
    allocation_id: str
    request_id: str
    workload_id: str
    
    # Allocated resources
    allocated_gpus: List[GPUDevice]
    allocated_nodes: List[str]
    total_gpu_memory_mb: int
    
    # Allocation metadata
    allocation_strategy: str
    estimated_performance: Dict[str, float]
    cost_estimate: float
    
    # Lifecycle
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    
    # Monitoring
    usage_metrics: Dict[str, Any] = None
    performance_metrics: Dict[str, Any] = None


class GPUResourceManager:
    """Enterprise GPU resource management and optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        self.logger = self._setup_logging()
        
        # Resource state
        self.gpu_nodes: Dict[str, GPUNode] = {}
        self.gpu_devices: Dict[str, GPUDevice] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.pending_requests: queue.PriorityQueue = queue.PriorityQueue()
        
        # Monitoring and metrics
        self.resource_monitor = GPUResourceMonitor(config)
        self.performance_optimizer = GPUPerformanceOptimizer(config)
        self.workload_predictor = WorkloadPredictor(config)
        self.cost_optimizer = CostOptimizer(config)
        
        # Scheduling
        self.scheduler = GPUScheduler(config)
        self.load_balancer = GPULoadBalancer(config)
        
        # Initialize NVIDIA ML
        try:
            pynvml.nvmlInit()
            self.nvml_initialized = True
        except:
            self.nvml_initialized = False
            self.logger.warning("NVIDIA ML not available")
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for GPU resource management"""
        logger = logging.getLogger('gpu_resource_manager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _start_background_tasks(self) -> None:
        """Start background monitoring and management tasks"""
        # Resource discovery and monitoring
        asyncio.create_task(self._discover_gpu_resources())
        asyncio.create_task(self._monitor_gpu_resources())
        
        # Request processing
        asyncio.create_task(self._process_resource_requests())
        
        # Optimization and cleanup
        asyncio.create_task(self._optimize_resource_allocation())
        asyncio.create_task(self._cleanup_expired_allocations())
        
        self.logger.info("Started GPU resource manager background tasks")
    
    async def _discover_gpu_resources(self) -> None:
        """Discover available GPU resources in the cluster"""
        while True:
            try:
                # Discover local GPUs
                await self._discover_local_gpus()
                
                # Discover Kubernetes GPU nodes
                if self.config.get('kubernetes_enabled'):
                    await self._discover_kubernetes_gpus()
                
                # Discover cloud GPU instances
                if self.config.get('cloud_discovery_enabled'):
                    await self._discover_cloud_gpus()
                
                await asyncio.sleep(300)  # Discover every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error discovering GPU resources: {e}")
                await asyncio.sleep(60)
    
    async def _discover_local_gpus(self) -> None:
        """Discover local GPU devices"""
        try:
            if not self.nvml_initialized:
                return
            
            device_count = pynvml.nvmlDeviceGetCount()
            local_node_id = f"local-{psutil.hostname()}"
            
            gpu_devices = []
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get device info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                
                # Determine GPU type
                gpu_type = self._identify_gpu_type(name)
                
                device = GPUDevice(
                    device_id=f"{local_node_id}-gpu-{i}",
                    gpu_index=i,
                    gpu_type=gpu_type,
                    total_memory_mb=memory_info.total // (1024 * 1024),
                    available_memory_mb=(memory_info.total - memory_info.used) // (1024 * 1024),
                    utilization_percent=utilization.gpu,
                    temperature_celsius=temperature,
                    power_usage_watts=power_usage,
                    compute_capability=(0, 0),  # Would get from CUDA
                    node_id=local_node_id,
                    status=ResourceStatus.AVAILABLE if utilization.gpu < 80 else ResourceStatus.BUSY
                )
                
                gpu_devices.append(device)
                self.gpu_devices[device.device_id] = device
            
            # Update or create node
            if local_node_id not in self.gpu_nodes:
                node = GPUNode(
                    node_id=local_node_id,
                    hostname=psutil.hostname(),
                    ip_address="127.0.0.1",
                    total_gpus=device_count,
                    available_gpus=sum(1 for d in gpu_devices if d.status == ResourceStatus.AVAILABLE),
                    gpu_devices=gpu_devices,
                    total_cpu_cores=psutil.cpu_count(),
                    available_cpu_cores=psutil.cpu_count(),
                    total_memory_gb=psutil.virtual_memory().total / (1024**3),
                    available_memory_gb=psutil.virtual_memory().available / (1024**3),
                    network_bandwidth_gbps=10.0,  # Default
                    storage_type="SSD",
                    storage_capacity_gb=100.0,  # Default
                    status=ResourceStatus.AVAILABLE,
                    health_score=1.0,
                    node_metrics={}
                )
                self.gpu_nodes[local_node_id] = node
            else:
                # Update existing node
                self.gpu_nodes[local_node_id].gpu_devices = gpu_devices
                self.gpu_nodes[local_node_id].available_gpus = sum(
                    1 for d in gpu_devices if d.status == ResourceStatus.AVAILABLE
                )
                self.gpu_nodes[local_node_id].last_heartbeat = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error discovering local GPUs: {e}")
    
    def _identify_gpu_type(self, gpu_name: str) -> GPUType:
        """Identify GPU type from device name"""
        gpu_name_lower = gpu_name.lower()
        
        if 'v100' in gpu_name_lower:
            return GPUType.V100
        elif 'a100' in gpu_name_lower:
            return GPUType.A100
        elif 'h100' in gpu_name_lower:
            return GPUType.H100
        elif 'rtx 3090' in gpu_name_lower or '3090' in gpu_name_lower:
            return GPUType.RTX_3090
        elif 'rtx 4090' in gpu_name_lower or '4090' in gpu_name_lower:
            return GPUType.RTX_4090
        elif 't4' in gpu_name_lower:
            return GPUType.T4
        elif 'k80' in gpu_name_lower:
            return GPUType.K80
        elif 'p100' in gpu_name_lower:
            return GPUType.P100
        else:
            return GPUType.UNKNOWN
    
    async def _discover_kubernetes_gpus(self) -> None:
        """Discover GPU nodes in Kubernetes cluster"""
        try:
            v1 = client.CoreV1Api()
            
            # Get all nodes with GPU resources
            nodes = v1.list_node()
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                # Check if node has GPU resources
                allocatable = node.status.allocatable or {}
                gpu_count = int(allocatable.get('nvidia.com/gpu', 0))
                
                if gpu_count > 0:
                    # Create node representation
                    gpu_devices = []
                    for i in range(gpu_count):
                        device = GPUDevice(
                            device_id=f"{node_name}-gpu-{i}",
                            gpu_index=i,
                            gpu_type=GPUType.UNKNOWN,  # Would need to query actual device
                            total_memory_mb=16384,  # Default, would query actual
                            available_memory_mb=16384,
                            utilization_percent=0.0,
                            temperature_celsius=0.0,
                            power_usage_watts=0.0,
                            compute_capability=(0, 0),
                            node_id=node_name,
                            status=ResourceStatus.AVAILABLE
                        )
                        gpu_devices.append(device)
                        self.gpu_devices[device.device_id] = device
                    
                    # Get node addresses
                    addresses = node.status.addresses or []
                    internal_ip = next(
                        (addr.address for addr in addresses if addr.type == 'InternalIP'),
                        '0.0.0.0'
                    )
                    
                    k8s_node = GPUNode(
                        node_id=node_name,
                        hostname=node_name,
                        ip_address=internal_ip,
                        total_gpus=gpu_count,
                        available_gpus=gpu_count,
                        gpu_devices=gpu_devices,
                        total_cpu_cores=int(allocatable.get('cpu', '0').rstrip('m')) // 1000,
                        available_cpu_cores=int(allocatable.get('cpu', '0').rstrip('m')) // 1000,
                        total_memory_gb=int(allocatable.get('memory', '0').rstrip('Ki')) / (1024 * 1024),
                        available_memory_gb=int(allocatable.get('memory', '0').rstrip('Ki')) / (1024 * 1024),
                        network_bandwidth_gbps=10.0,
                        storage_type="SSD",
                        storage_capacity_gb=100.0,
                        status=ResourceStatus.AVAILABLE,
                        health_score=1.0,
                        node_metrics={}
                    )
                    
                    self.gpu_nodes[node_name] = k8s_node
            
        except Exception as e:
            self.logger.error(f"Error discovering Kubernetes GPUs: {e}")
    
    async def _discover_cloud_gpus(self) -> None:
        """Discover cloud GPU instances (AWS, GCP, Azure)"""
        # Implementation for cloud GPU discovery
        pass
    
    async def _monitor_gpu_resources(self) -> None:
        """Monitor GPU resource utilization and health"""
        while True:
            try:
                for device_id, device in self.gpu_devices.items():
                    await self._update_device_metrics(device)
                
                # Update node health scores
                for node in self.gpu_nodes.values():
                    await self._update_node_health(node)
                
                # Store metrics in Redis
                await self._store_resource_metrics()
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring GPU resources: {e}")
                await asyncio.sleep(60)
    
    async def _update_device_metrics(self, device: GPUDevice) -> None:
        """Update device utilization and health metrics"""
        try:
            if device.node_id.startswith('local-') and self.nvml_initialized:
                handle = pynvml.nvmlDeviceGetHandleByIndex(device.gpu_index)
                
                # Update metrics
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                
                device.available_memory_mb = (memory_info.total - memory_info.used) // (1024 * 1024)
                device.utilization_percent = utilization.gpu
                device.temperature_celsius = temperature
                device.power_usage_watts = power_usage
                device.last_updated = datetime.utcnow()
                
                # Update status based on utilization
                if device.utilization_percent > 90:
                    device.status = ResourceStatus.BUSY
                elif device.allocated_to:
                    device.status = ResourceStatus.ALLOCATED
                else:
                    device.status = ResourceStatus.AVAILABLE
            
        except Exception as e:
            self.logger.error(f"Error updating device metrics for {device.device_id}: {e}")
    
    async def _update_node_health(self, node: GPUNode) -> None:
        """Update node health score based on various factors"""
        try:
            health_factors = []
            
            # GPU health
            gpu_health = 0.0
            for device in node.gpu_devices:
                device_health = 1.0
                
                # Temperature factor (penalty for high temperatures)
                if device.temperature_celsius > 80:
                    device_health *= 0.8
                elif device.temperature_celsius > 70:
                    device_health *= 0.9
                
                # Utilization stability factor
                if device.utilization_percent > 95:
                    device_health *= 0.85
                
                gpu_health += device_health
            
            if node.gpu_devices:
                gpu_health /= len(node.gpu_devices)
            
            health_factors.append(gpu_health)
            
            # Network connectivity (simplified)
            network_health = 1.0 if (datetime.utcnow() - node.last_heartbeat).seconds < 120 else 0.5
            health_factors.append(network_health)
            
            # Resource availability
            resource_health = (node.available_gpus / node.total_gpus) * 0.5 + 0.5
            health_factors.append(resource_health)
            
            # Calculate overall health score
            node.health_score = sum(health_factors) / len(health_factors)
            
        except Exception as e:
            self.logger.error(f"Error updating node health for {node.node_id}: {e}")
    
    async def request_gpu_resources(self, request: ResourceRequest) -> str:
        """Request GPU resources for a workload"""
        try:
            # Validate request
            if not self._validate_resource_request(request):
                raise ValueError("Invalid resource request")
            
            # Add to pending requests queue
            priority_score = self._calculate_request_priority(request)
            self.pending_requests.put((priority_score, request.requested_at, request))
            
            # Store request in Redis
            await self._store_resource_request(request)
            
            self.logger.info(f"Received resource request: {request.request_id}")
            return request.request_id
            
        except Exception as e:
            self.logger.error(f"Error processing resource request: {e}")
            raise
    
    def _validate_resource_request(self, request: ResourceRequest) -> bool:
        """Validate resource request parameters"""
        if request.gpu_count <= 0:
            return False
        
        if request.min_gpu_memory_mb <= 0:
            return False
        
        if request.cpu_cores <= 0:
            return False
        
        if request.memory_gb <= 0:
            return False
        
        return True
    
    def _calculate_request_priority(self, request: ResourceRequest) -> int:
        """Calculate request priority score for queue ordering"""
        base_priority = request.priority * 1000
        
        # Age factor (older requests get higher priority)
        age_minutes = (datetime.utcnow() - request.requested_at).total_seconds() / 60
        age_bonus = min(age_minutes * 10, 500)
        
        # Resource requirement factor (smaller requests get slight priority)
        resource_factor = max(0, 100 - request.gpu_count * 10)
        
        return int(base_priority + age_bonus + resource_factor)
    
    async def _process_resource_requests(self) -> None:
        """Process pending resource requests"""
        while True:
            try:
                if not self.pending_requests.empty():
                    _, _, request = self.pending_requests.get()
                    
                    # Try to allocate resources
                    allocation = await self._allocate_resources(request)
                    
                    if allocation:
                        self.active_allocations[allocation.allocation_id] = allocation
                        await self._store_resource_allocation(allocation)
                        
                        self.logger.info(f"Allocated resources for request: {request.request_id}")
                    else:
                        # Check if request has expired
                        if datetime.utcnow() - request.requested_at > request.max_wait_time:
                            self.logger.warning(f"Request {request.request_id} expired")
                        else:
                            # Put back in queue for retry
                            self.pending_requests.put((
                                self._calculate_request_priority(request),
                                request.requested_at,
                                request
                            ))
                
                await asyncio.sleep(5)  # Process requests every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error processing resource requests: {e}")
                await asyncio.sleep(10)
    
    async def _allocate_resources(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate GPU resources for a request"""
        try:
            # Find suitable GPUs
            suitable_gpus = await self._find_suitable_gpus(request)
            
            if len(suitable_gpus) < request.gpu_count:
                return None  # Not enough resources available
            
            # Select optimal GPUs using scheduling strategy
            selected_gpus = await self.scheduler.select_optimal_gpus(
                suitable_gpus, request
            )
            
            if not selected_gpus:
                return None
            
            # Mark GPUs as allocated
            allocated_nodes = set()
            for gpu in selected_gpus:
                gpu.status = ResourceStatus.ALLOCATED
                gpu.allocated_to = request.workload_id
                gpu.current_workload = request.workload_type.value
                allocated_nodes.add(gpu.node_id)
            
            # Create allocation
            allocation = ResourceAllocation(
                allocation_id=str(uuid.uuid4()),
                request_id=request.request_id,
                workload_id=request.workload_id,
                allocated_gpus=selected_gpus,
                allocated_nodes=list(allocated_nodes),
                total_gpu_memory_mb=sum(gpu.available_memory_mb for gpu in selected_gpus),
                allocation_strategy="optimal_placement",
                estimated_performance=await self._estimate_performance(selected_gpus, request),
                cost_estimate=await self.cost_optimizer.calculate_cost(selected_gpus, request),
                allocated_at=datetime.utcnow()
            )
            
            return allocation
            
        except Exception as e:
            self.logger.error(f"Error allocating resources: {e}")
            return None
    
    async def _find_suitable_gpus(self, request: ResourceRequest) -> List[GPUDevice]:
        """Find GPUs that meet the request requirements"""
        suitable_gpus = []
        
        for device in self.gpu_devices.values():
            # Check availability
            if device.status != ResourceStatus.AVAILABLE:
                continue
            
            # Check memory requirement
            if device.available_memory_mb < request.min_gpu_memory_mb:
                continue
            
            # Check GPU type preference
            if request.preferred_gpu_types and device.gpu_type not in request.preferred_gpu_types:
                continue
            
            # Check node affinity
            if request.node_affinity and device.node_id not in request.node_affinity:
                continue
            
            # Check anti-affinity
            if request.anti_affinity and device.node_id in request.anti_affinity:
                continue
            
            # Check node health
            node = self.gpu_nodes.get(device.node_id)
            if not node or node.health_score < 0.7:
                continue
            
            suitable_gpus.append(device)
        
        return suitable_gpus
    
    async def _estimate_performance(
        self,
        allocated_gpus: List[GPUDevice],
        request: ResourceRequest
    ) -> Dict[str, float]:
        """Estimate performance for allocated resources"""
        # Use workload predictor to estimate performance
        return await self.workload_predictor.predict_performance(
            allocated_gpus, request.workload_type
        )
    
    async def release_gpu_resources(self, allocation_id: str) -> bool:
        """Release allocated GPU resources"""
        try:
            allocation = self.active_allocations.get(allocation_id)
            if not allocation:
                return False
            
            # Release GPUs
            for gpu in allocation.allocated_gpus:
                gpu.status = ResourceStatus.AVAILABLE
                gpu.allocated_to = None
                gpu.current_workload = None
            
            # Update allocation
            allocation.released_at = datetime.utcnow()
            
            # Remove from active allocations
            del self.active_allocations[allocation_id]
            
            # Store final allocation state
            await self._store_resource_allocation(allocation)
            
            self.logger.info(f"Released GPU resources for allocation: {allocation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error releasing GPU resources: {e}")
            return False
    
    async def get_resource_status(self) -> Dict[str, Any]:
        """Get current cluster resource status"""
        total_gpus = len(self.gpu_devices)
        available_gpus = sum(1 for d in self.gpu_devices.values() if d.status == ResourceStatus.AVAILABLE)
        allocated_gpus = sum(1 for d in self.gpu_devices.values() if d.status == ResourceStatus.ALLOCATED)
        busy_gpus = sum(1 for d in self.gpu_devices.values() if d.status == ResourceStatus.BUSY)
        
        # Calculate total memory
        total_memory_mb = sum(d.total_memory_mb for d in self.gpu_devices.values())
        available_memory_mb = sum(d.available_memory_mb for d in self.gpu_devices.values())
        
        # Node statistics
        total_nodes = len(self.gpu_nodes)
        healthy_nodes = sum(1 for n in self.gpu_nodes.values() if n.health_score > 0.8)
        
        return {
            'cluster_summary': {
                'total_nodes': total_nodes,
                'healthy_nodes': healthy_nodes,
                'total_gpus': total_gpus,
                'available_gpus': available_gpus,
                'allocated_gpus': allocated_gpus,
                'busy_gpus': busy_gpus,
                'utilization_percent': (total_gpus - available_gpus) / total_gpus * 100 if total_gpus > 0 else 0
            },
            'memory_summary': {
                'total_memory_gb': total_memory_mb / 1024,
                'available_memory_gb': available_memory_mb / 1024,
                'utilization_percent': (total_memory_mb - available_memory_mb) / total_memory_mb * 100 if total_memory_mb > 0 else 0
            },
            'nodes': [
                {
                    'node_id': node.node_id,
                    'hostname': node.hostname,
                    'total_gpus': node.total_gpus,
                    'available_gpus': node.available_gpus,
                    'health_score': node.health_score,
                    'status': node.status.value
                }
                for node in self.gpu_nodes.values()
            ],
            'active_allocations': len(self.active_allocations),
            'pending_requests': self.pending_requests.qsize(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_workload_recommendations(
        self,
        workload_type: WorkloadType,
        resource_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get optimization recommendations for a workload"""
        try:
            recommendations = {
                'optimal_gpu_types': [],
                'resource_configuration': {},
                'performance_predictions': {},
                'cost_optimization': {},
                'scheduling_strategy': ''
            }
            
            # Get workload-specific recommendations
            if workload_type == WorkloadType.TRAINING:
                recommendations.update(await self._get_training_recommendations(resource_requirements))
            elif workload_type == WorkloadType.INFERENCE:
                recommendations.update(await self._get_inference_recommendations(resource_requirements))
            elif workload_type == WorkloadType.DISTRIBUTED_TRAINING:
                recommendations.update(await self._get_distributed_training_recommendations(resource_requirements))
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating workload recommendations: {e}")
            return {}
    
    async def _get_training_recommendations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for training workloads"""
        return {
            'optimal_gpu_types': [GPUType.A100, GPUType.V100, GPUType.RTX_4090],
            'resource_configuration': {
                'gpu_memory_utilization': 0.9,
                'batch_size_multiplier': 2.0,
                'mixed_precision': True
            },
            'performance_predictions': {
                'training_time_hours': 12.5,
                'throughput_samples_per_sec': 450.0,
                'memory_efficiency': 0.87
            },
            'scheduling_strategy': 'consolidate_nodes'
        }
    
    async def _get_inference_recommendations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for inference workloads"""
        return {
            'optimal_gpu_types': [GPUType.T4, GPUType.RTX_3090, GPUType.A100],
            'resource_configuration': {
                'gpu_memory_utilization': 0.6,
                'batch_size_optimization': True,
                'model_optimization': 'tensorrt'
            },
            'performance_predictions': {
                'latency_p95_ms': 15.2,
                'throughput_rps': 1250.0,
                'memory_efficiency': 0.65
            },
            'scheduling_strategy': 'distribute_load'
        }
    
    async def _get_distributed_training_recommendations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommendations for distributed training workloads"""
        return {
            'optimal_gpu_types': [GPUType.A100, GPUType.H100],
            'resource_configuration': {
                'nodes_per_job': 4,
                'gpus_per_node': 8,
                'communication_backend': 'nccl',
                'topology_aware': True
            },
            'performance_predictions': {
                'scaling_efficiency': 0.85,
                'communication_overhead': 0.15,
                'total_training_time_hours': 6.2
            },
            'scheduling_strategy': 'gang_scheduling'
        }
    
    async def _optimize_resource_allocation(self) -> None:
        """Optimize current resource allocation"""
        while True:
            try:
                # Run optimization every 10 minutes
                await self.performance_optimizer.optimize_allocations(self.active_allocations)
                await self.load_balancer.rebalance_workloads(self.gpu_nodes)
                
                await asyncio.sleep(600)
                
            except Exception as e:
                self.logger.error(f"Error optimizing resource allocation: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_expired_allocations(self) -> None:
        """Clean up expired resource allocations"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_allocations = []
                
                for allocation_id, allocation in self.active_allocations.items():
                    if (allocation.expires_at and 
                        current_time > allocation.expires_at):
                        expired_allocations.append(allocation_id)
                
                # Release expired allocations
                for allocation_id in expired_allocations:
                    await self.release_gpu_resources(allocation_id)
                    self.logger.info(f"Cleaned up expired allocation: {allocation_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning up expired allocations: {e}")
                await asyncio.sleep(300)
    
    async def _store_resource_metrics(self) -> None:
        """Store resource metrics in Redis"""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'nodes': {
                    node_id: {
                        'total_gpus': node.total_gpus,
                        'available_gpus': node.available_gpus,
                        'health_score': node.health_score,
                        'status': node.status.value
                    }
                    for node_id, node in self.gpu_nodes.items()
                },
                'devices': {
                    device_id: {
                        'utilization': device.utilization_percent,
                        'temperature': device.temperature_celsius,
                        'memory_used_percent': (
                            (device.total_memory_mb - device.available_memory_mb) / 
                            device.total_memory_mb * 100
                        ),
                        'status': device.status.value
                    }
                    for device_id, device in self.gpu_devices.items()
                }
            }
            
            self.redis_client.setex(
                "gpu_cluster_metrics",
                timedelta(hours=24),
                json.dumps(metrics)
            )
            
        except Exception as e:
            self.logger.error(f"Error storing resource metrics: {e}")
    
    async def _store_resource_request(self, request: ResourceRequest) -> None:
        """Store resource request in Redis"""
        request_data = asdict(request)
        self.redis_client.setex(
            f"gpu_request:{request.request_id}",
            timedelta(days=7),
            json.dumps(request_data, default=str)
        )
    
    async def _store_resource_allocation(self, allocation: ResourceAllocation) -> None:
        """Store resource allocation in Redis"""
        allocation_data = asdict(allocation)
        self.redis_client.setex(
            f"gpu_allocation:{allocation.allocation_id}",
            timedelta(days=30),
            json.dumps(allocation_data, default=str)
        )


class GPUResourceMonitor:
    """Monitor GPU resource utilization and performance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('gpu_resource_monitor')


class GPUPerformanceOptimizer:
    """Optimize GPU performance and resource utilization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('gpu_performance_optimizer')
    
    async def optimize_allocations(self, allocations: Dict[str, ResourceAllocation]) -> None:
        """Optimize current resource allocations"""
        # Implementation for allocation optimization
        pass


class WorkloadPredictor:
    """Predict workload performance and resource requirements"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('workload_predictor')
    
    async def predict_performance(
        self,
        gpus: List[GPUDevice],
        workload_type: WorkloadType
    ) -> Dict[str, float]:
        """Predict workload performance on given GPUs"""
        # Mock performance prediction
        base_performance = {
            'throughput': 1000.0,
            'latency': 10.0,
            'memory_efficiency': 0.8,
            'power_efficiency': 0.75
        }
        
        # Adjust based on GPU types and count
        gpu_multiplier = len(gpus) * 0.9  # Slight scaling inefficiency
        
        for metric in base_performance:
            if metric == 'latency':
                base_performance[metric] /= gpu_multiplier
            else:
                base_performance[metric] *= gpu_multiplier
        
        return base_performance


class CostOptimizer:
    """Optimize resource allocation costs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('cost_optimizer')
    
    async def calculate_cost(
        self,
        gpus: List[GPUDevice],
        request: ResourceRequest
    ) -> float:
        """Calculate estimated cost for resource allocation"""
        # Mock cost calculation
        gpu_hour_costs = {
            GPUType.H100: 4.0,
            GPUType.A100: 3.0,
            GPUType.V100: 2.0,
            GPUType.RTX_4090: 1.5,
            GPUType.RTX_3090: 1.2,
            GPUType.T4: 0.8,
            GPUType.P100: 0.6,
            GPUType.K80: 0.4
        }
        
        total_cost = 0.0
        for gpu in gpus:
            hourly_cost = gpu_hour_costs.get(gpu.gpu_type, 1.0)
            total_cost += hourly_cost
        
        return total_cost


class GPUScheduler:
    """Schedule GPU resource allocation using various strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('gpu_scheduler')
    
    async def select_optimal_gpus(
        self,
        suitable_gpus: List[GPUDevice],
        request: ResourceRequest
    ) -> List[GPUDevice]:
        """Select optimal GPUs from suitable candidates"""
        if len(suitable_gpus) < request.gpu_count:
            return []
        
        # Sort GPUs by suitability score
        scored_gpus = []
        for gpu in suitable_gpus:
            score = self._calculate_gpu_score(gpu, request)
            scored_gpus.append((score, gpu))
        
        # Sort by score (higher is better)
        scored_gpus.sort(key=lambda x: x[0], reverse=True)
        
        # Select top GPUs
        selected_gpus = [gpu for _, gpu in scored_gpus[:request.gpu_count]]
        
        return selected_gpus
    
    def _calculate_gpu_score(self, gpu: GPUDevice, request: ResourceRequest) -> float:
        """Calculate suitability score for a GPU"""
        score = 0.0
        
        # Memory score (higher available memory is better)
        memory_ratio = gpu.available_memory_mb / gpu.total_memory_mb
        score += memory_ratio * 30
        
        # Utilization score (lower utilization is better for new workloads)
        utilization_score = (100 - gpu.utilization_percent) / 100 * 25
        score += utilization_score
        
        # Temperature score (lower temperature is better)
        temp_score = max(0, (90 - gpu.temperature_celsius) / 90 * 15)
        score += temp_score
        
        # GPU type preference score
        if gpu.gpu_type in request.preferred_gpu_types:
            score += 20
        
        # Node health score
        node_score = 10  # Default if node not found
        # Would get actual node health score here
        score += node_score
        
        return score


class GPULoadBalancer:
    """Balance workloads across GPU resources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('gpu_load_balancer')
    
    async def rebalance_workloads(self, gpu_nodes: Dict[str, GPUNode]) -> None:
        """Rebalance workloads across GPU nodes"""
        # Implementation for load balancing
        pass


# Factory function for creating GPU resource manager
def create_gpu_resource_manager(config: Dict[str, Any]) -> GPUResourceManager:
    """Create GPU resource manager instance"""
    return GPUResourceManager(config)


# Helper functions for resource management
def create_training_resource_request(
    workload_id: str,
    gpu_count: int,
    gpu_memory_gb: int,
    preferred_gpu_types: List[GPUType] = None
) -> ResourceRequest:
    """Create resource request for training workload"""
    return ResourceRequest(
        request_id=str(uuid.uuid4()),
        workload_id=workload_id,
        workload_type=WorkloadType.TRAINING,
        gpu_count=gpu_count,
        min_gpu_memory_mb=gpu_memory_gb * 1024,
        preferred_gpu_types=preferred_gpu_types or [GPUType.A100, GPUType.V100],
        cpu_cores=gpu_count * 4,
        memory_gb=gpu_count * 16,
        priority=3,
        max_wait_time=timedelta(hours=2)
    )


def create_inference_resource_request(
    workload_id: str,
    max_latency_ms: float,
    min_throughput_ops_sec: float
) -> ResourceRequest:
    """Create resource request for inference workload"""
    return ResourceRequest(
        request_id=str(uuid.uuid4()),
        workload_id=workload_id,
        workload_type=WorkloadType.INFERENCE,
        gpu_count=1,
        min_gpu_memory_mb=4096,
        preferred_gpu_types=[GPUType.T4, GPUType.RTX_3090],
        cpu_cores=2,
        memory_gb=8,
        max_latency_ms=max_latency_ms,
        min_throughput_ops_sec=min_throughput_ops_sec,
        priority=4,
        max_wait_time=timedelta(minutes=30)
    )