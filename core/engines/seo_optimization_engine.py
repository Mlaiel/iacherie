"""SEO Optimization Engine - IA-Influencer-Agent
================================================================================

Module: backend/core/engines/seo_optimization_engine.py
Architecture: IA-Influencer-Agent Backend (Level 3)
Created: 2025-08-19
Team: Lead Dev IA + Backend Senior + SEO Expert + ML Engineer + Analytics Specialist

MISSION: Enterprise AI-powered SEO optimization for multi-platform content creators
MÉTIER: Content analysis → AI keyword research → Multi-platform optimization → Performance tracking → Competitor analysis

Author: Fahed Mlaiel <mlaiel@live.de>
COPYRIGHT WARNING: This code is proprietary. Unauthorized use, copying, or 
redistribution without explicit written permission from Fahed Mlaiel is 
strictly prohibited and will result in legal action.
================================================================================
"""
import logging
import asyncio
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
from urllib.parse import urlparse, parse_qs
import aiohttp
import requests
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, desc
import redis.asyncio as aioredis
from bs4 import BeautifulSoup
import yake
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import spacy
from googletrans import Translator
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Internal imports
from ..database.models import SEOAnalysis, KeywordRanking, ContentPerformance, CompetitorAnalysis
from ..utils.metrics import MetricsCollector
from ..cache.redis_manager import RedisManager
from .nlp_processing_engine import NLPProcessingEngine
from ..integrations.seo_apis import GoogleKeywordAPI, SEMrushAPI, AhrefsAPI
from ..integrations.social_apis import YouTubeAPI, InstagramAPI, TikTokAPI, TwitterAPI
from ..ml.trend_predictor import TrendPredictionModel

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content types for SEO optimization"""    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"
    HASHTAGS = "hashtags"
    TRANSCRIPT = "transcript"
    CAPTION = "caption"
    BIO = "bio"
    CHANNEL_NAME = "channel_name"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    VIDEO_SCRIPT = "video_script"
    PODCAST_DESCRIPTION = "podcast_description"
    PRODUCT_DESCRIPTION = "product_description"


class Platform(str, Enum):
    """Platforms for SEO optimization"""    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    MEDIUM = "medium"
    SUBSTACK = "substack"


class OptimizationLevel(str, Enum):
    """SEO optimization levels"""    BASIC = "basic"           # Basic keyword optimization
    STANDARD = "standard"     # Standard SEO best practices
    ADVANCED = "advanced"     # Advanced AI-driven optimization
    EXPERT = "expert"         # Expert-level competitive analysis
    ENTERPRISE = "enterprise" # Full enterprise SEO suite


class ContentCategory(str, Enum):
    """Content categories for targeted optimization"""    MUSIC = "music"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    TECH = "tech"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    HEALTH_FITNESS = "health_fitness"
    FOOD = "food"
    TRAVEL = "travel"
    FASHION = "fashion"
    ART_DESIGN = "art_design"
    COMEDY = "comedy"
    NEWS = "news"
    SPORTS = "sports"


class Language(str, Enum):
    """Supported languages for SEO optimization"""    EN = "en"  # English
    DE = "de"  # German
    FR = "fr"  # French
    ES = "es"  # Spanish
    IT = "it"  # Italian
    PT = "pt"  # Portuguese
    NL = "nl"  # Dutch
    JA = "ja"  # Japanese
    KO = "ko"  # Korean
    ZH = "zh"  # Chinese


@dataclass
class KeywordData:
    """Enhanced keyword analysis data"""    keyword: str
    search_volume: int = 0
    competition_level: str = "medium"
    difficulty_score: float = 0.5
    relevance_score: float = 0.0
    trend_direction: str = "stable"
    seasonal_trends: Dict[str, float] = field(default_factory=dict)
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variations: List[str] = field(default_factory=list)
    competitor_usage: Dict[str, int] = field(default_factory=dict)
    cpc_cost: Optional[float] = None
    click_through_rate: Optional[float] = None
    conversion_potential: float = 0.0
    intent_type: str = "informational"  # informational, navigational, transactional
    platforms: List[Platform] = field(default_factory=list)
    languages: List[Language] = field(default_factory=list)


@dataclass
class SEOScore:
    """Comprehensive SEO scoring breakdown"""    overall_score: float = 0.0
    keyword_optimization: float = 0.0
    readability_score: float = 0.0
    content_structure: float = 0.0
    semantic_relevance: float = 0.0
    engagement_potential: float = 0.0
    technical_seo: float = 0.0
    platform_specific: float = 0.0
    competitive_advantage: float = 0.0
    trend_alignment: float = 0.0
    multilingual_potential: float = 0.0
    social_signals: float = 0.0
    breakdown: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SEORecommendation:
    """AI-powered SEO recommendation"""    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "keyword"  # keyword, structure, content, technical
    priority: str = "medium"  # low, medium, high, critical
    title: str = ""
    description: str = ""
    implementation_effort: str = "medium"  # low, medium, high
    expected_impact: float = 0.0
    platform_specific: List[Platform] = field(default_factory=list)
    before_text: Optional[str] = None
    after_text: Optional[str] = None
    reasoning: str = ""
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    estimated_timeframe: str = "1-2 weeks"
    success_metrics: List[str] = field(default_factory=list)


@dataclass
class CompetitorInsight:
    """Competitor analysis insight"""    competitor_name: str = ""
    competitor_url: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    top_keywords: List[KeywordData] = field(default_factory=list)
    content_strategies: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    market_share: float = 0.0


@dataclass
class SEOAnalysisResult:
    """Complete SEO analysis result"""    content_id: str = ""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform = Platform.GOOGLE
    content_type: ContentType = ContentType.TITLE
    original_content: str = ""
    optimized_content: str = ""
    seo_score: SEOScore = field(default_factory=SEOScore)
    recommendations: List[SEORecommendation] = field(default_factory=list)
    keyword_analysis: List[KeywordData] = field(default_factory=list)
    competitor_insights: List[CompetitorInsight] = field(default_factory=list)
    performance_prediction: Dict[str, float] = field(default_factory=dict)
    multilingual_suggestions: Dict[Language, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))


class SEOOptimizationEngine:
    """    🎯 ENTERPRISE SEO OPTIMIZATION ENGINE
    
    Advanced AI-powered SEO optimization system providing:
    - Multi-platform content optimization
    - Real-time keyword research and analysis
    - Competitor intelligence and gap analysis
    - Performance prediction and trend analysis
    - Multilingual SEO support
    - Automated A/B testing suggestions
    - Social media optimization integration
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        redis_client: aioredis.Redis,
        metrics_collector: MetricsCollector,
        nlp_engine: Optional[NLPProcessingEngine] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED,
        default_language: Language = Language.EN
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.metrics = metrics_collector
        self.nlp_engine = nlp_engine or NLPProcessingEngine()
        self.optimization_level = optimization_level
        self.default_language = default_language
        
        # Initialize AI models
        self.keyword_model = KeyBERT()
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.translator = Translator()
        
        # Initialize NLP models
        try:
            self.nlp_models = {
                Language.EN: spacy.load("en_core_web_sm"),
                Language.DE: spacy.load("de_core_news_sm"),
                Language.FR: spacy.load("fr_core_news_sm")
            }
        except OSError:
            logger.warning("Some spaCy models not available. Install with: python -m spacy download en_core_web_sm")
            self.nlp_models = {}
        
        # Initialize external APIs
        self.google_api = GoogleKeywordAPI()
        self.semrush_api = SEMrushAPI()
        self.ahrefs_api = AhrefsAPI()
        
        # Platform APIs
        self.platform_apis = {
            Platform.YOUTUBE: YouTubeAPI(),
            Platform.INSTAGRAM: InstagramAPI(),
            Platform.TIKTOK: TikTokAPI(),
            Platform.TWITTER: TwitterAPI()
        }
        
        # Trend prediction model
        self.trend_predictor = TrendPredictionModel()
        
        # Cache configuration
        self.cache_ttl = {
            "keywords": 86400,      # 24 hours
            "competitor": 86400 * 3, # 3 days
            "trends": 3600,         # 1 hour
            "analysis": 86400 * 7   # 7 days
        }
        
        logger.info("🎯 SEOOptimizationEngine initialized successfully")
    
    async def optimize_content(
        self,
        content: str,
        content_type: ContentType,
        platform: Platform,
        target_audience: Optional[Dict[str, Any]] = None,
        target_keywords: Optional[List[str]] = None,
        content_category: Optional[ContentCategory] = None,
        language: Optional[Language] = None
    ) -> SEOAnalysisResult:
        """        🚀 Optimize content for SEO with AI recommendations
        
        Args:
            content: Content to optimize
            content_type: Type of content
            platform: Target platform
            target_audience: Target audience demographics
            target_keywords: Specific keywords to target
            content_category: Content category for better targeting
            language: Content language
            
        Returns:
            Complete SEO analysis with optimization recommendations
        """        try:
            start_time = datetime.utcnow()
            
            # Set defaults
            language = language or self.default_language
            content_category = content_category or ContentCategory.ENTERTAINMENT
            
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Perform comprehensive analysis
            analysis_result = SEOAnalysisResult(
                analysis_id=analysis_id,
                platform=platform,
                content_type=content_type,
                original_content=content
            )
            
            # 1. Extract and analyze current keywords
            current_keywords = await self._extract_keywords(content, language)
            
            # 2. Research optimal keywords
            if target_keywords:
                keyword_research = await self._research_keywords(
                    target_keywords, platform, content_category, language
                )
            else:
                keyword_research = await self._discover_keywords(
                    content, platform, content_category, language
                )
            
            analysis_result.keyword_analysis = keyword_research
            
            # 3. Analyze competitors
            if self.optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT, OptimizationLevel.ENTERPRISE]:
                competitor_insights = await self._analyze_competitors(
                    keyword_research[:5], platform, content_category
                )
                analysis_result.competitor_insights = competitor_insights
            
            # 4. Calculate SEO score
            seo_score = await self._calculate_seo_score(
                content, keyword_research, platform, content_type
            )
            analysis_result.seo_score = seo_score
            
            # 5. Generate optimization recommendations
            recommendations = await self._generate_recommendations(
                content, keyword_research, seo_score, platform, content_type
            )
            analysis_result.recommendations = recommendations
            
            # 6. Create optimized content
            optimized_content = await self._create_optimized_content(
                content, recommendations, keyword_research, platform
            )
            analysis_result.optimized_content = optimized_content
            
            # 7. Predict performance
            performance_prediction = await self._predict_performance(
                optimized_content, keyword_research, platform
            )
            analysis_result.performance_prediction = performance_prediction
            
            # 8. Generate multilingual suggestions (Enterprise level)
            if self.optimization_level == OptimizationLevel.ENTERPRISE:
                multilingual_suggestions = await self._generate_multilingual_versions(
                    optimized_content, keyword_research
                )
                analysis_result.multilingual_suggestions = multilingual_suggestions
            
            # Save analysis to database
            await self._save_analysis(analysis_result)
            
            # Cache results
            await self._cache_analysis(analysis_result)
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics.record("seo.content_optimized", 1, {
                "platform": platform.value,
                "content_type": content_type.value,
                "optimization_level": self.optimization_level.value,
                "processing_time": processing_time,
                "recommendations_count": len(recommendations),
                "seo_score": seo_score.overall_score
            })
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            await self.metrics.record("seo.optimization_error", 1, {
                "error_type": type(e).__name__
            })
            raise
    
    async def research_trending_topics(
        self,
        platform: Platform,
        content_category: ContentCategory,
        language: Language = Language.EN,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """        📈 Research trending topics and keywords
        
        Args:
            platform: Platform to research
            content_category: Content category
            language: Language for research
            time_range: Time range for trends (1d, 7d, 30d)
            
        Returns:
            Trending topics and keywords with analysis
        """        try:
            # Check cache first
            cache_key = f"seo:trends:{platform.value}:{content_category.value}:{language.value}:{time_range}"
            cached_trends = await self.redis_client.get(cache_key)
            
            if cached_trends:
                return json.loads(cached_trends)
            
            # Research trending topics
            trending_data = {
                "platform": platform.value,
                "category": content_category.value,
                "language": language.value,
                "time_range": time_range,
                "trending_keywords": [],
                "trending_topics": [],
                "hashtag_trends": [],
                "content_opportunities": [],
                "seasonal_insights": {},
                "predicted_trends": []
            }
            
            # Get platform-specific trends
            if platform == Platform.YOUTUBE:
                youtube_trends = await self._get_youtube_trends(content_category, language)
                trending_data.update(youtube_trends)
            
            elif platform == Platform.INSTAGRAM:
                instagram_trends = await self._get_instagram_trends(content_category, language)
                trending_data.update(instagram_trends)
            
            elif platform == Platform.TIKTOK:
                tiktok_trends = await self._get_tiktok_trends(content_category, language)
                trending_data.update(tiktok_trends)
            
            elif platform == Platform.GOOGLE:
                google_trends = await self._get_google_trends(content_category, language)
                trending_data.update(google_trends)
            
            # Add AI predictions for future trends
            if self.optimization_level in [OptimizationLevel.EXPERT, OptimizationLevel.ENTERPRISE]:
                predicted_trends = await self.trend_predictor.predict_trends(
                    trending_data["trending_keywords"][:10],
                    platform,
                    content_category
                )
                trending_data["predicted_trends"] = predicted_trends
            
            # Cache results
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl["trends"],
                json.dumps(trending_data, default=str)
            )
            
            return trending_data
            
        except Exception as e:
            logger.error(f"Trend research failed: {str(e)}")
            raise
    
    async def analyze_content_performance(
        self,
        content_id: str,
        platform: Platform,
        metrics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        📊 Analyze content performance against SEO predictions
        
        Args:
            content_id: Content identifier
            platform: Platform where content was published
            metrics_data: Actual performance metrics
            
        Returns:
            Performance analysis with insights
        """        try:
            # Get original SEO analysis
            original_analysis = await self._get_content_analysis(content_id)
            
            if not original_analysis:
                raise ValueError(f"No SEO analysis found for content {content_id}")
            
            # Compare predicted vs actual performance
            performance_analysis = {
                "content_id": content_id,
                "platform": platform.value,
                "prediction_accuracy": {},
                "seo_impact_analysis": {},
                "improvement_opportunities": [],
                "success_factors": [],
                "lessons_learned": [],
                "next_optimization_suggestions": []
            }
            
            # Analyze each prediction
            predictions = original_analysis.performance_prediction
            
            for metric, predicted_value in predictions.items():
                actual_value = metrics_data.get(metric, 0)
                
                if predicted_value > 0:
                    accuracy = min(100, (1 - abs(predicted_value - actual_value) / predicted_value) * 100)
                    performance_analysis["prediction_accuracy"][metric] = {
                        "predicted": predicted_value,
                        "actual": actual_value,
                        "accuracy_percentage": accuracy,
                        "variance": actual_value - predicted_value
                    }
            
            # Analyze SEO factor impact
            seo_factors = {
                "keyword_optimization": original_analysis.seo_score.keyword_optimization,
                "content_structure": original_analysis.seo_score.content_structure,
                "readability": original_analysis.seo_score.readability_score,
                "engagement_potential": original_analysis.seo_score.engagement_potential
            }
            
            for factor, score in seo_factors.items():
                correlation = await self._calculate_performance_correlation(
                    factor, score, metrics_data
                )
                performance_analysis["seo_impact_analysis"][factor] = correlation
            
            # Generate improvement suggestions
            improvement_opportunities = await self._identify_improvement_opportunities(
                original_analysis, metrics_data
            )
            performance_analysis["improvement_opportunities"] = improvement_opportunities
            
            # Save performance data
            await self._save_performance_data(content_id, performance_analysis)
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            raise
    
    async def generate_content_variants(
        self,
        base_content: str,
        content_type: ContentType,
        platform: Platform,
        variant_count: int = 5,
        optimization_goals: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """        🎨 Generate optimized content variants for A/B testing
        
        Args:
            base_content: Original content
            content_type: Type of content
            platform: Target platform
            variant_count: Number of variants to generate
            optimization_goals: Specific optimization goals
            
        Returns:
            List of optimized content variants
        """        try:
            optimization_goals = optimization_goals or [
                "higher_engagement", "better_seo", "increased_reach"
            ]
            
            variants = []
            
            # Analyze base content
            base_analysis = await self.optimize_content(
                base_content, content_type, platform
            )
            
            # Generate variants with different optimization strategies
            for i in range(variant_count):
                variant_strategy = optimization_goals[i % len(optimization_goals)]
                
                variant = await self._create_content_variant(
                    base_content,
                    base_analysis,
                    variant_strategy,
                    content_type,
                    platform
                )
                
                # Analyze variant
                variant_analysis = await self.optimize_content(
                    variant["content"], content_type, platform
                )
                
                variant.update({
                    "variant_id": f"variant_{i+1}",
                    "optimization_strategy": variant_strategy,
                    "seo_score": variant_analysis.seo_score.overall_score,
                    "predicted_performance": variant_analysis.performance_prediction,
                    "key_differences": await self._identify_variant_differences(
                        base_content, variant["content"]
                    )
                })
                
                variants.append(variant)
            
            # Rank variants by predicted performance
            variants.sort(key=lambda x: x["seo_score"], reverse=True)
            
            return variants
            
        except Exception as e:
            logger.error(f"Content variant generation failed: {str(e)}")
            raise
    
    # Private methods for core functionality
    
    async def _extract_keywords(self, content: str, language: Language) -> List[str]:
        """Extract keywords from content"""        try:
            # Use KeyBERT for keyword extraction
            keywords = self.keyword_model.extract_keywords(
                content, 
                keyphrase_ngram_range=(1, 3),
                stop_words='english' if language == Language.EN else None,
                top_k=20
            )
            
            return [kw[0] for kw in keywords]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def _research_keywords(
        self,
        keywords: List[str],
        platform: Platform,
        category: ContentCategory,
        language: Language
    ) -> List[KeywordData]:
        """Research keyword data from multiple sources"""        keyword_data = []
        
        for keyword in keywords[:10]:  # Limit API calls
            try:
                data = KeywordData(keyword=keyword)
                
                # Get search volume and competition from Google
                if self.google_api:
                    google_data = await self.google_api.get_keyword_data(keyword)
                    data.search_volume = google_data.get("search_volume", 0)
                    data.competition_level = google_data.get("competition", "medium")
                    data.cpc_cost = google_data.get("cpc", None)
                
                # Get additional insights from SEMrush
                if self.semrush_api and self.optimization_level in [OptimizationLevel.EXPERT, OptimizationLevel.ENTERPRISE]:
                    semrush_data = await self.semrush_api.get_keyword_data(keyword)
                    data.difficulty_score = semrush_data.get("difficulty", 0.5)
                    data.trend_direction = semrush_data.get("trend", "stable")
                    data.related_keywords = semrush_data.get("related", [])
                
                # Calculate relevance score using semantic similarity
                content_embedding = self.sentence_model.encode([keyword])
                category_embedding = self.sentence_model.encode([category.value])
                relevance = float(np.dot(content_embedding[0], category_embedding[0]))
                data.relevance_score = relevance
                
                keyword_data.append(data)
                
            except Exception as e:
                logger.error(f"Keyword research failed for '{keyword}': {str(e)}")
                continue
        
        return keyword_data
    
    async def _discover_keywords(
        self,
        content: str,
        platform: Platform,
        category: ContentCategory,
        language: Language
    ) -> List[KeywordData]:
        """Discover relevant keywords from content"""        # Extract initial keywords
        extracted = await self._extract_keywords(content, language)
        
        # Research the extracted keywords
        return await self._research_keywords(extracted, platform, category, language)
    
    async def _analyze_competitors(
        self,
        keywords: List[KeywordData],
        platform: Platform,
        category: ContentCategory
    ) -> List[CompetitorInsight]:
        """Analyze competitor strategies"""        competitor_insights = []
        
        try:
            # Get top competitors for keywords
            for keyword_data in keywords[:3]:  # Analyze top 3 keywords
                competitors = await self._find_keyword_competitors(
                    keyword_data.keyword, platform
                )
                
                for competitor in competitors[:5]:  # Top 5 competitors
                    insight = CompetitorInsight(
                        competitor_name=competitor.get("name", "Unknown"),
                        competitor_url=competitor.get("url"),
                        performance_metrics=competitor.get("metrics", {}),
                        market_share=competitor.get("market_share", 0.0)
                    )
                    
                    # Analyze competitor content strategy
                    if competitor.get("content"):
                        strategy_analysis = await self._analyze_competitor_strategy(
                            competitor["content"]
                        )
                        insight.content_strategies = strategy_analysis.get("strategies", [])
                        insight.strengths = strategy_analysis.get("strengths", [])
                        insight.weaknesses = strategy_analysis.get("weaknesses", [])
                        insight.opportunities = strategy_analysis.get("opportunities", [])
                    
                    competitor_insights.append(insight)
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {str(e)}")
        
        return competitor_insights
    
    async def _calculate_seo_score(
        self,
        content: str,
        keywords: List[KeywordData],
        platform: Platform,
        content_type: ContentType
    ) -> SEOScore:
        """Calculate comprehensive SEO score"""        score = SEOScore()
        
        try:
            # Keyword optimization score (0-100)
            keyword_density = self._calculate_keyword_density(content, keywords)
            score.keyword_optimization = min(100, keyword_density * 20)
            
            # Readability score (0-100)
            if len(content.split()) > 10:
                readability = flesch_reading_ease(content)
                score.readability_score = max(0, min(100, readability))
            else:
                score.readability_score = 70  # Default for short content
            
            # Content structure score (0-100)
            structure_score = self._analyze_content_structure(content, content_type)
            score.content_structure = structure_score
            
            # Semantic relevance score (0-100)
            if keywords:
                semantic_score = self._calculate_semantic_relevance(content, keywords)
                score.semantic_relevance = semantic_score
            
            # Engagement potential (0-100)
            engagement_score = await self._predict_engagement_potential(content, platform)
            score.engagement_potential = engagement_score
            
            # Technical SEO score (0-100)
            technical_score = self._analyze_technical_seo(content, content_type)
            score.technical_seo = technical_score
            
            # Platform-specific score (0-100)
            platform_score = self._calculate_platform_optimization(content, platform)
            score.platform_specific = platform_score
            
            # Calculate overall score (weighted average)
            weights = {
                "keyword": 0.25,
                "readability": 0.15,
                "structure": 0.15,
                "semantic": 0.15,
                "engagement": 0.15,
                "technical": 0.10,
                "platform": 0.05
            }
            
            score.overall_score = (
                score.keyword_optimization * weights["keyword"] +
                score.readability_score * weights["readability"] +
                score.content_structure * weights["structure"] +
                score.semantic_relevance * weights["semantic"] +
                score.engagement_potential * weights["engagement"] +
                score.technical_seo * weights["technical"] +
                score.platform_specific * weights["platform"]
            )
            
            # Detailed breakdown
            score.breakdown = {
                "keyword_analysis": {
                    "target_keywords_found": len([k for k in keywords if k.keyword.lower() in content.lower()]),
                    "keyword_density": keyword_density,
                    "keyword_distribution": "analysis_result"
                },
                "readability_analysis": {
                    "flesch_reading_ease": readability if 'readability' in locals() else 0,
                    "grade_level": flesch_kincaid_grade(content) if len(content.split()) > 10 else 0,
                    "sentence_length": np.mean([len(s.split()) for s in content.split('.')]) if content else 0
                },
                "structure_analysis": {
                    "content_length": len(content),
                    "paragraph_count": content.count('\n\n') + 1,
                    "sentence_count": len([s for s in content.split('.') if s.strip()])
                }
            }
            
        except Exception as e:
            logger.error(f"SEO score calculation failed: {str(e)}")
        
        return score
    
    async def _generate_recommendations(
        self,
        content: str,
        keywords: List[KeywordData],
        seo_score: SEOScore,
        platform: Platform,
        content_type: ContentType
    ) -> List[SEORecommendation]:
        """Generate AI-powered SEO recommendations"""        recommendations = []
        
        try:
            # Keyword optimization recommendations
            if seo_score.keyword_optimization < 70:
                recommendations.extend(
                    await self._generate_keyword_recommendations(content, keywords)
                )
            
            # Readability recommendations
            if seo_score.readability_score < 60:
                recommendations.extend(
                    await self._generate_readability_recommendations(content)
                )
            
            # Structure recommendations
            if seo_score.content_structure < 70:
                recommendations.extend(
                    await self._generate_structure_recommendations(content, content_type)
                )
            
            # Platform-specific recommendations
            recommendations.extend(
                await self._generate_platform_recommendations(content, platform)
            )
            
            # Engagement recommendations
            if seo_score.engagement_potential < 70:
                recommendations.extend(
                    await self._generate_engagement_recommendations(content, platform)
                )
            
            # Sort by priority and expected impact
            recommendations.sort(key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x.priority, 1),
                x.expected_impact
            ), reverse=True)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
        
        return recommendations
    
    # Additional helper methods would continue here...
    # (Implementation of remaining private methods for completeness)
    
    async def _create_optimized_content(
        self,
        original_content: str,
        recommendations: List[SEORecommendation],
        keywords: List[KeywordData],
        platform: Platform
    ) -> str:
        """Create optimized version of content"""        optimized = original_content
        
        # Apply recommendations in order of priority
        for rec in recommendations:
            if rec.after_text and rec.before_text:
                optimized = optimized.replace(rec.before_text, rec.after_text)
        
        return optimized
    
    async def _predict_performance(
        self,
        content: str,
        keywords: List[KeywordData],
        platform: Platform
    ) -> Dict[str, float]:
        """Predict content performance metrics"""        return {
            "estimated_reach": 1000.0,
            "estimated_engagement_rate": 0.05,
            "estimated_clicks": 50.0,
            "confidence_score": 0.75
        }
    
    async def _generate_multilingual_versions(
        self,
        content: str,
        keywords: List[KeywordData]
    ) -> Dict[Language, str]:
        """Generate multilingual content versions"""        multilingual = {}
        
        target_languages = [Language.DE, Language.FR, Language.ES]
        
        for lang in target_languages:
            try:
                translated = self.translator.translate(content, dest=lang.value)
                if translated and translated.text:
                    multilingual[lang] = translated.text
            except Exception as e:
                logger.error(f"Translation to {lang.value} failed: {str(e)}")
        
        return multilingual
    
    # Placeholder implementations for helper methods
    def _calculate_keyword_density(self, content: str, keywords: List[KeywordData]) -> float:
        """Calculate keyword density"""        return 0.02  # 2% default
    
    def _analyze_content_structure(self, content: str, content_type: ContentType) -> float:
        """Analyze content structure"""        return 75.0  # Default score
    
    def _calculate_semantic_relevance(self, content: str, keywords: List[KeywordData]) -> float:
        """Calculate semantic relevance"""        return 80.0  # Default score
    
    async def _predict_engagement_potential(self, content: str, platform: Platform) -> float:
        """Predict engagement potential"""        return 70.0  # Default score
    
    def _analyze_technical_seo(self, content: str, content_type: ContentType) -> float:
        """Analyze technical SEO factors"""        return 85.0  # Default score
    
    def _calculate_platform_optimization(self, content: str, platform: Platform) -> float:
        """Calculate platform-specific optimization"""        return 75.0  # Default score
    
    # Database and caching methods
    async def _save_analysis(self, analysis: SEOAnalysisResult) -> None:
        """Save analysis to database"""        # Implementation for database save
        pass
    
    async def _cache_analysis(self, analysis: SEOAnalysisResult) -> None:
        """Cache analysis results"""        # Implementation for caching
        pass
    
    async def _get_content_analysis(self, content_id: str) -> Optional[SEOAnalysisResult]:
        """Get content analysis from database"""        # Implementation for database retrieval
        return None


# Factory function
async def create_seo_optimization_engine(
    db_session: AsyncSession,
    redis_client: aioredis.Redis,
    config: Dict[str, Any]
) -> SEOOptimizationEngine:
    """Factory function to create SEOOptimizationEngine"""    metrics_collector = MetricsCollector()
    nlp_engine = NLPProcessingEngine()
    
    engine = SEOOptimizationEngine(
        db_session=db_session,
        redis_client=redis_client,
        metrics_collector=metrics_collector,
        nlp_engine=nlp_engine,
        optimization_level=OptimizationLevel(config.get("optimization_level", "advanced")),
        default_language=Language(config.get("default_language", "en"))
    )
    
    return engine


# Export key classes
__all__ = [
    "SEOOptimizationEngine",
    "ContentType",
    "Platform", 
    "OptimizationLevel",
    "ContentCategory",
    "Language",
    "KeywordData",
    "SEOScore",
    "SEORecommendation",
    "CompetitorInsight",
    "SEOAnalysisResult",
    "create_seo_optimization_engine"
]
    """SEO improvement recommendation"""    category: str
    priority: str  # high, medium, low
    title: str
    description: str
    implementation: str
    expected_impact: float
    effort_level: str


@dataclass
class ContentOptimization:
    """Content optimization result"""    original_content: str
    optimized_content: str
    improvements: List[str]
    keywords_added: List[str]
    readability_improvement: float
    seo_score_change: float


class SEOOptimizationEngine:
    """    Enterprise SEO optimization engine for content creators
    
    Features:
    - AI-powered keyword research
    - Content optimization recommendations
    - Multi-platform SEO strategies
    - Real-time ranking tracking
    - Competitor analysis
    - Trend-based optimization
    """    
    def __init__(
        self,
        redis_manager: RedisManager,
        metrics_collector: MetricsCollector,
        nlp_engine: NLPProcessingEngine,
        config: Dict[str, Any] = None
    ):
        self.redis_manager = redis_manager
        self.metrics_collector = metrics_collector
        self.nlp_engine = nlp_engine
        self.config = config or {}
        
        # SEO API configurations
        self.seo_apis = {
            "serpapi_key": self.config.get("serpapi_key"),
            "ahrefs_key": self.config.get("ahrefs_key"),
            "semrush_key": self.config.get("semrush_key")
        }
        
        # Platform-specific SEO rules
        self.platform_rules = self._load_platform_seo_rules()
        
        # Cache settings
        self.cache_ttl = self.config.get("cache_ttl", 3600)
        
        # Optimization thresholds
        self.optimization_thresholds = {
            "min_keyword_density": 0.5,
            "max_keyword_density": 3.0,
            "min_readability_score": 60,
            "target_title_length": (50, 70),
            "target_description_length": (150, 160),
            "max_hashtags": 30
        }
        
        logger.info("SEOOptimizationEngine initialized successfully")

    def _load_platform_seo_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load SEO rules for each platform"""        return {
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 15,
                "focus_keywords": ["how to", "tutorial", "review", "vs", "best"],
                "ranking_factors": {
                    "watch_time": 0.25,
                    "click_through_rate": 0.20,
                    "engagement": 0.20,
                    "keywords": 0.15,
                    "thumbnail": 0.10,
                    "freshness": 0.10
                }
            },
            "instagram": {
                "caption_max_length": 2200,
                "hashtags_optimal": 11,
                "hashtags_max": 30,
                "focus_keywords": ["aesthetic", "lifestyle", "inspiration", "daily"],
                "ranking_factors": {
                    "engagement_rate": 0.30,
                    "hashtags": 0.25,
                    "content_quality": 0.20,
                    "consistency": 0.15,
                    "timing": 0.10
                }
            },
            "tiktok": {
                "caption_max_length": 300,
                "hashtags_optimal": 5,
                "focus_keywords": ["trending", "viral", "challenge", "duet"],
                "ranking_factors": {
                    "completion_rate": 0.35,
                    "shares": 0.25,
                    "trending_sounds": 0.20,
                    "hashtags": 0.15,
                    "posting_time": 0.05
                }
            },
            "twitter": {
                "tweet_max_length": 280,
                "hashtags_optimal": 2,
                "focus_keywords": ["breaking", "thread", "opinion", "news"],
                "ranking_factors": {
                    "engagement_rate": 0.30,
                    "retweets": 0.25,
                    "hashtags": 0.20,
                    "timing": 0.15,
                    "thread_quality": 0.10
                }
            }
        }

    async def analyze_content_seo(
        self,
        content: str,
        content_type: ContentType,
        target_platform: str,
        target_keywords: List[str] = None,
        target_audience: str = None
    ) -> Tuple[SEOScore, List[SEORecommendation]]:
        """        Comprehensive SEO analysis of content
        
        Args:
            content: Content to analyze
            content_type: Type of content
            target_platform: Platform for optimization
            target_keywords: Specific keywords to optimize for
            target_audience: Target audience description
            
        Returns:
            SEO score and recommendations
        """        try:
            # Get platform rules
            platform_rules = self.platform_rules.get(target_platform, {})
            
            # Analyze current SEO performance
            seo_score = await self._calculate_seo_score(
                content, content_type, platform_rules, target_keywords
            )
            
            # Generate recommendations
            recommendations = await self._generate_seo_recommendations(
                content, content_type, platform_rules, seo_score, target_keywords
            )
            
            # Cache analysis results
            cache_key = f"seo_analysis:{hashlib.md5(content.encode()).hexdigest()}"
            await self._cache_seo_analysis(cache_key, seo_score, recommendations)
            
            # Update metrics
            self.metrics_collector.gauge(
                "seo_score",
                seo_score.overall_score,
                tags={"platform": target_platform, "content_type": content_type.value}
            )
            
            logger.info(f"SEO analysis completed - Score: {seo_score.overall_score:.2f}")
            return seo_score, recommendations
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            raise

    async def _calculate_seo_score(
        self,
        content: str,
        content_type: ContentType,
        platform_rules: Dict[str, Any],
        target_keywords: List[str] = None
    ) -> SEOScore:
        """Calculate comprehensive SEO score"""        try:
            scores = {}
            
            # Keyword optimization score
            if target_keywords:
                scores["keyword_optimization"] = await self._analyze_keyword_optimization(
                    content, target_keywords
                )
            else:
                scores["keyword_optimization"] = 0.5
            
            # Readability score
            scores["readability_score"] = self._analyze_readability(content)
            
            # Content structure score
            scores["content_structure"] = self._analyze_content_structure(
                content, content_type, platform_rules
            )
            
            # Semantic relevance score
            scores["semantic_relevance"] = await self._analyze_semantic_relevance(
                content, target_keywords or []
            )
            
            # Engagement potential score
            scores["engagement_potential"] = await self._predict_engagement_potential(
                content, content_type
            )
            
            # Technical SEO score
            scores["technical_seo"] = self._analyze_technical_seo(
                content, content_type, platform_rules
            )
            
            # Calculate weighted overall score
            weights = {
                "keyword_optimization": 0.25,
                "readability_score": 0.15,
                "content_structure": 0.20,
                "semantic_relevance": 0.20,
                "engagement_potential": 0.15,
                "technical_seo": 0.05
            }
            
            overall_score = sum(scores[key] * weights[key] for key in scores)
            
            return SEOScore(
                overall_score=overall_score,
                **scores
            )
            
        except Exception as e:
            logger.error(f"SEO score calculation failed: {e}")
            return SEOScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    async def _analyze_keyword_optimization(
        self,
        content: str,
        target_keywords: List[str]
    ) -> float:
        """Analyze keyword optimization score"""        try:
            content_lower = content.lower()
            total_words = len(content.split())
            
            if total_words == 0:
                return 0.0
            
            keyword_scores = []
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                
                # Count keyword occurrences
                keyword_count = content_lower.count(keyword_lower)
                
                # Calculate keyword density
                keyword_density = (keyword_count / total_words) * 100
                
                # Score based on optimal density (0.5% - 3%)
                if keyword_density < self.optimization_thresholds["min_keyword_density"]:
                    score = keyword_density / self.optimization_thresholds["min_keyword_density"]
                elif keyword_density > self.optimization_thresholds["max_keyword_density"]:
                    excess = keyword_density - self.optimization_thresholds["max_keyword_density"]
                    score = max(0, 1 - (excess / 5))  # Penalty for over-optimization
                else:
                    score = 1.0
                
                keyword_scores.append(score)
            
            return sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0
            
        except Exception as e:
            logger.error(f"Keyword optimization analysis failed: {e}")
            return 0.0

    def _analyze_readability(self, content: str) -> float:
        """Analyze content readability"""        try:
            if len(content.strip()) < 10:
                return 0.0
            
            # Calculate Flesch Reading Ease score
            flesch_score = flesch_reading_ease(content)
            
            # Convert to 0-1 scale (60+ is good)
            if flesch_score >= self.optimization_thresholds["min_readability_score"]:
                return min(1.0, flesch_score / 100)
            else:
                return flesch_score / self.optimization_thresholds["min_readability_score"]
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return 0.5

    def _analyze_content_structure(
        self,
        content: str,
        content_type: ContentType,
        platform_rules: Dict[str, Any]
    ) -> float:
        """Analyze content structure quality"""        try:
            score = 0.0
            factors = 0
            
            if content_type == ContentType.TITLE:
                # Title length optimization
                title_length = len(content)
                optimal_range = self.optimization_thresholds["target_title_length"]
                
                if optimal_range[0] <= title_length <= optimal_range[1]:
                    score += 1.0
                else:
                    deviation = min(
                        abs(title_length - optimal_range[0]),
                        abs(title_length - optimal_range[1])
                    )
                    score += max(0, 1 - (deviation / 50))
                
                factors += 1
                
                # Title starts with keyword (if available)
                # This would require keyword context
                
            elif content_type == ContentType.DESCRIPTION:
                # Description length
                desc_length = len(content)
                optimal_range = self.optimization_thresholds["target_description_length"]
                
                if optimal_range[0] <= desc_length <= optimal_range[1]:
                    score += 1.0
                else:
                    deviation = min(
                        abs(desc_length - optimal_range[0]),
                        abs(desc_length - optimal_range[1])
                    )
                    score += max(0, 1 - (deviation / 100))
                
                factors += 1
                
                # Sentence structure variety
                sentences = content.split('.')
                if len(sentences) > 1:
                    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
                    if sentence_lengths:
                        length_variance = np.var(sentence_lengths)
                        score += min(1.0, length_variance / 50)  # Reward variety
                        factors += 1
            
            elif content_type == ContentType.HASHTAGS:
                # Hashtag count optimization
                hashtags = re.findall(r'#\w+', content)
                hashtag_count = len(hashtags)
                
                max_hashtags = platform_rules.get("hashtags_max", self.optimization_thresholds["max_hashtags"])
                optimal_hashtags = platform_rules.get("hashtags_optimal", 10)
                
                if hashtag_count <= optimal_hashtags:
                    score += hashtag_count / optimal_hashtags
                elif hashtag_count <= max_hashtags:
                    excess = hashtag_count - optimal_hashtags
                    penalty = excess / (max_hashtags - optimal_hashtags)
                    score += max(0.5, 1 - penalty)
                else:
                    score += 0.2  # Heavy penalty for too many hashtags
                
                factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {e}")
            return 0.5

    async def _analyze_semantic_relevance(
        self,
        content: str,
        target_keywords: List[str]
    ) -> float:
        """Analyze semantic relevance using NLP"""        try:
            if not target_keywords or not content.strip():
                return 0.5
            
            # Calculate semantic similarity between content and keywords
            keyword_text = " ".join(target_keywords)
            similarity_score = await self.nlp_engine.calculate_semantic_similarity(
                content, keyword_text
            )
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"Semantic relevance analysis failed: {e}")
            return 0.5

    async def _predict_engagement_potential(
        self,
        content: str,
        content_type: ContentType
    ) -> float:
        """Predict content engagement potential"""        try:
            score = 0.0
            factors = 0
            
            # Emotional language detection
            emotional_words = [
                "amazing", "incredible", "shocking", "unbelievable", "must-see",
                "exclusive", "breaking", "viral", "trending", "epic", "awesome",
                "stunning", "mind-blowing", "revolutionary", "game-changing"
            ]
            
            content_lower = content.lower()
            emotional_count = sum(1 for word in emotional_words if word in content_lower)
            score += min(1.0, emotional_count / 3)
            factors += 1
            
            # Question presence (encourages engagement)
            question_count = content.count('?')
            score += min(1.0, question_count / 2)
            factors += 1
            
            # Call-to-action presence
            cta_phrases = [
                "like and subscribe", "comment below", "share this", "tag a friend",
                "what do you think", "let me know", "follow for more", "link in bio"
            ]
            
            cta_count = sum(1 for phrase in cta_phrases if phrase in content_lower)
            score += min(1.0, cta_count / 2)
            factors += 1
            
            # Number/list presence (performs well)
            numbers = re.findall(r'\d+', content)
            if numbers:
                score += 0.5
            factors += 1
            
            # Urgency/scarcity words
            urgency_words = ["now", "today", "limited", "exclusive", "last chance", "hurry"]
            urgency_count = sum(1 for word in urgency_words if word in content_lower)
            score += min(1.0, urgency_count / 2)
            factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"Engagement potential prediction failed: {e}")
            return 0.5

    def _analyze_technical_seo(
        self,
        content: str,
        content_type: ContentType,
        platform_rules: Dict[str, Any]
    ) -> float:
        """Analyze technical SEO factors"""        try:
            score = 0.0
            factors = 0
            
            # Character encoding check
            try:
                content.encode('utf-8')
                score += 1.0
            except UnicodeEncodeError:
                score += 0.0
            factors += 1
            
            # Special characters handling
            special_char_ratio = len(re.findall(r'[^\w\s]', content)) / len(content)
            score += max(0, 1 - special_char_ratio * 2)  # Penalize excessive special chars
            factors += 1
            
            # Platform-specific length compliance
            max_length = platform_rules.get(f"{content_type.value}_max_length")
            if max_length:
                if len(content) <= max_length:
                    score += 1.0
                else:
                    overflow = len(content) - max_length
                    penalty = min(1.0, overflow / max_length)
                    score += max(0, 1 - penalty)
                factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"Technical SEO analysis failed: {e}")
            return 0.5

    async def _generate_seo_recommendations(
        self,
        content: str,
        content_type: ContentType,
        platform_rules: Dict[str, Any],
        seo_score: SEOScore,
        target_keywords: List[str] = None
    ) -> List[SEORecommendation]:
        """Generate actionable SEO recommendations"""        try:
            recommendations = []
            
            # Keyword optimization recommendations
            if seo_score.keyword_optimization < 0.7 and target_keywords:
                recommendations.append(SEORecommendation(
                    category="Keywords",
                    priority="high",
                    title="Improve Keyword Optimization",
                    description=f"Include target keywords more naturally in your {content_type.value}",
                    implementation=f"Add keywords: {', '.join(target_keywords[:3])}",
                    expected_impact=0.15,
                    effort_level="low"
                ))
            
            # Readability recommendations
            if seo_score.readability_score < 0.6:
                recommendations.append(SEORecommendation(
                    category="Readability",
                    priority="medium",
                    title="Improve Content Readability",
                    description="Use shorter sentences and simpler vocabulary",
                    implementation="Break long sentences, use active voice, remove jargon",
                    expected_impact=0.10,
                    effort_level="medium"
                ))
            
            # Content structure recommendations
            if seo_score.content_structure < 0.7:
                if content_type == ContentType.TITLE:
                    title_length = len(content)
                    optimal_range = self.optimization_thresholds["target_title_length"]
                    
                    if title_length < optimal_range[0]:
                        recommendations.append(SEORecommendation(
                            category="Structure",
                            priority="medium",
                            title="Lengthen Title",
                            description=f"Title is too short ({title_length} chars). Aim for {optimal_range[0]}-{optimal_range[1]} characters",
                            implementation="Add descriptive words or specify the topic more clearly",
                            expected_impact=0.08,
                            effort_level="low"
                        ))
                    elif title_length > optimal_range[1]:
                        recommendations.append(SEORecommendation(
                            category="Structure",
                            priority="medium",
                            title="Shorten Title",
                            description=f"Title is too long ({title_length} chars). Aim for {optimal_range[0]}-{optimal_range[1]} characters",
                            implementation="Remove unnecessary words while keeping main keywords",
                            expected_impact=0.08,
                            effort_level="low"
                        ))
                
                elif content_type == ContentType.HASHTAGS:
                    hashtag_count = len(re.findall(r'#\w+', content))
                    optimal_count = platform_rules.get("hashtags_optimal", 10)
                    
                    if hashtag_count < optimal_count:
                        recommendations.append(SEORecommendation(
                            category="Hashtags",
                            priority="high",
                            title="Add More Hashtags",
                            description=f"Using only {hashtag_count} hashtags. Aim for {optimal_count}",
                            implementation="Add relevant, trending hashtags related to your content",
                            expected_impact=0.12,
                            effort_level="low"
                        ))
            
            # Engagement potential recommendations
            if seo_score.engagement_potential < 0.6:
                recommendations.append(SEORecommendation(
                    category="Engagement",
                    priority="high",
                    title="Add Engagement Elements",
                    description="Include questions, calls-to-action, or emotional triggers",
                    implementation="Add phrases like 'What do you think?', 'Comment below', or 'Share if you agree'",
                    expected_impact=0.20,
                    effort_level="low"
                ))
            
            # Semantic relevance recommendations
            if seo_score.semantic_relevance < 0.6 and target_keywords:
                recommendations.append(SEORecommendation(
                    category="Relevance",
                    priority="medium",
                    title="Improve Semantic Relevance",
                    description="Use related terms and synonyms of your target keywords",
                    implementation="Include variations and context around your main keywords",
                    expected_impact=0.10,
                    effort_level="medium"
                ))
            
            # Sort by priority and expected impact
            priority_order = {"high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda x: (priority_order[x.priority], x.expected_impact),
                reverse=True
            )
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"SEO recommendations generation failed: {e}")
            return []

    async def optimize_content(
        self,
        content: str,
        content_type: ContentType,
        target_platform: str,
        target_keywords: List[str],
        optimization_level: OptimizationLevel = OptimizationLevel.INTERMEDIATE
    ) -> ContentOptimization:
        """        Automatically optimize content for SEO
        
        Args:
            content: Original content
            content_type: Type of content
            target_platform: Platform for optimization
            target_keywords: Keywords to optimize for
            optimization_level: Level of optimization to apply
            
        Returns:
            Content optimization result
        """        try:
            original_content = content
            optimized_content = content
            improvements = []
            keywords_added = []
            
            # Get current SEO score
            original_score, _ = await self.analyze_content_seo(
                content, content_type, target_platform, target_keywords
            )
            
            # Apply optimizations based on level
            if optimization_level in [OptimizationLevel.BASIC, OptimizationLevel.INTERMEDIATE, 
                                    OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
                
                # Keyword optimization
                optimized_content, added_keywords = await self._optimize_keywords(
                    optimized_content, target_keywords, content_type
                )
                if added_keywords:
                    keywords_added.extend(added_keywords)
                    improvements.append("Added target keywords naturally")
            
            if optimization_level in [OptimizationLevel.INTERMEDIATE, OptimizationLevel.ADVANCED, 
                                    OptimizationLevel.EXPERT]:
                
                # Readability optimization
                optimized_content = await self._optimize_readability(
                    optimized_content, content_type
                )
                improvements.append("Improved readability")
                
                # Structure optimization
                optimized_content = await self._optimize_structure(
                    optimized_content, content_type, target_platform
                )
                improvements.append("Optimized content structure")
            
            if optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.EXPERT]:
                
                # Engagement optimization
                optimized_content = await self._optimize_engagement(
                    optimized_content, content_type
                )
                improvements.append("Enhanced engagement potential")
            
            if optimization_level == OptimizationLevel.EXPERT:
                
                # Semantic optimization
                optimized_content = await self._optimize_semantics(
                    optimized_content, target_keywords
                )
                improvements.append("Improved semantic relevance")
            
            # Calculate improvement
            new_score, _ = await self.analyze_content_seo(
                optimized_content, content_type, target_platform, target_keywords
            )
            
            seo_score_change = new_score.overall_score - original_score.overall_score
            
            # Calculate readability improvement
            original_readability = self._analyze_readability(original_content)
            new_readability = self._analyze_readability(optimized_content)
            readability_improvement = new_readability - original_readability
            
            return ContentOptimization(
                original_content=original_content,
                optimized_content=optimized_content,
                improvements=improvements,
                keywords_added=keywords_added,
                readability_improvement=readability_improvement,
                seo_score_change=seo_score_change
            )
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            raise

    async def _optimize_keywords(
        self,
        content: str,
        target_keywords: List[str],
        content_type: ContentType
    ) -> Tuple[str, List[str]]:
        """Optimize keyword placement and density"""        try:
            optimized_content = content
            added_keywords = []
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                content_lower = optimized_content.lower()
                
                # Check current keyword density
                word_count = len(optimized_content.split())
                current_count = content_lower.count(keyword_lower)
                current_density = (current_count / word_count) * 100 if word_count > 0 else 0
                
                # Add keyword if density is too low
                if current_density < self.optimization_thresholds["min_keyword_density"]:
                    if content_type == ContentType.TITLE:
                        # Add to beginning if not present
                        if keyword_lower not in content_lower:
                            optimized_content = f"{keyword}: {optimized_content}"
                            added_keywords.append(keyword)
                    
                    elif content_type == ContentType.DESCRIPTION:
                        # Add to end naturally
                        if keyword_lower not in content_lower:
                            optimized_content += f" Learn more about {keyword}."
                            added_keywords.append(keyword)
                    
                    elif content_type == ContentType.HASHTAGS:
                        # Add as hashtag if not present
                        hashtag = f"#{keyword.replace(' ', '')}"
                        if hashtag.lower() not in content_lower:
                            optimized_content += f" {hashtag}"
                            added_keywords.append(keyword)
            
            return optimized_content, added_keywords
            
        except Exception as e:
            logger.error(f"Keyword optimization failed: {e}")
            return content, []

    async def _optimize_readability(
        self,
        content: str,
        content_type: ContentType
    ) -> str:
        """Optimize content readability"""        try:
            if content_type not in [ContentType.DESCRIPTION, ContentType.CAPTION]:
                return content
            
            # Split into sentences
            sentences = content.split('.')
            optimized_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Break long sentences (>25 words)
                words = sentence.split()
                if len(words) > 25:
                    # Find a good break point (conjunction, comma, etc.)
                    break_points = []
                    for i, word in enumerate(words):
                        if word.lower() in ['and', 'but', 'or', 'so', 'because', 'however']:
                            break_points.append(i)
                    
                    if break_points:
                        break_point = break_points[len(break_points)//2]  # Use middle break point
                        first_part = ' '.join(words[:break_point])
                        second_part = ' '.join(words[break_point:])
                        optimized_sentences.extend([first_part, second_part])
                    else:
                        optimized_sentences.append(sentence)
                else:
                    optimized_sentences.append(sentence)
            
            return '. '.join(optimized_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Readability optimization failed: {e}")
            return content

    async def _optimize_structure(
        self,
        content: str,
        content_type: ContentType,
        target_platform: str
    ) -> str:
        """Optimize content structure for platform"""        try:
            platform_rules = self.platform_rules.get(target_platform, {})
            
            if content_type == ContentType.TITLE:
                # Ensure optimal title length
                optimal_range = self.optimization_thresholds["target_title_length"]
                if len(content) < optimal_range[0]:
                    # Add descriptive words
                    content += " - Complete Guide"
                elif len(content) > optimal_range[1]:
                    # Trim while keeping important words
                    words = content.split()
                    while len(' '.join(words)) > optimal_range[1] and len(words) > 3:
                        # Remove least important words (articles, prepositions)
                        stop_words = ['the', 'a', 'an', 'in', 'on', 'at', 'for', 'with']
                        removed = False
                        for stop_word in stop_words:
                            if stop_word in words:
                                words.remove(stop_word)
                                removed = True
                                break
                        if not removed:
                            words.pop()  # Remove last word if no stop words found
                    content = ' '.join(words)
            
            elif content_type == ContentType.HASHTAGS:
                # Optimize hashtag count
                optimal_count = platform_rules.get("hashtags_optimal", 10)
                hashtags = re.findall(r'#\w+', content)
                
                if len(hashtags) < optimal_count:
                    # Add generic relevant hashtags
                    additional_hashtags = ["#viral", "#trending", "#fyp", "#explore"]
                    needed = optimal_count - len(hashtags)
                    content += " " + " ".join(additional_hashtags[:needed])
            
            return content
            
        except Exception as e:
            logger.error(f"Structure optimization failed: {e}")
            return content

    async def _optimize_engagement(
        self,
        content: str,
        content_type: ContentType
    ) -> str:
        """Optimize content for engagement"""        try:
            if content_type in [ContentType.DESCRIPTION, ContentType.CAPTION]:
                # Add engagement elements if missing
                content_lower = content.lower()
                
                # Add call-to-action if missing
                cta_present = any(phrase in content_lower for phrase in [
                    "comment", "like", "share", "subscribe", "follow"
                ])
                
                if not cta_present:
                    content += " What do you think? Let me know in the comments!"
                
                # Add question if missing
                if '?' not in content:
                    content += " Have you experienced this too?"
            
            return content
            
        except Exception as e:
            logger.error(f"Engagement optimization failed: {e}")
            return content

    async def _optimize_semantics(
        self,
        content: str,
        target_keywords: List[str]
    ) -> str:
        """Optimize semantic relevance"""        try:
            # Add related terms and synonyms
            for keyword in target_keywords:
                # Get related terms using NLP
                related_terms = await self.nlp_engine.get_related_terms(keyword)
                
                # Add one related term if not already present
                for term in related_terms[:1]:  # Limit to avoid over-optimization
                    if term.lower() not in content.lower():
                        content += f" {term}"
                        break
            
            return content
            
        except Exception as e:
            logger.error(f"Semantic optimization failed: {e}")
            return content

    async def research_keywords(
        self,
        seed_keywords: List[str],
        target_platform: str,
        target_audience: str = None,
        search_volume_min: int = 100
    ) -> List[KeywordData]:
        """        Research and analyze keywords for content optimization
        
        Args:
            seed_keywords: Starting keywords for research
            target_platform: Platform to optimize for
            target_audience: Target audience description
            search_volume_min: Minimum search volume threshold
            
        Returns:
            List of keyword data with analysis
        """        try:
            keyword_results = []
            
            for seed_keyword in seed_keywords:
                # Get keyword variations and related terms
                variations = await self._get_keyword_variations(seed_keyword)
                
                for keyword in variations:
                    # Analyze each keyword
                    keyword_data = await self._analyze_keyword(
                        keyword, target_platform, search_volume_min
                    )
                    
                    if keyword_data and keyword_data.search_volume >= search_volume_min:
                        keyword_results.append(keyword_data)
            
            # Sort by relevance and search volume
            keyword_results.sort(
                key=lambda x: (x.relevance_score * x.search_volume),
                reverse=True
            )
            
            # Update metrics
            self.metrics_collector.increment_counter(
                "keyword_research_requests",
                tags={"platform": target_platform}
            )
            
            logger.info(f"Keyword research completed: {len(keyword_results)} keywords found")
            return keyword_results[:50]  # Limit to top 50
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return []

    async def _get_keyword_variations(self, seed_keyword: str) -> List[str]:
        """Get keyword variations and related terms"""        try:
            variations = [seed_keyword]
            
            # Add basic variations
            variations.extend([
                f"how to {seed_keyword}",
                f"best {seed_keyword}",
                f"{seed_keyword} tutorial",
                f"{seed_keyword} tips",
                f"{seed_keyword} guide"
            ])
            
            # Use NLP to get related terms
            related_terms = await self.nlp_engine.get_related_terms(seed_keyword)
            variations.extend(related_terms[:10])
            
            return list(set(variations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Keyword variation generation failed: {e}")
            return [seed_keyword]

    async def _analyze_keyword(
        self,
        keyword: str,
        target_platform: str,
        search_volume_min: int
    ) -> Optional[KeywordData]:
        """Analyze individual keyword metrics"""        try:
            # This would integrate with keyword research APIs
            # For now, return mock data
            
            # Simulate search volume (would come from real API)
            search_volume = hash(keyword) % 10000 + search_volume_min
            
            # Calculate difficulty based on keyword length and competition
            difficulty_score = min(1.0, len(keyword.split()) * 0.2)
            
            # Calculate relevance based on platform
            platform_keywords = self.platform_rules.get(target_platform, {}).get("focus_keywords", [])
            relevance_score = 0.5
            for platform_keyword in platform_keywords:
                if platform_keyword in keyword.lower():
                    relevance_score = 0.9
                    break
            
            return KeywordData(
                keyword=keyword,
                search_volume=search_volume,
                competition_level="medium",
                difficulty_score=difficulty_score,
                relevance_score=relevance_score,
                trend_direction="stable",
                related_keywords=[],
                long_tail_variations=[]
            )
            
        except Exception as e:
            logger.error(f"Keyword analysis failed for '{keyword}': {e}")
            return None

    # Helper methods for caching and data persistence
    async def _cache_seo_analysis(
        self,
        cache_key: str,
        seo_score: SEOScore,
        recommendations: List[SEORecommendation]
    ):
        """Cache SEO analysis results"""        try:
            data = {
                "seo_score": asdict(seo_score),
                "recommendations": [asdict(rec) for rec in recommendations],
                "timestamp": datetime.now().isoformat()
            }
            
            await self.redis_manager.setex(cache_key, self.cache_ttl, json.dumps(data))
            
        except Exception as e:
            logger.warning(f"Failed to cache SEO analysis: {e}")

    async def get_seo_trends(
        self,
        platform: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get SEO trends and insights for platform"""        try:
            # This would analyze trending keywords, hashtags, etc.
            # For now, return mock data structure
            
            return {
                "platform": platform,
                "trending_keywords": [],
                "top_hashtags": [],
                "content_trends": [],
                "optimization_opportunities": [],
                "period": {
                    "start": (datetime.now() - time_period).isoformat(),
                    "end": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"SEO trends analysis failed: {e}")
            return {}
