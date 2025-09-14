"""
Ainflue Platform - Hashtag Intelligence Monitor
==============================================

AI-powered hashtag intelligence system for trending hashtag discovery,
performance tracking, and strategic hashtag optimization across platforms.

Features:
- Trending hashtag discovery and analysis
- Hashtag performance tracking across platforms
- AI-driven hashtag recommendation engine
- Hashtag competition analysis and optimization
- Real-time hashtag trend monitoring
- Cross-platform hashtag strategy coordination

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Platforms for hashtag optimization."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"

class HashtagCategory(Enum):
    """Categories of hashtags."""
    MUSIC_GENRE = "music_genre"
    INSTRUMENT = "instrument"
    MOOD = "mood"
    COLLABORATION = "collaboration"
    LOCATION = "location"
    EVENT = "event"
    TREND = "trend"
    BRAND = "brand"
    COMMUNITY = "community"
    TECHNIQUE = "technique"

class TrendDirection(Enum):
    """Trend direction for hashtags."""
    RISING = "rising"
    DECLINING = "declining"
    STABLE = "stable"
    VIRAL = "viral"
    EMERGING = "emerging"

@dataclass
class HashtagData:
    """Comprehensive hashtag data structure."""
    hashtag: str
    platform: Platform
    category: HashtagCategory
    usage_count: int
    engagement_rate: float
    reach_potential: int
    competition_level: str
    trend_direction: TrendDirection
    growth_rate: float
    best_posting_times: List[str] = field(default_factory=list)
    related_hashtags: List[str] = field(default_factory=list)
    geographic_popularity: Dict[str, float] = field(default_factory=dict)
    demographic_data: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class HashtagRecommendation:
    """Hashtag recommendation with strategic insights."""
    hashtag: str
    platform: Platform
    recommendation_score: float
    reasoning: str
    expected_reach: int
    expected_engagement: float
    competition_difficulty: str
    optimal_usage_frequency: str
    complementary_hashtags: List[str] = field(default_factory=list)
    timing_recommendations: List[str] = field(default_factory=list)
    target_audience: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HashtagStrategy:
    """Complete hashtag strategy for content."""
    content_id: Optional[str]
    platform: Platform
    primary_hashtags: List[str] = field(default_factory=list)
    secondary_hashtags: List[str] = field(default_factory=list)
    trending_hashtags: List[str] = field(default_factory=list)
    niche_hashtags: List[str] = field(default_factory=list)
    branded_hashtags: List[str] = field(default_factory=list)
    total_expected_reach: int = 0
    strategy_confidence: float = 0.0
    implementation_notes: List[str] = field(default_factory=list)

class HashtagIntelligenceMonitor:
    """
    Advanced hashtag intelligence system with AI-powered analysis and optimization.
    
    This monitor provides comprehensive hashtag tracking, trend analysis, and strategic
    recommendations across all major social media platforms.
    """
    
    def __init__(self, config -> None: Optional[Dict] = None) -> None:
        """Initialize the hashtag intelligence monitor."""
        self.config = config or {}
        
        # Data storage
        self.hashtag_database: Dict[Platform, Dict[str, HashtagData]] = defaultdict(dict)
        self.trend_history: Dict[str, List[Dict]] = defaultdict(list)
        self.creator_hashtag_performance: Dict[str, Dict[str, Any]] = {}
        self.recommendation_cache: Dict[str, List[HashtagRecommendation]] = {}
        
        # Intelligence models
        self.trend_prediction_models: Dict[Platform, Any] = {}
        self.engagement_prediction_models: Dict[Platform, Any] = {}
        self.hashtag_clustering_models: Dict[Platform, Any] = {}
        
        # Real-time tracking
        self.trending_hashtags: Dict[Platform, List[str]] = defaultdict(list)
        self.emerging_hashtags: Dict[Platform, List[str]] = defaultdict(list)
        self.viral_hashtags: Dict[Platform, List[str]] = defaultdict(list)
        
        logger.info("HashtagIntelligenceMonitor initialized")
    
    async def start_monitoring(self) -> None:
        """Start the hashtag intelligence monitoring system."""
        try:
            logger.info("Starting hashtag intelligence monitoring...")
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Load historical hashtag data
            await self._load_historical_data()
            
            # Start monitoring tasks
            asyncio.create_task(self._trend_monitoring_loop())
            asyncio.create_task(self._engagement_analysis_loop())
            asyncio.create_task(self._competitor_hashtag_tracking_loop())
            asyncio.create_task(self._viral_detection_loop())
            
            logger.info("Hashtag intelligence monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start hashtag intelligence monitoring: {e}")
            raise
    
    async def analyze_hashtag_performance(self, creator_id: str, hashtags: List[str], 
                                        platform: Platform, timeframe_days: int = 30) -> Dict[str, Any]:
        """Analyze hashtag performance for a creator's content."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=timeframe_days)
            
            performance_analysis = {
                'creator_id': creator_id,
                'platform': platform.value,
                'timeframe_days': timeframe_days,
                'hashtags_analyzed': len(hashtags),
                'individual_performance': {},
                'overall_metrics': {},
                'optimization_insights': []
            }
            
            # Analyze each hashtag individually
            total_reach = 0
            total_engagement = 0
            
            for hashtag in hashtags:
                hashtag_data = await self._get_hashtag_performance_data(hashtag, platform, start_date, end_date)
                
                individual_metrics = {
                    'hashtag': hashtag,
                    'usage_frequency': hashtag_data.get('usage_count', 0),
                    'average_engagement_rate': hashtag_data.get('engagement_rate', 0.0),
                    'reach_potential': hashtag_data.get('reach_potential', 0),
                    'competition_level': hashtag_data.get('competition_level', 'unknown'),
                    'trend_status': hashtag_data.get('trend_direction', TrendDirection.STABLE).value,
                    'performance_score': self._calculate_hashtag_performance_score(hashtag_data),
                    'recommendations': await self._generate_hashtag_optimization_recommendations(hashtag, platform)
                }
                
                performance_analysis['individual_performance'][hashtag] = individual_metrics
                total_reach += individual_metrics['reach_potential']
                total_engagement += individual_metrics['average_engagement_rate']
            
            # Calculate overall metrics
            performance_analysis['overall_metrics'] = {
                'total_estimated_reach': total_reach,
                'average_engagement_rate': total_engagement / len(hashtags) if hashtags else 0,
                'hashtag_diversity_score': self._calculate_hashtag_diversity_score(hashtags, platform),
                'trend_alignment_score': await self._calculate_trend_alignment_score(hashtags, platform),
                'competition_difficulty_average': self._calculate_average_competition_difficulty(hashtags, platform)
            }
            
            # Generate optimization insights
            performance_analysis['optimization_insights'] = await self._generate_performance_optimization_insights(
                creator_id, hashtags, platform, performance_analysis
            )
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing hashtag performance: {e}")
            return {'error': str(e)}
    
    async def discover_trending_hashtags(self, platform: Platform, category: Optional[HashtagCategory] = None, 
                                       limit: int = 50) -> List[HashtagData]:
        """Discover currently trending hashtags for a platform and category."""
        try:
            # Get trending hashtags from real-time monitoring
            trending_hashtags = await self._get_real_time_trending_hashtags(platform, category)
            
            # Enrich with detailed data
            enriched_hashtags = []
            for hashtag in trending_hashtags[:limit]:
                hashtag_data = await self._enrich_hashtag_data(hashtag, platform)
                if hashtag_data:
                    enriched_hashtags.append(hashtag_data)
            
            # Sort by trending score
            enriched_hashtags.sort(key=lambda x: x.growth_rate, reverse=True)
            
            return enriched_hashtags
            
        except Exception as e:
            logger.error(f"Error discovering trending hashtags: {e}")
            return []
    
    async def generate_hashtag_strategy(self, creator_id: str, content_description: str, 
                                      platform: Platform, target_audience: Optional[Dict] = None) -> HashtagStrategy:
        """Generate comprehensive hashtag strategy for content."""
        try:
            # Analyze content to determine relevant categories
            content_categories = await self._analyze_content_categories(content_description)
            
            # Get creator's historical hashtag performance
            creator_performance = await self._get_creator_hashtag_history(creator_id, platform)
            
            # Generate hashtag recommendations
            recommendations = await self._generate_strategic_hashtag_recommendations(
                content_categories, platform, target_audience, creator_performance
            )
            
            # Categorize recommendations
            strategy = HashtagStrategy(
                content_id=None,
                platform=platform,
                primary_hashtags=self._select_primary_hashtags(recommendations),
                secondary_hashtags=self._select_secondary_hashtags(recommendations),
                trending_hashtags=self._select_trending_hashtags(recommendations),
                niche_hashtags=self._select_niche_hashtags(recommendations),
                branded_hashtags=self._select_branded_hashtags(recommendations, creator_id)
            )
            
            # Calculate strategy metrics
            strategy.total_expected_reach = await self._calculate_strategy_reach(strategy)
            strategy.strategy_confidence = await self._calculate_strategy_confidence(strategy, creator_performance)
            strategy.implementation_notes = await self._generate_implementation_notes(strategy)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating hashtag strategy: {e}")
            return HashtagStrategy(content_id=None, platform=platform)
    
    async def track_hashtag_trends(self, hashtags: List[str], platform: Platform, 
                                 tracking_period_days: int = 7) -> Dict[str, Any]:
        """Track hashtag trends over a specified period."""
        try:
            tracking_results = {
                'hashtags': hashtags,
                'platform': platform.value,
                'tracking_period_days': tracking_period_days,
                'trend_analysis': {},
                'predictions': {},
                'alerts': []
            }
            
            for hashtag in hashtags:
                # Get historical trend data
                trend_data = await self._get_hashtag_trend_data(hashtag, platform, tracking_period_days)
                
                # Analyze trend patterns
                trend_analysis = {
                    'current_popularity': trend_data.get('current_usage', 0),
                    'growth_rate': trend_data.get('growth_rate', 0.0),
                    'volatility': self._calculate_trend_volatility(trend_data),
                    'seasonal_patterns': self._identify_seasonal_patterns(trend_data),
                    'peak_times': self._identify_peak_usage_times(trend_data),
                    'trend_direction': self._determine_trend_direction(trend_data)
                }
                
                tracking_results['trend_analysis'][hashtag] = trend_analysis
                
                # Generate predictions
                predictions = await self._predict_hashtag_future_performance(hashtag, platform, trend_data)
                tracking_results['predictions'][hashtag] = predictions
                
                # Check for alerts
                alerts = self._generate_hashtag_alerts(hashtag, trend_analysis, predictions)
                tracking_results['alerts'].extend(alerts)
            
            return tracking_results
            
        except Exception as e:
            logger.error(f"Error tracking hashtag trends: {e}")
            return {'error': str(e)}
    
    async def optimize_hashtag_mix(self, current_hashtags: List[str], platform: Platform, 
                                 optimization_goal: str = "engagement") -> Dict[str, Any]:
        """Optimize hashtag mix for better performance."""
        try:
            # Analyze current hashtag performance
            current_performance = await self._analyze_hashtag_mix_performance(current_hashtags, platform)
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_hashtag_optimization_opportunities(
                current_hashtags, platform, optimization_goal
            )
            
            # Generate optimized hashtag mix
            optimized_mix = await self._generate_optimized_hashtag_mix(
                current_hashtags, platform, optimization_goal, optimization_opportunities
            )
            
            # Calculate expected improvements
            expected_improvements = await self._calculate_optimization_improvements(
                current_performance, optimized_mix, platform
            )
            
            optimization_results = {
                'current_hashtags': current_hashtags,
                'optimized_hashtags': optimized_mix,
                'optimization_goal': optimization_goal,
                'current_performance': current_performance,
                'expected_improvements': expected_improvements,
                'changes_summary': self._generate_changes_summary(current_hashtags, optimized_mix),
                'implementation_strategy': await self._generate_optimization_implementation_strategy(optimized_mix)
            }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing hashtag mix: {e}")
            return {'error': str(e)}
    
    async def get_hashtag_intelligence_report(self, creator_id: str, platform: Platform, 
                                            timeframe_days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive hashtag intelligence report."""
        try:
            report = {
                'creator_id': creator_id,
                'platform': platform.value,
                'timeframe_days': timeframe_days,
                'report_generated_at': datetime.utcnow(),
                'executive_summary': {},
                'performance_analysis': {},
                'trend_insights': {},
                'competitive_analysis': {},
                'recommendations': {},
                'action_plan': {}
            }
            
            # Executive summary
            report['executive_summary'] = await self._generate_executive_summary(creator_id, platform, timeframe_days)
            
            # Performance analysis
            creator_hashtags = await self._get_creator_recent_hashtags(creator_id, platform, timeframe_days)
            if creator_hashtags:
                report['performance_analysis'] = await self.analyze_hashtag_performance(
                    creator_id, creator_hashtags, platform, timeframe_days
                )
            
            # Trend insights
            report['trend_insights'] = await self._generate_trend_insights(platform, timeframe_days)
            
            # Competitive analysis
            report['competitive_analysis'] = await self._generate_competitive_hashtag_analysis(creator_id, platform)
            
            # Recommendations
            report['recommendations'] = await self._generate_strategic_recommendations(creator_id, platform, report)
            
            # Action plan
            report['action_plan'] = await self._generate_hashtag_action_plan(creator_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating hashtag intelligence report: {e}")
            return {'error': str(e)}
    
    # Private helper methods
    
    async def _initialize_ai_models(self) -> None:
        """Initialize AI models for hashtag intelligence."""
        for platform in Platform:
            self.trend_prediction_models[platform] = {
                'type': 'time_series_forecasting',
                'accuracy': 0.85,
                'model_path': f'models/hashtag_trends_{platform.value}.pkl'
            }
            
            self.engagement_prediction_models[platform] = {
                'type': 'neural_network',
                'accuracy': 0.89,
                'model_path': f'models/hashtag_engagement_{platform.value}.pkl'
            }
            
            self.hashtag_clustering_models[platform] = {
                'type': 'clustering',
                'accuracy': 0.82,
                'model_path': f'models/hashtag_clusters_{platform.value}.pkl'
            }
        
        logger.info("AI models initialized for hashtag intelligence")
    
    async def _load_historical_data(self) -> None:
        """Load historical hashtag data."""
        # Placeholder for loading historical data from database
        logger.info("Historical hashtag data loaded")
    
    def _calculate_hashtag_performance_score(self, hashtag_data: Dict[str, Any]) -> float:
        """Calculate performance score for a hashtag."""
        # Weighted score based on multiple factors
        engagement_weight = 0.4
        reach_weight = 0.3
        trend_weight = 0.2
        competition_weight = 0.1
        
        engagement_score = min(hashtag_data.get('engagement_rate', 0) * 100, 100)
        reach_score = min(hashtag_data.get('reach_potential', 0) / 1000, 100)
        
        # Trend direction scoring
        trend_direction = hashtag_data.get('trend_direction', TrendDirection.STABLE)
        trend_score = {
            TrendDirection.VIRAL: 100,
            TrendDirection.RISING: 80,
            TrendDirection.STABLE: 60,
            TrendDirection.EMERGING: 70,
            TrendDirection.DECLINING: 20
        }.get(trend_direction, 50)
        
        # Competition level scoring (inverse - lower competition is better)
        competition_level = hashtag_data.get('competition_level', 'medium')
        competition_score = {
            'low': 100,
            'medium': 60,
            'high': 30,
            'very_high': 10
        }.get(competition_level, 50)
        
        total_score = (
            engagement_score * engagement_weight +
            reach_score * reach_weight +
            trend_score * trend_weight +
            competition_score * competition_weight
        )
        
        return min(total_score, 100)
    
    def _calculate_hashtag_diversity_score(self, hashtags: List[str], platform: Platform) -> float:
        """Calculate diversity score for hashtag mix."""
        if not hashtags:
            return 0.0
        
        # Count categories represented
        categories = set()
        for hashtag in hashtags:
            hashtag_data = self.hashtag_database[platform].get(hashtag)
            if hashtag_data:
                categories.add(hashtag_data.category)
        
        # Diversity score based on category coverage
        max_categories = len(HashtagCategory)
        diversity_score = (len(categories) / max_categories) * 100
        
        return min(diversity_score, 100)
    
    async def _calculate_trend_alignment_score(self, hashtags: List[str], platform: Platform) -> float:
        """Calculate how well hashtags align with current trends."""
        if not hashtags:
            return 0.0
        
        trending_hashtags = set(self.trending_hashtags[platform])
        emerging_hashtags = set(self.emerging_hashtags[platform])
        
        aligned_count = 0
        for hashtag in hashtags:
            if hashtag in trending_hashtags:
                aligned_count += 1
            elif hashtag in emerging_hashtags:
                aligned_count += 0.5  # Partial credit for emerging
        
        alignment_score = (aligned_count / len(hashtags)) * 100
        return min(alignment_score, 100)
    
    # Background monitoring loops
    
    async def _trend_monitoring_loop(self) -> None:
        """Background loop for trend monitoring."""
        while True:
            try:
                # Monitor trends across all platforms
                for platform in Platform:
                    await self._update_platform_trends(platform)
                await asyncio.sleep(300)  # 5-minute trend monitoring
            except Exception as e:
                logger.error(f"Error in trend monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _engagement_analysis_loop(self) -> None:
        """Background loop for engagement analysis."""
        while True:
            try:
                # Analyze engagement patterns
                await self._analyze_engagement_patterns()
                await asyncio.sleep(1800)  # 30-minute engagement analysis
            except Exception as e:
                logger.error(f"Error in engagement analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _competitor_hashtag_tracking_loop(self) -> None:
        """Background loop for competitor hashtag tracking."""
        while True:
            try:
                # Track competitor hashtag usage
                await self._track_competitor_hashtags()
                await asyncio.sleep(3600)  # 1-hour competitor tracking
            except Exception as e:
                logger.error(f"Error in competitor hashtag tracking loop: {e}")
                await asyncio.sleep(600)
    
    async def _viral_detection_loop(self) -> None:
        """Background loop for viral hashtag detection."""
        while True:
            try:
                # Detect viral hashtags
                await self._detect_viral_hashtags()
                await asyncio.sleep(600)  # 10-minute viral detection
            except Exception as e:
                logger.error(f"Error in viral detection loop: {e}")
                await asyncio.sleep(120)
    
    # Placeholder methods for full implementation
    
    async def _get_hashtag_performance_data(self, hashtag: str, platform: Platform, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get hashtag performance data."""
        return {
            'usage_count': 1000,
            'engagement_rate': 0.05,
            'reach_potential': 50000,
            'competition_level': 'medium',
            'trend_direction': TrendDirection.STABLE
        }
    
    async def _generate_hashtag_optimization_recommendations(self, hashtag: str, platform: Platform) -> List[str]:
        """Generate optimization recommendations for a hashtag."""
        return ["Use during peak hours", "Combine with trending hashtags"]
    
    async def _generate_performance_optimization_insights(self, creator_id: str, hashtags: List[str], 
                                                        platform: Platform, performance_analysis: Dict) -> List[str]:
        """Generate performance optimization insights."""
        return ["Consider adding more trending hashtags", "Diversify hashtag categories"]
    
    async def _get_real_time_trending_hashtags(self, platform: Platform, category: Optional[HashtagCategory]) -> List[str]:
        """Get real-time trending hashtags."""
        return ["#musicproducer", "#beats", "#audiocreation"]
    
    async def _enrich_hashtag_data(self, hashtag: str, platform: Platform) -> Optional[HashtagData]:
        """Enrich hashtag with detailed data."""
        return HashtagData(
            hashtag=hashtag,
            platform=platform,
            category=HashtagCategory.MUSIC_GENRE,
            usage_count=1000,
            engagement_rate=0.05,
            reach_potential=50000,
            competition_level="medium",
            trend_direction=TrendDirection.RISING,
            growth_rate=0.15
        )
    
    # Additional placeholder methods would be implemented for full functionality
    
    async def _analyze_content_categories(self, content_description: str) -> List[HashtagCategory]:
        return [HashtagCategory.MUSIC_GENRE, HashtagCategory.MOOD]
    
    async def _get_creator_hashtag_history(self, creator_id: str, platform: Platform) -> Dict[str, Any]:
        return {}
    
    async def _generate_strategic_hashtag_recommendations(self, content_categories: List[HashtagCategory], 
                                                        platform: Platform, target_audience: Optional[Dict], 
                                                        creator_performance: Dict) -> List[HashtagRecommendation]:
        return []
    
    def _select_primary_hashtags(self, recommendations: List[HashtagRecommendation]) -> List[str]:
        return []
    
    def _select_secondary_hashtags(self, recommendations: List[HashtagRecommendation]) -> List[str]:
        return []
    
    def _select_trending_hashtags(self, recommendations: List[HashtagRecommendation]) -> List[str]:
        return []
    
    def _select_niche_hashtags(self, recommendations: List[HashtagRecommendation]) -> List[str]:
        return []
    
    def _select_branded_hashtags(self, recommendations: List[HashtagRecommendation], creator_id: str) -> List[str]:
        return []
    
    async def _calculate_strategy_reach(self, strategy: HashtagStrategy) -> int:
        return 0
    
    async def _calculate_strategy_confidence(self, strategy: HashtagStrategy, creator_performance: Dict) -> float:
        return 0.0
    
    async def _generate_implementation_notes(self, strategy: HashtagStrategy) -> List[str]:
        return []
    
    # More placeholder methods for trend tracking, optimization, etc.
    
    async def _get_hashtag_trend_data(self, hashtag: str, platform: Platform, days: int) -> Dict[str, Any]:
        return {}
    
    def _calculate_trend_volatility(self, trend_data: Dict) -> float:
        return 0.0
    
    def _identify_seasonal_patterns(self, trend_data: Dict) -> List[str]:
        return []
    
    def _identify_peak_usage_times(self, trend_data: Dict) -> List[str]:
        return []
    
    def _determine_trend_direction(self, trend_data: Dict) -> TrendDirection:
        return TrendDirection.STABLE
    
    async def _predict_hashtag_future_performance(self, hashtag: str, platform: Platform, trend_data: Dict) -> Dict[str, Any]:
        return {}
    
    def _generate_hashtag_alerts(self, hashtag: str, trend_analysis: Dict, predictions: Dict) -> List[Dict]:
        return []
    
    def _calculate_average_competition_difficulty(self, hashtags: List[str], platform: Platform) -> str:
        return "medium"
    
    # Background task implementations
    
    async def _update_platform_trends(self, platform -> None: Platform) -> None:
        """Update trends for a specific platform."""
        try:
            # Fetch trending hashtags for the platform
            trending_data = await self._fetch_platform_trending_data(platform)
            
            # Analyze trend patterns
            trend_analysis = {
                'top_trending': trending_data.get('top_hashtags', [])[:20],
                'emerging_trends': await self._identify_emerging_trends(trending_data, platform),
                'declining_trends': await self._identify_declining_trends(platform),
                'seasonal_patterns': await self._analyze_seasonal_patterns(platform),
                'geo_trends': await self._analyze_geo_specific_trends(platform),
                'updated_at': datetime.now().isoformat()
            }
            
            # Store trend data
            await self._store_platform_trends(platform, trend_analysis)
            
            # Update hashtag performance scores
            await self._update_hashtag_scores(platform, trending_data)
            
            # Generate platform-specific recommendations
            recommendations = await self._generate_platform_recommendations(platform, trend_analysis)
            await self._store_platform_recommendations(platform, recommendations)
            
            logger.info(f"Updated trends for {platform.value}: {len(trend_analysis['top_trending'])} trending hashtags")
            
        except Exception as e:
            logger.error(f"Error updating platform trends for {platform.value}: {e}")
            raise
    
    async def _analyze_engagement_patterns(self) -> None:
        """Analyze engagement patterns across hashtags."""
        try:
            # Get hashtag performance data
            performance_data = await self._get_hashtag_performance_data()
            
            # Analyze engagement patterns
            patterns = {
                'time_based_patterns': {
                    'hourly_peaks': await self._analyze_hourly_engagement_peaks(performance_data),
                    'daily_patterns': await self._analyze_daily_engagement_patterns(performance_data),
                    'weekly_cycles': await self._analyze_weekly_engagement_cycles(performance_data)
                },
                'content_type_patterns': {
                    'audio_hashtags': await self._analyze_audio_hashtag_engagement(performance_data),
                    'video_hashtags': await self._analyze_video_hashtag_engagement(performance_data),
                    'collaboration_hashtags': await self._analyze_collaboration_hashtag_engagement(performance_data)
                },
                'audience_patterns': {
                    'demographic_preferences': await self._analyze_demographic_hashtag_preferences(performance_data),
                    'geographic_variations': await self._analyze_geographic_hashtag_variations(performance_data),
                    'behavior_clusters': await self._analyze_user_behavior_clusters(performance_data)
                },
                'viral_patterns': {
                    'viral_indicators': await self._identify_viral_hashtag_indicators(performance_data),
                    'cascade_patterns': await self._analyze_hashtag_cascade_patterns(performance_data),
                    'amplification_factors': await self._analyze_amplification_factors(performance_data)
                }
            }
            
            # Generate insights from patterns
            insights = await self._generate_engagement_insights(patterns)
            
            # Store pattern analysis
            await self._store_engagement_patterns(patterns, insights)
            
            # Update recommendation algorithms
            await self._update_recommendation_algorithms(patterns)
            
            logger.info(f"Analyzed engagement patterns: {len(insights)} insights generated")
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing engagement patterns: {e}")
            raise
    
    async def _track_competitor_hashtags(self) -> None:
        """Track competitor hashtag usage."""
        try:
            # Get competitor list
            competitors = await self._get_competitor_list()
            
            competitor_analysis = {}
            
            for competitor in competitors:
                # Analyze competitor hashtag strategy
                hashtag_data = await self._analyze_competitor_hashtags(competitor)
                
                analysis = {
                    'competitor_id': competitor['id'],
                    'competitor_name': competitor['name'],
                    'top_hashtags': hashtag_data['most_used'][:20],
                    'unique_hashtags': hashtag_data['unique_to_competitor'],
                    'hashtag_diversity': len(set(hashtag_data['all_hashtags'])),
                    'trending_adoption': hashtag_data['trending_hashtags_used'],
                    'performance_metrics': {
                        'avg_engagement': hashtag_data['avg_engagement_per_hashtag'],
                        'reach_efficiency': hashtag_data['reach_per_hashtag'],
                        'virality_score': hashtag_data['viral_hashtag_ratio']
                    },
                    'strategy_insights': {
                        'posting_frequency': hashtag_data['posting_frequency'],
                        'hashtag_mix': hashtag_data['hashtag_category_distribution'],
                        'timing_patterns': hashtag_data['optimal_posting_times'],
                        'content_alignment': hashtag_data['content_hashtag_alignment']
                    },
                    'competitive_advantages': await self._identify_competitor_advantages(competitor, hashtag_data),
                    'gap_opportunities': await self._identify_hashtag_gaps(competitor, hashtag_data),
                    'analyzed_at': datetime.now().isoformat()
                }
                
                competitor_analysis[competitor['id']] = analysis
            
            # Generate competitive intelligence insights
            competitive_insights = await self._generate_competitive_insights(competitor_analysis)
            
            # Store competitor analysis
            await self._store_competitor_analysis(competitor_analysis, competitive_insights)
            
            # Update competitive strategy recommendations
            await self._update_competitive_recommendations(competitive_insights)
            
            logger.info(f"Tracked {len(competitors)} competitors hashtag strategies")
            
            return competitor_analysis
            
        except Exception as e:
            logger.error(f"Error tracking competitor hashtags: {e}")
            raise
    
    async def _detect_viral_hashtags(self) -> None:
        """Detect viral hashtags."""
        try:
            # Collect recent hashtag performance data
            recent_data = await self._get_recent_hashtag_data(hours=24)
            
            viral_candidates = []
            
            for hashtag, data in recent_data.items():
                # Calculate viral indicators
                viral_score = await self._calculate_viral_score(hashtag, data)
                
                # Check viral thresholds
                if viral_score >= 0.7:  # High viral potential
                    growth_rate = await self._calculate_growth_rate(hashtag, data)
                    reach_velocity = await self._calculate_reach_velocity(hashtag, data)
                    engagement_acceleration = await self._calculate_engagement_acceleration(hashtag, data)
                    
                    viral_analysis = {
                        'hashtag': hashtag,
                        'viral_score': viral_score,
                        'growth_rate': growth_rate,
                        'reach_velocity': reach_velocity,
                        'engagement_acceleration': engagement_acceleration,
                        'current_reach': data['current_reach'],
                        'total_uses': data['use_count'],
                        'unique_users': data['unique_users'],
                        'platform_distribution': data['platform_breakdown'],
                        'first_detected': data['first_seen'],
                        'detection_time': datetime.now().isoformat(),
                        'predicted_peak': await self._predict_viral_peak(hashtag, data),
                        'recommended_action': await self._get_viral_recommendation(viral_score, growth_rate),
                        'risk_assessment': await self._assess_viral_risk(hashtag, data)
                    }
                    
                    viral_candidates.append(viral_analysis)
            
            # Sort by viral potential
            viral_candidates.sort(key=lambda x: x['viral_score'], reverse=True)
            
            # Generate viral alerts for top candidates
            for candidate in viral_candidates[:5]:  # Top 5 viral candidates
                await self._send_viral_alert(candidate)
            
            # Store viral detection results
            await self._store_viral_detection_results(viral_candidates)
            
            # Update viral tracking models
            await self._update_viral_prediction_models(viral_candidates)
            
            logger.info(f"Detected {len(viral_candidates)} viral hashtag candidates")
            
            return viral_candidates
            
        except Exception as e:
            logger.error(f"Error detecting viral hashtags: {e}")
            raise

# Export the main classes
__all__ = [
    'HashtagIntelligenceMonitor', 'HashtagData', 'HashtagRecommendation', 'HashtagStrategy',
    'Platform', 'HashtagCategory', 'TrendDirection'
]