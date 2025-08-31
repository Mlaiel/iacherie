"""Content SEO Module - Professional SEO Optimization System

Module avancé pour l'optimisation SEO automatisée du contenu multimédia
dans la plateforme IA Influencer Agent selon la logique métier.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: SEO Expert, Content Marketing Specialist, AI Optimization Expert
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de

🎯 LOGIQUE MÉTIER SEO :
User Upload → IA Analysis → SEO Auto-Optimization → Multi-Platform Distribution → Performance Tracking
"""from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
import re
import json
import uuid
import asyncio
from pathlib import Path
from urllib.parse import urlparse

import requests
from textstat import flesch_reading_ease, automated_readability_index
from langdetect import detect
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .content_models import Base, ContentType

logger = logging.getLogger(__name__)

class SEOPriority(Enum):
    """SEO optimization priority levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class ContentOptimizationStatus(Enum):
    """Content optimization status"""    PENDING = "pending"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    OPTIMIZED = "optimized"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"

class SEOMetricType(Enum):
    """Types of SEO metrics"""    KEYWORD_DENSITY = "keyword_density"
    READABILITY_SCORE = "readability_score"
    META_COMPLETENESS = "meta_completeness"
    SEMANTIC_RELEVANCE = "semantic_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    SOCIAL_SHAREABILITY = "social_shareability"
    SEARCH_VISIBILITY = "search_visibility"
    CONVERSION_POTENTIAL = "conversion_potential"

class PlatformType(Enum):
    """Target platforms for SEO optimization"""    GOOGLE = "google"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"

@dataclass
class KeywordAnalysis:
    """Container for keyword analysis results"""    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    keyword_density: Dict[str, float]
    search_volume: Dict[str, int]
    competition_score: Dict[str, float]
    trending_keywords: List[str]
    semantic_keywords: List[str]
    
    def get_top_keywords(self, limit: int = 10) -> List[str]:
        """Get top keywords by relevance and search volume"""        # Sort by combination of search volume and low competition
        all_keywords = self.primary_keywords + self.secondary_keywords
        sorted_keywords = sorted(
            all_keywords,
            key=lambda k: self.search_volume.get(k, 0) * (1 - self.competition_score.get(k, 1)),
            reverse=True
        )
        return sorted_keywords[:limit]

@dataclass
class SEORecommendation:
    """Container for SEO recommendations"""    category: str
    priority: SEOPriority
    title: str
    description: str
    implementation: str
    expected_impact: str
    effort_level: str
    platform_specific: List[PlatformType] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""        return {
            'category': self.category,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'implementation': self.implementation,
            'expected_impact': self.expected_impact,
            'effort_level': self.effort_level,
            'platform_specific': [p.value for p in self.platform_specific]
        }

class ContentSEO(Base):
    """Database model for content SEO data"""    __tablename__ = "content_seo"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Content identification
    content_type = Column(String(20), nullable=False, index=True)
    content_title = Column(String(255), nullable=False)
    content_description = Column(Text, nullable=True)
    content_language = Column(String(10), nullable=False, default='en')
    
    # SEO optimization status
    optimization_status = Column(String(20), nullable=False, default='pending', index=True)
    optimization_score = Column(Float, nullable=False, default=0.0)
    last_optimization_date = Column(DateTime(timezone=True), nullable=True)
    
    # Keyword optimization
    primary_keywords = Column(ARRAY(String), nullable=False, default=[])
    secondary_keywords = Column(ARRAY(String), nullable=False, default=[])
    long_tail_keywords = Column(ARRAY(String), nullable=False, default=[])
    keyword_density = Column(JSONB, nullable=False, default={})
    
    # Meta data optimization
    optimized_title = Column(String(255), nullable=True)
    optimized_description = Column(Text, nullable=True)
    meta_keywords = Column(ARRAY(String), nullable=False, default=[])
    alt_text = Column(Text, nullable=True)
    canonical_url = Column(Text, nullable=True)
    
    # Social media optimization
    og_title = Column(String(255), nullable=True)
    og_description = Column(Text, nullable=True)
    og_image_url = Column(Text, nullable=True)
    twitter_title = Column(String(255), nullable=True)
    twitter_description = Column(Text, nullable=True)
    twitter_image_url = Column(Text, nullable=True)
    
    # Platform-specific optimization
    youtube_tags = Column(ARRAY(String), nullable=False, default=[])
    youtube_category = Column(String(100), nullable=True)
    instagram_hashtags = Column(ARRAY(String), nullable=False, default=[])
    tiktok_hashtags = Column(ARRAY(String), nullable=False, default=[])
    spotify_genres = Column(ARRAY(String), nullable=False, default=[])
    
    # SEO metrics and scores
    readability_score = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=False, default=0.0)
    virality_potential = Column(Float, nullable=False, default=0.0)
    search_visibility_score = Column(Float, nullable=False, default=0.0)
    
    # Performance tracking
    organic_views = Column(Integer, nullable=False, default=0)
    search_impressions = Column(Integer, nullable=False, default=0)
    click_through_rate = Column(Float, nullable=False, default=0.0)
    average_position = Column(Float, nullable=True)
    
    # AI analysis results
    content_sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    content_themes = Column(ARRAY(String), nullable=False, default=[])
    target_audience = Column(JSONB, nullable=False, default={})
    competitor_analysis = Column(JSONB, nullable=False, default={})
    
    # Recommendations and suggestions
    seo_recommendations = Column(JSONB, nullable=False, default=[])
    optimization_suggestions = Column(JSONB, nullable=False, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<ContentSEO(id={self.id}, score={self.optimization_score}, status={self.optimization_status})>"

class SEOPerformanceMetrics(Base):
    """Database model for SEO performance tracking"""    __tablename__ = "seo_performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_seo_id = Column(UUID(as_uuid=True), ForeignKey('content_seo.id'), nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    
    # Performance metrics
    impressions = Column(Integer, nullable=False, default=0)
    clicks = Column(Integer, nullable=False, default=0)
    ctr = Column(Float, nullable=False, default=0.0)
    average_position = Column(Float, nullable=True)
    conversions = Column(Integer, nullable=False, default=0)
    conversion_rate = Column(Float, nullable=False, default=0.0)
    
    # Engagement metrics
    likes = Column(Integer, nullable=False, default=0)
    shares = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    saves = Column(Integer, nullable=False, default=0)
    engagement_rate = Column(Float, nullable=False, default=0.0)
    
    # Reach and visibility
    reach = Column(Integer, nullable=False, default=0)
    unique_views = Column(Integer, nullable=False, default=0)
    repeat_views = Column(Integer, nullable=False, default=0)
    view_duration = Column(Float, nullable=False, default=0.0)
    
    # Traffic sources
    organic_traffic = Column(Integer, nullable=False, default=0)
    social_traffic = Column(Integer, nullable=False, default=0)
    referral_traffic = Column(Integer, nullable=False, default=0)
    direct_traffic = Column(Integer, nullable=False, default=0)
    
    # Revenue metrics
    revenue_generated = Column(Float, nullable=False, default=0.0)
    cost_per_acquisition = Column(Float, nullable=False, default=0.0)
    return_on_investment = Column(Float, nullable=False, default=0.0)
    
    # Tracking period
    date_recorded = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    content_seo = relationship("ContentSEO", back_populates="performance_metrics")
    
    def __repr__(self) -> str:
        return f"<SEOPerformanceMetrics(platform={self.platform}, impressions={self.impressions})>"

class KeywordResearcher:
    """Advanced keyword research and analysis engine"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.api_keys = self.config.get('api_keys', {})
        self.supported_languages = ['en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh']
    
    async def analyze_content_keywords(self, content: str, content_type: ContentType,
                                     language: str = 'en') -> KeywordAnalysis:
        """Analyze content to extract relevant keywords"""        try:
            # Clean and preprocess content
            cleaned_content = self._clean_content(content)
            
            # Extract keywords using multiple methods
            primary_keywords = await self._extract_primary_keywords(cleaned_content, language)
            secondary_keywords = await self._extract_secondary_keywords(cleaned_content, language)
            long_tail_keywords = await self._extract_long_tail_keywords(cleaned_content, language)
            
            # Calculate keyword density
            keyword_density = self._calculate_keyword_density(cleaned_content, 
                                                            primary_keywords + secondary_keywords)
            
            # Get search volume and competition data
            search_volume = await self._get_search_volumes(primary_keywords + secondary_keywords)
            competition_score = await self._get_competition_scores(primary_keywords + secondary_keywords)
            
            # Find trending keywords
            trending_keywords = await self._find_trending_keywords(primary_keywords, content_type)
            
            # Generate semantic keywords
            semantic_keywords = await self._generate_semantic_keywords(primary_keywords, language)
            
            return KeywordAnalysis(
                primary_keywords=primary_keywords,
                secondary_keywords=secondary_keywords,
                long_tail_keywords=long_tail_keywords,
                keyword_density=keyword_density,
                search_volume=search_volume,
                competition_score=competition_score,
                trending_keywords=trending_keywords,
                semantic_keywords=semantic_keywords
            )
            
        except Exception as e:
            self.logger.error(f"Keyword analysis failed: {e}")
            raise
    
    def _clean_content(self, content: str) -> str:
        """Clean and preprocess content for analysis"""        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove special characters but keep spaces and punctuation
        content = re.sub(r'[^\w\s\.,!?;:-]', '', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content.lower()
    
    async def _extract_primary_keywords(self, content: str, language: str) -> List[str]:
        """Extract primary keywords from content"""        try:
            # Simple keyword extraction (in production, would use NLP libraries)
            words = content.split()
            
            # Filter out common stop words
            stop_words = {
                'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'},
                'de': {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'an', 'zu', 'für', 'von', 'mit', 'bei', 'ist', 'sind', 'war', 'waren', 'sein', 'haben', 'hat', 'hatte'},
                'fr': {'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec', 'par', 'est', 'sont', 'était', 'étaient', 'être', 'avoir', 'a', 'avait'}
            }
            
            current_stop_words = stop_words.get(language, stop_words['en'])
            
            # Count word frequencies
            word_freq = {}
            for word in words:
                if len(word) > 2 and word not in current_stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords by frequency
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            primary_keywords = [word for word, freq in sorted_keywords[:20] if freq > 1]
            
            return primary_keywords
            
        except Exception as e:
            self.logger.error(f"Primary keyword extraction failed: {e}")
            return []
    
    async def _extract_secondary_keywords(self, content: str, language: str) -> List[str]:
        """Extract secondary keywords from content"""        try:
            # Extract 2-3 word phrases
            words = content.split()
            phrases = []
            
            for i in range(len(words) - 1):
                if len(words[i]) > 2 and len(words[i+1]) > 2:
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
                
                if i < len(words) - 2 and len(words[i+2]) > 2:
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    phrases.append(phrase)
            
            # Count phrase frequencies
            phrase_freq = {}
            for phrase in phrases:
                phrase_freq[phrase] = phrase_freq.get(phrase, 0) + 1
            
            # Get top phrases
            sorted_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)
            secondary_keywords = [phrase for phrase, freq in sorted_phrases[:15] if freq > 1]
            
            return secondary_keywords
            
        except Exception as e:
            self.logger.error(f"Secondary keyword extraction failed: {e}")
            return []
    
    async def _extract_long_tail_keywords(self, content: str, language: str) -> List[str]:
        """Extract long-tail keywords (4+ words)"""        try:
            # Extract longer phrases
            sentences = re.split(r'[.!?]+', content)
            long_tail = []
            
            for sentence in sentences:
                words = sentence.strip().split()
                if 4 <= len(words) <= 8:
                    # Check if it's a meaningful phrase
                    if not any(word in {'the', 'a', 'an', 'and', 'or', 'but'} for word in words[:2]):
                        long_tail.append(' '.join(words))
            
            return long_tail[:10]  # Return top 10 long-tail keywords
            
        except Exception as e:
            self.logger.error(f"Long-tail keyword extraction failed: {e}")
            return []
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density for each keyword"""        total_words = len(content.split())
        if total_words == 0:
            return {}
        
        density = {}
        for keyword in keywords:
            count = content.lower().count(keyword.lower())
            density[keyword] = (count / total_words) * 100
        
        return density
    
    async def _get_search_volumes(self, keywords: List[str]) -> Dict[str, int]:
        """Get search volume estimates for keywords"""        # Placeholder for search volume API integration
        # In production, would integrate with Google Keyword Planner API, SEMrush, etc.
        volumes = {}
        for keyword in keywords:
            # Simulate search volume based on keyword length and common patterns
            base_volume = max(100, 10000 // len(keyword.split()))
            volumes[keyword] = base_volume
        
        return volumes
    
    async def _get_competition_scores(self, keywords: List[str]) -> Dict[str, float]:
        """Get competition scores for keywords"""        # Placeholder for competition analysis
        # In production, would analyze SERP results and competitor density
        scores = {}
        for keyword in keywords:
            # Simulate competition score (0-1, where 1 is high competition)
            score = min(0.9, len(keyword.split()) * 0.2 + 0.1)
            scores[keyword] = score
        
        return scores
    
    async def _find_trending_keywords(self, keywords: List[str], content_type: ContentType) -> List[str]:
        """Find trending keywords related to content"""        # Placeholder for trending keyword discovery
        # In production, would integrate with Google Trends API, social media APIs
        trending = []
        
        # Add some trending patterns based on content type
        if content_type == ContentType.AUDIO:
            trending.extend(['viral music', 'trending audio', 'popular song'])
        elif content_type == ContentType.VIDEO:
            trending.extend(['viral video', 'trending content', 'popular clip'])
        elif content_type == ContentType.IMAGE:
            trending.extend(['viral image', 'trending photo', 'popular picture'])
        
        return trending[:5]
    
    async def _generate_semantic_keywords(self, primary_keywords: List[str], language: str) -> List[str]:
        """Generate semantically related keywords"""        # Placeholder for semantic keyword generation
        # In production, would use word embeddings, semantic networks
        semantic = []
        
        for keyword in primary_keywords[:5]:  # Process top 5 keywords
            # Simple semantic expansion (in production, use word2vec, BERT, etc.)
            if 'music' in keyword:
                semantic.extend(['audio', 'sound', 'melody', 'rhythm', 'song'])
            elif 'video' in keyword:
                semantic.extend(['film', 'movie', 'clip', 'footage', 'visual'])
            elif 'photo' in keyword or 'image' in keyword:
                semantic.extend(['picture', 'photography', 'visual', 'snapshot', 'portrait'])
        
        return list(set(semantic))  # Remove duplicates

class SEOOptimizer:
    """Advanced SEO optimization engine"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.keyword_researcher = KeywordResearcher(config)
    
    async def optimize_content(self, content_id: str, content_data: Dict[str, Any],
                             target_platforms: List[PlatformType] = None) -> ContentSEO:
        """Perform comprehensive SEO optimization"""        try:
            target_platforms = target_platforms or [PlatformType.GOOGLE, PlatformType.YOUTUBE]
            
            # Extract content information
            content_type = ContentType(content_data.get('type', 'text'))
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            content_text = content_data.get('content', '')
            language = content_data.get('language', 'en')
            
            # Detect language if not provided
            if not language and content_text:
                try:
                    language = detect(content_text)
                except:
                    language = 'en'
            
            # Perform keyword analysis
            full_content = f"{title} {description} {content_text}"
            keyword_analysis = await self.keyword_researcher.analyze_content_keywords(
                full_content, content_type, language
            )
            
            # Generate optimized meta data
            optimized_title = await self._optimize_title(title, keyword_analysis, content_type)
            optimized_description = await self._optimize_description(description, keyword_analysis)
            
            # Calculate SEO scores
            optimization_score = await self._calculate_optimization_score(
                optimized_title, optimized_description, keyword_analysis
            )
            readability_score = self._calculate_readability_score(full_content)
            engagement_score = await self._predict_engagement_score(content_data, keyword_analysis)
            
            # Generate platform-specific optimizations
            platform_optimizations = await self._optimize_for_platforms(
                content_data, keyword_analysis, target_platforms
            )
            
            # Generate SEO recommendations
            recommendations = await self._generate_recommendations(
                content_data, keyword_analysis, optimization_score
            )
            
            # Create SEO record
            content_seo = ContentSEO(
                content_id=content_id,
                user_id=content_data.get('user_id'),
                content_type=content_type.value,
                content_title=title,
                content_description=description,
                content_language=language,
                optimization_status=ContentOptimizationStatus.OPTIMIZED.value,
                optimization_score=optimization_score,
                last_optimization_date=datetime.utcnow().replace(tzinfo=timezone.utc),
                
                # Keywords
                primary_keywords=keyword_analysis.primary_keywords,
                secondary_keywords=keyword_analysis.secondary_keywords,
                long_tail_keywords=keyword_analysis.long_tail_keywords,
                keyword_density=keyword_analysis.keyword_density,
                
                # Optimized meta data
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                meta_keywords=keyword_analysis.get_top_keywords(10),
                
                # Social media optimization
                og_title=optimized_title[:60],  # Facebook OG title limit
                og_description=optimized_description[:160],  # Facebook OG description limit
                twitter_title=optimized_title[:70],  # Twitter title limit
                twitter_description=optimized_description[:200],  # Twitter description limit
                
                # Platform-specific
                youtube_tags=platform_optimizations.get('youtube_tags', []),
                youtube_category=platform_optimizations.get('youtube_category'),
                instagram_hashtags=platform_optimizations.get('instagram_hashtags', []),
                tiktok_hashtags=platform_optimizations.get('tiktok_hashtags', []),
                spotify_genres=platform_optimizations.get('spotify_genres', []),
                
                # Scores
                readability_score=readability_score,
                engagement_score=engagement_score,
                virality_potential=await self._predict_virality_potential(content_data, keyword_analysis),
                search_visibility_score=await self._predict_search_visibility(keyword_analysis),
                
                # AI analysis
                content_sentiment=await self._analyze_sentiment(full_content),
                content_themes=await self._extract_themes(full_content),
                target_audience=await self._analyze_target_audience(content_data, keyword_analysis),
                
                # Recommendations
                seo_recommendations=[rec.to_dict() for rec in recommendations],
                optimization_suggestions=platform_optimizations,
                
                analyzed_at=datetime.utcnow().replace(tzinfo=timezone.utc)
            )
            
            return content_seo
            
        except Exception as e:
            self.logger.error(f"SEO optimization failed: {e}")
            raise
    
    async def _optimize_title(self, original_title: str, keyword_analysis: KeywordAnalysis,
                            content_type: ContentType) -> str:
        """Optimize title for SEO"""        if not original_title:
            # Generate title from keywords
            top_keywords = keyword_analysis.get_top_keywords(3)
            if content_type == ContentType.AUDIO:
                return f"{' '.join(top_keywords[:2])} - Music"
            elif content_type == ContentType.VIDEO:
                return f"{' '.join(top_keywords[:2])} - Video"
            else:
                return ' '.join(top_keywords[:3])
        
        # Optimize existing title
        optimized = original_title
        top_keyword = keyword_analysis.get_top_keywords(1)
        
        if top_keyword and top_keyword[0].lower() not in optimized.lower():
            # Add primary keyword if not present
            optimized = f"{top_keyword[0]} - {optimized}"
        
        # Ensure optimal length (50-60 characters for Google)
        if len(optimized) > 60:
            optimized = optimized[:57] + "..."
        
        return optimized
    
    async def _optimize_description(self, original_description: str, 
                                  keyword_analysis: KeywordAnalysis) -> str:
        """Optimize description for SEO"""        if not original_description:
            # Generate description from keywords
            keywords = keyword_analysis.get_top_keywords(5)
            return f"Discover {', '.join(keywords[:3])} and more. High-quality content featuring {', '.join(keywords[3:])}."
        
        # Optimize existing description
        optimized = original_description
        top_keywords = keyword_analysis.get_top_keywords(3)
        
        # Ensure primary keywords are included
        for keyword in top_keywords:
            if keyword.lower() not in optimized.lower():
                optimized += f" {keyword.title()}"
        
        # Ensure optimal length (150-160 characters for Google)
        if len(optimized) > 160:
            optimized = optimized[:157] + "..."
        elif len(optimized) < 120:
            # Add call-to-action
            optimized += " Click to discover more!"
        
        return optimized
    
    async def _calculate_optimization_score(self, title: str, description: str,
                                          keyword_analysis: KeywordAnalysis) -> float:
        """Calculate overall SEO optimization score"""        score = 0.0
        
        # Title optimization (25 points)
        if title:
            if 30 <= len(title) <= 60:
                score += 10
            if any(kw.lower() in title.lower() for kw in keyword_analysis.get_top_keywords(3)):
                score += 15
        
        # Description optimization (25 points)
        if description:
            if 120 <= len(description) <= 160:
                score += 10
            if any(kw.lower() in description.lower() for kw in keyword_analysis.get_top_keywords(5)):
                score += 15
        
        # Keyword optimization (30 points)
        if keyword_analysis.primary_keywords:
            score += min(20, len(keyword_analysis.primary_keywords) * 2)
        if keyword_analysis.long_tail_keywords:
            score += min(10, len(keyword_analysis.long_tail_keywords))
        
        # Content quality (20 points)
        if keyword_analysis.semantic_keywords:
            score += min(10, len(keyword_analysis.semantic_keywords))
        if keyword_analysis.trending_keywords:
            score += 10
        
        return min(100.0, score)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score"""        if not content or len(content) < 100:
            return 50.0  # Neutral score for short content
        
        try:
            # Use Flesch Reading Ease score
            flesch_score = flesch_reading_ease(content)
            return max(0.0, min(100.0, flesch_score))
        except:
            return 50.0
    
    async def _predict_engagement_score(self, content_data: Dict[str, Any],
                                      keyword_analysis: KeywordAnalysis) -> float:
        """Predict content engagement potential"""        score = 50.0  # Base score
        
        # Trending keywords boost
        if keyword_analysis.trending_keywords:
            score += len(keyword_analysis.trending_keywords) * 5
        
        # Content type factors
        content_type = content_data.get('type', 'text')
        if content_type in ['video', 'audio']:
            score += 10  # Visual/audio content tends to engage more
        
        # Title quality
        title = content_data.get('title', '')
        if title:
            if '?' in title or '!' in title:
                score += 5  # Questions and exclamations engage more
            if any(word in title.lower() for word in ['how', 'why', 'best', 'top', 'ultimate']):
                score += 5
        
        return min(100.0, score)
    
    async def _predict_virality_potential(self, content_data: Dict[str, Any],
                                        keyword_analysis: KeywordAnalysis) -> float:
        """Predict content virality potential"""        score = 20.0  # Low base score (virality is rare)
        
        # Trending keywords significantly boost virality
        if keyword_analysis.trending_keywords:
            score += len(keyword_analysis.trending_keywords) * 10
        
        # High search volume keywords
        high_volume_keywords = [
            kw for kw in keyword_analysis.primary_keywords
            if keyword_analysis.search_volume.get(kw, 0) > 5000
        ]
        score += len(high_volume_keywords) * 5
        
        # Content type factors
        content_type = content_data.get('type', 'text')
        if content_type in ['video', 'image']:
            score += 15  # Visual content more likely to go viral
        
        return min(100.0, score)
    
    async def _predict_search_visibility(self, keyword_analysis: KeywordAnalysis) -> float:
        """Predict search engine visibility"""        if not keyword_analysis.primary_keywords:
            return 10.0
        
        # Calculate based on keyword strength and competition
        total_score = 0.0
        for keyword in keyword_analysis.get_top_keywords(10):
            search_volume = keyword_analysis.search_volume.get(keyword, 0)
            competition = keyword_analysis.competition_score.get(keyword, 1.0)
            
            # Higher volume, lower competition = better visibility
            keyword_score = (search_volume / 1000) * (1 - competition)
            total_score += min(10.0, keyword_score)
        
        return min(100.0, total_score)
    
    async def _optimize_for_platforms(self, content_data: Dict[str, Any],
                                    keyword_analysis: KeywordAnalysis,
                                    platforms: List[PlatformType]) -> Dict[str, Any]:
        """Generate platform-specific optimizations"""        optimizations = {}
        
        for platform in platforms:
            if platform == PlatformType.YOUTUBE:
                optimizations['youtube_tags'] = keyword_analysis.get_top_keywords(15)
                optimizations['youtube_category'] = self._determine_youtube_category(content_data)
            
            elif platform == PlatformType.INSTAGRAM:
                hashtags = ['#' + kw.replace(' ', '') for kw in keyword_analysis.get_top_keywords(20)]
                optimizations['instagram_hashtags'] = hashtags
            
            elif platform == PlatformType.TIKTOK:
                hashtags = ['#' + kw.replace(' ', '') for kw in keyword_analysis.get_top_keywords(10)]
                # Add trending TikTok hashtags
                hashtags.extend(['#fyp', '#viral', '#trending'])
                optimizations['tiktok_hashtags'] = hashtags
            
            elif platform == PlatformType.SPOTIFY:
                optimizations['spotify_genres'] = self._determine_spotify_genres(content_data, keyword_analysis)
        
        return optimizations
    
    def _determine_youtube_category(self, content_data: Dict[str, Any]) -> str:
        """Determine appropriate YouTube category"""        content_type = content_data.get('type', 'text')
        title = content_data.get('title', '').lower()
        
        if content_type == 'audio' or 'music' in title:
            return 'Music'
        elif 'game' in title or 'gaming' in title:
            return 'Gaming'
        elif 'education' in title or 'tutorial' in title:
            return 'Education'
        elif 'comedy' in title or 'funny' in title:
            return 'Comedy'
        else:
            return 'Entertainment'
    
    def _determine_spotify_genres(self, content_data: Dict[str, Any],
                                keyword_analysis: KeywordAnalysis) -> List[str]:
        """Determine Spotify genres from content"""        genres = []
        keywords = ' '.join(keyword_analysis.primary_keywords).lower()
        
        genre_mapping = {
            'rock': 'rock',
            'pop': 'pop',
            'jazz': 'jazz',
            'classical': 'classical',
            'electronic': 'electronic',
            'hip hop': 'hip-hop',
            'rap': 'hip-hop',
            'country': 'country',
            'folk': 'folk',
            'blues': 'blues',
            'reggae': 'reggae',
            'metal': 'metal'
        }
        
        for keyword, genre in genre_mapping.items():
            if keyword in keywords:
                genres.append(genre)
        
        return genres[:5]  # Limit to 5 genres
    
    async def _analyze_sentiment(self, content: str) -> str:
        """Analyze content sentiment"""        # Placeholder for sentiment analysis
        # In production, would use sentiment analysis libraries or APIs
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    async def _extract_themes(self, content: str) -> List[str]:
        """Extract main themes from content"""        # Placeholder for theme extraction
        # In production, would use topic modeling, NLP libraries
        themes = []
        
        theme_keywords = {
            'technology': ['tech', 'digital', 'computer', 'software', 'app', 'ai', 'machine'],
            'music': ['music', 'song', 'audio', 'sound', 'melody', 'rhythm', 'beat'],
            'entertainment': ['fun', 'entertainment', 'show', 'movie', 'game', 'comedy'],
            'education': ['learn', 'education', 'tutorial', 'teach', 'study', 'knowledge'],
            'business': ['business', 'company', 'market', 'finance', 'money', 'economy'],
            'health': ['health', 'fitness', 'medical', 'doctor', 'exercise', 'wellness'],
            'travel': ['travel', 'trip', 'vacation', 'destination', 'journey', 'explore']
        }
        
        content_lower = content.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Return top 5 themes
    
    async def _analyze_target_audience(self, content_data: Dict[str, Any],
                                     keyword_analysis: KeywordAnalysis) -> Dict[str, Any]:
        """Analyze target audience characteristics"""        audience = {
            'age_groups': [],
            'interests': [],
            'demographics': {},
            'behavior_patterns': []
        }
        
        # Analyze keywords for audience indicators
        keywords = ' '.join(keyword_analysis.primary_keywords).lower()
        
        # Age group indicators
        if any(word in keywords for word in ['teen', 'young', 'college', 'student']):
            audience['age_groups'].append('18-24')
        if any(word in keywords for word in ['professional', 'career', 'business']):
            audience['age_groups'].append('25-34')
        if any(word in keywords for word in ['family', 'parent', 'kids']):
            audience['age_groups'].append('35-44')
        
        # Interest indicators
        if 'music' in keywords:
            audience['interests'].append('music')
        if 'tech' in keywords or 'digital' in keywords:
            audience['interests'].append('technology')
        if 'fitness' in keywords or 'health' in keywords:
            audience['interests'].append('health_fitness')
        
        return audience
    
    async def _generate_recommendations(self, content_data: Dict[str, Any],
                                      keyword_analysis: KeywordAnalysis,
                                      optimization_score: float) -> List[SEORecommendation]:
        """Generate SEO improvement recommendations"""        recommendations = []
        
        # Title optimization recommendations
        title = content_data.get('title', '')
        if not title or len(title) < 30:
            recommendations.append(SEORecommendation(
                category='title',
                priority=SEOPriority.HIGH,
                title='Optimize Title Length',
                description='Title should be 30-60 characters for optimal SEO',
                implementation='Create a descriptive title with primary keywords',
                expected_impact='Improved click-through rates and search rankings',
                effort_level='Low'
            ))
        
        # Keyword recommendations
        if len(keyword_analysis.primary_keywords) < 5:
            recommendations.append(SEORecommendation(
                category='keywords',
                priority=SEOPriority.MEDIUM,
                title='Expand Keyword Strategy',
                description='Add more relevant keywords to improve discoverability',
                implementation='Research and include related keywords in content',
                expected_impact='Better search visibility and reach',
                effort_level='Medium'
            ))
        
        # Content length recommendations
        content = content_data.get('content', '')
        if len(content) < 300:
            recommendations.append(SEORecommendation(
                category='content',
                priority=SEOPriority.MEDIUM,
                title='Increase Content Length',
                description='Longer content tends to rank better in search results',
                implementation='Add more detailed information and context',
                expected_impact='Improved search rankings and user engagement',
                effort_level='Medium'
            ))
        
        # Platform-specific recommendations
        if optimization_score < 70:
            recommendations.append(SEORecommendation(
                category='optimization',
                priority=SEOPriority.HIGH,
                title='Improve Overall Optimization',
                description='Content needs comprehensive SEO improvements',
                implementation='Focus on title, keywords, and meta descriptions',
                expected_impact='Significant improvement in search visibility',
                effort_level='High'
            ))
        
        return recommendations

# Add relationships to existing models
ContentSEO.performance_metrics = relationship("SEOPerformanceMetrics", back_populates="content_seo")

# Export all classes and enums
__all__ = [
    'SEOPriority',
    'ContentOptimizationStatus',
    'SEOMetricType',
    'PlatformType',
    'KeywordAnalysis',
    'SEORecommendation',
    'ContentSEO',
    'SEOPerformanceMetrics',
    'KeywordResearcher',
    'SEOOptimizer'
]
