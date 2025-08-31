"""
IA Influencer Agent - Platform Integration Metrics Collector
Enterprise metrics for external platform integrations and API performance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

  AVERTISSEMENT LÉGAL STRICT 
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Multi-platform API performance tracking
- Integration health monitoring
- Rate limiting and quota management
- Authentication and authorization metrics
- Data synchronization performance
- Real-time platform status monitoring
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from prometheus_client import Counter, Histogram, Gauge, Summary

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager

logger = get_logger(__name__)


class Platform(Enum):
    """Supported external platforms"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"


class IntegrationType(Enum):
    """Types of platform integrations"""
    API_DIRECT = "api_direct"
    OAUTH2 = "oauth2"
    WEBHOOK = "webhook"
    SCRAPING = "scraping"
    RSS_FEED = "rss_feed"
    REALTIME_STREAM = "realtime_stream"
    FILE_SYNC = "file_sync"


class APIEndpointType(Enum):
    """Types of API endpoints"""
    AUTHENTICATION = "authentication"
    USER_PROFILE = "user_profile"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_DOWNLOAD = "content_download"
    METADATA_RETRIEVAL = "metadata_retrieval"
    ANALYTICS = "analytics"
    SEARCH = "search"
    LICENSING = "licensing"
    MONETIZATION = "monetization"
    NOTIFICATIONS = "notifications"


