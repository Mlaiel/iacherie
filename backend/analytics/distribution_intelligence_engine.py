"""Distribution Intelligence Engine - Advanced Distribution Analytics Backend
===========================================================================

Comprehensive distribution analytics system providing deep insights into
cross-platform content distribution, audience overlap intelligence, revenue
attribution algorithms, and optimization across 35+ platforms.

Analyzes distribution effectiveness, platform-specific performance correlation,
content reach optimization, and strategic distribution intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
import hashlib
import time
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, Counter, deque


# Configure logging
logger = logging.getLogger(__name__)


class DistributionPlatform(Enum):
    """Supported distribution platforms"""
    # Video Platforms
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    FACEBOOK_VIDEO = "facebook_video"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    RUMBLE = "rumble"
    
    # Audio Platforms
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    YOUTUBE_MUSIC = "youtube_music"
    SOUNDCLOUD = "soundcloud"
    DEEZER = "deezer"
    PANDORA = "pandora"
    PODCAST_PLATFORMS = "podcast_platforms"
    
    # Social Media
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    DISCORD = "discord"
    
    # Professional Platforms
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    GITHUB = "github"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    
    # E-commerce
    AMAZON = "amazon"
    ETSY = "etsy"
    SHOPIFY = "shopify"
    GUMROAD = "gumroad"
    
    # Gaming
    STEAM = "steam"
    ITCH_IO = "itch_io"
    EPIC_GAMES = "epic_games"


class ContentType(Enum):
    """Types of content for distribution"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    STORY = "story"
    REEL = "reel"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"
    INTERACTIVE = "interactive"
    DOCUMENT = "document"
    COURSE = "course"
    PRODUCT = "product"


class DistributionMetric(Enum):
    """Distribution performance metrics"""
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT_RATE = "engagement_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    REVENUE_ATTRIBUTION = "revenue_attribution"
    AUDIENCE_OVERLAP = "audience_overlap"
    PLATFORM_EFFECTIVENESS = "platform_effectiveness"
    DISTRIBUTION_EFFICIENCY = "distribution_efficiency"
    CONTENT_VELOCITY = "content_velocity"
    CROSS_PLATFORM_SYNERGY = "cross_platform_synergy"
    RESOURCE_UTILIZATION = "resource_utilization"


