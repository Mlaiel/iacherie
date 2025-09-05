"""Creator Monetization Orchestrator - Central Creator Monetization Management
========================================================================

Enterprise-grade creator monetization orchestrator providing centralized
management of multi-format content monetization, creator-type optimization,
and revenue stream coordination for content creators across all platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/creator_monetization_orchestrator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class CreatorType(str, Enum):
    """Creator type classifications."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class ContentFormat(str, Enum):
    """Content format types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"


class RevenueStreamType(str, Enum):
    """Revenue stream types."""
    STREAMING_ROYALTIES = "streaming_royalties"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    SUBSCRIPTIONS = "subscriptions"
    SPONSORSHIPS = "sponsorships"
    AFFILIATE_MARKETING = "affiliate_marketing"
    LIVE_EVENTS = "live_events"
    NFT_SALES = "nft_sales"
    COURSE_SALES = "course_sales"
    TIPS_DONATIONS = "tips_donations"


@dataclass
class CreatorProfile:
    """Creator monetization profile."""
    creator_id: str
    creator_type: CreatorType
    content_formats: List[ContentFormat]
    revenue_preferences: Dict[str, Any]
    monetization_goals: Dict[str, Any]
    preferred_platforms: List[str]
    payout_preferences: Dict[str, Any]
    tax_settings: Dict[str, Any]
    auto_optimization: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueStream:
    """Revenue stream definition."""
    stream_id: str
    creator_id: str
    stream_type: RevenueStreamType
    content_format: ContentFormat
    platform: str
    revenue_model: Dict[str, Any]
    optimization_settings: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MonetizationStrategy:
    """Creator monetization strategy."""
    strategy_id: str
    creator_id: str
    creator_type: CreatorType
    revenue_streams: List[RevenueStream]
    optimization_rules: Dict[str, Any]
    target_revenue: Decimal
    current_revenue: Decimal
    performance_metrics: Dict[str, Any]
    last_optimized: datetime = field(default_factory=datetime.utcnow)


class CreatorMonetizationOrchestrator:
    """
    Central orchestrator for creator monetization management.
    
    Provides comprehensive monetization coordination for content creators,
    including multi-format revenue optimization, creator-type specialization,
    and platform integration management.
    """
    
    def __init__(self):
        """Initialize the creator monetization orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.revenue_streams: Dict[str, List[RevenueStream]] = {}
        self.monetization_strategies: Dict[str, MonetizationStrategy] = {}
        self.initialized = False
        
        # Creator-type specific strategies
        self.creator_strategies = self._initialize_creator_strategies()
        
        self.logger.info("CreatorMonetizationOrchestrator initialized")
    
    def _initialize_creator_strategies(self) -> Dict[CreatorType, Dict[str, Any]]:
        """Initialize creator-type specific monetization strategies."""
        return {
            CreatorType.MUSICIAN: {
                "primary_formats": [ContentFormat.AUDIO, ContentFormat.VIDEO],
                "revenue_streams": [
                    RevenueStreamType.STREAMING_ROYALTIES,
                    RevenueStreamType.LICENSING,
                    RevenueStreamType.MERCHANDISE,
                    RevenueStreamType.LIVE_EVENTS,
                    RevenueStreamType.NFT_SALES
                ],
                "platforms": ["spotify", "apple_music", "youtube", "bandcamp", "soundcloud"],
                "optimization_focus": ["genre_pricing", "audience_analysis", "release_timing"],
                "collaboration_types": ["band_revenue_sharing", "producer_splits", "remix_royalties"]
            },
            CreatorType.BLOGGER: {
                "primary_formats": [ContentFormat.TEXT, ContentFormat.IMAGE],
                "revenue_streams": [
                    RevenueStreamType.AFFILIATE_MARKETING,
                    RevenueStreamType.SPONSORSHIPS,
                    RevenueStreamType.SUBSCRIPTIONS,
                    RevenueStreamType.COURSE_SALES
                ],
                "platforms": ["wordpress", "medium", "substack", "linkedin"],
                "optimization_focus": ["content_monetization", "seo_revenue", "conversion_optimization"],
                "collaboration_types": ["guest_posting", "content_partnerships", "cross_promotion"]
            },
            CreatorType.PHOTOGRAPHER: {
                "primary_formats": [ContentFormat.IMAGE],
                "revenue_streams": [
                    RevenueStreamType.LICENSING,
                    RevenueStreamType.NFT_SALES,
                    RevenueStreamType.LIVE_EVENTS,
                    RevenueStreamType.COURSE_SALES
                ],
                "platforms": ["shutterstock", "getty_images", "adobe_stock", "instagram"],
                "optimization_focus": ["image_value_prediction", "licensing_optimization", "market_trends"],
                "collaboration_types": ["model_revenue_sharing", "event_partnerships", "brand_collaborations"]
            },
            CreatorType.INFLUENCER: {
                "primary_formats": [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT],
                "revenue_streams": [
                    RevenueStreamType.SPONSORSHIPS,
                    RevenueStreamType.AFFILIATE_MARKETING,
                    RevenueStreamType.MERCHANDISE,
                    RevenueStreamType.COURSE_SALES
                ],
                "platforms": ["instagram", "tiktok", "youtube", "twitter"],
                "optimization_focus": ["engagement_monetization", "brand_matching", "audience_analysis"],
                "collaboration_types": ["influencer_networks", "campaign_partnerships", "joint_ventures"]
            },
            CreatorType.COMEDIAN: {
                "primary_formats": [ContentFormat.VIDEO, ContentFormat.AUDIO],
                "revenue_streams": [
                    RevenueStreamType.LIVE_EVENTS,
                    RevenueStreamType.STREAMING_ROYALTIES,
                    RevenueStreamType.MERCHANDISE,
                    RevenueStreamType.SUBSCRIPTIONS
                ],
                "platforms": ["youtube", "netflix", "spotify", "podcast_platforms"],
                "optimization_focus": ["performance_optimization", "audience_prediction", "venue_matching"],
                "collaboration_types": ["comedy_partnerships", "writing_collaborations", "tour_revenue_sharing"]
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the creator monetization orchestrator."""
        try:
            # Load existing creator profiles and strategies
            await self._load_creator_data()
            
            self.initialized = True
            self.logger.info("CreatorMonetizationOrchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CreatorMonetizationOrchestrator: {e}")
            return False
    
    async def _load_creator_data(self):
        """Load existing creator profiles and monetization data."""
        # In production, this would load from database
        # For now, initialize with empty data structures
        self.logger.info("Loading creator monetization data...")
    
    async def create_creator_profile(
        self,
        creator_id: str,
        creator_type: CreatorType,
        content_formats: List[ContentFormat],
        preferences: Optional[Dict[str, Any]] = None
    ) -> CreatorProfile:
        """Create a new creator monetization profile."""
        try:
            # Get default strategy for creator type
            default_strategy = self.creator_strategies.get(creator_type, {})
            
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_type=creator_type,
                content_formats=content_formats,
                revenue_preferences=preferences or {},
                monetization_goals=default_strategy.get("optimization_focus", []),
                preferred_platforms=default_strategy.get("platforms", []),
                payout_preferences={"schedule": "monthly", "minimum_threshold": 10.0},
                tax_settings={"jurisdiction": "default", "tax_rate": 0.0}
            )
            
            self.creator_profiles[creator_id] = profile
            
            # Initialize revenue streams for this creator
            await self._initialize_creator_revenue_streams(profile)
            
            self.logger.info(f"Created creator profile for {creator_id} ({creator_type})")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to create creator profile: {e}")
            raise
    
    async def _initialize_creator_revenue_streams(self, profile: CreatorProfile):
        """Initialize revenue streams for a creator based on their profile."""
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        suggested_streams = creator_strategy.get("revenue_streams", [])
        
        revenue_streams = []
        for stream_type in suggested_streams:
            for content_format in profile.content_formats:
                if self._is_compatible_format(stream_type, content_format):
                    stream = RevenueStream(
                        stream_id=str(uuid4()),
                        creator_id=profile.creator_id,
                        stream_type=stream_type,
                        content_format=content_format,
                        platform="default",
                        revenue_model={"type": "percentage", "rate": 0.7},
                        optimization_settings={"auto_optimize": True},
                        performance_metrics={"revenue": 0.0, "views": 0, "engagement": 0.0}
                    )
                    revenue_streams.append(stream)
        
        self.revenue_streams[profile.creator_id] = revenue_streams
        self.logger.info(f"Initialized {len(revenue_streams)} revenue streams for creator {profile.creator_id}")
    
    def _is_compatible_format(self, stream_type: RevenueStreamType, content_format: ContentFormat) -> bool:
        """Check if a revenue stream type is compatible with a content format."""
        compatibility_matrix = {
            RevenueStreamType.STREAMING_ROYALTIES: [ContentFormat.AUDIO, ContentFormat.VIDEO],
            RevenueStreamType.LICENSING: [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.IMAGE],
            RevenueStreamType.MERCHANDISE: [ContentFormat.IMAGE, ContentFormat.TEXT],
            RevenueStreamType.SUBSCRIPTIONS: [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.TEXT],
            RevenueStreamType.SPONSORSHIPS: [ContentFormat.VIDEO, ContentFormat.IMAGE, ContentFormat.TEXT],
            RevenueStreamType.AFFILIATE_MARKETING: [ContentFormat.TEXT, ContentFormat.VIDEO],
            RevenueStreamType.LIVE_EVENTS: [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.LIVESTREAM],
            RevenueStreamType.NFT_SALES: [ContentFormat.IMAGE, ContentFormat.AUDIO, ContentFormat.VIDEO],
            RevenueStreamType.COURSE_SALES: [ContentFormat.VIDEO, ContentFormat.TEXT],
            RevenueStreamType.TIPS_DONATIONS: [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.LIVESTREAM]
        }
        
        compatible_formats = compatibility_matrix.get(stream_type, [])
        return content_format in compatible_formats
    
    async def optimize_creator_monetization(self, creator_id: str) -> MonetizationStrategy:
        """Optimize monetization strategy for a specific creator."""
        try:
            profile = self.creator_profiles.get(creator_id)
            if not profile:
                raise ValueError(f"Creator profile not found for ID: {creator_id}")
            
            # Get current revenue streams
            current_streams = self.revenue_streams.get(creator_id, [])
            
            # Calculate current performance
            current_revenue = sum(
                Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                for stream in current_streams
            )
            
            # Generate optimization recommendations
            optimization_rules = await self._generate_optimization_rules(profile, current_streams)
            
            # Create monetization strategy
            strategy = MonetizationStrategy(
                strategy_id=str(uuid4()),
                creator_id=creator_id,
                creator_type=profile.creator_type,
                revenue_streams=current_streams,
                optimization_rules=optimization_rules,
                target_revenue=current_revenue * Decimal("1.2"),  # 20% increase target
                current_revenue=current_revenue,
                performance_metrics=self._calculate_performance_metrics(current_streams)
            )
            
            self.monetization_strategies[creator_id] = strategy
            
            self.logger.info(f"Optimized monetization strategy for creator {creator_id}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to optimize creator monetization: {e}")
            raise
    
    async def _generate_optimization_rules(
        self,
        profile: CreatorProfile,
        streams: List[RevenueStream]
    ) -> Dict[str, Any]:
        """Generate optimization rules based on creator profile and performance."""
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        
        return {
            "content_optimization": {
                "focus_formats": creator_strategy.get("primary_formats", []),
                "suggested_platforms": creator_strategy.get("platforms", []),
                "optimization_areas": creator_strategy.get("optimization_focus", [])
            },
            "revenue_optimization": {
                "underperforming_streams": self._identify_underperforming_streams(streams),
                "growth_opportunities": self._identify_growth_opportunities(profile, streams),
                "platform_recommendations": self._generate_platform_recommendations(profile)
            },
            "collaboration_opportunities": {
                "types": creator_strategy.get("collaboration_types", []),
                "potential_partners": [],
                "revenue_sharing_models": []
            }
        }
    
    def _identify_underperforming_streams(self, streams: List[RevenueStream]) -> List[str]:
        """Identify underperforming revenue streams."""
        underperforming = []
        
        if not streams:
            return underperforming
        
        # Calculate average performance
        total_revenue = sum(
            stream.performance_metrics.get("revenue", 0.0) for stream in streams
        )
        avg_revenue = total_revenue / len(streams) if streams else 0
        
        # Identify streams below average
        for stream in streams:
            stream_revenue = stream.performance_metrics.get("revenue", 0.0)
            if stream_revenue < avg_revenue * 0.5:  # Below 50% of average
                underperforming.append(stream.stream_id)
        
        return underperforming
    
    def _identify_growth_opportunities(
        self,
        profile: CreatorProfile,
        streams: List[RevenueStream]
    ) -> List[Dict[str, Any]]:
        """Identify growth opportunities for creator."""
        opportunities = []
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        suggested_streams = creator_strategy.get("revenue_streams", [])
        
        # Find missing revenue stream types
        current_stream_types = {stream.stream_type for stream in streams}
        
        for suggested_stream in suggested_streams:
            if suggested_stream not in current_stream_types:
                opportunities.append({
                    "type": "new_revenue_stream",
                    "stream_type": suggested_stream,
                    "potential_impact": "medium",
                    "effort_required": "low"
                })
        
        # Check for underutilized content formats
        current_formats = {stream.content_format for stream in streams}
        
        for content_format in profile.content_formats:
            if content_format not in current_formats:
                opportunities.append({
                    "type": "content_format_expansion",
                    "content_format": content_format,
                    "potential_impact": "high",
                    "effort_required": "medium"
                })
        
        return opportunities
    
    def _generate_platform_recommendations(self, profile: CreatorProfile) -> List[Dict[str, Any]]:
        """Generate platform recommendations for creator."""
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        recommended_platforms = creator_strategy.get("platforms", [])
        
        recommendations = []
        for platform in recommended_platforms:
            if platform not in profile.preferred_platforms:
                recommendations.append({
                    "platform": platform,
                    "reason": f"High revenue potential for {profile.creator_type}",
                    "priority": "medium",
                    "setup_complexity": "low"
                })
        
        return recommendations
    
    def _calculate_performance_metrics(self, streams: List[RevenueStream]) -> Dict[str, Any]:
        """Calculate overall performance metrics for revenue streams."""
        if not streams:
            return {"total_revenue": 0.0, "active_streams": 0, "avg_performance": 0.0}
        
        total_revenue = sum(
            stream.performance_metrics.get("revenue", 0.0) for stream in streams
        )
        active_streams = sum(1 for stream in streams if stream.is_active)
        avg_performance = total_revenue / len(streams) if streams else 0.0
        
        return {
            "total_revenue": total_revenue,
            "active_streams": active_streams,
            "total_streams": len(streams),
            "avg_performance": avg_performance,
            "top_performing_stream": max(
                streams,
                key=lambda s: s.performance_metrics.get("revenue", 0.0)
            ).stream_type if streams else None
        }
    
    async def get_creator_revenue_summary(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive revenue summary for a creator."""
        try:
            profile = self.creator_profiles.get(creator_id)
            if not profile:
                raise ValueError(f"Creator profile not found for ID: {creator_id}")
            
            streams = self.revenue_streams.get(creator_id, [])
            strategy = self.monetization_strategies.get(creator_id)
            
            # Calculate revenue metrics
            total_revenue = sum(
                Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                for stream in streams
            )
            
            # Revenue by stream type
            revenue_by_type = {}
            for stream in streams:
                stream_type = stream.stream_type
                stream_revenue = Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                revenue_by_type[stream_type] = revenue_by_type.get(stream_type, Decimal("0")) + stream_revenue
            
            # Revenue by platform
            revenue_by_platform = {}
            for stream in streams:
                platform = stream.platform
                stream_revenue = Decimal(str(stream.performance_metrics.get("revenue", 0.0)))
                revenue_by_platform[platform] = revenue_by_platform.get(platform, Decimal("0")) + stream_revenue
            
            return {
                "creator_id": creator_id,
                "creator_type": profile.creator_type,
                "total_revenue": float(total_revenue),
                "active_streams": len([s for s in streams if s.is_active]),
                "revenue_by_type": {k: float(v) for k, v in revenue_by_type.items()},
                "revenue_by_platform": {k: float(v) for k, v in revenue_by_platform.items()},
                "target_revenue": float(strategy.target_revenue) if strategy else None,
                "optimization_status": "active" if strategy else "pending",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get creator revenue summary: {e}")
            raise
    
    async def update_stream_performance(
        self,
        creator_id: str,
        stream_id: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update performance metrics for a specific revenue stream."""
        try:
            streams = self.revenue_streams.get(creator_id, [])
            
            for stream in streams:
                if stream.stream_id == stream_id:
                    stream.performance_metrics.update(performance_data)
                    self.logger.info(f"Updated performance for stream {stream_id}")
                    return True
            
            self.logger.warning(f"Revenue stream {stream_id} not found for creator {creator_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update stream performance: {e}")
            return False
    
    async def get_monetization_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get AI-powered monetization insights for a creator."""
        try:
            profile = self.creator_profiles.get(creator_id)
            if not profile:
                raise ValueError(f"Creator profile not found for ID: {creator_id}")
            
            streams = self.revenue_streams.get(creator_id, [])
            
            # Generate insights based on performance data
            insights = {
                "revenue_trends": self._analyze_revenue_trends(streams),
                "optimization_opportunities": self._identify_optimization_opportunities(profile, streams),
                "competitive_analysis": self._generate_competitive_insights(profile),
                "growth_recommendations": self._generate_growth_recommendations(profile, streams),
                "risk_assessment": self._assess_monetization_risks(streams)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to get monetization insights: {e}")
            raise
    
    def _analyze_revenue_trends(self, streams: List[RevenueStream]) -> Dict[str, Any]:
        """Analyze revenue trends across streams."""
        return {
            "trend": "stable",  # In production, this would analyze historical data
            "growth_rate": 0.05,
            "seasonal_patterns": [],
            "top_performing_formats": [stream.content_format for stream in streams[:3]]
        }
    
    def _identify_optimization_opportunities(
        self,
        profile: CreatorProfile,
        streams: List[RevenueStream]
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []
        
        # Check for format diversification
        current_formats = {stream.content_format for stream in streams}
        if len(current_formats) < len(profile.content_formats):
            opportunities.append({
                "type": "format_diversification",
                "description": "Expand to unused content formats",
                "impact": "medium",
                "effort": "low"
            })
        
        # Check for platform expansion
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        recommended_platforms = creator_strategy.get("platforms", [])
        current_platforms = {stream.platform for stream in streams}
        
        missing_platforms = set(recommended_platforms) - current_platforms
        if missing_platforms:
            opportunities.append({
                "type": "platform_expansion",
                "description": f"Consider expanding to {', '.join(missing_platforms)}",
                "impact": "high",
                "effort": "medium"
            })
        
        return opportunities
    
    def _generate_competitive_insights(self, profile: CreatorProfile) -> Dict[str, Any]:
        """Generate competitive analysis insights."""
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        
        return {
            "market_position": "emerging",  # In production, analyze against competitors
            "competitive_advantages": creator_strategy.get("optimization_focus", []),
            "market_opportunities": creator_strategy.get("revenue_streams", []),
            "benchmark_metrics": {
                "avg_revenue_per_stream": 1000.0,
                "top_performer_revenue": 5000.0,
                "market_growth_rate": 0.15
            }
        }
    
    def _generate_growth_recommendations(
        self,
        profile: CreatorProfile,
        streams: List[RevenueStream]
    ) -> List[Dict[str, Any]]:
        """Generate specific growth recommendations."""
        recommendations = []
        
        # Revenue stream recommendations
        current_stream_types = {stream.stream_type for stream in streams}
        creator_strategy = self.creator_strategies.get(profile.creator_type, {})
        suggested_streams = creator_strategy.get("revenue_streams", [])
        
        for stream_type in suggested_streams:
            if stream_type not in current_stream_types:
                recommendations.append({
                    "type": "new_revenue_stream",
                    "action": f"Add {stream_type} revenue stream",
                    "expected_impact": "20% revenue increase",
                    "timeline": "1-3 months",
                    "priority": "high"
                })
        
        # Collaboration recommendations
        collaboration_types = creator_strategy.get("collaboration_types", [])
        if collaboration_types:
            recommendations.append({
                "type": "collaboration",
                "action": f"Explore {collaboration_types[0]} opportunities",
                "expected_impact": "30% audience growth",
                "timeline": "2-6 months",
                "priority": "medium"
            })
        
        return recommendations
    
    def _assess_monetization_risks(self, streams: List[RevenueStream]) -> Dict[str, Any]:
        """Assess risks in current monetization approach."""
        risks = []
        
        # Platform concentration risk
        platform_revenue = {}
        for stream in streams:
            platform = stream.platform
            revenue = stream.performance_metrics.get("revenue", 0.0)
            platform_revenue[platform] = platform_revenue.get(platform, 0.0) + revenue
        
        if platform_revenue:
            max_platform_share = max(platform_revenue.values()) / sum(platform_revenue.values())
            if max_platform_share > 0.7:
                risks.append({
                    "type": "platform_concentration",
                    "severity": "high",
                    "description": "Over-dependence on single platform",
                    "mitigation": "Diversify across multiple platforms"
                })
        
        # Revenue stream concentration risk
        stream_type_revenue = {}
        for stream in streams:
            stream_type = stream.stream_type
            revenue = stream.performance_metrics.get("revenue", 0.0)
            stream_type_revenue[stream_type] = stream_type_revenue.get(stream_type, 0.0) + revenue
        
        if stream_type_revenue:
            max_stream_share = max(stream_type_revenue.values()) / sum(stream_type_revenue.values())
            if max_stream_share > 0.8:
                risks.append({
                    "type": "revenue_stream_concentration",
                    "severity": "medium",
                    "description": "Over-dependence on single revenue stream",
                    "mitigation": "Diversify revenue streams"
                })
        
        return {
            "overall_risk": "medium" if risks else "low",
            "identified_risks": risks,
            "risk_score": len(risks) * 0.3  # Simple risk scoring
        }


# Global instance getter
_creator_monetization_orchestrator = None

async def get_creator_monetization_orchestrator() -> CreatorMonetizationOrchestrator:
    """Get the global creator monetization orchestrator instance."""
    global _creator_monetization_orchestrator
    
    if _creator_monetization_orchestrator is None:
        _creator_monetization_orchestrator = CreatorMonetizationOrchestrator()
        await _creator_monetization_orchestrator.initialize()
    
    return _creator_monetization_orchestrator