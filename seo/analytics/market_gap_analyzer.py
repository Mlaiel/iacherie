"""Market Gap Analyzer - AI-Powered Market Opportunity Detection

This module analyzes market gaps and identifies content opportunities using advanced
AI algorithms, competitive intelligence, and predictive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class MarketGapType(Enum):
    """Types of market gaps"""
    KEYWORD_GAP = "keyword_gap"
    CONTENT_GAP = "content_gap"
    AUDIENCE_GAP = "audience_gap"
    PLATFORM_GAP = "platform_gap"
    SEASONAL_GAP = "seasonal_gap"
    TRENDING_GAP = "trending_gap"
    GEOGRAPHIC_GAP = "geographic_gap"
    DEMOGRAPHIC_GAP = "demographic_gap"


class OpportunityLevel(Enum):
    """Opportunity level classification"""
    CRITICAL = "critical"      # High traffic, low competition
    HIGH = "high"             # Good traffic, medium competition
    MEDIUM = "medium"         # Medium traffic, medium competition
    LOW = "low"              # Low traffic, high competition
    SATURATED = "saturated"   # High competition, limited opportunity


@dataclass
class MarketGap:
    """Represents a market gap opportunity"""
    gap_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    gap_type: MarketGapType = MarketGapType.KEYWORD_GAP
    opportunity_level: OpportunityLevel = OpportunityLevel.MEDIUM
    keywords: List[str] = field(default_factory=list)
    estimated_traffic: float = 0.0
    competition_score: float = 0.0
    difficulty_score: float = 0.0
    opportunity_score: float = 0.0
    target_audience: Dict[str, Any] = field(default_factory=dict)
    content_suggestions: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    trending_score: float = 0.0
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    competitors_missing: List[str] = field(default_factory=list)
    implementation_priority: int = 1
    roi_estimate: float = 0.0
    timeframe_estimate: str = "3-6 months"
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class CompetitorAnalysis:
    """Competitor analysis results"""
    competitor_name: str
    domain: str
    content_gaps: List[str] = field(default_factory=list)
    keyword_gaps: List[str] = field(default_factory=list)
    strength_areas: List[str] = field(default_factory=list)
    weakness_areas: List[str] = field(default_factory=list)
    content_volume: int = 0
    engagement_rate: float = 0.0
    authority_score: float = 0.0


class MarketGapAnalyzer:
    """Advanced market gap analysis with AI-powered opportunity detection"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Market Gap Analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.gaps_database: Dict[str, MarketGap] = {}
        self.competitor_data: Dict[str, CompetitorAnalysis] = {}
        self.keyword_clusters: Dict[str, List[str]] = {}
        self.market_trends: Dict[str, float] = {}
        
        # AI Models setup
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.clusterer = KMeans(n_clusters=20, random_state=42)
        
        # Configuration parameters
        self.min_opportunity_score = self.config.get('min_opportunity_score', 0.6)
        self.max_competition_score = self.config.get('max_competition_score', 0.7)
        self.trending_weight = self.config.get('trending_weight', 0.3)
        self.seasonal_weight = self.config.get('seasonal_weight', 0.2)
    
    async def analyze_market_gaps(
        self,
        keywords: List[str],
        competitors: List[str],
        target_audience: Optional[Dict[str, Any]] = None,
        platforms: Optional[List[str]] = None
    ) -> List[MarketGap]:
        """Comprehensive market gap analysis
        
        Args:
            keywords: Keywords to analyze
            competitors: Competitor domains/profiles
            target_audience: Target audience demographics
            platforms: Platforms to analyze
            
        Returns:
            List of identified market gaps
        """
        try:
            logger.info(f"Starting market gap analysis for {len(keywords)} keywords")
            
            # Analyze competitors
            competitor_analysis = await self._analyze_competitors(competitors)
            
            # Perform keyword gap analysis
            keyword_gaps = await self._identify_keyword_gaps(keywords, competitor_analysis)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(keywords, competitor_analysis)
            
            # Analyze platform gaps
            platform_gaps = await self._analyze_platform_gaps(platforms or [], competitor_analysis)
            
            # Detect trending opportunities
            trending_gaps = await self._detect_trending_gaps(keywords)
            
            # Analyze seasonal opportunities
            seasonal_gaps = await self._analyze_seasonal_gaps(keywords)
            
            # Combine all gaps
            all_gaps = keyword_gaps + content_gaps + platform_gaps + trending_gaps + seasonal_gaps
            
            # Score and prioritize gaps
            prioritized_gaps = await self._prioritize_gaps(all_gaps, target_audience)
            
            # Store results
            for gap in prioritized_gaps:
                self.gaps_database[gap.gap_id] = gap
            
            logger.info(f"Identified {len(prioritized_gaps)} market gaps")
            return prioritized_gaps
            
        except Exception as e:
            logger.error(f"Error in market gap analysis: {str(e)}")
            return []
    
    async def _analyze_competitors(self, competitors: List[str]) -> Dict[str, CompetitorAnalysis]:
        """Analyze competitor strengths and weaknesses"""
        try:
            competitor_analysis = {}
            
            for competitor in competitors:
                analysis = CompetitorAnalysis(
                    competitor_name=competitor,
                    domain=competitor
                )
                
                # Simulate competitor data analysis
                # In production, this would connect to real APIs
                analysis.content_volume = np.random.randint(100, 1000)
                analysis.engagement_rate = np.random.uniform(0.02, 0.15)
                analysis.authority_score = np.random.uniform(0.3, 0.9)
                
                # Identify strength and weakness areas
                analysis.strength_areas = await self._identify_competitor_strengths(competitor)
                analysis.weakness_areas = await self._identify_competitor_weaknesses(competitor)
                
                competitor_analysis[competitor] = analysis
                self.competitor_data[competitor] = analysis
            
            return competitor_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            return {}
    
    async def _identify_keyword_gaps(
        self,
        keywords: List[str],
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[MarketGap]:
        """Identify keyword opportunities not covered by competitors"""
        try:
            gaps = []
            
            # Cluster keywords for better analysis
            keyword_clusters = await self._cluster_keywords(keywords)
            
            for cluster_name, cluster_keywords in keyword_clusters.items():
                # Calculate competition for this cluster
                competition_score = await self._calculate_keyword_competition(cluster_keywords)
                
                # Estimate traffic potential
                traffic_estimate = await self._estimate_keyword_traffic(cluster_keywords)
                
                # Check if competitors are missing this cluster
                competitors_missing = await self._find_missing_competitors(
                    cluster_keywords, competitor_analysis
                )
                
                if len(competitors_missing) >= len(competitor_analysis) * 0.5:  # 50% of competitors missing
                    opportunity_score = await self._calculate_opportunity_score(
                        traffic_estimate, competition_score, len(competitors_missing)
                    )
                    
                    if opportunity_score >= self.min_opportunity_score:
                        gap = MarketGap(
                            gap_type=MarketGapType.KEYWORD_GAP,
                            keywords=cluster_keywords,
                            estimated_traffic=traffic_estimate,
                            competition_score=competition_score,
                            opportunity_score=opportunity_score,
                            competitors_missing=competitors_missing,
                            opportunity_level=await self._classify_opportunity_level(opportunity_score)
                        )
                        gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying keyword gaps: {str(e)}")
            return []
    
    async def _identify_content_gaps(
        self,
        keywords: List[str],
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[MarketGap]:
        """Identify content type gaps in the market"""
        try:
            gaps = []
            
            # Define content types to analyze
            content_types = [
                "tutorial", "review", "comparison", "guide", "tips",
                "news", "opinion", "case_study", "interview", "list"
            ]
            
            for content_type in content_types:
                # Check which competitors cover this content type
                competitors_covering = await self._find_competitors_with_content_type(
                    content_type, competitor_analysis
                )
                
                if len(competitors_covering) < len(competitor_analysis) * 0.3:  # Less than 30% coverage
                    # Generate content suggestions
                    content_suggestions = await self._generate_content_suggestions(
                        content_type, keywords
                    )
                    
                    # Estimate opportunity
                    traffic_estimate = await self._estimate_content_traffic(content_type, keywords)
                    competition_score = len(competitors_covering) / len(competitor_analysis)
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        traffic_estimate, competition_score, len(competitor_analysis) - len(competitors_covering)
                    )
                    
                    gap = MarketGap(
                        gap_type=MarketGapType.CONTENT_GAP,
                        keywords=[f"{content_type}_content"],
                        estimated_traffic=traffic_estimate,
                        competition_score=competition_score,
                        opportunity_score=opportunity_score,
                        content_suggestions=content_suggestions,
                        competitors_missing=[c for c in competitor_analysis.keys() if c not in competitors_covering],
                        opportunity_level=await self._classify_opportunity_level(opportunity_score)
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying content gaps: {str(e)}")
            return []
    
    async def _analyze_platform_gaps(
        self,
        platforms: List[str],
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[MarketGap]:
        """Analyze platform-specific opportunities"""
        try:
            gaps = []
            
            available_platforms = ["youtube", "instagram", "tiktok", "linkedin", "twitter", "spotify"]
            
            for platform in available_platforms:
                if platform not in platforms:
                    continue
                
                # Check competitor presence on platform
                competitors_on_platform = await self._check_competitor_platform_presence(
                    platform, competitor_analysis
                )
                
                if len(competitors_on_platform) < len(competitor_analysis) * 0.4:  # Less than 40% presence
                    # Estimate platform opportunity
                    traffic_estimate = await self._estimate_platform_traffic(platform)
                    competition_score = len(competitors_on_platform) / len(competitor_analysis)
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        traffic_estimate, competition_score, len(competitor_analysis) - len(competitors_on_platform)
                    )
                    
                    gap = MarketGap(
                        gap_type=MarketGapType.PLATFORM_GAP,
                        platforms=[platform],
                        estimated_traffic=traffic_estimate,
                        competition_score=competition_score,
                        opportunity_score=opportunity_score,
                        competitors_missing=[c for c in competitor_analysis.keys() if c not in competitors_on_platform],
                        opportunity_level=await self._classify_opportunity_level(opportunity_score)
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing platform gaps: {str(e)}")
            return []
    
    async def _detect_trending_gaps(self, keywords: List[str]) -> List[MarketGap]:
        """Detect trending opportunities not yet exploited"""
        try:
            gaps = []
            
            # Get trending keywords (simulated)
            trending_keywords = await self._get_trending_keywords()
            
            for trend_keyword in trending_keywords:
                if trend_keyword not in keywords:
                    continue
                
                # Calculate trending score
                trending_score = await self._calculate_trending_score(trend_keyword)
                
                if trending_score >= 0.7:  # High trending score
                    traffic_estimate = await self._estimate_trending_traffic(trend_keyword)
                    competition_score = 0.3  # Trending topics typically have lower competition initially
                    
                    opportunity_score = await self._calculate_opportunity_score(
                        traffic_estimate, competition_score, 5
                    )
                    
                    gap = MarketGap(
                        gap_type=MarketGapType.TRENDING_GAP,
                        keywords=[trend_keyword],
                        estimated_traffic=traffic_estimate,
                        competition_score=competition_score,
                        opportunity_score=opportunity_score,
                        trending_score=trending_score,
                        opportunity_level=await self._classify_opportunity_level(opportunity_score),
                        timeframe_estimate="1-3 months"  # Trending opportunities are time-sensitive
                    )
                    gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error detecting trending gaps: {str(e)}")
            return []
    
    async def _analyze_seasonal_gaps(self, keywords: List[str]) -> List[MarketGap]:
        """Analyze seasonal opportunities"""
        try:
            gaps = []
            
            # Define seasonal patterns
            seasonal_patterns = {
                "spring": ["fitness", "garden", "travel", "wedding"],
                "summer": ["vacation", "outdoor", "festival", "sports"],
                "fall": ["school", "fashion", "holiday_prep", "harvest"],
                "winter": ["holiday", "indoor", "gift", "winter_sports"]
            }
            
            current_month = datetime.now().month
            current_season = self._get_current_season(current_month)
            upcoming_season = self._get_upcoming_season(current_season)
            
            for season, seasonal_keywords in seasonal_patterns.items():
                if season == upcoming_season:
                    for seasonal_keyword in seasonal_keywords:
                        relevant_keywords = [k for k in keywords if seasonal_keyword in k.lower()]
                        
                        if relevant_keywords:
                            # Calculate seasonal opportunity
                            seasonal_factor = await self._calculate_seasonal_factor(seasonal_keyword, season)
                            traffic_estimate = await self._estimate_seasonal_traffic(relevant_keywords, seasonal_factor)
                            
                            gap = MarketGap(
                                gap_type=MarketGapType.SEASONAL_GAP,
                                keywords=relevant_keywords,
                                estimated_traffic=traffic_estimate,
                                competition_score=0.4,  # Seasonal content often has moderate competition
                                opportunity_score=seasonal_factor,
                                seasonal_factors={season: seasonal_factor},
                                opportunity_level=await self._classify_opportunity_level(seasonal_factor),
                                timeframe_estimate=f"Prepare for {season}"
                            )
                            gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal gaps: {str(e)}")
            return []
    
    async def _prioritize_gaps(
        self,
        gaps: List[MarketGap],
        target_audience: Optional[Dict[str, Any]] = None
    ) -> List[MarketGap]:
        """Prioritize gaps based on opportunity score and other factors"""
        try:
            # Calculate final scores with weights
            for gap in gaps:
                final_score = gap.opportunity_score
                
                # Apply trending weight
                if gap.trending_score > 0:
                    final_score += gap.trending_score * self.trending_weight
                
                # Apply seasonal weight
                if gap.seasonal_factors:
                    seasonal_boost = max(gap.seasonal_factors.values()) * self.seasonal_weight
                    final_score += seasonal_boost
                
                # Target audience alignment (if provided)
                if target_audience:
                    audience_alignment = await self._calculate_audience_alignment(gap, target_audience)
                    final_score *= audience_alignment
                
                gap.opportunity_score = min(final_score, 1.0)  # Cap at 1.0
                
                # Set implementation priority
                if gap.opportunity_score >= 0.8:
                    gap.implementation_priority = 1
                elif gap.opportunity_score >= 0.6:
                    gap.implementation_priority = 2
                else:
                    gap.implementation_priority = 3
                
                # Estimate ROI
                gap.roi_estimate = await self._estimate_roi(gap)
            
            # Sort by opportunity score and priority
            return sorted(gaps, key=lambda x: (x.implementation_priority, -x.opportunity_score))
            
        except Exception as e:
            logger.error(f"Error prioritizing gaps: {str(e)}")
            return gaps
    
    # Helper methods
    async def _cluster_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Cluster keywords using TF-IDF and K-means"""
        try:
            if len(keywords) < 10:
                return {"main_cluster": keywords}
            
            # Vectorize keywords
            tfidf_matrix = self.vectorizer.fit_transform(keywords)
            
            # Cluster
            n_clusters = min(10, len(keywords) // 3)
            clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = clusterer.fit_predict(tfidf_matrix)
            
            # Group keywords by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[f"cluster_{label}"].append(keywords[i])
            
            return dict(clusters)
            
        except Exception as e:
            logger.error(f"Error clustering keywords: {str(e)}")
            return {"main_cluster": keywords}
    
    async def _calculate_keyword_competition(self, keywords: List[str]) -> float:
        """Calculate competition score for keywords"""
        # Simulated competition calculation
        # In production, this would use real SEO tools APIs
        return np.random.uniform(0.2, 0.8)
    
    async def _estimate_keyword_traffic(self, keywords: List[str]) -> float:
        """Estimate traffic potential for keywords"""
        # Simulated traffic estimation
        base_traffic = len(keywords) * np.random.uniform(100, 1000)
        return base_traffic
    
    async def _calculate_opportunity_score(
        self,
        traffic: float,
        competition: float,
        missing_competitors: int
    ) -> float:
        """Calculate overall opportunity score"""
        # Normalize traffic (assuming max 10000)
        traffic_score = min(traffic / 10000, 1.0)
        
        # Competition score (lower is better)
        competition_score = 1.0 - competition
        
        # Missing competitors score
        competitor_gap_score = min(missing_competitors / 10, 1.0)
        
        # Weighted average
        opportunity_score = (
            traffic_score * 0.4 +
            competition_score * 0.4 +
            competitor_gap_score * 0.2
        )
        
        return min(opportunity_score, 1.0)
    
    async def _classify_opportunity_level(self, score: float) -> OpportunityLevel:
        """Classify opportunity level based on score"""
        if score >= 0.8:
            return OpportunityLevel.CRITICAL
        elif score >= 0.6:
            return OpportunityLevel.HIGH
        elif score >= 0.4:
            return OpportunityLevel.MEDIUM
        elif score >= 0.2:
            return OpportunityLevel.LOW
        else:
            return OpportunityLevel.SATURATED
    
    def _get_current_season(self, month: int) -> str:
        """Get current season based on month"""
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"
    
    def _get_upcoming_season(self, current_season: str) -> str:
        """Get upcoming season"""
        seasons = ["spring", "summer", "fall", "winter"]
        current_index = seasons.index(current_season)
        return seasons[(current_index + 1) % 4]
    
    async def _estimate_roi(self, gap: MarketGap) -> float:
        """Estimate ROI for implementing this opportunity"""
        # Simplified ROI calculation
        potential_revenue = gap.estimated_traffic * 0.02 * 50  # 2% conversion at $50 value
        implementation_cost = 5000  # Estimated implementation cost
        
        if implementation_cost > 0:
            return (potential_revenue - implementation_cost) / implementation_cost
        return 0.0
    
    # Placeholder methods for external integrations
    async def _identify_competitor_strengths(self, competitor: str) -> List[str]:
        """Identify competitor strengths"""
        return ["content_quality", "social_media_presence", "technical_seo"]
    
    async def _identify_competitor_weaknesses(self, competitor: str) -> List[str]:
        """Identify competitor weaknesses"""
        return ["mobile_optimization", "page_speed", "user_engagement"]
    
    async def _find_missing_competitors(
        self,
        keywords: List[str],
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[str]:
        """Find competitors missing from keyword cluster"""
        # Simulate missing competitors
        return list(competitor_analysis.keys())[:len(competitor_analysis) // 2]
    
    async def _find_competitors_with_content_type(
        self,
        content_type: str,
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[str]:
        """Find competitors with specific content type"""
        # Simulate content type coverage
        return list(competitor_analysis.keys())[:np.random.randint(0, len(competitor_analysis))]
    
    async def _generate_content_suggestions(self, content_type: str, keywords: List[str]) -> List[str]:
        """Generate content suggestions"""
        return [f"{content_type} about {keyword}" for keyword in keywords[:5]]
    
    async def _estimate_content_traffic(self, content_type: str, keywords: List[str]) -> float:
        """Estimate traffic for content type"""
        return len(keywords) * np.random.uniform(200, 800)
    
    async def _check_competitor_platform_presence(
        self,
        platform: str,
        competitor_analysis: Dict[str, CompetitorAnalysis]
    ) -> List[str]:
        """Check competitor presence on platform"""
        # Simulate platform presence
        return list(competitor_analysis.keys())[:np.random.randint(0, len(competitor_analysis))]
    
    async def _estimate_platform_traffic(self, platform: str) -> float:
        """Estimate platform traffic potential"""
        platform_multipliers = {
            "youtube": 1000,
            "instagram": 800,
            "tiktok": 1200,
            "linkedin": 400,
            "twitter": 600,
            "spotify": 300
        }
        return platform_multipliers.get(platform, 500)
    
    async def _get_trending_keywords(self) -> List[str]:
        """Get trending keywords"""
        # Simulate trending keywords
        return ["ai", "sustainability", "remote_work", "crypto", "wellness"]
    
    async def _calculate_trending_score(self, keyword: str) -> float:
        """Calculate trending score for keyword"""
        return np.random.uniform(0.5, 1.0)
    
    async def _estimate_trending_traffic(self, keyword: str) -> float:
        """Estimate traffic for trending keyword"""
        return np.random.uniform(1000, 5000)
    
    async def _calculate_seasonal_factor(self, keyword: str, season: str) -> float:
        """Calculate seasonal factor"""
        return np.random.uniform(0.6, 1.0)
    
    async def _estimate_seasonal_traffic(self, keywords: List[str], factor: float) -> float:
        """Estimate seasonal traffic"""
        base_traffic = len(keywords) * 500
        return base_traffic * factor
    
    async def _calculate_audience_alignment(
        self,
        gap: MarketGap,
        target_audience: Dict[str, Any]
    ) -> float:
        """Calculate audience alignment score"""
        # Simplified alignment calculation
        return np.random.uniform(0.7, 1.0)
    
    def get_gap_summary(self) -> Dict[str, Any]:
        """Get summary of all identified gaps"""
        try:
            total_gaps = len(self.gaps_database)
            critical_gaps = len([g for g in self.gaps_database.values() if g.opportunity_level == OpportunityLevel.CRITICAL])
            high_gaps = len([g for g in self.gaps_database.values() if g.opportunity_level == OpportunityLevel.HIGH])
            
            total_estimated_traffic = sum(g.estimated_traffic for g in self.gaps_database.values())
            average_opportunity_score = statistics.mean([g.opportunity_score for g in self.gaps_database.values()]) if total_gaps > 0 else 0
            
            return {
                "total_gaps": total_gaps,
                "critical_opportunities": critical_gaps,
                "high_opportunities": high_gaps,
                "total_estimated_traffic": total_estimated_traffic,
                "average_opportunity_score": average_opportunity_score,
                "gap_types": Counter([g.gap_type.value for g in self.gaps_database.values()]),
                "implementation_priorities": Counter([g.implementation_priority for g in self.gaps_database.values()])
            }
            
        except Exception as e:
            logger.error(f"Error generating gap summary: {str(e)}")
            return {}
    
    def export_gaps(self, format_type: str = "json") -> str:
        """Export gaps in specified format"""
        try:
            if format_type.lower() == "json":
                gaps_data = {}
                for gap_id, gap in self.gaps_database.items():
                    gap_dict = {
                        "gap_id": gap.gap_id,
                        "gap_type": gap.gap_type.value,
                        "opportunity_level": gap.opportunity_level.value,
                        "keywords": gap.keywords,
                        "estimated_traffic": gap.estimated_traffic,
                        "competition_score": gap.competition_score,
                        "opportunity_score": gap.opportunity_score,
                        "content_suggestions": gap.content_suggestions,
                        "platforms": gap.platforms,
                        "implementation_priority": gap.implementation_priority,
                        "roi_estimate": gap.roi_estimate,
                        "timeframe_estimate": gap.timeframe_estimate,
                        "discovered_at": gap.discovered_at.isoformat()
                    }
                    gaps_data[gap_id] = gap_dict
                
                return json.dumps(gaps_data, indent=2)
            
            else:
                return "Unsupported format. Use 'json'."
                
        except Exception as e:
            logger.error(f"Error exporting gaps: {str(e)}")
            return "{}"


# Example usage and testing
async def main() -> None:
    """Example usage of Market Gap Analyzer"""
    try:
        # Initialize analyzer
        config = {
            'min_opportunity_score': 0.5,
            'max_competition_score': 0.8,
            'trending_weight': 0.3,
            'seasonal_weight': 0.2
        }
        
        analyzer = MarketGapAnalyzer(config)
        
        # Example data
        keywords = [
            "ai content creation", "video editing tutorial", "social media strategy",
            "influencer marketing", "content monetization", "youtube optimization",
            "instagram growth", "tiktok viral content", "podcast marketing"
        ]
        
        competitors = [
            "competitor1.com", "competitor2.com", "competitor3.com"
        ]
        
        target_audience = {
            "age_range": "25-35",
            "interests": ["technology", "content creation", "marketing"],
            "platforms": ["youtube", "instagram", "tiktok"]
        }
        
        platforms = ["youtube", "instagram", "tiktok", "linkedin"]
        
        # Analyze market gaps
        print("🔍 Analyzing market gaps...")
        gaps = await analyzer.analyze_market_gaps(
            keywords=keywords,
            competitors=competitors,
            target_audience=target_audience,
            platforms=platforms
        )
        
        # Print results
        print(f"\n📊 Found {len(gaps)} market opportunities:")
        for i, gap in enumerate(gaps[:5]):  # Show top 5
            print(f"\n{i+1}. {gap.gap_type.value.upper()} - {gap.opportunity_level.value}")
            print(f"   Keywords: {', '.join(gap.keywords[:3])}")
            print(f"   Opportunity Score: {gap.opportunity_score:.2f}")
            print(f"   Estimated Traffic: {gap.estimated_traffic:.0f}")
            print(f"   Competition: {gap.competition_score:.2f}")
            print(f"   Priority: {gap.implementation_priority}")
            print(f"   ROI Estimate: {gap.roi_estimate:.1f}x")
            print(f"   Timeframe: {gap.timeframe_estimate}")
        
        # Get summary
        summary = analyzer.get_gap_summary()
        print(f"\n📈 Summary:")
        print(f"   Total Opportunities: {summary['total_gaps']}")
        print(f"   Critical: {summary['critical_opportunities']}")
        print(f"   High: {summary['high_opportunities']}")
        print(f"   Avg Score: {summary['average_opportunity_score']:.2f}")
        
        # Export results
        export_data = analyzer.export_gaps("json")
        print(f"\n💾 Export size: {len(export_data)} characters")
        
        print("\n✅ Market Gap Analysis completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())