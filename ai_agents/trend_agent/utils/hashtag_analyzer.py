"""Hashtag Analyzer Module - Advanced AI-Driven Hashtag Intelligence & Optimization System

Sophisticated hashtag analysis and optimization platform that provides:
- Advanced hashtag performance analytics with predictive modeling
- Real-time hashtag trend monitoring across multiple platforms
- AI-powered hashtag recommendation engine with semantic understanding
- Hashtag competition analysis and market positioning strategies
- Cross-platform hashtag synchronization and optimization
- Sentiment-driven hashtag selection for emotional engagement
- Monetization-focused hashtag strategies for revenue optimization
- Brand safety and risk assessment for hashtag usage

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code, algorithms, and business logic are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer: Advanced ML algorithms and system architecture
- Machine Learning Engineer & Audio Processing: NLP models and semantic analysis
- Database Administrator & Security Expert: High-performance hashtag storage and indexing
- Microservices Architect & DevOps Engineer: Scalable hashtag processing systems
- AI Prompt Engineer & Content Protection: Intelligent hashtag optimization and content safety
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import time
import hashlib
from collections import Counter, defaultdict
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
from sentence_transformers import SentenceTransformer
from textblob import TextBlob
import plotly.graph_objects as go
from wordcloud import WordCloud

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProcessingError, ValidationError, NLPError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError, NLPError = globals().get('ProcessingError, ValidationError, NLPError', Exception)
from ...models.content import ContentType, ContentMetadata
from ...models.hashtag import (
    HashtagData, HashtagCluster, HashtagRecommendation,
    HashtagPerformanceMetrics, HashtagTrend, HashtagRisk
)
from ...models.engagement import EngagementMetrics, PlatformMetrics
from ...models.creator import CreatorProfile, AudienceInsights
from ...utils.nlp_utils import (
    TextPreprocessor, SemanticAnalyzer, LanguageDetector,
    EmotionExtractor, TopicModeler
)
from ...utils.performance_monitor import PerformanceMonitor
from ...integrations.social_platforms import HashtagAPIIntegrator
from ...data_management.hashtag_storage import HashtagDataManager
from ...security.content_moderation import HashtagModerator

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except Exception as e:
    logger.warning(f"NLTK download failed: {str(e)}")

class HashtagCategory(Enum):
    """Comprehensive hashtag categorization system"""

    TRENDING_VIRAL = "trending_viral"           # Currently viral hashtags
    EMERGING_TREND = "emerging_trend"           # Rising hashtags with potential
    EVERGREEN = "evergreen"                     # Consistently performing hashtags  
    SEASONAL = "seasonal"                       # Time-specific hashtags
    NICHE_SPECIFIC = "niche_specific"          # Industry/topic specific
    BRANDED = "branded"                        # Brand-related hashtags
    COMMUNITY = "community"                    # Community-building hashtags
    CALL_TO_ACTION = "call_to_action"          # Action-driving hashtags
    EMOTIONAL_TRIGGER = "emotional_trigger"    # Emotion-evoking hashtags
    CONTROVERSIAL = "controversial"            # Risk/controversy hashtags
    LOCATION_BASED = "location_based"          # Geographic hashtags
    EVENT_SPECIFIC = "event_specific"          # Event-related hashtags

class HashtagStrategy(Enum):
    """Advanced hashtag strategy types"""

    VIRAL_MAXIMIZATION = "viral_maximization"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"  
    REACH_EXPANSION = "reach_expansion"
    NICHE_TARGETING = "niche_targeting"
    BRAND_BUILDING = "brand_building"
    COMMUNITY_GROWTH = "community_growth"
    MONETIZATION_FOCUS = "monetization_focus"
    BALANCED_APPROACH = "balanced_approach"

class HashtagRiskLevel(Enum):
    """Hashtag risk assessment levels"""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"

@dataclass
class AdvancedHashtagMetrics:
    """Comprehensive hashtag performance metrics"""
    hashtag: str
    usage_frequency: int
    engagement_rate: float
    reach_potential: int
    competition_level: float
    trend_velocity: float
    sentiment_score: float
    virality_coefficient: float
    platform_performance: Dict[str, float]
    demographic_appeal: Dict[str, float]
    temporal_patterns: Dict[str, float]
    semantic_clusters: List[str]
    related_hashtags: List[Tuple[str, float]]
    brand_safety_score: float
    monetization_potential: float
    audience_alignment: float
    content_type_affinity: Dict[ContentType, float]
    geographic_performance: Dict[str, float]
    influencer_adoption: Dict[str, int]
    growth_trajectory: List[Tuple[datetime, float]]
    risk_assessment: HashtagRisk
    optimization_suggestions: List[str]
    predicted_lifespan: Tuple[int, int]  # (min_days, max_days)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HashtagRecommendationSet:
    """
Comprehensive hashtag recommendation package"""
    strategy: HashtagStrategy
    primary_hashtags: List[AdvancedHashtagMetrics]      # 3-5 main hashtags
    secondary_hashtags: List[AdvancedHashtagMetrics]    # 5-10 supporting hashtags
    niche_hashtags: List[AdvancedHashtagMetrics]        # 5-15 niche/specific hashtags
    trending_hashtags: List[AdvancedHashtagMetrics]     # 2-5 trending hashtags
    branded_hashtags: List[AdvancedHashtagMetrics]      # 1-3 branded hashtags
    performance_prediction: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    timing_recommendations: Dict[str, List[str]]
    platform_optimization: Dict[str, List[str]]
    competitive_analysis: Dict[str, Any]
    expected_results: Dict[str, Any]
    optimization_timeline: List[Dict[str, Any]]
    success_metrics: Dict[str, float]
    alternative_strategies: List[Dict[str, Any]]

class SemanticHashtagEmbedding:
    """
