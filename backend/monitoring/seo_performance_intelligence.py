"""🔍 SEO Performance Intelligence - IA Influencer Agent Platform
=================================================================

Advanced SEO performance monitoring, search ranking analytics, and content
discoverability intelligence for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Content Creation → SEO Optimization → Search Indexing → Ranking Tracking → Performance Analytics
"""

import asyncio
import logging as std_logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics
import re

logger = std_logging.getLogger(__name__)


class SEOOptimizationType(Enum):
    """Types of SEO optimization"""
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    MOBILE_SEO = "mobile_seo"
    PAGE_SPEED = "page_speed"
    SCHEMA_MARKUP = "schema_markup"
    LINK_BUILDING = "link_building"
    IMAGE_SEO = "image_seo"
    VIDEO_SEO = "video_seo"


class SearchEngine(Enum):
    """Search engines for tracking"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"


class ContentType(Enum):
    """Content types for SEO tracking"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    PODCAST = "podcast"
    SOCIAL_POST = "social_post"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"


@dataclass
class SEOPerformanceMetrics:
    """Comprehensive SEO performance metrics"""
    content_id: str
    content_type: ContentType
    optimization_type: SEOOptimizationType
    
    # Search ranking metrics
    average_position: float = 0.0
    best_position: int = 100
    worst_position: int = 100
    position_change: int = 0
    
    # Traffic metrics
    organic_traffic: int = 0
    organic_sessions: int = 0
    organic_users: int = 0
    click_through_rate: float = 0.0
    
    # Keyword performance
    target_keywords: List[str] = field(default_factory=list)
    ranking_keywords: int = 0
    top_10_keywords: int = 0
    top_3_keywords: int = 0
    keyword_difficulty_score: float = 0.0
    
    # Content quality metrics
    content_score: float = 0.0
    readability_score: float = 0.0
    uniqueness_score: float = 0.0
    relevance_score: float = 0.0
    
    # Technical SEO metrics
    page_speed_score: float = 0.0
    mobile_friendliness: float = 0.0
    core_web_vitals_score: float = 0.0
    accessibility_score: float = 0.0
    
    # Engagement metrics
    bounce_rate: float = 0.0
    time_on_page: float = 0.0
    pages_per_session: float = 0.0
    conversion_rate: float = 0.0
    
    # Backlink metrics
    total_backlinks: int = 0
    referring_domains: int = 0
    domain_authority: float = 0.0
    link_quality_score: float = 0.0
    
    # SERP features
    featured_snippets: int = 0
    image_pack_appearances: int = 0
    video_pack_appearances: int = 0
    local_pack_appearances: int = 0
    
    # Revenue attribution
    seo_attributed_revenue: Decimal = Decimal('0')
    cost_per_acquisition: Decimal = Decimal('0')
    return_on_ad_spend: float = 0.0
    
    # Performance by search engine
    performance_by_engine: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Geographic performance
    performance_by_region: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Creator and platform info
    creator_id: Optional[str] = None
    platform: str = "web"
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    tracking_period: str = "weekly"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class KeywordPerformanceAnalytics:
    """Keyword-specific performance analytics"""
    keyword: str
    content_id: str
    
    # Ranking metrics
    current_position: int = 100
    previous_position: int = 100
    position_change: int = 0
    best_position_ever: int = 100
    
    # Search volume and competition
    search_volume: int = 0
    competition_score: float = 0.0
    keyword_difficulty: float = 0.0
    cost_per_click: Decimal = Decimal('0')
    
    # Performance metrics
    impressions: int = 0
    clicks: int = 0
    click_through_rate: float = 0.0
    
    # Intent and relevance
    search_intent: str = "informational"  # informational, commercial, transactional, navigational
    relevance_score: float = 0.0
    content_match_score: float = 0.0
    
    # Geographic and device performance
    performance_by_country: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    performance_by_device: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Trend data
    trend_direction: str = "stable"  # improving, declining, stable, volatile
    trend_strength: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SEOOptimizationRecommendations:
    """SEO optimization recommendations and action items"""
    content_id: str
    
    # Content optimization
    content_recommendations: List[str] = field(default_factory=list)
    keyword_optimization_suggestions: List[str] = field(default_factory=list)
    
    # Technical optimization
    technical_improvements: List[str] = field(default_factory=list)
    performance_optimizations: List[str] = field(default_factory=list)
    
    # Link building opportunities
    link_building_suggestions: List[str] = field(default_factory=list)
    internal_linking_improvements: List[str] = field(default_factory=list)
    
    # SERP feature opportunities
    featured_snippet_opportunities: List[str] = field(default_factory=list)
    rich_snippet_improvements: List[str] = field(default_factory=list)
    
    # Priority classification
    high_impact_actions: List[str] = field(default_factory=list)
    quick_wins: List[str] = field(default_factory=list)
    long_term_strategies: List[str] = field(default_factory=list)
    
    # Expected impact
    estimated_traffic_increase: int = 0
    estimated_ranking_improvement: int = 0
    estimated_revenue_impact: Decimal = Decimal('0')
    implementation_effort: str = "medium"  # low, medium, high
    
    timestamp: datetime = field(default_factory=datetime.now)


