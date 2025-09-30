"""Competitor Intelligence - Advanced Competitive Analysis Engine
=============================================================

Comprehensive competitor intelligence system providing deep insights into
competitive landscape, content strategies, performance benchmarking,
and market positioning for content creators and influencers.

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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random


def percentile(data, percent):
    """Calculate percentile of a dataset"""
    if not data:
        return 0
    data = sorted(data)
    k = (len(data) - 1) * percent / 100
    f = int(k)
    c = k - f
    if f == len(data) - 1:
        return data[f]
    return data[f] * (1 - c) + data[f + 1] * c
from collections import defaultdict, Counter


# Configure logging
logger = logging.getLogger(__name__)


class CompetitorTier(Enum):
    """Competitor tier classifications"""
    DIRECT = "direct"           # Same niche, similar audience size
    INDIRECT = "indirect"       # Related niche, different approach
    ASPIRATIONAL = "aspirational"  # Higher tier, target to reach
    EMERGING = "emerging"       # Smaller but growing fast
    SUBSTITUTE = "substitute"   # Different medium, same value


class AnalysisScope(Enum):
    """Scope of competitive analysis"""
    CONTENT_STRATEGY = "content_strategy"
    ENGAGEMENT_PERFORMANCE = "engagement_performance"
    MONETIZATION = "monetization"
    AUDIENCE_ANALYSIS = "audience_analysis"
    GROWTH_TRENDS = "growth_trends"
    PLATFORM_PRESENCE = "platform_presence"
    COLLABORATION_NETWORK = "collaboration_network"


class MetricType(Enum):
    """Types of metrics for comparison"""
    FOLLOWERS = "followers"
    ENGAGEMENT_RATE = "engagement_rate"
    CONTENT_FREQUENCY = "content_frequency"
    VIDEO_VIEWS = "video_views"
    REACH = "reach"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    GROWTH_RATE = "growth_rate"


class PlatformChannel(Enum):
    """Social media platforms for analysis"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"


@dataclass
class CompetitorProfile:
    """Competitor profile data structure"""
    competitor_id: str
    name: str
    tier: CompetitorTier
    niche: str
    platforms: Dict[PlatformChannel, Dict[str, Any]]
    metrics: Dict[MetricType, float]
    content_strategy: Dict[str, Any]
    audience_demographics: Dict[str, Any]
    monetization_streams: List[str]
    collaboration_history: List[str]
    strengths: List[str]
    weaknesses: List[str]
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitiveAnalysisRequest:
    """Competitive analysis request data structure"""
    analysis_id: str
    creator_id: str
    competitor_ids: List[str]
    analysis_scopes: List[AnalysisScope]
    target_platforms: List[PlatformChannel]
    time_period: timedelta
    benchmark_metrics: List[MetricType]
    include_gap_analysis: bool = True
    include_opportunities: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitiveGap:
    """Competitive gap data structure"""
    gap_id: str
    gap_type: str
    description: str
    impact_score: float  # 0-1
    difficulty_score: float  # 0-1
    priority_score: float  # 0-1
    recommendations: List[str]
    competitors_excelling: List[str]
    estimated_effort: str
    potential_roi: str


@dataclass
class MarketOpportunity:
    """Market opportunity data structure"""
    opportunity_id: str
    opportunity_type: str
    description: str
    market_size: str
    competition_level: str  # low, medium, high
    entry_barriers: List[str]
    success_probability: float
    time_to_market: str
    resource_requirements: List[str]
    potential_revenue: str