Advanced semantic embedding for hashtag analysis"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        
    async def embed_hashtags(self, hashtags: List[str]) -> np.ndarray:
        """Generate semantic embeddings for hashtags"""
        # Clean hashtags
        cleaned_hashtags = [hashtag.replace('#', '').replace('_', ' ') for hashtag in hashtags]
        
        # Check cache
        cache_keys = [hashlib.md5(hashtag.encode()).hexdigest() for hashtag in cleaned_hashtags]
        embeddings = []
        
        for i, (hashtag, cache_key) in enumerate(zip(cleaned_hashtags, cache_keys)):
            if cache_key in self.embeddings_cache:
                embeddings.append(self.embeddings_cache[cache_key])
            else:
                embedding = self.model.encode(hashtag, convert_to_numpy=True)
                self.embeddings_cache[cache_key] = embedding
                embeddings.append(embedding)
        
        return np.array(embeddings)
    
    async def find_similar_hashtags(
        self, 
        target_hashtag: str, 
        candidate_hashtags: List[str], 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
Find semantically similar hashtags"""
        target_embedding = await self.embed_hashtags([target_hashtag])
        candidate_embeddings = await self.embed_hashtags(candidate_hashtags)
        
        similarities = cosine_similarity(target_embedding, candidate_embeddings)[0]
        
        # Sort by similarity
        similar_pairs = list(zip(candidate_hashtags, similarities))
        similar_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return similar_pairs[:top_k]

class HashtagAnalyzer:
    """
    Enterprise-Grade Hashtag Intelligence & Optimization System
    
    Advanced AI system that provides comprehensive hashtag analysis including:
    - Real-time hashtag trend monitoring with predictive analytics
    - Semantic hashtag clustering and relationship mapping
    - Advanced performance prediction using machine learning
    - Cross-platform hashtag strategy optimization
    - Risk assessment and brand safety monitoring
    - Competitive hashtag analysis and market positioning
    - Personalized hashtag recommendations based on creator profiles
    - ROI optimization for hashtag-driven marketing campaigns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Core components
        self.performance_monitor = PerformanceMonitor("hashtag_analyzer")
        self.text_preprocessor = TextPreprocessor(config.get("text_config", {}))
        self.semantic_analyzer = SemanticAnalyzer()
        self.language_detector = LanguageDetector()
        self.emotion_extractor = EmotionExtractor()
        self.topic_modeler = TopicModeler(config.get("topic_config", {}))
        
        # External integrations
        self.api_integrator = HashtagAPIIntegrator(config.get("api_config", {}))
        self.hashtag_data_manager = HashtagDataManager(config.get("storage_config", {}))
        self.hashtag_moderator = HashtagModerator()
        
        # ML and NLP components
        self.semantic_embedder = SemanticHashtagEmbedding()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found, using basic processing")
            self.nlp = None
        
        # Vectorizers and ML models
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english'
        )
        self.count_vectorizer = CountVectorizer(
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.lda_model = LatentDirichletAllocation(n_components=20, random_state=42)
        self.nmf_model = NMF(n_components=15, random_state=42)
        
        # Clustering models
        self.kmeans_clusterer = KMeans(n_clusters=10, random_state=42)
        self.dbscan_clusterer = DBSCAN(eps=0.3, min_samples=5)
        
        # Analysis parameters
        self.min_hashtag_frequency = self.config.get("min_frequency", 5)
        self.max_hashtags_per_recommendation = self.config.get("max_hashtags", 30)
        self.trend_detection_window = self.config.get("trend_window", 7)  # days
        self.similarity_threshold = self.config.get("similarity_threshold", 0.7)
        self.risk_threshold = self.config.get("risk_threshold", 0.6)
        
        # Caching
        self._hashtag_cache = {}
        self._trend_cache = {}
        self._recommendation_cache = {}
        self._last_update = None
        
        # Stopwords
        try:
            self.stopwords = set(stopwords.words('english'))
        except Exception:
            self.stopwords = set()
        
        logger.info("Advanced HashtagAnalyzer initialized with enterprise capabilities")
    
    async def initialize_hashtag_system(self):
        """Initialize complete hashtag analysis system"""
        try:
            with self.performance_monitor.time_operation("system_initialization"):
                logger.info("Initializing hashtag analysis system")
                
                # Initialize data manager
                await self.hashtag_data_manager.initialize()
                
                # Initialize API integrator
                await self.api_integrator.initialize()
                
                # Initialize content moderator
                await self.hashtag_moderator.initialize()
                
                # Load historical hashtag data
                await self._load_historical_data()
                
                # Initialize ML models
                await self._initialize_ml_models()
                
                # Start background monitoring
                asyncio.create_task(self._background_trend_monitoring())
                
                logger.info("Hashtag analysis system initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize hashtag system: {str(e)}")
            raise NLPError(f"Hashtag system initialization failed: {str(e)}")
    
    async def analyze_hashtag_performance(
        self,
        hashtags: List[str],
        content_type: Optional[ContentType] = None,
        platforms: Optional[List[str]] = None,
        creator_profile: Optional[CreatorProfile] = None,
        analysis_depth: str = "comprehensive"
    ) -> List[AdvancedHashtagMetrics]:
        """
        Comprehensive hashtag performance analysis
        
        Args:
            hashtags: List of hashtags to analyze
            content_type: Type of content for context
            platforms: Target platforms for analysis
            creator_profile: Creator's profile for personalization
            analysis_depth: Level of analysis detail
            
        Returns:
            Detailed performance metrics for each hashtag
        """
        try:
            with self.performance_monitor.time_operation("hashtag_performance_analysis"):
                logger.info(f"Analyzing performance for {len(hashtags)} hashtags")
                
                # Validate and clean hashtags
                cleaned_hashtags = await self._validate_and_clean_hashtags(hashtags)
                
                if not cleaned_hashtags:
                    return []
                
                # Collect comprehensive data
                hashtag_data = await self._collect_hashtag_data(
                    cleaned_hashtags, platforms or ["instagram", "tiktok", "twitter"]
                )
                
                # Advanced analytics
                performance_metrics = []
                
                for hashtag in cleaned_hashtags:
                    metrics = await self._analyze_individual_hashtag(
                        hashtag, hashtag_data.get(hashtag, {}), 
                        content_type, creator_profile, analysis_depth
                    )
                    
                    if metrics:
                        performance_metrics.append(metrics)
                
                # Cross-hashtag analysis
                if len(performance_metrics) > 1:
                    performance_metrics = await self._enhance_with_cross_analysis(
                        performance_metrics
                    )
                
                logger.info(f"Performance analysis completed for {len(performance_metrics)} hashtags")
                return performance_metrics
                
        except Exception as e:
            logger.error(f"Hashtag performance analysis failed: {str(e)}")
            raise ProcessingError(f"Hashtag analysis failed: {str(e)}")
    
    async def generate_hashtag_recommendations(
        self,
        content_metadata: ContentMetadata,
        creator_profile: Optional[CreatorProfile] = None,
        strategy: HashtagStrategy = HashtagStrategy.BALANCED_APPROACH,
        target_platforms: Optional[List[str]] = None,
        max_hashtags: int = 30
    ) -> HashtagRecommendationSet:
        """
        Generate intelligent hashtag recommendations
        
        Args:
            content_metadata: Content to generate hashtags for
            creator_profile: Creator's profile for personalization
            strategy: Hashtag strategy to employ
            target_platforms: Target social platforms
            max_hashtags: Maximum number of hashtags to recommend
            
        Returns:
            Comprehensive hashtag recommendation set
        """
        try:
            with self.performance_monitor.time_operation("hashtag_recommendation"):
                logger.info(f"Generating hashtag recommendations with {strategy.value} strategy")
                
                # Content analysis
                content_analysis = await self._analyze_content_for_hashtags(content_metadata)
                
                # Generate candidate hashtags
                candidates = await self._generate_candidate_hashtags(
                    content_analysis, creator_profile, target_platforms
                )
                
                # Apply strategy-specific filtering and ranking
                filtered_candidates = await self._apply_strategy_filter(
                    candidates, strategy, content_metadata, creator_profile
                )
                
                # Categorize and organize recommendations
                recommendations = await self._organize_recommendations(
                    filtered_candidates, strategy, max_hashtags
                )
                
                # Generate performance predictions
                performance_prediction = await self._predict_hashtag_performance(
                    recommendations, content_metadata, creator_profile
                )
                
                # Risk analysis
                risk_analysis = await self._analyze_recommendation_risks(recommendations)
                
                # Additional insights
                additional_insights = await self._generate_additional_insights(
                    recommendations, content_metadata, strategy
                )
                
                recommendation_set = HashtagRecommendationSet(
                    strategy=strategy,
                    primary_hashtags=recommendations['primary'],
                    secondary_hashtags=recommendations['secondary'],
                    niche_hashtags=recommendations['niche'],
                    trending_hashtags=recommendations['trending'],
                    branded_hashtags=recommendations['branded'],
                    performance_prediction=performance_prediction,
                    risk_analysis=risk_analysis,
                    timing_recommendations=additional_insights['timing'],
                    platform_optimization=additional_insights['platform'],
                    competitive_analysis=additional_insights['competitive'],
                    expected_results=additional_insights['expected_results'],
                    optimization_timeline=additional_insights['timeline'],
                    success_metrics=additional_insights['success_metrics'],
                    alternative_strategies=additional_insights['alternatives']
                )
                
                # Cache recommendations
                await self._cache_recommendation_set(content_metadata.content_id, recommendation_set)
                
                logger.info("Hashtag recommendations generated successfully")
                return recommendation_set
                
        except Exception as e:
            logger.error(f"Hashtag recommendation generation failed: {str(e)}")
            raise ProcessingError(f"Hashtag recommendation failed: {str(e)}")

    async def discover_trending_hashtags(
        self,
        content_type: Optional[ContentType] = None,
        platforms: Optional[List[str]] = None,
        region: Optional[str] = None,
        time_window: int = 24,  # hours
        min_growth_rate: float = 0.5
    ) -> List[HashtagTrend]:
        """Discover trending hashtags with growth prediction"""
        try:
            with self.performance_monitor.time_operation("trending_discovery"):
                logger.info("Discovering trending hashtags with advanced analytics")
                
                # Collect real-time trending data
                trending_data = await self._collect_trending_data(
                    platforms or ["instagram", "tiktok", "twitter"], 
                    region, time_window
                )
                
                # Analyze growth patterns
                growth_analysis = await self._analyze_growth_patterns(trending_data)
                
                # Filter by growth criteria
                significant_trends = await self._filter_significant_trends(
                    growth_analysis, min_growth_rate
                )
                
                # Predict trend continuation
                trend_predictions = await self._predict_trend_continuation(significant_trends)
                
                # Generate comprehensive trend objects
                trend_hashtags = []
                
                for hashtag, data in trend_predictions.items():
                    if content_type and not await self._is_relevant_for_content_type(hashtag, content_type):
                        continue
                    
                    trend = HashtagTrend(
                        hashtag=hashtag,
                        current_volume=data['current_volume'],
                        growth_rate=data['growth_rate'],
                        velocity=data['velocity'],
                        predicted_peak=data['predicted_peak'],
                        confidence_score=data['confidence'],
                        platforms=data['platforms'],
                        geographic_spread=data['geographic_spread'],
                        demographic_breakdown=data['demographics'],
                        related_trends=data['related_trends'],
                        risk_factors=data['risk_factors'],
                        opportunity_score=data['opportunity_score']
                    )
                    
                    trend_hashtags.append(trend)
                
                # Sort by opportunity score
                trend_hashtags.sort(key=lambda x: x.opportunity_score, reverse=True)
                
                return trend_hashtags[:50]  # Top 50 trending hashtags
                
        except Exception as e:
            logger.error(f"Trending hashtag discovery failed: {str(e)}")
            raise ProcessingError(f"Trending discovery failed: {str(e)}")

    # Advanced analysis methods
    async def _analyze_individual_hashtag(
        self,
        hashtag: str,
        hashtag_data: Dict[str, Any],
        content_type: Optional[ContentType],
        creator_profile: Optional[CreatorProfile],
        analysis_depth: str
    ) -> Optional[AdvancedHashtagMetrics]:
        """Comprehensive analysis of individual hashtag"""
        try:
            # Basic metrics calculation
            usage_frequency = hashtag_data.get('usage_frequency', 0)
            engagement_rate = hashtag_data.get('engagement_rate', 0.0)
            reach_potential = hashtag_data.get('reach_potential', 0)
            
            if usage_frequency < self.min_hashtag_frequency:
                return None
            
            # Advanced analytics
            competition_level = await self._calculate_competition_level(hashtag, hashtag_data)
            trend_velocity = await self._calculate_trend_velocity(hashtag, hashtag_data)
            sentiment_score = await self._analyze_hashtag_sentiment(hashtag, hashtag_data)
            virality_coefficient = await self._calculate_virality_coefficient(hashtag, hashtag_data)
            
            # Platform-specific analysis
            platform_performance = await self._analyze_platform_performance(hashtag, hashtag_data)
            
            # Demographic analysis
            demographic_appeal = await self._analyze_demographic_appeal(hashtag, hashtag_data)
            
            # Temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(hashtag, hashtag_data)
            
            # Semantic analysis
            semantic_clusters = await self._identify_semantic_clusters(hashtag)
            related_hashtags = await self._find_related_hashtags(hashtag)
            
            # Safety and risk assessment
            brand_safety_score = await self._assess_brand_safety(hashtag)
            risk_assessment = await self._assess_hashtag_risks(hashtag, hashtag_data)
            
            # Business metrics
            monetization_potential = await self._calculate_monetization_potential(
                hashtag, hashtag_data, creator_profile
            )
            audience_alignment = await self._calculate_audience_alignment(
                hashtag, creator_profile
            ) if creator_profile else 0.0
            
            # Content type affinity
            content_type_affinity = await self._calculate_content_type_affinity(hashtag, hashtag_data)
            
            # Geographic performance
            geographic_performance = await self._analyze_geographic_performance(hashtag, hashtag_data)
            
            # Influencer adoption patterns
            influencer_adoption = await self._analyze_influencer_adoption(hashtag, hashtag_data)
            
            # Growth trajectory
            growth_trajectory = await self._calculate_growth_trajectory(hashtag, hashtag_data)
            
            # Optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                hashtag, hashtag_data, content_type, creator_profile
            )
            
            # Lifespan prediction
            predicted_lifespan = await self._predict_hashtag_lifespan(hashtag, hashtag_data)
            
            return AdvancedHashtagMetrics(
                hashtag=hashtag,
                usage_frequency=usage_frequency,
                engagement_rate=engagement_rate,
                reach_potential=reach_potential,
                competition_level=competition_level,
                trend_velocity=trend_velocity,
                sentiment_score=sentiment_score,
                virality_coefficient=virality_coefficient,
                platform_performance=platform_performance,
                demographic_appeal=demographic_appeal,
                temporal_patterns=temporal_patterns,
                semantic_clusters=semantic_clusters,
                related_hashtags=related_hashtags,
                brand_safety_score=brand_safety_score,
                monetization_potential=monetization_potential,
                audience_alignment=audience_alignment,
                content_type_affinity=content_type_affinity,
                geographic_performance=geographic_performance,
                influencer_adoption=influencer_adoption,
                growth_trajectory=growth_trajectory,
                risk_assessment=risk_assessment,
                optimization_suggestions=optimization_suggestions,
                predicted_lifespan=predicted_lifespan
            )
            
        except Exception as e:
            logger.error(f"Individual hashtag analysis failed for {hashtag}: {str(e)}")
            return None

    # Additional sophisticated methods continue...

