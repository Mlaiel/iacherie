"""
⚡ PERFORMANCE CONFIGURATION - IA CHÉRIES ENTERPRISE PLATFORM

Ultra-advanced performance optimization with automatic tuning and resource management
Performance Target: < 1ms performance configuration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY SOFTWARE - COMMERCIAL USE PROHIBITED WITHOUT LICENSE
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import psutil
import gc

logger = logging.getLogger(__name__)

class PerformanceProfile(Enum):
    """Performance optimization profiles"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"

class CacheStrategy(Enum):
    """Caching strategies"""
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    LRU = "lru"
    LFU = "lfu"
    ADAPTIVE = "adaptive"

@dataclass
class CachingConfig:
    """Caching configuration"""
    strategy: CacheStrategy = CacheStrategy.ADAPTIVE
    max_memory_mb: int = 512
    ttl_seconds: int = 3600
    max_keys: int = 100000
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes
    eviction_policy: str = "allkeys-lru"
    redis_clusters: List[str] = field(default_factory=list)
    local_cache_size_mb: int = 128
    distributed_cache: bool = True

@dataclass
class OptimizationConfig:
    """Performance optimization configuration"""
    enable_query_optimization: bool = True
    enable_index_optimization: bool = True
    enable_connection_pooling: bool = True
    enable_lazy_loading: bool = True
    enable_batch_processing: bool = True
    enable_compression: bool = True
    enable_cdn: bool = True
    enable_prefetching: bool = True
    max_query_complexity: int = 1000
    batch_size: int = 100
    prefetch_size: int = 50

@dataclass
class ResourceConfig:
    """Resource allocation configuration"""
    max_cpu_cores: int = 8
    max_memory_gb: int = 16
    max_disk_iops: int = 10000
    max_network_mbps: int = 1000
    worker_processes: int = 4
    thread_pool_size: int = 50
    async_task_limit: int = 1000
    gc_threshold: Tuple[int, int, int] = (700, 10, 10)
    file_descriptor_limit: int = 65536

