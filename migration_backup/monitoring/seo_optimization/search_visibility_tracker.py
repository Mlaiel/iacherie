"""
Search Visibility Tracker - SEO Optimization Module
=================================================

Advanced search visibility tracking system for monitoring content
discoverability across multiple search engines and platforms.

Features:
- Real-time search visibility monitoring
- Multi-platform search tracking
- Visibility score calculation
- Search result feature tracking
- Competitor visibility comparison
- Search trend analysis

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

class SearchEngine(Enum):
    """Search engines for visibility tracking"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"

class VisibilityStatus(Enum):
    """Search visibility status"""
    EXCELLENT = "excellent"    # 80-100%
    GOOD = "good"             # 60-79%
    AVERAGE = "average"       # 40-59%
    POOR = "poor"            # 20-39%
    VERY_POOR = "very_poor"  # 0-19%

class SearchFeature(Enum):
    """Search result features"""
    FEATURED_SNIPPET = "featured_snippet"
    KNOWLEDGE_PANEL = "knowledge_panel"
    IMAGE_PACK = "image_pack"
    VIDEO_CAROUSEL = "video_carousel"
    LOCAL_PACK = "local_pack"
    REVIEWS = "reviews"
    FAQ = "faq"
    PEOPLE_ALSO_ASK = "people_also_ask"

@dataclass
class VisibilityMetrics:
    """Search visibility metrics"""
    search_engine: SearchEngine = SearchEngine.GOOGLE
    keyword: str = ""
    content_id: str = ""
    
    # Visibility scores
    visibility_score: float = 0.0  # 0-100%
    ranking_position: int = 0
    search_volume: int = 0
    estimated_traffic: int = 0
    
    # Search features
    featured_snippet: bool = False
    knowledge_panel: bool = False
    image_results: bool = False
    video_results: bool = False
    
    # Click metrics
    impressions: int = 0
    clicks: int = 0
    click_through_rate: float = 0.0
    average_position: float = 0.0
    
    # Competitive metrics
    competitor_above_count: int = 0
    market_share: float = 0.0
    visibility_trend: str = "stable"  # rising, falling, stable
    
    # Metadata
    measured_at: datetime = field(default_factory=datetime.now)

