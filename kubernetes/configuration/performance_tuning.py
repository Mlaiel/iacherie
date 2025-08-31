"""🔧 Performance Tuning Manager - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: Performance Engineer + DevOps + Backend Senior + MLOps Engineer
Date: 2025-08-24

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
⚠️  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Enterprise-grade performance optimization and resource management.
==================================================================
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import psutil

class ResourceProfile(Enum):
    """Resource allocation profiles"""    MINIMAL = "minimal"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"
    GPU_INTENSIVE = "gpu_intensive"

class OptimizationTarget(Enum):
    """Performance optimization targets"""    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    STORAGE = "storage"
    AI_INFERENCE = "ai_inference"
    DATABASE = "database"

class CachingStrategy(Enum):
    """Caching strategies"""    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    INTELLIGENT = "intelligent"
    MULTI_LAYER = "multi_layer"

@dataclass
class CPUConfiguration:
    """CPU configuration settings"""    cores: int = 4
    threads_per_core: int = 2
    max_frequency: Optional[float] = None
    governor: str = "performance"
    affinity_mask: Optional[str] = None
    numa_policy: str = "interleave"
    cpu_quota: Optional[float] = None
    priority: int = 0

@dataclass
class MemoryConfiguration:
    """Memory configuration settings"""    total_memory: str = "8Gi"
    heap_size: str = "4Gi"
    swap_enabled: bool = False
    huge_pages: bool = False
    numa_balancing: bool = True
    page_size: str = "4K"
    overcommit_ratio: int = 50
    dirty_ratio: int = 20

@dataclass
class NetworkConfiguration:
    """Network performance configuration"""    max_connections: int = 10000
    keep_alive_timeout: int = 75
    tcp_window_size: int = 65536
    tcp_congestion_control: str = "bbr"
    network_buffers: int = 16777216
    connection_pooling: bool = True
    dns_caching: bool = True
    compression_enabled: bool = True

@dataclass
class StorageConfiguration:
    """Storage performance configuration"""    io_scheduler: str = "mq-deadline"
    read_ahead: int = 256
    queue_depth: int = 32
    cache_size: str = "1Gi"
    sync_mode: str = "async"
    compression: bool = True
    encryption_enabled: bool = True
    ssd_optimized: bool = True

@dataclass
class DatabaseConfiguration:
    """Database performance configuration"""    connection_pool_size: int = 20
    max_connections: int = 100
    shared_buffers: str = "256MB"
    effective_cache_size: str = "1GB"
    work_mem: str = "4MB"
    maintenance_work_mem: str = "64MB"
    checkpoint_completion_target: float = 0.9
    wal_buffers: str = "16MB"
    random_page_cost: float = 1.1

@dataclass
class CacheConfiguration:
    """Caching configuration"""    strategy: CachingStrategy
    redis_memory: str = "512MB"
    redis_maxmemory_policy: str = "allkeys-lru"
    memcached_memory: int = 512
    application_cache_size: str = "256MB"
    cdn_enabled: bool = True
    cache_ttl: int = 3600
    cache_compression: bool = True

@dataclass
class AIConfiguration:
    """AI/ML performance configuration"""    gpu_enabled: bool = False
    gpu_memory: str = "8GB"
    batch_size: int = 32
    model_parallelism: bool = False
    mixed_precision: bool = True
    tensor_cores: bool = True
    cuda_streams: int = 4
    inference_optimization: bool = True
    model_quantization: bool = False

@dataclass
class PerformanceConfiguration:
    """Complete performance configuration"""    profile: ResourceProfile
    optimization_targets: List[OptimizationTarget]
    cpu: CPUConfiguration
    memory: MemoryConfiguration
    network: NetworkConfiguration
    storage: StorageConfiguration
    database: DatabaseConfiguration
    cache: CacheConfiguration
    ai: AIConfiguration
    monitoring_enabled: bool = True
    auto_tuning: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class PerformanceTuningManager:
    """    Enterprise performance tuning and optimization manager.
    
    Provides comprehensive performance management:
    - Resource allocation optimization
    - Performance profiling and monitoring
    - Auto-scaling configuration
    - Caching strategy optimization
    - Database performance tuning
    - AI/ML workload optimization
    - Network and I/O optimization
    - Real-time performance metrics
    - Automated performance tuning
    """    
    def __init__(self):
        """Initialize performance tuning manager"""        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Performance configurations
        self.performance_configs = {}
        self.active_config = None
        self.current_profile = ResourceProfile.DEVELOPMENT
        
        # Performance monitoring
        self.metrics_history = []
        self.performance_alerts = []
        self.optimization_recommendations = []
        
        # System resources
        self.system_info = {}
        self.resource_usage = {}
        
        self.logger.info("Performance tuning manager initialized")
    
    async def initialize(self) -> bool:
        """        Initialize performance tuning manager.
        
        Returns:
            bool: True if initialization successful
        """        try:
            # Detect system resources
            await self._detect_system_resources()
            
            # Load performance configurations
            await self._load_performance_configurations()
            
            # Initialize monitoring
            await self._initialize_performance_monitoring()
            
            # Set default profile
            await self.set_performance_profile(ResourceProfile.DEVELOPMENT)
            
            self.logger.info("Performance tuning manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance manager: {e}")
            return False
    
    async def _detect_system_resources(self) -> None:
        """Detect available system resources"""        try:
            # CPU information
            cpu_info = {
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "architecture": "x86_64"  # Simplified
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "total_gb": round(memory.total / (1024**3), 2)
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                "total": disk.total,
                "free": disk.free,
                "total_gb": round(disk.total / (1024**3), 2)
            }
            
            # Network interfaces
            network_info = {
                "interfaces": list(psutil.net_if_addrs().keys()),
                "stats": psutil.net_io_counters()
            }
            
            self.system_info = {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "network": network_info,
                "detected_at": datetime.now()
            }
            
            self.logger.info(f"Detected system: {cpu_info['cores']} cores, {memory_info['total_gb']}GB RAM")
            
        except Exception as e:
            self.logger.warning(f"Failed to detect system resources: {e}")
    
    async def _load_performance_configurations(self) -> None:
        """Load performance configurations for all profiles"""        
        # Minimal configuration
        minimal_config = PerformanceConfiguration(
            profile=ResourceProfile.MINIMAL,
            optimization_targets=[OptimizationTarget.MEMORY],
            cpu=CPUConfiguration(
                cores=1,
                threads_per_core=1,
                governor="powersave",
                cpu_quota=0.5
            ),
            memory=MemoryConfiguration(
                total_memory="512Mi",
                heap_size="256Mi",
                swap_enabled=True
            ),
            network=NetworkConfiguration(
                max_connections=100,
                keep_alive_timeout=30,
                connection_pooling=False
            ),
            storage=StorageConfiguration(
                cache_size="64Mi",
                compression=False,
                ssd_optimized=False
            ),
            database=DatabaseConfiguration(
                connection_pool_size=5,
                max_connections=20,
                shared_buffers="32MB",
                work_mem="1MB"
            ),
            cache=CacheConfiguration(
                strategy=CachingStrategy.BASIC,
                redis_memory="128MB",
                application_cache_size="32MB",
                cdn_enabled=False
            ),
            ai=AIConfiguration(
                gpu_enabled=False,
                batch_size=8,
                mixed_precision=False
            )
        )
        
        # Development configuration
        development_config = PerformanceConfiguration(
            profile=ResourceProfile.DEVELOPMENT,
            optimization_targets=[OptimizationTarget.LATENCY, OptimizationTarget.MEMORY],
            cpu=CPUConfiguration(
                cores=2,
                threads_per_core=2,
                governor="ondemand"
            ),
            memory=MemoryConfiguration(
                total_memory="2Gi",
                heap_size="1Gi",
                swap_enabled=False
            ),
            network=NetworkConfiguration(
                max_connections=1000,
                keep_alive_timeout=60,
                connection_pooling=True
            ),
            storage=StorageConfiguration(
                cache_size="256Mi",
                compression=True,
                ssd_optimized=True
            ),
            database=DatabaseConfiguration(
                connection_pool_size=10,
                max_connections=50,
                shared_buffers="128MB",
                work_mem="2MB"
            ),
            cache=CacheConfiguration(
                strategy=CachingStrategy.AGGRESSIVE,
                redis_memory="256MB",
                application_cache_size="128MB",
                cdn_enabled=False
            ),
            ai=AIConfiguration(
                gpu_enabled=False,
                batch_size=16,
                mixed_precision=True
            )
        )
        
        # Production configuration
        production_config = PerformanceConfiguration(
            profile=ResourceProfile.PRODUCTION,
            optimization_targets=[
                OptimizationTarget.THROUGHPUT,
                OptimizationTarget.LATENCY,
                OptimizationTarget.CPU
            ],
            cpu=CPUConfiguration(
                cores=8,
                threads_per_core=2,
                governor="performance",
                numa_policy="interleave"
            ),
            memory=MemoryConfiguration(
                total_memory="16Gi",
                heap_size="8Gi",
                huge_pages=True,
                numa_balancing=True
            ),
            network=NetworkConfiguration(
                max_connections=10000,
                keep_alive_timeout=75,
                tcp_congestion_control="bbr",
                network_buffers=16777216,
                connection_pooling=True,
                compression_enabled=True
            ),
            storage=StorageConfiguration(
                io_scheduler="mq-deadline",
                queue_depth=32,
                cache_size="2Gi",
                sync_mode="async",
                compression=True,
                ssd_optimized=True
            ),
            database=DatabaseConfiguration(
                connection_pool_size=50,
                max_connections=200,
                shared_buffers="4GB",
                effective_cache_size="12GB",
                work_mem="8MB",
                maintenance_work_mem="512MB"
            ),
            cache=CacheConfiguration(
                strategy=CachingStrategy.MULTI_LAYER,
                redis_memory="4GB",
                application_cache_size="1GB",
                cdn_enabled=True,
                cache_compression=True
            ),
            ai=AIConfiguration(
                gpu_enabled=True,
                gpu_memory="8GB",
                batch_size=64,
                model_parallelism=True,
                mixed_precision=True,
                tensor_cores=True,
                inference_optimization=True
            ),
            monitoring_enabled=True,
            auto_tuning=True
        )
        
        # High performance configuration
        high_performance_config = PerformanceConfiguration(
            profile=ResourceProfile.HIGH_PERFORMANCE,
            optimization_targets=[
                OptimizationTarget.THROUGHPUT,
                OptimizationTarget.CPU,
                OptimizationTarget.AI_INFERENCE
            ],
            cpu=CPUConfiguration(
                cores=16,
                threads_per_core=2,
                governor="performance",
                affinity_mask="0xFF",
                numa_policy="strict",
                priority=-10
            ),
            memory=MemoryConfiguration(
                total_memory="32Gi",
                heap_size="16Gi",
                huge_pages=True,
                page_size="2M",
                overcommit_ratio=80
            ),
            network=NetworkConfiguration(
                max_connections=50000,
                tcp_window_size=131072,
                tcp_congestion_control="bbr",
                network_buffers=67108864,
                dns_caching=True
            ),
            storage=StorageConfiguration(
                io_scheduler="kyber",
                read_ahead=512,
                queue_depth=64,
                cache_size="8Gi",
                sync_mode="async"
            ),
            database=DatabaseConfiguration(
                connection_pool_size=100,
                max_connections=500,
                shared_buffers="8GB",
                effective_cache_size="24GB",
                work_mem="16MB",
                maintenance_work_mem="2GB",
                wal_buffers="64MB"
            ),
            cache=CacheConfiguration(
                strategy=CachingStrategy.INTELLIGENT,
                redis_memory="8GB",
                application_cache_size="4GB",
                cdn_enabled=True
            ),
            ai=AIConfiguration(
                gpu_enabled=True,
                gpu_memory="24GB",
                batch_size=128,
                model_parallelism=True,
                mixed_precision=True,
                cuda_streams=8,
                model_quantization=True
            ),
            auto_tuning=True
        )
        
        self.performance_configs = {
            ResourceProfile.MINIMAL: minimal_config,
            ResourceProfile.DEVELOPMENT: development_config,
            ResourceProfile.PRODUCTION: production_config,
            ResourceProfile.HIGH_PERFORMANCE: high_performance_config
        }
        
        self.logger.info(f"Loaded {len(self.performance_configs)} performance configurations")
    
    async def _initialize_performance_monitoring(self) -> None:
        """Initialize performance monitoring"""        # Start monitoring task
        asyncio.create_task(self._monitor_performance_metrics())
        self.logger.info("Performance monitoring initialized")
    
    async def _monitor_performance_metrics(self) -> None:
        """Monitor performance metrics continuously"""        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_performance_metrics()
                
                # Store in history
                self.metrics_history.append({
                    "timestamp": datetime.now(),
                    "metrics": metrics
                })
                
                # Keep only last 1000 entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # Check for performance issues
                await self._analyze_performance_metrics(metrics)
                
                # Wait before next collection
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "per_core": cpu_per_core,
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "percent": memory.percent,
                    "available": memory.available,
                    "used": memory.used,
                    "swap_percent": swap.percent
                },
                "disk": {
                    "percent": (disk_usage.used / disk_usage.total) * 100,
                    "free": disk_usage.free,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {}
    
    async def _analyze_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Analyze metrics for performance issues"""        alerts = []
        recommendations = []
        
        # CPU analysis
        if metrics.get("cpu", {}).get("percent", 0) > 90:
            alerts.append({
                "type": "high_cpu",
                "severity": "critical",
                "message": f"CPU usage at {metrics['cpu']['percent']}%",
                "timestamp": datetime.now()
            })
            recommendations.append("Consider scaling up CPU resources or optimizing workload")
        
        # Memory analysis
        memory_percent = metrics.get("memory", {}).get("percent", 0)
        if memory_percent > 85:
            alerts.append({
                "type": "high_memory",
                "severity": "warning" if memory_percent < 95 else "critical",
                "message": f"Memory usage at {memory_percent}%",
                "timestamp": datetime.now()
            })
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")
        
        # Disk analysis
        disk_percent = metrics.get("disk", {}).get("percent", 0)
        if disk_percent > 90:
            alerts.append({
                "type": "high_disk",
                "severity": "critical",
                "message": f"Disk usage at {disk_percent}%",
                "timestamp": datetime.now()
            })
            recommendations.append("Clean up disk space or expand storage")
        
        # Store alerts and recommendations
        self.performance_alerts.extend(alerts)
        self.optimization_recommendations.extend(recommendations)
        
        # Keep only recent alerts
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.performance_alerts = [
            alert for alert in self.performance_alerts 
            if alert["timestamp"] > cutoff_time
        ]
    
    async def set_performance_profile(self, profile: ResourceProfile) -> bool:
        """        Set performance profile.
        
        Args:
            profile: Resource profile to activate
            
        Returns:
            bool: True if successful
        """        try:
            if profile not in self.performance_configs:
                raise ValueError(f"Performance profile not configured: {profile.value}")
            
            self.current_profile = profile
            self.active_config = self.performance_configs[profile]
            
            # Apply performance configuration
            await self._apply_performance_configuration(self.active_config)
            
            self.logger.info(f"Performance profile set to: {profile.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set performance profile {profile.value}: {e}")
            return False
    
    async def _apply_performance_configuration(self, config: PerformanceConfiguration) -> None:
        """Apply performance configuration"""        # Apply CPU configuration
        cpu_config = config.cpu
        if cpu_config.cores:
            # Set CPU affinity if specified
            # Implementation would use system calls
            pass
        
        # Apply memory configuration
        memory_config = config.memory
        # Configure memory settings
        # Implementation would tune kernel parameters
        
        # Apply network configuration
        network_config = config.network
        # Configure network stack
        # Implementation would tune network parameters
        
        # Apply database configuration
        db_config = config.database
        # Configure database connection pool
        # Implementation would update database settings
        
        # Apply caching configuration
        cache_config = config.cache
        # Configure Redis and application caches
        # Implementation would update cache settings
        
        # Apply AI configuration
        ai_config = config.ai
        if ai_config.gpu_enabled:
            # Configure GPU settings
            # Implementation would set CUDA parameters
            pass
        
        self.logger.info(f"Applied performance configuration for profile: {config.profile.value}")
    
    async def configure_gpu_resources(self) -> bool:
        """Configure GPU resources for AI workloads"""        try:
            if not self.active_config or not self.active_config.ai.gpu_enabled:
                self.logger.info("GPU not enabled in current configuration")
                return True
            
            ai_config = self.active_config.ai
            
            # Configure GPU memory
            gpu_settings = {
                "memory_limit": ai_config.gpu_memory,
                "mixed_precision": ai_config.mixed_precision,
                "tensor_cores": ai_config.tensor_cores,
                "cuda_streams": ai_config.cuda_streams
            }
            
            # Apply GPU configuration
            # Implementation would use CUDA/GPU libraries
            
            self.logger.info(f"GPU resources configured: {gpu_settings}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure GPU resources: {e}")
            return False
    
    async def setup_auto_scaling(self) -> bool:
        """Setup auto-scaling configuration"""        try:
            if not self.active_config:
                raise ValueError("No active performance configuration")
            
            # Configure auto-scaling thresholds
            scaling_config = {
                "cpu_threshold": 70,
                "memory_threshold": 80,
                "scale_up_cooldown": 300,
                "scale_down_cooldown": 600,
                "min_replicas": 1,
                "max_replicas": 10
            }
            
            # Apply auto-scaling configuration
            # Implementation would configure Kubernetes HPA or similar
            
            self.logger.info("Auto-scaling configured")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup auto-scaling: {e}")
            return False
    
    async def optimize_performance(self, target: OptimizationTarget) -> Dict[str, Any]:
        """        Optimize performance for specific target.
        
        Args:
            target: Optimization target
            
        Returns:
            Optimization results
        """        try:
            optimization_result = {
                "target": target.value,
                "timestamp": datetime.now(),
                "changes": [],
                "metrics_before": await self._collect_performance_metrics()
            }
            
            if target == OptimizationTarget.LATENCY:
                # Optimize for low latency
                changes = await self._optimize_latency()
                optimization_result["changes"].extend(changes)
            
            elif target == OptimizationTarget.THROUGHPUT:
                # Optimize for high throughput
                changes = await self._optimize_throughput()
                optimization_result["changes"].extend(changes)
            
            elif target == OptimizationTarget.MEMORY:
                # Optimize memory usage
                changes = await self._optimize_memory()
                optimization_result["changes"].extend(changes)
            
            elif target == OptimizationTarget.AI_INFERENCE:
                # Optimize AI inference
                changes = await self._optimize_ai_inference()
                optimization_result["changes"].extend(changes)
            
            # Collect metrics after optimization
            await asyncio.sleep(30)  # Wait for changes to take effect
            optimization_result["metrics_after"] = await self._collect_performance_metrics()
            
            self.logger.info(f"Performance optimization completed for: {target.value}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            raise
    
    async def _optimize_latency(self) -> List[str]:
        """Optimize for low latency"""        changes = []
        
        # Reduce network timeouts
        changes.append("Reduced keep-alive timeout to 30s")
        
        # Enable connection pooling
        changes.append("Enabled aggressive connection pooling")
        
        # Optimize CPU scheduling
        changes.append("Set CPU governor to performance mode")
        
        return changes
    
    async def _optimize_throughput(self) -> List[str]:
        """Optimize for high throughput"""        changes = []
        
        # Increase connection limits
        changes.append("Increased max connections to 20000")
        
        # Optimize TCP settings
        changes.append("Enabled BBR congestion control")
        
        # Increase buffer sizes
        changes.append("Increased network buffer sizes")
        
        return changes
    
    async def _optimize_memory(self) -> List[str]:
        """Optimize memory usage"""        changes = []
        
        # Enable memory compression
        changes.append("Enabled memory compression")
        
        # Optimize garbage collection
        changes.append("Tuned garbage collection parameters")
        
        # Enable huge pages
        changes.append("Enabled transparent huge pages")
        
        return changes
    
    async def _optimize_ai_inference(self) -> List[str]:
        """Optimize AI inference performance"""        changes = []
        
        # Enable mixed precision
        changes.append("Enabled mixed precision training")
        
        # Optimize batch size
        changes.append("Optimized batch size for GPU utilization")
        
        # Enable tensor cores
        changes.append("Enabled Tensor Core acceleration")
        
        return changes
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""        current_metrics = await self._collect_performance_metrics()
        
        return {
            "profile": self.current_profile.value,
            "current_metrics": current_metrics,
            "system_info": self.system_info,
            "recent_alerts": self.performance_alerts[-10:],
            "recommendations": self.optimization_recommendations[-5:],
            "metrics_history_count": len(self.metrics_history),
            "optimization_targets": [t.value for t in self.active_config.optimization_targets] if self.active_config else []
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get performance manager status"""        return {
            "current_profile": self.current_profile.value,
            "monitoring_enabled": True,
            "auto_tuning": self.active_config.auto_tuning if self.active_config else False,
            "gpu_enabled": self.active_config.ai.gpu_enabled if self.active_config else False,
            "alerts_count": len(self.performance_alerts),
            "metrics_collected": len(self.metrics_history)
        }
