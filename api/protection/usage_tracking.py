"""Advanced content usage tracking and monitoring system for intellectual property protection.

This module implements comprehensive usage monitoring including:
- Real-time content usage detection across platforms
- Automated license compliance verification
- Revenue tracking from authorized usage
- Unauthorized usage detection and alerting
- Usage analytics and reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

Project Team Specialties:
- Lead AI Developer & Senior Backend Engineer: Fahed Mlaiel
- Usage Analytics Specialist: Content Monitoring & Tracking
- License Compliance Engineer: Automated Usage Verification
- Revenue Operations Analyst: Usage-Based Revenue Management
- Security Monitoring Expert: Unauthorized Usage Detection
- Data Pipeline Engineer: Real-time Usage Data Processing

Contact: mlaiel@live.de

LEGAL WARNING: This software and all associated intellectual property
belong exclusively to Fahed Mlaiel. Any unauthorized copying, redistribution,
reverse engineering, or commercial use without explicit written permission
will result in immediate legal action under international copyright laws.
"""import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import json
import hashlib
from urllib.parse import urlencode, urlparse
import re
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.config import get_database, get_redis_client
from ..core.exceptions import UsageException, MonitoringException


class UsageStatus(Enum):
    """Content usage status."""    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    PENDING_VERIFICATION = "pending_verification"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    MONITORING = "monitoring"


class DetectionMethod(Enum):
    """Usage detection methods."""    FINGERPRINTING = "fingerprinting"
    WATERMARK = "watermark"
    METADATA_ANALYSIS = "metadata_analysis"
    API_MONITORING = "api_monitoring"
    CRAWLER_DETECTION = "crawler_detection"
    USER_REPORT = "user_report"
    PLATFORM_NOTIFICATION = "platform_notification"


class UsageContext(Enum):
    """Context of content usage."""    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDUCATIONAL = "educational"
    EDITORIAL = "editorial"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    RESEARCH = "research"
    UNKNOWN = "unknown"


class PlatformType(Enum):
    """Types of platforms for usage monitoring."""    STREAMING_SERVICE = "streaming_service"
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    MUSIC_PLATFORM = "music_platform"
    BLOG_PLATFORM = "blog_platform"
    E_COMMERCE = "e_commerce"
    NEWS_WEBSITE = "news_website"
    PODCAST_PLATFORM = "podcast_platform"
    GAMING_PLATFORM = "gaming_platform"
    OTHER = "other"


@dataclass
class UsageDetection:
    """Content usage detection record."""    detection_id: str
    content_id: str
    detected_url: str
    platform: str
    platform_type: PlatformType
    detection_method: DetectionMethod
    usage_status: UsageStatus
    usage_context: UsageContext
    confidence_score: float
    detected_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_score: Optional[float] = None
    duration_detected: Optional[float] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    geographic_location: Optional[str] = None
    is_processed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UsageVerification:
    """Usage verification record."""    verification_id: str
    detection_id: str
    verified_by: str
    verification_method: str
    verification_result: UsageStatus
    license_reference: Optional[str] = None
    verification_notes: str = ""
    revenue_impact: Optional[Decimal] = None
    action_required: bool = False
    verified_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformMonitor:
    """Platform monitoring configuration."""    monitor_id: str
    platform_name: str
    platform_type: PlatformType
    base_url: str
    api_endpoint: Optional[str] = None
    authentication: Dict[str, str] = field(default_factory=dict)
    monitoring_enabled: bool = True
    scan_frequency_minutes: int = 60
    detection_methods: List[DetectionMethod] = field(default_factory=list)
    rate_limit_per_hour: int = 1000
    last_scan: Optional[datetime] = None
    total_detections: int = 0
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UsageMetrics:
    """Usage tracking metrics."""    metrics_id: str
    content_id: str
    period_start: datetime
    period_end: datetime
    total_detections: int = 0
    authorized_usage: int = 0
    unauthorized_usage: int = 0
    pending_verifications: int = 0
    revenue_generated: Decimal = Decimal("0.00")
    top_platforms: List[str] = field(default_factory=list)
    usage_trends: Dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.utcnow)


