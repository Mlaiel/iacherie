"""Competitive Intelligence Analytics - IA Influencer Agent Platform

Advanced competitive analysis and market intelligence for content creators.
Tracks competitors, analyzes market trends, and provides strategic insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from uuid import UUID, uuid4

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()


class CompetitorTier(Enum):
    """
Competitor classification tiers"""

    DIRECT = "direct"
    INDIRECT = "indirect"
    ASPIRATIONAL = "aspirational"
    EMERGING = "emerging"
    DECLINING = "declining"


class AnalysisType(Enum):
    """Types of competitive analysis"""

    CONTENT_STRATEGY = "content_strategy"
    ENGAGEMENT_PATTERNS = "engagement_patterns"
    AUDIENCE_OVERLAP = "audience_overlap"
    POSTING_FREQUENCY = "posting_frequency"
    HASHTAG_STRATEGY = "hashtag_strategy"
    COLLABORATION_NETWORK = "collaboration_network"
    REVENUE_ESTIMATION = "revenue_estimation"
    GROWTH_TRAJECTORY = "growth_trajectory"


class MarketPosition(Enum):
    """Market positioning categories"""

    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE_SPECIALIST = "niche_specialist"
    INNOVATOR = "innovator"


@dataclass
class CompetitorProfile:
    """Comprehensive competitor profile"""
    competitor_id: str
    name: str
    platforms: List[str]
    tier: CompetitorTier
    market_position: MarketPosition
    
    # Metrics
    total_followers: int
    avg_engagement_rate: float
    posting_frequency: float
    content_quality_score: float
    
    # Strategy insights
    content_themes: List[str]
    top_hashtags: List[str]
    posting_times: List[int]
    collaboration_score: float
    
    # Performance tracking
    growth_rate_30d: float
    performance_score: float
    threat_level: float
    opportunity_score: float
    
    last_analyzed: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary for serialization"""
        return {
            "competitor_id": self.competitor_id,
            "name": self.name,
            "platforms": self.platforms,
            "tier": self.tier.value,
            "market_position": self.market_position.value,
            "total_followers": self.total_followers,
            "avg_engagement_rate": self.avg_engagement_rate,
            "posting_frequency": self.posting_frequency,
            "content_quality_score": self.content_quality_score,
            "content_themes": self.content_themes,
            "top_hashtags": self.top_hashtags,
            "posting_times": self.posting_times,
            "collaboration_score": self.collaboration_score,
            "growth_rate_30d": self.growth_rate_30d,
            "performance_score": self.performance_score,
            "threat_level": self.threat_level,
            "opportunity_score": self.opportunity_score,
            "last_analyzed": self.last_analyzed.isoformat()
        }


class CompetitorAnalysis(Base):
    """Database model for competitor analysis data"""
    __tablename__ = "competitor_analysis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    competitor_id = Column(String, nullable=False, index=True)
    
    # Competitor information
    competitor_name = Column(String, nullable=False)
    platforms = Column(JSON)
    tier = Column(String, nullable=False)
    market_position = Column(String)
    
    # Performance metrics
    total_followers = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    posting_frequency = Column(Float, default=0.0)
    content_quality_score = Column(Float, default=0.0)
    growth_rate_30d = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    
    # Strategic analysis
    content_themes = Column(JSON)
    top_hashtags = Column(JSON)
    posting_times = Column(JSON)
    collaboration_score = Column(Float, default=0.0)
    threat_level = Column(Float, default=0.0)
    opportunity_score = Column(Float, default=0.0)
    
    # Analysis metadata
    analysis_type = Column(String)
    data_sources = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    insights = relationship("CompetitorInsight", back_populates="analysis")


class CompetitorInsight(Base):
    """Database model for competitor insights"""
    __tablename__ = "competitor_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    analysis_id = Column(String, ForeignKey("competitor_analysis.id"))
    
    insight_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    strategic_implication = Column(Text)
    
    # Actionable recommendations
    recommendations = Column(JSON)
    priority = Column(String, default="medium")
    effort_required = Column(String, default="medium")
    expected_impact = Column(Float, default=0.0)
    
    # Supporting data
    supporting_data = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("CompetitorAnalysis", back_populates="insights")


