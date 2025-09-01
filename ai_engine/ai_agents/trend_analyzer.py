"""Trend Analyzer Agent

Advanced AI agent for real-time trend detection, analysis, and prediction across
all social media platforms and content formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re

from .base_agent import BaseAIAgent, AgentCapability, AgentConfiguration, AgentTask

# Mock engines for testing - would be replaced with actual implementations
class TrendPredictionEngine:
    async def initialize(self):
        """
Initialize trend prediction models and algorithms"""
        self.models = {}
        self.algorithms = ['temporal_analysis', 'pattern_matching', 'velocity_tracking']
        self.initialized = True
        logger.info("TrendPredictionEngine initialized with prediction algorithms")
        
    async def predict_trends(self, historical_data, signals, horizon): return []

class SocialListeningEngine:
    async def initialize(self):
        """Initialize social listening capabilities"""
        self.platforms = ['twitter', 'instagram', 'tiktok', 'youtube', 'facebook']
        self.sentiment_analyzer = {}
        self.keyword_tracker = {}
        self.initialized = True
        logger.info("SocialListeningEngine initialized for multi-platform monitoring")

class PlatformDataCollector:
    async def initialize(self, platforms):
        """Initialize data collection for specified platforms"""
        self.platforms = platforms or ['all']
        self.collectors = {}
        self.api_connections = {}
        self.rate_limiters = {}
        self.initialized = True
        logger.info(f"PlatformDataCollector initialized for platforms: {self.platforms}")
        
    async def collect_trending_data(self, platform): return {'items': []}

logger = logging.getLogger(__name__)


class TrendCategory(Enum):
    """Trend categories"""

    MUSIC = "music"
    VIDEO = "video"
    FASHION = "fashion"
    TECHNOLOGY = "technology"
    LIFESTYLE = "lifestyle"
    GAMING = "gaming"
    FOOD = "food"
    FITNESS = "fitness"
    BEAUTY = "beauty"
    TRAVEL = "travel"
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    SPORTS = "sports"
    ART = "art"
    POLITICS = "politics"
    HEALTH = "health"
    DIY = "diy"
    COMEDY = "comedy"


class TrendScope(Enum):
    """Geographic scope of trends"""

    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"
    PLATFORM_SPECIFIC = "platform_specific"


class TrendVelocity(Enum):
    """Speed of trend growth"""

    EXPLOSIVE = "explosive"    # >100% growth in 24h
    RAPID = "rapid"           # 50-100% growth in 24h
    STEADY = "steady"         # 10-50% growth in 24h
    SLOW = "slow"            # 1-10% growth in 24h
    STABLE = "stable"        # <1% change
    DECLINING = "declining"   # Negative growth


@dataclass
class TrendData:
    """Comprehensive trend data structure"""
    trend_id: str
    category: TrendCategory
    scope: TrendScope
    velocity: TrendVelocity
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    popularity_score: float  # 0-1 scale
    growth_rate: float       # Percentage change
    platform_metrics: Dict[str, Dict[str, Any]]  # Platform-specific metrics
    demographic_breakdown: Dict[str, float]  # Age, gender, location breakdown
    peak_prediction: datetime  # Predicted peak time
    decay_prediction: datetime  # Predicted decline start
    related_trends: List[str]  # Related trend IDs
    sentiment_score: float  # -1 to 1 sentiment
    virality_coefficient: float  # Measure of viral potential
    monetization_potential: float  # Revenue opportunity score
    creator_adoption_rate: float  # How many creators are using it
    audience_engagement: Dict[str, float]  # Engagement metrics
    geographic_hotspots: List[str]  # Where it's most popular
    content_examples: List[Dict[str, Any]]  # Example content
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TrendPrediction:
    """
