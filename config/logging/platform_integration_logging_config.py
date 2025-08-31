"""Platform Integration Logging Configuration for IA-Influencer Agent Platform
===========================================================================

Industrial-grade logging configuration for multi-platform integrations,
API connections, social media platforms, and external service monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                 Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.

Contact: mlaiel@live.de for licensing inquiries only.
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

import structlog
from pythonjsonlogger import jsonlogger


class PlatformType(str, Enum):
    """Supported platform types for integration"""    # Music Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    TIDAL = "tidal"
    
    # Video Platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    VIMEO = "vimeo"
    TWITCH = "twitch"
    FACEBOOK_VIDEO = "facebook_video"
    
    # Social Media Platforms
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    
    # Professional Platforms
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB = "github"
    MEDIUM = "medium"
    
    # Monetization Platforms
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    SUBSTACK = "substack"
    GUMROAD = "gumroad"
    
    # Podcast Platforms
    SPOTIFY_PODCASTS = "spotify_podcasts"
    APPLE_PODCASTS = "apple_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    ANCHOR = "anchor"


class IntegrationType(str, Enum):
    """Types of platform integrations"""    API_INTEGRATION = "api_integration"
    WEBHOOK_INTEGRATION = "webhook_integration"
    OAUTH_INTEGRATION = "oauth_integration"
    RSS_FEED = "rss_feed"
    WEB_SCRAPING = "web_scraping"
    SDK_INTEGRATION = "sdk_integration"
    DIRECT_UPLOAD = "direct_upload"
    BATCH_SYNC = "batch_sync"
    REAL_TIME_SYNC = "real_time_sync"


class APIOperationType(str, Enum):
    """API operation types"""    CONTENT_UPLOAD = "content_upload"
    CONTENT_UPDATE = "content_update"
    CONTENT_DELETE = "content_delete"
    METADATA_FETCH = "metadata_fetch"
    ANALYTICS_FETCH = "analytics_fetch"
    USER_AUTH = "user_auth"
    PROFILE_UPDATE = "profile_update"
    COLLABORATION_REQUEST = "collaboration_request"
    MONETIZATION_SYNC = "monetization_sync"
    PROTECTION_SCAN = "protection_scan"


@dataclass
class PlatformIntegrationLogConfig:
    """Configuration for platform integration logging"""    enable_api_call_logging: bool = True
    enable_webhook_logging: bool = True
    enable_sync_logging: bool = True
    enable_error_tracking: bool = True
    enable_rate_limit_monitoring: bool = True
    enable_authentication_logging: bool = True
    enable_performance_tracking: bool = True
    enable_quota_monitoring: bool = True
    
    # Security settings
    mask_api_keys: bool = True
    mask_user_tokens: bool = True
    encrypt_sensitive_data: bool = True
    
    # Performance settings
    track_response_times: bool = True
    track_success_rates: bool = True
    track_error_rates: bool = True
    monitor_throughput: bool = True
    
    # Alerting
    rate_limit_alerts: bool = True
    api_failure_alerts: bool = True
    quota_exhaustion_alerts: bool = True
    authentication_failure_alerts: bool = True
    
    # Retention
    api_log_retention: int = 365  # 1 year
    webhook_log_retention: int = 180  # 6 months
    error_log_retention: int = 730  # 2 years


class PlatformIntegrationLogger:
    """Specialized logger for platform integration operations"""    
    def __init__(self, config: PlatformIntegrationLogConfig):
        self.config = config
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> structlog.BoundLogger:
        """Setup structured logger for platform integrations"""        processors = [
            structlog.threadlocal.merge_threadlocal_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder()
        ]
        
        if self.config.mask_api_keys:
            processors.append(self._mask_sensitive_credentials)
            
        processors.append(
            structlog.processors.JSONRenderer(serializer=json.dumps, ensure_ascii=False)
        )
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger("ia_influencer_platform_integration")
    
    def _mask_sensitive_credentials(self, logger, method_name, event_dict):
        """Mask sensitive credentials in platform logs"""        sensitive_fields = ['api_key', 'access_token', 'refresh_token', 'client_secret', 'password']
        for field in sensitive_fields:
            if field in event_dict:
                event_dict[field] = "[MASKED]"
        return event_dict
    
    def log_api_call(
        self,
        platform: PlatformType,
        operation: APIOperationType,
        endpoint: str,
        method: str,
        response_status: int,
        response_time: float,
        request_size: int,
        response_size: int,
        rate_limit_remaining: Optional[int] = None,
        error_details: Optional[str] = None
    ) -> None:
        """Log API calls to external platforms"""        if not self.config.enable_api_call_logging:
            return
            
        log_data = {
            "event_type": "platform_api_call",
            "platform": platform.value,
            "operation": operation.value,
            "endpoint": endpoint,
            "http_method": method,
            "response_status": response_status,
            "response_time_ms": response_time * 1000,
            "request_size_bytes": request_size,
            "response_size_bytes": response_size,
            "timestamp": datetime.utcnow().isoformat(),
            "success": 200 <= response_status < 300
        }
        
        if rate_limit_remaining is not None:
            log_data["rate_limit_remaining"] = rate_limit_remaining
            
        if self.config.rate_limit_alerts and rate_limit_remaining is not None and rate_limit_remaining < 10:
            log_data["rate_limit_warning"] = True
            
        if error_details and response_status >= 400:
            log_data["error_details"] = error_details
            
        if self.config.track_response_times:
            log_data["performance_metrics"] = {
                "response_time_ms": response_time * 1000,
                "throughput_bytes_per_second": (request_size + response_size) / response_time if response_time > 0 else 0
            }
            
        level = "info" if 200 <= response_status < 300 else "warning" if response_status < 500 else "error"
        getattr(self.logger, level)("Platform API call completed", **log_data)
    
    def log_content_upload(
        self,
        platform: PlatformType,
        content_id: str,
        content_type: str,
        upload_size: int,
        upload_time: float,
        processing_status: str,
        platform_content_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log content uploads to platforms"""        log_data = {
            "event_type": "platform_content_upload",
            "platform": platform.value,
            "content_id": content_id,
            "content_type": content_type,
            "upload_size_bytes": upload_size,
            "upload_time_seconds": upload_time,
            "processing_status": processing_status,
            "timestamp": datetime.utcnow().isoformat(),
            "upload_speed_mbps": (upload_size / (1024 * 1024)) / upload_time if upload_time > 0 else 0
        }
        
        if platform_content_id:
            log_data["platform_content_id"] = platform_content_id
            
        if metadata:
            log_data["metadata"] = metadata
            
        self.logger.info("Content upload to platform completed", **log_data)
    
    def log_analytics_sync(
        self,
        platform: PlatformType,
        content_ids: List[str],
        analytics_data: Dict[str, Any],
        sync_duration: float,
        records_synced: int,
        sync_status: str
    ) -> None:
        """Log analytics data synchronization"""        log_data = {
            "event_type": "platform_analytics_sync",
            "platform": platform.value,
            "content_count": len(content_ids),
            "sync_duration_seconds": sync_duration,
            "records_synced": records_synced,
            "sync_status": sync_status,
            "sync_rate_per_second": records_synced / sync_duration if sync_duration > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self.config.mask_user_tokens:
            log_data["analytics_summary"] = {
                "total_views": analytics_data.get("total_views", 0),
                "total_engagement": analytics_data.get("total_engagement", 0),
                "revenue_generated": analytics_data.get("revenue", 0.0)
            }
        else:
            log_data["analytics_summary"] = "[MASKED]"
            
        self.logger.info("Platform analytics sync completed", **log_data)
    
    def log_webhook_event(
        self,
        platform: PlatformType,
        webhook_event_type: str,
        payload_size: int,
        processing_time: float,
        event_data: Dict[str, Any],
        processing_status: str
    ) -> None:
        """Log webhook events from platforms"""        if not self.config.enable_webhook_logging:
            return
            
        log_data = {
            "event_type": "platform_webhook",
            "platform": platform.value,
            "webhook_event_type": webhook_event_type,
            "payload_size_bytes": payload_size,
            "processing_time_ms": processing_time * 1000,
            "processing_status": processing_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mask sensitive webhook data
        if not self.config.encrypt_sensitive_data:
            log_data["event_data"] = event_data
        else:
            log_data["event_data_summary"] = {
                "fields_count": len(event_data),
                "has_user_data": any("user" in key.lower() for key in event_data.keys()),
                "has_content_data": any("content" in key.lower() for key in event_data.keys())
            }
            
        self.logger.info("Platform webhook processed", **log_data)
    
    def log_authentication_event(
        self,
        platform: PlatformType,
        auth_type: str,
        user_id: str,
        auth_status: str,
        token_expiry: Optional[datetime] = None,
        scopes_granted: Optional[List[str]] = None
    ) -> None:
        """Log authentication events with platforms"""        if not self.config.enable_authentication_logging:
            return
            
        log_data = {
            "event_type": "platform_authentication",
            "platform": platform.value,
            "auth_type": auth_type,
            "user_id": user_id if not self.config.mask_user_tokens else "[MASKED]",
            "auth_status": auth_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if token_expiry:
            log_data["token_expiry"] = token_expiry.isoformat()
            log_data["token_valid_hours"] = (token_expiry - datetime.utcnow()).total_seconds() / 3600
            
        if scopes_granted:
            log_data["scopes_granted"] = scopes_granted
            log_data["scopes_count"] = len(scopes_granted)
            
        if self.config.authentication_failure_alerts and auth_status == "failed":
            log_data["auth_failure_alert"] = True
            
        level = "info" if auth_status == "success" else "warning"
        getattr(self.logger, level)("Platform authentication event", **log_data)
    
    def log_rate_limit_event(
        self,
        platform: PlatformType,
        endpoint: str,
        rate_limit_type: str,
        limit_reached: bool,
        current_usage: int,
        limit_threshold: int,
        reset_time: datetime,
        backoff_strategy: str
    ) -> None:
        """Log rate limiting events"""        if not self.config.enable_rate_limit_monitoring:
            return
            
        log_data = {
            "event_type": "platform_rate_limit",
            "platform": platform.value,
            "endpoint": endpoint,
            "rate_limit_type": rate_limit_type,
            "limit_reached": limit_reached,
            "current_usage": current_usage,
            "limit_threshold": limit_threshold,
            "usage_percentage": (current_usage / limit_threshold) * 100 if limit_threshold > 0 else 0,
            "reset_time": reset_time.isoformat(),
            "time_until_reset_minutes": (reset_time - datetime.utcnow()).total_seconds() / 60,
            "backoff_strategy": backoff_strategy,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.config.rate_limit_alerts and limit_reached:
            log_data["rate_limit_alert"] = True
            log_data["service_throttled"] = True
            
        level = "warning" if limit_reached else "info"
        getattr(self.logger, level)("Platform rate limit event", **log_data)
    
    def log_sync_operation(
        self,
        platforms: List[PlatformType],
        sync_type: str,
        sync_direction: str,
        items_synced: int,
        sync_duration: float,
        conflicts_detected: int,
        conflicts_resolved: int,
        sync_status: str
    ) -> None:
        """Log multi-platform synchronization operations"""        if not self.config.enable_sync_logging:
            return
            
        log_data = {
            "event_type": "multi_platform_sync",
            "platforms": [platform.value for platform in platforms],
            "platform_count": len(platforms),
            "sync_type": sync_type,
            "sync_direction": sync_direction,
            "items_synced": items_synced,
            "sync_duration_seconds": sync_duration,
            "sync_rate_per_second": items_synced / sync_duration if sync_duration > 0 else 0,
            "conflicts_detected": conflicts_detected,
            "conflicts_resolved": conflicts_resolved,
            "conflict_resolution_rate": conflicts_resolved / conflicts_detected if conflicts_detected > 0 else 1.0,
            "sync_status": sync_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info("Multi-platform sync operation completed", **log_data)
    
    def log_quota_monitoring(
        self,
        platform: PlatformType,
        quota_type: str,
        current_usage: int,
        quota_limit: int,
        billing_period: str,
        projected_usage: float,
        overage_risk: bool
    ) -> None:
        """Log quota and usage monitoring"""        if not self.config.enable_quota_monitoring:
            return
            
        log_data = {
            "event_type": "platform_quota_monitoring",
            "platform": platform.value,
            "quota_type": quota_type,
            "current_usage": current_usage,
            "quota_limit": quota_limit,
            "usage_percentage": (current_usage / quota_limit) * 100 if quota_limit > 0 else 0,
            "billing_period": billing_period,
            "projected_usage": projected_usage,
            "projected_usage_percentage": (projected_usage / quota_limit) * 100 if quota_limit > 0 else 0,
            "overage_risk": overage_risk,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.config.quota_exhaustion_alerts and overage_risk:
            log_data["quota_alert"] = True
            log_data["usage_optimization_needed"] = True
            
        level = "warning" if overage_risk else "info"
        getattr(self.logger, level)("Platform quota monitoring", **log_data)
    
    def get_platform_integration_metrics(self) -> Dict[str, Any]:
        """Get platform integration system metrics"""        return {
            "api_call_logging": self.config.enable_api_call_logging,
            "webhook_logging": self.config.enable_webhook_logging,
            "sync_logging": self.config.enable_sync_logging,
            "error_tracking": self.config.enable_error_tracking,
            "rate_limit_monitoring": self.config.enable_rate_limit_monitoring,
            "authentication_logging": self.config.enable_authentication_logging,
            "performance_tracking": self.config.enable_performance_tracking,
            "quota_monitoring": self.config.enable_quota_monitoring,
            "api_log_retention": self.config.api_log_retention,
            "webhook_log_retention": self.config.webhook_log_retention,
            "error_log_retention": self.config.error_log_retention
        }


class PlatformIntegrationLoggingConfig:
    """Main configuration class for platform integration logging"""    
    @staticmethod
    def create_default_config() -> PlatformIntegrationLogConfig:
        """Create default platform integration logging configuration"""        return PlatformIntegrationLogConfig()
    
    @staticmethod
    def create_enterprise_config() -> PlatformIntegrationLogConfig:
        """Create enterprise platform integration logging configuration"""        return PlatformIntegrationLogConfig(
            enable_api_call_logging=True,
            enable_webhook_logging=True,
            enable_sync_logging=True,
            enable_error_tracking=True,
            enable_rate_limit_monitoring=True,
            enable_authentication_logging=True,
            enable_performance_tracking=True,
            enable_quota_monitoring=True,
            mask_api_keys=True,
            mask_user_tokens=True,
            encrypt_sensitive_data=True,
            track_response_times=True,
            track_success_rates=True,
            track_error_rates=True,
            monitor_throughput=True,
            rate_limit_alerts=True,
            api_failure_alerts=True,
            quota_exhaustion_alerts=True,
            authentication_failure_alerts=True,
            api_log_retention=365,
            webhook_log_retention=180,
            error_log_retention=730
        )
