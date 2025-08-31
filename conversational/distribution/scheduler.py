"""Content Distribution Scheduler

Enterprise-grade intelligent scheduling system for multi-platform content distribution.
Provides AI-powered optimal timing, queue management, and automated publishing.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import heapq
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import aiohttp
import aioredis
from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from pydantic import BaseModel, Field, validator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....core.exceptions import SchedulingError, APIError, ValidationError
from ....utils.encryption import encrypt_data, decrypt_data
from ....utils.monitoring import MetricsCollector, track_performance
from ....utils.timezone import TimezoneManager
from ....models.content import ContentModel, ContentScheduleModel
from ....models.user import UserModel
from ....models.analytics import PlatformPerformanceModel, AudienceInsightsModel
from .platform_manager import PlatformType
from .optimization_engine import OptimizationEngine


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.scheduler")


class SchedulingStrategy(str, Enum):
    """Content scheduling strategies"""    IMMEDIATE = "immediate"
    OPTIMAL_TIMING = "optimal_timing"
    STAGGERED = "staggered"
    BATCH = "batch"
    DRIP_FEED = "drip_feed"
    EVENT_DRIVEN = "event_driven"
    COMPETITOR_BASED = "competitor_based"
    AUDIENCE_ACTIVITY = "audience_activity"
    CROSS_PLATFORM = "cross_platform"
    SEASONAL = "seasonal"
    VIRAL_WINDOW = "viral_window"
    AB_TEST = "ab_test"


class ScheduleStatus(str, Enum):
    """Schedule status tracking"""    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"
    DELAYED = "delayed"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Task priority levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


class TimeSlotType(str, Enum):
    """Time slot optimization types"""    PEAK_ENGAGEMENT = "peak_engagement"
    LOW_COMPETITION = "low_competition"
    OPTIMAL_REACH = "optimal_reach"
    VIRAL_POTENTIAL = "viral_potential"
    COST_EFFECTIVE = "cost_effective"
    AUDIENCE_ONLINE = "audience_online"
    TRENDING_WINDOW = "trending_window"


@dataclass
class OptimalTimeSlot:
    """Optimal time slot for content publishing"""    platform: PlatformType
    datetime: datetime
    confidence_score: float
    expected_engagement: float
    expected_reach: int
    competition_level: str  # low, medium, high
    audience_activity: float
    viral_potential: float
    cost_effectiveness: float
    reasoning: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduleTask:
    """Individual scheduling task"""    id: str
    user_id: int
    content_id: int
    platform: PlatformType
    scheduled_time: datetime
    strategy: SchedulingStrategy
    priority: Priority
    status: ScheduleStatus
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))


@dataclass
class BatchSchedule:
    """Batch scheduling configuration"""    name: str
    user_id: int
    content_ids: List[int]
    platforms: List[PlatformType]
    strategy: SchedulingStrategy
    start_time: datetime
    end_time: Optional[datetime]
    interval: timedelta
    priority: Priority
    max_concurrent: int = 3
    retry_failed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class SchedulingConfig(BaseModel):
    """Scheduling configuration model"""    user_id: int
    default_strategy: SchedulingStrategy = SchedulingStrategy.OPTIMAL_TIMING
    timezone: str = "UTC"
    working_hours: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            "monday": (9, 17),
            "tuesday": (9, 17),
            "wednesday": (9, 17),
            "thursday": (9, 17),
            "friday": (9, 17),
            "saturday": (10, 16),
            "sunday": (12, 18)
        }
    )
    blackout_periods: List[Tuple[datetime, datetime]] = Field(default_factory=list)
    platform_preferences: Dict[PlatformType, Dict[str, Any]] = Field(default_factory=dict)
    max_posts_per_day: Dict[PlatformType, int] = Field(default_factory=dict)
    min_interval_between_posts: Dict[PlatformType, timedelta] = Field(default_factory=dict)
    enable_cross_promotion: bool = True
    enable_ab_testing: bool = True
    
    class Config:
        arbitrary_types_allowed = True


class ContentDistributionScheduler:
    """    Enterprise-grade intelligent content distribution scheduler with AI optimization.
    
    Features:
    - AI-powered optimal timing prediction
    - Multi-platform queue management
    - Real-time audience activity analysis
    - Competitor scheduling intelligence
    - Automated retry and error handling
    - Cross-platform coordination
    - Batch and drip-feed scheduling
    - A/B testing for timing optimization
    - Dynamic priority adjustment
    - Performance feedback learning
    - Seasonal and trend-based optimization
    - Compliance and rate limiting
    """    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self.celery_app = None
        self.scheduler = AsyncIOScheduler()
        self.optimization_engine = OptimizationEngine(db)
        self.timezone_manager = TimezoneManager()
        
        # Load ML models for timing prediction
        self.timing_models = self._load_timing_models()
        self.engagement_models = self._load_engagement_models()
        
        # Initialize queue systems
        self.priority_queues = self._initialize_priority_queues()
        self.platform_queues = self._initialize_platform_queues()
        
        # Scheduling state
        self.active_tasks: Dict[str, ScheduleTask] = {}
        self.batch_schedules: Dict[str, BatchSchedule] = {}
        self.user_configs: Dict[int, SchedulingConfig] = {}
        
        # Rate limiting and compliance
        self.rate_limiters = self._initialize_rate_limiters()
        self.compliance_rules = self._initialize_compliance_rules()
        
        # Performance tracking
        self.performance_tracker = self._initialize_performance_tracker()
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def __aenter__(self):
        """Async context manager entry"""        self.redis_client = await aioredis.from_url(settings.REDIS_URL)
        self.celery_app = Celery('content_scheduler', broker=settings.CELERY_BROKER_URL)
        self.scheduler.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        if self.scheduler.running:
            self.scheduler.shutdown()
        if self.redis_client:
            await self.redis_client.close()
        self.executor.shutdown(wait=True)
    
    def _load_timing_models(self) -> Dict[str, Any]:
        """Load ML models for optimal timing prediction"""        models = {}
        
        try:
            # Platform-specific timing models
            for platform in PlatformType:
                models[f"{platform.value}_timing"] = joblib.load(
                    f"models/timing_{platform.value}_predictor.pkl"
                )
            
            # General timing models
            models["engagement_predictor"] = joblib.load("models/engagement_timing_predictor.pkl")
            models["reach_predictor"] = joblib.load("models/reach_timing_predictor.pkl")
            models["viral_predictor"] = joblib.load("models/viral_timing_predictor.pkl")
            models["competition_analyzer"] = joblib.load("models/competition_timing_analyzer.pkl")
            models["feature_scaler"] = joblib.load("models/timing_scaler.pkl")
            
            logger.info("Successfully loaded timing ML models")
            
        except FileNotFoundError:
            logger.warning("Timing ML models not found, using heuristic algorithms")
            models = self._create_fallback_timing_models()
        
        return models
    
    def _create_fallback_timing_models(self) -> Dict[str, Any]:
        """Create fallback timing models"""        return {
            "engagement_predictor": RandomForestRegressor(n_estimators=100, random_state=42),
            "reach_predictor": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "viral_predictor": RandomForestRegressor(n_estimators=50, random_state=42),
            "competition_analyzer": KMeans(n_clusters=5, random_state=42),
            "feature_scaler": StandardScaler()
        }
    
    def _load_engagement_models(self) -> Dict[str, Any]:
        """Load engagement prediction models"""        models = {}
        
        try:
            models["hourly_engagement"] = joblib.load("models/hourly_engagement_predictor.pkl")
            models["daily_engagement"] = joblib.load("models/daily_engagement_predictor.pkl")
            models["audience_activity"] = joblib.load("models/audience_activity_predictor.pkl")
            models["cross_platform_impact"] = joblib.load("models/cross_platform_impact.pkl")
            
        except FileNotFoundError:
            logger.warning("Engagement models not found, using statistical methods")
            models = self._create_fallback_engagement_models()
        
        return models
    
    def _create_fallback_engagement_models(self) -> Dict[str, Any]:
        """Create fallback engagement models"""        return {
            "hourly_engagement": RandomForestRegressor(n_estimators=50, random_state=42),
            "daily_engagement": GradientBoostingRegressor(n_estimators=50, random_state=42),
            "audience_activity": RandomForestRegressor(n_estimators=30, random_state=42),
            "cross_platform_impact": RandomForestRegressor(n_estimators=30, random_state=42)
        }
    
    def _initialize_priority_queues(self) -> Dict[Priority, deque]:
        """Initialize priority-based task queues"""        return {
            Priority.CRITICAL: deque(),
            Priority.HIGH: deque(),
            Priority.MEDIUM: deque(),
            Priority.LOW: deque(),
            Priority.BACKGROUND: deque()
        }
    
    def _initialize_platform_queues(self) -> Dict[PlatformType, deque]:
        """Initialize platform-specific task queues"""        return {platform: deque() for platform in PlatformType}
    
    def _initialize_rate_limiters(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize rate limiting configurations"""        return {
            PlatformType.YOUTUBE: {
                "requests_per_minute": 100,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
                "quota_reset_time": "00:00",
                "burst_limit": 20
            },
            PlatformType.INSTAGRAM: {
                "requests_per_minute": 200,
                "requests_per_hour": 5000,
                "requests_per_day": 50000,
                "quota_reset_time": "00:00",
                "burst_limit": 50
            },
            PlatformType.TIKTOK: {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
                "quota_reset_time": "00:00",
                "burst_limit": 15
            },
            PlatformType.TWITTER: {
                "requests_per_minute": 300,
                "requests_per_hour": 15000,
                "requests_per_day": 100000,
                "quota_reset_time": "00:00",
                "burst_limit": 100
            },
            PlatformType.LINKEDIN: {
                "requests_per_minute": 100,
                "requests_per_hour": 2000,
                "requests_per_day": 20000,
                "quota_reset_time": "00:00",
                "burst_limit": 25
            }
        }
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance and content policy rules"""        return {
            "content_approval_required": ["sensitive", "promotional", "political"],
            "restricted_times": {
                "political_content": ["election_periods", "voting_days"],
                "promotional_content": ["sundays", "holidays"],
                "sensitive_content": ["work_hours"]
            },
            "geographic_restrictions": {
                "political_content": ["certain_countries"],
                "gambling_content": ["restricted_regions"],
                "financial_content": ["regulated_markets"]
            },
            "age_restrictions": {
                "mature_content": "18+",
                "gambling_content": "21+",
                "financial_content": "18+"
            },
            "platform_specific_rules": {
                PlatformType.YOUTUBE: ["community_guidelines", "copyright_check"],
                PlatformType.INSTAGRAM: ["hashtag_limits", "story_restrictions"],
                PlatformType.TIKTOK: ["music_licensing", "region_blocks"],
                PlatformType.TWITTER: ["character_limits", "media_formats"],
                PlatformType.LINKEDIN: ["professional_standards", "spam_prevention"]
            }
        }
    
    def _initialize_performance_tracker(self) -> Dict[str, Any]:
        """Initialize performance tracking system"""        return {
            "metrics": {
                "scheduling_accuracy": 0.0,
                "optimal_timing_hits": 0.0,
                "cross_platform_sync": 0.0,
                "retry_rate": 0.0,
                "user_satisfaction": 0.0
            },
            "benchmarks": {
                "min_accuracy": 0.85,
                "target_timing_hits": 0.90,
                "max_retry_rate": 0.05,
                "min_satisfaction": 0.80
            },
            "tracking_windows": {
                "realtime": timedelta(minutes=15),
                "hourly": timedelta(hours=1),
                "daily": timedelta(days=1),
                "weekly": timedelta(weeks=1)
            }
        }
    
    @track_performance("scheduler.schedule_content")
    async def schedule_content(
        self,
        user_id: int,
        content_id: int,
        platforms: List[PlatformType],
        strategy: SchedulingStrategy = SchedulingStrategy.OPTIMAL_TIMING,
        target_time: Optional[datetime] = None,
        priority: Priority = Priority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ScheduleTask]:
        """        Schedule content for distribution across multiple platforms with intelligent timing.
        
        Args:
            user_id: User scheduling the content
            content_id: Content to be scheduled
            platforms: Target platforms for distribution
            strategy: Scheduling strategy to use
            target_time: Specific target time (optional)
            priority: Task priority level
            metadata: Additional scheduling metadata
            
        Returns:
            List of created schedule tasks
        """        
        with metrics.timer("scheduler.content_scheduling"):
            try:
                # Validate inputs
                await self._validate_scheduling_request(user_id, content_id, platforms)
                
                # Get user scheduling configuration
                config = await self._get_user_config(user_id)
                
                # Get content details
                content = await self._get_content_details(content_id)
                
                # Generate optimal time slots for each platform
                optimal_slots = await self._generate_optimal_time_slots(
                    user_id, content, platforms, strategy, target_time, config
                )
                
                # Create schedule tasks
                tasks = []
                for platform, time_slot in optimal_slots.items():
                    task = ScheduleTask(
                        id=f"{user_id}_{content_id}_{platform.value}_{int(time_slot.datetime.timestamp())}",
                        user_id=user_id,
                        content_id=content_id,
                        platform=platform,
                        scheduled_time=time_slot.datetime,
                        strategy=strategy,
                        priority=priority,
                        status=ScheduleStatus.PENDING,
                        metadata={
                            **(metadata or {}),
                            "optimal_slot": time_slot,
                            "config_used": config.dict()
                        }
                    )
                    tasks.append(task)
                
                # Validate scheduling constraints
                await self._validate_scheduling_constraints(tasks, config)
                
                # Add tasks to appropriate queues
                await self._enqueue_tasks(tasks)
                
                # Store tasks in database
                await self._store_schedule_tasks(tasks)
                
                # Set up automated execution
                await self._setup_task_execution(tasks)
                
                # Update performance metrics
                await self._update_scheduling_metrics(tasks)
                
                metrics.increment("scheduler.content.scheduled", tags={
                    "strategy": strategy.value,
                    "platforms": len(platforms),
                    "priority": priority.value
                })
                
                logger.info(f"Successfully scheduled content {content_id} for user {user_id} on {len(platforms)} platforms")
                
                return tasks
                
            except Exception as e:
                metrics.increment("scheduler.content.error")
                logger.error(f"Failed to schedule content {content_id} for user {user_id}: {e}")
                raise SchedulingError(f"Content scheduling failed: {e}")
    
    async def _validate_scheduling_request(
        self,
        user_id: int,
        content_id: int,
        platforms: List[PlatformType]
    ) -> None:
        """Validate scheduling request parameters"""        
        # Check user exists and has scheduling permissions
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise ValidationError(f"User {user_id} not found")
        
        if not getattr(user, 'scheduling_enabled', True):
            raise ValidationError("Scheduling not enabled for this user")
        
        # Check content exists and user has access
        content = self.db.query(ContentModel).filter(
            ContentModel.id == content_id,
            ContentModel.user_id == user_id
        ).first()
        if not content:
            raise ValidationError(f"Content {content_id} not found or access denied")
        
        # Validate platforms
        if not platforms:
            raise ValidationError("At least one platform must be specified")
        
        for platform in platforms:
            if platform not in PlatformType:
                raise ValidationError(f"Invalid platform: {platform}")
    
    async def _get_user_config(self, user_id: int) -> SchedulingConfig:
        """Get or create user scheduling configuration"""        
        if user_id in self.user_configs:
            return self.user_configs[user_id]
        
        # Try to load from database
        stored_config = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if stored_config and hasattr(stored_config, 'scheduling_config'):
            config = SchedulingConfig(**stored_config.scheduling_config)
        else:
            # Create default configuration
            config = SchedulingConfig(user_id=user_id)
        
        # Cache configuration
        self.user_configs[user_id] = config
        
        return config
    
    async def _get_content_details(self, content_id: int) -> ContentModel:
        """Get detailed content information"""        content = self.db.query(ContentModel).filter(ContentModel.id == content_id).first()
        if not content:
            raise ValidationError(f"Content {content_id} not found")
        
        return content
    
    async def _generate_optimal_time_slots(
        self,
        user_id: int,
        content: ContentModel,
        platforms: List[PlatformType],
        strategy: SchedulingStrategy,
        target_time: Optional[datetime],
        config: SchedulingConfig
    ) -> Dict[PlatformType, OptimalTimeSlot]:
        """Generate optimal time slots for each platform using AI prediction"""        
        optimal_slots = {}
        
        # Process each platform
        for platform in platforms:
            if strategy == SchedulingStrategy.IMMEDIATE:
                slot = await self._create_immediate_slot(platform, content)
            elif strategy == SchedulingStrategy.OPTIMAL_TIMING:
                slot = await self._predict_optimal_timing(user_id, content, platform, config)
            elif strategy == SchedulingStrategy.AUDIENCE_ACTIVITY:
                slot = await self._optimize_for_audience_activity(user_id, platform, config)
            elif strategy == SchedulingStrategy.COMPETITOR_BASED:
                slot = await self._analyze_competitor_timing(user_id, platform, content)
            elif strategy == SchedulingStrategy.VIRAL_WINDOW:
                slot = await self._identify_viral_window(user_id, platform, content)
            elif strategy == SchedulingStrategy.CROSS_PLATFORM:
                slot = await self._optimize_cross_platform_timing(user_id, content, platform, platforms)
            else:
                # Fallback to optimal timing
                slot = await self._predict_optimal_timing(user_id, content, platform, config)
            
            # Apply target time if specified
            if target_time:
                slot = await self._adjust_for_target_time(slot, target_time, config)
            
            optimal_slots[platform] = slot
        
        # Coordinate cross-platform timing
        if strategy == SchedulingStrategy.CROSS_PLATFORM:
            optimal_slots = await self._coordinate_cross_platform_timing(optimal_slots, config)
        
        return optimal_slots

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

import pytz
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from celery import current_app
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from ....core.database import get_db
from ....core.config import settings
from ....models.content import ContentModel
from ....models.user import UserModel
from ....models.schedule import ScheduledPostModel, ScheduleStatus
from .platform_manager import PlatformType, DistributionRequest
from .strategy_engine import DistributionStrategyEngine


logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Types of scheduling strategies"""    IMMEDIATE = "immediate"
    OPTIMAL_TIME = "optimal_time"
    SPECIFIC_TIME = "specific_time"
    RECURRING = "recurring"
    BATCH_RELEASE = "batch_release"
    DRIP_CAMPAIGN = "drip_campaign"


