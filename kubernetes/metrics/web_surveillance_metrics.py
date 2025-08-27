"""
IA Influencer Agent - Web Surveillance Metrics Collector
Enterprise metrics for web crawling and content surveillance operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
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
- Web crawler performance monitoring
- Content surveillance metrics
- Platform-specific crawling analytics
- Detection accuracy tracking
- Anti-piracy effectiveness metrics
- Real-time threat detection
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


class CrawlerPlatform(Enum):
    """Supported crawler platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    GENERIC_WEB = "generic_web"


class SurveillanceStatus(Enum):
    """Surveillance operation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    RATE_LIMITED = "rate_limited"


class ThreatLevel(Enum):
    """Content threat level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CrawlerSession:
    """Crawler session information"""
    session_id: str
    platform: CrawlerPlatform
    start_time: datetime
    user_id: str
    content_types: List[str]
    search_terms: List[str]
    status: SurveillanceStatus


@dataclass
class ContentMatch:
    """Detected content match information"""
    match_id: str
    original_content_id: str
    detected_url: str
    platform: CrawlerPlatform
    similarity_score: float
    threat_level: ThreatLevel
    detection_timestamp: datetime
    evidence_captured: bool


class WebSurveillanceMetricsCollector:
    """
    Comprehensive metrics collector for web surveillance and crawler operations
    
    Tracks:
    - Crawler performance and reliability
    - Content detection accuracy
    - Platform-specific metrics
    - Threat detection effectiveness
    - Anti-piracy operation success rates
    """
    
    def __init__(self, prometheus_manager=None):
        self.prometheus_manager = prometheus_manager
        self.redis_manager = RedisManager()
        self.logger = logger
        self._active_sessions: Dict[str, CrawlerSession] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics for web surveillance"""
        
        if not self.prometheus_manager:
            self.logger.warning("No Prometheus manager provided, metrics disabled")
            return
        
        # Crawler Performance Metrics
        self.crawler_sessions_total = Counter(
            'ia_influencer_crawler_sessions_total',
            'Total crawler sessions by platform and status',
            ['platform', 'status', 'user_id', 'tenant_id']
        )
        
        self.crawler_requests_total = Counter(
            'ia_influencer_crawler_requests_total',
            'Total crawler HTTP requests by platform and response code',
            ['platform', 'response_code', 'endpoint_type']
        )
        
        self.crawler_session_duration = Histogram(
            'ia_influencer_crawler_session_duration_seconds',
            'Duration of crawler sessions in seconds',
            ['platform', 'status'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200]
        )
        
        self.crawler_pages_scraped_total = Counter(
            'ia_influencer_crawler_pages_scraped_total',
            'Total pages scraped by platform',
            ['platform', 'content_type', 'success']
        )
        
        # Content Detection Metrics
        self.content_matches_detected_total = Counter(
            'ia_influencer_content_matches_detected_total',
            'Total content matches detected by platform and threat level',
            ['platform', 'threat_level', 'content_type', 'user_id']
        )
        
        self.content_similarity_score = Histogram(
            'ia_influencer_content_similarity_score',
            'Distribution of content similarity scores',
            ['platform', 'content_type'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
        )
        
        self.content_detection_latency = Histogram(
            'ia_influencer_content_detection_latency_seconds',
            'Time taken to detect content matches',
            ['platform', 'detection_algorithm'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120]
        )
        
        # Platform-Specific Metrics
        self.platform_api_calls_total = Counter(
            'ia_influencer_platform_api_calls_total',
            'Total API calls to platforms',
            ['platform', 'api_endpoint', 'response_code']
        )
        
        self.platform_rate_limits_hit_total = Counter(
            'ia_influencer_platform_rate_limits_hit_total',
            'Total rate limits encountered by platform',
            ['platform', 'limit_type']
        )
        
        self.platform_api_quota_usage = Gauge(
            'ia_influencer_platform_api_quota_usage_percent',
            'API quota usage percentage by platform',
            ['platform', 'quota_type']
        )
        
        # Surveillance Effectiveness Metrics
        self.threat_detection_accuracy = Gauge(
            'ia_influencer_threat_detection_accuracy_percent',
            'Threat detection accuracy percentage',
            ['platform', 'threat_level', 'time_window']
        )
        
        self.false_positive_rate = Gauge(
            'ia_influencer_false_positive_rate_percent',
            'False positive rate in content detection',
            ['platform', 'content_type', 'time_window']
        )
        
        self.surveillance_coverage = Gauge(
            'ia_influencer_surveillance_coverage_percent',
            'Coverage percentage of surveillance operations',
            ['platform', 'region', 'content_type']
        )
        
        # Anti-Piracy Metrics
        self.takedown_requests_sent_total = Counter(
            'ia_influencer_takedown_requests_sent_total',
            'Total takedown requests sent',
            ['platform', 'request_type', 'status']
        )
        
        self.takedown_success_rate = Gauge(
            'ia_influencer_takedown_success_rate_percent',
            'Success rate of takedown requests',
            ['platform', 'request_type', 'time_window']
        )
        
        self.takedown_response_time = Histogram(
            'ia_influencer_takedown_response_time_hours',
            'Response time for takedown requests',
            ['platform', 'priority'],
            buckets=[1, 6, 12, 24, 48, 72, 168, 336, 720]  # hours
        )
        
        # Real-time Monitoring Metrics
        self.active_crawlers_count = Gauge(
            'ia_influencer_active_crawlers_count',
            'Number of currently active crawlers',
            ['platform', 'region']
        )
        
        self.crawler_health_score = Gauge(
            'ia_influencer_crawler_health_score',
            'Health score of crawler instances (0-100)',
            ['platform', 'instance_id']
        )
        
        self.surveillance_alerts_triggered_total = Counter(
            'ia_influencer_surveillance_alerts_triggered_total',
            'Total surveillance alerts triggered',
            ['alert_type', 'severity', 'platform']
        )
        
        # Register metrics with Prometheus
        self._register_metrics()
        
        self.logger.info("Web surveillance metrics initialized")
    
    def _register_metrics(self) -> None:
        """Register all metrics with Prometheus manager"""
        
        metrics_to_register = [
            self.crawler_sessions_total,
            self.crawler_requests_total,
            self.crawler_session_duration,
            self.crawler_pages_scraped_total,
            self.content_matches_detected_total,
            self.content_similarity_score,
            self.content_detection_latency,
            self.platform_api_calls_total,
            self.platform_rate_limits_hit_total,
            self.platform_api_quota_usage,
            self.threat_detection_accuracy,
            self.false_positive_rate,
            self.surveillance_coverage,
            self.takedown_requests_sent_total,
            self.takedown_success_rate,
            self.takedown_response_time,
            self.active_crawlers_count,
            self.crawler_health_score,
            self.surveillance_alerts_triggered_total
        ]
        
        for metric in metrics_to_register:
            self.prometheus_manager.register_metric(metric)
    
    async def start_crawler_session(
        self,
        session_id: str,
        platform: CrawlerPlatform,
        user_id: str,
        content_types: List[str],
        search_terms: List[str],
        tenant_id: str = "default"
    ) -> None:
        """Record start of crawler session"""
        
        session = CrawlerSession(
            session_id=session_id,
            platform=platform,
            start_time=datetime.utcnow(),
            user_id=user_id,
            content_types=content_types,
            search_terms=search_terms,
            status=SurveillanceStatus.ACTIVE
        )
        
        self._active_sessions[session_id] = session
        
        # Update metrics
        self.crawler_sessions_total.labels(
            platform=platform.value,
            status=SurveillanceStatus.ACTIVE.value,
            user_id=user_id,
            tenant_id=tenant_id
        ).inc()
        
        self.active_crawlers_count.labels(
            platform=platform.value,
            region="global"  # Could be parameterized
        ).inc()
        
        # Store session in Redis for persistence
        await self.redis_manager.set(
            f"crawler_session:{session_id}",
            session.__dict__,
            ttl=86400  # 24 hours
        )
        
        self.logger.info(f"Started crawler session {session_id} for platform {platform.value}")
    
    async def end_crawler_session(
        self,
        session_id: str,
        status: SurveillanceStatus,
        pages_scraped: int = 0,
        matches_found: int = 0,
        tenant_id: str = "default"
    ) -> None:
        """Record end of crawler session"""
        
        if session_id not in self._active_sessions:
            self.logger.warning(f"Session {session_id} not found in active sessions")
            return
        
        session = self._active_sessions[session_id]
        end_time = datetime.utcnow()
        duration = (end_time - session.start_time).total_seconds()
        
        # Update session status
        session.status = status
        
        # Update metrics
        self.crawler_sessions_total.labels(
            platform=session.platform.value,
            status=status.value,
            user_id=session.user_id,
            tenant_id=tenant_id
        ).inc()
        
        self.crawler_session_duration.labels(
            platform=session.platform.value,
            status=status.value
        ).observe(duration)
        
        self.active_crawlers_count.labels(
            platform=session.platform.value,
            region="global"
        ).dec()
        
        # Clean up session
        del self._active_sessions[session_id]
        await self.redis_manager.delete(f"crawler_session:{session_id}")
        
        self.logger.info(
            f"Ended crawler session {session_id} with status {status.value}, "
            f"duration: {duration:.2f}s, pages: {pages_scraped}, matches: {matches_found}"
        )
    
    async def record_crawler_request(
        self,
        platform: CrawlerPlatform,
        response_code: int,
        endpoint_type: str = "api",
        response_time: float = None
    ) -> None:
        """Record individual crawler HTTP request"""
        
        self.crawler_requests_total.labels(
            platform=platform.value,
            response_code=str(response_code),
            endpoint_type=endpoint_type
        ).inc()
        
        # Track API-specific metrics
        if endpoint_type == "api":
            self.platform_api_calls_total.labels(
                platform=platform.value,
                api_endpoint=endpoint_type,
                response_code=str(response_code)
            ).inc()
        
        # Handle rate limiting
        if response_code == 429:  # Too Many Requests
            self.platform_rate_limits_hit_total.labels(
                platform=platform.value,
                limit_type="rate_limit"
            ).inc()
    
    async def record_content_match(
        self,
        match: ContentMatch,
        detection_algorithm: str,
        processing_time: float,
        tenant_id: str = "default"
    ) -> None:
        """Record detected content match"""
        
        # Update detection metrics
        self.content_matches_detected_total.labels(
            platform=match.platform.value,
            threat_level=match.threat_level.value,
            content_type="unknown",  # Could be extracted from match
            user_id="unknown"  # Could be extracted from match
        ).inc()
        
        self.content_similarity_score.labels(
            platform=match.platform.value,
            content_type="unknown"
        ).observe(match.similarity_score)
        
        self.content_detection_latency.labels(
            platform=match.platform.value,
            detection_algorithm=detection_algorithm
        ).observe(processing_time)
        
        # Trigger alert for high-threat matches
        if match.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            await self._trigger_surveillance_alert(
                alert_type="high_threat_content",
                severity=match.threat_level.value,
                platform=match.platform,
                details={
                    "match_id": match.match_id,
                    "similarity_score": match.similarity_score,
                    "detected_url": match.detected_url
                }
            )
        
        # Store match details in Redis for further processing
        await self.redis_manager.set(
            f"content_match:{match.match_id}",
            match.__dict__,
            ttl=2592000  # 30 days
        )
        
        self.logger.info(
            f"Recorded content match {match.match_id} with similarity {match.similarity_score:.3f}"
        )
    
    async def record_takedown_request(
        self,
        platform: CrawlerPlatform,
        request_type: str,
        status: str,
        response_time_hours: Optional[float] = None,
        priority: str = "normal"
    ) -> None:
        """Record takedown request and response"""
        
        self.takedown_requests_sent_total.labels(
            platform=platform.value,
            request_type=request_type,
            status=status
        ).inc()
        
        if response_time_hours is not None:
            self.takedown_response_time.labels(
                platform=platform.value,
                priority=priority
            ).observe(response_time_hours)
        
        self.logger.info(
            f"Recorded takedown request for {platform.value}: {request_type} - {status}"
        )
    
    async def update_api_quota_usage(
        self,
        platform: CrawlerPlatform,
        quota_type: str,
        usage_percent: float
    ) -> None:
        """Update API quota usage metrics"""
        
        self.platform_api_quota_usage.labels(
            platform=platform.value,
            quota_type=quota_type
        ).set(usage_percent)
        
        # Alert if quota usage is high
        if usage_percent > 90:
            await self._trigger_surveillance_alert(
                alert_type="api_quota_high",
                severity="warning",
                platform=platform,
                details={"quota_type": quota_type, "usage_percent": usage_percent}
            )
    
    async def update_detection_accuracy(
        self,
        platform: CrawlerPlatform,
        threat_level: ThreatLevel,
        accuracy_percent: float,
        time_window: str = "1h"
    ) -> None:
        """Update threat detection accuracy metrics"""
        
        self.threat_detection_accuracy.labels(
            platform=platform.value,
            threat_level=threat_level.value,
            time_window=time_window
        ).set(accuracy_percent)
    
    async def update_false_positive_rate(
        self,
        platform: CrawlerPlatform,
        content_type: str,
        false_positive_rate: float,
        time_window: str = "1h"
    ) -> None:
        """Update false positive rate metrics"""
        
        self.false_positive_rate.labels(
            platform=platform.value,
            content_type=content_type,
            time_window=time_window
        ).set(false_positive_rate)
    
    async def update_crawler_health(
        self,
        platform: CrawlerPlatform,
        instance_id: str,
        health_score: float
    ) -> None:
        """Update crawler instance health score"""
        
        self.crawler_health_score.labels(
            platform=platform.value,
            instance_id=instance_id
        ).set(health_score)
        
        # Alert if health score is low
        if health_score < 50:
            await self._trigger_surveillance_alert(
                alert_type="crawler_unhealthy",
                severity="critical",
                platform=platform,
                details={"instance_id": instance_id, "health_score": health_score}
            )
    
    async def _trigger_surveillance_alert(
        self,
        alert_type: str,
        severity: str,
        platform: CrawlerPlatform,
        details: Dict[str, Any]
    ) -> None:
        """Trigger surveillance alert"""
        
        self.surveillance_alerts_triggered_total.labels(
            alert_type=alert_type,
            severity=severity,
            platform=platform.value
        ).inc()
        
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "platform": platform.value,
            "details": details
        }
        
        # Store alert in Redis for processing
        await self.redis_manager.lpush(
            "surveillance_alerts",
            alert_data
        )
        
        self.logger.warning(f"Surveillance alert triggered: {alert_type} - {severity}")
    
    async def get_platform_statistics(
        self,
        platform: CrawlerPlatform,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive statistics for a platform"""
        
        # This would typically query metrics storage
        # For now, return computed statistics
        
        stats = {
            "platform": platform.value,
            "time_window_hours": time_window_hours,
            "active_sessions": len([
                s for s in self._active_sessions.values()
                if s.platform == platform
            ]),
            "total_matches_detected": 0,  # Would be computed from metrics
            "average_similarity_score": 0.0,  # Would be computed from metrics
            "api_quota_usage": 0.0,  # Would be queried from metrics
            "health_score": 100.0,  # Would be computed from health metrics
            "false_positive_rate": 0.0  # Would be computed from validation data
        }
        
        return stats
    
    async def get_surveillance_summary(self) -> Dict[str, Any]:
        """Get overall surveillance operations summary"""
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_sessions": len(self._active_sessions),
            "platforms_monitored": len(set(s.platform for s in self._active_sessions.values())),
            "total_active_users": len(set(s.user_id for s in self._active_sessions.values())),
            "session_breakdown": {}
        }
        
        # Breakdown by platform
        for platform in CrawlerPlatform:
            platform_sessions = [
                s for s in self._active_sessions.values()
                if s.platform == platform
            ]
            summary["session_breakdown"][platform.value] = len(platform_sessions)
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the surveillance metrics collector"""
        
        return {
            "status": "healthy",
            "active_sessions": len(self._active_sessions),
            "metrics_initialized": self.prometheus_manager is not None,
            "redis_connected": self.redis_manager is not None,
            "last_updated": datetime.utcnow().isoformat()
        }