class MarketIntelligence(Base):
    """Database model for market intelligence data"""
    __tablename__ = "market_intelligence"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False, index=True)
    market_segment = Column(String, nullable=False)
    
    # Market metrics
    total_market_size = Column(Integer)
    active_creators = Column(Integer)
    avg_engagement_rate = Column(Float)
    growth_rate = Column(Float)
    
    # Trend analysis
    emerging_trends = Column(JSON)
    declining_trends = Column(JSON)
    opportunity_areas = Column(JSON)
    threat_factors = Column(JSON)
    
    # Competitive landscape
    market_leaders = Column(JSON)
    market_gaps = Column(JSON)
    barrier_to_entry = Column(Float)
    market_saturation = Column(Float)
    
    # Analysis metadata
    data_sources = Column(JSON)
    analysis_period = Column(String)
    confidence_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CompetitiveIntelligenceEngine:
    """
    Advanced competitive intelligence engine for content creators.
    Provides comprehensive competitor analysis, market insights, and strategic recommendations.
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.ml_models = {}
        self.competitor_cache = {}
        
        # Initialize ML models for analysis
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """
Initialize machine learning models for competitive analysis"""
        try:
            # Initialize clustering model for competitor segmentation
            self.ml_models['competitor_clustering'] = KMeans(n_clusters=5, random_state=42)
            
            # Initialize similarity model for content analysis
            self.ml_models['content_similarity'] = StandardScaler()
            
            # Initialize network analysis for collaboration mapping
            self.ml_models['collaboration_network'] = nx.Graph()
            
        except Exception as e:
            print(f"Warning: Could not initialize all ML models: {e}")
    
    async def discover_competitors(self, user_id: str, user_profile: Dict[str, Any]) -> List[CompetitorProfile]:
        """Discover and identify relevant competitors for user"""
        try:
            competitors = []
            
            # Extract user characteristics for competitor matching
            user_niche = user_profile.get("niche", "general")
            user_platforms = user_profile.get("platforms", [])
            user_content_themes = user_profile.get("content_themes", [])
            user_follower_count = user_profile.get("followers", 0)
            
            # Discover competitors through multiple methods
            
            # 1. Hashtag-based discovery
            hashtag_competitors = await self._discover_by_hashtags(user_profile.get("hashtags", []))
            competitors.extend(hashtag_competitors)
            
            # 2. Content similarity discovery
            similarity_competitors = await self._discover_by_content_similarity(user_content_themes)
            competitors.extend(similarity_competitors)
            
            # 3. Audience overlap discovery
            audience_competitors = await self._discover_by_audience_overlap(user_id)
            competitors.extend(audience_competitors)
            
            # 4. Platform-specific discovery
            platform_competitors = await self._discover_by_platform(user_platforms, user_niche)
            competitors.extend(platform_competitors)
            
            # Remove duplicates and rank by relevance
            unique_competitors = self._deduplicate_competitors(competitors)
            ranked_competitors = await self._rank_competitors_by_relevance(unique_competitors, user_profile)
            
            # Store discovered competitors
            await self._store_competitor_discoveries(user_id, ranked_competitors)
            
            return ranked_competitors[:20]  # Return top 20
            
        except Exception as e:
            print(f"Failed to discover competitors: {e}")
            return []
    
    async def _discover_by_hashtags(self, user_hashtags: List[str]) -> List[CompetitorProfile]:
        """Discover competitors using hashtag overlap"""
        competitors = []
        
        # Mock hashtag-based discovery (would use actual social media APIs)
        hashtag_data = {
            "#music": ["artist_1", "musician_2", "producer_3"],
            "#photography": ["photographer_1", "visual_artist_2"],
            "#comedy": ["comedian_1", "entertainer_2"],
            "#lifestyle": ["influencer_1", "blogger_2"]
        }
        
        discovered_accounts = set()
        for hashtag in user_hashtags:
            if hashtag in hashtag_data:
                discovered_accounts.update(hashtag_data[hashtag])
        
        # Create competitor profiles for discovered accounts
        for account in discovered_accounts:
            competitor = CompetitorProfile(
                competitor_id=account,
                name=account.replace("_", " ").title(),
                platforms=["instagram", "youtube"],
                tier=CompetitorTier.DIRECT,
                market_position=MarketPosition.CHALLENGER,
                total_followers=np.random.randint(1000, 100000),
                avg_engagement_rate=np.random.uniform(2.0, 15.0),
                posting_frequency=np.random.uniform(3.0, 20.0),
                content_quality_score=np.random.uniform(0.6, 0.9),
                content_themes=user_hashtags[:3],
                top_hashtags=user_hashtags,
                posting_times=[9, 12, 18, 20],
                collaboration_score=np.random.uniform(0.3, 0.8),
                growth_rate_30d=np.random.uniform(-5.0, 25.0),
                performance_score=np.random.uniform(60.0, 95.0),
                threat_level=np.random.uniform(0.2, 0.7),
                opportunity_score=np.random.uniform(0.3, 0.8)
            )
            competitors.append(competitor)
        
        return competitors
    
    async def _discover_by_content_similarity(self, content_themes: List[str]) -> List[CompetitorProfile]:
        """Discover competitors with similar content themes"""
        competitors = []
        
        # Mock content similarity discovery
        theme_clusters = {
            "music_production": ["beat_maker_1", "music_producer_2", "studio_artist_3"],
            "photography": ["landscape_photographer", "portrait_artist", "street_photographer"],
            "comedy": ["stand_up_comic", "sketch_comedian", "viral_creator"],
            "lifestyle": ["lifestyle_blogger", "wellness_influencer", "travel_creator"]
        }
        
        for theme in content_themes:
            if theme in theme_clusters:
                for account in theme_clusters[theme]:
                    competitor = CompetitorProfile(
                        competitor_id=account,
                        name=account.replace("_", " ").title(),
                        platforms=["youtube", "instagram", "tiktok"],
                        tier=CompetitorTier.INDIRECT,
                        market_position=MarketPosition.FOLLOWER,
                        total_followers=np.random.randint(5000, 500000),
                        avg_engagement_rate=np.random.uniform(3.0, 12.0),
                        posting_frequency=np.random.uniform(5.0, 15.0),
                        content_quality_score=np.random.uniform(0.7, 0.95),
                        content_themes=[theme],
                        top_hashtags=[f"#{theme}", "#content", "#creator"],
                        posting_times=[10, 14, 19],
                        collaboration_score=np.random.uniform(0.4, 0.9),
                        growth_rate_30d=np.random.uniform(0.0, 30.0),
                        performance_score=np.random.uniform(70.0, 90.0),
                        threat_level=np.random.uniform(0.1, 0.5),
                        opportunity_score=np.random.uniform(0.4, 0.9)
                    )
                    competitors.append(competitor)
        
        return competitors
    
    async def _discover_by_audience_overlap(self, user_id: str) -> List[CompetitorProfile]:
        """Discover competitors with overlapping audiences"""
        # This would analyze audience overlap using social media analytics
        # For now, returning mock data
        return []
    
    async def _discover_by_platform(self, platforms: List[str], niche: str) -> List[CompetitorProfile]:
        """