class ConnectionStatus(Enum):
    """Platform connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_FAILED = "authentication_failed"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class PlatformConnection:
    """Platform connection information"""
    platform: Platform
    user_id: str
    integration_type: IntegrationType
    status: ConnectionStatus
    connected_at: datetime
    last_activity: datetime
    credentials_expire_at: Optional[datetime] = None


@dataclass
class APICall:
    """API call details"""
    call_id: str
    platform: Platform
    endpoint_type: APIEndpointType
    method: str
    response_code: int
    response_time_ms: float
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime
    user_id: str


class PlatformIntegrationMetricsCollector:
    """
    Comprehensive metrics collector for platform integrations
    
    Tracks:
    - API call performance and reliability
    - Platform connection health
    - Rate limiting and quota usage
    - Authentication success rates
    - Data synchronization metrics
    - Integration error patterns
    """
    
    def __init__(self, prometheus_manager=None):
        self.prometheus_manager = prometheus_manager
        self.redis_manager = RedisManager()
        self.logger = logger
        self._active_connections: Dict[str, PlatformConnection] = {}
        self._api_call_history: List[APICall] = []
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize comprehensive platform integration metrics"""
        
        if not self.prometheus_manager:
            self.logger.warning("No Prometheus manager provided, metrics disabled")
            return
        
        # API Performance Metrics
        self.api_calls_total = Counter(
            'ia_influencer_api_calls_total',
            'Total API calls by platform, endpoint, and response code',
            ['platform', 'endpoint_type', 'method', 'response_code', 'user_id']
        )
        
        self.api_response_time = Histogram(
            'ia_influencer_api_response_time_seconds',
            'API response time by platform and endpoint',
            ['platform', 'endpoint_type', 'method'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60]
        )
        
        self.api_request_size = Histogram(
            'ia_influencer_api_request_size_bytes',
            'API request size distribution',
            ['platform', 'endpoint_type'],
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        )
        
        self.api_response_size = Histogram(
            'ia_influencer_api_response_size_bytes',
            'API response size distribution',
            ['platform', 'endpoint_type'],
            buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000]
        )
        
        # Platform Connection Metrics
        self.platform_connections_total = Counter(
            'ia_influencer_platform_connections_total',
            'Total platform connections by platform and status',
            ['platform', 'integration_type', 'status', 'user_id']
        )
        
        self.active_platform_connections = Gauge(
            'ia_influencer_active_platform_connections',
            'Number of active platform connections',
            ['platform', 'integration_type']
        )
        
        self.connection_duration = Histogram(
            'ia_influencer_connection_duration_hours',
            'Duration of platform connections',
            ['platform', 'integration_type', 'disconnect_reason'],
            buckets=[0.1, 0.5, 1, 6, 12, 24, 48, 72, 168, 336, 720, 8760]
        )
        
        # Authentication Metrics
        self.authentication_attempts_total = Counter(
            'ia_influencer_authentication_attempts_total',
            'Total authentication attempts by platform and result',
            ['platform', 'auth_method', 'result', 'user_id']
        )
        
        self.authentication_success_rate = Gauge(
            'ia_influencer_authentication_success_rate_percent',
            'Authentication success rate by platform',
            ['platform', 'auth_method', 'time_window']
        )
        
        self.token_refresh_total = Counter(
            'ia_influencer_token_refresh_total',
            'Total token refresh operations',
            ['platform', 'result', 'refresh_reason']
        )
        
        # Rate Limiting Metrics
        self.rate_limit_hits_total = Counter(
            'ia_influencer_rate_limit_hits_total',
            'Total rate limit hits by platform and endpoint',
            ['platform', 'endpoint_type', 'limit_type']
        )
        
        self.api_quota_usage = Gauge(
            'ia_influencer_api_quota_usage_percent',
            'API quota usage percentage by platform',
            ['platform', 'quota_type', 'time_window']
        )
        
        self.rate_limit_reset_time = Gauge(
            'ia_influencer_rate_limit_reset_time_seconds',
            'Time until rate limit reset',
            ['platform', 'endpoint_type']
        )
        
        # Data Synchronization Metrics
        self.data_sync_operations_total = Counter(
            'ia_influencer_data_sync_operations_total',
            'Total data synchronization operations',
            ['platform', 'sync_type', 'direction', 'result']
        )
        
        self.data_sync_duration = Histogram(
            'ia_influencer_data_sync_duration_seconds',
            'Duration of data synchronization operations',
            ['platform', 'sync_type', 'data_size_range'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200]
        )
        
        self.data_sync_lag = Gauge(
            'ia_influencer_data_sync_lag_seconds',
            'Data synchronization lag by platform',
            ['platform', 'sync_type']
        )
        
        # Integration Health Metrics
        self.platform_health_score = Gauge(
            'ia_influencer_platform_health_score',
            'Platform integration health score (0-100)',
            ['platform', 'integration_type']
        )
        
        self.integration_errors_total = Counter(
            'ia_influencer_integration_errors_total',
            'Total integration errors by platform and error type',
            ['platform', 'error_type', 'severity', 'endpoint_type']
        )
        
        self.integration_uptime = Gauge(
            'ia_influencer_integration_uptime_percent',
            'Integration uptime percentage',
            ['platform', 'time_window']
        )
        
        # Webhook Metrics
        self.webhooks_received_total = Counter(
            'ia_influencer_webhooks_received_total',
            'Total webhooks received by platform and event type',
            ['platform', 'event_type', 'status']
        )
        
        self.webhook_processing_duration = Histogram(
            'ia_influencer_webhook_processing_duration_seconds',
            'Webhook processing duration',
            ['platform', 'event_type'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10, 30]
        )
        
        # Content Distribution Metrics
        self.content_distribution_operations_total = Counter(
            'ia_influencer_content_distribution_operations_total',
            'Total content distribution operations',
            ['platform', 'content_type', 'operation', 'result']
        )
        
        self.content_distribution_duration = Histogram(
            'ia_influencer_content_distribution_duration_seconds',
            'Content distribution operation duration',
            ['platform', 'content_type', 'file_size_range'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600]
        )
        
        # Register all metrics
        self._register_metrics()
        
        self.logger.info("Platform integration metrics initialized")
    
    def _register_metrics(self) -> None:
        """Register all metrics with Prometheus manager"""
        
        metrics_to_register = [
            self.api_calls_total,
            self.api_response_time,
            self.api_request_size,
            self.api_response_size,
            self.platform_connections_total,
            self.active_platform_connections,
            self.connection_duration,
            self.authentication_attempts_total,
            self.authentication_success_rate,
            self.token_refresh_total,
            self.rate_limit_hits_total,
            self.api_quota_usage,
            self.rate_limit_reset_time,
            self.data_sync_operations_total,
            self.data_sync_duration,
            self.data_sync_lag,
            self.platform_health_score,
            self.integration_errors_total,
            self.integration_uptime,
            self.webhooks_received_total,
            self.webhook_processing_duration,
            self.content_distribution_operations_total,
            self.content_distribution_duration
        ]
        
        for metric in metrics_to_register:
            self.prometheus_manager.register_metric(metric)
    
    async def record_api_call(self, api_call: APICall) -> None:
        """Record API call metrics"""
        
        self.api_calls_total.labels(
            platform=api_call.platform.value,
            endpoint_type=api_call.endpoint_type.value,
            method=api_call.method,
            response_code=str(api_call.response_code),
            user_id=api_call.user_id
        ).inc()
        
        self.api_response_time.labels(
            platform=api_call.platform.value,
            endpoint_type=api_call.endpoint_type.value,
            method=api_call.method
        ).observe(api_call.response_time_ms / 1000.0)  # Convert to seconds
        
        self.api_request_size.labels(
            platform=api_call.platform.value,
            endpoint_type=api_call.endpoint_type.value
        ).observe(api_call.request_size_bytes)
        
        self.api_response_size.labels(
            platform=api_call.platform.value,
            endpoint_type=api_call.endpoint_type.value
        ).observe(api_call.response_size_bytes)
        
        # Check for rate limiting
        if api_call.response_code == 429:  # Too Many Requests
            self.rate_limit_hits_total.labels(
                platform=api_call.platform.value,
                endpoint_type=api_call.endpoint_type.value,
                limit_type="rate_limit"
            ).inc()
        
        # Store API call for analysis
        self._api_call_history.append(api_call)
        if len(self._api_call_history) > 1000:  # Keep last 1000 calls
            self._api_call_history = self._api_call_history[-1000:]
        
        await self.redis_manager.lpush(
            f"api_calls:{api_call.platform.value}",
            api_call.__dict__
        )
        
        self.logger.debug(
            f"API call recorded: {api_call.platform.value} {api_call.endpoint_type.value} "
            f"- {api_call.response_code} ({api_call.response_time_ms:.1f}ms)"
        )
    
    async def establish_platform_connection(
        self,
        connection: PlatformConnection
    ) -> None:
        """Establish new platform connection"""
        
        connection_key = f"{connection.platform.value}:{connection.user_id}"
        self._active_connections[connection_key] = connection
        
        self.platform_connections_total.labels(
            platform=connection.platform.value,
            integration_type=connection.integration_type.value,
            status=connection.status.value,
            user_id=connection.user_id
        ).inc()
        
        self.active_platform_connections.labels(
            platform=connection.platform.value,
            integration_type=connection.integration_type.value
        ).inc()
        
        # Store connection details
        await self.redis_manager.set(
            f"platform_connection:{connection_key}",
            connection.__dict__,
            ttl=86400  # 24 hours
        )
        
        self.logger.info(
            f"Platform connection established: {connection.platform.value} "
            f"for user {connection.user_id}"
        )
    
    async def disconnect_platform(
        self,
        platform: Platform,
        user_id: str,
        disconnect_reason: str = "user_initiated"
    ) -> None:
        """Disconnect from platform"""
        
        connection_key = f"{platform.value}:{user_id}"
        
        if connection_key not in self._active_connections:
            self.logger.warning(f"Connection {connection_key} not found")
            return
        
        connection = self._active_connections[connection_key]
        disconnect_time = datetime.utcnow()
        duration_hours = (disconnect_time - connection.connected_at).total_seconds() / 3600
        
        # Update metrics
        self.connection_duration.labels(
            platform=platform.value,
            integration_type=connection.integration_type.value,
            disconnect_reason=disconnect_reason
        ).observe(duration_hours)
        
        self.active_platform_connections.labels(
            platform=platform.value,
            integration_type=connection.integration_type.value
        ).dec()
        
        # Clean up
        del self._active_connections[connection_key]
        await self.redis_manager.delete(f"platform_connection:{connection_key}")
        
        self.logger.info(
            f"Platform disconnected: {platform.value} for user {user_id} "
            f"after {duration_hours:.2f} hours"
        )
    
    async def record_authentication_attempt(
        self,
        platform: Platform,
        user_id: str,
        auth_method: str,
        success: bool,
        failure_reason: Optional[str] = None
    ) -> None:
        """Record authentication attempt"""
        
        result = "success" if success else "failure"
        
        self.authentication_attempts_total.labels(
            platform=platform.value,
            auth_method=auth_method,
            result=result,
            user_id=user_id
        ).inc()
        
        # Store failure details if applicable
        if not success and failure_reason:
            await self.redis_manager.lpush(
                f"auth_failures:{platform.value}",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "auth_method": auth_method,
                    "failure_reason": failure_reason
                }
            )
        
        self.logger.info(
            f"Authentication attempt: {platform.value} - {result} "
            f"({auth_method} for {user_id})"
        )
    
    async def record_token_refresh(
        self,
        platform: Platform,
        success: bool,
        refresh_reason: str = "automatic"
    ) -> None:
        """Record token refresh operation"""
        
        result = "success" if success else "failure"
        
        self.token_refresh_total.labels(
            platform=platform.value,
            result=result,
            refresh_reason=refresh_reason
        ).inc()
        
        self.logger.info(f"Token refresh: {platform.value} - {result}")
    
    async def update_api_quota_usage(
        self,
        platform: Platform,
        quota_type: str,
        usage_percent: float,
        time_window: str = "1h"
    ) -> None:
        """Update API quota usage metrics"""
        
        self.api_quota_usage.labels(
            platform=platform.value,
            quota_type=quota_type,
            time_window=time_window
        ).set(usage_percent)
        
        # Alert if quota usage is high
        if usage_percent > 90:
            await self._trigger_quota_alert(platform, quota_type, usage_percent)
    
    async def record_data_sync_operation(
        self,
        platform: Platform,
        sync_type: str,
        direction: str,  # "upload" or "download"
        success: bool,
        duration_seconds: float,
        data_size_bytes: int = 0
    ) -> None:
        """Record data synchronization operation"""
        
        result = "success" if success else "failure"
        
        # Determine data size range
        if data_size_bytes < 1000000:  # < 1MB
            size_range = "small"
        elif data_size_bytes < 10000000:  # < 10MB
            size_range = "medium"
        elif data_size_bytes < 100000000:  # < 100MB
            size_range = "large"
        else:
            size_range = "xlarge"
        
        self.data_sync_operations_total.labels(
            platform=platform.value,
            sync_type=sync_type,
            direction=direction,
            result=result
        ).inc()
        
        if success:
            self.data_sync_duration.labels(
                platform=platform.value,
                sync_type=sync_type,
                data_size_range=size_range
            ).observe(duration_seconds)
        
        self.logger.info(
            f"Data sync: {platform.value} {sync_type} {direction} - "
            f"{result} ({duration_seconds:.2f}s, {data_size_bytes} bytes)"
        )
    
    async def record_webhook(
        self,
        platform: Platform,
        event_type: str,
        processing_duration_seconds: float,
        success: bool = True
    ) -> None:
        """Record webhook reception and processing"""
        
        status = "success" if success else "failure"
        
        self.webhooks_received_total.labels(
            platform=platform.value,
            event_type=event_type,
            status=status
        ).inc()
        
        if success:
            self.webhook_processing_duration.labels(
                platform=platform.value,
                event_type=event_type
            ).observe(processing_duration_seconds)
        
        self.logger.debug(
            f"Webhook processed: {platform.value} {event_type} - "
            f"{status} ({processing_duration_seconds:.3f}s)"
        )
    
    async def record_integration_error(
        self,
        platform: Platform,
        error_type: str,
        severity: str,
        endpoint_type: APIEndpointType,
        error_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record integration error"""
        
        self.integration_errors_total.labels(
            platform=platform.value,
            error_type=error_type,
            severity=severity,
            endpoint_type=endpoint_type.value
        ).inc()
        
        # Store error details for analysis
        if error_details:
            await self.redis_manager.lpush(
                f"integration_errors:{platform.value}",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_type": error_type,
                    "severity": severity,
                    "endpoint_type": endpoint_type.value,
                    "details": error_details
                }
            )
        
        self.logger.warning(
            f"Integration error: {platform.value} - {error_type} ({severity})"
        )
    
    async def update_platform_health_score(
        self,
        platform: Platform,
        integration_type: IntegrationType,
        health_score: float
    ) -> None:
        """Update platform integration health score"""
        
        self.platform_health_score.labels(
            platform=platform.value,
            integration_type=integration_type.value
        ).set(health_score)
        
        # Alert if health score is low
        if health_score < 70:
            await self._trigger_health_alert(platform, integration_type, health_score)
    
    async def _trigger_quota_alert(
        self,
        platform: Platform,
        quota_type: str,
        usage_percent: float
    ) -> None:
        """Trigger quota usage alert"""
        
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": "api_quota_high",
            "platform": platform.value,
            "quota_type": quota_type,
            "usage_percent": usage_percent
        }
        
        await self.redis_manager.lpush("platform_alerts", alert_data)
        
        self.logger.warning(
            f"High quota usage alert: {platform.value} {quota_type} "
            f"at {usage_percent:.1f}%"
        )
    
    async def _trigger_health_alert(
        self,
        platform: Platform,
        integration_type: IntegrationType,
        health_score: float
    ) -> None:
        """Trigger platform health alert"""
        
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": "platform_health_low",
            "platform": platform.value,
            "integration_type": integration_type.value,
            "health_score": health_score
        }
        
        await self.redis_manager.lpush("platform_alerts", alert_data)
        
        self.logger.warning(
            f"Low health score alert: {platform.value} {integration_type.value} "
            f"at {health_score:.1f}"
        )
    
    async def get_platform_summary(
        self,
        platform: Optional[Platform] = None
    ) -> Dict[str, Any]:
        """Get comprehensive platform integration summary"""
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_statistics": {},
            "platform_breakdown": {}
        }
        
        # Filter connections by platform if specified
        connections = list(self._active_connections.values())
        if platform:
            connections = [c for c in connections if c.platform == platform]
        
        if connections:
            summary["overall_statistics"] = {
                "total_active_connections": len(connections),
                "platforms_connected": len(set(c.platform for c in connections)),
                "unique_users": len(set(c.user_id for c in connections)),
                "integration_types": len(set(c.integration_type for c in connections))
            }
            
            # Breakdown by platform
            for plat in Platform:
                plat_connections = [c for c in connections if c.platform == plat]
                if plat_connections:
                    summary["platform_breakdown"][plat.value] = {
                        "active_connections": len(plat_connections),
                        "integration_types": list(set(c.integration_type.value for c in plat_connections)),
                        "connection_statuses": list(set(c.status.value for c in plat_connections))
                    }
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the platform integration metrics collector"""



        
        return {
            "status": "healthy",
            "active_connections": len(self._active_connections),
            "api_call_history_size": len(self._api_call_history),
            "metrics_initialized": self.prometheus_manager is not None,
            "redis_connected": self.redis_manager is not None,
            "last_updated": datetime.utcnow().isoformat()
        }
