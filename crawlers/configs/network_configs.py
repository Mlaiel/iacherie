"""
Network and Performance Configurations
======================================

Advanced network configuration system for crawlers with performance optimization,
rate limiting, proxy management, and anti-detection mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class ProxyType(Enum):
    """Types of proxy connections."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"

class UserAgentType(Enum):
    """Types of user agents."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"
    MOBILE_CHROME = "mobile_chrome"
    MOBILE_SAFARI = "mobile_safari"
    MOBILE_FIREFOX = "mobile_firefox"

class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED = "fixed"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    ADAPTIVE = "adaptive"
    BURST_THEN_THROTTLE = "burst_then_throttle"
    RESPECTFUL = "respectful"

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"
    HASH_BASED = "hash_based"

class CacheStrategy(Enum):
    """Caching strategies."""
    NO_CACHE = "no_cache"
    MEMORY_ONLY = "memory_only"
    DISK_ONLY = "disk_only"
    HYBRID = "hybrid"
    REDIS = "redis"
    MEMCACHED = "memcached"

@dataclass
class ProxyServerConfig:
    """Configuration for individual proxy server."""
    host: str
    port: int
    proxy_type: ProxyType
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    provider: Optional[str] = None
    speed_mbps: Optional[float] = None
    reliability_score: float = 1.0
    last_used: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    avg_response_time_ms: float = 0.0
    enabled: bool = True

@dataclass
class ProxyRotationConfig:
    """Configuration for proxy rotation."""
    enabled: bool = True
    rotation_strategy: str = "round_robin"  # round_robin, random, least_used
    rotation_interval_requests: int = 100
    rotation_interval_minutes: int = 60
    
    # Health checking
    health_check_enabled: bool = True
    health_check_interval_minutes: int = 15
    health_check_timeout_seconds: int = 10
    health_check_url: str = "https://httpbin.org/ip"
    
    # Failure handling
    max_failures_before_disable: int = 5
    retry_disabled_after_minutes: int = 60
    blacklist_on_consecutive_failures: int = 10
    
    # Performance optimization
    concurrent_health_checks: int = 10
    prefer_faster_proxies: bool = True
    speed_weight: float = 0.3
    reliability_weight: float = 0.7

@dataclass
class UserAgentRotationConfig:
    """Configuration for user agent rotation."""
    enabled: bool = True
    rotation_strategy: str = "random"  # random, sequential, weighted
    rotation_interval_requests: int = 50
    
    # User agent types
    desktop_enabled: bool = True
    mobile_enabled: bool = True
    tablet_enabled: bool = False
    
    # Browser distribution (percentages)
    chrome_percentage: float = 0.65
    firefox_percentage: float = 0.15
    safari_percentage: float = 0.10
    edge_percentage: float = 0.08
    other_percentage: float = 0.02
    
    # Version management
    use_latest_versions: bool = True
    include_beta_versions: bool = False
    version_randomization: bool = True
    
    # Custom user agents
    custom_agents: List[str] = field(default_factory=list)
    custom_weight: float = 0.1

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE
    
    # Basic limits
    requests_per_second: float = 1.0
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 86400
    
    # Burst handling
    burst_enabled: bool = True
    burst_limit: int = 10
    burst_window_seconds: int = 60
    
    # Backoff configuration
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 300.0
    backoff_factor: float = 2.0
    jitter_enabled: bool = True
    jitter_percentage: float = 0.1
    
    # Adaptive settings
    adaptive_enabled: bool = True
    success_rate_threshold: float = 0.95
    error_rate_threshold: float = 0.05
    adaptation_window_minutes: int = 10
    
    # Respectful crawling
    respect_robots_txt: bool = True
    respect_429_headers: bool = True
    respect_retry_after: bool = True
    default_crawl_delay: float = 1.0

@dataclass
class ConnectionConfig:
    """Configuration for network connections."""
    # Timeouts
    connect_timeout_seconds: int = 30
    read_timeout_seconds: int = 60
    total_timeout_seconds: int = 300
    
    # Connection pooling
    pool_connections: int = 100
    pool_maxsize: int = 100
    pool_block: bool = False
    
    # Retry configuration
    max_retries: int = 3
    retry_on_timeout: bool = True
    retry_on_connection_error: bool = True
    retry_on_http_error: bool = False
    retry_backoff_factor: float = 0.3
    
    # Keep-alive
    keep_alive: bool = True
    keep_alive_timeout: int = 5
    
    # SSL/TLS
    verify_ssl: bool = True
    ssl_version: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None
    
    # Headers
    default_headers: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    # Compression
    compression_enabled: bool = True
    compression_threshold: int = 1024

@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing."""
    enabled: bool = True
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_CONNECTIONS
    
    # Health checking
    health_check_enabled: bool = True
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 10
    health_check_path: str = "/health"
    
    # Failover
    failover_enabled: bool = True
    max_failures_before_failover: int = 3
    failover_timeout_seconds: int = 60
    
    # Session affinity
    session_affinity_enabled: bool = False
    affinity_duration_minutes: int = 60
    
    # Weights (for weighted strategies)
    server_weights: Dict[str, float] = field(default_factory=dict)