Discover competitors on same platforms and niche"""
        competitors = []
        
        # Mock platform-specific discovery
        platform_leaders = {
            "youtube": ["youtube_creator_1", "video_artist_2", "content_king_3"],
            "instagram": ["insta_influencer_1", "visual_storyteller_2"],
            "tiktok": ["tiktok_star_1", "viral_creator_2", "trend_setter_3"]
        }
        
        for platform in platforms:
            if platform in platform_leaders:
                for creator in platform_leaders[platform]:
                    competitor = CompetitorProfile(
                        competitor_id=f"{platform}_{creator}",
                        name=creator.replace("_", " ").title(),
                        platforms=[platform],
                        tier=CompetitorTier.ASPIRATIONAL,
                        market_position=MarketPosition.LEADER,
                        total_followers=np.random.randint(50000, 1000000),
                        avg_engagement_rate=np.random.uniform(5.0, 20.0),
                        posting_frequency=np.random.uniform(7.0, 25.0),
                        content_quality_score=np.random.uniform(0.8, 0.98),
                        content_themes=[niche, "trending", "viral"],
                        top_hashtags=[f"#{niche}", f"#{platform}", "#viral"],
                        posting_times=[8, 12, 16, 20],
                        collaboration_score=np.random.uniform(0.6, 0.95),
                        growth_rate_30d=np.random.uniform(10.0, 50.0),
                        performance_score=np.random.uniform(85.0, 98.0),
                        threat_level=np.random.uniform(0.4, 0.8),
                        opportunity_score=np.random.uniform(0.2, 0.6)
                    )
                    competitors.append(competitor)
        
        return competitors
    
    def _deduplicate_competitors(self, competitors: List[CompetitorProfile]) -> List[CompetitorProfile]:
        """Remove duplicate competitors based on similarity"""
        unique_competitors = {}
        
        for competitor in competitors:
            # Use name similarity to identify duplicates
            key = competitor.name.lower().replace(" ", "")
            if key not in unique_competitors:
                unique_competitors[key] = competitor
            else:
                # Keep the one with higher performance score
                if competitor.performance_score > unique_competitors[key].performance_score:
                    unique_competitors[key] = competitor
        
        return list(unique_competitors.values())
    
    async def _rank_competitors_by_relevance(self, competitors: List[CompetitorProfile], user_profile: Dict[str, Any]) -> List[CompetitorProfile]:
        """Rank competitors by relevance to user"""
        user_followers = user_profile.get("followers", 0)
        user_engagement = user_profile.get("engagement_rate", 0)
        user_themes = set(user_profile.get("content_themes", []))
        
        def calculate_relevance_score(competitor: CompetitorProfile) -> float:
            score = 0.0
            
            # Follower similarity (prefer similar-sized creators)
            follower_ratio = min(competitor.total_followers / max(user_followers, 1), 
                                user_followers / max(competitor.total_followers, 1))
            score += follower_ratio * 30
            
            # Content theme overlap
            competitor_themes = set(competitor.content_themes)
            theme_overlap = len(user_themes.intersection(competitor_themes)) / max(len(user_themes.union(competitor_themes)), 1)
            score += theme_overlap * 40
            
            # Performance score
            score += competitor.performance_score * 0.2
            
            # Tier importance
            tier_weights = {
                CompetitorTier.DIRECT: 1.0,
                CompetitorTier.INDIRECT: 0.8,
                CompetitorTier.ASPIRATIONAL: 0.9,
                CompetitorTier.EMERGING: 0.7,
                CompetitorTier.DECLINING: 0.3
            }
            score *= tier_weights.get(competitor.tier, 0.5)
            
            return score
        
        # Calculate relevance scores and sort
        for competitor in competitors:
            competitor.relevance_score = calculate_relevance_score(competitor)
        
        return sorted(competitors, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)
    
    async def _store_competitor_discoveries(self, user_id: str, competitors: List[CompetitorProfile]):
        """Store discovered competitors in database"""
        try:
            for competitor in competitors:
                # Check if competitor already exists
                existing = self.db_session.query(CompetitorAnalysis).filter(
                    CompetitorAnalysis.user_id == user_id,
                    CompetitorAnalysis.competitor_id == competitor.competitor_id
                ).first()
                
                if not existing:
                    analysis = CompetitorAnalysis(
                        user_id=user_id,
                        competitor_id=competitor.competitor_id,
                        competitor_name=competitor.name,
                        platforms=competitor.platforms,
                        tier=competitor.tier.value,
                        market_position=competitor.market_position.value,
                        total_followers=competitor.total_followers,
                        avg_engagement_rate=competitor.avg_engagement_rate,
                        posting_frequency=competitor.posting_frequency,
                        content_quality_score=competitor.content_quality_score,
                        growth_rate_30d=competitor.growth_rate_30d,
                        performance_score=competitor.performance_score,
                        content_themes=competitor.content_themes,
                        top_hashtags=competitor.top_hashtags,
                        posting_times=competitor.posting_times,
                        collaboration_score=competitor.collaboration_score,
                        threat_level=competitor.threat_level,
                        opportunity_score=competitor.opportunity_score,
                        analysis_type="discovery",
                        confidence_score=0.8
                    )
                    self.db_session.add(analysis)
            
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to store competitor discoveries: {e}")
    
    async def analyze_competitor_strategies(self, user_id: str, competitor_id: str) -> Dict[str, Any]:
        """Analyze specific competitor's strategies and tactics"""
        try:
            # Get competitor data
            competitor_analysis = self.db_session.query(CompetitorAnalysis).filter(
                CompetitorAnalysis.user_id == user_id,
                CompetitorAnalysis.competitor_id == competitor_id
            ).first()
            
            if not competitor_analysis:
                return {"error": "Competitor not found"}
            
            strategy_analysis = {
                "competitor_id": competitor_id,
                "competitor_name": competitor_analysis.competitor_name,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "content_strategy": await self._analyze_content_strategy(competitor_analysis),
                "engagement_strategy": await self._analyze_engagement_strategy(competitor_analysis),
                "posting_strategy": await self._analyze_posting_strategy(competitor_analysis),
                "hashtag_strategy": await self._analyze_hashtag_strategy(competitor_analysis),
                "collaboration_strategy": await self._analyze_collaboration_strategy(competitor_analysis),
                "growth_strategy": await self._analyze_growth_strategy(competitor_analysis),
                "monetization_strategy": await self._analyze_monetization_strategy(competitor_analysis),
                "competitive_advantages": await self._identify_competitive_advantages(competitor_analysis),
                "strategic_insights": await self._generate_strategic_insights(competitor_analysis),
                "actionable_recommendations": await self._generate_competitive_recommendations(user_id, competitor_analysis)
            }
            
            # Store insights
            await self._store_competitor_insights(competitor_analysis.id, strategy_analysis)
            
            return strategy_analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze competitor strategies: {str(e)}"}
    
    async def _analyze_content_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's content strategy"""
        return {
            "primary_themes": competitor.content_themes[:5],
            "content_quality_score": competitor.content_quality_score,
            "posting_frequency": competitor.posting_frequency,
            "content_variety": len(set(competitor.content_themes)),
            "trend_adoption_speed": "high",  # Would be calculated from actual data
            "content_format_mix": {
                "video": 60,
                "image": 25,
                "text": 10,
                "live": 5
            },
            "engagement_per_post": competitor.avg_engagement_rate * competitor.total_followers / 100,
            "content_pillars": competitor.content_themes[:3],
            "seasonal_content": "yes",
            "user_generated_content": "moderate"
        }
    
    async def _analyze_engagement_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's engagement strategy"""
        return {
            "avg_engagement_rate": competitor.avg_engagement_rate,
            "engagement_tactics": [
                "Interactive stories",
                "Community posts",
                "Live sessions",
                "Giveaways"
            ],
            "response_rate": 85,  # Mock data
            "response_time": "2-4 hours",
            "community_building": "strong",
            "influencer_partnerships": "regular",
            "audience_interaction_score": competitor.collaboration_score * 100
        }
    
    async def _analyze_posting_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's posting strategy"""
        return {
            "posting_frequency": competitor.posting_frequency,
            "optimal_posting_times": competitor.posting_times,
            "posting_consistency": "high",
            "cross_platform_coordination": "synchronized",
            "content_scheduling": "strategic",
            "platform_specific_adaptation": "yes",
            "posting_pattern": "consistent_daily"
        }
    
    async def _analyze_hashtag_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's hashtag strategy"""
        return {
            "top_hashtags": competitor.top_hashtags,
            "hashtag_count_per_post": len(competitor.top_hashtags),
            "hashtag_variety": "high",
            "trending_hashtag_adoption": "fast",
            "branded_hashtags": f"#{competitor.competitor_name.lower().replace(' ', '')}",
            "hashtag_performance": "above_average",
            "niche_hashtags_ratio": 70,
            "popular_hashtags_ratio": 30
        }
    
    async def _analyze_collaboration_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's collaboration strategy"""
        return {
            "collaboration_score": competitor.collaboration_score,
            "partnership_frequency": "monthly",
            "collaboration_types": [
                "Influencer partnerships",
                "Brand collaborations", 
                "Cross-promotions",
                "Guest appearances"
            ],
            "network_strength": "strong",
            "brand_partnerships": "multiple",
            "creator_collaborations": "regular"
        }
    
    async def _analyze_growth_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's growth strategy"""
        return {
            "growth_rate_30d": competitor.growth_rate_30d,
            "growth_tactics": [
                "Viral content creation",
                "Trend participation",
                "Cross-platform promotion",
                "Community engagement"
            ],
            "audience_retention": "high",
            "new_follower_acquisition": "steady",
            "platform_expansion": "active",
            "growth_stage": "scaling"
        }
    
    async def _analyze_monetization_strategy(self, competitor: CompetitorAnalysis) -> Dict[str, Any]:
        """Analyze competitor's monetization strategy"""
        estimated_revenue = competitor.total_followers * 0.01  # Rough estimate
        
        return {
            "estimated_monthly_revenue": estimated_revenue,
            "revenue_streams": [
                "Sponsored content",
                "Affiliate marketing",
                "Product sales",
                "Brand partnerships"
            ],
            "monetization_effectiveness": "high",
            "pricing_strategy": "premium",
            "product_diversification": "moderate"
        }
    
    async def _identify_competitive_advantages(self, competitor: CompetitorAnalysis) -> List[Dict[str, Any]]:
        """Identify competitor's competitive advantages"""
        advantages = []
        
        if competitor.content_quality_score > 0.8:
            advantages.append({
                "advantage": "High Content Quality",
                "description": "Consistently produces high-quality content",
                "strength_level": "high",
                "impact": "Builds trust and loyalty with audience"
            })
        
        if competitor.avg_engagement_rate > 8.0:
            advantages.append({
                "advantage": "Strong Audience Engagement",
                "description": "Maintains high engagement rates",
                "strength_level": "high",
                "impact": "Increased algorithm visibility and reach"
            })
        
        if competitor.collaboration_score > 0.7:
            advantages.append({
                "advantage": "Strong Network",
                "description": "Well-connected in the creator community",
                "strength_level": "medium",
                "impact": "Access to collaboration opportunities"
            })
        
        if competitor.growth_rate_30d > 15.0:
            advantages.append({
                "advantage": "Rapid Growth",
                "description": "Experiencing fast follower growth",
                "strength_level": "high",
                "impact": "Increasing market share and influence"
            })
        
        return advantages
    
    async def _generate_strategic_insights(self, competitor: CompetitorAnalysis) -> List[Dict[str, str]]:
        """Generate strategic insights about competitor"""
        insights = []
        
        # Performance insights
        if competitor.performance_score > 90:
            insights.append({
                "category": "Performance",
                "insight": "Top performer in their category",
                "implication": "High competitive threat, study their strategies"
            })
        
        # Growth insights
        if competitor.growth_rate_30d > 20:
            insights.append({
                "category": "Growth", 
                "insight": "Experiencing rapid growth phase",
                "implication": "Identify and adopt their growth tactics"
            })
        
        # Engagement insights
        if competitor.avg_engagement_rate > 10:
            insights.append({
                "category": "Engagement",
                "insight": "Exceptional audience engagement",
                "implication": "Analyze their community building strategies"
            })
        
        # Content insights
        if competitor.posting_frequency > 15:
            insights.append({
                "category": "Content",
                "insight": "High content production volume",
                "implication": "May struggle with quality consistency"
            })
        
        return insights
    
    async def _generate_competitive_recommendations(self, user_id: str, competitor: CompetitorAnalysis) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on competitor analysis"""
        recommendations = []
        
        # Content strategy recommendations
        if competitor.content_quality_score > 0.85:
            recommendations.append({
                "category": "Content Strategy",
                "title": "Improve Content Quality",
                "description": f"{competitor.competitor_name} has high content quality scores",
                "action": "Invest in better equipment and production values",
                "priority": "high",
                "effort": "medium",
                "expected_impact": "20% engagement increase"
            })
        
        # Posting frequency recommendations  
        if competitor.posting_frequency > 12:
            recommendations.append({
                "category": "Posting Strategy",
                "title": "Increase Posting Frequency",
                "description": f"Competitor posts {competitor.posting_frequency} times per week",
                "action": "Develop content calendar for more frequent posting",
                "priority": "medium",
                "effort": "high",
                "expected_impact": "15% reach increase"
            })
        
        # Collaboration recommendations
        if competitor.collaboration_score > 0.8:
            recommendations.append({
                "category": "Networking",
                "title": "Expand Collaboration Network",
                "description": "Competitor has strong collaboration network",
                "action": "Reach out to creators for partnerships",
                "priority": "high",
                "effort": "medium",
                "expected_impact": "25% audience growth"
            })
        
        # Hashtag strategy recommendations
        if len(competitor.top_hashtags) > 10:
            recommendations.append({
                "category": "Discoverability",
                "title": "Optimize Hashtag Strategy",
                "description": "Competitor uses diverse hashtag strategy",
                "action": "Research and implement competitor's hashtag approach",
                "priority": "medium",
                "effort": "low",
                "expected_impact": "10% discoverability increase"
            })
        
        return recommendations
    
    async def _store_competitor_insights(self, analysis_id: str, strategy_analysis: Dict[str, Any]):
        """Store competitor insights in database"""
        try:
            # Store key insights as separate records
            for category, insights in strategy_analysis.items():
                if category in ["strategic_insights", "actionable_recommendations"]:
                    if isinstance(insights, list):
                        for insight_data in insights:
                            insight = CompetitorInsight(
                                analysis_id=analysis_id,
                                insight_type=category,
                                title=insight_data.get("title", insight_data.get("insight", "Unknown")),
                                description=insight_data.get("description", ""),
                                strategic_implication=insight_data.get("implication", insight_data.get("action", "")),
                                recommendations=insight_data.get("recommendations", []),
                                priority=insight_data.get("priority", "medium"),
                                effort_required=insight_data.get("effort", "medium"),
                                expected_impact=float(insight_data.get("expected_impact", "0").replace("%", "").split()[0]) if isinstance(insight_data.get("expected_impact"), str) else 0.0,
                                supporting_data=insight_data,
                                confidence_score=0.8
                            )
                            self.db_session.add(insight)
            
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to store competitor insights: {e}")
    
    async def generate_market_intelligence_report(self, user_id: str, market_segment: str) -> Dict[str, Any]:
        """Generate comprehensive market intelligence report"""
        try:
            report = {
                "market_segment": market_segment,
                "report_timestamp": datetime.utcnow().isoformat(),
                "market_overview": await self._analyze_market_overview(market_segment),
                "competitive_landscape": await self._analyze_competitive_landscape(user_id, market_segment),
                "market_trends": await self._analyze_market_trends(market_segment),
                "opportunity_analysis": await self._analyze_market_opportunities(user_id, market_segment),
                "threat_analysis": await self._analyze_market_threats(user_id, market_segment),
                "strategic_recommendations": await self._generate_market_recommendations(user_id, market_segment),
                "key_success_factors": await self._identify_success_factors(market_segment),
                "market_entry_barriers": await self._analyze_entry_barriers(market_segment)
            }
            
            # Store market intelligence
            await self._store_market_intelligence(user_id, market_segment, report)
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate market intelligence report: {str(e)}"}
    
    async def _analyze_market_overview(self, market_segment: str) -> Dict[str, Any]:
        """Analyze overall market conditions"""
        # Mock market data (would use real market intelligence in production)
        return {
            "total_market_size": 2500000,  # Total creators
            "active_creators": 1800000,
            "market_growth_rate": 15.2,
            "avg_engagement_rate": 6.8,
            "market_saturation": 0.72,
            "dominant_platforms": ["Instagram", "YouTube", "TikTok"],
            "emerging_platforms": ["BeReal", "Clubhouse", "Discord"],
            "market_maturity": "growth_stage"
        }
    
    async def _analyze_competitive_landscape(self, user_id: str, market_segment: str) -> Dict[str, Any]:
        """Analyze competitive landscape in market segment"""
        # Get all competitors for user
        competitors = self.db_session.query(CompetitorAnalysis).filter(
            CompetitorAnalysis.user_id == user_id
        ).all()
        
        if not competitors:
            return {"message": "No competitor data available"}
        
        # Analyze competitive positions
        market_leaders = [c for c in competitors if c.performance_score > 85]
        challengers = [c for c in competitors if 70 <= c.performance_score <= 85]
        followers = [c for c in competitors if c.performance_score < 70]
        
        return {
            "total_competitors_tracked": len(competitors),
            "market_leaders": len(market_leaders),
            "challengers": len(challengers),
            "followers": len(followers),
            "avg_performance_score": np.mean([c.performance_score for c in competitors]),
            "competitive_intensity": "high" if len(competitors) > 20 else "medium",
            "market_concentration": "fragmented",  # or "concentrated"
            "key_competitive_factors": [
                "Content quality",
                "Engagement rate", 
                "Posting consistency",
                "Collaboration network"
            ]
        }
    
    async def _analyze_market_trends(self, market_segment: str) -> Dict[str, Any]:
        """Analyze current market trends"""
        return {
            "emerging_trends": [
                {
                    "trend": "Short-form video content",
                    "growth_rate": 45.0,
                    "adoption_level": "mainstream",
                    "impact": "high"
                },
                {
                    "trend": "AI-generated content",
                    "growth_rate": 120.0,
                    "adoption_level": "early",
                    "impact": "medium"
                },
                {
                    "trend": "Live streaming",
                    "growth_rate": 25.0,
                    "adoption_level": "growing",
                    "impact": "high"
                }
            ],
            "declining_trends": [
                {
                    "trend": "Static image posts",
                    "decline_rate": -15.0,
                    "reason": "Algorithm preference for video"
                }
            ],
            "stable_trends": [
                "Educational content",
                "Behind-the-scenes content",
                "User-generated content"
            ]
        }
    
    async def _analyze_market_opportunities(self, user_id: str, market_segment: str) -> List[Dict[str, Any]]:
        """Identify market opportunities"""
        return [
            {
                "opportunity": "Underserved Niches",
                "description": "Several sub-niches with low competition",
                "potential_impact": "high",
                "effort_required": "medium",
                "time_to_market": "3-6 months"
            },
            {
                "opportunity": "Cross-Platform Expansion",
                "description": "Many creators focus on single platforms",
                "potential_impact": "medium",
                "effort_required": "high",
                "time_to_market": "6-12 months"
            },
            {
                "opportunity": "Collaboration Networks",
                "description": "Strong collaboration opportunities available",
                "potential_impact": "high",
                "effort_required": "low",
                "time_to_market": "1-3 months"
            }
        ]
    
    async def _analyze_market_threats(self, user_id: str, market_segment: str) -> List[Dict[str, Any]]:
        """Identify market threats"""
        return [
            {
                "threat": "Algorithm Changes",
                "description": "Platform algorithm updates affecting reach",
                "severity": "high",
                "probability": "high",
                "mitigation": "Diversify across multiple platforms"
            },
            {
                "threat": "Increased Competition",
                "description": "New creators entering market daily",
                "severity": "medium",
                "probability": "high",
                "mitigation": "Focus on unique value proposition"
            },
            {
                "threat": "Content Saturation",
                "description": "Similar content becoming oversaturated",
                "severity": "medium",
                "probability": "medium",
                "mitigation": "Innovate content formats and themes"
            }
        ]
    
    async def _generate_market_recommendations(self, user_id: str, market_segment: str) -> List[Dict[str, Any]]:
        """Generate strategic market recommendations"""
        return [
            {
                "category": "Market Positioning",
                "recommendation": "Focus on niche specialization",
                "rationale": "Market is fragmented with opportunities for specialists",
                "priority": "high",
                "timeline": "immediate"
            },
            {
                "category": "Content Strategy",
                "recommendation": "Adopt short-form video content",
                "rationale": "Fastest growing content format in market",
                "priority": "high",
                "timeline": "1-2 months"
            },
            {
                "category": "Platform Strategy",
                "recommendation": "Expand to 3+ platforms",
                "rationale": "Reduce platform dependency risk",
                "priority": "medium",
                "timeline": "3-6 months"
            }
        ]
    
    async def _identify_success_factors(self, market_segment: str) -> List[Dict[str, str]]:
        """Identify key success factors in market"""
        return [
            {
                "factor": "Content Quality",
                "importance": "critical",
                "description": "High production values drive engagement"
            },
            {
                "factor": "Consistency",
                "importance": "high",
                "description": "Regular posting maintains audience engagement"
            },
            {
                "factor": "Community Building",
                "importance": "high",
                "description": "Strong community drives loyalty and growth"
            },
            {
                "factor": "Trend Awareness",
                "importance": "medium",
                "description": "Quick adoption of trends increases visibility"
            }
        ]
    
    async def _analyze_entry_barriers(self, market_segment: str) -> Dict[str, Any]:
        """Analyze barriers to entry in market"""
        return {
            "overall_barrier_level": "medium",
            "barriers": [
                {
                    "barrier": "Content Quality Standards",
                    "level": "high",
                    "description": "Audience expects high production quality"
                },
                {
                    "barrier": "Algorithm Understanding",
                    "level": "medium",
                    "description": "Platform algorithms require expertise to navigate"
                },
                {
                    "barrier": "Network Effects",
                    "level": "medium",
                    "description": "Established creators have collaboration advantages"
                },
                {
                    "barrier": "Financial Investment",
                    "level": "low",
                    "description": "Low initial investment required to start"
                }
            ],
            "success_factors": [
                "Unique value proposition",
                "Consistent content creation",
                "Community engagement",
                "Cross-platform presence"
            ]
        }
    
    async def _store_market_intelligence(self, user_id: str, market_segment: str, report: Dict[str, Any]):
        """Store market intelligence report in database"""
        try:
            market_intel = MarketIntelligence(
                user_id=user_id,
                market_segment=market_segment,
                total_market_size=report["market_overview"].get("total_market_size"),
                active_creators=report["market_overview"].get("active_creators"),
                avg_engagement_rate=report["market_overview"].get("avg_engagement_rate"),
                growth_rate=report["market_overview"].get("market_growth_rate"),
                emerging_trends=[trend["trend"] for trend in report["market_trends"].get("emerging_trends", [])],
                declining_trends=[trend["trend"] for trend in report["market_trends"].get("declining_trends", [])],
                opportunity_areas=[opp["opportunity"] for opp in report["opportunity_analysis"]],
                threat_factors=[threat["threat"] for threat in report["threat_analysis"]],
                market_leaders=["Leader 1", "Leader 2"],  # Would extract from actual data
                market_gaps=["Gap 1", "Gap 2"],
                barrier_to_entry=0.6,  # Medium barrier level
                market_saturation=report["market_overview"].get("market_saturation", 0.5),
                data_sources=["social_media_apis", "competitor_analysis", "trend_analysis"],
                analysis_period="30_days",
                confidence_score=0.85
            )
            
            self.db_session.add(market_intel)
            self.db_session.commit()
            
        except Exception as e:
            self.db_session.rollback()
            print(f"Failed to store market intelligence: {e}")


# Export main classes and utilities
__all__ = [
    "CompetitiveIntelligenceEngine",
    "CompetitorProfile",
    "CompetitorAnalysis",
    "CompetitorInsight", 
    "MarketIntelligence",
    "CompetitorTier",
    "AnalysisType",
    "MarketPosition"
]
