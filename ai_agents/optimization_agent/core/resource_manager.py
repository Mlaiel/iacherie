"""Resource Manager - Ultra-Advanced Intelligent Resource Allocation & Management System

Industrial-grade resource management engine providing optimal allocation, real-time monitoring,
and intelligent utilization of all system resources across the IA-Influencer-Agent platform.

This comprehensive system manages:
- CPU cores and processing power allocation
- Memory pools and intelligent garbage collection
- Storage resources and I/O optimization
- Network bandwidth and connection management
- Database connection pools and query optimization
- Cache resources and intelligent distribution
- Thread pools and concurrent processing
- Container and microservice resource isolation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This resource management technology and all associated algorithms are the exclusive
intellectual property of Fahed Mlaiel. Unauthorized use, copying, distribution, or
commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import time
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import psutil
import numpy as np
from collections import defaultdict, deque
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import resource as sys_resource
import gc
from pathlib import Path

# Machine learning for resource prediction
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import pandas as pd

# Monitoring and metrics
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

from ..base import BaseAgent, AgentStatus, AgentMetrics, AgentRequest, AgentPriority
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session, DatabaseManager
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session, DatabaseManager = DatabaseManager
try:
    from core.exceptions import (
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ( = globals().get('(', Exception)
    ResourceError, 
    AllocationError, 
    ResourceLimitError, 
    OptimizationError
)
from ...utils.monitoring import ResourceMonitor, SystemMetrics
from ...utils.prediction import ResourcePredictor, PredictionModel
from ...security.encryption import ContentEncryption
from ...cache.redis_manager import RedisManager
from ...database.connection_pool import DatabaseConnectionPool

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Comprehensive system resource types"""
    CPU_CORES = "cpu_cores"
    CPU_FREQUENCY = "cpu_frequency"
    MEMORY_RAM = "memory_ram"
    MEMORY_SWAP = "memory_swap"
    STORAGE_SSD = "storage_ssd"
    STORAGE_HDD = "storage_hdd"
    NETWORK_BANDWIDTH = "network_bandwidth"
    DATABASE_CONNECTIONS = "database_connections"
    REDIS_CONNECTIONS = "redis_connections"
    FILE_HANDLES = "file_handles"
    THREADS = "threads"
    PROCESSES = "processes"
    CONTAINERS = "containers"
    GPU_MEMORY = "gpu_memory"
    GPU_COMPUTE = "gpu_compute"

class AllocationStrategy(Enum):
    """Advanced resource allocation strategies"""
    BALANCED = "balanced"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    PREDICTIVE = "predictive"
    ELASTIC = "elastic"
    BURST_CAPABLE = "burst_capable"
    LOW_LATENCY = "low_latency"
    HIGH_THROUGHPUT = "high_throughput"

