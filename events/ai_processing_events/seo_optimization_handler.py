"""SEO Optimization Event Handler

Enterprise-grade SEO optimization event processing for content visibility,
ranking improvement, and multi-platform discoverability in the IA Influencer Agent platform.

This module processes SEO optimization events following the business logic:
Content Protection → SEO Analysis → Keyword Optimization → Meta Enhancement → 
Platform Adaptation → Collaboration Matching → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
      Microservices + Audio + DevOps + IA Prompt Engineer

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.

Copyright © 2025 Fahed Mlaiel. All rights reserved.
"""import logging
import asyncio
import re
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import uuid
from enum import Enum
import numpy as np
from collections import Counter, defaultdict

# AI and ML imports for SEO analysis
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline, AutoTokenizer, AutoModel
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade

# Web scraping and analysis
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority
from ..core.event_status import EventStatus
from ...ai.seo.keyword_analyzer import KeywordAnalyzer
from ...ai.seo.content_optimizer import ContentOptimizer
from ...ai.seo.competitor_analyzer import CompetitorAnalyzer

logger = logging.getLogger(__name__)

class SEOOptimizationType(Enum):
    """SEO optimization types for different content formats"""    KEYWORD_OPTIMIZATION = "keyword_optimization"
    META_ENHANCEMENT = "meta_enhancement"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_OPTIMIZATION = "description_optimization"
    TAG_OPTIMIZATION = "tag_optimization"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TREND_ANALYSIS = "trend_analysis"
    PLATFORM_ADAPTATION = "platform_adaptation"

class PlatformType(Enum):
    """Target platforms for SEO optimization"""    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    GOOGLE_SEARCH = "google_search"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"

