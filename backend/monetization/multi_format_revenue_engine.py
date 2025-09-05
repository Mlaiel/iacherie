"""Multi-Format Revenue Engine - Content Revenue Stream Management
================================================================

Enterprise-grade multi-format content revenue engine providing automated
revenue optimization across audio, video, image, text, voice, and avatar
content formats with intelligent platform integration and performance tracking.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/multi_format_revenue_engine.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContentFormat(str, Enum):
    """Content format types for revenue optimization."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    MUSIC = "music"
    EBOOK = "ebook"
    COURSE = "course"


class RevenueModel(str, Enum):
    """Revenue model types."""
    PAY_PER_VIEW = "pay_per_view"
    SUBSCRIPTION = "subscription"
    LICENSING = "licensing"
    ROYALTY = "royalty"
    COMMISSION = "commission"
    FLAT_FEE = "flat_fee"
    REVENUE_SHARE = "revenue_share"
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    DONATION = "donation"


class PlatformType(str, Enum):
    """Platform types for content distribution."""
    STREAMING = "streaming"
    SOCIAL_MEDIA = "social_media"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION_PLATFORM = "subscription_platform"
    LICENSING_PLATFORM = "licensing_platform"
    EDUCATIONAL = "educational"
    ECOMMERCE = "ecommerce"
    BLOCKCHAIN = "blockchain"


@dataclass
class ContentMetadata:
    """Content metadata for revenue optimization."""
    content_id: str
    format: ContentFormat
    title: str
    description: str
    duration: Optional[float] = None  # Duration in seconds for time-based content
    file_size: Optional[int] = None  # File size in bytes
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformConfig:
    """Platform configuration for revenue optimization."""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    supported_formats: List[ContentFormat]
    revenue_models: List[RevenueModel]
    commission_rate: Decimal
    payout_threshold: Decimal
    payout_schedule: str  # daily, weekly, monthly
    api_config: Dict[str, Any] = field(default_factory=dict)
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    monetization_features: List[str] = field(default_factory=list)


