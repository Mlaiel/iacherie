"""Multi-Platform Distribution SLA Monitoring System
Advanced SLA tracking for cross-platform synchronization, content distribution, and social media integration.

⚠️ PROPRIETARY CODE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, distribution, or modification is strictly prohibited.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import deque, defaultdict
import json
import time
from enum import Enum

class PlatformType(Enum):
    """Supported platforms for distribution SLA tracking"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    TWITCH = "twitch"
    DISCORD = "discord"
    WEBSITE = "website"
    BLOG = "blog"

class DistributionType(Enum):
    """Types of content distribution"""
    AUTOMATIC_SYNC = "automatic_sync"
    SCHEDULED_POST = "scheduled_post"
    MANUAL_UPLOAD = "manual_upload"
    CROSS_POST = "cross_post"
    LIVE_STREAM = "live_stream"
    STORY_SYNC = "story_sync"
    BULK_UPLOAD = "bulk_upload"

class SyncStatus(Enum):
    """Synchronization status tracking"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_SYNCED = "partially_synced"
    RATE_LIMITED = "rate_limited"
    RETRY_NEEDED = "retry_needed"

@dataclass
class DistributionMetric:
    """Multi-platform distribution metric with SLA targets"""
    metric_name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    platform_type: PlatformType = PlatformType.YOUTUBE
    distribution_type: DistributionType = DistributionType.AUTOMATIC_SYNC
    measurement_window: int = 300  # 5 minutes default
    last_measurement: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    success_rate: float = 100.0

@dataclass
class MultiPlatformDistributionSLATargets:
    """Comprehensive Multi-Platform Distribution SLA targets"""
    # Cross-Platform Sync SLA
    cross_platform_sync_minutes: float = 5.0  # <5min cross-platform sync
    sync_success_rate: float = 99.9  # 99.9% sync success rate
    sync_consistency_accuracy: float = 98.0  # 98% content consistency
    metadata_sync_accuracy: float = 99.5  # 99.5% metadata accuracy
    
    # Content Distribution SLA
    content_distribution_success: float = 99.9  # 99.9% distribution success
    distribution_latency_minutes: float = 10.0  # <10min distribution latency
    batch_processing_minutes: float = 30.0  # <30min batch processing
    priority_content_minutes: float = 2.0  # <2min priority content
    
    # Social Media API SLA
    api_response_time_seconds: float = 3.0  # <3s API response time
    api_rate_limit_compliance: float = 99.5  # 99.5% rate limit compliance
    api_error_recovery_minutes: float = 5.0  # <5min error recovery
    api_quota_management_accuracy: float = 95.0  # 95% quota management
    
    # Global CDN Performance SLA
    cdn_response_time_ms: float = 100.0  # <100ms CDN response
    cdn_cache_hit_ratio: float = 95.0  # >95% cache hit ratio
    global_edge_availability: float = 99.99  # 99.99% edge availability
    content_delivery_speed_mbps: float = 50.0  # >50 Mbps delivery speed
    
    # Platform Integration Health SLA
    platform_connectivity_uptime: float = 99.9  # 99.9% platform connectivity
    oauth_token_refresh_success: float = 99.8  # 99.8% token refresh success
    webhook_delivery_reliability: float = 99.5  # 99.5% webhook reliability
    integration_health_check_minutes: float = 15.0  # <15min health checks
    
    # Content Format Compatibility SLA
    format_conversion_success: float = 99.7  # 99.7% format conversion success
    platform_specific_optimization: float = 95.0  # 95% optimization success
    quality_preservation_percentage: float = 98.0  # 98% quality preservation
    aspect_ratio_adaptation_accuracy: float = 99.0  # 99% aspect ratio accuracy
    
    # Analytics Sync SLA
    analytics_sync_latency_minutes: float = 30.0  # <30min analytics sync
    metrics_aggregation_accuracy: float = 96.0  # 96% metrics accuracy
    cross_platform_attribution: float = 90.0  # 90% attribution accuracy

class MultiPlatformDistributionSLA:
    """
    Advanced Multi-Platform Distribution SLA monitoring system
    Tracks cross-platform sync, content distribution, and social media integration performance
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.targets = MultiPlatformDistributionSLATargets()
        self.metrics: Dict[str, DistributionMetric] = {}
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        
        # Distribution tracking
        self.sync_operations: Dict[str, Dict[str, Any]] = {}
        self.platform_health: Dict[str, Dict[str, Any]] = {}
        self.content_distribution: Dict[str, Dict[str, Any]] = {}
        self.api_performance: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.sync_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.success_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.platform_performance: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.cdn_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        self._setup_default_metrics()
        
    def _setup_default_metrics(self):
        """Initialize default multi-platform distribution metrics"""
        default_metrics = [
            ("cross_platform_sync", self.targets.cross_platform_sync_minutes, "minutes", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
            ("content_distribution", self.targets.content_distribution_success, "percentage", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
            ("social_api_performance", self.targets.api_response_time_seconds, "seconds", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
            ("cdn_performance", self.targets.cdn_response_time_ms, "milliseconds", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
            ("platform_integration", self.targets.platform_connectivity_uptime, "percentage", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
            ("format_compatibility", self.targets.format_conversion_success, "percentage", PlatformType.YOUTUBE, DistributionType.AUTOMATIC_SYNC),
        ]
        
        for metric_name, target, unit, platform, dist_type in default_metrics:
            self.metrics[metric_name] = DistributionMetric(
                metric_name=metric_name,
                target_value=target,
                unit=unit,
                platform_type=platform,
                distribution_type=dist_type
            )
    
    async def track_cross_platform_sync(self, sync_id: str, creator_id: str, content_id: str,
                                      source_platform: PlatformType, target_platforms: List[PlatformType],
                                      sync_start: datetime, sync_end: datetime,
                                      sync_status: SyncStatus, synced_platforms: List[PlatformType],
                                      metadata_accuracy: float) -> Dict[str, Any]:
        """Track cross-platform synchronization SLA compliance"""
        try:
            sync_duration = (sync_end - sync_start).total_seconds() / 60  # Convert to minutes
            success_rate = (len(synced_platforms) / len(target_platforms) * 100) if target_platforms else 100
            
            # Update metric
            metric = self.metrics["cross_platform_sync"]
            metric.current_value = sync_duration
            metric.last_measurement = sync_end
            metric.platform_type = source_platform
            metric.success_rate = success_rate
            
            # Check SLA compliance
            duration_compliant = sync_duration <= self.targets.cross_platform_sync_minutes
            success_compliant = success_rate >= self.targets.sync_success_rate
            metadata_compliant = metadata_accuracy >= self.targets.metadata_sync_accuracy
            
            if not duration_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Cross-Platform Sync Duration SLA Violation",
                    f"Sync {sync_id} took {sync_duration:.2f}min (target: {self.targets.cross_platform_sync_minutes}min)",
                    "medium",
                    {
                        "sync_id": sync_id,
                        "creator_id": creator_id,
                        "content_id": content_id,
                        "source_platform": source_platform.value,
                        "target_platforms": [p.value for p in target_platforms],
                        "duration_minutes": sync_duration,
                        "sync_status": sync_status.value
                    }
                )
            
            if not success_compliant:
                await self._generate_alert(
                    "Cross-Platform Sync Success Rate SLA Violation",
                    f"Sync {sync_id} success rate: {success_rate:.2f}% (target: {self.targets.sync_success_rate}%)",
                    "high",
                    {
                        "sync_id": sync_id,
                        "creator_id": creator_id,
                        "content_id": content_id,
                        "success_rate": success_rate,
                        "synced_platforms": [p.value for p in synced_platforms],
                        "failed_platforms": [p.value for p in target_platforms if p not in synced_platforms]
                    }
                )
            
            if not metadata_compliant:
                await self._generate_alert(
                    "Metadata Sync Accuracy SLA Violation",
                    f"Sync {sync_id} metadata accuracy: {metadata_accuracy:.2f}% (target: {self.targets.metadata_sync_accuracy}%)",
                    "medium",
                    {
                        "sync_id": sync_id,
                        "content_id": content_id,
                        "metadata_accuracy": metadata_accuracy
                    }
                )
            
            # Store measurements
            self.measurements["cross_platform_sync"].append({
                "timestamp": sync_end,
                "value": sync_duration,
                "sync_id": sync_id,
                "creator_id": creator_id,
                "content_id": content_id,
                "source_platform": source_platform.value,
                "target_platforms": [p.value for p in target_platforms],
                "synced_platforms": [p.value for p in synced_platforms],
                "sync_status": sync_status.value,
                "success_rate": success_rate,
                "metadata_accuracy": metadata_accuracy,
                "duration_compliant": duration_compliant,
                "success_compliant": success_compliant,
                "metadata_compliant": metadata_compliant
            })
            
            # Update sync tracking
            self.sync_operations[sync_id] = {
                "creator_id": creator_id,
                "content_id": content_id,
                "source_platform": source_platform,
                "target_platforms": target_platforms,
                "synced_platforms": synced_platforms,
                "sync_duration": sync_duration,
                "sync_status": sync_status,
                "success_rate": success_rate,
                "metadata_accuracy": metadata_accuracy,
                "timestamp": sync_end
            }
            
            # Update performance tracking
            self.sync_times[source_platform.value].append(sync_duration)
            self.success_rates["cross_platform_sync"].append(success_rate)
            
            self.logger.info(f"Cross-platform sync tracked - ID: {sync_id}, Duration: {sync_duration:.2f}min, Success: {success_rate:.2f}%")
            
            return {
                "sync_id": sync_id,
                "creator_id": creator_id,
                "content_id": content_id,
                "sync_duration_minutes": sync_duration,
                "success_rate": success_rate,
                "metadata_accuracy": metadata_accuracy,
                "synced_platforms": len(synced_platforms),
                "total_platforms": len(target_platforms),
                "duration_compliant": duration_compliant,
                "success_compliant": success_compliant,
                "metadata_compliant": metadata_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking cross-platform sync: {e}")
            raise
    
    async def track_content_distribution(self, distribution_id: str, creator_id: str, content_id: str,
                                       platforms: List[PlatformType], distribution_type: DistributionType,
                                       distribution_start: datetime, distribution_end: datetime,
                                       successful_uploads: int, failed_uploads: int,
                                       quality_preservation: float) -> Dict[str, Any]:
        """Track content distribution SLA compliance"""
        try:
            distribution_duration = (distribution_end - distribution_start).total_seconds() / 60  # Convert to minutes
            total_uploads = successful_uploads + failed_uploads
            success_rate = (successful_uploads / total_uploads * 100) if total_uploads > 0 else 100
            
            # Update metric
            metric = self.metrics["content_distribution"]
            metric.current_value = success_rate
            metric.last_measurement = distribution_end
            metric.distribution_type = distribution_type
            metric.success_rate = success_rate
            
            # Dynamic SLA based on distribution type
            if distribution_type == DistributionType.LIVE_STREAM:
                target_duration = self.targets.priority_content_minutes
            elif distribution_type == DistributionType.BULK_UPLOAD:
                target_duration = self.targets.batch_processing_minutes
            else:
                target_duration = self.targets.distribution_latency_minutes
            
            # Check SLA compliance
            duration_compliant = distribution_duration <= target_duration
            success_compliant = success_rate >= self.targets.content_distribution_success
            quality_compliant = quality_preservation >= self.targets.quality_preservation_percentage
            
            if not duration_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Content Distribution Duration SLA Violation",
                    f"Distribution {distribution_id} took {distribution_duration:.2f}min (target: {target_duration:.2f}min)",
                    "medium",
                    {
                        "distribution_id": distribution_id,
                        "creator_id": creator_id,
                        "content_id": content_id,
                        "platforms": [p.value for p in platforms],
                        "distribution_type": distribution_type.value,
                        "duration_minutes": distribution_duration,
                        "target_duration": target_duration
                    }
                )
            
            if not success_compliant:
                await self._generate_alert(
                    "Content Distribution Success Rate SLA Violation",
                    f"Distribution {distribution_id} success rate: {success_rate:.2f}% (target: {self.targets.content_distribution_success}%)",
                    "high",
                    {
                        "distribution_id": distribution_id,
                        "creator_id": creator_id,
                        "content_id": content_id,
                        "success_rate": success_rate,
                        "successful_uploads": successful_uploads,
                        "failed_uploads": failed_uploads,
                        "platforms": [p.value for p in platforms]
                    }
                )
            
            if not quality_compliant:
                await self._generate_alert(
                    "Content Quality Preservation SLA Violation",
                    f"Distribution {distribution_id} quality preservation: {quality_preservation:.2f}% (target: {self.targets.quality_preservation_percentage}%)",
                    "medium",
                    {
                        "distribution_id": distribution_id,
                        "content_id": content_id,
                        "quality_preservation": quality_preservation
                    }
                )
            
            # Store measurements
            self.measurements["content_distribution"].append({
                "timestamp": distribution_end,
                "value": success_rate,
                "distribution_id": distribution_id,
                "creator_id": creator_id,
                "content_id": content_id,
                "platforms": [p.value for p in platforms],
                "distribution_type": distribution_type.value,
                "distribution_duration": distribution_duration,
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "quality_preservation": quality_preservation,
                "duration_compliant": duration_compliant,
                "success_compliant": success_compliant,
                "quality_compliant": quality_compliant,
                "target_duration": target_duration
            })
            
            # Update distribution tracking
            self.content_distribution[distribution_id] = {
                "creator_id": creator_id,
                "content_id": content_id,
                "platforms": platforms,
                "distribution_type": distribution_type,
                "distribution_duration": distribution_duration,
                "success_rate": success_rate,
                "quality_preservation": quality_preservation,
                "timestamp": distribution_end
            }
            
            self.logger.info(f"Content distribution tracked - ID: {distribution_id}, Success: {success_rate:.2f}%, Duration: {distribution_duration:.2f}min")
            
            return {
                "distribution_id": distribution_id,
                "creator_id": creator_id,
                "content_id": content_id,
                "distribution_duration_minutes": distribution_duration,
                "success_rate": success_rate,
                "quality_preservation": quality_preservation,
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "platforms_count": len(platforms),
                "duration_compliant": duration_compliant,
                "success_compliant": success_compliant,
                "quality_compliant": quality_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking content distribution: {e}")
            raise
    
    async def track_social_api_performance(self, api_call_id: str, platform: PlatformType,
                                         api_endpoint: str, call_start: datetime,
                                         call_end: datetime, status_code: int,
                                         rate_limited: bool, quota_usage: float,
                                         error_recovery_time: Optional[float] = None) -> Dict[str, Any]:
        """Track social media API performance SLA compliance"""
        try:
            response_time = (call_end - call_start).total_seconds()
            is_success = 200 <= status_code < 300
            
            # Update metric
            metric = self.metrics["social_api_performance"]
            metric.current_value = response_time
            metric.last_measurement = call_end
            metric.platform_type = platform
            metric.success_rate = 100.0 if is_success else 0.0
            
            # Check SLA compliance
            response_compliant = response_time <= self.targets.api_response_time_seconds
            rate_limit_compliant = not rate_limited
            quota_compliant = quota_usage <= 95.0  # Don't exceed 95% of quota
            
            if error_recovery_time:
                recovery_compliant = error_recovery_time <= self.targets.api_error_recovery_minutes
            else:
                recovery_compliant = True
            
            if not response_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Social API Response Time SLA Violation",
                    f"API call {api_call_id} to {platform.value} took {response_time:.2f}s (target: {self.targets.api_response_time_seconds}s)",
                    "medium",
                    {
                        "api_call_id": api_call_id,
                        "platform": platform.value,
                        "api_endpoint": api_endpoint,
                        "response_time": response_time,
                        "status_code": status_code
                    }
                )
            
            if not rate_limit_compliant:
                await self._generate_alert(
                    "Social API Rate Limit Violation",
                    f"API call {api_call_id} to {platform.value} was rate limited",
                    "high",
                    {
                        "api_call_id": api_call_id,
                        "platform": platform.value,
                        "api_endpoint": api_endpoint,
                        "quota_usage": quota_usage
                    }
                )
            
            if not quota_compliant:
                await self._generate_alert(
                    "Social API Quota Usage Warning",
                    f"Platform {platform.value} quota usage: {quota_usage:.2f}% (warning threshold: 95%)",
                    "medium",
                    {
                        "platform": platform.value,
                        "quota_usage": quota_usage,
                        "api_endpoint": api_endpoint
                    }
                )
            
            # Store measurements
            self.measurements["social_api_performance"].append({
                "timestamp": call_end,
                "value": response_time,
                "api_call_id": api_call_id,
                "platform": platform.value,
                "api_endpoint": api_endpoint,
                "status_code": status_code,
                "is_success": is_success,
                "rate_limited": rate_limited,
                "quota_usage": quota_usage,
                "error_recovery_time": error_recovery_time,
                "response_compliant": response_compliant,
                "rate_limit_compliant": rate_limit_compliant,
                "quota_compliant": quota_compliant,
                "recovery_compliant": recovery_compliant
            })
            
            # Update API performance tracking
            platform_key = f"{platform.value}:{api_endpoint}"
            if platform_key not in self.api_performance:
                self.api_performance[platform_key] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "rate_limited_calls": 0,
                    "avg_response_time": 0.0,
                    "quota_usage": quota_usage,
                    "last_updated": call_end
                }
            
            perf = self.api_performance[platform_key]
            perf["total_calls"] += 1
            if is_success:
                perf["successful_calls"] += 1
            if rate_limited:
                perf["rate_limited_calls"] += 1
            perf["avg_response_time"] = (perf["avg_response_time"] * (perf["total_calls"] - 1) + response_time) / perf["total_calls"]
            perf["quota_usage"] = quota_usage
            perf["last_updated"] = call_end
            
            self.platform_performance[platform.value].append(response_time)
            
            self.logger.info(f"Social API call tracked - Platform: {platform.value}, Endpoint: {api_endpoint}, Time: {response_time:.2f}s")
            
            return {
                "api_call_id": api_call_id,
                "platform": platform.value,
                "api_endpoint": api_endpoint,
                "response_time": response_time,
                "status_code": status_code,
                "is_success": is_success,
                "rate_limited": rate_limited,
                "quota_usage": quota_usage,
                "response_compliant": response_compliant,
                "rate_limit_compliant": rate_limit_compliant,
                "quota_compliant": quota_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking social API performance: {e}")
            raise
    
    async def track_platform_health(self, health_check_id: str, platform: PlatformType,
                                  check_start: datetime, check_end: datetime,
                                  connectivity_status: bool, oauth_refresh_success: bool,
                                  webhook_reliability: float, integration_errors: int) -> Dict[str, Any]:
        """Track platform integration health SLA compliance"""
        try:
            check_duration = (check_end - check_start).total_seconds() / 60  # Convert to minutes
            overall_health = (
                (100 if connectivity_status else 0) +
                (100 if oauth_refresh_success else 0) +
                webhook_reliability
            ) / 3
            
            # Update metric
            metric = self.metrics["platform_integration"]
            metric.current_value = overall_health
            metric.last_measurement = check_end
            metric.platform_type = platform
            metric.success_rate = overall_health
            
            # Check SLA compliance
            health_compliant = overall_health >= self.targets.platform_connectivity_uptime
            check_duration_compliant = check_duration <= self.targets.integration_health_check_minutes
            oauth_compliant = oauth_refresh_success
            webhook_compliant = webhook_reliability >= self.targets.webhook_delivery_reliability
            
            if not health_compliant:
                metric.violation_count += 1
                await self._generate_alert(
                    "Platform Integration Health SLA Violation",
                    f"Platform {platform.value} health: {overall_health:.2f}% (target: {self.targets.platform_connectivity_uptime}%)",
                    "high",
                    {
                        "health_check_id": health_check_id,
                        "platform": platform.value,
                        "overall_health": overall_health,
                        "connectivity_status": connectivity_status,
                        "oauth_refresh_success": oauth_refresh_success,
                        "webhook_reliability": webhook_reliability,
                        "integration_errors": integration_errors
                    }
                )
            
            if not oauth_compliant:
                await self._generate_alert(
                    "OAuth Token Refresh Failure",
                    f"Platform {platform.value} OAuth token refresh failed",
                    "critical",
                    {
                        "health_check_id": health_check_id,
                        "platform": platform.value
                    }
                )
            
            if not webhook_compliant:
                await self._generate_alert(
                    "Webhook Reliability SLA Violation",
                    f"Platform {platform.value} webhook reliability: {webhook_reliability:.2f}% (target: {self.targets.webhook_delivery_reliability}%)",
                    "medium",
                    {
                        "health_check_id": health_check_id,
                        "platform": platform.value,
                        "webhook_reliability": webhook_reliability
                    }
                )
            
            # Store measurements
            self.measurements["platform_integration"].append({
                "timestamp": check_end,
                "value": overall_health,
                "health_check_id": health_check_id,
                "platform": platform.value,
                "connectivity_status": connectivity_status,
                "oauth_refresh_success": oauth_refresh_success,
                "webhook_reliability": webhook_reliability,
                "integration_errors": integration_errors,
                "check_duration": check_duration,
                "health_compliant": health_compliant,
                "check_duration_compliant": check_duration_compliant,
                "oauth_compliant": oauth_compliant,
                "webhook_compliant": webhook_compliant
            })
            
            # Update platform health tracking
            self.platform_health[platform.value] = {
                "overall_health": overall_health,
                "connectivity_status": connectivity_status,
                "oauth_refresh_success": oauth_refresh_success,
                "webhook_reliability": webhook_reliability,
                "integration_errors": integration_errors,
                "last_checked": check_end
            }
            
            self.logger.info(f"Platform health tracked - Platform: {platform.value}, Health: {overall_health:.2f}%")
            
            return {
                "health_check_id": health_check_id,
                "platform": platform.value,
                "overall_health": overall_health,
                "connectivity_status": connectivity_status,
                "oauth_refresh_success": oauth_refresh_success,
                "webhook_reliability": webhook_reliability,
                "integration_errors": integration_errors,
                "check_duration_minutes": check_duration,
                "health_compliant": health_compliant,
                "oauth_compliant": oauth_compliant,
                "webhook_compliant": webhook_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking platform health: {e}")
            raise
    
    async def get_distribution_sla_summary(self, time_window_hours: int = 24,
                                         platform: Optional[PlatformType] = None,
                                         creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive multi-platform distribution SLA summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            summary = {
                "time_window_hours": time_window_hours,
                "cutoff_time": cutoff_time.isoformat(),
                "overall_compliance": {},
                "metric_summaries": {},
                "platform_analytics": {},
                "sync_analytics": {},
                "distribution_analytics": {},
                "api_analytics": {},
                "health_analytics": {},
                "recommendations": []
            }
            
            # Calculate overall compliance for each metric
            for metric_name, metric in self.metrics.items():
                measurements = [
                    m for m in self.measurements[metric_name]
                    if m["timestamp"] >= cutoff_time
                ]
                
                # Apply filters
                if platform:
                    measurements = [m for m in measurements if m.get("platform") == platform.value or m.get("source_platform") == platform.value]
                if creator_id:
                    measurements = [m for m in measurements if m.get("creator_id") == creator_id]
                
                if measurements:
                    if "compliant" in measurements[0]:
                        # For metrics with compliance tracking
                        compliant_fields = [k for k in measurements[0].keys() if k.endswith("_compliant")]
                        if compliant_fields:
                            compliance_rates = []
                            for field in compliant_fields:
                                field_compliance = (sum(1 for m in measurements if m.get(field, True)) / len(measurements)) * 100
                                compliance_rates.append(field_compliance)
                            compliance_rate = min(compliance_rates)  # Take the worst compliance rate
                        else:
                            compliance_rate = 100.0
                    else:
                        # For percentage-based metrics
                        compliance_rate = statistics.mean([m["value"] for m in measurements])
                    
                    avg_value = statistics.mean([m["value"] for m in measurements])
                    p95_value = statistics.quantiles([m["value"] for m in measurements], n=20)[18] if len(measurements) >= 20 else max([m["value"] for m in measurements])
                    
                    summary["metric_summaries"][metric_name] = {
                        "compliance_rate": compliance_rate,
                        "measurement_count": len(measurements),
                        "avg_value": avg_value,
                        "p95_value": p95_value,
                        "target_value": metric.target_value,
                        "unit": metric.unit,
                        "violation_count": metric.violation_count
                    }
                    
                    summary["overall_compliance"][metric_name] = compliance_rate >= 95.0
            
            # Platform analytics
            for platform_type in PlatformType:
                platform_data = {
                    "sync_operations": len([
                        op for op in self.sync_operations.values()
                        if (op["source_platform"] == platform_type or platform_type in op["target_platforms"]) and op["timestamp"] >= cutoff_time
                    ]),
                    "api_calls": len([
                        call for call in self.measurements["social_api_performance"]
                        if call["timestamp"] >= cutoff_time and call.get("platform") == platform_type.value
                    ]),
                    "health_status": self.platform_health.get(platform_type.value, {}).get("overall_health", 100.0)
                }
                
                if platform_data["sync_operations"] > 0 or platform_data["api_calls"] > 0:
                    summary["platform_analytics"][platform_type.value] = platform_data
            
            # Sync analytics
            recent_syncs = [
                sync for sync in self.sync_operations.values()
                if sync["timestamp"] >= cutoff_time
            ]
            
            if recent_syncs:
                summary["sync_analytics"] = {
                    "total_sync_operations": len(recent_syncs),
                    "successful_syncs": len([s for s in recent_syncs if s["sync_status"] == SyncStatus.COMPLETED]),
                    "avg_sync_duration": statistics.mean([s["sync_duration"] for s in recent_syncs]),
                    "avg_success_rate": statistics.mean([s["success_rate"] for s in recent_syncs]),
                    "avg_metadata_accuracy": statistics.mean([s["metadata_accuracy"] for s in recent_syncs])
                }
            
            # Distribution analytics
            recent_distributions = [
                dist for dist in self.content_distribution.values()
                if dist["timestamp"] >= cutoff_time
            ]
            
            if recent_distributions:
                summary["distribution_analytics"] = {
                    "total_distributions": len(recent_distributions),
                    "avg_success_rate": statistics.mean([d["success_rate"] for d in recent_distributions]),
                    "avg_distribution_duration": statistics.mean([d["distribution_duration"] for d in recent_distributions]),
                    "avg_quality_preservation": statistics.mean([d["quality_preservation"] for d in recent_distributions])
                }
            
            # API analytics
            if self.api_performance:
                summary["api_analytics"] = {
                    "total_api_endpoints": len(self.api_performance),
                    "avg_response_time": statistics.mean([
                        perf["avg_response_time"] for perf in self.api_performance.values()
                    ]),
                    "total_api_calls": sum([
                        perf["total_calls"] for perf in self.api_performance.values()
                    ]),
                    "overall_success_rate": (sum([
                        perf["successful_calls"] for perf in self.api_performance.values()
                    ]) / sum([
                        perf["total_calls"] for perf in self.api_performance.values()
                    ]) * 100) if sum([perf["total_calls"] for perf in self.api_performance.values()]) > 0 else 100
                }
            
            # Health analytics
            if self.platform_health:
                summary["health_analytics"] = {
                    "platforms_monitored": len(self.platform_health),
                    "avg_platform_health": statistics.mean([
                        health["overall_health"] for health in self.platform_health.values()
                    ]),
                    "platforms_fully_operational": len([
                        health for health in self.platform_health.values()
                        if health["overall_health"] >= 95.0
                    ]),
                    "oauth_success_rate": statistics.mean([
                        100.0 if health["oauth_refresh_success"] else 0.0
                        for health in self.platform_health.values()
                    ])
                }
            
            # Generate recommendations
            for metric_name, compliance in summary["overall_compliance"].items():
                if not compliance:
                    if metric_name == "cross_platform_sync":
                        summary["recommendations"].append("Optimize sync algorithms and implement parallel processing for multiple platforms")
                    elif metric_name == "content_distribution":
                        summary["recommendations"].append("Enhance distribution pipeline and implement retry mechanisms for failed uploads")
                    elif metric_name == "social_api_performance":
                        summary["recommendations"].append("Implement API request optimization and intelligent rate limiting")
                    elif metric_name == "platform_integration":
                        summary["recommendations"].append("Improve platform connectivity monitoring and implement automated failover")
                    elif metric_name == "format_compatibility":
                        summary["recommendations"].append("Enhance format conversion algorithms and quality preservation techniques")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating distribution SLA summary: {e}")
            raise
    
    async def _generate_alert(self, title: str, message: str, severity: str, metadata: Dict[str, Any]):
        """Generate SLA violation alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "component": "multi_platform_distribution_sla",
            "metadata": metadata
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Distribution SLA Alert - {title}: {message}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    async def get_real_time_distribution_metrics(self) -> Dict[str, Any]:
        """Get real-time distribution metrics for monitoring dashboards"""
        try:
            current_time = datetime.now()
            
            metrics_data = {}
            for metric_name, metric in self.metrics.items():
                # Get recent measurements (last 5 minutes)
                recent_measurements = [
                    m for m in self.measurements[metric_name]
                    if (current_time - m["timestamp"]).total_seconds() <= 300
                ]
                
                if recent_measurements:
                    current_avg = statistics.mean([m["value"] for m in recent_measurements])
                    if "compliant" in recent_measurements[0]:
                        compliant_fields = [k for k in recent_measurements[0].keys() if k.endswith("_compliant")]
                        if compliant_fields:
                            compliance_rates = []
                            for field in compliant_fields:
                                field_compliance = (sum(1 for m in recent_measurements if m.get(field, True)) / len(recent_measurements)) * 100
                                compliance_rates.append(field_compliance)
                            compliance_rate = min(compliance_rates)
                        else:
                            compliance_rate = 100.0
                    else:
                        compliance_rate = current_avg
                else:
                    current_avg = metric.current_value
                    compliance_rate = 100.0 if metric.current_value >= metric.target_value else 0.0
                
                metrics_data[metric_name] = {
                    "current_value": current_avg,
                    "target_value": metric.target_value,
                    "compliance_rate": compliance_rate,
                    "unit": metric.unit,
                    "status": "compliant" if compliance_rate >= 95.0 else "violation",
                    "last_updated": metric.last_measurement.isoformat(),
                    "recent_measurements_count": len(recent_measurements),
                    "success_rate": metric.success_rate
                }
            
            # Calculate distribution health
            active_syncs = len([
                sync for sync in self.sync_operations.values()
                if (current_time - sync["timestamp"]).total_seconds() <= 3600  # Last hour
            ])
            
            active_distributions = len([
                dist for dist in self.content_distribution.values()
                if (current_time - dist["timestamp"]).total_seconds() <= 3600  # Last hour
            ])
            
            distribution_health = {
                "active_sync_operations": active_syncs,
                "active_distributions": active_distributions,
                "platforms_healthy": len([
                    health for health in self.platform_health.values()
                    if health["overall_health"] >= 95.0
                ]),
                "total_platforms_monitored": len(self.platform_health),
                "api_calls_last_hour": len([
                    call for perf in self.api_performance.values()
                    if (current_time - perf["last_updated"]).total_seconds() <= 3600
                ])
            }
            
            return {
                "timestamp": current_time.isoformat(),
                "metrics": metrics_data,
                "distribution_health": distribution_health,
                "overall_status": "healthy" if all(m["compliance_rate"] >= 95.0 for m in metrics_data.values()) else "degraded",
                "active_alerts_count": len([a for a in self.alerts if (current_time - datetime.fromisoformat(a["timestamp"])).total_seconds() <= 3600])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time distribution metrics: {e}")
            raise

# Global instance for easy access
multi_platform_distribution_sla = MultiPlatformDistributionSLA()