"""
Revenue Benchmarker - Competitive analysis and industry benchmarking system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  STRICT COPYRIGHT WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.


REVENUE BENCHMARKER SYSTEM - ENTERPRISE EDITION


Developed by Expert Team:
 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Revenue Forecasting & Optimization Algorithms
  DBA: Advanced Data Management & Analytics
 Security Expert: Enterprise-Grade Security & Encryption
 Microservices: Scalable Distributed Architecture
 Audio Expert: Audio Revenue Stream Optimization
  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Decision Making
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import statistics
import uuid

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


class BenchmarkCategory(Enum):
    """Benchmark categories"""
    PLATFORM_REVENUE = "platform_revenue"
    CONTENT_TYPE = "content_type"
    GEOGRAPHIC = "geographic"
    DEMOGRAPHIC = "demographic"
    INDUSTRY_VERTICAL = "industry_vertical"
    CONTENT_SIZE = "content_size"
    ENGAGEMENT_LEVEL = "engagement_level"
    CREATOR_TIER = "creator_tier"


class BenchmarkMetric(Enum):
    """Benchmark metrics"""
    REVENUE_PER_STREAM = "revenue_per_stream"
    REVENUE_PER_VIEW = "revenue_per_view"
    REVENUE_PER_FOLLOWER = "revenue_per_follower"
    MONTHLY_RECURRING_REVENUE = "monthly_recurring_revenue"
    AVERAGE_REVENUE_PER_USER = "average_revenue_per_user"
    CONVERSION_RATE = "conversion_rate"
    ENGAGEMENT_RATE = "engagement_rate"
    RETENTION_RATE = "retention_rate"
    GROWTH_RATE = "growth_rate"
    PROFIT_MARGIN = "profit_margin"


class CompetitorTier(Enum):
    """Competitor tiers"""
    DIRECT_COMPETITOR = "direct_competitor"
    INDIRECT_COMPETITOR = "indirect_competitor"
    ASPIRATIONAL_TARGET = "aspirational_target"
    MARKET_LEADER = "market_leader"
    EMERGING_PLAYER = "emerging_player"
    NICHE_SPECIALIST = "niche_specialist"


@dataclass
class BenchmarkData:
    """Benchmark data point"""
    data_id: str
    category: BenchmarkCategory
    metric: BenchmarkMetric
    value: Decimal
    unit: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 1.0
    
    @property
    def age_days(self) -> int:
        """Get age of benchmark data in days"""



        return (datetime.utcnow() - self.timestamp).days


@dataclass
class CompetitorProfile:
    """Competitor profile"""
    competitor_id: str
    name: str
    tier: CompetitorTier
    platforms: List[str]
    content_types: List[str]
    follower_count: int
    engagement_metrics: Dict[str, float]
    revenue_estimates: Dict[str, Decimal]
    strengths: List[str]
    weaknesses: List[str]
    last_updated: datetime


@dataclass
class BenchmarkMetrics:
    """Benchmark analysis metrics"""
    metric: BenchmarkMetric
    category: BenchmarkCategory
    percentile_25: Decimal
    percentile_50: Decimal
    percentile_75: Decimal
    percentile_90: Decimal
    mean: Decimal
    std_dev: Decimal
    min_value: Decimal
    max_value: Decimal
    sample_size: int
    confidence_interval: Tuple[Decimal, Decimal]
    
    @property
    def performance_range(self) -> Decimal:
        """Get performance range (75th - 25th percentile)"""



        return self.percentile_75 - self.percentile_25


@dataclass
class CompetitorAnalysis:
    """Competitor analysis results"""
    user_position: Dict[str, Any]
    competitor_rankings: List[Dict[str, Any]]
    market_gaps: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    threats: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_date: datetime


class RevenueBenchmarker:
    """Advanced revenue benchmarking and competitive analysis system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.benchmark_data = []
        self.competitors = {}
        self.market_clusters = {}
        self.scaler = StandardScaler()
        
    async def initialize(self) -> None:
        """Initialize benchmarker"""



        try:
            # Load benchmark data sources
            await self._load_benchmark_data()
            
            # Load competitor profiles
            await self._load_competitor_profiles()
            
            # Initialize market clustering
            await self._initialize_market_clustering()
            
            logger.info("Revenue benchmarker initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing benchmarker: {e}")
            raise
    
    async def _load_benchmark_data(self) -> None:
        """Load benchmark data from various sources"""
        # In production, load from multiple data sources:
        # - Industry reports
        # - Public APIs
        # - Partner data exchanges
        # - Market research platforms
        
        # Sample benchmark data for demonstration
        sample_data = [
            BenchmarkData(
                data_id=str(uuid.uuid4()),
                category=BenchmarkCategory.PLATFORM_REVENUE,
                metric=BenchmarkMetric.REVENUE_PER_STREAM,
                value=Decimal('0.003'),
                unit="EUR",
                source="Spotify Industry Report 2025",
                timestamp=datetime.utcnow() - timedelta(days=30),
                metadata={"platform": "spotify", "region": "EU"}
            ),
            BenchmarkData(
                data_id=str(uuid.uuid4()),
                category=BenchmarkCategory.PLATFORM_REVENUE,
                metric=BenchmarkMetric.REVENUE_PER_VIEW,
                value=Decimal('0.002'),
                unit="EUR",
                source="YouTube Creator Analytics",
                timestamp=datetime.utcnow() - timedelta(days=15),
                metadata={"platform": "youtube", "region": "EU"}
            )
        ]
        
        self.benchmark_data.extend(sample_data)
    
    async def _load_competitor_profiles(self) -> None:
        """Load competitor profiles"""
        # Sample competitor data
        sample_competitor = CompetitorProfile(
            competitor_id=str(uuid.uuid4()),
            name="Sample Creator",
            tier=CompetitorTier.DIRECT_COMPETITOR,
            platforms=["spotify", "youtube", "instagram"],
            content_types=["music", "video", "image"],
            follower_count=50000,
            engagement_metrics={
                "engagement_rate": 3.5,
                "monthly_growth": 2.1,
                "retention_rate": 85.0
            },
            revenue_estimates={
                "monthly_revenue": Decimal('5000'),
                "revenue_per_follower": Decimal('0.10')
            },
            strengths=["High engagement", "Consistent content"],
            weaknesses=["Limited platform diversity"],
            last_updated=datetime.utcnow()
        )
        
        self.competitors[sample_competitor.competitor_id] = sample_competitor
    
    async def _initialize_market_clustering(self) -> None:
        """Initialize market clustering for segmentation"""
        if not self.benchmark_data:
            return
        
        # Prepare data for clustering
        features = []
        for data in self.benchmark_data:
            features.append([
                float(data.value),
                data.age_days,
                data.confidence_score
            ])
        
        if len(features) >= 3:  # Minimum for clustering
            features_array = np.array(features)
            scaled_features = self.scaler.fit_transform(features_array)
            
            # Determine optimal number of clusters
            optimal_k = self._find_optimal_clusters(scaled_features)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_features)
            
            # Store cluster information
            for i, data in enumerate(self.benchmark_data):
                data.metadata['cluster'] = int(cluster_labels[i])
            
            self.market_clusters = {
                'model': kmeans,
                'scaler': self.scaler,
                'n_clusters': optimal_k
            }
    
    def _find_optimal_clusters(self, data: np.ndarray, max_k: int = 10) -> int:
        """Find optimal number of clusters using elbow method and silhouette score"""
        if len(data) < 2:
            return 1
        
        max_k = min(max_k, len(data) - 1)
        silhouette_scores = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(data)
            silhouette_avg = silhouette_score(data, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        # Return k with highest silhouette score
        optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
        return optimal_k
    
    async def generate_benchmark_metrics(
        self,
        category: BenchmarkCategory,
        metric: BenchmarkMetric,
        filters: Optional[Dict[str, Any]] = None
    ) -> BenchmarkMetrics:
        """Generate benchmark metrics for specific category and metric"""



        try:
            # Filter benchmark data
            filtered_data = self._filter_benchmark_data(category, metric, filters)
            
            if not filtered_data:
                raise ValueError(f"No benchmark data found for {category.value} - {metric.value}")
            
            # Extract values
            values = [float(data.value) for data in filtered_data]
            values_decimal = [data.value for data in filtered_data]
            
            # Calculate statistics
            percentiles = np.percentile(values, [25, 50, 75, 90])
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            # Calculate confidence interval (95%)
            if len(values) > 1:
                sem = stats.sem(values)
                confidence_interval = stats.t.interval(
                    0.95, len(values) - 1, loc=mean_val, scale=sem
                )
            else:
                confidence_interval = (mean_val, mean_val)
            
            benchmark_metrics = BenchmarkMetrics(
                metric=metric,
                category=category,
                percentile_25=Decimal(str(percentiles[0])),
                percentile_50=Decimal(str(percentiles[1])),
                percentile_75=Decimal(str(percentiles[2])),
                percentile_90=Decimal(str(percentiles[3])),
                mean=Decimal(str(mean_val)),
                std_dev=Decimal(str(std_dev)),
                min_value=min(values_decimal),
                max_value=max(values_decimal),
                sample_size=len(values),
                confidence_interval=(
                    Decimal(str(confidence_interval[0])),
                    Decimal(str(confidence_interval[1]))
                )
            )
            
            return benchmark_metrics
            
        except Exception as e:
            logger.error(f"Error generating benchmark metrics: {e}")
            raise
    
    def _filter_benchmark_data(
        self,
        category: BenchmarkCategory,
        metric: BenchmarkMetric,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[BenchmarkData]:
        """Filter benchmark data based on criteria"""
        filtered = [
            data for data in self.benchmark_data
            if data.category == category and data.metric == metric
        ]
        
        if filters:
            # Apply additional filters
            if 'max_age_days' in filters:
                max_age = filters['max_age_days']
                filtered = [data for data in filtered if data.age_days <= max_age]
            
            if 'min_confidence' in filters:
                min_conf = filters['min_confidence']
                filtered = [data for data in filtered if data.confidence_score >= min_conf]
            
            if 'platform' in filters:
                platform = filters['platform']
                filtered = [
                    data for data in filtered
                    if data.metadata.get('platform') == platform
                ]
            
            if 'region' in filters:
                region = filters['region']
                filtered = [
                    data for data in filtered
                    if data.metadata.get('region') == region
                ]
        
        return filtered
    
    async def benchmark_user_performance(
        self,
        user_metrics: Dict[str, Any],
        categories: List[BenchmarkCategory],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Benchmark user performance against market data"""



        try:
            results = {}
            
            for category in categories:
                category_results = {}
                
                # Check each relevant metric for this category
                relevant_metrics = self._get_relevant_metrics_for_category(category)
                
                for metric in relevant_metrics:
                    metric_key = metric.value
                    
                    if metric_key in user_metrics:
                        user_value = Decimal(str(user_metrics[metric_key]))
                        
                        # Get benchmark metrics
                        benchmark = await self.generate_benchmark_metrics(
                            category, metric, filters
                        )
                        
                        # Calculate user's percentile position
                        percentile_position = self._calculate_percentile_position(
                            user_value, benchmark
                        )
                        
                        # Determine performance tier
                        performance_tier = self._determine_performance_tier(percentile_position)
                        
                        category_results[metric_key] = {
                            'user_value': str(user_value),
                            'benchmark_median': str(benchmark.percentile_50),
                            'benchmark_mean': str(benchmark.mean),
                            'percentile_position': percentile_position,
                            'performance_tier': performance_tier,
                            'vs_median': str(user_value - benchmark.percentile_50),
                            'vs_mean': str(user_value - benchmark.mean),
                            'improvement_potential': str(benchmark.percentile_90 - user_value),
                            'sample_size': benchmark.sample_size
                        }
                
                results[category.value] = category_results
            
            # Generate overall assessment
            results['overall_assessment'] = await self._generate_overall_assessment(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error benchmarking user performance: {e}")
            raise
    
    def _get_relevant_metrics_for_category(self, category: BenchmarkCategory) -> List[BenchmarkMetric]:
        """Get relevant metrics for a benchmark category"""
        category_metrics = {
            BenchmarkCategory.PLATFORM_REVENUE: [
                BenchmarkMetric.REVENUE_PER_STREAM,
                BenchmarkMetric.REVENUE_PER_VIEW,
                BenchmarkMetric.MONTHLY_RECURRING_REVENUE
            ],
            BenchmarkCategory.CONTENT_TYPE: [
                BenchmarkMetric.REVENUE_PER_STREAM,
                BenchmarkMetric.ENGAGEMENT_RATE,
                BenchmarkMetric.CONVERSION_RATE
            ],
            BenchmarkCategory.CREATOR_TIER: [
                BenchmarkMetric.REVENUE_PER_FOLLOWER,
                BenchmarkMetric.AVERAGE_REVENUE_PER_USER,
                BenchmarkMetric.GROWTH_RATE
            ]
        }
        
        return category_metrics.get(category, list(BenchmarkMetric))
    
    def _calculate_percentile_position(self, user_value: Decimal, benchmark: BenchmarkMetrics) -> float:
        """Calculate user's percentile position in benchmark distribution"""
        # Simple percentile calculation based on quartiles
        if user_value <= benchmark.percentile_25:
            return 25.0 * float(user_value / benchmark.percentile_25)
        elif user_value <= benchmark.percentile_50:
            return 25.0 + 25.0 * float((user_value - benchmark.percentile_25) / (benchmark.percentile_50 - benchmark.percentile_25))
        elif user_value <= benchmark.percentile_75:
            return 50.0 + 25.0 * float((user_value - benchmark.percentile_50) / (benchmark.percentile_75 - benchmark.percentile_50))
        elif user_value <= benchmark.percentile_90:
            return 75.0 + 15.0 * float((user_value - benchmark.percentile_75) / (benchmark.percentile_90 - benchmark.percentile_75))
        else:
            return min(100.0, 90.0 + 10.0 * float((user_value - benchmark.percentile_90) / benchmark.percentile_90))
    
    def _determine_performance_tier(self, percentile_position: float) -> str:
        """Determine performance tier based on percentile position"""
        if percentile_position >= 90:
            return "Exceptional"
        elif percentile_position >= 75:
            return "Above Average"
        elif percentile_position >= 50:
            return "Average"
        elif percentile_position >= 25:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    async def _generate_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall performance assessment"""



        try:
            all_percentiles = []
            category_assessments = {}
            
            for category, metrics in results.items():
                if category == 'overall_assessment':
                    continue
                
                category_percentiles = []
                for metric, data in metrics.items():
                    percentile = data['percentile_position']
                    all_percentiles.append(percentile)
                    category_percentiles.append(percentile)
                
                if category_percentiles:
                    avg_percentile = statistics.mean(category_percentiles)
                    category_assessments[category] = {
                        'average_percentile': avg_percentile,
                        'tier': self._determine_performance_tier(avg_percentile),
                        'metric_count': len(category_percentiles)
                    }
            
            if all_percentiles:
                overall_percentile = statistics.mean(all_percentiles)
                overall_tier = self._determine_performance_tier(overall_percentile)
            else:
                overall_percentile = 0
                overall_tier = "No Data"
            
            return {
                'overall_percentile': overall_percentile,
                'overall_tier': overall_tier,
                'category_assessments': category_assessments,
                'strong_categories': [
                    cat for cat, data in category_assessments.items()
                    if data['average_percentile'] >= 75
                ],
                'improvement_categories': [
                    cat for cat, data in category_assessments.items()
                    if data['average_percentile'] < 50
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating overall assessment: {e}")
            return {}
    
    async def analyze_competitors(
        self,
        user_profile: Dict[str, Any],
        competitor_tiers: Optional[List[CompetitorTier]] = None
    ) -> CompetitorAnalysis:
        """Analyze competitive landscape and positioning"""



        try:
            competitor_tiers = competitor_tiers or [
                CompetitorTier.DIRECT_COMPETITOR,
                CompetitorTier.MARKET_LEADER
            ]
            
            # Filter relevant competitors
            relevant_competitors = [
                comp for comp in self.competitors.values()
                if comp.tier in competitor_tiers
            ]
            
            # Analyze user position vs competitors
            user_position = await self._analyze_user_position(user_profile, relevant_competitors)
            
            # Rank competitors
            competitor_rankings = await self._rank_competitors(relevant_competitors)
            
            # Identify market gaps and opportunities
            market_gaps = await self._identify_market_gaps(user_profile, relevant_competitors)
            opportunities = await self._identify_opportunities(user_profile, relevant_competitors)
            threats = await self._identify_threats(user_profile, relevant_competitors)
            
            # Generate recommendations
            recommendations = await self._generate_competitive_recommendations(
                user_position, competitor_rankings, market_gaps, opportunities, threats
            )
            
            analysis = CompetitorAnalysis(
                user_position=user_position,
                competitor_rankings=competitor_rankings,
                market_gaps=market_gaps,
                opportunities=opportunities,
                threats=threats,
                recommendations=recommendations,
                analysis_date=datetime.utcnow()
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {e}")
            raise
    
    async def _analyze_user_position(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> Dict[str, Any]:
        """Analyze user's competitive position"""
        user_followers = user_profile.get('follower_count', 0)
        user_revenue = Decimal(str(user_profile.get('monthly_revenue', 0)))
        user_engagement = user_profile.get('engagement_rate', 0)
        
        # Compare against competitors
        competitor_followers = [comp.follower_count for comp in competitors]
        competitor_revenues = [comp.revenue_estimates.get('monthly_revenue', Decimal('0')) for comp in competitors]
        competitor_engagements = [comp.engagement_metrics.get('engagement_rate', 0) for comp in competitors]
        
        # Calculate rankings
        follower_rank = sum(1 for f in competitor_followers if f < user_followers) + 1
        revenue_rank = sum(1 for r in competitor_revenues if r < user_revenue) + 1
        engagement_rank = sum(1 for e in competitor_engagements if e < user_engagement) + 1
        
        total_competitors = len(competitors) + 1  # +1 for user
        
        return {
            'follower_count': user_followers,
            'follower_rank': follower_rank,
            'follower_percentile': (total_competitors - follower_rank) / total_competitors * 100,
            'monthly_revenue': str(user_revenue),
            'revenue_rank': revenue_rank,
            'revenue_percentile': (total_competitors - revenue_rank) / total_competitors * 100,
            'engagement_rate': user_engagement,
            'engagement_rank': engagement_rank,
            'engagement_percentile': (total_competitors - engagement_rank) / total_competitors * 100,
            'overall_rank': (follower_rank + revenue_rank + engagement_rank) / 3,
            'total_competitors_analyzed': len(competitors)
        }
    
    async def _rank_competitors(self, competitors: List[CompetitorProfile]) -> List[Dict[str, Any]]:
        """Rank competitors by multiple criteria"""
        ranked_competitors = []
        
        for comp in competitors:
            # Calculate composite score
            follower_score = min(comp.follower_count / 100000, 1.0)  # Normalize to max 100k
            revenue_score = min(float(comp.revenue_estimates.get('monthly_revenue', Decimal('0'))) / 10000, 1.0)
            engagement_score = min(comp.engagement_metrics.get('engagement_rate', 0) / 10, 1.0)
            
            composite_score = (follower_score * 0.3 + revenue_score * 0.4 + engagement_score * 0.3)
            
            ranked_competitors.append({
                'competitor_id': comp.competitor_id,
                'name': comp.name,
                'tier': comp.tier.value,
                'composite_score': composite_score,
                'follower_count': comp.follower_count,
                'monthly_revenue': str(comp.revenue_estimates.get('monthly_revenue', Decimal('0'))),
                'engagement_rate': comp.engagement_metrics.get('engagement_rate', 0),
                'strengths': comp.strengths,
                'weaknesses': comp.weaknesses,
                'platforms': comp.platforms
            })
        
        # Sort by composite score
        ranked_competitors.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Add rank numbers
        for i, comp in enumerate(ranked_competitors):
            comp['rank'] = i + 1
        
        return ranked_competitors
    
    async def _identify_market_gaps(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[Dict[str, Any]]:
        """Identify market gaps and underserved segments"""
        gaps = []
        
        # Platform gap analysis
        user_platforms = set(user_profile.get('platforms', []))
        competitor_platforms = set()
        for comp in competitors:
            competitor_platforms.update(comp.platforms)
        
        missing_platforms = competitor_platforms - user_platforms
        if missing_platforms:
            gaps.append({
                'type': 'platform_gap',
                'description': f"Underutilized platforms: {', '.join(missing_platforms)}",
                'priority': 'medium',
                'potential_impact': 'Expand audience reach and revenue streams'
            })
        
        # Content type gap analysis
        user_content_types = set(user_profile.get('content_types', []))
        competitor_content_types = set()
        for comp in competitors:
            competitor_content_types.update(comp.content_types)
        
        missing_content_types = competitor_content_types - user_content_types
        if missing_content_types:
            gaps.append({
                'type': 'content_gap',
                'description': f"Unexplored content types: {', '.join(missing_content_types)}",
                'priority': 'low',
                'potential_impact': 'Diversify content portfolio and audience'
            })
        
        # Revenue model gaps
        user_revenue = Decimal(str(user_profile.get('monthly_revenue', 0)))
        avg_competitor_revenue = statistics.mean([
            float(comp.revenue_estimates.get('monthly_revenue', Decimal('0')))
            for comp in competitors
        ])
        
        if user_revenue < Decimal(str(avg_competitor_revenue * 0.8)):
            gaps.append({
                'type': 'revenue_gap',
                'description': f"Revenue below competitor average by {avg_competitor_revenue - float(user_revenue):.0f} EUR/month",
                'priority': 'high',
                'potential_impact': 'Significant revenue increase opportunity'
            })
        
        return gaps
    
    async def _identify_opportunities(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[Dict[str, Any]]:
        """Identify growth opportunities"""
        opportunities = []
        
        # High-performing competitor strategies
        top_performers = [comp for comp in competitors if comp.tier == CompetitorTier.MARKET_LEADER]
        
        for performer in top_performers:
            common_strengths = set(performer.strengths)
            user_strengths = set(user_profile.get('strengths', []))
            
            potential_strengths = common_strengths - user_strengths
            if potential_strengths:
                opportunities.append({
                    'type': 'strategy_opportunity',
                    'source': performer.name,
                    'description': f"Adopt successful strategies: {', '.join(potential_strengths)}",
                    'priority': 'high',
                    'expected_impact': 'Significant performance improvement'
                })
        
        # Underperforming competitor weaknesses
        weak_competitors = [
            comp for comp in competitors
            if comp.revenue_estimates.get('monthly_revenue', Decimal('0')) < Decimal(str(user_profile.get('monthly_revenue', 0)))
        ]
        
        if weak_competitors:
            opportunities.append({
                'type': 'market_share_opportunity',
                'description': f"Capture market share from {len(weak_competitors)} underperforming competitors",
                'priority': 'medium',
                'expected_impact': 'Market position strengthening'
            })
        
        return opportunities
    
    async def _identify_threats(
        self,
        user_profile: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> List[Dict[str, Any]]:
        """Identify competitive threats"""
        threats = []
        
        # Fast-growing competitors
        fast_growers = [
            comp for comp in competitors
            if comp.engagement_metrics.get('monthly_growth', 0) > 5.0  # 5% monthly growth
        ]
        
        for grower in fast_growers:
            threats.append({
                'type': 'growth_threat',
                'source': grower.name,
                'description': f"Fast-growing competitor with {grower.engagement_metrics.get('monthly_growth', 0)}% monthly growth",
                'severity': 'medium',
                'mitigation': 'Accelerate own growth initiatives'
            })
        
        # Market leaders with similar positioning
        user_platforms = set(user_profile.get('platforms', []))
        
        similar_leaders = [
            comp for comp in competitors
            if (comp.tier == CompetitorTier.MARKET_LEADER and
                len(set(comp.platforms) & user_platforms) >= 2)
        ]
        
        for leader in similar_leaders:
            threats.append({
                'type': 'market_leader_threat',
                'source': leader.name,
                'description': f"Market leader with overlapping platform presence: {', '.join(set(leader.platforms) & user_platforms)}",
                'severity': 'high',
                'mitigation': 'Differentiate positioning and strengthen unique value proposition'
            })
        
        return threats
    
    async def _generate_competitive_recommendations(
        self,
        user_position: Dict[str, Any],
        competitor_rankings: List[Dict[str, Any]],
        market_gaps: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []
        
        # Position-based recommendations
        if user_position['revenue_percentile'] < 50:
            recommendations.append("Focus on revenue optimization - currently below median performance")
        
        if user_position['engagement_percentile'] < 25:
            recommendations.append("Prioritize engagement improvement - critical performance gap identified")
        
        # Gap-based recommendations
        high_priority_gaps = [gap for gap in market_gaps if gap['priority'] == 'high']
        for gap in high_priority_gaps:
            recommendations.append(f"Address {gap['type']}: {gap['description']}")
        
        # Opportunity-based recommendations
        high_impact_opportunities = [opp for opp in opportunities if opp['priority'] == 'high']
        for opp in high_impact_opportunities[:3]:  # Top 3 opportunities
            recommendations.append(f"Pursue opportunity: {opp['description']}")
        
        # Threat-based recommendations
        high_severity_threats = [threat for threat in threats if threat['severity'] == 'high']
        for threat in high_severity_threats:
            recommendations.append(f"Mitigate threat: {threat['mitigation']}")
        
        # Top performer insights
        if competitor_rankings:
            top_performer = competitor_rankings[0]
            recommendations.append(f"Study top performer {top_performer['name']} - focus on their strengths: {', '.join(top_performer['strengths'][:2])}")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def export_benchmark_report(
        self,
        user_profile: Dict[str, Any],
        categories: List[BenchmarkCategory]
    ) -> Dict[str, Any]:
        """Export comprehensive benchmark report"""



        try:
            # Generate benchmark analysis
            benchmark_results = await self.benchmark_user_performance(
                user_profile, categories
            )
            
            # Generate competitive analysis
            competitive_analysis = await self.analyze_competitors(user_profile)
            
            # Compile report
            report = {
                'report_info': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'user_profile': user_profile,
                    'categories_analyzed': [cat.value for cat in categories]
                },
                'benchmark_analysis': benchmark_results,
                'competitive_analysis': {
                    'user_position': competitive_analysis.user_position,
                    'competitor_rankings': competitive_analysis.competitor_rankings,
                    'market_gaps': competitive_analysis.market_gaps,
                    'opportunities': competitive_analysis.opportunities,
                    'threats': competitive_analysis.threats,
                    'recommendations': competitive_analysis.recommendations
                },
                'key_insights': await self._generate_key_insights(
                    benchmark_results, competitive_analysis
                ),
                'action_plan': await self._generate_action_plan(
                    benchmark_results, competitive_analysis
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting benchmark report: {e}")
            raise
    
    async def _generate_key_insights(
        self,
        benchmark_results: Dict[str, Any],
        competitive_analysis: CompetitorAnalysis
    ) -> List[str]:
        """Generate key insights from analysis"""
        insights = []
        
        # Benchmark insights
        overall_assessment = benchmark_results.get('overall_assessment', {})
        overall_tier = overall_assessment.get('overall_tier', 'Unknown')
        
        insights.append(f"Overall performance tier: {overall_tier}")
        
        strong_categories = overall_assessment.get('strong_categories', [])
        if strong_categories:
            insights.append(f"Strong performance in: {', '.join(strong_categories)}")
        
        improvement_categories = overall_assessment.get('improvement_categories', [])
        if improvement_categories:
            insights.append(f"Improvement needed in: {', '.join(improvement_categories)}")
        
        # Competitive insights
        user_position = competitive_analysis.user_position
        total_competitors = user_position.get('total_competitors_analyzed', 0)
        overall_rank = user_position.get('overall_rank', 0)
        
        if total_competitors > 0:
            insights.append(f"Ranked #{overall_rank:.1f} out of {total_competitors + 1} competitors analyzed")
        
        # Market gap insights
        high_priority_gaps = [
            gap for gap in competitive_analysis.market_gaps
            if gap['priority'] == 'high'
        ]
        
        if high_priority_gaps:
            insights.append(f"{len(high_priority_gaps)} high-priority market gaps identified")
        
        return insights
    
    async def _generate_action_plan(
        self,
        benchmark_results: Dict[str, Any],
        competitive_analysis: CompetitorAnalysis
    ) -> List[Dict[str, Any]]:
        """Generate actionable plan based on analysis"""
        action_plan = []
        
        # Priority actions from competitive recommendations
        recommendations = competitive_analysis.recommendations[:5]  # Top 5
        
        for i, recommendation in enumerate(recommendations):
            action_plan.append({
                'priority': i + 1,
                'action': recommendation,
                'category': 'competitive_improvement',
                'timeline': '1-3 months',
                'expected_impact': 'high' if i < 2 else 'medium'
            })
        
        # Benchmark improvement actions
        overall_assessment = benchmark_results.get('overall_assessment', {})
        improvement_categories = overall_assessment.get('improvement_categories', [])
        
        for category in improvement_categories[:3]:  # Top 3 categories
            action_plan.append({
                'priority': len(action_plan) + 1,
                'action': f"Improve performance in {category} category",
                'category': 'benchmark_improvement',
                'timeline': '2-4 months',
                'expected_impact': 'medium'
            })
        
        # Market gap actions
        high_priority_gaps = [
            gap for gap in competitive_analysis.market_gaps
            if gap['priority'] == 'high'
        ][:2]  # Top 2 gaps
        
        for gap in high_priority_gaps:
            action_plan.append({
                'priority': len(action_plan) + 1,
                'action': f"Address {gap['type']}: {gap['description']}",
                'category': 'market_expansion',
                'timeline': '3-6 months',
                'expected_impact': gap.get('potential_impact', 'medium')
            })
        
        return action_plan[:10]  # Limit to top 10 actions


async def create_benchmarker(config: Optional[Dict[str, Any]] = None) -> RevenueBenchmarker:
    """Factory function to create and initialize revenue benchmarker"""
    benchmarker = RevenueBenchmarker(config)
    await benchmarker.initialize()
    return benchmarker
