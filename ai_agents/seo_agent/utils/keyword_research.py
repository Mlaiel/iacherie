"""
Keyword Research Module - Advanced Keyword Analysis and Research

Comprehensive keyword research system with AI-powered analysis, trend detection,
and competitor intelligence for optimal SEO strategy development.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation

try:
    from core.exceptions import SEOError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SEOError, ValidationError = globals().get('SEOError, ValidationError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.text_analysis import TextAnalyzer
from ...integrations.search_apis import SearchAPIManager
from ...integrations.social_apis import SocialMediaAPIManager
from ...ml.keyword_models import KeywordSimilarityModel, TrendPredictionModel

logger = logging.getLogger(__name__)

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class KeywordIntent(Enum):
    """Search intent types"""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    LOCAL = "local"

class TrendDirection(Enum):
    """Trend direction"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"

@dataclass
class KeywordMetrics:
    """Comprehensive keyword metrics"""
    keyword: str
    search_volume: int
    competition: float
    cpc: float
    difficulty: KeywordDifficulty
    intent: KeywordIntent
    relevance_score: float
    trending_score: float
    seasonal_score: float
    commercial_value: float
    related_keywords: List[str] = field(default_factory=list)
    long_tail_variants: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendData:
    """Keyword trend analysis data"""
    keyword: str
    trend_direction: TrendDirection
    growth_rate: float
    seasonality_score: float
    trend_confidence: float
    historical_data: List[Dict[str, Any]] = field(default_factory=list)
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    related_trends: List[str] = field(default_factory=list)

@dataclass
class CompetitorKeywords:
    """Competitor keyword analysis"""
    competitor_url: str
    domain_authority: float
    top_keywords: List[KeywordMetrics]
    keyword_gaps: List[str]
    content_gaps: List[Dict[str, Any]]
    ranking_opportunities: List[Dict[str, Any]]
    estimated_traffic: int
    competitive_advantage: float

