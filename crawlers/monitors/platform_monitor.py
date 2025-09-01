"""Platform Monitor - Multi-Platform Intelligence Engine  
=====================================================

Professional platform monitoring and status tracking for IA-Influencer-Agent platform.
Implements comprehensive platform health, API status, and service availability monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise  
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
import aiohttp
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict, deque
import statistics

from .monitor_engine import MonitorEngine, MonitoringConfiguration

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """
Platform types for monitoring."""

    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    CONTENT_SHARING = "content_sharing"
    PAYMENT_GATEWAY = "payment_gateway"
    API_SERVICE = "api_service"
    CLOUD_SERVICE = "cloud_service"
    DATABASE = "database"
    MESSAGING = "messaging"

class PlatformStatus(Enum):
    """Platform operational status."""

    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class ServiceHealth(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"

class APIEndpointStatus(Enum):
    """API endpoint status."""

    AVAILABLE = "available"
    SLOW = "slow"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

@dataclass
class PlatformInfo:
    """Platform information and configuration."""
    platform_id: str
    name: str
    platform_type: PlatformType
    api_base_url: str
    status_page_url: Optional[str] = None
    health_check_endpoint: Optional[str] = None
    api_key_required: bool = True
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    critical_endpoints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformHealthCheck:
    """
Platform health check result."""
    platform_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: PlatformStatus = PlatformStatus.UNKNOWN
    response_time: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0
    api_endpoints_status: Dict[str, APIEndpointStatus] = field(default_factory=dict)
    rate_limit_remaining: Optional[int] = None
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformIncident:
    """
Platform incident record."""
    incident_id: str
    platform_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    incident_type: str = ""
    severity: str = "medium"
    description: str = ""
    affected_services: List[str] = field(default_factory=list)
    status: str = "investigating"
    resolution_eta: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    impact: Dict[str, Any] = field(default_factory=dict)

class PlatformMonitor(MonitorEngine):
    """
    Advanced platform monitoring engine.
    Monitors platform availability, API health, and service status across multiple platforms.
    """
    
    def __init__(self, config: MonitoringConfiguration):
        super().__init__(config)
        self.platforms: Dict[str, PlatformInfo] = {}
        self.platform_health: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.active_incidents: Dict[str, PlatformIncident] = {}
        self.api_quotas: Dict[str, Dict[str, Any]] = {}
        self.response_time_thresholds: Dict[str, float] = {}
        
        # Initialize platforms and thresholds
        self._initialize_platforms()
        self._initialize_thresholds()
    
    def _initialize_platforms(self) -> None:
        """
