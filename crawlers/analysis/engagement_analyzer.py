"""Engagement Analyzer
==================

Advanced engagement analysis and audience interaction intelligence system.
Implements engagement prediction, audience behavior analysis, and optimization strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import Counter, defaultdict
import json
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types of engagement interactions."""    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    VIEW = "view"
    FOLLOW = "follow"
    MENTION = "mention"
    DIRECT_MESSAGE = "direct_message"
    REACTION = "reaction"

class EngagementQuality(Enum):
    """Quality levels of engagement."""    EXCELLENT = "excellent"     # High-value meaningful interactions
    GOOD = "good"              # Positive meaningful interactions
    AVERAGE = "average"        # Standard interactions
    POOR = "poor"              # Low-value interactions
    SPAM = "spam"              # Spam or bot interactions

class AudienceSegment(Enum):
    """Audience segmentation categories."""    CORE_FANS = "core_fans"           # Most engaged loyal followers
    CASUAL_FOLLOWERS = "casual_followers"  # Regular but less engaged
    NEW_AUDIENCE = "new_audience"     # Recently discovered content
    TRENDING_VIEWERS = "trending_viewers"  # Came from trending content
    ORGANIC_DISCOVERY = "organic_discovery"  # Found through search/recommendations
    PAID_AUDIENCE = "paid_audience"   # Reached through paid promotion

@dataclass
class EngagementMetrics:
    """Comprehensive engagement metrics."""    total_interactions: int
    engagement_rate: float          # Total engagement / reach
    authentic_engagement_rate: float  # Excluding bots/spam
    
    # Interaction breakdown
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    views: int = 0
    
    # Quality metrics
    comment_sentiment: float = 0.0  # Average comment sentiment
    response_rate: float = 0.0      # Creator response rate to comments
    conversation_depth: float = 0.0  # Average comment thread length
    
    # Timing metrics
    engagement_velocity: float = 0.0  # Engagement growth rate
    peak_engagement_time: Optional[datetime] = None
    engagement_duration: float = 0.0  # How long engagement lasts
    
    # Audience metrics
    unique_users: int = 0
    repeat_engagers: int = 0
    new_vs_returning_ratio: float = 0.0

@dataclass
class AudienceInsights:
    """Audience behavior and demographic insights."""    total_audience_size: int
    active_audience_percentage: float
    
    # Segmentation
    segment_distribution: Dict[AudienceSegment, float] = field(default_factory=dict)
    engagement_by_segment: Dict[AudienceSegment, float] = field(default_factory=dict)
    
    # Behavior patterns
    optimal_posting_times: List[datetime] = field(default_factory=list)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Demographics (anonymized)
    age_distribution: Dict[str, float] = field(default_factory=dict)
    geographic_distribution: Dict[str, float] = field(default_factory=dict)
    device_usage: Dict[str, float] = field(default_factory=dict)
    
    # Growth metrics
    follower_growth_rate: float = 0.0
    audience_retention_rate: float = 0.0
    churn_rate: float = 0.0

@dataclass
class EngagementPrediction:
    """Engagement prediction and forecasting."""    predicted_engagement_rate: float
    predicted_interactions: int
    confidence_score: float
    
    # Detailed predictions
    predicted_likes: int = 0
    predicted_comments: int = 0
    predicted_shares: int = 0
    predicted_reach: int = 0
    
    # Factors influencing prediction
    content_factors: Dict[str, float] = field(default_factory=dict)
    timing_factors: Dict[str, float] = field(default_factory=dict)
    audience_factors: Dict[str, float] = field(default_factory=dict)
    
    # Optimization suggestions
    optimization_opportunities: List[str] = field(default_factory=list)
    predicted_improvement: float = 0.0  # Potential improvement with optimization

@dataclass
class EngagementAnalysisResult:
    """Complete engagement analysis result."""    content_id: str
    analysis_timestamp: datetime
    
    # Current metrics
    current_metrics: EngagementMetrics
    audience_insights: AudienceInsights
    
    # Predictions and forecasting
    engagement_prediction: EngagementPrediction
    viral_potential_score: float
    
    # Comparative analysis
    performance_vs_average: float  # How this content compares to user's average
    industry_benchmarks: Dict[str, float] = field(default_factory=dict)
    competitor_comparison: Dict[str, float] = field(default_factory=dict)
    
    # Optimization recommendations
    engagement_optimization: List[str] = field(default_factory=list)
    content_recommendations: List[str] = field(default_factory=list)
    timing_recommendations: List[str] = field(default_factory=list)
    
    # Alerts and insights
    engagement_alerts: List[str] = field(default_factory=list)
    growth_opportunities: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    data_quality_score: float = 0.0
    analysis_confidence: float = 0.0