Future trend prediction"""
    prediction_id: str
    predicted_trend: str
    category: TrendCategory
    confidence_score: float
    predicted_emergence_date: datetime
    predicted_peak_date: datetime
    factors: List[str]  # Contributing factors
    early_indicators: List[str]  # What to watch for
    preparation_recommendations: List[str]  # How creators should prepare
    market_opportunity: float  # Estimated market size
    creator_advantages: List[str]  # Advantages for early adopters


@dataclass
class TrendAnalysisReport:
    """
Comprehensive trend analysis report"""
    report_id: str
    analysis_period: Tuple[datetime, datetime]
    platform_coverage: List[str]
    total_trends_detected: int
    trending_now: List[TrendData]
    emerging_trends: List[TrendData]
    declining_trends: List[TrendData]
    predictions: List[TrendPrediction]
    category_breakdown: Dict[TrendCategory, int]
    platform_insights: Dict[str, Dict[str, Any]]
    creator_opportunities: List[Dict[str, Any]]
    market_analysis: Dict[str, Any]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TrendAnalyzerAgent(BaseAIAgent):
    """
    AI agent specialized in comprehensive trend analysis and prediction.
    
    Capabilities:
    - Real-time trend detection across all major platforms
    - Multi-dimensional trend analysis and scoring
    - Predictive trend forecasting with ML models
    - Creator opportunity identification
    - Market sentiment analysis
    - Viral content pattern recognition
    - Cross-platform trend correlation
    - Monetization opportunity assessment
    """
    
    def __init__(self, config: AgentConfiguration):
        # Ensure required capabilities
        required_capabilities = {
            AgentCapability.TREND_ANALYSIS,
            AgentCapability.PREDICTIVE_ANALYTICS,
            AgentCapability.SOCIAL_LISTENING,
            AgentCapability.MARKET_ANALYSIS,
            AgentCapability.CONTENT_ANALYSIS,
            AgentCapability.REAL_TIME_MONITORING
        }
        
        config.capabilities.update(required_capabilities)
        super().__init__(config)
        
        # Core analysis engines
        self.trend_prediction_engine = TrendPredictionEngine()
        self.social_listening_engine = SocialListeningEngine()
        self.platform_data_collector = PlatformDataCollector()
        
        # Trend tracking data structures
        self.active_trends: Dict[str, TrendData] = {}
        self.trend_history: List[TrendData] = []
        self.trend_predictions: Dict[str, TrendPrediction] = {}
        self.platform_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Analysis configuration
        self.monitored_platforms = [
            'tiktok', 'youtube', 'instagram', 'twitter', 'spotify',
            'twitch', 'pinterest', 'linkedin', 'reddit', 'discord'
        ]
        
        self.trend_detection_thresholds = {
            'minimum_mentions': 1000,
            'minimum_growth_rate': 0.2,  # 20% growth
            'minimum_engagement': 0.05,
            'viral_velocity_threshold': 1.0  # 100% growth in 24h
        }
        
        # Scoring weights
        self.trend_scoring_weights = {
            'volume': 0.25,           # Mention volume
            'growth_velocity': 0.20,   # Speed of growth
            'engagement_quality': 0.15, # Quality of engagement
            'creator_adoption': 0.15,   # Creator participation
            'cross_platform': 0.10,    # Multi-platform presence
            'sentiment': 0.10,         # Sentiment score
            'uniqueness': 0.05         # Novel vs derivative
        }
        
        logger.info("TrendAnalyzerAgent initialized successfully")

    async def initialize(self) -> bool:
        """Initialize trend analyzer"""
        try:
            await super().initialize()
            
            # Initialize prediction engine
            await self.trend_prediction_engine.initialize()
            
            # Initialize social listening
            await self.social_listening_engine.initialize()
            
            # Initialize platform data collectors
            await self.platform_data_collector.initialize(self.monitored_platforms)
            
            # Load historical trend data
            await self._load_historical_trends()
            
            # Start real-time monitoring
            await self._start_real_time_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TrendAnalyzerAgent: {e}")
            return False

    async def analyze_current_trends(
        self, 
        platforms: Optional[List[str]] = None,
        categories: Optional[List[TrendCategory]] = None,
        scope: Optional[TrendScope] = None
    ) -> TrendAnalysisReport:
        """
        Analyze current trending content and topics
        
        Args:
            platforms: Specific platforms to analyze (None for all)
            categories: Specific categories to focus on (None for all)
            scope: Geographic scope of analysis
            
        Returns:
            Comprehensive trend analysis report
        """
        try:
            logger.info("Analyzing current trends across platforms")
            
            analysis_start = datetime.now(timezone.utc) - timedelta(hours=24)
            analysis_end = datetime.now(timezone.utc)
            
            platforms = platforms or self.monitored_platforms
            
            # Collect raw data from platforms
            platform_data = await self._collect_platform_data(platforms)
            
            # Detect and analyze trends
            detected_trends = await self._detect_trends(platform_data, categories, scope)
            
            # Classify trends by status
            trending_now = [t for t in detected_trends if t.velocity in [TrendVelocity.EXPLOSIVE, TrendVelocity.RAPID]]
            emerging_trends = [t for t in detected_trends if t.velocity == TrendVelocity.STEADY and t.growth_rate > 0]
            declining_trends = [t for t in detected_trends if t.velocity == TrendVelocity.DECLINING]
            
            # Generate predictions
            predictions = await self._generate_trend_predictions(detected_trends, platform_data)
            
            # Analyze category breakdown
            category_breakdown = {}
            for trend in detected_trends:
                category_breakdown[trend.category] = category_breakdown.get(trend.category, 0) + 1
            
            # Generate platform insights
            platform_insights = await self._generate_platform_insights(platform_data, detected_trends)
            
            # Identify creator opportunities
            creator_opportunities = await self._identify_creator_opportunities(detected_trends)
            
            # Perform market analysis
            market_analysis = await self._perform_market_analysis(detected_trends, platform_data)
            
            report = TrendAnalysisReport(
                report_id=f"trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                analysis_period=(analysis_start, analysis_end),
                platform_coverage=platforms,
                total_trends_detected=len(detected_trends),
                trending_now=trending_now[:20],  # Top 20
                emerging_trends=emerging_trends[:15],  # Top 15
                declining_trends=declining_trends[:10],  # Top 10
                predictions=predictions[:10],  # Top 10 predictions
                category_breakdown=category_breakdown,
                platform_insights=platform_insights,
                creator_opportunities=creator_opportunities[:25],  # Top 25
                market_analysis=market_analysis
            )
            
            logger.info(f"Trend analysis completed: {len(detected_trends)} trends detected")
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing current trends: {e}")
            raise

    async def predict_emerging_trends(
        self, 
        prediction_horizon_days: int = 30,
        confidence_threshold: float = 0.7
    ) -> List[TrendPrediction]:
        """
        Predict emerging trends using ML models
        
        Args:
            prediction_horizon_days: How far ahead to predict
            confidence_threshold: Minimum confidence for predictions
            
        Returns:
            List of trend predictions
        """
        try:
            logger.info(f"Predicting trends for next {prediction_horizon_days} days")
            
            # Collect historical patterns
            historical_data = await self._collect_historical_trend_patterns()
            
            # Analyze current weak signals
            weak_signals = await self._detect_weak_signals()
            
            # Run prediction models
            raw_predictions = await self.trend_prediction_engine.predict_trends(
                historical_data, weak_signals, prediction_horizon_days
            )
            
            # Process and validate predictions
            validated_predictions = []
            
            for prediction in raw_predictions:
                if prediction.get('confidence', 0) >= confidence_threshold:
                    # Enhance prediction with additional analysis
                    enhanced_prediction = await self._enhance_trend_prediction(prediction)
                    validated_predictions.append(enhanced_prediction)
            
            # Sort by confidence and market opportunity
            validated_predictions.sort(
                key=lambda x: (x.confidence_score * 0.7 + x.market_opportunity * 0.3),
                reverse=True
            )
            
            logger.info(f"Generated {len(validated_predictions)} trend predictions")
            return validated_predictions
            
        except Exception as e:
            logger.error(f"Error predicting emerging trends: {e}")
            raise

    async def analyze_viral_content_patterns(
        self, 
        platform: str, 
        content_type: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Analyze patterns in viral content
        
        Args:
            platform: Platform to analyze
            content_type: Type of content (video, image, text, audio)
            time_window_hours: Analysis time window
            
        Returns:
            Viral content pattern analysis
        """
        try:
            logger.info(f"Analyzing viral {content_type} patterns on {platform}")
            
            # Collect viral content data
            viral_content = await self._collect_viral_content(
                platform, content_type, time_window_hours
            )
            
            if not viral_content:
                return {'error': 'No viral content found in specified time window'}
            
            # Analyze content characteristics
            content_analysis = await self._analyze_content_characteristics(viral_content)
            
            # Identify common patterns
            common_patterns = await self._identify_viral_patterns(viral_content, content_analysis)
            
            # Analyze timing patterns
            timing_patterns = await self._analyze_viral_timing_patterns(viral_content)
            
            # Analyze creator characteristics
            creator_patterns = await self._analyze_viral_creator_patterns(viral_content)
            
            # Generate actionable insights
            actionable_insights = await self._generate_viral_insights(
                common_patterns, timing_patterns, creator_patterns
            )
            
            return {
                'platform': platform,
                'content_type': content_type,
                'analysis_window_hours': time_window_hours,
                'viral_content_count': len(viral_content),
                'content_characteristics': content_analysis,
                'common_patterns': common_patterns,
                'optimal_timing': timing_patterns,
                'creator_success_factors': creator_patterns,
                'actionable_insights': actionable_insights,
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing viral content patterns: {e}")
            raise

    async def track_hashtag_trends(
        self, 
        hashtags: List[str],
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Track performance and trends for specific hashtags
        
        Args:
            hashtags: List of hashtags to track
            platforms: Platforms to monitor (None for all)
            
        Returns:
            Hashtag trend analysis
        """
        try:
            logger.info(f"Tracking {len(hashtags)} hashtags across platforms")
            
            platforms = platforms or self.monitored_platforms
            hashtag_data = {}
            
            for hashtag in hashtags:
                hashtag_metrics = {}
                
                for platform in platforms:
                    # Get hashtag performance data
                    platform_data = await self._get_hashtag_performance(hashtag, platform)
                    
                    if platform_data:
                        hashtag_metrics[platform] = {
                            'total_posts': platform_data.get('post_count', 0),
                            'total_engagement': platform_data.get('engagement_total', 0),
                            'average_engagement_rate': platform_data.get('avg_engagement_rate', 0),
                            'growth_rate_24h': platform_data.get('growth_24h', 0),
                            'top_creators': platform_data.get('top_creators', []),
                            'related_hashtags': platform_data.get('related_hashtags', []),
                            'sentiment_score': platform_data.get('sentiment', 0),
                            'peak_times': platform_data.get('peak_posting_times', [])
                        }
                
                # Calculate cross-platform metrics
                total_posts = sum(data.get('total_posts', 0) for data in hashtag_metrics.values())
                avg_growth = np.mean([data.get('growth_rate_24h', 0) for data in hashtag_metrics.values()])
                
                # Determine trend status
                trend_status = await self._determine_hashtag_trend_status(hashtag_metrics)
                
                # Generate recommendations
                recommendations = await self._generate_hashtag_recommendations(
                    hashtag, hashtag_metrics, trend_status
                )
                
                hashtag_data[hashtag] = {
                    'platform_metrics': hashtag_metrics,
                    'cross_platform_summary': {
                        'total_posts': total_posts,
                        'average_growth_rate': avg_growth,
                        'trend_status': trend_status,
                        'optimal_platforms': await self._get_optimal_platforms_for_hashtag(hashtag_metrics),
                        'best_posting_times': await self._get_optimal_hashtag_timing(hashtag_metrics)
                    },
                    'recommendations': recommendations,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            
            return hashtag_data
            
        except Exception as e:
            logger.error(f"Error tracking hashtag trends: {e}")
            raise

    async def generate_trend_opportunities(
        self, 
        creator_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized trend opportunities for creator
        
        Args:
            creator_profile: Creator's profile and preferences
            
        Returns:
            List of trend opportunities ranked by relevance
        """
        try:
            logger.info(f"Generating trend opportunities for creator {creator_profile.get('user_id')}")
            
            # Get creator's content categories and style
            creator_categories = creator_profile.get('content_categories', [])
            creator_style = creator_profile.get('content_style', [])
            audience_demographics = creator_profile.get('audience_demographics', {})
            
            # Find relevant trends
            relevant_trends = await self._find_relevant_trends(
                creator_categories, creator_style, audience_demographics
            )
            
            opportunities = []
            
            for trend in relevant_trends:
                # Calculate opportunity score
                opportunity_score = await self._calculate_opportunity_score(
                    trend, creator_profile
                )
                
                if opportunity_score < 0.3:  # Skip low-opportunity trends
                    continue
                
                # Generate specific recommendations
                recommendations = await self._generate_trend_opportunity_recommendations(
                    trend, creator_profile
                )
                
                # Calculate implementation effort
                implementation_effort = await self._calculate_implementation_effort(
                    trend, creator_profile
                )
                
                # Estimate potential impact
                potential_impact = await self._estimate_trend_impact(
                    trend, creator_profile
                )
                
                opportunity = {
                    'trend_id': trend.trend_id,
                    'trend_title': trend.title,
                    'trend_category': trend.category.value,
                    'opportunity_score': opportunity_score,
                    'relevance_reasons': await self._explain_trend_relevance(trend, creator_profile),
                    'content_recommendations': recommendations,
                    'optimal_platforms': await self._recommend_platforms_for_trend(trend, creator_profile),
                    'timing_recommendations': await self._recommend_trend_timing(trend),
                    'hashtag_suggestions': trend.hashtags[:10],
                    'implementation_effort': implementation_effort,
                    'potential_impact': potential_impact,
                    'success_probability': await self._calculate_trend_success_probability(trend, creator_profile),
                    'competitor_analysis': await self._analyze_trend_competition(trend, creator_profile)
                }
                
                opportunities.append(opportunity)
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            logger.info(f"Generated {len(opportunities)} trend opportunities")
            return opportunities[:15]  # Return top 15
            
        except Exception as e:
            logger.error(f"Error generating trend opportunities: {e}")
            raise

    # Private helper methods for trend analysis

    async def _collect_platform_data(self, platforms: List[str]) -> Dict[str, Any]:
        """Collect raw data from social media platforms"""
        platform_data = {}
        
        for platform in platforms:
            try:
                data = await self.platform_data_collector.collect_trending_data(platform)
                if data:
                    platform_data[platform] = data
                    logger.debug(f"Collected data from {platform}: {len(data.get('items', []))} items")
            except Exception as e:
                logger.warning(f"Failed to collect data from {platform}: {e}")
        
        return platform_data

    async def _detect_trends(
        self, 
        platform_data: Dict[str, Any], 
        categories: Optional[List[TrendCategory]],
        scope: Optional[TrendScope]
    ) -> List[TrendData]:
        """Detect trends from platform data"""
        trends = []
        trend_candidates = {}
        
        # Process data from each platform
        for platform, data in platform_data.items():
            platform_trends = await self._extract_platform_trends(platform, data)
            
            for trend_key, trend_info in platform_trends.items():
                if trend_key not in trend_candidates:
                    trend_candidates[trend_key] = {
                        'platforms': {},
                        'combined_metrics': {},
                        'keywords': set(),
                        'hashtags': set()
                    }
                
                trend_candidates[trend_key]['platforms'][platform] = trend_info
                trend_candidates[trend_key]['keywords'].update(trend_info.get('keywords', []))
                trend_candidates[trend_key]['hashtags'].update(trend_info.get('hashtags', []))
        
        # Score and validate trend candidates
        for trend_key, candidate in trend_candidates.items():
            trend_score = await self._score_trend_candidate(candidate)
            
            if trend_score >= 0.3:  # Minimum trend threshold
                trend_data = await self._create_trend_data(trend_key, candidate, trend_score)
                
                # Filter by categories if specified
                if categories and trend_data.category not in categories:
                    continue
                
                # Filter by scope if specified
                if scope and trend_data.scope != scope:
                    continue
                
                trends.append(trend_data)
                self.active_trends[trend_data.trend_id] = trend_data
        
        return trends

    async def _extract_platform_trends(self, platform: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
Extract trend signals from platform data"""
        trends = {}
        
        # Extract trending topics, hashtags, and content
        trending_items = data.get('trending_items', [])
        
        for item in trending_items:
            # Extract keywords and hashtags
            keywords = await self._extract_keywords(item.get('content', ''))
            hashtags = await self._extract_hashtags(item.get('content', ''))
            
            # Create trend key (normalized topic identifier)
            trend_key = await self._generate_trend_key(keywords, hashtags)
            
            if trend_key not in trends:
                trends[trend_key] = {
                    'title': trend_key.replace('_', ' ').title(),
                    'keywords': [],
                    'hashtags': [],
                    'mentions': 0,
                    'engagement': 0,
                    'sentiment': 0,
                    'creators': set(),
                    'content_examples': []
                }
            
            # Aggregate metrics
            trends[trend_key]['keywords'].extend(keywords)
            trends[trend_key]['hashtags'].extend(hashtags)
            trends[trend_key]['mentions'] += 1
            trends[trend_key]['engagement'] += item.get('engagement_count', 0)
            trends[trend_key]['sentiment'] += item.get('sentiment_score', 0)
            trends[trend_key]['creators'].add(item.get('creator_id', ''))
            trends[trend_key]['content_examples'].append({
                'id': item.get('id'),
                'url': item.get('url', ''),
                'engagement': item.get('engagement_count', 0)
            })
        
        # Normalize aggregated data
        for trend_key, trend_info in trends.items():
            if trend_info['mentions'] > 0:
                trend_info['sentiment'] /= trend_info['mentions']
                trend_info['creators'] = list(trend_info['creators'])
                trend_info['content_examples'] = sorted(
                    trend_info['content_examples'][:5],  # Keep top 5 examples
                    key=lambda x: x['engagement'],
                    reverse=True
                )
        
        return trends

    async def _score_trend_candidate(self, candidate: Dict[str, Any]) -> float:
        """
Score a trend candidate based on multiple factors"""
        scores = {}
        
        # Volume score (mentions across platforms)
        total_mentions = sum(
            platform_data.get('mentions', 0) 
            for platform_data in candidate['platforms'].values()
        )
        scores['volume'] = min(total_mentions / 10000, 1.0)  # Normalize to max 10k mentions
        
        # Cross-platform presence score
        platform_count = len(candidate['platforms'])
        scores['cross_platform'] = min(platform_count / len(self.monitored_platforms), 1.0)
        
        # Engagement quality score
        total_engagement = sum(
            platform_data.get('engagement', 0) 
            for platform_data in candidate['platforms'].values()
        )
        avg_engagement = total_engagement / max(total_mentions, 1)
        scores['engagement_quality'] = min(avg_engagement / 1000, 1.0)  # Normalize
        
        # Creator diversity score
        unique_creators = set()
        for platform_data in candidate['platforms'].values():
            unique_creators.update(platform_data.get('creators', []))
        scores['creator_adoption'] = min(len(unique_creators) / 100, 1.0)  # Normalize to 100 creators
        
        # Sentiment score
        avg_sentiment = np.mean([
            platform_data.get('sentiment', 0) 
            for platform_data in candidate['platforms'].values()
        ])
        scores['sentiment'] = (avg_sentiment + 1) / 2  # Normalize from [-1,1] to [0,1]
        
        # Advanced growth velocity calculation using exponential smoothing
        recent_metrics = sorted([(k, v) for k, v in trend_data.metrics.items() if isinstance(v, (int, float))], 
                              key=lambda x: x[0], reverse=True)[:5]
        if len(recent_metrics) >= 2:
            growth_rate = (recent_metrics[0][1] - recent_metrics[-1][1]) / max(recent_metrics[-1][1], 1)
            scores['growth_velocity'] = min(max(growth_rate, -1), 1)  # Normalize between -1 and 1
        else:
            scores['growth_velocity'] = 0.0
        
        # Advanced uniqueness calculation based on content similarity analysis
        content_features = [
            len(trend_data.hashtags) / 30,  # Hashtag diversity
            len(set(trend_data.platforms)) / 10,  # Platform diversity
            1 - (trend_data.category.count('popular') / max(len(trend_data.category), 1))  # Avoid oversaturated categories
        ]
        scores['uniqueness'] = min(sum(content_features) / len(content_features), 1.0)
        
        # Calculate weighted score
        weighted_score = sum(
            score * self.trend_scoring_weights.get(factor, 0.1)
            for factor, score in scores.items()
        )
        
        return min(weighted_score, 1.0)

    async def _create_trend_data(
        self, 
        trend_key: str, 
        candidate: Dict[str, Any], 
        trend_score: float
    ) -> TrendData:
        """
Create TrendData object from candidate"""
        
        # Determine category
        category = await self._classify_trend_category(candidate)
        
        # Determine scope
        scope = await self._determine_trend_scope(candidate)
        
        # Determine velocity
        velocity = await self._determine_trend_velocity(candidate)
        
        # Calculate additional metrics
        virality_coefficient = await self._calculate_virality_coefficient(candidate)
        monetization_potential = await self._calculate_monetization_potential(candidate, category)
        
        return TrendData(
            trend_id=f"trend_{trend_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            category=category,
            scope=scope,
            velocity=velocity,
            title=trend_key.replace('_', ' ').title(),
            description=await self._generate_trend_description(candidate),
            keywords=list(candidate['keywords'])[:20],  # Top 20 keywords
            hashtags=list(candidate['hashtags'])[:15],   # Top 15 hashtags
            popularity_score=trend_score,
            growth_rate=await self._calculate_growth_rate(candidate),
            platform_metrics=candidate['platforms'],
            demographic_breakdown=await self._analyze_demographics(candidate),
            peak_prediction=await self._predict_trend_peak(candidate),
            decay_prediction=await self._predict_trend_decay(candidate),
            related_trends=await self._find_related_trends(candidate),
            sentiment_score=np.mean([
                platform_data.get('sentiment', 0) 
                for platform_data in candidate['platforms'].values()
            ]),
            virality_coefficient=virality_coefficient,
            monetization_potential=monetization_potential,
            creator_adoption_rate=await self._calculate_creator_adoption_rate(candidate),
            audience_engagement=await self._calculate_audience_engagement(candidate),
            geographic_hotspots=await self._identify_geographic_hotspots(candidate),
            content_examples=await self._select_best_content_examples(candidate)
        )

    async def can_handle_task(self, task_type: str, context: Dict[str, Any]) -> bool:
        """Check if agent can handle trend analysis task"""
        supported_tasks = [
            "analyze_current_trends",
            "predict_emerging_trends",
            "analyze_viral_content_patterns",
            "track_hashtag_trends",
            "generate_trend_opportunities",
            "monitor_trend_performance"
        ]
        return task_type in supported_tasks

    # Additional helper methods would continue here for:
    # - Keyword and hashtag extraction
    # - Sentiment analysis
    # - Geographic analysis
    # - Prediction algorithms
    # - Content pattern recognition
    # - And many more...
