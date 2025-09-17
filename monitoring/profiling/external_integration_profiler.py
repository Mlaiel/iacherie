"""⚡ External Integration Profiling System
=========================================

Advanced external integration performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for third-party APIs, social media integrations, and external services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization  
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)

# Try to import HTTP libraries
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class IntegrationType(Enum):
    """Types of external integrations"""
    SOCIAL_MEDIA = "social_media"
    PAYMENT_GATEWAY = "payment_gateway"
    CDN_SERVICE = "cdn_service"
    CLOUD_STORAGE = "cloud_storage"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    ANALYTICS_SERVICE = "analytics_service"
    AI_SERVICE = "ai_service"
    WEBHOOK = "webhook"
    THIRD_PARTY_API = "third_party_api"


class SocialPlatform(Enum):
    """Social media platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"


class IntegrationOperation(Enum):
    """Integration operations"""
    AUTHENTICATE = "authenticate"
    UPLOAD_CONTENT = "upload_content"
    FETCH_DATA = "fetch_data"
    WEBHOOK_RECEIVE = "webhook_receive"
    PAYMENT_PROCESS = "payment_process"
    NOTIFICATION_SEND = "notification_send"
    ANALYTICS_SYNC = "analytics_sync"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"


@dataclass
class IntegrationMetadata:
    """Metadata for external integrations"""
    integration_name: str
    integration_type: IntegrationType
    operation: IntegrationOperation
    endpoint_url: str
    api_version: str = "v1"
    rate_limit: Optional[int] = None
    requires_auth: bool = True
    payload_size: int = 0
    content_type: Optional[str] = None
    social_platform: Optional[SocialPlatform] = None


