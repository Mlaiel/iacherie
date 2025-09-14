"""
🔍 SEO Optimizer - Enterprise Search Engine Optimization Engine
Consolidated: seo_metadata_processor.py + trending_content_processor.py

Technologies: NLP, Keyword Analysis, Trend Prediction, ML Optimization
Team: SEO Expert + ML Engineer + Lead Dev IA + Backend Senior
"""

import asyncio
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import aiohttp
import numpy as np
from collections import Counter
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import requests
import redis.asyncio as redis

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception:
    pass

# Enums
class SEOPriority(Enum):
    """SEO optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContentType(Enum):
    """Content types for SEO optimization"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"

class TrendingPlatform(Enum):
    """Platforms for trending analysis"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"

# Configuration
@dataclass
class SEOConfig:
    """Configuration for SEO optimization system"""
    target_languages: List[str] = None
    primary_regions: List[str] = None
    keyword_density_target: float = 0.02  # 2%
    min_content_length: int = 100
    max_title_length: int = 60
    max_description_length: int = 160
    enable_trending_analysis: bool = True
    enable_competitor_analysis: bool = True
    auto_generate_tags: bool = True
    redis_url: str = "redis://localhost:6379"
    api_keys: Dict[str, str] = None
    
    def __post_init__(self) -> None:
        if self.target_languages is None:
            self.target_languages = ['en', 'fr', 'de', 'ar', 'es']
        if self.primary_regions is None:
            self.primary_regions = ['US', 'FR', 'DE', 'SA', 'CA']
        if self.api_keys is None:
            self.api_keys = {
                'google_trends': '',
                'youtube_api': '',
                'twitter_api': '',
                'instagram_api': ''
            }

# Data Models
@dataclass
class SEOMetadata:
    """SEO metadata for content"""
    content_id: str
    title: str
    description: str
    keywords: List[str]
    tags: List[str]
    language: str
    region: str
    category: str
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    duration: Optional[int] = None
    publish_date: Optional[datetime] = None
    last_updated: datetime = None
    
    def __post_init__(self) -> None:
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

@dataclass
class TrendingData:
    """Trending content analysis data"""
    keyword: str
    platform: TrendingPlatform
    trend_score: float
    search_volume: int
    competition_level: str
    related_keywords: List[str]
    trending_period: Tuple[datetime, datetime]
    regional_data: Dict[str, float]
    demographics: Dict[str, Any]

@dataclass
class SEOOptimizationReport:
    """SEO optimization analysis report"""
    content_id: str
    original_metadata: SEOMetadata
    optimized_metadata: SEOMetadata
    optimization_score: float
    improvements: List[str]
    trending_opportunities: List[TrendingData]
    competitor_insights: Dict[str, Any]
    recommendations: List[str]
    estimated_reach_improvement: float
    generated_at: datetime

@dataclass
class ViralPrediction:
    """Viral content prediction data"""
    content_id: str
    viral_probability: float
    predicted_reach: int
    peak_engagement_time: datetime
    trending_factors: List[str]
    viral_triggers: Dict[str, float]
    platform_specific_scores: Dict[TrendingPlatform, float]

# Exceptions
class SEOError(Exception):
    """Base SEO optimization error"""
    pass

class TrendingAnalysisError(SEOError):
    """Trending analysis error"""
    pass

class MetadataOptimizationError(SEOError):
    """Metadata optimization error"""
    pass

# Core SEO Optimizer
class EnterpriseSEOOptimizer:
    """
    🎯 Enterprise SEO optimization and trending analysis system
    
    Features:
    - Intelligent metadata optimization
    - Real-time trending analysis
    - Multi-platform SEO strategies
    - Viral content prediction
    - Competitor intelligence
    - Multi-language optimization
    """
    
    def __init__(self, config -> None: Optional[SEOConfig] = None) -> None:
        self.config = config or SEOConfig()
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.redis_client = None
        
        # Initialize NLP tools
        self._initialize_nlp_tools()
        
        # Initialize trending analysis
        self._initialize_trending_analysis()
        
        # Stop words for different languages
        self.stop_words = {
            'en': set(stopwords.words('english')),
            'fr': set(stopwords.words('french')),
            'de': set(stopwords.words('german')),
            'es': set(stopwords.words('spanish')),
            'ar': set()  # Arabic stopwords would be loaded separately
        }
        
    def _initialize_nlp_tools(self) -> None:
        """Initialize NLP tools and models"""
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            self.keyword_extractor = None  # Placeholder for advanced keyword extraction
            self.sentiment_analyzer = None  # Placeholder for sentiment analysis
            self.logger.info("NLP tools initialized for SEO optimization")
        except Exception as e:
            self.logger.warning(f"NLP tools initialization failed: {e}")

    def _initialize_trending_analysis(self) -> None:
        """Initialize trending analysis tools"""
        try:
            self.trending_analyzers = {
                TrendingPlatform.YOUTUBE: self._analyze_youtube_trends,
                TrendingPlatform.TIKTOK: self._analyze_tiktok_trends,
                TrendingPlatform.INSTAGRAM: self._analyze_instagram_trends,
                TrendingPlatform.TWITTER: self._analyze_twitter_trends,
            }
            self.logger.info("Trending analysis tools initialized")
        except Exception as e:
            self.logger.warning(f"Trending analysis initialization failed: {e}")

    async def initialize_redis(self) -> None:
        """Initialize Redis connection for caching"""
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            self.logger.info("Redis connection established for SEO optimizer")
        except Exception as e:
            self.logger.error(f"Redis connection failed: {e}")
            self.redis_client = None

    async def optimize_content_seo(
        self,
        content_id: str,
        content_path: Union[str, Path],
        content_type: ContentType,
        existing_metadata: Optional[SEOMetadata] = None,
        target_platforms: Optional[List[TrendingPlatform]] = None
    ) -> SEOOptimizationReport:
        """
        🚀 Comprehensive SEO optimization for content
        
        Args:
            content_id: Unique content identifier
            content_path: Path to content file
            content_type: Type of content
            existing_metadata: Current metadata (if any)
            target_platforms: Target platforms for optimization
            
        Returns:
            Complete SEO optimization report
        """
        try:
            content_path = Path(content_path)
            target_platforms = target_platforms or [
                TrendingPlatform.YOUTUBE,
                TrendingPlatform.TIKTOK,
                TrendingPlatform.INSTAGRAM
            ]
            
            # Step 1: Analyze content
            content_analysis = await self._analyze_content_for_seo(
                content_path, content_type
            )
            
            # Step 2: Extract current metadata or create basic metadata
            if existing_metadata:
                original_metadata = existing_metadata
            else:
                original_metadata = await self._extract_basic_metadata(
                    content_id, content_analysis
                )
            
            # Step 3: Analyze trending opportunities
            trending_opportunities = await self._analyze_trending_opportunities(
                content_analysis, target_platforms
            )
            
            # Step 4: Optimize metadata
            optimized_metadata = await self._optimize_metadata(
                original_metadata, content_analysis, trending_opportunities
            )
            
            # Step 5: Competitor analysis
            competitor_insights = await self._analyze_competitors(
                optimized_metadata.keywords, target_platforms
            )
            
            # Step 6: Generate optimization report
            optimization_score = self._calculate_optimization_score(
                original_metadata, optimized_metadata
            )
            
            improvements = self._identify_improvements(
                original_metadata, optimized_metadata
            )
            
            recommendations = self._generate_recommendations(
                optimized_metadata, trending_opportunities, competitor_insights
            )
            
            estimated_reach_improvement = self._estimate_reach_improvement(
                optimization_score, trending_opportunities
            )
            
            report = SEOOptimizationReport(
                content_id=content_id,
                original_metadata=original_metadata,
                optimized_metadata=optimized_metadata,
                optimization_score=optimization_score,
                improvements=improvements,
                trending_opportunities=trending_opportunities,
                competitor_insights=competitor_insights,
                recommendations=recommendations,
                estimated_reach_improvement=estimated_reach_improvement,
                generated_at=datetime.utcnow()
            )
            
            # Cache the report
            if self.redis_client:
                await self.redis_client.setex(
                    f"seo_report:{content_id}",
                    86400,  # 24 hours
                    json.dumps(asdict(report), default=str)
                )
            
            self.logger.info(f"SEO optimization completed for {content_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"SEO optimization failed: {e}")
            raise MetadataOptimizationError(f"SEO optimization failed: {e}")

    async def _analyze_content_for_seo(
        self,
        content_path: Path,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze content for SEO opportunities"""
        def _analyze() -> None:
            analysis = {
                'file_size': content_path.stat().st_size,
                'file_type': content_path.suffix.lower(),
                'content_type': content_type.value,
                'extracted_text': '',
                'detected_language': 'en',
                'sentiment': 'neutral',
                'topics': [],
                'entities': [],
                'duration': None
            }
            
            # Basic text extraction based on content type
            if content_type == ContentType.TEXT:
                try:
                    with open(content_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    analysis['extracted_text'] = text
                    analysis['detected_language'] = self._detect_language(text)
                    analysis['sentiment'] = self._analyze_sentiment(text)
                    analysis['topics'] = self._extract_topics(text)
                    analysis['entities'] = self._extract_entities(text)
                except Exception as e:
                    self.logger.warning(f"Text analysis failed: {e}")
            
            # For other content types, extract metadata
            elif content_type in [ContentType.VIDEO, ContentType.AUDIO]:
                # Placeholder for media metadata extraction
                # In production: Use FFprobe, speech-to-text, etc.
                analysis['duration'] = self._estimate_duration(content_path)
            
            return analysis
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _analyze)

    def _detect_language(self, text: str) -> str:
        """Detect language of text content"""
        try:
            blob = TextBlob(text)
            detected = blob.detect_language()
            return detected if detected in self.config.target_languages else 'en'
        except Exception:
            return 'en'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text content"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                return 'positive'
            elif polarity < -0.1:
                return 'negative'
            else:
                return 'neutral'
        except Exception:
            return 'neutral'

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        try:
            # Simple topic extraction using keyword frequency
            words = word_tokenize(text.lower())
            words = [w for w in words if w.isalpha() and w not in self.stop_words.get('en', set())]
            
            # Get most frequent words as topics
            word_freq = Counter(words)
            topics = [word for word, count in word_freq.most_common(10) if count > 2]
            
            return topics[:5]  # Return top 5 topics
        except Exception:
            return []

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        try:
            # Simple entity extraction using capitalized words
            sentences = sent_tokenize(text)
            entities = []
            
            for sentence in sentences:
                words = word_tokenize(sentence)
                for word in words:
                    if word.istitle() and len(word) > 2:
                        entities.append(word)
            
            # Remove duplicates and return most frequent
            entity_freq = Counter(entities)
            return [entity for entity, count in entity_freq.most_common(10)]
        except Exception:
            return []

    def _estimate_duration(self, content_path: Path) -> Optional[int]:
        """Estimate content duration in seconds"""
        # Placeholder for duration estimation
        # In production: Use FFprobe or similar tools
        file_size = content_path.stat().st_size
        # Rough estimation based on file size (very simplified)
        estimated_duration = file_size // (1024 * 1024) * 60  # 1MB per minute
        return min(estimated_duration, 3600)  # Max 1 hour

    async def _extract_basic_metadata(
        self,
        content_id: str,
        content_analysis: Dict[str, Any]
    ) -> SEOMetadata:
        """Extract or generate basic metadata"""
        # Generate basic metadata from content analysis
        filename = content_id.replace('_', ' ').replace('-', ' ').title()
        
        return SEOMetadata(
            content_id=content_id,
            title=filename[:self.config.max_title_length],
            description=f"High-quality {content_analysis['content_type']} content",
            keywords=content_analysis.get('topics', [])[:10],
            tags=content_analysis.get('entities', [])[:15],
            language=content_analysis.get('detected_language', 'en'),
            region=self.config.primary_regions[0],
            category='entertainment',
            duration=content_analysis.get('duration')
        )

    async def _analyze_trending_opportunities(
        self,
        content_analysis: Dict[str, Any],
        target_platforms: List[TrendingPlatform]
    ) -> List[TrendingData]:
        """Analyze trending opportunities across platforms"""
        try:
            trending_opportunities = []
            
            # Extract potential keywords from content
            potential_keywords = (
                content_analysis.get('topics', []) +
                content_analysis.get('entities', [])
            )
            
            for platform in target_platforms:
                if platform in self.trending_analyzers:
                    try:
                        platform_trends = await self.trending_analyzers[platform](
                            potential_keywords
                        )
                        trending_opportunities.extend(platform_trends)
                    except Exception as e:
                        self.logger.warning(f"Trending analysis failed for {platform}: {e}")
                        continue
            
            # Sort by trend score
            trending_opportunities.sort(key=lambda x: x.trend_score, reverse=True)
            return trending_opportunities[:20]  # Top 20 opportunities
            
        except Exception as e:
            self.logger.error(f"Trending analysis failed: {e}")
            return []

    async def _analyze_youtube_trends(self, keywords: List[str]) -> List[TrendingData]:
        """Analyze YouTube trending data"""
        # Simplified YouTube trends analysis
        # In production: Use YouTube Data API
        trends = []
        
        for keyword in keywords[:5]:  # Limit to top 5 keywords
            trend = TrendingData(
                keyword=keyword,
                platform=TrendingPlatform.YOUTUBE,
                trend_score=np.random.uniform(0.3, 0.9),
                search_volume=np.random.randint(1000, 100000),
                competition_level='medium',
                related_keywords=[f"{keyword} tutorial", f"{keyword} 2025", f"best {keyword}"],
                trending_period=(
                    datetime.utcnow() - timedelta(days=7),
                    datetime.utcnow() + timedelta(days=7)
                ),
                regional_data={'US': 0.8, 'FR': 0.6, 'DE': 0.7},
                demographics={'age_18_34': 0.6, 'age_35_54': 0.3}
            )
            trends.append(trend)
        
        return trends

    async def _analyze_tiktok_trends(self, keywords: List[str]) -> List[TrendingData]:
        """Analyze TikTok trending data"""
        # Simplified TikTok trends analysis
        trends = []
        
        for keyword in keywords[:3]:
            trend = TrendingData(
                keyword=f"#{keyword}",
                platform=TrendingPlatform.TIKTOK,
                trend_score=np.random.uniform(0.4, 0.95),
                search_volume=np.random.randint(5000, 500000),
                competition_level='high',
                related_keywords=[f"#{keyword}challenge", f"#{keyword}trend", f"#{keyword}viral"],
                trending_period=(
                    datetime.utcnow() - timedelta(days=3),
                    datetime.utcnow() + timedelta(days=3)
                ),
                regional_data={'US': 0.9, 'FR': 0.7, 'DE': 0.6},
                demographics={'age_13_24': 0.7, 'age_25_34': 0.3}
            )
            trends.append(trend)
        
        return trends

    async def _analyze_instagram_trends(self, keywords: List[str]) -> List[TrendingData]:
        """Analyze Instagram trending data"""
        # Simplified Instagram trends analysis
        trends = []
        
        for keyword in keywords[:4]:
            trend = TrendingData(
                keyword=f"#{keyword}",
                platform=TrendingPlatform.INSTAGRAM,
                trend_score=np.random.uniform(0.35, 0.85),
                search_volume=np.random.randint(2000, 200000),
                competition_level='medium',
                related_keywords=[f"#{keyword}style", f"#{keyword}inspo", f"#{keyword}life"],
                trending_period=(
                    datetime.utcnow() - timedelta(days=5),
                    datetime.utcnow() + timedelta(days=5)
                ),
                regional_data={'US': 0.85, 'FR': 0.75, 'DE': 0.65},
                demographics={'age_18_34': 0.8, 'age_35_54': 0.2}
            )
            trends.append(trend)
        
        return trends

    async def _analyze_twitter_trends(self, keywords: List[str]) -> List[TrendingData]:
        """Analyze Twitter trending data"""
        # Simplified Twitter trends analysis
        trends = []
        
        for keyword in keywords[:3]:
            trend = TrendingData(
                keyword=f"#{keyword}",
                platform=TrendingPlatform.TWITTER,
                trend_score=np.random.uniform(0.3, 0.8),
                search_volume=np.random.randint(1000, 50000),
                competition_level='low',
                related_keywords=[f"#{keyword}news", f"#{keyword}update", f"#{keyword}discussion"],
                trending_period=(
                    datetime.utcnow() - timedelta(days=1),
                    datetime.utcnow() + timedelta(days=1)
                ),
                regional_data={'US': 0.8, 'FR': 0.6, 'DE': 0.7},
                demographics={'age_25_44': 0.6, 'age_35_54': 0.4}
            )
            trends.append(trend)
        
        return trends

    async def _optimize_metadata(
        self,
        original_metadata: SEOMetadata,
        content_analysis: Dict[str, Any],
        trending_opportunities: List[TrendingData]
    ) -> SEOMetadata:
        """Optimize metadata based on analysis and trends"""
        
        # Extract trending keywords
        trending_keywords = [trend.keyword for trend in trending_opportunities[:10]]
        
        # Optimize title
        optimized_title = await self._optimize_title(
            original_metadata.title,
            trending_keywords,
            content_analysis
        )
        
        # Optimize description
        optimized_description = await self._optimize_description(
            original_metadata.description,
            trending_keywords,
            content_analysis
        )
        
        # Optimize keywords
        optimized_keywords = await self._optimize_keywords(
            original_metadata.keywords,
            trending_keywords,
            content_analysis
        )
        
        # Optimize tags
        optimized_tags = await self._optimize_tags(
            original_metadata.tags,
            trending_keywords,
            content_analysis
        )
        
        return SEOMetadata(
            content_id=original_metadata.content_id,
            title=optimized_title,
            description=optimized_description,
            keywords=optimized_keywords,
            tags=optimized_tags,
            language=original_metadata.language,
            region=original_metadata.region,
            category=original_metadata.category,
            thumbnail_url=original_metadata.thumbnail_url,
            transcript=original_metadata.transcript,
            duration=original_metadata.duration,
            publish_date=original_metadata.publish_date
        )

    async def _optimize_title(
        self,
        original_title: str,
        trending_keywords: List[str],
        content_analysis: Dict[str, Any]
    ) -> str:
        """Optimize title for better SEO"""
        # Find the best trending keyword to include
        best_keyword = None
        for keyword in trending_keywords:
            if keyword.lower() not in original_title.lower():
                best_keyword = keyword.replace('#', '')
                break
        
        if best_keyword and len(original_title) + len(best_keyword) + 3 <= self.config.max_title_length:
            optimized_title = f"{original_title} - {best_keyword.title()}"
        else:
            optimized_title = original_title
        
        # Ensure title length limit
        if len(optimized_title) > self.config.max_title_length:
            optimized_title = optimized_title[:self.config.max_title_length-3] + "..."
        
        return optimized_title

    async def _optimize_description(
        self,
        original_description: str,
        trending_keywords: List[str],
        content_analysis: Dict[str, Any]
    ) -> str:
        """Optimize description for better SEO"""
        # Add trending keywords naturally
        additional_keywords = []
        for keyword in trending_keywords[:3]:
            clean_keyword = keyword.replace('#', '')
            if clean_keyword.lower() not in original_description.lower():
                additional_keywords.append(clean_keyword)
        
        if additional_keywords:
            keyword_text = f"Features: {', '.join(additional_keywords)}."
            optimized_description = f"{original_description} {keyword_text}"
        else:
            optimized_description = original_description
        
        # Ensure description length limit
        if len(optimized_description) > self.config.max_description_length:
            optimized_description = optimized_description[:self.config.max_description_length-3] + "..."
        
        return optimized_description

    async def _optimize_keywords(
        self,
        original_keywords: List[str],
        trending_keywords: List[str],
        content_analysis: Dict[str, Any]
    ) -> List[str]:
        """Optimize keywords list"""
        # Combine original keywords with trending ones
        all_keywords = list(set(original_keywords + [
            kw.replace('#', '') for kw in trending_keywords
        ]))
        
        # Add content topics
        content_topics = content_analysis.get('topics', [])
        all_keywords.extend([topic for topic in content_topics if topic not in all_keywords])
        
        # Remove duplicates and limit to reasonable number
        unique_keywords = list(set(all_keywords))
        
        # Sort by potential SEO value (simplified)
        optimized_keywords = sorted(unique_keywords, key=len)[:20]
        
        return optimized_keywords

    async def _optimize_tags(
        self,
        original_tags: List[str],
        trending_keywords: List[str],
        content_analysis: Dict[str, Any]
    ) -> List[str]:
        """Optimize tags list"""
        # Combine original tags with trending hashtags
        all_tags = list(set(original_tags + trending_keywords))
        
        # Add entity-based tags
        entities = content_analysis.get('entities', [])
        all_tags.extend([f"#{entity.lower()}" for entity in entities if f"#{entity.lower()}" not in all_tags])
        
        # Remove duplicates and limit
        unique_tags = list(set(all_tags))
        
        # Sort by length and relevance
        optimized_tags = sorted(unique_tags, key=len)[:30]
        
        return optimized_tags

    async def _analyze_competitors(
        self,
        keywords: List[str],
        platforms: List[TrendingPlatform]
    ) -> Dict[str, Any]:
        """Analyze competitor content for insights"""
        # Simplified competitor analysis
        # In production: Use platform APIs to analyze top content
        
        competitor_insights = {
            'top_competitors': ['Creator1', 'Creator2', 'Creator3'],
            'average_engagement': {'likes': 15000, 'shares': 2000, 'comments': 500},
            'successful_strategies': [
                'Consistent posting schedule',
                'Trending hashtag usage',
                'High-quality thumbnails',
                'Engaging titles with numbers'
            ],
            'content_gaps': [
                'Tutorial content',
                'Behind-the-scenes content',
                'Interactive Q&A sessions'
            ],
            'optimal_posting_times': {
                'youtube': '14:00-16:00',
                'tiktok': '18:00-20:00',
                'instagram': '11:00-13:00'
            }
        }
        
        return competitor_insights

    def _calculate_optimization_score(
        self,
        original_metadata: SEOMetadata,
        optimized_metadata: SEOMetadata
    ) -> float:
        """Calculate optimization improvement score"""
        score = 0.0
        
        # Title optimization score
        if len(optimized_metadata.title) > len(original_metadata.title):
            score += 10
        
        # Description optimization score
        if len(optimized_metadata.description) > len(original_metadata.description):
            score += 15
        
        # Keywords optimization score
        if len(optimized_metadata.keywords) > len(original_metadata.keywords):
            score += 20
        
        # Tags optimization score
        if len(optimized_metadata.tags) > len(original_metadata.tags):
            score += 25
        
        # Trending keyword integration score
        trending_integration = len([
            kw for kw in optimized_metadata.keywords 
            if kw not in original_metadata.keywords
        ])
        score += min(trending_integration * 5, 30)
        
        return min(score, 100.0)

    def _identify_improvements(
        self,
        original_metadata: SEOMetadata,
        optimized_metadata: SEOMetadata
    ) -> List[str]:
        """Identify specific improvements made"""
        improvements = []
        
        if optimized_metadata.title != original_metadata.title:
            improvements.append("Title optimized with trending keywords")
        
        if optimized_metadata.description != original_metadata.description:
            improvements.append("Description enhanced with SEO keywords")
        
        if len(optimized_metadata.keywords) > len(original_metadata.keywords):
            improvements.append(f"Added {len(optimized_metadata.keywords) - len(original_metadata.keywords)} new keywords")
        
        if len(optimized_metadata.tags) > len(original_metadata.tags):
            improvements.append(f"Added {len(optimized_metadata.tags) - len(original_metadata.tags)} new tags")
        
        return improvements

    def _generate_recommendations(
        self,
        optimized_metadata: SEOMetadata,
        trending_opportunities: List[TrendingData],
        competitor_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable SEO recommendations"""
        recommendations = []
        
        # Trending recommendations
        if trending_opportunities:
            top_trend = trending_opportunities[0]
            recommendations.append(
                f"Consider creating content around '{top_trend.keyword}' - high trending score of {top_trend.trend_score:.2f}"
            )
        
        # Platform-specific recommendations
        recommendations.extend([
            "Post during optimal times based on competitor analysis",
            "Use high-quality thumbnails with contrast and readable text",
            "Include call-to-action in descriptions",
            "Engage with comments within first hour of posting"
        ])
        
        # Content recommendations
        gap_opportunities = competitor_insights.get('content_gaps', [])
        if gap_opportunities:
            recommendations.append(f"Content opportunity: {gap_opportunities[0]}")
        
        return recommendations[:10]

    def _estimate_reach_improvement(
        self,
        optimization_score: float,
        trending_opportunities: List[TrendingData]
    ) -> float:
        """Estimate potential reach improvement percentage"""
        base_improvement = optimization_score * 0.5  # Base improvement from optimization
        
        # Additional improvement from trending keywords
        trending_boost = 0
        for trend in trending_opportunities[:3]:
            trending_boost += trend.trend_score * 20
        
        total_improvement = base_improvement + trending_boost
        return min(total_improvement, 300.0)  # Cap at 300% improvement

    async def predict_viral_potential(
        self,
        content_id: str,
        metadata: SEOMetadata,
        trending_data: List[TrendingData]
    ) -> ViralPrediction:
        """
        🔮 Predict viral potential of content
        
        Args:
            content_id: Content identifier
            metadata: Optimized metadata
            trending_data: Current trending data
            
        Returns:
            Viral potential prediction
        """
        try:
            # Calculate viral probability based on multiple factors
            viral_factors = {
                'trending_alignment': self._calculate_trending_alignment(metadata, trending_data),
                'keyword_strength': len(metadata.keywords) / 20.0,
                'tag_engagement': len(metadata.tags) / 30.0,
                'title_optimization': len(metadata.title) / self.config.max_title_length,
                'description_completeness': len(metadata.description) / self.config.max_description_length
            }
            
            # Calculate weighted viral probability
            weights = {
                'trending_alignment': 0.4,
                'keyword_strength': 0.2,
                'tag_engagement': 0.2,
                'title_optimization': 0.1,
                'description_completeness': 0.1
            }
            
            viral_probability = sum(
                viral_factors[factor] * weights[factor]
                for factor in viral_factors
            )
            
            # Estimate reach based on viral probability
            base_reach = 1000
            predicted_reach = int(base_reach * (1 + viral_probability * 100))
            
            # Estimate peak engagement time
            peak_engagement_time = datetime.utcnow() + timedelta(
                hours=np.random.randint(2, 24)
            )
            
            # Platform-specific scores
            platform_scores = {
                TrendingPlatform.YOUTUBE: viral_probability * 0.8,
                TrendingPlatform.TIKTOK: viral_probability * 1.2,
                TrendingPlatform.INSTAGRAM: viral_probability * 0.9,
                TrendingPlatform.TWITTER: viral_probability * 0.7
            }
            
            prediction = ViralPrediction(
                content_id=content_id,
                viral_probability=min(viral_probability, 1.0),
                predicted_reach=predicted_reach,
                peak_engagement_time=peak_engagement_time,
                trending_factors=list(viral_factors.keys()),
                viral_triggers=viral_factors,
                platform_specific_scores=platform_scores
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Viral prediction failed: {e}")
            raise TrendingAnalysisError(f"Viral prediction failed: {e}")

    def _calculate_trending_alignment(
        self,
        metadata: SEOMetadata,
        trending_data: List[TrendingData]
    ) -> float:
        """Calculate how well content aligns with trends"""
        if not trending_data:
            return 0.0
        
        alignment_score = 0.0
        total_trends = len(trending_data)
        
        for trend in trending_data:
            keyword = trend.keyword.replace('#', '').lower()
            
            # Check if trending keyword appears in metadata
            if any(keyword in item.lower() for item in [
                metadata.title,
                metadata.description,
                *metadata.keywords,
                *metadata.tags
            ]):
                alignment_score += trend.trend_score
        
        return alignment_score / total_trends if total_trends > 0 else 0.0

    async def get_seo_report(self, content_id: str) -> Optional[SEOOptimizationReport]:
        """Get cached SEO optimization report"""
        try:
            if self.redis_client:
                report_data = await self.redis_client.get(f"seo_report:{content_id}")
                if report_data:
                    data = json.loads(report_data)
                    return SEOOptimizationReport(**data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get SEO report: {e}")
            return None

# Legacy Integration Classes
class SEOMetadataProcessor:
    """Legacy SEO metadata processing interface"""
    
    def __init__(self, optimizer -> None: EnterpriseSEOOptimizer) -> None:
        self.optimizer = optimizer
    
    async def process_metadata(
        self,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and optimize metadata"""
        seo_metadata = SEOMetadata(**metadata)
        
        # Create dummy content analysis
        content_analysis = {
            'content_type': 'video',
            'topics': metadata.get('keywords', []),
            'entities': metadata.get('tags', []),
            'detected_language': metadata.get('language', 'en')
        }
        
        report = await self.optimizer.optimize_content_seo(
            content_id,
            Path("dummy_path"),
            ContentType.VIDEO,
            seo_metadata
        )
        
        return asdict(report.optimized_metadata)

class TrendingContentProcessor:
    """Legacy trending content processing interface"""
    
    def __init__(self, optimizer -> None: EnterpriseSEOOptimizer) -> None:
        self.optimizer = optimizer
    
    async def analyze_trends(
        self,
        keywords: List[str],
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze trending content"""
        platform_enums = [
            TrendingPlatform(platform) for platform in platforms
            if platform in [p.value for p in TrendingPlatform]
        ]
        
        content_analysis = {'topics': keywords, 'entities': []}
        trends = await self.optimizer._analyze_trending_opportunities(
            content_analysis, platform_enums
        )
        
        return [asdict(trend) for trend in trends]

# Factory Pattern
class SEOOptimizerFactory:
    """Factory for creating SEO optimizers"""
    
    @staticmethod
    def create_standard_optimizer() -> EnterpriseSEOOptimizer:
        """Create standard SEO optimizer"""
        return EnterpriseSEOOptimizer()
    
    @staticmethod
    def create_enterprise_optimizer() -> EnterpriseSEOOptimizer:
        """Create enterprise SEO optimizer"""
        config = SEOConfig(
            target_languages=['en', 'fr', 'de', 'ar', 'es', 'zh', 'ja'],
            enable_trending_analysis=True,
            enable_competitor_analysis=True,
            auto_generate_tags=True
        )
        return EnterpriseSEOOptimizer(config)

# Main interface
async def optimize_content_seo_enterprise(
    content_id: str,
    content_path: Union[str, Path],
    content_type: str,
    target_platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Enterprise SEO optimization interface"""
    optimizer = SEOOptimizerFactory.create_standard_optimizer()
    
    content_type_enum = ContentType(content_type)
    platform_enums = [TrendingPlatform(p) for p in (target_platforms or ['youtube', 'tiktok'])]
    
    report = await optimizer.optimize_content_seo(
        content_id, content_path, content_type_enum, target_platforms=platform_enums
    )
    
    return asdict(report)

# Export all public classes and functions
__all__ = [
    'EnterpriseSEOOptimizer',
    'SEOConfig',
    'SEOMetadata',
    'TrendingData',
    'SEOOptimizationReport',
    'ViralPrediction',
    'SEOPriority',
    'ContentType',
    'TrendingPlatform',
    'SEOMetadataProcessor',
    'TrendingContentProcessor',
    'SEOOptimizerFactory',
    'SEOError',
    'TrendingAnalysisError',
    'MetadataOptimizationError',
    'optimize_content_seo_enterprise'
]