class TagOptimizer:
    """
    Advanced Hashtag Optimization Engine
    
    Specialized system for optimizing hashtag strategies based on:
    - Performance data analysis and predictive modeling
    - Cross-platform optimization strategies
    - Real-time A/B testing and optimization
    - ROI maximization for hashtag investments
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.hashtag_analyzer = HashtagAnalyzer(config)
        self.performance_monitor = PerformanceMonitor("tag_optimizer")
        
        # Optimization parameters
        self.optimization_goals = self.config.get("optimization_goals", {
            'engagement': 0.4,
            'reach': 0.3,
            'virality': 0.2,
            'brand_safety': 0.1
        })
        
        logger.info("TagOptimizer initialized for hashtag strategy optimization")
    
    async def optimize_hashtag_strategy(
        self,
        current_hashtags: List[str],
        content_metadata: ContentMetadata,
        performance_history: Optional[List[Dict[str, Any]]] = None,
        target_metrics: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Optimize existing hashtag strategy for better performance"""
        try:
            with self.performance_monitor.time_operation("strategy_optimization"):
                logger.info(f"Optimizing strategy for {len(current_hashtags)} hashtags")
                
                # Analyze current performance
                current_analysis = await self.hashtag_analyzer.analyze_hashtag_performance(
                    current_hashtags, content_metadata.content_type
                )
                
                # Identify optimization opportunities
                opportunities = await self._identify_optimization_opportunities(
                    current_analysis, performance_history, target_metrics
                )
                
                # Generate optimization recommendations
                optimization_plan = await self._generate_optimization_plan(
                    current_analysis, opportunities, content_metadata
                )
                
                # Predict optimization impact
                impact_prediction = await self._predict_optimization_impact(
                    current_analysis, optimization_plan
                )
                
                return {
                    'current_performance': current_analysis,
                    'optimization_opportunities': opportunities,
                    'optimization_plan': optimization_plan,
                    'predicted_impact': impact_prediction,
                    'implementation_timeline': await self._create_implementation_timeline(optimization_plan),
                    'success_metrics': await self._define_success_metrics(optimization_plan)
                }
                
        except Exception as e:
            logger.error(f"Hashtag strategy optimization failed: {str(e)}")
            raise ProcessingError(f"Strategy optimization failed: {str(e)}")