class SEOPerformanceIntelligence:
    """
    Advanced SEO performance intelligence providing comprehensive analytics,
    search ranking insights, and content optimization recommendations.
    """
    
    def __init__(self) -> None:
        self.seo_metrics: Dict[str, List[SEOPerformanceMetrics]] = defaultdict(list)
        self.keyword_analytics: Dict[str, KeywordPerformanceAnalytics] = {}
        self.optimization_recommendations: Dict[str, SEOOptimizationRecommendations] = {}
        
        # SEO performance benchmarks
        self.seo_benchmarks = {
            "target_avg_position": 10.0,        # Top 10 average position
            "min_organic_ctr": 0.02,            # 2% minimum CTR
            "target_page_speed": 3.0,           # 3 seconds target load time
            "min_content_score": 70.0,          # 70% minimum content quality
            "target_mobile_score": 90.0,        # 90% mobile friendliness
            "min_core_web_vitals": 75.0,        # 75% Core Web Vitals score
        }
        
        # Search engine market share (for weighted calculations)
        self.search_engine_weights = {
            SearchEngine.GOOGLE: 0.85,
            SearchEngine.BING: 0.08,
            SearchEngine.YAHOO: 0.03,
            SearchEngine.DUCKDUCKGO: 0.02,
            SearchEngine.YANDEX: 0.01,
            SearchEngine.BAIDU: 0.01,
        }
        
        # Content type SEO priority weights
        self.content_type_weights = {
            ContentType.BLOG_POST: 1.0,
            ContentType.VIDEO: 0.9,
            ContentType.PODCAST: 0.8,
            ContentType.IMAGE: 0.7,
            ContentType.SOCIAL_POST: 0.6,
            ContentType.PRODUCT_PAGE: 1.2,
            ContentType.LANDING_PAGE: 1.1,
        }
    
    async def analyze_seo_performance(
        self,
        content_id: str,
        content_type: ContentType,
        optimization_type: SEOOptimizationType,
        timeframe: timedelta = timedelta(days=30)
    ) -> SEOPerformanceMetrics:
        """
        Comprehensive SEO performance analysis with ranking and traffic insights
        """
        try:
            # Collect SEO data
            raw_data = await self._collect_seo_data(content_id, content_type, timeframe)
            
            # Calculate SEO performance metrics
            metrics = await self._calculate_seo_metrics(
                content_id, content_type, optimization_type, raw_data
            )
            
            # Analyze keyword performance
            await self._analyze_keyword_performance(metrics, raw_data)
            
            # Calculate technical SEO scores
            await self._calculate_technical_seo_scores(metrics, raw_data)
            
            # Generate optimization recommendations
            if await self._requires_seo_optimization(metrics):
                await self._generate_seo_recommendations(content_id, metrics)
            
            # Store metrics
            self.seo_metrics[content_id].append(metrics)
            
            # Limit history to last 40 entries
            if len(self.seo_metrics[content_id]) > 40:
                self.seo_metrics[content_id] = self.seo_metrics[content_id][-40:]
            
            logger.info(f"SEO performance analysis completed for {content_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing SEO performance for {content_id}: {e}")
            return SEOPerformanceMetrics(
                content_id=content_id,
                content_type=content_type,
                optimization_type=optimization_type
            )
    
    async def track_keyword_performance(
        self,
        keyword: str,
        content_id: str,
        tracking_data: Dict[str, Any]
    ) -> KeywordPerformanceAnalytics:
        """
        Track keyword-specific performance and ranking changes
        """
        try:
            # Calculate keyword analytics
            analytics = await self._calculate_keyword_analytics(keyword, content_id, tracking_data)
            
            # Update trend analysis
            await self._update_keyword_trends(analytics)
            
            # Store analytics
            keyword_key = f"{keyword}_{content_id}"
            self.keyword_analytics[keyword_key] = analytics
            
            logger.info(f"Keyword performance tracking completed for '{keyword}' on {content_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error tracking keyword performance for '{keyword}': {e}")
            return KeywordPerformanceAnalytics(keyword=keyword, content_id=content_id)
    
    async def get_seo_dashboard(
        self,
        creator_id: Optional[str] = None,
        timeframe: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Generate comprehensive SEO performance dashboard
        """
        try:
            # Filter metrics by creator and timeframe
            cutoff_time = datetime.now() - timeframe
            relevant_metrics = []
            
            for content_id, metrics_list in self.seo_metrics.items():
                for metric in metrics_list:
                    if (metric.timestamp >= cutoff_time and 
                        (creator_id is None or metric.creator_id == creator_id)):
                        relevant_metrics.append(metric)
            
            if not relevant_metrics:
                return {"error": "No SEO data available for the specified criteria"}
            
            # Calculate dashboard data
            dashboard_data = {
                "timeframe": str(timeframe),
                "creator_id": creator_id,
                "last_updated": datetime.now().isoformat(),
                
                # SEO overview
                "seo_overview": await self._calculate_seo_overview(relevant_metrics),
                
                # Ranking performance
                "ranking_performance": await self._calculate_ranking_performance(relevant_metrics),
                
                # Traffic analytics
                "traffic_analytics": await self._calculate_traffic_analytics(relevant_metrics),
                
                # Keyword insights
                "keyword_insights": await self._calculate_keyword_insights(),
                
                # Technical SEO health
                "technical_seo": await self._calculate_technical_seo_health(relevant_metrics),
                
                # Content performance
                "content_performance": await self._analyze_content_seo_performance(relevant_metrics),
                
                # Search engine breakdown
                "search_engine_performance": await self._calculate_search_engine_performance(relevant_metrics),
                
                # Geographic insights
                "geographic_performance": await self._calculate_geographic_seo_performance(relevant_metrics),
                
                # Trend analysis
                "trend_data": await self._generate_seo_trends(relevant_metrics),
                
                # Optimization opportunities
                "optimization_opportunities": await self._get_seo_optimization_summary(),
                
                # Alerts and recommendations
                "alerts": await self._generate_seo_alerts(relevant_metrics),
                "recommendations": await self._get_top_seo_recommendations()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating SEO dashboard: {e}")
            return {"error": str(e)}
    
    async def optimize_seo_strategy(
        self,
        content_id: str,
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize SEO strategy based on performance analysis and goals
        """
        try:
            # Get current SEO performance
            current_metrics = await self._get_current_seo_metrics(content_id)
            
            if not current_metrics:
                return {"error": "No SEO performance data available for optimization"}
            
            # Analyze optimization opportunities
            opportunities = await self._identify_seo_opportunities(
                current_metrics, optimization_goals
            )
            
            # Generate optimization strategy
            strategy = await self._generate_seo_optimization_strategy(
                content_id, current_metrics, opportunities, optimization_goals
            )
            
            # Calculate expected impact
            expected_impact = await self._calculate_seo_optimization_impact(
                current_metrics, strategy
            )
            
            return {
                "content_id": content_id,
                "current_performance": {
                    "average_position": current_metrics.average_position,
                    "organic_traffic": current_metrics.organic_traffic,
                    "click_through_rate": current_metrics.click_through_rate,
                    "content_score": current_metrics.content_score,
                    "page_speed_score": current_metrics.page_speed_score
                },
                "optimization_opportunities": opportunities,
                "optimization_strategy": strategy,
                "expected_impact": expected_impact,
                "implementation_timeline": "3-8 weeks",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error optimizing SEO strategy for {content_id}: {e}")
            return {"error": str(e), "success": False}
    
    # Helper methods for data collection and analysis
    
    async def _collect_seo_data(
        self,
        content_id: str,
        content_type: ContentType,
        timeframe: timedelta
    ) -> Dict[str, Any]:
        """Collect SEO performance data"""
        # Simulate SEO data collection - in production this would integrate with SEO tools
        content_hash = hash(content_id)
        
        return {
            "average_position": 15.5 + (content_hash % 20),
            "best_position": 3 + (content_hash % 10),
            "organic_traffic": 2500 + (content_hash % 1000),
            "organic_sessions": 1800 + (content_hash % 800),
            "organic_users": 1200 + (content_hash % 600),
            "click_through_rate": 0.05 + (content_hash % 100) / 10000,
            "target_keywords": ["content creation", "influencer marketing", "social media"],
            "ranking_keywords": 25 + (content_hash % 15),
            "top_10_keywords": 8 + (content_hash % 5),
            "top_3_keywords": 2 + (content_hash % 3),
            "page_speed_score": 80 + (content_hash % 20),
            "mobile_friendliness": 85 + (content_hash % 15),
            "core_web_vitals": 75 + (content_hash % 25),
            "bounce_rate": 0.35 + (content_hash % 100) / 1000,
            "time_on_page": 120 + (content_hash % 180),
            "total_backlinks": 150 + (content_hash % 100),
            "referring_domains": 45 + (content_hash % 30),
            "featured_snippets": content_hash % 3,
            "seo_revenue": 1250.0 + (content_hash % 500),
            "performance_by_engine": {
                "google": {"position": 12 + (content_hash % 15), "traffic_share": 0.85},
                "bing": {"position": 18 + (content_hash % 20), "traffic_share": 0.12},
                "yahoo": {"position": 25 + (content_hash % 25), "traffic_share": 0.03}
            }
        }
    
    async def _calculate_seo_metrics(
        self,
        content_id: str,
        content_type: ContentType,
        optimization_type: SEOOptimizationType,
        raw_data: Dict[str, Any]
    ) -> SEOPerformanceMetrics:
        """Calculate comprehensive SEO performance metrics"""
        
        # Basic ranking metrics
        average_position = raw_data.get("average_position", 50.0)
        best_position = raw_data.get("best_position", 50)
        worst_position = max(best_position + 20, 100)
        
        # Traffic metrics
        organic_traffic = raw_data.get("organic_traffic", 0)
        organic_sessions = raw_data.get("organic_sessions", 0)
        organic_users = raw_data.get("organic_users", 0)
        click_through_rate = raw_data.get("click_through_rate", 0.0)
        
        # Keyword metrics
        target_keywords = raw_data.get("target_keywords", [])
        ranking_keywords = raw_data.get("ranking_keywords", 0)
        top_10_keywords = raw_data.get("top_10_keywords", 0)
        top_3_keywords = raw_data.get("top_3_keywords", 0)
        
        # Calculate keyword difficulty score
        keyword_difficulty_score = min(100.0, (len(target_keywords) * 10) + (ranking_keywords * 2))
        
        # Content quality scores (simulated based on content type and optimization)
        content_weight = self.content_type_weights.get(content_type, 1.0)
        base_score = 70.0 * content_weight
        
        content_score = min(100.0, base_score + (ranking_keywords * 2))
        readability_score = min(100.0, base_score + 10)
        uniqueness_score = min(100.0, base_score + 5)
        relevance_score = min(100.0, base_score + (top_10_keywords * 3))
        
        # Technical SEO metrics
        page_speed_score = raw_data.get("page_speed_score", 80.0)
        mobile_friendliness = raw_data.get("mobile_friendliness", 85.0)
        core_web_vitals_score = raw_data.get("core_web_vitals", 75.0)
        accessibility_score = min(100.0, (page_speed_score + mobile_friendliness) / 2)
        
        # Engagement metrics
        bounce_rate = raw_data.get("bounce_rate", 0.35)
        time_on_page = raw_data.get("time_on_page", 120.0)
        pages_per_session = max(1.0, organic_sessions / max(organic_users, 1))
        conversion_rate = max(0.0, click_through_rate * 0.1)  # Simplified conversion rate
        
        # Backlink metrics
        total_backlinks = raw_data.get("total_backlinks", 0)
        referring_domains = raw_data.get("referring_domains", 0)
        domain_authority = min(100.0, 20 + (referring_domains * 0.8))
        link_quality_score = min(100.0, domain_authority * 0.9)
        
        # SERP features
        featured_snippets = raw_data.get("featured_snippets", 0)
        image_pack_appearances = raw_data.get("image_pack", 0)
        video_pack_appearances = raw_data.get("video_pack", 0)
        local_pack_appearances = raw_data.get("local_pack", 0)
        
        # Revenue attribution
        seo_attributed_revenue = Decimal(str(raw_data.get("seo_revenue", 0)))
        cost_per_acquisition = seo_attributed_revenue / max(organic_users, 1)
        return_on_ad_spend = float(seo_attributed_revenue) / max(float(cost_per_acquisition * organic_users), 1)
        
        # Performance by search engine
        performance_by_engine = raw_data.get("performance_by_engine", {})
        
        # Geographic performance (simulated)
        performance_by_region = {
            "US": {"position": average_position - 2, "traffic_share": 0.4},
            "EU": {"position": average_position + 1, "traffic_share": 0.35},
            "UK": {"position": average_position, "traffic_share": 0.15},
            "Others": {"position": average_position + 5, "traffic_share": 0.1}
        }
        
        return SEOPerformanceMetrics(
            content_id=content_id,
            content_type=content_type,
            optimization_type=optimization_type,
            average_position=average_position,
            best_position=best_position,
            worst_position=worst_position,
            position_change=raw_data.get("position_change", 0),
            organic_traffic=organic_traffic,
            organic_sessions=organic_sessions,
            organic_users=organic_users,
            click_through_rate=click_through_rate,
            target_keywords=target_keywords,
            ranking_keywords=ranking_keywords,
            top_10_keywords=top_10_keywords,
            top_3_keywords=top_3_keywords,
            keyword_difficulty_score=keyword_difficulty_score,
            content_score=content_score,
            readability_score=readability_score,
            uniqueness_score=uniqueness_score,
            relevance_score=relevance_score,
            page_speed_score=page_speed_score,
            mobile_friendliness=mobile_friendliness,
            core_web_vitals_score=core_web_vitals_score,
            accessibility_score=accessibility_score,
            bounce_rate=bounce_rate,
            time_on_page=time_on_page,
            pages_per_session=pages_per_session,
            conversion_rate=conversion_rate,
            total_backlinks=total_backlinks,
            referring_domains=referring_domains,
            domain_authority=domain_authority,
            link_quality_score=link_quality_score,
            featured_snippets=featured_snippets,
            image_pack_appearances=image_pack_appearances,
            video_pack_appearances=video_pack_appearances,
            local_pack_appearances=local_pack_appearances,
            seo_attributed_revenue=seo_attributed_revenue,
            cost_per_acquisition=cost_per_acquisition,
            return_on_ad_spend=return_on_ad_spend,
            performance_by_engine=performance_by_engine,
            performance_by_region=performance_by_region,
            creator_id=raw_data.get("creator_id"),
            platform=raw_data.get("platform", "web")
        )
    
    async def _analyze_keyword_performance(
        self,
        metrics -> None: SEOPerformanceMetrics,
        raw_data -> None: Dict[str, Any]
    ) -> None:
        """Analyze keyword-specific performance"""
        # Keyword performance analysis would be implemented here
        logger.info(f"Keyword performance analysis completed for {metrics.content_id}")
    
    async def _calculate_technical_seo_scores(
        self,
        metrics -> None: SEOPerformanceMetrics,
        raw_data -> None: Dict[str, Any]
    ) -> None:
        """Calculate technical SEO performance scores"""
        # Technical SEO calculations would be implemented here
        logger.info(f"Technical SEO analysis completed for {metrics.content_id}")
    
    async def _requires_seo_optimization(self, metrics: SEOPerformanceMetrics) -> bool:
        """Determine if SEO optimization is required"""
        return (
            metrics.average_position > self.seo_benchmarks["target_avg_position"] or
            metrics.click_through_rate < self.seo_benchmarks["min_organic_ctr"] or
            metrics.page_speed_score < self.seo_benchmarks["target_page_speed"] * 20 or  # Convert to 0-100 scale
            metrics.content_score < self.seo_benchmarks["min_content_score"] or
            metrics.mobile_friendliness < self.seo_benchmarks["target_mobile_score"]
        )
    
    async def _generate_seo_recommendations(
        self,
        content_id -> None: str,
        metrics -> None: SEOPerformanceMetrics
    ) -> None:
        """Generate SEO optimization recommendations"""
        recommendations = SEOOptimizationRecommendations(content_id=content_id)
        
        # Content optimization recommendations
        if metrics.content_score < self.seo_benchmarks["min_content_score"]:
            recommendations.content_recommendations.extend([
                "Improve content depth and comprehensiveness",
                "Add more relevant keywords naturally",
                "Enhance content structure with proper headings",
                "Include more authoritative sources and references"
            ])
            recommendations.high_impact_actions.append("Content quality improvement")
        
        # Keyword optimization
        if metrics.top_10_keywords < 5:  # Less than 5 keywords in top 10
            recommendations.keyword_optimization_suggestions.extend([
                "Research and target long-tail keywords",
                "Optimize existing content for target keywords",
                "Create content clusters around main topics",
                "Improve keyword density and semantic relevance"
            ])
            recommendations.high_impact_actions.append("Keyword strategy optimization")
        
        # Technical SEO improvements
        if metrics.page_speed_score < 80:
            recommendations.technical_improvements.extend([
                "Optimize images and reduce file sizes",
                "Implement browser caching",
                "Minimize CSS and JavaScript",
                "Use Content Delivery Network (CDN)"
            ])
            recommendations.quick_wins.append("Page speed optimization")
        
        # Mobile optimization
        if metrics.mobile_friendliness < 90:
            recommendations.technical_improvements.extend([
                "Improve mobile responsive design",
                "Optimize touch targets and navigation",
                "Reduce mobile page load times",
                "Test and fix mobile usability issues"
            ])
            recommendations.high_impact_actions.append("Mobile optimization")
        
        # Link building opportunities
        if metrics.referring_domains < 20:
            recommendations.link_building_suggestions.extend([
                "Create linkable asset content",
                "Reach out to relevant websites for backlinks",
                "Guest posting on authoritative sites",
                "Build relationships with industry influencers"
            ])
            recommendations.long_term_strategies.append("Link building campaign")
        
        # SERP feature opportunities
        if metrics.featured_snippets == 0:
            recommendations.featured_snippet_opportunities.extend([
                "Structure content to answer specific questions",
                "Use FAQ sections and Q&A format",
                "Optimize for voice search queries",
                "Create comprehensive how-to guides"
            ])
            recommendations.quick_wins.append("Featured snippet optimization")
        
        # Calculate expected impact
        recommendations.estimated_traffic_increase = int(metrics.organic_traffic * 0.4)  # 40% increase
        recommendations.estimated_ranking_improvement = max(5, int(metrics.average_position * 0.3))
        recommendations.estimated_revenue_impact = metrics.seo_attributed_revenue * Decimal("0.5")
        
        self.optimization_recommendations[content_id] = recommendations
    
    # Dashboard calculation methods
    
    async def _calculate_seo_overview(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate SEO performance overview"""
        if not metrics:
            return {}
        
        return {
            "total_organic_traffic": sum(m.organic_traffic for m in metrics),
            "average_position": statistics.mean([m.average_position for m in metrics]),
            "total_ranking_keywords": sum(m.ranking_keywords for m in metrics),
            "average_click_through_rate": statistics.mean([m.click_through_rate for m in metrics]),
            "total_backlinks": sum(m.total_backlinks for m in metrics),
            "average_content_score": statistics.mean([m.content_score for m in metrics]),
            "total_seo_revenue": float(sum(m.seo_attributed_revenue for m in metrics)),
            "content_pieces_tracked": len(set(m.content_id for m in metrics))
        }
    
    async def _calculate_ranking_performance(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate ranking performance metrics"""
        if not metrics:
            return {}
        
        return {
            "best_average_position": min(m.average_position for m in metrics),
            "worst_average_position": max(m.average_position for m in metrics),
            "total_top_10_keywords": sum(m.top_10_keywords for m in metrics),
            "total_top_3_keywords": sum(m.top_3_keywords for m in metrics),
            "featured_snippets_total": sum(m.featured_snippets for m in metrics),
            "average_domain_authority": statistics.mean([m.domain_authority for m in metrics])
        }
    
    async def _calculate_traffic_analytics(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate traffic analytics summary"""
        if not metrics:
            return {}
        
        return {
            "total_organic_sessions": sum(m.organic_sessions for m in metrics),
            "total_organic_users": sum(m.organic_users for m in metrics),
            "average_bounce_rate": statistics.mean([m.bounce_rate for m in metrics]),
            "average_time_on_page": statistics.mean([m.time_on_page for m in metrics]),
            "average_pages_per_session": statistics.mean([m.pages_per_session for m in metrics]),
            "average_conversion_rate": statistics.mean([m.conversion_rate for m in metrics])
        }
    
    async def _calculate_keyword_insights(self) -> Dict[str, Any]:
        """Calculate keyword performance insights"""
        if not self.keyword_analytics:
            return {}
        
        keywords_list = list(self.keyword_analytics.values())
        
        return {
            "total_tracked_keywords": len(keywords_list),
            "average_keyword_position": statistics.mean([k.current_position for k in keywords_list]),
            "improving_keywords": len([k for k in keywords_list if k.trend_direction == "improving"]),
            "declining_keywords": len([k for k in keywords_list if k.trend_direction == "declining"]),
            "average_search_volume": statistics.mean([k.search_volume for k in keywords_list if k.search_volume > 0])
        }
    
    async def _calculate_technical_seo_health(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate technical SEO health summary"""
        if not metrics:
            return {}
        
        return {
            "average_page_speed": statistics.mean([m.page_speed_score for m in metrics]),
            "average_mobile_score": statistics.mean([m.mobile_friendliness for m in metrics]),
            "average_core_web_vitals": statistics.mean([m.core_web_vitals_score for m in metrics]),
            "average_accessibility": statistics.mean([m.accessibility_score for m in metrics])
        }
    
    async def _analyze_content_seo_performance(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Dict]:
        """Analyze SEO performance by content type"""
        content_performance = defaultdict(list)
        
        for metric in metrics:
            content_performance[metric.content_type.value].append(metric)
        
        analysis = {}
        for content_type, type_metrics in content_performance.items():
            avg_position = statistics.mean([m.average_position for m in type_metrics])
            total_traffic = sum(m.organic_traffic for m in type_metrics)
            
            analysis[content_type] = {
                "average_position": avg_position,
                "total_organic_traffic": total_traffic,
                "content_count": len(type_metrics),
                "average_content_score": statistics.mean([m.content_score for m in type_metrics])
            }
        
        return analysis
    
    async def _calculate_search_engine_performance(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Dict]:
        """Calculate performance by search engine"""
        engine_performance = defaultdict(lambda: {"traffic": 0, "positions": []})
        
        for metric in metrics:
            for engine, data in metric.performance_by_engine.items():
                engine_performance[engine]["traffic"] += metric.organic_traffic * data.get("traffic_share", 0)
                engine_performance[engine]["positions"].append(data.get("position", 50))
        
        summary = {}
        for engine, data in engine_performance.items():
            summary[engine] = {
                "total_traffic": int(data["traffic"]),
                "average_position": statistics.mean(data["positions"]) if data["positions"] else 50,
                "tracked_content": len(data["positions"])
            }
        
        return summary
    
    async def _calculate_geographic_seo_performance(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, Dict]:
        """Calculate geographic SEO performance"""
        geographic_performance = defaultdict(lambda: {"traffic": 0, "positions": []})
        
        for metric in metrics:
            for region, data in metric.performance_by_region.items():
                geographic_performance[region]["traffic"] += metric.organic_traffic * data.get("traffic_share", 0)
                geographic_performance[region]["positions"].append(data.get("position", 50))
        
        summary = {}
        for region, data in geographic_performance.items():
            summary[region] = {
                "total_traffic": int(data["traffic"]),
                "average_position": statistics.mean(data["positions"]) if data["positions"] else 50,
                "traffic_share": data["traffic"] / sum(d["traffic"] for d in geographic_performance.values()) if geographic_performance else 0
            }
        
        return summary
    
    async def _generate_seo_trends(self, metrics: List[SEOPerformanceMetrics]) -> Dict[str, List]:
        """Generate SEO trend data for charts"""
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Group by week for trend analysis
        weekly_data = defaultdict(list)
        for metric in sorted_metrics:
            # Get start of week
            week_start = metric.timestamp - timedelta(days=metric.timestamp.weekday())
            week_key = week_start.date()
            weekly_data[week_key].append(metric)
        
        trend_data = {
            "weeks": [],
            "average_positions": [],
            "organic_traffic": [],
            "click_through_rates": [],
            "content_scores": []
        }
        
        for week, week_metrics in sorted(weekly_data.items()):
            trend_data["weeks"].append(week.isoformat())
            trend_data["average_positions"].append(statistics.mean([m.average_position for m in week_metrics]))
            trend_data["organic_traffic"].append(sum(m.organic_traffic for m in week_metrics))
            trend_data["click_through_rates"].append(statistics.mean([m.click_through_rate for m in week_metrics]))
            trend_data["content_scores"].append(statistics.mean([m.content_score for m in week_metrics]))
        
        return trend_data
    
    async def _get_seo_optimization_summary(self) -> Dict[str, Any]:
        """Get SEO optimization opportunities summary"""
        if not self.optimization_recommendations:
            return {}
        
        recommendations_list = list(self.optimization_recommendations.values())
        
        return {
            "total_optimization_opportunities": len(recommendations_list),
            "high_impact_actions": sum(len(r.high_impact_actions) for r in recommendations_list),
            "quick_wins_available": sum(len(r.quick_wins) for r in recommendations_list),
            "estimated_total_traffic_increase": sum(r.estimated_traffic_increase for r in recommendations_list),
            "estimated_total_revenue_impact": float(sum(r.estimated_revenue_impact for r in recommendations_list))
        }
    
    async def _generate_seo_alerts(self, metrics: List[SEOPerformanceMetrics]) -> List[Dict[str, str]]:
        """Generate SEO performance alerts"""
        alerts = []
        
        # Check for ranking drops
        poor_rankings = [m for m in metrics if m.average_position > 30]
        if poor_rankings:
            alerts.append({
                "type": "ranking_decline",
                "severity": "high",
                "message": f"{len(poor_rankings)} content pieces have poor search rankings",
                "recommendation": "Review and optimize content for better search visibility"
            })
        
        # Check for low organic traffic
        low_traffic = [m for m in metrics if m.organic_traffic < 100]
        if len(low_traffic) > len(metrics) * 0.3:  # More than 30% have low traffic
            alerts.append({
                "type": "low_organic_traffic",
                "severity": "medium",
                "message": f"{len(low_traffic)} content pieces have low organic traffic",
                "recommendation": "Improve SEO optimization and content promotion"
            })
        
        # Check for technical issues
        slow_pages = [m for m in metrics if m.page_speed_score < 60]
        if slow_pages:
            alerts.append({
                "type": "page_speed",
                "severity": "medium",
                "message": f"{len(slow_pages)} pages have slow loading speeds",
                "recommendation": "Optimize page speed and Core Web Vitals"
            })
        
        return alerts
    
    async def _get_top_seo_recommendations(self) -> List[Dict[str, str]]:
        """Get top SEO recommendations across all content"""
        recommendations = []
        
        for content_id, rec in self.optimization_recommendations.items():
            for action in rec.high_impact_actions:
                recommendations.append({
                    "content_id": content_id,
                    "priority": "high",
                    "recommendation": action,
                    "estimated_traffic_impact": f"+{rec.estimated_traffic_increase:,} visits"
                })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    # Optimization methods
    
    async def _get_current_seo_metrics(self, content_id: str) -> Optional[SEOPerformanceMetrics]:
        """Get current SEO metrics for content"""
        metrics_list = self.seo_metrics.get(content_id, [])
        return metrics_list[-1] if metrics_list else None
    
    async def _identify_seo_opportunities(
        self,
        metrics: SEOPerformanceMetrics,
        optimization_goals: Dict[str, Any]
    ) -> List[str]:
        """Identify SEO optimization opportunities"""
        opportunities = []
        
        target_position = optimization_goals.get("target_position", 10)
        if metrics.average_position > target_position:
            opportunities.append("Improve search rankings")
        
        target_traffic = optimization_goals.get("target_organic_traffic", 5000)
        if metrics.organic_traffic < target_traffic:
            opportunities.append("Increase organic traffic")
        
        target_ctr = optimization_goals.get("target_click_through_rate", 0.05)
        if metrics.click_through_rate < target_ctr:
            opportunities.append("Optimize click-through rates")
        
        if metrics.page_speed_score < 85:
            opportunities.append("Improve page speed and technical SEO")
        
        return opportunities
    
    async def _generate_seo_optimization_strategy(
        self,
        content_id: str,
        metrics: SEOPerformanceMetrics,
        opportunities: List[str],
        optimization_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed SEO optimization strategy"""
        return {
            "phase_1": "Technical SEO optimization and page speed improvements",
            "phase_2": "Content optimization and keyword targeting",
            "phase_3": "Link building and authority development",
            "timeline_weeks": 6,
            "resource_requirements": "1 SEO Specialist, 1 Content Writer, 1 Developer",
            "estimated_investment": "€15,000"
        }
    
    async def _calculate_seo_optimization_impact(
        self,
        current_metrics: SEOPerformanceMetrics,
        strategy: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate expected SEO optimization impact"""
        return {
            "ranking_improvement": 15,           # 15 position improvement
            "traffic_increase": 0.60,           # 60% traffic increase
            "click_through_rate_improvement": 0.35,  # 35% CTR improvement
            "content_score_improvement": 0.25,  # 25% content score improvement
            "page_speed_improvement": 0.20      # 20% page speed improvement
        }
    
    async def _calculate_keyword_analytics(
        self,
        keyword: str,
        content_id: str,
        tracking_data: Dict[str, Any]
    ) -> KeywordPerformanceAnalytics:
        """Calculate keyword performance analytics"""
        
        current_position = tracking_data.get("position", 50)
        previous_position = tracking_data.get("previous_position", current_position)
        position_change = previous_position - current_position  # Positive is improvement
        
        return KeywordPerformanceAnalytics(
            keyword=keyword,
            content_id=content_id,
            current_position=current_position,
            previous_position=previous_position,
            position_change=position_change,
            best_position_ever=tracking_data.get("best_position", current_position),
            search_volume=tracking_data.get("search_volume", 1000),
            competition_score=tracking_data.get("competition", 0.5),
            keyword_difficulty=tracking_data.get("difficulty", 50.0),
            cost_per_click=Decimal(str(tracking_data.get("cpc", 1.50))),
            impressions=tracking_data.get("impressions", 5000),
            clicks=tracking_data.get("clicks", 100),
            click_through_rate=tracking_data.get("clicks", 100) / max(tracking_data.get("impressions", 5000), 1),
            search_intent=tracking_data.get("intent", "informational"),
            relevance_score=tracking_data.get("relevance", 0.8),
            content_match_score=tracking_data.get("content_match", 0.7),
            trend_direction="improving" if position_change > 5 else "declining" if position_change < -5 else "stable",
            trend_strength=abs(position_change) / 10.0
        )
    
    async def _update_keyword_trends(self, analytics -> None: KeywordPerformanceAnalytics) -> None:
        """Update keyword trend analysis"""
        # Keyword trend updates would be implemented here
        logger.info(f"Keyword trend analysis updated for '{analytics.keyword}'")


# Global SEO performance intelligence instance
seo_performance_intelligence = SEOPerformanceIntelligence()


# Convenience functions for external use
async def analyze_seo_performance(
    content_id: str,
    content_type: ContentType,
    optimization_type: SEOOptimizationType,
    timeframe: timedelta = timedelta(days=30)
) -> SEOPerformanceMetrics:
    """Analyze SEO performance for content"""
    return await seo_performance_intelligence.analyze_seo_performance(
        content_id, content_type, optimization_type, timeframe
    )


async def track_keyword_performance(
    keyword: str,
    content_id: str,
    tracking_data: Dict[str, Any]
) -> KeywordPerformanceAnalytics:
    """Track keyword performance"""
    return await seo_performance_intelligence.track_keyword_performance(keyword, content_id, tracking_data)


async def get_seo_dashboard(
    creator_id: Optional[str] = None,
    timeframe: timedelta = timedelta(days=30)
) -> Dict[str, Any]:
    """Get SEO performance dashboard"""
    return await seo_performance_intelligence.get_seo_dashboard(creator_id, timeframe)


async def optimize_seo_strategy(
    content_id: str,
    optimization_goals: Dict[str, Any]
) -> Dict[str, Any]:
    """Optimize SEO strategy for content"""
    return await seo_performance_intelligence.optimize_seo_strategy(content_id, optimization_goals)


def get_seo_metrics(content_id: str) -> Optional[List[SEOPerformanceMetrics]]:
    """Get SEO metrics history for content"""
    return seo_performance_intelligence.seo_metrics.get(content_id)


def get_keyword_analytics(keyword: str, content_id: str) -> Optional[KeywordPerformanceAnalytics]:
    """Get keyword analytics"""
    keyword_key = f"{keyword}_{content_id}"
    return seo_performance_intelligence.keyword_analytics.get(keyword_key)