class RecurrencePattern(str, Enum):
    """Recurrence patterns for scheduled content"""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class TimeZonePreference(str, Enum):
    """Common timezone preferences"""    UTC = "UTC"
    EST = "America/New_York"
    PST = "America/Los_Angeles"
    GMT = "Europe/London"
    CET = "Europe/Paris"
    JST = "Asia/Tokyo"
    LOCAL = "local"


@dataclass
class OptimalTimeSlot:
    """Optimal posting time slot"""    datetime: datetime
    platform: PlatformType
    expected_reach: int
    expected_engagement: float
    confidence_score: float
    reason: str


@dataclass
class ScheduleConflict:
    """Schedule conflict information"""    existing_post_id: int
    conflicting_time: datetime
    platform: PlatformType
    severity: str  # low, medium, high
    suggested_alternative: Optional[datetime] = None


class ScheduleRequest(BaseModel):
    """Content scheduling request"""    user_id: int
    content_id: int
    schedule_type: ScheduleType
    platforms: List[PlatformType]
    
    # Specific time scheduling
    target_datetime: Optional[datetime] = None
    timezone: TimeZonePreference = TimeZonePreference.UTC
    
    # Recurring scheduling
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_count: Optional[int] = None
    end_date: Optional[datetime] = None
    
    # Batch/drip campaign
    batch_interval: Optional[int] = None  # Minutes between posts
    campaign_duration: Optional[int] = None  # Days
    
    # Optimization preferences
    optimize_for_engagement: bool = True
    avoid_conflicts: bool = True
    respect_platform_limits: bool = True
    custom_message: Optional[str] = None


