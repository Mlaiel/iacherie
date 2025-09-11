"""
📡 Platform Monitoring Microservice
Platform health and performance monitoring across multiple social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import statistics
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MonitoringType(str, Enum):
    """Types of platform monitoring"""
    API_HEALTH = "api_health"
    PERFORMANCE = "performance"
    RATE_LIMITS = "rate_limits"
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    FEATURE_AVAILABILITY = "feature_availability"
    CONTENT_DELIVERY = "content_delivery"
    AUTHENTICATION = "authentication"
    COMPLIANCE = "compliance"


class HealthStatus(str, Enum):
    """Platform health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"
    OFFLINE = "offline"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MetricType(str, Enum):
    """Types of metrics to monitor"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    AVAILABILITY = "availability"
    QUOTA_USAGE = "quota_usage"
    CONCURRENT_USERS = "concurrent_users"
    DATA_TRANSFER = "data_transfer"


@dataclass
class PlatformEndpoint:
    """Platform API endpoint configuration"""
    endpoint_id: str
    platform_id: str
    url: str
    method: str
    purpose: str
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    headers: Dict[str, str] = field(default_factory=dict)
    auth_required: bool = True


@dataclass
class HealthCheck:
    """Health check result"""
    check_id: str
    platform_id: str
    endpoint_id: str
    status: HealthStatus
    response_time_ms: float
    status_code: Optional[int]
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_id: str
    platform_id: str
    metric_type: MetricType
    value: float
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """Monitoring alert"""
    alert_id: str
    platform_id: str
    alert_type: MonitoringType
    severity: AlertSeverity
    title: str
    description: str
    threshold_breached: Dict[str, Any]
    current_value: Any
    expected_value: Any
    suggested_actions: List[str]
    auto_resolved: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


@dataclass
class PlatformStatus:
    """Overall platform status"""
    platform_id: str
    overall_status: HealthStatus
    last_check: datetime
    uptime_percentage: float
    average_response_time: float
    error_rate: float
    active_alerts: int
    recent_incidents: List[Dict[str, Any]]
    service_levels: Dict[str, HealthStatus]
    metrics_summary: Dict[MetricType, float]


class PlatformHealthChecker:
    """Monitors platform health and availability"""
    
    def __init__(self):
        self.endpoints: Dict[str, List[PlatformEndpoint]] = {}
        self.health_history: Dict[str, List[HealthCheck]] = {}
        self._setup_platform_endpoints()
    
    def _setup_platform_endpoints(self) -> None:
        """Setup monitoring endpoints for each platform"""
        
        # YouTube endpoints
        youtube_endpoints = [
            PlatformEndpoint(
                endpoint_id="youtube_videos_api",
                platform_id="youtube",
                url="https://www.googleapis.com/youtube/v3/videos",
                method="GET",
                purpose="Video metadata API",
                rate_limit=10000,
                timeout_seconds=10
            ),
            PlatformEndpoint(
                endpoint_id="youtube_channels_api",
                platform_id="youtube",
                url="https://www.googleapis.com/youtube/v3/channels",
                method="GET",
                purpose="Channel information API",
                rate_limit=10000,
                timeout_seconds=10
            ),
            PlatformEndpoint(
                endpoint_id="youtube_upload_api",
                platform_id="youtube",
                url="https://www.googleapis.com/upload/youtube/v3/videos",
                method="POST",
                purpose="Video upload API",
                rate_limit=6,
                timeout_seconds=300
            )
        ]
        
        # Instagram endpoints
        instagram_endpoints = [
            PlatformEndpoint(
                endpoint_id="instagram_basic_api",
                platform_id="instagram",
                url="https://graph.instagram.com/me",
                method="GET",
                purpose="Basic profile information",
                rate_limit=200,
                timeout_seconds=10
            ),
            PlatformEndpoint(
                endpoint_id="instagram_media_api",
                platform_id="instagram",
                url="https://graph.instagram.com/me/media",
                method="GET",
                purpose="Media retrieval API",
                rate_limit=200,
                timeout_seconds=15
            ),
            PlatformEndpoint(
                endpoint_id="instagram_publish_api",
                platform_id="instagram",
                url="https://graph.instagram.com/me/media",
                method="POST",
                purpose="Content publishing API",
                rate_limit=25,
                timeout_seconds=60
            )
        ]
        
        # TikTok endpoints
        tiktok_endpoints = [
            PlatformEndpoint(
                endpoint_id="tiktok_user_api",
                platform_id="tiktok",
                url="https://open-api.tiktok.com/user/info/",
                method="GET",
                purpose="User information API",
                rate_limit=100,
                timeout_seconds=10
            ),
            PlatformEndpoint(
                endpoint_id="tiktok_video_api",
                platform_id="tiktok",
                url="https://open-api.tiktok.com/video/list/",
                method="GET",
                purpose="Video list API",
                rate_limit=100,
                timeout_seconds=15
            ),
            PlatformEndpoint(
                endpoint_id="tiktok_upload_api",
                platform_id="tiktok",
                url="https://open-api.tiktok.com/video/upload/",
                method="POST",
                purpose="Video upload API",
                rate_limit=10,
                timeout_seconds=120
            )
        ]
        
        self.endpoints["youtube"] = youtube_endpoints
        self.endpoints["instagram"] = instagram_endpoints
        self.endpoints["tiktok"] = tiktok_endpoints
    
    async def check_platform_health(self, platform_id: str) -> List[HealthCheck]:
        """Check health of all endpoints for a platform"""
        try:
            platform_endpoints = self.endpoints.get(platform_id, [])
            health_checks = []
            
            for endpoint in platform_endpoints:
                health_check = await self._check_endpoint_health(endpoint)
                health_checks.append(health_check)
                
                # Store in history
                if platform_id not in self.health_history:
                    self.health_history[platform_id] = []
                self.health_history[platform_id].append(health_check)
                
                # Keep only last 1000 checks per platform
                if len(self.health_history[platform_id]) > 1000:
                    self.health_history[platform_id] = self.health_history[platform_id][-1000:]
            
            return health_checks
            
        except Exception as e:
            logger.error(f"Failed to check platform health for {platform_id}: {e}")
            return []
    
    async def _check_endpoint_health(self, endpoint: PlatformEndpoint) -> HealthCheck:
        """Check health of a specific endpoint"""
        check_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Simulate API call (in real implementation, use aiohttp)
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Simulate response
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            status_code = 200  # Simulate successful response
            
            # Determine health status
            if response_time > endpoint.timeout_seconds * 1000:
                status = HealthStatus.UNHEALTHY
                error_message = "Response time exceeded timeout"
            elif response_time > 5000:  # 5 seconds
                status = HealthStatus.DEGRADED
                error_message = "High response time"
            elif status_code not in endpoint.expected_status_codes:
                status = HealthStatus.UNHEALTHY
                error_message = f"Unexpected status code: {status_code}"
            else:
                status = HealthStatus.HEALTHY
                error_message = None
            
            return HealthCheck(
                check_id=check_id,
                platform_id=endpoint.platform_id,
                endpoint_id=endpoint.endpoint_id,
                status=status,
                response_time_ms=response_time,
                status_code=status_code,
                error_message=error_message,
                metadata={
                    "url": endpoint.url,
                    "method": endpoint.method,
                    "purpose": endpoint.purpose
                }
            )
            
        except Exception as e:
            return HealthCheck(
                check_id=check_id,
                platform_id=endpoint.platform_id,
                endpoint_id=endpoint.endpoint_id,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=endpoint.timeout_seconds * 1000,
                status_code=None,
                error_message=str(e),
                metadata={
                    "url": endpoint.url,
                    "method": endpoint.method,
                    "purpose": endpoint.purpose
                }
            )
    
    def get_platform_uptime(
        self,
        platform_id: str,
        hours: int = 24
    ) -> float:
        """Calculate platform uptime percentage"""
        if platform_id not in self.health_history:
            return 0.0
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_checks = [
            check for check in self.health_history[platform_id]
            if check.checked_at >= cutoff_time
        ]
        
        if not recent_checks:
            return 0.0
        
        healthy_checks = len([
            check for check in recent_checks
            if check.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        ])
        
        return (healthy_checks / len(recent_checks)) * 100


class PerformanceMonitor:
    """Monitors platform performance metrics"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetric]] = {}
        self.thresholds: Dict[str, Dict[MetricType, float]] = {}
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self) -> None:
        """Setup default performance thresholds"""
        default_thresholds = {
            MetricType.LATENCY: 5000,  # 5 seconds
            MetricType.ERROR_RATE: 5.0,  # 5%
            MetricType.SUCCESS_RATE: 95.0,  # 95%
            MetricType.AVAILABILITY: 99.0,  # 99%
            MetricType.QUOTA_USAGE: 80.0  # 80%
        }
        
        for platform in ["youtube", "instagram", "tiktok", "twitter", "facebook"]:
            self.thresholds[platform] = default_thresholds.copy()
    
    async def collect_metrics(self, platform_id: str) -> List[PerformanceMetric]:
        """Collect performance metrics for a platform"""
        try:
            metrics = []
            timestamp = datetime.now()
            
            # Simulate metric collection
            metric_values = {
                MetricType.LATENCY: 2500 + (hash(platform_id) % 2000),  # 2.5-4.5s
                MetricType.THROUGHPUT: 100 + (hash(platform_id) % 50),  # 100-150 req/s
                MetricType.ERROR_RATE: 1.5 + (hash(platform_id) % 3),  # 1.5-4.5%
                MetricType.SUCCESS_RATE: 97.5 + (hash(platform_id) % 2),  # 97.5-99.5%
                MetricType.AVAILABILITY: 99.8 + (hash(platform_id) % 2) / 10,  # 99.8-99.9%
                MetricType.QUOTA_USAGE: 60 + (hash(platform_id) % 30)  # 60-90%
            }
            
            for metric_type, value in metric_values.items():
                metric = PerformanceMetric(
                    metric_id=str(uuid.uuid4()),
                    platform_id=platform_id,
                    metric_type=metric_type,
                    value=value,
                    unit=self._get_metric_unit(metric_type),
                    tags={"source": "platform_monitor"},
                    timestamp=timestamp
                )
                metrics.append(metric)
            
            # Store metrics
            if platform_id not in self.metrics_history:
                self.metrics_history[platform_id] = []
            
            self.metrics_history[platform_id].extend(metrics)
            
            # Keep only last 10000 metrics per platform
            if len(self.metrics_history[platform_id]) > 10000:
                self.metrics_history[platform_id] = self.metrics_history[platform_id][-10000:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics for {platform_id}: {e}")
            return []
    
    def _get_metric_unit(self, metric_type: MetricType) -> str:
        """Get unit for metric type"""
        units = {
            MetricType.LATENCY: "ms",
            MetricType.THROUGHPUT: "req/s",
            MetricType.ERROR_RATE: "%",
            MetricType.SUCCESS_RATE: "%",
            MetricType.AVAILABILITY: "%",
            MetricType.QUOTA_USAGE: "%",
            MetricType.CONCURRENT_USERS: "users",
            MetricType.DATA_TRANSFER: "MB"
        }
        return units.get(metric_type, "count")
    
    def get_metrics_summary(
        self,
        platform_id: str,
        hours: int = 24
    ) -> Dict[MetricType, Dict[str, float]]:
        """Get metrics summary for a platform"""
        if platform_id not in self.metrics_history:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            metric for metric in self.metrics_history[platform_id]
            if metric.timestamp >= cutoff_time
        ]
        
        summary = {}
        
        for metric_type in MetricType:
            type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            
            if type_metrics:
                values = [m.value for m in type_metrics]
                summary[metric_type] = {
                    "current": values[-1] if values else 0,
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return summary


class AlertManager:
    """Manages monitoring alerts and notifications"""
    
    def __init__(self):
        self.active_alerts: Dict[str, List[Alert]] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[str, Callable] = {}
        self._setup_alert_rules()
    
    def _setup_alert_rules(self) -> None:
        """Setup default alert rules"""
        self.alert_rules = {
            "high_latency": self._check_high_latency,
            "high_error_rate": self._check_high_error_rate,
            "low_availability": self._check_low_availability,
            "quota_exhaustion": self._check_quota_exhaustion,
            "endpoint_down": self._check_endpoint_down
        }
    
    async def check_alerts(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> List[Alert]:
        """Check for alert conditions"""
        try:
            new_alerts = []
            
            # Check each alert rule
            for rule_name, rule_func in self.alert_rules.items():
                alert = await rule_func(platform_id, health_checks, metrics)
                if alert:
                    new_alerts.append(alert)
            
            # Store alerts
            if platform_id not in self.active_alerts:
                self.active_alerts[platform_id] = []
            
            for alert in new_alerts:
                self.active_alerts[platform_id].append(alert)
                self.alert_history.append(alert)
                
                logger.warning(f"Alert triggered: {alert.title} for {platform_id}")
            
            return new_alerts
            
        except Exception as e:
            logger.error(f"Failed to check alerts for {platform_id}: {e}")
            return []
    
    async def _check_high_latency(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> Optional[Alert]:
        """Check for high latency alert"""
        latency_metrics = [m for m in metrics if m.metric_type == MetricType.LATENCY]
        
        if latency_metrics:
            current_latency = latency_metrics[-1].value
            threshold = 5000  # 5 seconds
            
            if current_latency > threshold:
                return Alert(
                    alert_id=str(uuid.uuid4()),
                    platform_id=platform_id,
                    alert_type=MonitoringType.PERFORMANCE,
                    severity=AlertSeverity.HIGH,
                    title="High Latency Detected",
                    description=f"Platform response time is {current_latency:.0f}ms, exceeding threshold of {threshold}ms",
                    threshold_breached={"metric": "latency", "threshold": threshold},
                    current_value=current_latency,
                    expected_value=f"< {threshold}ms",
                    suggested_actions=[
                        "Check platform status page",
                        "Review API rate limits",
                        "Implement request retry logic",
                        "Consider caching strategies"
                    ]
                )
        
        return None
    
    async def _check_high_error_rate(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> Optional[Alert]:
        """Check for high error rate alert"""
        error_metrics = [m for m in metrics if m.metric_type == MetricType.ERROR_RATE]
        
        if error_metrics:
            current_error_rate = error_metrics[-1].value
            threshold = 5.0  # 5%
            
            if current_error_rate > threshold:
                return Alert(
                    alert_id=str(uuid.uuid4()),
                    platform_id=platform_id,
                    alert_type=MonitoringType.ERROR_RATE,
                    severity=AlertSeverity.CRITICAL,
                    title="High Error Rate Detected",
                    description=f"Error rate is {current_error_rate:.1f}%, exceeding threshold of {threshold}%",
                    threshold_breached={"metric": "error_rate", "threshold": threshold},
                    current_value=current_error_rate,
                    expected_value=f"< {threshold}%",
                    suggested_actions=[
                        "Investigate recent API changes",
                        "Check authentication credentials",
                        "Review error logs",
                        "Implement circuit breaker pattern"
                    ]
                )
        
        return None
    
    async def _check_low_availability(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> Optional[Alert]:
        """Check for low availability alert"""
        availability_metrics = [m for m in metrics if m.metric_type == MetricType.AVAILABILITY]
        
        if availability_metrics:
            current_availability = availability_metrics[-1].value
            threshold = 99.0  # 99%
            
            if current_availability < threshold:
                return Alert(
                    alert_id=str(uuid.uuid4()),
                    platform_id=platform_id,
                    alert_type=MonitoringType.UPTIME,
                    severity=AlertSeverity.CRITICAL,
                    title="Low Availability Detected",
                    description=f"Platform availability is {current_availability:.1f}%, below threshold of {threshold}%",
                    threshold_breached={"metric": "availability", "threshold": threshold},
                    current_value=current_availability,
                    expected_value=f"> {threshold}%",
                    suggested_actions=[
                        "Check platform status page",
                        "Enable backup/failover systems",
                        "Notify stakeholders",
                        "Review incident response plan"
                    ]
                )
        
        return None
    
    async def _check_quota_exhaustion(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> Optional[Alert]:
        """Check for quota exhaustion alert"""
        quota_metrics = [m for m in metrics if m.metric_type == MetricType.QUOTA_USAGE]
        
        if quota_metrics:
            current_quota = quota_metrics[-1].value
            threshold = 90.0  # 90%
            
            if current_quota > threshold:
                return Alert(
                    alert_id=str(uuid.uuid4()),
                    platform_id=platform_id,
                    alert_type=MonitoringType.RATE_LIMITS,
                    severity=AlertSeverity.HIGH,
                    title="Quota Exhaustion Warning",
                    description=f"API quota usage is {current_quota:.1f}%, approaching limit",
                    threshold_breached={"metric": "quota_usage", "threshold": threshold},
                    current_value=current_quota,
                    expected_value=f"< {threshold}%",
                    suggested_actions=[
                        "Reduce API request frequency",
                        "Implement request batching",
                        "Review quota allocation",
                        "Consider upgrading API plan"
                    ]
                )
        
        return None
    
    async def _check_endpoint_down(
        self,
        platform_id: str,
        health_checks: List[HealthCheck],
        metrics: List[PerformanceMetric]
    ) -> Optional[Alert]:
        """Check for endpoint down alert"""
        unhealthy_checks = [
            check for check in health_checks
            if check.status == HealthStatus.UNHEALTHY
        ]
        
        if unhealthy_checks:
            endpoint_ids = [check.endpoint_id for check in unhealthy_checks]
            
            return Alert(
                alert_id=str(uuid.uuid4()),
                platform_id=platform_id,
                alert_type=MonitoringType.API_HEALTH,
                severity=AlertSeverity.CRITICAL,
                title="Endpoint(s) Down",
                description=f"The following endpoints are unhealthy: {', '.join(endpoint_ids)}",
                threshold_breached={"metric": "endpoint_health", "threshold": "healthy"},
                current_value="unhealthy",
                expected_value="healthy",
                suggested_actions=[
                    "Check platform status page",
                    "Verify authentication credentials",
                    "Review network connectivity",
                    "Implement failover procedures"
                ]
            )
        
        return None
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        try:
            for platform_alerts in self.active_alerts.values():
                for alert in platform_alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved_at = datetime.now()
                        platform_alerts.remove(alert)
                        logger.info(f"Alert resolved: {alert_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False


class PlatformMonitoringService:
    """
    📡 Platform Monitoring Microservice
    
    Monitors platform health, performance, and availability across multiple
    social media and content platforms, providing real-time alerts and insights.
    
    Features:
    - Real-time platform health monitoring
    - Performance metrics collection
    - Uptime tracking and SLA monitoring
    - Intelligent alerting system
    - Rate limit monitoring
    - API endpoint health checks
    - Historical performance analysis
    - Custom threshold configuration
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.health_checker = PlatformHealthChecker()
        self.performance_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()
        self.is_running = False
        
        # Service configuration
        self.check_interval = self.config.get("check_interval", 60)  # 1 minute
        self.supported_platforms = self.config.get("supported_platforms", [
            "youtube", "instagram", "tiktok", "twitter", "facebook",
            "linkedin", "spotify", "soundcloud"
        ])
        
        logger.info("Platform Monitoring Service initialized")
    
    async def start(self) -> None:
        """Start the monitoring service"""
        try:
            self.is_running = True
            logger.info("Platform Monitoring Service started")
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
        except Exception as e:
            logger.error(f"Failed to start Platform Monitoring Service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the monitoring service"""
        try:
            self.is_running = False
            logger.info("Platform Monitoring Service stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop Platform Monitoring Service: {e}")
            raise
    
    async def get_platform_status(self, platform_id: str) -> Dict[str, Any]:
        """Get comprehensive platform status"""
        try:
            # Get recent health checks
            health_checks = await self.health_checker.check_platform_health(platform_id)
            
            # Get performance metrics
            metrics = await self.performance_monitor.collect_metrics(platform_id)
            
            # Check for alerts
            alerts = await self.alert_manager.check_alerts(platform_id, health_checks, metrics)
            
            # Calculate overall status
            overall_status = self._determine_overall_status(health_checks)
            
            # Get uptime
            uptime = self.health_checker.get_platform_uptime(platform_id, 24)
            
            # Get metrics summary
            metrics_summary = self.performance_monitor.get_metrics_summary(platform_id, 24)
            
            # Get active alerts
            active_alerts = self.alert_manager.active_alerts.get(platform_id, [])
            
            platform_status = PlatformStatus(
                platform_id=platform_id,
                overall_status=overall_status,
                last_check=datetime.now(),
                uptime_percentage=uptime,
                average_response_time=self._calculate_avg_response_time(health_checks),
                error_rate=self._calculate_error_rate(health_checks),
                active_alerts=len(active_alerts),
                recent_incidents=self._get_recent_incidents(platform_id),
                service_levels=self._get_service_levels(health_checks),
                metrics_summary={
                    metric_type: summary.get("current", 0)
                    for metric_type, summary in metrics_summary.items()
                }
            )
            
            return {
                "platform_status": asdict(platform_status),
                "health_checks": [asdict(check) for check in health_checks],
                "performance_metrics": [asdict(metric) for metric in metrics],
                "active_alerts": [asdict(alert) for alert in active_alerts],
                "new_alerts": [asdict(alert) for alert in alerts],
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform status for {platform_id}: {e}")
            raise
    
    async def get_multi_platform_status(
        self,
        platform_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get status for multiple platforms"""
        try:
            platforms = platform_ids or self.supported_platforms
            platform_statuses = {}
            
            for platform_id in platforms:
                try:
                    status = await self.get_platform_status(platform_id)
                    platform_statuses[platform_id] = status
                except Exception as e:
                    platform_statuses[platform_id] = {
                        "error": str(e),
                        "status": "error"
                    }
            
            # Calculate aggregate metrics
            total_platforms = len(platforms)
            healthy_platforms = len([
                status for status in platform_statuses.values()
                if status.get("platform_status", {}).get("overall_status") == "healthy"
            ])
            
            total_alerts = sum([
                status.get("platform_status", {}).get("active_alerts", 0)
                for status in platform_statuses.values()
                if "error" not in status
            ])
            
            return {
                "multi_platform_status": platform_statuses,
                "summary": {
                    "total_platforms": total_platforms,
                    "healthy_platforms": healthy_platforms,
                    "unhealthy_platforms": total_platforms - healthy_platforms,
                    "total_active_alerts": total_alerts,
                    "overall_health_percentage": (healthy_platforms / total_platforms) * 100 if total_platforms > 0 else 0
                },
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get multi-platform status: {e}")
            raise
    
    async def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """Resolve a monitoring alert"""
        try:
            success = self.alert_manager.resolve_alert(alert_id)
            
            return {
                "alert_id": alert_id,
                "resolved": success,
                "resolved_at": datetime.now().isoformat() if success else None,
                "message": "Alert resolved successfully" if success else "Alert not found or already resolved"
            }
            
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            raise
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_running:
            try:
                for platform_id in self.supported_platforms:
                    try:
                        # Perform health checks and collect metrics
                        await self.get_platform_status(platform_id)
                    except Exception as e:
                        logger.error(f"Error monitoring {platform_id}: {e}")
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def _determine_overall_status(
        self,
        health_checks: List[HealthCheck]
    ) -> HealthStatus:
        """Determine overall platform status from health checks"""
        if not health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in health_checks]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN
    
    def _calculate_avg_response_time(
        self,
        health_checks: List[HealthCheck]
    ) -> float:
        """Calculate average response time from health checks"""
        if not health_checks:
            return 0.0
        
        response_times = [check.response_time_ms for check in health_checks]
        return statistics.mean(response_times)
    
    def _calculate_error_rate(
        self,
        health_checks: List[HealthCheck]
    ) -> float:
        """Calculate error rate from health checks"""
        if not health_checks:
            return 0.0
        
        error_checks = len([
            check for check in health_checks
            if check.status == HealthStatus.UNHEALTHY
        ])
        
        return (error_checks / len(health_checks)) * 100
    
    def _get_recent_incidents(self, platform_id: str) -> List[Dict[str, Any]]:
        """Get recent incidents for platform"""
        # Simulate recent incidents
        return [
            {
                "incident_id": "inc_001",
                "title": "Temporary API slowdown",
                "severity": "medium",
                "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "resolved_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "duration_minutes": 60
            }
        ]
    
    def _get_service_levels(
        self,
        health_checks: List[HealthCheck]
    ) -> Dict[str, HealthStatus]:
        """Get service level status breakdown"""
        service_levels = {}
        
        for check in health_checks:
            service_levels[check.endpoint_id] = check.status
        
        return service_levels
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            "service": "PlatformMonitoringService",
            "status": "healthy" if self.is_running else "stopped",
            "monitored_platforms": len(self.supported_platforms),
            "check_interval": self.check_interval,
            "active_alerts": sum(len(alerts) for alerts in self.alert_manager.active_alerts.values()),
            "timestamp": datetime.now().isoformat()
        }


# Service instance
platform_monitoring_service = PlatformMonitoringService()