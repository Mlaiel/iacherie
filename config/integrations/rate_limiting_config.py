"""
Rate Limiting Configuration Module for IA-Influencer Agent Platform
===================================================================

Professional rate limiting configuration for API protection and external service management.
Handles request throttling, quota management, and adaptive rate limiting strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, Any, Optional, List, Union, Tuple
from pydantic import BaseSettings, Field, validator
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class RateLimitScope(str, Enum):
    """Rate limiting scope levels."""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"
    PER_SERVICE = "per_service"


class RateLimitAction(str, Enum):
    """Actions to take when rate limit is exceeded."""
    REJECT = "reject"
    QUEUE = "queue"
    THROTTLE = "throttle"
    PRIORITIZE = "prioritize"
    ADAPTIVE_DELAY = "adaptive_delay"


class PriorityLevel(int, Enum):
    """Request priority levels."""
    EMERGENCY = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    name: str
    strategy: RateLimitStrategy
    scope: RateLimitScope
    requests_per_second: float
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_capacity: int
    window_size: int  # in seconds
    action: RateLimitAction = RateLimitAction.REJECT
    priority_level: PriorityLevel = PriorityLevel.NORMAL
    enabled: bool = True
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class QuotaConfig:
    """Quota configuration for external services."""
    service_name: str
    daily_quota: int
    hourly_quota: int
    minute_quota: int
    current_usage: int = 0
    reset_time: Optional[datetime] = None
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%


@dataclass
class BackoffConfig:
    """Backoff configuration for rate limiting."""
    initial_delay: float = 1.0
    max_delay: float = 300.0
    multiplier: float = 2.0
    jitter: bool = True
    max_retries: int = 3


class RateLimitingConfig(BaseSettings):
    """Rate limiting configuration for API protection and service management."""
    
    # === GLOBAL RATE LIMITING ===
    
    # Global rate limiting settings
    rate_limiting_enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    default_strategy: RateLimitStrategy = Field(default=RateLimitStrategy.SLIDING_WINDOW, env="DEFAULT_RATE_LIMIT_STRATEGY")
    global_requests_per_second: float = Field(default=100.0, env="GLOBAL_REQUESTS_PER_SECOND")
    global_requests_per_minute: int = Field(default=3000, env="GLOBAL_REQUESTS_PER_MINUTE")
    global_requests_per_hour: int = Field(default=100000, env="GLOBAL_REQUESTS_PER_HOUR")
    
    # Burst handling
    enable_burst_capacity: bool = Field(default=True, env="ENABLE_BURST_CAPACITY")
    default_burst_capacity: int = Field(default=200, env="DEFAULT_BURST_CAPACITY")
    burst_recovery_rate: float = Field(default=10.0, env="BURST_RECOVERY_RATE")  # tokens per second
    
    # === API ENDPOINT RATE LIMITING ===
    
    # Authentication endpoints
    auth_requests_per_minute: int = Field(default=60, env="AUTH_REQUESTS_PER_MINUTE")
    auth_requests_per_hour: int = Field(default=1000, env="AUTH_REQUESTS_PER_HOUR")
    auth_failed_attempts_limit: int = Field(default=5, env="AUTH_FAILED_ATTEMPTS_LIMIT")
    auth_lockout_duration: int = Field(default=900, env="AUTH_LOCKOUT_DURATION")  # 15 minutes
    
    # File upload endpoints
    upload_requests_per_minute: int = Field(default=10, env="UPLOAD_REQUESTS_PER_MINUTE")
    upload_requests_per_hour: int = Field(default=200, env="UPLOAD_REQUESTS_PER_HOUR")
    max_upload_size: int = Field(default=104857600, env="MAX_UPLOAD_SIZE")  # 100MB
    
    # Search endpoints
    search_requests_per_second: float = Field(default=5.0, env="SEARCH_REQUESTS_PER_SECOND")
    search_requests_per_minute: int = Field(default=100, env="SEARCH_REQUESTS_PER_MINUTE")
    
    # Analytics endpoints
    analytics_requests_per_minute: int = Field(default=30, env="ANALYTICS_REQUESTS_PER_MINUTE")
    analytics_requests_per_hour: int = Field(default=500, env="ANALYTICS_REQUESTS_PER_HOUR")
    
    # === EXTERNAL SERVICE RATE LIMITING ===
    
    # Spotify API limits
    spotify_requests_per_second: float = Field(default=10.0, env="SPOTIFY_REQUESTS_PER_SECOND")
    spotify_requests_per_hour: int = Field(default=30000, env="SPOTIFY_REQUESTS_PER_HOUR")
    spotify_burst_capacity: int = Field(default=50, env="SPOTIFY_BURST_CAPACITY")
    
    # YouTube API limits
    youtube_requests_per_second: float = Field(default=100.0, env="YOUTUBE_REQUESTS_PER_SECOND")
    youtube_daily_quota: int = Field(default=1000000, env="YOUTUBE_DAILY_QUOTA")
    youtube_quota_cost_per_request: int = Field(default=1, env="YOUTUBE_QUOTA_COST_PER_REQUEST")
    
    # Instagram API limits
    instagram_requests_per_hour: int = Field(default=200, env="INSTAGRAM_REQUESTS_PER_HOUR")
    instagram_requests_per_day: int = Field(default=5000, env="INSTAGRAM_REQUESTS_PER_DAY")
    
    # TikTok API limits
    tiktok_requests_per_second: float = Field(default=5.0, env="TIKTOK_REQUESTS_PER_SECOND")
    tiktok_requests_per_day: int = Field(default=10000, env="TIKTOK_REQUESTS_PER_DAY")
    
    # Twitter API limits
    twitter_requests_per_minute: int = Field(default=300, env="TWITTER_REQUESTS_PER_MINUTE")
    twitter_requests_per_hour: int = Field(default=18000, env="TWITTER_REQUESTS_PER_HOUR")
    
    # === PAYMENT API RATE LIMITING ===
    
    # Stripe API limits
    stripe_requests_per_second: float = Field(default=100.0, env="STRIPE_REQUESTS_PER_SECOND")
    stripe_read_requests_per_second: float = Field(default=100.0, env="STRIPE_READ_REQUESTS_PER_SECOND")
    stripe_write_requests_per_second: float = Field(default=100.0, env="STRIPE_WRITE_REQUESTS_PER_SECOND")
    
    # PayPal API limits
    paypal_requests_per_second: float = Field(default=20.0, env="PAYPAL_REQUESTS_PER_SECOND")
    paypal_requests_per_minute: int = Field(default=1000, env="PAYPAL_REQUESTS_PER_MINUTE")
    
    # === CONTENT PROTECTION LIMITS ===
    
    # Fingerprinting limits
    fingerprint_requests_per_second: float = Field(default=5.0, env="FINGERPRINT_REQUESTS_PER_SECOND")
    fingerprint_requests_per_hour: int = Field(default=10000, env="FINGERPRINT_REQUESTS_PER_HOUR")
    fingerprint_processing_timeout: int = Field(default=300, env="FINGERPRINT_PROCESSING_TIMEOUT")
    
    # Content scanning limits
    content_scan_requests_per_minute: int = Field(default=100, env="CONTENT_SCAN_REQUESTS_PER_MINUTE")
    content_scan_concurrent_limit: int = Field(default=20, env="CONTENT_SCAN_CONCURRENT_LIMIT")
    
    # === USER-BASED RATE LIMITING ===
    
    # Free tier limits
    free_tier_requests_per_hour: int = Field(default=1000, env="FREE_TIER_REQUESTS_PER_HOUR")
    free_tier_requests_per_day: int = Field(default=10000, env="FREE_TIER_REQUESTS_PER_DAY")
    free_tier_upload_limit: int = Field(default=50, env="FREE_TIER_UPLOAD_LIMIT")  # per day
    
    # Premium tier limits
    premium_tier_requests_per_hour: int = Field(default=5000, env="PREMIUM_TIER_REQUESTS_PER_HOUR")
    premium_tier_requests_per_day: int = Field(default=100000, env="PREMIUM_TIER_REQUESTS_PER_DAY")
    premium_tier_upload_limit: int = Field(default=500, env="PREMIUM_TIER_UPLOAD_LIMIT")  # per day
    
    # Enterprise tier limits
    enterprise_tier_requests_per_hour: int = Field(default=50000, env="ENTERPRISE_TIER_REQUESTS_PER_HOUR")
    enterprise_tier_requests_per_day: int = Field(default=1000000, env="ENTERPRISE_TIER_REQUESTS_PER_DAY")
    enterprise_tier_upload_limit: int = Field(default=10000, env="ENTERPRISE_TIER_UPLOAD_LIMIT")  # per day
    
    # === ADAPTIVE RATE LIMITING ===
    
    # Adaptive settings
    enable_adaptive_limiting: bool = Field(default=True, env="ENABLE_ADAPTIVE_LIMITING")
    adaptive_adjustment_factor: float = Field(default=0.1, env="ADAPTIVE_ADJUSTMENT_FACTOR")
    adaptive_response_time_threshold: float = Field(default=2.0, env="ADAPTIVE_RESPONSE_TIME_THRESHOLD")
    adaptive_error_rate_threshold: float = Field(default=0.05, env="ADAPTIVE_ERROR_RATE_THRESHOLD")
    
    # Load balancing
    enable_load_based_limiting: bool = Field(default=True, env="ENABLE_LOAD_BASED_LIMITING")
    cpu_threshold_for_limiting: float = Field(default=80.0, env="CPU_THRESHOLD_FOR_LIMITING")
    memory_threshold_for_limiting: float = Field(default=85.0, env="MEMORY_THRESHOLD_FOR_LIMITING")
    
    # === QUEUE MANAGEMENT ===
    
    # Queue settings
    enable_request_queuing: bool = Field(default=True, env="ENABLE_REQUEST_QUEUING")
    max_queue_size: int = Field(default=10000, env="MAX_QUEUE_SIZE")
    queue_timeout: int = Field(default=60, env="QUEUE_TIMEOUT")  # seconds
    priority_queue_enabled: bool = Field(default=True, env="PRIORITY_QUEUE_ENABLED")
    
    # Background processing
    background_worker_count: int = Field(default=10, env="BACKGROUND_WORKER_COUNT")
    background_queue_max_size: int = Field(default=50000, env="BACKGROUND_QUEUE_MAX_SIZE")
    
    # === MONITORING AND ALERTING ===
    
    # Rate limit monitoring
    monitor_rate_limits: bool = Field(default=True, env="MONITOR_RATE_LIMITS")
    rate_limit_alert_threshold: float = Field(default=0.8, env="RATE_LIMIT_ALERT_THRESHOLD")  # 80%
    quota_warning_threshold: float = Field(default=0.8, env="QUOTA_WARNING_THRESHOLD")
    quota_critical_threshold: float = Field(default=0.95, env="QUOTA_CRITICAL_THRESHOLD")
    
    # Logging
    log_rate_limit_violations: bool = Field(default=True, env="LOG_RATE_LIMIT_VIOLATIONS")
    log_quota_usage: bool = Field(default=True, env="LOG_QUOTA_USAGE")
    detailed_rate_limit_logging: bool = Field(default=False, env="DETAILED_RATE_LIMIT_LOGGING")
    
    # === SECURITY SETTINGS ===
    
    # DDoS protection
    enable_ddos_protection: bool = Field(default=True, env="ENABLE_DDOS_PROTECTION")
    ddos_detection_threshold: int = Field(default=1000, env="DDOS_DETECTION_THRESHOLD")  # requests per minute
    ddos_ban_duration: int = Field(default=3600, env="DDOS_BAN_DURATION")  # 1 hour
    
    # IP-based limiting
    enable_ip_based_limiting: bool = Field(default=True, env="ENABLE_IP_BASED_LIMITING")
    ip_requests_per_minute: int = Field(default=100, env="IP_REQUESTS_PER_MINUTE")
    ip_whitelist: List[str] = Field(default_factory=list, env="IP_WHITELIST")
    ip_blacklist: List[str] = Field(default_factory=list, env="IP_BLACKLIST")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class RateLimitManager:
    """Rate limit manager with advanced throttling strategies."""
    
    def __init__(self, config: RateLimitingConfig):
        self.config = config
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.quota_configs: Dict[str, QuotaConfig] = {}
        self.usage_counters: Dict[str, Dict[str, int]] = {}
        self.backoff_configs: Dict[str, BackoffConfig] = {}
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default rate limiting rules."""
        # Global API rate limit
        self.register_rate_limit_rule(RateLimitRule(
            name="global_api_limit",
            strategy=self.config.default_strategy,
            scope=RateLimitScope.GLOBAL,
            requests_per_second=self.config.global_requests_per_second,
            requests_per_minute=self.config.global_requests_per_minute,
            requests_per_hour=self.config.global_requests_per_hour,
            requests_per_day=self.config.global_requests_per_hour * 24,
            burst_capacity=self.config.default_burst_capacity,
            window_size=60,
            description="Global API rate limit"
        ))
        
        # Authentication rate limits
        self.register_rate_limit_rule(RateLimitRule(
            name="auth_endpoint_limit",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            scope=RateLimitScope.PER_IP,
            requests_per_second=1.0,
            requests_per_minute=self.config.auth_requests_per_minute,
            requests_per_hour=self.config.auth_requests_per_hour,
            requests_per_day=self.config.auth_requests_per_hour * 24,
            burst_capacity=5,
            window_size=300,  # 5 minutes
            action=RateLimitAction.REJECT,
            description="Authentication endpoint rate limit"
        ))
        
        # Upload endpoint limits
        self.register_rate_limit_rule(RateLimitRule(
            name="upload_endpoint_limit",
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            scope=RateLimitScope.PER_USER,
            requests_per_second=0.2,  # 1 every 5 seconds
            requests_per_minute=self.config.upload_requests_per_minute,
            requests_per_hour=self.config.upload_requests_per_hour,
            requests_per_day=self.config.upload_requests_per_hour * 24,
            burst_capacity=3,
            window_size=3600,
            action=RateLimitAction.QUEUE,
            description="File upload endpoint rate limit"
        ))
        
        # External service quotas
        if hasattr(self.config, 'youtube_daily_quota'):
            self.register_quota_config(QuotaConfig(
                service_name="youtube",
                daily_quota=self.config.youtube_daily_quota,
                hourly_quota=self.config.youtube_daily_quota // 24,
                minute_quota=self.config.youtube_daily_quota // (24 * 60)
            ))
    
    def register_rate_limit_rule(self, rule: RateLimitRule):
        """Register a rate limiting rule."""
        self.rate_limit_rules[rule.name] = rule
    
    def register_quota_config(self, quota: QuotaConfig):
        """Register a quota configuration."""
        self.quota_configs[quota.service_name] = quota
    
    def register_backoff_config(self, service_name: str, config: BackoffConfig):
        """Register backoff configuration for a service."""
        self.backoff_configs[service_name] = config
    
    def get_rate_limit_rule(self, rule_name: str) -> Optional[RateLimitRule]:
        """Get a rate limiting rule by name."""



        return self.rate_limit_rules.get(rule_name)
    
    def get_quota_config(self, service_name: str) -> Optional[QuotaConfig]:
        """Get quota configuration for a service."""



        return self.quota_configs.get(service_name)
    
    def calculate_delay(
        self, 
        service_name: str, 
        current_rate: float, 
        target_rate: float
    ) -> float:
        """Calculate adaptive delay based on current and target rates."""
        if current_rate <= target_rate:
            return 0.0
        
        backoff_config = self.backoff_configs.get(
            service_name, 
            BackoffConfig()
        )
        
        # Calculate delay based on rate overage
        rate_ratio = current_rate / target_rate
        delay = backoff_config.initial_delay * (rate_ratio - 1)
        
        # Apply exponential backoff if configured
        delay = min(delay * backoff_config.multiplier, backoff_config.max_delay)
        
        # Add jitter if enabled
        if backoff_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay
        
        return delay
    
    def get_service_rate_limits(self, service_name: str) -> Dict[str, Any]:
        """Get rate limiting configuration for a service."""
        service_attrs = {
            "requests_per_second": f"{service_name}_requests_per_second",
            "requests_per_minute": f"{service_name}_requests_per_minute",
            "requests_per_hour": f"{service_name}_requests_per_hour",
            "requests_per_day": f"{service_name}_requests_per_day",
            "burst_capacity": f"{service_name}_burst_capacity"
        }
        
        limits = {}
        for limit_type, attr_name in service_attrs.items():
            if hasattr(self.config, attr_name):
                limits[limit_type] = getattr(self.config, attr_name)
        
        return limits
    
    def get_user_tier_limits(self, tier: str) -> Dict[str, Any]:
        """Get rate limits for a user tier."""
        tier_limits = {}
        
        if tier == "free":
            tier_limits = {
                "requests_per_hour": self.config.free_tier_requests_per_hour,
                "requests_per_day": self.config.free_tier_requests_per_day,
                "upload_limit": self.config.free_tier_upload_limit
            }
        elif tier == "premium":
            tier_limits = {
                "requests_per_hour": self.config.premium_tier_requests_per_hour,
                "requests_per_day": self.config.premium_tier_requests_per_day,
                "upload_limit": self.config.premium_tier_upload_limit
            }
        elif tier == "enterprise":
            tier_limits = {
                "requests_per_hour": self.config.enterprise_tier_requests_per_hour,
                "requests_per_day": self.config.enterprise_tier_requests_per_day,
                "upload_limit": self.config.enterprise_tier_upload_limit
            }
        
        return tier_limits
    
    def is_quota_exceeded(self, service_name: str, cost: int = 1) -> bool:
        """Check if quota is exceeded for a service."""
        quota_config = self.get_quota_config(service_name)
        if not quota_config:
            return False
        
        return (quota_config.current_usage + cost) > quota_config.daily_quota
    
    def update_quota_usage(self, service_name: str, cost: int = 1):
        """Update quota usage for a service."""
        if service_name in self.quota_configs:
            self.quota_configs[service_name].current_usage += cost
    
    def get_quota_usage_percentage(self, service_name: str) -> float:
        """Get quota usage percentage for a service."""
        quota_config = self.get_quota_config(service_name)
        if not quota_config or quota_config.daily_quota == 0:
            return 0.0
        
        return (quota_config.current_usage / quota_config.daily_quota) * 100
    
    def should_apply_adaptive_limiting(self, metrics: Dict[str, float]) -> bool:
        """Determine if adaptive rate limiting should be applied."""
        if not self.config.enable_adaptive_limiting:
            return False
        
        response_time = metrics.get("response_time", 0.0)
        error_rate = metrics.get("error_rate", 0.0)
        cpu_usage = metrics.get("cpu_usage", 0.0)
        memory_usage = metrics.get("memory_usage", 0.0)
        
        conditions = [
            response_time > self.config.adaptive_response_time_threshold,
            error_rate > self.config.adaptive_error_rate_threshold,
            cpu_usage > self.config.cpu_threshold_for_limiting,
            memory_usage > self.config.memory_threshold_for_limiting
        ]
        
        return any(conditions)
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get overall rate limiting status."""
        total_rules = len(self.rate_limit_rules)
        enabled_rules = sum(1 for rule in self.rate_limit_rules.values() if rule.enabled)
        
        quota_status = {}
        for service_name, quota in self.quota_configs.items():
            quota_status[service_name] = {
                "usage_percentage": self.get_quota_usage_percentage(service_name),
                "current_usage": quota.current_usage,
                "daily_quota": quota.daily_quota,
                "warning_threshold_exceeded": (
                    self.get_quota_usage_percentage(service_name) / 100 
                    > quota.warning_threshold
                ),
                "critical_threshold_exceeded": (
                    self.get_quota_usage_percentage(service_name) / 100 
                    > quota.critical_threshold
                )
            }
        
        return {
            "rate_limiting_enabled": self.config.rate_limiting_enabled,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "adaptive_limiting_enabled": self.config.enable_adaptive_limiting,
            "quota_status": quota_status,
            "queue_settings": {
                "enabled": self.config.enable_request_queuing,
                "max_size": self.config.max_queue_size,
                "timeout": self.config.queue_timeout
            }
        }


# Global rate limiting configuration instance
rate_limiting_config = RateLimitingConfig()
rate_limit_manager = RateLimitManager(rate_limiting_config)