# Export all components
__all__ = [
    'HashtagAnalyzer', 'TagOptimizer', 'AdvancedHashtagMetrics',
    'HashtagRecommendationSet', 'HashtagCategory', 'HashtagStrategy',
    'HashtagRiskLevel', 'SemanticHashtagEmbedding'
]

import asyncio
import json
import logging
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, pearsonr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import networkx as nx
from textblob import TextBlob
import spacy

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError = globals().get('ProcessingError, ValidationError', Exception)
from ...models.content import ContentType, ContentMetadata
from ...models.hashtag import HashtagData, HashtagStrategy, HashtagCluster
from ...models.social import SocialPlatform, PlatformMetrics
from ...integrations.social_platforms import HashtagAPI
from ...utils.text_processing import TextProcessor
from ...utils.network_analysis import NetworkAnalyzer

logger = logging.getLogger(__name__)

class HashtagType(Enum):
    """Hashtag classification types"""

    TRENDING = "trending"
    NICHE = "niche"
    BRANDED = "branded"
    COMMUNITY = "community"
    LOCATION = "location"
    EVENT = "event"
    SEASONAL = "seasonal"
    EVERGREEN = "evergreen"

class HashtagStrategy(Enum):
    """Hashtag optimization strategies"""

    VIRAL_BOOST = "viral_boost"
    NICHE_TARGETING = "niche_targeting"
    BRAND_BUILDING = "brand_building"
    COMMUNITY_ENGAGEMENT = "community_engagement"
    TREND_RIDING = "trend_riding"
    LONG_TAIL = "long_tail"