class KeywordAnalyzer:
    """
    Advanced keyword analysis and research engine.
    
    Features:
    - Multi-source keyword research
    - AI-powered semantic analysis
    - Competition and difficulty assessment
    - Long-tail keyword discovery
    - Intent classification
    - Commercial value estimation
    - Keyword clustering and grouping
    - Localization and multilingual support
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Core components
        self.text_analyzer = TextAnalyzer()
        self.search_apis = SearchAPIManager()
        self.social_apis = SocialMediaAPIManager()
        
        # AI models
        self.similarity_model = None
        self.trend_model = None
        
        # Analysis tools
        self.tfidf_vectorizer = TfidfVectorizer(max_features=10000)
        self.keyword_clusters = {}
        
        # Data caches
        self.keyword_cache: Dict[str, KeywordMetrics] = {}
        self.search_volume_cache: Dict[str, int] = {}
        self.competition_cache: Dict[str, float] = {}
        
        # Configuration
        self.supported_languages = ['en', 'de', 'fr', 'es', 'it', 'pt']
        self.max_related_keywords = 50
        self.min_search_volume = 10
        self.cache_ttl = timedelta(hours=24)
        
    async def initialize(self):
        """Initialize keyword analyzer components"""



        try:
            # Initialize AI models
            self.similarity_model = KeywordSimilarityModel()
            await self.similarity_model.load_model()
            
            self.trend_model = TrendPredictionModel()
            await self.trend_model.load_model()
            
            # Initialize text analyzer
            await self.text_analyzer.initialize()
            
            # Initialize API managers
            await self.search_apis.initialize()
            await self.social_apis.initialize()
            
            logger.info("Keyword Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Keyword Analyzer: {e}")
            raise SEOError(f"Keyword Analyzer initialization failed: {e}")
    
    async def research_keywords(
        self,
        seed_keywords: List[str],
        topic: Optional[str] = None,
        language: str = 'en',
        location: str = 'US',
        include_long_tail: bool = True,
        include_questions: bool = True,
        max_results: int = 100
    ) -> List[KeywordMetrics]:
        """
        Comprehensive keyword research from multiple sources.
        
        Args:
            seed_keywords: Initial keywords to expand from
            topic: Topic/industry context
            language: Target language for keywords
            location: Geographic location for research
            include_long_tail: Include long-tail variations
            include_questions: Include question-based keywords
            max_results: Maximum number of keywords to return
        
        Returns:
            List of keyword metrics
        """



        try:
            if not seed_keywords and not topic:
                raise ValidationError("Either seed keywords or topic is required")
            
            all_keywords = set(seed_keywords)
            keyword_metrics = []
            
            # Generate topic-based keywords if topic provided
            if topic:
                topic_keywords = await self._generate_topic_keywords(topic, language)
                all_keywords.update(topic_keywords)
            
            # Expand seed keywords
            for seed_keyword in seed_keywords:
                expanded_keywords = await self._expand_keyword(
                    seed_keyword, language, location
                )
                all_keywords.update(expanded_keywords)
            
            # Generate long-tail variations
            if include_long_tail:
                long_tail_keywords = await self._generate_long_tail_keywords(
                    list(all_keywords), language
                )
                all_keywords.update(long_tail_keywords)
            
            # Generate question keywords
            if include_questions:
                question_keywords = await self._generate_question_keywords(
                    list(all_keywords), language
                )
                all_keywords.update(question_keywords)
            
            # Analyze each keyword
            for keyword in list(all_keywords)[:max_results * 2]:  # Analyze more than needed
                try:
                    metrics = await self._analyze_single_keyword(
                        keyword, language, location
                    )
                    if metrics and metrics.search_volume >= self.min_search_volume:
                        keyword_metrics.append(metrics)
                except Exception as e:
                    logger.warning(f"Error analyzing keyword '{keyword}': {e}")
            
            # Sort by relevance and commercial value
            keyword_metrics.sort(
                key=lambda k: (k.relevance_score * k.commercial_value),
                reverse=True
            )
            
            return keyword_metrics[:max_results]
            
        except Exception as e:
            logger.error(f"Keyword research error: {e}")
            raise SEOError(f"Keyword research failed: {e}")
    
    async def analyze_keyword_clusters(
        self,
        keywords: List[str],
        num_clusters: int = 10
    ) -> Dict[str, List[str]]:
        """
        Cluster keywords by semantic similarity and search intent.
        
        Args:
            keywords: List of keywords to cluster
            num_clusters: Number of clusters to create
        
        Returns:
            Dictionary mapping cluster names to keyword lists
        """



        try:
            if len(keywords) < num_clusters:
                num_clusters = len(keywords)
            
            # Get semantic embeddings for keywords
            embeddings = []
            valid_keywords = []
            
            for keyword in keywords:
                try:
                    embedding = await self.similarity_model.get_embedding(keyword)
                    embeddings.append(embedding)
                    valid_keywords.append(keyword)
                except Exception as e:
                    logger.warning(f"Error getting embedding for '{keyword}': {e}")
            
            if not embeddings:
                raise SEOError("No valid keyword embeddings found")
            
            # Perform clustering
            embeddings_array = np.array(embeddings)
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings_array)
            
            # Group keywords by cluster
            clusters = defaultdict(list)
            for keyword, label in zip(valid_keywords, cluster_labels):
                clusters[f"cluster_{label}"].append(keyword)
            
            # Generate meaningful cluster names
            named_clusters = {}
            for cluster_id, cluster_keywords in clusters.items():
                cluster_name = await self._generate_cluster_name(cluster_keywords)
                named_clusters[cluster_name] = cluster_keywords
            
            # Store clusters for future reference
            self.keyword_clusters.update(named_clusters)
            
            return named_clusters
            
        except Exception as e:
            logger.error(f"Keyword clustering error: {e}")
            raise SEOError(f"Keyword clustering failed: {e}")
    
    async def analyze_keyword_difficulty(
        self,
        keywords: List[str],
        language: str = 'en'
    ) -> Dict[str, KeywordDifficulty]:
        """
        Analyze keyword ranking difficulty using multiple factors.
        
        Args:
            keywords: List of keywords to analyze
            language: Language for analysis
        
        Returns:
            Dictionary mapping keywords to difficulty levels
        """



        try:
            difficulty_scores = {}
            
            for keyword in keywords:
                # Get search results analysis
                serp_analysis = await self._analyze_serp_competition(keyword, language)
                
                # Calculate difficulty factors
                factors = {
                    'search_volume': await self._get_search_volume(keyword, language),
                    'competition_score': serp_analysis['competition_score'],
                    'domain_strength': serp_analysis['avg_domain_authority'],
                    'content_quality': serp_analysis['avg_content_quality'],
                    'backlink_difficulty': serp_analysis['avg_backlinks'],
                    'page_authority': serp_analysis['avg_page_authority']
                }
                
                # Calculate overall difficulty
                difficulty_score = await self._calculate_difficulty_score(factors)
                difficulty_level = self._score_to_difficulty_level(difficulty_score)
                
                difficulty_scores[keyword] = difficulty_level
            
            return difficulty_scores
            
        except Exception as e:
            logger.error(f"Keyword difficulty analysis error: {e}")
            raise SEOError(f"Keyword difficulty analysis failed: {e}")
    
    async def identify_keyword_opportunities(
        self,
        current_keywords: List[str],
        competitor_keywords: List[str],
        industry: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Identify keyword opportunities by analyzing gaps and trends.
        
        Args:
            current_keywords: Currently targeted keywords
            competitor_keywords: Competitor keywords
            industry: Industry context
            language: Target language
        
        Returns:
            Keyword opportunities analysis
        """



        try:
            opportunities = {
                'keyword_gaps': [],
                'trending_keywords': [],
                'low_competition_keywords': [],
                'high_value_keywords': [],
                'long_tail_opportunities': [],
                'seasonal_opportunities': []
            }
            
            # Find keyword gaps
            current_set = set(current_keywords)
            competitor_set = set(competitor_keywords)
            keyword_gaps = list(competitor_set - current_set)
            
            # Analyze each gap keyword
            for gap_keyword in keyword_gaps:
                metrics = await self._analyze_single_keyword(gap_keyword, language)
                if metrics:
                    if metrics.difficulty in [KeywordDifficulty.VERY_EASY, KeywordDifficulty.EASY]:
                        opportunities['keyword_gaps'].append({
                            'keyword': gap_keyword,
                            'metrics': metrics,
                            'opportunity_score': metrics.relevance_score * metrics.commercial_value
                        })
            
            # Find trending keywords in industry
            trending_keywords = await self._find_trending_keywords(industry, language)
            for trend_keyword in trending_keywords:
                if trend_keyword not in current_set:
                    opportunities['trending_keywords'].append({
                        'keyword': trend_keyword,
                        'trend_score': await self._get_trend_score(trend_keyword),
                        'growth_potential': await self._estimate_growth_potential(trend_keyword)
                    })
            
            # Find low competition opportunities
            industry_keywords = await self._generate_industry_keywords(industry, language)
            for keyword in industry_keywords:
                if keyword not in current_set:
                    difficulty = await self.analyze_keyword_difficulty([keyword], language)
                    if difficulty.get(keyword) in [KeywordDifficulty.VERY_EASY, KeywordDifficulty.EASY]:
                        opportunities['low_competition_keywords'].append({
                            'keyword': keyword,
                            'difficulty': difficulty[keyword],
                            'estimated_traffic': await self._estimate_traffic_potential(keyword)
                        })
            
            # Identify high commercial value keywords
            for keyword in industry_keywords:
                if keyword not in current_set:
                    commercial_value = await self._calculate_commercial_value(keyword)
                    if commercial_value > 0.7:  # High commercial value threshold
                        opportunities['high_value_keywords'].append({
                            'keyword': keyword,
                            'commercial_value': commercial_value,
                            'estimated_revenue': await self._estimate_revenue_potential(keyword)
                        })
            
            # Generate long-tail opportunities
            long_tail_keywords = await self._generate_long_tail_opportunities(
                current_keywords, industry, language
            )
            opportunities['long_tail_opportunities'] = long_tail_keywords
            
            # Identify seasonal opportunities
            seasonal_keywords = await self._identify_seasonal_keywords(industry, language)
            opportunities['seasonal_opportunities'] = seasonal_keywords
            
            # Rank all opportunities
            ranked_opportunities = await self._rank_opportunities(opportunities)
            
            return {
                'opportunities': opportunities,
                'ranked_opportunities': ranked_opportunities,
                'total_opportunities': sum(len(opp_list) for opp_list in opportunities.values()),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Keyword opportunity identification error: {e}")
            raise SEOError(f"Keyword opportunity identification failed: {e}")
    
    async def _analyze_single_keyword(
        self,
        keyword: str,
        language: str,
        location: str = 'US'
    ) -> Optional[KeywordMetrics]:
        """Analyze a single keyword comprehensively"""



        try:
            # Check cache first
            cache_key = f"{keyword}_{language}_{location}"
            if cache_key in self.keyword_cache:
                cached_result = self.keyword_cache[cache_key]
                if datetime.utcnow() - cached_result.last_updated < self.cache_ttl:
                    return cached_result
            
            # Get search volume and competition
            search_volume = await self._get_search_volume(keyword, language, location)
            competition = await self._get_competition_score(keyword, language, location)
            cpc = await self._get_cpc_estimate(keyword, language, location)
            
            # Classify intent
            intent = await self._classify_search_intent(keyword)
            
            # Calculate difficulty
            difficulty_factors = await self._get_difficulty_factors(keyword, language)
            difficulty = self._calculate_keyword_difficulty(difficulty_factors)
            
            # Calculate relevance and trending scores
            relevance_score = await self._calculate_relevance_score(keyword)
            trending_score = await self._calculate_trending_score(keyword, language)
            seasonal_score = await self._calculate_seasonal_score(keyword)
            commercial_value = await self._calculate_commercial_value(keyword)
            
            # Find related keywords
            related_keywords = await self._find_related_keywords(keyword, language)
            long_tail_variants = await self._generate_long_tail_variants(keyword, language)
            questions = await self._generate_question_variations(keyword, language)
            topics = await self._extract_topics(keyword)
            
            # Create keyword metrics object
            metrics = KeywordMetrics(
                keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                cpc=cpc,
                difficulty=difficulty,
                intent=intent,
                relevance_score=relevance_score,
                trending_score=trending_score,
                seasonal_score=seasonal_score,
                commercial_value=commercial_value,
                related_keywords=related_keywords,
                long_tail_variants=long_tail_variants,
                questions=questions,
                topics=topics
            )
            
            # Cache the result
            self.keyword_cache[cache_key] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Single keyword analysis error for '{keyword}': {e}")
            return None
    
    async def _expand_keyword(
        self,
        seed_keyword: str,
        language: str,
        location: str
    ) -> List[str]:
        """Expand a seed keyword into related keywords"""



        try:
            expanded_keywords = set()
            
            # Use search API suggestions
            suggestions = await self.search_apis.get_keyword_suggestions(
                seed_keyword, language, location
            )
            expanded_keywords.update(suggestions)
            
            # Use semantic similarity
            similar_keywords = await self.similarity_model.find_similar_keywords(
                seed_keyword, top_k=20
            )
            expanded_keywords.update(similar_keywords)
            
            # Generate variations
            variations = self._generate_keyword_variations(seed_keyword)
            expanded_keywords.update(variations)
            
            return list(expanded_keywords)
            
        except Exception as e:
            logger.error(f"Keyword expansion error for '{seed_keyword}': {e}")
            return []
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate variations of a keyword"""
        variations = []
        
        # Plurals/singulars
        if keyword.endswith('s'):
            variations.append(keyword[:-1])
        else:
            variations.append(keyword + 's')
        
        # Common prefixes/suffixes
        prefixes = ['best', 'top', 'how to', 'what is', 'guide to']
        suffixes = ['guide', 'tips', 'tutorial', 'review', 'comparison']
        
        for prefix in prefixes:
            variations.append(f"{prefix} {keyword}")
        
        for suffix in suffixes:
            variations.append(f"{keyword} {suffix}")
        
        return variations


class TrendAnalyzer:
    """
    Advanced trend analysis for keywords and search patterns.
    
    Features:
    - Real-time trend detection
    - Seasonal pattern analysis
    - Predictive trend modeling
    - Social media trend correlation
    - Industry-specific trend tracking
    - Geographic trend variations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Components
        self.search_apis = SearchAPIManager()
        self.social_apis = SocialMediaAPIManager()
        
        # AI models
        self.trend_prediction_model = None
        
        # Data storage
        self.trend_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.seasonal_patterns: Dict[str, Dict[str, float]] = {}
        
        # Configuration
        self.trend_window = timedelta(days=30)
        self.prediction_horizon = timedelta(days=90)
        
    async def initialize(self):
        """Initialize trend analyzer"""



        try:
            # Initialize prediction model
            self.trend_prediction_model = TrendPredictionModel()
            await self.trend_prediction_model.load_model()
            
            # Initialize API managers
            await self.search_apis.initialize()
            await self.social_apis.initialize()
            
            logger.info("Trend Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Trend Analyzer: {e}")
            raise SEOError(f"Trend Analyzer initialization failed: {e}")
    
    async def analyze_keyword_trends(
        self,
        keywords: List[str],
        time_range: Optional[Dict[str, datetime]] = None,
        language: str = 'en',
        location: str = 'US'
    ) -> Dict[str, TrendData]:
        """
        Analyze trends for a list of keywords.
        
        Args:
            keywords: Keywords to analyze
            time_range: Time range for analysis
            language: Language for analysis
            location: Geographic location
        
        Returns:
            Dictionary mapping keywords to trend data
        """



        try:
            if not time_range:
                time_range = {
                    'start': datetime.utcnow() - self.trend_window,
                    'end': datetime.utcnow()
                }
            
            trend_results = {}
            
            for keyword in keywords:
                # Get historical trend data
                historical_data = await self._get_historical_trend_data(
                    keyword, time_range, language, location
                )
                
                # Analyze trend direction and growth
                trend_direction, growth_rate = self._analyze_trend_direction(historical_data)
                
                # Calculate seasonality
                seasonality_score = await self._calculate_seasonality(keyword, historical_data)
                
                # Get trend confidence
                trend_confidence = self._calculate_trend_confidence(historical_data)
                
                # Generate predictions
                predictions = await self._predict_future_trends(keyword, historical_data)
                
                # Find related trending topics
                related_trends = await self._find_related_trends(keyword, language)
                
                trend_data = TrendData(
                    keyword=keyword,
                    trend_direction=trend_direction,
                    growth_rate=growth_rate,
                    seasonality_score=seasonality_score,
                    trend_confidence=trend_confidence,
                    historical_data=historical_data,
                    predictions=predictions,
                    related_trends=related_trends
                )
                
                trend_results[keyword] = trend_data
                
                # Store for future reference
                self.trend_data[keyword].append({
                    'timestamp': datetime.utcnow(),
                    'trend_data': trend_data.__dict__
                })
            
            return trend_results
            
        except Exception as e:
            logger.error(f"Keyword trends analysis error: {e}")
            raise SEOError(f"Keyword trends analysis failed: {e}")
    
    async def detect_emerging_trends(
        self,
        industry: str,
        language: str = 'en',
        min_growth_rate: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect emerging trends in an industry.
        
        Args:
            industry: Industry or topic area
            language: Language for analysis
            min_growth_rate: Minimum growth rate to consider trending
        
        Returns:
            List of emerging trends with data
        """



        try:
            emerging_trends = []
            
            # Get industry-related keywords
            industry_keywords = await self._get_industry_keywords(industry, language)
            
            # Analyze each keyword for trend signals
            for keyword in industry_keywords:
                # Get recent trend data
                recent_data = await self._get_recent_trend_data(keyword, language)
                
                # Calculate growth metrics
                growth_rate = self._calculate_growth_rate(recent_data)
                acceleration = self._calculate_trend_acceleration(recent_data)
                
                # Check if trending
                if growth_rate >= min_growth_rate:
                    # Get additional context
                    social_signals = await self._get_social_trend_signals(keyword)
                    news_mentions = await self._get_news_mentions(keyword)
                    
                    emerging_trends.append({
                        'keyword': keyword,
                        'growth_rate': growth_rate,
                        'acceleration': acceleration,
                        'confidence_score': self._calculate_trend_confidence(recent_data),
                        'social_signals': social_signals,
                        'news_mentions': news_mentions,
                        'trend_strength': growth_rate * acceleration,
                        'detected_at': datetime.utcnow().isoformat()
                    })
            
            # Sort by trend strength
            emerging_trends.sort(key=lambda x: x['trend_strength'], reverse=True)
            
            return emerging_trends[:20]  # Return top 20 trends
            
        except Exception as e:
            logger.error(f"Emerging trends detection error: {e}")
            raise SEOError(f"Emerging trends detection failed: {e}")
    
    async def analyze_seasonal_patterns(
        self,
        keywords: List[str],
        years_of_data: int = 2
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze seasonal patterns for keywords.
        
        Args:
            keywords: Keywords to analyze
            years_of_data: Number of years of historical data to analyze
        
        Returns:
            Dictionary mapping keywords to seasonal patterns
        """



        try:
            seasonal_patterns = {}
            
            for keyword in keywords:
                # Get multi-year historical data
                historical_data = await self._get_multi_year_data(keyword, years_of_data)
                
                # Extract seasonal patterns
                monthly_patterns = self._extract_monthly_patterns(historical_data)
                quarterly_patterns = self._extract_quarterly_patterns(historical_data)
                
                # Calculate seasonal indices
                seasonal_indices = self._calculate_seasonal_indices(monthly_patterns)
                
                # Identify peak seasons
                peak_seasons = self._identify_peak_seasons(seasonal_indices)
                
                seasonal_patterns[keyword] = {
                    'monthly_patterns': monthly_patterns,
                    'quarterly_patterns': quarterly_patterns,
                    'seasonal_indices': seasonal_indices,
                    'peak_seasons': peak_seasons,
                    'seasonality_strength': max(seasonal_indices) - min(seasonal_indices)
                }
                
                # Store patterns for future reference
                self.seasonal_patterns[keyword] = seasonal_patterns[keyword]
            
            return seasonal_patterns
            
        except Exception as e:
            logger.error(f"Seasonal patterns analysis error: {e}")
            raise SEOError(f"Seasonal patterns analysis failed: {e}")
    
    def _analyze_trend_direction(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Tuple[TrendDirection, float]:
        """Analyze trend direction and calculate growth rate"""
        if len(historical_data) < 2:
            return TrendDirection.STABLE, 0.0
        
        # Calculate linear regression
        values = [point['value'] for point in historical_data]
        x = np.arange(len(values))
        
        # Calculate slope
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate growth rate
        start_value = values[0] if values[0] > 0 else 1
        end_value = values[-1] if values[-1] > 0 else 1
        growth_rate = (end_value - start_value) / start_value
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend_direction = TrendDirection.STABLE
        elif slope > 0:
            trend_direction = TrendDirection.RISING
        else:
            trend_direction = TrendDirection.DECLINING
        
        # Check for seasonality
        if self._has_seasonal_pattern(values):
            trend_direction = TrendDirection.SEASONAL
        
        return trend_direction, growth_rate


class CompetitorAnalyzer:
    """
    Advanced competitor analysis for SEO intelligence.
    
    Features:
    - Comprehensive competitor keyword analysis
    - Content gap identification
    - Backlink profile analysis
    - Ranking position tracking
    - Competitive advantage assessment
    - Market share analysis
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Components
        self.search_apis = SearchAPIManager()
        self.keyword_analyzer = KeywordAnalyzer()
        
        # Data storage
        self.competitor_data: Dict[str, CompetitorKeywords] = {}
        self.market_intelligence: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize competitor analyzer"""



        try:
            await self.search_apis.initialize()
            await self.keyword_analyzer.initialize()
            
            logger.info("Competitor Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Competitor Analyzer: {e}")
            raise SEOError(f"Competitor Analyzer initialization failed: {e}")
    
    async def analyze_competitors(
        self,
        competitor_urls: List[str],
        target_keywords: List[str],
        language: str = 'en'
    ) -> Dict[str, CompetitorKeywords]:
        """
        Comprehensive competitor analysis.
        
        Args:
            competitor_urls: URLs of competitors to analyze
            target_keywords: Keywords to analyze competitors for
            language: Language for analysis
        
        Returns:
            Dictionary mapping competitor URLs to analysis data
        """



        try:
            competitor_analysis = {}
            
            for competitor_url in competitor_urls:
                # Analyze competitor's keyword profile
                competitor_keywords = await self._analyze_competitor_keywords(
                    competitor_url, target_keywords, language
                )
                
                # Get domain authority
                domain_authority = await self._get_domain_authority(competitor_url)
                
                # Identify keyword gaps
                keyword_gaps = await self._identify_competitor_keyword_gaps(
                    competitor_keywords, target_keywords
                )
                
                # Analyze content gaps
                content_gaps = await self._analyze_content_gaps(
                    competitor_url, target_keywords
                )
                
                # Identify ranking opportunities
                ranking_opportunities = await self._identify_ranking_opportunities(
                    competitor_url, competitor_keywords, target_keywords
                )
                
                # Estimate traffic
                estimated_traffic = await self._estimate_competitor_traffic(
                    competitor_url, competitor_keywords
                )
                
                # Calculate competitive advantage
                competitive_advantage = await self._calculate_competitive_advantage(
                    competitor_keywords, target_keywords
                )
                
                competitor_data = CompetitorKeywords(
                    competitor_url=competitor_url,
                    domain_authority=domain_authority,
                    top_keywords=competitor_keywords,
                    keyword_gaps=keyword_gaps,
                    content_gaps=content_gaps,
                    ranking_opportunities=ranking_opportunities,
                    estimated_traffic=estimated_traffic,
                    competitive_advantage=competitive_advantage
                )
                
                competitor_analysis[competitor_url] = competitor_data
                self.competitor_data[competitor_url] = competitor_data
            
            return competitor_analysis
            
        except Exception as e:
            logger.error(f"Competitor analysis error: {e}")
            raise SEOError(f"Competitor analysis failed: {e}")