class DistributionStrategy(Enum):
    """Distribution strategy types"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PLATFORM_SPECIFIC = "platform_specific"
    AUDIENCE_TARGETED = "audience_targeted"
    TIME_OPTIMIZED = "time_optimized"
    RESOURCE_OPTIMIZED = "resource_optimized"
    VIRAL_OPTIMIZED = "viral_optimized"
    REVENUE_OPTIMIZED = "revenue_optimized"


class AudienceSegment(Enum):
    """Audience segmentation types"""
    DEMOGRAPHICS = "demographics"
    PSYCHOGRAPHICS = "psychographics"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    TECHNOGRAPHIC = "technographic"
    ENGAGEMENT_LEVEL = "engagement_level"
    PURCHASE_INTENT = "purchase_intent"
    PLATFORM_PREFERENCE = "platform_preference"


@dataclass
class PlatformPerformance:
    """Individual platform performance data"""
    platform: DistributionPlatform
    content_id: str
    content_type: ContentType
    
    # Performance metrics
    reach: int = 0
    impressions: int = 0
    engagement_count: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # Revenue metrics
    revenue_generated: Decimal = Decimal('0.00')
    cost_per_acquisition: Decimal = Decimal('0.00')
    return_on_ad_spend: float = 0.0
    
    # Timing metrics
    time_to_peak: timedelta = timedelta(hours=24)
    performance_duration: timedelta = timedelta(days=7)
    optimal_posting_time: Optional[datetime] = None
    
    # Audience insights
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    audience_overlap_coefficient: float = 0.0
    unique_audience_percentage: float = 0.0
    
    # Quality metrics
    completion_rate: float = 0.0
    retention_rate: float = 0.0
    share_rate: float = 0.0
    save_rate: float = 0.0
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionAnalysis:
    """Comprehensive distribution analysis results"""
    content_id: str
    analysis_period: Tuple[datetime, datetime]
    platforms_analyzed: List[DistributionPlatform]
    
    # Overall performance
    total_reach: int = 0
    total_impressions: int = 0
    total_engagement: int = 0
    total_revenue: Decimal = Decimal('0.00')
    
    # Cross-platform insights
    platform_performance: Dict[DistributionPlatform, PlatformPerformance] = field(default_factory=dict)
    platform_ranking: List[Tuple[DistributionPlatform, float]] = field(default_factory=list)
    platform_synergy_matrix: Dict[Tuple[DistributionPlatform, DistributionPlatform], float] = field(default_factory=dict)
    
    # Audience analytics
    audience_overlap_analysis: Dict[str, float] = field(default_factory=dict)
    unique_audience_size: int = 0
    audience_duplication_rate: float = 0.0
    
    # Revenue attribution
    revenue_attribution: Dict[DistributionPlatform, Decimal] = field(default_factory=dict)
    revenue_correlation_matrix: Dict[DistributionPlatform, float] = field(default_factory=dict)
    
    # Optimization insights
    optimal_distribution_strategy: DistributionStrategy = DistributionStrategy.SIMULTANEOUS
    recommended_platforms: List[DistributionPlatform] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    
    # Performance predictions
    projected_performance: Dict[DistributionPlatform, Dict[str, float]] = field(default_factory=dict)
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    analysis_confidence: float = 0.0
    recommendations_priority: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionRequest:
    """Distribution analytics request"""
    request_id: str
    user_id: str
    content_id: str
    content_type: ContentType
    target_platforms: List[DistributionPlatform]
    
    # Analysis parameters
    analysis_period_days: int = 30
    include_predictions: bool = True
    include_optimization: bool = True
    audience_analysis_depth: str = "detailed"  # basic, detailed, comprehensive
    
    # Filter parameters
    minimum_platform_reach: int = 1000
    exclude_platforms: List[DistributionPlatform] = field(default_factory=list)
    focus_metrics: List[DistributionMetric] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    priority: str = "normal"  # low, normal, high, urgent
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrossPlatformInsight:
    """Cross-platform performance insights"""
    insight_id: str
    insight_type: str
    platforms_involved: List[DistributionPlatform]
    
    # Insight details
    title: str
    description: str
    impact_score: float  # 0-100
    confidence_level: float  # 0-1
    
    # Metrics
    performance_lift: float = 0.0
    audience_overlap: float = 0.0
    revenue_impact: Decimal = Decimal('0.00')
    
    # Recommendations
    recommended_actions: List[str] = field(default_factory=list)
    implementation_difficulty: str = "medium"  # easy, medium, hard
    expected_timeline: timedelta = timedelta(days=7)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DistributionIntelligenceEngine:
    """
    Advanced Distribution Intelligence Engine
    
    Provides comprehensive analytics for content distribution across 35+ platforms,
    including performance tracking, audience overlap analysis, revenue attribution,
    optimization recommendations, and strategic distribution intelligence.
    """
    
    def __init__(self, max_history_days -> None: int = 90) -> None:
        """Initialize the Distribution Intelligence Engine"""
        self.distribution_data: Dict[str, List[PlatformPerformance]] = defaultdict(list)
        self.analysis_results: Dict[str, DistributionAnalysis] = {}
        self.cross_platform_insights: Dict[str, CrossPlatformInsight] = {}
        self.pending_requests: Dict[str, DistributionRequest] = {}
        
        # Configuration
        self.max_history_days = max_history_days
        
        # Platform capabilities and weights
        self.platform_capabilities = self._initialize_platform_capabilities()
        self.platform_weights = self._initialize_platform_weights()
        
        # Audience overlap models
        self.audience_overlap_models = self._initialize_overlap_models()
        
        # Revenue attribution models
        self.attribution_models = self._initialize_attribution_models()
        
        # Performance thresholds
        self.performance_thresholds = self._initialize_performance_thresholds()
        
        logger.info("📊 Distribution Intelligence Engine initialized")
    
    def _initialize_platform_capabilities(self) -> Dict[DistributionPlatform, Dict[str, Any]]:
        """Initialize platform-specific capabilities and characteristics"""
        return {
            DistributionPlatform.YOUTUBE: {
                "content_types": [ContentType.VIDEO, ContentType.LIVESTREAM],
                "max_reach_potential": 2000000000,
                "engagement_multiplier": 1.2,
                "revenue_potential": "high",
                "audience_targeting": "advanced",
                "optimal_length": {"min": 60, "max": 3600},
                "peak_hours": [19, 20, 21],
                "demographics": {"age_primary": "18-34", "global_reach": True}
            },
            DistributionPlatform.TIKTOK: {
                "content_types": [ContentType.SHORT_FORM, ContentType.VIDEO],
                "max_reach_potential": 1000000000,
                "engagement_multiplier": 2.5,
                "revenue_potential": "medium",
                "audience_targeting": "basic",
                "optimal_length": {"min": 15, "max": 180},
                "peak_hours": [18, 19, 20],
                "demographics": {"age_primary": "16-24", "global_reach": True}
            },
            DistributionPlatform.INSTAGRAM: {
                "content_types": [ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY],
                "max_reach_potential": 1500000000,
                "engagement_multiplier": 1.8,
                "revenue_potential": "high",
                "audience_targeting": "advanced",
                "optimal_length": {"min": 30, "max": 900},
                "peak_hours": [11, 14, 17],
                "demographics": {"age_primary": "18-29", "global_reach": True}
            },
            DistributionPlatform.SPOTIFY: {
                "content_types": [ContentType.AUDIO, ContentType.PODCAST],
                "max_reach_potential": 500000000,
                "engagement_multiplier": 1.5,
                "revenue_potential": "high",
                "audience_targeting": "moderate",
                "optimal_length": {"min": 180, "max": 7200},
                "peak_hours": [7, 8, 9, 17, 18],
                "demographics": {"age_primary": "18-44", "global_reach": True}
            },
            DistributionPlatform.LINKEDIN: {
                "content_types": [ContentType.TEXT, ContentType.VIDEO, ContentType.DOCUMENT],
                "max_reach_potential": 800000000,
                "engagement_multiplier": 1.1,
                "revenue_potential": "medium",
                "audience_targeting": "professional",
                "optimal_length": {"min": 120, "max": 1800},
                "peak_hours": [8, 9, 12, 17],
                "demographics": {"age_primary": "25-54", "professional_focus": True}
            }
        }
    
    def _initialize_platform_weights(self) -> Dict[DistributionPlatform, float]:
        """Initialize platform performance weights"""
        return {
            DistributionPlatform.YOUTUBE: 0.25,
            DistributionPlatform.INSTAGRAM: 0.20,
            DistributionPlatform.TIKTOK: 0.18,
            DistributionPlatform.FACEBOOK: 0.15,
            DistributionPlatform.TWITTER: 0.12,
            DistributionPlatform.LINKEDIN: 0.10,
            # Other platforms get smaller default weights
        }
    
    def _initialize_overlap_models(self) -> Dict[str, Dict[str, float]]:
        """Initialize audience overlap prediction models"""
        return {
            "platform_correlation": {
                "youtube_instagram": 0.65,
                "youtube_tiktok": 0.45,
                "instagram_tiktok": 0.78,
                "instagram_facebook": 0.82,
                "linkedin_twitter": 0.35,
                "spotify_youtube": 0.55,
            },
            "content_type_correlation": {
                "video_image": 0.70,
                "video_audio": 0.40,
                "image_text": 0.60,
                "audio_podcast": 0.85,
            },
            "demographic_overlap": {
                "age_18_24": 0.75,
                "age_25_34": 0.85,
                "age_35_44": 0.65,
                "age_45_plus": 0.45,
            }
        }
    
    def _initialize_attribution_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize revenue attribution models"""
        return {
            "first_touch": {"weight": 1.0, "decay": 0.0},
            "last_touch": {"weight": 1.0, "decay": 0.0},
            "linear": {"weight": 1.0, "decay": 0.0},
            "time_decay": {"weight": 1.0, "decay": 0.7},
            "position_based": {"first": 0.4, "last": 0.4, "middle": 0.2},
            "data_driven": {"ml_model": True, "confidence": 0.85}
        }
    
    def _initialize_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance threshold benchmarks"""
        return {
            "engagement_rate": {
                "excellent": 0.10,
                "good": 0.05,
                "average": 0.02,
                "poor": 0.01
            },
            "click_through_rate": {
                "excellent": 0.08,
                "good": 0.04,
                "average": 0.02,
                "poor": 0.01
            },
            "conversion_rate": {
                "excellent": 0.05,
                "good": 0.03,
                "average": 0.01,
                "poor": 0.005
            },
            "audience_overlap": {
                "high": 0.80,
                "medium": 0.50,
                "low": 0.20,
                "minimal": 0.05
            }
        }
    
    async def submit_distribution_request(self, request: DistributionRequest) -> bool:
        """Submit a distribution analysis request"""
        try:
            # Validate request
            if not request.content_id or not request.target_platforms:
                logger.error("Invalid distribution request: missing required fields")
                return False
            
            # Store request
            self.pending_requests[request.request_id] = request
            
            # Start analysis asynchronously
            asyncio.create_task(self._process_distribution_request(request))
            
            logger.info(f"📊 Distribution analysis request submitted: {request.request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting distribution request: {str(e)}")
            return False
    
    async def track_platform_performance(self, performance: PlatformPerformance) -> bool:
        """Track performance metrics for a specific platform"""
        try:
            # Validate performance data
            if not performance.content_id or not performance.platform:
                logger.error("Invalid performance data: missing required fields")
                return False
            
            # Store performance data
            self.distribution_data[performance.content_id].append(performance)
            
            # Maintain data history limit
            content_data = self.distribution_data[performance.content_id]
            cutoff_date = datetime.now() - timedelta(days=self.max_history_days)
            
            self.distribution_data[performance.content_id] = [
                p for p in content_data 
                if p.timestamp >= cutoff_date
            ]
            
            logger.debug(f"📈 Platform performance tracked: {performance.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking platform performance: {str(e)}")
            return False
    
    async def analyze_distribution_performance(
        self,
        content_id: str,
        platforms: Optional[List[DistributionPlatform]] = None,
        analysis_period_days: int = 30
    ) -> Optional[DistributionAnalysis]:
        """Analyze distribution performance across platforms"""
        try:
            if content_id not in self.distribution_data:
                logger.warning(f"No distribution data found for content: {content_id}")
                return None
            
            # Filter data by time period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            content_data = [
                p for p in self.distribution_data[content_id]
                if start_date <= p.timestamp <= end_date
            ]
            
            if not content_data:
                logger.warning(f"No data found for specified period: {content_id}")
                return None
            
            # Filter by platforms if specified
            if platforms:
                content_data = [p for p in content_data if p.platform in platforms]
                platforms_analyzed = platforms
            else:
                platforms_analyzed = list(set(p.platform for p in content_data))
            
            # Create analysis
            analysis = await self._calculate_distribution_analysis(
                content_id, content_data, platforms_analyzed, (start_date, end_date)
            )
            
            # Store analysis results
            self.analysis_results[content_id] = analysis
            
            logger.info(f"📊 Distribution analysis completed: {content_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing distribution performance: {str(e)}")
            return None
    
    async def _calculate_distribution_analysis(
        self,
        content_id: str,
        performance_data: List[PlatformPerformance],
        platforms_analyzed: List[DistributionPlatform],
        period: Tuple[datetime, datetime]
    ) -> DistributionAnalysis:
        """Calculate comprehensive distribution analysis"""
        
        # Initialize analysis
        analysis = DistributionAnalysis(
            content_id=content_id,
            analysis_period=period,
            platforms_analyzed=platforms_analyzed
        )
        
        # Group data by platform
        platform_data = defaultdict(list)
        for perf in performance_data:
            platform_data[perf.platform].append(perf)
        
        # Calculate platform-specific performance
        platform_scores = {}
        for platform, data in platform_data.items():
            # Aggregate metrics
            total_reach = sum(p.reach for p in data)
            total_impressions = sum(p.impressions for p in data)
            total_engagement = sum(p.engagement_count for p in data)
            total_revenue = sum(p.revenue_generated for p in data)
            
            # Calculate rates
            avg_engagement_rate = statistics.mean([p.engagement_rate for p in data]) if data else 0.0
            avg_ctr = statistics.mean([p.click_through_rate for p in data]) if data else 0.0
            avg_conversion_rate = statistics.mean([p.conversion_rate for p in data]) if data else 0.0
            
            # Create performance summary
            platform_performance = PlatformPerformance(
                platform=platform,
                content_id=content_id,
                content_type=data[0].content_type,
                reach=total_reach,
                impressions=total_impressions,
                engagement_count=total_engagement,
                engagement_rate=avg_engagement_rate,
                click_through_rate=avg_ctr,
                conversion_rate=avg_conversion_rate,
                revenue_generated=total_revenue
            )
            
            analysis.platform_performance[platform] = platform_performance
            
            # Calculate platform score
            platform_weight = self.platform_weights.get(platform, 0.05)
            performance_score = (
                (avg_engagement_rate * 40) +
                (avg_ctr * 30) +
                (avg_conversion_rate * 30)
            ) * platform_weight
            
            platform_scores[platform] = performance_score
        
        # Calculate overall metrics
        analysis.total_reach = sum(p.reach for p in analysis.platform_performance.values())
        analysis.total_impressions = sum(p.impressions for p in analysis.platform_performance.values())
        analysis.total_engagement = sum(p.engagement_count for p in analysis.platform_performance.values())
        analysis.total_revenue = sum(p.revenue_generated for p in analysis.platform_performance.values())
        
        # Platform ranking
        analysis.platform_ranking = sorted(
            platform_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate cross-platform synergy
        analysis.platform_synergy_matrix = await self._calculate_platform_synergy(platforms_analyzed)
        
        # Audience overlap analysis
        analysis.audience_overlap_analysis = await self._analyze_audience_overlap(platforms_analyzed)
        analysis.audience_duplication_rate = await self._calculate_duplication_rate(platforms_analyzed)
        
        # Revenue attribution
        analysis.revenue_attribution = await self._calculate_revenue_attribution(
            analysis.platform_performance
        )
        
        # Optimization recommendations
        analysis.optimal_distribution_strategy = await self._determine_optimal_strategy(analysis)
        analysis.recommended_platforms = await self._recommend_platforms(platform_scores)
        analysis.optimization_opportunities = await self._identify_optimization_opportunities(analysis)
        
        # Performance predictions
        analysis.projected_performance = await self._predict_platform_performance(
            analysis.platform_performance
        )
        
        # Calculate confidence score
        data_points = len(performance_data)
        time_coverage = (period[1] - period[0]).days
        platform_coverage = len(platforms_analyzed)
        
        analysis.analysis_confidence = min(
            1.0,
            (data_points / 100) * 0.4 +
            (min(time_coverage, 30) / 30) * 0.3 +
            (min(platform_coverage, 10) / 10) * 0.3
        )
        
        return analysis
    
    async def _calculate_platform_synergy(
        self,
        platforms: List[DistributionPlatform]
    ) -> Dict[Tuple[DistributionPlatform, DistributionPlatform], float]:
        """Calculate synergy coefficients between platforms"""
        synergy_matrix = {}
        
        for i, platform1 in enumerate(platforms):
            for j, platform2 in enumerate(platforms):
                if i < j:  # Avoid duplicates
                    # Get base correlation from overlap models
                    key = f"{platform1.value}_{platform2.value}"
                    reverse_key = f"{platform2.value}_{platform1.value}"
                    
                    base_correlation = (
                        self.audience_overlap_models["platform_correlation"].get(key, 0.3) +
                        self.audience_overlap_models["platform_correlation"].get(reverse_key, 0.3)
                    ) / 2
                    
                    # Adjust based on platform capabilities
                    cap1 = self.platform_capabilities.get(platform1, {})
                    cap2 = self.platform_capabilities.get(platform2, {})
                    
                    # Content type overlap
                    types1 = set(cap1.get("content_types", []))
                    types2 = set(cap2.get("content_types", []))
                    content_overlap = len(types1.intersection(types2)) / max(len(types1.union(types2)), 1)
                    
                    # Demographics overlap (simplified)
                    demo_overlap = 0.5  # Default moderate overlap
                    
                    # Calculate final synergy
                    synergy = (base_correlation * 0.5 + content_overlap * 0.3 + demo_overlap * 0.2)
                    synergy_matrix[(platform1, platform2)] = min(1.0, synergy)
        
        return synergy_matrix
    
    async def _analyze_audience_overlap(
        self,
        platforms: List[DistributionPlatform]
    ) -> Dict[str, float]:
        """Analyze audience overlap across platforms"""
        overlap_analysis = {}
        
        if len(platforms) < 2:
            return overlap_analysis
        
        # Calculate pairwise overlaps
        total_overlap = 0.0
        pairs = 0
        
        for i, platform1 in enumerate(platforms):
            for j, platform2 in enumerate(platforms):
                if i < j:
                    key = f"{platform1.value}_{platform2.value}"
                    
                    # Get overlap from models
                    overlap = self.audience_overlap_models["platform_correlation"].get(
                        key, 
                        self.audience_overlap_models["platform_correlation"].get(
                            f"{platform2.value}_{platform1.value}", 
                            0.4  # Default moderate overlap
                        )
                    )
                    
                    overlap_analysis[key] = overlap
                    total_overlap += overlap
                    pairs += 1
        
        # Calculate average overlap
        if pairs > 0:
            overlap_analysis["average_overlap"] = total_overlap / pairs
        
        # Estimate unique audience percentage
        avg_overlap = overlap_analysis.get("average_overlap", 0.4)
        overlap_analysis["unique_audience_coefficient"] = 1.0 - (avg_overlap * 0.7)
        
        return overlap_analysis
    
    async def _calculate_duplication_rate(self, platforms: List[DistributionPlatform]) -> float:
        """Calculate audience duplication rate across platforms"""
        if len(platforms) < 2:
            return 0.0
        
        # Simplified duplication calculation
        total_overlap = 0.0
        comparisons = 0
        
        for i, platform1 in enumerate(platforms):
            for j, platform2 in enumerate(platforms):
                if i < j:
                    # Get overlap estimate
                    key = f"{platform1.value}_{platform2.value}"
                    overlap = self.audience_overlap_models["platform_correlation"].get(key, 0.4)
                    
                    total_overlap += overlap
                    comparisons += 1
        
        return total_overlap / max(comparisons, 1)
    
    async def _calculate_revenue_attribution(
        self,
        platform_performance: Dict[DistributionPlatform, PlatformPerformance]
    ) -> Dict[DistributionPlatform, Decimal]:
        """Calculate revenue attribution across platforms"""
        attribution = {}
        total_revenue = sum(p.revenue_generated for p in platform_performance.values())
        
        if total_revenue == 0:
            return attribution
        
        # Use data-driven attribution model
        for platform, performance in platform_performance.items():
            # Base attribution on revenue + engagement influence
            direct_revenue = performance.revenue_generated
            
            # Add influence factor based on engagement
            engagement_influence = (
                performance.engagement_rate * 
                performance.reach * 
                0.001  # Scaling factor
            )
            
            # Calculate attributed revenue
            influence_revenue = Decimal(str(engagement_influence * 0.1))  # Convert influence to revenue
            attributed_revenue = direct_revenue + influence_revenue
            
            attribution[platform] = attributed_revenue
        
        return attribution
    
    async def _determine_optimal_strategy(self, analysis: DistributionAnalysis) -> DistributionStrategy:
        """Determine optimal distribution strategy"""
        
        # Analyze platform performance variance
        platform_scores = [score for _, score in analysis.platform_ranking]
        if not platform_scores:
            return DistributionStrategy.SIMULTANEOUS
        
        variance = statistics.variance(platform_scores) if len(platform_scores) > 1 else 0
        
        # High variance suggests platform-specific strategy
        if variance > 0.1:
            return DistributionStrategy.PLATFORM_SPECIFIC
        
        # Check audience overlap
        avg_overlap = analysis.audience_overlap_analysis.get("average_overlap", 0.5)
        
        # High overlap suggests sequential distribution
        if avg_overlap > 0.7:
            return DistributionStrategy.SEQUENTIAL
        
        # Check revenue concentration
        if analysis.total_revenue > 0:
            revenue_values = list(analysis.revenue_attribution.values())
            if revenue_values:
                max_revenue = max(revenue_values)
                revenue_concentration = float(max_revenue / analysis.total_revenue)
                
                if revenue_concentration > 0.6:
                    return DistributionStrategy.REVENUE_OPTIMIZED
        
        # Default to simultaneous for balanced performance
        return DistributionStrategy.SIMULTANEOUS
    
    async def _recommend_platforms(
        self,
        platform_scores: Dict[DistributionPlatform, float]
    ) -> List[DistributionPlatform]:
        """Recommend optimal platforms based on performance scores"""
        
        if not platform_scores:
            return []
        
        # Sort platforms by score
        sorted_platforms = sorted(
            platform_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Select top performers above threshold
        threshold = 0.05  # Minimum performance threshold
        recommended = [
            platform for platform, score in sorted_platforms
            if score >= threshold
        ]
        
        # Ensure at least top 3 platforms if available
        if len(recommended) < 3 and len(sorted_platforms) >= 3:
            recommended = [platform for platform, _ in sorted_platforms[:3]]
        
        return recommended[:5]  # Limit to top 5 recommendations
    
    async def _identify_optimization_opportunities(
        self,
        analysis: DistributionAnalysis
    ) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        # Check for underperforming platforms
        if analysis.platform_ranking:
            lowest_score = analysis.platform_ranking[-1][1]
            if lowest_score < 0.02:
                opportunities.append(
                    f"Consider optimizing content for {analysis.platform_ranking[-1][0].value} "
                    "or redistributing effort to higher-performing platforms"
                )
        
        # Check audience overlap
        avg_overlap = analysis.audience_overlap_analysis.get("average_overlap", 0.5)
        if avg_overlap > 0.8:
            opportunities.append(
                "High audience overlap detected - consider diversifying platform mix "
                "to reach new audiences"
            )
        
        # Check engagement rates
        platform_performance = analysis.platform_performance
        low_engagement_platforms = [
            platform.value for platform, perf in platform_performance.items()
            if perf.engagement_rate < self.performance_thresholds["engagement_rate"]["poor"]
        ]
        
        if low_engagement_platforms:
            opportunities.append(
                f"Low engagement on {', '.join(low_engagement_platforms)} - "
                "consider content optimization or timing adjustments"
            )
        
        # Check revenue efficiency
        if analysis.total_revenue > 0:
            for platform, revenue in analysis.revenue_attribution.items():
                perf = platform_performance.get(platform)
                if perf and perf.reach > 0:
                    revenue_per_reach = float(revenue) / perf.reach
                    if revenue_per_reach < 0.001:  # Low monetization efficiency
                        opportunities.append(
                            f"Low monetization efficiency on {platform.value} - "
                            "consider improving conversion funnel"
                        )
        
        return opportunities[:5]  # Limit to top 5 opportunities
    
    async def _predict_platform_performance(
        self,
        current_performance: Dict[DistributionPlatform, PlatformPerformance]
    ) -> Dict[DistributionPlatform, Dict[str, float]]:
        """Predict future platform performance"""
        predictions = {}
        
        for platform, performance in current_performance.items():
            # Simple growth prediction based on current trends
            base_engagement = performance.engagement_rate
            base_reach = performance.reach
            base_revenue = float(performance.revenue_generated)
            
            # Platform-specific growth factors
            platform_caps = self.platform_capabilities.get(platform, {})
            growth_potential = platform_caps.get("engagement_multiplier", 1.0)
            
            # Predict 30-day projections
            predicted_engagement = min(
                base_engagement * (1 + (growth_potential - 1) * 0.1),
                0.15  # Cap at 15% engagement rate
            )
            
            predicted_reach = int(base_reach * (1 + random.uniform(0.05, 0.15)))
            predicted_revenue = base_revenue * (1 + random.uniform(0.1, 0.25))
            
            predictions[platform] = {
                "engagement_rate": predicted_engagement,
                "reach": predicted_reach,
                "revenue": predicted_revenue,
                "confidence": 0.7 + random.uniform(-0.1, 0.1)
            }
        
        return predictions
    
    async def _process_distribution_request(self, request: DistributionRequest) -> None:
        """Process distribution analysis request asynchronously"""
        try:
            # Perform analysis
            analysis = await self.analyze_distribution_performance(
                request.content_id,
                request.target_platforms,
                request.analysis_period_days
            )
            
            if analysis:
                # Generate insights
                insights = await self.generate_cross_platform_insights(
                    request.content_id,
                    analysis
                )
                
                # Store insights
                for insight in insights:
                    self.cross_platform_insights[insight.insight_id] = insight
                
                logger.info(f"✅ Distribution request processed: {request.request_id}")
            else:
                logger.warning(f"⚠️ Failed to process distribution request: {request.request_id}")
            
            # Remove from pending
            self.pending_requests.pop(request.request_id, None)
            
        except Exception as e:
            logger.error(f"Error processing distribution request: {str(e)}")
            self.pending_requests.pop(request.request_id, None)
    
    async def generate_cross_platform_insights(
        self,
        content_id: str,
        analysis: DistributionAnalysis
    ) -> List[CrossPlatformInsight]:
        """Generate actionable cross-platform insights"""
        insights = []
        
        try:
            # Platform synergy insights
            if analysis.platform_synergy_matrix:
                for (platform1, platform2), synergy in analysis.platform_synergy_matrix.items():
                    if synergy > 0.7:  # High synergy
                        insight = CrossPlatformInsight(
                            insight_id=f"synergy_{platform1.value}_{platform2.value}_{int(time.time())}",
                            insight_type="platform_synergy",
                            platforms_involved=[platform1, platform2],
                            title=f"High Synergy Between {platform1.value.title()} and {platform2.value.title()}",
                            description=f"Strong audience correlation ({synergy:.1%}) suggests coordinated content strategy",
                            impact_score=synergy * 85,
                            confidence_level=0.8,
                            performance_lift=synergy * 0.15,
                            recommended_actions=[
                                f"Synchronize posting schedules on {platform1.value} and {platform2.value}",
                                "Cross-promote content between platforms",
                                "Develop platform-specific variations of successful content"
                            ]
                        )
                        insights.append(insight)
            
            # Revenue optimization insights
            if analysis.revenue_attribution:
                total_revenue = sum(analysis.revenue_attribution.values())
                if total_revenue > 0:
                    for platform, revenue in analysis.revenue_attribution.items():
                        revenue_share = float(revenue / total_revenue)
                        performance = analysis.platform_performance.get(platform)
                        
                        if performance and revenue_share > 0.4:  # High revenue concentration
                            insight = CrossPlatformInsight(
                                insight_id=f"revenue_focus_{platform.value}_{int(time.time())}",
                                insight_type="revenue_optimization",
                                platforms_involved=[platform],
                                title=f"{platform.value.title()} Revenue Dominance",
                                description=f"Platform generates {revenue_share:.1%} of total revenue",
                                impact_score=revenue_share * 90,
                                confidence_level=0.9,
                                revenue_impact=revenue,
                                recommended_actions=[
                                    f"Increase investment in {platform.value} content production",
                                    "Analyze successful content patterns for replication",
                                    "Consider premium features or monetization options"
                                ]
                            )
                            insights.append(insight)
            
            # Audience expansion insights
            overlap_analysis = analysis.audience_overlap_analysis
            avg_overlap = overlap_analysis.get("average_overlap", 0.5)
            
            if avg_overlap < 0.3:  # Low overlap = good audience diversification
                insight = CrossPlatformInsight(
                    insight_id=f"audience_diversification_{content_id}_{int(time.time())}",
                    insight_type="audience_expansion",
                    platforms_involved=analysis.platforms_analyzed,
                    title="Excellent Audience Diversification",
                    description=f"Low audience overlap ({avg_overlap:.1%}) indicates effective reach diversification",
                    impact_score=80,
                    confidence_level=0.85,
                    audience_overlap=avg_overlap,
                    recommended_actions=[
                        "Maintain current platform mix for maximum reach",
                        "Continue platform-specific content strategies",
                        "Monitor for emerging platform opportunities"
                    ]
                )
                insights.append(insight)
            
            elif avg_overlap > 0.8:  # High overlap = opportunity for expansion
                underused_platforms = [
                    DistributionPlatform.LINKEDIN,
                    DistributionPlatform.REDDIT,
                    DistributionPlatform.PINTEREST
                ]
                
                insight = CrossPlatformInsight(
                    insight_id=f"audience_expansion_{content_id}_{int(time.time())}",
                    insight_type="audience_expansion",
                    platforms_involved=underused_platforms[:2],
                    title="High Audience Overlap - Expansion Opportunity",
                    description=f"High overlap ({avg_overlap:.1%}) suggests untapped audience potential",
                    impact_score=75,
                    confidence_level=0.7,
                    audience_overlap=avg_overlap,
                    recommended_actions=[
                        "Explore new platforms to reach different audiences",
                        "Test content on professional networks like LinkedIn",
                        "Consider niche platforms for specialized content"
                    ]
                )
                insights.append(insight)
            
            # Performance optimization insights
            if analysis.platform_ranking:
                top_platform, top_score = analysis.platform_ranking[0]
                if len(analysis.platform_ranking) > 1:
                    bottom_platform, bottom_score = analysis.platform_ranking[-1]
                    
                    score_gap = top_score - bottom_score
                    if score_gap > 0.05:  # Significant performance gap
                        insight = CrossPlatformInsight(
                            insight_id=f"performance_gap_{top_platform.value}_{bottom_platform.value}_{int(time.time())}",
                            insight_type="performance_optimization",
                            platforms_involved=[top_platform, bottom_platform],
                            title="Significant Performance Gap Detected",
                            description=f"{top_platform.value.title()} outperforming {bottom_platform.value} by {score_gap:.1%}",
                            impact_score=score_gap * 100,
                            confidence_level=0.8,
                            performance_lift=score_gap,
                            recommended_actions=[
                                f"Analyze successful content patterns from {top_platform.value}",
                                f"Optimize content strategy for {bottom_platform.value}",
                                "Consider reallocating resources to top-performing platforms"
                            ]
                        )
                        insights.append(insight)
            
            logger.info(f"📊 Generated {len(insights)} cross-platform insights for {content_id}")
            return insights[:10]  # Limit to top 10 insights
            
        except Exception as e:
            logger.error(f"Error generating cross-platform insights: {str(e)}")
            return []
    
    async def get_distribution_recommendations(
        self,
        content_type: ContentType,
        target_audience: Optional[Dict[str, Any]] = None,
        budget_constraints: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Get platform recommendations for content distribution"""
        try:
            recommendations = {
                "recommended_platforms": [],
                "distribution_strategy": DistributionStrategy.SIMULTANEOUS,
                "timing_recommendations": {},
                "budget_allocation": {},
                "expected_performance": {}
            }
            
            # Filter platforms by content type compatibility
            suitable_platforms = []
            for platform, capabilities in self.platform_capabilities.items():
                if content_type in capabilities.get("content_types", []):
                    suitable_platforms.append(platform)
            
            # Rank platforms by potential
            platform_potential = {}
            for platform in suitable_platforms:
                caps = self.platform_capabilities[platform]
                base_score = self.platform_weights.get(platform, 0.05)
                
                # Adjust for content type fit
                content_fit = 1.0
                if content_type in caps.get("content_types", []):
                    content_fit = caps.get("engagement_multiplier", 1.0)
                
                # Adjust for audience targeting
                targeting_score = 1.0
                if target_audience:
                    # Simplified audience matching
                    targeting_score = 1.1  # Slight boost for targeted content
                
                potential = base_score * content_fit * targeting_score
                platform_potential[platform] = potential
            
            # Select top platforms
            sorted_platforms = sorted(
                platform_potential.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            recommendations["recommended_platforms"] = [
                platform.value for platform, _ in sorted_platforms[:5]
            ]
            
            # Generate timing recommendations
            for platform, _ in sorted_platforms[:5]:
                caps = self.platform_capabilities.get(platform, {})
                peak_hours = caps.get("peak_hours", [12, 18])
                recommendations["timing_recommendations"][platform.value] = {
                    "optimal_hours": peak_hours,
                    "timezone": "UTC",
                    "suggested_frequency": "daily" if platform in [
                        DistributionPlatform.TIKTOK, 
                        DistributionPlatform.INSTAGRAM
                    ] else "2-3 times per week"
                }
            
            # Budget allocation (if provided)
            if budget_constraints:
                total_budget = budget_constraints.get("total", 1000)
                num_platforms = len(recommendations["recommended_platforms"])
                
                for platform in recommendations["recommended_platforms"]:
                    # Weighted budget allocation
                    platform_enum = DistributionPlatform(platform)
                    weight = self.platform_weights.get(platform_enum, 0.05)
                    allocation = total_budget * (weight * num_platforms)
                    recommendations["budget_allocation"][platform] = allocation
            
            # Expected performance estimates
            for platform in recommendations["recommended_platforms"]:
                platform_enum = DistributionPlatform(platform)
                caps = self.platform_capabilities.get(platform_enum, {})
                
                recommendations["expected_performance"][platform] = {
                    "estimated_reach": caps.get("max_reach_potential", 100000) * 0.001,
                    "estimated_engagement_rate": 0.03 * caps.get("engagement_multiplier", 1.0),
                    "revenue_potential": caps.get("revenue_potential", "medium"),
                    "confidence": 0.7
                }
            
            logger.info(f"📊 Generated distribution recommendations for {content_type.value}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating distribution recommendations: {str(e)}")
            return {}
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            summary = {
                "total_content_analyzed": len(self.distribution_data),
                "total_platforms_tracked": len(set(
                    p.platform for performances in self.distribution_data.values()
                    for p in performances
                )),
                "total_insights_generated": len(self.cross_platform_insights),
                "pending_requests": len(self.pending_requests),
                "top_performing_platforms": [],
                "key_insights": [],
                "optimization_opportunities": 0,
                "system_health": "optimal"
            }
            
            # Calculate top performing platforms
            platform_performance = defaultdict(list)
            for performances in self.distribution_data.values():
                for perf in performances:
                    platform_performance[perf.platform].append(perf.engagement_rate)
            
            platform_avg_engagement = {}
            for platform, rates in platform_performance.items():
                if rates:
                    platform_avg_engagement[platform] = statistics.mean(rates)
            
            summary["top_performing_platforms"] = [
                {"platform": platform.value, "avg_engagement": rate}
                for platform, rate in sorted(
                    platform_avg_engagement.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            ]
            
            # Extract key insights
            high_impact_insights = [
                insight for insight in self.cross_platform_insights.values()
                if insight.impact_score > 70
            ]
            
            summary["key_insights"] = [
                {
                    "title": insight.title,
                    "impact_score": insight.impact_score,
                    "platforms": [p.value for p in insight.platforms_involved]
                }
                for insight in high_impact_insights[:5]
            ]
            
            # Count optimization opportunities
            summary["optimization_opportunities"] = sum(
                len(analysis.optimization_opportunities)
                for analysis in self.analysis_results.values()
            )
            
            # System health assessment
            total_data_points = sum(len(performances) for performances in self.distribution_data.values())
            if total_data_points > 1000:
                summary["system_health"] = "optimal"
            elif total_data_points > 100:
                summary["system_health"] = "good"
            else:
                summary["system_health"] = "limited_data"
            
            logger.info("📊 Generated analytics summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {str(e)}")
            return {}


# Global instance
distribution_engine = DistributionIntelligenceEngine()


# Export main class and functions
__all__ = [
    "DistributionIntelligenceEngine",
    "DistributionPlatform",
    "ContentType",
    "DistributionMetric",
    "DistributionStrategy",
    "PlatformPerformance",
    "DistributionAnalysis",
    "DistributionRequest",
    "CrossPlatformInsight",
    "distribution_engine"
]


# Module initialization
logger.info("📊 Distribution Intelligence Engine module loaded")
logger.info("🚀 Enterprise-grade distribution analytics ready")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")