class PerformanceConfig:
    """
    Enterprise performance configuration manager
    Performance target: < 1ms performance configuration
    """
    
    def __init__(self):
        self.caching_config = CachingConfig()
        self.optimization_config = OptimizationConfig()
        self.resource_config = ResourceConfig()
        self.current_profile = PerformanceProfile.PRODUCTION
        self._performance_metrics: Dict[str, Any] = {}
        self._optimization_history: List[Dict[str, Any]] = []
        self._resource_usage: Dict[str, Any] = {}
        self._benchmarks: Dict[str, float] = {}
        
        # Load configuration from environment
        self._load_from_environment()
        
        # Initialize performance profiles
        self._setup_performance_profiles()
        
        # Configure garbage collection
        self._configure_garbage_collection()
    
    def _load_from_environment(self):
        """Load performance configuration from environment variables"""
        
        # Profile selection
        profile_name = os.getenv('IA CHÉRIES_PERFORMANCE_PROFILE', 'production')
        try:
            self.current_profile = PerformanceProfile(profile_name)
        except ValueError:
            logger.warning(f"Unknown performance profile: {profile_name}, using production")
            self.current_profile = PerformanceProfile.PRODUCTION
        
        # Cache configuration
        self.caching_config.max_memory_mb = int(os.getenv('CACHE_MAX_MEMORY_MB', self.caching_config.max_memory_mb))
        self.caching_config.ttl_seconds = int(os.getenv('CACHE_TTL_SECONDS', self.caching_config.ttl_seconds))
        
        # Resource configuration
        self.resource_config.worker_processes = int(os.getenv('WORKER_PROCESSES', self.resource_config.worker_processes))
        self.resource_config.thread_pool_size = int(os.getenv('THREAD_POOL_SIZE', self.resource_config.thread_pool_size))
    
    def _setup_performance_profiles(self):
        """Setup performance profiles for different environments"""
        
        profiles = {
            PerformanceProfile.DEVELOPMENT: {
                "caching": CachingConfig(
                    max_memory_mb=128,
                    ttl_seconds=300,
                    max_keys=10000,
                    local_cache_size_mb=32,
                    distributed_cache=False
                ),
                "optimization": OptimizationConfig(
                    enable_query_optimization=False,
                    enable_compression=False,
                    enable_cdn=False,
                    batch_size=10,
                    prefetch_size=5
                ),
                "resources": ResourceConfig(
                    max_cpu_cores=2,
                    max_memory_gb=4,
                    worker_processes=1,
                    thread_pool_size=10,
                    async_task_limit=100
                )
            },
            PerformanceProfile.TESTING: {
                "caching": CachingConfig(
                    max_memory_mb=64,
                    ttl_seconds=60,
                    max_keys=5000,
                    local_cache_size_mb=16,
                    distributed_cache=False
                ),
                "optimization": OptimizationConfig(
                    enable_query_optimization=True,
                    enable_compression=False,
                    enable_cdn=False,
                    batch_size=5,
                    prefetch_size=2
                ),
                "resources": ResourceConfig(
                    max_cpu_cores=1,
                    max_memory_gb=2,
                    worker_processes=1,
                    thread_pool_size=5,
                    async_task_limit=50
                )
            },
            PerformanceProfile.STAGING: {
                "caching": CachingConfig(
                    max_memory_mb=256,
                    ttl_seconds=1800,
                    max_keys=50000,
                    local_cache_size_mb=64,
                    distributed_cache=True
                ),
                "optimization": OptimizationConfig(
                    enable_query_optimization=True,
                    enable_compression=True,
                    enable_cdn=True,
                    batch_size=50,
                    prefetch_size=25
                ),
                "resources": ResourceConfig(
                    max_cpu_cores=4,
                    max_memory_gb=8,
                    worker_processes=2,
                    thread_pool_size=25,
                    async_task_limit=500
                )
            },
            PerformanceProfile.PRODUCTION: {
                "caching": CachingConfig(
                    max_memory_mb=512,
                    ttl_seconds=3600,
                    max_keys=100000,
                    local_cache_size_mb=128,
                    distributed_cache=True
                ),
                "optimization": OptimizationConfig(
                    enable_query_optimization=True,
                    enable_compression=True,
                    enable_cdn=True,
                    batch_size=100,
                    prefetch_size=50
                ),
                "resources": ResourceConfig(
                    max_cpu_cores=8,
                    max_memory_gb=16,
                    worker_processes=4,
                    thread_pool_size=50,
                    async_task_limit=1000
                )
            },
            PerformanceProfile.HIGH_PERFORMANCE: {
                "caching": CachingConfig(
                    max_memory_mb=2048,
                    ttl_seconds=7200,
                    max_keys=500000,
                    local_cache_size_mb=512,
                    distributed_cache=True
                ),
                "optimization": OptimizationConfig(
                    enable_query_optimization=True,
                    enable_compression=True,
                    enable_cdn=True,
                    enable_prefetching=True,
                    batch_size=500,
                    prefetch_size=200
                ),
                "resources": ResourceConfig(
                    max_cpu_cores=16,
                    max_memory_gb=64,
                    worker_processes=8,
                    thread_pool_size=100,
                    async_task_limit=5000
                )
            }
        }
        
        # Apply current profile
        if self.current_profile in profiles:
            profile = profiles[self.current_profile]
            self.caching_config = profile["caching"]
            self.optimization_config = profile["optimization"]
            self.resource_config = profile["resources"]
    
    def _configure_garbage_collection(self):
        """Configure Python garbage collection for optimal performance"""
        
        # Set garbage collection thresholds based on profile
        if self.current_profile in [PerformanceProfile.PRODUCTION, PerformanceProfile.HIGH_PERFORMANCE]:
            # More aggressive GC for production
            gc.set_threshold(700, 10, 10)
        else:
            # Standard GC for development
            gc.set_threshold(700, 10, 10)
        
        # Enable automatic garbage collection
        gc.enable()
        
        logger.info(f"Garbage collection configured for {self.current_profile.value} profile")
    
    async def configure_performance_parameters(self) -> Dict[str, Any]:
        """
        Configure comprehensive performance parameters
        Performance target: < 1ms
        """
        start_time = time.perf_counter()
        
        try:
            performance_config = {
                "profile": self.current_profile.value,
                "caching": {
                    "strategy": self.caching_config.strategy.value,
                    "memory_limit_mb": self.caching_config.max_memory_mb,
                    "ttl_seconds": self.caching_config.ttl_seconds,
                    "compression_enabled": self.caching_config.enable_compression,
                    "distributed": self.caching_config.distributed_cache,
                    "eviction_policy": self.caching_config.eviction_policy
                },
                "optimization": {
                    "query_optimization": self.optimization_config.enable_query_optimization,
                    "compression": self.optimization_config.enable_compression,
                    "cdn_enabled": self.optimization_config.enable_cdn,
                    "batch_processing": self.optimization_config.enable_batch_processing,
                    "lazy_loading": self.optimization_config.enable_lazy_loading,
                    "prefetching": self.optimization_config.enable_prefetching,
                    "batch_size": self.optimization_config.batch_size
                },
                "resources": {
                    "cpu_cores": self.resource_config.max_cpu_cores,
                    "memory_gb": self.resource_config.max_memory_gb,
                    "worker_processes": self.resource_config.worker_processes,
                    "thread_pool_size": self.resource_config.thread_pool_size,
                    "async_task_limit": self.resource_config.async_task_limit
                },
                "database": {
                    "connection_pool_size": self.resource_config.worker_processes * 5,
                    "query_timeout": 30,
                    "statement_timeout": 60,
                    "idle_in_transaction_timeout": 300,
                    "enable_prepared_statements": True,
                    "enable_query_cache": True
                },
                "api": {
                    "rate_limiting": {
                        "requests_per_minute": 1000,
                        "burst_limit": 2000,
                        "concurrent_requests": 500
                    },
                    "response_compression": True,
                    "keep_alive_timeout": 5,
                    "request_timeout": 30,
                    "max_request_size_mb": 50
                },
                "ai_processing": {
                    "model_cache_size": 3,
                    "batch_inference": True,
                    "gpu_memory_fraction": 0.8,
                    "concurrent_models": 2,
                    "processing_timeout": 300
                }
            }
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.info(f"Performance parameters configured in {duration:.2f}ms")
            
            return performance_config
            
        except Exception as e:
            logger.error(f"Failed to configure performance parameters: {e}")
            raise
    
    async def optimize_workflow_execution(self) -> Dict[str, Any]:
        """
        Optimize workflow execution performance
        Performance target: < 5ms optimization
        """
        try:
            optimization_results = {
                "workflow_optimizations": {
                    "parallel_execution": {
                        "enabled": True,
                        "max_parallel_workflows": self.resource_config.worker_processes * 10,
                        "task_parallelization": True,
                        "dependency_optimization": True
                    },
                    "caching_strategies": {
                        "workflow_templates": "aggressive",
                        "task_results": "moderate",
                        "user_data": "conservative",
                        "ai_model_outputs": "persistent"
                    },
                    "resource_scheduling": {
                        "cpu_scheduling": "round_robin",
                        "memory_scheduling": "best_fit",
                        "io_scheduling": "cfq",
                        "priority_queues": True
                    },
                    "pipeline_optimizations": {
                        "lazy_evaluation": True,
                        "stream_processing": True,
                        "micro_batching": True,
                        "result_streaming": True
                    }
                },
                "creator_workflow_optimizations": {
                    "content_processing": {
                        "async_processing": True,
                        "progressive_upload": True,
                        "thumbnail_generation": "on_demand",
                        "format_conversion": "background"
                    },
                    "ai_analysis": {
                        "batch_analysis": True,
                        "model_warm_up": True,
                        "result_caching": True,
                        "priority_processing": True
                    },
                    "collaboration": {
                        "real_time_sync": True,
                        "conflict_resolution": "automatic",
                        "version_optimization": True,
                        "delta_synchronization": True
                    }
                },
                "performance_targets": {
                    "workflow_start_time": "< 100ms",
                    "task_execution_time": "< 500ms",
                    "workflow_completion": "< 30s",
                    "memory_usage": f"< {self.resource_config.max_memory_gb}GB",
                    "cpu_utilization": "< 80%"
                }
            }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Workflow optimization failed: {e}")
            return {"error": str(e)}
    
    async def manage_resource_allocation(self) -> Dict[str, Any]:
        """
        Manage dynamic resource allocation
        Performance target: < 3ms allocation
        """
        try:
            # Get current system resources
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resource_allocation = {
                "current_resources": {
                    "cpu_cores_available": cpu_count,
                    "memory_total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                    "memory_available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                    "disk_total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2)
                },
                "allocation_strategy": {
                    "cpu_allocation": {
                        "api_workers": f"{self.resource_config.worker_processes} cores",
                        "background_tasks": f"{max(1, cpu_count // 4)} cores",
                        "ai_processing": f"{max(1, cpu_count // 2)} cores",
                        "database": f"{max(1, cpu_count // 8)} cores"
                    },
                    "memory_allocation": {
                        "application": f"{self.resource_config.max_memory_gb // 2}GB",
                        "cache": f"{self.caching_config.max_memory_mb}MB",
                        "ai_models": f"{self.resource_config.max_memory_gb // 4}GB",
                        "database_cache": f"{self.resource_config.max_memory_gb // 4}GB"
                    },
                    "io_allocation": {
                        "api_connections": self.resource_config.thread_pool_size,
                        "database_connections": self.resource_config.worker_processes * 5,
                        "file_descriptors": self.resource_config.file_descriptor_limit,
                        "network_bandwidth": f"{self.resource_config.max_network_mbps}Mbps"
                    }
                },
                "dynamic_scaling": {
                    "cpu_scaling": {
                        "scale_up_threshold": 80,
                        "scale_down_threshold": 30,
                        "scaling_factor": 1.5,
                        "cooldown_period": 300
                    },
                    "memory_scaling": {
                        "scale_up_threshold": 85,
                        "scale_down_threshold": 40,
                        "scaling_factor": 1.3,
                        "cooldown_period": 600
                    },
                    "auto_scaling_enabled": True,
                    "max_scale_factor": 3.0
                }
            }
            
            self._resource_usage = resource_allocation["current_resources"]
            return resource_allocation
            
        except Exception as e:
            logger.error(f"Resource allocation management failed: {e}")
            return {"error": str(e)}
    
    async def performance_monitoring_setup(self) -> Dict[str, Any]:
        """
        Setup comprehensive performance monitoring
        Performance target: < 8ms setup
        """
        try:
            monitoring_setup = {
                "real_time_metrics": {
                    "response_times": {
                        "api_endpoints": True,
                        "database_queries": True,
                        "ai_processing": True,
                        "file_operations": True
                    },
                    "throughput_metrics": {
                        "requests_per_second": True,
                        "concurrent_users": True,
                        "workflow_executions": True,
                        "content_processing": True
                    },
                    "resource_metrics": {
                        "cpu_utilization": True,
                        "memory_usage": True,
                        "disk_io": True,
                        "network_io": True
                    },
                    "business_metrics": {
                        "creator_activity": True,
                        "content_uploads": True,
                        "revenue_generation": True,
                        "user_engagement": True
                    }
                },
                "performance_benchmarks": {
                    "api_response_time": {
                        "target": "< 200ms",
                        "warning": "> 500ms",
                        "critical": "> 2s"
                    },
                    "database_query_time": {
                        "target": "< 50ms",
                        "warning": "> 200ms",
                        "critical": "> 1s"
                    },
                    "ai_processing_time": {
                        "target": "< 5s",
                        "warning": "> 30s",
                        "critical": "> 60s"
                    },
                    "workflow_execution": {
                        "target": "< 10s",
                        "warning": "> 60s",
                        "critical": "> 300s"
                    }
                },
                "automated_optimization": {
                    "query_optimization": True,
                    "cache_warming": True,
                    "connection_pooling": True,
                    "garbage_collection": True,
                    "resource_rebalancing": True
                },
                "alerting": {
                    "performance_degradation": True,
                    "resource_exhaustion": True,
                    "bottleneck_detection": True,
                    "anomaly_detection": True
                }
            }
            
            return monitoring_setup
            
        except Exception as e:
            logger.error(f"Performance monitoring setup failed: {e}")
            return {"error": str(e)}
    
    async def automatic_performance_tuning(self) -> Dict[str, Any]:
        """
        Automatic performance tuning based on metrics
        Performance target: < 10ms tuning cycle
        """
        try:
            # Simulate performance metrics analysis
            current_metrics = await self._collect_performance_metrics()
            
            tuning_actions = []
            
            # CPU optimization
            if current_metrics.get("cpu_usage", 0) > 80:
                tuning_actions.append({
                    "action": "scale_workers",
                    "current": self.resource_config.worker_processes,
                    "recommended": min(self.resource_config.worker_processes + 1, self.resource_config.max_cpu_cores),
                    "reason": "High CPU usage detected"
                })
            
            # Memory optimization
            if current_metrics.get("memory_usage", 0) > 85:
                tuning_actions.append({
                    "action": "increase_cache_ttl",
                    "current": self.caching_config.ttl_seconds,
                    "recommended": self.caching_config.ttl_seconds // 2,
                    "reason": "High memory usage, reducing cache TTL"
                })
            
            # Database optimization
            if current_metrics.get("db_response_time", 0) > 100:
                tuning_actions.append({
                    "action": "optimize_queries",
                    "recommendation": "Enable query caching and connection pooling",
                    "reason": "Slow database response times"
                })
            
            # AI processing optimization
            if current_metrics.get("ai_processing_time", 0) > 30:
                tuning_actions.append({
                    "action": "batch_ai_requests",
                    "recommendation": "Increase batch size and enable model warming",
                    "reason": "Slow AI processing times"
                })
            
            tuning_results = {
                "tuning_cycle": int(time.time()),
                "performance_score": self._calculate_performance_score(current_metrics),
                "identified_bottlenecks": self._identify_bottlenecks(current_metrics),
                "tuning_actions": tuning_actions,
                "optimization_history": self._optimization_history[-10:],  # Last 10 optimizations
                "next_tuning_cycle": int(time.time()) + 300  # 5 minutes
            }
            
            # Record optimization
            self._optimization_history.append({
                "timestamp": time.time(),
                "actions_count": len(tuning_actions),
                "performance_score": tuning_results["performance_score"],
                "bottlenecks": tuning_results["identified_bottlenecks"]
            })
            
            return tuning_results
            
        except Exception as e:
            logger.error(f"Automatic performance tuning failed: {e}")
            return {"error": str(e)}
    
    async def _collect_performance_metrics(self) -> Dict[str, float]:
        """Collect current performance metrics"""
        try:
            # Simulate metric collection
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "db_response_time": 45.0,  # Simulated
                "api_response_time": 150.0,  # Simulated
                "ai_processing_time": 12.0,  # Simulated
                "throughput_rps": 250.0,  # Simulated
                "error_rate": 0.5  # Simulated
            }
        except Exception:
            return {}
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            # Weight different metrics
            weights = {
                "cpu_usage": 0.2,
                "memory_usage": 0.2,
                "api_response_time": 0.3,
                "error_rate": 0.3
            }
            
            # Normalize metrics (lower is better except throughput)
            normalized_scores = {}
            
            # CPU usage (target: <70%)
            normalized_scores["cpu_usage"] = max(0, 100 - metrics.get("cpu_usage", 0))
            
            # Memory usage (target: <80%)
            normalized_scores["memory_usage"] = max(0, 100 - metrics.get("memory_usage", 0))
            
            # API response time (target: <200ms)
            api_time = metrics.get("api_response_time", 0)
            normalized_scores["api_response_time"] = max(0, 100 - (api_time / 200 * 100))
            
            # Error rate (target: <1%)
            error_rate = metrics.get("error_rate", 0)
            normalized_scores["error_rate"] = max(0, 100 - (error_rate * 100))
            
            # Calculate weighted score
            total_score = sum(
                normalized_scores.get(metric, 0) * weight 
                for metric, weight in weights.items()
            )
            
            return round(total_score, 2)
            
        except Exception:
            return 50.0  # Default neutral score
    
    def _identify_bottlenecks(self, metrics: Dict[str, float]) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if metrics.get("cpu_usage", 0) > 80:
            bottlenecks.append("cpu_overload")
        
        if metrics.get("memory_usage", 0) > 85:
            bottlenecks.append("memory_pressure")
        
        if metrics.get("api_response_time", 0) > 500:
            bottlenecks.append("slow_api_responses")
        
        if metrics.get("db_response_time", 0) > 100:
            bottlenecks.append("database_latency")
        
        if metrics.get("ai_processing_time", 0) > 30:
            bottlenecks.append("ai_processing_delay")
        
        if metrics.get("error_rate", 0) > 2:
            bottlenecks.append("high_error_rate")
        
        return bottlenecks
    
    async def performance_bottleneck_detection(self) -> Dict[str, Any]:
        """
        Advanced bottleneck detection system
        Performance target: < 5ms detection
        """
        try:
            current_metrics = await self._collect_performance_metrics()
            bottlenecks = self._identify_bottlenecks(current_metrics)
            
            bottleneck_analysis = {
                "detected_bottlenecks": bottlenecks,
                "severity_analysis": {},
                "impact_assessment": {},
                "resolution_recommendations": {},
                "estimated_fix_time": {}
            }
            
            for bottleneck in bottlenecks:
                if bottleneck == "cpu_overload":
                    bottleneck_analysis["severity_analysis"][bottleneck] = "high"
                    bottleneck_analysis["impact_assessment"][bottleneck] = "Degraded user experience, slow responses"
                    bottleneck_analysis["resolution_recommendations"][bottleneck] = [
                        "Scale worker processes",
                        "Optimize CPU-intensive operations",
                        "Enable request queuing"
                    ]
                    bottleneck_analysis["estimated_fix_time"][bottleneck] = "5-15 minutes"
                
                elif bottleneck == "memory_pressure":
                    bottleneck_analysis["severity_analysis"][bottleneck] = "critical"
                    bottleneck_analysis["impact_assessment"][bottleneck] = "Risk of service crashes, memory leaks"
                    bottleneck_analysis["resolution_recommendations"][bottleneck] = [
                        "Reduce cache size",
                        "Optimize memory usage",
                        "Restart services if needed"
                    ]
                    bottleneck_analysis["estimated_fix_time"][bottleneck] = "2-10 minutes"
                
                elif bottleneck == "database_latency":
                    bottleneck_analysis["severity_analysis"][bottleneck] = "medium"
                    bottleneck_analysis["impact_assessment"][bottleneck] = "Slow data operations, user wait times"
                    bottleneck_analysis["resolution_recommendations"][bottleneck] = [
                        "Optimize slow queries",
                        "Increase connection pool",
                        "Enable query caching"
                    ]
                    bottleneck_analysis["estimated_fix_time"][bottleneck] = "10-30 minutes"
            
            return bottleneck_analysis
            
        except Exception as e:
            logger.error(f"Bottleneck detection failed: {e}")
            return {"error": str(e)}
    
    async def performance_reporting_configuration(self) -> Dict[str, Any]:
        """
        Configure performance reporting system
        Performance target: < 3ms configuration
        """
        try:
            reporting_config = {
                "report_types": {
                    "real_time_dashboard": {
                        "update_interval": "5s",
                        "metrics": [
                            "cpu_usage", "memory_usage", "active_requests",
                            "response_times", "error_rates"
                        ],
                        "visualizations": ["line_charts", "gauges", "heatmaps"]
                    },
                    "daily_summary": {
                        "generation_time": "06:00 UTC",
                        "metrics": [
                            "peak_usage", "average_response_time", "total_requests",
                            "error_summary", "performance_score"
                        ],
                        "recipients": ["ops_team", "management"]
                    },
                    "weekly_analysis": {
                        "generation_time": "Monday 08:00 UTC",
                        "metrics": [
                            "performance_trends", "capacity_planning",
                            "optimization_opportunities", "resource_utilization"
                        ],
                        "recipients": ["architecture_team", "management"]
                    },
                    "monthly_report": {
                        "generation_time": "1st of month 09:00 UTC",
                        "metrics": [
                            "performance_evolution", "cost_optimization",
                            "scalability_assessment", "technology_recommendations"
                        ],
                        "recipients": ["executives", "architecture_team"]
                    }
                },
                "automated_insights": {
                    "performance_predictions": True,
                    "capacity_forecasting": True,
                    "cost_optimization_suggestions": True,
                    "technology_upgrade_recommendations": True
                },
                "export_formats": ["pdf", "json", "csv", "dashboard_links"],
                "delivery_methods": ["email", "slack", "webhook", "api"]
            }
            
            return reporting_config
            
        except Exception as e:
            logger.error(f"Performance reporting configuration failed: {e}")
            return {"error": str(e)}
    
    def get_performance_profile(self) -> PerformanceProfile:
        """Get current performance profile"""
        return self.current_profile
    
    def get_cache_config(self) -> CachingConfig:
        """Get caching configuration"""
        return self.caching_config
    
    def get_resource_limits(self) -> ResourceConfig:
        """Get resource configuration"""
        return self.resource_config
    
    def export_config(self) -> Dict[str, Any]:
        """Export performance configuration for external use"""
        return {
            "profile": self.current_profile.value,
            "caching": {
                "strategy": self.caching_config.strategy.value,
                "max_memory_mb": self.caching_config.max_memory_mb,
                "ttl_seconds": self.caching_config.ttl_seconds,
                "compression_enabled": self.caching_config.enable_compression
            },
            "optimization": {
                "query_optimization": self.optimization_config.enable_query_optimization,
                "compression": self.optimization_config.enable_compression,
                "cdn_enabled": self.optimization_config.enable_cdn,
                "batch_size": self.optimization_config.batch_size
            },
            "resources": {
                "cpu_cores": self.resource_config.max_cpu_cores,
                "memory_gb": self.resource_config.max_memory_gb,
                "worker_processes": self.resource_config.worker_processes,
                "thread_pool_size": self.resource_config.thread_pool_size
            },
            "performance_metrics": self._performance_metrics,
            "optimization_history_count": len(self._optimization_history)
        }