class ContentUsageTracker:
    """    Advanced content usage tracking and monitoring system.
    
    Provides comprehensive usage monitoring including:
    - Real-time content usage detection across platforms
    - Automated license compliance verification
    - Revenue tracking from authorized usage
    - Unauthorized usage detection and enforcement
    - Usage analytics and trend analysis
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("protection.usage_tracking")
        self.db = get_database()
        self.redis = get_redis_client()
        
        # Session management
        self.session = None
        self.session_timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Monitoring settings
        self.monitoring_enabled = self.config.get("monitoring_enabled", True)
        self.scan_interval_minutes = self.config.get("scan_interval_minutes", 30)
        self.detection_threshold = self.config.get("detection_threshold", 0.8)
        self.max_concurrent_scans = self.config.get("max_concurrent_scans", 10)
        
        # Platform configurations
        self.platform_monitors = {}
        self.detection_engines = {}
        
        # Usage verification settings
        self.auto_verification_enabled = self.config.get("auto_verification", True)
        self.manual_verification_threshold = self.config.get("manual_threshold", 0.6)
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_scans)
        
        # Initialize components
        asyncio.create_task(self._initialize_usage_tracker())
        
        self.logger.info("ContentUsageTracker initialized successfully")
    
    async def _initialize_usage_tracker(self):
        """Initialize usage tracking system components."""        try:
            # Initialize HTTP session
            await self._initialize_session()
            
            # Load platform monitors
            await self._load_platform_monitors()
            
            # Initialize detection engines
            await self._initialize_detection_engines()
            
            # Start background monitoring
            if self.monitoring_enabled:
                await self._start_monitoring_tasks()
            
            self.logger.info("Usage tracker components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Usage tracker initialization failed: {e}")
            raise UsageException(f"Initialization error: {e}")
    
    async def _initialize_session(self):
        """Initialize aiohttp session for web requests."""        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                enable_cleanup_closed=True
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.session_timeout,
                headers={
                    "User-Agent": "IA-Influencer-Agent/2.0 Usage-Tracker"
                }
            )
            
            self.logger.info("Usage tracker HTTP session initialized")
            
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise UsageException(f"Session initialization error: {e}")
    
    async def _load_platform_monitors(self):
        """Load platform monitoring configurations from database."""        try:
            query = """            SELECT 
                monitor_id, platform_name, platform_type, base_url,
                api_endpoint, authentication, monitoring_enabled,
                scan_frequency_minutes, detection_methods, rate_limit_per_hour,
                last_scan, total_detections, success_rate
            FROM platform_monitors
            WHERE monitoring_enabled = true
            ORDER BY platform_name
            """            
            results = await self.db.fetch(query)
            
            for row in results:
                monitor = PlatformMonitor(
                    monitor_id=row["monitor_id"],
                    platform_name=row["platform_name"],
                    platform_type=PlatformType(row["platform_type"]),
                    base_url=row["base_url"],
                    api_endpoint=row["api_endpoint"],
                    authentication=json.loads(row["authentication"] or "{}"),
                    monitoring_enabled=row["monitoring_enabled"],
                    scan_frequency_minutes=row["scan_frequency_minutes"],
                    detection_methods=[DetectionMethod(m) for m in json.loads(row["detection_methods"] or "[]")],
                    rate_limit_per_hour=row["rate_limit_per_hour"],
                    last_scan=row["last_scan"],
                    total_detections=row["total_detections"],
                    success_rate=float(row["success_rate"])
                )
                
                self.platform_monitors[monitor.platform_name] = monitor
            
            self.logger.info(f"Loaded {len(self.platform_monitors)} platform monitors")
            
        except Exception as e:
            self.logger.error(f"Platform monitor loading failed: {e}")
            # Initialize with default monitors
            await self._initialize_default_monitors()
    
    async def _initialize_default_monitors(self):
        """Initialize default platform monitors."""        default_monitors = {
            "youtube": PlatformMonitor(
                monitor_id="youtube_monitor",
                platform_name="youtube",
                platform_type=PlatformType.VIDEO_PLATFORM,
                base_url="https://www.youtube.com",
                api_endpoint="https://www.googleapis.com/youtube/v3",
                detection_methods=[DetectionMethod.API_MONITORING, DetectionMethod.FINGERPRINTING],
                scan_frequency_minutes=30
            ),
            "instagram": PlatformMonitor(
                monitor_id="instagram_monitor",
                platform_name="instagram",
                platform_type=PlatformType.SOCIAL_MEDIA,
                base_url="https://www.instagram.com",
                api_endpoint="https://graph.instagram.com",
                detection_methods=[DetectionMethod.API_MONITORING, DetectionMethod.METADATA_ANALYSIS],
                scan_frequency_minutes=60
            ),
            "spotify": PlatformMonitor(
                monitor_id="spotify_monitor",
                platform_name="spotify",
                platform_type=PlatformType.MUSIC_PLATFORM,
                base_url="https://open.spotify.com",
                api_endpoint="https://api.spotify.com/v1",
                detection_methods=[DetectionMethod.API_MONITORING, DetectionMethod.FINGERPRINTING],
                scan_frequency_minutes=120
            )
        }
        
        self.platform_monitors.update(default_monitors)
    
    async def register_content_for_tracking(
        self,
        content_id: str,
        content_hash: str,
        content_metadata: Dict[str, Any],
        tracking_enabled: bool = True
    ) -> str:
        """        Register content for usage tracking.
        
        Args:
            content_id: Unique content identifier
            content_hash: Content fingerprint hash
            content_metadata: Content metadata for identification
            tracking_enabled: Whether to enable tracking
            
        Returns:
            Tracking registration ID
        """        try:
            tracking_id = f"track_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Registering content for tracking: {content_id}")
            
            # Store content tracking information
            await self._store_content_tracking_info(
                tracking_id,
                content_id,
                content_hash,
                content_metadata,
                tracking_enabled
            )
            
            # Initialize monitoring for this content
            if tracking_enabled:
                await self._initialize_content_monitoring(tracking_id, content_id)
            
            self.logger.info(f"Content registered for tracking: {tracking_id}")
            
            return tracking_id
            
        except Exception as e:
            self.logger.error(f"Content registration failed: {e}")
            raise UsageException(f"Registration error: {e}")
    
    async def detect_content_usage(
        self,
        content_id: str,
        search_platforms: List[str] = None,
        detection_methods: List[DetectionMethod] = None
    ) -> List[UsageDetection]:
        """        Detect content usage across platforms.
        
        Args:
            content_id: Content to search for
            search_platforms: Specific platforms to search
            detection_methods: Detection methods to use
            
        Returns:
            List of usage detections
        """        try:
            self.logger.info(f"Starting content usage detection for: {content_id}")
            
            detections = []
            
            # Get content information
            content_info = await self._get_content_tracking_info(content_id)
            if not content_info:
                raise UsageException(f"Content not registered for tracking: {content_id}")
            
            # Determine platforms to search
            platforms_to_search = search_platforms or list(self.platform_monitors.keys())
            
            # Determine detection methods
            methods_to_use = detection_methods or [
                DetectionMethod.FINGERPRINTING,
                DetectionMethod.API_MONITORING,
                DetectionMethod.METADATA_ANALYSIS
            ]
            
            # Perform detection on each platform
            detection_tasks = []
            for platform_name in platforms_to_search:
                if platform_name in self.platform_monitors:
                    monitor = self.platform_monitors[platform_name]
                    for method in methods_to_use:
                        if method in monitor.detection_methods:
                            task = self._detect_on_platform(
                                content_info,
                                monitor,
                                method
                            )
                            detection_tasks.append(task)
            
            # Execute detection tasks concurrently
            if detection_tasks:
                detection_results = await asyncio.gather(*detection_tasks, return_exceptions=True)
                
                for result in detection_results:
                    if isinstance(result, Exception):
                        self.logger.error(f"Detection task failed: {result}")
                        continue
                    
                    if isinstance(result, list):
                        detections.extend(result)
                    elif result:
                        detections.append(result)
            
            # Store detections in database
            for detection in detections:
                await self._store_usage_detection(detection)
            
            # Trigger automatic verification for high-confidence detections
            high_confidence_detections = [
                d for d in detections 
                if d.confidence_score >= self.detection_threshold
            ]
            
            if high_confidence_detections and self.auto_verification_enabled:
                await self._trigger_automatic_verification(high_confidence_detections)
            
            self.logger.info(f"Content usage detection completed: {len(detections)} detections found")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Content usage detection failed: {e}")
            raise UsageException(f"Detection error: {e}")
    
    async def _detect_on_platform(
        self,
        content_info: Dict[str, Any],
        monitor: PlatformMonitor,
        method: DetectionMethod
    ) -> List[UsageDetection]:
        """Detect content usage on specific platform using given method."""        try:
            detections = []
            
            if method == DetectionMethod.API_MONITORING:
                detections = await self._detect_via_api(content_info, monitor)
            elif method == DetectionMethod.FINGERPRINTING:
                detections = await self._detect_via_fingerprinting(content_info, monitor)
            elif method == DetectionMethod.METADATA_ANALYSIS:
                detections = await self._detect_via_metadata(content_info, monitor)
            elif method == DetectionMethod.CRAWLER_DETECTION:
                detections = await self._detect_via_crawler(content_info, monitor)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Platform detection failed for {monitor.platform_name}: {e}")
            return []
    
    async def _detect_via_api(
        self,
        content_info: Dict[str, Any],
        monitor: PlatformMonitor
    ) -> List[UsageDetection]:
        """Detect content usage via platform API."""        try:
            detections = []
            
            if not monitor.api_endpoint:
                return detections
            
            # Platform-specific API detection logic
            if monitor.platform_type == PlatformType.VIDEO_PLATFORM:
                detections = await self._detect_video_api(content_info, monitor)
            elif monitor.platform_type == PlatformType.MUSIC_PLATFORM:
                detections = await self._detect_music_api(content_info, monitor)
            elif monitor.platform_type == PlatformType.SOCIAL_MEDIA:
                detections = await self._detect_social_api(content_info, monitor)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"API detection failed: {e}")
            return []
    
    async def _detect_video_api(
        self,
        content_info: Dict[str, Any],
        monitor: PlatformMonitor
    ) -> List[UsageDetection]:
        """Detect video content via YouTube API."""        try:
            detections = []
            
            # Search for content using title and metadata
            search_query = content_info.get("title", "")
            if content_info.get("artist"):
                search_query += f" {content_info['artist']}"
            
            # YouTube API search
            if monitor.platform_name == "youtube" and monitor.authentication.get("api_key"):
                search_url = f"{monitor.api_endpoint}/search"
                params = {
                    "part": "snippet",
                    "q": search_query,
                    "type": "video",
                    "maxResults": 50,
                    "key": monitor.authentication["api_key"]
                }
                
                async with self.session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get("items", []):
                            # Calculate similarity score
                            similarity_score = await self._calculate_content_similarity(
                                content_info,
                                item["snippet"]
                            )
                            
                            if similarity_score >= 0.6:  # Minimum similarity threshold
                                detection = UsageDetection(
                                    detection_id=f"det_{uuid.uuid4().hex[:12]}",
                                    content_id=content_info["content_id"],
                                    detected_url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                                    platform=monitor.platform_name,
                                    platform_type=monitor.platform_type,
                                    detection_method=DetectionMethod.API_MONITORING,
                                    usage_status=UsageStatus.PENDING_VERIFICATION,
                                    usage_context=UsageContext.UNKNOWN,
                                    confidence_score=similarity_score,
                                    similarity_score=similarity_score,
                                    detected_at=datetime.utcnow(),
                                    metadata={
                                        "video_id": item["id"]["videoId"],
                                        "title": item["snippet"]["title"],
                                        "description": item["snippet"]["description"],
                                        "channel": item["snippet"]["channelTitle"],
                                        "published_at": item["snippet"]["publishedAt"]
                                    }
                                )
                                detections.append(detection)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Video API detection failed: {e}")
            return []
    
    async def _detect_music_api(
        self,
        content_info: Dict[str, Any],
        monitor: PlatformMonitor
    ) -> List[UsageDetection]:
        """Detect music content via Spotify API."""        try:
            detections = []
            
            # Search for content using title and artist
            search_query = content_info.get("title", "")
            if content_info.get("artist"):
                search_query += f" artist:{content_info['artist']}"
            
            # Spotify API search
            if monitor.platform_name == "spotify" and monitor.authentication.get("access_token"):
                search_url = f"{monitor.api_endpoint}/search"
                params = {
                    "q": search_query,
                    "type": "track",
                    "limit": 50
                }
                
                headers = {
                    "Authorization": f"Bearer {monitor.authentication['access_token']}"
                }
                
                async with self.session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for track in data.get("tracks", {}).get("items", []):
                            # Calculate similarity score
                            similarity_score = await self._calculate_music_similarity(
                                content_info,
                                track
                            )
                            
                            if similarity_score >= 0.7:  # Higher threshold for music
                                detection = UsageDetection(
                                    detection_id=f"det_{uuid.uuid4().hex[:12]}",
                                    content_id=content_info["content_id"],
                                    detected_url=track["external_urls"]["spotify"],
                                    platform=monitor.platform_name,
                                    platform_type=monitor.platform_type,
                                    detection_method=DetectionMethod.API_MONITORING,
                                    usage_status=UsageStatus.PENDING_VERIFICATION,
                                    usage_context=UsageContext.COMMERCIAL,
                                    confidence_score=similarity_score,
                                    similarity_score=similarity_score,
                                    detected_at=datetime.utcnow(),
                                    duration_detected=track.get("duration_ms", 0) / 1000,
                                    metadata={
                                        "track_id": track["id"],
                                        "name": track["name"],
                                        "artists": [artist["name"] for artist in track["artists"]],
                                        "album": track["album"]["name"],
                                        "popularity": track["popularity"],
                                        "preview_url": track.get("preview_url")
                                    }
                                )
                                detections.append(detection)
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Music API detection failed: {e}")
            return []
    
    async def verify_usage_authorization(
        self,
        detection_id: str,
        verified_by: str,
        verification_method: str = "manual"
    ) -> UsageVerification:
        """        Verify if detected content usage is authorized.
        
        Args:
            detection_id: Detection to verify
            verified_by: User performing verification
            verification_method: Method used for verification
            
        Returns:
            Usage verification record
        """        try:
            verification_id = f"verify_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Verifying usage authorization: {detection_id}")
            
            # Get detection record
            detection = await self._get_usage_detection(detection_id)
            if not detection:
                raise UsageException(f"Detection not found: {detection_id}")
            
            # Check for existing licenses/permissions
            license_reference = await self._check_usage_authorization(
                detection["content_id"],
                detection["detected_url"],
                detection["platform"]
            )
            
            # Determine verification result
            if license_reference:
                verification_result = UsageStatus.AUTHORIZED
                action_required = False
            else:
                verification_result = UsageStatus.UNAUTHORIZED
                action_required = True
            
            # Calculate potential revenue impact
            revenue_impact = await self._calculate_revenue_impact(detection, verification_result)
            
            # Create verification record
            verification = UsageVerification(
                verification_id=verification_id,
                detection_id=detection_id,
                verified_by=verified_by,
                verification_method=verification_method,
                verification_result=verification_result,
                license_reference=license_reference,
                revenue_impact=revenue_impact,
                action_required=action_required
            )
            
            # Store verification
            await self._store_usage_verification(verification)
            
            # Update detection status
            await self._update_detection_status(detection_id, verification_result)
            
            # Trigger actions if unauthorized usage detected
            if verification_result == UsageStatus.UNAUTHORIZED:
                await self._trigger_unauthorized_usage_actions(detection, verification)
            
            self.logger.info(f"Usage verification completed: {verification_id}")
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Usage verification failed: {e}")
            raise UsageException(f"Verification error: {e}")
    
    async def get_usage_analytics(
        self,
        content_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> UsageMetrics:
        """        Get comprehensive usage analytics for content.
        
        Args:
            content_id: Content identifier
            start_date: Analytics period start
            end_date: Analytics period end
            
        Returns:
            Usage metrics and analytics
        """        try:
            metrics_id = f"metrics_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(f"Generating usage analytics for content: {content_id}")
            
            # Get usage detections for the period
            detections_query = """            SELECT 
                detection_id, platform, platform_type, usage_status,
                confidence_score, detected_at, metadata
            FROM usage_detections
            WHERE content_id = $1 
                AND detected_at BETWEEN $2 AND $3
            ORDER BY detected_at DESC
            """            
            detections = await self.db.fetch(detections_query, content_id, start_date, end_date)
            
            # Calculate metrics
            total_detections = len(detections)
            authorized_usage = len([d for d in detections if d["usage_status"] == UsageStatus.AUTHORIZED.value])
            unauthorized_usage = len([d for d in detections if d["usage_status"] == UsageStatus.UNAUTHORIZED.value])
            pending_verifications = len([d for d in detections if d["usage_status"] == UsageStatus.PENDING_VERIFICATION.value])
            
            # Get revenue data
            revenue_query = """            SELECT COALESCE(SUM(revenue_impact), 0) as total_revenue
            FROM usage_verifications uv
            JOIN usage_detections ud ON uv.detection_id = ud.detection_id
            WHERE ud.content_id = $1 
                AND uv.verified_at BETWEEN $2 AND $3
            """            
            revenue_result = await self.db.fetchrow(revenue_query, content_id, start_date, end_date)
            revenue_generated = revenue_result["total_revenue"] or Decimal("0.00")
            
            # Get top platforms
            platform_usage = {}
            for detection in detections:
                platform = detection["platform"]
                platform_usage[platform] = platform_usage.get(platform, 0) + 1
            
            top_platforms = sorted(platform_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            top_platforms = [platform for platform, count in top_platforms]
            
            # Calculate usage trends
            usage_trends = await self._calculate_usage_trends(content_id, start_date, end_date)
            
            # Create metrics record
            metrics = UsageMetrics(
                metrics_id=metrics_id,
                content_id=content_id,
                period_start=start_date,
                period_end=end_date,
                total_detections=total_detections,
                authorized_usage=authorized_usage,
                unauthorized_usage=unauthorized_usage,
                pending_verifications=pending_verifications,
                revenue_generated=revenue_generated,
                top_platforms=top_platforms,
                usage_trends=usage_trends
            )
            
            # Store metrics
            await self._store_usage_metrics(metrics)
            
            self.logger.info(f"Usage analytics generated: {metrics_id}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Usage analytics generation failed: {e}")
            raise UsageException(f"Analytics error: {e}")
    
    async def cleanup_resources(self):
        """Clean up usage tracker resources."""        try:
            if self.session and not self.session.closed:
                await self.session.close()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            
            self.logger.info("Usage tracker resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Resource cleanup failed: {e}")


# Factory function for easy instantiation
def create_usage_tracker(config: Optional[Dict[str, Any]] = None) -> ContentUsageTracker:
    """Create and return configured usage tracker instance."""    return ContentUsageTracker(config)
