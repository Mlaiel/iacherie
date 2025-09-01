"""Performance & Optimization Configuration Module

Advanced performance tuning, caching strategies, and optimization settings
for the IA Influencer Agent enterprise platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected intellectual property. Unauthorized use is prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """
Caching strategies"""

    NO_CACHE = "no_cache"
    MEMORY_CACHE = "memory_cache"
    REDIS_CACHE = "redis_cache"
    DISTRIBUTED_CACHE = "distributed_cache"
    HYBRID_CACHE = "hybrid_cache"
    CDN_CACHE = "cdn_cache"


class OptimizationLevel(Enum):
    """Optimization levels"""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


class CompressionType(Enum):
    """Compression types"""

    NONE = "none"
    GZIP = "gzip"
    BROTLI = "brotli"
    LZ4 = "lz4"
    SNAPPY = "snappy"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"


@dataclass
class CacheConfig:
    """Advanced caching configuration"""
    
    # General cache settings
    enabled: bool = True
    strategy: CacheStrategy = CacheStrategy.HYBRID_CACHE
    default_ttl_seconds: int = 3600
    max_cache_size_mb: int = 1024
    
    # Memory cache
    memory_cache_size_mb: int = 256
    memory_cache_max_entries: int = 10000
    memory_cache_eviction_policy: str = "lru"  # lru, lfu, fifo
    
    # Redis cache
    redis_enabled: bool = True
    redis_host: str = "redis-cache"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_database: int = 0
    redis_connection_pool_size: int = 50
    redis_timeout_seconds: int = 5
    
    # Distributed cache
    distributed_cache_enabled: bool = True
    distributed_cache_nodes: List[str] = field(default_factory=lambda: ["cache-node-1", "cache-node-2", "cache-node-3"])
    distributed_cache_replication: int = 2
    distributed_cache_consistency: str = "eventual"  # eventual, strong
    
    # CDN cache
    cdn_cache_enabled: bool = True
    cdn_provider: str = "cloudflare"
    cdn_cache_ttl_seconds: int = 86400  # 24 hours
    cdn_purge_on_update: bool = True
    
    # Content-specific caching
    api_response_cache_ttl: int = 300  # 5 minutes
    static_content_cache_ttl: int = 86400  # 24 hours
    dynamic_content_cache_ttl: int = 300  # 5 minutes
    user_data_cache_ttl: int = 1800  # 30 minutes
    ai_model_cache_ttl: int = 3600  # 1 hour
    
    # Cache warming
    cache_warming_enabled: bool = True
    cache_warming_schedule: str = "0 2 * * *"  # Daily at 2 AM
    cache_warming_endpoints: List[str] = field(default_factory=lambda: [
        "/api/v1/popular-content",
        "/api/v1/trending-creators",
        "/api/v1/featured-content"
    ])
    
    # Cache invalidation
    intelligent_invalidation: bool = True
    cascade_invalidation: bool = True
    tag_based_invalidation: bool = True
    
    # Performance monitoring
    cache_hit_rate_target: float = 0.85
    cache_miss_alert_threshold: float = 0.3
    cache_performance_monitoring: bool = True


@dataclass
class DatabaseOptimizationConfig:
    """Database performance optimization"""
    
    # Connection pooling
    connection_pool_enabled: bool = True
    max_connections: int = 100
    min_connections: int = 10
    connection_timeout_seconds: int = 30
    idle_timeout_seconds: int = 600
    
    # Query optimization
    query_cache_enabled: bool = True
    query_cache_size_mb: int = 512
    prepared_statements: bool = True
    query_timeout_seconds: int = 60
    
    # Indexing strategy
    auto_indexing: bool = True
    index_maintenance_enabled: bool = True
    index_usage_monitoring: bool = True
    unused_index_cleanup: bool = True
    
    # Read replicas
    read_replicas_enabled: bool = True
    read_replica_count: int = 3
    read_write_split: bool = True
    replica_lag_monitoring: bool = True
    
    # Partitioning
    table_partitioning: bool = True
    partition_strategy: str = "date_based"  # date_based, hash_based, range_based
    partition_retention_days: int = 365
    
    # Compression
    table_compression: bool = True
    compression_algorithm: str = "lz4"
    compression_level: int = 3
    
    # Vacuum and maintenance
    auto_vacuum: bool = True
    vacuum_schedule: str = "0 3 * * 0"  # Weekly on Sunday at 3 AM
    analyze_schedule: str = "0 4 * * *"  # Daily at 4 AM
    
    # Performance monitoring
    slow_query_log: bool = True
    slow_query_threshold_seconds: float = 2.0
    query_performance_monitoring: bool = True
    deadlock_monitoring: bool = True


@dataclass
class APIOptimizationConfig:
    """API performance optimization"""
    
    # Rate limiting
    rate_limiting_enabled: bool = True
    global_rate_limit_per_minute: int = 60000
    user_rate_limit_per_minute: int = 1000
    burst_limit: int = 100
    rate_limit_strategy: str = "sliding_window"  # fixed_window, sliding_window, token_bucket
    
    # Request optimization
    request_compression: bool = True
    compression_type: CompressionType = CompressionType.BROTLI
    compression_threshold_bytes: int = 1024
    
    # Response optimization
    response_compression: bool = True
    response_streaming: bool = True
    chunked_transfer_encoding: bool = True
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    cursor_based_pagination: bool = True
    
    # Batching
    batch_requests_enabled: bool = True
    max_batch_size: int = 50
    batch_timeout_seconds: int = 10
    
    # Keep-alive
    keep_alive_enabled: bool = True
    keep_alive_timeout_seconds: int = 300
    max_keep_alive_requests: int = 1000
    
    # HTTP/2 and HTTP/3
    http2_enabled: bool = True
    http3_enabled: bool = True
    server_push_enabled: bool = True
    
    # API versioning
    version_header_required: bool = True
    deprecation_warnings: bool = True
    version_sunset_notifications: bool = True


@dataclass
class ContentDeliveryConfig:
    """Content delivery optimization"""
    
    # CDN settings
    cdn_enabled: bool = True
    cdn_provider: str = "cloudflare"
    global_cdn: bool = True
    edge_locations: List[str] = field(default_factory=lambda: [
        "us-east-1", "us-west-1", "eu-west-1", "eu-central-1",
        "ap-southeast-1", "ap-northeast-1"
    ])
    
    # Image optimization
    image_optimization: bool = True
    webp_conversion: bool = True
    avif_conversion: bool = True
    responsive_images: bool = True
    image_lazy_loading: bool = True
    
    # Video optimization
    video_optimization: bool = True
    adaptive_bitrate_streaming: bool = True
    video_transcoding: bool = True
    video_compression: CompressionType = CompressionType.BROTLI
    
    # Audio optimization
    audio_optimization: bool = True
    audio_compression_enabled: bool = True
    audio_format_conversion: bool = True
    
    # Static asset optimization
    asset_bundling: bool = True
    asset_minification: bool = True
    css_minification: bool = True
    js_minification: bool = True
    
    # Cache control
    static_cache_max_age_seconds: int = 31536000  # 1 year
    dynamic_cache_max_age_seconds: int = 300  # 5 minutes
    no_cache_endpoints: List[str] = field(default_factory=lambda: [
        "/api/v1/auth",
        "/api/v1/user/profile",
        "/api/v1/payments"
    ])


@dataclass
class LoadBalancingConfig:
    """Load balancing optimization"""
    
    # Strategy
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_RESPONSE_TIME
    
    # Health checks
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 10
    health_check_retries: int = 3
    
    # Session affinity
    session_affinity_enabled: bool = False
    affinity_cookie_name: str = "ia_session"
    affinity_duration_seconds: int = 3600
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    half_open_max_calls: int = 3
    
    # Auto scaling
    auto_scaling_enabled: bool = True
    min_instances: int = 2
    max_instances: int = 20
    scale_up_threshold: float = 0.7  # 70% CPU
    scale_down_threshold: float = 0.3  # 30% CPU
    scale_up_cooldown_seconds: int = 300
    scale_down_cooldown_seconds: int = 600
    
    # Geographic distribution
    geo_routing_enabled: bool = True
    geo_failover_enabled: bool = True
    latency_based_routing: bool = True


@dataclass
class ResourceOptimizationConfig:
    """System resource optimization"""
    
    # CPU optimization
    cpu_optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    cpu_affinity_enabled: bool = True
    numa_awareness: bool = True
    cpu_scaling_governor: str = "performance"  # performance, powersave, ondemand
    
    # Memory optimization
    memory_optimization_enabled: bool = True
    memory_pool_size_mb: int = 2048
    garbage_collection_tuning: bool = True
    memory_leak_detection: bool = True
    
    # I/O optimization
    async_io_enabled: bool = True
    io_queue_depth: int = 32
    disk_read_ahead_kb: int = 256
    disk_scheduler: str = "mq-deadline"  # mq-deadline, bfq, kyber
    
    # Network optimization
    network_buffer_size_kb: int = 64
    tcp_congestion_control: str = "bbr"  # bbr, cubic, reno
    tcp_window_scaling: bool = True
    tcp_fast_open: bool = True
    
    # Process optimization
    worker_processes: int = 0  # 0 = auto-detect CPU cores
    worker_connections: int = 1024
    process_priority: int = 0  # -20 to 19
    resource_limits_enabled: bool = True


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    
    # Metrics collection
    metrics_enabled: bool = True
    metrics_interval_seconds: int = 60
    detailed_metrics: bool = True
    
    # Performance metrics
    response_time_monitoring: bool = True
    throughput_monitoring: bool = True
    error_rate_monitoring: bool = True
    resource_usage_monitoring: bool = True
    
    # Alerting thresholds
    response_time_alert_ms: int = 1000
    error_rate_alert_percent: float = 5.0
    cpu_usage_alert_percent: float = 80.0
    memory_usage_alert_percent: float = 85.0
    disk_usage_alert_percent: float = 90.0
    
    # Performance profiling
    profiling_enabled: bool = True
    profiling_sample_rate: float = 0.01  # 1%
    continuous_profiling: bool = True
    
    # Benchmarking
    benchmark_testing: bool = True
    load_testing_schedule: str = "0 1 * * 0"  # Weekly on Sunday at 1 AM
    performance_regression_detection: bool = True


@dataclass
class OptimizationConfig:
    """Master optimization configuration"""
    
    # Core settings
    enabled: bool = True
    optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    
    # Configuration components
    cache: CacheConfig = field(default_factory=CacheConfig)
    database: DatabaseOptimizationConfig = field(default_factory=DatabaseOptimizationConfig)
    api: APIOptimizationConfig = field(default_factory=APIOptimizationConfig)
    content_delivery: ContentDeliveryConfig = field(default_factory=ContentDeliveryConfig)
    load_balancing: LoadBalancingConfig = field(default_factory=LoadBalancingConfig)
    resource: ResourceOptimizationConfig = field(default_factory=ResourceOptimizationConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Global optimization settings
    performance_mode: bool = True
    power_efficiency_mode: bool = False
    cost_optimization_mode: bool = False
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """
Get comprehensive optimization summary"""
        return {
            "optimization_level": self.optimization_level.value,
            "performance_mode": self.performance_mode,
            "cache": {
                "enabled": self.cache.enabled,
                "strategy": self.cache.strategy.value,
                "hit_rate_target": self.cache.cache_hit_rate_target,
                "size_mb": self.cache.max_cache_size_mb
            },
            "database": {
                "connection_pooling": self.database.connection_pool_enabled,
                "read_replicas": self.database.read_replica_count,
                "query_cache": self.database.query_cache_enabled
            },
            "api": {
                "rate_limiting": self.api.rate_limiting_enabled,
                "compression": self.api.response_compression,
                "http2": self.api.http2_enabled
            },
            "content_delivery": {
                "cdn_enabled": self.content_delivery.cdn_enabled,
                "image_optimization": self.content_delivery.image_optimization,
                "video_optimization": self.content_delivery.video_optimization
            },
            "load_balancing": {
                "strategy": self.load_balancing.strategy.value,
                "auto_scaling": self.load_balancing.auto_scaling_enabled,
                "health_checks": self.load_balancing.health_check_enabled
            }
        }
    
    def optimize_for_workload(self, workload_type: str) -> Dict[str, Any]:
        """Optimize configuration for specific workload type"""
        
        optimizations = {}
        
        if workload_type == "high_throughput":
            # Optimize for high throughput
            self.cache.strategy = CacheStrategy.DISTRIBUTED_CACHE
            self.api.global_rate_limit_per_minute = 120000
            self.load_balancing.strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
            self.resource.worker_processes = 0  # Auto-detect
            optimizations["throughput_optimized"] = True
            
        elif workload_type == "low_latency":
            # Optimize for low latency
            self.cache.strategy = CacheStrategy.MEMORY_CACHE
            self.api.keep_alive_enabled = True
            self.load_balancing.strategy = LoadBalancingStrategy.LEAST_RESPONSE_TIME
            self.resource.cpu_optimization_level = OptimizationLevel.MAXIMUM
            optimizations["latency_optimized"] = True
            
        elif workload_type == "content_heavy":
            # Optimize for content delivery
            self.content_delivery.cdn_enabled = True
            self.content_delivery.image_optimization = True
            self.content_delivery.video_optimization = True
            self.cache.cdn_cache_enabled = True
            optimizations["content_optimized"] = True
            
        elif workload_type == "ai_processing":
            # Optimize for AI workloads
            self.resource.memory_pool_size_mb = 8192
            self.resource.cpu_optimization_level = OptimizationLevel.MAXIMUM
            self.cache.ai_model_cache_ttl = 7200  # 2 hours
            self.api.rate_limiting_enabled = False  # For batch processing
            optimizations["ai_optimized"] = True
        
        return optimizations
    
    def validate_configuration(self) -> List[str]:
        """Validate optimization configuration"""
        issues = []
        
        # Cache validation
        if self.cache.enabled and self.cache.max_cache_size_mb < 64:
            issues.append("Cache size too small for effective caching")
        
        # Database validation
        if self.database.max_connections < 10:
            issues.append("Database connection pool too small")
        
        # API validation
        if self.api.global_rate_limit_per_minute < 1000:
            issues.append("Global rate limit too restrictive")
        
        # Resource validation
        if self.resource.worker_processes < 0:
            issues.append("Invalid worker process configuration")
        
        return issues


# Create global optimization configuration
optimization_config = OptimizationConfig()

# Export all components
__all__ = [
    'CacheStrategy',
    'OptimizationLevel',
    'CompressionType',
    'LoadBalancingStrategy',
    'CacheConfig',
    'DatabaseOptimizationConfig',
    'APIOptimizationConfig',
    'ContentDeliveryConfig',
    'LoadBalancingConfig',
    'ResourceOptimizationConfig',
    'MonitoringConfig',
    'OptimizationConfig',
    'optimization_config'
]