@dataclass
class CachingConfig:
    """Configuration for response caching."""
    enabled: bool = True
    strategy: CacheStrategy = CacheStrategy.HYBRID
    
    # Memory cache
    memory_cache_size_mb: int = 512
    memory_cache_ttl_seconds: int = 3600
    
    # Disk cache
    disk_cache_enabled: bool = True
    disk_cache_path: str = "./cache"
    disk_cache_size_gb: int = 10
    disk_cache_ttl_hours: int = 24
    
    # Redis cache
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ttl_seconds: int = 3600
    
    # Cache policies
    cache_get_requests: bool = True
    cache_post_requests: bool = False
    cache_authenticated_requests: bool = False
    cache_error_responses: bool = False
    
    # Cache keys
    include_headers_in_key: List[str] = field(default_factory=lambda: ["User-Agent"])
    include_params_in_key: bool = True
    
    # Compression
    compress_cached_responses: bool = True
    compression_threshold_bytes: int = 1024

@dataclass
class SecurityConfig:
    """Configuration for security features."""
    # Anti-detection
    anti_detection_enabled: bool = True
    randomize_request_order: bool = True
    simulate_human_behavior: bool = True
    mouse_movement_simulation: bool = False
    typing_speed_variation: bool = False
    
    # Fingerprinting resistance
    resist_fingerprinting: bool = True
    randomize_viewport_size: bool = True
    randomize_screen_resolution: bool = True
    randomize_timezone: bool = True
    randomize_language: bool = False
    
    # Request headers
    randomize_headers: bool = True
    add_noise_headers: bool = True
    mimic_browser_behavior: bool = True
    
    # Rate limiting evasion
    distributed_crawling: bool = False
    request_spacing_variance: float = 0.3
    session_rotation_enabled: bool = True
    session_rotation_interval_minutes: int = 30
    
    # Monitoring detection
    detect_rate_limiting: bool = True
    detect_captchas: bool = True
    detect_bot_detection: bool = True
    automatic_evasion: bool = True

@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    # Concurrency
    max_concurrent_requests: int = 50
    max_concurrent_requests_per_domain: int = 5
    concurrent_crawlers: int = 10
    
    # Threading
    use_async: bool = True
    thread_pool_size: int = 20
    process_pool_size: int = 4
    
    # Memory management
    max_memory_usage_mb: int = 2048
    garbage_collection_enabled: bool = True
    gc_interval_requests: int = 1000
    
    # Resource limits
    max_response_size_mb: int = 100
    max_download_time_seconds: int = 300
    max_redirects: int = 10
    
    # Optimization features
    compression_enabled: bool = True
    persistent_connections: bool = True
    http2_enabled: bool = True
    
    # Monitoring
    performance_monitoring: bool = True
    detailed_metrics: bool = True
    profiling_enabled: bool = False

