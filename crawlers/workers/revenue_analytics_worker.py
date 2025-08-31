"""Revenue Analytics Worker - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/revenue_analytics_worker.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Revenue Analytics Worker - AI-Powered Monetization Engine
Responsibility: Revenue tracking, prediction, and optimization across multiple platforms
Technologies: ML Revenue Models, Multi-Platform APIs, Real-time Analytics, Predictive AI
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Platform integration → Revenue data collection → ML analysis → 
Trend prediction → Optimization recommendations → Automated distribution → Performance tracking
"""from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import statistics
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, deque
import aiohttp
import jwt

from ...ai.ml.revenue_predictor import RevenuePredictor
from ...ai.ml.trend_analyzer import TrendAnalyzer
from ...ai.ml.optimization_engine import OptimizationEngine
from ...integrations.platform_apis.spotify_api import SpotifyAPI
from ...integrations.platform_apis.youtube_api import YouTubeAPI
from ...integrations.platform_apis.instagram_api import InstagramAPI
from ...integrations.platform_apis.tiktok_api import TikTokAPI
from ...integrations.payment_processors.stripe_api import StripeAPI
from ...integrations.payment_processors.paypal_api import PayPalAPI
from ...storage.revenue_storage import RevenueStorage
from ...monitoring.revenue_monitor import RevenueMonitor
from ...utils.currency_converter import CurrencyConverter
from ...utils.math_utils import MathUtils

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for revenue tracking"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    PATREON = "patreon"


class RevenueType(Enum):
    """Types of revenue"""    STREAMING = "streaming"
    ADVERTISING = "advertising"
    MERCHANDISE = "merchandise"
    SPONSORSHIP = "sponsorship"
    DONATIONS = "donations"
    PREMIUM_CONTENT = "premium_content"
    LICENSING = "licensing"
    LIVE_PERFORMANCE = "live_performance"
    COLLABORATION = "collaboration"


class RevenueStatus(Enum):
    """Revenue collection status"""    PENDING = "pending"
    COLLECTED = "collected"
    PROCESSING = "processing"
    PAID_OUT = "paid_out"
    DISPUTED = "disputed"
    FAILED = "failed"


class AnalyticsType(Enum):
    """Analytics computation types"""    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    TREND_ANALYSIS = "trend_analysis"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"


@dataclass
class RevenueEntry:
    """Single revenue entry data structure"""    entry_id: str
    creator_id: str
    platform: Platform
    revenue_type: RevenueType
    amount: Decimal
    currency: str
    content_id: Optional[str] = None
    content_title: Optional[str] = None
    period_start: date = field(default_factory=date.today)
    period_end: date = field(default_factory=date.today)
    status: RevenueStatus = RevenueStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


@dataclass
class PlatformMetrics:
    """Platform-specific metrics"""    platform: Platform
    total_revenue: Decimal
    revenue_growth: float
    content_count: int
    engagement_rate: float
    audience_size: int
    top_performing_content: List[Dict[str, Any]]
    revenue_breakdown: Dict[RevenueType, Decimal]
    period_comparison: Dict[str, float]


@dataclass
class RevenueAnalyticsTask:
    """Revenue analytics task definition"""    task_id: str
    creator_id: str
    analytics_type: AnalyticsType
    platforms: List[Platform]
    date_range: Tuple[date, date]
    include_predictions: bool = True
    include_optimization: bool = True
    currency_preference: str = "EUR"
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueReport:
    """Complete revenue analytics report"""    report_id: str
    creator_id: str
    report_type: AnalyticsType
    period_start: date
    period_end: date
    total_revenue: Decimal
    currency: str
    platform_metrics: List[PlatformMetrics]
    growth_metrics: Dict[str, float]
    predictions: Optional[Dict[str, Any]] = None
    optimization_recommendations: Optional[List[Dict[str, Any]]] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)