@dataclass
class ExternalIntegrationMetrics:
    """External integration performance metrics"""
    operation_id: str
    integration_name: str
    integration_type: IntegrationType
    operation: IntegrationOperation
    endpoint_url: str
    request_time_ms: float
    response_time_ms: float
    total_time_ms: float
    auth_time_ms: float
    payload_size_bytes: int
    response_size_bytes: int
    status_code: int
    rate_limit_remaining: int
    rate_limit_reset: datetime
    retry_count: int
    cache_used: bool
    ssl_verification: bool
    error_type: Optional[str]
    api_quota_used: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationBottleneck:
    """External integration bottleneck information"""
    bottleneck_type: str
    severity: str
    integration_name: str
    integration_type: IntegrationType
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class ExternalIntegrationProfiler:
    """
    External integration performance profiler for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 10.0,
                 max_history_size: int = 15000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.integration_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_integrations: Dict[str, Dict] = {}
        
        # Integration configurations
        self.integration_configs: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_integration_threshold': 5000.0,   # 5 seconds
            'very_slow_integration_threshold': 10000.0, # 10 seconds
            'high_error_rate_threshold': 10.0,     # 10%
            'rate_limit_threshold': 80.0,          # 80% of rate limit
            'auth_time_threshold': 1000.0,         # 1 second
            'quota_usage_threshold': 90.0          # 90% of quota
        }
        
        logger.info("ExternalIntegrationProfiler initialized")

    def start_monitoring(self):
        """Start background integration monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("External integration monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("External integration monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_rate_limits()
                self._analyze_integration_health()
                self._cleanup_stale_integrations()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in integration monitoring loop: {e}")

    def _check_rate_limits(self):
        """Check rate limits for all integrations"""
        try:
            current_time = datetime.utcnow()
            
            for integration_name, rate_limit_info in self.rate_limits.items():
                reset_time = rate_limit_info.get('reset_time')
                if reset_time and current_time >= reset_time:
                    # Reset rate limit
                    self.rate_limits[integration_name]['remaining'] = rate_limit_info.get('limit', 1000)
                    self.rate_limits[integration_name]['reset_time'] = None
                    
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")

    def _analyze_integration_health(self):
        """Analyze overall integration health"""
        try:
            # Get recent metrics for each integration
            now = datetime.utcnow()
            recent_cutoff = now - timedelta(minutes=30)
            
            integration_stats = defaultdict(list)
            for metrics in list(self.integration_metrics_history):
                if metrics.timestamp >= recent_cutoff:
                    integration_stats[metrics.integration_name].append(metrics)
            
            # Analyze each integration
            for integration_name, metrics_list in integration_stats.items():
                if metrics_list:
                    avg_response_time = statistics.mean([m.response_time_ms for m in metrics_list])
                    error_rate = (sum(1 for m in metrics_list if m.status_code >= 400) / len(metrics_list)) * 100
                    
                    # Create health check if issues detected
                    if avg_response_time > 5000 or error_rate > 10:
                        logger.warning(f"Integration health issue detected for {integration_name}: "
                                     f"avg_response_time={avg_response_time:.1f}ms, error_rate={error_rate:.1f}%")
                        
        except Exception as e:
            logger.error(f"Error analyzing integration health: {e}")

    def _cleanup_stale_integrations(self):
        """Clean up stale active integrations"""
        now = time.time()
        stale_threshold = 300  # 5 minutes
        
        stale_integrations = [
            int_id for int_id, int_data in self.active_integrations.items()
            if now - int_data.get('start_time', now) > stale_threshold
        ]
        
        for int_id in stale_integrations:
            self.active_integrations.pop(int_id, None)

    def register_integration(self,
                           integration_name: str,
                           integration_type: IntegrationType,
                           base_url: str,
                           rate_limit: Optional[int] = None,
                           api_quota: Optional[int] = None):
        """
        Register an external integration
        
        Args:
            integration_name: Name of the integration
            integration_type: Type of integration
            base_url: Base URL for the integration
            rate_limit: Rate limit per hour
            api_quota: API quota per day
        """
        self.integration_configs[integration_name] = {
            'type': integration_type,
            'base_url': base_url,
            'rate_limit': rate_limit,
            'api_quota': api_quota,
            'registered_at': datetime.utcnow()
        }
        
        if rate_limit:
            self.rate_limits[integration_name] = {
                'limit': rate_limit,
                'remaining': rate_limit,
                'reset_time': None
            }
        
        logger.info(f"Registered integration: {integration_name} ({integration_type.value})")

    def profile_integration_call(self,
                                integration_name: str,
                                operation: IntegrationOperation,
                                endpoint_url: str,
                                integration_type: IntegrationType = IntegrationType.THIRD_PARTY_API,
                                **kwargs) -> str:
        """
        Start profiling an integration call
        
        Args:
            integration_name: Name of the integration
            operation: Type of operation
            endpoint_url: Full endpoint URL
            integration_type: Type of integration
            **kwargs: Additional metadata
            
        Returns:
            Integration ID for tracking
        """
        integration_id = hashlib.md5(f"{integration_name}_{operation.value}_{time.time()}".encode()).hexdigest()[:16]
        start_time = time.time()
        
        # Store integration start info
        self.active_integrations[integration_id] = {
            'start_time': start_time,
            'integration_name': integration_name,
            'operation': operation,
            'endpoint_url': endpoint_url,
            'integration_type': integration_type,
            'metadata': kwargs
        }
        
        return integration_id

    def complete_integration_call(self,
                                integration_id: str,
                                status_code: int,
                                response_size_bytes: int = 0,
                                auth_time_ms: float = 0.0,
                                rate_limit_remaining: int = 1000,
                                rate_limit_reset: Optional[datetime] = None,
                                retry_count: int = 0,
                                cache_used: bool = False,
                                ssl_verification: bool = True,
                                error_type: Optional[str] = None,
                                api_quota_used: float = 0.0,
                                **kwargs) -> ExternalIntegrationMetrics:
        """
        Complete profiling an integration call
        
        Args:
            integration_id: Integration ID from profile_integration_call
            status_code: Response status code
            response_size_bytes: Size of response
            auth_time_ms: Time spent on authentication
            rate_limit_remaining: Remaining rate limit quota
            rate_limit_reset: Rate limit reset time
            retry_count: Number of retries
            cache_used: Whether cache was used
            ssl_verification: Whether SSL was verified
            error_type: Type of error if any
            api_quota_used: API quota used (percentage)
            **kwargs: Additional response metadata
            
        Returns:
            ExternalIntegrationMetrics with profiling results
        """
        end_time = time.time()
        
        # Get integration info
        integration_info = self.active_integrations.get(integration_id)
        if not integration_info:
            raise ValueError(f"Integration ID {integration_id} not found")
        
        start_time = integration_info['start_time']
        total_time_ms = (end_time - start_time) * 1000
        
        # Update rate limit info
        if rate_limit_remaining is not None:
            integration_name = integration_info['integration_name']
            if integration_name in self.rate_limits:
                self.rate_limits[integration_name]['remaining'] = rate_limit_remaining
                if rate_limit_reset:
                    self.rate_limits[integration_name]['reset_time'] = rate_limit_reset
        
        # Create metrics
        metrics = ExternalIntegrationMetrics(
            operation_id=integration_id,
            integration_name=integration_info['integration_name'],
            integration_type=integration_info['integration_type'],
            operation=integration_info['operation'],
            endpoint_url=integration_info['endpoint_url'],
            request_time_ms=0.0,  # Would need more detailed timing
            response_time_ms=total_time_ms - auth_time_ms,
            total_time_ms=total_time_ms,
            auth_time_ms=auth_time_ms,
            payload_size_bytes=integration_info['metadata'].get('payload_size', 0),
            response_size_bytes=response_size_bytes,
            status_code=status_code,
            rate_limit_remaining=rate_limit_remaining,
            rate_limit_reset=rate_limit_reset or datetime.utcnow(),
            retry_count=retry_count,
            cache_used=cache_used,
            ssl_verification=ssl_verification,
            error_type=error_type,
            api_quota_used=api_quota_used,
            timestamp=datetime.utcnow(),
            metadata={
                **integration_info['metadata'],
                **kwargs
            }
        )
        
        # Store metrics
        self.integration_metrics_history.append(metrics)
        
        # Remove from active integrations
        self.active_integrations.pop(integration_id, None)
        
        # Check for bottlenecks
        self._analyze_integration_bottlenecks(metrics)
        
        return metrics

    def _analyze_integration_bottlenecks(self, metrics: ExternalIntegrationMetrics):
        """Analyze integration bottlenecks"""
        bottlenecks = []
        
        # Check response time
        if metrics.total_time_ms > self.thresholds['very_slow_integration_threshold']:
            severity = "critical"
        elif metrics.total_time_ms > self.thresholds['slow_integration_threshold']:
            severity = "high"
        else:
            severity = None
        
        if severity:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="slow_integration",
                severity=severity,
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"Integration response too slow: {metrics.total_time_ms:.1f}ms",
                impact="Poor user experience, workflow delays",
                recommendations=[
                    "Optimize integration logic",
                    "Implement caching",
                    "Use async processing",
                    "Consider alternative providers"
                ],
                detected_at=datetime.utcnow(),
                metrics={'total_time_ms': metrics.total_time_ms}
            ))
        
        # Check rate limit usage
        if metrics.rate_limit_remaining is not None:
            integration_config = self.integration_configs.get(metrics.integration_name, {})
            rate_limit = integration_config.get('rate_limit')
            if rate_limit:
                usage_percentage = ((rate_limit - metrics.rate_limit_remaining) / rate_limit) * 100
                if usage_percentage > self.thresholds['rate_limit_threshold']:
                    bottlenecks.append(IntegrationBottleneck(
                        bottleneck_type="rate_limit_approaching",
                        severity="medium",
                        integration_name=metrics.integration_name,
                        integration_type=metrics.integration_type,
                        description=f"Rate limit usage high: {usage_percentage:.1f}%",
                        impact="Risk of hitting rate limits, API throttling",
                        recommendations=[
                            "Implement rate limiting logic",
                            "Use request queuing",
                            "Cache responses when possible",
                            "Optimize API call frequency"
                        ],
                        detected_at=datetime.utcnow(),
                        metrics={'rate_limit_usage': usage_percentage}
                    ))
        
        # Check authentication time
        if metrics.auth_time_ms > self.thresholds['auth_time_threshold']:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="slow_authentication",
                severity="medium",
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"Authentication too slow: {metrics.auth_time_ms:.1f}ms",
                impact="Delayed API calls, poor performance",
                recommendations=[
                    "Cache authentication tokens",
                    "Use longer-lived tokens",
                    "Implement token refresh logic",
                    "Optimize auth flow"
                ],
                detected_at=datetime.utcnow(),
                metrics={'auth_time_ms': metrics.auth_time_ms}
            ))
        
        # Check API quota usage
        if metrics.api_quota_used > self.thresholds['quota_usage_threshold']:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="quota_limit_approaching",
                severity="high",
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"API quota usage high: {metrics.api_quota_used:.1f}%",
                impact="Risk of hitting quota limits, service disruption",
                recommendations=[
                    "Monitor quota usage closely",
                    "Implement quota management",
                    "Optimize API usage patterns",
                    "Consider upgrading API plan"
                ],
                detected_at=datetime.utcnow(),
                metrics={'api_quota_used': metrics.api_quota_used}
            ))
        
        # Check for errors
        if metrics.status_code >= 500:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="integration_error",
                severity="critical",
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"Integration server error: {metrics.status_code}",
                impact="Integration functionality disrupted",
                recommendations=[
                    "Check integration service status",
                    "Implement error handling",
                    "Add retry mechanisms",
                    "Monitor service health"
                ],
                detected_at=datetime.utcnow(),
                metrics={'status_code': metrics.status_code}
            ))
        elif metrics.status_code >= 400:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="integration_client_error",
                severity="medium",
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"Integration client error: {metrics.status_code}",
                impact="Failed integration requests",
                recommendations=[
                    "Validate request parameters",
                    "Check API documentation",
                    "Review authentication",
                    "Monitor error patterns"
                ],
                detected_at=datetime.utcnow(),
                metrics={'status_code': metrics.status_code}
            ))
        
        # Check retry count
        if metrics.retry_count > 0:
            bottlenecks.append(IntegrationBottleneck(
                bottleneck_type="high_retry_count",
                severity="medium",
                integration_name=metrics.integration_name,
                integration_type=metrics.integration_type,
                description=f"High retry count: {metrics.retry_count}",
                impact="Increased latency, resource usage",
                recommendations=[
                    "Investigate intermittent failures",
                    "Optimize retry policies",
                    "Implement exponential backoff",
                    "Check network stability"
                ],
                detected_at=datetime.utcnow(),
                metrics={'retry_count': metrics.retry_count}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get integration performance summary"""
        if not self.integration_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.integration_metrics_history)[-1000:]  # Last 1000 calls
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in recent_metrics]
        total_times = [m.total_time_ms for m in recent_metrics]
        auth_times = [m.auth_time_ms for m in recent_metrics if m.auth_time_ms > 0]
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        cache_hits = sum(1 for m in recent_metrics if m.cache_used)
        retries = sum(m.retry_count for m in recent_metrics)
        
        return {
            "summary": {
                "total_integration_calls": len(recent_metrics),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "avg_total_time_ms": statistics.mean(total_times) if total_times else 0,
                "avg_auth_time_ms": statistics.mean(auth_times) if auth_times else 0,
                "p95_response_time_ms": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "cache_hit_rate": (cache_hits / len(recent_metrics)) * 100,
                "total_retries": retries,
                "active_integrations": len(self.active_integrations),
                "registered_integrations": len(self.integration_configs)
            },
            "by_integration": self._get_metrics_by_integration(),
            "by_integration_type": self._get_metrics_by_integration_type(),
            "by_operation": self._get_metrics_by_operation(),
            "rate_limits": self._get_rate_limit_status(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_integration_optimization_recommendations()
        }

    def _get_metrics_by_integration(self) -> Dict[str, Dict]:
        """Get metrics grouped by integration"""
        metrics_by_integration = defaultdict(list)
        
        for metrics in list(self.integration_metrics_history)[-1000:]:
            metrics_by_integration[metrics.integration_name].append(metrics)
        
        result = {}
        for integration_name, metrics_list in metrics_by_integration.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[integration_name] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100,
                "cache_hit_rate": (sum(1 for m in metrics_list if m.cache_used) / len(metrics_list)) * 100,
                "avg_retries": statistics.mean([m.retry_count for m in metrics_list]),
                "last_call": max(m.timestamp for m in metrics_list).isoformat()
            }
        
        return dict(sorted(result.items(), key=lambda x: x[1]['calls'], reverse=True)[:10])

    def _get_metrics_by_integration_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by integration type"""
        metrics_by_type = defaultdict(list)
        
        for metrics in list(self.integration_metrics_history)[-1000:]:
            metrics_by_type[metrics.integration_type.value].append(metrics)
        
        result = {}
        for integration_type, metrics_list in metrics_by_type.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[integration_type] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_operation(self) -> Dict[str, Dict]:
        """Get metrics grouped by operation type"""
        metrics_by_op = defaultdict(list)
        
        for metrics in list(self.integration_metrics_history)[-1000:]:
            metrics_by_op[metrics.operation.value].append(metrics)
        
        result = {}
        for operation, metrics_list in metrics_by_op.items():
            response_times = [m.response_time_ms for m in metrics_list]
            
            result[operation] = {
                "calls": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (sum(1 for m in metrics_list if m.status_code >= 400) / len(metrics_list)) * 100
            }
        
        return result

    def _get_rate_limit_status(self) -> Dict[str, Dict]:
        """Get current rate limit status"""
        result = {}
        for integration_name, rate_limit_info in self.rate_limits.items():
            limit = rate_limit_info.get('limit', 0)
            remaining = rate_limit_info.get('remaining', 0)
            usage_percentage = ((limit - remaining) / limit * 100) if limit > 0 else 0
            
            result[integration_name] = {
                "limit": limit,
                "remaining": remaining,
                "usage_percentage": usage_percentage,
                "reset_time": rate_limit_info.get('reset_time').isoformat() if rate_limit_info.get('reset_time') else None
            }
        
        return result

    def _get_integration_optimization_recommendations(self) -> List[str]:
        """Get integration optimization recommendations"""
        recommendations = []
        
        if not self.integration_metrics_history:
            return ["Start profiling integration calls to get recommendations"]
        
        recent_metrics = list(self.integration_metrics_history)[-500:]
        
        # Calculate key metrics
        avg_response_time = statistics.mean([m.response_time_ms for m in recent_metrics])
        error_rate = (sum(1 for m in recent_metrics if m.status_code >= 400) / len(recent_metrics)) * 100
        cache_hit_rate = (sum(1 for m in recent_metrics if m.cache_used) / len(recent_metrics)) * 100
        avg_retries = statistics.mean([m.retry_count for m in recent_metrics])
        
        if avg_response_time > 5000:
            recommendations.append("High integration response times - optimize slow integrations")
        if error_rate > 10:
            recommendations.append("High integration error rate - investigate failing integrations")
        if cache_hit_rate < 30:
            recommendations.append("Low cache usage - implement caching for external calls")
        if avg_retries > 0.5:
            recommendations.append("High retry rate - investigate intermittent failures")
        
        # Check rate limit usage
        high_usage_integrations = []
        for integration_name, rate_limit_info in self.rate_limits.items():
            limit = rate_limit_info.get('limit', 0)
            remaining = rate_limit_info.get('remaining', 0)
            if limit > 0:
                usage_percentage = ((limit - remaining) / limit) * 100
                if usage_percentage > 80:
                    high_usage_integrations.append(integration_name)
        
        if high_usage_integrations:
            recommendations.append(f"High rate limit usage: {', '.join(high_usage_integrations[:3])}")
        
        if not recommendations:
            recommendations.append("External integrations performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[IntegrationBottleneck]:
        """Get recent integration bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def export_metrics(self, format: str = "json") -> str:
        """Export integration metrics"""
        data = {
            "integration_metrics": [
                {
                    "operation_id": m.operation_id,
                    "integration_name": m.integration_name,
                    "integration_type": m.integration_type.value,
                    "operation": m.operation.value,
                    "response_time_ms": m.response_time_ms,
                    "status_code": m.status_code,
                    "rate_limit_remaining": m.rate_limit_remaining,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.integration_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "integration_name": b.integration_name,
                    "integration_type": b.integration_type.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ],
            "rate_limits": self._get_rate_limit_status()
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_external_integration_profiler(monitoring_interval: float = 10.0,
                                        max_history_size: int = 15000,
                                        start_monitoring: bool = True) -> ExternalIntegrationProfiler:
    """
    Create and configure an external integration profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured ExternalIntegrationProfiler instance
    """
    profiler = ExternalIntegrationProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_external_integration_profiler()
    
    try:
        # Register integrations
        profiler.register_integration(
            "youtube-api",
            IntegrationType.SOCIAL_MEDIA,
            "https://www.googleapis.com/youtube/v3/",
            rate_limit=10000  # 10k requests per hour
        )
        
        profiler.register_integration(
            "stripe-payment",
            IntegrationType.PAYMENT_GATEWAY,
            "https://api.stripe.com/v1/",
            rate_limit=1000  # 1k requests per hour
        )
        
        # Example: Profile an integration call
        integration_id = profiler.profile_integration_call(
            integration_name="youtube-api",
            operation=IntegrationOperation.UPLOAD_CONTENT,
            endpoint_url="https://www.googleapis.com/youtube/v3/videos",
            integration_type=IntegrationType.SOCIAL_MEDIA,
            payload_size=5 * 1024 * 1024  # 5MB video
        )
        
        # Simulate some processing time
        time.sleep(0.2)
        
        # Complete the integration call
        metrics = profiler.complete_integration_call(
            integration_id=integration_id,
            status_code=200,
            response_size_bytes=1024,
            auth_time_ms=150.0,
            rate_limit_remaining=9950,
            retry_count=0,
            cache_used=False,
            api_quota_used=5.2
        )
        
        print(f"Integration call response time: {metrics.response_time_ms:.2f}ms")
        print(f"Status code: {metrics.status_code}")
        print(f"Rate limit remaining: {metrics.rate_limit_remaining}")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Integration performance summary: {json.dumps(summary, indent=2)}")
        
    finally:
        profiler.stop_monitoring()