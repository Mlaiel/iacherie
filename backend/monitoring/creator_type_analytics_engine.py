"""🎭 Creator Type Analytics Engine - IA Influencer Agent Platform
================================================================

Advanced creator type analytics engine providing specialized analytics and optimization
for different creator types: Musicians, Bloggers, Photographers, Influencers, Comedians.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Creator Type Identification → Specialized Analytics → Type-Specific Optimization → Performance Enhancement
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Types of creators supported by the platform"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"  
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    WRITER = "writer"


class CreatorTier(Enum):
    """Creator performance tiers"""
    EMERGING = "emerging"      # 0-10k followers
    RISING = "rising"          # 10k-100k followers
    ESTABLISHED = "established" # 100k-1M followers
    STAR = "star"              # 1M-10M followers
    SUPERSTAR = "superstar"    # 10M+ followers


class CollaborationType(Enum):
    """Types of collaborations"""
    BRAND_PARTNERSHIP = "brand_partnership"
    CREATOR_COLLABORATION = "creator_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_MARKETING = "affiliate_marketing"


@dataclass
class CreatorTypeProfile:
    """Profile for specific creator type"""
    creator_id: str
    creator_type: CreatorType
    creator_tier: CreatorTier
    
    # Basic profile information
    name: str
    description: str = ""
    specializations: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    follower_count: int = 0
    total_content: int = 0
    average_engagement_rate: float = 0.0
    content_creation_frequency: str = "weekly"  # daily, weekly, monthly
    
    # Creator-specific metrics
    type_specific_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Platform presence
    platform_presence: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Revenue information
    revenue_streams: List[str] = field(default_factory=list)
    monthly_revenue: Decimal = Decimal('0')
    revenue_per_follower: Decimal = Decimal('0')
    
    # Collaboration data
    collaboration_history: List[Dict[str, Any]] = field(default_factory=list)
    collaboration_success_rate: float = 0.0
    
    # AI enhancement data
    ai_optimization_level: float = 0.0
    ai_tools_used: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TypeSpecificAnalytics:
    """Analytics specific to creator type"""
    creator_type: CreatorType
    analysis_period: str
    
    # Performance benchmarks for this creator type
    performance_benchmarks: Dict[str, float] = field(default_factory=dict)
    
    # Type-specific KPIs
    type_kpis: Dict[str, Any] = field(default_factory=dict)
    
    # Competitive analysis
    market_position: str = "unknown"  # leading, competitive, emerging, struggling
    peer_comparison: Dict[str, Any] = field(default_factory=dict)
    
    # Growth trajectory
    growth_metrics: Dict[str, float] = field(default_factory=dict)
    growth_prediction: Dict[str, float] = field(default_factory=dict)
    
    # Optimization opportunities
    optimization_opportunities: List[str] = field(default_factory=list)
    recommended_strategies: List[str] = field(default_factory=list)
    
    # Success factors
    success_factors: Dict[str, float] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)


class CreatorTypeAnalyticsEngine:
    """
    Advanced Creator Type Analytics Engine
    
    Provides specialized analytics, benchmarking, and optimization strategies
    tailored to specific creator types and their unique business models.
    """
    
    def __init__(self) -> None:
        self.creator_profiles: Dict[str, CreatorTypeProfile] = {}
        self.type_analytics: Dict[CreatorType, List[TypeSpecificAnalytics]] = defaultdict(list)
        self.benchmarks: Dict[CreatorType, Dict[str, float]] = defaultdict(dict)
        
        # Initialize type-specific configurations
        self.type_configurations = self._initialize_type_configurations()
        self.success_metrics = self._initialize_success_metrics()
        self.optimization_strategies = self._initialize_optimization_strategies()
        
        logger.info("🎭 Creator Type Analytics Engine initialized")
    
    def _initialize_type_configurations(self) -> Dict[CreatorType, Dict[str, Any]]:
        """Initialize type-specific configurations"""
        return {
            CreatorType.MUSICIAN: {
                "primary_platforms": ["spotify", "soundcloud", "youtube", "apple_music"],
                "key_metrics": ["streaming_count", "monthly_listeners", "playlist_adds", "concert_attendance"],
                "content_formats": ["audio", "video", "live_stream"],
                "revenue_streams": ["streaming", "merchandise", "concerts", "licensing"],
                "collaboration_types": ["featuring", "remixes", "producer_collaborations", "band_formations"],
                "success_indicators": ["viral_songs", "chart_performance", "festival_bookings", "label_interest"]
            },
            CreatorType.BLOGGER: {
                "primary_platforms": ["wordpress", "medium", "substack", "linkedin"],
                "key_metrics": ["page_views", "reading_time", "newsletter_subscribers", "article_shares"],
                "content_formats": ["text", "image", "video"],
                "revenue_streams": ["advertising", "affiliate", "subscriptions", "courses"],
                "collaboration_types": ["guest_posting", "content_partnerships", "expert_interviews"],
                "success_indicators": ["thought_leadership", "media_mentions", "speaking_opportunities"]
            },
            CreatorType.PHOTOGRAPHER: {
                "primary_platforms": ["instagram", "behance", "500px", "shutterstock"],
                "key_metrics": ["portfolio_views", "image_downloads", "client_inquiries", "gallery_features"],
                "content_formats": ["image", "video"],
                "revenue_streams": ["stock_photos", "client_work", "prints", "workshops"],
                "collaboration_types": ["model_collaborations", "brand_partnerships", "exhibition_features"],
                "success_indicators": ["award_recognition", "gallery_exhibitions", "brand_ambassadorships"]
            },
            CreatorType.INFLUENCER: {
                "primary_platforms": ["instagram", "tiktok", "youtube", "twitter"],
                "key_metrics": ["follower_growth", "engagement_rate", "story_views", "branded_content_performance"],
                "content_formats": ["image", "video", "text", "live_stream"],
                "revenue_streams": ["sponsored_posts", "affiliate_marketing", "brand_partnerships", "merchandise"],
                "collaboration_types": ["brand_campaigns", "influencer_networks", "cross_promotions"],
                "success_indicators": ["brand_deal_value", "audience_demographics", "influence_metrics"]
            },
            CreatorType.COMEDIAN: {
                "primary_platforms": ["youtube", "tiktok", "instagram", "podcast_platforms"],
                "key_metrics": ["video_views", "laugh_engagement", "show_attendance", "clip_virality"],
                "content_formats": ["video", "audio", "live_stream"],
                "revenue_streams": ["show_tickets", "streaming_specials", "merchandise", "podcast_monetization"],
                "collaboration_types": ["comedy_partnerships", "writing_collaborations", "tour_partnerships"],
                "success_indicators": ["special_deals", "tour_success", "viral_content", "industry_recognition"]
            },
            CreatorType.PODCASTER: {
                "primary_platforms": ["spotify", "apple_podcasts", "google_podcasts", "youtube"],
                "key_metrics": ["downloads", "subscribers", "episode_completion", "listener_retention"],
                "content_formats": ["audio", "video"],
                "revenue_streams": ["sponsorships", "premium_content", "merchandise", "patreon"],
                "collaboration_types": ["guest_interviews", "cross_promotion", "network_partnerships"],
                "success_indicators": ["chart_rankings", "sponsorship_deals", "listener_growth"]
            },
            CreatorType.ARTIST: {
                "primary_platforms": ["instagram", "behance", "artstation", "etsy"],
                "key_metrics": ["artwork_views", "commission_inquiries", "gallery_features", "sales"],
                "content_formats": ["image", "video", "live_stream"],
                "revenue_streams": ["artwork_sales", "commissions", "prints", "nft_sales"],
                "collaboration_types": ["gallery_exhibitions", "brand_collaborations", "artist_collectives"],
                "success_indicators": ["exhibition_features", "collector_interest", "art_awards"]
            },
            CreatorType.WRITER: {
                "primary_platforms": ["medium", "substack", "wattpad", "amazon_kdp"],
                "key_metrics": ["story_reads", "book_sales", "subscriber_count", "review_ratings"],
                "content_formats": ["text", "audio", "image"],
                "revenue_streams": ["book_sales", "subscriptions", "freelance_writing", "courses"],
                "collaboration_types": ["co_authoring", "anthology_contributions", "writing_partnerships"],
                "success_indicators": ["bestseller_status", "literary_awards", "publisher_interest"]
            }
        }
    
    def _initialize_success_metrics(self) -> Dict[CreatorType, Dict[str, float]]:
        """Initialize success metrics thresholds for each creator type"""
        return {
            CreatorType.MUSICIAN: {
                "monthly_listeners_threshold": 10000,
                "engagement_rate_threshold": 0.08,
                "streaming_revenue_threshold": 1000.0,
                "collaboration_success_rate": 0.7
            },
            CreatorType.BLOGGER: {
                "monthly_readers_threshold": 5000,
                "engagement_rate_threshold": 0.05,
                "newsletter_conversion_rate": 0.15,
                "content_depth_score": 0.8
            },
            CreatorType.PHOTOGRAPHER: {
                "portfolio_views_threshold": 2000,
                "engagement_rate_threshold": 0.06,
                "client_conversion_rate": 0.1,
                "image_quality_score": 0.85
            },
            CreatorType.INFLUENCER: {
                "follower_growth_rate": 0.05,
                "engagement_rate_threshold": 0.04,
                "brand_partnership_rate": 0.2,
                "audience_authenticity_score": 0.9
            },
            CreatorType.COMEDIAN: {
                "video_completion_rate": 0.7,
                "engagement_rate_threshold": 0.1,
                "show_attendance_rate": 0.8,
                "viral_content_rate": 0.1
            },
            CreatorType.PODCASTER: {
                "monthly_downloads_threshold": 5000,
                "engagement_rate_threshold": 0.06,
                "episode_completion_rate": 0.75,
                "subscriber_growth_rate": 0.05
            },
            CreatorType.ARTIST: {
                "monthly_views_threshold": 3000,
                "engagement_rate_threshold": 0.08,
                "commission_conversion_rate": 0.15,
                "artwork_quality_score": 0.85
            },
            CreatorType.WRITER: {
                "monthly_readers_threshold": 2000,
                "engagement_rate_threshold": 0.04,
                "content_depth_score": 0.9,
                "reader_retention_rate": 0.6
            }
        }
    
    def _initialize_optimization_strategies(self) -> Dict[CreatorType, List[str]]:
        """Initialize optimization strategies for each creator type"""
        return {
            CreatorType.MUSICIAN: [
                "Optimize release timing for maximum streaming impact",
                "Collaborate with artists in complementary genres",
                "Develop signature sound and consistent branding",
                "Engage with fans through behind-the-scenes content",
                "Leverage playlist placement strategies"
            ],
            CreatorType.BLOGGER: [
                "Create comprehensive content pillar strategy",
                "Optimize for SEO and search engine visibility",
                "Build email list with valuable lead magnets",
                "Establish thought leadership in niche areas",
                "Develop multimedia content for engagement"
            ],
            CreatorType.PHOTOGRAPHER: [
                "Develop distinctive visual style and aesthetic",
                "Build portfolio showcasing diverse skills",
                "Network with models, brands, and agencies",
                "Optimize for stock photography marketplaces",
                "Create educational content to build authority"
            ],
            CreatorType.INFLUENCER: [
                "Maintain authentic audience engagement",
                "Diversify content formats and platforms",
                "Develop long-term brand partnerships",
                "Create value-driven content beyond promotion",
                "Build community through interaction and response"
            ],
            CreatorType.COMEDIAN: [
                "Develop unique comedic voice and perspective",
                "Test material through multiple platforms",
                "Build live performance opportunities",
                "Create shareable, viral-worthy content",
                "Collaborate with other comedians for cross-pollination"
            ],
            CreatorType.PODCASTER: [
                "Maintain consistent publishing schedule",
                "Create engaging episode titles and descriptions",
                "Build guest network for diverse content",
                "Optimize audio quality and production",
                "Develop community engagement strategies"
            ],
            CreatorType.ARTIST: [
                "Develop distinctive artistic style",
                "Document creative process for engagement",
                "Build portfolio showcasing range",
                "Network within art community and galleries",
                "Explore digital art and NFT opportunities"
            ],
            CreatorType.WRITER: [
                "Develop consistent writing voice and style",
                "Build email list for direct reader communication", 
                "Create serialized content for retention",
                "Engage in writing communities and feedback groups",
                "Diversify content formats and topics"
            ]
        }
    
    async def register_creator_profile(self, profile: CreatorTypeProfile) -> bool:
        """Register a new creator profile"""
        try:
            # Validate creator type configuration
            if profile.creator_type not in self.type_configurations:
                logger.error(f"Unsupported creator type: {profile.creator_type}")
                return False
            
            # Determine creator tier based on follower count
            profile.creator_tier = self._determine_creator_tier(profile.follower_count)
            
            # Calculate initial metrics
            await self._calculate_initial_metrics(profile)
            
            # Store profile
            self.creator_profiles[profile.creator_id] = profile
            
            # Generate initial analytics
            analytics = await self._generate_type_analytics(profile)
            self.type_analytics[profile.creator_type].append(analytics)
            
            logger.info(f"✅ Creator profile registered: {profile.creator_id} ({profile.creator_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register creator profile: {e}")
            return False
    
    def _determine_creator_tier(self, follower_count: int) -> CreatorTier:
        """Determine creator tier based on follower count"""
        if follower_count >= 10_000_000:
            return CreatorTier.SUPERSTAR
        elif follower_count >= 1_000_000:
            return CreatorTier.STAR
        elif follower_count >= 100_000:
            return CreatorTier.ESTABLISHED
        elif follower_count >= 10_000:
            return CreatorTier.RISING
        else:
            return CreatorTier.EMERGING
    
    async def _calculate_initial_metrics(self, profile -> None: CreatorTypeProfile) -> None:
        """Calculate initial metrics for creator profile"""
        try:
            # Calculate revenue per follower
            if profile.follower_count > 0:
                profile.revenue_per_follower = profile.monthly_revenue / profile.follower_count
            
            # Set type-specific metrics based on creator type
            config = self.type_configurations[profile.creator_type]
            
            if profile.creator_type == CreatorType.MUSICIAN:
                profile.type_specific_metrics = {
                    "streaming_platforms": len([p for p in profile.platform_presence.keys() if p in config["primary_platforms"]]),
                    "music_genres": profile.specializations,
                    "release_frequency": profile.content_creation_frequency,
                    "collaboration_score": profile.collaboration_success_rate
                }
            
            elif profile.creator_type == CreatorType.BLOGGER:
                profile.type_specific_metrics = {
                    "content_categories": profile.specializations,
                    "publishing_frequency": profile.content_creation_frequency,
                    "average_article_length": 1000,  # Placeholder
                    "newsletter_subscribers": profile.platform_presence.get("newsletter", {}).get("subscribers", 0)
                }
            
            elif profile.creator_type == CreatorType.PHOTOGRAPHER:
                profile.type_specific_metrics = {
                    "photography_styles": profile.specializations,
                    "portfolio_size": profile.total_content,
                    "client_types": [],  # To be populated
                    "equipment_level": "professional"  # To be determined
                }
            
            elif profile.creator_type == CreatorType.INFLUENCER:
                profile.type_specific_metrics = {
                    "niche_categories": profile.specializations,
                    "audience_demographics": profile.target_audience,
                    "brand_affinity": [],  # To be calculated
                    "influence_score": profile.average_engagement_rate * 100
                }
            
            elif profile.creator_type == CreatorType.COMEDIAN:
                profile.type_specific_metrics = {
                    "comedy_styles": profile.specializations,
                    "performance_venues": [],  # To be populated
                    "viral_content_rate": 0.0,  # To be calculated
                    "audience_retention": 0.0   # To be calculated
                }
        
        except Exception as e:
            logger.error(f"❌ Failed to calculate initial metrics: {e}")
    
    async def _generate_type_analytics(self, profile: CreatorTypeProfile) -> TypeSpecificAnalytics:
        """Generate type-specific analytics for creator"""
        try:
            analytics = TypeSpecificAnalytics(
                creator_type=profile.creator_type,
                analysis_period="monthly"
            )
            
            # Set performance benchmarks
            analytics.performance_benchmarks = await self._get_performance_benchmarks(profile.creator_type, profile.creator_tier)
            
            # Calculate type-specific KPIs
            analytics.type_kpis = await self._calculate_type_kpis(profile)
            
            # Determine market position
            analytics.market_position = await self._determine_market_position(profile)
            
            # Generate growth metrics
            analytics.growth_metrics = await self._calculate_growth_metrics(profile)
            
            # Generate optimization opportunities
            analytics.optimization_opportunities = await self._identify_optimization_opportunities(profile)
            
            # Set recommended strategies
            analytics.recommended_strategies = self.optimization_strategies.get(profile.creator_type, [])
            
            # Calculate success factors
            analytics.success_factors = await self._calculate_success_factors(profile)
            
            # Identify risk factors
            analytics.risk_factors = await self._identify_risk_factors(profile)
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to generate type analytics: {e}")
            return TypeSpecificAnalytics(creator_type=profile.creator_type, analysis_period="monthly")
    
    async def _get_performance_benchmarks(self, creator_type: CreatorType, creator_tier: CreatorTier) -> Dict[str, float]:
        """Get performance benchmarks for creator type and tier"""
        base_benchmarks = self.success_metrics.get(creator_type, {})
        
        # Adjust benchmarks based on tier
        tier_multipliers = {
            CreatorTier.EMERGING: 0.5,
            CreatorTier.RISING: 0.8,
            CreatorTier.ESTABLISHED: 1.0,
            CreatorTier.STAR: 1.5,
            CreatorTier.SUPERSTAR: 2.0
        }
        
        multiplier = tier_multipliers.get(creator_tier, 1.0)
        
        adjusted_benchmarks = {}
        for metric, value in base_benchmarks.items():
            adjusted_benchmarks[metric] = value * multiplier
        
        return adjusted_benchmarks
    
    async def _calculate_type_kpis(self, profile: CreatorTypeProfile) -> Dict[str, Any]:
        """Calculate type-specific KPIs"""
        kpis = {}
        
        try:
            if profile.creator_type == CreatorType.MUSICIAN:
                kpis = {
                    "streaming_efficiency": profile.average_engagement_rate * 100,
                    "fan_loyalty_score": profile.collaboration_success_rate,
                    "revenue_diversification": len(profile.revenue_streams),
                    "platform_reach": len(profile.platform_presence)
                }
            
            elif profile.creator_type == CreatorType.BLOGGER:
                kpis = {
                    "content_authority": profile.average_engagement_rate * 10,
                    "audience_growth_rate": 0.05,  # Placeholder
                    "monetization_efficiency": float(profile.revenue_per_follower),
                    "content_consistency": 1.0 if profile.content_creation_frequency == "daily" else 0.7
                }
            
            elif profile.creator_type == CreatorType.PHOTOGRAPHER:
                kpis = {
                    "portfolio_quality": profile.average_engagement_rate * 10,
                    "client_satisfaction": profile.collaboration_success_rate,
                    "market_visibility": len(profile.platform_presence),
                    "revenue_stability": float(profile.monthly_revenue / 1000) if profile.monthly_revenue > 0 else 0
                }
            
            elif profile.creator_type == CreatorType.INFLUENCER:
                kpis = {
                    "influence_score": profile.average_engagement_rate * profile.follower_count / 1000,
                    "brand_partnership_value": float(profile.monthly_revenue),
                    "audience_authenticity": 0.9,  # Placeholder
                    "content_virality": 0.1  # Placeholder
                }
            
            elif profile.creator_type == CreatorType.COMEDIAN:
                kpis = {
                    "comedy_reach": profile.follower_count / 1000,
                    "content_engagement": profile.average_engagement_rate * 100,
                    "performance_success": profile.collaboration_success_rate,
                    "viral_potential": 0.1  # Placeholder
                }
        
        except Exception as e:
            logger.error(f"❌ Failed to calculate type KPIs: {e}")
        
        return kpis
    
    async def _determine_market_position(self, profile: CreatorTypeProfile) -> str:
        """Determine creator's market position"""
        try:
            # Simple market position determination based on tier and performance
            tier_scores = {
                CreatorTier.EMERGING: 1,
                CreatorTier.RISING: 2,
                CreatorTier.ESTABLISHED: 3,
                CreatorTier.STAR: 4,
                CreatorTier.SUPERSTAR: 5
            }
            
            tier_score = tier_scores.get(profile.creator_tier, 1)
            engagement_score = min(5, profile.average_engagement_rate * 100)
            revenue_score = min(5, float(profile.monthly_revenue) / 1000)
            
            overall_score = (tier_score + engagement_score + revenue_score) / 3
            
            if overall_score >= 4:
                return "leading"
            elif overall_score >= 3:
                return "competitive"
            elif overall_score >= 2:
                return "emerging"
            else:
                return "struggling"
        
        except Exception as e:
            logger.error(f"❌ Failed to determine market position: {e}")
            return "unknown"
    
    async def _calculate_growth_metrics(self, profile: CreatorTypeProfile) -> Dict[str, float]:
        """Calculate growth metrics for creator"""
        return {
            "follower_growth_rate": 0.05,  # 5% monthly growth (placeholder)
            "content_production_rate": 1.0 if profile.content_creation_frequency == "daily" else 0.5,
            "engagement_growth_rate": 0.02,  # 2% monthly growth (placeholder)
            "revenue_growth_rate": 0.1  # 10% monthly growth (placeholder)
        }
    
    async def _identify_optimization_opportunities(self, profile: CreatorTypeProfile) -> List[str]:
        """Identify optimization opportunities for creator"""
        opportunities = []
        
        try:
            config = self.type_configurations[profile.creator_type]
            success_metrics = self.success_metrics[profile.creator_type]
            
            # Platform presence optimization
            primary_platforms = config["primary_platforms"]
            current_platforms = list(profile.platform_presence.keys())
            missing_platforms = [p for p in primary_platforms if p not in current_platforms]
            
            if missing_platforms:
                opportunities.append(f"Expand to missing primary platforms: {', '.join(missing_platforms)}")
            
            # Engagement optimization
            engagement_threshold = success_metrics.get("engagement_rate_threshold", 0.05)
            if profile.average_engagement_rate < engagement_threshold:
                opportunities.append("Improve audience engagement through more interactive content")
            
            # Revenue optimization
            if len(profile.revenue_streams) < 3:
                opportunities.append("Diversify revenue streams for financial stability")
            
            # Content frequency optimization
            if profile.content_creation_frequency not in ["daily", "weekly"]:
                opportunities.append("Increase content creation frequency for better audience retention")
            
            # Collaboration optimization
            if profile.collaboration_success_rate < 0.7:
                opportunities.append("Improve collaboration strategies for better partnership outcomes")
            
            # Type-specific opportunities
            if profile.creator_type == CreatorType.MUSICIAN:
                if "streaming" not in profile.revenue_streams:
                    opportunities.append("Monetize streaming platforms more effectively")
            
            elif profile.creator_type == CreatorType.BLOGGER:
                if "newsletter" not in profile.platform_presence:
                    opportunities.append("Build email newsletter for direct audience communication")
            
            elif profile.creator_type == CreatorType.PHOTOGRAPHER:
                if "stock_photos" not in profile.revenue_streams:
                    opportunities.append("Monetize through stock photography platforms")
            
            elif profile.creator_type == CreatorType.INFLUENCER:
                if "brand_partnerships" not in profile.revenue_streams:
                    opportunities.append("Develop brand partnership opportunities")
            
            elif profile.creator_type == CreatorType.COMEDIAN:
                if "live_performance" not in profile.revenue_streams:
                    opportunities.append("Develop live performance revenue opportunities")
        
        except Exception as e:
            logger.error(f"❌ Failed to identify optimization opportunities: {e}")
        
        return opportunities
    
    async def _calculate_success_factors(self, profile: CreatorTypeProfile) -> Dict[str, float]:
        """Calculate success factors for creator"""
        try:
            success_factors = {
                "audience_engagement": min(1.0, profile.average_engagement_rate * 20),
                "content_consistency": 1.0 if profile.content_creation_frequency == "daily" else 0.7,
                "platform_optimization": len(profile.platform_presence) / 5,
                "revenue_diversification": min(1.0, len(profile.revenue_streams) / 4),
                "collaboration_effectiveness": profile.collaboration_success_rate,
                "ai_utilization": profile.ai_optimization_level
            }
            
            return success_factors
        
        except Exception as e:
            logger.error(f"❌ Failed to calculate success factors: {e}")
            return {}
    
    async def _identify_risk_factors(self, profile: CreatorTypeProfile) -> List[str]:
        """Identify risk factors for creator"""
        risks = []
        
        try:
            # Low engagement risk
            if profile.average_engagement_rate < 0.02:
                risks.append("Low audience engagement rate")
            
            # Platform dependency risk
            if len(profile.platform_presence) < 2:
                risks.append("Over-dependence on single platform")
            
            # Revenue concentration risk
            if len(profile.revenue_streams) < 2:
                risks.append("Limited revenue stream diversification")
            
            # Content production risk
            if profile.content_creation_frequency == "monthly":
                risks.append("Infrequent content production may impact audience retention")
            
            # Market position risk
            market_position = await self._determine_market_position(profile)
            if market_position == "struggling":
                risks.append("Weak market position relative to competitors")
            
            # Tier-specific risks
            if profile.creator_tier == CreatorTier.EMERGING:
                risks.append("Early stage creator with limited market presence")
        
        except Exception as e:
            logger.error(f"❌ Failed to identify risk factors: {e}")
        
        return risks
    
    async def get_creator_analytics(self, creator_id: str) -> Optional[TypeSpecificAnalytics]:
        """Get analytics for specific creator"""
        profile = self.creator_profiles.get(creator_id)
        if not profile:
            return None
        
        # Get latest analytics for this creator type
        type_analytics = self.type_analytics.get(profile.creator_type, [])
        if type_analytics:
            return type_analytics[-1]  # Return most recent analytics
        
        return None
    
    async def get_type_performance_summary(self, creator_type: CreatorType) -> Dict[str, Any]:
        """Get performance summary for specific creator type"""
        try:
            type_creators = [
                profile for profile in self.creator_profiles.values()
                if profile.creator_type == creator_type
            ]
            
            if not type_creators:
                return {"error": "No creators found for this type"}
            
            # Calculate aggregate metrics
            total_creators = len(type_creators)
            avg_engagement = statistics.mean(c.average_engagement_rate for c in type_creators)
            avg_followers = statistics.mean(c.follower_count for c in type_creators)
            total_revenue = sum(c.monthly_revenue for c in type_creators)
            
            # Tier distribution
            tier_distribution = {}
            for tier in CreatorTier:
                count = len([c for c in type_creators if c.creator_tier == tier])
                tier_distribution[tier.value] = count
            
            return {
                "creator_type": creator_type.value,
                "total_creators": total_creators,
                "average_engagement_rate": avg_engagement,
                "average_follower_count": avg_followers,
                "total_monthly_revenue": float(total_revenue),
                "tier_distribution": tier_distribution,
                "top_performer": max(type_creators, key=lambda x: x.average_engagement_rate).creator_id if type_creators else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get type performance summary: {e}")
            return {"error": str(e)}
    
    async def get_optimization_recommendations(self, creator_id: str) -> List[str]:
        """Get optimization recommendations for specific creator"""
        analytics = await self.get_creator_analytics(creator_id)
        if analytics:
            return analytics.optimization_opportunities + analytics.recommended_strategies
        return []
    
    async def compare_creators(self, creator_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple creators"""
        try:
            creators = [self.creator_profiles[cid] for cid in creator_ids if cid in self.creator_profiles]
            
            if len(creators) < 2:
                return {"error": "Need at least 2 creators for comparison"}
            
            comparison = {
                "creators": [],
                "metrics_comparison": {},
                "performance_ranking": [],
                "collaboration_recommendations": []
            }
            
            # Add creator data
            for creator in creators:
                comparison["creators"].append({
                    "id": creator.creator_id,
                    "type": creator.creator_type.value,
                    "tier": creator.creator_tier.value,
                    "followers": creator.follower_count,
                    "engagement_rate": creator.average_engagement_rate,
                    "monthly_revenue": float(creator.monthly_revenue)
                })
            
            # Calculate metrics comparison
            metrics = ["follower_count", "average_engagement_rate", "monthly_revenue"]
            for metric in metrics:
                values = [getattr(c, metric) for c in creators]
                comparison["metrics_comparison"][metric] = {
                    "max": max(values),
                    "min": min(values),
                    "average": statistics.mean(values) if values else 0
                }
            
            # Performance ranking
            creators_with_scores = []
            for creator in creators:
                score = (creator.average_engagement_rate * 100) + (creator.follower_count / 1000)
                creators_with_scores.append((creator.creator_id, score))
            
            creators_with_scores.sort(key=lambda x: x[1], reverse=True)
            comparison["performance_ranking"] = [{"creator_id": cid, "score": score} for cid, score in creators_with_scores]
            
            # Collaboration recommendations
            # Recommend collaborations between creators of similar tiers but different types
            for i, creator1 in enumerate(creators):
                for creator2 in creators[i+1:]:
                    if (creator1.creator_tier == creator2.creator_tier and 
                        creator1.creator_type != creator2.creator_type):
                        comparison["collaboration_recommendations"].append({
                            "creator1": creator1.creator_id,
                            "creator2": creator2.creator_id,
                            "reason": f"Similar tier ({creator1.creator_tier.value}) with complementary types"
                        })
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to compare creators: {e}")
            return {"error": str(e)}


# Global instance for easy access
creator_type_analytics_engine = CreatorTypeAnalyticsEngine()

# Convenience functions
async def register_creator_profile(profile: CreatorTypeProfile) -> bool:
    """Register creator profile - convenience function"""
    return await creator_type_analytics_engine.register_creator_profile(profile)

async def get_creator_analytics(creator_id: str) -> Optional[TypeSpecificAnalytics]:
    """Get creator analytics - convenience function"""
    return await creator_type_analytics_engine.get_creator_analytics(creator_id)

async def get_type_performance_summary(creator_type: CreatorType) -> Dict[str, Any]:
    """Get type performance summary - convenience function"""
    return await creator_type_analytics_engine.get_type_performance_summary(creator_type)

async def get_optimization_recommendations(creator_id: str) -> List[str]:
    """Get optimization recommendations - convenience function"""
    return await creator_type_analytics_engine.get_optimization_recommendations(creator_id)

async def compare_creators(creator_ids: List[str]) -> Dict[str, Any]:
    """Compare creators - convenience function"""
    return await creator_type_analytics_engine.compare_creators(creator_ids)