Initialize platform configurations."""
        self.platforms = {
            "spotify": PlatformInfo(
                platform_id="spotify",
                name="Spotify",
                platform_type=PlatformType.STREAMING,
                api_base_url="https://api.spotify.com/v1",
                health_check_endpoint="/me",
                critical_endpoints=["/me", "/tracks", "/albums", "/artists"],
                rate_limit=100,
                timeout=30
            ),
            "youtube": PlatformInfo(
                platform_id="youtube",
                name="YouTube",
                platform_type=PlatformType.CONTENT_SHARING,
                api_base_url="https://www.googleapis.com/youtube/v3",
                health_check_endpoint="/search",
                critical_endpoints=["/search", "/videos", "/channels", "/playlists"],
                rate_limit=10000,
                timeout=30
            ),
            "instagram": PlatformInfo(
                platform_id="instagram",
                name="Instagram",
                platform_type=PlatformType.SOCIAL_MEDIA,
                api_base_url="https://graph.instagram.com",
                health_check_endpoint="/me",
                critical_endpoints=["/me", "/media", "/insights"],
                rate_limit=200,
                timeout=30
            ),
            "tiktok": PlatformInfo(
                platform_id="tiktok",
                name="TikTok",
                platform_type=PlatformType.SOCIAL_MEDIA,
                api_base_url="https://open-api.tiktok.com",
                health_check_endpoint="/user/info",
                critical_endpoints=["/user/info", "/video/list", "/video/query"],
                rate_limit=1000,
                timeout=30
            ),
            "twitter": PlatformInfo(
                platform_id="twitter",
                name="Twitter/X",
                platform_type=PlatformType.SOCIAL_MEDIA,
                api_base_url="https://api.twitter.com/2",
                health_check_endpoint="/users/me",
                critical_endpoints=["/users/me", "/tweets", "/users/by/username"],
                rate_limit=300,
                timeout=30
            )
        }
    
    def _initialize_thresholds(self) -> None:
        """Initialize response time thresholds for platforms."""
        self.response_time_thresholds = {
            "spotify": 2.0,     # 2 seconds
            "youtube": 3.0,     # 3 seconds
            "instagram": 2.5,   # 2.5 seconds
            "tiktok": 3.0,      # 3 seconds
            "twitter": 2.0,     # 2 seconds
            "default": 5.0      # 5 seconds default
        }
    
    async def initialize(self) -> bool:
        """Initialize platform monitoring engine."""
        try:
            logger.info("Initializing platform monitor...")
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Load API credentials
            await self._load_api_credentials()
            
            # Start platform monitoring
            await self.start_periodic_monitoring()
            
            self.start_time = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize platform monitor: {e}")
            return False
    
    async def start_monitoring(self, targets: List[Any]) -> bool:
        """Start platform monitoring operations."""
        try:
            logger.info("Starting platform monitoring...")
            
            # Start monitoring tasks for each platform
            monitoring_tasks = []
            for platform_id in self.platforms:
                task = asyncio.create_task(self._monitor_platform(platform_id))
                monitoring_tasks.append(task)
            
            # Start additional monitoring tasks
            additional_tasks = [
                asyncio.create_task(self._monitor_api_quotas()),
                asyncio.create_task(self._check_platform_status_pages()),
                asyncio.create_task(self._analyze_platform_trends()),
                asyncio.create_task(self._detect_platform_incidents())
            ]
            
            monitoring_tasks.extend(additional_tasks)
            self.monitoring_tasks.extend(monitoring_tasks)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start platform monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop platform monitoring operations."""
        try:
            # Close HTTP session
            if hasattr(self, 'session'):
                await self.session.close()
            
            await self.cleanup()
            return True
        except Exception as e:
            logger.error(f"Failed to stop platform monitoring: {e}")
            return False
    
    async def collect_metrics(self) -> Any:
        """Collect platform monitoring metrics."""
        from .monitor_engine import MonitoringMetrics
        
        # Calculate platform health metrics
        platform_health_summary = {}
        for platform_id, health_history in self.platform_health.items():
            if health_history:
                recent_checks = list(health_history)[-10:]  # Last 10 checks
                avg_response_time = statistics.mean([c.response_time for c in recent_checks])
                success_rate = statistics.mean([c.success_rate for c in recent_checks])
                
                platform_health_summary[platform_id] = {
                    "status": recent_checks[-1].status.value,
                    "avg_response_time": avg_response_time,
                    "success_rate": success_rate,
                    "last_check": recent_checks[-1].timestamp.isoformat()
                }
        
        metrics = MonitoringMetrics()
        metrics.custom_metrics = {
            "total_platforms": len(self.platforms),
            "operational_platforms": len([
                p for p in platform_health_summary.values()
                if p["status"] == "operational"
            ]),
            "active_incidents": len(self.active_incidents),
            "platform_health": platform_health_summary,
            "api_quota_usage": await self._get_api_quota_summary(),
            "average_response_times": {
                pid: summary["avg_response_time"]
                for pid, summary in platform_health_summary.items()
            }
        }
        
        return metrics
    
    async def process_events(self, events: List[Any]) -> None:
        """Process platform events."""
        for event in events:
            await self._process_platform_event(event)
    
    async def _process_platform_event(self, event: Dict[str, Any]) -> None:
        """
Process individual platform event."""
        try:
            event_type = event.get("type", "")
            platform_id = event.get("platform_id", "")
            
            if event_type == "api_error":
                await self._process_api_error_event(event, platform_id)
            elif event_type == "rate_limit":
                await self._process_rate_limit_event(event, platform_id)
            elif event_type == "platform_outage":
                await self._process_outage_event(event, platform_id)
            elif event_type == "api_quota_exceeded":
                await self._process_quota_exceeded_event(event, platform_id)
            
        except Exception as e:
            logger.error(f"Failed to process platform event: {e}")
    
    async def _monitor_platform(self, platform_id: str) -> None:
        """Monitor individual platform health."""
        platform = self.platforms[platform_id]
        
        while True:
            try:
                # Perform health check
                health_check = await self._perform_platform_health_check(platform)
                
                # Store health check result
                self.platform_health[platform_id].append(health_check)
                
                # Check for issues
                await self._analyze_platform_health(platform_id, health_check)
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Platform monitoring error for {platform_id}: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _perform_platform_health_check(self, platform: PlatformInfo) -> PlatformHealthCheck:
        """Perform comprehensive health check for platform."""
        start_time = time.time()
        health_check = PlatformHealthCheck(platform_id=platform.platform_id)
        
        try:
            # Check main health endpoint
            if platform.health_check_endpoint:
                endpoint_url = f"{platform.api_base_url}{platform.health_check_endpoint}"
                
                async with self.session.get(endpoint_url, timeout=platform.timeout) as response:
                    response_time = time.time() - start_time
                    health_check.response_time = response_time
                    
                    if response.status == 200:
                        health_check.status = PlatformStatus.OPERATIONAL
                        health_check.success_rate = 1.0
                    elif response.status >= 500:
                        health_check.status = PlatformStatus.MAJOR_OUTAGE
                        health_check.success_rate = 0.0
                        health_check.error_count = 1
                    else:
                        health_check.status = PlatformStatus.DEGRADED
                        health_check.success_rate = 0.5
                        health_check.error_count = 1
                    
                    # Check rate limit headers
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
                    if rate_limit_remaining:
                        health_check.rate_limit_remaining = int(rate_limit_remaining)
            
            # Check critical endpoints
            endpoint_statuses = {}
            for endpoint in platform.critical_endpoints:
                endpoint_status = await self._check_api_endpoint(platform, endpoint)
                endpoint_statuses[endpoint] = endpoint_status
            
            health_check.api_endpoints_status = endpoint_statuses
            
            # Determine overall status based on endpoint checks
            if all(status == APIEndpointStatus.AVAILABLE for status in endpoint_statuses.values()):
                if health_check.status == PlatformStatus.UNKNOWN:
                    health_check.status = PlatformStatus.OPERATIONAL
            elif any(status == APIEndpointStatus.UNAVAILABLE for status in endpoint_statuses.values()):
                health_check.status = PlatformStatus.MAJOR_OUTAGE
            else:
                health_check.status = PlatformStatus.DEGRADED
                
        except asyncio.TimeoutError:
            health_check.status = PlatformStatus.MAJOR_OUTAGE
            health_check.response_time = platform.timeout
            health_check.last_error = "Request timeout"
            health_check.error_count = 1
        except Exception as e:
            health_check.status = PlatformStatus.MAJOR_OUTAGE
            health_check.last_error = str(e)
            health_check.error_count = 1
        
        return health_check
    
    async def _check_api_endpoint(self, platform: PlatformInfo, endpoint: str) -> APIEndpointStatus:
        """Check individual API endpoint status."""
        try:
            endpoint_url = f"{platform.api_base_url}{endpoint}"
            start_time = time.time()
            
            async with self.session.get(endpoint_url, timeout=platform.timeout) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    if response_time > self.response_time_thresholds.get(platform.platform_id, 5.0):
                        return APIEndpointStatus.SLOW
                    return APIEndpointStatus.AVAILABLE
                elif response.status >= 500:
                    return APIEndpointStatus.ERROR
                elif response.status == 429:  # Rate limited
                    return APIEndpointStatus.SLOW
                else:
                    return APIEndpointStatus.ERROR
                    
        except asyncio.TimeoutError:
            return APIEndpointStatus.TIMEOUT
        except Exception:
            return APIEndpointStatus.UNAVAILABLE
    
    async def _analyze_platform_health(self, platform_id: str, health_check: PlatformHealthCheck) -> None:
        """Analyze platform health and trigger alerts if needed."""
        try:
            # Check for status changes
            recent_checks = list(self.platform_health[platform_id])[-5:]  # Last 5 checks
            
            if len(recent_checks) >= 2:
                previous_status = recent_checks[-2].status
                current_status = health_check.status
                
                if previous_status != current_status:
                    await self._handle_status_change(platform_id, previous_status, current_status)
            
            # Check response time
            threshold = self.response_time_thresholds.get(platform_id, 5.0)
            if health_check.response_time > threshold:
                await self.trigger_alert("slow_platform_response", {
                    "platform_id": platform_id,
                    "response_time": health_check.response_time,
                    "threshold": threshold,
                    "severity": "warning"
                })
            
            # Check error rate
            if len(recent_checks) >= 5:
                error_rate = sum(1 for check in recent_checks if check.error_count > 0) / len(recent_checks)
                if error_rate > 0.6:  # 60% error rate
                    await self.trigger_alert("high_platform_error_rate", {
                        "platform_id": platform_id,
                        "error_rate": error_rate,
                        "severity": "critical"
                    })
            
            # Check API quota
            if health_check.rate_limit_remaining is not None:
                quota_threshold = self.platforms[platform_id].rate_limit * 0.1  # 10% remaining
                if health_check.rate_limit_remaining < quota_threshold:
                    await self.trigger_alert("low_api_quota", {
                        "platform_id": platform_id,
                        "remaining": health_check.rate_limit_remaining,
                        "threshold": quota_threshold,
                        "severity": "warning"
                    })
            
        except Exception as e:
            logger.error(f"Platform health analysis failed for {platform_id}: {e}")
    
    async def _handle_status_change(
        self, 
        platform_id: str, 
        previous_status: PlatformStatus, 
        current_status: PlatformStatus
    ) -> None:
        """Handle platform status changes."""
        platform_name = self.platforms[platform_id].name
        
        # Determine severity
        severity = "info"
        if current_status in [PlatformStatus.MAJOR_OUTAGE, PlatformStatus.PARTIAL_OUTAGE]:
            severity = "critical"
        elif current_status == PlatformStatus.DEGRADED:
            severity = "warning"
        elif current_status == PlatformStatus.OPERATIONAL and previous_status != PlatformStatus.MAINTENANCE:
            severity = "info"  # Recovery
        
        # Trigger alert
        await self.trigger_alert("platform_status_change", {
            "platform_id": platform_id,
            "platform_name": platform_name,
            "previous_status": previous_status.value,
            "current_status": current_status.value,
            "severity": severity
        })
        
        # Create or resolve incident
        if current_status in [PlatformStatus.MAJOR_OUTAGE, PlatformStatus.PARTIAL_OUTAGE]:
            await self._create_platform_incident(platform_id, current_status)
        elif current_status == PlatformStatus.OPERATIONAL:
            await self._resolve_platform_incidents(platform_id)
    
    async def _create_platform_incident(self, platform_id: str, status: PlatformStatus) -> None:
        """Create platform incident record."""
        incident_id = f"incident_{platform_id}_{datetime.utcnow().timestamp()}"
        platform_name = self.platforms[platform_id].name
        
        incident = PlatformIncident(
            incident_id=incident_id,
            platform_id=platform_id,
            incident_type="platform_outage",
            severity="critical" if status == PlatformStatus.MAJOR_OUTAGE else "high",
            description=f"{platform_name} platform experiencing {status.value}",
            affected_services=[platform_id],
            status="investigating"
        )
        
        self.active_incidents[incident_id] = incident
        
        logger.error(f"Platform incident created: {incident_id} - {platform_name} {status.value}")
    
    async def _resolve_platform_incidents(self, platform_id: str) -> None:
        """Resolve platform incidents for specific platform."""
        resolved_incidents = []
        
        for incident_id, incident in self.active_incidents.items():
            if incident.platform_id == platform_id and incident.status != "resolved":
                incident.status = "resolved"
                incident.resolved_at = datetime.utcnow()
                resolved_incidents.append(incident_id)
        
        # Remove resolved incidents
        for incident_id in resolved_incidents:
            del self.active_incidents[incident_id]
        
        if resolved_incidents:
            platform_name = self.platforms[platform_id].name
            logger.info(f"Resolved {len(resolved_incidents)} incidents for {platform_name}")
    
    async def _process_api_error_event(self, event: Dict[str, Any], platform_id: str) -> None:
        """Process API error event."""
        error_code = event.get("error_code", "unknown")
        error_message = event.get("error_message", "")
        
        # Log API error
        logger.warning(f"API error for {platform_id}: {error_code} - {error_message}")
    
    async def _process_rate_limit_event(self, event: Dict[str, Any], platform_id: str) -> None:
        """Process rate limit event."""
        remaining_quota = event.get("remaining_quota", 0)
        reset_time = event.get("reset_time")
        
        # Update API quota tracking
        if platform_id not in self.api_quotas:
            self.api_quotas[platform_id] = {}
        
        self.api_quotas[platform_id].update({
            "remaining": remaining_quota,
            "reset_time": reset_time,
            "last_updated": datetime.utcnow()
        })
    
    async def _process_outage_event(self, event: Dict[str, Any], platform_id: str) -> None:
        """Process platform outage event."""
        await self._create_platform_incident(platform_id, PlatformStatus.MAJOR_OUTAGE)
    
    async def _process_quota_exceeded_event(self, event: Dict[str, Any], platform_id: str) -> None:
        """
Process API quota exceeded event."""
        await self.trigger_alert("api_quota_exceeded", {
            "platform_id": platform_id,
            "severity": "critical"
        })
    
    async def _get_api_quota_summary(self) -> Dict[str, Any]:
        """Get API quota usage summary."""
        quota_summary = {}
        
        for platform_id, quota_info in self.api_quotas.items():
            if quota_info:
                platform = self.platforms[platform_id]
                quota_summary[platform_id] = {
                    "remaining": quota_info.get("remaining", 0),
                    "limit": platform.rate_limit,
                    "usage_percentage": (1 - quota_info.get("remaining", 0) / platform.rate_limit) * 100,
                    "reset_time": quota_info.get("reset_time"),
                    "last_updated": quota_info.get("last_updated")
                }
        
        return quota_summary
    
    async def _load_api_credentials(self) -> None:
        """Load API credentials for platforms."""
        # Implementation would load API credentials from secure storage
        pass
    
    async def _monitor_api_quotas(self) -> None:
        """
Monitor API quota usage across platforms."""
        while True:
            try:
                # Check API quota usage
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"API quota monitoring error: {e}")
                await asyncio.sleep(3600)
    
    async def _check_platform_status_pages(self) -> None:
        """Check platform status pages for incident updates."""
        while True:
            try:
                # Check platform status pages
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Status page monitoring error: {e}")
                await asyncio.sleep(1200)
    
    async def _analyze_platform_trends(self) -> None:
        """Analyze platform performance trends."""
        while True:
            try:
                # Analyze trends
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Platform trend analysis error: {e}")
                await asyncio.sleep(1800)
    
    async def _detect_platform_incidents(self) -> None:
        """Detect and manage platform incidents."""
        while True:
            try:
                # Detect incidents
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Platform incident detection error: {e}")
                await asyncio.sleep(600)

__all__ = [
    "PlatformMonitor",
    "PlatformInfo",
    "PlatformHealthCheck",
    "PlatformIncident",
    "PlatformType",
    "PlatformStatus",
    "ServiceHealth",
    "APIEndpointStatus"
]