class EngagementAnalyzer:
    """    Advanced engagement analysis and audience intelligence system.
    
    Features:
    - Real-time engagement monitoring and analysis
    - Predictive engagement modeling with ML
    - Audience segmentation and behavior analysis
    - Engagement optimization recommendations
    - Viral potential assessment
    - Cross-platform engagement tracking
    - Bot and spam detection
    - Performance benchmarking
    """    
    def __init__(
        self,
        enable_prediction: bool = True,
        enable_realtime_monitoring: bool = True,
        spam_detection_threshold: float = 0.8,
        prediction_model_type: str = "random_forest"
    ):
        """        Initialize engagement analyzer.
        
        Args:
            enable_prediction: Enable engagement prediction
            enable_realtime_monitoring: Enable real-time monitoring
            spam_detection_threshold: Threshold for spam detection
            prediction_model_type: Type of ML model for predictions
        """        self.enable_prediction = enable_prediction
        self.enable_realtime_monitoring = enable_realtime_monitoring
        self.spam_detection_threshold = spam_detection_threshold
        self.prediction_model_type = prediction_model_type
        
        # Historical data storage
        self.engagement_history = defaultdict(list)
        self.audience_data = defaultdict(dict)
        self.performance_baselines = {}
        
        # ML models
        self.engagement_model = None
        self.spam_detector = None
        self.audience_segmentation_model = None
        
        # Analytics
        self.analysis_count = 0
        self.prediction_count = 0
        self.processing_times = []
        
        # Initialize components
        self._initialize_ml_models()
        self._load_industry_benchmarks()
        
        logger.info(f"EngagementAnalyzer initialized with {prediction_model_type} prediction model")
    
    def _initialize_ml_models(self) -> None:
        """Initialize machine learning models for engagement analysis."""        try:
            if self.enable_prediction:
                # Engagement prediction model
                if self.prediction_model_type == "random_forest":
                    self.engagement_model = RandomForestRegressor(
                        n_estimators=100,
                        max_depth=10,
                        random_state=42
                    )
                
                # Feature scaler for preprocessing
                self.feature_scaler = StandardScaler()
            
            logger.info("ML models initialized for engagement analysis")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    def _load_industry_benchmarks(self) -> None:
        """Load industry benchmarks for performance comparison."""        # Industry engagement rate benchmarks by platform
        self.industry_benchmarks = {
            'instagram': {
                'excellent': 0.06,
                'good': 0.03,
                'average': 0.018,
                'poor': 0.01
            },
            'tiktok': {
                'excellent': 0.18,
                'good': 0.09,
                'average': 0.05,
                'poor': 0.02
            },
            'youtube': {
                'excellent': 0.08,
                'good': 0.04,
                'average': 0.02,
                'poor': 0.01
            },
            'twitter': {
                'excellent': 0.05,
                'good': 0.025,
                'average': 0.015,
                'poor': 0.008
            },
            'linkedin': {
                'excellent': 0.04,
                'good': 0.02,
                'average': 0.012,
                'poor': 0.006
            }
        }
        
        # Content type benchmarks
        self.content_benchmarks = {
            'video': {'avg_engagement': 0.045, 'avg_shares': 0.015},
            'image': {'avg_engagement': 0.035, 'avg_shares': 0.012},
            'text': {'avg_engagement': 0.025, 'avg_shares': 0.008},
            'carousel': {'avg_engagement': 0.055, 'avg_shares': 0.018},
            'live': {'avg_engagement': 0.065, 'avg_shares': 0.025}
        }
    
    async def analyze_engagement(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        engagement_data: Dict[str, Any],
        audience_data: Optional[Dict[str, Any]] = None,
        platform: str = "general"
    ) -> EngagementAnalysisResult:
        """        Analyze engagement patterns and predict future performance.
        
        Args:
            content_id: Unique content identifier
            content_data: Content information and metadata
            engagement_data: Current engagement metrics
            audience_data: Audience demographic and behavior data
            platform: Platform where content is published
            
        Returns:
            EngagementAnalysisResult: Complete engagement analysis
        """        start_time = datetime.now()
        
        try:
            audience_data = audience_data or {}
            
            # Calculate current engagement metrics
            current_metrics = await self._calculate_engagement_metrics(
                content_id, engagement_data, platform
            )
            
            # Analyze audience insights
            audience_insights = await self._analyze_audience_insights(
                content_id, audience_data, engagement_data
            )
            
            # Generate engagement predictions
            engagement_prediction = None
            if self.enable_prediction:
                engagement_prediction = await self._predict_engagement(
                    content_data, current_metrics, audience_insights, platform
                )
            else:
                engagement_prediction = EngagementPrediction(
                    predicted_engagement_rate=current_metrics.engagement_rate,
                    predicted_interactions=current_metrics.total_interactions,
                    confidence_score=0.0
                )
            
            # Calculate viral potential
            viral_potential_score = self._calculate_viral_potential(
                current_metrics, engagement_prediction, content_data
            )
            
            # Performance comparison
            performance_vs_average = self._compare_performance_to_average(
                content_id, current_metrics
            )
            
            # Industry benchmarking
            industry_benchmarks = self._benchmark_against_industry(
                current_metrics, platform, content_data.get('content_type', 'text')
            )
            
            # Generate recommendations
            engagement_optimization = self._generate_engagement_optimization(
                current_metrics, audience_insights, engagement_prediction
            )
            
            content_recommendations = self._generate_content_recommendations(
                current_metrics, audience_insights, industry_benchmarks
            )
            
            timing_recommendations = self._generate_timing_recommendations(
                audience_insights, engagement_data
            )
            
            # Generate alerts and insights
            engagement_alerts = self._generate_engagement_alerts(
                current_metrics, performance_vs_average
            )
            
            growth_opportunities = self._identify_growth_opportunities(
                audience_insights, engagement_prediction
            )
            
            risk_factors = self._identify_risk_factors(
                current_metrics, audience_insights
            )
            
            # Calculate analysis quality metrics
            data_quality_score = self._calculate_data_quality(engagement_data, audience_data)
            analysis_confidence = self._calculate_analysis_confidence(
                current_metrics, data_quality_score
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = EngagementAnalysisResult(
                content_id=content_id,
                analysis_timestamp=datetime.now(),
                current_metrics=current_metrics,
                audience_insights=audience_insights,
                engagement_prediction=engagement_prediction,
                viral_potential_score=viral_potential_score,
                performance_vs_average=performance_vs_average,
                industry_benchmarks=industry_benchmarks,
                engagement_optimization=engagement_optimization,
                content_recommendations=content_recommendations,
                timing_recommendations=timing_recommendations,
                engagement_alerts=engagement_alerts,
                growth_opportunities=growth_opportunities,
                risk_factors=risk_factors,
                processing_time=processing_time,
                data_quality_score=data_quality_score,
                analysis_confidence=analysis_confidence
            )
            
            # Update historical data
            self._update_engagement_history(content_id, current_metrics)
            
            # Update analytics
            self.analysis_count += 1
            self.processing_times.append(processing_time)
            
            logger.info(f"Engagement analysis completed for {content_id}: "
                       f"{current_metrics.engagement_rate:.3f} engagement rate")
            
            return result
            
        except Exception as e:
            logger.error(f"Engagement analysis failed for {content_id}: {e}")
            
            return EngagementAnalysisResult(
                content_id=content_id,
                analysis_timestamp=datetime.now(),
                current_metrics=EngagementMetrics(
                    total_interactions=0,
                    engagement_rate=0.0,
                    authentic_engagement_rate=0.0
                ),
                audience_insights=AudienceInsights(
                    total_audience_size=0,
                    active_audience_percentage=0.0
                ),
                engagement_prediction=EngagementPrediction(
                    predicted_engagement_rate=0.0,
                    predicted_interactions=0,
                    confidence_score=0.0
                ),
                viral_potential_score=0.0,
                performance_vs_average=0.0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                data_quality_score=0.0,
                analysis_confidence=0.0
            )
    
    async def _calculate_engagement_metrics(
        self,
        content_id: str,
        engagement_data: Dict[str, Any],
        platform: str
    ) -> EngagementMetrics:
        """Calculate comprehensive engagement metrics."""        try:
            # Extract basic engagement numbers
            likes = engagement_data.get('likes', 0)
            comments = engagement_data.get('comments', 0)
            shares = engagement_data.get('shares', 0)
            saves = engagement_data.get('saves', 0)
            clicks = engagement_data.get('clicks', 0)
            views = engagement_data.get('views', 0)
            
            total_interactions = likes + comments + shares + saves + clicks
            reach = engagement_data.get('reach', views)
            
            # Calculate engagement rate
            engagement_rate = total_interactions / max(1, reach)
            
            # Calculate authentic engagement (excluding spam)
            spam_interactions = await self._detect_spam_engagement(engagement_data)
            authentic_interactions = max(0, total_interactions - spam_interactions)
            authentic_engagement_rate = authentic_interactions / max(1, reach)
            
            # Calculate quality metrics
            comment_sentiment = self._analyze_comment_sentiment(
                engagement_data.get('comment_texts', [])
            )
            
            response_rate = self._calculate_response_rate(engagement_data)
            conversation_depth = self._calculate_conversation_depth(engagement_data)
            
            # Calculate timing metrics
            engagement_velocity = self._calculate_engagement_velocity(content_id, engagement_data)
            peak_engagement_time = self._find_peak_engagement_time(engagement_data)
            engagement_duration = self._calculate_engagement_duration(engagement_data)
            
            # Calculate audience metrics
            unique_users = engagement_data.get('unique_users', int(total_interactions * 0.8))
            repeat_engagers = engagement_data.get('repeat_engagers', int(unique_users * 0.3))
            new_vs_returning_ratio = self._calculate_new_vs_returning_ratio(engagement_data)
            
            return EngagementMetrics(
                total_interactions=total_interactions,
                engagement_rate=engagement_rate,
                authentic_engagement_rate=authentic_engagement_rate,
                likes=likes,
                comments=comments,
                shares=shares,
                saves=saves,
                clicks=clicks,
                views=views,
                comment_sentiment=comment_sentiment,
                response_rate=response_rate,
                conversation_depth=conversation_depth,
                engagement_velocity=engagement_velocity,
                peak_engagement_time=peak_engagement_time,
                engagement_duration=engagement_duration,
                unique_users=unique_users,
                repeat_engagers=repeat_engagers,
                new_vs_returning_ratio=new_vs_returning_ratio
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement metrics: {e}")
            return EngagementMetrics(
                total_interactions=0,
                engagement_rate=0.0,
                authentic_engagement_rate=0.0
            )
    
    async def _analyze_audience_insights(
        self,
        content_id: str,
        audience_data: Dict[str, Any],
        engagement_data: Dict[str, Any]
    ) -> AudienceInsights:
        """Analyze audience behavior and demographics."""        try:
            total_audience_size = audience_data.get('total_followers', 1000)
            active_users = engagement_data.get('unique_users', 0)
            active_audience_percentage = active_users / max(1, total_audience_size)
            
            # Audience segmentation
            segment_distribution = self._segment_audience(audience_data, engagement_data)
            engagement_by_segment = self._calculate_segment_engagement(
                segment_distribution, engagement_data
            )
            
            # Behavior patterns
            optimal_posting_times = self._analyze_optimal_posting_times(audience_data)
            content_preferences = self._analyze_content_preferences(audience_data)
            interaction_patterns = self._analyze_interaction_patterns(engagement_data)
            
            # Demographics (anonymized aggregates)
            age_distribution = audience_data.get('age_distribution', {})
            geographic_distribution = audience_data.get('geographic_distribution', {})
            device_usage = audience_data.get('device_usage', {})
            
            # Growth metrics
            follower_growth_rate = audience_data.get('follower_growth_rate', 0.0)
            audience_retention_rate = audience_data.get('retention_rate', 0.8)
            churn_rate = 1.0 - audience_retention_rate
            
            return AudienceInsights(
                total_audience_size=total_audience_size,
                active_audience_percentage=active_audience_percentage,
                segment_distribution=segment_distribution,
                engagement_by_segment=engagement_by_segment,
                optimal_posting_times=optimal_posting_times,
                content_preferences=content_preferences,
                interaction_patterns=interaction_patterns,
                age_distribution=age_distribution,
                geographic_distribution=geographic_distribution,
                device_usage=device_usage,
                follower_growth_rate=follower_growth_rate,
                audience_retention_rate=audience_retention_rate,
                churn_rate=churn_rate
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze audience insights: {e}")
            return AudienceInsights(
                total_audience_size=0,
                active_audience_percentage=0.0
            )
    
    async def _predict_engagement(
        self,
        content_data: Dict[str, Any],
        current_metrics: EngagementMetrics,
        audience_insights: AudienceInsights,
        platform: str
    ) -> EngagementPrediction:
        """Predict future engagement performance."""        try:
            # Extract features for prediction
            features = self._extract_prediction_features(
                content_data, current_metrics, audience_insights, platform
            )
            
            # Simple prediction model (in production, would use trained ML model)
            base_engagement = current_metrics.engagement_rate
            
            # Content factors
            content_factors = {}
            content_type = content_data.get('content_type', 'text')
            if content_type in self.content_benchmarks:
                content_factors['content_type_boost'] = self.content_benchmarks[content_type]['avg_engagement'] / 0.03
            else:
                content_factors['content_type_boost'] = 1.0
            
            # Timing factors
            timing_factors = {}
            post_time = content_data.get('post_time', datetime.now())
            if post_time.hour in [7, 8, 12, 19, 20]:  # Peak hours
                timing_factors['optimal_timing'] = 1.2
            else:
                timing_factors['optimal_timing'] = 0.9
            
            # Audience factors
            audience_factors = {}
            if audience_insights.active_audience_percentage > 0.1:
                audience_factors['high_engagement_audience'] = 1.3
            else:
                audience_factors['low_engagement_audience'] = 0.8
            
            # Calculate predictions
            multiplier = (
                content_factors.get('content_type_boost', 1.0) * 
                timing_factors.get('optimal_timing', 1.0) * 
                audience_factors.get('high_engagement_audience', 1.0)
            )
            
            predicted_engagement_rate = min(1.0, base_engagement * multiplier)
            predicted_reach = int(audience_insights.total_audience_size * 0.3)  # Estimated reach
            predicted_interactions = int(predicted_engagement_rate * predicted_reach)
            
            # Detailed predictions
            predicted_likes = int(predicted_interactions * 0.7)
            predicted_comments = int(predicted_interactions * 0.15)
            predicted_shares = int(predicted_interactions * 0.1)
            
            # Confidence based on data quality and model performance
            confidence_score = min(1.0, audience_insights.active_audience_percentage * 2)
            
            # Optimization suggestions
            optimization_opportunities = []
            if timing_factors.get('optimal_timing', 1.0) < 1.0:
                optimization_opportunities.append("Post during peak engagement hours")
            
            if content_factors.get('content_type_boost', 1.0) < 1.0:
                optimization_opportunities.append("Consider higher-engagement content formats")
            
            predicted_improvement = max(0.0, (multiplier - 1.0) * 100)  # Percentage improvement
            
            return EngagementPrediction(
                predicted_engagement_rate=predicted_engagement_rate,
                predicted_interactions=predicted_interactions,
                confidence_score=confidence_score,
                predicted_likes=predicted_likes,
                predicted_comments=predicted_comments,
                predicted_shares=predicted_shares,
                predicted_reach=predicted_reach,
                content_factors=content_factors,
                timing_factors=timing_factors,
                audience_factors=audience_factors,
                optimization_opportunities=optimization_opportunities,
                predicted_improvement=predicted_improvement
            )
            
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return EngagementPrediction(
                predicted_engagement_rate=0.0,
                predicted_interactions=0,
                confidence_score=0.0
            )
    
    async def _detect_spam_engagement(self, engagement_data: Dict[str, Any]) -> int:
        """Detect spam or bot engagement."""        spam_indicators = 0
        
        # Check for suspicious patterns
        comments = engagement_data.get('comment_texts', [])
        if comments:
            # Generic comment detection
            generic_comments = ['nice', 'good', 'great', 'wow', 'amazing', '👍', '❤️']
            generic_count = sum(1 for comment in comments if comment.lower().strip() in generic_comments)
            if generic_count > len(comments) * 0.5:
                spam_indicators += int(len(comments) * 0.3)
        
        # Rapid engagement detection
        engagement_timestamps = engagement_data.get('engagement_timestamps', [])
        if len(engagement_timestamps) > 10:
            # Check for unnatural clustering
            time_diffs = []
            for i in range(1, len(engagement_timestamps)):
                diff = (engagement_timestamps[i] - engagement_timestamps[i-1]).total_seconds()
                time_diffs.append(diff)
            
            if np.std(time_diffs) < 5:  # Very regular timing suggests bots
                spam_indicators += int(len(engagement_timestamps) * 0.2)
        
        return spam_indicators
    
    def _analyze_comment_sentiment(self, comments: List[str]) -> float:
        """Analyze sentiment of comments."""        if not comments:
            return 0.0
        
        positive_words = {'good', 'great', 'amazing', 'love', 'awesome', 'perfect', 'excellent'}
        negative_words = {'bad', 'hate', 'terrible', 'awful', 'worst', 'sucks', 'horrible'}
        
        sentiment_scores = []
        for comment in comments:
            comment_lower = comment.lower()
            positive_count = sum(1 for word in positive_words if word in comment_lower)
            negative_count = sum(1 for word in negative_words if word in comment_lower)
            
            if positive_count + negative_count > 0:
                sentiment = (positive_count - negative_count) / (positive_count + negative_count)
            else:
                sentiment = 0.0
            
            sentiment_scores.append(sentiment)
        
        return np.mean(sentiment_scores) if sentiment_scores else 0.0
    
    def _calculate_response_rate(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate creator response rate to comments."""        total_comments = engagement_data.get('comments', 0)
        creator_responses = engagement_data.get('creator_responses', 0)
        
        if total_comments == 0:
            return 0.0
        
        return creator_responses / total_comments
    
    def _calculate_conversation_depth(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate average conversation thread depth."""        comment_threads = engagement_data.get('comment_threads', [])
        
        if not comment_threads:
            return 0.0
        
        thread_depths = [len(thread) for thread in comment_threads]
        return np.mean(thread_depths)
    
    def _calculate_engagement_velocity(self, content_id: str, engagement_data: Dict[str, Any]) -> float:
        """Calculate engagement growth velocity."""        # Simple implementation - in production would track over time
        total_interactions = engagement_data.get('total_interactions', 0)
        time_since_post = engagement_data.get('hours_since_post', 1)
        
        return total_interactions / max(1, time_since_post)
    
    def _find_peak_engagement_time(self, engagement_data: Dict[str, Any]) -> Optional[datetime]:
        """Find peak engagement time."""        engagement_by_hour = engagement_data.get('engagement_by_hour', {})
        
        if not engagement_by_hour:
            return None
        
        peak_hour = max(engagement_by_hour.keys(), key=lambda h: engagement_by_hour[h])
        
        # Return today's date with peak hour
        today = datetime.now().date()
        return datetime.combine(today, datetime.min.time()).replace(hour=int(peak_hour))
    
    def _calculate_engagement_duration(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate how long engagement activity lasts."""        engagement_timestamps = engagement_data.get('engagement_timestamps', [])
        
        if len(engagement_timestamps) < 2:
            return 0.0
        
        first_engagement = min(engagement_timestamps)
        last_engagement = max(engagement_timestamps)
        
        duration = (last_engagement - first_engagement).total_seconds() / 3600  # Hours
        return duration
    
    def _calculate_new_vs_returning_ratio(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate ratio of new vs returning users."""        new_users = engagement_data.get('new_users', 0)
        returning_users = engagement_data.get('returning_users', 0)
        
        total_users = new_users + returning_users
        if total_users == 0:
            return 0.5  # Default neutral ratio
        
        return new_users / total_users
    
    def _segment_audience(
        self,
        audience_data: Dict[str, Any],
        engagement_data: Dict[str, Any]
    ) -> Dict[AudienceSegment, float]:
        """Segment audience based on engagement patterns."""        # Simplified segmentation - in production would use ML clustering
        total_audience = audience_data.get('total_followers', 1000)
        
        # Estimate segment sizes
        segments = {
            AudienceSegment.CORE_FANS: 0.15,      # 15% highly engaged
            AudienceSegment.CASUAL_FOLLOWERS: 0.35,  # 35% moderately engaged
            AudienceSegment.NEW_AUDIENCE: 0.20,    # 20% new followers
            AudienceSegment.TRENDING_VIEWERS: 0.15,  # 15% from trends
            AudienceSegment.ORGANIC_DISCOVERY: 0.10,  # 10% organic discovery
            AudienceSegment.PAID_AUDIENCE: 0.05    # 5% from paid promotion
        }
        
        return segments
    
    def _calculate_segment_engagement(
        self,
        segments: Dict[AudienceSegment, float],
        engagement_data: Dict[str, Any]
    ) -> Dict[AudienceSegment, float]:
        """Calculate engagement rates by audience segment."""        # Estimated engagement rates by segment
        engagement_rates = {
            AudienceSegment.CORE_FANS: 0.12,      # High engagement
            AudienceSegment.CASUAL_FOLLOWERS: 0.04,  # Medium engagement
            AudienceSegment.NEW_AUDIENCE: 0.06,    # Curious, higher initial engagement
            AudienceSegment.TRENDING_VIEWERS: 0.03,  # Lower engagement
            AudienceSegment.ORGANIC_DISCOVERY: 0.05,  # Medium engagement
            AudienceSegment.PAID_AUDIENCE: 0.02    # Lowest engagement
        }
        
        return engagement_rates
    
    def _analyze_optimal_posting_times(self, audience_data: Dict[str, Any]) -> List[datetime]:
        """Analyze optimal posting times for audience."""        # Default optimal times based on general social media patterns
        today = datetime.now().date()
        optimal_times = [
            datetime.combine(today, datetime.min.time()).replace(hour=7),   # 7 AM
            datetime.combine(today, datetime.min.time()).replace(hour=12),  # 12 PM
            datetime.combine(today, datetime.min.time()).replace(hour=19),  # 7 PM
        ]
        
        return optimal_times
    
    def _analyze_content_preferences(self, audience_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audience content preferences."""        # Simulated content preferences
        preferences = {
            'video': 0.4,
            'image': 0.3,
            'text': 0.2,
            'carousel': 0.1
        }
        
        return preferences
    
    def _analyze_interaction_patterns(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audience interaction patterns."""        patterns = {
            'quick_engagers': 0.3,  # Engage within first hour
            'delayed_engagers': 0.4,  # Engage within 24 hours
            'lurkers': 0.3,  # View but don't engage
            'comment_to_like_ratio': 0.15,  # Comments per like
            'share_to_like_ratio': 0.08   # Shares per like
        }
        
        return patterns
    
    def _extract_prediction_features(
        self,
        content_data: Dict[str, Any],
        current_metrics: EngagementMetrics,
        audience_insights: AudienceInsights,
        platform: str
    ) -> np.ndarray:
        """Extract features for ML prediction."""        features = [
            current_metrics.engagement_rate,
            audience_insights.active_audience_percentage,
            audience_insights.follower_growth_rate,
            len(content_data.get('hashtags', [])),
            len(content_data.get('text_content', '')),
            1 if content_data.get('has_media', False) else 0,
            current_metrics.comment_sentiment,
            current_metrics.response_rate
        ]
        
        return np.array(features)
    
    def _calculate_viral_potential(
        self,
        current_metrics: EngagementMetrics,
        prediction: EngagementPrediction,
        content_data: Dict[str, Any]
    ) -> float:
        """Calculate viral potential score."""        factors = []
        
        # High engagement rate factor
        if current_metrics.engagement_rate > 0.06:
            factors.append(0.8)
        elif current_metrics.engagement_rate > 0.03:
            factors.append(0.6)
        else:
            factors.append(0.3)
        
        # Share rate factor
        total_interactions = current_metrics.total_interactions
        if total_interactions > 0:
            share_rate = current_metrics.shares / total_interactions
            factors.append(min(1.0, share_rate * 10))  # Shares are strong viral indicator
        else:
            factors.append(0.2)
        
        # Growth velocity factor
        if current_metrics.engagement_velocity > 100:  # High velocity
            factors.append(0.9)
        elif current_metrics.engagement_velocity > 50:
            factors.append(0.6)
        else:
            factors.append(0.3)
        
        # Content type factor
        content_type = content_data.get('content_type', 'text')
        if content_type in ['video', 'carousel']:
            factors.append(0.8)
        elif content_type == 'image':
            factors.append(0.6)
        else:
            factors.append(0.4)
        
        # Prediction confidence factor
        factors.append(prediction.confidence_score)
        
        return np.mean(factors)
    
    def _compare_performance_to_average(self, content_id: str, metrics: EngagementMetrics) -> float:
        """Compare performance to user's historical average."""        # Get historical performance (simplified)
        if content_id in self.engagement_history:
            historical_rates = [m.engagement_rate for m in self.engagement_history[content_id]]
            if historical_rates:
                avg_rate = np.mean(historical_rates)
                if avg_rate > 0:
                    return (metrics.engagement_rate - avg_rate) / avg_rate
        
        return 0.0  # No historical data
    
    def _benchmark_against_industry(
        self,
        metrics: EngagementMetrics,
        platform: str,
        content_type: str
    ) -> Dict[str, float]:
        """Benchmark against industry standards."""        benchmarks = {}
        
        # Platform benchmarks
        if platform in self.industry_benchmarks:
            platform_benchmarks = self.industry_benchmarks[platform]
            user_rate = metrics.engagement_rate
            
            if user_rate >= platform_benchmarks['excellent']:
                benchmarks['platform_performance'] = 'excellent'
            elif user_rate >= platform_benchmarks['good']:
                benchmarks['platform_performance'] = 'good'
            elif user_rate >= platform_benchmarks['average']:
                benchmarks['platform_performance'] = 'average'
            else:
                benchmarks['platform_performance'] = 'poor'
        
        # Content type benchmarks
        if content_type in self.content_benchmarks:
            content_benchmark = self.content_benchmarks[content_type]['avg_engagement']
            benchmarks['content_type_ratio'] = metrics.engagement_rate / content_benchmark
        
        return benchmarks
    
    def _generate_engagement_optimization(
        self,
        metrics: EngagementMetrics,
        insights: AudienceInsights,
        prediction: EngagementPrediction
    ) -> List[str]:
        """Generate engagement optimization recommendations."""        recommendations = []
        
        # Comment engagement
        if metrics.response_rate < 0.3:
            recommendations.append("Increase response rate to comments to boost engagement")
        
        # Posting timing
        if insights.optimal_posting_times:
            recommendations.append("Post during optimal times for your audience")
        
        # Content format
        if 'video' in insights.content_preferences and insights.content_preferences['video'] > 0.3:
            recommendations.append("Create more video content - your audience prefers it")
        
        # Engagement velocity
        if metrics.engagement_velocity < 10:
            recommendations.append("Improve content to generate faster initial engagement")
        
        # Authenticity
        auth_rate = metrics.authentic_engagement_rate
        if auth_rate < metrics.engagement_rate * 0.8:
            recommendations.append("Focus on authentic engagement to improve quality")
        
        return recommendations[:5]
    
    def _generate_content_recommendations(
        self,
        metrics: EngagementMetrics,
        insights: AudienceInsights,
        benchmarks: Dict[str, float]
    ) -> List[str]:
        """Generate content strategy recommendations."""        recommendations = []
        
        # Content preferences
        top_preference = max(insights.content_preferences.items(), key=lambda x: x[1])
        recommendations.append(f"Focus on {top_preference[0]} content - highest audience preference")
        
        # Conversation starters
        if metrics.conversation_depth < 2.0:
            recommendations.append("Ask more questions to increase conversation depth")
        
        # Shareability
        if metrics.shares < metrics.total_interactions * 0.1:
            recommendations.append("Create more shareable content to increase reach")
        
        # Sentiment improvement
        if metrics.comment_sentiment < 0.5:
            recommendations.append("Focus on positive, uplifting content to improve sentiment")
        
        return recommendations[:4]
    
    def _generate_timing_recommendations(
        self,
        insights: AudienceInsights,
        engagement_data: Dict[str, Any]
    ) -> List[str]:
        """Generate timing optimization recommendations."""        recommendations = []
        
        # Optimal posting times
        if insights.optimal_posting_times:
            times = [t.strftime('%I %p') for t in insights.optimal_posting_times[:3]]
            recommendations.append(f"Post at optimal times: {', '.join(times)}")
        
        # Consistency
        recommendations.append("Maintain consistent posting schedule for better engagement")
        
        # Real-time engagement
        recommendations.append("Engage with audience within first hour of posting")
        
        return recommendations
    
    def _generate_engagement_alerts(
        self,
        metrics: EngagementMetrics,
        performance_vs_average: float
    ) -> List[str]:
        """Generate engagement alerts."""        alerts = []
        
        # Performance drops
        if performance_vs_average < -0.3:
            alerts.append("Engagement significantly below average - investigate content strategy")
        
        # Low authenticity
        if metrics.authentic_engagement_rate < metrics.engagement_rate * 0.7:
            alerts.append("High spam/bot engagement detected - monitor for fake interactions")
        
        # Low response rate
        if metrics.response_rate < 0.1:
            alerts.append("Very low response rate - increase community interaction")
        
        return alerts
    
    def _identify_growth_opportunities(
        self,
        insights: AudienceInsights,
        prediction: EngagementPrediction
    ) -> List[str]:
        """Identify audience growth opportunities."""        opportunities = []
        
        # High potential improvement
        if prediction.predicted_improvement > 20:
            opportunities.append("High growth potential with content optimization")
        
        # Underutilized segments
        for segment, engagement in insights.engagement_by_segment.items():
            if engagement > 0.08:  # High-engagement segment
                opportunities.append(f"Expand content for {segment.value} - high engagement potential")
        
        # Geographic expansion
        if insights.geographic_distribution:
            top_regions = sorted(insights.geographic_distribution.items(), 
                               key=lambda x: x[1], reverse=True)[:3]
            opportunities.append(f"Consider content for top regions: {', '.join([r[0] for r in top_regions])}")
        
        return opportunities[:3]
    
    def _identify_risk_factors(
        self,
        metrics: EngagementMetrics,
        insights: AudienceInsights
    ) -> List[str]:
        """Identify engagement risk factors."""        risks = []
        
        # High churn rate
        if insights.churn_rate > 0.3:
            risks.append("High audience churn rate - focus on retention strategies")
        
        # Low active audience
        if insights.active_audience_percentage < 0.05:
            risks.append("Very low active audience percentage - reengage dormant followers")
        
        # Declining engagement velocity
        if metrics.engagement_velocity < 5:
            risks.append("Low engagement velocity - content may not be resonating")
        
        # Poor comment sentiment
        if metrics.comment_sentiment < -0.2:
            risks.append("Negative comment sentiment - monitor brand reputation")
        
        return risks[:3]
    
    def _calculate_data_quality(
        self,
        engagement_data: Dict[str, Any],
        audience_data: Dict[str, Any]
    ) -> float:
        """Calculate data quality score."""        quality_factors = []
        
        # Engagement data completeness
        required_engagement_fields = ['likes', 'comments', 'shares', 'views']
        present_fields = sum(1 for field in required_engagement_fields 
                           if field in engagement_data and engagement_data[field] is not None)
        quality_factors.append(present_fields / len(required_engagement_fields))
        
        # Audience data completeness
        required_audience_fields = ['total_followers', 'age_distribution']
        present_audience_fields = sum(1 for field in required_audience_fields 
                                    if field in audience_data and audience_data[field] is not None)
        quality_factors.append(present_audience_fields / len(required_audience_fields))
        
        # Data recency
        last_update = engagement_data.get('last_updated', datetime.now() - timedelta(days=7))
        hours_old = (datetime.now() - last_update).total_seconds() / 3600
        recency_score = max(0.0, 1.0 - hours_old / 168)  # 1 week = 0 score
        quality_factors.append(recency_score)
        
        return np.mean(quality_factors)
    
    def _calculate_analysis_confidence(
        self,
        metrics: EngagementMetrics,
        data_quality: float
    ) -> float:
        """Calculate analysis confidence score."""        confidence_factors = []
        
        # Data quality factor
        confidence_factors.append(data_quality)
        
        # Sample size factor
        if metrics.total_interactions > 100:
            confidence_factors.append(0.9)
        elif metrics.total_interactions > 20:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)
        
        # Unique users factor
        if metrics.unique_users > 50:
            confidence_factors.append(0.9)
        elif metrics.unique_users > 10:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        return np.mean(confidence_factors)
    
    def _update_engagement_history(self, content_id: str, metrics: EngagementMetrics) -> None:
        """Update engagement history for analysis."""        self.engagement_history[content_id].append(metrics)
        
        # Keep only recent history (last 50 entries)
        if len(self.engagement_history[content_id]) > 50:
            self.engagement_history[content_id] = self.engagement_history[content_id][-50:]
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get engagement analysis analytics and performance metrics."""        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "total_analyses": self.analysis_count,
            "total_predictions": self.prediction_count,
            "average_processing_time": avg_processing_time,
            "prediction_enabled": self.enable_prediction,
            "realtime_monitoring": self.enable_realtime_monitoring,
            "spam_detection_threshold": self.spam_detection_threshold,
            "prediction_model": self.prediction_model_type,
            "tracked_content_count": len(self.engagement_history),
            "processing_time_percentiles": {
                "p50": np.percentile(self.processing_times, 50) if self.processing_times else 0,
                "p90": np.percentile(self.processing_times, 90) if self.processing_times else 0,
                "p99": np.percentile(self.processing_times, 99) if self.processing_times else 0
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources and clear caches."""        self.engagement_history.clear()
        self.audience_data.clear()
        self.performance_baselines.clear()
        self.processing_times.clear()
        
        logger.info("EngagementAnalyzer cleanup completed")