@dataclass
class CompetitiveIntelligenceResult:
    """Competitive intelligence analysis result"""
    analysis_id: str
    creator_id: str
    analysis_date: datetime
    market_position: Dict[str, Any]
    competitor_rankings: List[Dict[str, Any]]
    performance_benchmarks: Dict[str, Dict[str, float]]
    content_gap_analysis: Dict[str, Any]
    engagement_insights: Dict[str, Any]
    monetization_analysis: Dict[str, Any]
    audience_overlap: Dict[str, float]
    growth_opportunities: List[MarketOpportunity]
    competitive_gaps: List[CompetitiveGap]
    strategic_recommendations: List[str]
    threat_assessment: Dict[str, Any]
    market_trends: Dict[str, Any]
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompetitorIntelligence:
    """
    Advanced Competitor Intelligence Engine
    
    Provides comprehensive competitive analysis including:
    - Market positioning and benchmarking
    - Content strategy analysis
    - Performance gap identification
    - Growth opportunity detection
    - Threat assessment and monitoring
    """
    
    def __init__(self, 
                 analysis_ttl: int = 86400,  # 24 hours
                 update_frequency: int = 3600):  # 1 hour
        """
        Initialize Competitor Intelligence Engine
        
        Args:
            analysis_ttl: Analysis cache time-to-live in seconds
            update_frequency: Data update frequency in seconds
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analysis_ttl = analysis_ttl
        self.update_frequency = update_frequency
        
        # Analysis cache
        self.analysis_cache: Dict[str, CompetitiveIntelligenceResult] = {}
        
        # Competitor database (simulated)
        self.competitor_profiles: Dict[str, CompetitorProfile] = {}
        
        # Market benchmarks by niche
        self.niche_benchmarks = {
            "gaming": {
                MetricType.ENGAGEMENT_RATE: 0.08,
                MetricType.CONTENT_FREQUENCY: 5.0,  # posts per week
                MetricType.GROWTH_RATE: 0.15  # monthly
            },
            "lifestyle": {
                MetricType.ENGAGEMENT_RATE: 0.04,
                MetricType.CONTENT_FREQUENCY: 7.0,
                MetricType.GROWTH_RATE: 0.10
            },
            "education": {
                MetricType.ENGAGEMENT_RATE: 0.06,
                MetricType.CONTENT_FREQUENCY: 3.0,
                MetricType.GROWTH_RATE: 0.12
            },
            "entertainment": {
                MetricType.ENGAGEMENT_RATE: 0.05,
                MetricType.CONTENT_FREQUENCY: 6.0,
                MetricType.GROWTH_RATE: 0.18
            }
        }
        
        # Platform performance weights
        self.platform_weights = {
            PlatformChannel.YOUTUBE: {"reach": 0.3, "engagement": 0.4, "retention": 0.3},
            PlatformChannel.INSTAGRAM: {"reach": 0.25, "engagement": 0.5, "stories": 0.25},
            PlatformChannel.TIKTOK: {"reach": 0.2, "engagement": 0.6, "virality": 0.2},
            PlatformChannel.TWITTER: {"reach": 0.35, "engagement": 0.45, "conversations": 0.2}
        }
        
        # Content strategy patterns
        self.content_patterns = {
            "high_frequency": {"posts_per_week": 7, "engagement_impact": 1.2},
            "quality_focused": {"posts_per_week": 3, "engagement_impact": 1.5},
            "trend_following": {"trend_adoption": 0.8, "virality_chance": 1.3},
            "original_content": {"originality": 0.9, "brand_building": 1.4}
        }
        
        self.logger.info("🔍 Competitor Intelligence Engine initialized")
    
    async def analyze_competition(self, 
                                request: CompetitiveAnalysisRequest) -> CompetitiveIntelligenceResult:
        """
        Perform comprehensive competitive analysis
        
        Args:
            request: Competitive analysis request with parameters
            
        Returns:
            Detailed competitive intelligence result
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self._get_cached_analysis(cache_key)
            if cached_result:
                self.logger.debug(f"✅ Returning cached analysis: {request.analysis_id}")
                return cached_result
            
            self.logger.info(f"🔍 Starting competitive analysis for {request.analysis_id}")
            
            # Load competitor profiles
            competitor_profiles = await self._load_competitor_profiles(request.competitor_ids)
            
            # Analyze market position
            market_position = await self._analyze_market_position(
                request.creator_id, competitor_profiles, request.benchmark_metrics
            )
            
            # Rank competitors
            competitor_rankings = await self._rank_competitors(
                competitor_profiles, request.benchmark_metrics
            )
            
            # Calculate performance benchmarks
            performance_benchmarks = await self._calculate_performance_benchmarks(
                competitor_profiles, request.benchmark_metrics
            )
            
            # Analyze content gaps
            content_gap_analysis = await self._analyze_content_gaps(
                request.creator_id, competitor_profiles, request.target_platforms
            )
            
            # Analyze engagement patterns
            engagement_insights = await self._analyze_engagement_patterns(competitor_profiles)
            
            # Analyze monetization strategies
            monetization_analysis = await self._analyze_monetization_strategies(competitor_profiles)
            
            # Calculate audience overlap
            audience_overlap = await self._calculate_audience_overlap(
                request.creator_id, competitor_profiles
            )
            
            # Identify growth opportunities
            growth_opportunities = await self._identify_growth_opportunities(
                request.creator_id, competitor_profiles, market_position
            )
            
            # Identify competitive gaps
            competitive_gaps = await self._identify_competitive_gaps(
                request.creator_id, competitor_profiles, performance_benchmarks
            )
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                market_position, competitive_gaps, growth_opportunities
            )
            
            # Assess threats
            threat_assessment = await self._assess_threats(
                request.creator_id, competitor_profiles
            )
            
            # Analyze market trends
            market_trends = await self._analyze_market_trends(
                competitor_profiles, request.time_period
            )
            
            # Create result
            result = CompetitiveIntelligenceResult(
                analysis_id=request.analysis_id,
                creator_id=request.creator_id,
                analysis_date=datetime.now(),
                market_position=market_position,
                competitor_rankings=competitor_rankings,
                performance_benchmarks=performance_benchmarks,
                content_gap_analysis=content_gap_analysis,
                engagement_insights=engagement_insights,
                monetization_analysis=monetization_analysis,
                audience_overlap=audience_overlap,
                growth_opportunities=growth_opportunities,
                competitive_gaps=competitive_gaps,
                strategic_recommendations=strategic_recommendations,
                threat_assessment=threat_assessment,
                market_trends=market_trends,
                expires_at=datetime.now() + timedelta(seconds=self.analysis_ttl),
                metadata={
                    "competitors_analyzed": len(competitor_profiles),
                    "analysis_scopes": [scope.value for scope in request.analysis_scopes],
                    "platforms_covered": [platform.value for platform in request.target_platforms],
                    "analysis_version": "1.0"
                }
            )
            
            # Cache result
            await self._cache_analysis(cache_key, result)
            
            self.logger.info(
                f"✅ Competitive analysis completed for {request.analysis_id}: "
                f"{len(competitor_profiles)} competitors analyzed, "
                f"{len(growth_opportunities)} opportunities identified"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Competitive analysis failed for {request.analysis_id}: {str(e)}")
            raise
    
    async def monitor_competitor_changes(self, 
                                       competitor_ids: List[str],
                                       monitoring_period: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """
        Monitor competitor changes over time
        
        Args:
            competitor_ids: List of competitor IDs to monitor
            monitoring_period: Period to monitor changes
            
        Returns:
            Change detection analysis
        """
        try:
            changes_detected = {}
            
            for competitor_id in competitor_ids:
                # Load current and historical profiles (simulated)
                current_profile = await self._load_competitor_profile(competitor_id)
                if not current_profile:
                    continue
                
                # Detect changes (simplified analysis)
                changes = await self._detect_profile_changes(competitor_id, monitoring_period)
                
                if changes:
                    changes_detected[competitor_id] = {
                        "competitor_name": current_profile.name,
                        "changes": changes,
                        "change_score": sum(change.get("impact", 0) for change in changes),
                        "last_updated": current_profile.last_updated.isoformat()
                    }
            
            # Rank by significance
            significant_changes = sorted(
                changes_detected.items(),
                key=lambda x: x[1]["change_score"],
                reverse=True
            )
            
            return {
                "monitoring_period": str(monitoring_period),
                "competitors_monitored": len(competitor_ids),
                "changes_detected": len(changes_detected),
                "significant_changes": significant_changes[:5],  # Top 5
                "change_summary": await self._summarize_changes(changes_detected),
                "monitoring_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Competitor monitoring failed: {str(e)}")
            raise
    
    async def benchmark_performance(self, 
                                  creator_metrics: Dict[MetricType, float],
                                  niche: str,
                                  competitor_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Benchmark creator performance against competitors and industry
        
        Args:
            creator_metrics: Creator's current metrics
            niche: Creator's niche/category
            competitor_ids: Optional specific competitors to compare against
            
        Returns:
            Performance benchmarking analysis
        """
        try:
            benchmarks = {}
            
            # Industry benchmarks
            industry_benchmarks = self.niche_benchmarks.get(niche, {})
            
            # Compare against industry
            industry_comparison = {}
            for metric, value in creator_metrics.items():
                industry_avg = industry_benchmarks.get(metric, 0)
                if industry_avg > 0:
                    performance_ratio = value / industry_avg
                    industry_comparison[metric.value] = {
                        "creator_value": value,
                        "industry_average": industry_avg,
                        "performance_ratio": performance_ratio,
                        "performance_level": self._categorize_performance(performance_ratio)
                    }
            
            benchmarks["industry_comparison"] = industry_comparison
            
            # Competitor comparison
            if competitor_ids:
                competitor_profiles = await self._load_competitor_profiles(competitor_ids)
                competitor_comparison = await self._compare_against_competitors(
                    creator_metrics, competitor_profiles
                )
                benchmarks["competitor_comparison"] = competitor_comparison
            
            # Calculate overall performance score
            overall_score = statistics.mean([
                comp.get("performance_ratio", 1.0) 
                for comp in industry_comparison.values()
            ])
            
            benchmarks["overall_performance"] = {
                "score": round(overall_score, 2),
                "percentile": await self._calculate_percentile(overall_score, niche),
                "grade": self._assign_performance_grade(overall_score),
                "improvement_potential": max(0, 2.0 - overall_score)  # Assuming 2.0 is excellent
            }
            
            # Generate improvement recommendations
            benchmarks["improvement_recommendations"] = await self._generate_improvement_recommendations(
                industry_comparison, creator_metrics, niche
            )
            
            return benchmarks
            
        except Exception as e:
            self.logger.error(f"❌ Performance benchmarking failed: {str(e)}")
            raise
    
    async def _load_competitor_profiles(self, competitor_ids: List[str]) -> List[CompetitorProfile]:
        """Load competitor profiles (simulated)"""
        profiles = []
        
        for competitor_id in competitor_ids:
            profile = await self._load_competitor_profile(competitor_id)
            if profile:
                profiles.append(profile)
        
        return profiles
    
    async def _load_competitor_profile(self, competitor_id: str) -> Optional[CompetitorProfile]:
        """Load single competitor profile (simulated)"""
        # This would connect to actual data sources in production
        # For now, return simulated data
        
        simulated_profiles = {
            "competitor_001": CompetitorProfile(
                competitor_id="competitor_001",
                name="Top Gaming Influencer",
                tier=CompetitorTier.ASPIRATIONAL,
                niche="gaming",
                platforms={
                    PlatformChannel.YOUTUBE: {"subscribers": 2500000, "avg_views": 850000},
                    PlatformChannel.TWITCH: {"followers": 1200000, "avg_viewers": 15000}
                },
                metrics={
                    MetricType.FOLLOWERS: 2500000,
                    MetricType.ENGAGEMENT_RATE: 0.085,
                    MetricType.CONTENT_FREQUENCY: 5.0,
                    MetricType.GROWTH_RATE: 0.12
                },
                content_strategy={"posting_schedule": "daily", "content_mix": ["gameplay", "tutorials", "reviews"]},
                audience_demographics={"age_18_24": 0.4, "age_25_34": 0.35, "male": 0.75},
                monetization_streams=["sponsorships", "ad_revenue", "merchandise", "donations"],
                collaboration_history=["brand_001", "creator_002", "event_003"],
                strengths=["high engagement", "consistent content", "strong brand partnerships"],
                weaknesses=["limited platform diversity", "narrow content focus"],
                last_updated=datetime.now(),
                metadata={"tier_score": 0.9, "threat_level": "medium"}
            ),
            "competitor_002": CompetitorProfile(
                competitor_id="competitor_002",
                name="Lifestyle Content Creator",
                tier=CompetitorTier.DIRECT,
                niche="lifestyle",
                platforms={
                    PlatformChannel.INSTAGRAM: {"followers": 850000, "avg_likes": 42000},
                    PlatformChannel.YOUTUBE: {"subscribers": 450000, "avg_views": 180000}
                },
                metrics={
                    MetricType.FOLLOWERS: 850000,
                    MetricType.ENGAGEMENT_RATE: 0.049,
                    MetricType.CONTENT_FREQUENCY: 6.0,
                    MetricType.GROWTH_RATE: 0.08
                },
                content_strategy={"posting_schedule": "6x/week", "content_mix": ["fashion", "travel", "wellness"]},
                audience_demographics={"age_18_24": 0.3, "age_25_34": 0.45, "female": 0.80},
                monetization_streams=["sponsorships", "affiliate_marketing", "course_sales"],
                collaboration_history=["brand_004", "creator_005"],
                strengths=["high-quality visuals", "engaged community", "diverse content"],
                weaknesses=["inconsistent posting", "limited monetization"],
                last_updated=datetime.now(),
                metadata={"tier_score": 0.7, "threat_level": "low"}
            )
        }
        
        return simulated_profiles.get(competitor_id)
    
    async def _analyze_market_position(self, 
                                     creator_id: str,
                                     competitors: List[CompetitorProfile],
                                     metrics: List[MetricType]) -> Dict[str, Any]:
        """Analyze creator's market position relative to competitors"""
        # Simulated creator data
        creator_metrics = {
            MetricType.FOLLOWERS: 150000,
            MetricType.ENGAGEMENT_RATE: 0.055,
            MetricType.CONTENT_FREQUENCY: 4.0,
            MetricType.GROWTH_RATE: 0.15
        }
        
        position_analysis = {}
        
        for metric in metrics:
            if metric in creator_metrics:
                creator_value = creator_metrics[metric]
                competitor_values = [
                    comp.metrics.get(metric, 0) for comp in competitors
                    if metric in comp.metrics
                ]
                
                if competitor_values:
                    percentile = (sum(1 for v in competitor_values if v < creator_value) / 
                                len(competitor_values) * 100)
                    
                    position_analysis[metric.value] = {
                        "creator_value": creator_value,
                        "market_percentile": round(percentile, 1),
                        "market_average": statistics.mean(competitor_values),
                        "market_median": statistics.median(competitor_values),
                        "market_leader": max(competitor_values) if competitor_values else 0,
                        "position_rating": self._rate_market_position(percentile)
                    }
        
        # Overall market position
        avg_percentile = statistics.mean([
            analysis["market_percentile"] 
            for analysis in position_analysis.values()
        ])
        
        position_analysis["overall_position"] = {
            "average_percentile": round(avg_percentile, 1),
            "market_tier": self._determine_market_tier(avg_percentile),
            "competitive_strength": self._assess_competitive_strength(avg_percentile),
            "growth_potential": self._assess_growth_potential(creator_metrics, competitors)
        }
        
        return position_analysis
    
    async def _rank_competitors(self, 
                              competitors: List[CompetitorProfile],
                              metrics: List[MetricType]) -> List[Dict[str, Any]]:
        """Rank competitors based on performance metrics"""
        rankings = []
        
        for competitor in competitors:
            # Calculate composite score
            metric_scores = []
            for metric in metrics:
                if metric in competitor.metrics:
                    # Normalize scores (simplified)
                    score = min(competitor.metrics[metric] / 1000000, 1.0)  # Cap at 1M for followers
                    metric_scores.append(score)
            
            composite_score = statistics.mean(metric_scores) if metric_scores else 0
            
            rankings.append({
                "competitor_id": competitor.competitor_id,
                "name": competitor.name,
                "tier": competitor.tier.value,
                "composite_score": round(composite_score, 3),
                "key_metrics": {
                    metric.value: competitor.metrics.get(metric, 0)
                    for metric in metrics if metric in competitor.metrics
                },
                "strengths": competitor.strengths[:3],  # Top 3
                "threat_level": competitor.metadata.get("threat_level", "unknown")
            })
        
        # Sort by composite score
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        
        # Add ranking positions
        for i, ranking in enumerate(rankings):
            ranking["rank"] = i + 1
        
        return rankings
    
    async def _calculate_performance_benchmarks(self, 
                                              competitors: List[CompetitorProfile],
                                              metrics: List[MetricType]) -> Dict[str, Dict[str, float]]:
        """Calculate performance benchmarks from competitor data"""
        benchmarks = {}
        
        for metric in metrics:
            values = [
                comp.metrics.get(metric, 0) for comp in competitors
                if metric in comp.metrics
            ]
            
            if values:
                benchmarks[metric.value] = {
                    "min": min(values),
                    "max": max(values),
                    "average": statistics.mean(values),
                    "median": statistics.median(values),
                    "p25": percentile(values, 25),
                    "p75": percentile(values, 75),
                    "p90": percentile(values, 90)
                }
        
        return benchmarks
    
    async def _analyze_content_gaps(self, 
                                  creator_id: str,
                                  competitors: List[CompetitorProfile],
                                  platforms: List[PlatformChannel]) -> Dict[str, Any]:
        """Analyze content strategy gaps"""
        # Simulated creator content strategy
        creator_strategy = {
            "content_types": ["tutorials", "reviews"],
            "posting_frequency": 4,
            "platform_presence": [PlatformChannel.YOUTUBE, PlatformChannel.INSTAGRAM]
        }
        
        gap_analysis = {}
        
        # Content type gaps
        competitor_content_types = set()
        for competitor in competitors:
            content_mix = competitor.content_strategy.get("content_mix", [])
            competitor_content_types.update(content_mix)
        
        creator_content_types = set(creator_strategy["content_types"])
        missing_content_types = competitor_content_types - creator_content_types
        
        gap_analysis["content_type_gaps"] = {
            "missing_types": list(missing_content_types),
            "opportunity_score": len(missing_content_types) / len(competitor_content_types) if competitor_content_types else 0,
            "recommendations": [f"Consider adding {content_type} content" for content_type in list(missing_content_types)[:3]]
        }
        
        # Platform presence gaps
        competitor_platforms = set()
        for competitor in competitors:
            competitor_platforms.update(competitor.platforms.keys())
        
        creator_platforms = set(creator_strategy["platform_presence"])
        missing_platforms = competitor_platforms - creator_platforms
        
        gap_analysis["platform_gaps"] = {
            "missing_platforms": [platform.value for platform in missing_platforms],
            "expansion_opportunities": len(missing_platforms),
            "priority_platforms": await self._prioritize_platforms(missing_platforms, competitors)
        }
        
        # Frequency gaps
        competitor_frequencies = [
            comp.metrics.get(MetricType.CONTENT_FREQUENCY, 0) for comp in competitors
        ]
        avg_competitor_frequency = statistics.mean(competitor_frequencies) if competitor_frequencies else 0
        creator_frequency = creator_strategy["posting_frequency"]
        
        gap_analysis["frequency_analysis"] = {
            "creator_frequency": creator_frequency,
            "market_average": round(avg_competitor_frequency, 1),
            "frequency_gap": round(avg_competitor_frequency - creator_frequency, 1),
            "optimization_potential": max(0, avg_competitor_frequency - creator_frequency) / avg_competitor_frequency if avg_competitor_frequency > 0 else 0
        }
        
        return gap_analysis
    
    async def _analyze_engagement_patterns(self, 
                                         competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Analyze engagement patterns across competitors"""
        engagement_analysis = {}
        
        # Engagement rate analysis
        engagement_rates = [
            comp.metrics.get(MetricType.ENGAGEMENT_RATE, 0) for comp in competitors
        ]
        
        if engagement_rates:
            engagement_analysis["engagement_benchmarks"] = {
                "average_rate": round(statistics.mean(engagement_rates), 4),
                "top_quartile": round(percentile(engagement_rates, 75), 4),
                "distribution": {
                    "low": sum(1 for rate in engagement_rates if rate < 0.03),
                    "medium": sum(1 for rate in engagement_rates if 0.03 <= rate < 0.06),
                    "high": sum(1 for rate in engagement_rates if rate >= 0.06)
                }
            }
        
        # Content strategy patterns
        content_strategies = defaultdict(int)
        for competitor in competitors:
            strategy = competitor.content_strategy.get("posting_schedule", "unknown")
            content_strategies[strategy] += 1
        
        engagement_analysis["content_patterns"] = {
            "popular_strategies": dict(content_strategies),
            "winning_formula": max(content_strategies.items(), key=lambda x: x[1])[0] if content_strategies else "unknown"
        }
        
        # Platform performance
        platform_performance = defaultdict(list)
        for competitor in competitors:
            for platform, data in competitor.platforms.items():
                engagement_rate = competitor.metrics.get(MetricType.ENGAGEMENT_RATE, 0)
                platform_performance[platform.value].append(engagement_rate)
        
        platform_avg = {
            platform: statistics.mean(rates) if rates else 0
            for platform, rates in platform_performance.items()
        }
        
        engagement_analysis["platform_performance"] = {
            "average_by_platform": platform_avg,
            "best_platform": max(platform_avg.items(), key=lambda x: x[1])[0] if platform_avg else "unknown"
        }
        
        return engagement_analysis
    
    async def _analyze_monetization_strategies(self, 
                                             competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Analyze monetization strategies across competitors"""
        monetization_analysis = {}
        
        # Revenue stream analysis
        all_streams = []
        for competitor in competitors:
            all_streams.extend(competitor.monetization_streams)
        
        stream_popularity = Counter(all_streams)
        
        monetization_analysis["revenue_stream_analysis"] = {
            "popular_streams": dict(stream_popularity.most_common()),
            "average_streams_per_creator": len(all_streams) / len(competitors) if competitors else 0,
            "diversification_leaders": [
                {"name": comp.name, "stream_count": len(comp.monetization_streams)}
                for comp in sorted(competitors, key=lambda x: len(x.monetization_streams), reverse=True)
            ][:3]
        }
        
        # Monetization sophistication
        sophistication_scores = []
        for competitor in competitors:
            # Simple scoring based on number and type of streams
            score = len(competitor.monetization_streams) * 0.3
            if "sponsorships" in competitor.monetization_streams:
                score += 0.2
            if "course_sales" in competitor.monetization_streams:
                score += 0.3
            if "merchandise" in competitor.monetization_streams:
                score += 0.2
            
            sophistication_scores.append(score)
        
        monetization_analysis["sophistication_analysis"] = {
            "average_sophistication": round(statistics.mean(sophistication_scores), 2) if sophistication_scores else 0,
            "sophistication_leaders": [
                comp.name for comp in sorted(
                    competitors, 
                    key=lambda x: len(x.monetization_streams), 
                    reverse=True
                )
            ][:3]
        }
        
        return monetization_analysis
    
    async def _calculate_audience_overlap(self, 
                                        creator_id: str,
                                        competitors: List[CompetitorProfile]) -> Dict[str, float]:
        """Calculate estimated audience overlap"""
        # Simulated audience overlap calculation
        overlap_scores = {}
        
        for competitor in competitors:
            # Simplified overlap calculation based on demographics similarity
            # In production, this would use actual audience data
            overlap_score = random.uniform(0.1, 0.4)  # 10-40% overlap
            overlap_scores[competitor.competitor_id] = round(overlap_score, 3)
        
        return overlap_scores
    
    async def _identify_growth_opportunities(self, 
                                           creator_id: str,
                                           competitors: List[CompetitorProfile],
                                           market_position: Dict[str, Any]) -> List[MarketOpportunity]:
        """Identify growth opportunities based on competitive analysis"""
        opportunities = []
        
        # Platform expansion opportunities
        competitor_platforms = set()
        for competitor in competitors:
            competitor_platforms.update(competitor.platforms.keys())
        
        # Simulated creator platforms
        creator_platforms = {PlatformChannel.YOUTUBE, PlatformChannel.INSTAGRAM}
        missing_platforms = competitor_platforms - creator_platforms
        
        for platform in missing_platforms:
            opportunities.append(MarketOpportunity(
                opportunity_id=f"platform_expansion_{platform.value}",
                opportunity_type="platform_expansion",
                description=f"Expand to {platform.value} platform",
                market_size="Medium",
                competition_level="Medium",
                entry_barriers=["Content adaptation", "Platform learning curve"],
                success_probability=0.7,
                time_to_market="2-3 months",
                resource_requirements=["Content creation", "Platform strategy"],
                potential_revenue="$5,000-15,000/month"
            ))
        
        # Content diversification opportunities
        opportunities.append(MarketOpportunity(
            opportunity_id="content_diversification",
            opportunity_type="content_strategy",
            description="Diversify content types based on competitor success",
            market_size="Large",
            competition_level="High",
            entry_barriers=["Content expertise", "Production resources"],
            success_probability=0.6,
            time_to_market="1-2 months",
            resource_requirements=["Content planning", "Production upgrade"],
            potential_revenue="$2,000-8,000/month"
        ))
        
        # Monetization expansion
        opportunities.append(MarketOpportunity(
            opportunity_id="monetization_expansion",
            opportunity_type="monetization",
            description="Add missing revenue streams popular among competitors",
            market_size="Medium",
            competition_level="Low",
            entry_barriers=["Setup complexity", "Audience building"],
            success_probability=0.8,
            time_to_market="1 month",
            resource_requirements=["Platform setup", "Marketing"],
            potential_revenue="$1,000-5,000/month"
        ))
        
        return opportunities[:5]  # Top 5 opportunities
    
    async def _identify_competitive_gaps(self, 
                                       creator_id: str,
                                       competitors: List[CompetitorProfile],
                                       benchmarks: Dict[str, Dict[str, float]]) -> List[CompetitiveGap]:
        """Identify competitive gaps to address"""
        gaps = []
        
        # Simulated creator metrics
        creator_metrics = {
            MetricType.ENGAGEMENT_RATE: 0.055,
            MetricType.CONTENT_FREQUENCY: 4.0,
            MetricType.GROWTH_RATE: 0.15
        }
        
        for metric, creator_value in creator_metrics.items():
            benchmark = benchmarks.get(metric.value, {})
            market_average = benchmark.get("average", 0)
            
            if market_average > creator_value:
                gap_size = (market_average - creator_value) / market_average
                
                gaps.append(CompetitiveGap(
                    gap_id=f"gap_{metric.value}",
                    gap_type=metric.value,
                    description=f"Below market average in {metric.value}",
                    impact_score=gap_size,
                    difficulty_score=0.6,  # Moderate difficulty
                    priority_score=gap_size * 0.8,  # High priority for large gaps
                    recommendations=[
                        f"Analyze top performers in {metric.value}",
                        f"Implement improvement strategies for {metric.value}",
                        "Monitor progress monthly"
                    ],
                    competitors_excelling=[
                        comp.name for comp in competitors 
                        if comp.metrics.get(metric, 0) > market_average
                    ][:3],
                    estimated_effort="2-3 months",
                    potential_roi="Medium to High"
                ))
        
        # Sort by priority score
        gaps.sort(key=lambda x: x.priority_score, reverse=True)
        
        return gaps[:5]  # Top 5 gaps
    
    async def _generate_strategic_recommendations(self, 
                                                market_position: Dict[str, Any],
                                                gaps: List[CompetitiveGap],
                                                opportunities: List[MarketOpportunity]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Position-based recommendations
        overall_position = market_position.get("overall_position", {})
        percentile = overall_position.get("average_percentile", 50)
        
        if percentile < 25:
            recommendations.append("Focus on fundamental improvements in content quality and consistency")
            recommendations.append("Study and model successful competitors in your tier")
        elif percentile < 50:
            recommendations.append("Identify 2-3 key areas for competitive improvement")
            recommendations.append("Consider strategic partnerships with higher-tier creators")
        elif percentile < 75:
            recommendations.append("Focus on differentiation and unique value proposition")
            recommendations.append("Explore premium monetization strategies")
        else:
            recommendations.append("Maintain market leadership through innovation")
            recommendations.append("Consider mentoring or collaborative opportunities")
        
        # Gap-based recommendations
        top_gaps = sorted(gaps, key=lambda x: x.priority_score, reverse=True)[:2]
        for gap in top_gaps:
            recommendations.extend(gap.recommendations[:1])  # Top recommendation per gap
        
        # Opportunity-based recommendations
        top_opportunities = sorted(opportunities, key=lambda x: x.success_probability, reverse=True)[:2]
        for opportunity in top_opportunities:
            recommendations.append(f"Pursue {opportunity.opportunity_type}: {opportunity.description}")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    async def _assess_threats(self, 
                            creator_id: str,
                            competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Assess competitive threats"""
        threat_assessment = {}
        
        # Identify direct threats
        direct_threats = [
            comp for comp in competitors 
            if comp.tier in [CompetitorTier.DIRECT, CompetitorTier.EMERGING]
        ]
        
        # Growth rate threats
        high_growth_competitors = [
            comp for comp in competitors
            if comp.metrics.get(MetricType.GROWTH_RATE, 0) > 0.2  # >20% growth
        ]
        
        threat_assessment["immediate_threats"] = [
            {
                "competitor_id": comp.competitor_id,
                "name": comp.name,
                "threat_type": "high_growth",
                "growth_rate": comp.metrics.get(MetricType.GROWTH_RATE, 0),
                "risk_level": "high" if comp.metrics.get(MetricType.GROWTH_RATE, 0) > 0.25 else "medium"
            }
            for comp in high_growth_competitors
        ]
        
        # Market share threats
        threat_assessment["market_pressure"] = {
            "total_competitors": len(competitors),
            "direct_competitors": len(direct_threats),
            "market_saturation": "medium",  # Simplified assessment
            "entry_barriers": ["Content quality", "Audience building", "Monetization setup"]
        }
        
        # Trending threats
        threat_assessment["emerging_trends"] = [
            "New platform adoption by competitors",
            "Advanced monetization strategies",
            "AI-enhanced content creation",
            "Cross-platform integration"
        ]
        
        return threat_assessment
    
    async def _analyze_market_trends(self, 
                                   competitors: List[CompetitorProfile],
                                   time_period: timedelta) -> Dict[str, Any]:
        """Analyze market trends from competitor data"""
        trends = {}
        
        # Platform trends
        platform_adoption = defaultdict(int)
        for competitor in competitors:
            for platform in competitor.platforms.keys():
                platform_adoption[platform.value] += 1
        
        trends["platform_trends"] = {
            "most_popular": max(platform_adoption.items(), key=lambda x: x[1])[0] if platform_adoption else "unknown",
            "adoption_rates": dict(platform_adoption),
            "emerging_platforms": [platform for platform, count in platform_adoption.items() if count < len(competitors) * 0.3]
        }
        
        # Content trends
        content_types = []
        for competitor in competitors:
            content_mix = competitor.content_strategy.get("content_mix", [])
            content_types.extend(content_mix)
        
        content_popularity = Counter(content_types)
        
        trends["content_trends"] = {
            "trending_content": dict(content_popularity.most_common(5)),
            "content_diversity": len(set(content_types)),
            "specialization_vs_diversification": "diversification" if len(set(content_types)) > 10 else "specialization"
        }
        
        # Monetization trends
        monetization_streams = []
        for competitor in competitors:
            monetization_streams.extend(competitor.monetization_streams)
        
        monetization_popularity = Counter(monetization_streams)
        
        trends["monetization_trends"] = {
            "popular_streams": dict(monetization_popularity.most_common(5)),
            "avg_streams_per_creator": len(monetization_streams) / len(competitors) if competitors else 0,
            "innovation_level": "high" if len(set(monetization_streams)) > 8 else "medium"
        }
        
        return trends
    
    # Helper methods
    def _categorize_performance(self, ratio: float) -> str:
        """Categorize performance ratio"""
        if ratio >= 1.5:
            return "excellent"
        elif ratio >= 1.1:
            return "above_average"
        elif ratio >= 0.9:
            return "average"
        elif ratio >= 0.7:
            return "below_average"
        else:
            return "poor"
    
    def _rate_market_position(self, percentile: float) -> str:
        """Rate market position based on percentile"""
        if percentile >= 80:
            return "leader"
        elif percentile >= 60:
            return "strong"
        elif percentile >= 40:
            return "average"
        elif percentile >= 20:
            return "weak"
        else:
            return "challenger"
    
    def _determine_market_tier(self, percentile: float) -> str:
        """Determine market tier based on average percentile"""
        if percentile >= 75:
            return "top_tier"
        elif percentile >= 50:
            return "mid_tier"
        elif percentile >= 25:
            return "lower_mid_tier"
        else:
            return "entry_tier"
    
    def _assess_competitive_strength(self, percentile: float) -> str:
        """Assess competitive strength"""
        if percentile >= 70:
            return "strong"
        elif percentile >= 40:
            return "moderate"
        else:
            return "weak"
    
    def _assess_growth_potential(self, 
                               creator_metrics: Dict[MetricType, float],
                               competitors: List[CompetitorProfile]) -> str:
        """Assess growth potential"""
        creator_growth = creator_metrics.get(MetricType.GROWTH_RATE, 0)
        competitor_growth_rates = [
            comp.metrics.get(MetricType.GROWTH_RATE, 0) for comp in competitors
        ]
        avg_competitor_growth = statistics.mean(competitor_growth_rates) if competitor_growth_rates else 0
        
        if creator_growth > avg_competitor_growth * 1.2:
            return "high"
        elif creator_growth > avg_competitor_growth * 0.8:
            return "moderate"
        else:
            return "low"
    
    async def _prioritize_platforms(self, 
                                  platforms: Set[PlatformChannel],
                                  competitors: List[CompetitorProfile]) -> List[str]:
        """Prioritize platform expansion opportunities"""
        platform_scores = {}
        
        for platform in platforms:
            # Count competitors on platform
            competitor_count = sum(
                1 for comp in competitors if platform in comp.platforms
            )
            
            # Simple scoring (more competitors = higher opportunity)
            platform_scores[platform.value] = competitor_count
        
        # Sort by score
        sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        return [platform for platform, score in sorted_platforms]
    
    async def _detect_profile_changes(self, 
                                    competitor_id: str,
                                    period: timedelta) -> List[Dict[str, Any]]:
        """Detect changes in competitor profile (simulated)"""
        # This would compare historical data in production
        # For now, return simulated changes
        changes = [
            {
                "change_type": "follower_growth",
                "description": "Significant follower increase",
                "impact": 0.7,
                "date": datetime.now() - timedelta(days=3)
            },
            {
                "change_type": "content_strategy",
                "description": "New content type introduced",
                "impact": 0.5,
                "date": datetime.now() - timedelta(days=1)
            }
        ]
        
        return changes
    
    async def _summarize_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize detected changes"""
        total_changes = sum(len(data["changes"]) for data in changes.values())
        high_impact_changes = sum(
            1 for data in changes.values()
            for change in data["changes"]
            if change.get("impact", 0) > 0.6
        )
        
        return {
            "total_changes": total_changes,
            "high_impact_changes": high_impact_changes,
            "most_active_competitor": max(changes.items(), key=lambda x: x[1]["change_score"])[0] if changes else None,
            "change_categories": ["follower_growth", "content_strategy", "monetization", "partnerships"]
        }
    
    async def _compare_against_competitors(self, 
                                         creator_metrics: Dict[MetricType, float],
                                         competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Compare creator metrics against specific competitors"""
        comparison = {}
        
        for metric, creator_value in creator_metrics.items():
            competitor_values = [
                comp.metrics.get(metric, 0) for comp in competitors
                if metric in comp.metrics
            ]
            
            if competitor_values:
                comparison[metric.value] = {
                    "creator_value": creator_value,
                    "competitor_average": statistics.mean(competitor_values),
                    "creator_rank": sum(1 for v in competitor_values if v < creator_value) + 1,
                    "total_competitors": len(competitor_values) + 1,
                    "percentile": (sum(1 for v in competitor_values if v < creator_value) / len(competitor_values)) * 100,
                    "gap_to_leader": max(competitor_values) - creator_value if competitor_values else 0
                }
        
        return comparison
    
    async def _calculate_percentile(self, score: float, niche: str) -> float:
        """Calculate performance percentile for niche"""
        # Simplified percentile calculation
        # In production, this would use historical niche data
        if score >= 2.0:
            return 95.0
        elif score >= 1.5:
            return 85.0
        elif score >= 1.2:
            return 70.0
        elif score >= 1.0:
            return 50.0
        elif score >= 0.8:
            return 30.0
        else:
            return 15.0
    
    def _assign_performance_grade(self, score: float) -> str:
        """Assign performance grade"""
        if score >= 1.8:
            return "A+"
        elif score >= 1.5:
            return "A"
        elif score >= 1.2:
            return "B+"
        elif score >= 1.0:
            return "B"
        elif score >= 0.8:
            return "C+"
        elif score >= 0.6:
            return "C"
        else:
            return "D"
    
    async def _generate_improvement_recommendations(self, 
                                                  industry_comparison: Dict[str, Any],
                                                  creator_metrics: Dict[MetricType, float],
                                                  niche: str) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Find lowest performing metrics
        underperforming_metrics = [
            metric for metric, data in industry_comparison.items()
            if data.get("performance_ratio", 1.0) < 0.8
        ]
        
        for metric in underperforming_metrics[:3]:  # Top 3 issues
            if metric == "engagement_rate":
                recommendations.append("Focus on creating more engaging content and improving call-to-actions")
            elif metric == "content_frequency":
                recommendations.append("Increase posting consistency and frequency")
            elif metric == "growth_rate":
                recommendations.append("Implement growth strategies like collaborations and cross-platform promotion")
        
        # Niche-specific recommendations
        if niche == "gaming":
            recommendations.append("Consider live streaming and interactive content")
        elif niche == "lifestyle":
            recommendations.append("Focus on high-quality visuals and storytelling")
        elif niche == "education":
            recommendations.append("Create comprehensive tutorials and course content")
        
        return recommendations[:5]
    
    def _generate_cache_key(self, request: CompetitiveAnalysisRequest) -> str:
        """Generate cache key for analysis"""
        key_data = f"{request.analysis_id}_{request.creator_id}_{'_'.join(request.competitor_ids)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_analysis(self, cache_key: str) -> Optional[CompetitiveIntelligenceResult]:
        """Get analysis from cache if available and not expired"""
        if cache_key in self.analysis_cache:
            result = self.analysis_cache[cache_key]
            if datetime.now() < result.expires_at:
                return result
            else:
                del self.analysis_cache[cache_key]
        return None
    
    async def _cache_analysis(self, cache_key: str, result: CompetitiveIntelligenceResult) -> None:
        """Cache analysis result"""
        self.analysis_cache[cache_key] = result
        
        # Clean up expired cache entries
        current_time = datetime.now()
        expired_keys = [
            key for key, cached_result in self.analysis_cache.items()
            if current_time >= cached_result.expires_at
        ]
        for key in expired_keys:
            del self.analysis_cache[key]


# Export main classes
__all__ = [
    "CompetitorIntelligence",
    "CompetitiveAnalysisRequest",
    "CompetitiveIntelligenceResult",
    "CompetitorProfile",
    "CompetitiveGap",
    "MarketOpportunity",
    "CompetitorTier",
    "AnalysisScope",
    "MetricType",
    "PlatformChannel"
]