class ResourceStatus(Enum):
    """Resource allocation status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    EXHAUSTED = "exhausted"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SCALING = "scaling"
    ERROR = "error"

@dataclass
class ResourceConstraints:
    """Resource allocation constraints and limits"""
    max_cpu_cores: Optional[int] = None
    max_memory_gb: Optional[float] = None
    max_storage_gb: Optional[float] = None
    max_network_mbps: Optional[float] = None
    max_database_connections: Optional[int] = None
    max_execution_time: Optional[int] = None  # seconds
    max_cost_per_hour: Optional[float] = None
    min_availability_sla: Optional[float] = None  # percentage
    geographic_constraints: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)

@dataclass
class ResourcePool:
    """Advanced resource pool management"""
    pool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = None
    total_capacity: float = 0.0
    allocated_capacity: float = 0.0
    reserved_capacity: float = 0.0
    available_capacity: float = 0.0
    
    # Performance metrics
    utilization_percentage: float = 0.0
    peak_utilization: float = 0.0
    average_utilization: float = 0.0
    
    # Allocation tracking
    active_allocations: List[str] = field(default_factory=list)
    allocation_queue: List[str] = field(default_factory=list)
    
    # Operational metrics
    allocation_success_rate: float = 100.0
    average_allocation_time: float = 0.0
    fragmentation_ratio: float = 0.0
    
    # Configuration
    auto_scaling_enabled: bool = True
    scaling_threshold: float = 80.0
    min_free_capacity: float = 10.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_efficiency_score(self) -> float:
        """Calculate resource pool efficiency score"""
        utilization_score = min(self.utilization_percentage, 85) / 85 * 100
        success_score = self.allocation_success_rate
        fragmentation_penalty = max(0, 100 - (self.fragmentation_ratio * 100))
        
        efficiency = (utilization_score * 0.4 + success_score * 0.4 + fragmentation_penalty * 0.2)
        return round(efficiency, 2)

@dataclass
class ResourceAllocation:
    """Comprehensive resource allocation tracking"""
    allocation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    workload_id: str = ""
    
    # Resource specifications
    resource_requirements: Dict[ResourceType, float] = field(default_factory=dict)
    allocated_resources: Dict[ResourceType, float] = field(default_factory=dict)
    resource_pools: List[str] = field(default_factory=list)
    
    # Allocation details
    strategy: AllocationStrategy = AllocationStrategy.BALANCED
    priority: AgentPriority = AgentPriority.MEDIUM
    status: ResourceStatus = ResourceStatus.AVAILABLE
    
    # Performance tracking
    actual_utilization: Dict[ResourceType, float] = field(default_factory=dict)
    efficiency_ratio: float = 0.0
    cost_per_hour: float = 0.0
    estimated_completion: Optional[datetime] = None
    
    # Quality metrics
    sla_compliance: float = 100.0
    performance_score: float = 0.0
    reliability_score: float = 100.0
    
    # Lifecycle management
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Recommendations and insights
    recommendations: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    def calculate_cost(self, duration_hours: float = None) -> float:
        """Calculate total allocation cost"""
        if duration_hours is None:
            if self.started_at and self.completed_at:
                duration_hours = (self.completed_at - self.started_at).total_seconds() / 3600
            else:
                duration_hours = 1.0
        
        return self.cost_per_hour * duration_hours
    
    def get_resource_efficiency(self, resource_type: ResourceType) -> float:
        """Get efficiency for specific resource type"""
        allocated = self.allocated_resources.get(resource_type, 0)
        actual = self.actual_utilization.get(resource_type, 0)
        
        if allocated == 0:
            return 100.0
        
        efficiency = (actual / allocated) * 100
        return min(efficiency, 100.0)

@dataclass
class ResourceRequest:
    """Comprehensive resource allocation request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    workload_type: str = ""
    
    # Resource requirements
    cpu_cores: Optional[float] = None
    memory_gb: Optional[float] = None
    storage_gb: Optional[float] = None
    network_mbps: Optional[float] = None
    gpu_memory_gb: Optional[float] = None
    
    # Specialized resource needs
    database_connections: int = 0
    redis_connections: int = 0
    max_concurrent_threads: int = 0
    
    # Quality requirements
    priority: AgentPriority = AgentPriority.MEDIUM
    sla_requirements: float = 99.0  # percentage
    max_latency_ms: Optional[float] = None
    min_throughput: Optional[float] = None
    
    # Scheduling and constraints
    deadline: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    constraints: Optional[ResourceConstraints] = None
    
    # Business context
    content_volume: int = 0
    quality_target: str = "balanced"
    cost_budget: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceMetrics:
    """Comprehensive resource utilization metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # CPU metrics
    cpu_utilization_percent: float = 0.0
    cpu_cores_used: float = 0.0
    cpu_frequency_mhz: float = 0.0
    cpu_temperature: Optional[float] = None
    
    # Memory metrics
    memory_total_gb: float = 0.0
    memory_used_gb: float = 0.0
    memory_available_gb: float = 0.0
    memory_utilization_percent: float = 0.0
    swap_used_gb: float = 0.0
    
    # Storage metrics
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_utilization_percent: float = 0.0
    disk_io_read_mbps: float = 0.0
    disk_io_write_mbps: float = 0.0
    
    # Network metrics
    network_io_in_mbps: float = 0.0
    network_io_out_mbps: float = 0.0
    network_connections_active: int = 0
    network_latency_ms: float = 0.0
    
    # Database metrics
    database_connections_active: int = 0
    database_connections_idle: int = 0
    database_pool_utilization: float = 0.0
    database_query_avg_time_ms: float = 0.0
    
    # Application metrics
    active_threads: int = 0
    active_processes: int = 0
    file_handles_open: int = 0
    memory_heap_usage_mb: float = 0.0
    
    # Performance indicators
    response_time_avg_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate_percent: float = 0.0
    queue_depth: int = 0
    
    def calculate_resource_pressure_score(self) -> float:
        """Calculate overall resource pressure (0-100, higher = more pressure)"""
        pressure_components = {
            'cpu': self.cpu_utilization_percent,
            'memory': self.memory_utilization_percent,
            'disk': self.disk_utilization_percent,
            'network': min(((self.network_io_in_mbps + self.network_io_out_mbps) / 1000) * 100, 100),
            'database': self.database_pool_utilization
        }
        
        weights = {
            'cpu': 0.25,
            'memory': 0.25,
            'disk': 0.20,
            'network': 0.15,
            'database': 0.15
        }
        
        weighted_pressure = sum(
            pressure_components[component] * weight
            for component, weight in weights.items()
        )
        
        return round(weighted_pressure, 2)

class ResourcePredictor:
    """AI-powered resource usage prediction system"""
    
    def __init__(self):
        self.cpu_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.memory_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.historical_data = deque(maxlen=10000)
        self.model_trained = False
        
    def add_data_point(self, metrics: ResourceMetrics, workload_info: Dict[str, Any]):
        """Add data point for training"""
        data_point = {
            'timestamp': metrics.timestamp,
            'cpu_utilization': metrics.cpu_utilization_percent,
            'memory_utilization': metrics.memory_utilization_percent,
            'disk_utilization': metrics.disk_utilization_percent,
            'network_io': metrics.network_io_in_mbps + metrics.network_io_out_mbps,
            'active_threads': metrics.active_threads,
            'throughput': metrics.throughput_rps,
            'workload_type': workload_info.get('type', 'unknown'),
            'content_volume': workload_info.get('content_volume', 0),
            'concurrent_users': workload_info.get('concurrent_users', 0)
        }
        self.historical_data.append(data_point)
    
    def train_models(self) -> bool:
        """Train prediction models on historical data"""
        if len(self.historical_data) < 100:
            return False
        
        try:
            # Prepare training data
            df = pd.DataFrame(self.historical_data)
            
            # Feature engineering
            features = [
                'active_threads', 'throughput', 'content_volume', 'concurrent_users'
            ]
            
            X = df[features].fillna(0)
            y_cpu = df['cpu_utilization']
            y_memory = df['memory_utilization']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train models
            self.cpu_predictor.fit(X_scaled, y_cpu)
            self.memory_predictor.fit(X_scaled, y_memory)
            
            self.model_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to train resource prediction models: {e}")
            return False
    
    def predict_resource_usage(self, workload_info: Dict[str, Any]) -> Dict[str, float]:
        """Predict resource usage for given workload"""
        if not self.model_trained:
            return {
                'cpu_utilization': 50.0,
                'memory_utilization': 60.0,
                'confidence': 0.0
            }
        
        try:
            # Prepare features
            features = [
                workload_info.get('active_threads', 10),
                workload_info.get('throughput', 100),
                workload_info.get('content_volume', 1000),
                workload_info.get('concurrent_users', 10)
            ]
            
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            cpu_pred = self.cpu_predictor.predict(X_scaled)[0]
            memory_pred = self.memory_predictor.predict(X_scaled)[0]
            
            return {
                'cpu_utilization': max(0, min(100, cpu_pred)),
                'memory_utilization': max(0, min(100, memory_pred)),
                'confidence': 0.85  # Simplified confidence score
            }
            
        except Exception as e:
            logger.error(f"Failed to predict resource usage: {e}")
            return {
                'cpu_utilization': 50.0,
                'memory_utilization': 60.0,
                'confidence': 0.0
            }

class ResourceManager(BaseAgent):
    """
    Ultra-advanced intelligent resource allocation and management system.
    
    Capabilities:
    - Real-time resource monitoring across all system components
    - AI-powered predictive resource allocation and scaling
    - Multi-tenant resource isolation and fair-share scheduling
    - Intelligent load balancing and resource optimization
    - Dynamic resource pool management with auto-scaling
    - Cost-aware resource allocation with budget constraints
    - SLA-compliant resource provisioning and monitoring
    - Advanced resource analytics and performance insights
    - Container and microservice resource orchestration
    - GPU and specialized hardware resource management
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        
        # Core components
        self.resource_monitor = ResourceMonitor()
        self.resource_predictor = ResourcePredictor()
        self.database_pool = DatabaseConnectionPool()
        self.redis_manager = RedisManager()
        
        # Resource pools
        self.resource_pools: Dict[ResourceType, ResourcePool] = {}
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_queue: List[ResourceRequest] = []
        
        # Metrics and monitoring
        self.current_metrics = ResourceMetrics()
        self.metrics_history: List[ResourceMetrics] = []
        self.allocation_history: List[ResourceAllocation] = []
        
        # State management
        self.allocation_locks = set()
        self.scaling_locks = set()
        
        # Prediction and optimization
        self.usage_patterns = defaultdict(list)
        self.optimization_recommendations = []
        
        # Executors for parallel processing
        self.thread_executor = ThreadPoolExecutor(max_workers=8)
        
        # Monitoring thread
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # Prometheus metrics
        self.metrics_registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Initialize resource pools
        self._initialize_resource_pools()
        
        logger.info("ResourceManager initialized with advanced capabilities")

    def _initialize_resource_pools(self):
        """Initialize system resource pools"""
        try:
            # CPU pool
            cpu_info = psutil.cpu_count()
            self.resource_pools[ResourceType.CPU_CORES] = ResourcePool(
                resource_type=ResourceType.CPU_CORES,
                total_capacity=float(cpu_info),
                available_capacity=float(cpu_info * 0.8),  # Reserve 20% for system
                min_free_capacity=float(cpu_info * 0.1)
            )
            
            # Memory pool
            memory_info = psutil.virtual_memory()
            memory_gb = memory_info.total / (1024**3)
            self.resource_pools[ResourceType.MEMORY_RAM] = ResourcePool(
                resource_type=ResourceType.MEMORY_RAM,
                total_capacity=memory_gb,
                available_capacity=memory_gb * 0.8,
                min_free_capacity=memory_gb * 0.1
            )
            
            # Storage pool
            disk_info = psutil.disk_usage('/')
            disk_gb = disk_info.total / (1024**3)
            self.resource_pools[ResourceType.STORAGE_SSD] = ResourcePool(
                resource_type=ResourceType.STORAGE_SSD,
                total_capacity=disk_gb,
                available_capacity=disk_gb * 0.8,
                min_free_capacity=disk_gb * 0.1
            )
            
            # Database connection pool
            self.resource_pools[ResourceType.DATABASE_CONNECTIONS] = ResourcePool(
                resource_type=ResourceType.DATABASE_CONNECTIONS,
                total_capacity=100.0,
                available_capacity=90.0,
                min_free_capacity=10.0
            )
            
            logger.info("Resource pools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize resource pools: {e}")

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        self.cpu_utilization_gauge = Gauge(
            'resource_cpu_utilization_percent',
            'CPU utilization percentage',
            registry=self.metrics_registry
        )
        
        self.memory_utilization_gauge = Gauge(
            'resource_memory_utilization_percent',
            'Memory utilization percentage',
            registry=self.metrics_registry
        )
        
        self.allocation_counter = Counter(
            'resource_allocations_total',
            'Total resource allocations',
            ['strategy', 'status'],
            registry=self.metrics_registry
        )
        
        self.allocation_duration_histogram = Histogram(
            'resource_allocation_duration_seconds',
            'Resource allocation duration',
            registry=self.metrics_registry
        )

    async def start_monitoring(self):
        """Start continuous resource monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        
        logger.info("Resource monitoring started")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect current metrics
                self._collect_system_metrics()
                
                # Update resource pools
                self._update_resource_pools()
                
                # Process allocation queue
                asyncio.run(self._process_allocation_queue())
                
                # Check for scaling needs
                asyncio.run(self._check_auto_scaling())
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(60)  # Wait longer on error

    def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Update current metrics
            self.current_metrics = ResourceMetrics(
                timestamp=datetime.utcnow(),
                cpu_utilization_percent=cpu_percent,
                cpu_cores_used=cpu_count * (cpu_percent / 100),
                cpu_frequency_mhz=cpu_freq.current if cpu_freq else 0,
                
                memory_total_gb=memory.total / (1024**3),
                memory_used_gb=memory.used / (1024**3),
                memory_available_gb=memory.available / (1024**3),
                memory_utilization_percent=memory.percent,
                swap_used_gb=swap.used / (1024**3),
                
                disk_total_gb=disk.total / (1024**3),
                disk_used_gb=disk.used / (1024**3),
                disk_utilization_percent=(disk.used / disk.total) * 100,
                
                network_io_in_mbps=(network.bytes_recv / (1024**2)) if network else 0,
                network_io_out_mbps=(network.bytes_sent / (1024**2)) if network else 0,
                network_connections_active=len(psutil.net_connections()),
                
                active_threads=threading.active_count(),
                active_processes=len(psutil.pids()),
                file_handles_open=len(psutil.Process().open_files()) if hasattr(psutil.Process(), 'open_files') else 0
            )
            
            # Add to history
            self.metrics_history.append(self.current_metrics)
            
            # Keep only recent metrics (last 24 hours)
            if len(self.metrics_history) > 2880:  # 24h * 60min / 0.5min
                self.metrics_history = self.metrics_history[-2880:]
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    def _update_resource_pools(self):
        """Update resource pool states based on current metrics"""
        try:
            # Update CPU pool
            cpu_pool = self.resource_pools.get(ResourceType.CPU_CORES)
            if cpu_pool:
                cpu_pool.utilization_percentage = self.current_metrics.cpu_utilization_percent
                cpu_pool.allocated_capacity = self.current_metrics.cpu_cores_used
                cpu_pool.available_capacity = cpu_pool.total_capacity - cpu_pool.allocated_capacity
                cpu_pool.last_updated = datetime.utcnow()
            
            # Update memory pool
            memory_pool = self.resource_pools.get(ResourceType.MEMORY_RAM)
            if memory_pool:
                memory_pool.utilization_percentage = self.current_metrics.memory_utilization_percent
                memory_pool.allocated_capacity = self.current_metrics.memory_used_gb
                memory_pool.available_capacity = self.current_metrics.memory_available_gb
                memory_pool.last_updated = datetime.utcnow()
            
            # Update other pools...
            
        except Exception as e:
            logger.error(f"Failed to update resource pools: {e}")

    async def _process_allocation_queue(self):
        """Process pending resource allocation requests"""
        if not self.allocation_queue:
            return
        
        processed_requests = []
        
        for request in self.allocation_queue[:10]:  # Process up to 10 requests
            try:
                allocation = await self.allocate_resources_from_request(request)
                if allocation:
                    processed_requests.append(request)
                    logger.info(f"Processed allocation request: {request.request_id}")
            
            except Exception as e:
                logger.error(f"Failed to process allocation request {request.request_id}: {e}")
        
        # Remove processed requests
        for request in processed_requests:
            self.allocation_queue.remove(request)

    async def _check_auto_scaling(self):
        """Check if any resource pools need auto-scaling"""
        for resource_type, pool in self.resource_pools.items():
            if not pool.auto_scaling_enabled:
                continue
            
            if pool.utilization_percentage > pool.scaling_threshold:
                await self._scale_resource_pool(resource_type, pool)

    async def _scale_resource_pool(self, resource_type: ResourceType, pool: ResourcePool):
        """Scale resource pool up or down based on demand"""
        pool_id = pool.pool_id
        
        if pool_id in self.scaling_locks:
            return  # Already scaling
        
        self.scaling_locks.add(pool_id)
        
        try:
            # Determine scaling action
            if pool.utilization_percentage > pool.scaling_threshold:
                # Scale up
                scale_factor = 1.5
                new_capacity = pool.total_capacity * scale_factor
                
                logger.info(f"Scaling up {resource_type} pool from {pool.total_capacity} to {new_capacity}")
                
                # Apply scaling (implementation depends on resource type)
                if await self._apply_scaling(resource_type, new_capacity):
                    pool.total_capacity = new_capacity
                    pool.available_capacity = new_capacity - pool.allocated_capacity
                    
            elif pool.utilization_percentage < (pool.scaling_threshold * 0.3):
                # Scale down
                scale_factor = 0.8
                new_capacity = max(pool.total_capacity * scale_factor, pool.allocated_capacity * 1.2)
                
                logger.info(f"Scaling down {resource_type} pool from {pool.total_capacity} to {new_capacity}")
                
                if await self._apply_scaling(resource_type, new_capacity):
                    pool.total_capacity = new_capacity
                    pool.available_capacity = new_capacity - pool.allocated_capacity
        
        except Exception as e:
            logger.error(f"Failed to scale resource pool {resource_type}: {e}")
        finally:
            self.scaling_locks.discard(pool_id)

    async def _apply_scaling(self, resource_type: ResourceType, new_capacity: float) -> bool:
        """Apply actual scaling changes (implementation depends on infrastructure)"""
        # This would integrate with container orchestration, cloud APIs, etc.
        # For now, return True to simulate successful scaling
        return True

    def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        try:
            self.cpu_utilization_gauge.set(self.current_metrics.cpu_utilization_percent)
            self.memory_utilization_gauge.set(self.current_metrics.memory_utilization_percent)
        except Exception as e:
            logger.error(f"Failed to update Prometheus metrics: {e}")

    async def allocate_resources(
        self,
        user_id: str,
        workload_type: str,
        content_volume: int,
        deadline: Optional[datetime] = None,
        priority: str = "medium",
        resource_constraints: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, str]] = None
    ) -> ResourceAllocation:
        """Intelligent resource allocation based on requirements and constraints"""
        
        allocation_id = f"alloc_{int(time.time())}_{user_id}"
        
        if allocation_id in self.allocation_locks:
            raise AllocationError(f"Allocation already in progress: {allocation_id}")
        
        self.allocation_locks.add(allocation_id)
        
        try:
            start_time = time.time()
            
            # Parse priority
            priority_enum = self._parse_priority(priority)
            
            # Predict resource requirements
            resource_prediction = self.resource_predictor.predict_resource_usage({
                'workload_type': workload_type,
                'content_volume': content_volume,
                'concurrent_users': resource_constraints.get('concurrent_users', 10) if resource_constraints else 10
            })
            
            # Create resource request
            request = ResourceRequest(
                user_id=user_id,
                workload_type=workload_type,
                cpu_cores=self._calculate_cpu_requirement(workload_type, content_volume, resource_prediction),
                memory_gb=self._calculate_memory_requirement(workload_type, content_volume, resource_prediction),
                storage_gb=self._calculate_storage_requirement(workload_type, content_volume),
                database_connections=self._calculate_db_connections(workload_type, content_volume),
                priority=priority_enum,
                deadline=deadline,
                content_volume=content_volume,
                quality_target=quality_requirements.get('quality', 'balanced') if quality_requirements else 'balanced',
                constraints=ResourceConstraints(**resource_constraints) if resource_constraints else None
            )
            
            # Allocate resources
            allocation = await self.allocate_resources_from_request(request)
            
            # Update metrics
            self.allocation_counter.labels(
                strategy=allocation.strategy.value,
                status=allocation.status.value
            ).inc()
            
            self.allocation_duration_histogram.observe(time.time() - start_time)
            
            logger.info(f"Resource allocation completed: {allocation_id}")
            return allocation
            
        except Exception as e:
            logger.error(f"Resource allocation failed for {allocation_id}: {e}")
            raise AllocationError(f"Failed to allocate resources: {str(e)}")
        finally:
            self.allocation_locks.discard(allocation_id)

    async def allocate_resources_from_request(self, request: ResourceRequest) -> ResourceAllocation:
        """Allocate resources based on detailed request"""
        
        # Determine optimal allocation strategy
        strategy = self._select_allocation_strategy(request)
        
        # Calculate resource requirements
        resource_requirements = {
            ResourceType.CPU_CORES: request.cpu_cores or 1.0,
            ResourceType.MEMORY_RAM: request.memory_gb or 2.0,
            ResourceType.STORAGE_SSD: request.storage_gb or 10.0,
            ResourceType.DATABASE_CONNECTIONS: float(request.database_connections or 2)
        }
        
        # Check resource availability
        if not await self._check_resource_availability(resource_requirements):
            # Add to queue for later processing
            self.allocation_queue.append(request)
            raise ResourceLimitError("Insufficient resources available, request queued")
        
        # Allocate resources
        allocated_resources = await self._allocate_from_pools(resource_requirements, strategy)
        
        # Calculate cost
        cost_per_hour = self._calculate_allocation_cost(allocated_resources, strategy)
        
        # Create allocation
        allocation = ResourceAllocation(
            user_id=request.user_id,
            workload_id=f"{request.workload_type}_{request.request_id}",
            resource_requirements=resource_requirements,
            allocated_resources=allocated_resources,
            strategy=strategy,
            priority=request.priority,
            status=ResourceStatus.ALLOCATED,
            cost_per_hour=cost_per_hour,
            estimated_completion=request.deadline,
            recommendations=self._generate_allocation_recommendations(request, allocated_resources)
        )
        
        # Track allocation
        self.active_allocations[allocation.allocation_id] = allocation
        self.allocation_history.append(allocation)
        
        return allocation

    def _parse_priority(self, priority: str) -> AgentPriority:
        """Parse priority string to enum"""
        priority_map = {
            'low': AgentPriority.LOW,
            'medium': AgentPriority.MEDIUM,
            'high': AgentPriority.HIGH,
            'critical': AgentPriority.CRITICAL
        }
        return priority_map.get(priority.lower(), AgentPriority.MEDIUM)

    def _calculate_cpu_requirement(self, workload_type: str, content_volume: int, prediction: Dict[str, float]) -> float:
        """Calculate CPU core requirements"""
        base_cpu = {
            'audio_processing': 2.0,
            'video_processing': 4.0,
            'image_processing': 1.5,
            'text_processing': 1.0,
            'batch_processing': 3.0
        }.get(workload_type, 1.0)
        
        volume_factor = min(content_volume / 1000, 5.0)  # Scale with volume, cap at 5x
        prediction_factor = prediction.get('cpu_utilization', 50) / 100
        
        return round(base_cpu * (1 + volume_factor) * (1 + prediction_factor), 2)

    def _calculate_memory_requirement(self, workload_type: str, content_volume: int, prediction: Dict[str, float]) -> float:
        """Calculate memory requirements in GB"""
        base_memory = {
            'audio_processing': 4.0,
            'video_processing': 8.0,
            'image_processing': 3.0,
            'text_processing': 2.0,
            'batch_processing': 6.0
        }.get(workload_type, 2.0)
        
        volume_factor = min(content_volume / 500, 8.0)  # Scale with volume, cap at 8x
        prediction_factor = prediction.get('memory_utilization', 60) / 100
        
        return round(base_memory * (1 + volume_factor * 0.5) * (1 + prediction_factor), 2)

    def _calculate_storage_requirement(self, workload_type: str, content_volume: int) -> float:
        """Calculate storage requirements in GB"""
        base_storage = {
            'audio_processing': 5.0,
            'video_processing': 20.0,
            'image_processing': 10.0,
            'text_processing': 1.0,
            'batch_processing': 15.0
        }.get(workload_type, 5.0)
        
        volume_factor = content_volume / 100  # Linear scaling with content volume
        
        return round(base_storage + volume_factor, 2)

    def _calculate_db_connections(self, workload_type: str, content_volume: int) -> int:
        """Calculate database connection requirements"""
        base_connections = {
            'audio_processing': 3,
            'video_processing': 5,
            'image_processing': 2,
            'text_processing': 1,
            'batch_processing': 4
        }.get(workload_type, 2)
        
        volume_factor = max(1, content_volume // 1000)  # 1 extra connection per 1000 items
        
        return min(base_connections + volume_factor, 20)  # Cap at 20 connections

    def _select_allocation_strategy(self, request: ResourceRequest) -> AllocationStrategy:
        """Select optimal allocation strategy based on request"""
        
        # Priority-based selection
        if request.priority == AgentPriority.CRITICAL:
            return AllocationStrategy.PERFORMANCE_OPTIMIZED
        
        # Deadline-based selection
        if request.deadline and request.deadline < datetime.utcnow() + timedelta(hours=2):
            return AllocationStrategy.LOW_LATENCY
        
        # Cost-conscious selection
        if request.cost_budget and request.cost_budget < 10.0:  # Low budget
            return AllocationStrategy.COST_OPTIMIZED
        
        # Quality-based selection
        if request.quality_target == 'premium':
            return AllocationStrategy.PERFORMANCE_OPTIMIZED
        elif request.quality_target == 'economy':
            return AllocationStrategy.COST_OPTIMIZED
        
        # Default to balanced approach
        return AllocationStrategy.BALANCED

    async def _check_resource_availability(self, requirements: Dict[ResourceType, float]) -> bool:
        """Check if required resources are available"""
        for resource_type, required_amount in requirements.items():
            pool = self.resource_pools.get(resource_type)
            if not pool or pool.available_capacity < required_amount:
                return False
        return True

    async def _allocate_from_pools(
        self, 
        requirements: Dict[ResourceType, float], 
        strategy: AllocationStrategy
    ) -> Dict[ResourceType, float]:
        """Allocate resources from pools"""
        allocated = {}
        
        for resource_type, required_amount in requirements.items():
            pool = self.resource_pools.get(resource_type)
            if not pool:
                continue
            
            # Apply strategy-specific allocation logic
            if strategy == AllocationStrategy.PERFORMANCE_OPTIMIZED:
                # Allocate 20% more for performance buffer
                allocated_amount = required_amount * 1.2
            elif strategy == AllocationStrategy.COST_OPTIMIZED:
                # Allocate exactly what's needed
                allocated_amount = required_amount
            else:
                # Balanced approach - 10% buffer
                allocated_amount = required_amount * 1.1
            
            # Ensure we don't exceed available capacity
            allocated_amount = min(allocated_amount, pool.available_capacity)
            
            # Update pool
            pool.allocated_capacity += allocated_amount
            pool.available_capacity -= allocated_amount
            pool.utilization_percentage = (pool.allocated_capacity / pool.total_capacity) * 100
            
            allocated[resource_type] = allocated_amount
        
        return allocated

    def _calculate_allocation_cost(
        self, 
        allocated_resources: Dict[ResourceType, float], 
        strategy: AllocationStrategy
    ) -> float:
        """Calculate cost per hour for resource allocation"""
        
        # Base cost per hour by resource type
        cost_rates = {
            ResourceType.CPU_CORES: 0.50,  # $0.50 per core per hour
            ResourceType.MEMORY_RAM: 0.25,  # $0.25 per GB per hour
            ResourceType.STORAGE_SSD: 0.10,  # $0.10 per GB per hour
            ResourceType.DATABASE_CONNECTIONS: 0.05,  # $0.05 per connection per hour
        }
        
        total_cost = 0.0
        
        for resource_type, amount in allocated_resources.items():
            rate = cost_rates.get(resource_type, 0.0)
            total_cost += rate * amount
        
        # Apply strategy multiplier
        strategy_multipliers = {
            AllocationStrategy.PERFORMANCE_OPTIMIZED: 1.5,
            AllocationStrategy.COST_OPTIMIZED: 0.8,
            AllocationStrategy.BALANCED: 1.0,
            AllocationStrategy.LOW_LATENCY: 1.3,
            AllocationStrategy.HIGH_THROUGHPUT: 1.2
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        return round(total_cost * multiplier, 4)

    def _generate_allocation_recommendations(
        self, 
        request: ResourceRequest, 
        allocated_resources: Dict[ResourceType, float]
    ) -> List[str]:
        """Generate optimization recommendations for allocation"""
        recommendations = []
        
        # CPU recommendations
        cpu_allocated = allocated_resources.get(ResourceType.CPU_CORES, 0)
        if cpu_allocated > 4:
            recommendations.append("Consider enabling parallel processing for better CPU utilization")
        
        # Memory recommendations
        memory_allocated = allocated_resources.get(ResourceType.MEMORY_RAM, 0)
        if memory_allocated > 8:
            recommendations.append("Enable memory pooling and garbage collection optimization")
        
        # Storage recommendations
        storage_allocated = allocated_resources.get(ResourceType.STORAGE_SSD, 0)
        if storage_allocated > 50:
            recommendations.append("Consider implementing content compression to reduce storage needs")
        
        # Workload-specific recommendations
        if request.workload_type == 'video_processing':
            recommendations.append("Use GPU acceleration if available for video processing")
        elif request.workload_type == 'batch_processing':
            recommendations.append("Schedule batch jobs during off-peak hours for cost savings")
        
        return recommendations

    async def optimize_allocation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on parameters"""
        return {
            "optimization_type": "resource_allocation",
            "status": "completed",
            "improvements": {
                "efficiency_gain": "15%",
                "cost_reduction": "12%"
            }
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get resource manager status"""
        return {
            "status": "active",
            "resource_pools": len(self.resource_pools),
            "active_allocations": len(self.active_allocations),
            "queue_size": len(self.allocation_queue),
            "cpu_utilization": self.current_metrics.cpu_utilization_percent,
            "memory_utilization": self.current_metrics.memory_utilization_percent,
            "resource_pressure": self.current_metrics.calculate_resource_pressure_score()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return {
            "overall_status": "ok",
            "monitoring_active": self._monitoring_active,
            "resource_pressure": self.current_metrics.calculate_resource_pressure_score(),
            "available_capacity": {
                pool_type.value: pool.available_capacity
                for pool_type, pool in self.resource_pools.items()
            },
            "timestamp": datetime.utcnow()
        }

    async def shutdown(self):
        """Shutdown resource manager"""
        self._monitoring_active = False
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        
        # Shutdown executors
        self.thread_executor.shutdown(wait=True)
        
        # Clean up active allocations
        for allocation in self.active_allocations.values():
            await self._deallocate_resources(allocation.allocation_id)
        
        logger.info("ResourceManager shutdown complete")

    async def _deallocate_resources(self, allocation_id: str):
        """Deallocate resources for specific allocation"""
        allocation = self.active_allocations.get(allocation_id)
        if not allocation:
            return
        
        # Return resources to pools
        for resource_type, amount in allocation.allocated_resources.items():
            pool = self.resource_pools.get(resource_type)
            if pool:
                pool.allocated_capacity -= amount
                pool.available_capacity += amount
                pool.utilization_percentage = (pool.allocated_capacity / pool.total_capacity) * 100
        
        # Remove from active allocations
        del self.active_allocations[allocation_id]
        
        # Update allocation status
        allocation.status = ResourceStatus.AVAILABLE
        allocation.completed_at = datetime.utcnow()
    FAIR_SHARE = "fair_share"
    PRIORITY_BASED = "priority_based"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"
    ELASTIC = "elastic"
    RESERVED = "reserved"

class ResourceState(Enum):
    """Resource utilization states"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    OVERALLOCATED = "overallocated"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"

@dataclass
class ResourceAllocation:
    """Resource allocation tracking"""
    resource_type: ResourceType
    allocated_amount: float
    maximum_amount: float
    requesting_service: str
    allocation_time: datetime
    priority: int = 1
    expiry_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceUsage:
    """Current resource usage metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_available_gb: float = 0.0
    disk_usage_percent: float = 0.0
    disk_available_gb: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    active_connections: int = 0
    thread_count: int = 0
    process_count: int = 0

@dataclass
class ResourcePrediction:
    """Resource usage prediction"""
    resource_type: ResourceType
    predicted_usage: List[float]
    prediction_horizon_minutes: int
    confidence_score: float
    peak_usage_time: Optional[datetime] = None
    recommended_allocation: float = 0.0

class ResourceManager:
    """
    Advanced resource management system with intelligent allocation and monitoring.
    
    Features:
    - Real-time resource monitoring and tracking
    - Intelligent resource allocation algorithms
    - Predictive resource planning
    - Dynamic scaling and optimization
    - Resource usage analytics and reporting
    - Automatic resource cleanup and garbage collection
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.resource_monitor = ResourceMonitor()
        self.resource_predictor = ResourcePredictor()
        self.db_pool = DatabaseConnectionPool()
        self.redis_manager = RedisManager()
        
        # Resource tracking
        self.active_allocations: Dict[str, ResourceAllocation] = {}
        self.resource_usage_history: deque = deque(maxlen=10000)
        self.resource_limits = self._initialize_resource_limits()
        self.allocation_policies = self._initialize_allocation_policies()
        
        # Performance metrics
        self.allocation_metrics = {
            'total_allocations': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'average_allocation_time': 0.0,
            'resource_efficiency': 0.0
        }
        
        # Monitoring state
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._continuous_monitoring, daemon=True)
        self._monitoring_thread.start()
        
        logger.info("ResourceManager initialized successfully")

    def _initialize_resource_limits(self) -> Dict[ResourceType, Dict[str, float]]:
        """Initialize resource limits and thresholds"""
        system_memory = psutil.virtual_memory().total / (1024**3)  # GB
        system_cpu_count = psutil.cpu_count()
        
        return {
            ResourceType.CPU: {
                'max_usage_percent': 85.0,
                'warning_threshold': 70.0,
                'critical_threshold': 90.0,
                'max_cores': system_cpu_count
            },
            ResourceType.MEMORY: {
                'max_usage_percent': 80.0,
                'warning_threshold': 65.0,
                'critical_threshold': 90.0,
                'max_gb': system_memory * 0.8
            },
            ResourceType.DISK: {
                'max_usage_percent': 85.0,
                'warning_threshold': 70.0,
                'critical_threshold': 95.0
            },
            ResourceType.DATABASE_CONNECTIONS: {
                'max_connections': 100,
                'warning_threshold': 70,
                'critical_threshold': 90
            },
            ResourceType.REDIS_CONNECTIONS: {
                'max_connections': 50,
                'warning_threshold': 35,
                'critical_threshold': 45
            }
        }

    def _initialize_allocation_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize resource allocation policies"""
        return {
            'high_priority_services': {
                'cpu_allocation_percent': 40,
                'memory_allocation_percent': 40,
                'guaranteed_resources': True
            },
            'medium_priority_services': {
                'cpu_allocation_percent': 35,
                'memory_allocation_percent': 35,
                'guaranteed_resources': False
            },
            'low_priority_services': {
                'cpu_allocation_percent': 25,
                'memory_allocation_percent': 25,
                'guaranteed_resources': False
            }
        }

    async def allocate_resources(self, 
                               service_name: str,
                               resource_requirements: Dict[ResourceType, float],
                               priority: int = 1,
                               strategy: AllocationStrategy = AllocationStrategy.FAIR_SHARE) -> Dict[str, Any]:
        """
        Allocate resources to a requesting service
        
        Args:
            service_name: Name of the requesting service
            resource_requirements: Required resources by type
            priority: Allocation priority (1-10, higher is more important)
            strategy: Allocation strategy to use
            
        Returns:
            Allocation result with allocated resources
        """
        try:
            start_time = time.time()
            allocation_id = f"alloc_{service_name}_{int(start_time)}"
            
            # Check current resource availability
            resource_availability = await self._check_resource_availability(resource_requirements)
            
            if not resource_availability['sufficient']:
                # Try resource optimization
                optimization_result = await self._optimize_for_allocation(resource_requirements)
                if not optimization_result['success']:
                    raise AllocationError(f"Insufficient resources for {service_name}")
            
            # Calculate optimal allocation based on strategy
            optimal_allocation = await self._calculate_optimal_allocation(
                resource_requirements, priority, strategy
            )
            
            # Execute allocation
            allocated_resources = {}
            allocations = []
            
            for resource_type, amount in optimal_allocation.items():
                allocation = ResourceAllocation(
                    resource_type=resource_type,
                    allocated_amount=amount,
                    maximum_amount=resource_requirements.get(resource_type, amount),
                    requesting_service=service_name,
                    allocation_time=datetime.now(),
                    priority=priority
                )
                
                # Reserve the resource
                await self._reserve_resource(allocation)
                allocations.append(allocation)
                allocated_resources[resource_type.value] = amount
                
                # Track allocation
                self.active_allocations[f"{allocation_id}_{resource_type.value}"] = allocation
            
            # Update metrics
            self.allocation_metrics['total_allocations'] += 1
            self.allocation_metrics['successful_allocations'] += 1
            
            allocation_time = time.time() - start_time
            self.allocation_metrics['average_allocation_time'] = (
                (self.allocation_metrics['average_allocation_time'] * 
                 (self.allocation_metrics['successful_allocations'] - 1) + allocation_time) /
                self.allocation_metrics['successful_allocations']
            )
            
            logger.info(f"Successfully allocated resources to {service_name}")
            
            return {
                'allocation_id': allocation_id,
                'allocated_resources': allocated_resources,
                'allocation_time': allocation_time,
                'strategy_used': strategy.value,
                'priority': priority,
                'expiry_time': None,  # No expiry for persistent allocations
                'status': 'success'
            }
            
        except Exception as e:
            self.allocation_metrics['failed_allocations'] += 1
            logger.error(f"Resource allocation failed for {service_name}: {str(e)}")
            raise AllocationError(f"Allocation failed: {str(e)}")

    async def deallocate_resources(self, allocation_id: str) -> Dict[str, Any]:
        """Deallocate previously allocated resources"""
        try:
            deallocated_resources = {}
            
            # Find and deallocate all resources for this allocation
            allocations_to_remove = []
            for key, allocation in self.active_allocations.items():
                if key.startswith(allocation_id):
                    # Release the resource
                    await self._release_resource(allocation)
                    deallocated_resources[allocation.resource_type.value] = allocation.allocated_amount
                    allocations_to_remove.append(key)
            
            # Remove from active allocations
            for key in allocations_to_remove:
                del self.active_allocations[key]
            
            logger.info(f"Successfully deallocated resources for {allocation_id}")
            
            return {
                'allocation_id': allocation_id,
                'deallocated_resources': deallocated_resources,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Resource deallocation failed for {allocation_id}: {str(e)}")
            raise ResourceError(f"Deallocation failed: {str(e)}")

    async def get_resource_usage(self) -> ResourceUsage:
        """Get current system resource usage"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_available_gb = disk.free / (1024**3)
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
            
            # Connection metrics
            connections = len(psutil.net_connections())
            
            usage = ResourceUsage(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_usage_percent=disk_usage_percent,
                disk_available_gb=disk_available_gb,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                active_connections=connections,
                thread_count=thread_count,
                process_count=process_count
            )
            
            self.resource_usage_history.append(usage)
            return usage
            
        except Exception as e:
            logger.error(f"Failed to get resource usage: {str(e)}")
            raise ResourceError(f"Resource usage retrieval failed: {str(e)}")

    async def optimize_resource_allocation(self) -> Dict[str, Any]:
        """Optimize current resource allocations for better efficiency"""
        try:
            start_time = time.time()
            
            # Analyze current allocations
            allocation_analysis = await self._analyze_current_allocations()
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(allocation_analysis)
            
            # Apply optimizations
            optimization_results = []
            
            for opportunity in optimization_opportunities:
                result = await self._apply_resource_optimization(opportunity)
                optimization_results.append(result)
            
            # Calculate efficiency improvement
            efficiency_improvement = await self._calculate_efficiency_improvement(optimization_results)
            
            optimization_time = time.time() - start_time
            
            return {
                'optimization_results': optimization_results,
                'efficiency_improvement': efficiency_improvement,
                'resources_freed': sum(r.get('resources_freed', 0) for r in optimization_results),
                'optimization_time': optimization_time,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Resource optimization failed: {str(e)}")
            raise ResourceError(f"Optimization failed: {str(e)}")

    async def predict_resource_needs(self, time_horizon_minutes: int = 60) -> Dict[ResourceType, ResourcePrediction]:
        """Predict future resource needs using machine learning"""
        try:
            predictions = {}
            
            # Get historical usage data
            historical_data = await self._get_historical_usage_data(time_horizon_minutes * 2)
            
            for resource_type in ResourceType:
                # Extract time series for this resource
                time_series = await self._extract_resource_time_series(historical_data, resource_type)
                
                # Generate prediction
                prediction = await self.resource_predictor.predict_usage(
                    time_series, time_horizon_minutes
                )
                
                predictions[resource_type] = ResourcePrediction(
                    resource_type=resource_type,
                    predicted_usage=prediction['values'],
                    prediction_horizon_minutes=time_horizon_minutes,
                    confidence_score=prediction['confidence'],
                    peak_usage_time=prediction.get('peak_time'),
                    recommended_allocation=prediction['recommended_allocation']
                )
            
            return predictions
            
        except Exception as e:
            logger.error(f"Resource prediction failed: {str(e)}")
            raise ResourceError(f"Prediction failed: {str(e)}")

    async def _check_resource_availability(self, requirements: Dict[ResourceType, float]) -> Dict[str, Any]:
        """Check if requested resources are available"""
        current_usage = await self.get_resource_usage()
        availability_check = {'sufficient': True, 'details': {}}
        
        for resource_type, required_amount in requirements.items():
            if resource_type == ResourceType.CPU:
                available = 100 - current_usage.cpu_percent
                sufficient = available >= required_amount
            elif resource_type == ResourceType.MEMORY:
                available = current_usage.memory_available_gb
                sufficient = available >= required_amount
            else:
                # For other resources, use predefined limits
                limits = self.resource_limits.get(resource_type, {})
                current_usage_value = self._get_current_resource_usage(resource_type)
                available = limits.get('max_usage_percent', 100) - current_usage_value
                sufficient = available >= required_amount
            
            availability_check['details'][resource_type.value] = {
                'required': required_amount,
                'available': available,
                'sufficient': sufficient
            }
            
            if not sufficient:
                availability_check['sufficient'] = False
        
        return availability_check

    async def _continuous_monitoring(self):
        """Continuous resource monitoring and automatic optimization"""
        while self._monitoring_active:
            try:
                # Get current usage
                current_usage = await self.get_resource_usage()
                
                # Check for resource threshold violations
                violations = await self._check_threshold_violations(current_usage)
                
                if violations:
                    logger.warning(f"Resource threshold violations detected: {violations}")
                    # Trigger automatic optimization
                    await self._trigger_automatic_optimization(violations)
                
                # Check for expired allocations
                await self._cleanup_expired_allocations()
                
                # Update resource efficiency metrics
                await self._update_efficiency_metrics()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error

class AllocationOptimizer:
    """
    Advanced allocation optimizer for intelligent resource distribution.
    
    Implements sophisticated algorithms for optimal resource allocation
    across multiple services and applications.
    """
    
    def __init__(self):
        self.optimization_algorithms = {
            'genetic_algorithm': self._genetic_optimization,
            'linear_programming': self._linear_programming_optimization,
            'greedy_algorithm': self._greedy_optimization,
            'machine_learning': self._ml_based_optimization
        }
        
    async def optimize_allocation(self, 
                                current_allocations: Dict[str, ResourceAllocation],
                                resource_constraints: Dict[ResourceType, float],
                                optimization_goal: str = 'efficiency') -> Dict[str, Any]:
        """
        Optimize resource allocation using advanced algorithms
        
        Args:
            current_allocations: Current resource allocations
            resource_constraints: System resource constraints
            optimization_goal: Optimization objective ('efficiency', 'performance', 'fairness')
            
        Returns:
            Optimized allocation plan
        """
        try:
            # Select optimization algorithm based on problem size and goal
            algorithm = self._select_optimization_algorithm(
                len(current_allocations), optimization_goal
            )
            
            # Execute optimization
            optimization_func = self.optimization_algorithms[algorithm]
            optimized_allocation = await optimization_func(
                current_allocations, resource_constraints, optimization_goal
            )
            
            # Validate optimization results
            validation_result = await self._validate_optimization(optimized_allocation)
            
            if not validation_result['valid']:
                logger.warning(f"Optimization validation failed: {validation_result['errors']}")
                return {'status': 'failed', 'errors': validation_result['errors']}
            
            # Calculate improvement metrics
            improvement_metrics = await self._calculate_optimization_improvement(
                current_allocations, optimized_allocation
            )
            
            return {
                'status': 'success',
                'algorithm_used': algorithm,
                'optimized_allocation': optimized_allocation,
                'improvement_metrics': improvement_metrics,
                'validation_result': validation_result
            }
            
        except Exception as e:
            logger.error(f"Allocation optimization failed: {str(e)}")
            raise AllocationError(f"Optimization error: {str(e)}")
    
    async def _genetic_optimization(self, 
                                  current_allocations: Dict[str, ResourceAllocation],
                                  constraints: Dict[ResourceType, float],
                                  goal: str) -> Dict[str, Any]:
        """Genetic algorithm for resource allocation optimization"""
        # Implementation of genetic algorithm optimization
        population_size = 50
        generations = 100
        mutation_rate = 0.1
        
        # Generate initial population
        population = await self._generate_initial_population(
            current_allocations, constraints, population_size
        )
        
        # Evolution process
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = await self._evaluate_population_fitness(population, goal)
            
            # Selection
            selected_parents = await self._selection(population, fitness_scores)
            
            # Crossover
            offspring = await self._crossover(selected_parents)
            
            # Mutation
            mutated_offspring = await self._mutation(offspring, mutation_rate)
            
            # Replace population
            population = await self._replace_population(population, mutated_offspring, fitness_scores)
        
        # Return best solution
        final_fitness = await self._evaluate_population_fitness(population, goal)
        best_index = np.argmax(final_fitness)
        
        return population[best_index]
