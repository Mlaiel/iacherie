"""Distribution Strategy Engine

Enterprise-grade AI-powered engine for determining optimal content distribution strategies.
Analyzes audience data, platform performance, content characteristics, and market trends
to generate sophisticated multi-platform distribution recommendations.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and protected. Unauthorized use, reproduction, 
or distribution is strictly prohibited and will result in legal action.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
import joblib
import xgboost as xgb
import lightgbm as lgb
from scipy.optimize import minimize
import networkx as nx

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import asyncio
import aioredis

from ....core.database import get_db
from ....core.config import settings
from ....core.logging import get_logger
from ....utils.monitoring import MetricsCollector, track_performance
from ....utils.ml import MLPipeline, FeatureEngineering, ModelEvaluator
from ....models.content import ContentModel, ContentType
from ....models.user import UserModel
from ....models.analytics import (
    AnalyticsModel, 
    PlatformPerformanceModel, 
    AudienceInsightsModel,
    TrendAnalysisModel,
    CompetitorAnalysisModel
)
from .platform_manager import PlatformType


logger = get_logger(__name__)
metrics = MetricsCollector("distribution.strategy_engine")


class StrategyType(str, Enum):
    """Advanced distribution strategy types with business objectives"""    MAXIMUM_REACH = "maximum_reach"
    ENGAGEMENT_FOCUSED = "engagement_focused"
    REVENUE_OPTIMIZED = "revenue_optimized"
    BRAND_BUILDING = "brand_building"
    VIRAL_POTENTIAL = "viral_potential"
    CROSS_PROMOTION = "cross_promotion"
    NICHE_TARGETING = "niche_targeting"
    GROWTH_HACKING = "growth_hacking"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    SEASONAL_OPTIMIZATION = "seasonal_optimization"
    INFLUENCER_OUTREACH = "influencer_outreach"
    CONVERSION_FOCUSED = "conversion_focused"


class AudienceSegment(str, Enum):
    """Sophisticated audience segments with behavioral patterns"""    MUSIC_LOVERS = "music_lovers"
    CONTENT_CREATORS = "content_creators"
    BUSINESS_PROFESSIONALS = "business_professionals"
    LIFESTYLE_ENTHUSIASTS = "lifestyle_enthusiasts"
    TECH_ENTHUSIASTS = "tech_enthusiasts"
    ENTERTAINMENT_SEEKERS = "entertainment_seekers"
    EDUCATIONAL_SEEKERS = "educational_seekers"
    GAMERS = "gamers"
    FITNESS_COMMUNITY = "fitness_community"
    ARTISTS_DESIGNERS = "artists_designers"
    ENTREPRENEURS = "entrepreneurs"
    MILLENNIALS = "millennials"
    GEN_Z = "gen_z"
    EARLY_ADOPTERS = "early_adopters"
    TREND_SETTERS = "trend_setters"


class OptimizationObjective(str, Enum):
    """Multi-objective optimization targets"""    REACH = "reach"
    ENGAGEMENT = "engagement"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    BRAND_AWARENESS = "brand_awareness"
    FOLLOWER_GROWTH = "follower_growth"
    CLICK_THROUGH = "click_through"
    TIME_SPENT = "time_spent"
    SHARES = "shares"
    SAVES = "saves"
    COMMENTS = "comments"
    MENTIONS = "mentions"


@dataclass
class PlatformMetrics:
    """Enhanced platform performance metrics with predictive analytics"""    platform: PlatformType
    reach_score: float
    engagement_rate: float
    conversion_rate: float
    revenue_per_view: float
    audience_overlap: float
    posting_frequency: int
    optimal_times: List[int]  # Hours of day
    seasonal_trends: Dict[str, float]
    competitor_performance: Dict[str, float]
    trending_topics: List[str] = field(default_factory=list)
    hashtag_performance: Dict[str, float] = field(default_factory=dict)
    content_type_performance: Dict[str, float] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    growth_velocity: float = 0.0
    churn_rate: float = 0.0
    lifetime_value: float = 0.0


@dataclass
class ContentAnalysis:
    """Comprehensive content characteristics analysis with AI insights"""    content_type: ContentType
    duration: Optional[float]
    quality_score: float
    trending_topics: List[str]
    hashtag_performance: Dict[str, float]
    audience_sentiment: float
    virality_score: float
    monetization_potential: float
    content_category: str
    emotion_analysis: Dict[str, float] = field(default_factory=dict)
    complexity_score: float = 0.0
    readability_score: float = 0.0
    visual_appeal_score: float = 0.0
    audio_quality_score: float = 0.0
    brand_alignment_score: float = 0.0
    seasonal_relevance: float = 0.0
    competitive_advantage: float = 0.0


@dataclass
class MarketTrends:
    """Real-time market trends and competitive intelligence"""    trending_hashtags: Dict[str, float]
    viral_content_patterns: List[Dict[str, Any]]
    competitor_strategies: Dict[str, Any]
    platform_algorithm_changes: Dict[PlatformType, Dict[str, Any]]
    audience_behavior_shifts: Dict[str, float]
    seasonal_patterns: Dict[str, float]
    emerging_platforms: List[str]
    content_saturation_levels: Dict[str, float]


class DistributionStrategy(BaseModel):
    """Advanced distribution strategy with detailed recommendations"""    strategy_type: StrategyType
    recommended_platforms: List[PlatformType]
    priority_order: List[PlatformType]
    timing_recommendations: Dict[PlatformType, List[datetime]]
    content_adaptations: Dict[PlatformType, Dict[str, Any]]
    hashtag_recommendations: Dict[PlatformType, List[str]]
    audience_targeting: Dict[PlatformType, Dict[str, Any]]
    expected_metrics: Dict[PlatformType, Dict[str, float]]
    confidence_score: float
    reasoning: str
    
    # Advanced strategy components
    budget_allocation: Dict[PlatformType, float] = Field(default_factory=dict)
    cross_promotion_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    influencer_collaboration_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    competitive_positioning: Dict[str, Any] = Field(default_factory=dict)
    risk_assessment: Dict[str, float] = Field(default_factory=dict)
    roi_projections: Dict[PlatformType, Dict[str, float]] = Field(default_factory=dict)
    a_b_testing_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v


class DistributionStrategyEngine:
    """    Enterprise-grade AI-powered engine for optimizing content distribution strategies.
    
    Features:
    - Multi-objective optimization using advanced ML algorithms
    - Real-time market trend analysis and competitive intelligence
    - Sophisticated audience segmentation and behavioral analysis
    - Cross-platform synergy optimization
    - Revenue and ROI prediction models
    - A/B testing and experimentation framework
    - Influencer collaboration recommendations
    - Risk assessment and mitigation strategies
    """    
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        self.models = self._load_ml_models()
        self.platform_analyzers = self._initialize_platform_analyzers()
        self.content_analyzers = self._initialize_content_analyzers()
        self.market_intelligence = self._initialize_market_intelligence()
        self.feature_engineer = FeatureEngineering()
        self.ml_pipeline = MLPipeline()
        self.model_evaluator = ModelEvaluator()
        
        # Advanced analytics components
        self.audience_clusterer = KMeans(n_clusters=10, random_state=42)
        self.trend_analyzer = self._initialize_trend_analyzer()
        self.competitor_analyzer = self._initialize_competitor_analyzer()
        self.viral_predictor = self._initialize_viral_predictor()
        
    async def __aenter__(self):
        """Async context manager entry"""        self.redis_client = await aioredis.from_url(settings.REDIS_URL)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        if self.redis_client:
            await self.redis_client.close()
    
    def _load_ml_models(self) -> Dict[str, Any]:
        """Load sophisticated pre-trained ML models for strategy optimization"""        models = {}
        
        try:
            # Load ensemble models for different metrics
            models["engagement_ensemble"] = {
                "random_forest": joblib.load("models/engagement_rf.pkl"),
                "gradient_boost": joblib.load("models/engagement_gb.pkl"),
                "xgboost": joblib.load("models/engagement_xgb.pkl"),
                "neural_net": joblib.load("models/engagement_nn.pkl")
            }
            
            models["reach_ensemble"] = {
                "random_forest": joblib.load("models/reach_rf.pkl"),
                "gradient_boost": joblib.load("models/reach_gb.pkl"),
                "lightgbm": joblib.load("models/reach_lgb.pkl")
            }
            
            models["revenue_ensemble"] = {
                "xgboost": joblib.load("models/revenue_xgb.pkl"),
                "gradient_boost": joblib.load("models/revenue_gb.pkl"),
                "linear_regression": joblib.load("models/revenue_lr.pkl")
            }
            
            models["virality_ensemble"] = {
                "random_forest": joblib.load("models/virality_rf.pkl"),
                "svm": joblib.load("models/virality_svm.pkl"),
                "neural_net": joblib.load("models/virality_nn.pkl")
            }
            
            # Load platform-specific models
            for platform in PlatformType:
                models[f"{platform.value}_optimizer"] = joblib.load(
                    f"models/{platform.value}_optimizer.pkl"
                )
            
            # Load feature engineering components
            models["feature_scaler"] = joblib.load("models/feature_scaler.pkl")
            models["label_encoders"] = joblib.load("models/label_encoders.pkl")
            models["pca_transformer"] = joblib.load("models/pca_transformer.pkl")
            
            # Load advanced models
            models["audience_clusterer"] = joblib.load("models/audience_clusterer.pkl")
            models["trend_predictor"] = joblib.load("models/trend_predictor.pkl")
            models["sentiment_analyzer"] = joblib.load("models/sentiment_analyzer.pkl")
            models["content_classifier"] = joblib.load("models/content_classifier.pkl")
            
            logger.info("Successfully loaded all ML models")
            
        except FileNotFoundError as e:
            logger.warning(f"ML models not found: {e}, using fallback algorithms")
            models = self._create_fallback_models()
        
        return models
    
    def _create_fallback_models(self) -> Dict[str, Any]:
        """Create sophisticated fallback models when trained models are not available"""        fallback_models = {}
        
        # Create basic ensemble models
        fallback_models["engagement_ensemble"] = {
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "gradient_boost": GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        fallback_models["reach_ensemble"] = {
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "xgboost": xgb.XGBRegressor(n_estimators=100, random_state=42)
        }
        
        fallback_models["revenue_ensemble"] = {
            "gradient_boost": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "lightgbm": lgb.LGBMRegressor(n_estimators=100, random_state=42)
        }
        
        # Create feature preprocessing components
        fallback_models["feature_scaler"] = StandardScaler()
        fallback_models["label_encoders"] = {}
        fallback_models["audience_clusterer"] = KMeans(n_clusters=8, random_state=42)
        
        logger.info("Created fallback ML models")
        return fallback_models
    
    def _initialize_platform_analyzers(self) -> Dict[PlatformType, Any]:
        """Initialize platform-specific analyzers"""        analyzers = {}
        
        for platform in PlatformType:
            analyzers[platform] = {
                "algorithm_tracker": self._create_algorithm_tracker(platform),
                "performance_predictor": self._create_performance_predictor(platform),
                "audience_analyzer": self._create_audience_analyzer(platform),
                "trend_detector": self._create_trend_detector(platform),
                "competitor_monitor": self._create_competitor_monitor(platform)
            }
        
        return analyzers
    
    def _initialize_content_analyzers(self) -> Dict[str, Any]:
        """Initialize content analysis components"""        return {
            "sentiment_analyzer": self._create_sentiment_analyzer(),
            "emotion_detector": self._create_emotion_detector(),
            "quality_assessor": self._create_quality_assessor(),
            "trending_detector": self._create_trending_detector(),
            "viral_predictor": self._create_viral_predictor(),
            "monetization_evaluator": self._create_monetization_evaluator()
        }
    
    def _initialize_market_intelligence(self) -> Dict[str, Any]:
        """Initialize market intelligence and trend analysis"""        return {
            "trend_aggregator": self._create_trend_aggregator(),
            "competitor_tracker": self._create_competitor_tracker(),
            "market_analyzer": self._create_market_analyzer(),
            "opportunity_finder": self._create_opportunity_finder(),
            "risk_assessor": self._create_risk_assessor()
        }
    
    def _initialize_trend_analyzer(self):
        """Initialize trend analysis system"""        return {
            "hashtag_tracker": self._create_hashtag_tracker(),
            "viral_content_detector": self._create_viral_content_detector(),
            "seasonal_analyzer": self._create_seasonal_analyzer(),
            "emerging_trend_predictor": self._create_emerging_trend_predictor()
        }
    
    def _initialize_competitor_analyzer(self):
        """Initialize competitor analysis system"""        return {
            "strategy_detector": self._create_strategy_detector(),
            "performance_benchmarker": self._create_performance_benchmarker(),
            "content_gap_analyzer": self._create_content_gap_analyzer(),
            "opportunity_mapper": self._create_opportunity_mapper()
        }
    
    def _initialize_viral_predictor(self):
        """Initialize viral content prediction system"""        return {
            "pattern_matcher": self._create_pattern_matcher(),
            "timing_optimizer": self._create_timing_optimizer(),
            "network_analyzer": self._create_network_analyzer(),
            "cascade_predictor": self._create_cascade_predictor()
        }
    
    @track_performance("strategy.generate_strategy")
    async def generate_strategy(
        self,
        content_id: int,
        user_id: int,
        strategy_type: StrategyType,
        target_audiences: List[AudienceSegment],
        budget_constraints: Optional[Dict[str, float]] = None,
        time_constraints: Optional[Dict[str, Any]] = None,
        platform_preferences: Optional[List[PlatformType]] = None,
        optimization_objectives: List[OptimizationObjective] = None
    ) -> DistributionStrategy:
        """        Generate sophisticated distribution strategy using advanced AI algorithms.
        
        This method performs:
        - Multi-dimensional content analysis
        - Advanced audience segmentation and targeting
        - Platform algorithm optimization
        - Competitive intelligence integration
        - Real-time market trend analysis
        - Multi-objective optimization
        - Risk assessment and mitigation
        - ROI prediction and budget optimization
        
        Args:
            content_id: Content to distribute
            user_id: User requesting strategy
            strategy_type: Type of strategy to optimize for
            target_audiences: Target audience segments
            budget_constraints: Budget limitations per platform
            time_constraints: Timing requirements and constraints
            platform_preferences: Preferred platforms (optional)
            optimization_objectives: Metrics to optimize for
            
        Returns:
            Comprehensive distribution strategy with detailed recommendations
        """        
        with metrics.timer("strategy.generation_time"):
            try:
                # Step 1: Comprehensive data gathering and analysis
                content_analysis = await self._analyze_content_comprehensive(content_id)
                user_profile = await self._analyze_user_profile(user_id)
                market_trends = await self._analyze_market_trends()
                competitor_intelligence = await self._analyze_competitors(user_id, content_analysis)
                platform_performance = await self._analyze_platform_performance(user_id)
                
                # Step 2: Advanced audience analysis and segmentation
                audience_insights = await self._analyze_target_audiences(
                    target_audiences, user_profile, content_analysis
                )
                
                # Step 3: Platform suitability analysis with AI optimization
                platform_rankings = await self._rank_platforms_advanced(
                    content_analysis,
                    audience_insights,
                    platform_performance,
                    strategy_type,
                    platform_preferences
                )
                
                # Step 4: Multi-objective optimization
                optimization_results = await self._multi_objective_optimization(
                    content_analysis,
                    platform_rankings,
                    budget_constraints,
                    optimization_objectives or [OptimizationObjective.ENGAGEMENT, OptimizationObjective.REACH]
                )
                
                # Step 5: Generate platform-specific recommendations
                platform_recommendations = await self._generate_platform_recommendations(
                    optimization_results,
                    content_analysis,
                    audience_insights,
                    market_trends
                )
                
                # Step 6: Timing optimization with advanced algorithms
                timing_recommendations = await self._optimize_timing_advanced(
                    optimization_results["recommended_platforms"],
                    audience_insights,
                    market_trends,
                    time_constraints
                )
                
                # Step 7: Content adaptation strategies
                content_adaptations = await self._generate_content_adaptations(
                    content_analysis,
                    optimization_results["recommended_platforms"],
                    market_trends
                )
                
                # Step 8: Hashtag and SEO optimization
                hashtag_strategy = await self._optimize_hashtags_advanced(
                    content_analysis,
                    optimization_results["recommended_platforms"],
                    market_trends
                )
                
                # Step 9: Audience targeting optimization
                targeting_strategy = await self._optimize_audience_targeting(
                    audience_insights,
                    optimization_results["recommended_platforms"],
                    budget_constraints
                )
                
                # Step 10: Performance prediction and ROI analysis
                performance_predictions = await self._predict_performance_comprehensive(
                    content_analysis,
                    optimization_results,
                    platform_recommendations,
                    timing_recommendations
                )
                
                # Step 11: Risk assessment and mitigation
                risk_analysis = await self._assess_risks_comprehensive(
                    optimization_results,
                    market_trends,
                    competitor_intelligence
                )
                
                # Step 12: Advanced strategy components
                cross_promotion = await self._identify_cross_promotion_opportunities(
                    optimization_results["recommended_platforms"],
                    content_analysis,
                    user_profile
                )
                
                influencer_opportunities = await self._identify_influencer_opportunities(
                    content_analysis,
                    audience_insights,
                    budget_constraints
                )
                
                a_b_testing_plan = await self._generate_ab_testing_plan(
                    content_analysis,
                    optimization_results["recommended_platforms"],
                    performance_predictions
                )
                
                # Step 13: Generate comprehensive strategy
                strategy = DistributionStrategy(
                    strategy_type=strategy_type,
                    recommended_platforms=optimization_results["recommended_platforms"],
                    priority_order=optimization_results["priority_order"],
                    timing_recommendations=timing_recommendations,
                    content_adaptations=content_adaptations,
                    hashtag_recommendations=hashtag_strategy,
                    audience_targeting=targeting_strategy,
                    expected_metrics=performance_predictions,
                    confidence_score=optimization_results["confidence_score"],
                    reasoning=optimization_results["reasoning"],
                    budget_allocation=optimization_results.get("budget_allocation", {}),
                    cross_promotion_opportunities=cross_promotion,
                    influencer_collaboration_suggestions=influencer_opportunities,
                    competitive_positioning=competitor_intelligence,
                    risk_assessment=risk_analysis,
                    roi_projections=optimization_results.get("roi_projections", {}),
                    a_b_testing_recommendations=a_b_testing_plan,
                    follow_up_actions=await self._generate_follow_up_actions(optimization_results)
                )
                
                # Step 14: Cache strategy and update learning models
                await self._cache_strategy(content_id, user_id, strategy)
                await self._update_learning_models(content_analysis, strategy, optimization_results)
                
                metrics.increment("strategy.generation.success")
                logger.info(f"Generated advanced strategy for content {content_id} with {len(strategy.recommended_platforms)} platforms")
                
                return strategy
                
            except Exception as e:
                metrics.increment("strategy.generation.error")
                logger.error(f"Strategy generation failed for content {content_id}: {e}")
                
                # Return fallback strategy
                return await self._generate_fallback_strategy(
                    content_id, user_id, strategy_type, target_audiences
                )
    
    async def _analyze_content_comprehensive(self, content_id: int) -> ContentAnalysis:
        """Perform comprehensive content analysis using advanced AI"""        content = self.db.query(ContentModel).filter(ContentModel.id == content_id).first()
        if not content:
            raise ValueError(f"Content {content_id} not found")
        
        # Basic content features
        analysis = ContentAnalysis(
            content_type=content.content_type,
            duration=content.duration,
            quality_score=0.0,
            trending_topics=[],
            hashtag_performance={},
            audience_sentiment=0.0,
            virality_score=0.0,
            monetization_potential=0.0,
            content_category="general"
        )
        
        # Advanced AI analysis
        if self.content_analyzers:
            # Sentiment and emotion analysis
            if content.description:
                analysis.audience_sentiment = await self._analyze_sentiment(content.description)
                analysis.emotion_analysis = await self._analyze_emotions(content.description)
            
            # Quality assessment
            analysis.quality_score = await self._assess_content_quality(content)
            analysis.visual_appeal_score = await self._assess_visual_appeal(content)
            analysis.audio_quality_score = await self._assess_audio_quality(content)
            
            # Trend and virality analysis
            analysis.trending_topics = await self._extract_trending_topics(content)
            analysis.virality_score = await self._predict_virality(content)
            
            # Monetization potential
            analysis.monetization_potential = await self._assess_monetization_potential(content)
            
            # Advanced features
            analysis.complexity_score = await self._assess_complexity(content)
            analysis.readability_score = await self._assess_readability(content)
            analysis.seasonal_relevance = await self._assess_seasonal_relevance(content)
            analysis.competitive_advantage = await self._assess_competitive_advantage(content)
        
        return analysis
    
    async def _analyze_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Analyze user profile and historical performance"""        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get historical performance data
        historical_data = self.db.query(PlatformPerformanceModel).filter(
            PlatformPerformanceModel.user_id == user_id
        ).all()
        
        # Analyze audience insights
        audience_data = self.db.query(AudienceInsightsModel).filter(
            AudienceInsightsModel.user_id == user_id
        ).all()
        
        profile = {
            "user_type": getattr(user, 'user_type', 'creator'),
            "follower_counts": {},
            "engagement_rates": {},
            "posting_frequency": {},
            "best_performing_content": {},
            "audience_demographics": {},
            "brand_partnerships": [],
            "content_categories": [],
            "growth_trends": {},
            "platform_expertise": {}
        }
        
        # Process historical performance
        platform_performance = defaultdict(list)
        for perf in historical_data:
            platform_performance[perf.platform].append({
                "engagement_rate": perf.metrics.get("engagement_rate", 0),
                "reach": perf.metrics.get("reach", 0),
                "conversions": perf.metrics.get("conversions", 0),
                "timestamp": perf.created_at
            })
        
        # Calculate performance metrics per platform
        for platform, performances in platform_performance.items():
            if performances:
                profile["engagement_rates"][platform] = np.mean([p["engagement_rate"] for p in performances])
                profile["platform_expertise"][platform] = len(performances) / max(1, (datetime.utcnow() - min(p["timestamp"] for p in performances)).days)
        
        # Process audience insights
        for insight in audience_data:
            profile["audience_demographics"][insight.platform] = insight.demographics
        
        return profile
    
    async def _analyze_market_trends(self) -> MarketTrends:
        """Analyze current market trends and competitive landscape"""        trends = MarketTrends(
            trending_hashtags={},
            viral_content_patterns=[],
            competitor_strategies={},
            platform_algorithm_changes={},
            audience_behavior_shifts={},
            seasonal_patterns={},
            emerging_platforms=[],
            content_saturation_levels={}
        )
        
        # Get trending data from Redis cache or database
        if self.redis_client:
            # Get cached trend data
            cached_trends = await self.redis_client.get("market_trends:current")
            if cached_trends:
                trends_data = json.loads(cached_trends)
                trends.trending_hashtags = trends_data.get("trending_hashtags", {})
                trends.viral_content_patterns = trends_data.get("viral_content_patterns", [])
        
        # Get recent trend analysis from database
        recent_trends = self.db.query(TrendAnalysisModel).filter(
            TrendAnalysisModel.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        # Process trend data
        for trend in recent_trends:
            if trend.trend_type == "hashtag":
                trends.trending_hashtags[trend.trend_value] = trend.trend_score
            elif trend.trend_type == "content_pattern":
                trends.viral_content_patterns.append({
                    "pattern": trend.trend_value,
                    "score": trend.trend_score,
                    "platforms": trend.platforms
                })
        
        # Analyze seasonal patterns
        trends.seasonal_patterns = await self._analyze_seasonal_patterns()
        
        # Detect platform algorithm changes
        trends.platform_algorithm_changes = await self._detect_algorithm_changes()
        
        return trends
    
    async def _analyze_competitors(self, user_id: int, content_analysis: ContentAnalysis) -> Dict[str, Any]:
        """Analyze competitor strategies and performance"""        competitor_data = self.db.query(CompetitorAnalysisModel).filter(
            CompetitorAnalysisModel.user_id == user_id,
            CompetitorAnalysisModel.content_category == content_analysis.content_category
        ).all()
        
        analysis = {
            "top_competitors": [],
            "successful_strategies": [],
            "content_gaps": [],
            "opportunity_areas": [],
            "benchmark_metrics": {},
            "competitive_positioning": {}
        }
        
        # Process competitor data
        for competitor in competitor_data:
            analysis["top_competitors"].append({
                "competitor_id": competitor.competitor_id,
                "platform": competitor.platform,
                "performance_metrics": competitor.metrics,
                "content_strategy": competitor.strategy_analysis,
                "audience_overlap": competitor.audience_overlap
            })
        
        # Identify successful strategies
        analysis["successful_strategies"] = await self._identify_successful_strategies(competitor_data)
        
        # Find content gaps and opportunities
        analysis["content_gaps"] = await self._identify_content_gaps(competitor_data, content_analysis)
        analysis["opportunity_areas"] = await self._identify_opportunity_areas(competitor_data)
        
        return analysis
            "engagement_predictor": RandomForestRegressor(n_estimators=100),
            "reach_predictor": RandomForestRegressor(n_estimators=100),
            "revenue_predictor": RandomForestRegressor(n_estimators=100),
            "virality_predictor": RandomForestRegressor(n_estimators=100),
            "scaler": StandardScaler()
        }
    
    def _initialize_platform_analyzers(self) -> Dict[PlatformType, Any]:
        """Initialize platform-specific analyzers"""        return {
            PlatformType.YOUTUBE: self._create_youtube_analyzer(),
            PlatformType.INSTAGRAM: self._create_instagram_analyzer(),
            PlatformType.TIKTOK: self._create_tiktok_analyzer(),
            PlatformType.TWITTER: self._create_twitter_analyzer(),
            PlatformType.SPOTIFY: self._create_spotify_analyzer(),
            PlatformType.LINKEDIN: self._create_linkedin_analyzer()
        }
    
    def _create_youtube_analyzer(self) -> Dict[str, Any]:
        """YouTube-specific analysis configuration"""        return {
            "optimal_length": {"min": 60, "max": 600, "sweet_spot": 300},
            "best_times": [14, 15, 16, 17, 19, 20, 21],  # 2-5 PM, 7-9 PM
            "audience_peaks": {
                "weekdays": [17, 18, 19, 20],
                "weekends": [10, 11, 14, 15, 19, 20, 21]
            },
            "hashtag_weight": 0.3,
            "thumbnail_importance": 0.8,
            "title_optimization": True,
            "trending_topics_weight": 0.6
        }
    
    def _create_instagram_analyzer(self) -> Dict[str, Any]:
        """Instagram-specific analysis configuration"""        return {
            "optimal_length": {"min": 15, "max": 60, "sweet_spot": 30},
            "best_times": [11, 12, 13, 17, 18, 19],  # Lunch and evening
            "audience_peaks": {
                "weekdays": [8, 12, 17, 18, 19],
                "weekends": [10, 11, 12, 14, 15, 16]
            },
            "hashtag_weight": 0.9,
            "visual_quality_importance": 0.9,
            "story_engagement": True,
            "reels_priority": 0.8
        }
    
    def _create_tiktok_analyzer(self) -> Dict[str, Any]:
        """TikTok-specific analysis configuration"""        return {
            "optimal_length": {"min": 15, "max": 60, "sweet_spot": 30},
            "best_times": [6, 7, 8, 19, 20, 21, 22],  # Morning and evening
            "audience_peaks": {
                "weekdays": [6, 7, 19, 20, 21],
                "weekends": [9, 10, 11, 19, 20, 21, 22]
            },
            "hashtag_weight": 0.7,
            "trending_sounds": True,
            "viral_potential_high": True,
            "quick_engagement": 0.9
        }
    
    def _create_twitter_analyzer(self) -> Dict[str, Any]:
        """Twitter-specific analysis configuration"""        return {
            "optimal_length": {"min": 0, "max": 280, "sweet_spot": 100},
            "best_times": [8, 9, 12, 13, 17, 18],  # Work hours
            "audience_peaks": {
                "weekdays": [8, 9, 12, 17, 18],
                "weekends": [10, 11, 14, 15]
            },
            "hashtag_weight": 0.6,
            "real_time_relevance": True,
            "thread_potential": True,
            "news_cycle_awareness": 0.8
        }
    
    def _create_spotify_analyzer(self) -> Dict[str, Any]:
        """Spotify-specific analysis configuration"""        return {
            "optimal_length": {"min": 180, "max": 3600, "sweet_spot": 1200},
            "best_times": [7, 8, 12, 13, 17, 18, 22],  # Commute and relaxation
            "audience_peaks": {
                "weekdays": [7, 8, 12, 17, 18, 22],
                "weekends": [9, 10, 11, 14, 20, 21, 22]
            },
            "playlist_potential": True,
            "audio_quality_critical": True,
            "genre_matching": 0.9,
            "seasonal_trends": True
        }
    
    def _create_linkedin_analyzer(self) -> Dict[str, Any]:
        """LinkedIn-specific analysis configuration"""        return {
            "optimal_length": {"min": 0, "max": 1300, "sweet_spot": 150},
            "best_times": [8, 9, 12, 13, 17],  # Business hours
            "audience_peaks": {
                "weekdays": [8, 9, 12, 13, 17],
                "weekends": []  # Very low weekend activity
            },
            "professional_tone": True,
            "industry_relevance": 0.9,
            "networking_potential": 0.8,
            "thought_leadership": True
        }
    
    def _initialize_content_analyzers(self) -> Dict[ContentType, Any]:
        """Initialize content type analyzers"""        return {
            ContentType.AUDIO: self._create_audio_analyzer(),
            ContentType.VIDEO: self._create_video_analyzer(),
            ContentType.IMAGE: self._create_image_analyzer(),
            ContentType.TEXT: self._create_text_analyzer()
        }
    
    def _create_audio_analyzer(self) -> Dict[str, Any]:
        """Audio content analyzer"""        return {
            "platforms_priority": [
                PlatformType.SPOTIFY,
                PlatformType.YOUTUBE,
                PlatformType.INSTAGRAM,
                PlatformType.TIKTOK
            ],
            "quality_factors": ["bitrate", "sample_rate", "duration", "genre"],
            "viral_indicators": ["hook_strength", "tempo", "trend_alignment"],
            "monetization_platforms": [PlatformType.SPOTIFY, PlatformType.YOUTUBE]
        }
    
    def _create_video_analyzer(self) -> Dict[str, Any]:
        """Video content analyzer"""        return {
            "platforms_priority": [
                PlatformType.YOUTUBE,
                PlatformType.TIKTOK,
                PlatformType.INSTAGRAM,
                PlatformType.TWITTER
            ],
            "quality_factors": ["resolution", "fps", "duration", "editing_quality"],
            "viral_indicators": ["thumbnail_appeal", "hook_timing", "trend_following"],
            "monetization_platforms": [PlatformType.YOUTUBE, PlatformType.INSTAGRAM]
        }
    
    def _create_image_analyzer(self) -> Dict[str, Any]:
        """Image content analyzer"""        return {
            "platforms_priority": [
                PlatformType.INSTAGRAM,
                PlatformType.PINTEREST,
                PlatformType.TWITTER,
                PlatformType.LINKEDIN
            ],
            "quality_factors": ["resolution", "composition", "color_palette", "style"],
            "viral_indicators": ["visual_appeal", "trend_alignment", "meme_potential"],
            "monetization_platforms": [PlatformType.INSTAGRAM, PlatformType.PINTEREST]
        }
    
    def _create_text_analyzer(self) -> Dict[str, Any]:
        """Text content analyzer"""        return {
            "platforms_priority": [
                PlatformType.TWITTER,
                PlatformType.LINKEDIN,
                PlatformType.INSTAGRAM,
                PlatformType.FACEBOOK
            ],
            "quality_factors": ["readability", "engagement_hooks", "value_proposition"],
            "viral_indicators": ["shareability", "controversy_level", "timely_relevance"],
            "monetization_platforms": [PlatformType.LINKEDIN, PlatformType.TWITTER]
        }
    
    async def generate_distribution_strategy(
        self,
        user_id: int,
        content_id: int,
        strategy_type: StrategyType = StrategyType.MAXIMUM_REACH,
        target_audience: Optional[List[AudienceSegment]] = None
    ) -> DistributionStrategy:
        """        Generate optimized distribution strategy for content
        
        Args:
            user_id: User identifier
            content_id: Content identifier
            strategy_type: Type of strategy to optimize for
            target_audience: Target audience segments
            
        Returns:
            Optimized distribution strategy
        """        try:
            # Get user and content data
            user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
            content = self.db.query(ContentModel).filter(
                ContentModel.id == content_id
            ).first()
            
            if not user or not content:
                raise ValueError("User or content not found")
            
            # Analyze content characteristics
            content_analysis = await self._analyze_content(content)
            
            # Get user's platform performance history
            platform_metrics = await self._get_platform_metrics(user_id)
            
            # Get audience insights
            audience_insights = await self._get_audience_insights(
                user_id, target_audience
            )
            
            # Generate platform recommendations
            platform_recommendations = await self._recommend_platforms(
                content_analysis, platform_metrics, strategy_type, audience_insights
            )
            
            # Optimize timing for each platform
            timing_recommendations = await self._optimize_timing(
                platform_recommendations, audience_insights
            )
            
            # Generate content adaptations
            content_adaptations = await self._generate_content_adaptations(
                content, platform_recommendations
            )
            
            # Generate hashtag recommendations
            hashtag_recommendations = await self._generate_hashtag_recommendations(
                content, platform_recommendations
            )
            
            # Generate audience targeting
            audience_targeting = await self._generate_audience_targeting(
                platform_recommendations, audience_insights
            )
            
            # Predict expected metrics
            expected_metrics = await self._predict_performance_metrics(
                content_analysis, platform_recommendations, audience_insights
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                content_analysis, platform_metrics, expected_metrics
            )
            
            # Generate reasoning
            reasoning = await self._generate_strategy_reasoning(
                strategy_type, platform_recommendations, expected_metrics
            )
            
            return DistributionStrategy(
                strategy_type=strategy_type,
                recommended_platforms=platform_recommendations,
                priority_order=platform_recommendations,  # Already ordered by priority
                timing_recommendations=timing_recommendations,
                content_adaptations=content_adaptations,
                hashtag_recommendations=hashtag_recommendations,
                audience_targeting=audience_targeting,
                expected_metrics=expected_metrics,
                confidence_score=confidence_score,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Failed to generate distribution strategy: {e}")
            raise
    
    async def _analyze_content(self, content: ContentModel) -> ContentAnalysis:
        """Analyze content characteristics for strategy optimization"""        try:
            # Basic content information
            content_type = content.content_type
            duration = content.metadata.get("duration") if content.metadata else None
            
            # Calculate quality score based on metadata
            quality_score = await self._calculate_quality_score(content)
            
            # Extract trending topics from title and description
            trending_topics = await self._extract_trending_topics(
                content.title, content.description
            )
            
            # Analyze hashtag performance
            hashtag_performance = await self._analyze_hashtag_performance(
                content.hashtags or []
            )
            
            # Calculate audience sentiment
            audience_sentiment = await self._calculate_audience_sentiment(
                content.title, content.description
            )
            
            # Calculate virality score
            virality_score = await self._calculate_virality_score(content)
            
            # Calculate monetization potential
            monetization_potential = await self._calculate_monetization_potential(
                content
            )
            
            return ContentAnalysis(
                content_type=content_type,
                duration=duration,
                quality_score=quality_score,
                trending_topics=trending_topics,
                hashtag_performance=hashtag_performance,
                audience_sentiment=audience_sentiment,
                virality_score=virality_score,
                monetization_potential=monetization_potential
            )
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            raise
    
    async def _calculate_quality_score(self, content: ContentModel) -> float:
        """Calculate content quality score based on various factors"""        score = 0.5  # Base score
        
        if content.metadata:
            # Check technical quality indicators
            if content.metadata.get("resolution"):
                resolution = content.metadata["resolution"]
                if "1080p" in str(resolution) or "HD" in str(resolution):
                    score += 0.2
                elif "4K" in str(resolution) or "2160p" in str(resolution):
                    score += 0.3
            
            if content.metadata.get("bitrate"):
                bitrate = content.metadata["bitrate"]
                if isinstance(bitrate, (int, float)) and bitrate > 128000:
                    score += 0.1
            
            if content.metadata.get("fps"):
                fps = content.metadata["fps"]
                if isinstance(fps, (int, float)) and fps >= 30:
                    score += 0.1
        
        # Content completeness
        if content.title and len(content.title) > 10:
            score += 0.1
        
        if content.description and len(content.description) > 50:
            score += 0.1
        
        if content.hashtags and len(content.hashtags) > 3:
            score += 0.05
        
        if content.thumbnail_url:
            score += 0.05
        
        return min(1.0, score)
    
    async def _extract_trending_topics(
        self, title: str, description: Optional[str]
    ) -> List[str]:
        """Extract trending topics from content text"""        # This would integrate with a trending topics API or use NLP
        # For now, using a simplified keyword extraction
        
        text = f"{title} {description or ''}"
        
        # Common trending keywords in music/content creation
        trending_keywords = [
            "viral", "trending", "challenge", "remix", "cover", "reaction",
            "tutorial", "behind the scenes", "live", "acoustic", "unplugged",
            "collaboration", "duet", "mashup", "shorts", "tiktok", "instagram",
            "spotify", "playlist", "new music", "exclusive", "premiere"
        ]
        
        found_topics = []
        text_lower = text.lower()
        
        for keyword in trending_keywords:
            if keyword in text_lower:
                found_topics.append(keyword)
        
        return found_topics[:5]  # Return top 5 trending topics
    
    async def _analyze_hashtag_performance(
        self, hashtags: List[str]
    ) -> Dict[str, float]:
        """Analyze hashtag performance and popularity"""        hashtag_performance = {}
        
        # This would integrate with platform APIs to get real hashtag data
        # For now, using estimated scores based on hashtag characteristics
        
        for hashtag in hashtags:
            score = 0.5  # Base score
            
            # Length optimization
            if 5 <= len(hashtag) <= 20:
                score += 0.2
            
            # Check for music-related hashtags
            music_keywords = ["music", "song", "audio", "sound", "beat", "melody"]
            if any(keyword in hashtag.lower() for keyword in music_keywords):
                score += 0.2
            
            # Check for trending indicators
            trending_indicators = ["viral", "trending", "new", "2025", "challenge"]
            if any(indicator in hashtag.lower() for indicator in trending_indicators):
                score += 0.1
            
            hashtag_performance[hashtag] = min(1.0, score)
        
        return hashtag_performance
    
    async def _calculate_audience_sentiment(
        self, title: str, description: Optional[str]
    ) -> float:
        """Calculate audience sentiment for content"""        # This would use a sentiment analysis model
        # For now, using keyword-based approach
        
        text = f"{title} {description or ''}"
        
        positive_keywords = [
            "amazing", "awesome", "incredible", "beautiful", "perfect",
            "love", "best", "fantastic", "wonderful", "great"
        ]
        
        negative_keywords = [
            "hate", "terrible", "awful", "bad", "worst", "disappointing",
            "boring", "ugly", "stupid", "annoying"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.5
        
        sentiment_score = 0.5 + (positive_count - negative_count) / total_words
        return max(0.0, min(1.0, sentiment_score))
    
    async def _calculate_virality_score(self, content: ContentModel) -> float:
        """Calculate potential virality score"""        score = 0.3  # Base score
        
        # Content type impact
        if content.content_type == ContentType.VIDEO:
            score += 0.2
        elif content.content_type == ContentType.AUDIO:
            score += 0.15
        
        # Duration impact (shorter content often more viral)
        if content.metadata and content.metadata.get("duration"):
            duration = content.metadata["duration"]
            if isinstance(duration, (int, float)):
                if duration <= 30:  # Short content
                    score += 0.2
                elif duration <= 60:
                    score += 0.1
        
        # Title impact
        if content.title:
            viral_words = ["viral", "challenge", "reaction", "vs", "first time"]
            title_lower = content.title.lower()
            viral_count = sum(1 for word in viral_words if word in title_lower)
            score += viral_count * 0.1
        
        # Hashtag impact
        if content.hashtags:
            viral_hashtags = ["viral", "fyp", "trending", "challenge"]
            hashtag_text = " ".join(content.hashtags).lower()
            viral_hashtag_count = sum(
                1 for hashtag in viral_hashtags if hashtag in hashtag_text
            )
            score += viral_hashtag_count * 0.05
        
        return min(1.0, score)
    
    async def _calculate_monetization_potential(self, content: ContentModel) -> float:
        """Calculate monetization potential"""        score = 0.2  # Base score
        
        # Content type impact
        if content.content_type in [ContentType.AUDIO, ContentType.VIDEO]:
            score += 0.3
        elif content.content_type == ContentType.IMAGE:
            score += 0.1
        
        # Quality impact
        quality_score = await self._calculate_quality_score(content)
        score += quality_score * 0.3
        
        # Length impact (longer content often better for monetization)
        if content.metadata and content.metadata.get("duration"):
            duration = content.metadata["duration"]
            if isinstance(duration, (int, float)):
                if duration >= 300:  # 5+ minutes
                    score += 0.2
                elif duration >= 60:  # 1+ minute
                    score += 0.1
        
        return min(1.0, score)
    
    async def _get_platform_metrics(self, user_id: int) -> Dict[PlatformType, PlatformMetrics]:
        """Get historical platform performance metrics for user"""        platform_metrics = {}
        
        # Query analytics data
        analytics = self.db.query(AnalyticsModel).filter(
            AnalyticsModel.user_id == user_id
        ).all()
        
        # Group by platform and calculate metrics
        platform_data = {}
        for record in analytics:
            platform = record.platform
            if platform not in platform_data:
                platform_data[platform] = []
            platform_data[platform].append(record)
        
        for platform_str, records in platform_data.items():
            try:
                platform = PlatformType(platform_str)
                
                # Calculate aggregated metrics
                total_reach = sum(r.reach or 0 for r in records)
                total_engagement = sum(r.engagement or 0 for r in records)
                total_revenue = sum(r.revenue or 0 for r in records)
                avg_reach = total_reach / len(records) if records else 0
                
                engagement_rate = (
                    total_engagement / total_reach if total_reach > 0 else 0
                )
                revenue_per_view = (
                    total_revenue / total_reach if total_reach > 0 else 0
                )
                
                platform_metrics[platform] = PlatformMetrics(
                    platform=platform,
                    reach_score=min(1.0, avg_reach / 10000),  # Normalize to 0-1
                    engagement_rate=engagement_rate,
                    conversion_rate=0.02,  # Default 2%
                    revenue_per_view=revenue_per_view,
                    audience_overlap=0.3,  # Default 30%
                    posting_frequency=len(records),
                    optimal_times=self.platform_analyzers[platform]["best_times"],
                    seasonal_trends={}
                )
                
            except ValueError:
                continue  # Skip unknown platforms
        
        # Add default metrics for platforms without data
        for platform in PlatformType:
            if platform not in platform_metrics:
                analyzer = self.platform_analyzers[platform]
                platform_metrics[platform] = PlatformMetrics(
                    platform=platform,
                    reach_score=0.5,
                    engagement_rate=0.03,
                    conversion_rate=0.02,
                    revenue_per_view=0.001,
                    audience_overlap=0.3,
                    posting_frequency=0,
                    optimal_times=analyzer["best_times"],
                    seasonal_trends={}
                )
        
        return platform_metrics
    
    async def _get_audience_insights(
        self,
        user_id: int,
        target_audience: Optional[List[AudienceSegment]]
    ) -> Dict[str, Any]:
        """Get audience insights and demographics"""        # This would integrate with platform APIs and analytics
        # For now, returning default insights
        
        base_insights = {
            "primary_demographics": {
                "age_groups": {"18-24": 0.3, "25-34": 0.4, "35-44": 0.2, "45+": 0.1},
                "gender": {"male": 0.6, "female": 0.35, "other": 0.05},
                "locations": {"US": 0.4, "UK": 0.15, "CA": 0.1, "AU": 0.08, "other": 0.27}
            },
            "interests": [
                "music", "entertainment", "technology", "lifestyle", "creativity"
            ],
            "platform_preferences": {
                PlatformType.YOUTUBE: 0.8,
                PlatformType.INSTAGRAM: 0.7,
                PlatformType.TIKTOK: 0.6,
                PlatformType.SPOTIFY: 0.5,
                PlatformType.TWITTER: 0.4,
                PlatformType.LINKEDIN: 0.2
            },
            "engagement_patterns": {
                "peak_hours": [17, 18, 19, 20, 21],
                "peak_days": ["Tuesday", "Wednesday", "Thursday", "Saturday"],
                "content_preferences": ["video", "audio", "visual", "text"]
            }
        }
        
        # Adjust based on target audience
        if target_audience:
            for segment in target_audience:
                if segment == AudienceSegment.MUSIC_LOVERS:
                    base_insights["platform_preferences"][PlatformType.SPOTIFY] = 0.9
                    base_insights["platform_preferences"][PlatformType.YOUTUBE] = 0.9
                elif segment == AudienceSegment.BUSINESS_PROFESSIONALS:
                    base_insights["platform_preferences"][PlatformType.LINKEDIN] = 0.8
                    base_insights["engagement_patterns"]["peak_hours"] = [8, 9, 12, 17]
                elif segment == AudienceSegment.CONTENT_CREATORS:
                    base_insights["platform_preferences"][PlatformType.TIKTOK] = 0.9
                    base_insights["platform_preferences"][PlatformType.INSTAGRAM] = 0.9
        
        return base_insights
    
    async def _recommend_platforms(
        self,
        content_analysis: ContentAnalysis,
        platform_metrics: Dict[PlatformType, PlatformMetrics],
        strategy_type: StrategyType,
        audience_insights: Dict[str, Any]
    ) -> List[PlatformType]:
        """Recommend optimal platforms based on strategy and content"""        
        platform_scores = {}
        
        # Get content type analyzer
        content_analyzer = self.content_analyzers[content_analysis.content_type]
        base_platforms = content_analyzer["platforms_priority"]
        
        for platform in PlatformType:
            score = 0.0
            
            # Base platform suitability for content type
            if platform in base_platforms:
                score += (5 - base_platforms.index(platform)) * 0.2
            
            # Platform performance history
            metrics = platform_metrics[platform]
            score += metrics.reach_score * 0.3
            score += metrics.engagement_rate * 0.2
            
            # Audience preference
            audience_pref = audience_insights["platform_preferences"].get(platform, 0.5)
            score += audience_pref * 0.2
            
            # Strategy-specific adjustments
            if strategy_type == StrategyType.MAXIMUM_REACH:
                score += metrics.reach_score * 0.4
            elif strategy_type == StrategyType.ENGAGEMENT_FOCUSED:
                score += metrics.engagement_rate * 0.4
            elif strategy_type == StrategyType.REVENUE_OPTIMIZED:
                score += metrics.revenue_per_view * 0.4
                if platform in content_analyzer["monetization_platforms"]:
                    score += 0.3
            elif strategy_type == StrategyType.VIRAL_POTENTIAL:
                if platform in [PlatformType.TIKTOK, PlatformType.INSTAGRAM]:
                    score += 0.4
                score += content_analysis.virality_score * 0.3
            
            platform_scores[platform] = score
        
        # Sort platforms by score and return top performers
        sorted_platforms = sorted(
            platform_scores.items(), key=lambda x: x[1], reverse=True
        )
        
        # Return top 4-6 platforms with score > 0.3
        recommended = [
            platform for platform, score in sorted_platforms
            if score > 0.3
        ][:6]
        
        return recommended
    
    async def _optimize_timing(
        self,
        platforms: List[PlatformType],
        audience_insights: Dict[str, Any]
    ) -> Dict[PlatformType, List[datetime]]:
        """Optimize posting timing for each platform"""        timing_recommendations = {}
        
        base_time = datetime.utcnow()
        peak_hours = audience_insights["engagement_patterns"]["peak_hours"]
        
        for platform in platforms:
            analyzer = self.platform_analyzers[platform]
            platform_best_times = analyzer["best_times"]
            
            # Find intersection of peak hours and platform best times
            optimal_hours = list(set(peak_hours) & set(platform_best_times))
            
            if not optimal_hours:
                optimal_hours = platform_best_times[:3]
            
            # Generate specific datetime recommendations for next 7 days
            recommendations = []
            for day in range(7):
                target_date = base_time + timedelta(days=day)
                
                for hour in optimal_hours[:2]:  # Top 2 times per day
                    posting_time = target_date.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    recommendations.append(posting_time)
            
            timing_recommendations[platform] = recommendations[:10]  # Top 10 times
        
        return timing_recommendations
    
    async def _generate_content_adaptations(
        self,
        content: ContentModel,
        platforms: List[PlatformType]
    ) -> Dict[PlatformType, Dict[str, Any]]:
        """Generate platform-specific content adaptations"""        adaptations = {}
        
        for platform in platforms:
            analyzer = self.platform_analyzers[platform]
            
            adaptation = {
                "title": content.title,
                "description": content.description,
                "hashtags": content.hashtags or [],
                "format_adjustments": {},
                "optimization_suggestions": []
            }
            
            # Platform-specific optimizations
            if platform == PlatformType.YOUTUBE:
                adaptation["optimization_suggestions"].extend([
                    "Add compelling thumbnail",
                    "Include keywords in title",
                    "Use detailed description with timestamps"
                ])
                if analyzer.get("optimal_length"):
                    adaptation["format_adjustments"]["recommended_length"] = (
                        analyzer["optimal_length"]["sweet_spot"]
                    )
            
            elif platform == PlatformType.INSTAGRAM:
                adaptation["optimization_suggestions"].extend([
                    "Use square or vertical format",
                    "Add story highlights",
                    "Include call-to-action"
                ])
                if analyzer.get("reels_priority"):
                    adaptation["format_adjustments"]["format"] = "reels"
            
            elif platform == PlatformType.TIKTOK:
                adaptation["optimization_suggestions"].extend([
                    "Use trending sounds",
                    "Add quick hook in first 3 seconds",
                    "Include popular challenges"
                ])
                adaptation["format_adjustments"]["aspect_ratio"] = "9:16"
            
            elif platform == PlatformType.TWITTER:
                adaptation["optimization_suggestions"].extend([
                    "Keep text concise",
                    "Use thread for longer content",
                    "Include relevant mentions"
                ])
                adaptation["format_adjustments"]["max_length"] = 280
            
            elif platform == PlatformType.SPOTIFY:
                adaptation["optimization_suggestions"].extend([
                    "Optimize audio quality",
                    "Create compelling episode description",
                    "Add to relevant playlists"
                ])
                adaptation["format_adjustments"]["audio_format"] = "high_quality"
            
            elif platform == PlatformType.LINKEDIN:
                adaptation["optimization_suggestions"].extend([
                    "Add professional context",
                    "Include industry insights",
                    "Tag relevant professionals"
                ])
                adaptation["format_adjustments"]["tone"] = "professional"
            
            adaptations[platform] = adaptation
        
        return adaptations
    
    async def _generate_hashtag_recommendations(
        self,
        content: ContentModel,
        platforms: List[PlatformType]
    ) -> Dict[PlatformType, List[str]]:
        """Generate platform-specific hashtag recommendations"""        hashtag_recommendations = {}
        
        # Base hashtags from content
        base_hashtags = content.hashtags or []
        
        # Content type specific hashtags
        content_hashtags = {
            ContentType.AUDIO: ["music", "audio", "sound", "musician", "song"],
            ContentType.VIDEO: ["video", "content", "creator", "viral", "entertainment"],
            ContentType.IMAGE: ["photo", "visual", "art", "creative", "design"],
            ContentType.TEXT: ["content", "writing", "thoughts", "share", "story"]
        }
        
        type_hashtags = content_hashtags.get(content.content_type, [])
        
        for platform in platforms:
            analyzer = self.platform_analyzers[platform]
            max_hashtags = analyzer.get("hashtag_weight", 0.5) * 30  # Max based on platform
            
            platform_hashtags = list(base_hashtags)
            
            # Add content type hashtags
            platform_hashtags.extend(type_hashtags[:3])
            
            # Platform-specific hashtags
            if platform == PlatformType.INSTAGRAM:
                platform_hashtags.extend([
                    "instagram", "insta", "ig", "reels", "explore"
                ])
            elif platform == PlatformType.TIKTOK:
                platform_hashtags.extend([
                    "tiktok", "fyp", "foryou", "viral", "trending"
                ])
            elif platform == PlatformType.YOUTUBE:
                platform_hashtags.extend([
                    "youtube", "youtuber", "subscribe", "video", "content"
                ])
            elif platform == PlatformType.TWITTER:
                platform_hashtags.extend([
                    "twitter", "tweet", "thread", "viral", "trending"
                ])
            elif platform == PlatformType.SPOTIFY:
                platform_hashtags.extend([
                    "spotify", "podcast", "music", "audio", "listen"
                ])
            elif platform == PlatformType.LINKEDIN:
                platform_hashtags.extend([
                    "linkedin", "professional", "business", "career", "networking"
                ])
            
            # Remove duplicates and limit count
            unique_hashtags = list(dict.fromkeys(platform_hashtags))
            hashtag_recommendations[platform] = unique_hashtags[:int(max_hashtags)]
        
        return hashtag_recommendations
    
    async def _generate_audience_targeting(
        self,
        platforms: List[PlatformType],
        audience_insights: Dict[str, Any]
    ) -> Dict[PlatformType, Dict[str, Any]]:
        """Generate audience targeting parameters for each platform"""        targeting = {}
        
        demographics = audience_insights["primary_demographics"]
        interests = audience_insights["interests"]
        
        for platform in platforms:
            platform_targeting = {
                "age_groups": demographics["age_groups"],
                "gender": demographics["gender"],
                "locations": demographics["locations"],
                "interests": interests,
                "behaviors": [],
                "custom_audiences": []
            }
            
            # Platform-specific targeting
            if platform == PlatformType.INSTAGRAM:
                platform_targeting["behaviors"].extend([
                    "frequent_travelers", "online_shoppers", "mobile_users"
                ])
            elif platform == PlatformType.LINKEDIN:
                platform_targeting["behaviors"].extend([
                    "business_decision_makers", "job_seekers", "professional_networkers"
                ])
            elif platform == PlatformType.TIKTOK:
                platform_targeting["behaviors"].extend([
                    "trend_followers", "music_lovers", "content_creators"
                ])
            
            targeting[platform] = platform_targeting
        
        return targeting
    
    async def _predict_performance_metrics(
        self,
        content_analysis: ContentAnalysis,
        platforms: List[PlatformType],
        audience_insights: Dict[str, Any]
    ) -> Dict[PlatformType, Dict[str, float]]:
        """Predict performance metrics for each platform"""        predictions = {}
        
        for platform in platforms:
            # Base predictions using simple heuristics
            # In production, this would use trained ML models
            
            base_reach = 1000
            base_engagement = 0.03
            base_revenue = 0.001
            
            # Adjust based on content quality
            quality_multiplier = content_analysis.quality_score
            reach = base_reach * quality_multiplier * (1 + content_analysis.virality_score)
            
            # Adjust based on platform characteristics
            platform_pref = audience_insights["platform_preferences"].get(platform, 0.5)
            reach *= platform_pref
            
            engagement_rate = base_engagement * quality_multiplier * platform_pref
            
            # Revenue predictions
            revenue_per_view = base_revenue * content_analysis.monetization_potential
            total_revenue = reach * revenue_per_view
            
            predictions[platform] = {
                "estimated_reach": round(reach),
                "engagement_rate": round(engagement_rate, 4),
                "estimated_engagement": round(reach * engagement_rate),
                "estimated_revenue": round(total_revenue, 2),
                "conversion_rate": round(base_engagement * 0.1, 4),
                "virality_potential": round(content_analysis.virality_score, 2)
            }
        
        return predictions
    
    async def _calculate_confidence_score(
        self,
        content_analysis: ContentAnalysis,
        platform_metrics: Dict[PlatformType, PlatformMetrics],
        expected_metrics: Dict[PlatformType, Dict[str, float]]
    ) -> float:
        """Calculate confidence score for the strategy"""        
        # Factors affecting confidence
        factors = []
        
        # Content quality factor
        factors.append(content_analysis.quality_score)
        
        # Historical performance factor
        avg_reach_score = np.mean([
            metrics.reach_score for metrics in platform_metrics.values()
        ])
        factors.append(avg_reach_score)
        
        # Prediction consistency factor
        reach_predictions = [
            metrics["estimated_reach"] for metrics in expected_metrics.values()
        ]
        if reach_predictions:
            cv = np.std(reach_predictions) / np.mean(reach_predictions)
            consistency_score = max(0, 1 - cv)  # Lower CV = higher consistency
            factors.append(consistency_score)
        
        # Overall confidence
        confidence = np.mean(factors)
        return round(confidence, 2)
    
    async def _generate_strategy_reasoning(
        self,
        strategy_type: StrategyType,
        platforms: List[PlatformType],
        expected_metrics: Dict[PlatformType, Dict[str, float]]
    ) -> str:
        """Generate human-readable reasoning for the strategy"""        
        total_reach = sum(
            metrics["estimated_reach"] for metrics in expected_metrics.values()
        )
        
        avg_engagement = np.mean([
            metrics["engagement_rate"] for metrics in expected_metrics.values()
        ])
        
        total_revenue = sum(
            metrics["estimated_revenue"] for metrics in expected_metrics.values()
        )
        
        top_platform = max(
            expected_metrics.items(),
            key=lambda x: x[1]["estimated_reach"]
        )[0]
        
        reasoning = f"This {strategy_type.value.replace('_', ' ')} strategy recommends "
        reasoning += f"distributing to {len(platforms)} platforms, with {top_platform.value} "
        reasoning += f"as the primary platform. Expected total reach: {total_reach:,} users, "
        reasoning += f"average engagement rate: {avg_engagement:.2%}, "
        reasoning += f"estimated revenue: ${total_revenue:.2f}."
        
        return reasoning