class RevenueAnalyticsWorker:
    """Advanced revenue analytics worker with ML-powered insights"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.worker_id = str(uuid.uuid4())
        self.is_running = False
        
        # Initialize AI components
        self.revenue_predictor = RevenuePredictor(self.config.get("predictor_config", {}))
        self.trend_analyzer = TrendAnalyzer(self.config.get("trend_config", {}))
        self.optimization_engine = OptimizationEngine(self.config.get("optimization_config", {}))
        
        # Initialize platform APIs
        self._initialize_platform_apis()
        
        # Initialize services
        self.revenue_storage = RevenueStorage(self.config.get("storage_config", {}))
        self.revenue_monitor = RevenueMonitor(self.config.get("monitor_config", {}))
        self.currency_converter = CurrencyConverter(self.config.get("currency_config", {}))
        
        # Processing queue
        self.analytics_queue = asyncio.Queue()
        self.active_tasks: Dict[str, RevenueAnalyticsTask] = {}
        
        # Performance tracking
        self.processing_stats = {
            "total_tasks_processed": 0,
            "successful_reports": 0,
            "failed_reports": 0,
            "total_revenue_tracked": Decimal("0.00"),
            "average_processing_time": 0.0,
            "platform_api_calls": defaultdict(int),
            "last_update": datetime.utcnow()
        }
        
        # Revenue cache for real-time access
        self.revenue_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        
        logger.info(f"💰 RevenueAnalyticsWorker {self.worker_id} initialized")
    
    def _initialize_platform_apis(self):
        """Initialize platform API clients"""        try:
            api_configs = self.config.get("platform_apis", {})
            
            self.platform_apis = {
                Platform.SPOTIFY: SpotifyAPI(api_configs.get("spotify", {})),
                Platform.YOUTUBE: YouTubeAPI(api_configs.get("youtube", {})),
                Platform.INSTAGRAM: InstagramAPI(api_configs.get("instagram", {})),
                Platform.TIKTOK: TikTokAPI(api_configs.get("tiktok", {})),
            }
            
            # Initialize payment processors
            payment_configs = self.config.get("payment_processors", {})
            self.payment_apis = {
                "stripe": StripeAPI(payment_configs.get("stripe", {})),
                "paypal": PayPalAPI(payment_configs.get("paypal", {}))
            }
            
            logger.info("✅ Platform APIs initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize platform APIs: {e}")
            self.platform_apis = {}
            self.payment_apis = {}
    
    async def start(self) -> bool:
        """Start the revenue analytics worker"""        try:
            if self.is_running:
                logger.warning("RevenueAnalyticsWorker is already running")
                return True
            
            self.is_running = True
            self._start_time = time.time()
            
            # Start processing loops
            asyncio.create_task(self._analytics_processing_loop())
            asyncio.create_task(self._data_collection_loop())
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cache_cleanup_loop())
            
            logger.info(f"🚀 RevenueAnalyticsWorker {self.worker_id} started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start RevenueAnalyticsWorker: {e}")
            self.is_running = False
            return False
    
    async def stop(self) -> bool:
        """Stop the revenue analytics worker"""        try:
            self.is_running = False
            
            # Wait for active tasks to complete
            timeout = 60  # 60 seconds timeout
            start_time = time.time()
            
            while self.active_tasks and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.5)
            
            logger.info(f"🛑 RevenueAnalyticsWorker {self.worker_id} stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop RevenueAnalyticsWorker: {e}")
            return False
    
    async def submit_analytics_task(self, task: RevenueAnalyticsTask) -> bool:
        """Submit a revenue analytics task"""        try:
            if not self.is_running:
                logger.error("RevenueAnalyticsWorker is not running")
                return False
            
            # Validate task
            if not self._validate_analytics_task(task):
                logger.error(f"Invalid analytics task: {task.task_id}")
                return False
            
            # Add to processing queue
            await self.analytics_queue.put(task)
            self.active_tasks[task.task_id] = task
            
            logger.info(f"📊 Analytics task submitted: {task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit analytics task: {e}")
            return False
    
    async def _analytics_processing_loop(self):
        """Main processing loop for analytics tasks"""        while self.is_running:
            try:
                # Get task from queue (with timeout)
                try:
                    task = await asyncio.wait_for(
                        self.analytics_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the task
                await self._process_analytics_task(task)
                
                # Mark task as processed
                self.analytics_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error in analytics processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_analytics_task(self, task: RevenueAnalyticsTask):
        """Process a single analytics task"""        start_time = time.time()
        
        try:
            logger.info(f"🔄 Processing analytics task: {task.task_id}")
            
            # Step 1: Collect revenue data from platforms
            revenue_data = await self._collect_revenue_data(task)
            
            # Step 2: Generate analytics report
            report = await self._generate_analytics_report(task, revenue_data)
            
            # Step 3: Add predictions if requested
            if task.include_predictions:
                report.predictions = await self._generate_predictions(task, revenue_data)
            
            # Step 4: Add optimization recommendations if requested
            if task.include_optimization:
                report.optimization_recommendations = await self._generate_optimization_recommendations(
                    task, revenue_data, report
                )
            
            # Step 5: Store the report
            await self._store_analytics_report(report)
            
            # Step 6: Update cache
            await self._update_revenue_cache(task.creator_id, report)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, success=True, revenue_tracked=report.total_revenue)
            
            logger.info(f"✅ Analytics task completed: {task.task_id} ({processing_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Failed to process analytics task {task.task_id}: {e}")
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, success=False)
        
        finally:
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    async def _collect_revenue_data(self, task: RevenueAnalyticsTask) -> Dict[Platform, List[RevenueEntry]]:
        """Collect revenue data from multiple platforms"""        revenue_data = {}
        
        for platform in task.platforms:
            try:
                platform_revenue = await self._collect_platform_revenue(
                    platform, task.creator_id, task.date_range
                )
                revenue_data[platform] = platform_revenue
                
                # Update API call stats
                self.processing_stats["platform_api_calls"][platform.value] += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to collect revenue data from {platform.value}: {e}")
                revenue_data[platform] = []
        
        return revenue_data
    
    async def _collect_platform_revenue(self, platform: Platform, creator_id: str, date_range: Tuple[date, date]) -> List[RevenueEntry]:
        """Collect revenue data from a specific platform"""        try:
            if platform not in self.platform_apis:
                logger.warning(f"Platform API not configured: {platform.value}")
                return []
            
            api = self.platform_apis[platform]
            start_date, end_date = date_range
            
            # Get platform-specific revenue data
            if platform == Platform.SPOTIFY:
                return await self._collect_spotify_revenue(api, creator_id, start_date, end_date)
            elif platform == Platform.YOUTUBE:
                return await self._collect_youtube_revenue(api, creator_id, start_date, end_date)
            elif platform == Platform.INSTAGRAM:
                return await self._collect_instagram_revenue(api, creator_id, start_date, end_date)
            elif platform == Platform.TIKTOK:
                return await self._collect_tiktok_revenue(api, creator_id, start_date, end_date)
            else:
                logger.warning(f"Revenue collection not implemented for platform: {platform.value}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Failed to collect {platform.value} revenue: {e}")
            return []
    
    async def _collect_spotify_revenue(self, api: SpotifyAPI, creator_id: str, start_date: date, end_date: date) -> List[RevenueEntry]:
        """Collect Spotify streaming revenue"""        try:
            revenue_entries = []
            
            # Get artist analytics
            analytics_data = await api.get_artist_analytics(creator_id, start_date, end_date)
            
            if analytics_data:
                # Process streaming data
                for track_data in analytics_data.get("tracks", []):
                    streams = track_data.get("streams", 0)
                    revenue_per_stream = Decimal("0.003")  # Average Spotify payout per stream
                    total_revenue = Decimal(str(streams)) * revenue_per_stream
                    
                    entry = RevenueEntry(
                        entry_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        platform=Platform.SPOTIFY,
                        revenue_type=RevenueType.STREAMING,
                        amount=total_revenue,
                        currency="USD",
                        content_id=track_data.get("track_id"),
                        content_title=track_data.get("track_name"),
                        period_start=start_date,
                        period_end=end_date,
                        status=RevenueStatus.COLLECTED,
                        metadata={
                            "streams": streams,
                            "revenue_per_stream": float(revenue_per_stream),
                            "country_breakdown": track_data.get("country_data", {}),
                            "playlist_adds": track_data.get("playlist_adds", 0)
                        }
                    )
                    revenue_entries.append(entry)
            
            return revenue_entries
            
        except Exception as e:
            logger.error(f"❌ Failed to collect Spotify revenue: {e}")
            return []
    
    async def _collect_youtube_revenue(self, api: YouTubeAPI, creator_id: str, start_date: date, end_date: date) -> List[RevenueEntry]:
        """Collect YouTube ad revenue"""        try:
            revenue_entries = []
            
            # Get YouTube analytics
            analytics_data = await api.get_channel_analytics(creator_id, start_date, end_date)
            
            if analytics_data:
                # Process ad revenue data
                estimated_revenue = analytics_data.get("estimatedRevenue", 0)
                views = analytics_data.get("views", 0)
                
                if estimated_revenue > 0:
                    entry = RevenueEntry(
                        entry_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        platform=Platform.YOUTUBE,
                        revenue_type=RevenueType.ADVERTISING,
                        amount=Decimal(str(estimated_revenue)),
                        currency="USD",
                        period_start=start_date,
                        period_end=end_date,
                        status=RevenueStatus.COLLECTED,
                        metadata={
                            "views": views,
                            "cpm": estimated_revenue / views * 1000 if views > 0 else 0,
                            "subscriber_count": analytics_data.get("subscriberCount", 0),
                            "watch_time_hours": analytics_data.get("watchTimeHours", 0)
                        }
                    )
                    revenue_entries.append(entry)
                
                # Process individual video revenue
                for video_data in analytics_data.get("videos", []):
                    video_revenue = video_data.get("estimatedRevenue", 0)
                    if video_revenue > 0:
                        entry = RevenueEntry(
                            entry_id=str(uuid.uuid4()),
                            creator_id=creator_id,
                            platform=Platform.YOUTUBE,
                            revenue_type=RevenueType.ADVERTISING,
                            amount=Decimal(str(video_revenue)),
                            currency="USD",
                            content_id=video_data.get("videoId"),
                            content_title=video_data.get("title"),
                            period_start=start_date,
                            period_end=end_date,
                            status=RevenueStatus.COLLECTED,
                            metadata={
                                "views": video_data.get("views", 0),
                                "likes": video_data.get("likes", 0),
                                "comments": video_data.get("comments", 0),
                                "shares": video_data.get("shares", 0)
                            }
                        )
                        revenue_entries.append(entry)
            
            return revenue_entries
            
        except Exception as e:
            logger.error(f"❌ Failed to collect YouTube revenue: {e}")
            return []
    
    async def _collect_instagram_revenue(self, api: InstagramAPI, creator_id: str, start_date: date, end_date: date) -> List[RevenueEntry]:
        """Collect Instagram creator revenue"""        try:
            revenue_entries = []
            
            # Get Instagram insights
            insights_data = await api.get_creator_insights(creator_id, start_date, end_date)
            
            if insights_data:
                # Process reels play bonus
                reels_bonus = insights_data.get("reelsPlayBonus", 0)
                if reels_bonus > 0:
                    entry = RevenueEntry(
                        entry_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        platform=Platform.INSTAGRAM,
                        revenue_type=RevenueType.PREMIUM_CONTENT,
                        amount=Decimal(str(reels_bonus)),
                        currency="USD",
                        period_start=start_date,
                        period_end=end_date,
                        status=RevenueStatus.COLLECTED,
                        metadata={
                            "reels_plays": insights_data.get("reelsPlays", 0),
                            "bonus_program": "reels_play_bonus"
                        }
                    )
                    revenue_entries.append(entry)
                
                # Process brand partnerships (estimated)
                sponsored_posts = insights_data.get("sponsoredPosts", [])
                for post_data in sponsored_posts:
                    # Estimate revenue based on engagement and follower count
                    followers = insights_data.get("followerCount", 0)
                    engagement_rate = post_data.get("engagementRate", 0)
                    estimated_revenue = self._estimate_instagram_sponsorship_revenue(
                        followers, engagement_rate
                    )
                    
                    if estimated_revenue > 0:
                        entry = RevenueEntry(
                            entry_id=str(uuid.uuid4()),
                            creator_id=creator_id,
                            platform=Platform.INSTAGRAM,
                            revenue_type=RevenueType.SPONSORSHIP,
                            amount=estimated_revenue,
                            currency="USD",
                            content_id=post_data.get("postId"),
                            period_start=start_date,
                            period_end=end_date,
                            status=RevenueStatus.COLLECTED,
                            metadata={
                                "followers": followers,
                                "engagement_rate": engagement_rate,
                                "estimation_method": "engagement_based",
                                "post_type": post_data.get("mediaType", "unknown")
                            }
                        )
                        revenue_entries.append(entry)
            
            return revenue_entries
            
        except Exception as e:
            logger.error(f"❌ Failed to collect Instagram revenue: {e}")
            return []
    
    async def _collect_tiktok_revenue(self, api: TikTokAPI, creator_id: str, start_date: date, end_date: date) -> List[RevenueEntry]:
        """Collect TikTok creator revenue"""        try:
            revenue_entries = []
            
            # Get TikTok analytics
            analytics_data = await api.get_creator_analytics(creator_id, start_date, end_date)
            
            if analytics_data:
                # Process Creator Fund earnings
                creator_fund_earnings = analytics_data.get("creatorFundEarnings", 0)
                if creator_fund_earnings > 0:
                    entry = RevenueEntry(
                        entry_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        platform=Platform.TIKTOK,
                        revenue_type=RevenueType.PREMIUM_CONTENT,
                        amount=Decimal(str(creator_fund_earnings)),
                        currency="USD",
                        period_start=start_date,
                        period_end=end_date,
                        status=RevenueStatus.COLLECTED,
                        metadata={
                            "views": analytics_data.get("totalViews", 0),
                            "likes": analytics_data.get("totalLikes", 0),
                            "fund_program": "creator_fund"
                        }
                    )
                    revenue_entries.append(entry)
                
                # Process Live gifts
                live_gifts = analytics_data.get("liveGifts", 0)
                if live_gifts > 0:
                    entry = RevenueEntry(
                        entry_id=str(uuid.uuid4()),
                        creator_id=creator_id,
                        platform=Platform.TIKTOK,
                        revenue_type=RevenueType.DONATIONS,
                        amount=Decimal(str(live_gifts)),
                        currency="USD",
                        period_start=start_date,
                        period_end=end_date,
                        status=RevenueStatus.COLLECTED,
                        metadata={
                            "live_sessions": analytics_data.get("liveSessionCount", 0),
                            "gift_type": "virtual_gifts"
                        }
                    )
                    revenue_entries.append(entry)
            
            return revenue_entries
            
        except Exception as e:
            logger.error(f"❌ Failed to collect TikTok revenue: {e}")
            return []
    
    def _estimate_instagram_sponsorship_revenue(self, followers: int, engagement_rate: float) -> Decimal:
        """Estimate Instagram sponsorship revenue based on metrics"""        try:
            # Industry standard: $1-3 per 1000 followers for sponsored posts
            if followers < 1000:
                return Decimal("0.00")
            
            base_rate = Decimal("2.00")  # $2 per 1000 followers
            follower_multiplier = Decimal(str(followers / 1000))
            engagement_multiplier = Decimal(str(max(1.0, engagement_rate * 10)))
            
            estimated_revenue = base_rate * follower_multiplier * engagement_multiplier
            return estimated_revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate Instagram sponsorship revenue: {e}")
            return Decimal("0.00")
    
    async def _generate_analytics_report(self, task: RevenueAnalyticsTask, revenue_data: Dict[Platform, List[RevenueEntry]]) -> RevenueReport:
        """Generate comprehensive analytics report"""        try:
            # Calculate total revenue
            total_revenue = Decimal("0.00")
            platform_metrics = []
            
            for platform, entries in revenue_data.items():
                platform_total = sum(entry.amount for entry in entries)
                total_revenue += platform_total
                
                # Convert to preferred currency
                if task.currency_preference != "USD":
                    platform_total = await self.currency_converter.convert(
                        platform_total, "USD", task.currency_preference
                    )
                    total_revenue = await self.currency_converter.convert(
                        total_revenue, "USD", task.currency_preference
                    )
                
                # Generate platform metrics
                metrics = await self._generate_platform_metrics(platform, entries, task)
                platform_metrics.append(metrics)
            
            # Calculate growth metrics
            growth_metrics = await self._calculate_growth_metrics(
                task.creator_id, task.date_range, revenue_data
            )
            
            # Create report
            report = RevenueReport(
                report_id=str(uuid.uuid4()),
                creator_id=task.creator_id,
                report_type=task.analytics_type,
                period_start=task.date_range[0],
                period_end=task.date_range[1],
                total_revenue=total_revenue,
                currency=task.currency_preference,
                platform_metrics=platform_metrics,
                growth_metrics=growth_metrics
            )
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate analytics report: {e}")
            raise
    
    async def _generate_platform_metrics(self, platform: Platform, entries: List[RevenueEntry], task: RevenueAnalyticsTask) -> PlatformMetrics:
        """Generate detailed metrics for a specific platform"""        try:
            if not entries:
                return PlatformMetrics(
                    platform=platform,
                    total_revenue=Decimal("0.00"),
                    revenue_growth=0.0,
                    content_count=0,
                    engagement_rate=0.0,
                    audience_size=0,
                    top_performing_content=[],
                    revenue_breakdown={},
                    period_comparison={}
                )
            
            # Calculate total revenue
            total_revenue = sum(entry.amount for entry in entries)
            
            # Revenue breakdown by type
            revenue_breakdown = defaultdict(lambda: Decimal("0.00"))
            for entry in entries:
                revenue_breakdown[entry.revenue_type] += entry.amount
            
            # Content analysis
            content_revenues = defaultdict(lambda: Decimal("0.00"))
            content_titles = {}
            
            for entry in entries:
                if entry.content_id:
                    content_revenues[entry.content_id] += entry.amount
                    content_titles[entry.content_id] = entry.content_title or "Unknown"
            
            # Top performing content
            top_content = sorted(
                content_revenues.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            top_performing_content = [
                {
                    "content_id": content_id,
                    "title": content_titles.get(content_id, "Unknown"),
                    "revenue": float(revenue)
                }
                for content_id, revenue in top_content
            ]
            
            # Calculate growth (compare with previous period)
            previous_period_revenue = await self._get_previous_period_revenue(
                task.creator_id, platform, task.date_range
            )
            
            revenue_growth = 0.0
            if previous_period_revenue > 0:
                revenue_growth = float((total_revenue - previous_period_revenue) / previous_period_revenue * 100)
            
            # Estimated metrics (would be retrieved from actual APIs in production)
            engagement_rate = self._estimate_engagement_rate(platform, entries)
            audience_size = self._estimate_audience_size(platform, entries)
            
            return PlatformMetrics(
                platform=platform,
                total_revenue=total_revenue,
                revenue_growth=revenue_growth,
                content_count=len(content_revenues),
                engagement_rate=engagement_rate,
                audience_size=audience_size,
                top_performing_content=top_performing_content,
                revenue_breakdown=dict(revenue_breakdown),
                period_comparison={
                    "previous_period_revenue": float(previous_period_revenue),
                    "growth_rate": revenue_growth
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate platform metrics: {e}")
            raise
    
    async def _generate_predictions(self, task: RevenueAnalyticsTask, revenue_data: Dict[Platform, List[RevenueEntry]]) -> Dict[str, Any]:
        """Generate revenue predictions using ML models"""        try:
            # Prepare historical data for prediction
            historical_data = await self._prepare_historical_data(task.creator_id, task.platforms)
            
            # Generate predictions for each platform
            platform_predictions = {}
            
            for platform in task.platforms:
                platform_data = historical_data.get(platform, [])
                if len(platform_data) >= 10:  # Need minimum data for prediction
                    prediction = await self.revenue_predictor.predict_revenue(
                        platform, platform_data, prediction_days=30
                    )
                    platform_predictions[platform.value] = prediction
            
            # Generate overall predictions
            total_prediction = await self.revenue_predictor.predict_total_revenue(
                historical_data, prediction_days=30
            )
            
            return {
                "platform_predictions": platform_predictions,
                "total_prediction": total_prediction,
                "confidence_score": await self.revenue_predictor.get_confidence_score(),
                "prediction_period": "30_days",
                "model_version": self.revenue_predictor.get_model_version()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate predictions: {e}")
            return {}
    
    async def _generate_optimization_recommendations(self, task: RevenueAnalyticsTask, revenue_data: Dict[Platform, List[RevenueEntry]], report: RevenueReport) -> List[Dict[str, Any]]:
        """Generate optimization recommendations using ML analysis"""        try:
            recommendations = []
            
            # Analyze revenue patterns
            analysis_data = {
                "revenue_data": revenue_data,
                "platform_metrics": report.platform_metrics,
                "growth_metrics": report.growth_metrics,
                "creator_id": task.creator_id
            }
            
            # Get optimization suggestions
            optimization_results = await self.optimization_engine.analyze_revenue_optimization(
                analysis_data
            )
            
            for suggestion in optimization_results:
                recommendations.append({
                    "type": suggestion.get("type", "general"),
                    "platform": suggestion.get("platform"),
                    "title": suggestion.get("title", ""),
                    "description": suggestion.get("description", ""),
                    "potential_impact": suggestion.get("potential_impact", ""),
                    "implementation_effort": suggestion.get("implementation_effort", "medium"),
                    "priority": suggestion.get("priority", "medium"),
                    "confidence_score": suggestion.get("confidence_score", 0.0)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
            return []
    
    async def _store_analytics_report(self, report: RevenueReport):
        """Store the analytics report"""        try:
            await self.revenue_storage.store_revenue_report(report)
            logger.info(f"✅ Stored analytics report: {report.report_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store analytics report: {e}")
            raise
    
    async def _update_revenue_cache(self, creator_id: str, report: RevenueReport):
        """Update revenue cache for real-time access"""        try:
            cache_key = f"revenue_summary_{creator_id}"
            cache_data = {
                "total_revenue": float(report.total_revenue),
                "currency": report.currency,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "platform_count": len(report.platform_metrics),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.revenue_cache[cache_key] = {
                "data": cache_data,
                "expires_at": datetime.utcnow() + self.cache_ttl
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update revenue cache: {e}")
    
    async def _data_collection_loop(self):
        """Periodic data collection loop"""        while self.is_running:
            try:
                # Collect revenue data for active creators every hour
                await self._periodic_data_collection()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error in data collection loop: {e}")
                await asyncio.sleep(300)  # 5 minutes on error
    
    async def _monitoring_loop(self):
        """Monitoring loop for worker health"""        while self.is_running:
            try:
                # Report worker status
                await self.revenue_monitor.report_worker_status(
                    self.worker_id,
                    {
                        "active_tasks": len(self.active_tasks),
                        "queue_size": self.analytics_queue.qsize(),
                        "stats": self.processing_stats.copy()
                    }
                )
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _cache_cleanup_loop(self):
        """Cache cleanup loop"""        while self.is_running:
            try:
                current_time = datetime.utcnow()
                expired_keys = [
                    key for key, value in self.revenue_cache.items()
                    if value["expires_at"] < current_time
                ]
                
                for key in expired_keys:
                    del self.revenue_cache[key]
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Error in cache cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_data_collection(self):
        """Perform periodic data collection for all active creators"""        try:
            # This would typically get active creators from database
            # For now, this is a placeholder
            logger.info("🔄 Performing periodic data collection...")
            
        except Exception as e:
            logger.error(f"❌ Failed periodic data collection: {e}")
    
    def _validate_analytics_task(self, task: RevenueAnalyticsTask) -> bool:
        """Validate analytics task parameters"""        try:
            # Check required fields
            if not task.task_id or not task.creator_id:
                return False
            
            # Check platforms
            if not task.platforms:
                return False
            
            # Check date range
            start_date, end_date = task.date_range
            if start_date > end_date:
                return False
            
            # Check analytics type
            if task.analytics_type not in AnalyticsType:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating analytics task: {e}")
            return False
    
    def _update_processing_stats(self, processing_time: float, success: bool, revenue_tracked: Decimal = None):
        """Update processing statistics"""        try:
            self.processing_stats["total_tasks_processed"] += 1
            
            if success:
                self.processing_stats["successful_reports"] += 1
                if revenue_tracked:
                    self.processing_stats["total_revenue_tracked"] += revenue_tracked
            else:
                self.processing_stats["failed_reports"] += 1
            
            # Update average processing time
            total_time = (
                self.processing_stats["average_processing_time"] * 
                (self.processing_stats["total_tasks_processed"] - 1) + 
                processing_time
            )
            self.processing_stats["average_processing_time"] = (
                total_time / self.processing_stats["total_tasks_processed"]
            )
            
            self.processing_stats["last_update"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Error updating processing stats: {e}")
    
    def _estimate_engagement_rate(self, platform: Platform, entries: List[RevenueEntry]) -> float:
        """Estimate engagement rate based on revenue data"""        # This would be calculated from actual engagement metrics in production
        base_rates = {
            Platform.SPOTIFY: 0.15,
            Platform.YOUTUBE: 0.08,
            Platform.INSTAGRAM: 0.12,
            Platform.TIKTOK: 0.18
        }
        return base_rates.get(platform, 0.10)
    
    def _estimate_audience_size(self, platform: Platform, entries: List[RevenueEntry]) -> int:
        """Estimate audience size based on revenue data"""        # This would be retrieved from actual platform metrics in production
        if not entries:
            return 0
        
        total_revenue = sum(entry.amount for entry in entries)
        
        # Rough estimates based on platform monetization rates
        if platform == Platform.SPOTIFY:
            return int(total_revenue / Decimal("0.003") / 10)  # Streams to followers ratio
        elif platform == Platform.YOUTUBE:
            return int(total_revenue * 100)  # Revenue to subscriber ratio
        else:
            return int(total_revenue * 50)  # General estimate
    
    async def _get_previous_period_revenue(self, creator_id: str, platform: Platform, current_period: Tuple[date, date]) -> Decimal:
        """Get revenue from previous comparable period"""        try:
            start_date, end_date = current_period
            period_length = (end_date - start_date).days
            
            # Calculate previous period dates
            previous_end = start_date - timedelta(days=1)
            previous_start = previous_end - timedelta(days=period_length)
            
            # Query previous period revenue (placeholder implementation)
            previous_revenue = await self.revenue_storage.get_period_revenue(
                creator_id, platform, previous_start, previous_end
            )
            
            return previous_revenue or Decimal("0.00")
            
        except Exception as e:
            logger.error(f"❌ Failed to get previous period revenue: {e}")
            return Decimal("0.00")
    
    async def _prepare_historical_data(self, creator_id: str, platforms: List[Platform]) -> Dict[Platform, List[Dict[str, Any]]]:
        """Prepare historical data for ML predictions"""        try:
            historical_data = {}
            
            for platform in platforms:
                # Get historical revenue data (placeholder implementation)
                platform_history = await self.revenue_storage.get_historical_revenue(
                    creator_id, platform, days=365
                )
                historical_data[platform] = platform_history
            
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare historical data: {e}")
            return {}
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""        return {
            "worker_id": self.worker_id,
            "is_running": self.is_running,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.analytics_queue.qsize(),
            "cache_size": len(self.revenue_cache),
            "statistics": self.processing_stats.copy(),
            "uptime": time.time() - getattr(self, '_start_time', time.time()),
            "supported_platforms": [p.value for p in Platform],
            "supported_currencies": ["USD", "EUR", "GBP", "CAD"]
        }


# Global worker instance
_revenue_analytics_worker: Optional[RevenueAnalyticsWorker] = None


async def get_revenue_analytics_worker() -> Optional[RevenueAnalyticsWorker]:
    """Get the global revenue analytics worker instance"""    return _revenue_analytics_worker


async def initialize_revenue_analytics_worker(config: Dict[str, Any] = None) -> bool:
    """Initialize the revenue analytics worker"""    global _revenue_analytics_worker
    
    try:
        if _revenue_analytics_worker is not None:
            logger.warning("RevenueAnalyticsWorker already initialized")
            return True
        
        _revenue_analytics_worker = RevenueAnalyticsWorker(config)
        success = await _revenue_analytics_worker.start()
        
        if success:
            logger.info("✅ RevenueAnalyticsWorker initialized successfully")
        else:
            logger.error("❌ Failed to initialize RevenueAnalyticsWorker")
            _revenue_analytics_worker = None
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RevenueAnalyticsWorker: {e}")
        _revenue_analytics_worker = None
        return False


async def shutdown_revenue_analytics_worker() -> bool:
    """Shutdown the revenue analytics worker"""    global _revenue_analytics_worker
    
    try:
        if _revenue_analytics_worker is None:
            logger.warning("RevenueAnalyticsWorker not initialized")
            return True
        
        success = await _revenue_analytics_worker.stop()
        _revenue_analytics_worker = None
        
        if success:
            logger.info("✅ RevenueAnalyticsWorker shutdown successfully")
        else:
            logger.error("❌ Failed to shutdown RevenueAnalyticsWorker")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to shutdown RevenueAnalyticsWorker: {e}")
        return False


# Export classes and functions
__all__ = [
    "RevenueAnalyticsWorker",
    "Platform",
    "RevenueType",
    "RevenueStatus",
    "AnalyticsType",
    "RevenueEntry",
    "PlatformMetrics",
    "RevenueAnalyticsTask",
    "RevenueReport",
    "get_revenue_analytics_worker",
    "initialize_revenue_analytics_worker",
    "shutdown_revenue_analytics_worker"
]