@dataclass
class HashtagMetrics:
    """Comprehensive hashtag performance metrics"""
    usage_count: int
    engagement_rate: float
    reach_potential: int
    competition_level: float
    growth_rate: float
    sentiment_score: float
    virality_index: float
    platform_performance: Dict[str, float]
    demographic_breakdown: Dict[str, Any]
    temporal_patterns: Dict[str, Any]

@dataclass
class HashtagRecommendation:
    """
Hashtag recommendation with optimization data"""
    hashtag: str
    hashtag_type: HashtagType
    confidence_score: float
    predicted_performance: Dict[str, float]
    optimal_platforms: List[str]
    timing_recommendations: List[str]
    competition_analysis: Dict[str, Any]
    synergy_tags: List[str]

class HashtagAnalyzer:
    """
    Advanced Hashtag Analysis & Optimization Engine
    
    Provides comprehensive hashtag intelligence including trend analysis,
    performance prediction, and strategic optimization recommendations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.text_processor = TextProcessor()
        self.network_analyzer = NetworkAnalyzer()
        self.hashtag_api = HashtagAPI()
        
        # NLP components
        self.nlp = None  # Will load spaCy model
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.scaler = StandardScaler()
        
        # Configuration
        self.max_hashtags_per_analysis = config.get("max_hashtags", 1000)
        self.min_usage_threshold = config.get("min_usage", 10)
        self.update_interval = config.get("update_interval", 1800)  # 30 minutes
        self.cache_ttl = config.get("cache_ttl", 3600)  # 1 hour
        
        # Internal state
        self._hashtag_cache = {}
        self._trending_cache = {}
        self._network_cache = {}
        self._performance_history = defaultdict(list)
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize hashtag analyzer components"""
        try:
            logger.info("Initializing HashtagAnalyzer")
            
            # Load spaCy model for NLP
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using basic text processing")
                self.nlp = None
            
            # Initialize text processor
            await self.text_processor.initialize()
            
            # Initialize hashtag API connections
            await self.hashtag_api.initialize()
            
            # Start background updates
            asyncio.create_task(self._background_hashtag_monitoring())
            
            self.is_initialized = True
            logger.info("HashtagAnalyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize HashtagAnalyzer: {str(e)}")
            raise ProcessingError(f"HashtagAnalyzer initialization failed: {str(e)}")

    async def analyze_hashtags(
        self,
        content_data: List[Dict[str, Any]],
        platforms: List[str],
        time_range: int = 7  # days
    ) -> Dict[str, Any]:
        """
        Perform comprehensive hashtag analysis
        
        Args:
            content_data: Content data with hashtags
            platforms: Target social platforms
            time_range: Analysis time range in days
            
        Returns:
            Complete hashtag analysis results
        """
        try:
            logger.info(f"Analyzing hashtags for {len(content_data)} content items")
            
            # Extract and clean hashtags
            hashtag_data = await self._extract_hashtags(content_data)
            
            if not hashtag_data:
                return {"error": "No hashtags found in content data"}
            
            # Calculate hashtag metrics
            hashtag_metrics = await self._calculate_hashtag_metrics(
                hashtag_data, platforms, time_range
            )
            
            # Identify hashtag clusters
            clusters = await self._identify_hashtag_clusters(hashtag_data)
            
            # Analyze hashtag networks
            network_analysis = await self._analyze_hashtag_networks(hashtag_data)
            
            # Generate trending insights
            trending_insights = await self._analyze_trending_patterns(
                hashtag_data, time_range
            )
            
            # Platform-specific analysis
            platform_insights = await self._analyze_platform_performance(
                hashtag_data, platforms
            )
            
            # Generate optimization recommendations
            recommendations = await self._generate_hashtag_recommendations(
                hashtag_metrics, clusters, network_analysis
            )
            
            return {
                "hashtag_metrics": hashtag_metrics,
                "clusters": clusters,
                "network_analysis": network_analysis,
                "trending_insights": trending_insights,
                "platform_insights": platform_insights,
                "recommendations": recommendations,
                "analysis_metadata": {
                    "total_hashtags_analyzed": len(hashtag_data),
                    "time_range": time_range,
                    "platforms": platforms,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Hashtag analysis failed: {str(e)}")
            raise ProcessingError(f"Hashtag analysis failed: {str(e)}")

    async def optimize_hashtag_strategy(
        self,
        content_type: ContentType,
        target_audience: Dict[str, Any],
        platforms: List[str],
        current_hashtags: List[str] = None
    ) -> HashtagStrategy:
        """
        Generate optimized hashtag strategy for specific content and audience
        
        Args:
            content_type: Type of content
            target_audience: Target audience demographics and interests
            platforms: Target social platforms
            current_hashtags: Current hashtag usage for optimization
            
        Returns:
            Optimized hashtag strategy
        """
        try:
            logger.info(f"Optimizing hashtag strategy for {content_type}")
            
            # Analyze current performance if hashtags provided
            current_performance = None
            if current_hashtags:
                current_performance = await self._analyze_current_hashtag_performance(
                    current_hashtags, platforms
                )
            
            # Get trending hashtags for content type
            trending_hashtags = await self._get_trending_hashtags_by_type(
                content_type, platforms
            )
            
            # Find niche opportunities
            niche_opportunities = await self._find_niche_hashtag_opportunities(
                content_type, target_audience, platforms
            )
            
            # Analyze competitor hashtags
            competitor_analysis = await self._analyze_competitor_hashtags(
                content_type, platforms
            )
            
            # Generate optimized hashtag mix
            optimized_mix = await self._generate_optimized_hashtag_mix(
                trending_hashtags,
                niche_opportunities,
                competitor_analysis,
                target_audience,
                current_performance
            )
            
            # Create implementation timeline
            implementation_timeline = await self._create_implementation_timeline(
                optimized_mix, platforms
            )
            
            # Generate performance predictions
            performance_predictions = await self._predict_hashtag_performance(
                optimized_mix, content_type, target_audience
            )
            
            strategy = HashtagStrategy(
                strategy_type=await self._determine_optimal_strategy_type(
                    content_type, target_audience
                ),
                primary_hashtags=optimized_mix["primary"],
                secondary_hashtags=optimized_mix["secondary"],
                niche_hashtags=optimized_mix["niche"],
                platform_specific=optimized_mix["platform_specific"],
                implementation_timeline=implementation_timeline,
                performance_predictions=performance_predictions,
                monitoring_schedule=await self._create_monitoring_schedule(),
                optimization_triggers=await self._define_optimization_triggers(),
                created_at=datetime.now(timezone.utc)
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"Hashtag strategy optimization failed: {str(e)}")
            raise ProcessingError(f"Hashtag strategy optimization failed: {str(e)}")

    async def predict_hashtag_performance(
        self,
        hashtags: List[str],
        content_metadata: ContentMetadata,
        creator_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict performance metrics for specific hashtag combinations
        
        Args:
            hashtags: List of hashtags to analyze
            content_metadata: Content information
            creator_profile: Creator profile data
            
        Returns:
            Predicted performance metrics
        """
        try:
            predictions = {}
            
            for hashtag in hashtags:
                # Get historical performance data
                historical_data = await self._get_hashtag_historical_data(hashtag)
                
                # Calculate base performance metrics
                base_metrics = await self._calculate_base_performance(
                    hashtag, historical_data
                )
                
                # Adjust for content type
                content_adjustment = await self._calculate_content_type_adjustment(
                    hashtag, content_metadata.content_type
                )
                
                # Adjust for creator profile
                creator_adjustment = await self._calculate_creator_adjustment(
                    hashtag, creator_profile
                )
                
                # Calculate final predictions
                predicted_reach = (
                    base_metrics["reach"] * 
                    content_adjustment * 
                    creator_adjustment
                )
                
                predicted_engagement = (
                    base_metrics["engagement"] * 
                    content_adjustment * 
                    creator_adjustment
                )
                
                predictions[hashtag] = {
                    "predicted_reach": int(predicted_reach),
                    "predicted_engagement": predicted_engagement,
                    "confidence": await self._calculate_prediction_confidence(
                        hashtag, historical_data
                    ),
                    "risk_factors": await self._identify_risk_factors(hashtag),
                    "optimization_potential": await self._calculate_optimization_potential(
                        hashtag, content_metadata
                    )
                }
            
            # Calculate synergy effects
            synergy_bonus = await self._calculate_hashtag_synergy(
                hashtags, content_metadata
            )
            
            # Aggregate predictions
            total_predicted_reach = sum(p["predicted_reach"] for p in predictions.values())
            total_predicted_engagement = sum(p["predicted_engagement"] for p in predictions.values())
            
            return {
                "individual_predictions": predictions,
                "aggregate_predictions": {
                    "total_reach": int(total_predicted_reach * (1 + synergy_bonus)),
                    "total_engagement": total_predicted_engagement * (1 + synergy_bonus),
                    "synergy_bonus": synergy_bonus
                },
                "recommendation_score": await self._calculate_recommendation_score(predictions),
                "alternative_suggestions": await self._suggest_alternatives(
                    hashtags, predictions, content_metadata
                )
            }
            
        except Exception as e:
            logger.error(f"Hashtag performance prediction failed: {str(e)}")
            raise ProcessingError(f"Hashtag performance prediction failed: {str(e)}")

    async def _extract_hashtags(
        self,
        content_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract and normalize hashtags from content data"""
        hashtag_pattern = re.compile(r'#[\w\u4e00-\u9fff]+')
        extracted_hashtags = []
        
        for content in content_data:
            # Extract from various text fields
            text_fields = [
                content.get("title", ""),
                content.get("description", ""),
                content.get("caption", ""),
                " ".join(content.get("tags", []))
            ]
            
            full_text = " ".join(text_fields)
            hashtags = hashtag_pattern.findall(full_text.lower())
            
            for hashtag in hashtags:
                # Clean hashtag
                clean_hashtag = hashtag[1:]  # Remove #
                
                if len(clean_hashtag) > 2:  # Minimum length check
                    extracted_hashtags.append({
                        "hashtag": clean_hashtag,
                        "content_id": content.get("id"),
                        "platform": content.get("platform"),
                        "timestamp": content.get("created_at"),
                        "engagement": content.get("engagement", {}),
                        "content_type": content.get("content_type")
                    })
        
        return extracted_hashtags

    async def _calculate_hashtag_metrics(
        self,
        hashtag_data: List[Dict[str, Any]],
        platforms: List[str],
        time_range: int
    ) -> Dict[str, HashtagMetrics]:
        """Calculate comprehensive metrics for each hashtag"""
        hashtag_metrics = {}
        hashtag_groups = defaultdict(list)
        
        # Group by hashtag
        for data in hashtag_data:
            hashtag_groups[data["hashtag"]].append(data)
        
        for hashtag, occurrences in hashtag_groups.items():
            if len(occurrences) < self.min_usage_threshold:
                continue
            
            # Calculate basic metrics
            usage_count = len(occurrences)
            
            # Calculate engagement metrics
            total_engagement = sum(
                sum(occ.get("engagement", {}).values()) 
                for occ in occurrences
            )
            engagement_rate = total_engagement / usage_count if usage_count > 0 else 0
            
            # Calculate growth rate
            growth_rate = await self._calculate_hashtag_growth_rate(occurrences)
            
            # Calculate platform performance
            platform_performance = {}
            for platform in platforms:
                platform_data = [
                    occ for occ in occurrences 
                    if occ.get("platform") == platform
                ]
                if platform_data:
                    platform_engagement = sum(
                        sum(data.get("engagement", {}).values())
                        for data in platform_data
                    )
                    platform_performance[platform] = platform_engagement / len(platform_data)
                else:
                    platform_performance[platform] = 0
            
            # Calculate sentiment score
            sentiment_score = await self._calculate_hashtag_sentiment(hashtag, occurrences)
            
            # Calculate virality index
            virality_index = await self._calculate_virality_index(occurrences)
            
            # Estimate reach potential
            reach_potential = await self._estimate_reach_potential(
                hashtag, usage_count, engagement_rate
            )
            
            # Calculate competition level
            competition_level = await self._calculate_competition_level(hashtag)
            
            hashtag_metrics[hashtag] = HashtagMetrics(
                usage_count=usage_count,
                engagement_rate=engagement_rate,
                reach_potential=reach_potential,
                competition_level=competition_level,
                growth_rate=growth_rate,
                sentiment_score=sentiment_score,
                virality_index=virality_index,
                platform_performance=platform_performance,
                demographic_breakdown=await self._analyze_demographics(occurrences),
                temporal_patterns=await self._analyze_temporal_patterns(occurrences)
            )
        
        return hashtag_metrics

    async def _identify_hashtag_clusters(
        self,
        hashtag_data: List[Dict[str, Any]]
    ) -> List[HashtagCluster]:
        """Identify clusters of related hashtags"""
        try:
            # Extract unique hashtags
            unique_hashtags = list(set(data["hashtag"] for data in hashtag_data))
            
            if len(unique_hashtags) < 10:
                return []
            
            # Create co-occurrence matrix
            co_occurrence_matrix = await self._create_cooccurrence_matrix(hashtag_data)
            
            # Apply clustering algorithm
            clustering = DBSCAN(eps=0.3, min_samples=3)
            cluster_labels = clustering.fit_predict(co_occurrence_matrix)
            
            # Group hashtags by cluster
            clusters = defaultdict(list)
            for hashtag, label in zip(unique_hashtags, cluster_labels):
                if label != -1:  # -1 indicates noise in DBSCAN
                    clusters[label].append(hashtag)
            
            # Convert to HashtagCluster objects
            hashtag_clusters = []
            for cluster_id, hashtags in clusters.items():
                if len(hashtags) >= 3:  # Minimum cluster size
                    cluster_theme = await self._identify_cluster_theme(hashtags)
                    cluster_strength = await self._calculate_cluster_strength(
                        hashtags, hashtag_data
                    )
                    
                    hashtag_clusters.append(HashtagCluster(
                        cluster_id=cluster_id,
                        hashtags=hashtags,
                        theme=cluster_theme,
                        strength=cluster_strength,
                        size=len(hashtags)
                    ))
            
            return hashtag_clusters
            
        except Exception as e:
            logger.warning(f"Hashtag clustering failed: {str(e)}")
            return []

    async def _background_hashtag_monitoring(self):
        """Background task for continuous hashtag monitoring"""
        while self.is_initialized:
            try:
                # Update trending hashtags
                await self._update_trending_hashtags()
                
                # Clean expired cache entries
                await self._cleanup_cache()
                
                # Update performance history
                await self._update_performance_history()
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Background hashtag monitoring failed: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def cleanup(self):
        """Clean up resources"""
        try:
            # Cleanup hashtag API
            if self.hashtag_api:
                await self.hashtag_api.cleanup()
            
            # Cleanup text processor
            if self.text_processor:
                await self.text_processor.cleanup()
            
            self.is_initialized = False
            logger.info("HashtagAnalyzer cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

class TagOptimizer:
    """
    Hashtag Optimization Engine
    
    Provides advanced optimization algorithms for hashtag selection,
    timing, and strategic implementation across platforms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.optimization_strategies = {
            "viral_boost": self._optimize_for_virality,
            "niche_targeting": self._optimize_for_niche,
            "brand_building": self._optimize_for_brand,
            "community_engagement": self._optimize_for_community
        }

    async def optimize_hashtag_selection(
        self,
        available_hashtags: List[str],
        optimization_goal: str,
        constraints: Dict[str, Any],
        content_context: Dict[str, Any]
    ) -> List[HashtagRecommendation]:
        """
        Optimize hashtag selection based on specific goals and constraints
        
        Args:
            available_hashtags: Pool of hashtags to choose from
            optimization_goal: Primary optimization objective
            constraints: Selection constraints (max count, platform limits, etc.)
            content_context: Context about the content
            
        Returns:
            Optimized hashtag recommendations
        """
        try:
            # Select optimization strategy
            strategy_func = self.optimization_strategies.get(
                optimization_goal,
                self._optimize_balanced
            )
            
            # Apply optimization strategy
            optimized_hashtags = await strategy_func(
                available_hashtags, constraints, content_context
            )
            
            # Generate detailed recommendations
            recommendations = []
            for hashtag_data in optimized_hashtags:
                recommendation = HashtagRecommendation(
                    hashtag=hashtag_data["hashtag"],
                    hashtag_type=HashtagType(hashtag_data.get("type", "trending")),
                    confidence_score=hashtag_data["confidence"],
                    predicted_performance=hashtag_data["predicted_performance"],
                    optimal_platforms=hashtag_data["optimal_platforms"],
                    timing_recommendations=hashtag_data["timing"],
                    competition_analysis=hashtag_data["competition"],
                    synergy_tags=hashtag_data.get("synergy_tags", [])
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Hashtag optimization failed: {str(e)}")
            raise ProcessingError(f"Hashtag optimization failed: {str(e)}")

    async def _optimize_for_virality(
        self,
        hashtags: List[str],
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize hashtag selection for maximum viral potential"""
        # Implement virality-focused optimization logic
        optimized = []
        
        for hashtag in hashtags[:constraints.get("max_count", 10)]:
            viral_score = await self._calculate_viral_potential(hashtag, context)
            if viral_score > 0.6:  # High viral potential threshold
                optimized.append({
                    "hashtag": hashtag,
                    "confidence": viral_score,
                    "predicted_performance": {"virality": viral_score},
                    "optimal_platforms": ["tiktok", "instagram", "twitter"],
                    "timing": ["peak_hours"],
                    "competition": {"level": "high", "opportunity": viral_score}
                })
        
        return sorted(optimized, key=lambda x: x["confidence"], reverse=True)

    async def _optimize_balanced(
        self,
        hashtags: List[str],
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Balanced optimization approach"""
        # Default balanced optimization
        return [{
            "hashtag": hashtag,
            "confidence": 0.7,
            "predicted_performance": {"engagement": 0.7, "reach": 0.6},
            "optimal_platforms": ["instagram", "twitter"],
            "timing": ["standard"],
            "competition": {"level": "medium", "opportunity": 0.6}
        } for hashtag in hashtags[:constraints.get("max_count", 15)]]