class ScheduleResult(BaseModel):
    """Scheduling operation result"""    schedule_id: str
    success: bool
    scheduled_posts: List[Dict[str, Any]] = Field(default_factory=list)
    conflicts: List[ScheduleConflict] = Field(default_factory=list)
    optimal_times: List[OptimalTimeSlot] = Field(default_factory=list)
    error_message: Optional[str] = None
    total_posts_scheduled: int = 0


class ContentScheduler:
    """    Intelligent content scheduling system with AI-powered optimization
    """    
    def __init__(self, db: Session):
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.strategy_engine = DistributionStrategyEngine(db)
        self.timezone_cache: Dict[int, str] = {}
        self.platform_limits = self._initialize_platform_limits()
        
        # Start the scheduler
        if not self.scheduler.running:
            self.scheduler.start()
    
    def _initialize_platform_limits(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Initialize platform-specific posting limits and guidelines"""        return {
            PlatformType.YOUTUBE: {
                "daily_limit": 10,
                "hourly_limit": 3,
                "min_interval": 30,  # minutes
                "optimal_frequency": "daily",
                "avoid_hours": [0, 1, 2, 3, 4, 5, 6]  # Late night/early morning
            },
            PlatformType.INSTAGRAM: {
                "daily_limit": 5,
                "hourly_limit": 2,
                "min_interval": 60,
                "optimal_frequency": "1-2 times daily",
                "stories_limit": 20,
                "reels_limit": 3
            },
            PlatformType.TIKTOK: {
                "daily_limit": 10,
                "hourly_limit": 4,
                "min_interval": 15,
                "optimal_frequency": "3-5 times daily",
                "trending_hours": [19, 20, 21, 22]
            },
            PlatformType.TWITTER: {
                "daily_limit": 50,
                "hourly_limit": 15,
                "min_interval": 5,
                "optimal_frequency": "multiple times daily",
                "thread_spacing": 2  # minutes between thread posts
            },
            PlatformType.SPOTIFY: {
                "weekly_limit": 7,
                "daily_limit": 1,
                "min_interval": 1440,  # 24 hours
                "optimal_frequency": "weekly",
                "episode_spacing": 2  # days minimum
            },
            PlatformType.LINKEDIN: {
                "daily_limit": 3,
                "hourly_limit": 1,
                "min_interval": 120,
                "optimal_frequency": "daily",
                "business_hours_only": True
            }
        }
    
    async def schedule_content(self, request: ScheduleRequest) -> ScheduleResult:
        """        Schedule content distribution with AI optimization
        
        Args:
            request: Scheduling request with parameters
            
        Returns:
            Scheduling result with created schedules
        """        try:
            # Validate request
            await self._validate_schedule_request(request)
            
            # Get user timezone
            user_timezone = await self._get_user_timezone(request.user_id)
            
            # Generate optimal timing recommendations
            if request.schedule_type == ScheduleType.OPTIMAL_TIME:
                optimal_times = await self._find_optimal_times(request, user_timezone)
            else:
                optimal_times = []
            
            # Check for schedule conflicts
            conflicts = await self._check_schedule_conflicts(request)
            
            # Create scheduled posts
            scheduled_posts = await self._create_scheduled_posts(
                request, optimal_times, user_timezone
            )
            
            # Store in database
            schedule_id = await self._save_schedule(request, scheduled_posts)
            
            return ScheduleResult(
                schedule_id=schedule_id,
                success=True,
                scheduled_posts=scheduled_posts,
                conflicts=conflicts,
                optimal_times=optimal_times,
                total_posts_scheduled=len(scheduled_posts)
            )
            
        except Exception as e:
            logger.error(f"Content scheduling failed: {e}")
            return ScheduleResult(
                schedule_id="",
                success=False,
                error_message=str(e)
            )
    
    async def _validate_schedule_request(self, request: ScheduleRequest) -> None:
        """Validate scheduling request parameters"""        # Check user exists
        user = self.db.query(UserModel).filter(UserModel.id == request.user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check content exists
        content = self.db.query(ContentModel).filter(
            ContentModel.id == request.content_id,
            ContentModel.user_id == request.user_id
        ).first()
        if not content:
            raise ValueError("Content not found or access denied")
        
        # Validate platforms
        if not request.platforms:
            raise ValueError("At least one platform must be specified")
        
        # Validate specific time scheduling
        if request.schedule_type == ScheduleType.SPECIFIC_TIME:
            if not request.target_datetime:
                raise ValueError("Target datetime required for specific time scheduling")
            
            if request.target_datetime <= datetime.utcnow():
                raise ValueError("Target datetime must be in the future")
        
        # Validate recurring scheduling
        if request.schedule_type == ScheduleType.RECURRING:
            if not request.recurrence_pattern:
                raise ValueError("Recurrence pattern required for recurring scheduling")
            
            if request.recurrence_count and request.recurrence_count < 1:
                raise ValueError("Recurrence count must be positive")
        
        # Validate batch/drip campaign
        if request.schedule_type in [ScheduleType.BATCH_RELEASE, ScheduleType.DRIP_CAMPAIGN]:
            if not request.batch_interval or request.batch_interval < 5:
                raise ValueError("Batch interval must be at least 5 minutes")
    
    async def _get_user_timezone(self, user_id: int) -> str:
        """Get user's preferred timezone"""        if user_id in self.timezone_cache:
            return self.timezone_cache[user_id]
        
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        timezone = "UTC"  # Default
        
        if user and user.settings:
            timezone = user.settings.get("timezone", "UTC")
        
        self.timezone_cache[user_id] = timezone
        return timezone
    
    async def _find_optimal_times(
        self,
        request: ScheduleRequest,
        user_timezone: str
    ) -> List[OptimalTimeSlot]:
        """Find optimal posting times using AI analysis"""        try:
            # Get content analysis
            content = self.db.query(ContentModel).filter(
                ContentModel.id == request.content_id
            ).first()
            
            # Get distribution strategy
            strategy = await self.strategy_engine.generate_distribution_strategy(
                user_id=request.user_id,
                content_id=request.content_id
            )
            
            optimal_slots = []
            
            for platform in request.platforms:
                # Get platform-specific optimal times from strategy
                if platform in strategy.timing_recommendations:
                    platform_times = strategy.timing_recommendations[platform]
                    
                    for time_slot in platform_times[:3]:  # Top 3 times per platform
                        # Convert to user timezone
                        user_tz = pytz.timezone(user_timezone)
                        local_time = time_slot.astimezone(user_tz)
                        
                        # Calculate expected metrics
                        expected_metrics = strategy.expected_metrics.get(platform, {})
                        
                        optimal_slots.append(OptimalTimeSlot(
                            datetime=local_time,
                            platform=platform,
                            expected_reach=expected_metrics.get("estimated_reach", 0),
                            expected_engagement=expected_metrics.get("engagement_rate", 0),
                            confidence_score=strategy.confidence_score,
                            reason=f"Peak engagement time for {platform.value}"
                        ))
            
            # Sort by expected performance
            optimal_slots.sort(
                key=lambda x: x.expected_reach * x.expected_engagement,
                reverse=True
            )
            
            return optimal_slots[:10]  # Return top 10 slots
            
        except Exception as e:
            logger.error(f"Failed to find optimal times: {e}")
            return []
    
    async def _check_schedule_conflicts(
        self, request: ScheduleRequest
    ) -> List[ScheduleConflict]:
        """Check for scheduling conflicts with existing posts"""        conflicts = []
        
        try:
            # Get existing scheduled posts for user
            existing_schedules = self.db.query(ScheduledPostModel).filter(
                ScheduledPostModel.user_id == request.user_id,
                ScheduledPostModel.status == ScheduleStatus.PENDING,
                ScheduledPostModel.scheduled_time >= datetime.utcnow()
            ).all()
            
            # Check for conflicts based on schedule type
            if request.schedule_type == ScheduleType.SPECIFIC_TIME:
                target_time = request.target_datetime
                
                for platform in request.platforms:
                    platform_conflicts = [
                        schedule for schedule in existing_schedules
                        if schedule.platform == platform.value
                        and abs((schedule.scheduled_time - target_time).total_seconds()) < 1800  # 30 min window
                    ]
                    
                    for conflict in platform_conflicts:
                        conflicts.append(ScheduleConflict(
                            existing_post_id=conflict.id,
                            conflicting_time=conflict.scheduled_time,
                            platform=PlatformType(conflict.platform),
                            severity="medium",
                            suggested_alternative=target_time + timedelta(minutes=30)
                        ))
            
            # Check platform-specific limits
            for platform in request.platforms:
                limits = self.platform_limits[platform]
                
                # Check daily limits
                today_posts = [
                    schedule for schedule in existing_schedules
                    if schedule.platform == platform.value
                    and schedule.scheduled_time.date() == datetime.utcnow().date()
                ]
                
                if len(today_posts) >= limits["daily_limit"]:
                    conflicts.append(ScheduleConflict(
                        existing_post_id=0,
                        conflicting_time=datetime.utcnow(),
                        platform=platform,
                        severity="high",
                        suggested_alternative=datetime.utcnow() + timedelta(days=1)
                    ))
            
        except Exception as e:
            logger.error(f"Error checking schedule conflicts: {e}")
        
        return conflicts
    
    async def _create_scheduled_posts(
        self,
        request: ScheduleRequest,
        optimal_times: List[OptimalTimeSlot],
        user_timezone: str
    ) -> List[Dict[str, Any]]:
        """Create scheduled post entries based on request type"""        scheduled_posts = []
        
        try:
            if request.schedule_type == ScheduleType.IMMEDIATE:
                scheduled_posts = await self._create_immediate_posts(request)
                
            elif request.schedule_type == ScheduleType.OPTIMAL_TIME:
                scheduled_posts = await self._create_optimal_time_posts(
                    request, optimal_times
                )
                
            elif request.schedule_type == ScheduleType.SPECIFIC_TIME:
                scheduled_posts = await self._create_specific_time_posts(
                    request, user_timezone
                )
                
            elif request.schedule_type == ScheduleType.RECURRING:
                scheduled_posts = await self._create_recurring_posts(
                    request, user_timezone
                )
                
            elif request.schedule_type == ScheduleType.BATCH_RELEASE:
                scheduled_posts = await self._create_batch_posts(request)
                
            elif request.schedule_type == ScheduleType.DRIP_CAMPAIGN:
                scheduled_posts = await self._create_drip_campaign_posts(request)
            
        except Exception as e:
            logger.error(f"Error creating scheduled posts: {e}")
            raise
        
        return scheduled_posts
    
    async def _create_immediate_posts(
        self, request: ScheduleRequest
    ) -> List[Dict[str, Any]]:
        """Create immediate posting schedule"""        posts = []
        base_time = datetime.utcnow()
        
        for i, platform in enumerate(request.platforms):
            # Stagger immediate posts by 2 minutes to avoid rate limits
            post_time = base_time + timedelta(minutes=i * 2)
            
            posts.append({
                "platform": platform.value,
                "scheduled_time": post_time,
                "content_id": request.content_id,
                "user_id": request.user_id,
                "custom_message": request.custom_message,
                "schedule_type": request.schedule_type.value
            })
        
        return posts
    
    async def _create_optimal_time_posts(
        self,
        request: ScheduleRequest,
        optimal_times: List[OptimalTimeSlot]
    ) -> List[Dict[str, Any]]:
        """Create posts scheduled for optimal times"""        posts = []
        used_times = set()
        
        for platform in request.platforms:
            # Find best optimal time for this platform
            platform_times = [
                slot for slot in optimal_times
                if slot.platform == platform and slot.datetime not in used_times
            ]
            
            if platform_times:
                best_time = platform_times[0]
                used_times.add(best_time.datetime)
                
                posts.append({
                    "platform": platform.value,
                    "scheduled_time": best_time.datetime,
                    "content_id": request.content_id,
                    "user_id": request.user_id,
                    "custom_message": request.custom_message,
                    "schedule_type": request.schedule_type.value,
                    "expected_reach": best_time.expected_reach,
                    "expected_engagement": best_time.expected_engagement
                })
            else:
                # Fallback to default optimal time
                default_time = datetime.utcnow() + timedelta(hours=2)
                posts.append({
                    "platform": platform.value,
                    "scheduled_time": default_time,
                    "content_id": request.content_id,
                    "user_id": request.user_id,
                    "custom_message": request.custom_message,
                    "schedule_type": request.schedule_type.value
                })
        
        return posts
    
    async def _create_specific_time_posts(
        self,
        request: ScheduleRequest,
        user_timezone: str
    ) -> List[Dict[str, Any]]:
        """Create posts scheduled for specific time"""        posts = []
        
        # Convert target time to UTC
        user_tz = pytz.timezone(user_timezone)
        if request.target_datetime.tzinfo is None:
            # Assume target time is in user's timezone
            localized_time = user_tz.localize(request.target_datetime)
        else:
            localized_time = request.target_datetime
        
        utc_time = localized_time.astimezone(pytz.UTC)
        
        for i, platform in enumerate(request.platforms):
            # Respect platform limits for spacing
            limits = self.platform_limits[platform]
            min_interval = limits.get("min_interval", 5)
            
            # Stagger posts by minimum interval
            post_time = utc_time + timedelta(minutes=i * min_interval)
            
            posts.append({
                "platform": platform.value,
                "scheduled_time": post_time,
                "content_id": request.content_id,
                "user_id": request.user_id,
                "custom_message": request.custom_message,
                "schedule_type": request.schedule_type.value
            })
        
        return posts
    
    async def _create_recurring_posts(
        self,
        request: ScheduleRequest,
        user_timezone: str
    ) -> List[Dict[str, Any]]:
        """Create recurring post schedule"""        posts = []
        
        if not request.target_datetime:
            # Default to next optimal time
            base_time = datetime.utcnow() + timedelta(hours=1)
        else:
            base_time = request.target_datetime
        
        # Convert to UTC
        user_tz = pytz.timezone(user_timezone)
        if base_time.tzinfo is None:
            localized_time = user_tz.localize(base_time)
        else:
            localized_time = base_time
        
        start_time = localized_time.astimezone(pytz.UTC)
        
        # Calculate recurrence intervals
        interval_map = {
            RecurrencePattern.DAILY: timedelta(days=1),
            RecurrencePattern.WEEKLY: timedelta(weeks=1),
            RecurrencePattern.MONTHLY: timedelta(days=30)
        }
        
        interval = interval_map.get(request.recurrence_pattern, timedelta(days=1))
        
        # Generate recurring posts
        count = request.recurrence_count or 10  # Default 10 occurrences
        end_date = request.end_date or (start_time + timedelta(days=365))
        
        for occurrence in range(count):
            occurrence_time = start_time + (interval * occurrence)
            
            if occurrence_time > end_date:
                break
            
            for i, platform in enumerate(request.platforms):
                # Stagger platforms within each occurrence
                post_time = occurrence_time + timedelta(minutes=i * 5)
                
                posts.append({
                    "platform": platform.value,
                    "scheduled_time": post_time,
                    "content_id": request.content_id,
                    "user_id": request.user_id,
                    "custom_message": request.custom_message,
                    "schedule_type": request.schedule_type.value,
                    "recurrence_occurrence": occurrence + 1
                })
        
        return posts
    
    async def _create_batch_posts(
        self, request: ScheduleRequest
    ) -> List[Dict[str, Any]]:
        """Create batch release schedule"""        posts = []
        base_time = datetime.utcnow() + timedelta(minutes=5)  # Start in 5 minutes
        
        interval = timedelta(minutes=request.batch_interval or 30)
        
        for i, platform in enumerate(request.platforms):
            post_time = base_time + (interval * i)
            
            posts.append({
                "platform": platform.value,
                "scheduled_time": post_time,
                "content_id": request.content_id,
                "user_id": request.user_id,
                "custom_message": request.custom_message,
                "schedule_type": request.schedule_type.value,
                "batch_sequence": i + 1
            })
        
        return posts
    
    async def _create_drip_campaign_posts(
        self, request: ScheduleRequest
    ) -> List[Dict[str, Any]]:
        """Create drip campaign schedule"""        posts = []
        
        campaign_duration = request.campaign_duration or 7  # Default 7 days
        interval = timedelta(minutes=request.batch_interval or 60)
        
        # Calculate total posts across campaign duration
        total_posts = len(request.platforms)
        posts_per_day = max(1, total_posts // campaign_duration)
        
        base_time = datetime.utcnow() + timedelta(hours=1)
        
        post_index = 0
        for day in range(campaign_duration):
            day_start = base_time + timedelta(days=day)
            
            for post_in_day in range(posts_per_day):
                if post_index >= len(request.platforms):
                    break
                
                platform = request.platforms[post_index]
                post_time = day_start + (interval * post_in_day)
                
                posts.append({
                    "platform": platform.value,
                    "scheduled_time": post_time,
                    "content_id": request.content_id,
                    "user_id": request.user_id,
                    "custom_message": request.custom_message,
                    "schedule_type": request.schedule_type.value,
                    "campaign_day": day + 1,
                    "day_sequence": post_in_day + 1
                })
                
                post_index += 1
        
        return posts
    
    async def _save_schedule(
        self,
        request: ScheduleRequest,
        scheduled_posts: List[Dict[str, Any]]
    ) -> str:
        """Save schedule to database and create background tasks"""        try:
            schedule_id = f"schedule_{request.user_id}_{request.content_id}_{int(datetime.utcnow().timestamp())}"
            
            # Save to database
            for post_data in scheduled_posts:
                scheduled_post = ScheduledPostModel(
                    schedule_id=schedule_id,
                    user_id=post_data["user_id"],
                    content_id=post_data["content_id"],
                    platform=post_data["platform"],
                    scheduled_time=post_data["scheduled_time"],
                    custom_message=post_data.get("custom_message"),
                    schedule_type=post_data["schedule_type"],
                    status=ScheduleStatus.PENDING,
                    metadata={
                        k: v for k, v in post_data.items()
                        if k not in ["user_id", "content_id", "platform", "scheduled_time"]
                    }
                )
                
                self.db.add(scheduled_post)
            
            self.db.commit()
            
            # Create background tasks for execution
            await self._create_execution_tasks(scheduled_posts)
            
            return schedule_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save schedule: {e}")
            raise
    
    async def _create_execution_tasks(
        self, scheduled_posts: List[Dict[str, Any]]
    ) -> None:
        """Create Celery tasks for scheduled execution"""        from ....tasks.distribution import execute_scheduled_post
        
        for post_data in scheduled_posts:
            # Schedule Celery task
            task = execute_scheduled_post.apply_async(
                args=[post_data],
                eta=post_data["scheduled_time"]
            )
            
            logger.info(
                f"Created execution task {task.id} for "
                f"{post_data['platform']} at {post_data['scheduled_time']}"
            )
    
    async def get_user_schedule(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get user's scheduled posts"""        query = self.db.query(ScheduledPostModel).filter(
            ScheduledPostModel.user_id == user_id
        )
        
        if start_date:
            query = query.filter(ScheduledPostModel.scheduled_time >= start_date)
        
        if end_date:
            query = query.filter(ScheduledPostModel.scheduled_time <= end_date)
        
        scheduled_posts = query.order_by(ScheduledPostModel.scheduled_time).all()
        
        return [
            {
                "id": post.id,
                "schedule_id": post.schedule_id,
                "content_id": post.content_id,
                "platform": post.platform,
                "scheduled_time": post.scheduled_time,
                "status": post.status.value,
                "custom_message": post.custom_message,
                "schedule_type": post.schedule_type,
                "metadata": post.metadata,
                "created_at": post.created_at,
                "executed_at": post.executed_at
            }
            for post in scheduled_posts
        ]
    
    async def cancel_scheduled_post(
        self, user_id: int, schedule_id: str, post_id: Optional[int] = None
    ) -> bool:
        """Cancel scheduled post(s)"""        try:
            query = self.db.query(ScheduledPostModel).filter(
                ScheduledPostModel.user_id == user_id,
                ScheduledPostModel.schedule_id == schedule_id,
                ScheduledPostModel.status == ScheduleStatus.PENDING
            )
            
            if post_id:
                query = query.filter(ScheduledPostModel.id == post_id)
            
            posts_to_cancel = query.all()
            
            for post in posts_to_cancel:
                post.status = ScheduleStatus.CANCELLED
                post.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Cancel Celery tasks
            # This would require storing task IDs, which we could add to metadata
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cancel scheduled posts: {e}")
            return False
    
    async def reschedule_post(
        self,
        user_id: int,
        post_id: int,
        new_time: datetime,
        timezone: Optional[str] = None
    ) -> bool:
        """Reschedule a specific post"""        try:
            post = self.db.query(ScheduledPostModel).filter(
                ScheduledPostModel.id == post_id,
                ScheduledPostModel.user_id == user_id,
                ScheduledPostModel.status == ScheduleStatus.PENDING
            ).first()
            
            if not post:
                return False
            
            # Convert new time to UTC if timezone provided
            if timezone and new_time.tzinfo is None:
                user_tz = pytz.timezone(timezone)
                localized_time = user_tz.localize(new_time)
                new_time = localized_time.astimezone(pytz.UTC)
            
            post.scheduled_time = new_time
            post.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Reschedule Celery task
            # This would require task ID management
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reschedule post: {e}")
            return False
    
    async def get_schedule_analytics(
        self, user_id: int, schedule_id: str
    ) -> Dict[str, Any]:
        """Get analytics for a specific schedule"""        posts = self.db.query(ScheduledPostModel).filter(
            ScheduledPostModel.user_id == user_id,
            ScheduledPostModel.schedule_id == schedule_id
        ).all()
        
        if not posts:
            return {}
        
        total_posts = len(posts)
        completed_posts = len([p for p in posts if p.status == ScheduleStatus.COMPLETED])
        failed_posts = len([p for p in posts if p.status == ScheduleStatus.FAILED])
        pending_posts = len([p for p in posts if p.status == ScheduleStatus.PENDING])
        
        platform_breakdown = {}
        for post in posts:
            platform = post.platform
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "pending": 0
                }
            
            platform_breakdown[platform]["total"] += 1
            platform_breakdown[platform][post.status.value] += 1
        
        return {
            "schedule_id": schedule_id,
            "total_posts": total_posts,
            "completed_posts": completed_posts,
            "failed_posts": failed_posts,
            "pending_posts": pending_posts,
            "success_rate": completed_posts / total_posts if total_posts > 0 else 0,
            "platform_breakdown": platform_breakdown,
            "first_post": min(posts, key=lambda p: p.scheduled_time).scheduled_time,
            "last_post": max(posts, key=lambda p: p.scheduled_time).scheduled_time
        }
    
    async def cleanup_old_schedules(self, days_old: int = 30) -> int:
        """Cleanup old completed/cancelled schedules"""        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_posts = self.db.query(ScheduledPostModel).filter(
            ScheduledPostModel.updated_at < cutoff_date,
            ScheduledPostModel.status.in_([
                ScheduleStatus.COMPLETED,
                ScheduleStatus.CANCELLED,
                ScheduleStatus.FAILED
            ])
        ).all()
        
        count = len(old_posts)
        
        for post in old_posts:
            self.db.delete(post)
        
        self.db.commit()
        
        logger.info(f"Cleaned up {count} old scheduled posts")
        return count
    
    def __del__(self):
        """Cleanup scheduler on deletion"""        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown()