@dataclass
class RevenueStream:
    """Individual revenue stream for content."""
    stream_id: str
    content_id: str
    platform_id: str
    revenue_model: RevenueModel
    rate: Decimal  # Rate/price for the revenue model
    currency: str = "USD"
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueOptimization:
    """Revenue optimization recommendation."""
    optimization_id: str
    content_id: str
    format: ContentFormat
    current_revenue: Decimal
    projected_revenue: Decimal
    confidence: float  # 0.0 to 1.0
    recommendations: List[Dict[str, Any]]
    implementation_effort: str  # low, medium, high
    expected_timeframe: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class MultiFormatRevenueEngine:
    """
    Multi-format content revenue engine.
    
    Provides comprehensive revenue management for all content formats,
    including intelligent platform selection, revenue model optimization,
    and performance tracking across multiple distribution channels.
    """
    
    def __init__(self):
        """Initialize the multi-format revenue engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.platform_configs: Dict[str, PlatformConfig] = {}
        self.content_metadata: Dict[str, ContentMetadata] = {}
        self.revenue_streams: Dict[str, List[RevenueStream]] = {}
        self.optimization_cache: Dict[str, RevenueOptimization] = {}
        self.initialized = False
        
        # Format-specific optimization rules
        self.format_optimization_rules = self._initialize_format_rules()
        
        self.logger.info("MultiFormatRevenueEngine initialized")
    
    def _initialize_format_rules(self) -> Dict[ContentFormat, Dict[str, Any]]:
        """Initialize format-specific optimization rules."""
        return {
            ContentFormat.AUDIO: {
                "optimal_platforms": ["spotify", "apple_music", "amazon_music", "youtube_music"],
                "revenue_models": [RevenueModel.ROYALTY, RevenueModel.LICENSING, RevenueModel.SUBSCRIPTION],
                "quality_factors": ["bitrate", "duration", "genre_popularity"],
                "optimization_focus": ["streaming_optimization", "playlist_inclusion", "artist_branding"],
                "pricing_strategy": "competitive_streaming",
                "content_requirements": {
                    "min_duration": 30,  # seconds
                    "max_duration": 3600,  # seconds
                    "recommended_bitrate": 320,  # kbps
                    "format_support": ["mp3", "wav", "flac"]
                }
            },
            ContentFormat.VIDEO: {
                "optimal_platforms": ["youtube", "vimeo", "tiktok", "instagram", "netflix"],
                "revenue_models": [RevenueModel.ADVERTISING, RevenueModel.SUBSCRIPTION, RevenueModel.PAY_PER_VIEW],
                "quality_factors": ["resolution", "duration", "engagement_rate", "production_quality"],
                "optimization_focus": ["seo_optimization", "thumbnail_optimization", "engagement_metrics"],
                "pricing_strategy": "engagement_based",
                "content_requirements": {
                    "min_duration": 10,  # seconds
                    "max_duration": 7200,  # seconds
                    "recommended_resolution": "1080p",
                    "format_support": ["mp4", "mov", "avi", "webm"]
                }
            },
            ContentFormat.IMAGE: {
                "optimal_platforms": ["shutterstock", "getty_images", "adobe_stock", "unsplash", "instagram"],
                "revenue_models": [RevenueModel.LICENSING, RevenueModel.ROYALTY, RevenueModel.FLAT_FEE],
                "quality_factors": ["resolution", "composition", "uniqueness", "commercial_appeal"],
                "optimization_focus": ["keyword_optimization", "category_placement", "trend_alignment"],
                "pricing_strategy": "market_based",
                "content_requirements": {
                    "min_resolution": "1920x1080",
                    "max_file_size": 50 * 1024 * 1024,  # 50MB
                    "recommended_dpi": 300,
                    "format_support": ["jpg", "png", "tiff", "raw"]
                }
            },
            ContentFormat.TEXT: {
                "optimal_platforms": ["medium", "substack", "wordpress", "kindle", "blog_platforms"],
                "revenue_models": [RevenueModel.SUBSCRIPTION, RevenueModel.ADVERTISING, RevenueModel.SPONSORSHIP],
                "quality_factors": ["word_count", "readability", "seo_score", "engagement"],
                "optimization_focus": ["seo_optimization", "readability_optimization", "content_marketing"],
                "pricing_strategy": "subscription_tiered",
                "content_requirements": {
                    "min_word_count": 300,
                    "max_word_count": 10000,
                    "recommended_readability": "grade_8",
                    "format_support": ["markdown", "html", "plain_text", "pdf"]
                }
            },
            ContentFormat.VOICE: {
                "optimal_platforms": ["podcast_platforms", "audiobook_platforms", "voice_marketplaces"],
                "revenue_models": [RevenueModel.SUBSCRIPTION, RevenueModel.LICENSING, RevenueModel.FLAT_FEE],
                "quality_factors": ["clarity", "emotional_expression", "uniqueness", "commercial_viability"],
                "optimization_focus": ["voice_branding", "niche_targeting", "quality_enhancement"],
                "pricing_strategy": "skill_based",
                "content_requirements": {
                    "min_duration": 15,  # seconds
                    "recommended_sample_rate": 44100,  # Hz
                    "format_support": ["wav", "mp3", "aiff"]
                }
            },
            ContentFormat.AVATAR: {
                "optimal_platforms": ["virtual_platforms", "gaming_platforms", "social_vr", "nft_marketplaces"],
                "revenue_models": [RevenueModel.FLAT_FEE, RevenueModel.ROYALTY, RevenueModel.LICENSING],
                "quality_factors": ["visual_quality", "animation_smoothness", "uniqueness", "platform_compatibility"],
                "optimization_focus": ["platform_optimization", "customization_options", "trending_styles"],
                "pricing_strategy": "premium_positioning",
                "content_requirements": {
                    "polygon_count": {"min": 1000, "max": 50000},
                    "texture_resolution": "1024x1024",
                    "format_support": ["fbx", "obj", "glb", "vrm"]
                }
            },
            ContentFormat.LIVESTREAM: {
                "optimal_platforms": ["twitch", "youtube_live", "facebook_live", "instagram_live"],
                "revenue_models": [RevenueModel.DONATION, RevenueModel.SUBSCRIPTION, RevenueModel.SPONSORSHIP],
                "quality_factors": ["stream_quality", "consistency", "audience_engagement", "content_variety"],
                "optimization_focus": ["audience_building", "engagement_optimization", "monetization_timing"],
                "pricing_strategy": "engagement_driven",
                "content_requirements": {
                    "min_bitrate": 2500,  # kbps
                    "recommended_resolution": "1080p",
                    "min_duration": 600,  # 10 minutes
                    "consistency": "regular_schedule"
                }
            },
            ContentFormat.PODCAST: {
                "optimal_platforms": ["spotify", "apple_podcasts", "google_podcasts", "podcast_platforms"],
                "revenue_models": [RevenueModel.SPONSORSHIP, RevenueModel.SUBSCRIPTION, RevenueModel.ADVERTISING],
                "quality_factors": ["audio_quality", "content_value", "consistency", "audience_growth"],
                "optimization_focus": ["seo_optimization", "audience_retention", "monetization_diversification"],
                "pricing_strategy": "audience_based",
                "content_requirements": {
                    "min_duration": 900,  # 15 minutes
                    "recommended_frequency": "weekly",
                    "audio_quality": "broadcast_standard",
                    "format_support": ["mp3", "wav"]
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the multi-format revenue engine."""
        try:
            # Initialize platform configurations
            await self._initialize_platform_configs()
            
            # Load content metadata and revenue streams
            await self._load_content_data()
            
            self.initialized = True
            self.logger.info("MultiFormatRevenueEngine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MultiFormatRevenueEngine: {e}")
            return False
    
    async def _initialize_platform_configs(self):
        """Initialize platform configurations."""
        # Streaming platforms
        self.platform_configs["spotify"] = PlatformConfig(
            platform_id="spotify",
            platform_name="Spotify",
            platform_type=PlatformType.STREAMING,
            supported_formats=[ContentFormat.AUDIO, ContentFormat.PODCAST],
            revenue_models=[RevenueModel.ROYALTY, RevenueModel.SUBSCRIPTION],
            commission_rate=Decimal("0.3"),
            payout_threshold=Decimal("10.0"),
            payout_schedule="monthly",
            monetization_features=["playlist_placement", "algorithm_optimization", "artist_tools"]
        )
        
        # Video platforms
        self.platform_configs["youtube"] = PlatformConfig(
            platform_id="youtube",
            platform_name="YouTube",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[ContentFormat.VIDEO, ContentFormat.AUDIO, ContentFormat.LIVESTREAM],
            revenue_models=[RevenueModel.ADVERTISING, RevenueModel.SUBSCRIPTION, RevenueModel.SPONSORSHIP],
            commission_rate=Decimal("0.45"),
            payout_threshold=Decimal("100.0"),
            payout_schedule="monthly",
            monetization_features=["ad_revenue", "channel_memberships", "super_chat", "merchandise_shelf"]
        )
        
        # Stock photography platforms
        self.platform_configs["shutterstock"] = PlatformConfig(
            platform_id="shutterstock",
            platform_name="Shutterstock",
            platform_type=PlatformType.MARKETPLACE,
            supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO],
            revenue_models=[RevenueModel.ROYALTY, RevenueModel.LICENSING],
            commission_rate=Decimal("0.15"),
            payout_threshold=Decimal("35.0"),
            payout_schedule="monthly",
            monetization_features=["exclusive_content", "contributor_tiers", "earnings_calculator"]
        )
        
        # Social media platforms
        self.platform_configs["instagram"] = PlatformConfig(
            platform_id="instagram",
            platform_name="Instagram",
            platform_type=PlatformType.SOCIAL_MEDIA,
            supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.LIVESTREAM],
            revenue_models=[RevenueModel.SPONSORSHIP, RevenueModel.ADVERTISING, RevenueModel.COMMISSION],
            commission_rate=Decimal("0.0"),  # Direct creator-brand negotiations
            payout_threshold=Decimal("0.0"),
            payout_schedule="immediate",
            monetization_features=["branded_content", "shopping_tags", "reels_bonus", "creator_fund"]
        )
        
        # NFT and blockchain platforms
        self.platform_configs["opensea"] = PlatformConfig(
            platform_id="opensea",
            platform_name="OpenSea",
            platform_type=PlatformType.BLOCKCHAIN,
            supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO, ContentFormat.AVATAR],
            revenue_models=[RevenueModel.FLAT_FEE, RevenueModel.ROYALTY],
            commission_rate=Decimal("0.025"),
            payout_threshold=Decimal("0.0"),
            payout_schedule="immediate",
            monetization_features=["nft_minting", "royalty_enforcement", "collection_tools"]
        )
        
        self.logger.info(f"Initialized {len(self.platform_configs)} platform configurations")
    
    async def _load_content_data(self):
        """Load existing content metadata and revenue streams."""
        # In production, this would load from database
        self.logger.info("Loading content metadata and revenue streams...")
    
    async def register_content(
        self,
        content_id: str,
        format: ContentFormat,
        metadata: Dict[str, Any]
    ) -> ContentMetadata:
        """Register new content for revenue optimization."""
        try:
            content_metadata = ContentMetadata(
                content_id=content_id,
                format=format,
                title=metadata.get("title", ""),
                description=metadata.get("description", ""),
                duration=metadata.get("duration"),
                file_size=metadata.get("file_size"),
                quality_metrics=metadata.get("quality_metrics", {}),
                tags=metadata.get("tags", []),
                category=metadata.get("category"),
                language=metadata.get("language", "en")
            )
            
            self.content_metadata[content_id] = content_metadata
            
            # Initialize revenue streams for this content
            await self._initialize_content_revenue_streams(content_metadata)
            
            self.logger.info(f"Registered content {content_id} with format {format}")
            return content_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to register content: {e}")
            raise
    
    async def _initialize_content_revenue_streams(self, content: ContentMetadata):
        """Initialize revenue streams for content based on format and platform compatibility."""
        format_rules = self.format_optimization_rules.get(content.format, {})
        optimal_platforms = format_rules.get("optimal_platforms", [])
        revenue_models = format_rules.get("revenue_models", [])
        
        revenue_streams = []
        
        for platform_name in optimal_platforms:
            platform_config = self._find_platform_by_name(platform_name)
            if not platform_config:
                continue
            
            # Check format compatibility
            if content.format not in platform_config.supported_formats:
                continue
            
            # Create revenue streams for compatible revenue models
            for revenue_model in revenue_models:
                if revenue_model in platform_config.revenue_models:
                    stream = RevenueStream(
                        stream_id=str(uuid4()),
                        content_id=content.content_id,
                        platform_id=platform_config.platform_id,
                        revenue_model=revenue_model,
                        rate=await self._calculate_optimal_rate(content, platform_config, revenue_model),
                        performance_metrics={
                            "views": 0,
                            "revenue": 0.0,
                            "engagement_rate": 0.0,
                            "conversion_rate": 0.0
                        },
                        optimization_settings={
                            "auto_optimize": True,
                            "optimization_frequency": "weekly"
                        }
                    )
                    revenue_streams.append(stream)
        
        self.revenue_streams[content.content_id] = revenue_streams
        self.logger.info(f"Initialized {len(revenue_streams)} revenue streams for content {content.content_id}")
    
    def _find_platform_by_name(self, platform_name: str) -> Optional[PlatformConfig]:
        """Find platform configuration by name."""
        for platform_config in self.platform_configs.values():
            if platform_config.platform_name.lower() == platform_name.lower() or platform_config.platform_id == platform_name:
                return platform_config
        return None
    
    async def _calculate_optimal_rate(
        self,
        content: ContentMetadata,
        platform: PlatformConfig,
        revenue_model: RevenueModel
    ) -> Decimal:
        """Calculate optimal rate for content on platform with specific revenue model."""
        format_rules = self.format_optimization_rules.get(content.format, {})
        base_rates = {
            RevenueModel.PAY_PER_VIEW: Decimal("0.99"),
            RevenueModel.SUBSCRIPTION: Decimal("9.99"),
            RevenueModel.LICENSING: Decimal("49.99"),
            RevenueModel.ROYALTY: Decimal("0.05"),  # 5% royalty
            RevenueModel.COMMISSION: Decimal("0.15"),  # 15% commission
            RevenueModel.FLAT_FEE: Decimal("19.99"),
            RevenueModel.REVENUE_SHARE: Decimal("0.50"),  # 50% revenue share
            RevenueModel.ADVERTISING: Decimal("0.01"),  # $0.01 per view
            RevenueModel.SPONSORSHIP: Decimal("100.00"),
            RevenueModel.DONATION: Decimal("5.00")
        }
        
        base_rate = base_rates.get(revenue_model, Decimal("1.00"))
        
        # Adjust rate based on content quality and format
        quality_multiplier = await self._calculate_quality_multiplier(content)
        platform_multiplier = await self._calculate_platform_multiplier(platform, content.format)
        
        optimal_rate = base_rate * quality_multiplier * platform_multiplier
        
        return round(optimal_rate, 2)
    
    async def _calculate_quality_multiplier(self, content: ContentMetadata) -> Decimal:
        """Calculate quality multiplier based on content metrics."""
        multiplier = Decimal("1.0")
        
        # Format-specific quality factors
        format_rules = self.format_optimization_rules.get(content.format, {})
        quality_factors = format_rules.get("quality_factors", [])
        
        for factor in quality_factors:
            if factor in content.quality_metrics:
                factor_value = content.quality_metrics[factor]
                # Simple quality scoring (in production, this would be more sophisticated)
                if isinstance(factor_value, (int, float)):
                    if factor_value > 0.8:  # High quality
                        multiplier *= Decimal("1.2")
                    elif factor_value < 0.4:  # Low quality
                        multiplier *= Decimal("0.8")
        
        return multiplier
    
    async def _calculate_platform_multiplier(self, platform: PlatformConfig, format: ContentFormat) -> Decimal:
        """Calculate platform-specific multiplier."""
        # Premium platforms get higher rates
        premium_platforms = ["netflix", "spotify", "apple_music", "getty_images"]
        
        if platform.platform_id in premium_platforms:
            return Decimal("1.5")
        elif platform.platform_type == PlatformType.BLOCKCHAIN:
            return Decimal("2.0")  # Higher rates for NFT platforms
        else:
            return Decimal("1.0")
    
    async def optimize_content_revenue(self, content_id: str) -> RevenueOptimization:
        """Optimize revenue for specific content."""
        try:
            content = self.content_metadata.get(content_id)
            if not content:
                raise ValueError(f"Content not found: {content_id}")
            
            revenue_streams = self.revenue_streams.get(content_id, [])
            
            # Calculate current revenue
            current_revenue = sum(
                Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                for stream in revenue_streams
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(content, revenue_streams)
            
            # Calculate projected revenue
            projected_revenue = await self._calculate_projected_revenue(content, revenue_streams, recommendations)
            
            # Calculate confidence score
            confidence = await self._calculate_optimization_confidence(content, revenue_streams, recommendations)
            
            optimization = RevenueOptimization(
                optimization_id=str(uuid4()),
                content_id=content_id,
                format=content.format,
                current_revenue=current_revenue,
                projected_revenue=projected_revenue,
                confidence=confidence,
                recommendations=recommendations,
                implementation_effort=self._assess_implementation_effort(recommendations),
                expected_timeframe=self._estimate_optimization_timeframe(recommendations)
            )
            
            self.optimization_cache[content_id] = optimization
            
            self.logger.info(f"Generated revenue optimization for content {content_id}")
            return optimization
            
        except Exception as e:
            self.logger.error(f"Failed to optimize content revenue: {e}")
            raise
    
    async def _generate_optimization_recommendations(
        self,
        content: ContentMetadata,
        streams: List[RevenueStream]
    ) -> List[Dict[str, Any]]:
        """Generate specific optimization recommendations."""
        recommendations = []
        format_rules = self.format_optimization_rules.get(content.format, {})
        
        # Platform optimization recommendations
        current_platforms = {stream.platform_id for stream in streams}
        optimal_platforms = format_rules.get("optimal_platforms", [])
        
        missing_platforms = []
        for platform_name in optimal_platforms:
            platform_config = self._find_platform_by_name(platform_name)
            if platform_config and platform_config.platform_id not in current_platforms:
                missing_platforms.append(platform_config)
        
        if missing_platforms:
            recommendations.append({
                "type": "platform_expansion",
                "priority": "high",
                "description": f"Expand to {len(missing_platforms)} additional platforms",
                "platforms": [p.platform_name for p in missing_platforms],
                "expected_impact": "25-40% revenue increase",
                "implementation_time": "1-2 weeks"
            })
        
        # Revenue model optimization
        underperforming_streams = self._identify_underperforming_streams(streams)
        if underperforming_streams:
            recommendations.append({
                "type": "revenue_model_optimization",
                "priority": "medium",
                "description": "Optimize revenue models for underperforming streams",
                "affected_streams": len(underperforming_streams),
                "expected_impact": "15-25% revenue increase",
                "implementation_time": "1 week"
            })
        
        # Content quality improvements
        quality_recommendations = await self._analyze_content_quality(content)
        if quality_recommendations:
            recommendations.extend(quality_recommendations)
        
        # Pricing optimization
        pricing_recommendations = await self._analyze_pricing_optimization(streams)
        if pricing_recommendations:
            recommendations.extend(pricing_recommendations)
        
        return recommendations
    
    def _identify_underperforming_streams(self, streams: List[RevenueStream]) -> List[RevenueStream]:
        """Identify underperforming revenue streams."""
        if not streams:
            return []
        
        # Calculate performance metrics
        revenues = [
            stream.performance_metrics.get("revenue", 0.0) for stream in streams
        ]
        
        if not revenues or max(revenues) == 0:
            return []
        
        avg_revenue = sum(revenues) / len(revenues)
        threshold = avg_revenue * 0.3  # Below 30% of average is underperforming
        
        underperforming = []
        for stream in streams:
            stream_revenue = stream.performance_metrics.get("revenue", 0.0)
            if stream_revenue < threshold:
                underperforming.append(stream)
        
        return underperforming
    
    async def _analyze_content_quality(self, content: ContentMetadata) -> List[Dict[str, Any]]:
        """Analyze content quality and generate improvement recommendations."""
        recommendations = []
        format_rules = self.format_optimization_rules.get(content.format, {})
        content_requirements = format_rules.get("content_requirements", {})
        
        # Check duration requirements
        if content.format in [ContentFormat.AUDIO, ContentFormat.VIDEO] and content.duration:
            min_duration = content_requirements.get("min_duration", 0)
            max_duration = content_requirements.get("max_duration", float('inf'))
            
            if content.duration < min_duration:
                recommendations.append({
                    "type": "content_length_optimization",
                    "priority": "medium",
                    "description": f"Content duration ({content.duration}s) below optimal minimum ({min_duration}s)",
                    "suggestion": "Consider extending content length",
                    "expected_impact": "10-15% engagement increase"
                })
            elif content.duration > max_duration:
                recommendations.append({
                    "type": "content_length_optimization",
                    "priority": "low",
                    "description": f"Content duration ({content.duration}s) above optimal maximum ({max_duration}s)",
                    "suggestion": "Consider splitting into multiple parts",
                    "expected_impact": "5-10% retention improvement"
                })
        
        # Check quality metrics
        quality_factors = format_rules.get("quality_factors", [])
        for factor in quality_factors:
            if factor in content.quality_metrics:
                quality_value = content.quality_metrics[factor]
                if isinstance(quality_value, (int, float)) and quality_value < 0.6:
                    recommendations.append({
                        "type": "quality_improvement",
                        "priority": "high",
                        "description": f"Low {factor} score ({quality_value})",
                        "suggestion": f"Improve {factor} to increase monetization potential",
                        "expected_impact": "20-30% revenue increase"
                    })
        
        return recommendations
    
    async def _analyze_pricing_optimization(self, streams: List[RevenueStream]) -> List[Dict[str, Any]]:
        """Analyze pricing and generate optimization recommendations."""
        recommendations = []
        
        if not streams:
            return recommendations
        
        # Analyze pricing competitiveness
        for stream in streams:
            # Simple pricing analysis (in production, this would use market data)
            current_rate = stream.rate
            performance = stream.performance_metrics.get("conversion_rate", 0.0)
            
            if performance < 0.02:  # Low conversion rate
                recommendations.append({
                    "type": "pricing_optimization",
                    "priority": "medium",
                    "description": f"Low conversion rate ({performance:.2%}) on {stream.platform_id}",
                    "suggestion": "Consider reducing price to improve conversion",
                    "current_rate": float(current_rate),
                    "suggested_rate": float(current_rate * Decimal("0.8")),
                    "expected_impact": "30-50% conversion increase"
                })
            elif performance > 0.1:  # High conversion rate
                recommendations.append({
                    "type": "pricing_optimization",
                    "priority": "low",
                    "description": f"High conversion rate ({performance:.2%}) on {stream.platform_id}",
                    "suggestion": "Consider increasing price to maximize revenue",
                    "current_rate": float(current_rate),
                    "suggested_rate": float(current_rate * Decimal("1.2")),
                    "expected_impact": "15-25% revenue increase"
                })
        
        return recommendations
    
    async def _calculate_projected_revenue(
        self,
        content: ContentMetadata,
        streams: List[RevenueStream],
        recommendations: List[Dict[str, Any]]
    ) -> Decimal:
        """Calculate projected revenue after implementing recommendations."""
        current_revenue = sum(
            Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
            for stream in streams
        )
        
        if current_revenue == 0:
            # Estimate initial revenue based on format and platforms
            format_rules = self.format_optimization_rules.get(content.format, {})
            estimated_revenue = Decimal("100.0")  # Base estimate
            
            # Adjust based on number of platforms
            platform_multiplier = len(streams) * Decimal("0.5")
            estimated_revenue *= (1 + platform_multiplier)
            
            return estimated_revenue
        
        # Calculate improvement from recommendations
        total_improvement = Decimal("0.0")
        for recommendation in recommendations:
            impact_str = recommendation.get("expected_impact", "0%")
            
            # Extract percentage from impact string
            import re
            match = re.search(r'(\d+)', impact_str)
            if match:
                impact_percentage = Decimal(match.group(1)) / 100
                total_improvement += impact_percentage
        
        # Cap total improvement at 100%
        total_improvement = min(total_improvement, Decimal("1.0"))
        
        projected_revenue = current_revenue * (1 + total_improvement)
        return projected_revenue
    
    async def _calculate_optimization_confidence(
        self,
        content: ContentMetadata,
        streams: List[RevenueStream],
        recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for optimization recommendations."""
        confidence_factors = []
        
        # Content quality factor
        quality_metrics = content.quality_metrics
        if quality_metrics:
            avg_quality = sum(
                float(v) for v in quality_metrics.values()
                if isinstance(v, (int, float))
            ) / len(quality_metrics)
            confidence_factors.append(avg_quality)
        
        # Platform coverage factor
        format_rules = self.format_optimization_rules.get(content.format, {})
        optimal_platforms = format_rules.get("optimal_platforms", [])
        current_platforms = {stream.platform_id for stream in streams}
        
        platform_coverage = len(current_platforms) / len(optimal_platforms) if optimal_platforms else 0
        confidence_factors.append(platform_coverage)
        
        # Recommendation quality factor
        high_priority_recs = sum(
            1 for rec in recommendations
            if rec.get("priority") == "high"
        )
        rec_quality = min(high_priority_recs / 3, 1.0) if recommendations else 0.5
        confidence_factors.append(rec_quality)
        
        # Calculate overall confidence
        if confidence_factors:
            overall_confidence = sum(confidence_factors) / len(confidence_factors)
        else:
            overall_confidence = 0.5
        
        return min(max(overall_confidence, 0.0), 1.0)
    
    def _assess_implementation_effort(self, recommendations: List[Dict[str, Any]]) -> str:
        """Assess implementation effort for recommendations."""
        effort_scores = {
            "platform_expansion": 3,
            "revenue_model_optimization": 2,
            "content_length_optimization": 3,
            "quality_improvement": 4,
            "pricing_optimization": 1
        }
        
        total_effort = sum(
            effort_scores.get(rec.get("type", "unknown"), 2)
            for rec in recommendations
        )
        
        if total_effort <= 3:
            return "low"
        elif total_effort <= 6:
            return "medium"
        else:
            return "high"
    
    def _estimate_optimization_timeframe(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estimate timeframe for implementing recommendations."""
        timeframes = []
        
        for rec in recommendations:
            implementation_time = rec.get("implementation_time", "1 week")
            if "day" in implementation_time.lower():
                timeframes.append(1)
            elif "week" in implementation_time.lower():
                weeks = 1
                if "2" in implementation_time:
                    weeks = 2
                elif "3" in implementation_time:
                    weeks = 3
                timeframes.append(weeks)
            elif "month" in implementation_time.lower():
                timeframes.append(4)
        
        if not timeframes:
            return "1-2 weeks"
        
        max_timeframe = max(timeframes)
        if max_timeframe <= 1:
            return "1 week"
        elif max_timeframe <= 2:
            return "1-2 weeks"
        elif max_timeframe <= 4:
            return "2-4 weeks"
        else:
            return "1-2 months"
    
    async def get_format_performance_summary(self, format: ContentFormat) -> Dict[str, Any]:
        """Get performance summary for a specific content format."""
        try:
            format_content = [
                (content_id, content) for content_id, content in self.content_metadata.items()
                if content.format == format
            ]
            
            if not format_content:
                return {
                    "format": format,
                    "total_content": 0,
                    "total_revenue": 0.0,
                    "avg_revenue_per_content": 0.0,
                    "top_platforms": [],
                    "optimization_opportunities": 0
                }
            
            # Calculate metrics
            total_revenue = Decimal("0.0")
            platform_revenue = defaultdict(Decimal)
            total_streams = 0
            
            for content_id, content in format_content:
                streams = self.revenue_streams.get(content_id, [])
                total_streams += len(streams)
                
                for stream in streams:
                    stream_revenue = Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                    total_revenue += stream_revenue
                    platform_revenue[stream.platform_id] += stream_revenue
            
            # Top platforms by revenue
            top_platforms = sorted(
                platform_revenue.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Count optimization opportunities
            optimization_count = sum(
                1 for content_id, _ in format_content
                if content_id in self.optimization_cache
            )
            
            return {
                "format": format,
                "total_content": len(format_content),
                "total_revenue": float(total_revenue),
                "avg_revenue_per_content": float(total_revenue / len(format_content)) if format_content else 0.0,
                "total_streams": total_streams,
                "avg_streams_per_content": total_streams / len(format_content) if format_content else 0.0,
                "top_platforms": [
                    {"platform_id": platform_id, "revenue": float(revenue)}
                    for platform_id, revenue in top_platforms
                ],
                "optimization_opportunities": optimization_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get format performance summary: {e}")
            raise
    
    async def get_platform_compatibility_matrix(self) -> Dict[str, Any]:
        """Get compatibility matrix showing which formats work on which platforms."""
        try:
            compatibility_matrix = {}
            
            for platform_id, platform_config in self.platform_configs.items():
                platform_info = {
                    "platform_name": platform_config.platform_name,
                    "platform_type": platform_config.platform_type,
                    "supported_formats": platform_config.supported_formats,
                    "revenue_models": platform_config.revenue_models,
                    "commission_rate": float(platform_config.commission_rate),
                    "payout_threshold": float(platform_config.payout_threshold),
                    "monetization_features": platform_config.monetization_features
                }
                compatibility_matrix[platform_id] = platform_info
            
            # Add format-specific recommendations
            format_recommendations = {}
            for format, rules in self.format_optimization_rules.items():
                format_recommendations[format] = {
                    "optimal_platforms": rules.get("optimal_platforms", []),
                    "revenue_models": rules.get("revenue_models", []),
                    "optimization_focus": rules.get("optimization_focus", []),
                    "content_requirements": rules.get("content_requirements", {})
                }
            
            return {
                "platform_compatibility": compatibility_matrix,
                "format_recommendations": format_recommendations,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform compatibility matrix: {e}")
            raise
    
    async def update_stream_performance(
        self,
        content_id: str,
        stream_id: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update performance metrics for a specific revenue stream."""
        try:
            streams = self.revenue_streams.get(content_id, [])
            
            for stream in streams:
                if stream.stream_id == stream_id:
                    stream.performance_metrics.update(performance_data)
                    stream.last_updated = datetime.utcnow()
                    
                    # Invalidate optimization cache for this content
                    if content_id in self.optimization_cache:
                        del self.optimization_cache[content_id]
                    
                    self.logger.info(f"Updated performance for stream {stream_id}")
                    return True
            
            self.logger.warning(f"Revenue stream {stream_id} not found for content {content_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update stream performance: {e}")
            return False


# Global instance getter
_multi_format_revenue_engine = None

async def get_multi_format_revenue_engine() -> MultiFormatRevenueEngine:
    """Get the global multi-format revenue engine instance."""
    global _multi_format_revenue_engine
    
    if _multi_format_revenue_engine is None:
        _multi_format_revenue_engine = MultiFormatRevenueEngine()
        await _multi_format_revenue_engine.initialize()
    
    return _multi_format_revenue_engine