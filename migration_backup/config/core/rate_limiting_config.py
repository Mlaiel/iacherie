"""Ainflue Enterprise Rate Limiting Configuration - HIGH PERFORMANCE PROTECTION
=================================================================================

🚦 ENTERPRISE RATE LIMITING FEATURES:
- Advanced rate limiting with multiple algorithms
- Distributed rate limiting across microservices
- Intelligent traffic analysis & bot detection
- Adaptive rate limiting based on system load
- Priority-based rate limiting for different user tiers
- Real-time rate limit monitoring & alerting
- Rate limit bypass for trusted sources
- Geographic rate limiting patterns
- API endpoint-specific rate limiting
- Burst handling & traffic smoothing
- Redis-based distributed counters
- Custom rate limiting rules engine

Business Logic Integration:
Creator Upload Limits → AI Processing Queues → Content Distribution → 
Monetization API Calls → Collaboration Requests → Analytics Tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"
    WEIGHTED = "weighted"

class UserTier(str, Enum):
    """User tier for different rate limits"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    VIP = "vip"
    CREATOR_VERIFIED = "creator_verified"

class EndpointCategory(str, Enum):
    """API endpoint categories for rate limiting"""
    AUTHENTICATION = "authentication"
    CONTENT_UPLOAD = "content_upload"
    AI_PROCESSING = "ai_processing"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    SEARCH = "search"
    DISTRIBUTION = "distribution"
    ADMIN = "admin"

@dataclass
class RateLimitRule:
    """Individual rate limit rule configuration"""
    name: str
    algorithm: RateLimitAlgorithm
    requests_per_second: int
    burst_size: int
    window_size_seconds: int
    user_tiers: List[UserTier] = field(default_factory=list)
    endpoint_patterns: List[str] = field(default_factory=list)
    bypass_conditions: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 100
    