@dataclass
class NetworkConfig:
    """Complete network configuration."""
    # Core configurations
    proxy_rotation: ProxyRotationConfig = field(default_factory=ProxyRotationConfig)
    user_agent_rotation: UserAgentRotationConfig = field(default_factory=UserAgentRotationConfig)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    load_balancing: LoadBalancingConfig = field(default_factory=LoadBalancingConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Proxy servers
    proxy_servers: List[ProxyServerConfig] = field(default_factory=list)
    
    # Global settings
    enabled: bool = True
    debug_mode: bool = False
    verbose_logging: bool = False
    
    # Environment-specific settings
    development_mode: bool = False
    production_optimizations: bool = True
    testing_mode: bool = False

class NetworkConfigManager:
    """Manager for network configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize network config manager."""
        self.config_dir = Path(config_dir or os.getenv("NETWORK_CONFIG_DIR", "./configs"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> NetworkConfig:
        """Load default network configuration."""
        return NetworkConfig(
            proxy_rotation=ProxyRotationConfig(
                enabled=True,
                rotation_strategy="round_robin",
                health_check_enabled=True,
                max_failures_before_disable=3
            ),
            user_agent_rotation=UserAgentRotationConfig(
                enabled=True,
                rotation_strategy="random",
                desktop_enabled=True,
                mobile_enabled=True
            ),
            rate_limiting=RateLimitConfig(
                strategy=RateLimitStrategy.ADAPTIVE,
                requests_per_second=1.0,
                adaptive_enabled=True,
                respect_robots_txt=True
            ),
            connection=ConnectionConfig(
                connect_timeout_seconds=30,
                read_timeout_seconds=60,
                max_retries=3,
                keep_alive=True
            ),
            caching=CachingConfig(
                enabled=True,
                strategy=CacheStrategy.HYBRID,
                memory_cache_size_mb=512,
                disk_cache_enabled=True
            ),
            security=SecurityConfig(
                anti_detection_enabled=True,
                resist_fingerprinting=True,
                randomize_headers=True
            ),
            performance=PerformanceConfig(
                max_concurrent_requests=50,
                use_async=True,
                compression_enabled=True
            ),
            proxy_servers=[
                # Example proxy configurations would be loaded from environment
            ]
        )
    
    def add_proxy_server(self, proxy: ProxyServerConfig) -> None:
        """Add proxy server to configuration."""
        self.config.proxy_servers.append(proxy)
        self.save_config()
    
    def remove_proxy_server(self, host: str, port: int) -> None:
        """Remove proxy server from configuration."""
        self.config.proxy_servers = [
            proxy for proxy in self.config.proxy_servers
            if not (proxy.host == host and proxy.port == port)
        ]
        self.save_config()
    
    def get_active_proxies(self) -> List[ProxyServerConfig]:
        """Get list of active proxy servers."""
        return [proxy for proxy in self.config.proxy_servers if proxy.enabled]
    
    def update_proxy_stats(self, host: str, port: int, success: bool, response_time_ms: float) -> None:
        """Update proxy statistics."""
        for proxy in self.config.proxy_servers:
            if proxy.host == host and proxy.port == port:
                if success:
                    proxy.success_count += 1
                    proxy.failure_count = 0  # Reset failure count on success
                else:
                    proxy.failure_count += 1
                
                # Update average response time
                if proxy.success_count > 0:
                    proxy.avg_response_time_ms = (
                        (proxy.avg_response_time_ms * (proxy.success_count - 1) + response_time_ms) 
                        / proxy.success_count
                    )
                
                proxy.last_used = datetime.now()
                
                # Disable proxy if too many failures
                if proxy.failure_count >= self.config.proxy_rotation.max_failures_before_disable:
                    proxy.enabled = False
                
                break
    
    def get_config(self) -> NetworkConfig:
        """Get current network configuration."""
        return self.config
    
    def update_config(self, config: NetworkConfig) -> None:
        """Update network configuration."""
        self.config = config
        self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_file = self.config_dir / "network_config.json"
        # Convert dataclass to dict, handling datetime objects
        config_dict = self._serialize_config(self.config)
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def load_config(self) -> None:
        """Load configuration from file."""
        config_file = self.config_dir / "network_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                self.config = self._deserialize_config(data)
    
    def _serialize_config(self, config: NetworkConfig) -> dict:
        """Serialize configuration to dictionary."""
        # Implementation for converting dataclass to dict
        # Handle datetime and enum serialization
        pass
    
    def _deserialize_config(self, data: dict) -> NetworkConfig:
        """Deserialize configuration from dictionary."""
        # Implementation for converting dict back to NetworkConfig
        pass
    
    def validate_config(self) -> List[str]:
        """Validate network configuration."""
        errors = []
        
        # Validate rate limiting
        if self.config.rate_limiting.requests_per_second <= 0:
            errors.append("Requests per second must be positive")
        
        # Validate timeouts
        if self.config.connection.connect_timeout_seconds <= 0:
            errors.append("Connect timeout must be positive")
        
        # Validate proxy servers
        for i, proxy in enumerate(self.config.proxy_servers):
            if not proxy.host:
                errors.append(f"Proxy {i+1}: Host is required")
            if proxy.port <= 0 or proxy.port > 65535:
                errors.append(f"Proxy {i+1}: Invalid port number")
        
        # Validate performance settings
        if self.config.performance.max_concurrent_requests <= 0:
            errors.append("Max concurrent requests must be positive")
        
        return errors
    
    def get_optimal_settings_for_platform(self, platform: str) -> dict:
        """Get optimal network settings for specific platform."""
        platform_settings = {
            "youtube": {
                "rate_limit": {"requests_per_second": 0.5},
                "user_agent": {"prefer_desktop": True},
                "connection": {"timeout": 60}
            },
            "instagram": {
                "rate_limit": {"requests_per_second": 0.2},
                "user_agent": {"prefer_mobile": True},
                "security": {"anti_detection": True}
            },
            "tiktok": {
                "rate_limit": {"requests_per_second": 0.1},
                "security": {"resist_fingerprinting": True},
                "connection": {"timeout": 90}
            }
        }
        return platform_settings.get(platform, {})
    
    def export_config(self, file_path: str) -> None:
        """Export configuration to file."""
        config_dict = self._serialize_config(self.config)
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)

# Global network config manager instance
network_config_manager = NetworkConfigManager()
