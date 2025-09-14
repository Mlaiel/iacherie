"""
Competitive Analytics Engine
===========================

Advanced competitive analysis and benchmarking for Ainflue Distribution Platform.
Provides insights on competitor strategies, performance, and market positioning.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

class CompetitorTier(Enum):
    """Competitor tier classification"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    ASPIRATIONAL = "aspirational"
    EMERGING = "emerging"

class AnalysisMetric(Enum):
    """Analysis metrics to track"""
    ENGAGEMENT_RATE = "engagement_rate"
    POSTING_FREQUENCY = "posting_frequency"
    CONTENT_QUALITY = "content_quality"
    AUDIENCE_GROWTH = "audience_growth"
    REACH_ESTIMATE = "reach_estimate"
    HASHTAG_PERFORMANCE = "hashtag_performance"
    TIMING_STRATEGY = "timing_strategy"

class PlatformType(Enum):
    """Platform types for analysis"""
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    BLOG_PLATFORM = "blog_platform"
    STREAMING_PLATFORM = "streaming_platform"
    ECOMMERCE_PLATFORM = "ecommerce_platform"

@dataclass
class Competitor:
    """Competitor profile"""
    competitor_id: str
    name: str
    platforms: Dict[str, str]  # platform -> handle/username
    tier: str = "direct"
    industry: str = ""
    size_category: str = "medium"  # small, medium, large, enterprise
    location: str = ""
    last_analyzed: Optional[datetime] = None
    is_active: bool = True

@dataclass
class CompetitorMetrics:
    """Competitor performance metrics"""
    competitor_id: str
    platform: str
    date_analyzed: datetime
    followers_count: int
    following_count: int
    posts_count: int
    engagement_rate: float
    avg_likes: float
    avg_comments: float
    avg_shares: float
    posting_frequency: float  # posts per day
    content_quality_score: float
    reach_estimate: int
    growth_rate: float  # percentage

@dataclass
class ContentAnalysis:
    """Analysis of competitor content"""
    competitor_id: str
    platform: str
    content_id: str
    content_type: str
    publish_time: datetime
    engagement_metrics: Dict[str, int]
    hashtags: List[str]
    mentions: List[str]
    content_themes: List[str]
    performance_score: float

@dataclass
class CompetitiveBenchmark:
    """Competitive benchmark results"""
    metric: str
    your_value: float
    competitor_avg: float
    competitor_median: float
    competitor_best: float
    your_ranking: int
    total_competitors: int
    percentile: float
    gap_analysis: str