@dataclass
class VisibilityAlert:
    """Visibility alert for significant changes"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    keyword: str = ""
    search_engine: SearchEngine = SearchEngine.GOOGLE
    
    # Alert details
    alert_type: str = ""  # visibility_drop, visibility_gain, feature_lost, feature_gained
    severity: str = "medium"  # low, medium, high, critical
    previous_value: float = 0.0
    current_value: float = 0.0
    change_percentage: float = 0.0
    
    # Context
    description: str = ""
    possible_causes: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Metadata
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

@dataclass
class CompetitorVisibility:
    """Competitor visibility analysis"""
    competitor_name: str = ""
    competitor_url: str = ""
    search_engine: SearchEngine = SearchEngine.GOOGLE
    
    # Visibility comparison
    our_visibility: float = 0.0
    competitor_visibility: float = 0.0
    visibility_gap: float = 0.0
    
    # Keyword overlap
    shared_keywords: List[str] = field(default_factory=list)
    competitor_winning_keywords: List[str] = field(default_factory=list)
    our_winning_keywords: List[str] = field(default_factory=list)
    
    # Feature comparison
    competitor_features: List[SearchFeature] = field(default_factory=list)
    our_features: List[SearchFeature] = field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)

class SearchVisibilityTracker:
    """Main search visibility tracking system"""
    
    def __init__(self):
        self.visibility_metrics: Dict[str, List[VisibilityMetrics]] = defaultdict(list)
        self.visibility_alerts: List[VisibilityAlert] = []
        self.competitor_analyses: List[CompetitorVisibility] = []
        
        # Configuration
        self.tracking_keywords = self._initialize_tracking_keywords()
        self.competitors = self._initialize_competitors()
        self.alert_thresholds = self._initialize_alert_thresholds()
        
        # Monitoring state
        self.monitoring_active = False
        self.tracking_frequency_minutes = 60
        
    def _initialize_tracking_keywords(self) -> List[Dict[str, Any]]:
        """Initialize keywords to track for visibility"""
        return [
            {
                "keyword": "music production",
                "priority": "high",
                "target_engines": [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
                "target_visibility": 70.0
            },
            {
                "keyword": "content creator",
                "priority": "high",
                "target_engines": [SearchEngine.GOOGLE, SearchEngine.INSTAGRAM],
                "target_visibility": 60.0
            },
            {
                "keyword": "viral content",
                "priority": "medium",
                "target_engines": [SearchEngine.GOOGLE, SearchEngine.TIKTOK],
                "target_visibility": 50.0
            },
            {
                "keyword": "youtube optimization",
                "priority": "high",
                "target_engines": [SearchEngine.GOOGLE, SearchEngine.YOUTUBE],
                "target_visibility": 65.0
            },
            {
                "keyword": "social media growth",
                "priority": "medium",
                "target_engines": [SearchEngine.GOOGLE, SearchEngine.INSTAGRAM],
                "target_visibility": 55.0
            }
        ]
        
    def _initialize_competitors(self) -> List[Dict[str, Any]]:
        """Initialize competitor list for visibility comparison"""
        return [
            {
                "name": "CreatorStudio",
                "url": "creatorstudio.com",
                "focus_area": "content_creation"
            },
            {
                "name": "VideoBoost",
                "url": "videoboost.io",
                "focus_area": "video_optimization"
            },
            {
                "name": "SocialGrow",
                "url": "socialgrow.co",
                "focus_area": "social_media"
            }
        ]
        
    def _initialize_alert_thresholds(self) -> Dict[str, float]:
        """Initialize alert thresholds for visibility changes"""
        return {
            "visibility_drop_warning": -10.0,  # 10% drop
            "visibility_drop_critical": -25.0,  # 25% drop
            "visibility_gain_notable": 15.0,   # 15% gain
            "ranking_drop_warning": 5,         # Drop 5+ positions
            "ranking_drop_critical": 15,       # Drop 15+ positions
            "traffic_drop_warning": -20.0,     # 20% traffic drop
            "traffic_drop_critical": -40.0     # 40% traffic drop
        }
        
    async def start_monitoring(self):
        """Start search visibility monitoring"""
        self.monitoring_active = True
        
        monitoring_tasks = [
            self._monitor_keyword_visibility(),
            self._detect_visibility_changes(),
            self._analyze_search_features(),
            self._compare_competitor_visibility(),
            self._generate_visibility_reports()
        ]
        
        await asyncio.gather(*monitoring_tasks)
        
    async def stop_monitoring(self):
        """Stop search visibility monitoring"""
        self.monitoring_active = False
        logger.info("Search visibility monitoring stopped")
        
    async def _monitor_keyword_visibility(self):
        """Monitor visibility for tracked keywords"""
        while self.monitoring_active:
            try:
                for keyword_data in self.tracking_keywords:
                    keyword = keyword_data["keyword"]
                    target_engines = keyword_data["target_engines"]
                    
                    for search_engine in target_engines:
                        metrics = await self._measure_visibility(keyword, search_engine)
                        
                        # Store metrics
                        key = f"{keyword}_{search_engine.value}"
                        self.visibility_metrics[key].append(metrics)
                        
                        # Keep only last 100 measurements
                        if len(self.visibility_metrics[key]) > 100:
                            self.visibility_metrics[key].pop(0)
                            
                        # Check for alerts
                        await self._check_visibility_alerts(metrics, keyword_data)
                        
                await asyncio.sleep(self.tracking_frequency_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error monitoring keyword visibility: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    async def _measure_visibility(self, keyword: str, search_engine: SearchEngine) -> VisibilityMetrics:
        """Measure search visibility for keyword (simulated implementation)"""
        import random
        
        # Simulate search visibility measurement
        ranking_position = random.randint(1, 100)
        search_volume = random.randint(1000, 50000)
        
        # Calculate visibility score based on ranking
        if ranking_position <= 3:
            visibility_score = random.uniform(80, 100)
        elif ranking_position <= 10:
            visibility_score = random.uniform(50, 80)
        elif ranking_position <= 20:
            visibility_score = random.uniform(25, 50)
        elif ranking_position <= 50:
            visibility_score = random.uniform(10, 25)
        else:
            visibility_score = random.uniform(0, 10)
            
        # Estimate traffic based on ranking and volume
        position_ctr = max(0.01, 0.3 * (1 / ranking_position))
        estimated_traffic = int(search_volume * position_ctr)
        
        # Simulate search features
        featured_snippet = ranking_position <= 5 and random.random() < 0.3
        knowledge_panel = keyword in ["music production", "content creator"] and random.random() < 0.2
        image_results = random.random() < 0.4
        video_results = search_engine in [SearchEngine.GOOGLE, SearchEngine.YOUTUBE] and random.random() < 0.6
        
        # Calculate impressions and clicks
        impressions = int(search_volume * 0.1)  # 10% of search volume
        ctr = position_ctr
        clicks = int(impressions * ctr)
        
        return VisibilityMetrics(
            search_engine=search_engine,
            keyword=keyword,
            content_id=f"content_{keyword.replace(' ', '_')}",
            visibility_score=visibility_score,
            ranking_position=ranking_position,
            search_volume=search_volume,
            estimated_traffic=estimated_traffic,
            featured_snippet=featured_snippet,
            knowledge_panel=knowledge_panel,
            image_results=image_results,
            video_results=video_results,
            impressions=impressions,
            clicks=clicks,
            click_through_rate=ctr,
            average_position=ranking_position + random.uniform(-1, 1),
            competitor_above_count=random.randint(0, min(5, ranking_position)),
            market_share=visibility_score / 100.0,
            visibility_trend="stable"
        )
        
    async def _check_visibility_alerts(self, metrics: VisibilityMetrics, keyword_data: Dict[str, Any]):
        """Check for visibility alerts based on metrics"""
        keyword = metrics.keyword
        search_engine = metrics.search_engine
        
        # Get historical data for comparison
        key = f"{keyword}_{search_engine.value}"
        historical_metrics = self.visibility_metrics[key]
        
        if len(historical_metrics) < 2:
            return  # Need at least 2 measurements for comparison
            
        previous_metrics = historical_metrics[-2]
        current_metrics = metrics
        
        # Check visibility score changes
        visibility_change = current_metrics.visibility_score - previous_metrics.visibility_score
        visibility_change_pct = (visibility_change / previous_metrics.visibility_score) * 100 if previous_metrics.visibility_score > 0 else 0
        
        # Visibility drop alerts
        if visibility_change_pct <= self.alert_thresholds["visibility_drop_critical"]:
            await self._create_alert(
                metrics, "visibility_drop", "critical",
                f"Critical visibility drop: {visibility_change_pct:.1f}%",
                ["Algorithm update", "Technical issues", "Competitor improvement"],
                ["Investigate technical issues", "Review content quality", "Check for penalties"]
            )
        elif visibility_change_pct <= self.alert_thresholds["visibility_drop_warning"]:
            await self._create_alert(
                metrics, "visibility_drop", "high",
                f"Significant visibility drop: {visibility_change_pct:.1f}%",
                ["Content freshness", "Competition increase", "Search trends"],
                ["Update content", "Improve SEO", "Monitor competitors"]
            )
            
        # Visibility gain alerts
        elif visibility_change_pct >= self.alert_thresholds["visibility_gain_notable"]:
            await self._create_alert(
                metrics, "visibility_gain", "low",
                f"Notable visibility improvement: {visibility_change_pct:.1f}%",
                ["Content optimization", "Backlink acquisition", "Algorithm favor"],
                ["Scale successful strategies", "Analyze winning factors"]
            )
            
        # Ranking position alerts
        ranking_change = current_metrics.ranking_position - previous_metrics.ranking_position
        if ranking_change >= self.alert_thresholds["ranking_drop_critical"]:
            await self._create_alert(
                metrics, "ranking_drop", "critical",
                f"Critical ranking drop: {ranking_change} positions",
                ["Technical SEO issues", "Content penalties", "Strong competitors"],
                ["Immediate technical audit", "Content review", "Competitor analysis"]
            )
        elif ranking_change >= self.alert_thresholds["ranking_drop_warning"]:
            await self._create_alert(
                metrics, "ranking_drop", "high",
                f"Ranking position drop: {ranking_change} positions",
                ["Content staleness", "Competition", "Algorithm changes"],
                ["Content refresh", "SEO optimization", "Monitor trends"]
            )
            
        # Search feature changes
        if previous_metrics.featured_snippet and not current_metrics.featured_snippet:
            await self._create_alert(
                metrics, "feature_lost", "high",
                "Lost featured snippet position",
                ["Content quality decline", "Competitor optimization", "Algorithm changes"],
                ["Optimize for featured snippets", "Improve answer quality"]
            )
        elif not previous_metrics.featured_snippet and current_metrics.featured_snippet:
            await self._create_alert(
                metrics, "feature_gained", "low",
                "Gained featured snippet position",
                ["Content optimization success", "Algorithm favor"],
                ["Monitor and maintain", "Apply to similar content"]
            )
            
    async def _create_alert(self, 
                          metrics: VisibilityMetrics,
                          alert_type: str,
                          severity: str,
                          description: str,
                          possible_causes: List[str],
                          recommended_actions: List[str]):
        """Create visibility alert"""
        
        alert = VisibilityAlert(
            content_id=metrics.content_id,
            keyword=metrics.keyword,
            search_engine=metrics.search_engine,
            alert_type=alert_type,
            severity=severity,
            current_value=metrics.visibility_score,
            description=description,
            possible_causes=possible_causes,
            recommended_actions=recommended_actions
        )
        
        self.visibility_alerts.append(alert)
        logger.warning(f"Visibility alert: {description} for {metrics.keyword}")
        
    async def _detect_visibility_changes(self):
        """Detect and analyze visibility changes"""
        while self.monitoring_active:
            try:
                # Analyze trends across all tracked keywords
                for key, metrics_list in self.visibility_metrics.items():
                    if len(metrics_list) >= 5:  # Need sufficient data
                        await self._analyze_visibility_trend(key, metrics_list[-5:])
                        
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Error detecting visibility changes: {e}")
                await asyncio.sleep(300)
                
    async def _analyze_visibility_trend(self, key: str, recent_metrics: List[VisibilityMetrics]):
        """Analyze visibility trend for keyword"""
        
        visibility_scores = [m.visibility_score for m in recent_metrics]
        ranking_positions = [m.ranking_position for m in recent_metrics]
        
        # Calculate trend direction
        if len(visibility_scores) >= 3:
            # Linear regression for trend
            x = list(range(len(visibility_scores)))
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(visibility_scores)
            sum_xy = sum(xi * yi for xi, yi in zip(x, visibility_scores))
            sum_x2 = sum(xi * xi for xi in x)
            
            # Calculate slope
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                if slope > 1:
                    trend = "rising"
                elif slope < -1:
                    trend = "falling"
                else:
                    trend = "stable"
                    
                # Update trend in latest metrics
                if recent_metrics:
                    recent_metrics[-1].visibility_trend = trend
                    
    async def _analyze_search_features(self):
        """Analyze search result features"""
        while self.monitoring_active:
            try:
                # Analyze feature presence across keywords
                feature_analysis = defaultdict(int)
                total_measurements = 0
                
                for metrics_list in self.visibility_metrics.values():
                    if metrics_list:
                        latest_metrics = metrics_list[-1]
                        total_measurements += 1
                        
                        if latest_metrics.featured_snippet:
                            feature_analysis["featured_snippet"] += 1
                        if latest_metrics.knowledge_panel:
                            feature_analysis["knowledge_panel"] += 1
                        if latest_metrics.image_results:
                            feature_analysis["image_results"] += 1
                        if latest_metrics.video_results:
                            feature_analysis["video_results"] += 1
                            
                # Calculate feature presence percentages
                if total_measurements > 0:
                    feature_percentages = {
                        feature: (count / total_measurements) * 100
                        for feature, count in feature_analysis.items()
                    }
                    
                    logger.info(f"Search feature analysis: {feature_percentages}")
                    
                await asyncio.sleep(600)  # Analyze every 10 minutes
                
            except Exception as e:
                logger.error(f"Error analyzing search features: {e}")
                await asyncio.sleep(600)
                
    async def _compare_competitor_visibility(self):
        """Compare visibility with competitors"""
        while self.monitoring_active:
            try:
                for competitor in self.competitors:
                    analysis = await self._analyze_competitor_visibility(competitor)
                    if analysis:
                        self.competitor_analyses.append(analysis)
                        
                # Keep only recent analyses
                cutoff_date = datetime.now() - timedelta(days=7)
                self.competitor_analyses = [
                    analysis for analysis in self.competitor_analyses
                    if analysis.analyzed_at > cutoff_date
                ]
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Error comparing competitor visibility: {e}")
                await asyncio.sleep(3600)
                
    async def _analyze_competitor_visibility(self, competitor: Dict[str, Any]) -> Optional[CompetitorVisibility]:
        """Analyze competitor visibility for comparison"""
        import random
        
        # Simulate competitor visibility analysis
        our_avg_visibility = 0.0
        competitor_avg_visibility = random.uniform(30, 80)
        
        # Calculate our average visibility
        all_our_visibility = []
        for metrics_list in self.visibility_metrics.values():
            if metrics_list:
                all_our_visibility.append(metrics_list[-1].visibility_score)
                
        if all_our_visibility:
            our_avg_visibility = statistics.mean(all_our_visibility)
        else:
            our_avg_visibility = random.uniform(20, 70)
            
        visibility_gap = competitor_avg_visibility - our_avg_visibility
        
        # Simulate keyword overlap
        our_keywords = [kw["keyword"] for kw in self.tracking_keywords]
        competitor_keywords = ["social media tips", "content strategy", "viral marketing", "creator tools"]
        
        shared_keywords = list(set(our_keywords).intersection(set(competitor_keywords)))
        competitor_winning = [kw for kw in shared_keywords if random.random() < 0.6]
        our_winning = [kw for kw in shared_keywords if kw not in competitor_winning]
        
        # Simulate search features
        competitor_features = []
        if random.random() < 0.4:
            competitor_features.append(SearchFeature.FEATURED_SNIPPET)
        if random.random() < 0.3:
            competitor_features.append(SearchFeature.KNOWLEDGE_PANEL)
        if random.random() < 0.6:
            competitor_features.append(SearchFeature.VIDEO_CAROUSEL)
            
        our_features = []
        if random.random() < 0.3:
            our_features.append(SearchFeature.FEATURED_SNIPPET)
        if random.random() < 0.2:
            our_features.append(SearchFeature.KNOWLEDGE_PANEL)
        if random.random() < 0.5:
            our_features.append(SearchFeature.VIDEO_CAROUSEL)
            
        return CompetitorVisibility(
            competitor_name=competitor["name"],
            competitor_url=competitor["url"],
            search_engine=SearchEngine.GOOGLE,
            our_visibility=our_avg_visibility,
            competitor_visibility=competitor_avg_visibility,
            visibility_gap=visibility_gap,
            shared_keywords=shared_keywords,
            competitor_winning_keywords=competitor_winning,
            our_winning_keywords=our_winning,
            competitor_features=competitor_features,
            our_features=our_features
        )
        
    async def _generate_visibility_reports(self):
        """Generate periodic visibility reports"""
        while self.monitoring_active:
            try:
                # Generate daily visibility summary
                summary = await self.get_visibility_summary()
                logger.info(f"Daily visibility summary: {summary['overall_visibility_score']:.1f}%")
                
                await asyncio.sleep(86400)  # Generate daily reports
                
            except Exception as e:
                logger.error(f"Error generating visibility reports: {e}")
                await asyncio.sleep(86400)
                
    async def get_visibility_summary(self, keyword: str = None) -> Dict[str, Any]:
        """Get comprehensive visibility summary"""
        
        if keyword:
            return await self._get_keyword_visibility_summary(keyword)
        else:
            return await self._get_overall_visibility_summary()
            
    async def _get_keyword_visibility_summary(self, keyword: str) -> Dict[str, Any]:
        """Get visibility summary for specific keyword"""
        
        keyword_metrics = []
        for key, metrics_list in self.visibility_metrics.items():
            if keyword in key and metrics_list:
                keyword_metrics.append(metrics_list[-1])
                
        if not keyword_metrics:
            return {"error": f"No visibility data for keyword: {keyword}"}
            
        # Calculate summary statistics
        avg_visibility = statistics.mean([m.visibility_score for m in keyword_metrics])
        avg_ranking = statistics.mean([m.ranking_position for m in keyword_metrics])
        total_traffic = sum([m.estimated_traffic for m in keyword_metrics])
        
        # Search engines breakdown
        engine_performance = {}
        for metrics in keyword_metrics:
            engine_performance[metrics.search_engine.value] = {
                "visibility_score": metrics.visibility_score,
                "ranking": metrics.ranking_position,
                "traffic": metrics.estimated_traffic
            }
            
        # Search features
        features_present = []
        for metrics in keyword_metrics:
            if metrics.featured_snippet:
                features_present.append("featured_snippet")
            if metrics.knowledge_panel:
                features_present.append("knowledge_panel")
            if metrics.image_results:
                features_present.append("image_results")
            if metrics.video_results:
                features_present.append("video_results")
                
        return {
            "keyword": keyword,
            "overall_visibility_score": avg_visibility,
            "visibility_status": self._get_visibility_status(avg_visibility),
            "average_ranking": avg_ranking,
            "estimated_monthly_traffic": total_traffic,
            "search_engines": engine_performance,
            "search_features": list(set(features_present)),
            "recommendations": await self._get_keyword_recommendations(keyword, avg_visibility, avg_ranking)
        }
        
    async def _get_overall_visibility_summary(self) -> Dict[str, Any]:
        """Get overall visibility summary across all keywords"""
        
        all_latest_metrics = []
        for metrics_list in self.visibility_metrics.values():
            if metrics_list:
                all_latest_metrics.append(metrics_list[-1])
                
        if not all_latest_metrics:
            return {"error": "No visibility data available"}
            
        # Calculate overall statistics
        overall_visibility = statistics.mean([m.visibility_score for m in all_latest_metrics])
        total_keywords = len(set([m.keyword for m in all_latest_metrics]))
        total_traffic = sum([m.estimated_traffic for m in all_latest_metrics])
        
        # Visibility distribution
        visibility_distribution = {
            "excellent": len([m for m in all_latest_metrics if m.visibility_score >= 80]),
            "good": len([m for m in all_latest_metrics if 60 <= m.visibility_score < 80]),
            "average": len([m for m in all_latest_metrics if 40 <= m.visibility_score < 60]),
            "poor": len([m for m in all_latest_metrics if 20 <= m.visibility_score < 40]),
            "very_poor": len([m for m in all_latest_metrics if m.visibility_score < 20])
        }
        
        # Top performing keywords
        top_keywords = sorted(all_latest_metrics, key=lambda x: x.visibility_score, reverse=True)[:5]
        
        # Recent alerts
        recent_alerts = [
            alert for alert in self.visibility_alerts
            if alert.triggered_at > datetime.now() - timedelta(days=7)
        ]
        
        # Search engine performance
        engine_performance = defaultdict(list)
        for metrics in all_latest_metrics:
            engine_performance[metrics.search_engine.value].append(metrics.visibility_score)
            
        engine_averages = {
            engine: statistics.mean(scores)
            for engine, scores in engine_performance.items()
        }
        
        return {
            "overall_visibility_score": overall_visibility,
            "visibility_status": self._get_visibility_status(overall_visibility),
            "total_keywords_tracked": total_keywords,
            "estimated_monthly_traffic": total_traffic,
            "visibility_distribution": visibility_distribution,
            "top_performing_keywords": [
                {
                    "keyword": m.keyword,
                    "visibility_score": m.visibility_score,
                    "ranking": m.ranking_position,
                    "traffic": m.estimated_traffic
                }
                for m in top_keywords
            ],
            "search_engine_performance": engine_averages,
            "recent_alerts": len(recent_alerts),
            "critical_alerts": len([a for a in recent_alerts if a.severity == "critical"]),
            "insights": await self._generate_visibility_insights(all_latest_metrics)
        }
        
    def _get_visibility_status(self, visibility_score: float) -> str:
        """Get visibility status based on score"""
        if visibility_score >= 80:
            return VisibilityStatus.EXCELLENT.value
        elif visibility_score >= 60:
            return VisibilityStatus.GOOD.value
        elif visibility_score >= 40:
            return VisibilityStatus.AVERAGE.value
        elif visibility_score >= 20:
            return VisibilityStatus.POOR.value
        else:
            return VisibilityStatus.VERY_POOR.value
            
    async def _get_keyword_recommendations(self, keyword: str, visibility: float, ranking: int) -> List[str]:
        """Get recommendations for improving keyword visibility"""
        recommendations = []
        
        if visibility < 40:
            recommendations.append("Focus on comprehensive content optimization")
            recommendations.append("Build high-quality backlinks to improve authority")
            
        if ranking > 20:
            recommendations.append("Improve on-page SEO optimization")
            recommendations.append("Create more relevant, high-quality content")
            
        if visibility < 60:
            recommendations.append("Optimize for featured snippets")
            recommendations.append("Improve page loading speed and technical SEO")
            
        recommendations.append("Monitor competitor strategies")
        recommendations.append("Update content regularly to maintain freshness")
        
        return recommendations
        
    async def _generate_visibility_insights(self, metrics: List[VisibilityMetrics]) -> List[str]:
        """Generate insights from visibility data"""
        insights = []
        
        # Overall performance insights
        avg_visibility = statistics.mean([m.visibility_score for m in metrics])
        if avg_visibility < 40:
            insights.append("Overall visibility is below average - focus on core SEO improvements")
        elif avg_visibility > 70:
            insights.append("Strong visibility performance across tracked keywords")
            
        # Search feature insights
        snippet_count = len([m for m in metrics if m.featured_snippet])
        if snippet_count == 0:
            insights.append("No featured snippets captured - opportunity for optimization")
        elif snippet_count > 3:
            insights.append("Good featured snippet presence - maintain and expand")
            
        # Traffic insights
        total_traffic = sum([m.estimated_traffic for m in metrics])
        if total_traffic < 1000:
            insights.append("Low estimated traffic - consider expanding keyword portfolio")
        elif total_traffic > 10000:
            insights.append("Strong traffic potential from search visibility")
            
        # Ranking insights
        top_10_count = len([m for m in metrics if m.ranking_position <= 10])
        if top_10_count / len(metrics) < 0.3:
            insights.append("Less than 30% of keywords in top 10 - focus on ranking improvements")
            
        return insights

# Export main classes
__all__ = [
    'SearchVisibilityTracker',
    'VisibilityMetrics',
    'VisibilityAlert',
    'CompetitorVisibility',
    'SearchEngine',
    'VisibilityStatus',
    'SearchFeature'
]