@dataclass
class SEOMetrics:
    """SEO performance and optimization metrics"""    keyword_density: Dict[str, float]
    readability_score: float
    sentiment_score: float
    trend_alignment: float
    competitor_gap_score: float
    platform_optimization_score: Dict[str, float]
    seo_potential_score: float
    processing_time: float
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_overall_score(self) -> float:
        """Calculate overall SEO optimization score"""        scores = [
            self.readability_score * 0.15,
            abs(self.sentiment_score) * 0.10,
            self.trend_alignment * 0.25,
            self.competitor_gap_score * 0.20,
            np.mean(list(self.platform_optimization_score.values())) * 0.30
        ]
        return min(100.0, sum(scores))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format"""        return {
            'keyword_density': self.keyword_density,
            'readability_score': self.readability_score,
            'sentiment_score': self.sentiment_score,
            'trend_alignment': self.trend_alignment,
            'competitor_gap_score': self.competitor_gap_score,
            'platform_optimization_score': self.platform_optimization_score,
            'seo_potential_score': self.seo_potential_score,
            'overall_score': self.calculate_overall_score(),
            'processing_time': self.processing_time,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }

@dataclass
class SEOOptimizationResult:
    """Comprehensive SEO optimization results"""    content_id: str
    optimization_type: SEOOptimizationType
    target_platforms: List[PlatformType]
    original_content: Dict[str, Any]
    optimized_content: Dict[str, Any]
    keywords: Dict[str, float]
    seo_metrics: SEOMetrics
    recommendations: List[str]
    competitor_insights: Dict[str, Any]
    trend_data: Dict[str, Any]
    
    def get_platform_specific_optimization(self, platform: PlatformType) -> Dict[str, Any]:
        """Get platform-specific optimization recommendations"""        platform_configs = {
            PlatformType.YOUTUBE: {
                'title_length': 60,
                'description_length': 125,
                'tags_count': 10,
                'focus_keywords': 3
            },
            PlatformType.SPOTIFY: {
                'title_length': 50,
                'description_length': 100,
                'tags_count': 5,
                'focus_keywords': 2
            },
            PlatformType.INSTAGRAM: {
                'title_length': 30,
                'description_length': 150,
                'hashtags_count': 20,
                'focus_keywords': 2
            },
            PlatformType.TIKTOK: {
                'title_length': 40,
                'description_length': 80,
                'hashtags_count': 15,
                'focus_keywords': 2
            }
        }
        
        config = platform_configs.get(platform, {})
        return {
            'platform': platform.value,
            'optimized_title': self._optimize_title_for_platform(platform, config),
            'optimized_description': self._optimize_description_for_platform(platform, config),
            'optimized_tags': self._optimize_tags_for_platform(platform, config),
            'platform_score': self.seo_metrics.platform_optimization_score.get(platform.value, 0.0)
        }
    
    def _optimize_title_for_platform(self, platform: PlatformType, config: Dict[str, Any]) -> str:
        """Optimize title for specific platform"""        original_title = self.original_content.get('title', '')
        max_length = config.get('title_length', 60)
        focus_keywords = config.get('focus_keywords', 2)
        
        # Extract top keywords
        top_keywords = sorted(self.keywords.items(), key=lambda x: x[1], reverse=True)[:focus_keywords]
        keyword_list = [kw[0] for kw in top_keywords]
        
        # Platform-specific title optimization
        if platform == PlatformType.YOUTUBE:
            return self._create_youtube_title(original_title, keyword_list, max_length)
        elif platform == PlatformType.SPOTIFY:
            return self._create_spotify_title(original_title, keyword_list, max_length)
        elif platform == PlatformType.INSTAGRAM:
            return self._create_instagram_title(original_title, keyword_list, max_length)
        elif platform == PlatformType.TIKTOK:
            return self._create_tiktok_title(original_title, keyword_list, max_length)
        
        return original_title[:max_length]
    
    def _optimize_description_for_platform(self, platform: PlatformType, config: Dict[str, Any]) -> str:
        """Optimize description for specific platform"""        original_desc = self.original_content.get('description', '')
        max_length = config.get('description_length', 125)
        
        # Platform-specific description optimization logic
        optimized_desc = self.optimized_content.get('description', original_desc)
        return optimized_desc[:max_length]
    
    def _optimize_tags_for_platform(self, platform: PlatformType, config: Dict[str, Any]) -> List[str]:
        """Optimize tags/hashtags for specific platform"""        max_tags = config.get('tags_count', 10)
        tags = list(self.keywords.keys())[:max_tags]
        
        if platform in [PlatformType.INSTAGRAM, PlatformType.TIKTOK]:
            return [f"#{tag.replace(' ', '')}" for tag in tags]
        
        return tags
    
    def _create_youtube_title(self, title: str, keywords: List[str], max_length: int) -> str:
        """Create YouTube-optimized title"""        if not keywords:
            return title[:max_length]
        
        main_keyword = keywords[0]
        if main_keyword.lower() not in title.lower():
            title = f"{main_keyword} - {title}"
        
        return title[:max_length]
    
    def _create_spotify_title(self, title: str, keywords: List[str], max_length: int) -> str:
        """Create Spotify-optimized title"""        # Spotify focuses on artist and track clarity
        return title[:max_length]
    
    def _create_instagram_title(self, title: str, keywords: List[str], max_length: int) -> str:
        """Create Instagram-optimized title"""        if keywords:
            title = f"✨ {title} ✨"
        return title[:max_length]
    
    def _create_tiktok_title(self, title: str, keywords: List[str], max_length: int) -> str:
        """Create TikTok-optimized title"""        if keywords:
            title = f"🔥 {title}"
        return title[:max_length]

class SEOOptimizationHandler(BaseEventHandler):
    """    Enterprise-grade SEO optimization event handler
    
    Processes SEO optimization events with advanced keyword analysis,
    competitor insights, trend alignment, and platform-specific optimization.
    """    
    def __init__(self, ai_engine: Any):
        """Initialize SEO optimization handler"""        super().__init__()
        self.ai_engine = ai_engine
        self.keyword_analyzer = KeywordAnalyzer()
        self.content_optimizer = ContentOptimizer()
        self.competitor_analyzer = CompetitorAnalyzer()
        
        # Initialize NLP models
        self._initialize_nlp_models()
        
        # Platform-specific configuration
        self.platform_configs = self._load_platform_configs()
        
        # SEO processing metrics
        self.optimization_stats = defaultdict(int)
        self.performance_metrics = defaultdict(list)
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for text analysis"""        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            # Initialize spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found, using basic tokenization")
                self.nlp = None
            
            # Initialize transformer models
            self.keyword_extractor = pipeline(
                "feature-extraction",
                model="distilbert-base-uncased",
                return_tensors="pt"
            )
            
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            self.sentiment_analyzer = None
            self.nlp = None
            self.keyword_extractor = None
    
    def _load_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific SEO configurations"""        return {
            "youtube": {
                "title_length": 60,
                "description_length": 125,
                "tags_count": 10,
                "keyword_density_range": (2, 5),
                "trending_topics_weight": 0.3,
                "engagement_factors": ["watch_time", "likes", "comments", "shares"]
            },
            "spotify": {
                "title_length": 50,
                "description_length": 100,
                "tags_count": 5,
                "keyword_density_range": (1, 3),
                "trending_topics_weight": 0.2,
                "engagement_factors": ["plays", "saves", "playlist_adds"]
            },
            "instagram": {
                "title_length": 30,
                "description_length": 150,
                "hashtags_count": 20,
                "keyword_density_range": (3, 7),
                "trending_topics_weight": 0.4,
                "engagement_factors": ["likes", "comments", "saves", "shares"]
            },
            "tiktok": {
                "title_length": 40,
                "description_length": 80,
                "hashtags_count": 15,
                "keyword_density_range": (4, 8),
                "trending_topics_weight": 0.5,
                "engagement_factors": ["views", "likes", "shares", "comments"]
            }
        }
    
    async def handle_event(self, event_data: Dict[str, Any]) -> SEOOptimizationResult:
        """        Handle SEO optimization event
        
        Args:
            event_data: Event data containing content and optimization parameters
            
        Returns:
            SEOOptimizationResult: Comprehensive optimization results
        """        start_time = time.time()
        
        try:
            # Extract event information
            content_id = event_data.get('content_id')
            optimization_type = SEOOptimizationType(event_data.get('optimization_type', 'keyword_optimization'))
            target_platforms = [PlatformType(p) for p in event_data.get('target_platforms', ['youtube'])]
            content_data = event_data.get('content_data', {})
            
            logger.info(f"Processing SEO optimization for content {content_id}")
            
            # Perform comprehensive SEO analysis
            seo_analysis = await self._perform_seo_analysis(content_data, target_platforms)
            
            # Generate optimization recommendations
            optimization_result = await self._generate_optimization_result(
                content_id, optimization_type, target_platforms, content_data, seo_analysis
            )
            
            # Update metrics
            processing_time = time.time() - start_time
            self.optimization_stats[optimization_type.value] += 1
            self.performance_metrics['processing_time'].append(processing_time)
            
            logger.info(f"SEO optimization completed for {content_id} in {processing_time:.2f}s")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"SEO optimization failed for content {event_data.get('content_id')}: {e}")
            raise
    
    async def _perform_seo_analysis(self, content_data: Dict[str, Any], 
                                   target_platforms: List[PlatformType]) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis"""        analysis_tasks = [
            self._extract_keywords(content_data),
            self._analyze_readability(content_data),
            self._analyze_sentiment(content_data),
            self._analyze_trends(content_data, target_platforms),
            self._analyze_competitors(content_data, target_platforms),
            self._calculate_platform_scores(content_data, target_platforms)
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        return {
            'keywords': results[0] if not isinstance(results[0], Exception) else {},
            'readability': results[1] if not isinstance(results[1], Exception) else 0.0,
            'sentiment': results[2] if not isinstance(results[2], Exception) else 0.0,
            'trends': results[3] if not isinstance(results[3], Exception) else {},
            'competitors': results[4] if not isinstance(results[4], Exception) else {},
            'platform_scores': results[5] if not isinstance(results[5], Exception) else {}
        }
    
    async def _extract_keywords(self, content_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract and score keywords from content"""        try:
            text_content = self._extract_text_content(content_data)
            
            if not text_content:
                return {}
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text_content)
            
            # Extract keywords using TF-IDF
            tfidf_keywords = self._extract_tfidf_keywords(cleaned_text)
            
            # Extract named entities if spaCy is available
            if self.nlp:
                entity_keywords = self._extract_entity_keywords(cleaned_text)
                tfidf_keywords.update(entity_keywords)
            
            # Score and rank keywords
            scored_keywords = self._score_keywords(tfidf_keywords, cleaned_text)
            
            return dict(sorted(scored_keywords.items(), key=lambda x: x[1], reverse=True)[:20])
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {}
    
    def _extract_text_content(self, content_data: Dict[str, Any]) -> str:
        """Extract all text content from various sources"""        text_parts = []
        
        # Extract from different content fields
        fields_to_extract = ['title', 'description', 'lyrics', 'transcript', 'tags', 'metadata']
        
        for field in fields_to_extract:
            if field in content_data:
                value = content_data[field]
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(item) for item in value])
                elif isinstance(value, dict):
                    text_parts.extend([str(v) for v in value.values() if isinstance(v, str)])
        
        return ' '.join(text_parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip().lower()
    
    def _extract_tfidf_keywords(self, text: str) -> Dict[str, float]:
        """Extract keywords using TF-IDF"""        try:
            # Tokenize and remove stopwords
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(text)
            words = [word for word in words if word not in stop_words and len(word) > 2]
            
            if len(words) < 3:
                return {}
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=50,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([' '.join(words)])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            return dict(zip(feature_names, tfidf_scores))
            
        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return {}
    
    def _extract_entity_keywords(self, text: str) -> Dict[str, float]:
        """Extract named entities as keywords"""        try:
            doc = self.nlp(text)
            entities = {}
            
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                    entities[ent.text.lower()] = 0.8  # High relevance score
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {}
    
    def _score_keywords(self, keywords: Dict[str, float], text: str) -> Dict[str, float]:
        """Score keywords based on various factors"""        scored_keywords = {}
        text_length = len(text.split())
        
        for keyword, base_score in keywords.items():
            # Calculate keyword density
            keyword_count = text.lower().count(keyword.lower())
            density = (keyword_count / text_length) * 100 if text_length > 0 else 0
            
            # Adjust score based on density (optimal range 2-5%)
            density_score = 1.0
            if 2 <= density <= 5:
                density_score = 1.2
            elif density > 8:
                density_score = 0.6
            
            # Consider keyword length (longer phrases often more specific)
            length_score = min(1.5, 1.0 + (len(keyword.split()) - 1) * 0.2)
            
            final_score = base_score * density_score * length_score
            scored_keywords[keyword] = final_score
        
        return scored_keywords
    
    async def _analyze_readability(self, content_data: Dict[str, Any]) -> float:
        """Analyze content readability"""        try:
            text_content = self._extract_text_content(content_data)
            
            if not text_content or len(text_content) < 10:
                return 50.0  # Default moderate score
            
            # Calculate Flesch Reading Ease score
            readability_score = flesch_reading_ease(text_content)
            
            # Normalize to 0-100 scale
            return max(0.0, min(100.0, readability_score))
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return 50.0
    
    async def _analyze_sentiment(self, content_data: Dict[str, Any]) -> float:
        """Analyze content sentiment"""        try:
            if not self.sentiment_analyzer:
                return 0.0
            
            text_content = self._extract_text_content(content_data)
            
            if not text_content:
                return 0.0
            
            # Analyze sentiment
            sentiment_scores = self.sentiment_analyzer.polarity_scores(text_content)
            
            # Return compound score (-1 to 1)
            return sentiment_scores['compound']
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.0
    
    async def _analyze_trends(self, content_data: Dict[str, Any], 
                            target_platforms: List[PlatformType]) -> Dict[str, Any]:
        """Analyze trending topics and keywords"""        try:
            # Simulate trend analysis (in production, integrate with real trend APIs)
            trending_keywords = [
                "viral", "trending", "2025", "new", "exclusive",
                "live", "original", "remix", "cover", "acoustic"
            ]
            
            content_text = self._extract_text_content(content_data).lower()
            
            trend_alignment = 0.0
            matched_trends = []
            
            for keyword in trending_keywords:
                if keyword in content_text:
                    trend_alignment += 0.1
                    matched_trends.append(keyword)
            
            return {
                'trend_alignment_score': min(1.0, trend_alignment),
                'matched_trends': matched_trends,
                'trending_keywords': trending_keywords[:10],
                'platform_trends': {platform.value: trending_keywords[:5] for platform in target_platforms}
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {'trend_alignment_score': 0.0, 'matched_trends': []}
    
    async def _analyze_competitors(self, content_data: Dict[str, Any], 
                                  target_platforms: List[PlatformType]) -> Dict[str, Any]:
        """Analyze competitor content and strategies"""        try:
            # Simulate competitor analysis
            competitor_data = {
                'top_performers': [
                    {'title': 'Viral Song 2025', 'engagement': 95.5, 'keywords': ['viral', '2025', 'hit']},
                    {'title': 'Trending Track', 'engagement': 88.2, 'keywords': ['trending', 'music', 'new']}
                ],
                'keyword_gaps': ['exclusive', 'premiere', 'collaboration'],
                'optimization_opportunities': [
                    'Include trending hashtags',
                    'Optimize title length for platform',
                    'Use competitor successful keywords'
                ],
                'average_engagement': 75.3,
                'competitor_gap_score': 0.65
            }
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {'competitor_gap_score': 0.5}
    
    async def _calculate_platform_scores(self, content_data: Dict[str, Any], 
                                        target_platforms: List[PlatformType]) -> Dict[str, float]:
        """Calculate optimization scores for each target platform"""        platform_scores = {}
        
        for platform in target_platforms:
            try:
                config = self.platform_configs.get(platform.value, {})
                
                # Analyze content against platform requirements
                title_score = self._calculate_title_score(content_data, config)
                description_score = self._calculate_description_score(content_data, config)
                keyword_score = self._calculate_keyword_score(content_data, config)
                
                # Combined platform score
                platform_score = (title_score + description_score + keyword_score) / 3
                platform_scores[platform.value] = platform_score
                
            except Exception as e:
                logger.error(f"Platform score calculation failed for {platform.value}: {e}")
                platform_scores[platform.value] = 50.0
        
        return platform_scores
    
    def _calculate_title_score(self, content_data: Dict[str, Any], config: Dict[str, Any]) -> float:
        """Calculate title optimization score for platform"""        title = content_data.get('title', '')
        max_length = config.get('title_length', 60)
        
        if not title:
            return 0.0
        
        # Length optimization score
        length_score = 100.0 if len(title) <= max_length else max(0.0, 100.0 - (len(title) - max_length) * 2)
        
        # Keyword presence score (simplified)
        keyword_score = 80.0 if any(kw in title.lower() for kw in ['new', 'exclusive', 'original']) else 60.0
        
        return (length_score + keyword_score) / 2
    
    def _calculate_description_score(self, content_data: Dict[str, Any], config: Dict[str, Any]) -> float:
        """Calculate description optimization score for platform"""        description = content_data.get('description', '')
        max_length = config.get('description_length', 125)
        
        if not description:
            return 50.0
        
        # Length optimization score
        length_score = 100.0 if len(description) <= max_length else max(0.0, 100.0 - (len(description) - max_length))
        
        # Content quality score (simplified)
        quality_score = 90.0 if len(description.split()) >= 5 else 70.0
        
        return (length_score + quality_score) / 2
    
    def _calculate_keyword_score(self, content_data: Dict[str, Any], config: Dict[str, Any]) -> float:
        """Calculate keyword optimization score for platform"""        # Simplified keyword scoring
        tags = content_data.get('tags', [])
        max_tags = config.get('tags_count', 10)
        
        if not tags:
            return 40.0
        
        # Tag count score
        tag_count_score = min(100.0, (len(tags) / max_tags) * 100)
        
        # Tag quality score (simplified)
        quality_score = 85.0 if len(tags) > 0 else 0.0
        
        return (tag_count_score + quality_score) / 2
    
    async def _generate_optimization_result(self, content_id: str, optimization_type: SEOOptimizationType,
                                          target_platforms: List[PlatformType], content_data: Dict[str, Any],
                                          seo_analysis: Dict[str, Any]) -> SEOOptimizationResult:
        """Generate comprehensive optimization result"""        
        # Create SEO metrics
        seo_metrics = SEOMetrics(
            keyword_density=self._calculate_keyword_densities(seo_analysis['keywords'], content_data),
            readability_score=seo_analysis['readability'],
            sentiment_score=seo_analysis['sentiment'],
            trend_alignment=seo_analysis['trends'].get('trend_alignment_score', 0.0),
            competitor_gap_score=seo_analysis['competitors'].get('competitor_gap_score', 0.5),
            platform_optimization_score=seo_analysis['platform_scores'],
            seo_potential_score=0.0,  # Will be calculated
            processing_time=0.0  # Will be set by caller
        )
        
        # Calculate SEO potential score
        seo_metrics.seo_potential_score = seo_metrics.calculate_overall_score()
        
        # Generate optimized content
        optimized_content = await self._generate_optimized_content(content_data, seo_analysis, target_platforms)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(seo_analysis, target_platforms)
        
        return SEOOptimizationResult(
            content_id=content_id,
            optimization_type=optimization_type,
            target_platforms=target_platforms,
            original_content=content_data,
            optimized_content=optimized_content,
            keywords=seo_analysis['keywords'],
            seo_metrics=seo_metrics,
            recommendations=recommendations,
            competitor_insights=seo_analysis['competitors'],
            trend_data=seo_analysis['trends']
        )
    
    def _calculate_keyword_densities(self, keywords: Dict[str, float], content_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate keyword density percentages"""        text_content = self._extract_text_content(content_data)
        word_count = len(text_content.split()) if text_content else 1
        
        densities = {}
        for keyword, score in keywords.items():
            keyword_count = text_content.lower().count(keyword.lower()) if text_content else 0
            density = (keyword_count / word_count) * 100
            densities[keyword] = density
        
        return densities
    
    async def _generate_optimized_content(self, original_content: Dict[str, Any], 
                                         seo_analysis: Dict[str, Any], 
                                         target_platforms: List[PlatformType]) -> Dict[str, Any]:
        """Generate optimized content based on SEO analysis"""        optimized = original_content.copy()
        keywords = seo_analysis['keywords']
        trends = seo_analysis['trends'].get('matched_trends', [])
        
        # Optimize title
        if 'title' in optimized and keywords:
            top_keywords = list(keywords.keys())[:2]
            original_title = optimized['title']
            
            # Add trending keywords if not present
            for keyword in top_keywords:
                if keyword.lower() not in original_title.lower():
                    optimized['title'] = f"{keyword.title()} {original_title}"
                    break
        
        # Optimize description
        if 'description' in optimized and keywords:
            description = optimized['description']
            top_keywords = list(keywords.keys())[:3]
            
            # Ensure top keywords are mentioned
            for keyword in top_keywords:
                if keyword.lower() not in description.lower():
                    description += f" #{keyword.replace(' ', '')}"
            
            optimized['description'] = description
        
        # Optimize tags
        if keywords:
            suggested_tags = list(keywords.keys())[:10]
            optimized['suggested_tags'] = suggested_tags
            
            # Add trending tags
            if trends:
                optimized['trending_tags'] = trends
        
        return optimized
    
    def _generate_recommendations(self, seo_analysis: Dict[str, Any], 
                                 target_platforms: List[PlatformType]) -> List[str]:
        """Generate SEO optimization recommendations"""        recommendations = []
        
        # Keyword recommendations
        keywords = seo_analysis['keywords']
        if keywords:
            top_keyword = list(keywords.keys())[0]
            recommendations.append(f"Focus on primary keyword: '{top_keyword}'")
            recommendations.append(f"Include top 3 keywords in title and description")
        
        # Platform-specific recommendations
        for platform in target_platforms:
            config = self.platform_configs.get(platform.value, {})
            recommendations.append(f"For {platform.value}: Optimize title to {config.get('title_length', 60)} characters")
        
        # Trend recommendations
        trends = seo_analysis['trends']
        if trends.get('matched_trends'):
            recommendations.append(f"Leverage trending topics: {', '.join(trends['matched_trends'][:3])}")
        
        # Competitor recommendations
        competitor_data = seo_analysis['competitors']
        if competitor_data.get('keyword_gaps'):
            gap_keywords = competitor_data['keyword_gaps'][:2]
            recommendations.append(f"Consider competitor keywords: {', '.join(gap_keywords)}")
        
        # Readability recommendations
        readability = seo_analysis['readability']
        if readability < 60:
            recommendations.append("Improve readability with shorter sentences and simpler words")
        
        # Sentiment recommendations
        sentiment = seo_analysis['sentiment']
        if sentiment < -0.3:
            recommendations.append("Consider more positive language to improve engagement")
        elif sentiment > 0.5:
            recommendations.append("Great positive sentiment - maintain this tone")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get handler performance statistics"""        return {
            'optimization_counts': dict(self.optimization_stats),
            'average_processing_time': np.mean(self.performance_metrics['processing_time']) if self.performance_metrics['processing_time'] else 0,
            'total_optimizations': sum(self.optimization_stats.values()),
            'supported_platforms': [platform.value for platform in PlatformType],
            'supported_optimization_types': [opt_type.value for opt_type in SEOOptimizationType]
        }
    
    async def cleanup(self):
        """Cleanup handler resources"""        logger.info("Cleaning up SEO optimization handler resources")
        self.optimization_stats.clear()
        self.performance_metrics.clear()
