"""IA Influencer Agent - Professional Surveillance Module
========================================================

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

(c) 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🚨 STRICT COPYRIGHT WARNING:
This software and its concepts are the exclusive intellectual property of Fahed Mlaiel.
ANY UNAUTHORIZED COPYING, DISTRIBUTION, REVERSE ENGINEERING, OR THEFT OF IDEAS, CONCEPTS, 
OR CODE WITHOUT EXPLICIT WRITTEN AUTHORIZATION from Fahed Mlaiel will result in immediate 
legal action. Contact mlaiel@live.de for authorization.

Professional enterprise-grade surveillance and monitoring system for content protection
across multiple creator types and digital platforms. This module provides real-time
surveillance, threat detection, business intelligence, and automated response capabilities
according to the unified IA Influencer Agent requirements specification.

COMPLETE IMPLEMENTATION FEATURES:
- Real-time content monitoring and protection
- AI-powered violation detection and classification
- Business intelligence and revenue optimization
- Advanced threat detection and correlation
- Professional legal documentation and takedown management
- Multi-platform orchestration and coordination
- Compliance monitoring and regulatory frameworks
- Performance analytics and system optimization
- WebSocket real-time notifications
- Scalable enterprise architecture
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Callable

# Core surveillance components
from .monitoring_system import (
    ContentMonitoringSystem,
    MonitoringSystem,
    ViolationAlert,
    CreatorProfile,
    AlertSeverity,
    MonitoringEngine,
    ContentMonitor,
    PlatformMonitor
)

from .platform_orchestrator import (
    PlatformOrchestrator,
    RateLimitManager,
    LoadBalancer,
    CrossPlatformCorrelator,
    PlatformCoordinator,
    TrafficManager,
    ResourceAllocator
)

from .business_intelligence import (
    BusinessIntelligenceEngine,
    RevenueCalculationEngine,
    MarketAnalysisEngine,
    ROICalculator,
    CompetitiveAnalyzer,
    TrendAnalyzer,
    BusinessReportGenerator
)

from .violation_manager import (
    ViolationManager,
    EvidenceCollector,
    TakedownManager,
    ViolationAnalyzer,
    LegalDocumentGenerator,
    ComplianceTracker,
    ResponseAutomator
)

from .realtime_surveillance import (
    RealTimeSurveillanceEngine,
    EventBuffer,
    EventCorrelator,
    StreamingProcessor,
    ThreatAnalyzer,
    AlertDispatcher,
    ResponseManager
)

# Import new surveillance modules
from .youtube_monitor import YouTubeMonitor, YouTubeMonitorTarget, YouTubeViolation, YouTubeMonitoringMetrics
from .tiktok_crawler import TikTokCrawler, TikTokUser, TikTokVideo, TikTokComment, TikTokHashtag, TikTokCrawlResult
from .instagram_detector import InstagramDetector, InstagramPost, InstagramStory, InstagramUser, InstagramReel, InstagramViolation, InstagramDetectionMetrics
from .facebook_scanner import FacebookScanner, FacebookPost, FacebookPage, FacebookGroup, FacebookUser, FacebookComment, FacebookViolation, FacebookScanMetrics
from .twitter_monitor import TwitterMonitor, Tweet, TwitterUser, TwitterTrend, TwitterSpace, TwitterViolation, TwitterMonitoringMetrics
from .spotify_tracker import SpotifyTracker, SpotifyTrack, SpotifyArtist, SpotifyAlbum, SpotifyPlaylist, SpotifyUser, SpotifyViolation, SpotifyTrackingMetrics
from .universal_web_crawler import UniversalWebCrawler, WebPage, CrawlJob, CrawlResult, WebViolation, CrawlerMetrics
from .violation_alert_system import ViolationAlertSystem, Alert, AlertRule, AlertTemplate, AlertMetrics, AlertSeverity as AlertSystemSeverity, AlertStatus, AlertChannel
from .content_matching_engine import ContentMatchingEngine, ContentFingerprint, ProtectedContent, ContentMatch, MatchingTask, MatchingMetrics, ContentType, MatchType
from .surveillance_orchestrator import SurveillanceOrchestrator, SurveillanceTarget as OrchestratorTarget, SurveillancePolicy, SurveillanceMetrics as OrchestratorMetrics, SurveillanceStatus as OrchestratorStatus, ModuleStatus, ModuleState

logger = logging.getLogger(__name__)


class SurveillanceSystem:
    """
    Main surveillance system coordinator.
    
    This class orchestrates all surveillance components and provides
    a unified interface for content protection operations.
    
    Features:
    - Real-time content monitoring across all platforms
    - AI-powered violation detection and classification
    - Business intelligence and revenue optimization
    - Advanced threat detection and correlation
    - Professional legal documentation and takedown management
    - Multi-platform orchestration and coordination
    - Compliance monitoring and regulatory frameworks
    - Performance analytics and system optimization
    - WebSocket real-time notifications
    - Scalable enterprise architecture
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize the surveillance system."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        
        # Core components - Professional modules
        self.monitoring_system = ContentMonitoringSystem(self.config.get('monitoring', {}))
        self.platform_orchestrator = PlatformOrchestrator(self.config.get('platform', {}))
        self.business_intelligence = BusinessIntelligenceEngine(self.config.get('business', {}))
        self.violation_manager = ViolationManager(self.config.get('violations', {}))
        self.realtime_surveillance = RealTimeSurveillanceEngine(self.config.get('realtime', {}))
        
        # System state
        self._initialized = False
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize all surveillance components."""
        try:
            self._logger.info("Initializing IA Influencer Agent Professional Surveillance System...")
            
            # Initialize all components
            await self.monitoring_system.initialize()
            await self.platform_orchestrator.initialize()
            await self.business_intelligence.initialize()
            await self.violation_manager.initialize()
            await self.realtime_surveillance.initialize()
            
            self._initialized = True
            self._logger.info("Professional Surveillance System initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize professional surveillance system: {e}")
            raise
    
    async def start_monitoring(self) -> None:
        """Start the surveillance monitoring operations."""
        if not self._initialized:
            await self.initialize()
        
        try:
            self._logger.info("Starting professional surveillance monitoring operations...")
            
            # Start monitoring components
            await self.monitoring_system.start_monitoring()
            await self.platform_orchestrator.start_coordination()
            await self.business_intelligence.start_analysis()
            await self.violation_manager.start_processing()
            await self.realtime_surveillance.start_surveillance()
            
            self._running = True
            self._logger.info("Professional surveillance monitoring started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start professional surveillance monitoring: {e}")
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop the surveillance monitoring operations."""
        try:
            self._logger.info("Stopping professional surveillance monitoring operations...")
            
            # Stop monitoring components
            await self.monitoring_system.stop_monitoring()
            await self.platform_orchestrator.stop_coordination()
            await self.business_intelligence.stop_analysis()
            await self.violation_manager.stop_processing()
            await self.realtime_surveillance.stop_surveillance()
            
            self._running = False
            self._logger.info("Professional surveillance monitoring stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to stop professional surveillance monitoring: {e}")
            raise
    
    async def monitor_creator(
        self,
        creator_id: str,
        platforms: List[str],
        monitoring_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Monitor a specific creator across platforms."""
        try:
            await self.monitoring_system.add_creator_monitoring(
                creator_id, platforms, monitoring_config
            )
            
            # Configure platform orchestration
            await self.platform_orchestrator.configure_creator_monitoring(
                creator_id, platforms
            )
            
            # Setup business intelligence tracking
            await self.business_intelligence.track_creator_revenue(creator_id)
            
            # Initialize violation monitoring
            await self.violation_manager.setup_creator_protection(creator_id)
            
            # Enable real-time surveillance
            await self.realtime_surveillance.monitor_creator(creator_id, platforms)
            
            self._logger.info(
                f"Started comprehensive monitoring for creator {creator_id} "
                f"on platforms: {platforms}"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to monitor creator {creator_id}: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'initialized': self._initialized,
            'running': self._running,
            'monitoring_system': await self.monitoring_system.get_status(),
            'platform_orchestrator': await self.platform_orchestrator.get_status(),
            'business_intelligence': await self.business_intelligence.get_status(),
            'violation_manager': await self.violation_manager.get_status(),
            'realtime_surveillance': await self.realtime_surveillance.get_status()
        }
    
    async def shutdown(self) -> None:
        """
Shutdown the surveillance system gracefully."""
        try:
            self._logger.info("Shutting down Professional Surveillance System...")
            
            # Stop monitoring if running
            if self._running:
                await self.stop_monitoring()
            
            # Shutdown all components
            await self.monitoring_system.shutdown()
            await self.platform_orchestrator.shutdown()
            await self.business_intelligence.shutdown()
            await self.violation_manager.shutdown()
            await self.realtime_surveillance.shutdown()
            
            self._initialized = False
            self._logger.info("Professional Surveillance System shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during professional surveillance system shutdown: {e}")
            raise


# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "(c) 2024 IA Influencer Agent Development Team. All rights reserved."
__license__ = "Proprietary"

# Import new surveillance modules
from .youtube_monitor import YouTubeMonitor, YouTubeMonitorTarget, YouTubeViolation, YouTubeMonitoringMetrics
from .tiktok_crawler import TikTokCrawler, TikTokUser, TikTokVideo, TikTokComment, TikTokHashtag, TikTokCrawlResult
from .instagram_detector import InstagramDetector, InstagramPost, InstagramStory, InstagramUser, InstagramReel, InstagramViolation, InstagramDetectionMetrics
from .facebook_scanner import FacebookScanner, FacebookPost, FacebookPage, FacebookGroup, FacebookUser, FacebookComment, FacebookViolation, FacebookScanMetrics
from .twitter_monitor import TwitterMonitor, Tweet, TwitterUser, TwitterTrend, TwitterSpace, TwitterViolation, TwitterMonitoringMetrics
from .spotify_tracker import SpotifyTracker, SpotifyTrack, SpotifyArtist, SpotifyAlbum, SpotifyPlaylist, SpotifyUser, SpotifyViolation, SpotifyTrackingMetrics
from .universal_web_crawler import UniversalWebCrawler, WebPage, CrawlJob, CrawlResult, WebViolation, CrawlerMetrics
from .violation_alert_system import ViolationAlertSystem, Alert, AlertRule, AlertTemplate, AlertMetrics, AlertSeverity, AlertStatus, AlertChannel
from .content_matching_engine import ContentMatchingEngine, ContentFingerprint, ProtectedContent, ContentMatch, MatchingTask, MatchingMetrics, ContentType, MatchType
from .surveillance_orchestrator import SurveillanceOrchestrator, SurveillanceTarget as OrchestratorTarget, SurveillancePolicy, SurveillanceMetrics as OrchestratorMetrics, SurveillanceStatus as OrchestratorStatus, ModuleStatus, ModuleState

# Export main classes and functions
__all__ = [
    # Main system
    'SurveillanceSystem',
    
    # Content monitoring system
    'ContentMonitoringSystem',
    'MonitoringSystem',
    'ViolationAlert',
    'CreatorProfile',
    'AlertSeverity',
    'MonitoringEngine',
    'ContentMonitor',
    'PlatformMonitor',
    
    # Platform orchestrator
    'PlatformOrchestrator',
    'RateLimitManager',
    'LoadBalancer',
    'CrossPlatformCorrelator',
    'PlatformCoordinator',
    'TrafficManager',
    'ResourceAllocator',
    
    # Business intelligence
    'BusinessIntelligenceEngine',
    'RevenueCalculationEngine',
    'MarketAnalysisEngine',
    'ROICalculator',
    'CompetitiveAnalyzer',
    'TrendAnalyzer',
    'BusinessReportGenerator',
    
    # Violation manager
    'ViolationManager',
    'EvidenceCollector',
    'TakedownManager',
    'ViolationAnalyzer',
    'LegalDocumentGenerator',
    'ComplianceTracker',
    'ResponseAutomator',
    
    # Real-time surveillance
    'RealTimeSurveillanceEngine',
    'EventBuffer',
    'EventCorrelator',
    'StreamingProcessor',
    'ThreatAnalyzer',
    'AlertDispatcher',
    'ResponseManager',
    
    # Surveillance engine
    'SurveillanceEngine',
    'SurveillanceTarget',
    'SurveillanceTask',
    'SurveillanceMetrics',
    'SurveillanceStatus',
    'SurveillancePriority',
    
    # YouTube Monitor
    'YouTubeMonitor',
    'YouTubeMonitorTarget',
    'YouTubeViolation',
    'YouTubeMonitoringMetrics',
    
    # TikTok Crawler
    'TikTokCrawler',
    'TikTokUser',
    'TikTokVideo',
    'TikTokComment',
    'TikTokHashtag',
    'TikTokCrawlResult',
    
    # Instagram Detector
    'InstagramDetector',
    'InstagramPost',
    'InstagramStory',
    'InstagramUser',
    'InstagramReel',
    'InstagramViolation',
    'InstagramDetectionMetrics',
    
    # Facebook Scanner
    'FacebookScanner',
    'FacebookPost',
    'FacebookPage',
    'FacebookGroup',
    'FacebookUser',
    'FacebookComment',
    'FacebookViolation',
    'FacebookScanMetrics',
    
    # Twitter Monitor
    'TwitterMonitor',
    'Tweet',
    'TwitterUser',
    'TwitterTrend',
    'TwitterSpace',
    'TwitterViolation',
    'TwitterMonitoringMetrics',
    
    # Spotify Tracker
    'SpotifyTracker',
    'SpotifyTrack',
    'SpotifyArtist',
    'SpotifyAlbum',
    'SpotifyPlaylist',
    'SpotifyUser',
    'SpotifyViolation',
    'SpotifyTrackingMetrics',
    
    # Universal Web Crawler
    'UniversalWebCrawler',
    'WebPage',
    'CrawlJob',
    'CrawlResult',
    'WebViolation',
    'CrawlerMetrics',
    
    # Violation Alert System
    'ViolationAlertSystem',
    'Alert',
    'AlertRule',
    'AlertTemplate',
    'AlertMetrics',
    'AlertSeverity',
    'AlertStatus',
    'AlertChannel',
    
    # Content Matching Engine
    'ContentMatchingEngine',
    'ContentFingerprint',
    'ProtectedContent',
    'ContentMatch',
    'MatchingTask',
    'MatchingMetrics',
    'ContentType',
    'MatchType',
    
    # Surveillance Orchestrator
    'SurveillanceOrchestrator',
    'OrchestratorTarget',
    'SurveillancePolicy',
    'OrchestratorMetrics',
    'OrchestratorStatus',
    'ModuleStatus',
    'ModuleState'
]

class SurveillanceStatus(Enum):
    """Surveillance task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class SurveillancePriority(Enum):
    """Surveillance priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class SurveillanceTarget:
    """
Surveillance target definition."""
    target_id: str
    platform: str
    target_type: str  # channel, user, hashtag, keyword, url
    identifier: str  # channel_id, username, hashtag, keyword, url
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: SurveillancePriority = SurveillancePriority.NORMAL
    frequency: int = 3600  # seconds between checks
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None
    next_check: Optional[datetime] = None

@dataclass
class SurveillanceTask:
    """
Surveillance task execution unit."""
    task_id: str
    target: SurveillanceTarget
    status: SurveillanceStatus = SurveillanceStatus.PENDING
    scheduled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    results: Optional[Dict[str, Any]] = None

@dataclass
class SurveillanceMetrics:
    """
Surveillance system metrics."""
    total_targets: int = 0
    active_targets: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    violations_detected: int = 0
    content_items_processed: int = 0
    average_processing_time: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)

class SurveillanceEngine:
    """
    Professional surveillance coordination system.
    
    Features:
    - Multi-platform coordination
    - Intelligent task scheduling
    - Priority-based execution
    - Rate limiting coordination
    - Resource optimization
    - Real-time monitoring
    - Violation detection
    - Alert management
    - Performance tracking
    - Scalable architecture
    """
    
    def __init__(self):
        """
Initialize surveillance engine."""
        # Core managers
        self.rate_limiter = RateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session_manager = SessionManager(
            self.proxy_manager,
            self.user_agent_rotator,
            self.rate_limiter
        )
        
        # Platform crawlers
        self.crawlers = {
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler(),
            'tiktok': TikTokCrawler(),
            'twitter': TwitterCrawler(),
            'facebook': FacebookCrawler(),
            'spotify': SpotifyCrawler(),
            'generic': GenericCrawler()
        }
        
        # Surveillance state
        self.targets: Dict[str, SurveillanceTarget] = {}
        self.tasks: Dict[str, SurveillanceTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Set[str] = set()
        self.metrics = SurveillanceMetrics()
        
        # Configuration
        self.max_concurrent_tasks = 50
        self.task_timeout = 300  # 5 minutes
        self.cleanup_interval = 3600  # 1 hour
        self.metrics_update_interval = 60  # 1 minute
        
        # Callbacks
        self.violation_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self) -> None:
        """
Start background monitoring tasks."""
        asyncio.create_task(self._task_scheduler())
        asyncio.create_task(self._task_executor())
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._cleanup_task())
    
    async def add_target(
        self,
        platform: str,
        target_type: str,
        identifier: str,
        priority: SurveillancePriority = SurveillancePriority.NORMAL,
        frequency: int = 3600,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add surveillance target.
        
        Args:
            platform: Platform name (youtube, instagram, etc.)
            target_type: Type of target (channel, user, hashtag, etc.)
            identifier: Target identifier
            priority: Surveillance priority
            frequency: Check frequency in seconds
            metadata: Additional metadata
            
        Returns:
            Target ID
        """
        target_id = f"{platform}_{target_type}_{uuid.uuid4().hex[:8]}"
        
        target = SurveillanceTarget(
            target_id=target_id,
            platform=platform,
            target_type=target_type,
            identifier=identifier,
            metadata=metadata or {},
            priority=priority,
            frequency=frequency
        )
        
        # Calculate next check time
        target.next_check = datetime.now() + timedelta(seconds=frequency)
        
        self.targets[target_id] = target
        
        logger.info(
            f"Added surveillance target: {platform}/{target_type}/{identifier} "
            f"(priority: {priority.name}, frequency: {frequency}s)"
        )
        
        return target_id
    
    async def remove_target(self, target_id: str) -> bool:
        """Remove surveillance target."""
        if target_id in self.targets:
            target = self.targets[target_id]
            target.enabled = False
            
            # Cancel any pending tasks for this target
            pending_tasks = [
                task for task in self.tasks.values()
                if task.target.target_id == target_id and task.status == SurveillanceStatus.PENDING
            ]
            
            for task in pending_tasks:
                task.status = SurveillanceStatus.CANCELLED
            
            logger.info(f"Removed surveillance target: {target_id}")
            return True
        
        return False
    
    async def update_target_frequency(self, target_id: str, frequency: int) -> bool:
        """Update target check frequency."""
        if target_id in self.targets:
            target = self.targets[target_id]
            target.frequency = frequency
            target.next_check = datetime.now() + timedelta(seconds=frequency)
            
            logger.info(f"Updated target {target_id} frequency to {frequency}s")
            return True
        
        return False
    
    async def pause_target(self, target_id: str) -> bool:
        """Pause surveillance for target."""
        if target_id in self.targets:
            self.targets[target_id].enabled = False
            logger.info(f"Paused surveillance for target: {target_id}")
            return True
        
        return False
    
    async def resume_target(self, target_id: str) -> bool:
        """Resume surveillance for target."""
        if target_id in self.targets:
            target = self.targets[target_id]
            target.enabled = True
            target.next_check = datetime.now() + timedelta(seconds=target.frequency)
            
            logger.info(f"Resumed surveillance for target: {target_id}")
            return True
        
        return False
    
    async def _task_scheduler(self) -> None:
        """Background task scheduler."""
        while True:
            try:
                current_time = datetime.now()
                
                # Find targets that need checking
                for target in self.targets.values():
                    if not target.enabled:
                        continue
                    
                    if target.next_check and current_time >= target.next_check:
                        # Create surveillance task
                        task = SurveillanceTask(
                            task_id=f"task_{uuid.uuid4().hex[:8]}",
                            target=target,
                            scheduled_at=current_time
                        )
                        
                        self.tasks[task.task_id] = task
                        await self.task_queue.put(task.task_id)
                        
                        # Schedule next check
                        target.next_check = current_time + timedelta(seconds=target.frequency)
                        target.last_checked = current_time
                
                # Sleep before next scheduling cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(30)
    
    async def _task_executor(self) -> None:
        """Background task executor."""
        while True:
            try:
                # Limit concurrent tasks
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(1)
                    continue
                
                # Get next task
                try:
                    task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                if task_id not in self.tasks:
                    continue
                
                task = self.tasks[task_id]
                
                # Execute task
                asyncio.create_task(self._execute_task(task))
                
            except Exception as e:
                logger.error(f"Task executor error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: SurveillanceTask) -> None:
        """Execute surveillance task."""
        task_id = task.task_id
        
        try:
            self.running_tasks.add(task_id)
            task.status = SurveillanceStatus.RUNNING
            task.started_at = datetime.now()
            
            logger.debug(f"Executing task {task_id} for {task.target.platform}/{task.target.identifier}")
            
            # Get appropriate crawler
            crawler = self.crawlers.get(task.target.platform)
            if not crawler:
                raise ValueError(f"No crawler available for platform: {task.target.platform}")
            
            # Execute based on target type
            results = await self._execute_target_surveillance(task.target, crawler)
            
            # Process results
            if results:
                await self._process_surveillance_results(task.target, results)
                task.results = results
            
            task.status = SurveillanceStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Call completion callbacks
            for callback in self.completion_callbacks:
                try:
                    await callback(task)
                except Exception as e:
                    logger.error(f"Completion callback error: {e}")
            
            logger.debug(f"Task {task_id} completed successfully")
            
        except Exception as e:
            task.error_message = str(e)
            task.status = SurveillanceStatus.FAILED
            task.completed_at = datetime.now()
            
            # Handle retries
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = SurveillanceStatus.PENDING
                task.scheduled_at = datetime.now() + timedelta(minutes=5)  # Retry in 5 minutes
                await self.task_queue.put(task_id)
                
                logger.warning(f"Task {task_id} failed, retry {task.retry_count}/{task.max_retries}: {e}")
            else:
                logger.error(f"Task {task_id} failed permanently: {e}")
                
                # Call error callbacks
                for callback in self.error_callbacks:
                    try:
                        await callback(task, e)
                    except Exception as cb_error:
                        logger.error(f"Error callback error: {cb_error}")
        
        finally:
            self.running_tasks.discard(task_id)
    
    async def _execute_target_surveillance(
        self,
        target: SurveillanceTarget,
        crawler
    ) -> Optional[Dict[str, Any]]:
        """Execute surveillance for specific target."""
        platform = target.platform
        target_type = target.target_type
        identifier = target.identifier
        
        try:
            if platform == 'youtube':
                if target_type == 'channel':
                    return await crawler.monitor_channel(identifier)
                elif target_type == 'video':
                    return await crawler.get_video_details(identifier)
                elif target_type == 'search':
                    return await crawler.search_videos(identifier, max_results=50)
                    
            elif platform == 'instagram':
                if target_type == 'user':
                    return await crawler.get_user_profile(identifier)
                elif target_type == 'hashtag':
                    return await crawler.search_hashtag(identifier, limit=50)
                    
            elif platform == 'tiktok':
                if target_type == 'user':
                    return await crawler.get_user_profile(identifier)
                elif target_type == 'hashtag':
                    return await crawler.search_hashtag(identifier, limit=50)
                elif target_type == 'search':
                    return await crawler.search_videos(identifier, limit=50)
                    
            elif platform == 'twitter':
                if target_type == 'user':
                    return await crawler.get_user_timeline(identifier, max_results=50)
                elif target_type == 'search':
                    return await crawler.search_tweets(identifier, max_results=50)
                elif target_type == 'hashtag':
                    return await crawler.search_tweets(f"#{identifier}", max_results=50)
                    
            elif platform == 'facebook':
                if target_type == 'page':
                    return await crawler.get_page_posts(identifier, limit=50)
                elif target_type == 'search':
                    return await crawler.search_pages(identifier, limit=50)
                    
            elif platform == 'spotify':
                if target_type == 'artist':
                    return await crawler.monitor_artist(identifier)
                elif target_type == 'search':
                    return await crawler.search_tracks(identifier, limit=50)
                    
            elif platform == 'generic':
                if target_type == 'url':
                    return await crawler.crawl_url(identifier)
            
            logger.warning(f"Unknown target type: {platform}/{target_type}")
            return None
            
        except Exception as e:
            logger.error(f"Surveillance execution error for {platform}/{target_type}/{identifier}: {e}")
            raise
    
    async def _process_surveillance_results(
        self,
        target: SurveillanceTarget,
        results: Dict[str, Any]
    ) -> None:
        """Process surveillance results and detect violations."""
        try:
            # Extract content items
            content_items = []
            
            if isinstance(results, dict):
                if 'videos' in results:
                    content_items.extend(results['videos'])
                elif 'posts' in results:
                    content_items.extend(results['posts'])
                elif 'tweets' in results:
                    content_items.extend(results['tweets'])
                elif 'tracks' in results:
                    content_items.extend(results['tracks'])
                elif 'content' in results:
                    content_items.append(results)
            elif isinstance(results, list):
                content_items = results
            
            # Update metrics
            self.metrics.content_items_processed += len(content_items)
            
            # Check for violations
            violations = await self._detect_violations(target, content_items)
            
            if violations:
                self.metrics.violations_detected += len(violations)
                
                # Call violation callbacks
                for callback in self.violation_callbacks:
                    try:
                        await callback(target, violations)
                    except Exception as e:
                        logger.error(f"Violation callback error: {e}")
                        
                logger.warning(f"Detected {len(violations)} violations for target {target.target_id}")
            
        except Exception as e:
            logger.error(f"Results processing error: {e}")
    
    async def _detect_violations(
        self,
        target: SurveillanceTarget,
        content_items: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect content violations."""
        violations = []
        
        # This would integrate with the content analysis module
        # For now, implement basic keyword detection
        violation_keywords = target.metadata.get('violation_keywords', [])
        
        if not violation_keywords:
            return violations
        
        for item in content_items:
            item_text = ""
            
            # Extract text from item
            if 'title' in item:
                item_text += item['title'] + " "
            if 'description' in item:
                item_text += item['description'] + " "
            if 'content' in item:
                item_text += item['content'] + " "
            if 'text' in item:
                item_text += item['text'] + " "
            
            item_text = item_text.lower()
            
            # Check for violations
            found_keywords = [kw for kw in violation_keywords if kw.lower() in item_text]
            
            if found_keywords:
                violation = {
                    'target_id': target.target_id,
                    'platform': target.platform,
                    'item_id': item.get('id', ''),
                    'item_url': item.get('url', ''),
                    'violation_type': 'keyword_match',
                    'detected_keywords': found_keywords,
                    'confidence': len(found_keywords) / len(violation_keywords),
                    'detected_at': datetime.now(),
                    'item_data': item
                }
                violations.append(violation)
        
        return violations
    
    async def _metrics_updater(self) -> None:
        """Background metrics updater."""
        while True:
            try:
                await asyncio.sleep(self.metrics_update_interval)
                
                # Update metrics
                self.metrics.total_targets = len(self.targets)
                self.metrics.active_targets = len([t for t in self.targets.values() if t.enabled])
                self.metrics.pending_tasks = len([t for t in self.tasks.values() if t.status == SurveillanceStatus.PENDING])
                self.metrics.running_tasks = len(self.running_tasks)
                self.metrics.completed_tasks = len([t for t in self.tasks.values() if t.status == SurveillanceStatus.COMPLETED])
                self.metrics.failed_tasks = len([t for t in self.tasks.values() if t.status == SurveillanceStatus.FAILED])
                
                # Calculate average processing time
                completed_tasks = [t for t in self.tasks.values() if t.status == SurveillanceStatus.COMPLETED and t.started_at and t.completed_at]
                if completed_tasks:
                    processing_times = [(t.completed_at - t.started_at).total_seconds() for t in completed_tasks]
                    self.metrics.average_processing_time = sum(processing_times) / len(processing_times)
                
                self.metrics.last_update = datetime.now()
                
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
    
    async def _cleanup_task(self) -> None:
        """Background cleanup task."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean old completed/failed tasks
                cutoff_time = datetime.now() - timedelta(hours=24)
                tasks_to_remove = []
                
                for task_id, task in self.tasks.items():
                    if (task.status in [SurveillanceStatus.COMPLETED, SurveillanceStatus.FAILED, SurveillanceStatus.CANCELLED] 
                        and task.completed_at and task.completed_at < cutoff_time):
                        tasks_to_remove.append(task_id)
                
                for task_id in tasks_to_remove:
                    del self.tasks[task_id]
                
                if tasks_to_remove:
                    logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
    
    def add_violation_callback(self, callback: Callable) -> None:
        """Add violation detection callback."""
        self.violation_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable) -> None:
        """
Add task completion callback."""
        self.completion_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable) -> None:
        """
Add error callback."""
        self.error_callbacks.append(callback)
    
    def get_metrics(self) -> SurveillanceMetrics:
        """
Get current surveillance metrics."""
        return self.metrics
    
    def get_target_status(self, target_id: str) -> Optional[Dict]:
        """
Get status for specific target."""
        target = self.targets.get(target_id)
        if not target:
            return None
        
        # Get recent tasks for this target
        recent_tasks = [
            task for task in self.tasks.values()
            if task.target.target_id == target_id
        ]
        
        # Sort by creation time
        recent_tasks.sort(key=lambda t: t.scheduled_at, reverse=True)
        
        last_task = recent_tasks[0] if recent_tasks else None
        
        return {
            'target_id': target_id,
            'platform': target.platform,
            'target_type': target.target_type,
            'identifier': target.identifier,
            'enabled': target.enabled,
            'priority': target.priority.name,
            'frequency': target.frequency,
            'last_checked': target.last_checked,
            'next_check': target.next_check,
            'last_task_status': last_task.status.value if last_task else None,
            'last_task_error': last_task.error_message if last_task else None,
            'total_tasks': len(recent_tasks),
            'failed_tasks': len([t for t in recent_tasks if t.status == SurveillanceStatus.FAILED])
        }
    
    def get_all_targets_status(self) -> List[Dict]:
        """
Get status for all targets."""
        return [self.get_target_status(target_id) for target_id in self.targets.keys()]
    
    async def force_target_check(self, target_id: str) -> bool:
        """
Force immediate check for target."""
        target = self.targets.get(target_id)
        if not target or not target.enabled:
            return False
        
        # Create immediate task
        task = SurveillanceTask(
            task_id=f"force_task_{uuid.uuid4().hex[:8]}",
            target=target,
            scheduled_at=datetime.now()
        )
        
        self.tasks[task.task_id] = task
        await self.task_queue.put(task.task_id)
        
        logger.info(f"Forced check for target: {target_id}")
        return True
    
    async def shutdown(self) -> None:
        """Shutdown surveillance engine gracefully."""
        logger.info("Shutting down surveillance engine...")
        
        # Stop accepting new tasks
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Wait for running tasks to complete (with timeout)
        max_wait = 30  # seconds
        start_time = datetime.now()
        
        while self.running_tasks and (datetime.now() - start_time).total_seconds() < max_wait:
            await asyncio.sleep(1)
        
        # Close session manager
        await self.session_manager.close_all_sessions()
        
        logger.info("Surveillance engine shutdown complete")