class RateLimitingConfiguration:
    """Enterprise rate limiting configuration management"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.redis_enabled = True
        self.distributed_mode = True
        self.monitoring_enabled = True
        
        # Global settings
        self.global_settings = {
            "default_algorithm": RateLimitAlgorithm.SLIDING_WINDOW,
            "redis_key_prefix": "ainflue:rate_limit:",
            "redis_key_ttl": 3600,
            "enable_metrics": True,
            "enable_alerts": True,
            "alert_threshold_percentage": 90,
            "bypass_internal_requests": True,
            "log_violations": True,
            "block_on_violation": True
        }
        
        # Configure rules based on level
        self._configure_rate_limit_rules()
        self._configure_endpoint_specific_limits()
        self._configure_geographic_limits()
        self._configure_adaptive_limits()
    
    def _configure_rate_limit_rules(self):
        """Configure basic rate limit rules"""
        if self.level == "enterprise":
            self.user_tier_limits = {
                UserTier.FREE: {
                    "requests_per_second": 10,
                    "burst_size": 20,
                    "daily_limit": 1000,
                    "upload_limit_mb": 100
                },
                UserTier.BASIC: {
                    "requests_per_second": 50,
                    "burst_size": 100,
                    "daily_limit": 10000,
                    "upload_limit_mb": 500
                },
                UserTier.PREMIUM: {
                    "requests_per_second": 200,
                    "burst_size": 400,
                    "daily_limit": 100000,
                    "upload_limit_mb": 2000
                },
                UserTier.ENTERPRISE: {
                    "requests_per_second": 1000,
                    "burst_size": 2000,
                    "daily_limit": 1000000,
                    "upload_limit_mb": 10000
                },
                UserTier.VIP: {
                    "requests_per_second": 5000,
                    "burst_size": 10000,
                    "daily_limit": 10000000,
                    "upload_limit_mb": 50000
                },
                UserTier.CREATOR_VERIFIED: {
                    "requests_per_second": 500,
                    "burst_size": 1000,
                    "daily_limit": 500000,
                    "upload_limit_mb": 5000
                }
            }
        else:
            # Basic level limits
            self.user_tier_limits = {
                UserTier.FREE: {
                    "requests_per_second": 5,
                    "burst_size": 10,
                    "daily_limit": 500,
                    "upload_limit_mb": 50
                }
            }
    
    def _configure_endpoint_specific_limits(self):
        """Configure endpoint-specific rate limits"""
        self.endpoint_limits = {
            EndpointCategory.AUTHENTICATION: {
                "login": {"requests_per_minute": 5, "burst": 10},
                "register": {"requests_per_minute": 3, "burst": 5},
                "password_reset": {"requests_per_hour": 3, "burst": 3},
                "token_refresh": {"requests_per_minute": 10, "burst": 20}
            },
            
            EndpointCategory.CONTENT_UPLOAD: {
                "upload_audio": {"requests_per_minute": 10, "burst": 20},
                "upload_video": {"requests_per_minute": 5, "burst": 10},
                "upload_image": {"requests_per_minute": 20, "burst": 40},
                "batch_upload": {"requests_per_hour": 5, "burst": 10}
            },
            
            EndpointCategory.AI_PROCESSING: {
                "analyze_content": {"requests_per_minute": 20, "burst": 40},
                "generate_content": {"requests_per_minute": 5, "burst": 10},
                "transcribe_audio": {"requests_per_minute": 10, "burst": 20},
                "optimize_content": {"requests_per_minute": 15, "burst": 30}
            },
            
            EndpointCategory.ANALYTICS: {
                "view_stats": {"requests_per_minute": 60, "burst": 120},
                "export_data": {"requests_per_hour": 10, "burst": 20},
                "real_time_metrics": {"requests_per_second": 10, "burst": 20}
            },
            
            EndpointCategory.MONETIZATION: {
                "create_payment": {"requests_per_minute": 10, "burst": 20},
                "check_balance": {"requests_per_minute": 30, "burst": 60},
                "withdraw_funds": {"requests_per_hour": 5, "burst": 10}
            },
            
            EndpointCategory.SEARCH: {
                "content_search": {"requests_per_minute": 100, "burst": 200},
                "creator_search": {"requests_per_minute": 50, "burst": 100},
                "advanced_search": {"requests_per_minute": 20, "burst": 40}
            }
        }
    
    def _configure_geographic_limits(self):
        """Configure geographic-based rate limits"""
        self.geographic_limits = {
            "high_risk_countries": {
                "countries": ["CN", "RU", "IR", "KP"],
                "rate_multiplier": 0.5,
                "additional_verification": True
            },
            "premium_regions": {
                "countries": ["US", "CA", "GB", "DE", "FR", "JP"],
                "rate_multiplier": 1.2,
                "priority_processing": True
            },
            "default_regions": {
                "rate_multiplier": 1.0,
                "standard_processing": True
            }
        }
    
    def _configure_adaptive_limits(self):
        """Configure adaptive rate limiting based on system load"""
        self.adaptive_settings = {
            "enable_adaptive": True,
            "load_thresholds": {
                "low": 30,      # < 30% system load
                "medium": 70,   # 30-70% system load  
                "high": 90,     # 70-90% system load
                "critical": 95  # > 95% system load
            },
            "rate_multipliers": {
                "low": 1.5,     # Allow 50% more requests
                "medium": 1.0,  # Normal rate limits
                "high": 0.7,    # Reduce to 70% of normal
                "critical": 0.3 # Emergency mode - 30% of normal
            },
            "monitoring_interval": 30,  # seconds
            "adjustment_sensitivity": 0.1
        }
    
    def get_rate_limit_for_user(self, user_tier: UserTier, endpoint: str) -> Dict[str, Any]:
        """Get rate limit configuration for specific user and endpoint"""
        base_limits = self.user_tier_limits.get(user_tier, self.user_tier_limits[UserTier.FREE])
        
        # Check for endpoint-specific overrides
        for category, endpoints in self.endpoint_limits.items():
            if endpoint in endpoints:
                endpoint_limits = endpoints[endpoint]
                # Merge with base limits
                return {**base_limits, **endpoint_limits}
        
        return base_limits
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration for distributed rate limiting"""
        return {
            "enabled": self.redis_enabled,
            "key_prefix": self.global_settings["redis_key_prefix"],
            "key_ttl": self.global_settings["redis_key_ttl"],
            "connection_pool_size": 20,
            "max_connections": 100,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return {
            "enabled": self.monitoring_enabled,
            "metrics_enabled": self.global_settings["enable_metrics"],
            "alerts_enabled": self.global_settings["enable_alerts"],
            "alert_threshold": self.global_settings["alert_threshold_percentage"],
            "log_violations": self.global_settings["log_violations"],
            "violation_retention_days": 30,
            "metrics_retention_days": 90,
            "real_time_dashboard": True,
            "export_metrics": True
        }
    
    def get_bypass_rules(self) -> List[Dict[str, Any]]:
        """Get rate limit bypass rules"""
        return [
            {
                "name": "Internal Services",
                "conditions": ["source_ip_internal", "service_account"],
                "bypass_all": True
            },
            {
                "name": "Health Checks",
                "conditions": ["endpoint_health_check", "monitoring_service"],
                "bypass_all": True
            },
            {
                "name": "Emergency Override",
                "conditions": ["emergency_token", "admin_override"],
                "bypass_all": True,
                "requires_approval": True
            },
            {
                "name": "VIP Content Creators", 
                "conditions": ["user_tier_vip", "verified_creator"],
                "rate_multiplier": 2.0
            }
        ]

# Configuration instance
rate_limiting_config = RateLimitingConfiguration()

# Helper functions
def get_rate_limit_config() -> RateLimitingConfiguration:
    """Get rate limiting configuration instance"""
    return rate_limiting_config

def get_user_rate_limit(user_tier: str, endpoint: str) -> Dict[str, Any]:
    """Get rate limit for specific user tier and endpoint"""
    tier_enum = UserTier(user_tier) if user_tier in [t.value for t in UserTier] else UserTier.FREE
    return rate_limiting_config.get_rate_limit_for_user(tier_enum, endpoint)

def is_rate_limit_enabled() -> bool:
    """Check if rate limiting is enabled"""
    return rate_limiting_config.level in ["professional", "enterprise", "quantum"]

def get_adaptive_settings() -> Dict[str, Any]:
    """Get adaptive rate limiting settings"""
    return rate_limiting_config.adaptive_settings

__all__ = [
    "RateLimitingConfiguration", "RateLimitAlgorithm", "UserTier", "EndpointCategory",
    "RateLimitRule", "rate_limiting_config", "get_rate_limit_config", 
    "get_user_rate_limit", "is_rate_limit_enabled", "get_adaptive_settings"
]

logger.info("🚦 Ainflue Rate Limiting Configuration initialized")
logger.info(f"📊 User tiers configured: {len(rate_limiting_config.user_tier_limits)}")
logger.info(f"🔧 Endpoint categories: {len(rate_limiting_config.endpoint_limits)}")
logger.info("⚠️ Protected by copyright - All Rights Reserved")