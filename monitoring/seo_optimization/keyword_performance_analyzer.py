"""
Keyword Performance Analyzer - SEO Optimization Module
=====================================================

Advanced keyword performance analysis system for tracking and optimizing
keyword rankings, search volumes, and competitive positioning.

Features:
- Real-time keyword ranking tracking
- Search volume analysis and trends
- Competitor keyword analysis
- Long-tail keyword discovery
- Keyword difficulty assessment
- ROI analysis for keyword investments

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class KeywordStatus(Enum):
    """Keyword tracking status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DECLINED = "declined"
    IMPROVED = "improved"
    NEW = "new"
    LOST = "lost"

class SearchEngine(Enum):
    """Search engines for tracking"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    BING = "bing"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"     # 0-20
    EASY = "easy"               # 21-40
    MEDIUM = "medium"           # 41-60
    HARD = "hard"               # 61-80
    VERY_HARD = "very_hard"     # 81-100

@dataclass
class KeywordMetrics:
    """Comprehensive keyword metrics"""
    keyword: str = ""
    search_engine: SearchEngine = SearchEngine.GOOGLE
    
    # Ranking metrics
    current_ranking: int = 0
    previous_ranking: int = 0
    ranking_change: int = 0
    best_ranking: int = 0
    worst_ranking: int = 0
    
    # Search volume metrics
    monthly_search_volume: int = 0
    search_volume_trend: float = 0.0  # % change
    seasonal_factor: float = 1.0
    
    # Competition metrics
    keyword_difficulty: float = 0.0
    competition_level: str = "medium"
    top_competitor_count: int = 0
    
    # Performance metrics
    clicks: int = 0
    impressions: int = 0
    click_through_rate: float = 0.0
    average_position: float = 0.0
    
    # Business metrics
    conversion_rate: float = 0.0
    revenue_attribution: float = 0.0
    cost_per_click: float = 0.0
    roi: float = 0.0
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class KeywordOpportunity:
    """Keyword optimization opportunity"""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str = ""
    opportunity_type: str = ""  # "ranking_improvement", "new_keyword", "long_tail"
    
    # Opportunity details
    current_position: int = 0
    target_position: int = 0
    estimated_effort: str = "medium"  # low, medium, high
    estimated_timeframe: str = "3-6 months"
    
    # Potential impact
    estimated_traffic_increase: int = 0
    estimated_revenue_increase: float = 0.0
    confidence_score: float = 0.0
    
    # Action items
    recommended_actions: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=list)
    
    # Metadata
    identified_at: datetime = field(default_factory=datetime.now)
    priority_score: float = 0.0

@dataclass
class CompetitorKeywordAnalysis:
    """Competitor keyword analysis"""
    competitor_name: str = ""
    competitor_url: str = ""
    
    # Keyword overlap
    shared_keywords: List[str] = field(default_factory=list)
    competitor_only_keywords: List[str] = field(default_factory=list)
    our_only_keywords: List[str] = field(default_factory=list)
    
    # Performance comparison
    competitor_avg_ranking: float = 0.0
    our_avg_ranking: float = 0.0
    ranking_advantage: float = 0.0
    
    # Gap analysis
    keyword_gaps: List[str] = field(default_factory=list)
    opportunity_keywords: List[str] = field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)

@dataclass
class KeywordTrendAnalysis:
    """Keyword trend analysis and forecasting"""
    keyword: str = ""
    analysis_period_days: int = 30
    
    # Trend metrics
    trend_direction: str = "stable"  # rising, falling, stable, volatile
    growth_rate: float = 0.0  # % change over period
    volatility_score: float = 0.0
    
    # Seasonal patterns
    seasonal_peaks: List[str] = field(default_factory=list)  # months
    seasonal_lows: List[str] = field(default_factory=list)
    
    # Forecasting
    predicted_volume_next_month: int = 0
    predicted_ranking_change: int = 0
    forecast_confidence: float = 0.0
    
    # Events correlation
    correlated_events: List[str] = field(default_factory=list)
    external_factors: List[str] = field(default_factory=list)

class KeywordPerformanceAnalyzer:
    """Main keyword performance analysis system"""
    
    def __init__(self):
        self.keyword_metrics: Dict[str, List[KeywordMetrics]] = defaultdict(list)
        self.opportunities: List[KeywordOpportunity] = []
        self.competitor_analyses: List[CompetitorKeywordAnalysis] = []
        self.trend_analyses: List[KeywordTrendAnalysis] = []
        
        # Configuration
        self.tracking_frequency_minutes = 60
        self.analysis_enabled = True
        self.auto_discovery_enabled = True
        
        # Initialize keyword database
        self.keyword_database = self._initialize_keyword_database()
        self.competitor_list = self._initialize_competitors()
        
    def _initialize_keyword_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize keyword database with target keywords"""
        return {
            # Music keywords
            "music production": {
                "category": "music",
                "primary": True,
                "target_ranking": 10,
                "search_engines": [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
                "difficulty": 65,
                "monthly_volume": 45000
            },
            "beat making": {
                "category": "music",
                "primary": True,
                "target_ranking": 15,
                "search_engines": [SearchEngine.YOUTUBE, SearchEngine.GOOGLE],
                "difficulty": 55,
                "monthly_volume": 32000
            },
            "how to make music": {
                "category": "music",
                "primary": False,
                "target_ranking": 20,
                "search_engines": [SearchEngine.YOUTUBE],
                "difficulty": 70,
                "monthly_volume": 28000
            },
            
            # Content creation keywords
            "content creator": {
                "category": "content",
                "primary": True,
                "target_ranking": 25,
                "search_engines": [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
                "difficulty": 75,
                "monthly_volume": 125000
            },
            "viral content": {
                "category": "content",
                "primary": False,
                "target_ranking": 30,
                "search_engines": [SearchEngine.GOOGLE, SearchEngine.TIKTOK],
                "difficulty": 60,
                "monthly_volume": 18000
            },
            
            # Platform-specific keywords
            "youtube optimization": {
                "category": "platform",
                "primary": True,
                "target_ranking": 15,
                "search_engines": [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
                "difficulty": 68,
                "monthly_volume": 22000
            },
            "tiktok growth": {
                "category": "platform",
                "primary": False,
                "target_ranking": 20,
                "search_engines": [SearchEngine.GOOGLE, SearchEngine.TIKTOK],
                "difficulty": 58,
                "monthly_volume": 15000
            }
        }
        
    def _initialize_competitors(self) -> List[Dict[str, Any]]:
        """Initialize competitor list for analysis"""
        return [
            {
                "name": "TubeGuru",
                "url": "tubeguru.com",
                "category": "youtube_optimization",
                "authority_score": 75
            },
            {
                "name": "CreatorHub",
                "url": "creatorhub.io", 
                "category": "content_creation",
                "authority_score": 68
            },
            {
                "name": "ViralBoost",
                "url": "viralboost.co",
                "category": "social_media_growth",
                "authority_score": 62
            },
            {
                "name": "BeatMakers",
                "url": "beatmakers.com",
                "category": "music_production",
                "authority_score": 70
            }
        ]
        
    async def track_keyword_performance(self, 
                                      keyword: str,
                                      search_engine: SearchEngine = SearchEngine.GOOGLE) -> KeywordMetrics:
        """Track performance for a specific keyword"""
        
        # Get current metrics (simulated data for demonstration)
        current_metrics = await self._fetch_keyword_metrics(keyword, search_engine)
        
        # Get historical data for comparison
        historical_metrics = self.keyword_metrics.get(f"{keyword}_{search_engine.value}", [])
        
        # Calculate changes
        if historical_metrics:
            previous_metrics = historical_metrics[-1]
            current_metrics.previous_ranking = previous_metrics.current_ranking
            current_metrics.ranking_change = previous_metrics.current_ranking - current_metrics.current_ranking
            
            # Calculate search volume trend
            if previous_metrics.monthly_search_volume > 0:
                volume_change = (current_metrics.monthly_search_volume - previous_metrics.monthly_search_volume)
                current_metrics.search_volume_trend = (volume_change / previous_metrics.monthly_search_volume) * 100
                
        # Store metrics
        self.keyword_metrics[f"{keyword}_{search_engine.value}"].append(current_metrics)
        
        # Keep only last 100 entries per keyword
        if len(self.keyword_metrics[f"{keyword}_{search_engine.value}"]) > 100:
            self.keyword_metrics[f"{keyword}_{search_engine.value}"].pop(0)
            
        logger.info(f"Tracked keyword performance: {keyword} - Ranking: {current_metrics.current_ranking}")
        
        return current_metrics
        
    async def _fetch_keyword_metrics(self, keyword: str, search_engine: SearchEngine) -> KeywordMetrics:
        """Fetch current keyword metrics (simulated implementation)"""
        import random
        
        # Get baseline data from database
        keyword_data = self.keyword_database.get(keyword, {})
        base_difficulty = keyword_data.get("difficulty", 50)
        base_volume = keyword_data.get("monthly_volume", 10000)
        
        # Simulate realistic ranking data
        if keyword in self.keyword_database:
            # Tracked keywords have better rankings
            current_ranking = random.randint(1, 50)
        else:
            # Untracked keywords have worse rankings
            current_ranking = random.randint(20, 100)
            
        # Simulate other metrics
        search_volume = int(base_volume * random.uniform(0.8, 1.2))
        clicks = max(0, int((100 - current_ranking) * random.uniform(0.5, 2.0)))
        impressions = clicks * random.randint(10, 50)
        ctr = clicks / impressions if impressions > 0 else 0
        
        # Calculate business metrics
        conversion_rate = random.uniform(0.01, 0.05)
        revenue_per_conversion = random.uniform(10, 100)
        revenue_attribution = clicks * conversion_rate * revenue_per_conversion
        
        return KeywordMetrics(
            keyword=keyword,
            search_engine=search_engine,
            current_ranking=current_ranking,
            monthly_search_volume=search_volume,
            keyword_difficulty=base_difficulty + random.uniform(-10, 10),
            competition_level=self._calculate_competition_level(base_difficulty),
            clicks=clicks,
            impressions=impressions,
            click_through_rate=ctr,
            average_position=current_ranking + random.uniform(-2, 2),
            conversion_rate=conversion_rate,
            revenue_attribution=revenue_attribution,
            cost_per_click=random.uniform(0.5, 5.0),
            roi=revenue_attribution / max(1, clicks * 0.5)  # Simplified ROI
        )
        
    def _calculate_competition_level(self, difficulty: float) -> str:
        """Calculate competition level from difficulty score"""
        if difficulty < 20:
            return "very_low"
        elif difficulty < 40:
            return "low"
        elif difficulty < 60:
            return "medium"
        elif difficulty < 80:
            return "high"
        else:
            return "very_high"
            
    async def analyze_keyword_opportunities(self) -> List[KeywordOpportunity]:
        """Analyze and identify keyword optimization opportunities"""
        opportunities = []
        
        # Analyze existing tracked keywords
        for keyword_key, metrics_list in self.keyword_metrics.items():
            if not metrics_list:
                continue
                
            keyword = keyword_key.split("_")[0]  # Extract keyword from key
            latest_metrics = metrics_list[-1]
            
            # Opportunity 1: Ranking improvement for existing keywords
            if 11 <= latest_metrics.current_ranking <= 50:
                opportunity = await self._create_ranking_improvement_opportunity(keyword, latest_metrics)
                if opportunity:
                    opportunities.append(opportunity)
                    
            # Opportunity 2: High-volume, low-competition keywords
            if (latest_metrics.monthly_search_volume > 5000 and 
                latest_metrics.keyword_difficulty < 60 and 
                latest_metrics.current_ranking > 20):
                opportunity = await self._create_high_value_opportunity(keyword, latest_metrics)
                if opportunity:
                    opportunities.append(opportunity)
                    
        # Opportunity 3: Long-tail keyword discovery
        long_tail_opportunities = await self._discover_long_tail_opportunities()
        opportunities.extend(long_tail_opportunities)
        
        # Opportunity 4: Competitor keyword gaps
        competitor_opportunities = await self._analyze_competitor_gaps()
        opportunities.extend(competitor_opportunities)
        
        # Sort by priority score
        opportunities.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Store top opportunities
        self.opportunities.extend(opportunities[:20])  # Keep top 20
        
        logger.info(f"Identified {len(opportunities)} keyword opportunities")
        return opportunities
        
    async def _create_ranking_improvement_opportunity(self, 
                                                   keyword: str, 
                                                   metrics: KeywordMetrics) -> Optional[KeywordOpportunity]:
        """Create ranking improvement opportunity"""
        
        current_pos = metrics.current_ranking
        target_pos = min(10, current_pos - 5)  # Aim for top 10 or 5 positions better
        
        # Calculate potential impact
        ctr_improvement = self._estimate_ctr_improvement(current_pos, target_pos)
        traffic_increase = int(metrics.impressions * ctr_improvement)
        revenue_increase = traffic_increase * metrics.conversion_rate * 50  # Avg revenue per conversion
        
        # Determine effort level
        ranking_improvement_needed = current_pos - target_pos
        if ranking_improvement_needed <= 5:
            effort = "low"
            timeframe = "1-3 months"
        elif ranking_improvement_needed <= 15:
            effort = "medium"
            timeframe = "3-6 months"
        else:
            effort = "high"
            timeframe = "6-12 months"
            
        # Generate recommendations
        recommendations = []
        if metrics.click_through_rate < 0.05:
            recommendations.append("Optimize title and meta description for higher CTR")
        if metrics.keyword_difficulty > 70:
            recommendations.append("Build high-quality backlinks to improve authority")
        recommendations.append(f"Create comprehensive content targeting '{keyword}'")
        recommendations.append("Optimize on-page SEO elements")
        
        # Calculate priority score
        priority_score = (
            (traffic_increase / 1000) * 0.3 +
            (revenue_increase / 100) * 0.4 +
            (1 / metrics.keyword_difficulty) * 0.2 +
            (metrics.monthly_search_volume / 10000) * 0.1
        )
        
        return KeywordOpportunity(
            keyword=keyword,
            opportunity_type="ranking_improvement",
            current_position=current_pos,
            target_position=target_pos,
            estimated_effort=effort,
            estimated_timeframe=timeframe,
            estimated_traffic_increase=traffic_increase,
            estimated_revenue_increase=revenue_increase,
            confidence_score=0.8,
            recommended_actions=recommendations,
            required_resources=["Content creation", "SEO optimization", "Link building"],
            priority_score=priority_score
        )
        
    def _estimate_ctr_improvement(self, current_pos: int, target_pos: int) -> float:
        """Estimate CTR improvement from ranking change"""
        # Simplified CTR model based on position
        ctr_by_position = {
            1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.07,
            6: 0.05, 7: 0.04, 8: 0.03, 9: 0.03, 10: 0.025
        }
        
        current_ctr = ctr_by_position.get(current_pos, 0.01)
        target_ctr = ctr_by_position.get(target_pos, current_ctr * 1.5)
        
        return target_ctr - current_ctr
        
    async def _create_high_value_opportunity(self, 
                                           keyword: str, 
                                           metrics: KeywordMetrics) -> Optional[KeywordOpportunity]:
        """Create high-value keyword opportunity"""
        
        # Calculate opportunity score
        volume_score = min(1.0, metrics.monthly_search_volume / 50000)
        difficulty_score = 1.0 - (metrics.keyword_difficulty / 100)
        opportunity_score = (volume_score + difficulty_score) / 2
        
        if opportunity_score < 0.6:
            return None
            
        target_position = 15  # Aim for first page
        traffic_increase = int(metrics.monthly_search_volume * 0.1)  # 10% of search volume
        revenue_increase = traffic_increase * 0.03 * 40  # 3% conversion, $40 per conversion
        
        return KeywordOpportunity(
            keyword=keyword,
            opportunity_type="high_value_keyword",
            current_position=metrics.current_ranking,
            target_position=target_position,
            estimated_effort="medium",
            estimated_timeframe="3-6 months",
            estimated_traffic_increase=traffic_increase,
            estimated_revenue_increase=revenue_increase,
            confidence_score=0.7,
            recommended_actions=[
                "Create in-depth content targeting this keyword",
                "Optimize for related long-tail variations",
                "Build topical authority in this area"
            ],
            required_resources=["Content strategy", "SEO optimization"],
            priority_score=opportunity_score * 10
        )
        
    async def _discover_long_tail_opportunities(self) -> List[KeywordOpportunity]:
        """Discover long-tail keyword opportunities"""
        opportunities = []
        
        # Generate long-tail variations of main keywords
        main_keywords = list(self.keyword_database.keys())
        long_tail_modifiers = [
            "how to", "best", "tutorial", "guide", "tips", "for beginners",
            "step by step", "free", "online", "2025", "easy", "quick"
        ]
        
        for main_keyword in main_keywords[:5]:  # Limit to top 5 keywords
            for modifier in long_tail_modifiers[:3]:  # Top 3 modifiers
                long_tail = f"{modifier} {main_keyword}"
                
                # Simulate metrics for long-tail keyword
                estimated_volume = self.keyword_database[main_keyword]["monthly_volume"] // 10
                estimated_difficulty = max(20, self.keyword_database[main_keyword]["difficulty"] - 20)
                
                if estimated_volume > 500:  # Only consider if decent volume
                    opportunity = KeywordOpportunity(
                        keyword=long_tail,
                        opportunity_type="long_tail_keyword",
                        current_position=0,  # Not currently ranking
                        target_position=25,
                        estimated_effort="low",
                        estimated_timeframe="1-3 months",
                        estimated_traffic_increase=int(estimated_volume * 0.15),
                        estimated_revenue_increase=estimated_volume * 0.15 * 0.02 * 25,
                        confidence_score=0.6,
                        recommended_actions=[
                            f"Create specific content for '{long_tail}'",
                            "Target in blog posts or video descriptions",
                            "Use in FAQ sections"
                        ],
                        required_resources=["Content creation"],
                        priority_score=estimated_volume / 1000
                    )
                    opportunities.append(opportunity)
                    
        return opportunities[:10]  # Return top 10
        
    async def _analyze_competitor_gaps(self) -> List[KeywordOpportunity]:
        """Analyze competitor keyword gaps"""
        opportunities = []
        
        # Simulate competitor keyword analysis
        competitor_keywords = [
            "music marketing", "creator economy", "youtube analytics",
            "content monetization", "influencer tips", "social media strategy"
        ]
        
        for keyword in competitor_keywords:
            # Simulate that competitors rank well for these but we don't
            opportunity = KeywordOpportunity(
                keyword=keyword,
                opportunity_type="competitor_gap",
                current_position=0,  # We're not ranking
                target_position=20,
                estimated_effort="medium",
                estimated_timeframe="3-6 months",
                estimated_traffic_increase=2000,
                estimated_revenue_increase=2000 * 0.025 * 30,
                confidence_score=0.5,
                recommended_actions=[
                    f"Research competitor content for '{keyword}'",
                    "Create better, more comprehensive content",
                    "Target related long-tail variations"
                ],
                required_resources=["Competitive research", "Content creation"],
                priority_score=3.0
            )
            opportunities.append(opportunity)
            
        return opportunities[:5]  # Return top 5
        
    async def analyze_competitor_keywords(self, competitor_url: str) -> CompetitorKeywordAnalysis:
        """Analyze competitor keyword performance"""
        
        competitor = next((c for c in self.competitor_list if c["url"] == competitor_url), None)
        if not competitor:
            raise ValueError(f"Competitor {competitor_url} not found")
            
        # Simulate competitor keyword analysis
        our_keywords = set(self.keyword_database.keys())
        competitor_keywords = set([
            "video optimization", "content strategy", "creator tools",
            "audience growth", "monetization tips", "viral marketing"
        ])
        
        # Calculate overlaps and gaps
        shared_keywords = list(our_keywords.intersection(competitor_keywords))
        competitor_only = list(competitor_keywords - our_keywords)
        our_only = list(our_keywords - competitor_keywords)
        
        # Simulate ranking comparison
        competitor_avg_ranking = 15.5
        our_avg_ranking = 25.2
        ranking_advantage = our_avg_ranking - competitor_avg_ranking
        
        # Identify opportunities
        opportunity_keywords = [kw for kw in competitor_only if "marketing" in kw or "growth" in kw]
        
        analysis = CompetitorKeywordAnalysis(
            competitor_name=competitor["name"],
            competitor_url=competitor_url,
            shared_keywords=shared_keywords,
            competitor_only_keywords=competitor_only,
            our_only_keywords=our_only,
            competitor_avg_ranking=competitor_avg_ranking,
            our_avg_ranking=our_avg_ranking,
            ranking_advantage=ranking_advantage,
            keyword_gaps=competitor_only,
            opportunity_keywords=opportunity_keywords
        )
        
        self.competitor_analyses.append(analysis)
        logger.info(f"Analyzed competitor keywords for {competitor['name']}")
        
        return analysis
        
    async def analyze_keyword_trends(self, keyword: str, days_back: int = 90) -> KeywordTrendAnalysis:
        """Analyze keyword trends and patterns"""
        
        # Get historical data
        keyword_history = []
        for key, metrics_list in self.keyword_metrics.items():
            if keyword in key:
                keyword_history.extend(metrics_list)
                
        if not keyword_history:
            # Create simulated trend analysis
            return await self._create_simulated_trend_analysis(keyword, days_back)
            
        # Sort by date
        keyword_history.sort(key=lambda x: x.last_updated)
        
        # Calculate trend metrics
        search_volumes = [m.monthly_search_volume for m in keyword_history]
        rankings = [m.current_ranking for m in keyword_history]
        
        # Trend direction
        if len(search_volumes) >= 2:
            volume_change = search_volumes[-1] - search_volumes[0]
            growth_rate = (volume_change / search_volumes[0]) * 100 if search_volumes[0] > 0 else 0
            
            if growth_rate > 10:
                trend_direction = "rising"
            elif growth_rate < -10:
                trend_direction = "falling"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
            growth_rate = 0.0
            
        # Volatility calculation
        if len(search_volumes) > 1:
            volatility = statistics.stdev(search_volumes) / statistics.mean(search_volumes)
        else:
            volatility = 0.0
            
        # Seasonal patterns (simplified)
        current_month = datetime.now().month
        seasonal_peaks = ["December", "January"] if "music" in keyword else ["June", "July"]
        seasonal_lows = ["February", "March"] if "music" in keyword else ["November", "December"]
        
        # Forecasting
        if search_volumes:
            predicted_volume = int(search_volumes[-1] * (1 + growth_rate / 100))
        else:
            predicted_volume = 10000
            
        predicted_ranking_change = 0
        if rankings and len(rankings) >= 2:
            ranking_trend = rankings[-1] - rankings[0]
            predicted_ranking_change = int(ranking_trend * 0.5)  # Conservative prediction
            
        analysis = KeywordTrendAnalysis(
            keyword=keyword,
            analysis_period_days=days_back,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            volatility_score=volatility,
            seasonal_peaks=seasonal_peaks,
            seasonal_lows=seasonal_lows,
            predicted_volume_next_month=predicted_volume,
            predicted_ranking_change=predicted_ranking_change,
            forecast_confidence=0.7,
            correlated_events=["Holiday seasons", "Industry events"],
            external_factors=["Algorithm updates", "Market trends"]
        )
        
        self.trend_analyses.append(analysis)
        return analysis
        
    async def _create_simulated_trend_analysis(self, keyword: str, days_back: int) -> KeywordTrendAnalysis:
        """Create simulated trend analysis for new keywords"""
        import random
        
        # Simulate trend based on keyword characteristics
        if "tutorial" in keyword or "how to" in keyword:
            trend_direction = "rising"
            growth_rate = random.uniform(5, 20)
        elif "2024" in keyword:
            trend_direction = "falling"
            growth_rate = random.uniform(-15, -5)
        else:
            trend_direction = "stable"
            growth_rate = random.uniform(-5, 5)
            
        return KeywordTrendAnalysis(
            keyword=keyword,
            analysis_period_days=days_back,
            trend_direction=trend_direction,
            growth_rate=growth_rate,
            volatility_score=random.uniform(0.1, 0.4),
            seasonal_peaks=["December", "January"],
            seasonal_lows=["February", "March"],
            predicted_volume_next_month=random.randint(5000, 50000),
            predicted_ranking_change=random.randint(-5, 5),
            forecast_confidence=0.6,
            correlated_events=["Holiday seasons"],
            external_factors=["Market trends"]
        )
        
    async def generate_keyword_report(self, keyword: str = None) -> Dict[str, Any]:
        """Generate comprehensive keyword performance report"""
        
        if keyword:
            # Single keyword report
            return await self._generate_single_keyword_report(keyword)
        else:
            # Overall keyword portfolio report
            return await self._generate_portfolio_report()
            
    async def _generate_single_keyword_report(self, keyword: str) -> Dict[str, Any]:
        """Generate report for single keyword"""
        
        # Get keyword metrics
        keyword_metrics = []
        for key, metrics_list in self.keyword_metrics.items():
            if keyword in key:
                keyword_metrics.extend(metrics_list)
                
        if not keyword_metrics:
            return {"error": f"No data available for keyword: {keyword}"}
            
        latest_metrics = keyword_metrics[-1]
        
        # Calculate performance over time
        if len(keyword_metrics) > 1:
            ranking_improvement = keyword_metrics[0].current_ranking - latest_metrics.current_ranking
            traffic_change = latest_metrics.clicks - keyword_metrics[0].clicks
        else:
            ranking_improvement = 0
            traffic_change = 0
            
        # Get opportunities for this keyword
        keyword_opportunities = [
            opp for opp in self.opportunities 
            if opp.keyword == keyword
        ]
        
        return {
            "keyword": keyword,
            "current_performance": {
                "ranking": latest_metrics.current_ranking,
                "search_volume": latest_metrics.monthly_search_volume,
                "clicks": latest_metrics.clicks,
                "impressions": latest_metrics.impressions,
                "ctr": latest_metrics.click_through_rate,
                "revenue": latest_metrics.revenue_attribution
            },
            "performance_changes": {
                "ranking_improvement": ranking_improvement,
                "traffic_change": traffic_change,
                "ranking_trend": "improving" if ranking_improvement > 0 else "declining" if ranking_improvement < 0 else "stable"
            },
            "keyword_metrics": {
                "difficulty": latest_metrics.keyword_difficulty,
                "competition": latest_metrics.competition_level,
                "roi": latest_metrics.roi
            },
            "opportunities": [
                {
                    "type": opp.opportunity_type,
                    "potential_traffic": opp.estimated_traffic_increase,
                    "potential_revenue": opp.estimated_revenue_increase,
                    "effort_required": opp.estimated_effort
                }
                for opp in keyword_opportunities
            ],
            "recommendations": await self._generate_keyword_recommendations(keyword, latest_metrics)
        }
        
    async def _generate_portfolio_report(self) -> Dict[str, Any]:
        """Generate overall keyword portfolio report"""
        
        # Aggregate metrics across all keywords
        all_metrics = []
        for metrics_list in self.keyword_metrics.values():
            if metrics_list:
                all_metrics.append(metrics_list[-1])  # Latest metrics for each keyword
                
        if not all_metrics:
            return {"error": "No keyword data available"}
            
        # Calculate portfolio statistics
        total_keywords = len(all_metrics)
        avg_ranking = statistics.mean([m.current_ranking for m in all_metrics])
        total_traffic = sum([m.clicks for m in all_metrics])
        total_revenue = sum([m.revenue_attribution for m in all_metrics])
        
        # Ranking distribution
        ranking_distribution = {
            "top_10": len([m for m in all_metrics if m.current_ranking <= 10]),
            "top_20": len([m for m in all_metrics if 11 <= m.current_ranking <= 20]),
            "top_50": len([m for m in all_metrics if 21 <= m.current_ranking <= 50]),
            "beyond_50": len([m for m in all_metrics if m.current_ranking > 50])
        }
        
        # Performance by category
        category_performance = defaultdict(list)
        for keyword, data in self.keyword_database.items():
            category = data.get("category", "other")
            keyword_metric = next((m for m in all_metrics if m.keyword == keyword), None)
            if keyword_metric:
                category_performance[category].append(keyword_metric)
                
        category_stats = {}
        for category, metrics in category_performance.items():
            category_stats[category] = {
                "keyword_count": len(metrics),
                "avg_ranking": statistics.mean([m.current_ranking for m in metrics]),
                "total_traffic": sum([m.clicks for m in metrics]),
                "total_revenue": sum([m.revenue_attribution for m in metrics])
            }
            
        # Top opportunities
        top_opportunities = sorted(self.opportunities, key=lambda x: x.priority_score, reverse=True)[:10]
        
        return {
            "portfolio_overview": {
                "total_keywords": total_keywords,
                "average_ranking": avg_ranking,
                "total_monthly_traffic": total_traffic,
                "total_monthly_revenue": total_revenue,
                "average_roi": statistics.mean([m.roi for m in all_metrics if m.roi > 0])
            },
            "ranking_distribution": ranking_distribution,
            "category_performance": category_stats,
            "top_performing_keywords": [
                {
                    "keyword": m.keyword,
                    "ranking": m.current_ranking,
                    "traffic": m.clicks,
                    "revenue": m.revenue_attribution
                }
                for m in sorted(all_metrics, key=lambda x: x.clicks, reverse=True)[:10]
            ],
            "top_opportunities": [
                {
                    "keyword": opp.keyword,
                    "type": opp.opportunity_type,
                    "potential_traffic": opp.estimated_traffic_increase,
                    "potential_revenue": opp.estimated_revenue_increase,
                    "priority_score": opp.priority_score
                }
                for opp in top_opportunities
            ],
            "insights": await self._generate_portfolio_insights(all_metrics)
        }
        
    async def _generate_keyword_recommendations(self, keyword: str, metrics: KeywordMetrics) -> List[str]:
        """Generate specific recommendations for a keyword"""
        recommendations = []
        
        if metrics.current_ranking > 20:
            recommendations.append("Focus on improving overall content quality and relevance")
            recommendations.append("Build high-quality backlinks to increase domain authority")
            
        if metrics.click_through_rate < 0.03:
            recommendations.append("Optimize title and meta description to improve CTR")
            recommendations.append("Add compelling call-to-action elements")
            
        if metrics.conversion_rate < 0.02:
            recommendations.append("Improve landing page experience and relevance")
            recommendations.append("Add clear value propositions and trust signals")
            
        if metrics.keyword_difficulty > 70:
            recommendations.append("Consider targeting long-tail variations of this keyword")
            recommendations.append("Build topical authority through comprehensive content")
            
        return recommendations
        
    async def _generate_portfolio_insights(self, all_metrics: List[KeywordMetrics]) -> List[str]:
        """Generate insights for the entire keyword portfolio"""
        insights = []
        
        # Ranking insights
        top_10_count = len([m for m in all_metrics if m.current_ranking <= 10])
        top_10_percentage = (top_10_count / len(all_metrics)) * 100
        
        if top_10_percentage < 20:
            insights.append("Focus on improving rankings for high-potential keywords to increase top 10 presence")
        elif top_10_percentage > 50:
            insights.append("Strong keyword portfolio with good top 10 representation")
            
        # Traffic insights
        total_traffic = sum([m.clicks for m in all_metrics])
        if total_traffic < 1000:
            insights.append("Low overall traffic - consider expanding keyword portfolio or improving rankings")
        elif total_traffic > 10000:
            insights.append("Strong traffic performance across keyword portfolio")
            
        # Revenue insights
        total_revenue = sum([m.revenue_attribution for m in all_metrics])
        avg_revenue_per_keyword = total_revenue / len(all_metrics)
        
        if avg_revenue_per_keyword < 10:
            insights.append("Focus on improving conversion rates and revenue attribution")
        elif avg_revenue_per_keyword > 100:
            insights.append("Excellent revenue performance - consider scaling successful strategies")
            
        # Opportunity insights
        if len(self.opportunities) > 10:
            insights.append("Multiple keyword opportunities identified - prioritize by ROI potential")
            
        return insights

# Export main classes
__all__ = [
    'KeywordPerformanceAnalyzer',
    'KeywordMetrics',
    'KeywordOpportunity',
    'CompetitorKeywordAnalysis',
    'KeywordTrendAnalysis',
    'KeywordStatus',
    'SearchEngine',
    'KeywordDifficulty'
]