class CompetitiveAnalytics:
    """
    Advanced Competitive Analytics Engine
    
    Provides comprehensive competitive analysis including:
    - Competitor identification and tracking
    - Performance benchmarking
    - Content strategy analysis
    - Market positioning insights
    - Trend identification
    """
    
    def __init__(self) -> None:
        """Initialize competitive analytics engine"""
        self.competitors: Dict[str, Competitor] = {}
        self.metrics_history: Dict[str, List[CompetitorMetrics]] = defaultdict(list)
        self.content_analysis: Dict[str, List[ContentAnalysis]] = defaultdict(list)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def add_competitor(self, competitor: Competitor) -> bool:
        """
        Add a new competitor to track
        
        Args:
            competitor: Competitor profile
            
        Returns:
            bool: Success status
        """
        try:
            # Validate competitor data
            if not competitor.competitor_id or not competitor.name:
                logger.error("Competitor ID and name are required")
                return False
            
            if not competitor.platforms:
                logger.error("At least one platform must be specified")
                return False
            
            # Store competitor
            self.competitors[competitor.competitor_id] = competitor
            
            # Initialize metrics tracking
            if competitor.competitor_id not in self.metrics_history:
                self.metrics_history[competitor.competitor_id] = []
            
            logger.info(f"Added competitor: {competitor.name} ({competitor.competitor_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding competitor: {str(e)}")
            return False
    
    async def analyze_competitor(self, competitor_id: str) -> Optional[Dict[str, CompetitorMetrics]]:
        """
        Analyze a specific competitor across all their platforms
        
        Args:
            competitor_id: Competitor ID to analyze
            
        Returns:
            Optional[Dict[str, CompetitorMetrics]]: Metrics by platform
        """
        try:
            if competitor_id not in self.competitors:
                logger.error(f"Competitor not found: {competitor_id}")
                return None
            
            competitor = self.competitors[competitor_id]
            platform_metrics = {}
            
            for platform, handle in competitor.platforms.items():
                metrics = await self._analyze_platform_performance(
                    competitor_id, platform, handle
                )
                if metrics:
                    platform_metrics[platform] = metrics
                    self.metrics_history[competitor_id].append(metrics)
            
            # Update last analyzed timestamp
            competitor.last_analyzed = datetime.now()
            
            logger.info(f"Analyzed competitor {competitor.name} across {len(platform_metrics)} platforms")
            return platform_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing competitor: {str(e)}")
            return None
    
    async def _analyze_platform_performance(self, competitor_id: str, platform: str, 
                                          handle: str) -> Optional[CompetitorMetrics]:
        """
        Analyze competitor performance on a specific platform
        
        Args:
            competitor_id: Competitor ID
            platform: Platform name
            handle: Platform handle/username
            
        Returns:
            Optional[CompetitorMetrics]: Platform metrics
        """
        try:
            # This would integrate with actual platform APIs or scraping tools
            # For demonstration, we'll simulate the analysis
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Generate simulated metrics (in real implementation, fetch from APIs)
            metrics = CompetitorMetrics(
                competitor_id=competitor_id,
                platform=platform,
                date_analyzed=datetime.now(),
                followers_count=self._simulate_followers_count(platform),
                following_count=self._simulate_following_count(platform),
                posts_count=self._simulate_posts_count(platform),
                engagement_rate=self._simulate_engagement_rate(platform),
                avg_likes=self._simulate_avg_likes(platform),
                avg_comments=self._simulate_avg_comments(platform),
                avg_shares=self._simulate_avg_shares(platform),
                posting_frequency=self._simulate_posting_frequency(platform),
                content_quality_score=self._simulate_content_quality(platform),
                reach_estimate=self._simulate_reach_estimate(platform),
                growth_rate=self._simulate_growth_rate(platform)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing platform {platform}: {str(e)}")
            return None
    
    def _simulate_followers_count(self, platform: str) -> int:
        """Simulate followers count (replace with real API integration)"""
        base_counts = {
            "instagram": (1000, 1000000),
            "twitter": (500, 500000),
            "tiktok": (2000, 2000000),
            "youtube": (100, 100000),
            "linkedin": (300, 50000),
            "facebook": (800, 800000)
        }
        min_count, max_count = base_counts.get(platform, (1000, 100000))
        return np.random.randint(min_count, max_count)
    
    def _simulate_following_count(self, platform: str) -> int:
        """Simulate following count"""
        return np.random.randint(50, 5000)
    
    def _simulate_posts_count(self, platform: str) -> int:
        """Simulate posts count"""
        return np.random.randint(100, 10000)
    
    def _simulate_engagement_rate(self, platform: str) -> float:
        """Simulate engagement rate"""
        base_rates = {
            "instagram": (0.01, 0.08),
            "twitter": (0.005, 0.03),
            "tiktok": (0.03, 0.15),
            "youtube": (0.02, 0.06),
            "linkedin": (0.01, 0.05),
            "facebook": (0.005, 0.04)
        }
        min_rate, max_rate = base_rates.get(platform, (0.01, 0.05))
        return round(np.random.uniform(min_rate, max_rate), 4)
    
    def _simulate_avg_likes(self, platform: str) -> float:
        """Simulate average likes"""
        return round(np.random.uniform(10, 1000), 1)
    
    def _simulate_avg_comments(self, platform: str) -> float:
        """Simulate average comments"""
        return round(np.random.uniform(2, 100), 1)
    
    def _simulate_avg_shares(self, platform: str) -> float:
        """Simulate average shares"""
        return round(np.random.uniform(1, 50), 1)
    
    def _simulate_posting_frequency(self, platform: str) -> float:
        """Simulate posting frequency (posts per day)"""
        frequencies = {
            "instagram": (0.5, 3.0),
            "twitter": (2.0, 15.0),
            "tiktok": (0.3, 2.0),
            "youtube": (0.1, 1.0),
            "linkedin": (0.2, 1.0),
            "facebook": (0.3, 2.0)
        }
        min_freq, max_freq = frequencies.get(platform, (0.5, 3.0))
        return round(np.random.uniform(min_freq, max_freq), 2)
    
    def _simulate_content_quality(self, platform: str) -> float:
        """Simulate content quality score (0-10)"""
        return round(np.random.uniform(3.0, 9.0), 2)
    
    def _simulate_reach_estimate(self, platform: str) -> int:
        """Simulate estimated reach"""
        return np.random.randint(1000, 100000)
    
    def _simulate_growth_rate(self, platform: str) -> float:
        """Simulate growth rate percentage"""
        return round(np.random.uniform(-5.0, 25.0), 2)
    
    async def analyze_all_competitors(self) -> Dict[str, Dict[str, CompetitorMetrics]]:
        """
        Analyze all tracked competitors
        
        Returns:
            Dict[str, Dict[str, CompetitorMetrics]]: Results by competitor and platform
        """
        try:
            all_results = {}
            
            # Use semaphore to limit concurrent analyses
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent analyses
            
            async def analyze_with_semaphore(competitor_id) -> None:
                async with semaphore:
                    return await self.analyze_competitor(competitor_id)
            
            # Analyze all competitors concurrently
            tasks = [
                analyze_with_semaphore(competitor_id)
                for competitor_id in self.competitors.keys()
                if self.competitors[competitor_id].is_active
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, (competitor_id, result) in enumerate(zip(self.competitors.keys(), results)):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing {competitor_id}: {result}")
                elif result:
                    all_results[competitor_id] = result
            
            logger.info(f"Analyzed {len(all_results)} competitors successfully")
            return all_results
            
        except Exception as e:
            logger.error(f"Error analyzing all competitors: {str(e)}")
            return {}
    
    async def generate_competitive_benchmarks(self, your_metrics: Dict[str, CompetitorMetrics]) -> List[CompetitiveBenchmark]:
        """
        Generate competitive benchmarks comparing your performance to competitors
        
        Args:
            your_metrics: Your own metrics by platform
            
        Returns:
            List[CompetitiveBenchmark]: Benchmark results
        """
        try:
            benchmarks = []
            
            # Get all competitor metrics for comparison
            competitor_results = await self.analyze_all_competitors()
            
            for platform in your_metrics.keys():
                your_platform_metrics = your_metrics[platform]
                
                # Collect competitor metrics for this platform
                competitor_platform_metrics = []
                for comp_results in competitor_results.values():
                    if platform in comp_results:
                        competitor_platform_metrics.append(comp_results[platform])
                
                if not competitor_platform_metrics:
                    continue
                
                # Generate benchmarks for key metrics
                metrics_to_benchmark = [
                    ("engagement_rate", "engagement_rate"),
                    ("posting_frequency", "posting_frequency"),
                    ("content_quality_score", "content_quality_score"),
                    ("growth_rate", "growth_rate"),
                    ("followers_count", "followers_count")
                ]
                
                for metric_name, metric_attr in metrics_to_benchmark:
                    benchmark = self._create_benchmark(
                        metric_name,
                        platform,
                        getattr(your_platform_metrics, metric_attr),
                        competitor_platform_metrics,
                        metric_attr
                    )
                    benchmarks.append(benchmark)
            
            logger.info(f"Generated {len(benchmarks)} competitive benchmarks")
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error generating benchmarks: {str(e)}")
            return []
    
    def _create_benchmark(self, metric_name: str, platform: str, your_value: float,
                         competitor_metrics: List[CompetitorMetrics], 
                         metric_attr: str) -> CompetitiveBenchmark:
        """Create a single competitive benchmark"""
        
        # Extract competitor values
        competitor_values = [getattr(metric, metric_attr) for metric in competitor_metrics]
        
        # Calculate statistics
        competitor_avg = np.mean(competitor_values)
        competitor_median = np.median(competitor_values)
        competitor_best = max(competitor_values)
        
        # Calculate ranking
        all_values = competitor_values + [your_value]
        all_values.sort(reverse=True)  # Higher is better for most metrics
        your_ranking = all_values.index(your_value) + 1
        total_competitors = len(competitor_values) + 1
        
        # Calculate percentile
        percentile = ((total_competitors - your_ranking) / total_competitors) * 100
        
        # Generate gap analysis
        gap_analysis = self._generate_gap_analysis(
            your_value, competitor_avg, competitor_best, percentile
        )
        
        return CompetitiveBenchmark(
            metric=f"{platform}_{metric_name}",
            your_value=your_value,
            competitor_avg=competitor_avg,
            competitor_median=competitor_median,
            competitor_best=competitor_best,
            your_ranking=your_ranking,
            total_competitors=total_competitors,
            percentile=percentile,
            gap_analysis=gap_analysis
        )
    
    def _generate_gap_analysis(self, your_value: float, competitor_avg: float,
                              competitor_best: float, percentile: float) -> str:
        """Generate gap analysis text"""
        
        if percentile >= 80:
            return "Excellent performance - Leading the competition"
        elif percentile >= 60:
            return "Above average performance - Competitive position"
        elif percentile >= 40:
            return "Average performance - Room for improvement"
        elif percentile >= 20:
            return "Below average performance - Significant improvement needed"
        else:
            return "Poor performance - Urgent attention required"
    
    async def identify_content_opportunities(self, competitor_id: str, 
                                           days_back: int = 30) -> Dict[str, Any]:
        """
        Identify content opportunities based on competitor analysis
        
        Args:
            competitor_id: Competitor to analyze
            days_back: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Content opportunities and insights
        """
        try:
            if competitor_id not in self.competitors:
                logger.error(f"Competitor not found: {competitor_id}")
                return {}
            
            # Analyze competitor's recent content (simulated)
            opportunities = {
                "high_performing_themes": [],
                "optimal_posting_times": {},
                "trending_hashtags": [],
                "content_gaps": [],
                "engagement_patterns": {},
                "recommended_strategies": []
            }
            
            # Simulate content analysis
            competitor = self.competitors[competitor_id]
            
            # High-performing content themes (simulated)
            themes = ["tutorial", "behind_the_scenes", "user_generated", "trending", "educational"]
            opportunities["high_performing_themes"] = np.random.choice(themes, 3, replace=False).tolist()
            
            # Optimal posting times by platform
            for platform in competitor.platforms.keys():
                times = ["09:00", "12:00", "15:00", "18:00", "21:00"]
                opportunities["optimal_posting_times"][platform] = np.random.choice(times, 2, replace=False).tolist()
            
            # Trending hashtags (simulated)
            hashtag_base = ["marketing", "business", "growth", "success", "tips"]
            opportunities["trending_hashtags"] = [f"#{tag}" for tag in np.random.choice(hashtag_base, 3, replace=False)]
            
            # Content gaps (opportunities not being exploited)
            gap_types = ["video_content", "interactive_posts", "live_streaming", "community_engagement"]
            opportunities["content_gaps"] = np.random.choice(gap_types, 2, replace=False).tolist()
            
            # Engagement patterns
            opportunities["engagement_patterns"] = {
                "best_day": np.random.choice(["Monday", "Wednesday", "Friday"]),
                "best_time": np.random.choice(["9AM", "2PM", "6PM"]),
                "avg_engagement_rate": round(np.random.uniform(0.02, 0.08), 4)
            }
            
            # Recommended strategies
            strategies = [
                "Increase video content frequency",
                "Engage more with audience comments",
                "Use trending hashtags strategically",
                "Post during peak engagement hours",
                "Create more interactive content"
            ]
            opportunities["recommended_strategies"] = np.random.choice(strategies, 3, replace=False).tolist()
            
            logger.info(f"Identified content opportunities for competitor: {competitor.name}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying content opportunities: {str(e)}")
            return {}
    
    async def track_competitor_growth(self, competitor_id: str, period_days: int = 90) -> Dict[str, Any]:
        """
        Track competitor growth trends over time
        
        Args:
            competitor_id: Competitor to track
            period_days: Period to analyze
            
        Returns:
            Dict[str, Any]: Growth trends and insights
        """
        try:
            if competitor_id not in self.competitors:
                logger.error(f"Competitor not found: {competitor_id}")
                return {}
            
            competitor = self.competitors[competitor_id]
            growth_data = {
                "competitor_name": competitor.name,
                "analysis_period": f"{period_days} days",
                "platform_growth": {},
                "overall_trends": {},
                "growth_insights": []
            }
            
            # Analyze growth for each platform
            for platform in competitor.platforms.keys():
                # Simulate historical data points
                dates = []
                followers = []
                engagement_rates = []
                
                current_date = datetime.now()
                base_followers = self._simulate_followers_count(platform)
                base_engagement = self._simulate_engagement_rate(platform)
                
                for i in range(period_days, 0, -7):  # Weekly data points
                    date = current_date - timedelta(days=i)
                    dates.append(date.isoformat())
                    
                    # Simulate growth/decline
                    growth_factor = 1 + np.random.uniform(-0.02, 0.05)  # -2% to +5% weekly
                    followers_count = int(base_followers * (growth_factor ** (period_days - i) / 7))
                    followers.append(followers_count)
                    
                    # Simulate engagement changes
                    engagement_factor = 1 + np.random.uniform(-0.1, 0.1)  # -10% to +10%
                    engagement_rate = base_engagement * engagement_factor
                    engagement_rates.append(round(engagement_rate, 4))
                
                platform_growth = {
                    "dates": dates,
                    "followers_history": followers,
                    "engagement_history": engagement_rates,
                    "total_growth_percent": round(((followers[-1] - followers[0]) / followers[0]) * 100, 2),
                    "avg_weekly_growth": round(np.mean(np.diff(followers)) / np.mean(followers[:-1]) * 100, 2),
                    "engagement_trend": "increasing" if engagement_rates[-1] > engagement_rates[0] else "decreasing"
                }
                
                growth_data["platform_growth"][platform] = platform_growth
            
            # Overall trends
            all_growth_rates = [data["total_growth_percent"] for data in growth_data["platform_growth"].values()]
            growth_data["overall_trends"] = {
                "avg_growth_rate": round(np.mean(all_growth_rates), 2),
                "best_performing_platform": max(growth_data["platform_growth"].keys(), 
                                              key=lambda p: growth_data["platform_growth"][p]["total_growth_percent"]),
                "growth_consistency": "high" if np.std(all_growth_rates) < 5 else "low"
            }
            
            # Growth insights
            insights = []
            if growth_data["overall_trends"]["avg_growth_rate"] > 10:
                insights.append("Competitor showing strong overall growth")
            elif growth_data["overall_trends"]["avg_growth_rate"] < -5:
                insights.append("Competitor experiencing decline")
            
            if growth_data["overall_trends"]["growth_consistency"] == "high":
                insights.append("Consistent growth across platforms")
            else:
                insights.append("Inconsistent growth - some platforms performing better")
            
            growth_data["growth_insights"] = insights
            
            logger.info(f"Tracked growth for competitor: {competitor.name}")
            return growth_data
            
        except Exception as e:
            logger.error(f"Error tracking competitor growth: {str(e)}")
            return {}
    
    async def generate_market_intelligence_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive market intelligence report
        
        Returns:
            Dict[str, Any]: Market intelligence insights
        """
        try:
            report = {
                "report_date": datetime.now().isoformat(),
                "market_overview": {},
                "competitive_landscape": {},
                "platform_insights": {},
                "trends_and_opportunities": {},
                "strategic_recommendations": []
            }
            
            # Market overview
            active_competitors = [c for c in self.competitors.values() if c.is_active]
            report["market_overview"] = {
                "total_competitors_tracked": len(active_competitors),
                "market_segments": list(set(c.industry for c in active_competitors if c.industry)),
                "geographic_coverage": list(set(c.location for c in active_competitors if c.location)),
                "size_distribution": self._analyze_size_distribution(active_competitors)
            }
            
            # Competitive landscape
            all_metrics = await self.analyze_all_competitors()
            report["competitive_landscape"] = self._analyze_competitive_landscape(all_metrics)
            
            # Platform insights
            report["platform_insights"] = self._generate_platform_insights(all_metrics)
            
            # Trends and opportunities
            report["trends_and_opportunities"] = await self._identify_market_trends(all_metrics)
            
            # Strategic recommendations
            report["strategic_recommendations"] = self._generate_strategic_recommendations(report)
            
            logger.info("Generated comprehensive market intelligence report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating market intelligence report: {str(e)}")
            return {}
    
    def _analyze_size_distribution(self, competitors: List[Competitor]) -> Dict[str, int]:
        """Analyze competitor size distribution"""
        size_counts = defaultdict(int)
        for competitor in competitors:
            size_counts[competitor.size_category] += 1
        return dict(size_counts)
    
    def _analyze_competitive_landscape(self, all_metrics: Dict[str, Dict[str, CompetitorMetrics]]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        landscape = {
            "market_leaders": [],
            "emerging_competitors": [],
            "declining_competitors": [],
            "engagement_benchmarks": {},
            "posting_frequency_benchmarks": {}
        }
        
        # Collect all engagement rates and posting frequencies
        all_engagement_rates = []
        all_posting_frequencies = []
        competitor_scores = {}
        
        for comp_id, platforms in all_metrics.items():
            total_engagement = 0
            total_frequency = 0
            platform_count = 0
            
            for platform, metrics in platforms.items():
                all_engagement_rates.append(metrics.engagement_rate)
                all_posting_frequencies.append(metrics.posting_frequency)
                total_engagement += metrics.engagement_rate
                total_frequency += metrics.posting_frequency
                platform_count += 1
            
            if platform_count > 0:
                avg_engagement = total_engagement / platform_count
                avg_frequency = total_frequency / platform_count
                competitor_scores[comp_id] = {
                    "avg_engagement": avg_engagement,
                    "avg_frequency": avg_frequency,
                    "score": avg_engagement * 100 + avg_frequency  # Simple scoring
                }
        
        # Identify leaders, emerging, and declining
        if competitor_scores:
            sorted_competitors = sorted(competitor_scores.items(), 
                                      key=lambda x: x[1]["score"], reverse=True)
            
            total_competitors = len(sorted_competitors)
            leaders_count = max(1, total_competitors // 4)
            
            landscape["market_leaders"] = [comp_id for comp_id, _ in sorted_competitors[:leaders_count]]
            landscape["emerging_competitors"] = [comp_id for comp_id, _ in sorted_competitors[leaders_count:]]
            
            # Benchmarks
            if all_engagement_rates:
                landscape["engagement_benchmarks"] = {
                    "average": round(np.mean(all_engagement_rates), 4),
                    "median": round(np.median(all_engagement_rates), 4),
                    "top_quartile": round(np.percentile(all_engagement_rates, 75), 4)
                }
            
            if all_posting_frequencies:
                landscape["posting_frequency_benchmarks"] = {
                    "average": round(np.mean(all_posting_frequencies), 2),
                    "median": round(np.median(all_posting_frequencies), 2),
                    "top_quartile": round(np.percentile(all_posting_frequencies, 75), 2)
                }
        
        return landscape
    
    def _generate_platform_insights(self, all_metrics: Dict[str, Dict[str, CompetitorMetrics]]) -> Dict[str, Any]:
        """Generate platform-specific insights"""
        platform_data = defaultdict(list)
        
        # Collect data by platform
        for platforms in all_metrics.values():
            for platform, metrics in platforms.items():
                platform_data[platform].append(metrics)
        
        insights = {}
        for platform, metrics_list in platform_data.items():
            if not metrics_list:
                continue
                
            engagement_rates = [m.engagement_rate for m in metrics_list]
            posting_frequencies = [m.posting_frequency for m in metrics_list]
            growth_rates = [m.growth_rate for m in metrics_list]
            
            insights[platform] = {
                "competitor_count": len(metrics_list),
                "avg_engagement_rate": round(np.mean(engagement_rates), 4),
                "avg_posting_frequency": round(np.mean(posting_frequencies), 2),
                "avg_growth_rate": round(np.mean(growth_rates), 2),
                "engagement_leader": max(metrics_list, key=lambda m: m.engagement_rate).competitor_id,
                "most_active": max(metrics_list, key=lambda m: m.posting_frequency).competitor_id,
                "fastest_growing": max(metrics_list, key=lambda m: m.growth_rate).competitor_id
            }
        
        return insights
    
    async def _identify_market_trends(self, all_metrics: Dict[str, Dict[str, CompetitorMetrics]]) -> Dict[str, Any]:
        """Identify market trends and opportunities"""
        trends = {
            "content_trends": [],
            "timing_trends": [],
            "engagement_trends": [],
            "growth_opportunities": [],
            "market_gaps": []
        }
        
        # Simulated trend identification (in real implementation, use historical data)
        content_trends = [
            "Increased video content adoption",
            "Rise in user-generated content campaigns",
            "More interactive and poll-based content",
            "Growing emphasis on authentic storytelling"
        ]
        
        timing_trends = [
            "Shift towards evening posting times",
            "Increased weekend activity",
            "More frequent but shorter content"
        ]
        
        engagement_trends = [
            "Higher engagement on video content",
            "Increased comment-to-like ratios",
            "Growing importance of story features"
        ]
        
        trends["content_trends"] = np.random.choice(content_trends, 2, replace=False).tolist()
        trends["timing_trends"] = np.random.choice(timing_trends, 2, replace=False).tolist()
        trends["engagement_trends"] = np.random.choice(engagement_trends, 2, replace=False).tolist()
        
        # Growth opportunities (simulated)
        opportunities = [
            "Underutilized platform: TikTok",
            "Content gap: Educational tutorials",
            "Timing opportunity: Early morning posts",
            "Engagement opportunity: Live streaming"
        ]
        trends["growth_opportunities"] = np.random.choice(opportunities, 2, replace=False).tolist()
        
        return trends
    
    def _generate_strategic_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # Based on competitive landscape
        if "market_leaders" in report.get("competitive_landscape", {}):
            leaders = report["competitive_landscape"]["market_leaders"]
            if leaders:
                recommendations.append(f"Study and benchmark against market leader: {leaders[0]}")
        
        # Based on platform insights
        platform_insights = report.get("platform_insights", {})
        if platform_insights:
            best_platform = max(platform_insights.keys(), 
                              key=lambda p: platform_insights[p]["avg_engagement_rate"])
            recommendations.append(f"Focus content efforts on {best_platform} for highest engagement")
        
        # Based on trends
        trends = report.get("trends_and_opportunities", {})
        if trends.get("growth_opportunities"):
            recommendations.append(f"Explore opportunity: {trends['growth_opportunities'][0]}")
        
        # General recommendations
        recommendations.extend([
            "Increase posting frequency during peak engagement hours",
            "Invest in video content creation capabilities",
            "Develop more interactive content formats",
            "Monitor competitor strategies monthly for adaptation"
        ])
        
        return recommendations

# Usage example
async def main() -> None:
    """Example usage of CompetitiveAnalytics"""
    async with CompetitiveAnalytics() as analytics:
        
        # Add competitors
        competitor1 = Competitor(
            competitor_id="comp_001",
            name="Competitor A",
            platforms={"instagram": "@competitora", "twitter": "@competitora"},
            tier="direct",
            industry="marketing",
            size_category="medium"
        )
        
        await analytics.add_competitor(competitor1)
        
        # Analyze competitor
        results = await analytics.analyze_competitor("comp_001")
        print(f"Analysis results: {results}")
        
        # Generate market intelligence report
        report = await analytics.generate_market_intelligence_report()
        print(f"Market intelligence report generated with {len(report)} sections")

if __name__ == "__main__":
    asyncio.run(main())